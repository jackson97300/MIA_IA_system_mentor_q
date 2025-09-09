#!/usr/bin/env python3
"""
📊 SIERRA VIX ANALYZER - Volatility Intelligence Elite
Analyse VIX avancée pour régimes de volatilité et signals trading
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, NamedTuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger
from core.base_types import MarketData

logger = get_logger(__name__)

class VIXRegime(Enum):
    """Régimes de volatilité VIX"""
    ULTRA_LOW = "ultra_low"       # VIX < 12 - Complacence extrême
    LOW = "low"                   # VIX 12-18 - Marché calme
    NORMAL = "normal"             # VIX 18-25 - Volatilité normale
    HIGH = "high"                 # VIX 25-35 - Stress élevé
    EXTREME = "extreme"           # VIX > 35 - Panique
    BACKWARDATION = "backwardation"  # Structure VIX inversée

class VIXSignalType(Enum):
    """Types de signaux VIX"""
    SPIKE_REVERSAL = "spike_reversal"           # Spike VIX = bottom
    COMPLACENCY_WARNING = "complacency_warning" # VIX trop bas = correction
    REGIME_CHANGE = "regime_change"             # Changement régime
    TERM_STRUCTURE = "term_structure"           # Signal structure terme
    MOMENTUM = "momentum"                       # Momentum VIX
    MEAN_REVERSION = "mean_reversion"           # Mean reversion

class VIXTradingImplication(Enum):
    """Implications trading selon VIX"""
    INCREASE_SIZE = "increase_size"             # Augmenter position
    REDUCE_SIZE = "reduce_size"                 # Réduire position
    ADD_HEDGING = "add_hedging"                 # Ajouter hedge
    CONTRARIAN_ENTRY = "contrarian_entry"       # Entrée contraire
    TREND_FOLLOWING = "trend_following"         # Suivre tendance
    DEFENSIVE_ONLY = "defensive_only"           # Mode défensif

@dataclass
class VIXData:
    """Données VIX complètes"""
    timestamp: datetime
    vix_spot: float                    # VIX spot
    vix_9d: Optional[float] = None     # VIX 9 jours
    vix_3m: Optional[float] = None     # VIX 3 mois
    vix_6m: Optional[float] = None     # VIX 6 mois
    
    # Métriques calculées
    vix_percentile: float = 0.0        # Percentile 252 jours
    term_structure: float = 0.0        # VIX_3M / VIX_SPOT
    momentum_5d: float = 0.0           # Momentum 5 jours
    momentum_20d: float = 0.0          # Momentum 20 jours

@dataclass
class VIXSignal:
    """Signal VIX détecté"""
    timestamp: datetime
    signal_type: VIXSignalType
    regime: VIXRegime
    trading_implication: VIXTradingImplication
    
    # Métriques signal
    strength: float                    # Force signal 0-1
    confidence: float                  # Confidence 0-1
    time_horizon: str                  # IMMEDIATE, SHORT, MEDIUM, LONG
    
    # Détails
    vix_level: float
    percentile: float
    reasoning: str
    
    # Paramètres trading
    position_sizing_factor: float = 1.0  # Facteur taille position
    stop_distance_factor: float = 1.0    # Facteur distance stop
    target_distance_factor: float = 1.0  # Facteur distance target

@dataclass
class VIXConfig:
    """Configuration VIX Analyzer"""
    
    # Seuils régimes
    ultra_low_threshold: float = 12.0
    low_threshold: float = 18.0
    normal_threshold: float = 25.0
    high_threshold: float = 35.0
    
    # Périodes analyse
    percentile_period: int = 252       # 1 an pour percentiles
    momentum_short: int = 5            # Momentum court terme
    momentum_long: int = 20            # Momentum long terme
    
    # Seuils signaux
    spike_threshold: float = 0.20      # +20% spike = signal
    complacency_percentile: float = 10.0  # <10% percentile = complacency
    momentum_threshold: float = 0.15   # 15% momentum pour signal
    
    # Performance
    history_size: int = 500            # Historique VIX gardé
    analysis_interval_seconds: int = 60  # Analyse toutes les 60s

class SierraVIXAnalyzer:
    """
    Analyseur VIX Elite pour Sierra Chart
    
    Fonctionnalités:
    ✅ Détection régimes volatilité avancés
    ✅ Signaux VIX multi-timeframe
    ✅ Implications trading automatiques
    ✅ Structure terme VIX
    ✅ Momentum et mean reversion
    ✅ Position sizing adaptatif
    """
    
    def __init__(self, config: Optional[VIXConfig] = None):
        self.config = config or VIXConfig()
        
        # Historiques VIX
        self.vix_history: deque = deque(maxlen=self.config.history_size)
        self.signal_history: deque = deque(maxlen=100)
        
        # État régime actuel
        self.current_regime: Optional[VIXRegime] = None
        self.regime_start_time: Optional[datetime] = None
        self.regime_duration_days = 0
        
        # Cache calculs
        self._percentile_cache: Optional[Tuple[float, float]] = None  # (timestamp, percentile)
        self._last_analysis_time = 0
        
        # Statistiques
        self.stats = {
            'total_vix_updates': 0,
            'signals_generated': defaultdict(int),
            'regime_changes': 0,
            'avg_analysis_time_ms': 0.0,
            'current_regime_duration_days': 0
        }
        
        logger.info("📊 Sierra VIX Analyzer initialisé")
    
    def update_vix_data(self, vix_data: VIXData) -> None:
        """Met à jour les données VIX"""
        
        # Ajouter à l'historique
        self.vix_history.append(vix_data)
        
        # Calculer métriques si données suffisantes
        if len(self.vix_history) >= 20:
            self._calculate_vix_metrics(vix_data)
        
        # Détecter changement régime
        new_regime = self._detect_vix_regime(vix_data)
        if new_regime != self.current_regime:
            self._update_regime(new_regime, vix_data.timestamp)
        
        self.stats['total_vix_updates'] += 1
    
    def analyze_vix_signals(self, vix_data: VIXData, market_context: Optional[Dict] = None) -> List[VIXSignal]:
        """Analyse signaux VIX en temps réel"""
        
        start_time = time.perf_counter()
        
        # Vérifier intervalle d'analyse
        current_time = time.time()
        if current_time - self._last_analysis_time < self.config.analysis_interval_seconds:
            return []
        
        self._last_analysis_time = current_time
        
        # Vérifier fenêtre minimale pour régimes (60 ticks minimum)
        if len(self.vix_history) < 60:
            logger.warning(f"Fenêtre VIX insuffisante: {len(self.vix_history)}/60 ticks - Retour UNKNOWN")
            # Retourner signal UNKNOWN au lieu de FAIL
            unknown_signal = VIXSignal(
                timestamp=datetime.now(),
                signal_type=VIXSignalType.REGIME_CHANGE,
                regime=VIXRegime.NORMAL,  # Régime par défaut
                trading_implication=VIXTradingImplication.DEFENSIVE_ONLY,
                strength=0.0,
                confidence=0.0,
                time_horizon="UNKNOWN",
                vix_level=vix_data.vix_spot if vix_data else 20.0,
                percentile=50.0,
                reasoning="Fenêtre VIX insuffisante pour analyse régime",
                position_sizing_factor=0.5,
                stop_distance_factor=1.5,
                target_distance_factor=0.5
            )
            return [unknown_signal]
        
        signals = []
        
        try:
            # 1. Signal Spike Reversal
            spike_signal = self._detect_spike_reversal(vix_data, market_context)
            if spike_signal:
                signals.append(spike_signal)
            
            # 2. Signal Complacency Warning
            complacency_signal = self._detect_complacency_warning(vix_data, market_context)
            if complacency_signal:
                signals.append(complacency_signal)
            
            # 3. Signal Regime Change
            regime_signal = self._detect_regime_change(vix_data, market_context)
            if regime_signal:
                signals.append(regime_signal)
            
            # 4. Signal Term Structure
            term_signal = self._detect_term_structure_signal(vix_data, market_context)
            if term_signal:
                signals.append(term_signal)
            
            # 5. Signal Momentum
            momentum_signal = self._detect_momentum_signal(vix_data, market_context)
            if momentum_signal:
                signals.append(momentum_signal)
            
            # Mise à jour statistiques
            analysis_time = (time.perf_counter() - start_time) * 1000
            self._update_stats(signals, analysis_time)
            
            # Ajouter à l'historique
            for signal in signals:
                self.signal_history.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse VIX: {e}")
            return []
    
    def _calculate_vix_metrics(self, vix_data: VIXData) -> None:
        """Calcule métriques VIX avancées"""
        
        if len(self.vix_history) < 20:
            return
        
        vix_values = [v.vix_spot for v in self.vix_history]
        
        # Percentile VIX (lookback 252 jours ou disponible)
        lookback = min(len(vix_values), self.config.percentile_period)
        recent_values = vix_values[-lookback:]
        current_vix = vix_data.vix_spot
        
        percentile = (sum(1 for v in recent_values if v <= current_vix) / len(recent_values)) * 100
        vix_data.vix_percentile = percentile
        
        # Momentum court terme (5 jours)
        if len(vix_values) >= self.config.momentum_short + 1:
            short_period = vix_values[-self.config.momentum_short-1:-1]
            vix_data.momentum_5d = (current_vix - np.mean(short_period)) / np.mean(short_period)
        
        # Momentum long terme (20 jours)
        if len(vix_values) >= self.config.momentum_long + 1:
            long_period = vix_values[-self.config.momentum_long-1:-1]
            vix_data.momentum_20d = (current_vix - np.mean(long_period)) / np.mean(long_period)
        
        # Term structure (si VIX 3M disponible)
        if vix_data.vix_3m:
            vix_data.term_structure = vix_data.vix_3m / vix_data.vix_spot
    
    def _detect_vix_regime(self, vix_data: VIXData) -> VIXRegime:
        """Détecte régime VIX actuel"""
        
        vix = vix_data.vix_spot
        
        if vix < self.config.ultra_low_threshold:
            return VIXRegime.ULTRA_LOW
        elif vix < self.config.low_threshold:
            return VIXRegime.LOW
        elif vix < self.config.normal_threshold:
            return VIXRegime.NORMAL
        elif vix < self.config.high_threshold:
            return VIXRegime.HIGH
        else:
            return VIXRegime.EXTREME
    
    def _detect_spike_reversal(self, vix_data: VIXData, market_context: Optional[Dict]) -> Optional[VIXSignal]:
        """Détecte spike VIX = signal bottom"""
        
        if len(self.vix_history) < 5:
            return None
        
        recent_vix = [v.vix_spot for v in list(self.vix_history)[-5:]]
        current_vix = vix_data.vix_spot
        
        # Spike = hausse >20% en 1-3 jours + VIX >25
        if len(recent_vix) >= 3:
            min_recent = min(recent_vix[:-1])
            spike_pct = (current_vix - min_recent) / min_recent
            
            if spike_pct > self.config.spike_threshold and current_vix > 25:
                # Signal contrarian (VIX spike = bottom marché)
                return VIXSignal(
                    timestamp=vix_data.timestamp,
                    signal_type=VIXSignalType.SPIKE_REVERSAL,
                    regime=self.current_regime or self._detect_vix_regime(vix_data),
                    trading_implication=VIXTradingImplication.CONTRARIAN_ENTRY,
                    strength=min(1.0, spike_pct / 0.5),  # Force basée sur amplitude spike
                    confidence=0.75,
                    time_horizon="SHORT",
                    vix_level=current_vix,
                    percentile=vix_data.vix_percentile,
                    reasoning=f"VIX spike +{spike_pct:.1%} vers {current_vix:.1f} - Signal bottom probable",
                    position_sizing_factor=1.5,  # Augmenter taille sur spike
                    stop_distance_factor=0.8,    # Stop plus serré
                    target_distance_factor=1.3   # Target plus généreux
                )
        
        return None
    
    def _detect_complacency_warning(self, vix_data: VIXData, market_context: Optional[Dict]) -> Optional[VIXSignal]:
        """Détecte complacency (VIX trop bas)"""
        
        # VIX <10ème percentile = complacency extrême
        if vix_data.vix_percentile < self.config.complacency_percentile and vix_data.vix_spot < 15:
            
            return VIXSignal(
                timestamp=vix_data.timestamp,
                signal_type=VIXSignalType.COMPLACENCY_WARNING,
                regime=self.current_regime or self._detect_vix_regime(vix_data),
                trading_implication=VIXTradingImplication.ADD_HEDGING,
                strength=1.0 - (vix_data.vix_percentile / 20.0),  # Plus fort si percentile bas
                confidence=0.70,
                time_horizon="MEDIUM",
                vix_level=vix_data.vix_spot,
                percentile=vix_data.vix_percentile,
                reasoning=f"VIX {vix_data.vix_spot:.1f} au {vix_data.vix_percentile:.0f}ème percentile - Complacency extrême",
                position_sizing_factor=0.8,  # Réduire taille
                stop_distance_factor=0.9,    # Stop un peu plus serré
                target_distance_factor=0.8   # Target plus prudent
            )
        
        return None
    
    def _detect_regime_change(self, vix_data: VIXData, market_context: Optional[Dict]) -> Optional[VIXSignal]:
        """Détecte changement régime VIX"""
        
        # Signal seulement si changement récent (<2 jours)
        if (self.regime_start_time and 
            (vix_data.timestamp - self.regime_start_time).days < 2):
            
            # Implications selon nouveau régime
            implications = {
                VIXRegime.ULTRA_LOW: VIXTradingImplication.ADD_HEDGING,
                VIXRegime.LOW: VIXTradingImplication.INCREASE_SIZE,
                VIXRegime.NORMAL: VIXTradingImplication.TREND_FOLLOWING,
                VIXRegime.HIGH: VIXTradingImplication.REDUCE_SIZE,
                VIXRegime.EXTREME: VIXTradingImplication.DEFENSIVE_ONLY
            }
            
            implication = implications.get(self.current_regime, VIXTradingImplication.TREND_FOLLOWING)
            
            return VIXSignal(
                timestamp=vix_data.timestamp,
                signal_type=VIXSignalType.REGIME_CHANGE,
                regime=self.current_regime,
                trading_implication=implication,
                strength=0.8,
                confidence=0.65,
                time_horizon="MEDIUM",
                vix_level=vix_data.vix_spot,
                percentile=vix_data.vix_percentile,
                reasoning=f"Changement régime vers {self.current_regime.value} - VIX {vix_data.vix_spot:.1f}",
                position_sizing_factor=1.0,
                stop_distance_factor=1.0,
                target_distance_factor=1.0
            )
        
        return None
    
    def _detect_term_structure_signal(self, vix_data: VIXData, market_context: Optional[Dict]) -> Optional[VIXSignal]:
        """Détecte signal structure terme VIX"""
        
        if not vix_data.vix_3m or vix_data.term_structure == 0:
            return None
        
        # Backwardation forte = stress marché
        if vix_data.term_structure < 0.9:  # VIX 3M < 90% VIX spot
            return VIXSignal(
                timestamp=vix_data.timestamp,
                signal_type=VIXSignalType.TERM_STRUCTURE,
                regime=self.current_regime or self._detect_vix_regime(vix_data),
                trading_implication=VIXTradingImplication.REDUCE_SIZE,
                strength=1.0 - vix_data.term_structure,
                confidence=0.70,
                time_horizon="SHORT",
                vix_level=vix_data.vix_spot,
                percentile=vix_data.vix_percentile,
                reasoning=f"Backwardation VIX forte - Structure {vix_data.term_structure:.2f}",
                position_sizing_factor=0.7,
                stop_distance_factor=0.8,
                target_distance_factor=0.9
            )
        
        return None
    
    def _detect_momentum_signal(self, vix_data: VIXData, market_context: Optional[Dict]) -> Optional[VIXSignal]:
        """Détecte signal momentum VIX"""
        
        # Momentum fort = continuation probable
        if abs(vix_data.momentum_5d) > self.config.momentum_threshold:
            
            direction = "hausse" if vix_data.momentum_5d > 0 else "baisse"
            implication = (VIXTradingImplication.REDUCE_SIZE if vix_data.momentum_5d > 0 
                          else VIXTradingImplication.INCREASE_SIZE)
            
            return VIXSignal(
                timestamp=vix_data.timestamp,
                signal_type=VIXSignalType.MOMENTUM,
                regime=self.current_regime or self._detect_vix_regime(vix_data),
                trading_implication=implication,
                strength=min(1.0, abs(vix_data.momentum_5d) / 0.5),
                confidence=0.60,
                time_horizon="SHORT",
                vix_level=vix_data.vix_spot,
                percentile=vix_data.vix_percentile,
                reasoning=f"Momentum VIX {direction} fort ({vix_data.momentum_5d:.1%})",
                position_sizing_factor=1.0,
                stop_distance_factor=1.0,
                target_distance_factor=1.0
            )
        
        return None
    
    def _update_regime(self, new_regime: VIXRegime, timestamp: datetime) -> None:
        """Met à jour régime VIX"""
        
        if new_regime != self.current_regime:
            logger.info(f"🔄 Changement régime VIX: {self.current_regime} → {new_regime}")
            
            self.current_regime = new_regime
            self.regime_start_time = timestamp
            self.regime_duration_days = 0
            self.stats['regime_changes'] += 1
        else:
            # Mettre à jour durée
            if self.regime_start_time:
                self.regime_duration_days = (timestamp - self.regime_start_time).days
                self.stats['current_regime_duration_days'] = self.regime_duration_days
    
    def _update_stats(self, signals: List[VIXSignal], analysis_time_ms: float) -> None:
        """Met à jour statistiques"""
        
        for signal in signals:
            self.stats['signals_generated'][signal.signal_type.value] += 1
        
        # Moyenne mobile temps analyse
        current_avg = self.stats['avg_analysis_time_ms']
        self.stats['avg_analysis_time_ms'] = (current_avg * 0.9 + analysis_time_ms * 0.1)
    
    def get_current_regime_info(self) -> Dict[str, Any]:
        """Informations régime VIX actuel"""
        
        if not self.current_regime:
            return {'regime': 'UNKNOWN'}
        
        # Implications trading par régime
        regime_implications = {
            VIXRegime.ULTRA_LOW: {
                'description': 'Complacency extrême - Risque correction',
                'trading_advice': 'Ajouter hedging, réduire leverage',
                'position_sizing': 0.8,
                'risk_level': 'ELEVATED'
            },
            VIXRegime.LOW: {
                'description': 'Marché calme - Conditions favorables',
                'trading_advice': 'Trading normal, opportunités trend',
                'position_sizing': 1.2,
                'risk_level': 'LOW'
            },
            VIXRegime.NORMAL: {
                'description': 'Volatilité normale',
                'trading_advice': 'Trading standard',
                'position_sizing': 1.0,
                'risk_level': 'NORMAL'
            },
            VIXRegime.HIGH: {
                'description': 'Stress élevé - Prudence requise',
                'trading_advice': 'Réduire positions, privilégier hedging',
                'position_sizing': 0.7,
                'risk_level': 'HIGH'
            },
            VIXRegime.EXTREME: {
                'description': 'Panique - Opportunités contrarian',
                'trading_advice': 'Position sizing minimal, chercher bottoms',
                'position_sizing': 0.5,
                'risk_level': 'EXTREME'
            }
        }
        
        regime_info = regime_implications.get(self.current_regime, {})
        
        return {
            'regime': self.current_regime.value,
            'duration_days': self.regime_duration_days,
            'description': regime_info.get('description', ''),
            'trading_advice': regime_info.get('trading_advice', ''),
            'position_sizing_factor': regime_info.get('position_sizing', 1.0),
            'risk_level': regime_info.get('risk_level', 'UNKNOWN')
        }
    
    def get_vix_summary(self) -> Dict[str, Any]:
        """Résumé analyse VIX"""
        
        recent_vix = self.vix_history[-1] if self.vix_history else None
        
        return {
            'current_vix': recent_vix.vix_spot if recent_vix else None,
            'current_percentile': recent_vix.vix_percentile if recent_vix else None,
            'current_regime': self.current_regime.value if self.current_regime else None,
            'regime_duration_days': self.regime_duration_days,
            'total_vix_updates': self.stats['total_vix_updates'],
            'signals_generated': dict(self.stats['signals_generated']),
            'regime_changes': self.stats['regime_changes'],
            'avg_analysis_time_ms': self.stats['avg_analysis_time_ms'],
            'recent_signals_count': len(self.signal_history)
        }

# Factory functions
def create_scalping_vix_config() -> VIXConfig:
    """Configuration VIX pour scalping"""
    config = VIXConfig()
    config.analysis_interval_seconds = 30    # Plus fréquent
    config.spike_threshold = 0.15            # Seuils plus sensibles
    config.momentum_threshold = 0.10
    return config

def create_swing_vix_config() -> VIXConfig:
    """Configuration VIX pour swing trading"""
    config = VIXConfig()
    config.analysis_interval_seconds = 300   # 5 minutes
    config.spike_threshold = 0.25            # Seuils plus élevés
    config.momentum_threshold = 0.20
    return config

# Export principal
__all__ = [
    'SierraVIXAnalyzer',
    'VIXConfig',
    'VIXData',
    'VIXSignal',
    'VIXRegime',
    'VIXSignalType',
    'VIXTradingImplication',
    'create_scalping_vix_config',
    'create_swing_vix_config'
]


