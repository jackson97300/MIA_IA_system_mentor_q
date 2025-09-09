#!/usr/bin/env python3
"""
🎯 SIERRA DOM INTEGRATOR
Intégration complète DOM avec Battle Navale et OrderFlow
"""

import asyncio
import time
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from automation_modules.sierra_dom_analyzer import (
    SierraDOMAnalyzer, 
    DOMConfig, 
    DOMSnapshot, 
    DOMPatternSignal,
    DOMPattern,
    DOMIntensity,
    create_scalping_dom_config
)
from automation_modules.sierra_battle_navale_integrator import SierraBattleNavaleIntegrator
from automation_modules.orderflow_analyzer import OrderFlowAnalyzer
from core.base_types import MarketData, OrderFlowData
from core.logger import get_logger

logger = get_logger(__name__)

@dataclass
class DOMBattleNavaleSignal:
    """Signal intégré DOM + Battle Navale"""
    timestamp: datetime
    symbol: str
    price_level: float
    
    # Composants signaux
    dom_patterns: List[DOMPatternSignal] = field(default_factory=list)
    battle_navale_score: float = 0.0
    orderflow_score: float = 0.0
    
    # Score final intégré
    integrated_score: float = 0.0
    signal_direction: str = "NEUTRAL"  # BULLISH, BEARISH, NEUTRAL
    confidence: float = 0.0
    
    # Métadonnées confluence
    confluence_categories: List[str] = field(default_factory=list)
    confluence_strength: float = 0.0
    time_horizon: str = "SHORT"  # IMMEDIATE, SHORT, MEDIUM, LONG
    reasoning: str = ""

@dataclass
class DOMIntegrationConfig:
    """Configuration intégration DOM"""
    
    # Seuils confluence
    min_confluence_categories: int = 2        # Min 2 catégories pour signal
    min_integrated_score: float = 0.65        # Score min pour signal
    min_confidence: float = 0.60              # Confidence min
    
    # Pondérations
    dom_weight: float = 0.4                   # 40% DOM
    battle_navale_weight: float = 0.35        # 35% Battle Navale
    orderflow_weight: float = 0.25            # 25% OrderFlow
    
    # Bonus confluence
    confluence_bonus_multiplier: float = 1.2   # +20% si confluence forte
    iceberg_bonus: float = 0.1                 # +10% si iceberg détecté
    wall_bonus: float = 0.15                   # +15% si mur détecté
    
    # Filtres qualité
    max_signals_per_minute: int = 5           # Max 5 signaux/minute
    signal_timeout_seconds: int = 180         # Timeout signal 3min

