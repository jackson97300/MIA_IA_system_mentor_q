"""
MIA_IA_SYSTEM - Core Base Types CORRIGÉ
Types fondamentaux + utilitaires système
Version: Production Ready
Performance: Critical types optimisés

CORRECTION: Suppression import circulaire StructureData
"""

from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import time
import logging

# Configure logging
logger = logging.getLogger(__name__)

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

# === ENUMS ADDITIONNELS ===

class TradingDecision(Enum):
    """Décisions de trading"""
    LONG = "long"
    SHORT = "short"
    EXIT = "exit"
    HOLD = "hold"
    NO_TRADE = "no_trade"

class MarketState(Enum):
    """État du marché"""
    OPEN = "open"
    CLOSED = "closed"
    PRE_MARKET = "pre_market"
    AFTER_HOURS = "after_hours"

class SystemState(Enum):
    """État du système"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    MAINTENANCE = "maintenance"

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
            logger.warning(f"OHLC incohérent: O={self.open}, H={self.high}, L={self.low}, C={self.close}")
    
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
        """Calculs post-init"""
        total_volume = self.bid_volume + self.ask_volume
        if total_volume > 0:
            self.imbalance_ratio = abs(self.bid_volume - self.ask_volume) / total_volume
        
        # Si net_delta pas fourni, le calculer
        if self.net_delta is None:
            self.net_delta = self.ask_volume - self.bid_volume
    
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
                logger.warning(f"Stop loss incohérent pour LONG: price={self.price}, stop={self.stop_loss}")
    
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
            'market_regime': self.market_regime.value,
            'patterns_detected': [p.value for p in self.patterns_detected],
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'position_size': self.position_size,
            'risk_reward_ratio': self.risk_reward_ratio,
            'metadata': self.metadata
        }

@dataclass
class TradeResult:
    """Résultat d'un trade exécuté"""
    trade_id: str
    entry_signal: TradingSignal
    entry_timestamp: pd.Timestamp
    entry_price: float
    quantity: float
    
    # Exit data
    exit_timestamp: Optional[pd.Timestamp] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None
    
    # Performance
    pnl_ticks: Optional[float] = None
    pnl_dollars: Optional[float] = None
    duration_minutes: Optional[int] = None
    max_favorable: Optional[float] = None
    max_adverse: Optional[float] = None
    
    # Fees
    commission: float = 0.0
    slippage: float = 0.0
    
    def __post_init__(self):
        """Calculs automatiques"""
        if self.exit_price and self.exit_timestamp:
            self._calculate_performance()
    
    def _calculate_performance(self):
        """Calcul performance trade"""
        if not (self.exit_price and self.entry_price):
            return
        
        # Direction du trade
        is_long = self.entry_signal.signal_type in [SignalType.LONG_TREND, SignalType.LONG_RANGE]
        
        # PnL en ticks
        if is_long:
            self.pnl_ticks = (self.exit_price - self.entry_price) / ES_TICK_SIZE
        else:
            self.pnl_ticks = (self.entry_price - self.exit_price) / ES_TICK_SIZE
        
        # PnL en dollars (ES)
        self.pnl_dollars = self.pnl_ticks * ES_TICK_VALUE * abs(self.quantity)
        
        # Frais
        self.pnl_dollars -= (self.commission + self.slippage)
        
        # Durée
        if self.exit_timestamp:
            duration = self.exit_timestamp - self.entry_timestamp
            self.duration_minutes = int(duration.total_seconds() / 60)
    
    @property
    def is_winner(self) -> bool:
        """Trade gagnant"""
        return self.pnl_dollars > 0 if self.pnl_dollars else False
    
    @property
    def return_pct(self) -> Optional[float]:
        """Retour en pourcentage"""
        if not self.pnl_dollars:
            return None
        
        invested = abs(self.entry_price * self.quantity * ES_TICK_VALUE / ES_TICK_SIZE)
        return (self.pnl_dollars / invested) * 100 if invested > 0 else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion dictionnaire pour analyse"""
        return {
            'trade_id': self.trade_id,
            'entry_timestamp': self.entry_timestamp,
            'exit_timestamp': self.exit_timestamp,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'quantity': self.quantity,
            'pnl_ticks': self.pnl_ticks,
            'pnl_dollars': self.pnl_dollars,
            'duration_minutes': self.duration_minutes,
            'exit_reason': self.exit_reason,
            'is_winner': self.is_winner,
            'return_pct': self.return_pct,
            'signal_type': self.entry_signal.signal_type.value,
            'confidence': self.entry_signal.confidence,
            'patterns': [p.value for p in self.entry_signal.patterns_detected]
        }

# === DATACLASSES POUR MÉTRIQUES ===

@dataclass
class SystemMetrics:
    """Métriques système globales"""
    timestamp: pd.Timestamp
    total_trades: int = 0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    daily_pnl: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'total_trades': self.total_trades,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'daily_pnl': self.daily_pnl
        }

@dataclass
class PerformanceReport:
    """Rapport de performance"""
    period_start: pd.Timestamp
    period_end: pd.Timestamp
    metrics: SystemMetrics
    trades: List[TradeResult] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'period_start': self.period_start,
            'period_end': self.period_end,
            'metrics': self.metrics.to_dict(),
            'total_trades': len(self.trades),
            'trades': [t.to_dict() for t in self.trades[:10]]  # Top 10 seulement
        }

# === CONSTANTES TRADING ===

# ES Futures
ES_TICK_SIZE = 0.25
ES_TICK_VALUE = 12.50
MES_TICK_VALUE = 1.25

# Trading hours (UTC)
TRADING_HOURS = {
    'pre_market': (9, 14),      # 3h-8h ET
    'london_open': (14, 16),    # 8h-10h ET
    'ny_open': (16, 20),        # 10h-14h ET
    'lunch': (20, 21),          # 14h-15h ET
    'afternoon': (21, 23),      # 15h-17h ET
    'close': (23, 1),           # 17h-19h ET
}

# Risk management
DEFAULT_RISK_PARAMS = {
    'max_position_size': 3,
    'max_daily_loss': 1000.0,
    'max_daily_trades': 10,
    'min_confidence': 0.65,
    'min_risk_reward': 1.2
}

# Performance targets - UPDATED avec nos valeurs
PERFORMANCE_TARGETS = {
    'daily_profit_target': 500.0,
    'weekly_profit_target': 2000.0,
    'max_drawdown_pct': 10.0,
    'min_win_rate': 0.60,
    'min_profit_factor': 1.5,
    'max_signal_generation_ms': 50,      # NOUVEAU
    'max_order_execution_ms': 100,       # NOUVEAU
    'max_end_to_end_ms': 200,           # NOUVEAU
    'analysis_frequency_ms': 1000        # NOUVEAU
}

# === UTILITY FUNCTIONS ===

def get_session_phase(timestamp: pd.Timestamp) -> SessionPhase:
    """Détermine phase de session"""
    hour = timestamp.hour
    
    if 9 <= hour < 14:
        return SessionPhase.PRE_MARKET
    elif 14 <= hour < 16:
        return SessionPhase.LONDON_OPEN
    elif 16 <= hour < 20:
        return SessionPhase.NY_OPEN
    elif 20 <= hour < 21:
        return SessionPhase.LUNCH
    elif 21 <= hour < 23:
        return SessionPhase.AFTERNOON
    elif 23 <= hour or hour < 1:
        return SessionPhase.CLOSE
    else:
        return SessionPhase.AFTER_HOURS

def validate_market_data(data: MarketData) -> bool:
    """Validation données marché"""
    try:
        # Check OHLC coherence
        if not (data.low <= data.open <= data.high and 
                data.low <= data.close <= data.high):
            return False
        
        # Check positive volume
        if data.volume <= 0:
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
    
    profit_factor = abs(avg_win * len(winners) / (avg_loss * len(losers))) if losers else float('inf')
    
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
    
    logger.info("\n🎯 BASE TYPES TEST COMPLETED")
    return True

if __name__ == "__main__":
    test_base_types()