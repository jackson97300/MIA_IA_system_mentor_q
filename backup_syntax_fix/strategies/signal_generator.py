"""
MIA_IA_SYSTEM - Signal Generator
🧠 CERVEAU CENTRAL du système de trading
Version: Production Ready v3.1 (avec optimisations cache)
Performance: <5ms pour génération signal complet (objectif <2ms avec cache)

Le SignalGenerator est l'orchestrateur principal qui :
1. Coordonne tous les composants d'analyse
2. Génère UN signal unifié pour exécution
3. Garantit cohérence et qualité des décisions
4. NOUVEAU : Utilise le Feature Calculator optimisé avec cache
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import pandas as pd

# === CORE IMPORTS ===
from core.base_types import (
    MarketData, OrderFlowData, TradingSignal,
    SignalType, MarketRegime
)

# === FEATURES IMPORTS - MISE À JOUR POUR OPTIMISATION ===
from features import (
    create_feature_calculator,  # Factory qui utilise version optimisée
    MarketRegimeDetector, 
    ConfluenceAnalyzer,
    OPTIMIZED_CALCULATOR_AVAILABLE  # Pour vérifier si disponible
)
from features.market_regime import MarketRegimeData

# === STRATEGIES IMPORTS ===
from core.battle_navale import BattleNavaleAnalyzer
from strategies.trend_strategy import TrendStrategy
from strategies.range_strategy import RangeStrategy

logger = logging.getLogger(__name__)

# === ENUMS ===

class SignalDecision(Enum):
    """Décisions finales possibles"""
    EXECUTE_LONG = "execute_long"
    EXECUTE_SHORT = "execute_short"
    EXIT_POSITION = "exit_position"
    WAIT_BETTER_SETUP = "wait_better_setup"
    NO_TRADE = "no_trade"

class SignalSource(Enum):
    """Source du signal"""
    BATTLE_NAVALE = "battle_navale"
    TREND_STRATEGY = "trend_strategy"
    RANGE_STRATEGY = "range_strategy"
    ML_PREDICTION = "ml_prediction"
    MANUAL_OVERRIDE = "manual_override"

class QualityLevel(Enum):
    """Niveau de qualité du signal"""
    PREMIUM = "premium"      # >85% confluence
    STRONG = "strong"        # 75-85%
    MODERATE = "moderate"    # 65-75%
    WEAK = "weak"           # 55-65%
    REJECTED = "rejected"    # <55%

# === DATA STRUCTURES ===

@dataclass
class SignalComponents:
    """Composants analysés pour génération signal"""
    timestamp: pd.Timestamp
    features: Optional[Dict[str, float]] = None
    battle_navale: Optional[Any] = None
    market_regime: Optional[MarketRegimeData] = None
    trend_signal: Optional[Any] = None
    range_signal: Optional[Any] = None
    confluence_analysis: Optional[Any] = None
    risk_assessment: Optional[Dict[str, float]] = None

@dataclass
class FinalSignal:
    """Signal final généré par le système"""
    timestamp: pd.Timestamp
    decision: SignalDecision
    signal_type: SignalType
    confidence: float
    quality_level: QualityLevel
    
    # Détails exécution
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    
    # Contexte et reasoning
    source: SignalSource
    regime: MarketRegime
    components: SignalComponents
    reasoning: str
    
    # Risk metrics
    risk_reward_ratio: float
    max_risk_dollars: float
    
    # Metadata
    generation_time_ms: float
    cache_hits: int = 0  # NOUVEAU : Tracking cache
    metadata: Dict[str, Any] = field(default_factory=dict)

# === SIGNAL GENERATOR ===

class SignalGenerator:
    """
    🧠 CERVEAU CENTRAL - Générateur de signaux unifié
    
    Workflow :
    1. Analyse tous les composants (bataille navale, features, confluence, etc.)
    2. Détermine régime marché et stratégie appropriée
    3. Valide qualité et cohérence des signaux
    4. Génère 1 signal final unifié pour exécution
    
    Performance garantie : <5ms pour analyse complète
    NOUVEAU : <2ms avec cache activé
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation du générateur de signaux"""
        self.config = config or {}
        
        # === COMPOSANTS SYSTÈME ===
        # MISE À JOUR : Utilisation de la factory qui gère l'optimisation
        logger.info("🧠 Initialisation SignalGenerator v3.1...")
        
        # Feature Calculator avec cache optimisé
        cache_config = self.config.get('cache_config', {
            'cache_ttl': 60,     # 1 minute TTL
            'cache_size': 500    # 500 entrées max
        })
        
        self.feature_calculator = create_feature_calculator(
            config=config,
            optimized=True,  # Forcer version optimisée
            cache_config=cache_config
        )
        
        # Log du type de calculator utilisé
        calc_type = type(self.feature_calculator).__name__
        if calc_type == 'OptimizedFeatureCalculator':
            logger.info("✅ Feature Calculator OPTIMISÉ avec cache LRU activé")
            logger.info(f"  - Cache TTL: {cache_config.get('cache_ttl', 60)}s")
            logger.info(f"  - Cache size: {cache_config.get('cache_size', 500)} entrées")
        else:
            logger.warning("⚠️ Feature Calculator standard (sans cache)")
        
        # Autres composants
        self.confluence_analyzer = ConfluenceAnalyzer(config)
        self.market_regime = MarketRegimeDetector(config)
        self.battle_navale = BattleNavaleAnalyzer(config)
        self.trend_strategy = TrendStrategy(config)
        self.range_strategy = RangeStrategy(config)
        
        # === PARAMÈTRES GÉNÉRATION ===
        self.min_confidence = self.config.get('min_signal_confidence', 0.70)
        self.min_confluence = self.config.get('min_confluence_score', 0.60)
        self.min_risk_reward = self.config.get('min_risk_reward', 1.5)
        self.max_position_size = self.config.get('max_position_size', 3.0)
        
        # === ÉTAT SYSTÈME ===
        self.last_signal: Optional[FinalSignal] = None
        self.signal_history: deque = deque(maxlen=100)
        self.current_regime: Optional[MarketRegimeData] = None
        
        # === PERFORMANCE TRACKING ===
        self.stats = {
            'signals_generated': 0,
            'signals_executed': 0,
            'avg_generation_time_ms': 0.0,
            'cache_hit_rate': 0.0,  # NOUVEAU
            'quality_distribution': defaultdict(int),
            'regime_distribution': defaultdict(int),
            'success_by_source': defaultdict(list)
        }
        
        # NOUVEAU : Tracking dernière mise à jour stats cache
        self._last_cache_stats_update = time.time()
        
        logger.info("SignalGenerator initialisé - Cerveau central prêt")
    
    def generate_signal(self,
                       market_data: MarketData,
                       order_flow: Optional[OrderFlowData] = None,
                       options_data: Optional[Dict[str, Any]] = None,
                       structure_data: Optional[Dict[str, Any]] = None,
                       sierra_patterns: Optional[Dict[str, float]] = None) -> FinalSignal:
        """
        🎯 GÉNÉRATION SIGNAL PRINCIPAL
        
        Workflow complet d'analyse et génération signal final :
        1. Calcul features avec confluence (OPTIMISÉ avec cache)
        2. Analyse bataille navale (votre méthode signature)
        3. Détection régime marché (trend vs range)
        4. Sélection et exécution stratégie appropriée
        5. Validation confluence et qualité
        6. Construction signal final avec risk management
        
        Performance : <5ms garanti (<2ms avec cache hits)
        """
        start_time = time.time()
        cache_hits_start = self._get_cache_hits()
        
        try:
            # 1. ANALYSE COMPLÈTE DE TOUS LES COMPOSANTS
            components = self._analyze_all_components(
                market_data, order_flow, options_data, 
                structure_data, sierra_patterns
            )
            
            # 2. VALIDATION QUALITÉ MINIMALE
            if not self._validate_signal_quality(components):
                return self._create_no_trade_signal(
                    market_data, components, 
                    "Qualité signal insuffisante"
                )
            
            # 3. SÉLECTION STRATÉGIE SELON RÉGIME
            strategy_signal = self._select_and_execute_strategy(
                components, market_data
            )
            
            if not strategy_signal:
                return self._create_no_trade_signal(
                    market_data, components,
                    "Aucun signal stratégie valide"
                )
            
            # 4. VALIDATION CONFLUENCE FINALE
            confluence_valid = self._validate_confluence(
                components, strategy_signal
            )
            
            if not confluence_valid:
                return self._create_no_trade_signal(
                    market_data, components,
                    "Confluence insuffisante"
                )
            
            # 5. CONSTRUCTION SIGNAL FINAL
            final_signal = self._build_final_signal(
                market_data, components, strategy_signal
            )
            
            # 6. RISK MANAGEMENT VALIDATION
            if not self._validate_risk_parameters(final_signal):
                return self._create_no_trade_signal(
                    market_data, components,
                    "Paramètres risk invalides"
                )
            
            # NOUVEAU : Calcul cache hits pour ce signal
            cache_hits_end = self._get_cache_hits()
            final_signal.cache_hits = cache_hits_end - cache_hits_start
            
            # Calcul temps génération
            execution_time = (time.time() - start_time) * 1000
            final_signal.generation_time_ms = execution_time
            
            # Mise à jour stats
            self._update_stats(final_signal, execution_time)
            self.last_signal = final_signal
            self.signal_history.append(final_signal)
            
            # NOUVEAU : Log performance avec cache
            logger.info(f"Signal généré en {execution_time:.2f}ms "
                       f"(Cache hits: {final_signal.cache_hits}): "
                       f"{final_signal.decision.value} "
                       f"(Confidence: {final_signal.confidence:.3f})")
            
            # NOUVEAU : Mise à jour périodique stats cache
            self._update_cache_stats_periodically()
            
            return final_signal
            
        except Exception as e:
            logger.error(f"Erreur génération signal: {e}")
            return self._create_error_signal(market_data, str(e))
    
    def _analyze_all_components(self,
                               market_data: MarketData,
                               order_flow: Optional[OrderFlowData],
                               options_data: Optional[Dict[str, Any]],
                               structure_data: Optional[Dict[str, Any]],
                               sierra_patterns: Optional[Dict[str, float]]) -> SignalComponents:
        """Analyse complète de tous les composants"""
        
        components = SignalComponents(timestamp=market_data.timestamp)
        
        try:
            # 1. CALCUL FEATURES AVEC CONFLUENCE (OPTIMISÉ)
            components.features = self.feature_calculator.calculate_all_features(
                market_data=market_data,
                order_flow=order_flow,
                options_data=options_data,
                structure_data=structure_data,
                sierra_patterns=sierra_patterns
            )
            
            # 2. ANALYSE BATAILLE NAVALE (votre méthode signature)
            components.battle_navale = self.battle_navale.analyze_battle_navale(market_data, order_flow)
            
            # 3. DÉTECTION RÉGIME MARCHÉ
            components.market_regime = self.market_regime.analyze_market_regime(market_data)
            self.current_regime = components.market_regime
            
            # 4. ANALYSE CONFLUENCE MULTI-NIVEAUX
            if structure_data:
                components.confluence_analysis = self.confluence_analyzer.analyze_confluence(
                    market_data.close, structure_data
                )
            
            # 5. ÉVALUATION RISK
            components.risk_assessment = self._assess_risk_metrics(
                market_data, components
            )
            
        except Exception as e:
            logger.error(f"Erreur analyse composants: {e}")
        
        return components
    
    def _validate_signal_quality(self, components: SignalComponents) -> bool:
        """Validation qualité minimale du signal"""
        if not components.features:
            return False
        
        # Confluence score minimum
        confluence_score = components.features.get('confluence_score', 0)
        if confluence_score < self.min_confluence:
            logger.debug(f"Confluence insuffisante: {confluence_score:.3f} < {self.min_confluence}")
            return False
        
        # Battle navale signal minimum
        if components.battle_navale:
            battle_signal = getattr(components.battle_navale, 'battle_navale_signal', 0)
            if battle_signal < 0.5:  # Minimum 50% pour considérer
                logger.debug(f"Battle navale faible: {battle_signal:.3f}")
                return False
        
        return True
    
    def _select_and_execute_strategy(self,
                                   components: SignalComponents,
                                   market_data: MarketData) -> Optional[Any]:
        """Sélection et exécution de la stratégie appropriée"""
        
        if not components.market_regime:
            return None
        
        regime = components.market_regime.regime
        
        # TREND STRATEGY
        if regime in [MarketRegime.TREND_BULLISH, MarketRegime.TREND_BEARISH]:
            return self.trend_strategy.analyze_trend_opportunity(
                market_data=market_data,
                regime_data=components.market_regime,
                features=components.features,
                battle_navale=components.battle_navale
            )
        
        # RANGE STRATEGY
        elif regime in [MarketRegime.RANGE_TIGHT, MarketRegime.RANGE_WIDE]:
            return self.range_strategy.analyze_range_opportunity(
                market_data=market_data,
                regime_data=components.market_regime,
                features=components.features,
                sierra_patterns=components.features  # Features incluent patterns
            )
        
        # TRANSITION - Plus conservateur
        else:
            logger.debug("Régime en transition - pas de signal")
            return None
    
    def _validate_confluence(self,
                           components: SignalComponents,
                           strategy_signal: Any) -> bool:
        """Validation confluence finale"""
        
        # Si pas d'analyse confluence, on accepte
        if not components.confluence_analysis:
            return True
        
        # Vérifier alignement avec zones de confluence
        if hasattr(components.confluence_analysis, 'strongest_zone'):
            zone = components.confluence_analysis.strongest_zone
            if zone and hasattr(strategy_signal, 'entry_price'):
                # Vérifier que entry price est proche d'une zone forte
                distance = abs(strategy_signal.entry_price - zone.price)
                if distance > 2.0:  # Plus de 2 points de distance
                    logger.debug("Signal trop loin des zones de confluence")
                    return False
        
        return True
    
    def _build_final_signal(self,
                          market_data: MarketData,
                          components: SignalComponents,
                          strategy_signal: Any) -> FinalSignal:
        """Construction du signal final complet"""
        
        # Déterminer décision finale
        if hasattr(strategy_signal, 'signal_type'):
            if strategy_signal.signal_type in ['LONG_TREND', 'LONG_RANGE']:
                decision = SignalDecision.EXECUTE_LONG
                signal_type = SignalType.LONG_TREND if 'TREND' in strategy_signal.signal_type else SignalType.LONG_RANGE
            elif strategy_signal.signal_type in ['SHORT_TREND', 'SHORT_RANGE']:
                decision = SignalDecision.EXECUTE_SHORT
                signal_type = SignalType.SHORT_TREND if 'TREND' in strategy_signal.signal_type else SignalType.SHORT_RANGE
            else:
                decision = SignalDecision.NO_TRADE
                signal_type = SignalType.NO_SIGNAL
        else:
            decision = SignalDecision.NO_TRADE
            signal_type = SignalType.NO_SIGNAL
        
        # Calcul confidence finale
        confidence = self._calculate_final_confidence(components, strategy_signal)
        
        # Quality level
        quality_level = self._determine_quality_level(confidence)
        
        # Position sizing
        position_size = self._calculate_position_size(confidence, components)
        
        # Risk parameters
        entry_price = getattr(strategy_signal, 'entry_price', market_data.close)
        stop_loss = getattr(strategy_signal, 'stop_loss', entry_price - 2.0)
        take_profit = getattr(strategy_signal, 'take_profit', entry_price + 4.0)
        
        # Risk/Reward
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        # Source
        if components.battle_navale and getattr(components.battle_navale, 'battle_navale_signal', 0) > 0.7:
            source = SignalSource.BATTLE_NAVALE
        elif 'TREND' in str(signal_type):
            source = SignalSource.TREND_STRATEGY
        else:
            source = SignalSource.RANGE_STRATEGY
        
        return FinalSignal(
            timestamp=market_data.timestamp,
            decision=decision,
            signal_type=signal_type,
            confidence=confidence,
            quality_level=quality_level,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size,
            source=source,
            regime=components.market_regime.regime if components.market_regime else MarketRegime.UNKNOWN,
            components=components,
            reasoning=self._generate_reasoning(components, strategy_signal),
            risk_reward_ratio=risk_reward_ratio,
            max_risk_dollars=position_size * risk * ES_TICK_VALUE / ES_TICK_SIZE,
            generation_time_ms=0,  # Sera mis à jour
            metadata={
                'features_count': len(components.features) if components.features else 0,
                'battle_navale_signal': getattr(components.battle_navale, 'battle_navale_signal', 0) if components.battle_navale else 0,
                'confluence_score': components.features.get('confluence_score', 0) if components.features else 0
            }
        )
    
    def _calculate_final_confidence(self,
                                  components: SignalComponents,
                                  strategy_signal: Any) -> float:
        """Calcul confidence finale pondérée"""
        
        weights = {
            'strategy': 0.40,
            'battle_navale': 0.30,
            'confluence': 0.20,
            'regime': 0.10
        }
        
        confidence = 0.0
        
        # Strategy confidence
        if hasattr(strategy_signal, 'confidence'):
            confidence += strategy_signal.confidence * weights['strategy']
        
        # Battle navale
        if components.battle_navale:
            battle_signal = getattr(components.battle_navale, 'battle_navale_signal', 0.5)
            confidence += battle_signal * weights['battle_navale']
        
        # Confluence
        if components.features:
            confluence_score = components.features.get('confluence_score', 0.5)
            confidence += confluence_score * weights['confluence']
        
        # Regime strength
        if components.market_regime:
            regime_confidence = getattr(components.market_regime, 'confidence', 0.5)
            confidence += regime_confidence * weights['regime']
        
        return min(1.0, max(0.0, confidence))
    
    def _determine_quality_level(self, confidence: float) -> QualityLevel:
        """Détermine niveau de qualité selon confidence"""
        if confidence >= 0.85:
            return QualityLevel.PREMIUM
        elif confidence >= 0.75:
            return QualityLevel.STRONG
        elif confidence >= 0.65:
            return QualityLevel.MODERATE
        elif confidence >= 0.55:
            return QualityLevel.WEAK
        else:
            return QualityLevel.REJECTED
    
    def _calculate_position_size(self,
                               confidence: float,
                               components: SignalComponents) -> float:
        """Calcul taille position selon confidence et risk"""
        
        base_size = 1.0  # MES contracts
        
        # Ajustement selon confidence
        if confidence >= 0.85:
            size_multiplier = 1.5
        elif confidence >= 0.75:
            size_multiplier = 1.0
        elif confidence >= 0.65:
            size_multiplier = 0.75
        else:
            size_multiplier = 0.5
        
        # Ajustement selon volatilité
        if components.market_regime:
            if hasattr(components.market_regime, 'volatility'):
                if components.market_regime.volatility > 0.8:  # High vol
                    size_multiplier *= 0.75
        
        final_size = base_size * size_multiplier
        
        # Limites
        return min(self.max_position_size, max(0.5, final_size))
    
    def _assess_risk_metrics(self,
                           market_data: MarketData,
                           components: SignalComponents) -> Dict[str, float]:
        """Évaluation métriques de risque"""
        
        risk_metrics = {
            'volatility': 0.5,
            'trend_strength': 0.5,
            'support_resistance_distance': 2.0,
            'time_of_day_risk': 0.5
        }
        
        # Volatilité depuis regime
        if components.market_regime:
            risk_metrics['volatility'] = getattr(components.market_regime, 'volatility', 0.5)
        
        # Distance support/resistance depuis confluence
        if components.confluence_analysis:
            if hasattr(components.confluence_analysis, 'nearest_support'):
                support = components.confluence_analysis.nearest_support
                risk_metrics['support_resistance_distance'] = abs(market_data.close - support)
        
        # Time of day risk
        hour = market_data.timestamp.hour
        if hour < 10 or hour > 15:  # Outside main session
            risk_metrics['time_of_day_risk'] = 0.7
        
        return risk_metrics
    
    def _validate_risk_parameters(self, signal: FinalSignal) -> bool:
        """Validation finale paramètres de risque"""
        
        # Risk/Reward minimum
        if signal.risk_reward_ratio < self.min_risk_reward:
            logger.debug(f"R:R insuffisant: {signal.risk_reward_ratio:.2f} < {self.min_risk_reward}")
            return False
        
        # Stop loss raisonnable
        risk_ticks = abs(signal.entry_price - signal.stop_loss) / ES_TICK_SIZE
        if risk_ticks > 20:  # Max 5 points ES
            logger.debug(f"Stop loss trop large: {risk_ticks} ticks")
            return False
        
        # Position size valide
        if signal.position_size <= 0 or signal.position_size > self.max_position_size:
            logger.debug(f"Position size invalide: {signal.position_size}")
            return False
        
        return True
    
    def _generate_reasoning(self,
                          components: SignalComponents,
                          strategy_signal: Any) -> str:
        """Génération explication textuelle du signal"""
        
        reasons = []
        
        # Régime
        if components.market_regime:
            reasons.append(f"Régime: {components.market_regime.regime.value}")
        
        # Battle navale
        if components.battle_navale:
            battle_signal = getattr(components.battle_navale, 'battle_navale_signal', 0)
            if battle_signal > 0.7:
                reasons.append(f"Battle Navale fort ({battle_signal:.2f})")
        
        # Confluence
        if components.features:
            confluence = components.features.get('confluence_score', 0)
            reasons.append(f"Confluence: {confluence:.2f}")
        
        # Strategy
        if hasattr(strategy_signal, 'reasoning'):
            reasons.append(strategy_signal.reasoning)
        
        return " | ".join(reasons)
    
    def _create_no_trade_signal(self,
                              market_data: MarketData,
                              components: SignalComponents,
                              reason: str) -> FinalSignal:
        """Création signal NO_TRADE avec raison"""
        
        return FinalSignal(
            timestamp=market_data.timestamp,
            decision=SignalDecision.WAIT_BETTER_SETUP,
            signal_type=SignalType.NO_SIGNAL,
            confidence=0.0,
            quality_level=QualityLevel.REJECTED,
            entry_price=market_data.close,
            stop_loss=market_data.close,
            take_profit=market_data.close,
            position_size=0.0,
            source=SignalSource.BATTLE_NAVALE,
            regime=components.market_regime.regime if components.market_regime else MarketRegime.UNKNOWN,
            components=components,
            reasoning=reason,
            risk_reward_ratio=0.0,
            max_risk_dollars=0.0,
            generation_time_ms=0.0,
            metadata={'rejection_reason': reason}
        )
    
    def _create_error_signal(self, market_data: MarketData, error: str) -> FinalSignal:
        """Signal d'erreur"""
        components = SignalComponents(timestamp=market_data.timestamp)
        return self._create_no_trade_signal(market_data, components, f"Erreur: {error}")
    
    # === NOUVELLES MÉTHODES POUR CACHE ===
    
    def _get_cache_hits(self) -> int:
        """Récupère nombre total de cache hits"""
        if hasattr(self.feature_calculator, 'get_cache_stats'):
            stats = self.feature_calculator.get_cache_stats()
            return stats.get('cache_hits', 0)
        return 0
    
    def _update_cache_stats_periodically(self):
        """Met à jour stats cache toutes les 5 minutes"""
        now = time.time()
        if now - self._last_cache_stats_update > 300:  # 5 minutes
            if hasattr(self.feature_calculator, 'get_cache_stats'):
                cache_stats = self.feature_calculator.get_cache_stats()
                self.stats['cache_hit_rate'] = cache_stats.get('hit_rate', 0)
                
                logger.info(f"📊 Cache Stats Update: "
                           f"Hit rate={cache_stats.get('hit_rate', 0):.1%}, "
                           f"Avg time={cache_stats.get('avg_calculation_time_ms', 0):.2f}ms, "
                           f"Total calcs={cache_stats.get('total_calculations', 0)}")
            
            self._last_cache_stats_update = now
    
    def _update_stats(self, signal: FinalSignal, execution_time: float):
        """Mise à jour statistiques avec cache"""
        self.stats['signals_generated'] += 1
        
        # Rolling average temps génération
        count = self.stats['signals_generated']
        prev_avg = self.stats['avg_generation_time_ms']
        self.stats['avg_generation_time_ms'] = ((prev_avg * (count - 1)) + execution_time) / count
        
        # Distribution qualité
        self.stats['quality_distribution'][signal.quality_level.value] += 1
        
        # Distribution régime
        self.stats['regime_distribution'][signal.regime.value] += 1
        
        # Tracking par source
        if signal.decision in [SignalDecision.EXECUTE_LONG, SignalDecision.EXECUTE_SHORT]:
            self.stats['signals_executed'] += 1
            self.stats['success_by_source'][signal.source.value].append({
                'timestamp': signal.timestamp,
                'confidence': signal.confidence,
                'cache_hits': signal.cache_hits  # NOUVEAU
            })
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Statistiques performance avec cache"""
        executed_rate = self.stats['signals_executed'] / max(1, self.stats['signals_generated'])
        
        # NOUVEAU : Stats cache si disponibles
        cache_stats = {}
        if hasattr(self.feature_calculator, 'get_cache_stats'):
            cache_stats = self.feature_calculator.get_cache_stats()
        
        return {
            'signals_generated': self.stats['signals_generated'],
            'signals_executed': self.stats['signals_executed'],
            'execution_rate': executed_rate,
            'avg_generation_time_ms': self.stats['avg_generation_time_ms'],
            'quality_distribution': dict(self.stats['quality_distribution']),
            'regime_distribution': dict(self.stats['regime_distribution']),
            'cache_performance': {  # NOUVEAU
                'hit_rate': cache_stats.get('hit_rate', 0),
                'avg_calc_time_ms': cache_stats.get('avg_calculation_time_ms', 0),
                'total_calculations': cache_stats.get('total_calculations', 0),
                'min_calc_time_ms': cache_stats.get('min_calculation_time_ms', 0),
                'max_calc_time_ms': cache_stats.get('max_calculation_time_ms', 0)
            }
        }
    
    def clear_cache(self):
        """Vide le cache du feature calculator"""
        if hasattr(self.feature_calculator, 'clear_cache'):
            self.feature_calculator.clear_cache()
            logger.info("✅ Cache vidé dans SignalGenerator")

# === FACTORY FUNCTIONS ===

def create_signal_generator(config: Optional[Dict[str, Any]] = None) -> SignalGenerator:
    """
    Factory pour créer SignalGenerator
    NOUVEAU : Avec support cache optimisé
    """
    return SignalGenerator(config)

def generate_trading_signal(market_data: MarketData,
                          order_flow: Optional[OrderFlowData] = None,
                          options_data: Optional[Dict[str, Any]] = None,
                          structure_data: Optional[Dict[str, Any]] = None,
                          sierra_patterns: Optional[Dict[str, float]] = None,
                          generator: Optional[SignalGenerator] = None) -> FinalSignal:
    """
    Helper function pour génération rapide signal
    
    Usage:
        signal = generate_trading_signal(market_data, order_flow, options_data)
        if signal.decision == SignalDecision.EXECUTE_LONG:
            execute_trade(signal)
    """
    
    if generator is None:
        generator = create_signal_generator()
    
    return generator.generate_signal(
        market_data=market_data,
        order_flow=order_flow,
        options_data=options_data,
        structure_data=structure_data,
        sierra_patterns=sierra_patterns
    )

# === EXPORTS ===

__all__ = [
    # Classes principales
    'SignalGenerator',
    'FinalSignal',
    'SignalComponents',
    
    # Enums
    'SignalDecision',
    'SignalSource', 
    'QualityLevel',
    
    # Factory functions
    'create_signal_generator',
    'generate_trading_signal'
]

if __name__ == "__main__":
    # Test basique
    import sys
    from pathlib import Path
    
    # Ajouter le dossier parent au path
    sys.path.append(str(Path(__file__).parent.parent))
    
    logger.info("🧠 Test SignalGenerator v3.1 avec optimisations...")
    
    try:
        # Test création
        generator = create_signal_generator()
        logger.info("SignalGenerator créé avec succès")
        
        # Vérifier type de calculator
        calc_type = type(generator.feature_calculator).__name__
        logger.info("📊 Feature Calculator: {calc_type}")
        
        # Test données factices
        test_data = MarketData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            open=4500.0,
            high=4505.0,
            low=4495.0,
            close=4502.0,
            volume=1000
        )
        
        # Test génération signal
        signal = generator.generate_signal(test_data)
        logger.info("Signal généré: {signal.decision.value}")
        logger.info("   └─ Confiance: {signal.confidence:.3f}")
        logger.info("   └─ Qualité: {signal.quality_level.value}")
        logger.info("   └─ Temps: {signal.generation_time_ms:.2f}ms")
        logger.info("   └─ Cache hits: {signal.cache_hits}")
        
        # Test stats
        stats = generator.get_performance_stats()
        logger.info("Stats: {stats['signals_generated']} signaux générés")
        if 'cache_performance' in stats:
            cache = stats['cache_performance']
            logger.info("📊 Cache: Hit rate={cache['hit_rate']:.1%}, Avg={cache['avg_calc_time_ms']:.2f}ms")
        
    except Exception as e:
        logger.error("Erreur test: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("\n🎯 SignalGenerator v3.1 avec cache optimisé prêt!")