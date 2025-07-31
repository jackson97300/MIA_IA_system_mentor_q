"""
MIA_IA_SYSTEM - Strategies Package
Orchestration complète des stratégies trading
Version: Production Ready
Performance: Système intégré trend + range + régime

ARCHITECTURE FINALE :
├── StrategySelector     - CHEF D'ORCHESTRE SYSTÈME COMPLET 🎯
├── TrendStrategy        - Dow Theory + Pullback preference
├── RangeStrategy        - Standards + Direction bias  
├── MarketRegimeDetector - Cerveau système (bias determination)
├── StrategyOrchestrator - Coordination intelligente
└── SignalAggregator     - Fusion signaux + validation finale

WORKFLOW COMPLET :
1. StrategySelector → orchestration globale système
2. MarketRegime détermine régime + bias
3. Strategy appropriée génère signaux  
4. Orchestrator valide + priorise
5. Aggregator fusionne + décision finale
6. Risk management appliqué selon qualité

POINT D'ENTRÉE PRINCIPAL : execute_full_analysis()

HIÉRARCHIE SIGNAUX FINALE :
- PREMIUM (85-100%) : Pullback + confluence maximale
- STRONG (70-84%)   : Signaux confirmés  
- WEAK (60-69%)     : Size réduite
- NO_TRADE (0-59%)  : Attendre
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

# Local imports  
from core.base_types import (
    MarketData, OrderFlowData, TradingSignal, SignalType,
    MarketRegime, SignalStrength, ES_TICK_SIZE
)
from features.feature_calculator import (
    FeatureCalculationResult, FeatureCalculator, SignalQuality
)
from .trend_strategy import (
    TrendStrategy, TrendSignalData, TrendSignalType, analyze_trend_opportunity
)
from .range_strategy import (
    RangeStrategy, RangeSignalData, RangeSignalType, analyze_range_opportunity
)
from .strategy_selector import (
    StrategySelector, StrategySelectionResult, TradingContext, SystemPerformance,
    StrategyType, SignalDecision, ExecutionMode, create_strategy_selector, execute_full_analysis
)
from features.market_regime import (
    MarketRegimeDetector, MarketRegimeData, MarketRegime as RegimeType,
    analyze_market_regime
)

logger = logging.getLogger(__name__)

# === ORCHESTRATION ENUMS ===

class FinalSignalType(Enum):
    """Types signaux finaux après orchestration"""
    PREMIUM_LONG_TREND = "premium_long_trend"        # Top tier trend
    PREMIUM_LONG_PULLBACK = "premium_long_pullback"  # Top tier pullback
    PREMIUM_LONG_RANGE = "premium_long_range"        # Top tier range
    STRONG_LONG = "strong_long"                      # Signal long fort
    WEAK_LONG = "weak_long"                          # Signal long faible
    
    PREMIUM_SHORT_TREND = "premium_short_trend"      # Top tier short trend
    PREMIUM_SHORT_RANGE = "premium_short_range"      # Top tier short range
    STRONG_SHORT = "strong_short"                    # Signal short fort
    WEAK_SHORT = "weak_short"                        # Signal short faible
    
    EXIT_SPECIAL = "exit_special"                    # Exit spécial (2 vertes)
    EXIT_STRUCTURE = "exit_structure"                # Exit structure cassée
    EXIT_TIME = "exit_time"                          # Exit temps
    
    NO_TRADE = "no_trade"                           # Pas de signal

class StrategyPriority(Enum):
    """Priorité stratégies selon régime"""
    TREND_ONLY = "trend_only"        # Trend fort : trend strategy seulement
    TREND_PREFERRED = "trend_preferred"  # Trend faible : trend préféré
    RANGE_ONLY = "range_only"        # Range : range strategy seulement  
    BOTH_ALLOWED = "both_allowed"    # Transition : both strategies
    WAIT_MODE = "wait_mode"          # Unclear : attendre

# === DATACLASSES ===

@dataclass
class StrategySignal:
    """Signal unifié entre strategies"""
    timestamp: pd.Timestamp
    strategy_source: str  # trend, range
    signal_type: str
    direction: str
    confidence: float
    
    # Entry data
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    
    # Quality metrics
    risk_reward_ratio: float
    confluence_score: float
    pattern_quality: float
    
    # Context
    regime_compliance: bool
    bias_alignment: bool
    
    # Metadata
    reasoning: str
    sierra_patterns: Dict[str, float] = field(default_factory=dict)
    
    def calculate_signal_score(self) -> float:
        """Score global du signal"""
        score = (
            self.confidence * 0.4 +
            self.confluence_score * 0.3 +
            self.pattern_quality * 0.2 +
            min(self.risk_reward_ratio / 3.0, 1.0) * 0.1
        )
        
        # Bonus compliance
        if self.regime_compliance and self.bias_alignment:
            score += 0.1
        
        return min(score, 1.0)

@dataclass  
class FinalTradingSignal:
    """Signal final après orchestration"""
    timestamp: pd.Timestamp
    signal_type: FinalSignalType
    direction: str
    
    # Entry execution
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    
    # Quality assessment
    final_confidence: float
    signal_score: float
    risk_reward_ratio: float
    
    # Source tracking
    primary_strategy: str
    contributing_strategies: List[str]
    regime_context: str
    
    # Risk management
    max_risk_dollars: float
    expected_pnl: float
    
    # Execution metadata
    reasoning: str
    execution_priority: int  # 1=immediate, 2=normal, 3=patient
    
    def is_executable(self) -> bool:
        """Signal prêt pour exécution"""
        return (
            self.signal_type != FinalSignalType.NO_TRADE and
            self.final_confidence >= 0.60 and
            self.risk_reward_ratio >= 1.2 and
            self.position_size > 0
        )

# === STRATEGY ORCHESTRATOR ===

class StrategyOrchestrator:
    """
    Orchestrateur stratégies - Coordination intelligente
    
    Responsabilités :
    1. Analyse régime marché (bias determination)
    2. Sélection stratégie appropriée selon régime
    3. Validation signaux vs compliance régime
    4. Priorisation signaux multiples
    5. Génération signal final unifié
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation orchestrateur"""
        self.config = config or {}
        
        # Composants stratégies
        self.feature_calculator = FeatureCalculator()
        self.trend_strategy = TrendStrategy()
        self.range_strategy = RangeStrategy()
        self.regime_detector = MarketRegimeDetector()
        
        # Paramètres orchestration
        self.min_signal_confidence = self.config.get('min_signal_confidence', 0.60)
        self.regime_compliance_required = self.config.get('regime_compliance', True)
        self.allow_multiple_strategies = self.config.get('allow_multiple', False)
        
        # État système
        self.current_regime: Optional[MarketRegimeData] = None
        self.active_signals: List[StrategySignal] = []
        self.last_final_signal: Optional[FinalTradingSignal] = None
        
        # Performance tracking
        self.stats = {
            'signals_processed': 0,
            'trend_signals': 0,
            'range_signals': 0,
            'rejected_regime': 0,
            'rejected_quality': 0,
            'final_signals_generated': 0
        }
        
        logger.info("StrategyOrchestrator initialisé - Coordination complète")
    
    def analyze_trading_opportunity(self,
                                  market_data: MarketData,
                                  order_flow: Optional[OrderFlowData] = None,
                                  options_data: Optional[Dict[str, Any]] = None,
                                  structure_data: Optional[Dict[str, Any]] = None,
                                  es_nq_data: Optional[Dict[str, float]] = None,
                                  sierra_patterns: Optional[Dict[str, float]] = None) -> Optional[FinalTradingSignal]:
        """
        ANALYSE COMPLÈTE OPPORTUNITÉ TRADING
        
        Workflow complet :
        1. Calcul features avec confluence
        2. Détection régime marché + bias
        3. Sélection stratégie selon régime
        4. Génération signaux strategies
        5. Validation compliance régime
        6. Agrégation + priorisation
        7. Signal final unifié
        
        Returns:
            FinalTradingSignal prêt pour exécution ou None
        """
        start_time = time.perf_counter()
        
        try:
            # 1. CALCUL FEATURES AVEC CONFLUENCE
            features = self.feature_calculator.calculate_all_features(
                market_data=market_data,
                order_flow=order_flow,
                options_data=options_data,
                structure_data=structure_data,
                es_nq_data=es_nq_data,
                sierra_patterns=sierra_patterns
            )
            
            # 2. DÉTECTION RÉGIME MARCHÉ
            regime_data = self.regime_detector.analyze_market_regime(
                market_data=market_data,
                es_nq_data=es_nq_data,
                structure_data=structure_data
            )
            self.current_regime = regime_data
            
            # 3. SÉLECTION STRATÉGIE SELON RÉGIME
            strategy_priority = self._determine_strategy_priority(regime_data)
            
            if strategy_priority == StrategyPriority.WAIT_MODE:
                return None  # Pas de trading en mode wait
            
            # 4. GÉNÉRATION SIGNAUX STRATEGIES
            candidate_signals = self._generate_strategy_signals(
                features=features,
                market_data=market_data,
                regime_data=regime_data,
                strategy_priority=strategy_priority,
                structure_data=structure_data,
                sierra_patterns=sierra_patterns
            )
            
            # 5. VALIDATION COMPLIANCE RÉGIME
            validated_signals = self._validate_regime_compliance(
                candidate_signals, regime_data
            )
            
            if not validated_signals:
                return None  # Aucun signal valide
            
            # 6. AGRÉGATION + PRIORISATION
            final_signal = self._aggregate_and_prioritize_signals(
                validated_signals, regime_data, features
            )
            
            # 7. TRACKING PERFORMANCE
            self._update_stats(final_signal, regime_data)
            
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.info(f"Signal final généré en {execution_time:.2f}ms: "
                       f"{final_signal.signal_type.value if final_signal else 'NONE'}")
            
            self.last_final_signal = final_signal
            return final_signal
            
        except Exception as e:
            logger.error(f"Erreur orchestration trading: {e}")
            return None
    
    def _determine_strategy_priority(self, regime_data: MarketRegimeData) -> StrategyPriority:
        """DÉTERMINATION PRIORITÉ STRATÉGIE"""
        
        regime = regime_data.regime
        confidence = regime_data.regime_confidence
        
        # TRENDS FORTS - Trend strategy seulement
        if regime in [RegimeType.STRONG_TREND_BULLISH, RegimeType.STRONG_TREND_BEARISH]:
            return StrategyPriority.TREND_ONLY
        
        # TRENDS FAIBLES - Trend préféré
        elif regime in [RegimeType.WEAK_TREND_BULLISH, RegimeType.WEAK_TREND_BEARISH]:
            return StrategyPriority.TREND_PREFERRED
        
        # RANGES - Range strategy seulement
        elif regime in [RegimeType.RANGE_BULLISH_BIAS, RegimeType.RANGE_BEARISH_BIAS, RegimeType.RANGE_NEUTRAL]:
            return StrategyPriority.RANGE_ONLY
        
        # TRANSITION - Both strategies (si confidence suffisante)
        elif regime == RegimeType.TRANSITION and confidence >= 0.5:
            return StrategyPriority.BOTH_ALLOWED
        
        # UNCLEAR ou faible confidence - Attendre
        else:
            return StrategyPriority.WAIT_MODE
    
    def _generate_strategy_signals(self,
                                 features: FeatureCalculationResult,
                                 market_data: MarketData,
                                 regime_data: MarketRegimeData,
                                 strategy_priority: StrategyPriority,
                                 structure_data: Optional[Dict[str, Any]],
                                 sierra_patterns: Optional[Dict[str, float]]) -> List[StrategySignal]:
        """GÉNÉRATION SIGNAUX SELON STRATÉGIES AUTORISÉES"""
        
        candidate_signals = []
        
        # TREND STRATEGY
        if strategy_priority in [StrategyPriority.TREND_ONLY, StrategyPriority.TREND_PREFERRED, StrategyPriority.BOTH_ALLOWED]:
            
            trend_context = {
                'vwap_slope': regime_data.trend_analysis.vwap_slope if regime_data.trend_analysis else 0,
                'dow_trend_direction': self._get_dow_direction(regime_data),
                'trend_strength': regime_data.trend_analysis.trend_consistency if regime_data.trend_analysis else 0
            }
            
            trend_signal = self.trend_strategy.analyze_trend_signal(
                features=features,
                market_data=market_data,
                structure_data=structure_data,
                sierra_patterns=sierra_patterns
            )
            
            if trend_signal:
                unified_signal = self._convert_trend_signal(trend_signal, regime_data)
                candidate_signals.append(unified_signal)
                self.stats['trend_signals'] += 1
        
        # RANGE STRATEGY
        if strategy_priority in [StrategyPriority.RANGE_ONLY, StrategyPriority.BOTH_ALLOWED]:
            
            trend_context = {
                'vwap_slope': regime_data.trend_analysis.vwap_slope if regime_data.trend_analysis else 0,
                'dow_trend_direction': self._get_dow_direction(regime_data),
                'trend_strength': regime_data.trend_analysis.trend_consistency if regime_data.trend_analysis else 0
            }
            
            range_signal = self.range_strategy.analyze_range_signal(
                features=features,
                market_data=market_data,
                trend_context=trend_context,
                structure_data=structure_data,
                sierra_patterns=sierra_patterns
            )
            
            if range_signal:
                unified_signal = self._convert_range_signal(range_signal, regime_data)
                candidate_signals.append(unified_signal)
                self.stats['range_signals'] += 1
        
        self.stats['signals_processed'] += len(candidate_signals)
        return candidate_signals
    
    def _validate_regime_compliance(self,
                                  signals: List[StrategySignal],
                                  regime_data: MarketRegimeData) -> List[StrategySignal]:
        """VALIDATION COMPLIANCE RÉGIME"""
        
        validated_signals = []
        allowed_directions = regime_data.allowed_directions
        
        for signal in signals:
            # Validation direction autorisée
            if signal.direction not in allowed_directions:
                logger.info(f"Signal {signal.direction} rejeté - direction non autorisée {allowed_directions}")
                self.stats['rejected_regime'] += 1
                continue
            
            # Validation confidence minimum
            if signal.confidence < self.min_signal_confidence:
                logger.info(f"Signal rejeté - confidence {signal.confidence:.2f} < {self.min_signal_confidence}")
                self.stats['rejected_quality'] += 1
                continue
            
            # Validation bias alignment
            signal.regime_compliance = True
            signal.bias_alignment = True
            
            validated_signals.append(signal)
        
        return validated_signals
    
    def _aggregate_and_prioritize_signals(self,
                                        signals: List[StrategySignal],
                                        regime_data: MarketRegimeData,
                                        features: FeatureCalculationResult) -> Optional[FinalTradingSignal]:
        """AGRÉGATION ET PRIORISATION SIGNAUX"""
        
        if not signals:
            return None
        
        # Calcul scores globaux
        for signal in signals:
            signal.pattern_quality = signal.calculate_signal_score()
        
        # Tri par score décroissant
        signals.sort(key=lambda s: s.calculate_signal_score(), reverse=True)
        
        # Sélection signal principal
        primary_signal = signals[0]
        
        # Classification signal final selon qualité
        final_signal_type = self._classify_final_signal_type(
            primary_signal, regime_data
        )
        
        # Agrégation informations
        contributing_strategies = list(set([s.strategy_source for s in signals]))
        
        # Calcul position size finale
        final_position_size = self._calculate_final_position_size(
            primary_signal, regime_data, features
        )
        
        # Risk calculation
        risk_per_share = abs(primary_signal.entry_price - primary_signal.stop_loss)
        symbol_info = getattr(market_data, 'symbol', 'ES')
        tick_value = 1.25 if 'MES' in str(symbol_info) else 12.50
        
        max_risk_dollars = risk_per_share * final_position_size * tick_value
        expected_pnl = abs(primary_signal.take_profit - primary_signal.entry_price) * final_position_size * tick_value
        
        final_signal = FinalTradingSignal(
            timestamp=primary_signal.timestamp,
            signal_type=final_signal_type,
            direction=primary_signal.direction,
            entry_price=primary_signal.entry_price,
            stop_loss=primary_signal.stop_loss,
            take_profit=primary_signal.take_profit,
            position_size=final_position_size,
            final_confidence=primary_signal.confidence,
            signal_score=primary_signal.calculate_signal_score(),
            risk_reward_ratio=primary_signal.risk_reward_ratio,
            primary_strategy=primary_signal.strategy_source,
            contributing_strategies=contributing_strategies,
            regime_context=regime_data.regime.value,
            max_risk_dollars=max_risk_dollars,
            expected_pnl=expected_pnl,
            reasoning=primary_signal.reasoning,
            execution_priority=self._determine_execution_priority(primary_signal, regime_data)
        )
        
        self.stats['final_signals_generated'] += 1
        return final_signal
    
    def _classify_final_signal_type(self,
                                  signal: StrategySignal,
                                  regime_data: MarketRegimeData) -> FinalSignalType:
        """Classification type signal final"""
        
        direction = signal.direction
        strategy = signal.strategy_source
        score = signal.calculate_signal_score()
        
        # PREMIUM SIGNALS (85%+)
        if score >= 0.85:
            if strategy == "trend":
                if "pullback" in signal.signal_type.lower():
                    return FinalSignalType.PREMIUM_LONG_PULLBACK if direction == "LONG" else FinalSignalType.PREMIUM_SHORT_TREND
                else:
                    return FinalSignalType.PREMIUM_LONG_TREND if direction == "LONG" else FinalSignalType.PREMIUM_SHORT_TREND
            else:  # range
                return FinalSignalType.PREMIUM_LONG_RANGE if direction == "LONG" else FinalSignalType.PREMIUM_SHORT_RANGE
        
        # STRONG SIGNALS (70-84%)
        elif score >= 0.70:
            return FinalSignalType.STRONG_LONG if direction == "LONG" else FinalSignalType.STRONG_SHORT
        
        # WEAK SIGNALS (60-69%)
        elif score >= 0.60:
            return FinalSignalType.WEAK_LONG if direction == "LONG" else FinalSignalType.WEAK_SHORT
        
        # EXIT SIGNALS
        elif "exit" in signal.signal_type.lower():
            if "special" in signal.signal_type.lower():
                return FinalSignalType.EXIT_SPECIAL
            else:
                return FinalSignalType.EXIT_STRUCTURE
        
        return FinalSignalType.NO_TRADE
    
    def _calculate_final_position_size(self,
                                     signal: StrategySignal,
                                     regime_data: MarketRegimeData,
                                     features: FeatureCalculationResult) -> float:
        """Calcul taille position finale"""
        
        base_size = signal.position_size
        
        # Ajustement selon régime
        regime_multiplier = regime_data.position_sizing_multiplier
        
        # Ajustement selon qualité signal
        quality_multiplier = 1.0
        if features.signal_quality == SignalQuality.PREMIUM:
            quality_multiplier = 1.2
        elif features.signal_quality == SignalQuality.WEAK:
            quality_multiplier = 0.8
        
        # Ajustement selon confluence
        confluence_multiplier = 0.8 + (features.confluence_score * 0.4)  # 0.8 to 1.2
        
        final_size = base_size * regime_multiplier * quality_multiplier * confluence_multiplier
        
        # Limites sécurité
        final_size = max(0.5, min(3.0, final_size))
        
        return round(final_size, 1)
    
    def _determine_execution_priority(self,
                                    signal: StrategySignal,
                                    regime_data: MarketRegimeData) -> int:
        """Détermination priorité exécution"""
        
        score = signal.calculate_signal_score()
        
        # Priority 1: Immediate (premium signals)
        if score >= 0.85:
            return 1
        
        # Priority 2: Normal (strong signals)
        elif score >= 0.70:
            return 2
        
        # Priority 3: Patient (weak signals)
        else:
            return 3
    
    # === HELPER METHODS ===
    
    def _get_dow_direction(self, regime_data: MarketRegimeData) -> str:
        """Direction Dow depuis régime"""
        if regime_data.trend_analysis:
            hh_hl = regime_data.trend_analysis.higher_highs_count + regime_data.trend_analysis.higher_lows_count
            lh_ll = regime_data.trend_analysis.lower_highs_count + regime_data.trend_analysis.lower_lows_count
            
            if hh_hl > lh_ll:
                return "bullish"
            elif lh_ll > hh_hl:
                return "bearish"
        
        return "sideways"
    
    def _convert_trend_signal(self, trend_signal: TrendSignalData, regime_data: MarketRegimeData) -> StrategySignal:
        """Conversion signal trend vers format unifié"""
        
        return StrategySignal(
            timestamp=trend_signal.timestamp,
            strategy_source="trend",
            signal_type=trend_signal.signal_type.value,
            direction=trend_signal.direction.value if hasattr(trend_signal.direction, 'value') else str(trend_signal.direction),
            confidence=trend_signal.confluence_score,
            entry_price=trend_signal.entry_price,
            stop_loss=trend_signal.stop_loss,
            take_profit=trend_signal.take_profit,
            position_size=trend_signal.position_size,
            risk_reward_ratio=trend_signal.risk_reward_ratio(),
            confluence_score=trend_signal.confluence_score,
            pattern_quality=0.8,  # Default high for trend
            regime_compliance=True,
            bias_alignment=True,
            reasoning=trend_signal.entry_reason,
            sierra_patterns=trend_signal.sierra_patterns
        )
    
    def _convert_range_signal(self, range_signal: RangeSignalData, regime_data: MarketRegimeData) -> StrategySignal:
        """Conversion signal range vers format unifié"""
        
        return StrategySignal(
            timestamp=range_signal.timestamp,
            strategy_source="range",
            signal_type=range_signal.signal_type.value,
            direction=range_signal.direction,
            confidence=range_signal.confluence_score,
            entry_price=range_signal.entry_price,
            stop_loss=range_signal.stop_loss,
            take_profit=range_signal.take_profit,
            position_size=range_signal.position_size,
            risk_reward_ratio=range_signal.risk_reward_ratio(),
            confluence_score=range_signal.confluence_score,
            pattern_quality=0.7,  # Default good for range
            regime_compliance=range_signal.bias_compliance,
            bias_alignment=range_signal.bias_compliance,
            reasoning=range_signal.entry_reason,
            sierra_patterns=range_signal.sierra_patterns
        )
    
    def _update_stats(self, final_signal: Optional[FinalTradingSignal], regime_data: MarketRegimeData):
        """Mise à jour statistiques"""
        if final_signal:
            self.stats['final_signals_generated'] += 1
    
    def get_current_regime(self) -> Optional[MarketRegimeData]:
        """Régime marché actuel"""
        return self.current_regime
    
    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques orchestrateur"""
        return {
            'signals_processed': self.stats['signals_processed'],
            'trend_signals': self.stats['trend_signals'],
            'range_signals': self.stats['range_signals'],
            'rejected_regime': self.stats['rejected_regime'],
            'rejected_quality': self.stats['rejected_quality'],
            'final_signals_generated': self.stats['final_signals_generated'],
            'current_regime': self.current_regime.regime.value if self.current_regime else "none",
            'last_signal': self.last_final_signal.signal_type.value if self.last_final_signal else "none"
        }

