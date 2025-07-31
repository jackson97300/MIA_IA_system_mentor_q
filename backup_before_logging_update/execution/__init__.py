"""
Execution module pour MIA_IA_SYSTEM
"""

import logging

logger = logging.getLogger(__name__)

__all__ = []

# Import principal : OrderManager
try:
    from .order_manager import OrderManager, create_order_manager
    __all__.extend(['OrderManager', 'create_order_manager'])
except ImportError as e:
    logger.warning(f"Could not import order_manager: {e}")

# Import RiskManager
try:
    from .risk_manager import RiskManager, create_risk_manager
    __all__.extend(['RiskManager', 'create_risk_manager'])
except ImportError as e:
    logger.warning(f"Could not import risk_manager: {e}")

# Import SimpleBattleNavaleTrader et ses types associés
try:
    from .simple_trader import (
        SimpleBattleNavaleTrader, 
        create_simple_trader,
        AutomationStatus,  # <-- Import depuis simple_trader, pas trade_snapshotter
        TradingMode,       # <-- Aussi depuis simple_trader
        TradingSession,    # <-- Optionnel mais utile
        Position          # <-- Optionnel mais utile
    )
    __all__.extend([
        'SimpleBattleNavaleTrader', 
        'create_simple_trader',
        'AutomationStatus',
        'TradingMode',
        'TradingSession',
        'Position'
    ])
except ImportError as e:
    logger.warning(f"Could not import simple_trader: {e}")

# Import TradeSnapshotter
try:
    from .trade_snapshotter import TradeSnapshotter, create_trade_snapshotter
    __all__.extend(['TradeSnapshotter', 'create_trade_snapshotter'])
except ImportError as e:
    logger.warning(f"Could not import trade_snapshotter: {e}")