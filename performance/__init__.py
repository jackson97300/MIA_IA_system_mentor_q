"""
Performance module pour MIA_IA_SYSTEM
"""

from core.logger import get_logger

logger = get_logger(__name__)

# Safe imports
__all__ = []

try:
    from .trade_logger import TradeLogger, create_trade_logger
    __all__.extend(['TradeLogger', 'create_trade_logger'])
except ImportError as e:
    logger.warning(f"Could not import trade_logger: {e}")

try:
    from .performance_analyzer import PerformanceAnalyzer, create_performance_analyzer
    __all__.extend(['PerformanceAnalyzer', 'create_performance_analyzer'])
except ImportError as e:
    logger.warning(f"Could not import performance_analyzer: {e}")

try:
    from .adaptive_optimizer import AdaptiveOptimizer, create_adaptive_optimizer
    __all__.extend(['AdaptiveOptimizer', 'create_adaptive_optimizer'])
except ImportError as e:
    logger.warning(f"Could not import adaptive_optimizer: {e}")

try:
    from .automation_metrics import AutomationMetrics, create_automation_metrics
    __all__.extend(['AutomationMetrics', 'create_automation_metrics'])
except ImportError as e:
    logger.warning(f"Could not import automation_metrics: {e}")