# === SIGNAL AGGREGATOR ===

class SignalAggregator:
    """
    Agrégateur de signaux - Fusion finale et validation
    
    Responsabilités :
    1. Fusion signaux multiples strategies
    2. Validation finale qualité
    3. Ajustement position sizing
    4. Génération ordre exécution
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation aggregator"""
        self.config = config or {}
        self.min_final_score = self.config.get('min_final_score', 0.65)
        self.max_signals_to_aggregate = self.config.get('max_signals', 3)
        
        logger.info("SignalAggregator initialisé")
    
    def aggregate_signals(self, 
                         signals: List[StrategySignal],
                         regime_data: MarketRegimeData) -> Optional[FinalTradingSignal]:
        """Agrégation finale des signaux"""
        
        if not signals:
            return None
        
        # Limitation nombre signaux
        if len(signals) > self.max_signals_to_aggregate:
            signals = signals[:self.max_signals_to_aggregate]
        
        # Calcul weighted average des paramètres
        total_weight = sum(s.confidence for s in signals)
        
        if total_weight == 0:
            return None
        
        # Moyennes pondérées
        avg_entry = sum(s.entry_price * s.confidence for s in signals) / total_weight
        avg_stop = sum(s.stop_loss * s.confidence for s in signals) / total_weight
        avg_tp = sum(s.take_profit * s.confidence for s in signals) / total_weight
        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        
        # Sélection direction majoritaire
        directions = [s.direction for s in signals]
        final_direction = max(set(directions), key=directions.count)
        
        # Score final combiné
        final_score = self._calculate_combined_score(signals)
        
        if final_score < self.min_final_score:
            return None
        
        # Position size conservatrice
        position_size = min(s.position_size for s in signals)
        
        # Création signal final
        primary_signal = max(signals, key=lambda s: s.confidence)
        
        return FinalTradingSignal(
            timestamp=primary_signal.timestamp,
            signal_type=self._determine_aggregated_signal_type(signals, final_score),
            direction=final_direction,
            entry_price=avg_entry,
            stop_loss=avg_stop,
            take_profit=avg_tp,
            position_size=position_size,
            final_confidence=avg_confidence,
            signal_score=final_score,
            risk_reward_ratio=abs(avg_tp - avg_entry) / abs(avg_entry - avg_stop),
            primary_strategy=primary_signal.strategy_source,
            contributing_strategies=[s.strategy_source for s in signals],
            regime_context=regime_data.regime.value,
            max_risk_dollars=0.0,  # Calculé plus tard
            expected_pnl=0.0,      # Calculé plus tard
            reasoning=f"Aggregated from {len(signals)} signals",
            execution_priority=2
        )
    
    def _calculate_combined_score(self, signals: List[StrategySignal]) -> float:
        """Calcul score combiné avec bonification"""
        
        base_score = sum(s.calculate_signal_score() for s in signals) / len(signals)
        
        # Bonus pour convergence directions
        directions = [s.direction for s in signals]
        if len(set(directions)) == 1:  # Toutes mêmes directions
            base_score += 0.05
        
        # Bonus pour stratégies différentes
        strategies = [s.strategy_source for s in signals]
        if len(set(strategies)) > 1:  # Stratégies différentes
            base_score += 0.03
        
        return min(base_score, 1.0)
    
    def _determine_aggregated_signal_type(self, 
                                        signals: List[StrategySignal], 
                                        final_score: float) -> FinalSignalType:
        """Détermination type signal agrégé"""
        
        primary_signal = max(signals, key=lambda s: s.confidence)
        direction = primary_signal.direction
        
        # Classification selon score final
        if final_score >= 0.85:
            return FinalSignalType.PREMIUM_LONG_TREND if direction == "LONG" else FinalSignalType.PREMIUM_SHORT_TREND
        elif final_score >= 0.75:
            return FinalSignalType.STRONG_LONG if direction == "LONG" else FinalSignalType.STRONG_SHORT
        else:
            return FinalSignalType.WEAK_LONG if direction == "LONG" else FinalSignalType.WEAK_SHORT

