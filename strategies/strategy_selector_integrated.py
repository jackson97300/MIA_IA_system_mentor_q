#!/usr/bin/env python3
"""
Strategy Selector Intégré avec les 10 nouvelles stratégies patterns
Version qui utilise le système de lazy loading existant et évite les imports problématiques.
"""

import sys
import os
import time
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.logger import get_logger
except ImportError:
    # Fallback si core.logger n'est pas disponible
    import logging
    def get_logger(name):
        return logging.getLogger(name)

# === Imports des 10 nouvelles stratégies ===
from strategies.gamma_pin_reversion import GammaPinReversion
from strategies.dealer_flip_breakout import DealerFlipBreakout
from strategies.liquidity_sweep_reversal import LiquiditySweepReversal
from strategies.stacked_imbalance_continuation import StackedImbalanceContinuation
from strategies.iceberg_tracker_follow import IcebergTrackerFollow
from strategies.cvd_divergence_trap import CvdDivergenceTrap
from strategies.opening_drive_fail import OpeningDriveFail
from strategies.es_nq_lead_lag_mirror import EsNqLeadLagMirror
from strategies.vwap_band_squeeze_break import VwapBandSqueezeBreak
from strategies.profile_gap_fill import ProfileGapFill

# === Imports des 6 nouvelles stratégies MenthorQ ===
from strategies.menthorq_of_bundle import (
    ZeroDTEWallSweepReversal, GammaWallBreakAndGo, HVLMagnetFade,
    D1ExtremeTrap, GexClusterMeanRevert, CallPutChannelRotation,
    get_family_tag, deduplicate_by_family, FAMILY_TAGS
)

# === Imports du système de lazy loading ===
try:
    from features import create_feature_calculator, create_market_regime_detector
except ImportError:
    # Fallback si features n'est pas disponible
    def create_feature_calculator(config=None):
        return None
    def create_market_regime_detector(config=None):
        return None

logger = get_logger(__name__)

# === ENUMS ===

class StrategyType(Enum):
    """Types de stratégies disponibles"""
    TREND_STRATEGY = "trend_strategy"
    RANGE_STRATEGY = "range_strategy"
    PATTERN_STRATEGY = "pattern_strategy"
    WAIT_STRATEGY = "wait_strategy"

class SignalDecision(Enum):
    """Décisions finales de signal"""
    EXECUTE_SIGNAL = "execute_signal"
    REJECT_SIGNAL = "reject_signal"
    WAIT_BETTER_SETUP = "wait_better_setup"
    REGIME_UNCLEAR = "regime_unclear"

# === DATACLASSES ===

@dataclass
class PatternSignal:
    """Signal généré par une pattern strategy"""
    strategy: str
    side: str
    confidence: float
    entry: float
    stop: float
    targets: List[float]
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StrategySelectionResult:
    """Résultat sélection stratégie avec patterns"""
    timestamp: pd.Timestamp
    
    # Strategy selection
    selected_strategy: StrategyType
    selection_reason: str
    selection_confidence: float
    
    # Market context (simplifié)
    market_regime: str = "UNKNOWN"
    regime_confidence: float = 0.0
    
    # Signal data
    signal_generated: bool = False
    pattern_signal: Optional[PatternSignal] = None
    final_decision: SignalDecision = SignalDecision.WAIT_BETTER_SETUP
    
    # Performance metrics
    confluence_score: float = 0.0
    total_processing_time_ms: float = 0.0
    
    # Pattern strategies tracking
    patterns_considered: List[str] = field(default_factory=list)
    best_pattern: Optional[str] = None
    pattern_signals_count: int = 0

@dataclass
class TradingContext:
    """Contexte trading complet"""
    timestamp: pd.Timestamp
    symbol: str = "ES"
    price: float = 4500.0
    volume: float = 1000.0
    tick_size: float = 0.25
    
    # Données optionnelles pour compatibilité
    market_data: Optional[Dict[str, Any]] = None
    structure_data: Optional[Dict[str, Any]] = None
    es_nq_data: Optional[Dict[str, Any]] = None
    sierra_patterns: Optional[Dict[str, Any]] = None

