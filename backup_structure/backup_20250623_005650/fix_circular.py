#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Fix Rapide Import Circulaire
Correction immédiate du problème deque causé par import circulaire
"""

import shutil
from pathlib import Path

def fix_circular_import_problem():
    """Correction rapide du problème d'import circulaire"""
    
    logger.info("🎯 FIX RAPIDE: Import Circulaire → deque error")
    print("="*55)
    
    # === 1. CORRIGER STRATEGY_SELECTOR.PY ===
    
    selector_path = Path("strategies/strategy_selector.py")
    
    if selector_path.exists():
        logger.info("🔧 Correction strategy_selector.py...")
        
        # Backup
        backup_path = Path("strategies/strategy_selector.py.backup_circular")
        shutil.copy2(selector_path, backup_path)
        
        # Lire et corriger
        with open(selector_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Corrections d'imports
        fixes = [
            ('from strategies.trend_strategy import', 'from .trend_strategy import'),
            ('from strategies.range_strategy import', 'from .range_strategy import'),
        ]
        
        for old, new in fixes:
            if old in content:
                content = content.replace(old, new)
                logger.info("   ✅ {old} → {new}")
        
        # Écrire version corrigée
        with open(selector_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("strategy_selector.py corrigé (backup: {backup_path})")
    
    # === 2. SIMPLIFIER __INIT__.PY ===
    
    logger.info("\n🔧 Simplification strategies/__init__.py...")
    
    init_path = Path("strategies/__init__.py")
    backup_init = Path("strategies/__init__.py.backup_simple")
    shutil.copy2(init_path, backup_init)
    
    # Nouveau contenu simplifié SANS import strategy_selector direct
    simple_content = '''"""
MIA_IA_SYSTEM - Strategies Package
Version: Import Circulaire Fixed - Simplifié
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

# Strategy imports DIRECTS - SANS STRATEGY_SELECTOR
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
    """Factory avec import LOCAL pour éviter cycle"""
    from .strategy_selector import StrategySelector
    return StrategySelector(config)

def create_strategy_orchestrator(config: Optional[Dict[str, Any]] = None):
    """Factory function orchestrateur"""
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
    """FONCTION PRINCIPALE avec imports locaux"""
    
    if orchestrator is None:
        orchestrator = create_strategy_selector()
    
    # Import LOCAL des classes pour éviter cycle
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

# Package exports SAFE - SANS strategy_selector classes directes
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
    
    # Factory functions CRITIQUES ✅
    'create_trend_strategy',        # ✅ SAFE
    'create_range_strategy',        # ✅ SAFE  
    'create_strategy_selector',     # ✅ SAFE (import local)
    'create_strategy_orchestrator', # ✅ SAFE
    
    # Analysis functions
    'analyze_trend_opportunity',
    'analyze_range_opportunity', 
    'analyze_market_regime',
    'analyze_complete_trading_opportunity',
    
    # Market regime
    'MarketRegimeDetector',
    'MarketRegimeData',
]

def get_package_info() -> dict:
    """Information du package"""
    return {
        'version': '2.0.3',
        'status': 'CIRCULAR_IMPORT_FIXED',
        'strategies_available': ['TrendStrategy', 'RangeStrategy'],
        'factory_functions': ['create_trend_strategy', 'create_range_strategy', 'create_strategy_selector'],
        'note': 'StrategySelector via factory function seulement'
    }
'''
    
    # Écrire version simplifiée
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(simple_content)
    
    logger.info("__init__.py simplifié (backup: {backup_init})")
    
    return True

def test_fix():
    """Test de la correction"""
    
    logger.info("\n🔍 TEST DE LA CORRECTION...")
    print("-" * 40)
    
    try:
        # Nettoyer cache
        import sys
        modules_to_clean = [k for k in sys.modules.keys() if k.startswith('strategies')]
        for mod in modules_to_clean:
            del sys.modules[mod]
        logger.info("🧹 Cache modules nettoyé")
        
        # Test import package
        import strategies
        logger.info("Package strategies importé")
        
        # Test factory functions
        from strategies import create_trend_strategy, create_range_strategy
        logger.info("Factory functions importées") 
        
        # Test instantiation (là où deque échouait)
        trend_strategy = create_trend_strategy()
        logger.info("create_trend_strategy() - SUCCESS!")
        
        range_strategy = create_range_strategy()
        logger.info("create_range_strategy() - SUCCESS!")
        
        # Test strategy selector
        from strategies import create_strategy_selector
        selector = create_strategy_selector()
        logger.info("create_strategy_selector() - SUCCESS!")
        
        return True
        
    except Exception as e:
        logger.error("Erreur: {e}")
        return False

def main():
    """Correction principale"""
    
    logger.info("🚨 PROBLÈME DÉTECTÉ: Import Circulaire")
    logger.info("📋 CYCLE:")
    logger.info("   strategies/__init__.py → strategy_selector")
    logger.info("   strategy_selector → strategies.trend_strategy")  
    logger.info("   strategies.trend_strategy → __init__.py → 💥")
    print()
    
    logger.info("🔧 SOLUTION: Imports relatifs + Factory functions")
    print()
    
    # Appliquer correction
    success = fix_circular_import_problem()
    
    if success:
        logger.info("\n🔍 TEST CORRECTION...")
        
        if test_fix():
            logger.info("\n🎉 PROBLÈME RÉSOLU!")
            logger.info("Import circulaire corrigé")
            logger.info("Erreur 'deque' résolue")
            logger.info("Toutes les factory functions fonctionnent")
            print()
            logger.info("🚀 RELANCEZ MAINTENANT:")
            logger.info("   python test_phase2_integration.py")
        else:
            logger.info("\n⚠️ Correction partielle")
            logger.info("💡 Problèmes persistants - investigation manuelle nécessaire")
    else:
        logger.info("\n❌ Échec correction automatique")

if __name__ == "__main__":
    main()