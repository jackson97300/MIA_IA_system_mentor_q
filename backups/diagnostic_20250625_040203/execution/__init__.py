"""
MIA_IA_SYSTEM - Execution Package
Exports pour order execution + automation trading + data collection
Version: Phase 3 - Automation Ready v4.0.0
Performance: Trading automation + snapshots obsessifs + Sierra Chart/IBKR intégré

ÉVOLUTION ARCHITECTURE :
- Phase 1 : Order execution de base (OrderManager, RiskManager)
- Phase 2 : Risk management avancé
- Phase 3 : Trading automation + Data collection intensive
- Phase 3.1 : Intégration Sierra Chart + IBKR (CURRENT v4.0)

NOUVEAUTÉS v4.0 :
- Configuration Sierra Chart + IBKR centralisée
- OrderManager multi-broker avec failover
- SimpleBattleNavaleTrader intégré Sierra/IBKR
- Modes DATA_COLLECTION optimisé pour ML
- Kill switch et sécurité renforcée
- Diagnostics système complets

COMPOSANTS INTÉGRÉS :
- OrderManager v4.0 : Multi-broker IBKR/Sierra + Kill switch
- RiskManager : Gestion risque Battle Navale spécialisée  
- SimpleBattleNavaleTrader : Automation complète avec modes adaptatifs
- TradeSnapshotter : Data collection obsessive ML-ready
"""

# Core execution components (Phase 1 & 2 - Enhanced v4.0)
from .order_manager import (
import logging

# Configure logging
logger = logging.getLogger(__name__)

    OrderManager,
    create_order_manager,
    # Data structures
    OrderRequest,
    OrderResult,
    Position as OrderPosition,  # ALIAS pour éviter conflit
    BrokerConnection,
    # Enums
    TradingMode as OrderTradingMode,  # ALIAS pour éviter conflit
    OrderType,
    OrderStatus,
    BrokerType,
    ConnectionStatus
)

from .risk_manager import (
    RiskManager,
    create_risk_manager,
    # Data structures
    RiskParameters,
    RiskMetrics,
    RiskDecision,
    # Enums
    RiskLevel,
    RiskAction
)

# Simple Battle Navale Trader - Automation Core (Phase 3 Enhanced v4.0)
from .simple_trader import (
    # Main automation class
    SimpleBattleNavaleTrader,
    
    # Data structures
    TradingSession,
    Position as TraderPosition,  # ALIAS - Position du trader
    
    # Enums
    AutomationStatus,
    TradingMode as TraderTradingMode,  # ALIAS - Mode du trader
    
    # Utility functions
    create_simple_trader,
    run_data_collection_session
)

# Trade Snapshotter - Data Collection Intensive (Phase 3)
from .trade_snapshotter import (
    # Main snapshotter class
    TradeSnapshotter,
    
    # Snapshot data structures
    MarketSnapshot,
    BattleNavaleSnapshot,
    ExecutionSnapshot,
    PositionSnapshot,
    TradeResultSnapshot,
    
    # Enums
    SnapshotType,
    DataQuality,
    
    # Factory function
    create_trade_snapshotter
)

# === RÉSOLUTION DES CONFLITS ===
# Export des types avec leurs noms complets pour éviter confusion

# Position types
Position = TraderPosition  # Par défaut, on utilise la version du trader
__all_positions__ = {
    'Position': TraderPosition,           # Version par défaut
    'OrderPosition': OrderPosition,       # Position de l'order manager
    'TraderPosition': TraderPosition      # Position du trader
}

# TradingMode types  
TradingMode = TraderTradingMode  # Par défaut, on utilise la version du trader
__all_trading_modes__ = {
    'TradingMode': TraderTradingMode,     # Version par défaut
    'OrderTradingMode': OrderTradingMode, # Mode de l'order manager
    'TraderTradingMode': TraderTradingMode # Mode du trader
}

# Version info - Updated
__version__ = "4.0.0"
__author__ = "MIA Trading System"

