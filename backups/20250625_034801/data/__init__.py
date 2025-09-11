"""
MIA_IA_SYSTEM - Data Package
📊 COLLECTION & STREAMING DONNÉES MARCHÉ
Version: Production Ready
Performance: <50ms latency, validation qualité, stockage intelligent

MODULES DISPONIBLES :
- market_data_feed : Streaming données temps réel multi-source
- data_collector : Collection et organisation snapshots trades
- trade_snapshotter : Capture détaillée trades avec métadonnées

WORKFLOW PRINCIPAL :
market_data_feed → data_collector → snapshots → ML pipeline
"""
import logging

# Configure logging
logger = logging.getLogger(__name__)


# Core data imports
try:
    from .market_data_feed import (
        MarketDataFeed, DataSource, FeedStatus, DataQuality,
        TickData, TickType, FeedStatistics, DataQualityMonitor,
        create_market_data_feed, start_data_feed_service
    )
    DATA_FEED_AVAILABLE = True
except ImportError as e:
    logger.warning("market_data_feed import failed: {e}")
    DATA_FEED_AVAILABLE = False

try:
    from .data_collector import (
        DataCollector, DataFormat, DataPeriod, DataQuality,
        create_data_collector
    )
    DATA_COLLECTOR_AVAILABLE = True
except ImportError as e:
    logger.warning("data_collector import failed: {e}")
    DATA_COLLECTOR_AVAILABLE = False

# Export control
__all__ = []

if DATA_FEED_AVAILABLE:
    __all__.extend([
        'MarketDataFeed', 'DataSource', 'FeedStatus', 'DataQuality',
        'TickData', 'TickType', 'FeedStatistics', 'DataQualityMonitor',
        'create_market_data_feed', 'start_data_feed_service'
    ])

if DATA_COLLECTOR_AVAILABLE:
    __all__.extend([
        'DataCollector', 'DataFormat', 'DataPeriod', 'DataQuality',
        'create_data_collector'
    ])

# Package info
__version__ = "1.0.0"
__author__ = "MIA Trading System"

# Status functions
def get_data_package_status():
    """Status du package data"""
    return {
        'market_data_feed_available': DATA_FEED_AVAILABLE,
        'data_collector_available': DATA_COLLECTOR_AVAILABLE,
        'version': __version__
    }

def test_data_package():
    """Test rapide du package data"""
    logger.info("📊 TEST DATA PACKAGE")
    print("=" * 25)
    
    status = get_data_package_status()
    
    for module, available in status.items():
        if module != 'version':
            icon = "✅" if available else "❌"
            logger.info("{icon} {module}: {'Available' if available else 'Not available'}")
    
    logger.info("📦 Version: {status['version']}")
    
    # Test imports
    if DATA_FEED_AVAILABLE:
        try:
            feed = create_market_data_feed()
            logger.info("MarketDataFeed: Factory function OK")
        except Exception as e:
            logger.error("MarketDataFeed: {e}")
    
    if DATA_COLLECTOR_AVAILABLE:
        try:
            collector = create_data_collector()
            logger.info("DataCollector: Factory function OK")
        except Exception as e:
            logger.error("DataCollector: {e}")
    
    return status

if __name__ == "__main__":
    test_data_package()