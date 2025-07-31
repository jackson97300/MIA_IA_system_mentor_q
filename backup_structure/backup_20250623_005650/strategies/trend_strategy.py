"""
MIA_IA_SYSTEM - Trend Strategy
Stratégie tendance avec Dow Theory + Pullback emphasis
Version: Production Ready
Performance: Hiérarchie signaux + gestion complète

HIÉRARCHIE SIGNAUX TREND :
1. PREMIUM_PULLBACK (90-100%) - Pullback + confluence maximale
2. STRONG_PULLBACK (75-89%)   - Pullback + confluence forte  
3. PREMIUM_BREAKOUT (80-95%)  - Breakout + volume exceptionnel
4. STRONG_TREND (70-84%)      - Continuation tendance
5. WEAK_SIGNAL (60-69%)       - Signal faible (size réduite)
6. NO_TRADE (0-59%)          - Attendre meilleur setup

RÈGLES GESTION :
- ENTRÉE : Confirmation confluence + pattern + pullback preferred
- STOPS : Structure Dow (HL/LH) + buffer adaptatif
- SORTIES : Target + trailing + violation structure
- JAMAIS contre tendance primaire
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from collections import deque
import logging

# Local imports
from core.base_types import (
    MarketData, OrderFlowData, TradingSignal, SignalType, 
    MarketRegime, SignalStrength, ES_TICK_SIZE, ES_TICK_VALUE
)
from features.feature_calculator import (
    FeatureCalculationResult, SignalQuality, TRADING_THRESHOLDS
)

logger = logging.getLogger(__name__)

# === TREND SIGNAL HIERARCHY ===

class TrendSignalType(Enum):
    """Types de signaux tendance avec hiérarchie"""
    PREMIUM_PULLBACK = "premium_pullback"      # 90-100% - Top tier
    STRONG_PULLBACK = "strong_pullback"        # 75-89%  - Preferred
    PREMIUM_BREAKOUT = "premium_breakout"      # 80-95%  - Volume exception
    STRONG_TREND = "strong_trend"              # 70-84%  - Standard
    WEAK_SIGNAL = "weak_signal"                # 60-69%  - Reduced size
    NO_TRADE = "no_trade"                      # 0-59%   - Wait

class TrendDirection(Enum):
    """Direction tendance"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"
    TRANSITION = "transition"

class ExitReason(Enum):
    """Raisons de sortie"""
    TARGET_HIT = "target_hit"
    STOP_LOSS = "stop_loss"
    STRUCTURE_BREAK = "structure_break"
    TIME_STOP = "time_stop"
    CONFLUENCE_LOSS = "confluence_loss"
    MANUAL_EXIT = "manual_exit"

# === DATACLASSES ===

@dataclass
class TrendStructure:
    """Structure tendance Dow Theory"""
    timestamp: pd.Timestamp
    
    # Trend identification
    direction: TrendDirection = TrendDirection.SIDEWAYS
    strength: float = 0.0  # 0-1
    
    # Dow structure levels
    last_higher_high: float = 0.0
    last_higher_low: float = 0.0
    last_lower_high: float = 0.0
    last_lower_low: float = 0.0
    
    # Support/Resistance levels
    key_support: float = 0.0
    key_resistance: float = 0.0
    
    # Momentum
    momentum_score: float = 0.0
    volume_trend: float = 0.0
    
    # Validation flags
    structure_intact: bool = True
    es_nq_aligned: bool = False

@dataclass
class PullbackData:
    """Données pullback analysis"""
    timestamp: pd.Timestamp
    
    # Pullback identification
    pullback_detected: bool = False
    pullback_type: str = "none"  # fibonacci, structural, time-based
    
    # Levels
    pullback_start: float = 0.0
    pullback_target: float = 0.0
    current_retracement: float = 0.0  # Percentage
    
    # Quality metrics
    pullback_quality: float = 0.0  # 0-1
    confluence_at_level: float = 0.0
    volume_support: bool = False
    
    # Timing
    pullback_duration: int = 0  # Minutes
    optimal_entry_zone: Tuple[float, float] = (0.0, 0.0)

