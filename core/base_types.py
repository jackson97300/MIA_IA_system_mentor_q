"""
MIA_IA_SYSTEM - Core Base Types CORRIGÉ
Types fondamentaux + utilitaires système
Version: Production Ready
Performance: Critical types optimisés

CORRECTION APPLIQUÉE:
- Ligne ~150 : Correction OrderFlowData.__post_init__
  Suppression de self.order_flow inexistant
- Import circulaire StructureData supprimé
"""

from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import time
from core.logger import get_logger

# Configure logging
logger = get_logger(__name__)

# Export principal - SANS StructureData qui sera géré dans __init__.py
__all__ = [
    'MarketData',
    'TradingSignal',
    'TradingDecision',
    'MarketRegime',
    'MarketState',
    'TradeResult',
    'SystemMetrics',
    'PerformanceReport',
    'ConfigError',
    'SystemState',
    'OrderFlowData',
    'TradingFeatures',
    'SignalType',
    'PatternType',
    'SignalStrength',
    'SessionPhase',
    'ES_TICK_SIZE',
    'ES_TICK_VALUE',
    'MES_TICK_VALUE',
    'TRADING_HOURS',
    'DEFAULT_RISK_PARAMS',
    'PERFORMANCE_TARGETS',
    'get_session_phase',
    'validate_market_data',
    'calculate_performance_metrics'
]

# === CORE ENUMS ===


class MarketRegime(Enum):
    """Régimes de marché détectés"""
    TREND_BULLISH = "trend_bullish"
    TREND_BEARISH = "trend_bearish"
    RANGE_TIGHT = "range_tight"
    RANGE_WIDE = "range_wide"
    TRANSITION = "transition"
    UNKNOWN = "unknown"


class SignalType(Enum):
    """Types de signaux trading"""
    LONG_TREND = "long_trend"
    LONG_RANGE = "long_range"
    SHORT_TREND = "short_trend"
    SHORT_RANGE = "short_range"
    EXIT_PROFIT = "exit_profit"
    EXIT_STOP = "exit_stop"
    EXIT_RULE = "exit_rule"
    NO_SIGNAL = "no_signal"



class OrderType(Enum):
    """Types d'ordres"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"



class OrderStatus(Enum):
    """Statuts des ordres"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class PatternType(Enum):
    """Types de patterns détectés"""
    BATTLE_NAVALE = "battle_navale"
    GAMMA_PIN = "gamma_pin"
    HEADFAKE = "headfake"
    MICROSTRUCTURE = "microstructure"
    CONFLUENCE = "confluence"


class SignalStrength(IntEnum):
    """Force du signal (pour scoring)"""
    VERY_WEAK = 1
    WEAK = 2
    MEDIUM = 3
    STRONG = 4
    VERY_STRONG = 5


class SessionPhase(Enum):
    """Phases de session trading"""
    PRE_MARKET = "pre_market"
    LONDON_OPEN = "london_open"
    NY_OPEN = "ny_open"
    LUNCH = "lunch"
    AFTERNOON = "afternoon"
    CLOSE = "close"
    AFTER_HOURS = "after_hours"


