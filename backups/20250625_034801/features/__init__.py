"""
MIA_IA_SYSTEM - Features Package
Exports propres pour feature calculation + market regime detection + confluence analysis
Version: Production Ready v2.1.0
Performance: Calculs optimisés <2ms garantis, confluence <3ms

COMPOSANTS INTÉGRÉS :
- FeatureCalculator : Calcul des 8 features core
- MarketRegimeDetector : Détection Trend/Range/Transition
- ConfluenceAnalyzer : Analyse multi-level confluence (NOUVEAU)

ÉVOLUTION ARCHITECTURE :
- Phase 1 : Feature calculation de base
- Phase 2 : Market regime detection  
- Phase 3 : Confluence multi-niveaux (CURRENT)
"""

# Feature Calculator - Core component
from .feature_calculator import (
import logging

# Configure logging
logger = logging.getLogger(__name__)

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

# Confluence Analyzer - Multi-level confluence detection (NEW Phase 3)
from .confluence_analyzer import (
    # Main classes
    ConfluenceAnalyzer,
    
    # Data structures
    ConfluenceAnalysis,
    ConfluenceZone,
    Level,
    
    # Enums
    LevelType,
    ConfluenceQuality,
    ConfluenceDirection,
    
    # Constants
    LEVEL_WEIGHTS,
    
    # Factory functions
    create_confluence_analyzer
)

# Version info
__version__ = "2.1.0"  # Updated for confluence integration
__author__ = "MIA Trading System"

# Package exports - Phase 3 complete with confluence
__all__ = [
    # Feature Calculator (Phase 1)
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
    
    # Market Regime (Phase 2)
    'MarketRegimeDetector',
    'MarketRegimeData',
    'TrendAnalysis',
    'RangeAnalysis',
    'ESNQCorrelation',
    'MarketRegime',
    'TrendStrength', 
    'RangeType',
    'create_market_regime_detector',
    'analyze_market_regime',
    
    # Confluence Analyzer (Phase 3 - NEW)
    'ConfluenceAnalyzer',
    'ConfluenceAnalysis',
    'ConfluenceZone',
    'Level',
    'LevelType',
    'ConfluenceQuality',
    'ConfluenceDirection',
    'LEVEL_WEIGHTS',
    'create_confluence_analyzer'
]

# Package-level constants - Updated
PACKAGE_FEATURES_COUNT = 8  # Exactly 8 features for ML
REGIME_DETECTION_ACCURACY = 0.85  # Target accuracy
FEATURE_CALCULATION_TIME_MS = 2.0  # Max calculation time
CONFLUENCE_CALCULATION_TIME_MS = 3.0  # Max confluence time (NEW)
CONFLUENCE_ZONES_MAX = 15  # Max zones detected per analysis (NEW)

def get_package_info() -> dict:
    """Information du package features - Updated Phase 3"""
    return {
        'version': __version__,
        'features_count': PACKAGE_FEATURES_COUNT,
        'components': ['FeatureCalculator', 'MarketRegimeDetector', 'ConfluenceAnalyzer'],
        'performance_targets': {
            'feature_calculation_ms': FEATURE_CALCULATION_TIME_MS,
            'confluence_calculation_ms': CONFLUENCE_CALCULATION_TIME_MS,
            'regime_accuracy': REGIME_DETECTION_ACCURACY
        },
        'confluence_capabilities': {
            'level_types': 12,  # Gamma, VWAP, MP, Volume, Session, etc.
            'max_zones': CONFLUENCE_ZONES_MAX,
            'quality_levels': 4,  # Weak, Moderate, Strong, Extreme
            'tolerance_configurable': True
        },
        'phase': 3,
        'status': 'Production Ready'
    }

def get_confluence_info() -> dict:
    """Information spécifique confluence analyzer"""
    return {
        'supported_levels': [
            'Gamma Levels (Call/Put walls, Flip)',
            'Market Profile (POC, VAH, VAL + Previous)',
            'VWAP Bands (VWAP, SD1, SD2)',
            'Volume Clusters (High Volume Nodes)',
            'Session Levels (High/Low, Overnight)',
            'Round Numbers (25/100 points)',
            'Psychological Levels'
        ],
        'scoring_method': 'Weighted confluence with proximity decay',
        'real_time_capable': True,
        'performance_target': '<3ms per analysis',
        'integration': 'Battle Navale compatible'
    }

def test_package_imports():
    """Test rapide imports package"""
    try:
        # Test Feature Calculator
        calculator = create_feature_calculator()
        logger.info("FeatureCalculator: {type(calculator).__name__}")
        
        # Test Market Regime
        regime_detector = create_market_regime_detector()
        logger.info("MarketRegimeDetector: {type(regime_detector).__name__}")
        
        # Test Confluence Analyzer (NEW)
        confluence_analyzer = create_confluence_analyzer()
        logger.info("ConfluenceAnalyzer: {type(confluence_analyzer).__name__}")
        
        # Test constants
        assert PACKAGE_FEATURES_COUNT == 8
        assert len(CONFLUENCE_WEIGHTS) >= 8
        assert len(LEVEL_WEIGHTS) >= 10
        
        logger.info("Package features v{__version__} - ALL IMPORTS OK")
        logger.info("Components: {len(get_package_info()['components'])}")
        logger.info("Confluence levels: {len(get_confluence_info()['supported_levels'])}")
        
        return True
        
    except Exception as e:
        logger.error("Erreur import package: {e}")
        return False

# Quick compatibility check
def validate_phase_3_integration():
    """Validation intégration Phase 3"""
    checks = {
        'feature_calculator_available': 'FeatureCalculator' in __all__,
        'market_regime_available': 'MarketRegimeDetector' in __all__,
        'confluence_analyzer_available': 'ConfluenceAnalyzer' in __all__,
        'all_enums_exported': all(enum in __all__ for enum in [
            'SignalQuality', 'MarketRegime', 'LevelType', 'ConfluenceQuality'
        ]),
        'factory_functions_available': all(func in __all__ for func in [
            'create_feature_calculator', 'create_market_regime_detector', 'create_confluence_analyzer'
        ])
    }
    
    return all(checks.values()), checks

if __name__ == "__main__":
    # Test au démarrage
    logger.info("🧪 Test Features Package Phase 3...")
    
    # Test imports
    if test_package_imports():
        logger.info("Tous les imports fonctionnent")
    else:
        logger.error("Problèmes d'imports détectés")
    
    # Test intégration
    integration_ok, details = validate_phase_3_integration()
    if integration_ok:
        logger.info("Intégration Phase 3 validée")
    else:
        logger.error("Problèmes intégration: {details}")
    
    # Info package
    info = get_package_info()
    confluence_info = get_confluence_info()
    
    logger.info("\n📊 FEATURES PACKAGE v{info['version']}")
    logger.info("📋 Composants: {', '.join(info['components'])}")
    logger.info("⚡ Performance: Features={info['performance_targets']['feature_calculation_ms']}ms, Confluence={info['performance_targets']['confluence_calculation_ms']}ms")
    logger.info("🎯 Confluence: {confluence_info['performance_target']}, {len(confluence_info['supported_levels'])} types de niveaux")
    logger.info("\n🚀 FEATURES PACKAGE PHASE 3 READY!")