class SierraDOMIntegrator:
    """
    Intégrateur DOM Elite pour Sierra Chart
    
    Fonctionnalités:
    ✅ Fusion DOM + Battle Navale + OrderFlow
    ✅ Scoring confluence intelligent
    ✅ Détection patterns haute probabilité
    ✅ Filtrage signaux premium
    ✅ Performance <10ms par analyse
    ✅ Signaux multi-timeframe
    """
    
    def __init__(self, 
                 dom_config: Optional[DOMConfig] = None,
                 integration_config: Optional[DOMIntegrationConfig] = None):
        
        self.dom_config = dom_config or create_scalping_dom_config()
        self.integration_config = integration_config or DOMIntegrationConfig()
        
        # Composants d'analyse
        self.dom_analyzer = SierraDOMAnalyzer(self.dom_config)
        self.battle_navale_integrator = SierraBattleNavaleIntegrator()
        self.orderflow_analyzer = OrderFlowAnalyzer({})
        
        # Historique signaux
        self.signal_history: List[DOMBattleNavaleSignal] = []
        self.last_signal_time = 0
        
        # Cache
        self._market_data_cache: Dict[str, MarketData] = {}
        self._orderflow_cache: Dict[str, OrderFlowData] = {}
        
        # Statistiques
        self.stats = {
            'total_analyses': 0,
            'signals_generated': 0,
            'confluence_signals': 0,
            'dom_patterns_detected': 0,
            'avg_integration_time_ms': 0.0,
            'signal_accuracy': 0.0
        }
        
        logger.info("🎯 Sierra DOM Integrator initialisé")
    
    async def analyze_integrated_signal(self,
                                       bid_levels: List[Tuple[float, int]],
                                       ask_levels: List[Tuple[float, int]],
                                       market_data: Optional[MarketData] = None,
                                       orderflow_data: Optional[OrderFlowData] = None,
                                       symbol: str = "ES") -> Optional[DOMBattleNavaleSignal]:
        """Analyse signal intégré DOM + Battle Navale + OrderFlow"""
        
        start_time = time.perf_counter()
        
        try:
            # Vérifier limite signaux
            current_time = time.time()
            if self._is_signal_rate_limited(current_time):
                return None
            
            # 1. Analyse DOM
            dom_snapshot = self.dom_analyzer.update_dom(bid_levels, ask_levels, symbol)
            dom_patterns = self.dom_analyzer.analyze_dom_patterns(dom_snapshot)
            
            self.stats['dom_patterns_detected'] += len(dom_patterns)
            
            if not dom_patterns:
                return None  # Pas de patterns DOM détectés
            
            # 2. Analyse Battle Navale (si données disponibles)
            battle_navale_score = 0.0
            if market_data:
                # Utiliser données marché pour Battle Navale
                self._market_data_cache[symbol] = market_data
                
                # Analyser avec Battle Navale (simulation)
                battle_signal = await self._analyze_battle_navale_context(
                    market_data, dom_snapshot, dom_patterns
                )
                battle_navale_score = battle_signal.get('strength', 0.0) if battle_signal else 0.0
            
            # 3. Analyse OrderFlow (si données disponibles)
            orderflow_score = 0.0
            if orderflow_data:
                self._orderflow_cache[symbol] = orderflow_data
                
                orderflow_signal = await self._analyze_orderflow_context(
                    orderflow_data, dom_snapshot, dom_patterns
                )
                orderflow_score = orderflow_signal.get('strength', 0.0) if orderflow_signal else 0.0
            
            # 4. Calcul score intégré
            signal = self._calculate_integrated_signal(
                dom_patterns, battle_navale_score, orderflow_score, 
                dom_snapshot, symbol
            )
            
            # 5. Validation qualité
            if signal and self._validate_signal_quality(signal):
                self.signal_history.append(signal)
                self.last_signal_time = current_time
                self.stats['signals_generated'] += 1
                
                if len(signal.confluence_categories) >= self.integration_config.min_confluence_categories:
                    self.stats['confluence_signals'] += 1
                
                # Mise à jour stats
                analysis_time = (time.perf_counter() - start_time) * 1000
                self._update_stats(analysis_time)
                
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse intégrée DOM: {e}")
            return None
    
    async def _analyze_battle_navale_context(self, 
                                           market_data: MarketData,
                                           dom_snapshot: DOMSnapshot,
                                           dom_patterns: List[DOMPatternSignal]) -> Optional[Dict[str, Any]]:
        """Analyse contexte Battle Navale avec DOM"""
        
        try:
            # Créer contexte enrichi pour Battle Navale
            enhanced_context = {
                'price': market_data.close,
                'volume': market_data.volume,
                'dom_imbalance': dom_snapshot.imbalance_ratio,
                'dom_spread': dom_snapshot.spread,
                'dom_patterns_count': len(dom_patterns),
                'has_iceberg': any('iceberg' in p.pattern_type.value for p in dom_patterns),
                'has_wall': any('wall' in p.pattern_type.value for p in dom_patterns),
                'has_absorption': any('absorption' in p.pattern_type.value for p in dom_patterns)
            }
            
            # Utiliser Battle Navale integrator
            battle_signal = await self.battle_navale_integrator.analyze_signal(
                market_data, enhanced_context
            )
            
            return battle_signal
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse Battle Navale: {e}")
            return None
    
    async def _analyze_orderflow_context(self,
                                       orderflow_data: OrderFlowData,
                                       dom_snapshot: DOMSnapshot, 
                                       dom_patterns: List[DOMPatternSignal]) -> Optional[Dict[str, Any]]:
        """Analyse contexte OrderFlow avec DOM"""
        
        try:
            # Enrichir OrderFlow avec contexte DOM
            dom_context = {
                'dom_imbalance': dom_snapshot.imbalance_ratio,
                'total_dom_size': dom_snapshot.total_bid_size + dom_snapshot.total_ask_size,
                'spread_ticks': dom_snapshot.spread / 0.25,  # ES tick = 0.25
                'iceberg_present': any('iceberg' in p.pattern_type.value for p in dom_patterns),
                'wall_present': any('wall' in p.pattern_type.value for p in dom_patterns)
            }
            
            # Analyser avec OrderFlow analyzer
            analysis = self.orderflow_analyzer.analyze_orderflow(orderflow_data, dom_context)
            
            return {
                'strength': analysis.get('flow_strength', 0.0),
                'direction': analysis.get('flow_direction', 'NEUTRAL'),
                'smart_money_detected': analysis.get('smart_money_score', 0.0) > 0.7
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse OrderFlow: {e}")
            return None
    
    def _calculate_integrated_signal(self,
                                   dom_patterns: List[DOMPatternSignal],
                                   battle_navale_score: float,
                                   orderflow_score: float,
                                   dom_snapshot: DOMSnapshot,
                                   symbol: str) -> Optional[DOMBattleNavaleSignal]:
        """Calcule signal intégré avec pondérations"""
        
        if not dom_patterns:
            return None
        
        # Score DOM basé sur patterns
        dom_score = self._calculate_dom_score(dom_patterns)
        
        # Score intégré pondéré
        integrated_score = (
            dom_score * self.integration_config.dom_weight +
            battle_navale_score * self.integration_config.battle_navale_weight +
            orderflow_score * self.integration_config.orderflow_weight
        )
        
        # Déterminer direction
        signal_direction = self._determine_signal_direction(
            dom_patterns, battle_navale_score, orderflow_score
        )
        
        # Confluence categories
        confluence_categories = self._identify_confluence_categories(
            dom_patterns, battle_navale_score, orderflow_score
        )
        
        # Bonus confluence
        if len(confluence_categories) >= 3:
            integrated_score *= self.integration_config.confluence_bonus_multiplier
        
        # Bonus patterns spéciaux
        integrated_score += self._calculate_pattern_bonus(dom_patterns)
        
        # Confidence
        confidence = min(0.95, integrated_score)
        
        # Niveau de prix principal
        if dom_patterns:
            price_level = np.mean([p.price_level for p in dom_patterns])
        else:
            price_level = (dom_snapshot.best_bid + dom_snapshot.best_ask) / 2
        
        # Time horizon
        time_horizon = self._determine_time_horizon(dom_patterns)
        
        # Reasoning
        reasoning = self._generate_reasoning(
            dom_patterns, battle_navale_score, orderflow_score, confluence_categories
        )
        
        signal = DOMBattleNavaleSignal(
            timestamp=datetime.now(),
            symbol=symbol,
            price_level=price_level,
            dom_patterns=dom_patterns,
            battle_navale_score=battle_navale_score,
            orderflow_score=orderflow_score,
            integrated_score=integrated_score,
            signal_direction=signal_direction,
            confidence=confidence,
            confluence_categories=confluence_categories,
            confluence_strength=len(confluence_categories) / 5.0,  # Max 5 catégories
            time_horizon=time_horizon,
            reasoning=reasoning
        )
        
        return signal
    
    def _calculate_dom_score(self, dom_patterns: List[DOMPatternSignal]) -> float:
        """Calcule score DOM basé sur patterns"""
        
        if not dom_patterns:
            return 0.0
        
        # Pondération par type de pattern
        pattern_weights = {
            'iceberg': 0.8,      # Icebergs = très fort
            'wall': 0.9,         # Murs = très fort
            'ladder': 0.7,       # Ladders = fort
            'absorption': 0.85,   # Absorption = très fort
            'spoofing': 0.6,     # Spoofing = moyen
            'squeeze': 0.75      # Squeeze = fort
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for pattern in dom_patterns:
            # Trouver poids pattern
            pattern_weight = 0.5  # Default
            for key, weight in pattern_weights.items():
                if key in pattern.pattern_type.value:
                    pattern_weight = weight
                    break
            
            # Score pattern = confidence × intensité × poids
            intensity_multiplier = {
                DOMIntensity.EXTREME: 1.0,
                DOMIntensity.HIGH: 0.8,
                DOMIntensity.MEDIUM: 0.6,
                DOMIntensity.LOW: 0.4,
                DOMIntensity.NOISE: 0.2
            }.get(pattern.intensity, 0.5)
            
            pattern_score = pattern.confidence * intensity_multiplier * pattern_weight
            total_score += pattern_score
            total_weight += pattern_weight
        
        return min(1.0, total_score / max(total_weight, 1.0))
    
    def _determine_signal_direction(self,
                                  dom_patterns: List[DOMPatternSignal],
                                  battle_navale_score: float,
                                  orderflow_score: float) -> str:
        """Détermine direction signal"""
        
        bullish_signals = 0
        bearish_signals = 0
        
        # Analyser patterns DOM
        for pattern in dom_patterns:
            if pattern.expected_direction == "BULLISH":
                bullish_signals += 1
            elif pattern.expected_direction == "BEARISH":
                bearish_signals += 1
        
        # Analyser Battle Navale
        if battle_navale_score > 0.6:
            bullish_signals += 1
        elif battle_navale_score < -0.6:
            bearish_signals += 1
        
        # Analyser OrderFlow
        if orderflow_score > 0.6:
            bullish_signals += 1
        elif orderflow_score < -0.6:
            bearish_signals += 1
        
        # Décision
        if bullish_signals > bearish_signals:
            return "BULLISH"
        elif bearish_signals > bullish_signals:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def _identify_confluence_categories(self,
                                      dom_patterns: List[DOMPatternSignal],
                                      battle_navale_score: float,
                                      orderflow_score: float) -> List[str]:
        """Identifie catégories en confluence"""
        
        categories = []
        
        # Catégories DOM
        if any('iceberg' in p.pattern_type.value for p in dom_patterns):
            categories.append("DOM_ICEBERG")
        
        if any('wall' in p.pattern_type.value for p in dom_patterns):
            categories.append("DOM_WALL")
        
        if any('ladder' in p.pattern_type.value for p in dom_patterns):
            categories.append("DOM_LADDER")
        
        if any('absorption' in p.pattern_type.value for p in dom_patterns):
            categories.append("DOM_ABSORPTION")
        
        # Catégories Battle Navale
        if abs(battle_navale_score) > 0.5:
            categories.append("BATTLE_NAVALE")
        
        # Catégories OrderFlow
        if abs(orderflow_score) > 0.5:
            categories.append("ORDERFLOW")
        
        return categories
    
    def _calculate_pattern_bonus(self, dom_patterns: List[DOMPatternSignal]) -> float:
        """Calcule bonus patterns spéciaux"""
        
        bonus = 0.0
        
        for pattern in dom_patterns:
            if 'iceberg' in pattern.pattern_type.value:
                bonus += self.integration_config.iceberg_bonus
            elif 'wall' in pattern.pattern_type.value:
                bonus += self.integration_config.wall_bonus
        
        return min(0.3, bonus)  # Max 30% bonus
    
    def _determine_time_horizon(self, dom_patterns: List[DOMPatternSignal]) -> str:
        """Détermine horizon temporel"""
        
        immediate_patterns = ['ladder', 'squeeze', 'absorption']
        short_patterns = ['iceberg', 'wall']
        
        for pattern in dom_patterns:
            for immediate in immediate_patterns:
                if immediate in pattern.pattern_type.value:
                    return "IMMEDIATE"
        
        for pattern in dom_patterns:
            for short in short_patterns:
                if short in pattern.pattern_type.value:
                    return "SHORT"
        
        return "MEDIUM"
    
    def _generate_reasoning(self,
                          dom_patterns: List[DOMPatternSignal],
                          battle_navale_score: float,
                          orderflow_score: float,
                          confluence_categories: List[str]) -> str:
        """Génère explication signal"""
        
        reasoning_parts = []
        
        # DOM patterns
        if dom_patterns:
            pattern_types = [p.pattern_type.value for p in dom_patterns]
            reasoning_parts.append(f"DOM: {', '.join(pattern_types)}")
        
        # Battle Navale
        if abs(battle_navale_score) > 0.5:
            direction = "haussier" if battle_navale_score > 0 else "baissier"
            reasoning_parts.append(f"Battle Navale {direction} ({battle_navale_score:.2f})")
        
        # OrderFlow
        if abs(orderflow_score) > 0.5:
            direction = "acheteur" if orderflow_score > 0 else "vendeur"
            reasoning_parts.append(f"OrderFlow {direction} ({orderflow_score:.2f})")
        
        # Confluence
        if len(confluence_categories) >= 2:
            reasoning_parts.append(f"Confluence {len(confluence_categories)} signaux")
        
        return " | ".join(reasoning_parts)
    
    def _validate_signal_quality(self, signal: DOMBattleNavaleSignal) -> bool:
        """Valide qualité signal"""
        
        # Seuils minimums
        if signal.integrated_score < self.integration_config.min_integrated_score:
            return False
        
        if signal.confidence < self.integration_config.min_confidence:
            return False
        
        if len(signal.confluence_categories) < self.integration_config.min_confluence_categories:
            return False
        
        return True
    
    def _is_signal_rate_limited(self, current_time: float) -> bool:
        """Vérifie limite taux signaux"""
        
        # Nettoyer signaux anciens
        cutoff_time = current_time - 60  # 1 minute
        recent_signals = [s for s in self.signal_history 
                         if s.timestamp.timestamp() > cutoff_time]
        
        self.signal_history = self.signal_history[-100:]  # Garder 100 derniers
        
        return len(recent_signals) >= self.integration_config.max_signals_per_minute
    
    def _update_stats(self, analysis_time_ms: float):
        """Met à jour statistiques"""
        
        self.stats['total_analyses'] += 1
        
        # Moyenne mobile temps analyse
        current_avg = self.stats['avg_integration_time_ms']
        self.stats['avg_integration_time_ms'] = (current_avg * 0.9 + analysis_time_ms * 0.1)
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """Résumé intégration DOM"""
        
        return {
            'total_analyses': self.stats['total_analyses'],
            'signals_generated': self.stats['signals_generated'],
            'confluence_signals': self.stats['confluence_signals'],
            'dom_patterns_detected': self.stats['dom_patterns_detected'],
            'avg_integration_time_ms': self.stats['avg_integration_time_ms'],
            'signal_accuracy': self.stats['signal_accuracy'],
            'recent_signals_count': len(self.signal_history),
            'config': {
                'min_confluence_categories': self.integration_config.min_confluence_categories,
                'min_integrated_score': self.integration_config.min_integrated_score,
                'dom_weight': self.integration_config.dom_weight,
                'battle_navale_weight': self.integration_config.battle_navale_weight,
                'orderflow_weight': self.integration_config.orderflow_weight
            }
        }

# Factory functions
def create_scalping_dom_integrator() -> SierraDOMIntegrator:
    """Intégrateur DOM pour scalping"""
    dom_config = create_scalping_dom_config()
    
    integration_config = DOMIntegrationConfig()
    integration_config.min_confluence_categories = 2
    integration_config.max_signals_per_minute = 10  # Plus fréquent pour scalping
    integration_config.min_integrated_score = 0.60  # Seuil plus bas
    
    return SierraDOMIntegrator(dom_config, integration_config)

def create_swing_dom_integrator() -> SierraDOMIntegrator:
    """Intégrateur DOM pour swing trading"""
    integration_config = DOMIntegrationConfig()
    integration_config.min_confluence_categories = 3  # Plus strict
    integration_config.max_signals_per_minute = 3     # Moins fréquent
    integration_config.min_integrated_score = 0.75    # Seuil plus élevé
    
    return SierraDOMIntegrator(None, integration_config)

# Export principal
__all__ = [
    'SierraDOMIntegrator',
    'DOMBattleNavaleSignal',
    'DOMIntegrationConfig',
    'create_scalping_dom_integrator',
    'create_swing_dom_integrator'
]
