"""
Monitoring module pour MIA_IA_SYSTEM
"""

from core.logger import get_logger

logger = get_logger(__name__)

# Initialize variables to None first
LiveMonitor = None
create_live_monitor = None
PerformanceTracker = None
create_performance_tracker = None
AlertSystem = None
create_alert_system = None
HealthChecker = None
create_health_checker = None
DiscordNotifier = None
create_discord_notifier = None
notify_discord_available = None

# Safe imports with availability tracking
__all__ = []
LIVE_MONITOR_AVAILABLE = False
PERFORMANCE_TRACKER_AVAILABLE = False
ALERT_SYSTEM_AVAILABLE = False
HEALTH_CHECKER_AVAILABLE = False
DISCORD_NOTIFIER_AVAILABLE = False

try:
    from .live_monitor import LiveMonitor, create_live_monitor
    __all__.extend(['LiveMonitor', 'create_live_monitor'])
    LIVE_MONITOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import live_monitor: {e}")

try:
    from .performance_tracker import PerformanceTracker, create_performance_tracker
    __all__.extend(['PerformanceTracker', 'create_performance_tracker'])
    PERFORMANCE_TRACKER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import performance_tracker: {e}")

try:
    from .alert_system import AlertSystem, create_alert_system
    __all__.extend(['AlertSystem', 'create_alert_system'])
    ALERT_SYSTEM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import alert_system: {e}")

try:
    from .health_checker import HealthChecker, create_health_checker
    __all__.extend(['HealthChecker', 'create_health_checker'])
    HEALTH_CHECKER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import health_checker: {e}")

try:
    from .discord_notifier import DiscordNotifier, create_discord_notifier, notify_discord_available
    __all__.extend(['DiscordNotifier', 'create_discord_notifier', 'notify_discord_available'])
    DISCORD_NOTIFIER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import discord_notifier or notify_discord_available: {e}")
    # Fallback function if discord_notifier not available
    def notify_discord_available():
        return False

# Function helper to check module availability
def is_module_available(module_name: str) -> bool:
    """Check if a monitoring module is available"""
    availability_map = {
        'live_monitor': LIVE_MONITOR_AVAILABLE,
        'LiveMonitor': LIVE_MONITOR_AVAILABLE,
        'performance_tracker': PERFORMANCE_TRACKER_AVAILABLE,
        'PerformanceTracker': PERFORMANCE_TRACKER_AVAILABLE,
        'alert_system': ALERT_SYSTEM_AVAILABLE,
        'AlertSystem': ALERT_SYSTEM_AVAILABLE,
        'health_checker': HEALTH_CHECKER_AVAILABLE,
        'HealthChecker': HEALTH_CHECKER_AVAILABLE,
        'discord_notifier': DISCORD_NOTIFIER_AVAILABLE,
        'DiscordNotifier': DISCORD_NOTIFIER_AVAILABLE,
    }
    
    if module_name in availability_map:
        return availability_map[module_name]
    
    return module_name in globals() and globals()[module_name] is not None

__all__.append('is_module_available')

# Log summary of successful imports
successful_imports = []
if LIVE_MONITOR_AVAILABLE:
    successful_imports.append('live_monitor')
if PERFORMANCE_TRACKER_AVAILABLE:
    successful_imports.append('performance_tracker')
if ALERT_SYSTEM_AVAILABLE:
    successful_imports.append('alert_system')
if HEALTH_CHECKER_AVAILABLE:
    successful_imports.append('health_checker')
if DISCORD_NOTIFIER_AVAILABLE:
    successful_imports.append('discord_notifier')

if successful_imports:
    logger.debug(f"Monitoring module loaded successfully: {', '.join(successful_imports)}")
else:
    logger.error("No monitoring modules could be loaded!")

# Export notify_discord_available fallback if not imported
if not DISCORD_NOTIFIER_AVAILABLE and 'notify_discord_available' not in globals():
    __all__.append('notify_discord_available')