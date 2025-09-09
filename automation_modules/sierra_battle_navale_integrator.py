#!/usr/bin/env python3
"""
🚀 SIERRA BATTLE NAVALE INTEGRATOR
Intégration complète OrderFlow Sierra Chart + Battle Navale
"""

import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from collections import deque

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger
from core.base_types import MarketData, OrderFlowData
from core.battle_navale import BattleNavaleDetector, create_battle_navale_detector
from automation_modules.sierra_patterns_optimizer import (
    SierraPatternsOptimizer, 
    SierraPatternConfig,
    PatternSignal,
    PatternType
)
from automation_modules.sierra_connector_v2 import SierraConnectorV2
from automation_modules.orderflow_analyzer import OrderFlowAnalyzer

logger = get_logger(__name__)

class IntegrationMode(Enum):
    """Modes d'intégration"""
    BATTLE_NAVALE_ONLY = "battle_navale_only"      # Seulement Battle Navale
    SIERRA_ONLY = "sierra_only"                    # Seulement Sierra patterns
    FULL_INTEGRATION = "full_integration"          # Intégration complète
    ADAPTIVE = "adaptive"                          # Mode adaptatif selon conditions

class SignalQuality(Enum):
    """Qualité du signal intégré"""
    ELITE = "elite"           # 95-100% - Signal exceptionnel
    PREMIUM = "premium"       # 85-94% - Signal premium
    STRONG = "strong"         # 75-84% - Signal fort
    GOOD = "good"            # 65-74% - Signal correct
    WEAK = "weak"            # 50-64% - Signal faible
    NO_SIGNAL = "no_signal"  # <50% - Pas de signal

@dataclass
class IntegratedSignal:
    """Signal intégré Battle Navale + Sierra"""
    
    # Informations de base
    timestamp: pd.Timestamp
    symbol: str
    price_level: float
    signal_direction: str                # "LONG", "SHORT", "NEUTRAL"
    
    # Scores composants
    battle_navale_score: float           # 0.0-1.0
    sierra_patterns_score: float         # 0.0-1.0
    orderflow_score: float              # 0.0-1.0
    volume_profile_score: float         # 0.0-1.0
    
    # Score final
    integrated_score: float             # 0.0-1.0
    signal_quality: SignalQuality
    confidence: float                   # 0.0-1.0
    
    # Détails techniques
    battle_patterns: List[str] = field(default_factory=list)
    sierra_patterns: List[PatternSignal] = field(default_factory=list)
    orderflow_signals: Dict[str, Any] = field(default_factory=dict)
    
    # Métadonnées
    confluence_count: int = 0
    risk_reward_ratio: float = 0.0
    stop_loss_level: float = 0.0
    take_profit_level: float = 0.0
    reasoning: str = ""

@dataclass 
class IntegrationConfig:
    """Configuration intégration"""
    
    # Mode intégration
    integration_mode: IntegrationMode = IntegrationMode.FULL_INTEGRATION
    
    # Pondérations scores (doivent sommer à 1.0)
    battle_navale_weight: float = 0.4    # 40% - Battle Navale core
    sierra_patterns_weight: float = 0.3  # 30% - Sierra patterns
    orderflow_weight: float = 0.2        # 20% - OrderFlow
    volume_profile_weight: float = 0.1   # 10% - Volume Profile
    
    # Seuils qualité
    elite_threshold: float = 0.95
    premium_threshold: float = 0.85
    strong_threshold: float = 0.75
    good_threshold: float = 0.65
    weak_threshold: float = 0.50
    
    # Confluence
    min_confluence_signals: int = 2      # Minimum 2 signaux concordants
    confluence_boost: float = 0.15       # +15% si confluence
    
    # Performance
    analysis_interval_ms: int = 500      # 500ms entre analyses
    max_signals_per_minute: int = 3      # Anti-spam
    signal_timeout_seconds: int = 300    # 5min timeout signal

