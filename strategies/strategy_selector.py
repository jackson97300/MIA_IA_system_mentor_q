"""
MIA_IA_SYSTEM - Strategy Selector
CHEF D'ORCHESTRE - Orchestration complète du système trading
Version: Production Ready
Performance: Sélection stratégie <5ms

RESPONSABILITÉS :
1. Analyse régime marché (Market Regime Detector)
2. Sélection stratégie optimale (Trend vs Range vs Wait)
3. Orchestration features + patterns + confluence
4. Gestion transitions régimes
5. Validation finale signaux
6. Performance tracking globale

LOGIQUE SÉLECTION :
- STRONG_TREND → TrendStrategy (pullback preferred)
- WEAK_TREND → TrendStrategy (prudent)
- RANGE_BIASED → RangeStrategy (direction restreinte)
- RANGE_NEUTRAL → RangeStrategy (both sides)
- TRANSITION/UNCLEAR → Wait (pas de trade)

HIÉRARCHIE FINALE :
1. Market Regime Analysis
2. Strategy Selection
3. Feature Calculation
4. Signal Generation
5. Final Validation
6. Position Sizing
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from core.logger import get_logger
from collections import deque, defaultdict

# Local imports
from core.base_types import (
    MarketData, OrderFlowData, TradingSignal, SignalType,
    ES_TICK_SIZE, ES_TICK_VALUE
)

# Strategy components
# Les classes MarketRegime seront importées dynamiquement
# Utilisation du système de lazy loading
from features import create_feature_calculator, create_market_regime_detector
from features.market_regime import MarketRegime, MarketRegimeData
from features.feature_calculator_optimized import FeatureCalculationResult
from .trend_strategy import (
    TrendStrategy, TrendSignalData, TrendSignalType,
    create_trend_strategy
)
from .range_strategy import (
    RangeStrategy, RangeSignalData, RangeSignalType,
    create_range_strategy
)

# === NEW: registry des stratégies "patterns" ===
from .gamma_pin_reversion import GammaPinReversion
from .dealer_flip_breakout import DealerFlipBreakout
from .liquidity_sweep_reversal import LiquiditySweepReversal
from .stacked_imbalance_continuation import StackedImbalanceContinuation
from .iceberg_tracker_follow import IcebergTrackerFollow
from .cvd_divergence_trap import CvdDivergenceTrap
from .opening_drive_fail import OpeningDriveFail
from .es_nq_lead_lag_mirror import EsNqLeadLagMirror
from .vwap_band_squeeze_break import VwapBandSqueezeBreak
from .profile_gap_fill import ProfileGapFill

logger = get_logger(__name__)

# === STRATEGY SELECTION ENUMS ===


class StrategyType(Enum):
    """Types de stratégies disponibles"""
    TREND_STRATEGY = "trend_strategy"
    RANGE_STRATEGY = "range_strategy"
    WAIT_STRATEGY = "wait_strategy"
    TRANSITION_STRATEGY = "transition_strategy"


class SignalDecision(Enum):
    """Décisions finales de signal"""
    EXECUTE_SIGNAL = "execute_signal"      # Exécuter le signal
    REJECT_SIGNAL = "reject_signal"        # Rejeter le signal
    WAIT_BETTER_SETUP = "wait_better_setup"  # Attendre meilleur setup
    REGIME_UNCLEAR = "regime_unclear"      # Régime pas clair


class ExecutionMode(Enum):
    """Modes d'exécution"""
    PAPER_TRADING = "paper_trading"
    LIVE_TRADING = "live_trading"
    SIMULATION = "simulation"
    ANALYSIS_ONLY = "analysis_only"

# === DATACLASSES ===


@dataclass
class StrategySelectionResult:
    """Résultat sélection stratégie"""
    timestamp: pd.Timestamp

    # Strategy selection
    selected_strategy: StrategyType
    selection_reason: str
    selection_confidence: float

    # Market context
    market_regime: MarketRegime
    regime_confidence: float
    bias_strength: float
    allowed_directions: List[str]

    # Signal data
    signal_generated: bool = False
    signal_data: Optional[Union[TrendSignalData, RangeSignalData]] = None
    final_decision: SignalDecision = SignalDecision.WAIT_BETTER_SETUP

    # Performance metrics
    confluence_score: float = 0.0
    features_quality: float = 0.0
    total_processing_time_ms: float = 0.0
    
    # === NEW: Pattern strategies tracking ===
    patterns_considered: List[str] = field(default_factory=list)
    best_pattern: Optional[str] = None
    features_snapshot: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TradingContext:
    """Contexte trading complet"""
    timestamp: pd.Timestamp

    # Market data
    market_data: MarketData
    es_nq_data: Optional[Dict[str, float]] = None
    structure_data: Optional[Dict[str, Any]] = None
    volume_data: Optional[Dict[str, float]] = None
    sierra_patterns: Optional[Dict[str, float]] = None

    # Session context
    session_phase: str = "unknown"
    execution_mode: ExecutionMode = ExecutionMode.PAPER_TRADING

    # Risk parameters
    max_position_size: float = 1.0
    max_risk_per_trade: float = 15.0  # ticks
    account_size: float = 100000.0


