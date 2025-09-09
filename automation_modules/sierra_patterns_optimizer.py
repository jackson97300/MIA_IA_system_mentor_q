#!/usr/bin/env python3
"""
🎨 SIERRA PATTERNS OPTIMIZER
Optimiseur des patterns Sierra Chart avec intégration Battle Navale
"""

import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from collections import defaultdict, deque

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger
from core.base_types import MarketData

logger = get_logger(__name__)

class PatternType(Enum):
    """Types de patterns Sierra Chart"""
    LONG_DOWN_UP_BAR = "long_down_up_bar"
    LONG_UP_DOWN_BAR = "long_up_down_bar" 
    COLOR_DOWN_SETTING = "color_down_setting"
    VOLUME_PROFILE_IMBALANCE = "volume_profile_imbalance"
    SMART_MONEY_FLOW = "smart_money_flow"
    INSTITUTIONAL_ABSORPTION = "institutional_absorption"
    BATTLE_NAVALE_SETUP = "battle_navale_setup"
    ICEBERG_DETECTION = "iceberg_detection"
    BLOCK_TRADE_ALERT = "block_trade_alert"

class PatternQuality(Enum):
    """Qualité des patterns"""
    ELITE = "elite"         # 90-100% - Qualité exceptionnelle
    HIGH = "high"           # 80-89% - Haute qualité
    GOOD = "good"           # 70-79% - Bonne qualité
    MEDIUM = "medium"       # 60-69% - Qualité moyenne
    LOW = "low"             # <60% - Qualité faible

@dataclass
class PatternSignal:
    """Signal de pattern détecté"""
    pattern_type: PatternType
    timestamp: pd.Timestamp
    strength: float                    # 0.0 - 1.0
    quality: PatternQuality
    confidence: float                  # 0.0 - 1.0
    price_level: float
    volume_support: int
    reasoning: str
    
    # Métadonnées additionnelles
    setup_bars: int = 0
    projected_move: float = 0.0
    risk_reward_ratio: float = 0.0
    confluence_score: float = 0.0

@dataclass
class SierraPatternConfig:
    """Configuration optimisée pour patterns Sierra"""
    
    # Battle Navale Config
    battle_navale_enabled: bool = True
    battle_min_strength: float = 0.6        # Minimum pour signal valide
    battle_confluence_weight: float = 0.4   # 40% du score total
    
    # Volume Profile Config  
    volume_profile_enabled: bool = True
    min_volume_threshold: int = 100          # Volume minimum analyse
    imbalance_threshold: float = 0.3         # 30% imbalance minimum
    
    # Smart Money Detection
    smart_money_enabled: bool = True
    block_trade_threshold: int = 300         # Optimisé par tests
    institutional_threshold: int = 800       # Optimisé par tests
    iceberg_threshold: int = 150             # Optimisé par tests
    
    # Pattern Quality Filters
    min_pattern_quality: PatternQuality = PatternQuality.GOOD  # 70%+
    min_confidence: float = 0.65             # 65% confidence minimum
    max_patterns_per_minute: int = 5         # Anti-spam
    
    # Performance
    max_lookback_bars: int = 50              # Historique pattern
    analysis_interval_ms: int = 250          # 250ms entre analyses
    cache_enabled: bool = True
    cache_size: int = 100

