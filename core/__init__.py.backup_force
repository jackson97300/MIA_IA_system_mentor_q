"""
MIA_IA_SYSTEM - Core Package
Exports sécurisés sans imports circulaires
Version: Production Ready - CORRIGÉ

CORRECTIONS APPLIQUÉES:
- Import de StructureData rendu optionnel et sécurisé
- Lazy loading pour éviter les dépendances circulaires
- Logging approprié au lieu de print()
- Protection contre les erreurs d'import
"""

import logging
import sys

if sys.platform == "win32":

# Configure logging
logger = logging.getLogger(__name__)

# === IMPORTS NIVEAU 0 (aucune dépendance locale) ===

# Import base types first (no local dependencies)
from .base_types import (
    # Core data structures
    MarketData,
    OrderFlowData,
    TradingFeatures,
    TradingSignal,
    TradeResult,
    
    # Enums
    MarketRegime,
    SignalType,
    PatternType,
    SignalStrength,
    SessionPhase,
    TradingDecision,
    MarketState,
    SystemState,
    
    # Metrics
    SystemMetrics,
    PerformanceReport,
    
    # Exceptions
    ConfigError,
    
    # Constants
    ES_TICK_SIZE,
    ES_TICK_VALUE,
    MES_TICK_VALUE,
    TRADING_HOURS,
    DEFAULT_RISK_PARAMS,
    PERFORMANCE_TARGETS,
    
    # Utility functions
    get_session_phase,
    validate_market_data,
    calculate_performance_metrics
)

# === LAZY LOADING POUR MODULES AVEC DÉPENDANCES ===

# Variables pour lazy loading
_structure_data_module = None
_battle_navale_module = None
_patterns_detector_module = None
_ibkr_connector_module = None
_sierra_connector_module = None

def get_structure_data():
    """Lazy loading de StructureData pour éviter imports circulaires"""
    global _structure_data_module
    if _structure_data_module is None:
        try:
            from . import structure_data as _structure_data_module
        except ImportError as e:
            logger.error(f"Impossible d'importer structure_data: {e}")
            return None
    return _structure_data_module

def get_battle_navale():
    """Lazy loading de BattleNavale"""
    global _battle_navale_module
    if _battle_navale_module is None:
        try:
            from . import battle_navale as _battle_navale_module
        except ImportError as e:
            logger.error(f"Impossible d'importer battle_navale: {e}")
            return None
    return _battle_navale_module

def get_patterns_detector():
    """Lazy loading de PatternsDetector"""
    global _patterns_detector_module
    if _patterns_detector_module is None:
        try:
            from . import patterns_detector as _patterns_detector_module
        except ImportError as e:
            logger.error(f"Impossible d'importer patterns_detector: {e}")
            return None
    return _patterns_detector_module

def get_ibkr_connector():
    """Lazy loading de IBKRConnector"""
    global _ibkr_connector_module
    if _ibkr_connector_module is None:
        try:
            from . import ibkr_connector as _ibkr_connector_module
        except ImportError as e:
            logger.error(f"Impossible d'importer ibkr_connector: {e}")
            return None
    return _ibkr_connector_module

def get_sierra_connector():
    """Lazy loading de SierraConnector"""
    global _sierra_connector_module
    if _sierra_connector_module is None:
        try:
            from . import sierra_connector as _sierra_connector_module
        except ImportError as e:
            logger.error(f"Impossible d'importer sierra_connector: {e}")
            return None
    return _sierra_connector_module

# === FACTORY FUNCTIONS POUR CRÉATION SÉCURISÉE ===

def create_structure_data(**kwargs):
    """Factory pour créer StructureData de manière sécurisée"""
    module = get_structure_data()
    if module and hasattr(module, 'create_structure_data'):
        return module.create_structure_data(**kwargs)
    else:
        logger.error("create_structure_data non disponible")
        return None

def create_battle_navale_analyzer(**kwargs):
    """Factory pour créer BattleNavaleAnalyzer"""
    module = get_battle_navale()
    if module and hasattr(module, 'BattleNavaleAnalyzer'):
        return module.BattleNavaleAnalyzer(**kwargs)
    else:
        logger.error("BattleNavaleAnalyzer non disponible")
        return None

def create_patterns_detector(**kwargs):
    """Factory pour créer PatternsDetector"""
    module = get_patterns_detector()
    if module and hasattr(module, 'PatternsDetector'):
        return module.PatternsDetector(**kwargs)
    else:
        logger.error("PatternsDetector non disponible")
        return None

def create_ibkr_connector(**kwargs):
    """Factory pour créer IBKRConnector"""
    module = get_ibkr_connector()
    if module and hasattr(module, 'IBKRConnector'):
        return module.IBKRConnector(**kwargs)
    else:
        logger.error("IBKRConnector non disponible")
        return None

def create_sierra_connector(**kwargs):
    """Factory pour créer SierraConnector"""
    module = get_sierra_connector()
    if module and hasattr(module, 'SierraConnector'):
        return module.SierraConnector(**kwargs)
    else:
        logger.error("SierraConnector non disponible")
        return None

# === EXPORTS PRINCIPAUX ===

# Exports de base (toujours disponibles)
__all__ = [
    # Types de base
    'MarketData',
    'OrderFlowData', 
    'TradingFeatures',
    'TradingSignal',
    'TradeResult',
    
    # Enums
    'MarketRegime',
    'SignalType',
    'PatternType',
    'SignalStrength',
    'SessionPhase',
    'TradingDecision',
    'MarketState',
    'SystemState',
    
    # Metrics
    'SystemMetrics',
    'PerformanceReport',
    
    # Exceptions
    'ConfigError',
    
    # Constants
    'ES_TICK_SIZE',
    'ES_TICK_VALUE',
    'MES_TICK_VALUE',
    'TRADING_HOURS',
    'DEFAULT_RISK_PARAMS',
    'PERFORMANCE_TARGETS',
    
    # Utility functions
    'get_session_phase',
    'validate_market_data',
    'calculate_performance_metrics',
    
    # Lazy loading functions
    'get_structure_data',
    'get_battle_navale',
    'get_patterns_detector',
    'get_ibkr_connector',
    'get_sierra_connector',
    
    # Factory functions
    'create_structure_data',
    'create_battle_navale_analyzer',
    'create_patterns_detector',
    'create_ibkr_connector',
    'create_sierra_connector'
]

# === VERSION INFO ===

__version__ = "3.0.0"
__author__ = "MIA Trading System"

# === VALIDATION IMPORTS ===

def test_core_imports():
    """Test que tous les imports core fonctionnent"""
    logger.info("Test imports core...")
    
    results = {
        'base_types': True,  # Toujours True car importé directement
        'structure_data': False,
        'battle_navale': False,
        'patterns_detector': False,
        'ibkr_connector': False,
        'sierra_connector': False
    }
    
    # Test lazy loading
    if get_structure_data():
        results['structure_data'] = True
    
    if get_battle_navale():
        results['battle_navale'] = True
        
    if get_patterns_detector():
        results['patterns_detector'] = True
        
    if get_ibkr_connector():
        results['ibkr_connector'] = True
        
    if get_sierra_connector():
        results['sierra_connector'] = True
    
    # Rapport
    total = len(results)
    success = sum(results.values())
    
    logger.info(f"Imports core: {success}/{total} réussis")
    
    for module, status in results.items():
        status_str = "✅" if status else "❌"
        logger.info(f"  {status_str} {module}")
    
    return success == total

# Test au chargement si en mode debug
if __name__ == "__main__":
    test_core_imports()