# === PACKAGE EXPORTS ===

# Strategy classes
from .trend_strategy import TrendStrategy, TrendSignalData, TrendSignalType
from .range_strategy import RangeStrategy, RangeSignalData, RangeSignalType
from .strategy_selector import (
    StrategySelector, StrategySelectionResult, TradingContext, SystemPerformance,
    StrategyType, SignalDecision, ExecutionMode
)

# Market regime
from features.market_regime import MarketRegimeDetector, MarketRegimeData

# Factory functions
def create_strategy_orchestrator(config: Optional[Dict[str, Any]] = None) -> StrategyOrchestrator:
    """Factory function orchestrateur"""
    return StrategyOrchestrator(config)

def create_signal_aggregator(config: Optional[Dict[str, Any]] = None) -> SignalAggregator:
    """Factory function aggregator"""
    return SignalAggregator(config)

def create_strategy_selector(config: Optional[Dict[str, Any]] = None) -> StrategySelector:
    """Factory function chef d'orchestre système complet"""
    from .strategy_selector import create_strategy_selector as _create_selector
    return _create_selector(config)

def analyze_complete_trading_opportunity(
    market_data: MarketData,
    order_flow: Optional[OrderFlowData] = None,
    options_data: Optional[Dict[str, Any]] = None,
    structure_data: Optional[Dict[str, Any]] = None,
    es_nq_data: Optional[Dict[str, float]] = None,
    sierra_patterns: Optional[Dict[str, float]] = None,
    orchestrator: Optional[StrategyOrchestrator] = None
) -> Optional[FinalTradingSignal]:
    """
    FONCTION PRINCIPALE - ANALYSE COMPLÈTE
    
    Point d'entrée unique pour analyse trading complète
    """
    
    if orchestrator is None:
        orchestrator = create_strategy_orchestrator()
    
    return orchestrator.analyze_trading_opportunity(
        market_data=market_data,
        order_flow=order_flow,
        options_data=options_data,
        structure_data=structure_data,
        es_nq_data=es_nq_data,
        sierra_patterns=sierra_patterns
    )