class TradingDecision(Enum):
    """Décisions de trading possibles"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    CLOSE = "close"
    WAIT = "wait"


class MarketState(Enum):
    """État général du marché"""
    NORMAL = "normal"
    VOLATILE = "volatile"
    EXTREMELY_VOLATILE = "extremely_volatile"
    THIN = "thin"
    CLOSED = "closed"


class SystemState(Enum):
    """État du système de trading"""
    IDLE = "idle"
    ANALYZING = "analyzing"
    READY = "ready"
    TRADING = "trading"
    ERROR = "error"
    SHUTDOWN = "shutdown"

# === CONSTANTS ===


# ES Futures specifications
ES_TICK_SIZE = 0.25
ES_TICK_VALUE = 12.5  # Per tick
MES_TICK_VALUE = 1.25  # Micro ES

# Trading hours (ET)
TRADING_HOURS = {
    'pre_market': (4, 0),     # 4:00 AM
    'london_open': (8, 0),    # 8:00 AM
    'ny_open': (9, 30),       # 9:30 AM
    'lunch': (12, 0),         # 12:00 PM
    'afternoon': (14, 0),     # 2:00 PM
    'close': (16, 0),         # 4:00 PM
    'after_hours': (18, 0)    # 6:00 PM
}

# Default risk parameters
DEFAULT_RISK_PARAMS = {
    'max_position_size': 3,
    'daily_loss_limit': 1000.0,
    'max_risk_per_trade': 200.0,
    'default_stop_ticks': 12,
    'default_target_ticks': 24
}

# Performance targets
PERFORMANCE_TARGETS = {
    'min_win_rate': 0.55,
    'min_profit_factor': 1.5,
    'min_sharpe_ratio': 1.0,
    'max_drawdown': 0.10,
    'target_daily_return': 0.005
}

# === EXCEPTIONS ===


class ConfigError(Exception):
    """Erreur de configuration"""
    pass

# === CORE DATACLASSES ===


@dataclass
class MarketData:
    """Données marché standardisées"""
    timestamp: pd.Timestamp
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread: Optional[float] = None

    def __post_init__(self):
        """Validation et calculs post-init"""
        # Calcul spread si bid/ask disponibles
        if self.bid and self.ask:
            self.spread = self.ask - self.bid

        # Validation cohérence OHLC
        if not (self.low <= self.open <= self.high and
                self.low <= self.close <= self.high):
            logger.warning(
                f"OHLC incohérent: O={
                    self.open}, H={
                    self.high}, L={
                    self.low}, C={
                    self.close}")

    @property
    def range_size(self) -> float:
        """Taille range H-L"""
        return self.high - self.low

    @property
    def body_size(self) -> float:
        """Taille corps bougie"""
        return abs(self.close - self.open)

    @property
    def is_bullish(self) -> bool:
        """Bougie haussière"""
        return self.close > self.open

    def to_dict(self) -> Dict[str, Any]:
        """Conversion dictionnaire"""
        return {
            'timestamp': self.timestamp,
            'symbol': self.symbol,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'bid': self.bid,
            'ask': self.ask,
            'spread': self.spread
        }


@dataclass
class OrderFlowData:
    """Données order flow"""
    timestamp: pd.Timestamp
    symbol: str
    cumulative_delta: float
    bid_volume: int
    ask_volume: int
    aggressive_buys: int
    aggressive_sells: int

    # Champs optionnels avancés
    net_delta: Optional[float] = None
    large_trades: List[Dict[str, Any]] = field(default_factory=list)
    absorption_score: float = 0.0
    imbalance_ratio: float = 0.0

    def __post_init__(self):
        """Calculs post-init - CORRIGÉ"""
        # Calcul imbalance ratio
        total_volume = self.bid_volume + self.ask_volume
        if total_volume > 0:
            self.imbalance_ratio = abs(self.bid_volume - self.ask_volume) / total_volume

        # Si net_delta pas fourni, le calculer
        if self.net_delta is None:
            self.net_delta = self.ask_volume - self.bid_volume

        # Validation cohérence des données
        if self.net_delta != 0 and self.cumulative_delta == 0:
            logger.warning("Net delta non-nul avec cumulative delta zéro")

    @property
    def total_volume(self) -> int:
        """Volume total"""
        return self.bid_volume + self.ask_volume

    @property
    def aggressor_ratio(self) -> float:
        """Ratio aggressive buyers vs sellers"""
        total_aggressive = self.aggressive_buys + self.aggressive_sells
        if total_aggressive == 0:
            return 0.0
        return self.aggressive_buys / total_aggressive

    def get_net_delta(self) -> float:
        """Méthode pour obtenir net_delta (compatibilité)"""
        return self.net_delta if self.net_delta is not None else (self.ask_volume - self.bid_volume)


@dataclass
class TradingFeatures:
    """Features calculées pour ML"""
    timestamp: pd.Timestamp

    # Core features (8 maximum)
    battle_navale_signal: float
    gamma_pin_strength: float
    headfake_signal: float
    microstructure_anomaly: float
    market_regime_score: float
    base_quality: float
    confluence_score: float
    session_context: float

    # Metadata
    calculation_time_ms: float = 0.0
    feature_quality: float = 1.0

    def __post_init__(self):
        """Validation features"""
        # Validation range [0,1] pour toutes les features
        feature_values = [
            self.battle_navale_signal, self.gamma_pin_strength,
            self.headfake_signal, self.microstructure_anomaly,
            self.market_regime_score, self.base_quality,
            self.confluence_score, self.session_context
        ]

        for i, value in enumerate(feature_values):
            if not (0.0 <= value <= 1.0):
                logger.warning(f"Feature {i} hors range [0,1]: {value}")

    def to_array(self) -> np.ndarray:
        """Conversion array numpy pour ML"""
        return np.array([
            self.battle_navale_signal,
            self.gamma_pin_strength,
            self.headfake_signal,
            self.microstructure_anomaly,
            self.market_regime_score,
            self.base_quality,
            self.confluence_score,
            self.session_context
        ], dtype=np.float32)

    def to_dict(self) -> Dict[str, float]:
        """Conversion dictionnaire"""
        return {
            'battle_navale_signal': self.battle_navale_signal,
            'gamma_pin_strength': self.gamma_pin_strength,
            'headfake_signal': self.headfake_signal,
            'microstructure_anomaly': self.microstructure_anomaly,
            'market_regime_score': self.market_regime_score,
            'base_quality': self.base_quality,
            'confluence_score': self.confluence_score,
            'session_context': self.session_context
        }


@dataclass
class TradingSignal:
    """Signal de trading complet"""
    timestamp: pd.Timestamp
    signal_type: SignalType
    confidence: float
    strength: SignalStrength
    price: float

    # Context
    market_regime: MarketRegime
    patterns_detected: List[PatternType]
    features: TradingFeatures

    # Risk management
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_size: float = 1.0

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validation signal"""
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence doit être [0,1]: {self.confidence}")

        if self.stop_loss and self.signal_type in [SignalType.LONG_TREND, SignalType.LONG_RANGE]:
            if self.stop_loss >= self.price:
                logger.warning(
                    f"Stop loss incohérent pour LONG: price={
                        self.price}, stop={
                        self.stop_loss}")

    @property
    def risk_reward_ratio(self) -> Optional[float]:
        """Calcul ratio risk/reward"""
        if not (self.stop_loss and self.take_profit):
            return None

        if self.signal_type in [SignalType.LONG_TREND, SignalType.LONG_RANGE]:
            risk = abs(self.price - self.stop_loss)
            reward = abs(self.take_profit - self.price)
        else:
            risk = abs(self.stop_loss - self.price)
            reward = abs(self.price - self.take_profit)

        return reward / risk if risk > 0 else None

    def to_dict(self) -> Dict[str, Any]:
        """Conversion dictionnaire"""
        return {
            'timestamp': self.timestamp,
            'signal_type': self.signal_type.value,
            'confidence': self.confidence,
            'strength': self.strength.value,
            'price': self.price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'position_size': self.position_size,
            'risk_reward_ratio': self.risk_reward_ratio,
            'market_regime': self.market_regime.value,
            'patterns': [p.value for p in self.patterns_detected],
            'features': self.features.to_dict(),
            'metadata': self.metadata
        }