class SierraPatternsOptimizer:
    """
    Optimiseur patterns Sierra Chart avec intégration Battle Navale
    
    Fonctionnalités:
    ✅ Détection patterns temps réel
    ✅ Intégration Battle Navale existant
    ✅ Volume Profile avancé
    ✅ Smart Money tracking
    ✅ Scoring confluence
    ✅ Cache performance
    """
    
    def __init__(self, config: Optional[SierraPatternConfig] = None):
        self.config = config or SierraPatternConfig()
        
        # Historique données
        self.market_data_history: deque = deque(maxlen=self.config.max_lookback_bars)
        self.pattern_history: deque = deque(maxlen=200)
        
        # Cache patterns
        self.pattern_cache: Dict[str, PatternSignal] = {}
        self.last_analysis_time = 0
        
        # Statistiques
        self.stats = {
            'total_patterns_detected': 0,
            'patterns_by_type': defaultdict(int),
            'patterns_by_quality': defaultdict(int),
            'avg_analysis_time_ms': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Configuration Battle Navale existante
        self.battle_navale_config = {
            'long_down_up_enabled': True,
            'long_up_down_enabled': True,
            'color_down_enabled': True,
            'base_quality_threshold': 0.7,
            'trend_continuation_weight': 0.2
        }
        
        logger.info("🎨 Sierra Patterns Optimizer initialisé")
    
    def analyze_patterns(self, market_data: MarketData, 
                        orderflow_data: Optional[Dict] = None,
                        volume_profile: Optional[Dict] = None) -> List[PatternSignal]:
        """Analyse patterns en temps réel"""
        
        start_time = time.perf_counter()
        
        # Vérifier intervalle d'analyse
        current_time = time.time() * 1000
        if current_time - self.last_analysis_time < self.config.analysis_interval_ms:
            return []
        
        self.last_analysis_time = current_time
        
        # Ajouter données à l'historique
        self.market_data_history.append(market_data)
        
        if len(self.market_data_history) < 10:
            return []  # Pas assez de données
        
        patterns_detected = []
        
        try:
            # 1. Patterns Battle Navale existants
            if self.config.battle_navale_enabled:
                battle_patterns = self._analyze_battle_navale_patterns(market_data)
                patterns_detected.extend(battle_patterns)
            
            # 2. Patterns Volume Profile
            if self.config.volume_profile_enabled and volume_profile:
                vp_patterns = self._analyze_volume_profile_patterns(market_data, volume_profile)
                patterns_detected.extend(vp_patterns)
            
            # 3. Patterns Smart Money
            if self.config.smart_money_enabled and orderflow_data:
                sm_patterns = self._analyze_smart_money_patterns(market_data, orderflow_data)
                patterns_detected.extend(sm_patterns)
            
            # 4. Filtrage qualité
            filtered_patterns = self._filter_patterns_by_quality(patterns_detected)
            
            # 5. Confluence scoring
            final_patterns = self._calculate_confluence_scores(filtered_patterns)
            
            # Statistiques
            analysis_time = (time.perf_counter() - start_time) * 1000
            self._update_stats(analysis_time, final_patterns)
            
            # Ajouter à l'historique
            for pattern in final_patterns:
                self.pattern_history.append(pattern)
            
            return final_patterns
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse patterns: {e}")
            return []
    
    def _analyze_battle_navale_patterns(self, market_data: MarketData) -> List[PatternSignal]:
        """Analyse patterns Battle Navale existants"""
        
        patterns = []
        
        if len(self.market_data_history) < 3:
            return patterns
        
        # Récupérer dernières barres
        current_bar = self.market_data_history[-1]
        prev_bar = self.market_data_history[-2]
        prev2_bar = self.market_data_history[-3]
        
        # Pattern Long Down Up Bar
        ldu_signal = self._detect_long_down_up_bar(current_bar, prev_bar, prev2_bar)
        if ldu_signal:
            patterns.append(ldu_signal)
        
        # Pattern Long Up Down Bar
        lud_signal = self._detect_long_up_down_bar(current_bar, prev_bar, prev2_bar)
        if lud_signal:
            patterns.append(lud_signal)
        
        # Pattern Color Down Setting
        cds_signal = self._detect_color_down_setting(current_bar, prev_bar)
        if cds_signal:
            patterns.append(cds_signal)
        
        return patterns
    
    def _detect_long_down_up_bar(self, current: MarketData, prev: MarketData, prev2: MarketData) -> Optional[PatternSignal]:
        """Détection Long Down Up Bar optimisée"""
        
        # Critères Long Down Up Bar
        is_long_bar = (current.high - current.low) > (prev.high - prev.low) * 1.5
        is_down_then_up = prev.close < prev.open and current.close > current.open
        volume_support = current.volume > prev.volume * 1.2
        
        if not (is_long_bar and is_down_then_up and volume_support):
            return None
        
        # Calcul force
        bar_range = current.high - current.low
        prev_range = prev.high - prev.low
        range_ratio = bar_range / prev_range if prev_range > 0 else 1.0
        
        volume_ratio = current.volume / prev.volume if prev.volume > 0 else 1.0
        
        strength = min(1.0, (range_ratio * 0.6 + volume_ratio * 0.4) / 2.0)
        
        # Qualité basée sur confluence
        quality = self._determine_pattern_quality(strength)
        
        return PatternSignal(
            pattern_type=PatternType.LONG_DOWN_UP_BAR,
            timestamp=current.timestamp,
            strength=strength,
            quality=quality,
            confidence=min(0.95, strength + 0.1),
            price_level=current.close,
            volume_support=current.volume,
            reasoning=f"Long Down Up Bar - Range {range_ratio:.1f}x, Volume {volume_ratio:.1f}x",
            setup_bars=2,
            projected_move=bar_range * 0.618,  # Fibonacci retracement
            risk_reward_ratio=2.0
        )
    
    def _detect_long_up_down_bar(self, current: MarketData, prev: MarketData, prev2: MarketData) -> Optional[PatternSignal]:
        """Détection Long Up Down Bar optimisée"""
        
        # Critères Long Up Down Bar (inverse)
        is_long_bar = (current.high - current.low) > (prev.high - prev.low) * 1.5
        is_up_then_down = prev.close > prev.open and current.close < current.open
        volume_support = current.volume > prev.volume * 1.2
        
        if not (is_long_bar and is_up_then_down and volume_support):
            return None
        
        # Calcul similaire mais inverse
        bar_range = current.high - current.low
        prev_range = prev.high - prev.low
        range_ratio = bar_range / prev_range if prev_range > 0 else 1.0
        
        volume_ratio = current.volume / prev.volume if prev.volume > 0 else 1.0
        
        strength = min(1.0, (range_ratio * 0.6 + volume_ratio * 0.4) / 2.0)
        quality = self._determine_pattern_quality(strength)
        
        return PatternSignal(
            pattern_type=PatternType.LONG_UP_DOWN_BAR,
            timestamp=current.timestamp,
            strength=strength,
            quality=quality,
            confidence=min(0.95, strength + 0.1),
            price_level=current.close,
            volume_support=current.volume,
            reasoning=f"Long Up Down Bar - Range {range_ratio:.1f}x, Volume {volume_ratio:.1f}x",
            setup_bars=2,
            projected_move=bar_range * 0.618,
            risk_reward_ratio=2.0
        )
    
    def _detect_color_down_setting(self, current: MarketData, prev: MarketData) -> Optional[PatternSignal]:
        """Détection Color Down Setting"""
        
        # Critères Color Down Setting
        is_red_bar = current.close < current.open
        is_penetration = current.low < prev.low
        is_recovery = current.close > prev.low
        volume_confirmation = current.volume > prev.volume
        
        if not (is_red_bar and is_penetration and is_recovery and volume_confirmation):
            return None
        
        # Force basée sur pénétration et récupération
        penetration_depth = prev.low - current.low
        recovery_strength = current.close - current.low
        bar_range = current.high - current.low
        
        if bar_range == 0:
            return None
        
        strength = min(1.0, (recovery_strength / bar_range) * 0.8)
        quality = self._determine_pattern_quality(strength)
        
        return PatternSignal(
            pattern_type=PatternType.COLOR_DOWN_SETTING,
            timestamp=current.timestamp,
            strength=strength,
            quality=quality,
            confidence=min(0.90, strength + 0.05),
            price_level=current.close,
            volume_support=current.volume,
            reasoning=f"Color Down Setting - Pénétration {penetration_depth:.2f}, Récupération {recovery_strength:.2f}",
            setup_bars=1,
            projected_move=penetration_depth * 1.618,
            risk_reward_ratio=1.5
        )
    
    def _analyze_volume_profile_patterns(self, market_data: MarketData, volume_profile: Dict) -> List[PatternSignal]:
        """Analyse patterns Volume Profile"""
        
        patterns = []
        
        # Récupérer données volume profile
        volume_levels = volume_profile.get('levels', [])
        if not volume_levels:
            return patterns
        
        # Pattern Volume Imbalance
        imbalance_signal = self._detect_volume_imbalance(market_data, volume_levels)
        if imbalance_signal:
            patterns.append(imbalance_signal)
        
        return patterns
    
    def _detect_volume_imbalance(self, market_data: MarketData, volume_levels: List) -> Optional[PatternSignal]:
        """Détection déséquilibre volume"""
        
        current_price = market_data.close
        current_volume = market_data.volume
        
        # Trouver niveau volume proche
        nearest_level = None
        min_distance = float('inf')
        
        for level in volume_levels:
            price = level.get('price', 0)
            distance = abs(price - current_price)
            
            if distance < min_distance:
                min_distance = distance
                nearest_level = level
        
        if not nearest_level:
            return None
        
        level_volume = nearest_level.get('volume', 0)
        if level_volume < self.config.min_volume_threshold:
            return None
        
        # Calcul ratio imbalance
        volume_ratio = current_volume / level_volume if level_volume > 0 else 0
        
        if volume_ratio < self.config.imbalance_threshold:
            return None
        
        strength = min(1.0, volume_ratio / 3.0)  # Normaliser à 1.0
        quality = self._determine_pattern_quality(strength)
        
        return PatternSignal(
            pattern_type=PatternType.VOLUME_PROFILE_IMBALANCE,
            timestamp=market_data.timestamp,
            strength=strength,
            quality=quality,
            confidence=min(0.85, strength),
            price_level=current_price,
            volume_support=current_volume,
            reasoning=f"Volume Imbalance - Ratio {volume_ratio:.2f}x niveau {nearest_level.get('price', 0):.2f}",
            projected_move=min_distance * 2.0,
            risk_reward_ratio=1.8
        )
    
    def _analyze_smart_money_patterns(self, market_data: MarketData, orderflow_data: Dict) -> List[PatternSignal]:
        """Analyse patterns Smart Money"""
        
        patterns = []
        
        # Pattern Block Trade
        block_signal = self._detect_block_trade(market_data, orderflow_data)
        if block_signal:
            patterns.append(block_signal)
        
        # Pattern Iceberg Order
        iceberg_signal = self._detect_iceberg_order(market_data, orderflow_data)
        if iceberg_signal:
            patterns.append(iceberg_signal)
        
        return patterns
    
    def _detect_block_trade(self, market_data: MarketData, orderflow_data: Dict) -> Optional[PatternSignal]:
        """Détection Block Trade (Smart Money)"""
        
        # Récupérer données orderflow
        block_volume = orderflow_data.get('block_volume', 0)
        total_volume = orderflow_data.get('total_volume', market_data.volume)
        
        if block_volume < self.config.block_trade_threshold:
            return None
        
        # Calcul force basée sur ratio block/total
        block_ratio = block_volume / total_volume if total_volume > 0 else 0
        
        if block_ratio < 0.1:  # Minimum 10% du volume
            return None
        
        strength = min(1.0, block_ratio * 2.0)  # Multiplier par 2 pour normaliser
        quality = self._determine_pattern_quality(strength)
        
        return PatternSignal(
            pattern_type=PatternType.BLOCK_TRADE_ALERT,
            timestamp=market_data.timestamp,
            strength=strength,
            quality=quality,
            confidence=min(0.90, strength + 0.1),
            price_level=market_data.close,
            volume_support=block_volume,
            reasoning=f"Block Trade Détecté - {block_volume} contrats ({block_ratio:.1%} du volume)",
            projected_move=0.25 * 3,  # 3 ticks ES
            risk_reward_ratio=2.5
        )
    
    def _detect_iceberg_order(self, market_data: MarketData, orderflow_data: Dict) -> Optional[PatternSignal]:
        """Détection Iceberg Order"""
        
        iceberg_volume = orderflow_data.get('iceberg_volume', 0)
        
        if iceberg_volume < self.config.iceberg_threshold:
            return None
        
        # Force basée sur taille iceberg
        strength = min(1.0, iceberg_volume / 500.0)  # Normaliser sur 500
        quality = self._determine_pattern_quality(strength)
        
        return PatternSignal(
            pattern_type=PatternType.ICEBERG_DETECTION,
            timestamp=market_data.timestamp,
            strength=strength,
            quality=quality,
            confidence=min(0.80, strength),
            price_level=market_data.close,
            volume_support=iceberg_volume,
            reasoning=f"Iceberg Order - {iceberg_volume} contrats cachés",
            projected_move=0.25 * 2,  # 2 ticks ES
            risk_reward_ratio=2.0
        )
    
    def _determine_pattern_quality(self, strength: float) -> PatternQuality:
        """Détermine qualité pattern basée sur force"""
        
        if strength >= 0.90:
            return PatternQuality.ELITE
        elif strength >= 0.80:
            return PatternQuality.HIGH
        elif strength >= 0.70:
            return PatternQuality.GOOD
        elif strength >= 0.60:
            return PatternQuality.MEDIUM
        else:
            return PatternQuality.LOW
    
    def _filter_patterns_by_quality(self, patterns: List[PatternSignal]) -> List[PatternSignal]:
        """Filtre patterns par qualité minimum"""
        
        quality_order = {
            PatternQuality.ELITE: 5,
            PatternQuality.HIGH: 4,
            PatternQuality.GOOD: 3,
            PatternQuality.MEDIUM: 2,
            PatternQuality.LOW: 1
        }
        
        min_quality_score = quality_order[self.config.min_pattern_quality]
        
        filtered = []
        for pattern in patterns:
            if quality_order[pattern.quality] >= min_quality_score:
                if pattern.confidence >= self.config.min_confidence:
                    filtered.append(pattern)
        
        return filtered
    
    def _calculate_confluence_scores(self, patterns: List[PatternSignal]) -> List[PatternSignal]:
        """Calcule scores confluence entre patterns"""
        
        for pattern in patterns:
            confluence_score = 0.0
            
            # Confluence temporelle (patterns simultanés)
            simultaneous_patterns = [p for p in patterns if p != pattern and 
                                   abs((p.timestamp - pattern.timestamp).total_seconds()) < 60]
            
            confluence_score += len(simultaneous_patterns) * 0.2
            
            # Confluence de prix (patterns au même niveau)
            price_confluence = [p for p in patterns if p != pattern and
                              abs(p.price_level - pattern.price_level) < 1.0]
            
            confluence_score += len(price_confluence) * 0.3
            
            # Confluence volume (patterns avec volume similaire)
            volume_confluence = [p for p in patterns if p != pattern and
                               abs(p.volume_support - pattern.volume_support) / max(p.volume_support, pattern.volume_support) < 0.5]
            
            confluence_score += len(volume_confluence) * 0.1
            
            pattern.confluence_score = min(1.0, confluence_score)
        
        return patterns
    
    def _update_stats(self, analysis_time_ms: float, patterns: List[PatternSignal]):
        """Met à jour statistiques"""
        
        self.stats['total_patterns_detected'] += len(patterns)
        
        for pattern in patterns:
            self.stats['patterns_by_type'][pattern.pattern_type.value] += 1
            self.stats['patterns_by_quality'][pattern.quality.value] += 1
        
        # Moyenne mobile analyse time
        current_avg = self.stats['avg_analysis_time_ms']
        self.stats['avg_analysis_time_ms'] = (current_avg * 0.9 + analysis_time_ms * 0.1)
    
    def get_pattern_summary(self) -> Dict[str, Any]:
        """Résumé patterns détectés"""
        
        return {
            'total_patterns': self.stats['total_patterns_detected'],
            'patterns_by_type': dict(self.stats['patterns_by_type']),
            'patterns_by_quality': dict(self.stats['patterns_by_quality']),
            'avg_analysis_time_ms': self.stats['avg_analysis_time_ms'],
            'recent_patterns': len(self.pattern_history),
            'cache_hit_ratio': self.stats['cache_hits'] / max(1, self.stats['cache_hits'] + self.stats['cache_misses'])
        }
    
    def export_sierra_patterns_dict(self, patterns: List[PatternSignal]) -> Dict[str, float]:
        """Export patterns au format attendu par feature_calculator.py"""
        
        if not patterns:
            return {}
        
        # Calculs scores pour compatibilité avec Battle Navale
        battle_navale_patterns = [p for p in patterns if p.pattern_type in [
            PatternType.LONG_DOWN_UP_BAR, PatternType.LONG_UP_DOWN_BAR, PatternType.COLOR_DOWN_SETTING
        ]]
        
        volume_patterns = [p for p in patterns if p.pattern_type == PatternType.VOLUME_PROFILE_IMBALANCE]
        smart_money_patterns = [p for p in patterns if p.pattern_type in [
            PatternType.BLOCK_TRADE_ALERT, PatternType.ICEBERG_DETECTION
        ]]
        
        # Scores agrégés
        battle_signal = np.mean([p.strength for p in battle_navale_patterns]) if battle_navale_patterns else 0.0
        base_quality = np.mean([p.confidence for p in battle_navale_patterns]) if battle_navale_patterns else 0.0
        
        volume_strength = np.mean([p.strength for p in volume_patterns]) if volume_patterns else 0.0
        smart_money_strength = np.mean([p.strength for p in smart_money_patterns]) if smart_money_patterns else 0.0
        
        # Score global
        all_strengths = [p.strength for p in patterns]
        battle_strength = np.mean(all_strengths) if all_strengths else 0.0
        
        return {
            'battle_navale_signal': battle_signal,
            'base_quality': base_quality,
            'trend_continuation': battle_signal * 0.8,  # Approximation
            'battle_strength': battle_strength,
            'volume_profile_strength': volume_strength,
            'smart_money_strength': smart_money_strength,
            'pattern_confluence': np.mean([p.confluence_score for p in patterns]) if patterns else 0.0
        }

# Factory functions
def create_scalping_patterns_config() -> SierraPatternConfig:
    """Configuration patterns pour scalping"""
    config = SierraPatternConfig()
    config.analysis_interval_ms = 100        # 100ms pour scalping
    config.min_confidence = 0.75             # Plus strict
    config.max_patterns_per_minute = 10      # Plus permissif
    config.min_pattern_quality = PatternQuality.HIGH
    return config

def create_swing_patterns_config() -> SierraPatternConfig:
    """Configuration patterns pour swing trading"""
    config = SierraPatternConfig()
    config.analysis_interval_ms = 1000       # 1s pour swing
    config.min_confidence = 0.60             # Plus permissif
    config.max_patterns_per_minute = 2       # Moins de patterns
    config.min_pattern_quality = PatternQuality.GOOD
    config.max_lookback_bars = 100           # Plus d'historique
    return config

# Export principal
__all__ = [
    'SierraPatternsOptimizer',
    'SierraPatternConfig', 
    'PatternSignal',
    'PatternType',
    'PatternQuality',
    'create_scalping_patterns_config',
    'create_swing_patterns_config'
]