# === MAIN EXPORTS ===
__all__ = [
    # OrderManager exports
    'OrderManager',
    'create_order_manager',
    'OrderRequest',
    'OrderResult',
    'OrderPosition',           # Avec alias
    'BrokerConnection',
    'OrderTradingMode',        # Avec alias
    'OrderType',
    'OrderStatus',
    'BrokerType',
    'ConnectionStatus',
    
    # RiskManager exports
    'RiskManager',
    'create_risk_manager',
    'RiskParameters',
    'RiskMetrics',
    'RiskDecision',
    'RiskLevel',
    'RiskAction',
    
    # SimpleBattleNavaleTrader exports
    'SimpleBattleNavaleTrader',
    'TradingSession',
    'TraderPosition',          # Avec alias
    'Position',                # Alias par défaut
    'AutomationStatus',
    'TraderTradingMode',       # Avec alias
    'TradingMode',             # Alias par défaut
    'create_simple_trader',
    'run_data_collection_session',
    
    # TradeSnapshotter exports
    'TradeSnapshotter',
    'MarketSnapshot',
    'BattleNavaleSnapshot',
    'ExecutionSnapshot',
    'PositionSnapshot',
    'TradeResultSnapshot',
    'SnapshotType',
    'DataQuality',
    'create_trade_snapshotter',
    
    # Version
    '__version__'
]

# === HELPER FUNCTIONS ===

def get_position_type(type_name: str = 'default'):
    """
    Récupère le bon type Position selon le contexte
    
    Args:
        type_name: 'order', 'trader' ou 'default'
    """
    if type_name == 'order':
        return OrderPosition
    elif type_name == 'trader':
        return TraderPosition
    else:
        return Position  # Par défaut = TraderPosition

def get_trading_mode_type(type_name: str = 'default'):
    """
    Récupère le bon type TradingMode selon le contexte
    
    Args:
        type_name: 'order', 'trader' ou 'default'
    """
    if type_name == 'order':
        return OrderTradingMode
    elif type_name == 'trader':
        return TraderTradingMode
    else:
        return TradingMode  # Par défaut = TraderTradingMode

# === DIAGNOSTIC FUNCTIONS ===

def check_imports():
    """Vérifie que tous les imports fonctionnent"""
    import_status = {}
    
    try:
        from .order_manager import OrderManager
        import_status['order_manager'] = True
    except ImportError as e:
        import_status['order_manager'] = f"Error: {e}"
    
    try:
        from .risk_manager import RiskManager
        import_status['risk_manager'] = True
    except ImportError as e:
        import_status['risk_manager'] = f"Error: {e}"
    
    try:
        from .simple_trader import SimpleBattleNavaleTrader
        import_status['simple_trader'] = True
    except ImportError as e:
        import_status['simple_trader'] = f"Error: {e}"
    
    try:
        from .trade_snapshotter import TradeSnapshotter
        import_status['trade_snapshotter'] = True
    except ImportError as e:
        import_status['trade_snapshotter'] = f"Error: {e}"
    
    return import_status

def diagnose_package():
    """Diagnostic complet du package execution"""
    logger.debug("DIAGNOSTIC EXECUTION PACKAGE v4.0")
    print("=" * 50)
    
    # Check imports
    logger.info("\n📦 IMPORT STATUS:")
    import_status = check_imports()
    for module, status in import_status.items():
        icon = "✅" if status is True else "❌"
        logger.info("  {icon} {module}: {status if status is not True else 'OK'}")
    
    # Check types resolution
    logger.info("\n🔧 TYPE RESOLUTION:")
    logger.info("  Position default → {Position.__name__}")
    logger.info("  TradingMode default → {TradingMode.__name__}")
    logger.info("  Aliases disponibles: OrderPosition, TraderPosition")
    logger.info("  Aliases disponibles: OrderTradingMode, TraderTradingMode")
    
    # Package info
    logger.info("\n📋 PACKAGE INFO:")
    logger.info("  Version: {__version__}")
    logger.info("  Components: 4 (OrderManager, RiskManager, SimpleBattleNavaleTrader, TradeSnapshotter)")
    
    return all(status is True for status in import_status.values())

# Auto-diagnostic au chargement (optionnel)
if __name__ == "__main__":
    diagnose_package()