@dataclass
class Position:
    """Position de trading"""
    symbol: str
    quantity: int
    side: str  # 'long' ou 'short'
    entry_price: float
    stop_loss: float
    take_profit: float
    entry_time: datetime
    
@dataclass
class TradeResult:
    """Résultat d'un trade complet"""
    trade_id: str
    timestamp_open: pd.Timestamp
    timestamp_close: Optional[pd.Timestamp]

    # Trade details
    symbol: str
    signal_type: SignalType
    entry_price: float
    exit_price: Optional[float] = None
    position_size: float = 1.0

    # Performance
    pnl_ticks: Optional[float] = None
    pnl_dollars: Optional[float] = None
    commission: float = 0.0

    # Risk metrics
    max_favorable_excursion: float = 0.0
    max_adverse_excursion: float = 0.0

    # Status
    is_open: bool = True
    exit_reason: Optional[str] = None

    def close_trade(self, exit_price: float, exit_reason: str = "manual"):
        """Ferme le trade"""
        self.exit_price = exit_price
        self.timestamp_close = pd.Timestamp.now()
        self.is_open = False
        self.exit_reason = exit_reason

        # Calcul P&L
        if self.signal_type in [SignalType.LONG_TREND, SignalType.LONG_RANGE]:
            self.pnl_ticks = (exit_price - self.entry_price) / ES_TICK_SIZE
        else:
            self.pnl_ticks = (self.entry_price - exit_price) / ES_TICK_SIZE

        self.pnl_dollars = self.pnl_ticks * ES_TICK_VALUE * self.position_size - self.commission

    @property
    def duration_minutes(self) -> Optional[float]:
        """Durée du trade en minutes"""
        if self.timestamp_close:
            return (self.timestamp_close - self.timestamp_open).total_seconds() / 60
        return None

    @property
    def is_winner(self) -> bool:
        """Trade gagnant ?"""
        return self.pnl_dollars > 0 if self.pnl_dollars is not None else False


