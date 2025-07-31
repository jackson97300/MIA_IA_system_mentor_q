"""
Core module pour MIA_IA_SYSTEM
Version avec support UTF-8 et logger centralisé
"""

# IMPORTANT: Importer le logger en premier pour configurer UTF-8
from .logger import get_logger

logger = get_logger(__name__)

# Import base types
try:
    from .base_types import (
        MarketData, TradingSignal, SignalType, MarketRegime,
        ES_TICK_SIZE, ES_TICK_VALUE, OrderFlowData,
        get_session_phase, validate_market_data, TradeResult,
        SystemState
    )
    base_imports = True
    logger.debug("✅ base_types importé avec succès")
except ImportError as e:
    logger.warning(f"Could not import base_types: {e}")
    base_imports = False

# Import detectors
try:
    from .battle_navale import (
        BattleNavaleDetector, 
        BattleNavaleAnalyzer,
        create_battle_navale_detector
    )
    battle_imports = True
    logger.debug("✅ battle_navale importé avec succès")
except ImportError as e:
    logger.warning(f"Could not import battle_navale: {e}")
    battle_imports = False

try:
    from .patterns_detector import PatternsDetector, create_patterns_detector
    patterns_imports = True
    logger.debug("✅ patterns_detector importé avec succès")
except ImportError as e:
    logger.warning(f"Could not import patterns_detector: {e}")
    patterns_imports = False

# Import connectors
try:
    from .ibkr_connector import IBKRConnector, create_ibkr_connector
    ibkr_imports = True
    logger.debug("✅ ibkr_connector importé avec succès")
except ImportError as e:
    logger.warning(f"Could not import ibkr_connector: {e}")
    ibkr_imports = False

try:
    from .sierra_connector import SierraConnector, create_sierra_connector
    sierra_imports = True
    logger.debug("✅ sierra_connector importé avec succès")
except ImportError as e:
    logger.warning(f"Could not import sierra_connector: {e}")
    sierra_imports = False

try:
    from .structure_data import StructureData, create_structure_data
    structure_imports = True
    logger.debug("✅ structure_data importé avec succès")
except ImportError as e:
    logger.warning(f"Could not import structure_data: {e}")
    structure_imports = False

# Import logger functions pour export
try:
    from .logger import get_logger, setup_logging, get_logger_config
    logger_imports = True
    logger.debug("✅ logger functions importées avec succès")
except ImportError as e:
    logger.warning(f"Could not import logger functions: {e}")
    logger_imports = False

# Build __all__ based on successful imports
__all__ = []

# Logger functions (priorité pour configuration UTF-8)
if logger_imports:
    __all__.extend(['get_logger', 'setup_logging', 'get_logger_config'])

# Base types
if base_imports:
    __all__.extend([
        'MarketData', 'TradingSignal', 'SignalType', 'MarketRegime',
        'ES_TICK_SIZE', 'ES_TICK_VALUE', 'OrderFlowData',
        'get_session_phase', 'validate_market_data', 'TradeResult',
        'SystemState'
    ])

# Detectors
if battle_imports:
    __all__.extend([
        'BattleNavaleDetector', 
        'BattleNavaleAnalyzer',
        'create_battle_navale_detector'
    ])

if patterns_imports:
    __all__.extend(['PatternsDetector', 'create_patterns_detector'])

# Connectors
if ibkr_imports:
    __all__.extend(['IBKRConnector', 'create_ibkr_connector'])

if sierra_imports:
    __all__.extend(['SierraConnector', 'create_sierra_connector'])

# Structure data
if structure_imports:
    __all__.extend(['StructureData', 'create_structure_data'])

# Log summary of imports
successful_imports = []
failed_imports = []

if base_imports: successful_imports.append("base_types")
else: failed_imports.append("base_types")

if battle_imports: successful_imports.append("battle_navale")
else: failed_imports.append("battle_navale")

if patterns_imports: successful_imports.append("patterns_detector")
else: failed_imports.append("patterns_detector")

if ibkr_imports: successful_imports.append("ibkr_connector")
else: failed_imports.append("ibkr_connector")

if sierra_imports: successful_imports.append("sierra_connector")
else: failed_imports.append("sierra_connector")

if structure_imports: successful_imports.append("structure_data")
else: failed_imports.append("structure_data")

if logger_imports: successful_imports.append("logger")
else: failed_imports.append("logger")

# Log initialization status
if successful_imports:
    logger.info(f"Core module initialized. Loaded: {', '.join(successful_imports)}")
if failed_imports:
    logger.warning(f"Failed to load: {', '.join(failed_imports)}")

# Version info
__version__ = "3.1.0"
__author__ = "MIA Trading System"

# Module status function
def get_module_status():
    """Get status of core module imports"""
    return {
        'version': __version__,
        'successful_imports': successful_imports,
        'failed_imports': failed_imports,
        'total_exports': len(__all__),
        'logger_configured': logger_imports,
        'base_types_available': base_imports,
        'battle_navale_available': battle_imports,
        'patterns_available': patterns_imports,
        'ibkr_available': ibkr_imports,
        'sierra_available': sierra_imports,
        'structure_available': structure_imports
    }

__all__.append('get_module_status')