@dataclass
class SystemPerformance:
    """Performance système avec patterns"""
    total_analyses: int = 0
    trend_signals: int = 0
    range_signals: int = 0
    pattern_signals: int = 0
    rejected_signals: int = 0
    avg_processing_time: float = 0.0
    current_risk: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0

# === MAIN STRATEGY SELECTOR ===

class IntegratedStrategySelector:
    """
    Strategy Selector intégré avec les pattern strategies.
    
    Utilise le système de lazy loading existant et intègre les 10 nouvelles stratégies.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation du selector intégré"""
        self.config = config or {}
        
        # === Composants système (lazy loading) ===
        try:
            self.regime_detector = create_market_regime_detector(self.config.get('regime_config', {}))
            self.feature_calculator = create_feature_calculator(self.config.get('features_config', {}))
            logger.info("✅ Composants système chargés avec succès")
        except Exception as e:
            logger.warning(f"⚠️ Erreur chargement composants système: {e}")
            self.regime_detector = None
            self.feature_calculator = None
        
        # === Registry des pattern strategies ===
        self.pattern_strategies = [
            # 10 stratégies originales
            GammaPinReversion(), DealerFlipBreakout(), LiquiditySweepReversal(),
            StackedImbalanceContinuation(), IcebergTrackerFollow(),
            CvdDivergenceTrap(), OpeningDriveFail(),
            EsNqLeadLagMirror(), VwapBandSqueezeBreak(), ProfileGapFill(),
            # 6 nouvelles stratégies MenthorQ
            ZeroDTEWallSweepReversal(), GammaWallBreakAndGo(), HVLMagnetFade(),
            D1ExtremeTrap(), GexClusterMeanRevert(), CallPutChannelRotation(),
        ]
        
        # Anti-sur-sollicitation par stratégie
        self.last_fire_ts = defaultdict(lambda: pd.Timestamp(0))
        self.fire_cooldown_sec = self.config.get("pattern_fire_cooldown_sec", 60)
        
        # Cache de performance pour optimiser les calculs répétitifs
        self.cache = {}
        self.cache_ttl = 2.0  # 2 secondes
        self.last_cache_cleanup = time.time()
        
        # Paramètres
        self.min_pattern_confidence = self.config.get('min_pattern_confidence', 0.60)
        self.min_confluence_for_execution = self.config.get('min_confluence_execution', 0.70)
        self.min_dist_ticks_wall = self.config.get('min_dist_ticks_wall', 6)
        self.max_risk_budget = self.config.get('max_risk_budget', 1.0)
        
        # Performance tracking
        self.performance = SystemPerformance()
        self.signal_history: deque = deque(maxlen=200)
        
        logger.info(f"IntegratedStrategySelector initialisé avec {len(self.pattern_strategies)} pattern strategies")

    def analyze_and_select(self, trading_context: TradingContext) -> StrategySelectionResult:
        """
        Analyse complète et sélection du meilleur pattern.
        
        Args:
            trading_context: Contexte de trading
            
        Returns:
            StrategySelectionResult avec le meilleur pattern sélectionné
        """
        start_time = time.perf_counter()
        
        try:
            # === 1. ANALYSE RÉGIME MARCHÉ (si disponible) ===
            regime_data = None
            if self.regime_detector and trading_context.market_data:
                try:
                    regime_data = self.regime_detector.analyze_market_regime(
                        market_data=trading_context.market_data,
                        es_nq_data=trading_context.es_nq_data,
                        structure_data=trading_context.structure_data
                    )
                except Exception as e:
                    logger.warning(f"Erreur analyse régime: {e}")
            
            # === 2. CALCUL FEATURES (si disponible) avec cache ===
            features_result = None
            if self.feature_calculator and trading_context.market_data:
                # Clé de cache basée sur les données principales
                cache_key = f"features_{trading_context.price}_{trading_context.timestamp.timestamp()}"
                features_result = self._get_cached_result(cache_key)
                
                if features_result is None:
                    try:
                        features_result = self.feature_calculator.calculate_all_features(
                            market_data=trading_context.market_data,
                            structure_data=trading_context.structure_data,
                            sierra_patterns=trading_context.sierra_patterns,
                            es_nq_data=trading_context.es_nq_data
                        )
                        self._cache_result(cache_key, features_result)
                    except Exception as e:
                        logger.warning(f"Erreur calcul features: {e}")
            
            # === 3. EXPLORATION DES PATTERNS (OPTIMISÉE) ===
            pattern_signals = []
            now_ts = trading_context.timestamp
            
            # Filtrage précoce par régime marché pour éviter les calculs inutiles
            eligible_strategies = self._filter_strategies_by_regime(regime_data)
            
            for strat in eligible_strategies:
                # Cooldown par stratégie
                if (now_ts - self.last_fire_ts[strat.name]).total_seconds() < self.fire_cooldown_sec:
                    continue
                    
                try:
                    # Créer un contexte standardisé pour les patterns
                    pattern_ctx = self._create_pattern_context(trading_context, features_result)
                    sig = strat.generate(pattern_ctx)
                except Exception as e:
                    logger.exception("Pattern %s crashed: %s", strat.name, e)
                    continue
                    
                if not sig:
                    continue
                    
                # Scoring contextuel
                score = self._score_pattern_signal(sig, regime_data, features_result)
                if score is not None:
                    pattern_signals.append((score, sig))
                    
                # Arrêt précoce si on a déjà un signal de haute qualité
                if pattern_signals and max(pattern_signals, key=lambda x: x[0])[0] > 0.85:
                    break
            
            # === 4. DÉDOUBLONNAGE PAR FAMILLE ===
            if pattern_signals:
                pattern_signals = deduplicate_by_family(pattern_signals)
                logger.debug(f"Dédoublonnage: {len(pattern_signals)} signaux uniques par famille")
            
            # === 5. SÉLECTION DU MEILLEUR PATTERN ===
            best_pattern = None
            best_score = 0.0
            
            if pattern_signals:
                best_score, best_signal = max(pattern_signals, key=lambda x: x[0])
                if best_signal.get("confidence", 0) >= self.min_pattern_confidence:
                    best_pattern = best_signal
            
            # === 6. VALIDATION FINALE ===
            final_decision = self._make_final_decision(best_pattern, features_result, trading_context)
            
            # === 7. PERFORMANCE TRACKING ===
            processing_time = (time.perf_counter() - start_time) * 1000
            self._update_performance_metrics(processing_time, final_decision)
            
            # === 8. CRÉATION RÉSULTAT ===
            result = StrategySelectionResult(
                timestamp=trading_context.timestamp,
                selected_strategy=StrategyType.PATTERN_STRATEGY if best_pattern else StrategyType.WAIT_STRATEGY,
                selection_reason=f"Pattern {best_pattern['strategy']}" if best_pattern else "Aucun pattern valide",
                selection_confidence=best_score if best_pattern else 0.0,
                market_regime=getattr(regime_data, 'regime', {}).get('name', 'UNKNOWN') if regime_data else 'UNKNOWN',
                regime_confidence=getattr(regime_data, 'regime_confidence', 0.0) if regime_data else 0.0,
                signal_generated=best_pattern is not None,
                pattern_signal=PatternSignal(**best_pattern) if best_pattern else None,
                final_decision=final_decision,
                confluence_score=getattr(features_result, 'confluence_score', 0.0) if features_result else 0.0,
                total_processing_time_ms=processing_time,
                patterns_considered=[s["strategy"] for _, s in pattern_signals],
                best_pattern=(best_pattern or {}).get("strategy"),
                pattern_signals_count=len(pattern_signals)
            )
            
            # Enregistrer le fire time si signal validé
            if best_pattern and final_decision == SignalDecision.EXECUTE_SIGNAL:
                self.last_fire_ts[best_pattern["strategy"]] = now_ts
            
            # Ajout historique
            self.signal_history.append(result)
            
            # Logging
            logger.info(f"Analyse intégrée terminée: {len(pattern_signals)} patterns → {final_decision.value} "
                       f"(meilleur: {result.best_pattern}, {processing_time:.1f}ms)")
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur analyse intégrée: {e}")
            return StrategySelectionResult(
                timestamp=trading_context.timestamp,
                selected_strategy=StrategyType.WAIT_STRATEGY,
                selection_reason=f"Erreur: {e}",
                selection_confidence=0.0,
                final_decision=SignalDecision.REGIME_UNCLEAR,
                total_processing_time_ms=(time.perf_counter() - start_time) * 1000
            )

    def _filter_strategies_by_regime(self, regime_data) -> List:
        """Filtre les stratégies selon le régime marché pour optimiser les performances"""
        if not regime_data or not hasattr(regime_data, 'regime'):
            return self.pattern_strategies  # Toutes les stratégies si régime inconnu
        
        regime_name = getattr(regime_data.regime, 'value', 'UNKNOWN')
        
        # Mapping régime → stratégies prioritaires
        regime_strategy_map = {
            'STRONG_TREND_BULLISH': [
                'DealerFlipBreakout', 'LiquiditySweepReversal', 'StackedImbalanceContinuation',
                'GammaPinReversion', 'VwapBandSqueezeBreak'
            ],
            'STRONG_TREND_BEARISH': [
                'DealerFlipBreakout', 'LiquiditySweepReversal', 'StackedImbalanceContinuation',
                'GammaPinReversion', 'VwapBandSqueezeBreak'
            ],
            'RANGE_BULLISH_BIAS': [
                'GammaPinReversion', 'CvdDivergenceTrap', 'ProfileGapFill',
                'ZeroDTEWallSweepReversal', 'GexClusterMeanRevert'
            ],
            'RANGE_BEARISH_BIAS': [
                'GammaPinReversion', 'CvdDivergenceTrap', 'ProfileGapFill',
                'ZeroDTEWallSweepReversal', 'GexClusterMeanRevert'
            ],
            'RANGE_NEUTRAL': [
                'GammaPinReversion', 'CvdDivergenceTrap', 'ProfileGapFill',
                'IcebergTrackerFollow', 'EsNqLeadLagMirror'
            ]
        }
        
        # Stratégies prioritaires pour ce régime
        priority_strategies = regime_strategy_map.get(regime_name, [])
        
        # Filtrer les stratégies
        filtered_strategies = []
        for strat in self.pattern_strategies:
            if strat.name in priority_strategies:
                filtered_strategies.append(strat)
        
        # Si aucune stratégie prioritaire, prendre les 6 premières
        if not filtered_strategies:
            filtered_strategies = self.pattern_strategies[:6]
        
        return filtered_strategies

    def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Récupère un résultat du cache s'il est encore valide"""
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                self.performance.cache_hits += 1
                return result
        
        self.performance.cache_misses += 1
        return None

    def _cache_result(self, cache_key: str, result: Any) -> None:
        """Met en cache un résultat avec timestamp"""
        self.cache[cache_key] = (result, time.time())
        
        # Nettoyage périodique du cache
        if time.time() - self.last_cache_cleanup > 10.0:  # Toutes les 10 secondes
            self._cleanup_cache()
            self.last_cache_cleanup = time.time()

    def _cleanup_cache(self) -> None:
        """Nettoie le cache des entrées expirées"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp > self.cache_ttl
        ]
        for key in expired_keys:
            del self.cache[key]

    def _create_pattern_context(self, trading_context: TradingContext, features_result: Optional[Any] = None) -> Dict[str, Any]:
        """Crée un contexte standardisé pour les pattern strategies."""
        ctx = {
            "price": {"last": trading_context.price},
            "atr": 2.0,
            "tick_size": trading_context.tick_size,
            "symbol": trading_context.symbol,
        }
        
        # Utiliser les données des features si disponibles
        if features_result:
            # VWAP data
            if hasattr(features_result, 'vwap_data'):
                ctx["vwap"] = features_result.vwap_data
            else:
                ctx["vwap"] = {
                    "vwap": trading_context.price,
                    "sd1_up": trading_context.price + 2.0,
                    "sd1_dn": trading_context.price - 2.0,
                    "sd2_up": trading_context.price + 6.0,
                    "sd2_dn": trading_context.price - 6.0,
                }
            
            # VVA data
            if hasattr(features_result, 'vva_data'):
                ctx["vva"] = features_result.vva_data
            else:
                ctx["vva"] = {
                    "vpoc": trading_context.price,
                    "vah": trading_context.price + 5.0,
                    "val": trading_context.price - 5.0,
                    "lvn_low": trading_context.price - 2.0,
                    "lvn_high": trading_context.price + 2.0,
                }
            
            # MenthorQ data
            if hasattr(features_result, 'menthorq'):
                ctx["menthorq"] = features_result.menthorq
            else:
                ctx["menthorq"] = {
                    "nearest_wall": {"type": "CALL", "price": trading_context.price + 10.0, "dist_ticks": 40},
                    "gamma_flip": False
                }
            
            # Orderflow data
            if hasattr(features_result, 'orderflow'):
                ctx["orderflow"] = features_result.orderflow
            else:
                ctx["orderflow"] = {
                    "delta_burst": False,
                    "delta_flip": False,
                    "cvd_divergence": False,
                    "stacked_imbalance": {"side": "BUY", "rows": 0},
                    "absorption": None,
                    "iceberg": None,
                }
        else:
            # Fallback avec données par défaut
            ctx.update({
                "vwap": {
                    "vwap": trading_context.price,
                    "sd1_up": trading_context.price + 2.0,
                    "sd1_dn": trading_context.price - 2.0,
                    "sd2_up": trading_context.price + 6.0,
                    "sd2_dn": trading_context.price - 6.0,
                },
                "vva": {
                    "vpoc": trading_context.price,
                    "vah": trading_context.price + 5.0,
                    "val": trading_context.price - 5.0,
                    "lvn_low": trading_context.price - 2.0,
                    "lvn_high": trading_context.price + 2.0,
                },
                "menthorq": {
                    "nearest_wall": {"type": "CALL", "price": trading_context.price + 10.0, "dist_ticks": 40},
                    "gamma_flip": False
                },
                "orderflow": {
                    "delta_burst": False,
                    "delta_flip": False,
                    "cvd_divergence": False,
                    "stacked_imbalance": {"side": "BUY", "rows": 0},
                    "absorption": None,
                    "iceberg": None,
                }
            })
        
        # Autres données
        ctx.update({
            "quotes": {"speed_up": False},
            "correlation": {"es_nq": 0.9, "leader": "ES"},
            "vix": {"last": 20.0, "rising": False},
            "session": {"label": "OTHER", "time_ok": True},
            "basedata": {"last_wick_ticks": 0}
        })
        
        return ctx

    def _score_pattern_signal(self, sig: Dict[str, Any], regime_data: Optional[Any] = None, features_result: Optional[Any] = None) -> Optional[float]:
        """Score contextuel d'un signal pattern avec règles de priorité avancées."""
        conf = float(sig.get("confidence", 0.0))
        if conf <= 0.0:
            return None

        score = conf
        strategy_name = sig.get("strategy", "")
        
        # === RÈGLES DE PRIORITÉ SPÉCIFIQUES ===
        
        # +0.06 si gamma_flip=True et stratégie breakout
        if (strategy_name in ("gamma_wall_break_and_go", "dealer_flip_breakout") and 
            features_result and hasattr(features_result, 'menthorq') and 
            features_result.menthorq.get("gamma_flip", False)):
            score += 0.06
            
        # +0.04 si regime=RANGE et stratégie mean_revert
        if (strategy_name in ("call_put_channel_rotation", "gex_cluster_mean_revert", "hvl_magnet_fade") and
            regime_data and hasattr(regime_data, 'regime')):
            regime_name = getattr(regime_data, 'regime', {}).get('name', '') if hasattr(regime_data, 'regime') else str(regime_data)
            if "RANGE" in regime_name:
                score += 0.04
                
        # +0.03 si session=OPEN et stratégie breakout
        if (strategy_name == "gamma_wall_break_and_go" and 
            features_result and hasattr(features_result, 'session') and
            features_result.session.get("label") == "OPEN"):
            score += 0.03
            
        # -0.05 si mur opposé < 6 ticks (sauf GammaWall...)
        if (strategy_name not in ("gamma_wall_break_and_go",) and 
            features_result and hasattr(features_result, 'menthorq')):
            menthorq = features_result.menthorq
            wall = menthorq.get("nearest_wall", {})
            if wall and wall.get("dist_ticks", 999) < 6:
                # Vérifier si le mur est opposé à la direction du trade
                side = sig.get("side", "")
                wall_type = wall.get("type", "")
                if ((side == "LONG" and wall_type == "PUT") or 
                    (side == "SHORT" and wall_type == "CALL")):
                    score -= 0.05
                    
        # -0.03 si VIX rising et signal contrtrend en trend day
        if (features_result and hasattr(features_result, 'vix') and 
            features_result.vix.get("rising", False) and
            regime_data and hasattr(regime_data, 'regime')):
            regime_name = getattr(regime_data, 'regime', {}).get('name', '') if hasattr(regime_data, 'regime') else str(regime_data)
            if "TREND" in regime_name and strategy_name in ("gamma_pin_reversion", "hvl_magnet_fade", "profile_gap_fill"):
                score -= 0.03

        # === BOOSTS GÉNÉRIQUES ===
        
        # Boost pour les stratégies de breakout en tendance
        if strategy_name in ("dealer_flip_breakout", "vwap_band_squeeze_break", "gamma_wall_break_and_go"):
            score += 0.05
            
        # Boost pour les stratégies de reversion en range
        if strategy_name in ("gamma_pin_reversion", "profile_gap_fill", "hvl_magnet_fade"):
            score += 0.03
            
        # Boost pour les stratégies d'ouverture
        if strategy_name == "opening_drive_fail":
            score += 0.02
            
        # Boost pour les stratégies MenthorQ spécialisées
        if strategy_name in ("zero_dte_wall_sweep_reversal", "d1_extreme_trap", "gex_cluster_mean_revert"):
            score += 0.02

        return max(0.0, min(1.0, score))

    def _make_final_decision(self, best_pattern: Optional[Dict[str, Any]], features_result: Optional[Any], trading_context: TradingContext) -> SignalDecision:
        """Décision finale de validation."""
        
        if not best_pattern:
            return SignalDecision.WAIT_BETTER_SETUP
            
        # Validation confiance minimale
        if best_pattern.get("confidence", 0) < self.min_pattern_confidence:
            return SignalDecision.REJECT_SIGNAL
            
        # Validation confluence si disponible
        if features_result and hasattr(features_result, 'confluence_score'):
            if features_result.confluence_score < self.min_confluence_for_execution:
                return SignalDecision.REJECT_SIGNAL
            
        # Validation risque
        entry = best_pattern.get("entry", 0)
        stop = best_pattern.get("stop", 0)
        risk_ticks = abs(entry - stop) / trading_context.tick_size
        
        if risk_ticks > 20:  # Risque trop élevé
            return SignalDecision.REJECT_SIGNAL
            
        # Validation R:R
        targets = best_pattern.get("targets", [])
        if targets:
            max_target = max(targets)
            reward_ticks = abs(max_target - entry) / trading_context.tick_size
            if reward_ticks / max(1, risk_ticks) < 1.2:  # R:R minimum 1.2
                return SignalDecision.REJECT_SIGNAL
        
        return SignalDecision.EXECUTE_SIGNAL

    def _update_performance_metrics(self, processing_time: float, decision: SignalDecision):
        """Mise à jour des métriques de performance."""
        self.performance.total_analyses += 1
        
        # Rolling average
        count = self.performance.total_analyses
        prev_time = self.performance.avg_processing_time
        self.performance.avg_processing_time = ((prev_time * (count - 1)) + processing_time) / count
        
        # Compteurs
        if decision == SignalDecision.EXECUTE_SIGNAL:
            self.performance.pattern_signals += 1
        elif decision == SignalDecision.REJECT_SIGNAL:
            self.performance.rejected_signals += 1

    def get_system_status(self) -> Dict[str, Any]:
        """État complet du système intégré."""
        # Séparer les stratégies par type
        original_strategies = [s.name for s in self.pattern_strategies[:10]]
        menthorq_strategies = [s.name for s in self.pattern_strategies[10:]]
        
        return {
            'total_analyses': self.performance.total_analyses,
            'pattern_signals': self.performance.pattern_signals,
            'rejected_signals': self.performance.rejected_signals,
            'avg_processing_time_ms': round(self.performance.avg_processing_time, 2),
            'pattern_strategies_count': len(self.pattern_strategies),
            'original_strategies_count': len(original_strategies),
            'menthorq_strategies_count': len(menthorq_strategies),
            'active_strategies': [s.name for s in self.pattern_strategies],
            'original_strategies': original_strategies,
            'menthorq_strategies': menthorq_strategies,
            'cooldown_sec': self.fire_cooldown_sec,
            'min_confidence': self.min_pattern_confidence,
            'deduplication_enabled': True,
            'family_tags_count': len(FAMILY_TAGS),
            'system_components': {
                'regime_detector': self.regime_detector is not None,
                'feature_calculator': self.feature_calculator is not None,
            }
        }

