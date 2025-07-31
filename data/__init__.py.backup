"""
MIA_IA_SYSTEM - Data Package
📊 COLLECTION & STREAMING DONNÉES MARCHÉ
Version: Production Ready - CORRIGÉ
Performance: <50ms latency, validation qualité, stockage intelligent

CORRECTIONS APPLIQUÉES:
- Remplacement de tous les print() par logging
- Ajout configuration logging appropriée
- Messages de log structurés et informatifs
"""

import sys
import logging

if sys.platform == "win32":

# Configure logging
logger = logging.getLogger(__name__)

"""
MODULES DISPONIBLES :
- market_data_feed : Streaming données temps réel multi-source
- data_collector : Collection et organisation snapshots trades
- trade_snapshotter : Capture détaillée trades avec métadonnées

WORKFLOW PRINCIPAL :
market_data_feed → data_collector → snapshots → ML pipeline
"""

# Core data imports
try:
    from .market_data_feed import (
        MarketDataFeed, DataSource, FeedStatus, DataQuality,
        TickData, TickType, FeedStatistics, DataQualityMonitor,
        create_market_data_feed, start_data_feed_service
    )
    DATA_FEED_AVAILABLE = True
    logger.debug("market_data_feed importé avec succès")
except ImportError as e:
    logger.warning(f"market_data_feed import failed: {e}")
    DATA_FEED_AVAILABLE = False

try:
    from .data_collector import (
        DataCollector, DataFormat, DataPeriod, DataQuality,
        create_data_collector
    )
    DATA_COLLECTOR_AVAILABLE = True
    logger.debug("data_collector importé avec succès")
except ImportError as e:
    logger.warning(f"data_collector import failed: {e}")
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
    status = {
        'market_data_feed_available': DATA_FEED_AVAILABLE,
        'data_collector_available': DATA_COLLECTOR_AVAILABLE,
        'version': __version__
    }
    
    # Log status si des modules manquent
    if not DATA_FEED_AVAILABLE or not DATA_COLLECTOR_AVAILABLE:
        logger.info(f"Data package status: {status}")
    
    return status

# Log au chargement du module
logger.info(f"Data package v{__version__} loaded - Feed: {DATA_FEED_AVAILABLE}, Collector: {DATA_COLLECTOR_AVAILABLE}")