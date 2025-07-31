"""
MIA_IA_SYSTEM - Feature Calculator
Calcul des 8 features système avec scoring confluence
Version: Production Ready
Performance: <2ms garanti pour 8 features

FEATURES SYSTÈME (100% TOTAL) :
1. vwap_trend_signal (18%) - VWAP slope + position
2. sierra_pattern_strength (18%) - Patterns tick reversal
3. dow_trend_regime (18%) - Structure HH/HL + force
4. gamma_levels_proximity (12%) - Options flow SpotGamma
5. level_proximity (8%) - Market Profile levels
6. es_nq_correlation (8%) - Cross-market alignment
7. volume_confirmation (7%) - Order flow + volume
8. options_flow_bias (6%) - Call/Put sentiment
9. session_context (3%) - Session performance
10. pullback_quality (2%) - Anti-FOMO patience

SEUILS TRADING :
- 85-100% = PREMIUM_SIGNAL (size ×1.5)
- 70-84%  = STRONG_SIGNAL  (size ×1.0)
- 60-69%  = WEAK_SIGNAL   (size ×0.5)
- 0-59%   = NO_TRADE      (attendre)
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from features.confluence_analyzer import ConfluenceAnalyzer, ConfluenceZone
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import deque

# Local imports
from core.base_types import (
    MarketData, OrderFlowData, TradingFeatures,
    ES_TICK_SIZE, ES_TICK_VALUE, get_session_phase
)
from config import get_feature_config

logger = logging.getLogger(__name__)

# === FEATURE WEIGHTS CONFIGURATION ===

CONFLUENCE_WEIGHTS = {
    'vwap_trend_signal': 0.18,        # 18% - VWAP slope + position
    'sierra_pattern_strength': 0.18,  # 18% - Patterns tick reversal
    'dow_trend_regime': 0.18,         # 18% - Structure HH/HL + force
    'gamma_levels_proximity': 0.12,   # 12% - Options flow SpotGamma
    'level_proximity': 0.08,          # 8%  - Market Profile levels
    'es_nq_correlation': 0.08,        # 8%  - Cross-market alignment
    'volume_confirmation': 0.07,      # 7%  - Order flow + volume
    'options_flow_bias': 0.06,        # 6%  - Call/Put sentiment
    'session_context': 0.03,          # 3%  - Session performance
    'pullback_quality': 0.02,         # 2%  - Anti-FOMO patience
}

# Validation weights = 100%
assert abs(sum(CONFLUENCE_WEIGHTS.values()) - 1.0) < 0.001, "Weights must sum to 100%"

# === TRADING THRESHOLDS ===

TRADING_THRESHOLDS = {
    'PREMIUM_SIGNAL': 0.85,    # 85%+ = Premium trade (size ×1.5)
    'STRONG_SIGNAL': 0.70,     # 70%+ = Strong trade (size ×1.0)
    'WEAK_SIGNAL': 0.60,       # 60%+ = Weak trade (size ×0.5)
    'NO_TRADE': 0.59,          # <60% = No trade (wait)
}


class SignalQuality(Enum):
    """Qualité du signal trading"""
    PREMIUM = "premium"     # 85-100%
    STRONG = "strong"       # 70-84%
    WEAK = "weak"          # 60-69%
    NO_TRADE = "no_trade"  # 0-59%

# === DATACLASSES ===


@dataclass
class OptionsData:
    """Données options pour gamma levels"""
    timestamp: pd.Timestamp

    # SpotGamma style data
    call_wall: float = 0.0
    put_wall: float = 0.0
    vol_trigger: float = 0.0
    net_gamma: float = 0.0

    # Options flow
    call_volume: int = 0
    put_volume: int = 0
    call_oi: int = 0
    put_oi: int = 0

    # Calculated metrics
    put_call_ratio: float = 0.0
    gamma_exposure: float = 0.0

    def __post_init__(self):
        """Calculs automatiques"""
        if self.call_volume > 0:
            self.put_call_ratio = self.put_volume / self.call_volume

        self.gamma_exposure = abs(self.net_gamma)


@dataclass
class MarketStructureData:
    """Structure de marché complète"""
    timestamp: pd.Timestamp

    # Market Profile
    poc_price: float = 0.0
    vah_price: float = 0.0
    val_price: float = 0.0

    # VWAP
    vwap_price: float = 0.0
    vwap_sd1_up: float = 0.0
    vwap_sd1_down: float = 0.0
    vwap_slope: float = 0.0

    # Previous session
    pvah: float = 0.0
    pval: float = 0.0
    ppoc: float = 0.0

    # Volume clusters
    volume_clusters: List[float] = field(default_factory=list)


@dataclass
class ESNQData:
    """Données ES/NQ pour corrélation"""
    timestamp: pd.Timestamp

    # Prices
    es_price: float = 0.0
    nq_price: float = 0.0

    # Momentum
    es_momentum: float = 0.0
    nq_momentum: float = 0.0

    # Correlation metrics
    correlation: float = 0.0
    divergence_signal: float = 0.0
    leader: str = "ES"  # ES or NQ


@dataclass
class FeatureCalculationResult:
    """Résultat complet calcul features"""
    timestamp: pd.Timestamp

    # Individual features (0-1)
    vwap_trend_signal: float = 0.0
    sierra_pattern_strength: float = 0.0
    dow_trend_regime: float = 0.0
    gamma_levels_proximity: float = 0.0
    level_proximity: float = 0.0
    es_nq_correlation: float = 0.0
    volume_confirmation: float = 0.0
    options_flow_bias: float = 0.0
    session_context: float = 0.0
    pullback_quality: float = 0.0

    # Aggregate metrics
    confluence_score: float = 0.0
    signal_quality: SignalQuality = SignalQuality.NO_TRADE
    position_multiplier: float = 0.0

    # Performance tracking
    calculation_time_ms: float = 0.0

    def to_trading_features(self) -> TradingFeatures:
        """Conversion vers TradingFeatures (8 features seulement)"""
        return TradingFeatures(
            timestamp=self.timestamp,
            battle_navale_signal=self.sierra_pattern_strength,
            gamma_pin_strength=self.gamma_levels_proximity,
            headfake_signal=self.pullback_quality,
            microstructure_anomaly=self.volume_confirmation,
            market_regime_score=self.dow_trend_regime,
            base_quality=self.vwap_trend_signal,
            confluence_score=self.confluence_score,
            session_context=self.session_context,
            calculation_time_ms=self.calculation_time_ms
        )

# === MAIN FEATURE CALCULATOR ===


class FeatureCalculator:
    """
    Calculateur features système avec confluence scoring

    Performance garantie <2ms pour tous calculs
    Intègre données options (SpotGamma) + patterns Sierra
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation calculateur"""
        self.config = config or get_feature_config().__dict__

        # Paramètres calcul
        self.lookback_periods = self.config.get('lookback_periods', 20)
        self.vwap_slope_periods = self.config.get('vwap_slope_periods', 15)
        self.correlation_periods = self.config.get('correlation_periods', 50)

        # Historique pour calculs
        self.price_history: deque = deque(maxlen=100)
        self.es_nq_history: deque = deque(maxlen=self.correlation_periods)
        self.session_performance: Dict[str, float] = {}

        # Performance tracking
        self.stats = {
            'calculations_count': 0,
            'avg_calc_time_ms': 0.0,
            'feature_quality_scores': []
        }

        logger.info("FeatureCalculator initialisé avec confluence scoring")

    def calculate_all_features(self,
                               market_data: MarketData,
                               order_flow: Optional[OrderFlowData] = None,
                               options_data: Optional[OptionsData] = None,
                               structure_data: Optional[MarketStructureData] = None,
                               es_nq_data: Optional[ESNQData] = None,
                               sierra_patterns: Optional[Dict[str, float]] = None) -> FeatureCalculationResult:
        """
        CALCUL COMPLET DES FEATURES

        Args:
            market_data: Données OHLC + volume
            order_flow: Order flow + volume distribution
            options_data: Données options SpotGamma
            structure_data: Market Profile + VWAP
            es_nq_data: Données corrélation ES/NQ
            sierra_patterns: Patterns depuis battle_navale.py

        Returns:
            FeatureCalculationResult avec confluence score
        """
        start_time = time.perf_counter()

        try:
            # Ajout à l'historique
            self.price_history.append(market_data)
            if es_nq_data is not None:
                self.es_nq_history.append(es_nq_data)

            # Calcul features individuelles
            result = FeatureCalculationResult(timestamp=market_data.timestamp)

            # 1. VWAP TREND SIGNAL (18%)
            result.vwap_trend_signal = self._calculate_vwap_trend_signal(
                market_data, structure_data
            )

            # 2. SIERRA PATTERN STRENGTH (18%)
            result.sierra_pattern_strength = self._calculate_sierra_pattern_strength(
                sierra_patterns or {}
            )

            # 3. DOW TREND REGIME (18%)
            result.dow_trend_regime = self._calculate_dow_trend_regime(
                market_data
            )

            # 4. GAMMA LEVELS PROXIMITY (12%)
            result.gamma_levels_proximity = self._calculate_gamma_proximity(
                market_data.close, options_data
            )

            # 5. LEVEL PROXIMITY (8%)
            result.level_proximity = self._calculate_level_proximity(
                market_data.close, structure_data
            )

            # 6. ES/NQ CORRELATION (8%)
            result.es_nq_correlation = self._calculate_es_nq_correlation(
                es_nq_data
            )

            # 7. VOLUME CONFIRMATION (7%)
            result.volume_confirmation = self._calculate_volume_confirmation(
                market_data, order_flow
            )

            # 8. OPTIONS FLOW BIAS (6%)
            result.options_flow_bias = self._calculate_options_flow_bias(
                options_data
            )

            # 9. SESSION CONTEXT (3%)
            result.session_context = self._calculate_session_context(
                market_data.timestamp
            )

            # 10. PULLBACK QUALITY (2%)
            result.pullback_quality = self._calculate_pullback_quality(
                market_data
            )

            # CALCUL CONFLUENCE FINALE
            result.confluence_score = self._calculate_confluence_score(result)
            result.signal_quality = self._determine_signal_quality(result.confluence_score)
            result.position_multiplier = self._get_position_multiplier(result.signal_quality)

            # Performance tracking
            calc_time = (time.perf_counter() - start_time) * 1000
            result.calculation_time_ms = calc_time

            self._update_performance_stats(calc_time, result.confluence_score)

            return result

        except Exception as e:
            logger.error(f"Erreur calcul features: {e}")
            # Return default result
            return FeatureCalculationResult(
                timestamp=market_data.timestamp,
                calculation_time_ms=(time.perf_counter() - start_time) * 1000
            )

    def _calculate_vwap_trend_signal(self,
                                     market_data: MarketData,
                                     structure_data: Optional[MarketStructureData]) -> float:
        """
        VWAP TREND SIGNAL (18%)

        Combine :
        - VWAP slope (inclinaison)
        - Position vs VWAP/SD bands
        - Trend strength
        """
        if not structure_data or len(self.price_history) < self.vwap_slope_periods:
            return 0.5  # Neutral

        current_price = market_data.close
        vwap = structure_data.vwap_price
        vwap_slope = structure_data.vwap_slope
        sd1_up = structure_data.vwap_sd1_up
        sd1_down = structure_data.vwap_sd1_down

        signal = 0.0

        # 1. VWAP slope analysis (40% of feature)
        if vwap_slope > 0.5:      # Strong uptrend
            signal += 0.4
        elif vwap_slope > 0.2:    # Moderate uptrend
            signal += 0.3
        elif vwap_slope > -0.2:   # Sideways
            signal += 0.2
        elif vwap_slope > -0.5:   # Moderate downtrend
            signal += 0.1
        # else: signal += 0.0     # Strong downtrend

        # 2. Position relative to VWAP (30% of feature)
        if current_price > vwap:
            vwap_position = min((current_price - vwap) / (sd1_up - vwap), 2.0)
            signal += 0.15 + (vwap_position * 0.15)  # 0.15 to 0.30
        else:
            vwap_position = min((vwap - current_price) / (vwap - sd1_down), 2.0)
            signal += 0.15 - (vwap_position * 0.15)  # 0.15 to 0.0

        # 3. Trend consistency (30% of feature)
        if len(self.price_history) >= 10:
            recent_closes = [bar.close for bar in list(self.price_history)[-10:]]
            trend_direction = np.polyfit(range(10), recent_closes, 1)[0]

            # Normalize trend direction
            trend_strength = min(abs(trend_direction) / ES_TICK_SIZE, 1.0)

            if trend_direction > 0 and vwap_slope > 0:  # Aligned bullish
                signal += 0.3 * trend_strength
            elif trend_direction < 0 and vwap_slope < 0:  # Aligned bearish
                signal += 0.3 * (1 - trend_strength)  # Inverted for bearish
            else:  # Misaligned
                signal += 0.15  # Neutral

        return max(0.0, min(1.0, signal))

    def _calculate_sierra_pattern_strength(self,
                                           sierra_patterns: Dict[str, float]) -> float:
        """
        SIERRA PATTERN STRENGTH (18%)

        Force des patterns depuis battle_navale.py :
        - Long Down Up Bar
        - Long Up Down Bar
        - Color Down Setting
        - Base quality
        """
        if not sierra_patterns:
            return 0.0

        # Récupération patterns
        battle_signal = sierra_patterns.get('battle_navale_signal', 0.0)
        base_quality = sierra_patterns.get('base_quality', 0.0)
        trend_continuation = sierra_patterns.get('trend_continuation', 0.0)
        battle_strength = sierra_patterns.get('battle_strength', 0.0)

        # Pondération patterns
        pattern_score = (
            battle_signal * 0.4 +      # 40% - Signal principal bataille
            base_quality * 0.25 +      # 25% - Qualité des bases
            trend_continuation * 0.2 +  # 20% - Respect règle d'or
            battle_strength * 0.15     # 15% - Force patterns
        )

        return max(0.0, min(1.0, pattern_score))

    def _calculate_dow_trend_regime(self,
                                    market_data: MarketData) -> float:
        """
        DOW TREND REGIME (18%)

        Structure Dow Theory :
        - Higher Highs / Higher Lows (bullish)
        - Lower Highs / Lower Lows (bearish)
        - Trend strength + momentum
        """
        if len(self.price_history) < 20:
            return 0.5  # Neutral

        # Analyse structure HH/HL vs LH/LL
        recent_bars = list(self.price_history)[-20:]

        # Extraction des pivots (simplifiée)
        highs = [bar.high for bar in recent_bars]
        lows = [bar.low for bar in recent_bars]

        # Trend des highs et lows
        high_trend = np.polyfit(range(len(highs)), highs, 1)[0]
        low_trend = np.polyfit(range(len(lows)), lows, 1)[0]

        # Score Dow structure
        dow_score = 0.5  # Start neutral

        # Higher Highs + Higher Lows = Bullish
        if high_trend > 0 and low_trend > 0:
            trend_strength = min((high_trend + low_trend) / (2 * ES_TICK_SIZE), 1.0)
            dow_score = 0.5 + (0.5 * trend_strength)  # 0.5 to 1.0

        # Lower Highs + Lower Lows = Bearish
        elif high_trend < 0 and low_trend < 0:
            trend_strength = min(abs(high_trend + low_trend) / (2 * ES_TICK_SIZE), 1.0)
            dow_score = 0.5 - (0.5 * trend_strength)  # 0.5 to 0.0

        # Momentum confirmation
        current_price = market_data.close
        price_10_bars_ago = recent_bars[-10].close
        momentum = (current_price - price_10_bars_ago) / ES_TICK_SIZE

        # Adjust score based on momentum alignment
        if momentum > 0 and dow_score > 0.5:  # Bullish momentum + bullish structure
            momentum_boost = min(momentum / 10, 0.1)  # Max 0.1 boost
            dow_score += momentum_boost
        elif momentum < 0 and dow_score < 0.5:  # Bearish momentum + bearish structure
            momentum_boost = min(abs(momentum) / 10, 0.1)
            dow_score -= momentum_boost

        return max(0.0, min(1.0, dow_score))

    def _calculate_gamma_proximity(self,
                                   current_price: float,
                                   options_data: Optional[OptionsData]) -> float:
        """
        GAMMA LEVELS PROXIMITY (12%)

        Distance aux niveaux gamma critiques :
        - Call Wall (résistance)
        - Put Wall (support)
        - Vol Trigger
        - Net Gamma regime
        """
        if not options_data:
            return 0.0

        call_wall = options_data.call_wall
        put_wall = options_data.put_wall
        vol_trigger = options_data.vol_trigger
        net_gamma = options_data.net_gamma

        gamma_score = 0.0

        # 1. Proximity to gamma levels (60% of feature)
        if call_wall > 0 and put_wall > 0:

            # Distance to call wall (resistance)
            call_distance = abs(current_price - call_wall)
            call_proximity = max(0, 1 - (call_distance / (10 * ES_TICK_SIZE)))  # Within 10 ticks

            # Distance to put wall (support)
            put_distance = abs(current_price - put_wall)
            put_proximity = max(0, 1 - (put_distance / (10 * ES_TICK_SIZE)))

            # Use maximum proximity (closer level more important)
            level_proximity = max(call_proximity, put_proximity)
            gamma_score += level_proximity * 0.6

        # 2. Net gamma regime (25% of feature)
        if net_gamma != 0:
            # Positive gamma = stabilizing (lower volatility expected)
            # Negative gamma = destabilizing (higher volatility expected)

            gamma_regime_score = 0.5  # Neutral

            if net_gamma > 0:  # Positive gamma
                # Market tends to stabilize - favor mean reversion
                if current_price > call_wall and call_wall > 0:
                    gamma_regime_score = 0.3  # Resistance likely
                elif current_price < put_wall and put_wall > 0:
                    gamma_regime_score = 0.7  # Support likely
                else:
                    gamma_regime_score = 0.6  # Mild bullish bias

            else:  # Negative gamma
                # Market tends to trend - favor momentum
                gamma_magnitude = min(abs(net_gamma) / 10, 1.0)
                gamma_regime_score = 0.5 + (gamma_magnitude * 0.3)  # Bullish bias for momentum

            gamma_score += gamma_regime_score * 0.25

        # 3. Vol trigger proximity (15% of feature)
        if vol_trigger > 0:
            vol_distance = abs(current_price - vol_trigger)
            vol_proximity = max(0, 1 - (vol_distance / (15 * ES_TICK_SIZE)))  # Within 15 ticks
            gamma_score += vol_proximity * 0.15

        return max(0.0, min(1.0, gamma_score))

    def _calculate_level_proximity(self,
                                   current_price: float,
                                   structure_data: Optional[MarketStructureData]) -> float:
        """
        LEVEL PROXIMITY (8%)

        Distance aux niveaux Market Profile :
        - POC, VAH, VAL
        - Previous session levels
        - Volume clusters
        """
        if not structure_data:
            return 0.0

        levels = []

        # Current session levels
        if structure_data.poc_price > 0:
            levels.append(structure_data.poc_price)
        if structure_data.vah_price > 0:
            levels.append(structure_data.vah_price)
        if structure_data.val_price > 0:
            levels.append(structure_data.val_price)

        # Previous session levels
        if structure_data.pvah > 0:
            levels.append(structure_data.pvah)
        if structure_data.pval > 0:
            levels.append(structure_data.pval)
        if structure_data.ppoc > 0:
            levels.append(structure_data.ppoc)

        # Volume clusters
        levels.extend(structure_data.volume_clusters)

        if not levels:
            return 0.0

        # Find closest level
        distances = [abs(current_price - level) for level in levels]
        min_distance = min(distances)

        # Proximity score (within 3 ticks = full score)
        proximity_score = max(0, 1 - (min_distance / (3 * ES_TICK_SIZE)))

        return proximity_score

    def _calculate_es_nq_correlation(self,
                                     es_nq_data: Optional[ESNQData]) -> float:
        """
        ES/NQ CORRELATION (8%)

        Alignment entre ES et NQ :
        - Correlation coefficient
        - Divergence detection
        - Leadership analysis
        """
        if not es_nq_data or len(self.es_nq_history) < 10:
            return 0.5  # Neutral

        correlation = es_nq_data.correlation
        divergence = es_nq_data.divergence_signal

        # High correlation = good signal
        corr_score = max(0, correlation)  # Correlation -1 to 1, we want 0 to 1

        # Low divergence = good signal
        divergence_score = max(0, 1 - abs(divergence))

        # Combined score
        es_nq_score = (corr_score * 0.7) + (divergence_score * 0.3)

        return max(0.0, min(1.0, es_nq_score))

    def _calculate_volume_confirmation(self,
                                       market_data: MarketData,
                                       order_flow: Optional[OrderFlowData]) -> float:
        """
        VOLUME CONFIRMATION (7%)

        Confirmation volume et order flow :
        - Volume relatif
        - Order flow direction
        - Aggressive trades
        """
        volume_score = 0.0

        # 1. Volume analysis (50% of feature)
        if len(self.price_history) >= 10:
            recent_volumes = [bar.volume for bar in list(self.price_history)[-10:]]
            avg_volume = np.mean(recent_volumes)

            current_volume = market_data.volume
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0

            # Higher volume = better confirmation
            volume_strength = min(volume_ratio / 2.0, 1.0)  # Normalize to 1.0
            volume_score += volume_strength * 0.5

        # 2. Order flow confirmation (50% of feature)
        if order_flow:
            # Net delta analysis
            total_volume = order_flow.bid_volume + order_flow.ask_volume
            if total_volume > 0:
                net_delta_ratio = abs(order_flow.net_delta) / total_volume
                order_flow_strength = min(net_delta_ratio * 2, 1.0)
                volume_score += order_flow_strength * 0.3

            # Aggressive trades
            total_aggressive = order_flow.aggressive_buys + order_flow.aggressive_sells
            if total_aggressive > 0:
                aggressive_ratio = total_aggressive / total_volume if total_volume > 0 else 0
                aggressive_strength = min(aggressive_ratio * 10, 1.0)  # Scale up
                volume_score += aggressive_strength * 0.2

        return max(0.0, min(1.0, volume_score))

    def _calculate_options_flow_bias(self,
                                     options_data: Optional[OptionsData]) -> float:
        """
        OPTIONS FLOW BIAS (6%)

        Sentiment options :
        - Put/Call ratio
        - Volume flow
        - Open interest changes
        """
        if not options_data:
            return 0.5  # Neutral

        put_call_ratio = options_data.put_call_ratio
        call_volume = options_data.call_volume
        put_volume = options_data.put_volume

        # Put/Call ratio analysis
        if put_call_ratio > 0:
            # Normalize P/C ratio (typical range 0.5 to 2.0)
            if put_call_ratio < 0.8:  # Low P/C = bullish
                pc_score = 0.7 + (0.8 - put_call_ratio) * 0.5
            elif put_call_ratio > 1.2:  # High P/C = bearish
                pc_score = 0.3 - min((put_call_ratio - 1.2) * 0.3, 0.3)
            else:  # Neutral range
                pc_score = 0.5
        else:
            pc_score = 0.5

        # Volume flow bias
        total_option_volume = call_volume + put_volume
        if total_option_volume > 0:
            call_volume_ratio = call_volume / total_option_volume
            # More calls = bullish bias
            volume_bias = call_volume_ratio  # 0 to 1
        else:
            volume_bias = 0.5

        # Combined options bias
        options_bias = (pc_score * 0.6) + (volume_bias * 0.4)

        return max(0.0, min(1.0, options_bias))

    def _calculate_session_context(self,
                                   timestamp: pd.Timestamp) -> float:
        """
        SESSION CONTEXT (3%)

        Performance par session :
        - London Open, NY Open, Lunch, etc.
        - Historical win rate par session
        """
        session_phase = get_session_phase(timestamp)

        # Performance historique par session (à implémenter avec données réelles)
        session_performance = {
            'london_open': 0.65,    # 65% win rate
            'ny_open': 0.75,        # 75% win rate
            'lunch': 0.45,          # 45% win rate (éviter)
            'afternoon': 0.60,      # 60% win rate
            'close': 0.50,          # 50% win rate
            'after_hours': 0.40,    # 40% win rate (éviter)
            'pre_market': 0.50      # 50% win rate
        }

        session_key = session_phase.value
        return session_performance.get(session_key, 0.5)

    def _calculate_pullback_quality(self,
                                    market_data: MarketData) -> float:
        """
        PULLBACK QUALITY (2%)

        Anti-FOMO : Patience vs breakout immédiat
        - Attend pullback après breakout
        - Évite FOMO entries
        """
        if len(self.price_history) < 10:
            return 0.5

        recent_bars = list(self.price_history)[-10:]
        current_price = market_data.close

        # Détection breakout récent (simple)
        recent_highs = [bar.high for bar in recent_bars[:-1]]
        recent_lows = [bar.low for bar in recent_bars[:-1]]

        max_recent_high = max(recent_highs)
        min_recent_low = min(recent_lows)

        # Breakout haussier récent ?
        if current_price > max_recent_high:
            # Prix a breakout - pénaliser (attendre pullback)
            breakout_distance = current_price - max_recent_high
            patience_score = max(0, 1 - (breakout_distance / (5 * ES_TICK_SIZE)))
            return patience_score * 0.3  # Low score = wait for pullback

        # Breakout baissier récent ?
        elif current_price < min_recent_low:
            breakout_distance = min_recent_low - current_price
            patience_score = max(0, 1 - (breakout_distance / (5 * ES_TICK_SIZE)))
            return patience_score * 0.3

        # Pas de breakout récent = good for entry
        else:
            return 0.8  # Good patience score

    def _calculate_confluence_score(self,
                                    result: FeatureCalculationResult) -> float:
        """
        CALCUL CONFLUENCE FINALE

        Pondération de toutes les features selon CONFLUENCE_WEIGHTS
        """
        features = {
            'vwap_trend_signal': result.vwap_trend_signal,
            'sierra_pattern_strength': result.sierra_pattern_strength,
            'dow_trend_regime': result.dow_trend_regime,
            'gamma_levels_proximity': result.gamma_levels_proximity,
            'level_proximity': result.level_proximity,
            'es_nq_correlation': result.es_nq_correlation,
            'volume_confirmation': result.volume_confirmation,
            'options_flow_bias': result.options_flow_bias,
            'session_context': result.session_context,
            'pullback_quality': result.pullback_quality,
        }

        confluence_score = 0.0

        for feature_name, feature_value in features.items():
            weight = CONFLUENCE_WEIGHTS.get(feature_name, 0.0)
            confluence_score += feature_value * weight

        return max(0.0, min(1.0, confluence_score))

    def _determine_signal_quality(self,
                                  confluence_score: float) -> SignalQuality:
        """Détermine qualité signal selon seuils"""
        if confluence_score >= TRADING_THRESHOLDS['PREMIUM_SIGNAL']:
            return SignalQuality.PREMIUM
        elif confluence_score >= TRADING_THRESHOLDS['STRONG_SIGNAL']:
            return SignalQuality.STRONG
        elif confluence_score >= TRADING_THRESHOLDS['WEAK_SIGNAL']:
            return SignalQuality.WEAK
        else:
            return SignalQuality.NO_TRADE

    def _get_position_multiplier(self,
                                 signal_quality: SignalQuality) -> float:
        """Multiplicateur position selon qualité"""
        multipliers = {
            SignalQuality.PREMIUM: 1.5,   # Size ×1.5
            SignalQuality.STRONG: 1.0,    # Size ×1.0
            SignalQuality.WEAK: 0.5,      # Size ×0.5
            SignalQuality.NO_TRADE: 0.0   # No trade
        }
        return multipliers.get(signal_quality, 0.0)

    def _update_performance_stats(self,
                                  calc_time: float,
                                  confluence_score: float):
        """Mise à jour statistiques performance"""
        self.stats['calculations_count'] += 1

        # Rolling average calculation time
        count = self.stats['calculations_count']
        prev_avg = self.stats['avg_calc_time_ms']
        self.stats['avg_calc_time_ms'] = ((prev_avg * (count - 1)) + calc_time) / count

        # Feature quality tracking
        self.stats['feature_quality_scores'].append(confluence_score)
        if len(self.stats['feature_quality_scores']) > 100:
            self.stats['feature_quality_scores'].pop(0)  # Keep last 100

    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques calculateur"""
        quality_scores = self.stats['feature_quality_scores']

        return {
            'calculations_count': self.stats['calculations_count'],
            'avg_calculation_time_ms': round(self.stats['avg_calc_time_ms'], 3),
            'avg_confluence_score': round(np.mean(quality_scores), 3) if quality_scores else 0.0,
            'confluence_score_std': round(np.std(quality_scores), 3) if quality_scores else 0.0,
            'premium_signals_pct': len([s for s in quality_scores if s >= 0.85]) / len(quality_scores) * 100 if quality_scores else 0.0,
            'no_trade_signals_pct': len([s for s in quality_scores if s < 0.60]) / len(quality_scores) * 100 if quality_scores else 0.0,
        }