@dataclass
class SystemMetrics:
    """Métriques système temps réel"""
    timestamp: datetime

    # Performance
    latency_ms: float
    throughput_signals_per_min: float
    cpu_usage_percent: float
    memory_usage_mb: float

    # Trading
    active_positions: int
    signals_generated: int
    signals_executed: int
    orders_pending: int

    # Quality
    data_quality_score: float
    system_health_score: float

    def to_dict(self) -> Dict[str, Any]:
        """Conversion dictionnaire"""
        return asdict(self)


@dataclass
class PerformanceReport:
    """Rapport de performance"""
    period_start: datetime
    period_end: datetime

    # Trading metrics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float

    # Financial metrics
    gross_pnl: float
    net_pnl: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float

    # Risk metrics
    avg_risk_per_trade: float
    max_risk_exposure: float
    risk_adjusted_return: float

    # Details by strategy
    performance_by_strategy: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Conversion dictionnaire"""
        return asdict(self)

# === UTILITY FUNCTIONS ===


def get_session_phase(timestamp: pd.Timestamp) -> SessionPhase:
    """Détermine la phase de session actuelle"""
    hour = timestamp.hour

    if hour < 4:
        return SessionPhase.AFTER_HOURS
    elif hour < 8:
        return SessionPhase.PRE_MARKET
    elif hour < 9:
        return SessionPhase.LONDON_OPEN
    elif 9 <= hour < 10 or (hour == 9 and timestamp.minute < 30):
        return SessionPhase.LONDON_OPEN
    elif hour < 12:
        return SessionPhase.NY_OPEN
    elif hour < 14:
        return SessionPhase.LUNCH
    elif hour < 16:
        return SessionPhase.AFTERNOON
    elif hour < 18:
        return SessionPhase.CLOSE
    else:
        return SessionPhase.AFTER_HOURS


def validate_market_data(data: MarketData) -> bool:
    """Valide la cohérence des données marché"""
    try:
        # Check OHLC coherence
        if not (data.low <= data.open <= data.high and
                data.low <= data.close <= data.high):
            return False

        # Check volume
        if data.volume < 0:
            return False

        # Check reasonable price range
        if not (1000 < data.close < 10000):  # ES range reasonable
            return False

        return True
    except Exception:
        return False


def calculate_performance_metrics(trades: List[TradeResult]) -> Dict[str, float]:
    """Calcul métriques performance"""
    if not trades:
        return {}

    completed_trades = [t for t in trades if t.pnl_dollars is not None]
    if not completed_trades:
        return {}

    # Basic metrics
    total_pnl = sum(t.pnl_dollars for t in completed_trades)
    winners = [t for t in completed_trades if t.is_winner]
    losers = [t for t in completed_trades if not t.is_winner]

    win_rate = len(winners) / len(completed_trades)
    avg_win = np.mean([t.pnl_dollars for t in winners]) if winners else 0
    avg_loss = np.mean([t.pnl_dollars for t in losers]) if losers else 0

    profit_factor = abs(avg_win * len(winners) / (avg_loss * len(losers))
                        ) if losers else float('inf')

    return {
        'total_trades': len(completed_trades),
        'total_pnl': total_pnl,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
        'avg_duration': np.mean([t.duration_minutes for t in completed_trades if t.duration_minutes])
    }

# === TESTING ===


def test_base_types():
    """Test des types de base"""
    logger.debug("Test base types...")

    # Test MarketData
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4500.0,
        high=4510.0,
        low=4495.0,
        close=4505.0,
        volume=1000,
        bid=4504.75,
        ask=4505.25
    )

    logger.info("MarketData: {market_data.symbol} @ {market_data.close}")
    logger.info("Range: {market_data.range_size}, Spread: {market_data.spread}")

    # Test OrderFlowData
    order_flow = OrderFlowData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        cumulative_delta=150.0,
        bid_volume=800,
        ask_volume=1200,
        aggressive_buys=60,
        aggressive_sells=40
    )

    logger.info("OrderFlow: net_delta={order_flow.net_delta}")
    logger.info("Imbalance ratio: {order_flow.imbalance_ratio:.2%}")

    logger.info("\n[TARGET] BASE TYPES TEST COMPLETED")
    return True


if __name__ == "__main__":
    test_base_types()
