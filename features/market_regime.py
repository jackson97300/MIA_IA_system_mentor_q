"""
MIA_IA_SYSTEM - Market Regime Detector
CERVEAU DU SYSTÈME - Détermine régime marché + bias directionnel
Version: Production Ready
Performance: Détection temps réel <3ms

RÉGIMES DÉTECTÉS :
1. STRONG_TREND_BULLISH   - Tendance haussière forte (HH/HL + VWAP slope+)
2. WEAK_TREND_BULLISH     - Tendance haussière faible (correction possible)
3. STRONG_TREND_BEARISH   - Tendance baissière forte (LH/LL + VWAP slope-)
4. WEAK_TREND_BEARISH     - Tendance baissière faible (correction possible)
5. RANGE_BULLISH_BIAS     - Range avec bias haussier (longs seulement)
6. RANGE_BEARISH_BIAS     - Range avec bias baissier (shorts seulement)
7. RANGE_NEUTRAL          - Range pur (both sides autorisés)
8. TRANSITION             - Changement régime en cours
9. UNCLEAR                - Pas de régime clair

FILTRES RANGE :
- Range minimum : 12 ticks (éviter micro-ranges)
- Range maximum : 50 ticks (éviter ranges trop larges)
- Durée minimum : 20 minutes
- Tests minimum : 3 par niveau

BIAS DETERMINATION :
- VWAP slope + Dow structure + Volume trend + ES/NQ correlation
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from core.logger import get_logger
from collections import deque
import statistics

# Local imports
from core.base_types import (
    MarketData, OrderFlowData, ES_TICK_SIZE, ES_TICK_VALUE,
    get_session_phase
)

logger = get_logger(__name__)

# === MARKET REGIME ENUMS ===


class MarketRegime(Enum):
    """Régimes de marché détaillés"""
    STRONG_TREND_BULLISH = "strong_trend_bullish"    # Trend fort haussier
    WEAK_TREND_BULLISH = "weak_trend_bullish"        # Trend faible haussier
    STRONG_TREND_BEARISH = "strong_trend_bearish"    # Trend fort baissier
    WEAK_TREND_BEARISH = "weak_trend_bearish"        # Trend faible baissier
    RANGE_BULLISH_BIAS = "range_bullish_bias"        # Range bias haussier
    RANGE_BEARISH_BIAS = "range_bearish_bias"        # Range bias baissier
    RANGE_NEUTRAL = "range_neutral"                  # Range neutre
    TRANSITION = "transition"                        # Changement régime
    UNCLEAR = "unclear"                              # Pas de régime clair

    # ✅ Compat: certains appels traitent MarketRegime comme un dict
    def get(self, key: str, default=None):
        """Compatibilité .get(): retourne value pour 'value' sinon défaut."""
        if key == 'value':
            return self.value
        return default


class TrendStrength(Enum):
    """Force de la tendance"""
    VERY_STRONG = "very_strong"      # >85%
    STRONG = "strong"                # 70-85%
    MODERATE = "moderate"            # 50-70%
    WEAK = "weak"                    # 30-50%
    VERY_WEAK = "very_weak"          # <30%


class RangeType(Enum):
    """Types de range"""
    TIGHT_RANGE = "tight_range"      # 12-20 ticks
    NORMAL_RANGE = "normal_range"    # 20-35 ticks
    WIDE_RANGE = "wide_range"        # 35-50 ticks
    TOO_SMALL = "too_small"          # <12 ticks (éviter)
    TOO_LARGE = "too_large"          # >50 ticks (éviter)

# === DATACLASSES ===


@dataclass
class TrendAnalysis:
    """Analyse tendance complète"""
    timestamp: pd.Timestamp

    # Dow Theory structure
    higher_highs_count: int = 0
    higher_lows_count: int = 0
    lower_highs_count: int = 0
    lower_lows_count: int = 0

    # Trend metrics
    price_slope: float = 0.0
    vwap_slope: float = 0.0
    volume_trend: float = 0.0
    momentum_score: float = 0.0

    # Strength assessment
    trend_strength: TrendStrength = TrendStrength.WEAK
    trend_consistency: float = 0.0
    trend_duration_minutes: int = 0

    # Support/Resistance levels
    key_support: float = 0.0
    key_resistance: float = 0.0
    last_swing_high: float = 0.0
    last_swing_low: float = 0.0

    # Validation
    structure_intact: bool = False
    volume_confirms: bool = False


@dataclass
class RangeAnalysis:
    """Analyse range complète"""
    timestamp: pd.Timestamp

    # Range identification
    range_detected: bool = False
    range_type: RangeType = RangeType.TOO_SMALL

    # Levels
    support_level: float = 0.0
    resistance_level: float = 0.0
    range_midpoint: float = 0.0
    range_size_ticks: float = 0.0

    # Quality metrics
    support_tests: int = 0
    resistance_tests: int = 0
    range_duration_minutes: int = 0
    level_respect_rate: float = 0.0

    # Volume analysis
    range_volume_avg: float = 0.0
    breakout_volume_threshold: float = 0.0
    volume_contraction: bool = False

    # Bias context
    underlying_bias: str = "neutral"  # bullish, bearish, neutral
    bias_strength: float = 0.0


@dataclass
class ESNQCorrelation:
    """Analyse corrélation ES/NQ"""
    timestamp: pd.Timestamp

    # Correlation metrics
    correlation_coefficient: float = 0.0
    correlation_strength: str = "weak"

    # Divergence analysis
    price_divergence: float = 0.0
    momentum_divergence: float = 0.0

    # Leadership
    market_leader: str = "ES"  # ES or NQ
    leadership_strength: float = 0.0

    # Signals
    aligned: bool = False
    divergence_warning: bool = False


@dataclass
class MarketRegimeData:
    """Données complètes régime marché"""
    timestamp: pd.Timestamp

    # Primary regime
    regime: MarketRegime = MarketRegime.UNCLEAR
    regime_confidence: float = 0.0
    regime_duration_minutes: int = 0

    # Component analysis
    trend_analysis: Optional[TrendAnalysis] = None
    range_analysis: Optional[RangeAnalysis] = None
    es_nq_correlation: Optional[ESNQCorrelation] = None

    # Trading implications
    preferred_strategy: str = "None"  # trend, range, wait
    allowed_directions: List[str] = field(default_factory=list)
    bias_strength: float = 0.0

    # Risk management
    expected_volatility: str = "normal"  # low, normal, high
    position_sizing_multiplier: float = 1.0

    # Session context
    session_phase: str = "unknown"
    session_performance_factor: float = 1.0

# === TICK CONVERSION UTILITIES ===

class TickConverter:
    """🎯 Utilitaire de conversion prix ↔ ticks pour différents instruments"""
    
    # Tick sizes par instrument
    TICK_SIZES = {
        'ES': 0.25,    # E-mini S&P 500
        'MES': 0.25,   # Micro E-mini S&P 500
        'NQ': 0.25,    # E-mini NASDAQ-100
        'MNQ': 0.25,   # Micro E-mini NASDAQ-100
        'YM': 1.0,     # E-mini Dow Jones
        'MYM': 1.0,    # Micro E-mini Dow Jones
        'RTY': 0.1,    # E-mini Russell 2000
        'M2K': 0.1,    # Micro E-mini Russell 2000
    }
    
    # Tick values par instrument (pour calcul P&L)
    TICK_VALUES = {
        'ES': 12.50,   # $12.50 par tick
        'MES': 1.25,   # $1.25 par tick
        'NQ': 5.00,    # $5.00 par tick
        'MNQ': 0.50,   # $0.50 par tick
        'YM': 5.00,    # $5.00 par tick
        'MYM': 0.50,   # $0.50 par tick
        'RTY': 5.00,   # $5.00 par tick
        'M2K': 0.50,   # $0.50 par tick
    }
    
    @classmethod
    def price_to_ticks(cls, price: float, instrument: str = 'ES') -> float:
        """🎯 Convertit un prix en nombre de ticks"""
        try:
            tick_size = cls.TICK_SIZES.get(instrument.upper(), 0.25)
            return price / tick_size
        except (TypeError, ValueError, ZeroDivisionError):
            logger.warning(f"⚠️ Erreur conversion prix→ticks: {price} pour {instrument}")
            return 0.0
    
    @classmethod
    def ticks_to_price(cls, ticks: float, instrument: str = 'ES') -> float:
        """🎯 Convertit un nombre de ticks en prix"""
        try:
            tick_size = cls.TICK_SIZES.get(instrument.upper(), 0.25)
            return ticks * tick_size
        except (TypeError, ValueError):
            logger.warning(f"⚠️ Erreur conversion ticks→prix: {ticks} pour {instrument}")
            return 0.0
    
    @classmethod
    def price_range_to_ticks(cls, price1: float, price2: float, instrument: str = 'ES') -> float:
        """🎯 Convertit une plage de prix en ticks"""
        try:
            return abs(cls.price_to_ticks(price1, instrument) - cls.price_to_ticks(price2, instrument))
        except (TypeError, ValueError):
            logger.warning(f"⚠️ Erreur conversion plage→ticks: {price1}-{price2} pour {instrument}")
            return 0.0
    
    @classmethod
    def ticks_to_dollar_value(cls, ticks: float, instrument: str = 'ES') -> float:
        """🎯 Convertit des ticks en valeur dollar"""
        try:
            tick_value = cls.TICK_VALUES.get(instrument.upper(), 12.50)
            return ticks * tick_value
        except (TypeError, ValueError):
            logger.warning(f"⚠️ Erreur conversion ticks→dollars: {ticks} pour {instrument}")
            return 0.0
    
    @classmethod
    def round_to_tick(cls, price: float, instrument: str = 'ES') -> float:
        """🎯 Arrondit un prix au tick le plus proche"""
        try:
            tick_size = cls.TICK_SIZES.get(instrument.upper(), 0.25)
            return round(price / tick_size) * tick_size
        except (TypeError, ValueError):
            logger.warning(f"⚠️ Erreur arrondi tick: {price} pour {instrument}")
            return price
    
    @classmethod
    def get_tick_size(cls, instrument: str = 'ES') -> float:
        """🎯 Retourne la taille de tick pour un instrument"""
        return cls.TICK_SIZES.get(instrument.upper(), 0.25)
    
    @classmethod
    def get_tick_value(cls, instrument: str = 'ES') -> float:
        """🎯 Retourne la valeur de tick pour un instrument"""
        return cls.TICK_VALUES.get(instrument.upper(), 12.50)
    
    @classmethod
    def is_valid_tick_price(cls, price: float, instrument: str = 'ES') -> bool:
        """🎯 Vérifie si un prix est aligné sur les ticks"""
        try:
            tick_size = cls.get_tick_size(instrument)
            return abs(price - cls.round_to_tick(price, instrument)) < 1e-6
        except (TypeError, ValueError):
            return False

# === MAIN MARKET REGIME DETECTOR ===


class MarketRegimeDetector:
    """
    Détecteur régime marché - CERVEAU DU SYSTÈME

    Responsabilités :
    1. Analyse tendance (Dow Theory + VWAP + Volume)
    2. Détection range (taille + qualité + bias)
    3. Corrélation ES/NQ
    4. Classification régime final
    5. Détermination bias trading
    6. Filtrage ranges (minimum 12 ticks)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation détecteur régime"""
        self.config = config or {}

        # Paramètres trend analysis
        self.trend_lookback = self.config.get('trend_lookback', 50)
        self.min_trend_strength = self.config.get('min_trend_strength', 0.6)
        self.dow_structure_periods = self.config.get('dow_structure_periods', 30)

        # Paramètres range detection
        self.min_range_size_ticks = self.config.get('min_range_size_ticks', 12)  # IMPORTANT
        self.max_range_size_ticks = self.config.get('max_range_size_ticks', 50)
        self.min_range_duration = self.config.get('min_range_duration', 20)  # minutes
        self.min_level_tests = self.config.get('min_level_tests', 3)
        self.range_respect_threshold = self.config.get('range_respect_threshold', 0.75)

        # Paramètres corrélation
        self.correlation_lookback = self.config.get('correlation_lookback', 100)
        self.min_correlation_strength = self.config.get('min_correlation_strength', 0.7)

        # Paramètres session
        self.session_volatility_factors = self.config.get('session_volatility_factors', {
            'london_open': 1.3,    # Plus volatil
            'ny_open': 1.5,        # Très volatil
            'lunch': 0.7,          # Moins volatil
            'afternoon': 1.0,      # Normal
            'close': 1.2,          # Modérément volatil
            'after_hours': 0.5     # Faible volatilité
        })
        
        # 🎯 Paramètres de classification des tendances (configurables)
        self.trend_classification_thresholds = self.config.get('trend_classification_thresholds', {
            'very_strong': 0.85,   # >= 0.85
            'strong': 0.70,        # >= 0.70
            'moderate': 0.50,      # >= 0.50
            'weak': 0.30,          # >= 0.30
            'very_weak': 0.0       # < 0.30
        })
        
        # 🎯 Paramètres de validation des volumes
        self.volume_validation_thresholds = self.config.get('volume_validation_thresholds', {
            'min_volume_change': 0.1,  # 10% change minimum
            'volume_confirmation_weight': 0.2  # Poids dans le calcul
        })
        
        # 🎯 Paramètres de corrélation ES/NQ
        self.correlation_classification_thresholds = self.config.get('correlation_classification_thresholds', {
            'very_high': 0.8,      # >= 0.8
            'high': 0.6,           # >= 0.6
            'moderate': 0.4,       # >= 0.4
            'low': 0.0             # < 0.4
        })
        
        # 🎯 Paramètres de divergence
        self.divergence_thresholds = self.config.get('divergence_thresholds', {
            'warning_threshold': 0.02,  # 2% divergence warning
            'critical_threshold': 0.05  # 5% divergence critical
        })
        
        # 🎯 Paramètres de bias
        self.bias_thresholds = self.config.get('bias_thresholds', {
            'min_bias_strength': 0.5,    # Force minimum pour bias
            'vwap_slope_strong': 0.5,    # VWAP slope pour tendance forte
            'vwap_slope_moderate': 0.2   # VWAP slope pour tendance modérée
        })
        
        # 🎯 Paramètres de qualité des ranges
        self.range_quality_thresholds = self.config.get('range_quality_thresholds', {
            'optimal_size_min': 15,      # Taille optimale minimum
            'optimal_size_max': 30,      # Taille optimale maximum
            'acceptable_size_min': 12,   # Taille acceptable minimum
            'acceptable_size_max': 40,   # Taille acceptable maximum
            'duration_weight': 0.2,      # Poids durée dans score
            'size_weight': 0.15,         # Poids taille dans score
            'tests_weight': 0.25,        # Poids tests dans score
            'respect_weight': 0.4        # Poids respect dans score
        })

        # État système
        self.price_history: deque = deque(maxlen=200)
        self.es_nq_history: deque = deque(maxlen=self.correlation_lookback)
        self.regime_history: deque = deque(maxlen=50)
        self.current_regime: Optional[MarketRegimeData] = None

        # Performance tracking
        self.stats = {
            'regimes_detected': 0,
            'trend_periods': 0,
            'range_periods': 0,
            'transition_periods': 0,
            'avg_regime_duration': 0.0,
            'regime_changes': 0,
            'ranges_filtered_small': 0,  # Ranges <12 ticks filtrés
            'ranges_filtered_large': 0   # Ranges >50 ticks filtrés
        }

        logger.info("MarketRegimeDetector initialisé - Cerveau système trading")

    def analyze_market_regime(self,
                              market_data: MarketData,
                              es_nq_data: Optional[Dict[str, float]] = None,
                              structure_data: Optional[Dict[str, Any]] = None,
                              volume_data: Optional[Dict[str, float]] = None) -> MarketRegimeData:
        """
        ANALYSE COMPLÈTE RÉGIME MARCHÉ

        Processus :
        1. Analyse tendance (Dow + VWAP + Volume)
        2. Détection range (avec filtres taille)
        3. Corrélation ES/NQ
        4. Classification régime final
        5. Détermination bias + implications trading

        Args:
            market_data: Données OHLC + volume
            es_nq_data: Données ES/NQ pour corrélation
            structure_data: VWAP + Market Profile levels
            volume_data: Données volume avancées

        Returns:
            MarketRegimeData avec régime + bias + implications
        """
        start_time = time.perf_counter()

        try:
            # --- Normalisation robuste : dict/objet -> MarketData complet (OHLC + timestamp)
            from core.base_types import MarketData as _MD

            def _extract_close_from_dict(d: dict) -> float:
                md = d.get("market_data", d)
                for k in ("close", "c", "price"):
                    v = md.get(k)
                    if v is not None:
                        return v
                q = md.get("quotes") or {}
                mid = q.get("mid")
                if mid is not None:
                    return mid
                bid, ask = q.get("bid"), q.get("ask")
                if bid is not None and ask is not None:
                    return (bid + ask) / 2.0
                trades = md.get("trades") or []
                if trades:
                    return trades[-1].get("price", 0.0)
                return 0.0

            def _extract_volume_from_dict(d: dict) -> float:
                md = d.get("market_data", d)
                v = md.get("volume") or md.get("v")
                if v is not None:
                    return v
                trades = md.get("trades") or []
                if trades:
                    return float(sum(t.get("volume", 0) for t in trades[-50:]))
                return 0.0

            def _extract_timestamp_from_obj(x):
                if isinstance(x, dict):
                    return x.get("timestamp") or x.get("t") or (x.get("market_data", {}).get("timestamp") if "market_data" in x else None)
                return getattr(x, "timestamp", None)

            def _as_market_data(x):
                if isinstance(x, dict):
                    symbol = x.get("symbol") or "ES"
                    close  = _extract_close_from_dict(x)
                    volume = _extract_volume_from_dict(x)
                    ts     = _extract_timestamp_from_obj(x)
                    open_  = x.get("open")  or close
                    high   = x.get("high")  or close
                    low    = x.get("low")   or close
                else:
                    symbol = getattr(x, "symbol", "ES")
                    close  = getattr(x, "close", None) or getattr(x, "price", 0.0)
                    volume = getattr(x, "volume", 0.0)
                    ts     = getattr(x, "timestamp", None)
                    open_  = getattr(x, "open", None) or close
                    high   = getattr(x, "high", None) or close
                    low    = getattr(x, "low", None)  or close
                # Normaliser timestamp Excel → Unix puis fallback
                def _normalize_ts(ts):
                    if ts is None:
                        return None
                    # Gérer les objets Timestamp pandas
                    if hasattr(ts, 'timestamp'):
                        return ts.timestamp()
                    # Gérer les autres types
                    ts = float(ts)
                    if ts > 1e12:      # ms
                        return ts / 1000.0
                    if 40000 < ts < 80000:  # Excel days (Sierra/SC)
                        from datetime import datetime, timezone, timedelta
                        base = datetime(1899, 12, 30, tzinfo=timezone.utc)
                        return (base + timedelta(days=ts)).timestamp()
                    return ts
                
                ts = _normalize_ts(ts)
                if ts is None:
                    from datetime import datetime, timezone
                    ts = datetime.now(timezone.utc).replace(tzinfo=None)
                return _MD(symbol=symbol, open=open_, high=high, low=low, close=close, volume=volume, timestamp=ts)

            # ---- dans analyze(...)
            market_data = _as_market_data(market_data)
            # À partir d'ici, plus d'accès directs au dict : on utilise market_data.open/high/low/close/volume/timestamp

            # Ajout historique
            self.price_history.append(market_data)
            if es_nq_data:
                self.es_nq_history.append(es_nq_data)

            # 1. ANALYSE TENDANCE (DOW THEORY + VWAP)
            trend_analysis = self._analyze_trend_structure(
                market_data, structure_data, volume_data
            )

            # 2. DÉTECTION RANGE (AVEC FILTRES)
            range_analysis = self._analyze_range_structure(
                market_data, structure_data, trend_analysis
            )

            # 3. CORRÉLATION ES/NQ
            es_nq_correlation = self._analyze_es_nq_correlation(es_nq_data)

            # 4. CLASSIFICATION RÉGIME FINAL
            regime, confidence = self._classify_market_regime(
                trend_analysis, range_analysis, es_nq_correlation
            )

            # 5. DÉTERMINATION IMPLICATIONS TRADING
            regime_data = self._generate_regime_implications(
                regime=regime,
                confidence=confidence,
                trend_analysis=trend_analysis,
                range_analysis=range_analysis,
                es_nq_correlation=es_nq_correlation,
                market_data=market_data
            )

            # 6. MISE À JOUR HISTORIQUE
            self._update_regime_history(regime_data)
            self.current_regime = regime_data

            # Performance tracking
            detection_time = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Régime détecté en {detection_time:.2f}ms: {regime.value}")

            return regime_data

        except Exception as e:
            logger.error(f"Erreur analyse régime marché: {e}")
            return MarketRegimeData(
                timestamp=market_data.timestamp,
                regime=MarketRegime.UNCLEAR,
                regime_confidence=0.0
            )

    def _analyze_trend_structure(self,
                                 market_data: MarketData,
                                 structure_data: Optional[Dict[str, Any]],
                                 volume_data: Optional[Dict[str, float]]) -> TrendAnalysis:
        """
        ANALYSE STRUCTURE TENDANCE

        Combine :
        - Dow Theory (HH/HL vs LH/LL)
        - VWAP slope analysis
        - Volume trend confirmation
        - Momentum indicators
        """

        if len(self.price_history) < self.dow_structure_periods:
            return TrendAnalysis(
                timestamp=market_data.timestamp,
                trend_strength=TrendStrength.VERY_WEAK
            )

        recent_bars = list(self.price_history)[-self.dow_structure_periods:]

        # === DOW THEORY STRUCTURE ANALYSIS ===

        # Identification pivots (méthode robuste)
        highs, lows = self._identify_swing_points(recent_bars)

        # Comptage structure Dow
        hh_count, hl_count = self._count_higher_structure(highs, lows)
        lh_count, ll_count = self._count_lower_structure(highs, lows)

        # === VWAP SLOPE ANALYSIS ===

        vwap_slope = 0.0
        if structure_data and 'vwap_slope' in structure_data:
            vwap_slope = structure_data['vwap_slope']
        else:
            # Calcul approximatif si pas fourni
            closes = [bar.close for bar in recent_bars]
            vwap_slope = TickConverter.price_to_ticks(np.polyfit(range(len(closes)), closes, 1)[0], 'ES')

        # === PRICE SLOPE ===

        closes = [bar.close for bar in recent_bars]
        price_slope = TickConverter.price_to_ticks(np.polyfit(range(len(closes)), closes, 1)[0], 'ES')

        # === VOLUME TREND ===

        volumes = [bar.volume for bar in recent_bars]
        if len(volumes) >= 10:
            recent_vol = np.mean(volumes[-5:])
            older_vol = np.mean(volumes[-15:-5])
            volume_trend = (recent_vol - older_vol) / older_vol if older_vol > 0 else 0
        else:
            volume_trend = 0.0

        # === MOMENTUM SCORE ===

        momentum_score = self._calculate_momentum_score(recent_bars)

        # === TREND STRENGTH ASSESSMENT ===

        # Combinaison facteurs pour force tendance
        structure_score = self._calculate_structure_score(hh_count, hl_count, lh_count, ll_count)
        slope_score = min(abs(vwap_slope) / 2.0, 1.0)  # Normalise slope
        momentum_score_norm = min(momentum_score, 1.0)

        trend_strength_value = (
            structure_score *
            0.4 +
            slope_score *
            0.35 +
            momentum_score_norm *
            0.25)

        # Classification force
        # 🎯 Classification basée sur les seuils configurables
        thresholds = self.trend_classification_thresholds
        if trend_strength_value >= thresholds['very_strong']:
            trend_strength = TrendStrength.VERY_STRONG
        elif trend_strength_value >= thresholds['strong']:
            trend_strength = TrendStrength.STRONG
        elif trend_strength_value >= thresholds['moderate']:
            trend_strength = TrendStrength.MODERATE
        elif trend_strength_value >= thresholds['weak']:
            trend_strength = TrendStrength.WEAK
        else:
            trend_strength = TrendStrength.VERY_WEAK

        # === SUPPORT/RESISTANCE LEVELS ===

        if hh_count + hl_count > lh_count + ll_count:  # Bullish structure
            key_support = min([bar.low for bar in recent_bars[-10:]])
            key_resistance = max([bar.high for bar in recent_bars[-5:]])
        else:  # Bearish structure
            key_support = min([bar.low for bar in recent_bars[-5:]])
            key_resistance = max([bar.high for bar in recent_bars[-10:]])

        # === VALIDATION ===

        structure_intact = (hh_count + hl_count >= 3) or (lh_count + ll_count >= 3)
        volume_confirms = abs(volume_trend) > self.volume_validation_thresholds['min_volume_change']

        return TrendAnalysis(
            timestamp=market_data.timestamp,
            higher_highs_count=hh_count,
            higher_lows_count=hl_count,
            lower_highs_count=lh_count,
            lower_lows_count=ll_count,
            price_slope=price_slope,
            vwap_slope=vwap_slope,
            volume_trend=volume_trend,
            momentum_score=momentum_score,
            trend_strength=trend_strength,
            trend_consistency=trend_strength_value,
            trend_duration_minutes=len(recent_bars),
            key_support=key_support,
            key_resistance=key_resistance,
            last_swing_high=max(highs) if highs else 0.0,
            last_swing_low=min(lows) if lows else 0.0,
            structure_intact=structure_intact,
            volume_confirms=volume_confirms
        )

    def _analyze_range_structure(self,
                                 market_data: MarketData,
                                 structure_data: Optional[Dict[str, Any]],
                                 trend_analysis: TrendAnalysis) -> RangeAnalysis:
        """
        ANALYSE STRUCTURE RANGE AVEC FILTRES

        FILTRES CRITIQUES :
        - Range minimum : 12 ticks (éviter micro-ranges)
        - Range maximum : 50 ticks (éviter ranges trop larges)
        - Durée minimum : 20 minutes
        - Tests minimum : 3 par niveau
        """

        if len(self.price_history) < 30:
            return RangeAnalysis(
                timestamp=market_data.timestamp,
                range_detected=False,
                range_type=RangeType.TOO_SMALL
            )

        # Analyse dernière période pour range
        lookback_bars = min(60, len(self.price_history))  # Max 60 barres
        recent_bars = list(self.price_history)[-lookback_bars:]

        # === DÉTECTION NIVEAUX SUPPORT/RÉSISTANCE ===

        highs = [bar.high for bar in recent_bars]
        lows = [bar.low for bar in recent_bars]

        # Méthode percentiles + clustering
        resistance_candidates = np.percentile(highs, [85, 90, 95])
        support_candidates = np.percentile(lows, [5, 10, 15])

        # Sélection niveaux les plus testés
        resistance_level = self._find_most_tested_level(highs, resistance_candidates)
        support_level = self._find_most_tested_level(lows, support_candidates)

        # === VALIDATION TAILLE RANGE ===

        range_size_ticks = TickConverter.price_range_to_ticks(resistance_level, support_level, 'ES')

        # FILTRE PRINCIPAL : Taille range
        if range_size_ticks < self.min_range_size_ticks:
            self.stats['ranges_filtered_small'] += 1
            return RangeAnalysis(
                timestamp=market_data.timestamp,
                range_detected=False,
                range_type=RangeType.TOO_SMALL,
                range_size_ticks=range_size_ticks
            )

        if range_size_ticks > self.max_range_size_ticks:
            self.stats['ranges_filtered_large'] += 1
            return RangeAnalysis(
                timestamp=market_data.timestamp,
                range_detected=False,
                range_type=RangeType.TOO_LARGE,
                range_size_ticks=range_size_ticks
            )

        # === COMPTAGE TESTS NIVEAUX ===

        support_tests = self._count_level_tests(
            lows, support_level, tolerance=TickConverter.ticks_to_price(1.5, 'ES')
        )
        resistance_tests = self._count_level_tests(
            highs, resistance_level, tolerance=TickConverter.ticks_to_price(1.5, 'ES')
        )

        # FILTRE : Tests minimum
        if support_tests < self.min_level_tests or resistance_tests < self.min_level_tests:
            return RangeAnalysis(
                timestamp=market_data.timestamp,
                range_detected=False,
                range_type=RangeType.TOO_SMALL,
                range_size_ticks=range_size_ticks,
                support_tests=support_tests,
                resistance_tests=resistance_tests
            )

        # === DURÉE RANGE ===

        range_duration = len(recent_bars)  # Approximation en barres

        # FILTRE : Durée minimum
        if range_duration < self.min_range_duration:
            return RangeAnalysis(
                timestamp=market_data.timestamp,
                range_detected=False,
                range_type=RangeType.TOO_SMALL,
                range_duration_minutes=range_duration
            )

        # === RESPECT NIVEAUX ===

        level_respect_rate = self._calculate_level_respect_rate(
            recent_bars, support_level, resistance_level
        )

        if level_respect_rate < self.range_respect_threshold:
            return RangeAnalysis(
                timestamp=market_data.timestamp,
                range_detected=False,
                level_respect_rate=level_respect_rate
            )

        # === CLASSIFICATION TYPE RANGE ===

        if 12 <= range_size_ticks <= 20:
            range_type = RangeType.TIGHT_RANGE
        elif 20 <= range_size_ticks <= 35:
            range_type = RangeType.NORMAL_RANGE
        elif 35 <= range_size_ticks <= 50:
            range_type = RangeType.WIDE_RANGE
        else:
            range_type = RangeType.TOO_LARGE  # Shouldn't happen due to filters

        # === BIAS DETERMINATION ===

        # Bias basé sur tendance sous-jacente
        underlying_bias = "neutral"
        bias_strength = 0.0

        if trend_analysis.trend_strength in [TrendStrength.STRONG, TrendStrength.VERY_STRONG]:
            if trend_analysis.higher_highs_count + trend_analysis.higher_lows_count > 4:
                underlying_bias = "bullish"
                bias_strength = trend_analysis.trend_consistency
            elif trend_analysis.lower_highs_count + trend_analysis.lower_lows_count > 4:
                underlying_bias = "bearish"
                bias_strength = trend_analysis.trend_consistency

        # === VOLUME ANALYSIS ===

        volumes = [bar.volume for bar in recent_bars]
        range_volume_avg = np.mean(volumes)

        # Volume contraction dans range
        if len(volumes) >= 10:
            recent_vol = np.mean(volumes[-5:])
            older_vol = np.mean(volumes[:5])
            volume_contraction = recent_vol < older_vol * 0.8
        else:
            volume_contraction = False

        return RangeAnalysis(
            timestamp=market_data.timestamp,
            range_detected=True,
            range_type=range_type,
            support_level=support_level,
            resistance_level=resistance_level,
            range_midpoint=(support_level + resistance_level) / 2,
            range_size_ticks=range_size_ticks,
            support_tests=support_tests,
            resistance_tests=resistance_tests,
            range_duration_minutes=range_duration,
            level_respect_rate=level_respect_rate,
            range_volume_avg=range_volume_avg,
            breakout_volume_threshold=range_volume_avg * 1.5,
            volume_contraction=volume_contraction,
            underlying_bias=underlying_bias,
            bias_strength=bias_strength
        )

    def _analyze_es_nq_correlation(self,
                                   es_nq_data: Optional[Dict[str, float]]) -> ESNQCorrelation:
        """
        ANALYSE CORRÉLATION ES/NQ

        Examine :
        - Corrélation prix
        - Divergences momentum
        - Leadership market
        - Signaux d'alignement
        """

        if not es_nq_data or len(self.es_nq_history) < 20:
            return ESNQCorrelation(
                timestamp=pd.Timestamp.now(),
                correlation_coefficient=0.0,
                correlation_strength="unknown",
                aligned=False
            )

        # Extraction données historiques
        es_prices = [data.get('es_price', 0) for data in self.es_nq_history]
        nq_prices = [data.get('nq_price', 0) for data in self.es_nq_history]

        # Calcul corrélation
        if len(es_prices) >= 20:
            correlation_coef = np.corrcoef(es_prices, nq_prices)[0, 1]
        else:
            correlation_coef = 0.0

        # Classification force corrélation
        # 🎯 Classification basée sur les seuils configurables
        corr_thresholds = self.correlation_classification_thresholds
        if abs(correlation_coef) >= corr_thresholds['very_high']:
            correlation_strength = "very_strong"
        elif abs(correlation_coef) >= corr_thresholds['high']:
            correlation_strength = "strong"
        elif abs(correlation_coef) >= corr_thresholds['moderate']:
            correlation_strength = "moderate"
        else:
            correlation_strength = "weak"

        # Divergence analysis
        if len(es_prices) >= 10:
            es_momentum = (es_prices[-1] - es_prices[-10]) / \
                es_prices[-10] if es_prices[-10] != 0 else 0
            nq_momentum = (nq_prices[-1] - nq_prices[-10]) / \
                nq_prices[-10] if nq_prices[-10] != 0 else 0

            price_divergence = abs(es_momentum - nq_momentum)
            momentum_divergence = price_divergence
        else:
            price_divergence = 0.0
            momentum_divergence = 0.0

        # Leadership analysis
        if len(es_prices) >= 5:
            es_recent_change = (es_prices[-1] - es_prices[-5]) / \
                es_prices[-5] if es_prices[-5] != 0 else 0
            nq_recent_change = (nq_prices[-1] - nq_prices[-5]) / \
                nq_prices[-5] if nq_prices[-5] != 0 else 0

            if abs(es_recent_change) > abs(nq_recent_change):
                market_leader = "ES"
                leadership_strength = abs(es_recent_change) - abs(nq_recent_change)
            else:
                market_leader = "NQ"
                leadership_strength = abs(nq_recent_change) - abs(es_recent_change)
        else:
            market_leader = "ES"
            leadership_strength = 0.0

        # Signaux
        aligned = correlation_coef > self.min_correlation_strength
        divergence_warning = price_divergence > self.divergence_thresholds['warning_threshold']

        return ESNQCorrelation(
            timestamp=pd.Timestamp.now(),
            correlation_coefficient=correlation_coef,
            correlation_strength=correlation_strength,
            price_divergence=price_divergence,
            momentum_divergence=momentum_divergence,
            market_leader=market_leader,
            leadership_strength=leadership_strength,
            aligned=aligned,
            divergence_warning=divergence_warning
        )

    def _classify_market_regime(self,
                                trend_analysis: TrendAnalysis,
                                range_analysis: RangeAnalysis,
                                es_nq_correlation: ESNQCorrelation) -> Tuple[MarketRegime, float]:
        """
        CLASSIFICATION RÉGIME MARCHÉ FINAL

        Hiérarchie décision :
        1. TREND fort → Strong Trend (bullish/bearish)
        2. TREND faible → Weak Trend (bullish/bearish)
        3. RANGE avec bias → Range biased
        4. RANGE sans bias → Range neutral
        5. Sinon → Transition ou Unclear
        """

        confidence = 0.0

        # === ANALYSE TREND PRIORITY ===

        trend_strength = trend_analysis.trend_strength
        hh_hl_score = trend_analysis.higher_highs_count + trend_analysis.higher_lows_count
        lh_ll_score = trend_analysis.lower_highs_count + trend_analysis.lower_lows_count
        vwap_slope = trend_analysis.vwap_slope

        # STRONG TREND BULLISH
        if (trend_strength in [TrendStrength.VERY_STRONG, TrendStrength.STRONG] and
            hh_hl_score >= 4 and hh_hl_score > lh_ll_score and
                vwap_slope > self.bias_thresholds['vwap_slope_strong'] and trend_analysis.structure_intact):

            confidence = 0.85 + min(trend_analysis.trend_consistency * 0.15, 0.15)
            return MarketRegime.STRONG_TREND_BULLISH, confidence

        # STRONG TREND BEARISH
        elif (trend_strength in [TrendStrength.VERY_STRONG, TrendStrength.STRONG] and
              lh_ll_score >= 4 and lh_ll_score > hh_hl_score and
              vwap_slope < -0.5 and trend_analysis.structure_intact):

            confidence = 0.85 + min(trend_analysis.trend_consistency * 0.15, 0.15)
            return MarketRegime.STRONG_TREND_BEARISH, confidence

        # WEAK TREND BULLISH
        elif (trend_strength == TrendStrength.MODERATE and
              hh_hl_score >= 2 and hh_hl_score > lh_ll_score and
              vwap_slope > self.bias_thresholds['vwap_slope_moderate']):

            confidence = 0.65 + min(trend_analysis.trend_consistency * 0.2, 0.2)
            return MarketRegime.WEAK_TREND_BULLISH, confidence

        # WEAK TREND BEARISH
        elif (trend_strength == TrendStrength.MODERATE and
              lh_ll_score >= 2 and lh_ll_score > hh_hl_score and
              vwap_slope < -0.2):

            confidence = 0.65 + min(trend_analysis.trend_consistency * 0.2, 0.2)
            return MarketRegime.WEAK_TREND_BEARISH, confidence

        # === ANALYSE RANGE PRIORITY ===

        elif range_analysis.range_detected:

            bias = range_analysis.underlying_bias
            bias_strength = range_analysis.bias_strength
            range_quality = self._calculate_range_quality_score(range_analysis)

            # RANGE BULLISH BIAS
            if bias == "bullish" and bias_strength > self.bias_thresholds['min_bias_strength']:
                confidence = 0.70 + (range_quality * 0.2)
                return MarketRegime.RANGE_BULLISH_BIAS, confidence

            # RANGE BEARISH BIAS
            elif bias == "bearish" and bias_strength > self.bias_thresholds['min_bias_strength']:
                confidence = 0.70 + (range_quality * 0.2)
                return MarketRegime.RANGE_BEARISH_BIAS, confidence

            # RANGE NEUTRAL
            else:
                confidence = 0.60 + (range_quality * 0.25)
                return MarketRegime.RANGE_NEUTRAL, confidence

        # === TRANSITION OU UNCLEAR ===

        # Transition si changement récent de régime
        elif self._detect_regime_transition():
            confidence = 0.50
            return MarketRegime.TRANSITION, confidence

        # Unclear par défaut
        else:
            confidence = 0.30
            return MarketRegime.UNCLEAR, confidence

    def _generate_regime_implications(self,
                                      regime: MarketRegime,
                                      confidence: float,
                                      trend_analysis: TrendAnalysis,
                                      range_analysis: RangeAnalysis,
                                      es_nq_correlation: ESNQCorrelation,
                                      market_data: MarketData) -> MarketRegimeData:
        """
        GÉNÉRATION IMPLICATIONS TRADING

        Détermine :
        - Stratégie préférée (trend/range/wait)
        - Directions autorisées (long/short/both)
        - Multiplicateur position sizing
        - Volatilité attendue
        """

        # === STRATÉGIE PRÉFÉRÉE ===

        if regime in [MarketRegime.STRONG_TREND_BULLISH, MarketRegime.STRONG_TREND_BEARISH]:
            preferred_strategy = "trend"
            position_multiplier = 1.3  # Boost pour trends forts
            expected_volatility = "high"

        elif regime in [MarketRegime.WEAK_TREND_BULLISH, MarketRegime.WEAK_TREND_BEARISH]:
            preferred_strategy = "trend"
            position_multiplier = 1.0  # Standard
            expected_volatility = "normal"

        elif regime in [MarketRegime.RANGE_BULLISH_BIAS, MarketRegime.RANGE_BEARISH_BIAS, MarketRegime.RANGE_NEUTRAL]:
            preferred_strategy = "range"
            position_multiplier = 0.9  # Légèrement réduit pour range
            expected_volatility = "low"

        else:  # TRANSITION, UNCLEAR
            preferred_strategy = "wait"
            position_multiplier = 0.5  # Très réduit
            expected_volatility = "normal"

        # === DIRECTIONS AUTORISÉES ===

        allowed_directions = []
        bias_strength = 0.0

        if regime == MarketRegime.STRONG_TREND_BULLISH:
            allowed_directions = ["LONG"]
            bias_strength = trend_analysis.trend_consistency

        elif regime == MarketRegime.WEAK_TREND_BULLISH:
            allowed_directions = ["LONG"]  # Mais plus prudent
            bias_strength = trend_analysis.trend_consistency * 0.7

        elif regime == MarketRegime.STRONG_TREND_BEARISH:
            allowed_directions = ["SHORT"]
            bias_strength = trend_analysis.trend_consistency

        elif regime == MarketRegime.WEAK_TREND_BEARISH:
            allowed_directions = ["SHORT"]  # Mais plus prudent
            bias_strength = trend_analysis.trend_consistency * 0.7

        elif regime == MarketRegime.RANGE_BULLISH_BIAS:
            allowed_directions = ["LONG"]  # Seulement longs en bas range
            bias_strength = range_analysis.bias_strength

        elif regime == MarketRegime.RANGE_BEARISH_BIAS:
            allowed_directions = ["SHORT"]  # Seulement shorts en haut range
            bias_strength = range_analysis.bias_strength

        elif regime == MarketRegime.RANGE_NEUTRAL:
            allowed_directions = ["LONG", "SHORT"]  # Both sides
            bias_strength = 0.0

        else:  # TRANSITION, UNCLEAR
            allowed_directions = []  # Pas de trade
            bias_strength = 0.0

        # === SESSION CONTEXT ===

        session_phase = get_session_phase(market_data.timestamp)
        session_factor = self.session_volatility_factors.get(session_phase.value, 1.0)

        # Ajustement multiplicateur selon session
        position_multiplier *= session_factor

        # === DURÉE RÉGIME ===

        regime_duration = 0
        if self.regime_history:
            # Comptage durée régime actuel
            for i, past_regime in enumerate(reversed(self.regime_history)):
                if past_regime.regime == regime:
                    regime_duration += 1
                else:
                    break

        return MarketRegimeData(
            timestamp=market_data.timestamp,
            regime=regime,
            regime_confidence=confidence,
            regime_duration_minutes=regime_duration,
            trend_analysis=trend_analysis,
            range_analysis=range_analysis,
            es_nq_correlation=es_nq_correlation,
            preferred_strategy=preferred_strategy,
            allowed_directions=allowed_directions,
            bias_strength=bias_strength,
            expected_volatility=expected_volatility,
            position_sizing_multiplier=position_multiplier,
            session_phase=session_phase.value,
            session_performance_factor=session_factor
        )

    # === HELPER METHODS ===

    def _identify_swing_points(self, bars: List[MarketData]) -> Tuple[List[float], List[float]]:
        """Identification pivots hauts/bas"""
        highs = []
        lows = []

        for i in range(2, len(bars) - 2):
            # Pivot high : high[i] > high[i-1] and high[i] > high[i+1]
            if (bars[i].high > bars[i-1].high and bars[i].high > bars[i+1].high and
                    bars[i].high > bars[i-2].high and bars[i].high > bars[i+2].high):
                highs.append(bars[i].high)

            # Pivot low : low[i] < low[i-1] and low[i] < low[i+1]
            if (bars[i].low < bars[i-1].low and bars[i].low < bars[i+1].low and
                    bars[i].low < bars[i-2].low and bars[i].low < bars[i+2].low):
                lows.append(bars[i].low)

        return highs, lows

    def _count_higher_structure(self, highs: List[float], lows: List[float]) -> Tuple[int, int]:
        """Comptage Higher Highs / Higher Lows"""
        hh_count = 0
        hl_count = 0

        # Higher Highs
        for i in range(1, len(highs)):
            if highs[i] > highs[i-1]:
                hh_count += 1

        # Higher Lows
        for i in range(1, len(lows)):
            if lows[i] > lows[i-1]:
                hl_count += 1

        return hh_count, hl_count

    def _count_lower_structure(self, highs: List[float], lows: List[float]) -> Tuple[int, int]:
        """Comptage Lower Highs / Lower Lows"""
        lh_count = 0
        ll_count = 0

        # Lower Highs
        for i in range(1, len(highs)):
            if highs[i] < highs[i-1]:
                lh_count += 1

        # Lower Lows
        for i in range(1, len(lows)):
            if lows[i] < lows[i-1]:
                ll_count += 1

        return lh_count, ll_count

    def _calculate_structure_score(self, hh: int, hl: int, lh: int, ll: int) -> float:
        """Score structure Dow Theory"""
        bullish_score = (hh + hl) / max(hh + hl + lh + ll, 1)
        bearish_score = (lh + ll) / max(hh + hl + lh + ll, 1)

        # Retourne force de la structure dominante
        return max(bullish_score, bearish_score)

    def _calculate_momentum_score(self, bars: List[MarketData]) -> float:
        """Calcul score momentum"""
        if len(bars) < 10:
            return 0.0

        # ROC (Rate of Change) sur différentes périodes
        roc_5 = (bars[-1].close - bars[-6].close) / bars[-6].close if bars[-6].close != 0 else 0
        roc_10 = (bars[-1].close - bars[-11].close) / bars[-11].close if bars[-11].close != 0 else 0

        # Momentum composite
        momentum = (roc_5 * 0.6 + roc_10 * 0.4) * 100  # Percentage

        return min(abs(momentum) / 5.0, 1.0)  # Normalise à 1.0

    def _find_most_tested_level(self, prices: List[float], candidates: np.ndarray) -> float:
        """Trouve niveau le plus testé parmi candidats"""
        best_level = candidates[0]
        max_tests = 0

        for candidate in candidates:
            tests = self._count_level_tests(prices, candidate, tolerance=TickConverter.ticks_to_price(2, 'ES'))
            if tests > max_tests:
                max_tests = tests
                best_level = candidate

        return best_level

    def _count_level_tests(self, prices: List[float], level: float, tolerance: float) -> int:
        """Compte tests d'un niveau"""
        return sum(1 for price in prices if abs(price - level) <= tolerance)

    def _calculate_level_respect_rate(self,
                                      bars: List[MarketData],
                                      support: float,
                                      resistance: float) -> float:
        """Calcul taux respect des niveaux"""

        violations = 0
        total_tests = 0

        for bar in bars:
            # Test support
            if abs(bar.low - support) <= TickConverter.ticks_to_price(2, 'ES'):
                total_tests += 1
                if bar.close < support - TickConverter.ticks_to_price(1, 'ES'):  # Violation
                    violations += 1

            # Test résistance
            if abs(bar.high - resistance) <= TickConverter.ticks_to_price(2, 'ES'):
                total_tests += 1
                if bar.close > resistance + TickConverter.ticks_to_price(1, 'ES'):  # Violation
                    violations += 1

        if total_tests == 0:
            return 1.0  # Pas de tests = respect parfait

        return 1.0 - (violations / total_tests)

    def _calculate_range_quality_score(self, range_analysis: RangeAnalysis) -> float:
        """Score qualité range"""
        score = 0.0

        # Tests des niveaux (30%)
        test_score = min((range_analysis.support_tests + range_analysis.resistance_tests) / 8, 1.0)
        score += test_score * 0.3

        # 🎯 Poids configurables pour le calcul de qualité
        quality_weights = self.range_quality_thresholds
        
        # Respect niveaux (configurable)
        score += range_analysis.level_respect_rate * quality_weights['respect_weight']

        # Durée (configurable)
        duration_score = min(range_analysis.range_duration_minutes / 60, 1.0)  # Normalise à 1h
        score += duration_score * quality_weights['duration_weight']

        # 🎯 Taille optimale basée sur les seuils configurables
        size = range_analysis.range_size_ticks
        size_thresholds = self.range_quality_thresholds
        if size_thresholds['optimal_size_min'] <= size <= size_thresholds['optimal_size_max']:
            size_score = 1.0
        elif size_thresholds['acceptable_size_min'] <= size <= size_thresholds['acceptable_size_max']:
            size_score = 0.7
        else:
            size_score = 0.3
        score += size_score * quality_weights['size_weight']

        # Volume contraction (10%)
        if range_analysis.volume_contraction:
            score += 0.1

        return min(score, 1.0)

    def _detect_regime_transition(self) -> bool:
        """Détection transition de régime"""
        if len(self.regime_history) < 3:
            return False

        # Changement récent de régime
        recent_regimes = [r.regime for r in list(self.regime_history)[-3:]]

        # Si les 3 derniers régimes sont différents = transition
        return len(set(recent_regimes)) == 3

    def _update_regime_history(self, regime_data: MarketRegimeData):
        """Mise à jour historique régimes"""
        self.regime_history.append(regime_data)

        # Mise à jour stats
        self.stats['regimes_detected'] += 1

        if "trend" in regime_data.regime.value:
            self.stats['trend_periods'] += 1
        elif "range" in regime_data.regime.value:
            self.stats['range_periods'] += 1
        else:
            self.stats['transition_periods'] += 1

        # Détection changement régime
        if len(self.regime_history) >= 2:
            if self.regime_history[-1].regime != self.regime_history[-2].regime:
                self.stats['regime_changes'] += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques détecteur régime"""
        total_periods = self.stats['regimes_detected']

        return {
            'total_regimes_detected': total_periods,
            'trend_periods': self.stats['trend_periods'],
            'range_periods': self.stats['range_periods'],
            'transition_periods': self.stats['transition_periods'],
            'regime_changes': self.stats['regime_changes'],
            'trend_percentage': (self.stats['trend_periods'] / total_periods * 100) if total_periods > 0 else 0,
            'range_percentage': (self.stats['range_periods'] / total_periods * 100) if total_periods > 0 else 0,
            'ranges_filtered_small': self.stats['ranges_filtered_small'],
            'ranges_filtered_large': self.stats['ranges_filtered_large'],
            'current_regime': self.current_regime.regime.value if self.current_regime else "None",
            'current_confidence': self.current_regime.regime_confidence if self.current_regime else 0.0,
            'current_bias': self.current_regime.allowed_directions if self.current_regime else [],
            'filter_efficiency': f"{self.stats['ranges_filtered_small'] + self.stats['ranges_filtered_large']} ranges filtrés"
        }

# === FACTORY FUNCTIONS ===


def create_market_regime_detector(config: Optional[Dict[str, Any]] = None) -> MarketRegimeDetector:
    """Factory function pour détecteur régime"""
    return MarketRegimeDetector(config)


def analyze_market_regime(market_data: MarketData,
                          es_nq_data: Optional[Dict[str, float]] = None,
                          structure_data: Optional[Dict[str, Any]] = None,
                          volume_data: Optional[Dict[str, float]] = None,
                          detector: Optional[MarketRegimeDetector] = None) -> MarketRegimeData:
    """Helper function pour analyse régime"""

    if detector is None:
        detector = create_market_regime_detector()

    return detector.analyze_market_regime(
        market_data=market_data,
        es_nq_data=es_nq_data,
        structure_data=structure_data,
        volume_data=volume_data
    )

# === TESTING ===


def test_market_regime_detector():
    """Test complet détecteur régime"""
    logger.debug("TEST MARKET REGIME DETECTOR")
    print("=" * 45)

    # Création détecteur
    detector = create_market_regime_detector()

    # Simulation trend haussier puis range
    regimes_detected = []

    logger.info("[UP] SIMULATION TREND HAUSSIER:")
    base_price = 4500.0

    # Phase 1: Trend haussier (HH/HL)
    for i in range(40):
        trend_price = base_price + (i * 0.5) + np.random.normal(0, 1)

        market_data = MarketData(
            timestamp=pd.Timestamp.now() + pd.Timedelta(minutes=i),
            symbol="ES",
            open=trend_price - 0.5,
            high=trend_price + 1.5,
            low=trend_price - 1.0,
            close=trend_price,
            volume=1500 + int(np.random.normal(0, 200))
        )

        # Structure data avec VWAP slope positif
        structure_data = {
            'vwap_slope': 0.6,  # Slope haussier
            'vwap_price': trend_price - 1,
            'poc_price': trend_price - 0.5
        }

        # ES/NQ data aligné
        es_nq_data = {
            'es_price': trend_price,
            'nq_price': trend_price * 4.5,  # Ratio ES/NQ approximatif
        }

        regime_data = detector.analyze_market_regime(
            market_data=market_data,
            structure_data=structure_data,
            es_nq_data=es_nq_data
        )

        regimes_detected.append(regime_data)

        if i % 10 == 0:
            print(f"[{i:2d}] Régime: {regime_data.regime.value} "
                  f"(conf: {regime_data.regime_confidence:.2f})")

    logger.info("\n[STATS] SIMULATION RANGE (minimum 12 ticks):")

    # Phase 2: Range 4520-4535 (15 ticks - acceptable)
    range_support = 4520.0
    range_resistance = 4535.0
    range_mid = (range_support + range_resistance) / 2

    for i in range(30):
        # Prix oscille dans range
        if i % 6 == 0:  # Test support
            range_price = range_support + np.random.normal(0, 0.5)
        elif i % 6 == 3:  # Test résistance
            range_price = range_resistance + np.random.normal(0, 0.5)
        else:  # Dans range
            range_price = range_mid + np.random.normal(0, 3)

        # Clamp dans range
        range_price = max(range_support - 1, min(range_resistance + 1, range_price))

        market_data = MarketData(
            timestamp=pd.Timestamp.now() + pd.Timedelta(minutes=40+i),
            symbol="ES",
            open=range_price - 0.3,
            high=range_price + 0.8,
            low=range_price - 0.8,
            close=range_price,
            volume=1200 + int(np.random.normal(0, 150))  # Volume plus faible
        )

        # VWAP slope neutre pour range
        structure_data = {
            'vwap_slope': 0.1,  # Quasi flat
            'vwap_price': range_mid,
            'poc_price': range_mid + 1
        }

        regime_data = detector.analyze_market_regime(
            market_data=market_data,
            structure_data=structure_data,
            es_nq_data={'es_price': range_price, 'nq_price': range_price * 4.5}
        )

        regimes_detected.append(regime_data)

        if i % 8 == 0:
            print(f"[{i:2d}] Régime: {regime_data.regime.value} "
                  f"(conf: {regime_data.regime_confidence:.2f})")

            if regime_data.range_analysis and regime_data.range_analysis.range_detected:
                range_info = regime_data.range_analysis
                print(f"     Range: {range_info.support_level:.1f}-{range_info.resistance_level:.1f} "
                      f"({range_info.range_size_ticks:.1f} ticks)")

    # Test range trop petit (filtré)
    logger.info("\n[ERROR] TEST RANGE TROP PETIT (filtre <12 ticks):")

    # Micro-range 4530-4536 (6 ticks - filtré)
    micro_support = 4530.0
    micro_resistance = 4536.0  # Seulement 6 ticks

    for i in range(15):
        micro_price = micro_support + (i % 2) * (micro_resistance -
                                                 micro_support) + np.random.normal(0, 0.3)

        market_data = MarketData(
            timestamp=pd.Timestamp.now() + pd.Timedelta(minutes=70+i),
            symbol="ES",
            open=micro_price,
            high=micro_price + 0.5,
            low=micro_price - 0.5,
            close=micro_price,
            volume=1000
        )

        regime_data = detector.analyze_market_regime(market_data=market_data)

        if i == 10:  # Check après stabilisation
            if regime_data.range_analysis:
                print(f"Range {regime_data.range_analysis.range_size_ticks:.1f} ticks: "
                      f"Détecté = {regime_data.range_analysis.range_detected}")

    # Analyse finale
    final_regime = regimes_detected[-1]

    logger.info("\n[STATS] RÉGIME FINAL:")
    logger.info("   • Régime: {final_regime.regime.value}")
    logger.info("   • Confidence: {final_regime.regime_confidence:.2f}")
    logger.info("   • Stratégie: {final_regime.preferred_strategy}")
    logger.info("   • Directions: {final_regime.allowed_directions}")
    logger.info("   • Bias strength: {final_regime.bias_strength:.2f}")
    logger.info("   • Position multiplier: {final_regime.position_sizing_multiplier:.2f}")

    if final_regime.range_analysis and final_regime.range_analysis.range_detected:
        range_data = final_regime.range_analysis
        logger.info("   • Range: {range_data.support_level:.1f}-{range_data.resistance_level:.1f}")
        logger.info("   • Range size: {range_data.range_size_ticks:.1f} ticks")
        logger.info("   • Range type: {range_data.range_type.value}")
        logger.info("   • Tests: S={range_data.support_tests}, R={range_data.resistance_tests}")

    # Statistiques
    stats = detector.get_statistics()
    logger.info("\n[UP] STATISTICS:")
    for key, value in stats.items():
        logger.info("   • {key}: {value}")

    logger.info("\n[TARGET] MARKET REGIME DETECTOR TEST COMPLETED")
    return True


if __name__ == "__main__":
    test_market_regime_detector()
