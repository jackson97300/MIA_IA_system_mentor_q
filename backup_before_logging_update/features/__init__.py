"""
Features module pour MIA_IA_SYSTEM
"""

import logging

logger = logging.getLogger(__name__)
# Vérifier si la version optimisée est disponible
OPTIMIZED_CALCULATOR_AVAILABLE = False
try:
    from .feature_calculator_optimized import FeatureCalculatorOptimized
    OPTIMIZED_CALCULATOR_AVAILABLE = True
except ImportError:
    pass


# Safe imports with error handling
__all__ = []

try:
    from .feature_calculator import FeatureCalculator, create_feature_calculator
    __all__.extend(['FeatureCalculator', 'create_feature_calculator'])
except ImportError as e:
    logger.warning(f"Could not import feature_calculator: {e}")

try:
    from .market_regime import MarketRegimeDetector, create_market_regime_detector
    __all__.extend(['MarketRegimeDetector', 'create_market_regime_detector'])
except ImportError as e:
    logger.warning(f"Could not import market_regime: {e}")

try:
    from .confluence_analyzer import ConfluenceAnalyzer, create_confluence_analyzer
    __all__.extend(['ConfluenceAnalyzer', 'create_confluence_analyzer'])
except ImportError as e:
    logger.warning(f"Could not import confluence_analyzer: {e}")