# === FACTORY FUNCTIONS ===

def create_integrated_strategy_selector(config: Optional[Dict[str, Any]] = None) -> IntegratedStrategySelector:
    """Factory function pour integrated strategy selector"""
    return IntegratedStrategySelector(config)

# === TESTING ===

def test_integrated_strategy_selector():
    """Test complet du integrated strategy selector"""
    logger.info("TEST INTEGRATED STRATEGY SELECTOR")
    print("=" * 50)
    
    # Création selector
    config = {
        'pattern_fire_cooldown_sec': 30,
        'min_pattern_confidence': 0.55,
        'min_confluence_execution': 0.65,
    }
    
    selector = create_integrated_strategy_selector(config)
    
    # Test avec contexte simple
    trading_context = TradingContext(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        price=4500.0,
        volume=2000.0
    )
    
    # Analyse
    result = selector.analyze_and_select(trading_context)
    
    print(f"Résultat: {result.selected_strategy.value}")
    print(f"Régime: {result.market_regime}")
    print(f"Patterns considérés: {len(result.patterns_considered)}")
    print(f"Meilleur pattern: {result.best_pattern}")
    print(f"Décision: {result.final_decision.value}")
    print(f"Confluence: {result.confluence_score:.2f}")
    print(f"Temps: {result.total_processing_time_ms:.1f}ms")
    
    # Status
    status = selector.get_system_status()
    print(f"\nStatus système:")
    for key, value in status.items():
        if key != 'active_strategies':
            print(f"  • {key}: {value}")
    
    logger.info("TEST INTEGRATED STRATEGY SELECTOR TERMINÉ")
    return True

if __name__ == "__main__":
    test_integrated_strategy_selector()