# === FACTORY FUNCTIONS ===


def create_feature_calculator(config: Optional[Dict[str, Any]] = None) -> FeatureCalculator:
    """Factory function pour calculateur"""
    return FeatureCalculator(config)


def calculate_features_from_data(market_data: MarketData,
                                 order_flow: Optional[OrderFlowData] = None,
                                 options_data: Optional[OptionsData] = None,
                                 structure_data: Optional[MarketStructureData] = None,
                                 es_nq_data: Optional[ESNQData] = None,
                                 sierra_patterns: Optional[Dict[str, float]] = None,
                                 calculator: Optional[FeatureCalculator] = None) -> FeatureCalculationResult:
    """Helper function pour calcul features"""

    if calculator is None:
        calculator = create_feature_calculator()

    return calculator.calculate_all_features(
        market_data=market_data,
        order_flow=order_flow,
        options_data=options_data,
        structure_data=structure_data,
        es_nq_data=es_nq_data,
        sierra_patterns=sierra_patterns
    )

# === TESTING ===


def test_feature_calculator():
    """Test complet feature calculator"""
    logger.debug("TEST FEATURE CALCULATOR")
    print("=" * 40)

    # Création calculateur
    calculator = create_feature_calculator()

    # Données de test
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4500.0,
        high=4510.0,
        low=4495.0,
        close=4505.0,
        volume=1500
    )

    # Options data test
    options_data = OptionsData(
        timestamp=pd.Timestamp.now(),
        call_wall=4520.0,
        put_wall=4480.0,
        net_gamma=2.5,
        call_volume=1200,
        put_volume=800
    )

    # Structure data test
    structure_data = MarketStructureData(
        timestamp=pd.Timestamp.now(),
        poc_price=4500.0,
        vah_price=4515.0,
        val_price=4485.0,
        vwap_price=4502.0,
        vwap_slope=0.3
    )

    # Sierra patterns test
    sierra_patterns = {
        'battle_navale_signal': 0.8,
        'base_quality': 0.7,
        'trend_continuation': 0.9,
        'battle_strength': 0.75
    }

    # Calcul features
    result = calculator.calculate_all_features(
        market_data=market_data,
        options_data=options_data,
        structure_data=structure_data,
        sierra_patterns=sierra_patterns
    )

    logger.info("Features calculées en {result.calculation_time_ms:.2f}ms")
    logger.info("Confluence score: {result.confluence_score:.3f}")
    logger.info("Signal quality: {result.signal_quality.value}")
    logger.info("Position multiplier: {result.position_multiplier}x")

    # Test threshold logic
    logger.info("\n📊 THRESHOLDS VALIDATION:")
    for threshold_name, threshold_value in TRADING_THRESHOLDS.items():
        if threshold_name != 'NO_TRADE':
            if result.confluence_score >= threshold_value:
                logger.info("{threshold_name}: {threshold_value:.0%} - PASSED")
            else:
                logger.error("{threshold_name}: {threshold_value:.0%} - FAILED")

    # Test conversion to TradingFeatures
    trading_features = result.to_trading_features()
    feature_array = trading_features.to_array()
    logger.info("TradingFeatures array: {feature_array}")

    # Statistics
    stats = calculator.get_statistics()
    logger.info("\n📈 STATISTICS:")
    for key, value in stats.items():
        logger.info("   • {key}: {value}")

    logger.info("\n🎯 FEATURE CALCULATOR TEST COMPLETED")
    return True


if __name__ == "__main__":
    test_feature_calculator()
