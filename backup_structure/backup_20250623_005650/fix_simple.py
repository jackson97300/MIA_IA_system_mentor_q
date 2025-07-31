#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Fix Exports Simple
Correction simple et directe des exports manquants
"""

import shutil
from pathlib import Path

def create_simple_init():
    """Crée un __init__.py simple SANS __getattr__ compliqué"""
    
    logger.info("🔧 CRÉATION __init__.py SIMPLE ET DIRECT")
    print("="*50)
    
    init_path = Path("strategies/__init__.py")
    
    # Backup
    backup_path = Path("strategies/__init__.py.backup_simple2")
    shutil.copy2(init_path, backup_path)
    logger.info("Backup créé: {backup_path}")
    
    # Contenu simple et direct
    simple_content = '''"""
MIA_IA_SYSTEM - Strategies Package
Version: Simple Direct Exports
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging

# Local imports de base
from core.base_types import (
    MarketData, OrderFlowData, TradingSignal, SignalType,
    ES_TICK_SIZE
)
from features.feature_calculator import (
    FeatureCalculationResult, FeatureCalculator, SignalQuality
)

# Strategy imports DIRECTS - SANS PROBLÈME
from .trend_strategy import (
    TrendStrategy, TrendSignalData, TrendSignalType, 
    create_trend_strategy, analyze_trend_opportunity
)
from .range_strategy import (
    RangeStrategy, RangeSignalData, RangeSignalType, 
    create_range_strategy, analyze_range_opportunity
)

# Market regime
from features.market_regime import (
    MarketRegimeDetector, MarketRegimeData, MarketRegime as RegimeType,
    analyze_market_regime
)

logger = logging.getLogger(__name__)

# === FACTORY FUNCTIONS SAFE ===

def create_strategy_selector(config: Optional[Dict[str, Any]] = None):
    """Factory avec import LOCAL"""
    from .strategy_selector import StrategySelector
    return StrategySelector(config)

def create_strategy_orchestrator(config: Optional[Dict[str, Any]] = None):
    """Alias pour strategy_selector"""
    return create_strategy_selector(config)

def analyze_complete_trading_opportunity(
    market_data: MarketData,
    order_flow: Optional[OrderFlowData] = None,
    options_data: Optional[Dict[str, Any]] = None,
    structure_data: Optional[Dict[str, Any]] = None,
    es_nq_data: Optional[Dict[str, float]] = None,
    sierra_patterns: Optional[Dict[str, float]] = None,
    orchestrator = None
) -> Optional[Any]:
    """FONCTION PRINCIPALE"""
    
    if orchestrator is None:
        orchestrator = create_strategy_selector()
    
    # Import LOCAL des classes
    from .strategy_selector import TradingContext, ExecutionMode
    
    trading_context = TradingContext(
        timestamp=market_data.timestamp,
        market_data=market_data,
        es_nq_data=es_nq_data,
        structure_data=structure_data,
        sierra_patterns=sierra_patterns,
        execution_mode=ExecutionMode.PAPER_TRADING
    )
    
    return orchestrator.analyze_and_select(trading_context)

# === IMPORTS DIRECTS POUR LES CLASSES MANQUANTES ===
# Import direct mais paresseux pour éviter cycles

def get_strategy_selector_class():
    """Lazy import StrategySelector"""
    from .strategy_selector import StrategySelector
    return StrategySelector

def get_trading_context_class():
    """Lazy import TradingContext"""
    from .strategy_selector import TradingContext
    return TradingContext

def get_strategy_selection_result_class():
    """Lazy import StrategySelectionResult"""
    from .strategy_selector import StrategySelectionResult
    return StrategySelectionResult

def get_system_performance_class():
    """Lazy import SystemPerformance"""
    from .strategy_selector import SystemPerformance
    return SystemPerformance

def get_strategy_type_enum():
    """Lazy import StrategyType"""
    from .strategy_selector import StrategyType
    return StrategyType

def get_signal_decision_enum():
    """Lazy import SignalDecision"""
    from .strategy_selector import SignalDecision
    return SignalDecision