@dataclass
class TrendSignalData:
    """Signal tendance complet"""
    timestamp: pd.Timestamp
    signal_type: TrendSignalType
    direction: TrendDirection
    
    # Entry data
    entry_price: float
    entry_reason: str
    confluence_score: float
    
    # Risk management
    stop_loss: float
    take_profit: float
    position_size: float
    max_risk_ticks: float
    
    # Structure data
    trend_structure: TrendStructure
    pullback_data: Optional[PullbackData] = None
    
    # Metadata
    sierra_patterns: Dict[str, float] = field(default_factory=dict)
    options_levels: Dict[str, float] = field(default_factory=dict)
    
    def risk_reward_ratio(self) -> float:
        """Calcul R:R"""
        risk = abs(self.entry_price - self.stop_loss)
        reward = abs(self.take_profit - self.entry_price)
        return reward / risk if risk > 0 else 0.0

# === MAIN TREND STRATEGY CLASS ===

class TrendStrategy:
    """
    Stratégie tendance avec hiérarchie signaux
    
    Implémente :
    - Dow Theory structure analysis
    - Pullback preference over breakouts
    - Hiérarchie signaux avec thresholds
    - Gestion complète entrée/sortie
    - Jamais contre tendance primaire
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation stratégie tendance"""
        self.config = config or {}
        
        # Paramètres Dow Theory
        self.structure_lookback = self.config.get('structure_lookback', 30)
        self.min_trend_strength = self.config.get('min_trend_strength', 0.6)
        self.pullback_preference = self.config.get('pullback_preference', True)
        
        # Paramètres pullback
        self.fibonacci_levels = [0.382, 0.5, 0.618, 0.786]
        self.max_pullback_duration = self.config.get('max_pullback_duration', 60)  # minutes
        
        # Risk management
        self.base_position_size = self.config.get('base_position_size', 1.0)
        self.max_risk_per_trade = self.config.get('max_risk_per_trade', 15.0)  # ticks
        self.target_risk_reward = self.config.get('target_risk_reward', 2.0)
        
        # État
        self.current_trend: Optional[TrendStructure] = None
        self.active_pullback: Optional[PullbackData] = None
        self.price_history: deque = deque(maxlen=100)
        
        # Performance tracking
        self.stats = {
            'signals_generated': 0,
            'pullback_signals': 0,
            'breakout_signals': 0,
            'trend_strength_avg': 0.0,
            'avg_confluence_score': 0.0
        }
        
        logger.info("TrendStrategy initialisée avec hiérarchie signaux Dow Theory")
    
    def analyze_trend_signal(self,
                           features: FeatureCalculationResult,
                           market_data: MarketData,
                           structure_data: Optional[Dict[str, Any]] = None,
                           sierra_patterns: Optional[Dict[str, float]] = None) -> Optional[TrendSignalData]:
        """
        ANALYSE SIGNAL TENDANCE PRINCIPAL
        
        Processus hiérarchique :
        1. Analyse structure Dow Theory
        2. Détection pullback opportunities
        3. Évaluation confluence
        4. Classification signal selon hiérarchie
        5. Calcul risk/reward
        
        Args:
            features: Features calculées avec confluence
            market_data: Données marché actuelles
            structure_data: Données structure (VWAP, MP, etc.)
            sierra_patterns: Patterns depuis battle_navale
            
        Returns:
            TrendSignalData avec hiérarchie ou None
        """
        start_time = time.perf_counter()
        
        try:
            # Ajout à l'historique
            self.price_history.append(market_data)
            
            # 1. ANALYSE STRUCTURE DOW THEORY
            trend_structure = self._analyze_dow_structure(market_data, structure_data)
            self.current_trend = trend_structure
            
            # 2. VÉRIFICATION DIRECTION AUTORISÉE
            if trend_structure.direction == TrendDirection.SIDEWAYS:
                return None  # Pas de signal trend en sideways
            
            # 3. DÉTECTION PULLBACK
            pullback_data = self._analyze_pullback_opportunity(
                market_data, trend_structure, structure_data
            )
            self.active_pullback = pullback_data
            
            # 4. ÉVALUATION CONFLUENCE
            confluence_score = features.confluence_score
            
            # 5. CLASSIFICATION SIGNAL SELON HIÉRARCHIE
            signal_type = self._classify_trend_signal(
                confluence_score, pullback_data, trend_structure, features
            )
            
            if signal_type == TrendSignalType.NO_TRADE:
                return None
            
            # 6. GÉNÉRATION SIGNAL COMPLET
            signal = self._generate_trend_signal(
                signal_type=signal_type,
                trend_structure=trend_structure,
                pullback_data=pullback_data,
                market_data=market_data,
                confluence_score=confluence_score,
                sierra_patterns=sierra_patterns or {}
            )
            
            # 7. VALIDATION FINALE
            if self._validate_signal(signal):
                self._update_stats(signal)
                logger.info(f"Signal tendance généré: {signal.signal_type.value} "
                          f"@ {signal.entry_price:.2f} (conf: {signal.confluence_score:.2f})")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur analyse signal tendance: {e}")
            return None
    
    def _analyze_dow_structure(self,
                             market_data: MarketData,
                             structure_data: Optional[Dict[str, Any]]) -> TrendStructure:
        """
        ANALYSE STRUCTURE DOW THEORY
        
        Identifie :
        - Higher Highs / Higher Lows (bullish)
        - Lower Highs / Lower Lows (bearish)
        - Force de la tendance
        - Niveaux clés support/résistance
        """
        if len(self.price_history) < self.structure_lookback:
            return TrendStructure(
                timestamp=market_data.timestamp,
                direction=TrendDirection.TRANSITION
            )
        
        recent_bars = list(self.price_history)[-self.structure_lookback:]
        
        # Extraction pivots (méthode simplifiée mais efficace)
        highs = [bar.high for bar in recent_bars]
        lows = [bar.low for bar in recent_bars]
        closes = [bar.close for bar in recent_bars]
        
        # Calcul trend des highs et lows
        high_trend = np.polyfit(range(len(highs)), highs, 1)[0]
        low_trend = np.polyfit(range(len(lows)), lows, 1)[0]
        close_trend = np.polyfit(range(len(closes)), closes, 1)[0]
        
        # Détermination direction
        direction = TrendDirection.SIDEWAYS
        strength = 0.0
        
        # Structure haussière : HH + HL
        if high_trend > 0 and low_trend > 0:
            direction = TrendDirection.BULLISH
            # Force basée sur slope + consistency
            trend_slope = (high_trend + low_trend) / 2
            strength = min(trend_slope / ES_TICK_SIZE, 1.0)
            
        # Structure baissière : LH + LL  
        elif high_trend < 0 and low_trend < 0:
            direction = TrendDirection.BEARISH
            trend_slope = abs(high_trend + low_trend) / 2
            strength = min(trend_slope / ES_TICK_SIZE, 1.0)
            
        # Transition ou sideways
        else:
            direction = TrendDirection.TRANSITION
            strength = 0.3  # Faible
        
        # Identification niveaux clés
        if direction == TrendDirection.BULLISH:
            # Support = dernier HL significatif
            key_support = min(lows[-10:])  # Last 10 lows
            # Résistance = high récent
            key_resistance = max(highs[-5:])
            
        elif direction == TrendDirection.BEARISH:
            # Support = low récent  
            key_support = min(lows[-5:])
            # Résistance = dernier LH significatif
            key_resistance = max(highs[-10:])
            
        else:
            key_support = min(lows[-10:])
            key_resistance = max(highs[-10:])
        
        # Momentum et volume analysis
        momentum_score = self._calculate_momentum_score(recent_bars)
        volume_trend = self._calculate_volume_trend(recent_bars)
        
        # ES/NQ alignment check
        es_nq_aligned = self._check_es_nq_alignment(structure_data)
        
        return TrendStructure(
            timestamp=market_data.timestamp,
            direction=direction,
            strength=strength,
            last_higher_high=max(highs) if direction == TrendDirection.BULLISH else 0.0,
            last_higher_low=key_support if direction == TrendDirection.BULLISH else 0.0,
            last_lower_high=key_resistance if direction == TrendDirection.BEARISH else 0.0,
            last_lower_low=min(lows) if direction == TrendDirection.BEARISH else 0.0,
            key_support=key_support,
            key_resistance=key_resistance,
            momentum_score=momentum_score,
            volume_trend=volume_trend,
            structure_intact=True,  # À implémenter validation
            es_nq_aligned=es_nq_aligned
        )
    
    def _analyze_pullback_opportunity(self,
                                    market_data: MarketData,
                                    trend_structure: TrendStructure,
                                    structure_data: Optional[Dict[str, Any]]) -> Optional[PullbackData]:
        """
        ANALYSE OPPORTUNITÉ PULLBACK
        
        Détecte :
        - Pullback en cours dans tendance
        - Qualité du pullback (fibonacci, structure)
        - Zone d'entrée optimale
        - Confluence avec niveaux techniques
        """
        if trend_structure.direction == TrendDirection.SIDEWAYS:
            return None
        
        current_price = market_data.close
        
        # Identification pullback selon direction tendance
        if trend_structure.direction == TrendDirection.BULLISH:
            # Pullback = retracement depuis dernier high
            recent_high = trend_structure.last_higher_high
            pullback_target = trend_structure.key_support
            
            # Vérifier si on est en pullback
            if current_price < recent_high * 0.998:  # Au moins 0.2% de retracement
                pullback_detected = True
                retracement_pct = (recent_high - current_price) / (recent_high - pullback_target)
            else:
                pullback_detected = False
                retracement_pct = 0.0
                
        elif trend_structure.direction == TrendDirection.BEARISH:
            # Pullback = retracement depuis dernier low
            recent_low = trend_structure.last_lower_low
            pullback_target = trend_structure.key_resistance
            
            if current_price > recent_low * 1.002:  # Au moins 0.2% de retracement
                pullback_detected = True
                retracement_pct = (current_price - recent_low) / (pullback_target - recent_low)
            else:
                pullback_detected = False
                retracement_pct = 0.0
        else:
            return None
        
        if not pullback_detected:
            return None
        
        # Évaluation qualité pullback
        pullback_quality = self._evaluate_pullback_quality(
            retracement_pct, market_data, structure_data
        )
        
        # Confluence à ce niveau
        confluence_score = self._calculate_pullback_confluence(
            current_price, structure_data
        )
        
        # Zone d'entrée optimale (fibonacci levels)
        entry_zone = self._calculate_optimal_entry_zone(
            trend_structure, retracement_pct
        )
        
        return PullbackData(
            timestamp=market_data.timestamp,
            pullback_detected=pullback_detected,
            pullback_type="fibonacci" if 0.35 <= retracement_pct <= 0.65 else "structural",
            current_retracement=retracement_pct,
            pullback_quality=pullback_quality,
            confluence_at_level=confluence_score,
            volume_support=self._check_volume_support(market_data),
            optimal_entry_zone=entry_zone
        )
    
    def _classify_trend_signal(self,
                             confluence_score: float,
                             pullback_data: Optional[PullbackData],
                             trend_structure: TrendStructure,
                             features: FeatureCalculationResult) -> TrendSignalType:
        """
        CLASSIFICATION HIÉRARCHIQUE DES SIGNAUX
        
        Hiérarchie (du meilleur au moins bon) :
        1. PREMIUM_PULLBACK (90-100%) - Pullback + confluence max
        2. STRONG_PULLBACK (75-89%)   - Pullback + confluence forte
        3. PREMIUM_BREAKOUT (80-95%)  - Breakout + volume exceptionnel
        4. STRONG_TREND (70-84%)      - Continuation standard  
        5. WEAK_SIGNAL (60-69%)       - Signal faible
        6. NO_TRADE (0-59%)          - Pas de trade
        """
        
        # Base thresholds
        if confluence_score < TRADING_THRESHOLDS['WEAK_SIGNAL']:
            return TrendSignalType.NO_TRADE
        
        # PULLBACK SIGNALS (PRÉFÉRÉS)
        if pullback_data and pullback_data.pullback_detected:
            
            # Évaluation qualité pullback
            pullback_quality = pullback_data.pullback_quality
            confluence_at_level = pullback_data.confluence_at_level
            
            # PREMIUM PULLBACK (90-100%)
            if (confluence_score >= 0.85 and 
                pullback_quality >= 0.8 and
                confluence_at_level >= 0.7 and
                trend_structure.strength >= 0.7):
                return TrendSignalType.PREMIUM_PULLBACK
            
            # STRONG PULLBACK (75-89%)
            elif (confluence_score >= 0.70 and
                  pullback_quality >= 0.6 and
                  confluence_at_level >= 0.5):
                return TrendSignalType.STRONG_PULLBACK
        
        # BREAKOUT SIGNALS (MOINS PRÉFÉRÉS)
        else:
            # Détection breakout avec volume exceptionnel
            volume_exceptional = self._detect_exceptional_volume()
            sierra_strength = features.sierra_pattern_strength
            
            # PREMIUM BREAKOUT (80-95%)
            if (confluence_score >= 0.80 and
                volume_exceptional and
                sierra_strength >= 0.8 and
                trend_structure.strength >= 0.8):
                return TrendSignalType.PREMIUM_BREAKOUT
        
        # STRONG TREND (70-84%)
        if (confluence_score >= TRADING_THRESHOLDS['STRONG_SIGNAL'] and
            trend_structure.strength >= self.min_trend_strength):
            return TrendSignalType.STRONG_TREND
        
        # WEAK SIGNAL (60-69%)
        elif confluence_score >= TRADING_THRESHOLDS['WEAK_SIGNAL']:
            return TrendSignalType.WEAK_SIGNAL
        
        return TrendSignalType.NO_TRADE
    
    def _generate_trend_signal(self,
                             signal_type: TrendSignalType,
                             trend_structure: TrendStructure,
                             pullback_data: Optional[PullbackData],
                             market_data: MarketData,
                             confluence_score: float,
                             sierra_patterns: Dict[str, float]) -> TrendSignalData:
        """
        GÉNÉRATION SIGNAL TENDANCE COMPLET
        
        Calcule :
        - Prix d'entrée optimal
        - Stop loss selon structure Dow
        - Take profit selon R:R target
        - Position size selon hiérarchie
        """
        
        direction = trend_structure.direction
        current_price = market_data.close
        
        # CALCUL PRIX D'ENTRÉE
        if pullback_data and pullback_data.pullback_detected:
            # Entrée pullback : zone optimale
            entry_zone = pullback_data.optimal_entry_zone
            entry_price = (entry_zone[0] + entry_zone[1]) / 2
            entry_reason = f"Pullback {pullback_data.current_retracement:.1%}"
        else:
            # Entrée breakout : prix actuel + buffer
            entry_price = current_price
            entry_reason = "Trend continuation"
        
        # CALCUL STOP LOSS (STRUCTURE DOW)
        if direction == TrendDirection.BULLISH:
            # Stop sous dernier HL ou support clé
            structural_stop = trend_structure.key_support
            stop_loss = structural_stop - (2 * ES_TICK_SIZE)  # Buffer 2 ticks
            
        elif direction == TrendDirection.BEARISH:
            # Stop au-dessus dernier LH ou résistance clé
            structural_stop = trend_structure.key_resistance  
            stop_loss = structural_stop + (2 * ES_TICK_SIZE)
            
        else:
            # Fallback pour transition
            stop_distance = 10 * ES_TICK_SIZE  # Default 10 ticks
            if direction == TrendDirection.BULLISH:
                stop_loss = entry_price - stop_distance
            else:
                stop_loss = entry_price + stop_distance
        
        # CALCUL TAKE PROFIT
        risk_ticks = abs(entry_price - stop_loss) / ES_TICK_SIZE
        target_ticks = risk_ticks * self.target_risk_reward
        
        if direction == TrendDirection.BULLISH:
            take_profit = entry_price + (target_ticks * ES_TICK_SIZE)
        else:
            take_profit = entry_price - (target_ticks * ES_TICK_SIZE)
        
        # CALCUL POSITION SIZE
        position_multiplier = self._get_position_multiplier(signal_type)
        base_size = self.base_position_size
        position_size = base_size * position_multiplier
        
        # Limitation risque maximum
        max_risk_ticks = min(risk_ticks, self.max_risk_per_trade)
        if risk_ticks > self.max_risk_per_trade:
            # Réduire position size si risque trop élevé
            position_size *= (self.max_risk_per_trade / risk_ticks)
        
        return TrendSignalData(
            timestamp=market_data.timestamp,
            signal_type=signal_type,
            direction=direction,
            entry_price=entry_price,
            entry_reason=entry_reason,
            confluence_score=confluence_score,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size,
            max_risk_ticks=max_risk_ticks,
            trend_structure=trend_structure,
            pullback_data=pullback_data,
            sierra_patterns=sierra_patterns
        )
    
    def _get_position_multiplier(self, signal_type: TrendSignalType) -> float:
        """Multiplicateur position selon hiérarchie signal"""
        multipliers = {
            TrendSignalType.PREMIUM_PULLBACK: 1.8,  # Max size pour premium pullback
            TrendSignalType.STRONG_PULLBACK: 1.5,   # Size élevée pour pullback
            TrendSignalType.PREMIUM_BREAKOUT: 1.3,  # Size modérée pour breakout
            TrendSignalType.STRONG_TREND: 1.0,      # Size standard
            TrendSignalType.WEAK_SIGNAL: 0.5,       # Size réduite
            TrendSignalType.NO_TRADE: 0.0           # Pas de trade
        }
        return multipliers.get(signal_type, 0.0)
    
    def _validate_signal(self, signal: TrendSignalData) -> bool:
        """
        VALIDATION FINALE SIGNAL
        
        Vérifications :
        - R:R acceptable
        - Risque dans limites
        - Structure intacte
        - Pas de contre-indication
        """
        
        # R:R minimum
        if signal.risk_reward_ratio() < 1.2:
            logger.warning(f"R:R trop faible: {signal.risk_reward_ratio():.2f}")
            return False
        
        # Risque maximum
        if signal.max_risk_ticks > self.max_risk_per_trade:
            logger.warning(f"Risque trop élevé: {signal.max_risk_ticks:.1f} ticks")
            return False
        
        # Structure intacte
        if not signal.trend_structure.structure_intact:
            logger.warning("Structure Dow compromise")
            return False
        
        # Confluence minimum pour signal fort
        min_confluence = {
            TrendSignalType.PREMIUM_PULLBACK: 0.85,
            TrendSignalType.STRONG_PULLBACK: 0.70,
            TrendSignalType.PREMIUM_BREAKOUT: 0.80,
            TrendSignalType.STRONG_TREND: 0.70,
            TrendSignalType.WEAK_SIGNAL: 0.60
        }
        
        required_confluence = min_confluence.get(signal.signal_type, 0.60)
        if signal.confluence_score < required_confluence:
            logger.warning(f"Confluence insuffisante: {signal.confluence_score:.2f} < {required_confluence:.2f}")
            return False
        
        return True
    
    # === HELPER METHODS ===
    
    def _calculate_momentum_score(self, bars: List[MarketData]) -> float:
        """Calcul score momentum"""
        if len(bars) < 10:
            return 0.5
        
        closes = [bar.close for bar in bars[-10:]]
        momentum = np.polyfit(range(10), closes, 1)[0]
        return min(abs(momentum) / ES_TICK_SIZE, 1.0)
    
    def _calculate_volume_trend(self, bars: List[MarketData]) -> float:
        """Calcul tendance volume"""
        if len(bars) < 10:
            return 0.5
        
        volumes = [bar.volume for bar in bars[-10:]]
        volume_trend = np.polyfit(range(10), volumes, 1)[0]
        avg_volume = np.mean(volumes)
        
        return min(abs(volume_trend) / avg_volume, 1.0) if avg_volume > 0 else 0.5
    
    def _check_es_nq_alignment(self, structure_data: Optional[Dict[str, Any]]) -> bool:
        """Vérification alignment ES/NQ"""
        if not structure_data:
            return False
        
        es_nq_corr = structure_data.get('es_nq_correlation', 0.0)
        return es_nq_corr > 0.7
    
    def _evaluate_pullback_quality(self,
                                 retracement_pct: float,
                                 market_data: MarketData,
                                 structure_data: Optional[Dict[str, Any]]) -> float:
        """Évaluation qualité pullback"""
        quality = 0.0
        
        # 1. Fibonacci level (40%)
        if 0.35 <= retracement_pct <= 0.65:  # Sweet spot
            quality += 0.4
        elif 0.25 <= retracement_pct <= 0.80:  # Acceptable
            quality += 0.2
        
        # 2. Volume support (30%)
        if self._check_volume_support(market_data):
            quality += 0.3
        
        # 3. Time factor (30%)
        # Si pullback pas trop long = mieux
        # À implémenter avec timing réel
        quality += 0.2  # Default
        
        return min(quality, 1.0)
    
    def _calculate_pullback_confluence(self,
                                     price: float,
                                     structure_data: Optional[Dict[str, Any]]) -> float:
        """Confluence au niveau pullback"""
        if not structure_data:
            return 0.0
        
        confluence = 0.0
        
        # VWAP proximity
        vwap = structure_data.get('vwap_price', 0)
        if vwap and abs(price - vwap) <= 2 * ES_TICK_SIZE:
            confluence += 0.3
        
        # MP levels proximity  
        poc = structure_data.get('poc_price', 0)
        if poc and abs(price - poc) <= 1.5 * ES_TICK_SIZE:
            confluence += 0.4
        
        # Gamma levels
        put_wall = structure_data.get('put_wall', 0)
        if put_wall and abs(price - put_wall) <= 3 * ES_TICK_SIZE:
            confluence += 0.3
        
        return min(confluence, 1.0)
    
    def _calculate_optimal_entry_zone(self,
                                    trend_structure: TrendStructure,
                                    retracement_pct: float) -> Tuple[float, float]:
        """Zone d'entrée optimale"""
        if trend_structure.direction == TrendDirection.BULLISH:
            high = trend_structure.last_higher_high
            low = trend_structure.key_support
            
            # Zone entre 38.2% et 61.8% de retracement
            zone_low = high - (high - low) * 0.618
            zone_high = high - (high - low) * 0.382
            
        else:  # BEARISH
            low = trend_structure.last_lower_low
            high = trend_structure.key_resistance
            
            zone_low = low + (high - low) * 0.382
            zone_high = low + (high - low) * 0.618
        
        return (zone_low, zone_high)
    
    def _check_volume_support(self, market_data: MarketData) -> bool:
        """Vérification support volume"""
        if len(self.price_history) < 10:
            return False
        
        recent_volumes = [bar.volume for bar in list(self.price_history)[-10:]]
        avg_volume = np.mean(recent_volumes)
        
        return market_data.volume > avg_volume * 1.1  # 10% au-dessus moyenne
    
    def _detect_exceptional_volume(self) -> bool:
        """Détection volume exceptionnel"""
        if len(self.price_history) < 20:
            return False
        
        recent_volumes = [bar.volume for bar in list(self.price_history)[-20:]]
        current_volume = self.price_history[-1].volume
        avg_volume = np.mean(recent_volumes[:-1])
        
        return current_volume > avg_volume * 2.0  # 2x volume moyen
    
    def _update_stats(self, signal: TrendSignalData):
        """Mise à jour statistiques"""
        self.stats['signals_generated'] += 1
        
        if signal.pullback_data and signal.pullback_data.pullback_detected:
            self.stats['pullback_signals'] += 1
        else:
            self.stats['breakout_signals'] += 1
        
        # Rolling averages
        count = self.stats['signals_generated']
        prev_trend_avg = self.stats['trend_strength_avg']
        prev_conf_avg = self.stats['avg_confluence_score']
        
        self.stats['trend_strength_avg'] = ((prev_trend_avg * (count - 1)) + signal.trend_structure.strength) / count
        self.stats['avg_confluence_score'] = ((prev_conf_avg * (count - 1)) + signal.confluence_score) / count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques stratégie"""
        total_signals = self.stats['signals_generated']
        
        return {
            'total_signals': total_signals,
            'pullback_signals': self.stats['pullback_signals'],
            'breakout_signals': self.stats['breakout_signals'],
            'pullback_preference_pct': (self.stats['pullback_signals'] / total_signals * 100) if total_signals > 0 else 0,
            'avg_trend_strength': round(self.stats['trend_strength_avg'], 3),
            'avg_confluence_score': round(self.stats['avg_confluence_score'], 3),
            'current_trend_direction': self.current_trend.direction.value if self.current_trend else "none",
            'active_pullback': self.active_pullback.pullback_detected if self.active_pullback else False
        }

# === FACTORY FUNCTIONS ===

def create_trend_strategy(config: Optional[Dict[str, Any]] = None) -> TrendStrategy:
    """Factory function pour stratégie tendance"""
    return TrendStrategy(config)

def analyze_trend_opportunity(features: FeatureCalculationResult,
                            market_data: MarketData,
                            structure_data: Optional[Dict[str, Any]] = None,
                            sierra_patterns: Optional[Dict[str, float]] = None,
                            strategy: Optional[TrendStrategy] = None) -> Optional[TrendSignalData]:
    """Helper function pour analyse tendance"""
    
    if strategy is None:
        strategy = create_trend_strategy()
    
    return strategy.analyze_trend_signal(
        features=features,
        market_data=market_data,
        structure_data=structure_data,
        sierra_patterns=sierra_patterns
    )

# === TESTING ===

def test_trend_strategy():
    """Test complet stratégie tendance"""
    logger.debug("TEST TREND STRATEGY")
    print("=" * 40)
    
    # Création stratégie
    strategy = create_trend_strategy()
    
    # Simulation données
    from features.feature_calculator import FeatureCalculationResult, SignalQuality
    
    # Features test (confluence élevée)
    features = FeatureCalculationResult(
        timestamp=pd.Timestamp.now(),
        confluence_score=0.87,  # Premium signal
        signal_quality=SignalQuality.PREMIUM
    )
    
    # Market data test
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4500.0,
        high=4510.0,
        low=4495.0,
        close=4505.0,
        volume=2000
    )
    
    # Structure data test
    structure_data = {
        'vwap_price': 4502.0,
        'poc_price': 4501.0,
        'put_wall': 4480.0,
        'es_nq_correlation': 0.8
    }
    
    # Sierra patterns test
    sierra_patterns = {
        'battle_navale_signal': 0.85,
        'base_quality': 0.80,
        'trend_continuation': 0.90
    }
    
    # Simulation historique pour structure Dow
    for i in range(35):
        test_bar = MarketData(
            timestamp=pd.Timestamp.now() - pd.Timedelta(minutes=35-i),
            symbol="ES",
            open=4480.0 + i,
            high=4485.0 + i,
            low=4475.0 + i,
            close=4482.0 + i,
            volume=1500
        )
        strategy.price_history.append(test_bar)
    
    # Analyse signal
    signal = strategy.analyze_trend_signal(
        features=features,
        market_data=market_data,
        structure_data=structure_data,
        sierra_patterns=sierra_patterns
    )
    
    if signal:
        logger.info("Signal généré: {signal.signal_type.value}")
        logger.info("Direction: {signal.direction.value}")
        logger.info("Entry: {signal.entry_price:.2f}")
        logger.info("Stop: {signal.stop_loss:.2f}")
        logger.info("Target: {signal.take_profit:.2f}")
        logger.info("R:R: {signal.risk_reward_ratio():.2f}")
        logger.info("Position size: {signal.position_size:.1f}")
        logger.info("Confluence: {signal.confluence_score:.2f}")
        
        if signal.pullback_data:
            logger.info("Pullback: {signal.pullback_data.current_retracement:.1%}")
    else:
        logger.error("Aucun signal généré")
    
    # Statistiques
    stats = strategy.get_statistics()
    logger.info("\n📊 STATISTICS:")
    for key, value in stats.items():
        logger.info("   • {key}: {value}")
    
    logger.info("\n🎯 TREND STRATEGY TEST COMPLETED")
    return True

if __name__ == "__main__":
    test_trend_strategy()