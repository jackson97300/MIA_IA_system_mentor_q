"""
Configuration module pour MIA_IA_SYSTEM
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# --- Initialisations explicites (évite les NameError) ---
TradingConfig = None
get_trading_config = None
get_feature_config = None

AutomationConfig = None
get_automation_config = None

MLConfig = None
get_ml_config = None

SierraIBKRConfig = None
get_sierra_config = None

# --- Imports try/except ---
try:
    from .trading_config import TradingConfig, get_trading_config, get_feature_config
except ImportError:
    logger.warning("Could not import trading_config")
    TradingConfig = None
    get_trading_config = None
    get_feature_config = None

try:
    from .automation_config import AutomationConfig, get_automation_config
except ImportError:
    logger.warning("Could not import automation_config")
    AutomationConfig = None
    get_automation_config = None

try:
    from .ml_config import MLConfig, get_ml_config
except ImportError:
    logger.warning("Could not import ml_config")
    MLConfig = None
    get_ml_config = None

try:
    from .sierra_config import SierraIBKRConfig, get_sierra_config
except ImportError:
    logger.warning("Could not import sierra_config")
    SierraIBKRConfig = None
    get_sierra_config = None

# --- Exports seulement les imports OK ---
__all__ = []

if TradingConfig:
    __all__.extend(['TradingConfig', 'get_trading_config', 'get_feature_config'])
if AutomationConfig:
    __all__.extend(['AutomationConfig', 'get_automation_config'])
if MLConfig:
    __all__.extend(['MLConfig', 'get_ml_config'])
if SierraIBKRConfig:
    __all__.extend(['SierraIBKRConfig', 'get_sierra_config'])