class SierraBattleNavaleIntegrator:
    """
    Intégrateur Sierra Chart + Battle Navale
    
    Fonctionnalités:
    ✅ Fusion signals Battle Navale + Sierra patterns
    ✅ OrderFlow analysis en temps réel
    ✅ Volume Profile integration
    ✅ Confluence scoring avancé
    ✅ Risk management intégré
    ✅ Performance monitoring
    """
    
    def __init__(self, config: Optional[IntegrationConfig] = None):
        self.config = config or IntegrationConfig()
        
        # Composants Battle Navale
        self.battle_navale_detector = create_battle_navale_detector()
        
        # Composants Sierra Chart
        sierra_pattern_config = SierraPatternConfig()
        sierra_pattern_config.analysis_interval_ms = self.config.analysis_interval_ms
        self.sierra_patterns_optimizer = SierraPatternsOptimizer(sierra_pattern_config)
        
        # Analyseur OrderFlow
        self.orderflow_analyzer = OrderFlowAnalyzer({})
        
        # Connecteur Sierra (optionnel pour données temps réel)
        self.sierra_connector: Optional[SierraConnectorV2] = None
        
        # Historique et cache
        self.market_data_history: deque = deque(maxlen=100)
        self.integrated_signals_history: deque = deque(maxlen=50)
        self.last_analysis_time = 0
        
        # Statistiques
        self.stats = {
            'total_signals_generated': 0,
            'signals_by_quality': {quality.value: 0 for quality in SignalQuality},
            'battle_navale_hits': 0,
            'sierra_patterns_hits': 0,
            'confluence_hits': 0,
            'avg_integration_time_ms': 0.0
        }
        
        logger.info("🚀 Sierra Battle Navale Integrator initialisé")
    
    async def connect_sierra_chart(self, symbols: List[str] = ['ES']) -> bool:
        """Connexion optionnelle à Sierra Chart pour données temps réel"""
        
        try:
            self.sierra_connector = SierraConnectorV2()
            success = await self.sierra_connector.connect(symbols)
            
            if success:
                logger.info("✅ Sierra Chart connecté pour données temps réel")
                return True
            else:
                logger.warning("❌ Échec connexion Sierra Chart")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur connexion Sierra Chart: {e}")
            return False
    
    async def analyze_integrated_signals(self, 
                                       market_data: MarketData,
                                       orderflow_data: Optional[OrderFlowData] = None,
                                       volume_profile: Optional[Dict] = None) -> Optional[IntegratedSignal]:
        """Analyse intégrée des signaux"""
        
        start_time = time.perf_counter()
        
        # Vérifier intervalle d'analyse
        current_time = time.time() * 1000
        if current_time - self.last_analysis_time < self.config.analysis_interval_ms:
            return None
        
        self.last_analysis_time = current_time
        
        # Ajouter données à l'historique
        self.market_data_history.append(market_data)
        
        if len(self.market_data_history) < 5:
            return None  # Pas assez de données
        
        try:
            # 1. Analyse Battle Navale
            battle_score, battle_patterns = await self._analyze_battle_navale(market_data)
            
            # 2. Analyse Sierra Patterns
            sierra_score, sierra_patterns = await self._analyze_sierra_patterns(market_data, orderflow_data, volume_profile)
            
            # 3. Analyse OrderFlow
            orderflow_score, orderflow_signals = await self._analyze_orderflow(market_data, orderflow_data)
            
            # 4. Analyse Volume Profile
            volume_score = self._analyze_volume_profile(market_data, volume_profile)
            
            # 5. Intégration et scoring
            integrated_signal = self._integrate_signals(
                market_data, battle_score, sierra_score, orderflow_score, volume_score,
                battle_patterns, sierra_patterns, orderflow_signals
            )
            
            if integrated_signal:
                # Ajouter à l'historique
                self.integrated_signals_history.append(integrated_signal)
                
                # Mise à jour statistiques
                analysis_time = (time.perf_counter() - start_time) * 1000
                self._update_stats(integrated_signal, analysis_time)
                
                logger.info(f"🎯 Signal intégré: {integrated_signal.signal_quality.value} - Score {integrated_signal.integrated_score:.3f}")
                
                return integrated_signal
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse intégrée: {e}")
            return None
    
    async def _analyze_battle_navale(self, market_data: MarketData) -> Tuple[float, List[str]]:
        """Analyse Battle Navale"""
        
        try:
            # Convertir historique en format compatible
            market_data_list = list(self.market_data_history)
            
            # Analyse Battle Navale
            result = await self.battle_navale_detector.analyze_market_data(market_data, market_data_list)
            
            if result and hasattr(result, 'signal_strength'):
                score = result.signal_strength
                patterns = getattr(result, 'detected_patterns', [])
                
                # Normaliser score à 0-1
                normalized_score = max(0.0, min(1.0, score))
                
                return normalized_score, patterns
            
            return 0.0, []
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse Battle Navale: {e}")
            return 0.0, []
    
    async def _analyze_sierra_patterns(self, 
                                     market_data: MarketData,
                                     orderflow_data: Optional[OrderFlowData] = None,
                                     volume_profile: Optional[Dict] = None) -> Tuple[float, List[PatternSignal]]:
        """Analyse Sierra Patterns"""
        
        try:
            # Convertir OrderFlowData en dict si nécessaire
            orderflow_dict = None
            if orderflow_data:
                orderflow_dict = {
                    'block_volume': getattr(orderflow_data, 'block_volume', 0),
                    'total_volume': getattr(orderflow_data, 'total_volume', market_data.volume),
                    'iceberg_volume': getattr(orderflow_data, 'iceberg_volume', 0),
                    'delta': getattr(orderflow_data, 'delta', 0.0)
                }
            
            # Analyse patterns Sierra
            patterns = self.sierra_patterns_optimizer.analyze_patterns(
                market_data, orderflow_dict, volume_profile
            )
            
            if patterns:
                # Score basé sur force moyenne des patterns
                avg_strength = np.mean([p.strength for p in patterns])
                
                # Bonus confluence
                confluence_bonus = min(0.2, len(patterns) * 0.05)  # +5% par pattern, max +20%
                
                final_score = min(1.0, avg_strength + confluence_bonus)
                
                return final_score, patterns
            
            return 0.0, []
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse Sierra patterns: {e}")
            return 0.0, []
    
    async def _analyze_orderflow(self, 
                               market_data: MarketData,
                               orderflow_data: Optional[OrderFlowData] = None) -> Tuple[float, Dict[str, Any]]:
        """Analyse OrderFlow"""
        
        try:
            if not orderflow_data:
                return 0.0, {}
            
            # Analyse via OrderFlowAnalyzer
            market_data_dict = {
                'symbol': market_data.symbol,
                'price': market_data.close,
                'volume': market_data.volume,
                'timestamp': market_data.timestamp
            }
            
            signal = await self.orderflow_analyzer.analyze_orderflow_data(market_data_dict)
            
            if signal:
                score = signal.strength
                signals_dict = {
                    'signal_type': signal.signal_type,
                    'strength': signal.strength,
                    'confidence': signal.confidence,
                    'reasoning': signal.reasoning
                }
                
                return score, signals_dict
            
            return 0.0, {}
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse OrderFlow: {e}")
            return 0.0, {}
    
    def _analyze_volume_profile(self, 
                              market_data: MarketData,
                              volume_profile: Optional[Dict] = None) -> float:
        """Analyse Volume Profile"""
        
        try:
            if not volume_profile:
                return 0.0
            
            current_price = market_data.close
            current_volume = market_data.volume
            
            # Analyser niveaux volume
            levels = volume_profile.get('levels', [])
            if not levels:
                return 0.0
            
            # Trouver niveau le plus proche
            nearest_level = min(levels, key=lambda x: abs(x.get('price', 0) - current_price))
            
            if nearest_level:
                level_volume = nearest_level.get('volume', 0)
                price_distance = abs(nearest_level.get('price', 0) - current_price)
                
                # Score basé sur volume et proximité
                volume_ratio = current_volume / max(level_volume, 1)
                distance_factor = max(0.1, 1.0 - (price_distance / 2.0))  # Pénalité distance
                
                score = min(1.0, volume_ratio * distance_factor * 0.5)  # Facteur conservateur
                
                return score
            
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse Volume Profile: {e}")
            return 0.0
    
    def _integrate_signals(self,
                          market_data: MarketData,
                          battle_score: float,
                          sierra_score: float, 
                          orderflow_score: float,
                          volume_score: float,
                          battle_patterns: List[str],
                          sierra_patterns: List[PatternSignal],
                          orderflow_signals: Dict[str, Any]) -> Optional[IntegratedSignal]:
        """Intégration finale des signaux"""
        
        # Calcul score pondéré
        weighted_score = (
            battle_score * self.config.battle_navale_weight +
            sierra_score * self.config.sierra_patterns_weight +
            orderflow_score * self.config.orderflow_weight +
            volume_score * self.config.volume_profile_weight
        )
        
        # Compter signaux concordants
        active_signals = sum([
            1 if battle_score > 0.5 else 0,
            1 if sierra_score > 0.5 else 0,
            1 if orderflow_score > 0.5 else 0,
            1 if volume_score > 0.3 else 0  # Seuil plus bas pour volume
        ])
        
        # Vérifier confluence minimum
        if active_signals < self.config.min_confluence_signals:
            return None
        
        # Bonus confluence
        if active_signals >= 3:
            weighted_score += self.config.confluence_boost
        
        # Normaliser score final
        final_score = max(0.0, min(1.0, weighted_score))
        
        # Déterminer qualité signal
        signal_quality = self._determine_signal_quality(final_score)
        
        # Déterminer direction signal
        signal_direction = self._determine_signal_direction(
            battle_patterns, sierra_patterns, orderflow_signals
        )
        
        # Calculs risk management
        stop_loss, take_profit, rr_ratio = self._calculate_risk_management(
            market_data.close, signal_direction, final_score
        )
        
        # Reasoning détaillé
        reasoning = self._generate_reasoning(
            battle_score, sierra_score, orderflow_score, volume_score,
            battle_patterns, sierra_patterns, active_signals
        )
        
        return IntegratedSignal(
            timestamp=market_data.timestamp,
            symbol=market_data.symbol,
            price_level=market_data.close,
            signal_direction=signal_direction,
            battle_navale_score=battle_score,
            sierra_patterns_score=sierra_score,
            orderflow_score=orderflow_score,
            volume_profile_score=volume_score,
            integrated_score=final_score,
            signal_quality=signal_quality,
            confidence=final_score,
            battle_patterns=battle_patterns,
            sierra_patterns=sierra_patterns,
            orderflow_signals=orderflow_signals,
            confluence_count=active_signals,
            risk_reward_ratio=rr_ratio,
            stop_loss_level=stop_loss,
            take_profit_level=take_profit,
            reasoning=reasoning
        )
    
    def _determine_signal_quality(self, score: float) -> SignalQuality:
        """Détermine la qualité du signal"""
        
        if score >= self.config.elite_threshold:
            return SignalQuality.ELITE
        elif score >= self.config.premium_threshold:
            return SignalQuality.PREMIUM
        elif score >= self.config.strong_threshold:
            return SignalQuality.STRONG
        elif score >= self.config.good_threshold:
            return SignalQuality.GOOD
        elif score >= self.config.weak_threshold:
            return SignalQuality.WEAK
        else:
            return SignalQuality.NO_SIGNAL
    
    def _determine_signal_direction(self, 
                                  battle_patterns: List[str],
                                  sierra_patterns: List[PatternSignal],
                                  orderflow_signals: Dict[str, Any]) -> str:
        """Détermine la direction du signal"""
        
        bullish_indicators = 0
        bearish_indicators = 0
        
        # Battle Navale patterns
        for pattern in battle_patterns:
            if any(keyword in pattern.lower() for keyword in ['viking', 'green', 'bull', 'up']):
                bullish_indicators += 1
            elif any(keyword in pattern.lower() for keyword in ['defender', 'red', 'bear', 'down']):
                bearish_indicators += 1
        
        # Sierra patterns
        for pattern in sierra_patterns:
            if pattern.pattern_type in [PatternType.LONG_DOWN_UP_BAR, PatternType.COLOR_DOWN_SETTING]:
                bullish_indicators += 1
            elif pattern.pattern_type == PatternType.LONG_UP_DOWN_BAR:
                bearish_indicators += 1
        
        # OrderFlow
        if orderflow_signals:
            signal_type = orderflow_signals.get('signal_type', '')
            if 'bullish' in signal_type.lower() or 'buy' in signal_type.lower():
                bullish_indicators += 1
            elif 'bearish' in signal_type.lower() or 'sell' in signal_type.lower():
                bearish_indicators += 1
        
        # Déterminer direction
        if bullish_indicators > bearish_indicators:
            return "LONG"
        elif bearish_indicators > bullish_indicators:
            return "SHORT"
        else:
            return "NEUTRAL"
    
    def _calculate_risk_management(self, 
                                 current_price: float,
                                 direction: str,
                                 signal_strength: float) -> Tuple[float, float, float]:
        """Calcule niveaux risk management"""
        
        # Distances basées sur force signal
        base_stop_distance = 2.0 * 0.25  # 2 ticks ES
        base_target_distance = 4.0 * 0.25  # 4 ticks ES
        
        # Ajustement selon force signal
        strength_multiplier = 1.0 + signal_strength  # 1.0 à 2.0
        
        stop_distance = base_stop_distance / strength_multiplier
        target_distance = base_target_distance * strength_multiplier
        
        if direction == "LONG":
            stop_loss = current_price - stop_distance
            take_profit = current_price + target_distance
        elif direction == "SHORT":
            stop_loss = current_price + stop_distance
            take_profit = current_price - target_distance
        else:  # NEUTRAL
            stop_loss = current_price
            take_profit = current_price
        
        # Risk/Reward ratio
        risk = abs(current_price - stop_loss)
        reward = abs(take_profit - current_price)
        rr_ratio = reward / risk if risk > 0 else 0.0
        
        return stop_loss, take_profit, rr_ratio
    
    def _generate_reasoning(self,
                          battle_score: float,
                          sierra_score: float,
                          orderflow_score: float,
                          volume_score: float,
                          battle_patterns: List[str],
                          sierra_patterns: List[PatternSignal],
                          confluence_count: int) -> str:
        """Génère explication détaillée du signal"""
        
        reasoning_parts = []
        
        # Confluence
        reasoning_parts.append(f"🎯 Confluence: {confluence_count} signaux concordants")
        
        # Battle Navale
        if battle_score > 0.5:
            patterns_str = ", ".join(battle_patterns[:3]) if battle_patterns else "Pattern détecté"
            reasoning_parts.append(f"⚔️ Battle Navale ({battle_score:.2f}): {patterns_str}")
        
        # Sierra Patterns
        if sierra_score > 0.5:
            sierra_types = [p.pattern_type.value for p in sierra_patterns[:2]]
            sierra_str = ", ".join(sierra_types) if sierra_types else "Patterns Sierra"
            reasoning_parts.append(f"📊 Sierra ({sierra_score:.2f}): {sierra_str}")
        
        # OrderFlow
        if orderflow_score > 0.5:
            reasoning_parts.append(f"💹 OrderFlow ({orderflow_score:.2f}): Smart Money détecté")
        
        # Volume Profile
        if volume_score > 0.3:
            reasoning_parts.append(f"📈 Volume ({volume_score:.2f}): Imbalance confirmé")
        
        return " | ".join(reasoning_parts)
    
    def _update_stats(self, signal: IntegratedSignal, analysis_time_ms: float):
        """Met à jour statistiques"""
        
        self.stats['total_signals_generated'] += 1
        self.stats['signals_by_quality'][signal.signal_quality.value] += 1
        
        if signal.battle_navale_score > 0.5:
            self.stats['battle_navale_hits'] += 1
        
        if signal.sierra_patterns_score > 0.5:
            self.stats['sierra_patterns_hits'] += 1
        
        if signal.confluence_count >= 3:
            self.stats['confluence_hits'] += 1
        
        # Moyenne mobile temps analyse
        current_avg = self.stats['avg_integration_time_ms']
        self.stats['avg_integration_time_ms'] = (current_avg * 0.9 + analysis_time_ms * 0.1)
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """Résumé intégration"""
        
        total_signals = self.stats['total_signals_generated']
        
        return {
            'total_signals': total_signals,
            'signals_by_quality': dict(self.stats['signals_by_quality']),
            'battle_navale_hit_rate': self.stats['battle_navale_hits'] / max(1, total_signals),
            'sierra_patterns_hit_rate': self.stats['sierra_patterns_hits'] / max(1, total_signals),
            'confluence_hit_rate': self.stats['confluence_hits'] / max(1, total_signals),
            'avg_analysis_time_ms': self.stats['avg_integration_time_ms'],
            'recent_signals_count': len(self.integrated_signals_history),
            'integration_mode': self.config.integration_mode.value
        }
    
    def export_for_feature_calculator(self, signal: IntegratedSignal) -> Dict[str, float]:
        """Export signal pour feature_calculator.py"""
        
        # Format compatible avec sierra_pattern_strength
        sierra_dict = self.sierra_patterns_optimizer.export_sierra_patterns_dict(signal.sierra_patterns)
        
        # Ajout données intégrées
        sierra_dict.update({
            'integrated_signal_strength': signal.integrated_score,
            'battle_navale_integration': signal.battle_navale_score,
            'orderflow_integration': signal.orderflow_score,
            'volume_profile_integration': signal.volume_profile_score,
            'confluence_score': signal.confluence_count / 4.0,  # Normaliser à 0-1
            'signal_quality_score': self._quality_to_score(signal.signal_quality)
        })
        
        return sierra_dict
    
    def _quality_to_score(self, quality: SignalQuality) -> float:
        """Convertit qualité en score numérique"""
        
        quality_scores = {
            SignalQuality.ELITE: 1.0,
            SignalQuality.PREMIUM: 0.9,
            SignalQuality.STRONG: 0.8,
            SignalQuality.GOOD: 0.7,
            SignalQuality.WEAK: 0.6,
            SignalQuality.NO_SIGNAL: 0.0
        }
        
        return quality_scores.get(quality, 0.0)

# Factory functions
def create_scalping_integrator() -> SierraBattleNavaleIntegrator:
    """Intégrateur optimisé pour scalping"""
    config = IntegrationConfig()
    config.analysis_interval_ms = 250        # 250ms pour scalping
    config.min_confluence_signals = 2        # Moins strict
    config.strong_threshold = 0.70           # Seuils plus bas
    config.good_threshold = 0.60
    
    return SierraBattleNavaleIntegrator(config)

def create_swing_integrator() -> SierraBattleNavaleIntegrator:
    """Intégrateur optimisé pour swing trading"""
    config = IntegrationConfig()
    config.analysis_interval_ms = 2000       # 2s pour swing
    config.min_confluence_signals = 3        # Plus strict
    config.strong_threshold = 0.80           # Seuils plus élevés
    config.good_threshold = 0.70
    
    return SierraBattleNavaleIntegrator(config)

# Export principal
__all__ = [
    'SierraBattleNavaleIntegrator',
    'IntegratedSignal',
    'IntegrationConfig',
    'IntegrationMode',
    'SignalQuality',
    'create_scalping_integrator',
    'create_swing_integrator'
]


