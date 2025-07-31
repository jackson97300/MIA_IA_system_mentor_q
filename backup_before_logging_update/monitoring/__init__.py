"""
Monitoring module pour MIA_IA_SYSTEM
"""

import logging

logger = logging.getLogger(__name__)

# Safe imports
__all__ = []

try:
    from .live_monitor import LiveMonitor, create_live_monitor
    __all__.extend(['LiveMonitor', 'create_live_monitor'])
except ImportError as e:
    logger.warning(f"Could not import live_monitor: {e}")

try:
    from .performance_tracker import PerformanceTracker, create_performance_tracker
    __all__.extend(['PerformanceTracker', 'create_performance_tracker'])
except ImportError as e:
    logger.warning(f"Could not import performance_tracker: {e}")

try:
    from .alert_system import AlertSystem, create_alert_system
    __all__.extend(['AlertSystem', 'create_alert_system'])
except ImportError as e:
    logger.warning(f"Could not import alert_system: {e}")

try:
    from .health_checker import HealthChecker, create_health_checker
    __all__.extend(['HealthChecker', 'create_health_checker'])
except ImportError as e:
    logger.warning(f"Could not import health_checker: {e}")

try:
    from .discord_notifier import DiscordNotifier, create_discord_notifier, notify_discord_available
    __all__.extend(['DiscordNotifier', 'create_discord_notifier', 'notify_discord_available'])
except ImportError as e:
    logger.warning(f"Could not import discord_notifier or notify_discord_available: {e}")