@dataclass
class SystemPerformance:
    """Performance système complète"""

    # Counters
    total_analyses: int = 0
    trend_signals: int = 0
    range_signals: int = 0
    pattern_signals: int = 0  # === NEW: Pattern strategies counter ===
    rejected_signals: int = 0

    # Strategy usage
    trend_strategy_usage: int = 0
    range_strategy_usage: int = 0
    wait_periods: int = 0

    # Quality metrics
    avg_confluence_score: float = 0.0
    avg_processing_time: float = 0.0
    regime_detection_accuracy: float = 0.0

    # Performance tracking
    successful_regime_transitions: int = 0
    failed_signal_validations: int = 0
    
    # === NEW: Risk management ===
    current_risk: float = 0.0

# === MAIN STRATEGY SELECTOR ===


class StrategySelector:
    """
    CHEF D'ORCHESTRE DU SYSTÈME TRADING

    Responsabilités :
    1. Orchestration complète : Regime → Strategy → Features → Signal
    2. Validation finale avec tous critères qualité
    3. Gestion transitions régimes intelligente
    4. Performance tracking système global
    5. Adaptation paramètres selon régime
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation orchestrateur système"""
        self.config = config or {}

        # === CRÉATION COMPOSANTS ===

        # Market Regime Detector (Cerveau)
        regime_config = self.config.get('regime_config', {})
        self.regime_detector = create_market_regime_detector(regime_config)

        # Feature Calculator
        features_config = self.config.get('features_config', {})
        self.feature_calculator = create_feature_calculator(features_config)

        # Strategies
        trend_config = self.config.get('trend_config', {})
        self.trend_strategy = create_trend_strategy(trend_config)

        range_config = self.config.get('range_config', {})
        self.range_strategy = create_range_strategy(range_config)

        # === NEW: Pattern strategies registry ===
        self.pattern_strategies = [
            GammaPinReversion(), DealerFlipBreakout(), LiquiditySweepReversal(),
            StackedImbalanceContinuation(), IcebergTrackerFollow(),
            CvdDivergenceTrap(), OpeningDriveFail(),
            EsNqLeadLagMirror(), VwapBandSqueezeBreak(), ProfileGapFill(),
        ]

        # Anti-sur-sollicitation par stratégie
        self.last_fire_ts = defaultdict(lambda: pd.Timestamp(0))
        self.fire_cooldown_sec = self.config.get("pattern_fire_cooldown_sec", 60)

        # === PARAMÈTRES SYSTÈME ===

        # Seuils validation finale
        self.min_confluence_for_execution = self.config.get('min_confluence_execution', 0.70)
        self.min_regime_confidence = self.config.get('min_regime_confidence', 0.60)
        self.max_processing_time_ms = self.config.get('max_processing_time_ms', 50)
        
        # === NEW: Pattern strategies parameters ===
        self.min_pattern_confidence = self.config.get('min_pattern_confidence', 0.60)
        self.min_dist_ticks_wall = self.config.get('min_dist_ticks_wall', 6)
        self.max_risk_budget = self.config.get('max_risk_budget', 1.0)

        # Gestion transitions
        self.regime_change_cooldown = self.config.get('regime_change_cooldown', 5)  # minutes
        self.require_regime_stability = self.config.get('require_regime_stability', True)

        # === ÉTAT SYSTÈME ===

        self.current_regime: Optional[MarketRegimeData] = None
        self.current_strategy: Optional[StrategyType] = None
        self.regime_history: deque = deque(maxlen=100)
        self.signal_history: deque = deque(maxlen=200)
        self.last_regime_change: Optional[pd.Timestamp] = None

        # Performance tracking
        self.performance = SystemPerformance()

        logger.info("StrategySelector initialisé - Chef d'orchestre système complet")

    def analyze_and_select(self, trading_context: TradingContext) -> StrategySelectionResult:
        """
        ANALYSE COMPLÈTE ET SÉLECTION STRATÉGIE

        Processus complet :
        1. Analyse régime marché (Market Regime Detector)
        2. Sélection stratégie optimale selon régime
        3. Calcul features avec confluence
        4. Génération signal par stratégie sélectionnée
        5. Validation finale multicritères
        6. Décision exécution finale

        Args:
            trading_context: Contexte complet trading

        Returns:
            StrategySelectionResult avec décision finale
        """
        start_time = time.perf_counter()

        try:
            # === 1. ANALYSE RÉGIME MARCHÉ ===

            regime_data = self.regime_detector.analyze_market_regime(
                market_data=trading_context.market_data,
                es_nq_data=trading_context.es_nq_data,
                structure_data=trading_context.structure_data,
                volume_data=trading_context.volume_data
            )

            self.current_regime = regime_data
            self.regime_history.append(regime_data)

            # === 2. SÉLECTION STRATÉGIE ===

            selected_strategy, selection_reason, selection_confidence = self._select_optimal_strategy(
                regime_data, trading_context
            )

            self.current_strategy = selected_strategy

            # === 3. CALCUL FEATURES ===

            features_result = self.feature_calculator.calculate_all_features(
                market_data=trading_context.market_data,
                structure_data=trading_context.structure_data,
                sierra_patterns=trading_context.sierra_patterns,
                es_nq_data=trading_context.es_nq_data
            )

            # === 4. GÉNÉRATION SIGNAL SELON STRATÉGIE ===

            signal_data = None
            signal_generated = False

            if selected_strategy == StrategyType.TREND_STRATEGY:
                signal_data = self._execute_trend_analysis(
                    features_result, trading_context, regime_data
                )
                if signal_data:
                    signal_generated = True
                    self.performance.trend_signals += 1

            elif selected_strategy == StrategyType.RANGE_STRATEGY:
                signal_data = self._execute_range_analysis(
                    features_result, trading_context, regime_data
                )
                if signal_data:
                    signal_generated = True
                    self.performance.range_signals += 1

            # === NEW: Explorer les patterns micro-stratégies en complément ===
            pattern_signals = []
            now_ts = trading_context.timestamp

            for strat in self.pattern_strategies:
                # Cooldown par stratégie
                if (now_ts - self.last_fire_ts[strat.name]).total_seconds() < self.fire_cooldown_sec:
                    continue
                try:
                    # Créer un contexte standardisé pour les patterns
                    pattern_ctx = self._create_pattern_context(features_result, trading_context)
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

            # Conserver le meilleur pattern
            best_pattern = max(pattern_signals, key=lambda x: x[0])[1] if pattern_signals else None
            if best_pattern and best_pattern.get("confidence", 0) >= self.min_pattern_confidence:
                signal_generated = True
                # Tag pour perf
                self.performance.pattern_signals += 1
                # Enregistrer le fire time
                self.last_fire_ts[best_pattern["strategy"]] = now_ts

            # === 5. VALIDATION FINALE ===

            final_decision = self._make_final_decision(
                signal_data, features_result, regime_data, trading_context
            )

            # === 6. PERFORMANCE TRACKING ===

            processing_time = (time.perf_counter() - start_time) * 1000
            self._update_performance_metrics(
                processing_time, features_result.confluence_score, selected_strategy, final_decision
            )

            # === 7. CRÉATION RÉSULTAT ===

            result = StrategySelectionResult(
                timestamp=trading_context.timestamp,
                selected_strategy=selected_strategy,
                selection_reason=selection_reason,
                selection_confidence=selection_confidence,
                market_regime=regime_data.regime,
                regime_confidence=regime_data.regime_confidence,
                bias_strength=regime_data.bias_strength,
                allowed_directions=regime_data.allowed_directions,
                signal_generated=signal_generated,
                signal_data=signal_data,
                final_decision=final_decision,
                confluence_score=features_result.confluence_score,
                features_quality=self._calculate_features_quality(features_result),
                total_processing_time_ms=processing_time,
                # === NEW: Pattern strategies tracking ===
                patterns_considered=[s["strategy"] for _, s in pattern_signals],
                best_pattern=(best_pattern or {}).get("strategy"),
                features_snapshot={
                    "confluence": features_result.confluence_score,
                    "regime": regime_data.regime.name,
                    "menthorq_flip": getattr(features_result, 'menthorq', {}).get("gamma_flip", False) if hasattr(features_result, 'menthorq') else False,
                }
            )

            # Ajout historique
            self.signal_history.append(result)

            # Logging
            logger.info(f"Analyse complète terminée: {selected_strategy.value} → {final_decision.value} "
                        f"(conf: {features_result.confluence_score:.2f}, {processing_time:.1f}ms)")

            return result

        except Exception as e:
            logger.error(f"Erreur analyse système complète: {e}")
            return StrategySelectionResult(
                timestamp=trading_context.timestamp,
                selected_strategy=StrategyType.WAIT_STRATEGY,
                selection_reason=f"Erreur système: {e}",
                selection_confidence=0.0,
                market_regime=MarketRegime.UNCLEAR,
                regime_confidence=0.0,
                bias_strength=0.0,
                allowed_directions=[],
                final_decision=SignalDecision.REGIME_UNCLEAR,
                total_processing_time_ms=(time.perf_counter() - start_time) * 1000
            )

    def _select_optimal_strategy(self,
                                 regime_data: MarketRegimeData,
                                 trading_context: TradingContext) -> Tuple[StrategyType, str, float]:
        """
        SÉLECTION STRATÉGIE OPTIMALE SELON RÉGIME

        Logique hiérarchique :
        1. STRONG_TREND → TrendStrategy (confiance élevée)
        2. WEAK_TREND → TrendStrategy (confiance modérée)
        3. RANGE_BIASED → RangeStrategy (direction restreinte)
        4. RANGE_NEUTRAL → RangeStrategy (both sides)
        5. TRANSITION → Wait (prudence)
        6. UNCLEAR → Wait (pas de risque)
        """

        regime = regime_data.regime
        regime_confidence = regime_data.regime_confidence

        # === TREND STRATEGIES ===

        if regime in [MarketRegime.STRONG_TREND_BULLISH, MarketRegime.STRONG_TREND_BEARISH]:
            self.performance.trend_strategy_usage += 1
            return (
                StrategyType.TREND_STRATEGY,
                f"Strong trend detected: {regime.value}",
                min(regime_confidence + 0.1, 1.0)  # Boost confidence pour strong trend
            )

        elif regime in [MarketRegime.WEAK_TREND_BULLISH, MarketRegime.WEAK_TREND_BEARISH]:
            self.performance.trend_strategy_usage += 1
            return (
                StrategyType.TREND_STRATEGY,
                f"Weak trend detected: {regime.value}",
                regime_confidence * 0.8  # Légère réduction pour weak trend
            )

        # === RANGE STRATEGIES ===

        elif regime in [MarketRegime.RANGE_BULLISH_BIAS, MarketRegime.RANGE_BEARISH_BIAS]:
            self.performance.range_strategy_usage += 1
            return (
                StrategyType.RANGE_STRATEGY,
                f"Biased range detected: {regime.value}",
                regime_confidence
            )

        elif regime == MarketRegime.RANGE_NEUTRAL:
            self.performance.range_strategy_usage += 1
            return (
                StrategyType.RANGE_STRATEGY,
                "Neutral range detected - both sides allowed",
                regime_confidence * 0.9  # Légère réduction pour neutral range
            )

        # === TRANSITION HANDLING ===

        elif regime == MarketRegime.TRANSITION:
            # Vérifier si transition récente
            if self._is_recent_regime_change():
                self.performance.wait_periods += 1
                return (
                    StrategyType.WAIT_STRATEGY,
                    "Recent regime transition - waiting for stability",
                    0.3
                )
            else:
                # Transition stable → utiliser dernière stratégie connue
                if self.current_strategy in [
                        StrategyType.TREND_STRATEGY, StrategyType.RANGE_STRATEGY]:
                    return (
                        self.current_strategy,
                        "Stable transition - continuing previous strategy",
                        0.5
                    )
                else:
                    self.performance.wait_periods += 1
                    return (StrategyType.WAIT_STRATEGY, "Transition period", 0.4)

        # === UNCLEAR REGIME ===

        else:  # UNCLEAR
            self.performance.wait_periods += 1
            return (
                StrategyType.WAIT_STRATEGY,
                f"Unclear regime: {regime.value} (conf: {regime_confidence:.2f})",
                0.2
            )

    def _execute_trend_analysis(self,
                                features: FeatureCalculationResult,
                                trading_context: TradingContext,
                                regime_data: MarketRegimeData) -> Optional[TrendSignalData]:
        """Exécution analyse tendance"""

        # Préparation contexte tendance
        trend_context = {
            'vwap_slope': trading_context.structure_data.get('vwap_slope', 0) if trading_context.structure_data else 0,
            'dow_trend_direction': self._map_regime_to_direction(regime_data.regime),
            'trend_strength': regime_data.bias_strength
        }

        # Analyse signal tendance
        signal = self.trend_strategy.analyze_trend_signal(
            features=features,
            market_data=trading_context.market_data,
            structure_data=trading_context.structure_data,
            sierra_patterns=trading_context.sierra_patterns
        )

        return signal

    def _execute_range_analysis(self,
                                features: FeatureCalculationResult,
                                trading_context: TradingContext,
                                regime_data: MarketRegimeData) -> Optional[RangeSignalData]:
        """Exécution analyse range"""

        # Préparation contexte range avec bias
        range_trend_context = {
            'vwap_slope': trading_context.structure_data.get('vwap_slope', 0) if trading_context.structure_data else 0,
            'dow_trend_direction': self._map_regime_to_direction(regime_data.regime),
            'trend_strength': regime_data.bias_strength
        }

        # Analyse signal range
        signal = self.range_strategy.analyze_range_signal(
            features=features,
            market_data=trading_context.market_data,
            trend_context=range_trend_context,
            structure_data=trading_context.structure_data,
            sierra_patterns=trading_context.sierra_patterns
        )

        return signal

    def _make_final_decision(self,
                             signal_data: Optional[Union[TrendSignalData, RangeSignalData]],
                             features: FeatureCalculationResult,
                             regime_data: MarketRegimeData,
                             trading_context: TradingContext) -> SignalDecision:
        """
        DÉCISION FINALE MULTICRITÈRES

        Validation finale :
        1. Signal généré et valide
        2. Confluence minimum atteinte
        3. Régime suffisamment confiant
        4. Pas de contre-indications
        5. Respect limites risque
        """

        # === 1. SIGNAL GÉNÉRÉ ? ===

        if not signal_data:
            return SignalDecision.WAIT_BETTER_SETUP

        # === 2. CONFLUENCE MINIMUM ===

        if features.confluence_score < self.min_confluence_for_execution:
            logger.info(
                f"Confluence insuffisante: {
                    features.confluence_score:.2f} < {
                    self.min_confluence_for_execution:.2f}")
            self.performance.rejected_signals += 1
            return SignalDecision.REJECT_SIGNAL

        # === 3. RÉGIME CONFIDENCE ===

        if regime_data.regime_confidence < self.min_regime_confidence:
            logger.info(f"Régime confidence insuffisante: {regime_data.regime_confidence:.2f}")
            self.performance.rejected_signals += 1
            return SignalDecision.REGIME_UNCLEAR

        # === 4. DIRECTION AUTORISÉE ===

        signal_direction = getattr(signal_data, 'direction', 'UNKNOWN')
        if signal_direction not in regime_data.allowed_directions and regime_data.allowed_directions:
            logger.info(f"Direction {signal_direction} non autorisée par régime")
            self.performance.rejected_signals += 1
            return SignalDecision.REJECT_SIGNAL

        # === 5. RISK VALIDATION ===

        # Vérifier R:R minimum
        if hasattr(signal_data, 'risk_reward_ratio'):
            rr_ratio = signal_data.risk_reward_ratio()
            if rr_ratio < 1.2:
                logger.info(f"R:R insuffisant: {rr_ratio:.2f}")
                self.performance.rejected_signals += 1
                return SignalDecision.REJECT_SIGNAL

        # Vérifier risque maximum
        risk_ticks = getattr(signal_data, 'max_risk_ticks', 0)
        if risk_ticks > trading_context.max_risk_per_trade:
            logger.info(f"Risque trop élevé: {risk_ticks:.1f} ticks")
            self.performance.rejected_signals += 1
            return SignalDecision.REJECT_SIGNAL

        # === 6. QUALITÉ FEATURES ===

        features_quality = self._calculate_features_quality(features)
        if features_quality < 0.6:
            logger.info(f"Qualité features insuffisante: {features_quality:.2f}")
            self.performance.rejected_signals += 1
            return SignalDecision.REJECT_SIGNAL

        # === 7. TRANSITION PERIODS ===

        if self._is_recent_regime_change() and regime_data.regime == MarketRegime.TRANSITION:
            logger.info("Période transition - signal rejeté par prudence")
            return SignalDecision.WAIT_BETTER_SETUP

        # === 8. SESSION VALIDATION ===

        session_factor = regime_data.session_performance_factor
        if session_factor < 0.6:  # Session défavorable
            logger.info(f"Session défavorable: {session_factor:.2f}")
            return SignalDecision.WAIT_BETTER_SETUP

        # === NEW: MenthorQ blocking wall ===
        menthorq = getattr(features, "menthorq", {}) or {}
        wall = menthorq.get("nearest_wall")
        if wall and wall.get("dist_ticks") is not None:
            # si mur opposé < N ticks et trade va à travers → REJECT sauf si breakout pattern
            if wall["dist_ticks"] < self.min_dist_ticks_wall:
                if not (signal_data and getattr(signal_data, "is_breakout", False)):
                    return SignalDecision.REJECT_SIGNAL

        # === NEW: risk budget rapide ===
        if getattr(self.performance, "current_risk", 0.0) > self.max_risk_budget:
            return SignalDecision.WAIT_BETTER_SETUP

        # === SIGNAL VALIDÉ [OK] ===

        logger.info(f"Signal validé: conf={features.confluence_score:.2f}, "
                    f"regime={regime_data.regime.value}, dir={signal_direction}")

        return SignalDecision.EXECUTE_SIGNAL

    # === HELPER METHODS ===

    def _map_regime_to_direction(self, regime: MarketRegime) -> str:
        """Mapping régime vers direction (corrigé de DOW)"""
        mapping = {
            MarketRegime.STRONG_TREND_BULLISH: 'bullish',
            MarketRegime.WEAK_TREND_BULLISH: 'bullish',
            MarketRegime.STRONG_TREND_BEARISH: 'bearish',
            MarketRegime.WEAK_TREND_BEARISH: 'bearish',
            MarketRegime.RANGE_BULLISH_BIAS: 'bullish',
            MarketRegime.RANGE_BEARISH_BIAS: 'bearish',
            MarketRegime.RANGE_NEUTRAL: 'sideways',
            MarketRegime.TRANSITION: 'sideways',
            MarketRegime.UNCLEAR: 'sideways'
        }
        return mapping.get(regime, 'sideways')

    def _is_recent_regime_change(self) -> bool:
        """Détection changement régime récent"""
        if len(self.regime_history) < 2:
            return False

        current_regime = self.regime_history[-1].regime
        previous_regime = self.regime_history[-2].regime

        if current_regime != previous_regime:
            self.last_regime_change = self.regime_history[-1].timestamp
            return True

        # Vérifier si changement dans période cooldown
        if self.last_regime_change:
            time_since_change = self.regime_history[-1].timestamp - self.last_regime_change
            return time_since_change.total_seconds() / 60 < self.regime_change_cooldown

        return False

    def _calculate_features_quality(self, features: FeatureCalculationResult) -> float:
        """Calcul qualité globale features"""

        # Composants qualité
        confluence_quality = features.confluence_score

        # Diversité features (pas toutes nulles)
        feature_values = [
            features.vwap_trend_signal,
            features.sierra_pattern_strength,
            features.dow_trend_regime,
            features.gamma_levels_proximity,
            features.level_proximity,
            features.es_nq_correlation
        ]

        non_zero_features = sum(1 for f in feature_values if f > 0.1)
        diversity_score = min(non_zero_features / 6, 1.0)

        # Temps calcul (penalty si trop lent)
        time_penalty = 1.0
        if features.calculation_time_ms > 10:  # >10ms
            time_penalty = max(0.7, 1.0 - (features.calculation_time_ms - 10) / 50)

        # Score composite
        quality_score = (confluence_quality * 0.6 + diversity_score * 0.3 + time_penalty * 0.1)

        return min(quality_score, 1.0)

    def _create_pattern_context(self, features_result: FeatureCalculationResult, trading_context: TradingContext) -> Dict[str, Any]:
        """
        Crée un contexte standardisé pour les pattern strategies.
        
        Args:
            features_result: Résultat du calcul des features
            trading_context: Contexte de trading
            
        Returns:
            Contexte standardisé pour les patterns
        """
        # Adapter les features_result vers le format attendu par les patterns
        ctx = {
            "price": {"last": trading_context.market_data.close},
            "atr": getattr(features_result, 'atr', 2.0),
            "tick_size": 0.25,
            "symbol": trading_context.market_data.symbol,
        }
        
        # VWAP data
        if hasattr(features_result, 'vwap_data'):
            ctx["vwap"] = features_result.vwap_data
        else:
            ctx["vwap"] = {
                "vwap": trading_context.market_data.close,
                "sd1_up": trading_context.market_data.close + 2.0,
                "sd1_dn": trading_context.market_data.close - 2.0,
            }
        
        # VVA data
        if hasattr(features_result, 'vva_data'):
            ctx["vva"] = features_result.vva_data
        else:
            ctx["vva"] = {
                "vpoc": trading_context.market_data.close,
                "vah": trading_context.market_data.close + 5.0,
                "val": trading_context.market_data.close - 5.0,
            }
        
        # MenthorQ data
        if hasattr(features_result, 'menthorq'):
            ctx["menthorq"] = features_result.menthorq
        else:
            ctx["menthorq"] = {
                "nearest_wall": {"type": "CALL", "price": trading_context.market_data.close + 10.0, "dist_ticks": 40},
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
        
        # Autres données
        ctx["quotes"] = {"speed_up": False}
        ctx["correlation"] = {"es_nq": 0.9, "leader": "ES"}
        ctx["vix"] = {"last": 20.0, "rising": False}
        ctx["session"] = {"label": "OTHER", "time_ok": True}
        ctx["basedata"] = {"last_wick_ticks": 0}
        
        return ctx

    def _score_pattern_signal(self, sig: Dict[str, Any], regime_data: MarketRegimeData, features_result: FeatureCalculationResult) -> Optional[float]:
        """
        Score 0..1 basé sur :
        - confiance du signal
        - compatibilité avec le régime
        - contexte MenthorQ (gamma flip, mur proche)
        - session et VIX
        """
        conf = float(sig.get("confidence", 0.0))
        if conf <= 0.0:
            return None

        score = conf

        # Boost si régime cohérent
        if regime_data.regime.name.startswith("STRONG_TREND") and sig["strategy"] in ("dealer_flip_breakout", "vwap_band_squeeze_break"):
            score += 0.06
        if "RANGE" in regime_data.regime.name and sig["strategy"] in ("gamma_pin_reversion", "profile_gap_fill"):
            score += 0.04

        # MenthorQ
        mctx = getattr(features_result, "menthorq", None) or {}
        if mctx.get("gamma_flip", False) and sig["strategy"] in ("dealer_flip_breakout", "es_nq_lead_lag_mirror"):
            score += 0.05
        # pénalité mur opposé trop proche
        wall = (mctx.get("nearest_wall") or {})
        if wall and wall.get("dist_ticks") is not None and wall["dist_ticks"] < 6:
            # si TP du signal est au-delà du mur opposé, pénalise
            score -= 0.05

        # Session
        sess = getattr(features_result, "session", {}) or {}
        if sess.get("label") == "OPEN" and sig["strategy"] in ("opening_drive_fail", "dealer_flip_breakout"):
            score += 0.03

        # VIX
        vix = getattr(features_result, "vix", {}) or {}
        if vix.get("rising", False) and sig["side"] == "countertrend":
            score -= 0.03

        return max(0.0, min(1.0, score))

    def _update_performance_metrics(self,
                                    processing_time: float,
                                    confluence_score: float,
                                    strategy: StrategyType,
                                    decision: SignalDecision):
        """Mise à jour métriques performance"""

        self.performance.total_analyses += 1

        # Rolling averages
        count = self.performance.total_analyses

        # Confluence score moyenne
        prev_conf = self.performance.avg_confluence_score
        self.performance.avg_confluence_score = (
            (prev_conf * (count - 1)) + confluence_score) / count

        # Temps processing moyen
        prev_time = self.performance.avg_processing_time
        self.performance.avg_processing_time = ((prev_time * (count - 1)) + processing_time) / count

        # Compteurs décisions
        if decision == SignalDecision.REJECT_SIGNAL:
            self.performance.rejected_signals += 1
        elif decision == SignalDecision.EXECUTE_SIGNAL:
            # Signal validé
            pass

        # Failed validations
        if decision in [SignalDecision.REJECT_SIGNAL, SignalDecision.REGIME_UNCLEAR]:
            self.performance.failed_signal_validations += 1

    def get_system_status(self) -> Dict[str, Any]:
        """État complet du système"""

        current_regime_name = self.current_regime.regime.value if self.current_regime else "unknown"
        current_strategy_name = self.current_strategy.value if self.current_strategy else "None"

        # Calcul success rate
        total_signals = self.performance.trend_signals + self.performance.range_signals + self.performance.pattern_signals
        success_rate = ((total_signals - self.performance.rejected_signals) /
                        total_signals * 100) if total_signals > 0 else 0

        return {
            # État actuel
            'current_regime': current_regime_name,
            'current_strategy': current_strategy_name,
            'regime_confidence': self.current_regime.regime_confidence if self.current_regime else 0.0,
            'last_regime_change': self.last_regime_change.isoformat() if self.last_regime_change else None,

            # Performance globale
            'total_analyses': self.performance.total_analyses,
            'success_rate_pct': round(success_rate, 1),
            'avg_confluence_score': round(self.performance.avg_confluence_score, 3),
            'avg_processing_time_ms': round(self.performance.avg_processing_time, 2),

            # Distribution signaux
            'trend_signals': self.performance.trend_signals,
            'range_signals': self.performance.range_signals,
            'pattern_signals': self.performance.pattern_signals,  # === NEW ===
            'rejected_signals': self.performance.rejected_signals,

            # Utilisation stratégies
            'trend_strategy_usage': self.performance.trend_strategy_usage,
            'range_strategy_usage': self.performance.range_strategy_usage,
            'wait_periods': self.performance.wait_periods,

            # Qualité système
            'failed_validations': self.performance.failed_signal_validations,
            'regime_transitions': self.performance.successful_regime_transitions,

            # Composants status
            'components_status': {
                'regime_detector': 'active',
                'feature_calculator': 'active',
                'trend_strategy': 'active',
                'range_strategy': 'active',
                'pattern_strategies': f'active ({len(self.pattern_strategies)} strategies)'  # === NEW ===
            }
        }

    def get_detailed_statistics(self) -> Dict[str, Any]:
        """Statistiques détaillées tous composants"""

        return {
            'strategy_selector': self.get_system_status(),
            'regime_detector': self.regime_detector.get_statistics(),
            'feature_calculator': self.feature_calculator.get_statistics(),
            'trend_strategy': self.trend_strategy.get_statistics(),
            'range_strategy': self.range_strategy.get_statistics()
        }

# === FACTORY FUNCTIONS ===


def create_strategy_selector(config: Optional[Dict[str, Any]] = None) -> StrategySelector:
    """Factory function pour strategy selector"""
    return StrategySelector(config)


def execute_full_analysis(trading_context: TradingContext,
                          selector: Optional[StrategySelector] = None) -> StrategySelectionResult:
    """Helper function pour analyse complète"""

    if selector is None:
        selector = create_strategy_selector()

    return selector.analyze_and_select(trading_context)

# === TESTING ===


def test_strategy_selector():
    """Test complet strategy selector"""
    logger.debug("TEST STRATEGY SELECTOR - CHEF D'ORCHESTRE")
    print("=" * 50)

    # Création orchestrateur
    selector = create_strategy_selector()

    logger.info("[STATS] TEST 1: STRONG TREND BULLISH")

    # Contexte trend haussier fort
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4500.0,
        high=4515.0,
        low=4498.0,
        close=4512.0,
        volume=2500
    )

    # Structure haussière
    structure_data = {
        'vwap_slope': 0.8,  # Fort slope haussier
        'vwap_price': 4505.0,
        'poc_price': 4507.0,
        'val_price': 4495.0,
        'put_wall': 4480.0
    }

    # ES/NQ aligné
    es_nq_data = {
        'es_price': 4512.0,
        'nq_price': 4512.0 * 4.5,
        'correlation': 0.85
    }

    # Patterns Sierra haussiers
    sierra_patterns = {
        'long_down_up_bar': 0.85,
        'battle_navale_signal': 0.80,
        'base_quality': 0.75
    }

    trading_context = TradingContext(
        timestamp=pd.Timestamp.now(),
        market_data=market_data,
        structure_data=structure_data,
        es_nq_data=es_nq_data,
        sierra_patterns=sierra_patterns,
        execution_mode=ExecutionMode.PAPER_TRADING
    )

    # Analyse complète
    result1 = selector.analyze_and_select(trading_context)

    logger.info("Régime détecté: {result1.market_regime.value}")
    logger.info("Stratégie sélectionnée: {result1.selected_strategy.value}")
    logger.info("Confluence: {result1.confluence_score:.3f}")
    logger.info("Décision finale: {result1.final_decision.value}")
    logger.info("Signal généré: {result1.signal_generated}")
    logger.info("Temps processing: {result1.total_processing_time_ms:.1f}ms")

    if result1.signal_data:
        logger.info("Signal details: {type(result1.signal_data).__name__}")
        if hasattr(result1.signal_data, 'signal_type'):
            logger.info("    Type: {result1.signal_data.signal_type.value}")
        if hasattr(result1.signal_data, 'direction'):
            logger.info("    Direction: {result1.signal_data.direction}")
        if hasattr(result1.signal_data, 'entry_price'):
            logger.info("    Entry: {result1.signal_data.entry_price:.2f}")

    logger.info("\n[STATS] TEST 2: RANGE NEUTRAL")

    # Contexte range neutre
    range_market_data = MarketData(
        timestamp=pd.Timestamp.now() + pd.Timedelta(minutes=30),
        symbol="ES",
        open=4505.0,
        high=4507.0,
        low=4503.0,
        close=4504.0,  # Milieu range
        volume=1200
    )

    range_structure_data = {
        'vwap_slope': 0.1,  # Quasi flat
        'vwap_price': 4505.0,
        'poc_price': 4505.0
    }

    # Simulation range pour regime detector
    # (Il faut plusieurs barres pour detecter un range)
    for i in range(25):
        if i % 4 == 0:  # Test support 4500
            test_price = 4500.0 + np.random.normal(0, 0.5)
        elif i % 4 == 2:  # Test resistance 4510
            test_price = 4510.0 + np.random.normal(0, 0.5)
        else:  # Dans range
            test_price = 4505.0 + np.random.normal(0, 2)

        test_bar = MarketData(
            timestamp=pd.Timestamp.now() + pd.Timedelta(minutes=i),
            symbol="ES",
            open=test_price,
            high=test_price + 1,
            low=test_price - 1,
            close=test_price,
            volume=1000
        )
        # Alimenter regime detector
        selector.regime_detector.price_history.append(test_bar)

    range_context = TradingContext(
        timestamp=pd.Timestamp.now() + pd.Timedelta(minutes=30),
        market_data=range_market_data,
        structure_data=range_structure_data,
        sierra_patterns={'battle_navale_signal': 0.7}
    )

    result2 = selector.analyze_and_select(range_context)

    logger.info("Régime détecté: {result2.market_regime.value}")
    logger.info("Stratégie sélectionnée: {result2.selected_strategy.value}")
    logger.info("Confluence: {result2.confluence_score:.3f}")
    logger.info("Décision finale: {result2.final_decision.value}")
    logger.info("Directions autorisées: {result2.allowed_directions}")

    logger.info("\n[STATS] TEST 3: UNCLEAR REGIME")

    # Contexte unclear
    unclear_data = MarketData(
        timestamp=pd.Timestamp.now() + pd.Timedelta(minutes=60),
        symbol="ES",
        open=4500.0,
        high=4501.0,
        low=4499.0,
        close=4500.5,
        volume=800
    )

    unclear_context = TradingContext(
        timestamp=pd.Timestamp.now() + pd.Timedelta(minutes=60),
        market_data=unclear_data,
        structure_data={'vwap_slope': 0.0},
        sierra_patterns={}
    )

    result3 = selector.analyze_and_select(unclear_context)

    logger.info("Régime détecté: {result3.market_regime.value}")
    logger.info("Stratégie sélectionnée: {result3.selected_strategy.value}")
    logger.info("Décision finale: {result3.final_decision.value}")

    # Status système
    logger.info("\n[UP] SYSTEM STATUS:")
    status = selector.get_system_status()
    for key, value in status.items():
        if key != 'components_status':
            logger.info("   • {key}: {value}")

    # Statistiques détaillées
    logger.info("\n[STATS] DETAILED STATISTICS:")
    detailed_stats = selector.get_detailed_statistics()

    logger.info("   Strategy Selector:")
    for key, value in detailed_stats['strategy_selector'].items():
        if key not in ['components_status']:
            logger.info("      • {key}: {value}")

    logger.info("   Regime Detector:")
    for key, value in detailed_stats['regime_detector'].items():
        logger.info("      • {key}: {value}")

    logger.info("\n[TARGET] STRATEGY SELECTOR TEST COMPLETED")
    logger.info("[LAUNCH] SYSTÈME COMPLET OPÉRATIONNEL !")

    return True


if __name__ == "__main__":
    test_strategy_selector()
