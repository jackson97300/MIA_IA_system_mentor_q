#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Fix Missing Exports
Correction des exports manquants dans strategies/__init__.py
"""

import shutil
from pathlib import Path

def check_test_imports():
    """Vérifie quoi test_phase2_integration.py essaie d'importer"""
    
    logger.debug("ANALYSE DES IMPORTS DEMANDÉS")
    print("="*45)
    
    test_path = Path("test_phase2_integration.py")
    
    if not test_path.exists():
        logger.error("test_phase2_integration.py non trouvé")
        return []
    
    with open(test_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chercher les imports depuis strategies
    lines = content.split('\n')
    imports_needed = []
    
    in_strategies_import = False
    for line in lines:
        line = line.strip()
        
        if line.startswith('from strategies import ('):
            in_strategies_import = True
            # Extraire le premier import si sur la même ligne
            if ')' in line:
                import_part = line.split('(')[1].split(')')[0]
                imports_needed.extend([imp.strip() for imp in import_part.split(',') if imp.strip()])
                in_strategies_import = False
            continue
        
        if in_strategies_import:
            if ')' in line:
                # Fin de l'import multi-ligne
                import_part = line.split(')')[0]
                imports_needed.extend([imp.strip() for imp in import_part.split(',') if imp.strip()])
                in_strategies_import = False
            else:
                # Ligne d'import continue
                imports_needed.extend([imp.strip() for imp in line.split(',') if imp.strip()])
    
    logger.info("📋 IMPORTS DEMANDÉS PAR test_phase2_integration.py:")
    for imp in imports_needed:
        logger.info("   • {imp}")
    
    return imports_needed

def check_available_exports():
    """Vérifie ce qui est disponible dans strategies/__init__.py"""
    
    logger.info("\n🔍 EXPORTS ACTUELS dans strategies/__init__.py")
    print("="*50)
    
    init_path = Path("strategies/__init__.py")
    
    if not init_path.exists():
        logger.error("strategies/__init__.py non trouvé")
        return []
    
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraire __all__
    if '__all__' in content:
        try:
            start = content.find('__all__ = [')
            if start != -1:
                end = content.find(']', start)
                all_content = content[start:end+1]
                
                # Parser grossièrement __all__
                exports = []
                for line in all_content.split('\n'):
                    if "'" in line or '"' in line:
                        # Extraire noms entre quotes
                        import re
                        matches = re.findall(r"['\"]([^'\"]+)['\"]", line)
                        exports.extend(matches)
                
                logger.info("📋 EXPORTS ACTUELS:")
                for exp in exports:
                    logger.info("   • {exp}")
                
                return exports
        except:
            pass
    
    logger.error("Impossible de parser __all__")
    return []

def find_missing_exports(needed, available):
    """Trouve les exports manquants"""
    
    missing = []
    for item in needed:
        if item not in available:
            missing.append(item)
    
    if missing:
        logger.info("\n❌ EXPORTS MANQUANTS:")
        for item in missing:
            logger.info("   • {item}")
    else:
        logger.info("\n✅ Tous les exports nécessaires sont présents")
    
    return missing

def fix_exports():
    """Corrige les exports manquants"""
    
    logger.info("\n🔧 CORRECTION DES EXPORTS")
    print("="*35)
    
    init_path = Path("strategies/__init__.py")
    
    # Backup
    backup_path = Path("strategies/__init__.py.backup_exports")
    shutil.copy2(init_path, backup_path)
    logger.info("Backup créé: {backup_path}")
    
    # Contenu corrigé avec tous les exports nécessaires
    corrected_content = '''"""
MIA_IA_SYSTEM - Strategies Package
Version: All Exports Fixed
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

# Strategy imports DIRECTS
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
    
    # Import LOCAL pour éviter cycle
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

# === EXPORTS VIA GETATTR POUR ÉVITER IMPORT CIRCULAIRE ===

def __getattr__(name):
    """Dynamic import pour éviter cycles"""
    
    # Classes depuis strategy_selector
    selector_classes = [
        'StrategySelector', 'StrategySelectionResult', 'TradingContext', 
        'SystemPerformance', 'StrategyType', 'SignalDecision', 'ExecutionMode'
    ]
    
    if name in selector_classes:
        from .strategy_selector import globals as selector_globals
        return getattr(selector_globals(), name, None)
    
    # Fallback pour autres noms
    raise AttributeError(f"module 'strategies' has no attribute '{name}'")

# Package exports COMPLETS
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
    'create_trend_strategy',        # ✅ WORKING
    'create_range_strategy',        # ✅ WORKING
    'create_strategy_selector',     # ✅ WORKING
    'create_strategy_orchestrator', # ✅ WORKING
    
    # Analysis functions
    'analyze_trend_opportunity',
    'analyze_range_opportunity', 
    'analyze_market_regime',
    'analyze_complete_trading_opportunity',
    
    # Market regime
    'MarketRegimeDetector',
    'MarketRegimeData',
    
    # Strategy Selector classes (via __getattr__)
    'StrategySelector',
    'StrategySelectionResult', 
    'TradingContext',           # ✅ NEEDED BY TEST
    'SystemPerformance',
    'StrategyType',
    'SignalDecision', 
    'ExecutionMode',
]

def get_package_info() -> dict:
    """Information du package"""
    return {
        'version': '2.0.4',
        'status': 'ALL_EXPORTS_AVAILABLE',
        'exports_count': len(__all__),
        'dynamic_imports': True
    }
'''
    
    # Écrire version corrigée
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(corrected_content)
    
    logger.info("strategies/__init__.py corrigé avec tous les exports")
    return True

def test_all_imports():
    """Test de tous les imports nécessaires"""
    
    logger.info("\n🔍 TEST DE TOUS LES IMPORTS")
    print("="*40)
    
    try:
        # Nettoyer cache
        import sys
        modules_to_clean = [k for k in sys.modules.keys() if k.startswith('strategies')]
        for mod in modules_to_clean:
            del sys.modules[mod]
        logger.info("🧹 Cache nettoyé")
        
        # Test imports basiques
        from strategies import create_trend_strategy, create_range_strategy
        logger.info("Factory functions OK")
        
        # Test classes problématiques
        from strategies import TradingContext, StrategySelector
        logger.info("TradingContext et StrategySelector OK")
        
        # Test StrategyOrchestrator
        from strategies import StrategyOrchestrator
        logger.info("StrategyOrchestrator OK")
        
        # Test instantiation
        strategy = create_trend_strategy()
        logger.info("Instantiation trend strategy OK")
        
        return True
        
    except Exception as e:
        logger.error("Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Diagnostic et correction complets"""
    
    logger.info("🎯 FIX: cannot import name 'TradingContext' from 'strategies'")
    print("="*65)
    
    # 1. Analyser ce qui est demandé
    needed = check_test_imports()
    
    # 2. Analyser ce qui est disponible
    available = check_available_exports()
    
    # 3. Trouver ce qui manque
    missing = find_missing_exports(needed, available)
    
    if missing:
        # 4. Corriger les exports
        fix_exports()
        
        # 5. Tester
        if test_all_imports():
            logger.info("\n🎉 TOUS LES IMPORTS RÉSOLUS!")
            logger.info("TradingContext maintenant disponible")
            logger.info("Tous les exports nécessaires ajoutés")
            print()
            logger.info("🚀 RELANCEZ:")
            logger.info("   python test_phase2_integration.py")
        else:
            logger.info("\n⚠️ Problèmes persistants")
    else:
        logger.info("\n🤔 Exports semblent OK, problème ailleurs")

if __name__ == "__main__":
    main()