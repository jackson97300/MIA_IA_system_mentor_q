#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test Imports Rapide
Validation imports strategies après correction
"""

import sys
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)


def test_critical_imports():
    """Test des imports critiques qui causaient l'erreur"""
    
    logger.debug("TESTING CRITICAL IMPORTS")
    print("="*40)
    
    errors = []
    
    # 1. Test import strategies package
    try:
        import strategies
        logger.info("strategies package imported")
    except ImportError as e:
        errors.append(f"strategies package: {e}")
        logger.error("strategies package: {e}")
    
    # 2. Test factory functions critiques
    critical_functions = [
        'create_trend_strategy',
        'create_range_strategy', 
        'create_strategy_selector'
    ]
    
    for func_name in critical_functions:
        try:
            from strategies import *
            func = globals().get(func_name)
            if func:
                logger.info("{func_name} imported successfully")
            else:
                errors.append(f"{func_name}: not found in globals")
                logger.error("{func_name}: not found in globals")
        except ImportError as e:
            errors.append(f"{func_name}: {e}")
            logger.error("{func_name}: {e}")
    
    # 3. Test import direct depuis le module
    try:
        from strategies import (
            StrategyOrchestrator, TrendStrategy, RangeStrategy,
            create_trend_strategy, create_range_strategy
        )
        logger.info("All main imports successful")
    except ImportError as e:
        errors.append(f"Main imports: {e}")
        logger.error("Main imports: {e}")
    
    # 4. Test __all__ exports
    try:
        import strategies
        all_exports = getattr(strategies, '__all__', [])
        logger.info("📋 __all__ exports count: {len(all_exports)}")
        
        missing_in_all = []
        for func in critical_functions:
            if func not in all_exports:
                missing_in_all.append(func)
        
        if missing_in_all:
            errors.append(f"Missing in __all__: {missing_in_all}")
            logger.error("Missing in __all__: {missing_in_all}")
        else:
            logger.info("All critical functions in __all__")
            
    except Exception as e:
        errors.append(f"__all__ check: {e}")
        logger.error("__all__ check: {e}")
    
    # 5. Test instantiation rapide
    try:
        from strategies import create_trend_strategy
        trend_strategy = create_trend_strategy()
        logger.info("create_trend_strategy() instantiation successful")
    except Exception as e:
        errors.append(f"Instantiation: {e}")
        logger.error("Instantiation: {e}")
    
    return len(errors) == 0, errors

def main():
    logger.info("🚀 MIA_IA_SYSTEM - Import Validation")
    print("="*50)
    
    # Nettoyer cache modules
    modules_to_clean = [k for k in sys.modules.keys() if k.startswith('strategies')]
    for mod in modules_to_clean:
        del sys.modules[mod]
    logger.info("🧹 Module cache cleaned")
    
    success, errors = test_critical_imports()
    
    logger.info("\n{'='*50}")
    if success:
        logger.info("🎉 TOUS LES IMPORTS RÉUSSIS!")
        logger.info("Vous pouvez relancer: python test_phase2_integration.py")
    else:
        logger.error("ERREURS DÉTECTÉES:")
        for error in errors:
            logger.info("   • {error}")
        logger.info("\n💡 SOLUTIONS POSSIBLES:")
        logger.info("1. Vérifier que strategies/__init__.py contient les factory functions")
        logger.info("2. Vérifier que create_trend_strategy est dans __all__")
        logger.info("3. Vérifier la syntaxe Python dans les fichiers strategies/")
    
    return success

if __name__ == "__main__":
    main()