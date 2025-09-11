#!/usr/bin/env python3
"""
🎯 SIERRA VIX + DOM INTEGRATOR
Intégration complète VIX + DOM + Battle Navale pour signaux Elite
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

from features.sierra_vix_analyzer import (
    SierraVIXAnalyzer, VIXConfig, VIXData, VIXSignal, VIXRegime, 
    VIXTradingImplication, create_scalping_vix_config
)
from features.sierra_dom_integrator import (
    SierraDOMIntegrator, DOMBattleNavaleSignal, DOMIntegrationConfig
)
from features.sierra_dom_analyzer import DOMConfig
from core.base_types import MarketData, OrderFlowData
from core.logger import get_logger

logger = get_logger(__name__)

@dataclass
class VIXDOMSignal:
    """Signal intégré VIX + DOM + Battle Navale"""
    timestamp: datetime
    symbol: str
    price_level: float
    
    # Composants signaux
    vix_signals: List[VIXSignal] = field(default_factory=list)
    dom_signal: Optional[DOMBattleNavaleSignal] = None
    
    # Scores individuels
    vix_score: float = 0.0
    dom_score: float = 0.0
    volatility_regime_score: float = 0.0
    
    # Score final Elite
    elite_score: float = 0.0
    signal_direction: str = "NEUTRAL"  # BULLISH, BEARISH, NEUTRAL
    confidence: float = 0.0
    
    # Contexte VIX
    vix_regime: VIXRegime = VIXRegime.NORMAL
    vix_level: float = 0.0
    vix_percentile: float = 50.0
    
    # Implications trading
    position_sizing_factor: float = 1.0
    stop_distance_factor: float = 1.0
    target_distance_factor: float = 1.0
    trading_implication: VIXTradingImplication = VIXTradingImplication.TREND_FOLLOWING
    
    # Métadonnées Elite
    confluence_strength: float = 0.0
    time_horizon: str = "SHORT"
    reasoning: str = ""
    risk_level: str = "NORMAL"

@dataclass
class VIXDOMConfig:
    """Configuration intégration VIX + DOM"""
    
    # Pondérations signaux
    vix_weight: float = 0.30              # 30% VIX
    dom_weight: float = 0.45              # 45% DOM 
    volatility_regime_weight: float = 0.25  # 25% Régime volatilité
    
    # Seuils Elite
    min_elite_score: float = 0.70         # Score min pour signal Elite
    min_confidence: float = 0.65          # Confidence min
    min_confluence_strength: float = 0.50  # Force confluence min
    
    # Bonus spéciaux
    vix_spike_bonus: float = 0.15         # +15% si VIX spike
    extreme_vol_bonus: float = 0.20       # +20% si volatilité extrême
    complacency_penalty: float = -0.10    # -10% si complacency
    
    # Gestion signaux
    max_signals_per_hour: int = 6         # Max 6 signaux/heure
    signal_timeout_minutes: int = 30      # Timeout 30min

class SierraVIXDOMIntegrator:
    """
    Intégrateur Elite VIX + DOM pour Sierra Chart
    
    Fonctionnalités:
    ✅ Fusion VIX + DOM + Battle Navale + OrderFlow
    ✅ Scoring Elite multi-facteurs
    ✅ Régimes volatilité adaptatifs
    ✅ Position sizing intelligent
    ✅ Risk management automatique
    ✅ Signaux haute probabilité uniquement
    """
    
    def __init__(self,
                 vix_config: Optional[VIXConfig] = None,
                 dom_config: Optional[DOMConfig] = None,
                 integration_config: Optional[VIXDOMConfig] = None):
        
        self.vix_config = vix_config or create_scalping_vix_config()
        self.integration_config = integration_config or VIXDOMConfig()
        
        # Composants d'analyse
        self.vix_analyzer = SierraVIXAnalyzer(self.vix_config)
        self.dom_integrator = SierraDOMIntegrator(dom_config=dom_config)
        
        # Historique signaux Elite
        self.elite_signals: List[VIXDOMSignal] = []
        self.last_signal_time = 0
        
        # Cache contexte marché
        self._market_context: Dict[str, Any] = {}
        self._vix_context: Dict[str, Any] = {}
        
        # Statistiques Elite
        self.stats = {
            'total_analyses': 0,
            'elite_signals_generated': 0,
            'vix_signals_processed': 0,
            'dom_signals_processed': 0,
            'confluence_signals': 0,
            'avg_elite_score': 0.0,
            'avg_integration_time_ms': 0.0,
            'regime_distribution': {},
            'performance_tracking': []
        }
        
        logger.info("🎯 Sierra VIX + DOM Integrator Elite initialisé")
    
    async def analyze_elite_signal(self,
                                  # DOM données
                                  bid_levels: List[Tuple[float, int]],
                                  ask_levels: List[Tuple[float, int]],
                                  # Contexte marché
                                  market_data: Optional[MarketData] = None,
                                  orderflow_data: Optional[OrderFlowData] = None,
                                  # VIX données
                                  vix_data: Optional[VIXData] = None,
                                  symbol: str = "ES") -> Optional[VIXDOMSignal]:
        """Analyse signal Elite VIX + DOM intégré"""
        
        start_time = time.perf_counter()
        
        try:
            # Vérifier limite signaux
            current_time = time.time()
            if self._is_signal_rate_limited(current_time):
                return None
            
            # 1. Analyse VIX (si données disponibles)
            vix_signals = []
            vix_regime_info = {}
            
            if vix_data:
                self.vix_analyzer.update_vix_data(vix_data)
                vix_signals = self.vix_analyzer.analyze_vix_signals(vix_data, self._market_context)
                vix_regime_info = self.vix_analyzer.get_current_regime_info()
                
                self.stats['vix_signals_processed'] += len(vix_signals)
            
            # 2. Analyse DOM + Battle Navale + OrderFlow
            dom_signal = await self.dom_integrator.analyze_integrated_signal(
                bid_levels, ask_levels, market_data, orderflow_data, symbol
            )
            
            if dom_signal:
                self.stats['dom_signals_processed'] += 1
            
            # 3. Calcul signal Elite intégré
            elite_signal = self._calculate_elite_signal(
                vix_signals, dom_signal, vix_data, vix_regime_info, 
                market_data, symbol
            )
            
            # 4. Validation Elite
            if elite_signal and self._validate_elite_quality(elite_signal):
                self.elite_signals.append(elite_signal)
                self.last_signal_time = current_time
                self.stats['elite_signals_generated'] += 1
                
                # Tracking confluence
                if elite_signal.confluence_strength >= self.integration_config.min_confluence_strength:
                    self.stats['confluence_signals'] += 1
                
                # Mise à jour stats
                analysis_time = (time.perf_counter() - start_time) * 1000
                self._update_elite_stats(elite_signal, analysis_time)
                
                return elite_signal
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse Elite VIX+DOM: {e}")
            return None
    
    def _calculate_elite_signal(self,
                               vix_signals: List[VIXSignal],
                               dom_signal: Optional[DOMBattleNavaleSignal],
                               vix_data: Optional[VIXData],
                               vix_regime_info: Dict[str, Any],
                               market_data: Optional[MarketData],
                               symbol: str) -> Optional[VIXDOMSignal]:
        """Calcule signal Elite intégré"""
        
        # Score VIX
        vix_score = self._calculate_vix_score(vix_signals, vix_data, vix_regime_info)
        
        # Score DOM
        dom_score = dom_signal.integrated_score if dom_signal else 0.0
        
        # Score régime volatilité
        volatility_regime_score = self._calculate_volatility_regime_score(vix_regime_info, vix_data)
        
        # Score Elite pondéré
        elite_score = (
            vix_score * self.integration_config.vix_weight +
            dom_score * self.integration_config.dom_weight +
            volatility_regime_score * self.integration_config.volatility_regime_weight
        )
        
        # Bonus/Penalty spéciaux
        elite_score += self._calculate_special_adjustments(vix_signals, vix_data, vix_regime_info)
        
        # Direction signal
        signal_direction = self._determine_elite_direction(
            vix_signals, dom_signal, vix_regime_info
        )
        
        # Confluence
        confluence_strength = self._calculate_confluence_strength(
            vix_signals, dom_signal, vix_regime_info
        )
        
        # Confidence
        confidence = min(0.95, elite_score * confluence_strength)
        
        # Niveau prix
        if dom_signal:
            price_level = dom_signal.price_level
        elif market_data:
            price_level = market_data.close
        else:
            price_level = 5000.0  # Default ES
        
        # Paramètres trading
        position_sizing, stop_factor, target_factor = self._calculate_trading_parameters(
            vix_signals, vix_regime_info, elite_score
        )
        
        # Trading implication
        trading_implication = self._determine_trading_implication(
            vix_signals, dom_signal, vix_regime_info
        )
        
        # Time horizon
        time_horizon = self._determine_time_horizon(vix_signals, dom_signal)
        
        # Risk level
        risk_level = vix_regime_info.get('risk_level', 'NORMAL')
        
        # Reasoning
        reasoning = self._generate_elite_reasoning(
            vix_signals, dom_signal, vix_regime_info, confluence_strength
        )
        
        elite_signal = VIXDOMSignal(
            timestamp=datetime.now(),
            symbol=symbol,
            price_level=price_level,
            vix_signals=vix_signals,
            dom_signal=dom_signal,
            vix_score=vix_score,
            dom_score=dom_score,
            volatility_regime_score=volatility_regime_score,
            elite_score=elite_score,
            signal_direction=signal_direction,
            confidence=confidence,
            vix_regime=VIXRegime(vix_regime_info.get('regime', 'normal')) if vix_regime_info.get('regime') else VIXRegime.NORMAL,
            vix_level=vix_data.vix_spot if vix_data else 20.0,
            vix_percentile=vix_data.vix_percentile if vix_data else 50.0,
            position_sizing_factor=position_sizing,
            stop_distance_factor=stop_factor,
            target_distance_factor=target_factor,
            trading_implication=trading_implication,
            confluence_strength=confluence_strength,
            time_horizon=time_horizon,
            reasoning=reasoning,
            risk_level=risk_level
        )
        
        return elite_signal
    
    def _calculate_vix_score(self, 
                            vix_signals: List[VIXSignal],
                            vix_data: Optional[VIXData],
                            vix_regime_info: Dict[str, Any]) -> float:
        """Calcule score VIX"""
        
        if not vix_signals:
            return 0.0
        
        # Score basé sur force des signaux VIX
        signal_scores = [signal.strength * signal.confidence for signal in vix_signals]
        base_score = np.mean(signal_scores) if signal_scores else 0.0
        
        # Ajustement selon régime
        regime_multiplier = {
            'ultra_low': 0.8,    # Réduire score en complacency
            'low': 1.0,
            'normal': 1.0,
            'high': 1.2,         # Augmenter score en stress
            'extreme': 1.5       # Maximum en panique
        }
        
        regime = vix_regime_info.get('regime', 'normal')
        multiplier = regime_multiplier.get(regime, 1.0)
        
        return min(1.0, base_score * multiplier)
    
    def _calculate_volatility_regime_score(self,
                                         vix_regime_info: Dict[str, Any],
                                         vix_data: Optional[VIXData]) -> float:
        """Calcule score régime volatilité"""
        
        if not vix_regime_info:
            return 0.5  # Neutre
        
        # Score selon régime actuel
        regime_scores = {
            'ultra_low': 0.3,    # Défavorable (complacency)
            'low': 0.7,         # Favorable (conditions calmes)
            'normal': 0.6,      # Standard
            'high': 0.8,        # Favorable (opportunités)
            'extreme': 0.9      # Très favorable (contrarian)
        }
        
        regime = vix_regime_info.get('regime', 'normal')
        base_score = regime_scores.get(regime, 0.5)
        
        # Ajustement selon durée dans régime
        duration_days = vix_regime_info.get('duration_days', 0)
        if duration_days > 30:  # Régime stable
            base_score *= 1.1
        elif duration_days < 3:  # Transition récente
            base_score *= 0.9
        
        return min(1.0, base_score)
    
    def _calculate_special_adjustments(self,
                                     vix_signals: List[VIXSignal],
                                     vix_data: Optional[VIXData],
                                     vix_regime_info: Dict[str, Any]) -> float:
        """Calcule ajustements spéciaux"""
        
        adjustment = 0.0
        
        # Bonus VIX spike
        spike_signals = [s for s in vix_signals if 'spike' in s.signal_type.value]
        if spike_signals:
            adjustment += self.integration_config.vix_spike_bonus
        
        # Bonus volatilité extrême
        if vix_regime_info.get('regime') == 'extreme':
            adjustment += self.integration_config.extreme_vol_bonus
        
        # Penalty complacency
        if vix_regime_info.get('regime') == 'ultra_low':
            adjustment += self.integration_config.complacency_penalty
        
        return adjustment
    
    def _determine_elite_direction(self,
                                  vix_signals: List[VIXSignal],
                                  dom_signal: Optional[DOMBattleNavaleSignal],
                                  vix_regime_info: Dict[str, Any]) -> str:
        """Détermine direction signal Elite"""
        
        bullish_votes = 0
        bearish_votes = 0
        
        # Votes VIX
        for signal in vix_signals:
            if signal.trading_implication in [VIXTradingImplication.CONTRARIAN_ENTRY, VIXTradingImplication.INCREASE_SIZE]:
                if signal.signal_type.value == 'spike_reversal':
                    bullish_votes += 2  # Spike VIX = bullish contrarian
                else:
                    bullish_votes += 1
            elif signal.trading_implication in [VIXTradingImplication.REDUCE_SIZE, VIXTradingImplication.ADD_HEDGING]:
                bearish_votes += 1
        
        # Votes DOM
        if dom_signal:
            if dom_signal.signal_direction == "BULLISH":
                bullish_votes += 2
            elif dom_signal.signal_direction == "BEARISH":
                bearish_votes += 2
        
        # Décision
        if bullish_votes > bearish_votes:
            return "BULLISH"
        elif bearish_votes > bullish_votes:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def _calculate_confluence_strength(self,
                                     vix_signals: List[VIXSignal],
                                     dom_signal: Optional[DOMBattleNavaleSignal],
                                     vix_regime_info: Dict[str, Any]) -> float:
        """Calcule force confluence"""
        
        confluence_factors = 0
        max_factors = 5
        
        # Facteur 1: Signaux VIX multiples
        if len(vix_signals) >= 2:
            confluence_factors += 1
        
        # Facteur 2: Signal DOM fort
        if dom_signal and dom_signal.integrated_score > 0.7:
            confluence_factors += 1
        
        # Facteur 3: Régime volatilité favorable
        favorable_regimes = ['high', 'extreme', 'low']
        if vix_regime_info.get('regime') in favorable_regimes:
            confluence_factors += 1
        
        # Facteur 4: Confluence DOM multi-patterns
        if dom_signal and len(dom_signal.confluence_categories) >= 3:
            confluence_factors += 1
        
        # Facteur 5: Timing favorable (nouveaux régimes)
        if vix_regime_info.get('duration_days', 0) < 5:
            confluence_factors += 1
        
        return confluence_factors / max_factors
    
    def _calculate_trading_parameters(self,
                                    vix_signals: List[VIXSignal],
                                    vix_regime_info: Dict[str, Any],
                                    elite_score: float) -> Tuple[float, float, float]:
        """Calcule paramètres trading adaptatifs"""
        
        # Position sizing selon régime VIX
        regime_sizing = vix_regime_info.get('position_sizing_factor', 1.0)
        
        # Ajustement selon signaux VIX
        vix_sizing_avg = 1.0
        if vix_signals:
            vix_sizings = [s.position_sizing_factor for s in vix_signals]
            vix_sizing_avg = np.mean(vix_sizings)
        
        # Position sizing final
        position_sizing = min(2.0, max(0.3, regime_sizing * vix_sizing_avg * elite_score))
        
        # Stop distance (serré en volatilité haute)
        stop_factor = 1.0
        if vix_regime_info.get('regime') in ['high', 'extreme']:
            stop_factor = 0.8
        elif vix_regime_info.get('regime') == 'ultra_low':
            stop_factor = 1.2
        
        # Target distance (généreux en volatilité extrême)
        target_factor = 1.0
        if vix_regime_info.get('regime') == 'extreme':
            target_factor = 1.5
        elif vix_regime_info.get('regime') == 'ultra_low':
            target_factor = 0.8
        
        return position_sizing, stop_factor, target_factor
    
    def _determine_trading_implication(self,
                                     vix_signals: List[VIXSignal],
                                     dom_signal: Optional[DOMBattleNavaleSignal],
                                     vix_regime_info: Dict[str, Any]) -> VIXTradingImplication:
        """Détermine implication trading"""
        
        # Prioriser signaux VIX spéciaux
        for signal in vix_signals:
            if signal.signal_type.value == 'spike_reversal':
                return VIXTradingImplication.CONTRARIAN_ENTRY
            elif signal.signal_type.value == 'complacency_warning':
                return VIXTradingImplication.ADD_HEDGING
        
        # Selon régime général
        regime = vix_regime_info.get('regime', 'normal')
        regime_implications = {
            'ultra_low': VIXTradingImplication.ADD_HEDGING,
            'low': VIXTradingImplication.INCREASE_SIZE,
            'normal': VIXTradingImplication.TREND_FOLLOWING,
            'high': VIXTradingImplication.REDUCE_SIZE,
            'extreme': VIXTradingImplication.CONTRARIAN_ENTRY
        }
        
        return regime_implications.get(regime, VIXTradingImplication.TREND_FOLLOWING)
    
    def _determine_time_horizon(self,
                              vix_signals: List[VIXSignal],
                              dom_signal: Optional[DOMBattleNavaleSignal]) -> str:
        """Détermine horizon temporel"""
        
        # Prioriser signaux immédiats
        for signal in vix_signals:
            if signal.time_horizon == "IMMEDIATE":
                return "IMMEDIATE"
        
        if dom_signal and dom_signal.time_horizon == "IMMEDIATE":
            return "IMMEDIATE"
        
        # Majoritairement court terme
        horizons = []
        for signal in vix_signals:
            horizons.append(signal.time_horizon)
        
        if dom_signal:
            horizons.append(dom_signal.time_horizon)
        
        if horizons.count("SHORT") > len(horizons) / 2:
            return "SHORT"
        elif horizons.count("MEDIUM") > len(horizons) / 2:
            return "MEDIUM"
        else:
            return "SHORT"  # Default
    
    def _generate_elite_reasoning(self,
                                 vix_signals: List[VIXSignal],
                                 dom_signal: Optional[DOMBattleNavaleSignal],
                                 vix_regime_info: Dict[str, Any],
                                 confluence_strength: float) -> str:
        """Génère explication signal Elite"""
        
        reasoning_parts = []
        
        # VIX context
        regime = vix_regime_info.get('regime', 'normal')
        reasoning_parts.append(f"VIX régime {regime}")
        
        # VIX signals
        if vix_signals:
            signal_types = [s.signal_type.value for s in vix_signals]
            reasoning_parts.append(f"VIX signaux: {', '.join(signal_types)}")
        
        # DOM signal
        if dom_signal:
            reasoning_parts.append(f"DOM score {dom_signal.integrated_score:.2f}")
            if dom_signal.confluence_categories:
                reasoning_parts.append(f"Confluence {len(dom_signal.confluence_categories)} patterns")
        
        # Confluence finale
        reasoning_parts.append(f"Confluence Elite {confluence_strength:.1%}")
        
        return " | ".join(reasoning_parts)
    
    def _validate_elite_quality(self, signal: VIXDOMSignal) -> bool:
        """Valide qualité signal Elite"""
        
        # Seuils Elite stricts
        if signal.elite_score < self.integration_config.min_elite_score:
            return False
        
        if signal.confidence < self.integration_config.min_confidence:
            return False
        
        if signal.confluence_strength < self.integration_config.min_confluence_strength:
            return False
        
        return True
    
    def _is_signal_rate_limited(self, current_time: float) -> bool:
        """Vérifie limite taux signaux Elite"""
        
        # Nettoyer signaux anciens (1 heure)
        cutoff_time = current_time - 3600
        recent_signals = [s for s in self.elite_signals 
                         if s.timestamp.timestamp() > cutoff_time]
        
        self.elite_signals = self.elite_signals[-50:]  # Garder 50 derniers
        
        return len(recent_signals) >= self.integration_config.max_signals_per_hour
    
    def _update_elite_stats(self, signal: VIXDOMSignal, analysis_time_ms: float):
        """Met à jour statistiques Elite"""
        
        self.stats['total_analyses'] += 1
        
        # Score Elite moyen
        current_avg = self.stats['avg_elite_score']
        self.stats['avg_elite_score'] = (current_avg * 0.9 + signal.elite_score * 0.1)
        
        # Temps analyse moyen
        current_avg_time = self.stats['avg_integration_time_ms']
        self.stats['avg_integration_time_ms'] = (current_avg_time * 0.9 + analysis_time_ms * 0.1)
        
        # Distribution régimes
        regime = signal.vix_regime.value
        if regime not in self.stats['regime_distribution']:
            self.stats['regime_distribution'][regime] = 0
        self.stats['regime_distribution'][regime] += 1
    
    def get_elite_summary(self) -> Dict[str, Any]:
        """Résumé Elite VIX + DOM"""
        
        return {
            'total_analyses': self.stats['total_analyses'],
            'elite_signals_generated': self.stats['elite_signals_generated'],
            'vix_signals_processed': self.stats['vix_signals_processed'],
            'dom_signals_processed': self.stats['dom_signals_processed'],
            'confluence_signals': self.stats['confluence_signals'],
            'avg_elite_score': self.stats['avg_elite_score'],
            'avg_integration_time_ms': self.stats['avg_integration_time_ms'],
            'regime_distribution': dict(self.stats['regime_distribution']),
            'recent_elite_signals': len(self.elite_signals),
            'current_vix_regime': self.vix_analyzer.current_regime.value if self.vix_analyzer.current_regime else None,
            'vix_summary': self.vix_analyzer.get_vix_summary(),
            'dom_summary': self.dom_integrator.get_integration_summary()
        }

# Factory functions
def create_scalping_vix_dom_integrator() -> SierraVIXDOMIntegrator:
    """Intégrateur VIX+DOM pour scalping"""
    from features.sierra_dom_analyzer import create_scalping_dom_config
    
    vix_config = create_scalping_vix_config()
    dom_config = create_scalping_dom_config()
    
    integration_config = VIXDOMConfig()
    integration_config.max_signals_per_hour = 12  # Plus fréquent
    integration_config.min_elite_score = 0.65     # Seuil plus bas
    
    return SierraVIXDOMIntegrator(vix_config, dom_config, integration_config)

def create_professional_vix_dom_integrator() -> SierraVIXDOMIntegrator:
    """Intégrateur VIX+DOM professionnel"""
    integration_config = VIXDOMConfig()
    integration_config.max_signals_per_hour = 6   # Moins fréquent
    integration_config.min_elite_score = 0.75     # Seuil plus élevé
    integration_config.min_confidence = 0.70      # Plus strict
    
    return SierraVIXDOMIntegrator(None, None, integration_config)

# Export principal
__all__ = [
    'SierraVIXDOMIntegrator',
    'VIXDOMSignal',
    'VIXDOMConfig',
    'create_scalping_vix_dom_integrator',
    'create_professional_vix_dom_integrator'
]
