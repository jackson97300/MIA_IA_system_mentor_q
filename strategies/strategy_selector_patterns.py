#!/usr/bin/env python3
"""
Strategy Selector avec intégration des 10 nouvelles stratégies patterns
Version simplifiée qui évite les dépendances complexes et se concentre sur l'intégration des patterns.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque

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

logger = get_logger(__name__)

# === ENUMS ===

class StrategyType(Enum):
    """Types de stratégies disponibles"""
    TREND_STRATEGY = "trend_strategy"
    RANGE_STRATEGY = "range_strategy"
    PATTERN_STRATEGY = "pattern_strategy"  # === NEW ===
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
    
    # Signal data
    signal_generated: bool = False
    pattern_signal: Optional[PatternSignal] = None
    final_decision: SignalDecision = SignalDecision.WAIT_BETTER_SETUP
    
    # Performance metrics
    total_processing_time_ms: float = 0.0
    
    # === Pattern strategies tracking ===
    patterns_considered: List[str] = field(default_factory=list)
    best_pattern: Optional[str] = None
    pattern_signals_count: int = 0

@dataclass
class TradingContext:
    """Contexte trading simplifié"""
    timestamp: pd.Timestamp
    symbol: str = "ES"
    price: float = 4500.0
    volume: float = 1000.0
    tick_size: float = 0.25

@dataclass
class SystemPerformance:
    """Performance système avec patterns"""
    total_analyses: int = 0
    pattern_signals: int = 0
    rejected_signals: int = 0
    avg_processing_time: float = 0.0

# === MAIN STRATEGY SELECTOR ===

class PatternStrategySelector:
    """
    Strategy Selector spécialisé pour les pattern strategies.
    
    Responsabilités :
    1. Gestion du registry des 10 pattern strategies
    2. Cooldown et anti-sur-sollicitation
    3. Scoring contextuel des signaux
    4. Sélection du meilleur pattern
    5. Validation finale
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation du selector patterns"""
        self.config = config or {}
        
        # === Registry des pattern strategies ===
        self.pattern_strategies = [
            GammaPinReversion(), DealerFlipBreakout(), LiquiditySweepReversal(),
            StackedImbalanceContinuation(), IcebergTrackerFollow(),
            CvdDivergenceTrap(), OpeningDriveFail(),
            EsNqLeadLagMirror(), VwapBandSqueezeBreak(), ProfileGapFill(),
        ]
        
        # Anti-sur-sollicitation par stratégie
        self.last_fire_ts = defaultdict(lambda: pd.Timestamp(0))
        self.fire_cooldown_sec = self.config.get("pattern_fire_cooldown_sec", 60)
        
        # Paramètres
        self.min_pattern_confidence = self.config.get('min_pattern_confidence', 0.60)
        self.min_dist_ticks_wall = self.config.get('min_dist_ticks_wall', 6)
        self.max_risk_budget = self.config.get('max_risk_budget', 1.0)
        
        # Performance tracking
        self.performance = SystemPerformance()
        self.signal_history: deque = deque(maxlen=200)
        
        logger.info(f"PatternStrategySelector initialisé avec {len(self.pattern_strategies)} strategies")

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
            # === 1. EXPLORATION DES PATTERNS ===
            pattern_signals = []
            now_ts = trading_context.timestamp
            
            for strat in self.pattern_strategies:
                # Cooldown par stratégie
                if (now_ts - self.last_fire_ts[strat.name]).total_seconds() < self.fire_cooldown_sec:
                    continue
                    
                try:
                    # Créer un contexte standardisé pour les patterns
                    pattern_ctx = self._create_pattern_context(trading_context)
                    sig = strat.generate(pattern_ctx)
                except Exception as e:
                    logger.exception("Pattern %s crashed: %s", strat.name, e)
                    continue
                    
                if not sig:
                    continue
                    
                # Scoring contextuel
                score = self._score_pattern_signal(sig, trading_context)
                if score is not None:
                    pattern_signals.append((score, sig))
            
            # === 2. SÉLECTION DU MEILLEUR PATTERN ===
            best_pattern = None
            best_score = 0.0
            
            if pattern_signals:
                best_score, best_signal = max(pattern_signals, key=lambda x: x[0])
                if best_signal.get("confidence", 0) >= self.min_pattern_confidence:
                    best_pattern = best_signal
            
            # === 3. VALIDATION FINALE ===
            final_decision = self._make_final_decision(best_pattern, trading_context)
            
            # === 4. PERFORMANCE TRACKING ===
            processing_time = (time.perf_counter() - start_time) * 1000
            self._update_performance_metrics(processing_time, final_decision)
            
            # === 5. CRÉATION RÉSULTAT ===
            result = StrategySelectionResult(
                timestamp=trading_context.timestamp,
                selected_strategy=StrategyType.PATTERN_STRATEGY if best_pattern else StrategyType.WAIT_STRATEGY,
                selection_reason=f"Pattern {best_pattern['strategy']}" if best_pattern else "Aucun pattern valide",
                selection_confidence=best_score if best_pattern else 0.0,
                signal_generated=best_pattern is not None,
                pattern_signal=PatternSignal(**best_pattern) if best_pattern else None,
                final_decision=final_decision,
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
            logger.info(f"Analyse patterns terminée: {len(pattern_signals)} patterns → {final_decision.value} "
                       f"(meilleur: {result.best_pattern}, {processing_time:.1f}ms)")
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur analyse patterns: {e}")
            return StrategySelectionResult(
                timestamp=trading_context.timestamp,
                selected_strategy=StrategyType.WAIT_STRATEGY,
                selection_reason=f"Erreur: {e}",
                selection_confidence=0.0,
                final_decision=SignalDecision.REGIME_UNCLEAR,
                total_processing_time_ms=(time.perf_counter() - start_time) * 1000
            )

    def _create_pattern_context(self, trading_context: TradingContext) -> Dict[str, Any]:
        """Crée un contexte standardisé pour les pattern strategies."""
        return {
            "price": {"last": trading_context.price},
            "atr": 2.0,
            "tick_size": trading_context.tick_size,
            "symbol": trading_context.symbol,
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
            },
            "quotes": {"speed_up": False},
            "correlation": {"es_nq": 0.9, "leader": "ES"},
            "vix": {"last": 20.0, "rising": False},
            "session": {"label": "OTHER", "time_ok": True},
            "basedata": {"last_wick_ticks": 0}
        }

    def _score_pattern_signal(self, sig: Dict[str, Any], trading_context: TradingContext) -> Optional[float]:
        """Score contextuel d'un signal pattern."""
        conf = float(sig.get("confidence", 0.0))
        if conf <= 0.0:
            return None

        score = conf

        # Boost selon le type de stratégie
        strategy_name = sig.get("strategy", "")
        
        # Boost pour les stratégies de breakout en tendance
        if strategy_name in ("dealer_flip_breakout", "vwap_band_squeeze_break"):
            score += 0.05
            
        # Boost pour les stratégies de reversion en range
        if strategy_name in ("gamma_pin_reversion", "profile_gap_fill"):
            score += 0.03
            
        # Boost pour les stratégies d'ouverture
        if strategy_name == "opening_drive_fail":
            score += 0.02

        return max(0.0, min(1.0, score))

    def _make_final_decision(self, best_pattern: Optional[Dict[str, Any]], trading_context: TradingContext) -> SignalDecision:
        """Décision finale de validation."""
        
        if not best_pattern:
            return SignalDecision.WAIT_BETTER_SETUP
            
        # Validation confiance minimale
        if best_pattern.get("confidence", 0) < self.min_pattern_confidence:
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
        """État complet du système patterns."""
        return {
            'total_analyses': self.performance.total_analyses,
            'pattern_signals': self.performance.pattern_signals,
            'rejected_signals': self.performance.rejected_signals,
            'avg_processing_time_ms': round(self.performance.avg_processing_time, 2),
            'pattern_strategies_count': len(self.pattern_strategies),
            'active_strategies': [s.name for s in self.pattern_strategies],
            'cooldown_sec': self.fire_cooldown_sec,
            'min_confidence': self.min_pattern_confidence
        }

# === FACTORY FUNCTIONS ===

def create_pattern_strategy_selector(config: Optional[Dict[str, Any]] = None) -> PatternStrategySelector:
    """Factory function pour pattern strategy selector"""
    return PatternStrategySelector(config)

# === TESTING ===

def test_pattern_strategy_selector():
    """Test complet du pattern strategy selector"""
    logger.info("TEST PATTERN STRATEGY SELECTOR")
    print("=" * 50)
    
    # Création selector
    config = {
        'pattern_fire_cooldown_sec': 30,
        'min_pattern_confidence': 0.55,
    }
    
    selector = create_pattern_strategy_selector(config)
    
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
    print(f"Patterns considérés: {len(result.patterns_considered)}")
    print(f"Meilleur pattern: {result.best_pattern}")
    print(f"Décision: {result.final_decision.value}")
    print(f"Temps: {result.total_processing_time_ms:.1f}ms")
    
    # Status
    status = selector.get_system_status()
    print(f"\nStatus système:")
    for key, value in status.items():
        print(f"  • {key}: {value}")
    
    logger.info("TEST PATTERN STRATEGY SELECTOR TERMINÉ")
    return True

if __name__ == "__main__":
    test_pattern_strategy_selector()
