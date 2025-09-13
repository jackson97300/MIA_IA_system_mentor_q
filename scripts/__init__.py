"""
Scripts module pour MIA_IA_SYSTEM
"""

from core.logger import get_logger

logger = get_logger(__name__)

# Safe imports
__all__ = []

try:
    from .archive_legacy import main as archive_legacy_main
    __all__.extend(['archive_legacy_main'])
except ImportError as e:
    logger.warning(f"Could not import archive_legacy: {e}")

try:
    from .backup_data import main as backup_data_main
    __all__.extend(['backup_data_main'])
except ImportError as e:
    logger.warning(f"Could not import backup_data: {e}")

try:
    from .cleanup_root import main as cleanup_root_main
    __all__.extend(['cleanup_root_main'])
except ImportError as e:
    logger.warning(f"Could not import cleanup_root: {e}")

try:
    from .deploy_live import main as deploy_live_main
    __all__.extend(['deploy_live_main'])
except ImportError as e:
    logger.warning(f"Could not import deploy_live: {e}")

try:
    from .start_automation import main as start_automation_main
    __all__.extend(['start_automation_main'])
except ImportError as e:
    logger.warning(f"Could not import start_automation: {e}")

try:
    from .train_models import main as train_models_main
    __all__.extend(['train_models_main'])
except ImportError as e:
    logger.warning(f"Could not import train_models: {e}")