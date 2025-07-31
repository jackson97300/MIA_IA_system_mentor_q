"""
MIA_IA_SYSTEM - Features Package
Exports propres pour feature calculation + market regime detection
Version: Production Ready
Performance: Calculs optimisés <2ms garantis
"""

# Feature Calculator - Core component
from .feature_calculator import (
    # Main classes
    FeatureCalculator,
    FeatureCalculationResult,
    
    # Data structures
    OptionsData,
    MarketStructureData,
    ESNQData,
    
    # Enums
    SignalQuality,
    
    # Constants
    CONFLUENCE_WEIGHTS,
    TRADING_THRESHOLDS,
    
    # Factory functions
    create_feature_calculator,
    calculate_features_from_data
)

# Market Regime Detector - Brain of system
from .market_regime import (
    # Main classes
    MarketRegimeDetector,
    MarketRegimeData,
    
    # Analysis components
    TrendAnalysis,
    RangeAnalysis, 
    ESNQCorrelation,
    
    # Enums
    MarketRegime,
    TrendStrength,
    RangeType,
    
    # Factory functions
    create_market_regime_detector,
    analyze_market_regime
)

# Version info
__version__ = "2.0.0"
__author__ = "MIA Trading System"

# Package exports - Phase 2 complete
__all__ = [
    # Feature Calculator
    'FeatureCalculator',
    'FeatureCalculationResult',
    'OptionsData',
    'MarketStructureData', 
    'ESNQData',
    'SignalQuality',
    'CONFLUENCE_WEIGHTS',
    'TRADING_THRESHOLDS',
    'create_feature_calculator',
    'calculate_features_from_data',
    
    # Market Regime
    'MarketRegimeDetector',
    'MarketRegimeData',
    'TrendAnalysis',
    'RangeAnalysis',
    'ESNQCorrelation',
    'MarketRegime',
    'TrendStrength', 
    'RangeType',
    'create_market_regime_detector',
    'analyze_market_regime'
]

# Package-level constants
PACKAGE_FEATURES_COUNT = 8  # Exactly 8 features for ML
REGIME_DETECTION_ACCURACY = 0.85  # Target accuracy
FEATURE_CALCULATION_TIME_MS = 2.0  # Max calculation time

def get_package_info() -> dict:
    """Information du package features"""
    return {
        'version': __version__,
        'features_count': PACKAGE_FEATURES_COUNT,
        'components': ['FeatureCalculator', 'MarketRegimeDetector'],
        'performance_target_ms': FEATURE_CALCULATION_TIME_MS,
        'regime_accuracy_target': REGIME_DETECTION_ACCURACY
    }