def execute_full_analysis(trading_context: 'TradingContext',
                         selector: Optional[StrategySelector] = None) -> 'StrategySelectionResult':
    """
    ANALYSE COMPLÈTE AVEC STRATEGY SELECTOR
    
    Point d'entrée pour orchestration complète du système
    """
    from .strategy_selector import execute_full_analysis as _execute_analysis
    return _execute_analysis(trading_context, selector)

# Package exports
__all__ = [
    # Core classes
    'TrendStrategy',
    'RangeStrategy', 
    'MarketRegimeDetector',
    'StrategyOrchestrator',
    'SignalAggregator',
    'StrategySelector',  # Chef d'orchestre système complet
    
    # Data classes
    'TrendSignalData',
    'RangeSignalData', 
    'MarketRegimeData',
    'FinalTradingSignal',
    'StrategySignal',
    'StrategySelectionResult',  # Résultat sélection stratégie
    'TradingContext',          # Contexte trading complet
    'SystemPerformance',       # Métriques performance système
    
    # Enums
    'TrendSignalType',
    'RangeSignalType',
    'FinalSignalType',
    'StrategyPriority',
    'StrategyType',           # Types stratégies (TREND/RANGE/WAIT)
    'SignalDecision',         # Décisions finales (EXECUTE/REJECT/WAIT)
    'ExecutionMode',          # Modes exécution (PAPER/LIVE/SIMULATION)
    
    # Factory functions
    'create_strategy_orchestrator',
    'create_signal_aggregator',
    'create_strategy_selector',  # Factory chef d'orchestre
    'analyze_complete_trading_opportunity',
    'execute_full_analysis',     # Analysis complète avec StrategySelector
    
    # Analysis functions
    'analyze_trend_opportunity',
    'analyze_range_opportunity',
    'analyze_market_regime'
]