def get_execution_mode_enum():
    """Lazy import ExecutionMode"""
    from .strategy_selector import ExecutionMode
    return ExecutionMode

# Aliases directs pour compatibilité
StrategySelector = get_strategy_selector_class()
TradingContext = get_trading_context_class()
StrategySelectionResult = get_strategy_selection_result_class()
SystemPerformance = get_system_performance_class()
StrategyType = get_strategy_type_enum()
SignalDecision = get_signal_decision_enum()
ExecutionMode = get_execution_mode_enum()

# Alias pour StrategyOrchestrator 
StrategyOrchestrator = StrategySelector

# Package exports COMPLETS ET SIMPLES
__all__ = [
    # Core strategy classes
    'TrendStrategy',
    'RangeStrategy', 
    
    # Data classes
    'TrendSignalData',
    'RangeSignalData', 
    
    # Enums
    'TrendSignalType',
    'RangeSignalType',
    
    # Factory functions ✅
    'create_trend_strategy',        
    'create_range_strategy',        
    'create_strategy_selector',     
    'create_strategy_orchestrator', 
    
    # Analysis functions
    'analyze_trend_opportunity',
    'analyze_range_opportunity', 
    'analyze_market_regime',
    'analyze_complete_trading_opportunity',
    
    # Market regime
    'MarketRegimeDetector',
    'MarketRegimeData',
    
    # Strategy Selector classes ✅ TOUS DISPONIBLES
    'StrategySelector',
    'StrategySelectionResult', 
    'TradingContext',           # ✅ CRITIQUE POUR TEST
    'SystemPerformance',
    'StrategyType',
    'SignalDecision', 
    'ExecutionMode',
    'StrategyOrchestrator',     # ✅ ALIAS
]

def get_package_info() -> dict:
    """Information du package"""
    return {
        'version': '2.0.5',
        'status': 'SIMPLE_DIRECT_EXPORTS',
        'exports_count': len(__all__),
        'approach': 'lazy_imports'
    }
'''
    
    # Écrire version simple
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(simple_content)
    
    logger.info("__init__.py simple créé")
    return True

def test_simple_imports():
    """Test imports simples"""
    
    logger.info("\n🔍 TEST IMPORTS SIMPLES")
    print("="*35)
    
    try:
        # Nettoyer cache
        import sys
        modules_to_clean = [k for k in sys.modules.keys() if k.startswith('strategies')]
        for mod in modules_to_clean:
            del sys.modules[mod]
        logger.info("🧹 Cache nettoyé")
        
        # Test 1: Factory functions (déjà marche)
        from strategies import create_trend_strategy, create_range_strategy
        logger.info("Factory functions OK")
        
        # Test 2: TradingContext (le problème)
        from strategies import TradingContext
        logger.info("TradingContext OK")
        
        # Test 3: StrategyOrchestrator
        from strategies import StrategyOrchestrator
        logger.info("StrategyOrchestrator OK")
        
        # Test 4: Tous les imports du test
        from strategies import (
            StrategyOrchestrator, TrendStrategy, RangeStrategy,
            create_trend_strategy, create_range_strategy
        )
        logger.info("Tous les imports du test OK")
        
        # Test 5: Instantiation
        strategy = create_trend_strategy()
        logger.info("Instantiation OK")
        
        return True
        
    except Exception as e:
        logger.error("Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Correction simple et directe"""
    
    logger.info("🎯 FIX SIMPLE: Exports directs sans __getattr__ compliqué")
    print("="*65)
    
    # Créer version simple
    create_simple_init()
    
    # Tester
    if test_simple_imports():
        logger.info("\n🎉 APPROCHE SIMPLE RÉUSSIE!")
        logger.info("Tous les exports disponibles")
        logger.info("TradingContext importable")
        logger.info("Pas de cycles d'imports")
        print()
        logger.info("🚀 RELANCEZ:")
        logger.info("   python test_phase2_integration.py")
    else:
        logger.info("\n⚠️ Problèmes persistants même avec approche simple")

if __name__ == "__main__":
    main()