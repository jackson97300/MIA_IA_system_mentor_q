"""
Data module pour MIA_IA_SYSTEM
"""

from core.logger import get_logger

logger = get_logger(__name__)

# Safe imports
__all__ = []

try:
    from .data_collector import DataCollector, create_data_collector
    __all__.extend(['DataCollector', 'create_data_collector'])
except ImportError as e:
    logger.warning(f"Could not import data_collector: {e}")

try:
    from .market_data_feed import MarketDataFeed, create_market_data_feed
    __all__.extend(['MarketDataFeed', 'create_market_data_feed'])
except ImportError as e:
    logger.warning(f"Could not import market_data_feed: {e}")

try:
    from .analytics import (
        DataAnalytics,
        PerformanceMetrics,
        PatternAnalysis,
        RiskAnalysis,
        MLAnalysis,
        AnalyticsReport,
        AnalysisType,
        ReportFormat,
        TimeFrame,
        create_data_analytics,
        generate_performance_report,
        test_data_analytics
    )
    __all__.extend([
        'DataAnalytics',
        'PerformanceMetrics',
        'PatternAnalysis',
        'RiskAnalysis',
        'MLAnalysis',
        'AnalyticsReport',
        'AnalysisType',
        'ReportFormat',
        'TimeFrame',
        'create_data_analytics',
        'generate_performance_report',
        'test_data_analytics'
    ])
except ImportError as e:
    logger.warning(f"Could not import analytics: {e}")