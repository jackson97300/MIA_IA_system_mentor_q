#!/usr/bin/env python3
"""
📊 SIERRA DOM ANALYZER - Depth of Market Elite
Analyse avancée du DOM (Depth of Market) avec détection Smart Money
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, NamedTuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger
from core.base_types import MarketData

logger = get_logger(__name__)

class DOMPattern(Enum):
    """Patterns DOM détectés"""
    ICEBERG_BID = "iceberg_bid"               # Iceberg côté achat
    ICEBERG_ASK = "iceberg_ask"               # Iceberg côté vente
    WALL_BID = "wall_bid"                     # Mur achat (support)
    WALL_ASK = "wall_ask"                     # Mur vente (résistance)
    LADDER_BID = "ladder_bid"                 # Échelle achat agressive
    LADDER_ASK = "ladder_ask"                 # Échelle vente agressive
    SPOOFING_BID = "spoofing_bid"             # Spoofing côté achat
    SPOOFING_ASK = "spoofing_ask"             # Spoofing côté vente
    ABSORPTION_BID = "absorption_bid"         # Absorption côté achat
    ABSORPTION_ASK = "absorption_ask"         # Absorption côté vente
    SQUEEZE_UP = "squeeze_up"                 # Squeeze vers le haut
    SQUEEZE_DOWN = "squeeze_down"             # Squeeze vers le bas

class DOMIntensity(Enum):
    """Intensité patterns DOM"""
    EXTREME = "extreme"           # 95-100% - Pattern extrême
    HIGH = "high"                # 85-94% - Pattern fort
    MEDIUM = "medium"            # 70-84% - Pattern moyen
    LOW = "low"                  # 50-69% - Pattern faible
    NOISE = "noise"              # <50% - Bruit de marché

@dataclass
class DOMLevel:
    """Niveau DOM individuel"""
    price: float
    size: int
    orders_count: int = 1        # Nombre d'ordres à ce niveau
    avg_order_size: float = 0.0  # Taille moyenne ordre
    first_seen: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)
    updates_count: int = 1       # Nombre de mises à jour
    
    def __post_init__(self):
        if self.avg_order_size == 0.0:
            self.avg_order_size = self.size / max(self.orders_count, 1)

@dataclass
class DOMSnapshot:
    """Snapshot complet DOM"""
    timestamp: datetime
    symbol: str
    bid_levels: List[DOMLevel] = field(default_factory=list)
    ask_levels: List[DOMLevel] = field(default_factory=list)
    
    # Métriques calculées
    total_bid_size: int = 0
    total_ask_size: int = 0
    best_bid: float = 0.0
    best_ask: float = 0.0
    spread: float = 0.0
    imbalance_ratio: float = 0.5  # 0.0=100% ask, 1.0=100% bid, 0.5=équilibré
    
    # Niveaux significatifs
    max_bid_level: Optional[DOMLevel] = None
    max_ask_level: Optional[DOMLevel] = None
    wall_levels: List[DOMLevel] = field(default_factory=list)

@dataclass
class DOMPatternSignal:
    """Signal pattern DOM détecté"""
    timestamp: datetime
    pattern_type: DOMPattern
    intensity: DOMIntensity
    price_level: float
    size_involved: int
    confidence: float             # 0.0-1.0
    expected_direction: str       # "BULLISH", "BEARISH", "NEUTRAL"
    time_horizon: str            # "IMMEDIATE", "SHORT", "MEDIUM"
    reasoning: str
    
    # Métadonnées pattern
    levels_count: int = 1
    duration_seconds: float = 0.0
    volume_impact: float = 0.0

@dataclass
class DOMConfig:
    """Configuration DOM Analyzer"""
    
    # Profondeur analyse
    max_levels_analyzed: int = 10         # Niveaux max analysés
    min_size_threshold: int = 50          # Taille minimum significative
    
    # Détection patterns
    iceberg_threshold: int = 500          # Seuil détection iceberg
    wall_threshold: int = 1000            # Seuil détection mur
    spoofing_detection_enabled: bool = True
    absorption_analysis_enabled: bool = True
    
    # Performance
    analysis_interval_ms: int = 250       # 250ms entre analyses
    dom_history_size: int = 100           # Historique DOM gardé
    pattern_timeout_seconds: int = 300    # Timeout patterns (5min)
    
    # Seuils avancés
    imbalance_threshold: float = 0.7      # 70% imbalance significatif
    size_anomaly_multiplier: float = 3.0  # 3x taille moyenne = anomalie
    ladder_min_levels: int = 3            # Minimum niveaux pour ladder

class SierraDOMAnalyzer:
    """
    Analyseur DOM (Depth of Market) Elite pour Sierra Chart
    
    Fonctionnalités:
    ✅ Détection icebergs & murs en temps réel
    ✅ Analyse absorption & spoofing
    ✅ Patterns ladder & squeeze
    ✅ Scoring Smart Money intensity
    ✅ Prédictions direction court terme
    ✅ Performance <5ms par analyse
    """
    
    def __init__(self, config: Optional[DOMConfig] = None):
        self.config = config or DOMConfig()
        
        # Historique DOM
        self.dom_history: deque = deque(maxlen=self.config.dom_history_size)
        self.pattern_history: deque = deque(maxlen=200)
        
        # Cache niveaux
        self.level_tracking: Dict[float, DOMLevel] = {}
        self.last_analysis_time = 0
        
        # Statistiques
        self.stats = {
            'total_snapshots_analyzed': 0,
            'patterns_detected': defaultdict(int),
            'avg_analysis_time_ms': 0.0,
            'icebergs_detected': 0,
            'walls_detected': 0,
            'spoofing_detected': 0,
            'absorption_events': 0
        }
        
        logger.info("📊 Sierra DOM Analyzer initialisé")
    
    def update_dom(self, bid_levels: List[Tuple[float, int]], 
                   ask_levels: List[Tuple[float, int]], 
                   symbol: str = "ES") -> DOMSnapshot:
        """Mise à jour DOM avec nouvelles données"""
        
        timestamp = datetime.now()
        
        # Convertir en DOMLevel
        bid_dom_levels = []
        for price, size in bid_levels[:self.config.max_levels_analyzed]:
            if size >= self.config.min_size_threshold:
                level = DOMLevel(price=price, size=size)
                bid_dom_levels.append(level)
        
        ask_dom_levels = []
        for price, size in ask_levels[:self.config.max_levels_analyzed]:
            if size >= self.config.min_size_threshold:
                level = DOMLevel(price=price, size=size)
                ask_dom_levels.append(level)
        
        # Créer snapshot
        snapshot = DOMSnapshot(
            timestamp=timestamp,
            symbol=symbol,
            bid_levels=bid_dom_levels,
            ask_levels=ask_dom_levels
        )
        
        # Calculer métriques
        self._calculate_snapshot_metrics(snapshot)
        
        # Ajouter à l'historique
        self.dom_history.append(snapshot)
        
        return snapshot
    
    def analyze_dom_patterns(self, snapshot: DOMSnapshot) -> List[DOMPatternSignal]:
        """Analyse patterns DOM en temps réel"""
        
        start_time = time.perf_counter()
        
        # Vérifier intervalle d'analyse
        current_time = time.time() * 1000
        if current_time - self.last_analysis_time < self.config.analysis_interval_ms:
            return []
        
        self.last_analysis_time = current_time
        
        if len(self.dom_history) < 3:
            return []
        
        patterns_detected = []
        
        try:
            # 1. Détection icebergs
            icebergs = self._detect_icebergs(snapshot)
            patterns_detected.extend(icebergs)
            
            # 2. Détection murs
            walls = self._detect_walls(snapshot)
            patterns_detected.extend(walls)
            
            # 3. Détection ladders
            ladders = self._detect_ladders(snapshot)
            patterns_detected.extend(ladders)
            
            # 4. Détection spoofing
            if self.config.spoofing_detection_enabled:
                spoofing = self._detect_spoofing(snapshot)
                patterns_detected.extend(spoofing)
            
            # 5. Détection absorption
            if self.config.absorption_analysis_enabled:
                absorption = self._detect_absorption(snapshot)
                patterns_detected.extend(absorption)
            
            # 6. Détection squeeze
            squeeze = self._detect_squeeze(snapshot)
            patterns_detected.extend(squeeze)
            
            # Mise à jour statistiques
            analysis_time = (time.perf_counter() - start_time) * 1000
            self._update_stats(patterns_detected, analysis_time)
            
            # Ajouter à l'historique
            for pattern in patterns_detected:
                self.pattern_history.append(pattern)
            
            return patterns_detected
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse DOM: {e}")
            return []
    
    def _calculate_snapshot_metrics(self, snapshot: DOMSnapshot):
        """Calcule métriques snapshot DOM"""
        
        # Totaux
        snapshot.total_bid_size = sum(level.size for level in snapshot.bid_levels)
        snapshot.total_ask_size = sum(level.size for level in snapshot.ask_levels)
        
        # Best bid/ask
        if snapshot.bid_levels:
            snapshot.best_bid = max(level.price for level in snapshot.bid_levels)
        if snapshot.ask_levels:
            snapshot.best_ask = min(level.price for level in snapshot.ask_levels)
        
        # Spread
        if snapshot.best_bid > 0 and snapshot.best_ask > 0:
            snapshot.spread = snapshot.best_ask - snapshot.best_bid
        
        # Imbalance ratio
        total_size = snapshot.total_bid_size + snapshot.total_ask_size
        if total_size > 0:
            snapshot.imbalance_ratio = snapshot.total_bid_size / total_size
        
        # Niveaux max
        if snapshot.bid_levels:
            snapshot.max_bid_level = max(snapshot.bid_levels, key=lambda x: x.size)
        if snapshot.ask_levels:
            snapshot.max_ask_level = max(snapshot.ask_levels, key=lambda x: x.size)
    
    def _detect_icebergs(self, snapshot: DOMSnapshot) -> List[DOMPatternSignal]:
        """Détection ordres iceberg"""
        
        icebergs = []
        
        # Analyser côté bid
        for level in snapshot.bid_levels:
            if level.size >= self.config.iceberg_threshold:
                # Vérifier si taille anormalement grosse vs niveaux adjacents
                avg_size = np.mean([l.size for l in snapshot.bid_levels])
                
                # Seuil plus bas pour détecter icebergs (2x au lieu de 3x)
                if level.size > avg_size * max(2.0, self.config.size_anomaly_multiplier * 0.7):
                    intensity = self._calculate_intensity(level.size / avg_size)
                    
                    iceberg = DOMPatternSignal(
                        timestamp=snapshot.timestamp,
                        pattern_type=DOMPattern.ICEBERG_BID,
                        intensity=intensity,
                        price_level=level.price,
                        size_involved=level.size,
                        confidence=min(0.95, level.size / (avg_size * 3)),  # Confidence plus réaliste
                        expected_direction="BULLISH",
                        time_horizon="SHORT",
                        reasoning=f"Iceberg bid {level.size} contrats à {level.price:.2f} ({level.size/avg_size:.1f}x moyenne)"
                    )
                    
                    icebergs.append(iceberg)
        
        # Analyser côté ask
        for level in snapshot.ask_levels:
            if level.size >= self.config.iceberg_threshold:
                avg_size = np.mean([l.size for l in snapshot.ask_levels])
                
                # Seuil plus bas pour détecter icebergs (2x au lieu de 3x)
                if level.size > avg_size * max(2.0, self.config.size_anomaly_multiplier * 0.7):
                    intensity = self._calculate_intensity(level.size / avg_size)
                    
                    iceberg = DOMPatternSignal(
                        timestamp=snapshot.timestamp,
                        pattern_type=DOMPattern.ICEBERG_ASK,
                        intensity=intensity,
                        price_level=level.price,
                        size_involved=level.size,
                        confidence=min(0.95, level.size / (avg_size * 3)),  # Confidence plus réaliste
                        expected_direction="BEARISH",
                        time_horizon="SHORT",
                        reasoning=f"Iceberg ask {level.size} contrats à {level.price:.2f} ({level.size/avg_size:.1f}x moyenne)"
                    )
                    
                    icebergs.append(iceberg)
        
        return icebergs
    
    def _detect_walls(self, snapshot: DOMSnapshot) -> List[DOMPatternSignal]:
        """Détection murs de support/résistance"""
        
        walls = []
        
        # Mur bid (support)
        if snapshot.max_bid_level and snapshot.max_bid_level.size >= self.config.wall_threshold:
            avg_bid_size = snapshot.total_bid_size / max(len(snapshot.bid_levels), 1)
            
            if snapshot.max_bid_level.size > avg_bid_size * 2:  # 2x plus gros
                intensity = self._calculate_intensity(snapshot.max_bid_level.size / avg_bid_size)
                
                wall = DOMPatternSignal(
                    timestamp=snapshot.timestamp,
                    pattern_type=DOMPattern.WALL_BID,
                    intensity=intensity,
                    price_level=snapshot.max_bid_level.price,
                    size_involved=snapshot.max_bid_level.size,
                    confidence=min(0.90, snapshot.max_bid_level.size / 2000),
                    expected_direction="BULLISH",
                    time_horizon="MEDIUM",
                    reasoning=f"Mur support {snapshot.max_bid_level.size} contrats à {snapshot.max_bid_level.price:.2f}"
                )
                
                walls.append(wall)
        
        # Mur ask (résistance)
        if snapshot.max_ask_level and snapshot.max_ask_level.size >= self.config.wall_threshold:
            avg_ask_size = snapshot.total_ask_size / max(len(snapshot.ask_levels), 1)
            
            if snapshot.max_ask_level.size > avg_ask_size * 2:
                intensity = self._calculate_intensity(snapshot.max_ask_level.size / avg_ask_size)
                
                wall = DOMPatternSignal(
                    timestamp=snapshot.timestamp,
                    pattern_type=DOMPattern.WALL_ASK,
                    intensity=intensity,
                    price_level=snapshot.max_ask_level.price,
                    size_involved=snapshot.max_ask_level.size,
                    confidence=min(0.90, snapshot.max_ask_level.size / 2000),
                    expected_direction="BEARISH",
                    time_horizon="MEDIUM",
                    reasoning=f"Mur résistance {snapshot.max_ask_level.size} contrats à {snapshot.max_ask_level.price:.2f}"
                )
                
                walls.append(wall)
        
        return walls
    
    def _detect_ladders(self, snapshot: DOMSnapshot) -> List[DOMPatternSignal]:
        """Détection échelles agressives"""
        
        ladders = []
        
        # Ladder bid (achat agressif)
        if len(snapshot.bid_levels) >= self.config.ladder_min_levels:
            # Vérifier progression tailles croissantes vers best bid
            sorted_bids = sorted(snapshot.bid_levels, key=lambda x: x.price, reverse=True)
            
            ladder_levels = 0
            for i in range(1, min(len(sorted_bids), 5)):
                if sorted_bids[i-1].size > sorted_bids[i].size * 1.2:  # 20% plus gros
                    ladder_levels += 1
                else:
                    break
            
            if ladder_levels >= self.config.ladder_min_levels:
                total_ladder_size = sum(level.size for level in sorted_bids[:ladder_levels+1])
                
                ladder = DOMPatternSignal(
                    timestamp=snapshot.timestamp,
                    pattern_type=DOMPattern.LADDER_BID,
                    intensity=self._calculate_intensity(ladder_levels / 5.0),
                    price_level=sorted_bids[0].price,  # Best bid
                    size_involved=total_ladder_size,
                    confidence=min(0.85, ladder_levels / 5.0),
                    expected_direction="BULLISH",
                    time_horizon="IMMEDIATE",
                    reasoning=f"Ladder bid {ladder_levels} niveaux, {total_ladder_size} contrats",
                    levels_count=ladder_levels
                )
                
                ladders.append(ladder)
        
        # Ladder ask (vente agressive)
        if len(snapshot.ask_levels) >= self.config.ladder_min_levels:
            sorted_asks = sorted(snapshot.ask_levels, key=lambda x: x.price)
            
            ladder_levels = 0
            for i in range(1, min(len(sorted_asks), 5)):
                if sorted_asks[i-1].size > sorted_asks[i].size * 1.2:
                    ladder_levels += 1
                else:
                    break
            
            if ladder_levels >= self.config.ladder_min_levels:
                total_ladder_size = sum(level.size for level in sorted_asks[:ladder_levels+1])
                
                ladder = DOMPatternSignal(
                    timestamp=snapshot.timestamp,
                    pattern_type=DOMPattern.LADDER_ASK,
                    intensity=self._calculate_intensity(ladder_levels / 5.0),
                    price_level=sorted_asks[0].price,  # Best ask
                    size_involved=total_ladder_size,
                    confidence=min(0.85, ladder_levels / 5.0),
                    expected_direction="BEARISH",
                    time_horizon="IMMEDIATE",
                    reasoning=f"Ladder ask {ladder_levels} niveaux, {total_ladder_size} contrats",
                    levels_count=ladder_levels
                )
                
                ladders.append(ladder)
        
        return ladders
    
    def _detect_spoofing(self, snapshot: DOMSnapshot) -> List[DOMPatternSignal]:
        """Détection spoofing (ordres fantômes)"""
        
        spoofing = []
        
        if len(self.dom_history) < 5:
            return spoofing
        
        # Comparer avec snapshots précédents
        prev_snapshots = list(self.dom_history)[-5:]
        
        # Détecter ordres qui apparaissent/disparaissent rapidement
        for level in snapshot.bid_levels:
            if level.size >= 500:  # Seuil spoofing
                # Vérifier si ce niveau était absent dans snapshots précédents
                was_absent = True
                for prev_snapshot in prev_snapshots[:-1]:
                    for prev_level in prev_snapshot.bid_levels:
                        if abs(prev_level.price - level.price) < 0.1:  # Même niveau
                            was_absent = False
                            break
                
                if was_absent:  # Ordre apparu soudainement
                    spoofing_signal = DOMPatternSignal(
                        timestamp=snapshot.timestamp,
                        pattern_type=DOMPattern.SPOOFING_BID,
                        intensity=DOMIntensity.MEDIUM,
                        price_level=level.price,
                        size_involved=level.size,
                        confidence=0.70,
                        expected_direction="BEARISH",  # Spoofing bid = bearish intent
                        time_horizon="IMMEDIATE",
                        reasoning=f"Spoofing bid détecté: {level.size} contrats apparus à {level.price:.2f}"
                    )
                    
                    spoofing.append(spoofing_signal)
        
        return spoofing
    
    def _detect_absorption(self, snapshot: DOMSnapshot) -> List[DOMPatternSignal]:
        """Détection absorption d'ordres"""
        
        absorption = []
        
        if len(self.dom_history) < 3:
            return absorption
        
        prev_snapshot = self.dom_history[-2]
        
        # Détecter niveaux qui ont significativement diminué
        for prev_level in prev_snapshot.bid_levels:
            current_level = None
            
            # Trouver niveau correspondant dans snapshot actuel
            for level in snapshot.bid_levels:
                if abs(level.price - prev_level.price) < 0.1:
                    current_level = level
                    break
            
            # Si niveau a disparu ou significativement réduit
            if current_level is None or current_level.size < prev_level.size * 0.5:
                size_absorbed = prev_level.size - (current_level.size if current_level else 0)
                
                if size_absorbed >= 200:  # Seuil absorption
                    absorption_signal = DOMPatternSignal(
                        timestamp=snapshot.timestamp,
                        pattern_type=DOMPattern.ABSORPTION_BID,
                        intensity=self._calculate_intensity(size_absorbed / 1000),
                        price_level=prev_level.price,
                        size_involved=size_absorbed,
                        confidence=min(0.90, size_absorbed / 500),
                        expected_direction="BEARISH",
                        time_horizon="IMMEDIATE",
                        reasoning=f"Absorption bid: {size_absorbed} contrats absorbés à {prev_level.price:.2f}"
                    )
                    
                    absorption.append(absorption_signal)
        
        return absorption
    
    def _detect_squeeze(self, snapshot: DOMSnapshot) -> List[DOMPatternSignal]:
        """Détection squeeze (compression spread)"""
        
        squeeze = []
        
        if len(self.dom_history) < 3:
            return squeeze
        
        # Analyser évolution spread
        recent_spreads = [s.spread for s in list(self.dom_history)[-3:] if s.spread > 0]
        
        if len(recent_spreads) >= 3:
            avg_spread = np.mean(recent_spreads)
            current_spread = snapshot.spread
            
            # Squeeze = spread réduit significativement
            if current_spread < avg_spread * 0.6 and current_spread <= 0.75:  # Spread ≤ 3 ticks
                # Analyser direction probable
                direction = "BULLISH" if snapshot.imbalance_ratio > 0.6 else "BEARISH"
                
                squeeze_signal = DOMPatternSignal(
                    timestamp=snapshot.timestamp,
                    pattern_type=DOMPattern.SQUEEZE_UP if direction == "BULLISH" else DOMPattern.SQUEEZE_DOWN,
                    intensity=self._calculate_intensity((avg_spread - current_spread) / avg_spread),
                    price_level=(snapshot.best_bid + snapshot.best_ask) / 2,
                    size_involved=snapshot.total_bid_size + snapshot.total_ask_size,
                    confidence=min(0.80, (avg_spread - current_spread) / avg_spread),
                    expected_direction=direction,
                    time_horizon="IMMEDIATE",
                    reasoning=f"Squeeze détecté: spread {current_spread:.2f} vs {avg_spread:.2f} moyenne"
                )
                
                squeeze.append(squeeze_signal)
        
        return squeeze
    
    def _calculate_intensity(self, ratio: float) -> DOMIntensity:
        """Calcule intensité pattern selon ratio"""
        
        if ratio >= 0.95:
            return DOMIntensity.EXTREME
        elif ratio >= 0.85:
            return DOMIntensity.HIGH
        elif ratio >= 0.70:
            return DOMIntensity.MEDIUM
        elif ratio >= 0.50:
            return DOMIntensity.LOW
        else:
            return DOMIntensity.NOISE
    
    def _update_stats(self, patterns: List[DOMPatternSignal], analysis_time_ms: float):
        """Met à jour statistiques"""
        
        self.stats['total_snapshots_analyzed'] += 1
        
        for pattern in patterns:
            self.stats['patterns_detected'][pattern.pattern_type.value] += 1
            
            if 'iceberg' in pattern.pattern_type.value:
                self.stats['icebergs_detected'] += 1
            elif 'wall' in pattern.pattern_type.value:
                self.stats['walls_detected'] += 1
            elif 'spoofing' in pattern.pattern_type.value:
                self.stats['spoofing_detected'] += 1
            elif 'absorption' in pattern.pattern_type.value:
                self.stats['absorption_events'] += 1
        
        # Moyenne mobile temps analyse
        current_avg = self.stats['avg_analysis_time_ms']
        self.stats['avg_analysis_time_ms'] = (current_avg * 0.9 + analysis_time_ms * 0.1)
    
    def get_dom_summary(self) -> Dict[str, Any]:
        """Résumé analyse DOM"""
        
        return {
            'total_snapshots': self.stats['total_snapshots_analyzed'],
            'patterns_detected': dict(self.stats['patterns_detected']),
            'icebergs_detected': self.stats['icebergs_detected'],
            'walls_detected': self.stats['walls_detected'],
            'spoofing_detected': self.stats['spoofing_detected'],
            'absorption_events': self.stats['absorption_events'],
            'avg_analysis_time_ms': self.stats['avg_analysis_time_ms'],
            'recent_patterns_count': len(self.pattern_history),
            'config': {
                'iceberg_threshold': self.config.iceberg_threshold,
                'wall_threshold': self.config.wall_threshold,
                'analysis_interval_ms': self.config.analysis_interval_ms
            }
        }

# Factory functions
def create_scalping_dom_config() -> DOMConfig:
    """Configuration DOM pour scalping"""
    config = DOMConfig()
    config.analysis_interval_ms = 100        # 100ms ultra-rapide
    config.iceberg_threshold = 300           # Seuils plus bas
    config.wall_threshold = 600
    config.min_size_threshold = 25
    return config

def create_swing_dom_config() -> DOMConfig:
    """Configuration DOM pour swing trading"""
    config = DOMConfig()
    config.analysis_interval_ms = 1000       # 1s plus relaxé
    config.iceberg_threshold = 1000          # Seuils plus élevés
    config.wall_threshold = 2000
    config.pattern_timeout_seconds = 600     # 10min timeout
    return config

# Export principal
__all__ = [
    'SierraDOMAnalyzer',
    'DOMConfig',
    'DOMSnapshot',
    'DOMPatternSignal',
    'DOMPattern',
    'DOMIntensity',
    'DOMLevel',
    'create_scalping_dom_config',
    'create_swing_dom_config'
]
