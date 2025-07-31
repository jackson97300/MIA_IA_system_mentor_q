"""
MIA_IA_SYSTEM - Range Strategy Complete
Stratégie range avec direction bias + standards universels
Version: Production Ready
Performance: Hiérarchie signaux + gestion complète

HIÉRARCHIE SIGNAUX RANGE :
1. PREMIUM_BOUNCE (85-100%)  - Bounce + confluence max + bias direction
2. STRONG_BOUNCE (70-84%)    - Bounce + confluence forte
3. WEAK_BOUNCE (60-69%)      - Bounce faible (size réduite)
4. FADE_SIGNAL (75-90%)      - Fade range en transition
5. NO_TRADE (0-59%)         - Attendre meilleur setup

RÈGLE SUPRÊME : JAMAIS CONTRE TENDANCE PRIMAIRE
- Trend haussier + Range → ACHATS SEULEMENT en bas
- Trend baissier + Range → VENTES SEULEMENT en haut
- Pas de trend clair → Range trading classique (both sides)

GESTION SPÉCIALE :
- Stops ÉLARGIS si base ≥4 ticks (VOTRE RÈGLE)
- Exit spécial : 2 boules vertes après base rouge
- Patience obligatoire : pas d'entrée FOMO
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from core.logger import get_logger
from collections import deque
from features.market_regime import MarketRegimeDetector

# Local imports
from core.base_types import (
    MarketData, OrderFlowData, TradingSignal, SignalType,
    MarketRegime, SignalStrength, ES_TICK_SIZE, ES_TICK_VALUE
)
from features.feature_calculator import (
    FeatureCalculationResult, SignalQuality, TRADING_THRESHOLDS
)

logger = get_logger(__name__)

# === RANGE SIGNAL HIERARCHY ===


class RangeSignalType(Enum):
    """Types de signaux range avec hiérarchie"""
    PREMIUM_BOUNCE = "premium_bounce"        # 85-100% - Bounce + confluence max
    STRONG_BOUNCE = "strong_bounce"          # 70-84%  - Bounce + confluence forte
    WEAK_BOUNCE = "weak_bounce"              # 60-69%  - Bounce faible
    FADE_SIGNAL = "fade_signal"              # 75-90%  - Fade range breakout
    EXIT_SPECIAL = "exit_special"            # 80%+    - Exit spécial (2 vertes)
    NO_TRADE = "no_trade"                    # 0-59%   - Wait


class RangeBias(Enum):
    """Bias directionnel range"""
    BULLISH_BIAS = "bullish_bias"    # Trend haussier → longs seulement
    BEARISH_BIAS = "bearish_bias"    # Trend baissier → shorts seulement
    NEUTRAL = "neutral"              # Pas de trend → both sides
    FORBIDDEN = "forbidden"          # Signal interdit


class RangeQuality(Enum):
    """Qualité du range"""
    EXCELLENT = "excellent"    # 80-100% - Range parfait
    GOOD = "good"             # 60-79%  - Range acceptable
    POOR = "poor"             # 40-59%  - Range faible
    INVALID = "invalid"       # 0-39%   - Pas un range

# === DATACLASSES ===


@dataclass
class RangeStructure:
    """Structure range complète"""
    timestamp: pd.Timestamp

    # Range identification
    range_detected: bool = False
    range_quality: RangeQuality = RangeQuality.INVALID

    # Levels
    support_level: float = 0.0
    resistance_level: float = 0.0
    range_midpoint: float = 0.0
    range_size_ticks: float = 0.0

    # Tests and validation
    support_tests: int = 0
    resistance_tests: int = 0
    range_duration_minutes: int = 0

    # Volume analysis
    support_volume_avg: float = 0.0
    resistance_volume_avg: float = 0.0
    range_volume_profile: Dict[str, float] = field(default_factory=dict)

    # Quality metrics
    range_respect_rate: float = 0.0  # % of times levels held
    volatility_contraction: float = 0.0

    # Bias and trend context
    primary_trend_bias: RangeBias = RangeBias.NEUTRAL
    allowed_directions: List[str] = field(default_factory=list)


@dataclass
class BounceSetup:
    """Setup bounce sur niveau"""
    timestamp: pd.Timestamp

    # Setup identification
    bounce_type: str = "support"  # support or resistance
    target_level: float = 0.0
    current_distance: float = 0.0

    # Entry criteria
    pattern_confirmation: bool = False
    volume_confirmation: bool = False
    confluence_score: float = 0.0

    # Sierra patterns context
    sierra_pattern_detected: str = "None"
    pattern_strength: float = 0.0

    # Quality assessment
    setup_quality: float = 0.0
    risk_reward_ratio: float = 0.0

    # Special conditions
    base_size_ticks: float = 0.0
    requires_wide_stop: bool = False


@dataclass
class RangeSignalData:
    """Signal range complet"""
    timestamp: pd.Timestamp
    signal_type: RangeSignalType
    direction: str  # LONG or SHORT
    bias: RangeBias

    # Entry data
    entry_price: float
    entry_reason: str
    confluence_score: float

    # Risk management
    stop_loss: float
    take_profit: float
    position_size: float
    stop_type: str  # normal, wide, adaptive

    # Context
    range_structure: RangeStructure
    bounce_setup: Optional[BounceSetup] = None

    # Special rules
    special_exit_rule: Optional[str] = None
    bias_compliance: bool = True

    # Metadata
    sierra_patterns: Dict[str, float] = field(default_factory=dict)

    def risk_reward_ratio(self) -> float:
        """Calcul R:R"""
        risk = abs(self.entry_price - self.stop_loss)
        reward = abs(self.take_profit - self.entry_price)
        return reward / risk if risk > 0 else 0.0

# === MAIN RANGE STRATEGY CLASS ===


class RangeStrategy:
    """
    Stratégie range avec bias directionnel

    Implémente :
    - Standards range trading universels
    - Bias selon tendance primaire (JAMAIS contre-tendance)
    - Stops adaptatifs selon taille base (VOTRE RÈGLE)
    - Exit spécial : 2 boules vertes après base rouge
    - Hiérarchie signaux avec confluence
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation stratégie range"""
        self.config = config or {}

        # Paramètres range detection
        self.min_range_size_ticks = self.config.get('min_range_size_ticks', 8)
        self.max_range_size_ticks = self.config.get('max_range_size_ticks', 40)
        self.min_test_count = self.config.get('min_test_count', 2)
        self.min_range_duration = self.config.get('min_range_duration', 15)  # minutes

        # Paramètres risk management
        self.base_position_size = self.config.get('base_position_size', 1.0)
        self.normal_stop_buffer = self.config.get('normal_stop_buffer', 3)  # ticks
        self.wide_stop_threshold = self.config.get('wide_stop_threshold', 4)  # ticks (VOTRE RÈGLE)
        self.wide_stop_minimum = self.config.get('wide_stop_minimum', 6)    # ticks minimum

        # Paramètres confluence
        self.proximity_tolerance = self.config.get('proximity_tolerance', 2)  # ticks
        self.min_confluence_for_trade = self.config.get('min_confluence', 0.6)

        # État
        self.current_range: Optional[RangeStructure] = None
        self.price_history: deque = deque(maxlen=100)
        self.sierra_pattern_history: deque = deque(maxlen=20)

        # Performance tracking
        self.stats = {
            'ranges_detected': 0,
            'bounce_signals': 0,
            'fade_signals': 0,
            'bias_compliant_trades': 0,
            'wide_stops_used': 0,
            'special_exits_triggered': 0
        }

        logger.info("RangeStrategy initialisée avec bias directionnel + stops adaptatifs")

    def analyze_range_signal(self,
                             features: FeatureCalculationResult,
                             market_data: MarketData,
                             trend_context: Optional[Dict[str, Any]] = None,
                             structure_data: Optional[Dict[str, Any]] = None,
                             sierra_patterns: Optional[Dict[str, float]] = None) -> Optional[RangeSignalData]:
        """
        ANALYSE SIGNAL RANGE PRINCIPAL

        Processus :
        1. Détection range structure
        2. Détermination bias selon tendance primaire
        3. Identification bounce opportunities
        4. Validation bias compliance
        5. Classification signal selon hiérarchie
        6. Calcul risk/reward avec stops adaptatifs

        Args:
            features: Features avec confluence score
            market_data: Données marché actuelles
            trend_context: Contexte tendance primaire (bias)
            structure_data: Niveaux techniques
            sierra_patterns: Patterns depuis battle_navale

        Returns:
            RangeSignalData avec hiérarchie ou None
        """

        try:
            # Ajout à l'historique
            self.price_history.append(market_data)
            if sierra_patterns:
                self.sierra_pattern_history.append(sierra_patterns)

            # 1. DÉTECTION RANGE STRUCTURE
            range_structure = self._detect_range_structure(market_data, structure_data)
            self.current_range = range_structure

            if not range_structure.range_detected:
                return None  # Pas de range valide

            # 2. DÉTERMINATION BIAS DIRECTIONNEL
            bias = self._determine_range_bias(trend_context, range_structure)

            # 3. DÉTECTION BOUNCE OPPORTUNITY
            bounce_setup = self._analyze_bounce_opportunity(
                market_data, range_structure, structure_data, sierra_patterns
            )

            if not bounce_setup:
                return None  # Pas d'opportunity bounce

            # 4. VALIDATION BIAS COMPLIANCE
            if not self._validate_bias_compliance(bounce_setup, bias):
                logger.info(f"Signal rejeté - contre bias {bias.value}")
                return None

            # 5. CLASSIFICATION SIGNAL
            signal_type = self._classify_range_signal(
                features.confluence_score, bounce_setup, range_structure
            )

            if signal_type == RangeSignalType.NO_TRADE:
                return None

            # 6. VÉRIFICATION EXIT SPÉCIAL
            special_exit = self._check_special_exit_conditions(sierra_patterns)
            if special_exit:
                return self._generate_special_exit_signal(
                    market_data, special_exit, sierra_patterns
                )

            # 7. GÉNÉRATION SIGNAL COMPLET
            signal = self._generate_range_signal(
                signal_type=signal_type,
                bias=bias,
                range_structure=range_structure,
                bounce_setup=bounce_setup,
                market_data=market_data,
                confluence_score=features.confluence_score,
                sierra_patterns=sierra_patterns or {}
            )

            # 8. VALIDATION FINALE
            if self._validate_signal(signal):
                self._update_stats(signal)
                logger.info(f"Signal range généré: {signal.signal_type.value} "
                            f"{signal.direction} @ {signal.entry_price:.2f}")
                return signal

            return None

        except Exception as e:
            logger.error(f"Erreur analyse signal range: {e}")
            return None

    def _detect_range_structure(self,
                                market_data: MarketData,
                                structure_data: Optional[Dict[str, Any]]) -> RangeStructure:
        """
        DÉTECTION STRUCTURE RANGE

        Critères standards :
        - Support/résistance testés 2+ fois
        - Range size entre min/max ticks
        - Durée minimum
        - Respect des niveaux
        """

        if len(self.price_history) < 20:
            return RangeStructure(
                timestamp=market_data.timestamp,
                range_detected=False
            )

        recent_bars = list(self.price_history)[-30:]  # 30 dernières barres

        # Calcul support/résistance
        highs = [bar.high for bar in recent_bars]
        lows = [bar.low for bar in recent_bars]

        # Support = zone basse fréquente
        support_zone = np.percentile(lows, 10)  # 10% plus bas
        resistance_zone = np.percentile(highs, 90)  # 10% plus hauts

        # Affinage avec clustering
        support_level = self._find_clustered_level(lows, support_zone, tolerance=2*ES_TICK_SIZE)
        resistance_level = self._find_clustered_level(
            highs, resistance_zone, tolerance=2*ES_TICK_SIZE)

        # Validation range
        range_size_ticks = (resistance_level - support_level) / ES_TICK_SIZE

        if not (self.min_range_size_ticks <= range_size_ticks <= self.max_range_size_ticks):
            return RangeStructure(
                timestamp=market_data.timestamp,
                range_detected=False
            )

        # Comptage tests des niveaux
        support_tests = self._count_level_tests(lows, support_level, tolerance=1.5*ES_TICK_SIZE)
        resistance_tests = self._count_level_tests(
            highs, resistance_level, tolerance=1.5*ES_TICK_SIZE)

        if support_tests < self.min_test_count or resistance_tests < self.min_test_count:
            return RangeStructure(
                timestamp=market_data.timestamp,
                range_detected=False
            )

        # Calcul qualité range
        range_quality = self._evaluate_range_quality(
            range_size_ticks, support_tests, resistance_tests, recent_bars
        )

        # Détermination bias selon contexte
        primary_bias = self._analyze_primary_trend_bias(recent_bars)

        return RangeStructure(
            timestamp=market_data.timestamp,
            range_detected=True,
            range_quality=range_quality,
            support_level=support_level,
            resistance_level=resistance_level,
            range_midpoint=(support_level + resistance_level) / 2,
            range_size_ticks=range_size_ticks,
            support_tests=support_tests,
            resistance_tests=resistance_tests,
            range_duration_minutes=len(recent_bars),  # Approximation
            primary_trend_bias=primary_bias
        )

    def _determine_range_bias(self,
                              trend_context: Optional[Dict[str, Any]],
                              range_structure: RangeStructure) -> RangeBias:
        """
        DÉTERMINATION BIAS DIRECTIONNEL

        RÈGLE SUPRÊME : JAMAIS CONTRE TENDANCE PRIMAIRE
        - Trend haussier → LONGS SEULEMENT en bas range
        - Trend baissier → SHORTS SEULEMENT en haut range
        - Pas de trend → Both sides autorisés
        """

        if not trend_context:
            return RangeBias.NEUTRAL

        # Analyse tendance primaire (VWAP slope + Dow structure)
        vwap_slope = trend_context.get('vwap_slope', 0.0)
        dow_trend = trend_context.get('dow_trend_direction', 'sideways')
        trend_strength = trend_context.get('trend_strength', 0.0)

        # Seuils pour bias determination
        strong_trend_threshold = 0.7
        moderate_trend_threshold = 0.4

        # BIAS BULLISH (longs seulement)
        if ((vwap_slope > 0.3 and trend_strength > moderate_trend_threshold) or
                (dow_trend == 'bullish' and trend_strength > strong_trend_threshold)):
            return RangeBias.BULLISH_BIAS

        # BIAS BEARISH (shorts seulement)
        elif ((vwap_slope < -0.3 and trend_strength > moderate_trend_threshold) or
              (dow_trend == 'bearish' and trend_strength > strong_trend_threshold)):
            return RangeBias.BEARISH_BIAS

        # NEUTRAL (both sides)
        else:
            return RangeBias.NEUTRAL

    def _analyze_bounce_opportunity(self,
                                    market_data: MarketData,
                                    range_structure: RangeStructure,
                                    structure_data: Optional[Dict[str, Any]],
                                    sierra_patterns: Optional[Dict[str, float]]) -> Optional[BounceSetup]:
        """
        ANALYSE OPPORTUNITÉ BOUNCE

        Détecte :
        - Proximité support/résistance
        - Patterns Sierra Chart confirmation
        - Confluence avec niveaux techniques
        - Qualité du setup
        """

        current_price = market_data.close
        support = range_structure.support_level
        resistance = range_structure.resistance_level

        # Distance aux niveaux
        distance_to_support = abs(current_price - support)
        distance_to_resistance = abs(current_price - resistance)

        bounce_setup = None

        # BOUNCE SUPPORT (LONG)
        if distance_to_support <= self.proximity_tolerance * ES_TICK_SIZE:

            # Pattern confirmation (Sierra Chart)
            pattern_confirmed, pattern_name, pattern_strength = self._check_bullish_patterns(
                sierra_patterns)

            # Volume confirmation
            volume_confirmed = self._check_volume_confirmation(market_data, "support")

            # Confluence score
            confluence = self._calculate_bounce_confluence(current_price, structure_data, "support")

            bounce_setup = BounceSetup(
                timestamp=market_data.timestamp,
                bounce_type="support",
                target_level=support,
                current_distance=distance_to_support / ES_TICK_SIZE,
                pattern_confirmation=pattern_confirmed,
                volume_confirmation=volume_confirmed,
                confluence_score=confluence,
                sierra_pattern_detected=pattern_name,
                pattern_strength=pattern_strength
            )

        # BOUNCE RÉSISTANCE (SHORT)
        elif distance_to_resistance <= self.proximity_tolerance * ES_TICK_SIZE:

            pattern_confirmed, pattern_name, pattern_strength = self._check_bearish_patterns(
                sierra_patterns)
            volume_confirmed = self._check_volume_confirmation(market_data, "resistance")
            confluence = self._calculate_bounce_confluence(
                current_price, structure_data, "resistance")

            bounce_setup = BounceSetup(
                timestamp=market_data.timestamp,
                bounce_type="resistance",
                target_level=resistance,
                current_distance=distance_to_resistance / ES_TICK_SIZE,
                pattern_confirmation=pattern_confirmed,
                volume_confirmation=volume_confirmed,
                confluence_score=confluence,
                sierra_pattern_detected=pattern_name,
                pattern_strength=pattern_strength
            )

        if bounce_setup:
            # Évaluation qualité setup
            bounce_setup.setup_quality = self._evaluate_bounce_quality(bounce_setup)

            # Détection base size pour stops adaptatifs
            base_size = self._detect_base_size_from_sierra(sierra_patterns)
            bounce_setup.base_size_ticks = base_size
            bounce_setup.requires_wide_stop = base_size >= self.wide_stop_threshold

        return bounce_setup

    def _validate_bias_compliance(self,
                                  bounce_setup: BounceSetup,
                                  bias: RangeBias) -> bool:
        """
        VALIDATION COMPLIANCE BIAS

        Vérifie que le signal respecte le bias directionnel
        """

        bounce_type = bounce_setup.bounce_type

        # BIAS BULLISH : seulement longs (bounce support)
        if bias == RangeBias.BULLISH_BIAS:
            return bounce_type == "support"

        # BIAS BEARISH : seulement shorts (bounce résistance)
        elif bias == RangeBias.BEARISH_BIAS:
            return bounce_type == "resistance"

        # NEUTRAL : both sides autorisés
        elif bias == RangeBias.NEUTRAL:
            return True

        return False

    def _classify_range_signal(self,
                               confluence_score: float,
                               bounce_setup: BounceSetup,
                               range_structure: RangeStructure) -> RangeSignalType:
        """
        CLASSIFICATION HIÉRARCHIQUE SIGNAUX RANGE

        1. PREMIUM_BOUNCE (85-100%) - Confluence max + pattern fort
        2. STRONG_BOUNCE (70-84%)   - Confluence forte + pattern
        3. WEAK_BOUNCE (60-69%)     - Confluence faible
        4. NO_TRADE (0-59%)        - Pas de trade
        """

        # Base confluence threshold
        if confluence_score < TRADING_THRESHOLDS['WEAK_SIGNAL']:
            return RangeSignalType.NO_TRADE

        setup_quality = bounce_setup.setup_quality
        pattern_strength = bounce_setup.pattern_strength
        range_quality_score = self._get_range_quality_score(range_structure.range_quality)

        # PREMIUM BOUNCE (85-100%)
        if (confluence_score >= 0.85 and
            setup_quality >= 0.8 and
            pattern_strength >= 0.7 and
                range_quality_score >= 0.8):
            return RangeSignalType.PREMIUM_BOUNCE

        # STRONG BOUNCE (70-84%)
        elif (confluence_score >= 0.70 and
              setup_quality >= 0.6 and
              pattern_strength >= 0.5):
            return RangeSignalType.STRONG_BOUNCE

        # WEAK BOUNCE (60-69%)
        elif confluence_score >= 0.60:
            return RangeSignalType.WEAK_BOUNCE

        return RangeSignalType.NO_TRADE

    def _check_special_exit_conditions(self,
                                       sierra_patterns: Optional[Dict[str, float]]) -> Optional[str]:
        """
        VÉRIFICATION CONDITIONS EXIT SPÉCIALES

        VOTRE RÈGLE : "2 boules vertes consécutives après base rouge en tendance baissière = EXIT"
        """

        if not sierra_patterns or len(self.sierra_pattern_history) < 5:
            return None

        recent_patterns = list(self.sierra_pattern_history)[-5:]

        # Recherche pattern : base rouge suivie de 2 boules vertes
        for i in range(len(recent_patterns) - 2):
            pattern_1 = recent_patterns[i]
            pattern_2 = recent_patterns[i + 1]
            pattern_3 = recent_patterns[i + 2]

            # Base rouge détectée
            if (pattern_1.get('color_down_setting', 0) > 0.7 and
                    pattern_1.get('battle_navale_signal', 0.5) < 0.4):  # Signal baissier

                # 2 boules vertes consécutives après
                if (pattern_2.get('battle_navale_signal', 0.5) > 0.6 and
                        pattern_3.get('battle_navale_signal', 0.5) > 0.6):

                    return "two_green_after_red_base"

        return None

    def _generate_special_exit_signal(self,
                                      market_data: MarketData,
                                      exit_reason: str,
                                      sierra_patterns: Dict[str, float]) -> RangeSignalData:
        """Génération signal exit spécial"""

        return RangeSignalData(
            timestamp=market_data.timestamp,
            signal_type=RangeSignalType.EXIT_SPECIAL,
            direction="EXIT",
            bias=RangeBias.NEUTRAL,
            entry_price=market_data.close,
            entry_reason=f"Exit spécial: {exit_reason}",
            confluence_score=0.8,  # Exit signals ont confluence élevée
            stop_loss=0.0,
            take_profit=0.0,
            position_size=0.0,
            stop_type="exit",
            range_structure=self.current_range or RangeStructure(timestamp=market_data.timestamp),
            special_exit_rule=exit_reason,
            sierra_patterns=sierra_patterns
        )

    def _generate_range_signal(self,
                               signal_type: RangeSignalType,
                               bias: RangeBias,
                               range_structure: RangeStructure,
                               bounce_setup: BounceSetup,
                               market_data: MarketData,
                               confluence_score: float,
                               sierra_patterns: Dict[str, float]) -> RangeSignalData:
        """
        GÉNÉRATION SIGNAL RANGE COMPLET

        Calcule :
        - Prix d'entrée optimal
        - Stop loss adaptatif selon base size (VOTRE RÈGLE)
        - Take profit vers borne opposée
        - Position size selon hiérarchie
        """

        current_price = market_data.close
        bounce_type = bounce_setup.bounce_type

        # DIRECTION ET PRIX D'ENTRÉE
        if bounce_type == "support":
            direction = "LONG"
            entry_price = bounce_setup.target_level + \
                (0.5 * ES_TICK_SIZE)  # Légèrement au-dessus support
            target_level = range_structure.resistance_level
        else:  # resistance
            direction = "SHORT"
            entry_price = bounce_setup.target_level - \
                (0.5 * ES_TICK_SIZE)  # Légèrement sous résistance
            target_level = range_structure.support_level

        # CALCUL STOP LOSS ADAPTATIF (VOTRE RÈGLE)
        stop_loss = self._calculate_adaptive_stop(
            bounce_setup, range_structure, direction
        )

        # CALCUL TAKE PROFIT
        if direction == "LONG":
            take_profit = target_level - (1 * ES_TICK_SIZE)  # 1 tick avant résistance
        else:
            take_profit = target_level + (1 * ES_TICK_SIZE)  # 1 tick au-dessus support

        # CALCUL POSITION SIZE
        position_multiplier = self._get_range_position_multiplier(signal_type)
        position_size = self.base_position_size * position_multiplier

        # VALIDATION R:R
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)

        if risk > 0:
            rr_ratio = reward / risk
            # Réduire size si R:R faible
            if rr_ratio < 1.5:
                position_size *= 0.7

        return RangeSignalData(
            timestamp=market_data.timestamp,
            signal_type=signal_type,
            direction=direction,
            bias=bias,
            entry_price=entry_price,
            entry_reason=f"Bounce {bounce_type} + confluence {confluence_score:.2f}",
            confluence_score=confluence_score,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size,
            stop_type="wide" if bounce_setup.requires_wide_stop else "normal",
            range_structure=range_structure,
            bounce_setup=bounce_setup,
            bias_compliance=True,
            sierra_patterns=sierra_patterns
        )

    def _calculate_adaptive_stop(self,
                                 bounce_setup: BounceSetup,
                                 range_structure: RangeStructure,
                                 direction: str) -> float:
        """
        CALCUL STOP ADAPTATIF SELON VOTRE RÈGLE

        RÈGLE : Si base ≥4 ticks → stop élargi
        Sinon → stop normal
        """

        base_size = bounce_setup.base_size_ticks
        target_level = bounce_setup.target_level

        # VOTRE RÈGLE : Base ≥4 ticks = stop élargi
        if base_size >= self.wide_stop_threshold:
            # Stop élargi : max(6 ticks, base_size + 2)
            stop_distance_ticks = max(self.wide_stop_minimum, base_size + 2)
            logger.info(
                f"Stop élargi appliqué: base {
                    base_size:.1f} ticks → stop {
                    stop_distance_ticks:.1f} ticks")
        else:
            # Stop normal
            stop_distance_ticks = self.normal_stop_buffer

        stop_distance = stop_distance_ticks * ES_TICK_SIZE

        if direction == "LONG":
            stop_loss = target_level - stop_distance
        else:  # SHORT
            stop_loss = target_level + stop_distance

        return stop_loss

    def _get_range_position_multiplier(self, signal_type: RangeSignalType) -> float:
        """Multiplicateur position selon hiérarchie range"""
        multipliers = {
            RangeSignalType.PREMIUM_BOUNCE: 1.5,   # Size max pour premium
            RangeSignalType.STRONG_BOUNCE: 1.0,    # Size standard
            RangeSignalType.WEAK_BOUNCE: 0.5,      # Size réduite
            RangeSignalType.FADE_SIGNAL: 0.8,      # Size modérée pour fade
            RangeSignalType.EXIT_SPECIAL: 0.0,     # Exit signal
            RangeSignalType.NO_TRADE: 0.0          # No trade
        }
        return multipliers.get(signal_type, 0.0)

    def _validate_signal(self, signal: RangeSignalData) -> bool:
        """
        VALIDATION FINALE SIGNAL RANGE

        Vérifications :
        - R:R acceptable
        - Bias compliance
        - Confluence minimum
        - Range quality
        """

        # Exit signals toujours valides
        if signal.signal_type == RangeSignalType.EXIT_SPECIAL:
            return True

        # R:R minimum pour range
        if signal.risk_reward_ratio() < 1.2:
            logger.warning(f"R:R range trop faible: {signal.risk_reward_ratio():.2f}")
            return False

        # Bias compliance
        if not signal.bias_compliance:
            logger.warning("Signal ne respecte pas le bias")
            return False

        # Confluence minimum
        min_confluence = {
            RangeSignalType.PREMIUM_BOUNCE: 0.85,
            RangeSignalType.STRONG_BOUNCE: 0.70,
            RangeSignalType.WEAK_BOUNCE: 0.60
        }

        required_confluence = min_confluence.get(signal.signal_type, 0.60)
        if signal.confluence_score < required_confluence:
            logger.warning(f"Confluence range insuffisante: {signal.confluence_score:.2f}")
            return False

        # Range quality minimum
        if signal.range_structure.range_quality == RangeQuality.INVALID:
            logger.warning("Range quality insuffisante")
            return False

        return True

    # === HELPER METHODS ===

    def _find_clustered_level(self, prices: List[float], target: float, tolerance: float) -> float:
        """Trouve niveau clustered près du target"""
        nearby_prices = [p for p in prices if abs(p - target) <= tolerance]
        return np.mean(nearby_prices) if nearby_prices else target

    def _count_level_tests(self, prices: List[float], level: float, tolerance: float) -> int:
        """Compte tests d'un niveau"""
        return sum(1 for p in prices if abs(p - level) <= tolerance)

    def _evaluate_range_quality(self,
                                range_size: float,
                                support_tests: int,
                                resistance_tests: int,
                                bars: List[MarketData]) -> RangeQuality:
        """Évaluation qualité range"""

        score = 0.0

        # Range size optimal (25%)
        if 10 <= range_size <= 25:
            score += 0.25
        elif 8 <= range_size <= 35:
            score += 0.15

        # Tests des niveaux (35%)
        test_score = min((support_tests + resistance_tests) / 6, 1.0)  # Max à 6 tests
        score += test_score * 0.35

        # Respect des niveaux (25%)
        respect_rate = self._calculate_level_respect_rate(bars)
        score += respect_rate * 0.25

        # Volatilité contraction (15%)
        vol_contraction = self._calculate_volatility_contraction(bars)
        score += vol_contraction * 0.15

        # Classification
        if score >= 0.8:
            return RangeQuality.EXCELLENT
        elif score >= 0.6:
            return RangeQuality.GOOD
        elif score >= 0.4:
            return RangeQuality.POOR
        else:
            return RangeQuality.INVALID

    def _analyze_primary_trend_bias(self, bars: List[MarketData]) -> RangeBias:
        """Analyse bias tendance primaire"""
        if len(bars) < 10:
            return RangeBias.NEUTRAL

        closes = [bar.close for bar in bars]
        trend = np.polyfit(range(len(closes)), closes, 1)[0]

        if trend > ES_TICK_SIZE:
            return RangeBias.BULLISH_BIAS
        elif trend < -ES_TICK_SIZE:
            return RangeBias.BEARISH_BIAS
        else:
            return RangeBias.NEUTRAL

    def _check_bullish_patterns(
            self, sierra_patterns: Optional[Dict[str, float]]) -> Tuple[bool, str, float]:
        """Vérification patterns haussiers Sierra"""
        if not sierra_patterns:
            return False, "None", 0.0

        # Long Down Up Bar
        long_down_up = sierra_patterns.get('long_down_up_bar', 0.0)
        if long_down_up > 0.6:
            return True, "long_down_up_bar", long_down_up

        # Battle navale signal haussier
        battle_signal = sierra_patterns.get('battle_navale_signal', 0.5)
        if battle_signal > 0.7:
            return True, "battle_navale_bullish", battle_signal

        return False, "None", 0.0

    def _check_bearish_patterns(
            self, sierra_patterns: Optional[Dict[str, float]]) -> Tuple[bool, str, float]:
        """Vérification patterns baissiers Sierra"""
        if not sierra_patterns:
            return False, "None", 0.0

        # Color Down Setting
        color_down = sierra_patterns.get('color_down_setting', 0.0)
        if color_down > 0.6:
            return True, "color_down_setting", color_down

        # Long Up Down Bar
        long_up_down = sierra_patterns.get('long_up_down_bar', 0.0)
        if long_up_down > 0.6:
            return True, "long_up_down_bar", long_up_down

        # Battle navale signal baissier
        battle_signal = sierra_patterns.get('battle_navale_signal', 0.5)
        if battle_signal < 0.3:
            return True, "battle_navale_bearish", 1.0 - battle_signal

        return False, "None", 0.0

    def _check_volume_confirmation(self, market_data: MarketData, level_type: str) -> bool:
        """Vérification confirmation volume"""
        if len(self.price_history) < 10:
            return False

        recent_volumes = [bar.volume for bar in list(self.price_history)[-10:]]
        avg_volume = np.mean(recent_volumes)

        return market_data.volume > avg_volume * 1.1

    def _calculate_bounce_confluence(self,
                                     price: float,
                                     structure_data: Optional[Dict[str, Any]],
                                     bounce_type: str) -> float:
        """Calcul confluence au niveau bounce"""
        if not structure_data:
            return 0.0

        confluence = 0.0

        # VWAP proximity
        vwap = structure_data.get('vwap_price', 0)
        if vwap and abs(price - vwap) <= 2 * ES_TICK_SIZE:
            confluence += 0.25

        # Market Profile levels
        if bounce_type == "support":
            val = structure_data.get('val_price', 0)
            pval = structure_data.get('pval', 0)
            if val and abs(price - val) <= 1.5 * ES_TICK_SIZE:
                confluence += 0.3
            if pval and abs(price - pval) <= 1.5 * ES_TICK_SIZE:
                confluence += 0.2
        else:  # resistance
            vah = structure_data.get('vah_price', 0)
            pvah = structure_data.get('pvah', 0)
            if vah and abs(price - vah) <= 1.5 * ES_TICK_SIZE:
                confluence += 0.3
            if pvah and abs(price - pvah) <= 1.5 * ES_TICK_SIZE:
                confluence += 0.2

        # Gamma levels
        if bounce_type == "support":
            put_wall = structure_data.get('put_wall', 0)
            if put_wall and abs(price - put_wall) <= 3 * ES_TICK_SIZE:
                confluence += 0.25
        else:
            call_wall = structure_data.get('call_wall', 0)
            if call_wall and abs(price - call_wall) <= 3 * ES_TICK_SIZE:
                confluence += 0.25

        return min(confluence, 1.0)

    def _evaluate_bounce_quality(self, bounce_setup: BounceSetup) -> float:
        """Évaluation qualité bounce setup"""
        quality = 0.0

        # Pattern confirmation (40%)
        if bounce_setup.pattern_confirmation:
            quality += 0.4 * bounce_setup.pattern_strength

        # Volume confirmation (30%)
        if bounce_setup.volume_confirmation:
            quality += 0.3

        # Confluence (30%)
        quality += bounce_setup.confluence_score * 0.3

        return min(quality, 1.0)

    def _detect_base_size_from_sierra(self, sierra_patterns: Optional[Dict[str, float]]) -> float:
        """Détection taille base depuis patterns Sierra"""
        if not sierra_patterns:
            return 2.0  # Default small base

        # Base quality donne indication de taille
        base_quality = sierra_patterns.get('base_quality', 0.0)

        # Estimation taille base selon qualité
        if base_quality > 0.8:
            return 6.0  # Large base
        elif base_quality > 0.6:
            return 4.5  # Medium base (trigger wide stop)
        else:
            return 2.5  # Small base

    def _get_range_quality_score(self, quality: RangeQuality) -> float:
        """Score numérique qualité range"""
        scores = {
            RangeQuality.EXCELLENT: 1.0,
            RangeQuality.GOOD: 0.7,
            RangeQuality.POOR: 0.4,
            RangeQuality.INVALID: 0.0
        }
        return scores.get(quality, 0.0)

    def _calculate_level_respect_rate(self, bars: List[MarketData]) -> float:
        """Calcul taux respect des niveaux"""
        # Implémentation simplifiée
        return 0.8  # Default good respect rate

    def _calculate_volatility_contraction(self, bars: List[MarketData]) -> float:
        """Calcul contraction volatilité"""
        if len(bars) < 10:
            return 0.5

        recent_ranges = [(bar.high - bar.low) for bar in bars[-5:]]
        older_ranges = [(bar.high - bar.low) for bar in bars[-10:-5]]

        recent_avg = np.mean(recent_ranges)
        older_avg = np.mean(older_ranges)

        if older_avg > 0:
            contraction = max(0, 1 - (recent_avg / older_avg))
            return min(contraction, 1.0)

        return 0.5

    def _update_stats(self, signal: RangeSignalData):
        """Mise à jour statistiques"""
        self.stats['bounce_signals'] += 1

        if signal.bias_compliance:
            self.stats['bias_compliant_trades'] += 1

        if signal.stop_type == "wide":
            self.stats['wide_stops_used'] += 1

        if signal.signal_type == RangeSignalType.EXIT_SPECIAL:
            self.stats['special_exits_triggered'] += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques stratégie range"""
        total_signals = self.stats['bounce_signals'] + self.stats['fade_signals']

        return {
            'total_range_signals': total_signals,
            'bounce_signals': self.stats['bounce_signals'],
            'fade_signals': self.stats['fade_signals'],
            'bias_compliance_rate': (self.stats['bias_compliant_trades'] / total_signals * 100) if total_signals > 0 else 0,
            'wide_stops_usage': self.stats['wide_stops_used'],
            'special_exits': self.stats['special_exits_triggered'],
            'current_range_active': self.current_range.range_detected if self.current_range else False,
            'current_range_quality': self.current_range.range_quality.value if self.current_range else "None"
        }

# === FACTORY FUNCTIONS ===


def create_range_strategy(config: Optional[Dict[str, Any]] = None) -> RangeStrategy:
    """Factory function pour stratégie range"""
    return RangeStrategy(config)


def analyze_range_opportunity(features: FeatureCalculationResult,
                              market_data: MarketData,
                              trend_context: Optional[Dict[str, Any]] = None,
                              structure_data: Optional[Dict[str, Any]] = None,
                              sierra_patterns: Optional[Dict[str, float]] = None,
                              strategy: Optional[RangeStrategy] = None) -> Optional[RangeSignalData]:
    """Helper function pour analyse range"""

    if strategy is None:
        strategy = create_range_strategy()

    return strategy.analyze_range_signal(
        features=features,
        market_data=market_data,
        trend_context=trend_context,
        structure_data=structure_data,
        sierra_patterns=sierra_patterns
    )

# === TESTING ===


def test_range_strategy():
    """Test complet stratégie range"""
    logger.debug("TEST RANGE STRATEGY")
    print("=" * 40)

    # Création stratégie
    strategy = create_range_strategy()

    # Simulation données
    from features.feature_calculator import FeatureCalculationResult, SignalQuality

    # Features test (confluence élevée)
    features = FeatureCalculationResult(
        timestamp=pd.Timestamp.now(),
        confluence_score=0.82,  # Strong signal
        signal_quality=SignalQuality.STRONG
    )

    # Market data test
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4500.0,
        high=4502.0,
        low=4498.0,
        close=4499.0,  # Près du support
        volume=1800
    )

    # Trend context (bias bullish)
    trend_context = {
        'vwap_slope': 0.4,
        'dow_trend_direction': 'bullish',
        'trend_strength': 0.7
    }

    # Structure data test
    structure_data = {
        'vwap_price': 4501.0,
        'val_price': 4498.5,
        'put_wall': 4495.0
    }

    # Sierra patterns test
    sierra_patterns = {
        'long_down_up_bar': 0.8,
        'battle_navale_signal': 0.75,
        'base_quality': 0.7
    }

    # Simulation historique pour range detection
    # Range 4498-4515
    for i in range(35):
        if i % 4 == 0:  # Test support
            test_close = 4498.0 + np.random.normal(0, 0.5)
        elif i % 4 == 2:  # Test resistance
            test_close = 4515.0 + np.random.normal(0, 0.5)
        else:  # Dans le range
            test_close = 4506.0 + np.random.normal(0, 3)

        test_bar = MarketData(
            timestamp=pd.Timestamp.now() - pd.Timedelta(minutes=35-i),
            symbol="ES",
            open=test_close - 1,
            high=test_close + 1.5,
            low=test_close - 1.5,
            close=test_close,
            volume=1500
        )
        strategy.price_history.append(test_bar)

    # Analyse signal
    signal = strategy.analyze_range_signal(
        features=features,
        market_data=market_data,
        trend_context=trend_context,
        structure_data=structure_data,
        sierra_patterns=sierra_patterns
    )

    if signal:
        logger.info("Signal généré: {signal.signal_type.value}")
        logger.info("Direction: {signal.direction}")
        logger.info("Bias: {signal.bias.value}")
        logger.info("Entry: {signal.entry_price:.2f}")
        logger.info("Stop: {signal.stop_loss:.2f}")
        logger.info("Target: {signal.take_profit:.2f}")
        logger.info("Stop type: {signal.stop_type}")
        logger.info("R:R: {signal.risk_reward_ratio():.2f}")
        logger.info("Position size: {signal.position_size:.1f}")
        logger.info("Confluence: {signal.confluence_score:.2f}")
        logger.info("Bias compliance: {signal.bias_compliance}")

        if signal.bounce_setup:
            logger.info("Bounce type: {signal.bounce_setup.bounce_type}")
            logger.info("Base size: {signal.bounce_setup.base_size_ticks:.1f} ticks")
            logger.info("Wide stop: {signal.bounce_setup.requires_wide_stop}")
    else:
        logger.error("Aucun signal généré")

    # Test range detection
    if strategy.current_range:
        range_struct = strategy.current_range
        logger.info("\n[STATS] RANGE DETECTED:")
        logger.info("   • Support: {range_struct.support_level:.2f}")
        logger.info("   • Resistance: {range_struct.resistance_level:.2f}")
        logger.info("   • Size: {range_struct.range_size_ticks:.1f} ticks")
        logger.info("   • Quality: {range_struct.range_quality.value}")
        logger.info("   • Tests: S={range_struct.support_tests}, R={range_struct.resistance_tests}")

    # Statistiques
    stats = strategy.get_statistics()
    logger.info("\n[UP] STATISTICS:")
    for key, value in stats.items():
        logger.info("   • {key}: {value}")

    logger.info("\n[TARGET] RANGE STRATEGY TEST COMPLETED")
    return True


if __name__ == "__main__":
    test_range_strategy()
