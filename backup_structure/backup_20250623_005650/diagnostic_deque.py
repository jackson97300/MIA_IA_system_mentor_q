#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Diagnostic Précision Deque
Trouvez EXACTEMENT quel fichier cause name 'deque' is not defined
"""

import sys
import traceback
import importlib
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)


def diagnostic_step_by_step():
    """Diagnostic étape par étape pour isoler le problème"""
    
    logger.debug("DIAGNOSTIC PRÉCISION: name 'deque' is not defined")
    print("="*60)
    
    # Nettoyer cache modules
    logger.info("🧹 Nettoyage cache modules...")
    modules_to_clean = [k for k in sys.modules.keys() 
                       if any(part in k for part in ['strategies', 'features', 'core'])]
    for mod in modules_to_clean:
        del sys.modules[mod]
    logger.info("   Supprimé {len(modules_to_clean)} modules du cache")
    
    # Test 1: Import core.base_types
    logger.info("\n📋 ÉTAPE 1: Test core.base_types")
    try:
        from core.base_types import MarketData
        logger.info("   ✅ core.base_types OK")
    except Exception as e:
        logger.info("   ❌ core.base_types: {e}")
        return False
    
    # Test 2: Import features
    logger.info("\n📋 ÉTAPE 2: Test features")
    try:
        from features.feature_calculator import FeatureCalculator
        logger.info("   ✅ features.feature_calculator OK")
    except Exception as e:
        logger.info("   ❌ features.feature_calculator: {e}")
        logger.info("   📊 Stack trace:")
        traceback.print_exc()
        return False
    
    # Test 3: Import trend_strategy SEUL
    logger.info("\n📋 ÉTAPE 3: Test trend_strategy ISOLÉ")
    try:
        from strategies.trend_strategy import TrendStrategy
        logger.info("   ✅ strategies.trend_strategy OK")
    except Exception as e:
        logger.info("   ❌ strategies.trend_strategy: {e}")
        logger.info("   📊 Stack trace:")
        traceback.print_exc()
        return False
    
    # Test 4: Import range_strategy SEUL  
    logger.info("\n📋 ÉTAPE 4: Test range_strategy ISOLÉ")
    try:
        from strategies.range_strategy import RangeStrategy
        logger.info("   ✅ strategies.range_strategy OK")
    except Exception as e:
        logger.info("   ❌ strategies.range_strategy: {e}")
        logger.info("   📊 Stack trace:")
        traceback.print_exc()
        return False
    
    # Test 5: Import strategy_selector SEUL
    logger.info("\n📋 ÉTAPE 5: Test strategy_selector ISOLÉ")
    try:
        from strategies.strategy_selector import StrategySelector
        logger.info("   ✅ strategies.strategy_selector OK")
    except Exception as e:
        logger.info("   ❌ strategies.strategy_selector: {e}")
        logger.info("   📊 Stack trace complète:")
        traceback.print_exc()
        return False
    
    # Test 6: Factory functions
    logger.info("\n📋 ÉTAPE 6: Test factory functions")
    try:
        from strategies.trend_strategy import create_trend_strategy
        logger.info("   ✅ create_trend_strategy import OK")
        
        # Test instantiation
        strategy = create_trend_strategy()
        logger.info("   ✅ create_trend_strategy() instantiation OK")
    except Exception as e:
        logger.info("   ❌ create_trend_strategy: {e}")
        logger.info("   📊 Stack trace:")
        traceback.print_exc()
        return False
    
    try:
        from strategies.range_strategy import create_range_strategy
        strategy = create_range_strategy()
        logger.info("   ✅ create_range_strategy() OK")
    except Exception as e:
        logger.info("   ❌ create_range_strategy: {e}")
        logger.info("   📊 Stack trace:")
        traceback.print_exc()
        return False
    
    logger.info("\n✅ TOUS LES TESTS PASSÉS!")
    return True

def check_deque_imports():
    """Vérification exhaustive des imports deque dans tous les fichiers"""
    
    logger.info("\n🔍 VÉRIFICATION IMPORTS DEQUE")
    print("="*40)
    
    files_to_check = [
        "strategies/trend_strategy.py",
        "strategies/range_strategy.py", 
        "strategies/strategy_selector.py",
        "features/feature_calculator.py",
        "features/market_regime.py",
        "core/battle_navale.py"
    ]
    
    for file_path in files_to_check:
        if Path(file_path).exists():
            logger.info("\n📄 {file_path}:")
            check_file_deque_usage(file_path)
        else:
            logger.info("\n❌ {file_path}: MANQUANT")

def check_file_deque_usage(file_path):
    """Vérifie l'usage de deque dans un fichier spécifique"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Chercher import deque
        has_deque_import = False
        deque_usage_lines = []
        
        for i, line in enumerate(lines, 1):
            if 'from collections import deque' in line:
                logger.info("   ✅ Import deque ligne {i}: {line.strip()}")
                has_deque_import = True
            elif 'import deque' in line:
                logger.info("   ✅ Import deque ligne {i}: {line.strip()}")
                has_deque_import = True
            elif 'deque(' in line or 'deque[' in line or ': deque' in line:
                deque_usage_lines.append((i, line.strip()))
        
        if deque_usage_lines:
            logger.info("   📊 Usage deque trouvé:")
            for line_num, line in deque_usage_lines:
                logger.info("      Ligne {line_num}: {line}")
            
            if not has_deque_import:
                logger.info("   ❌ PROBLÈME: Usage deque SANS import!")
                return False
        
        if has_deque_import or deque_usage_lines:
            logger.info("   ✅ Imports deque cohérents")
        else:
            logger.info("   ℹ️ Pas d'usage deque")
            
        return True
        
    except Exception as e:
        logger.info("   ❌ Erreur lecture: {e}")
        return False

def trace_import_error():
    """Trace précisément où l'erreur deque se produit"""
    
    logger.info("\n🎯 TRACE PRÉCISE DE L'ERREUR")
    print("="*45)
    
    try:
        # Import progressif avec traces
        logger.info("1. Import strategies package...")
        import strategies
        logger.info("   ✅ Package importé")
        
        logger.info("2. Access create_trend_strategy...")
        create_func = getattr(strategies, 'create_trend_strategy', None)
        if create_func:
            logger.info("   ✅ Fonction trouvée")
        else:
            logger.info("   ❌ Fonction non trouvée")
            return
        
        logger.info("3. Appel create_trend_strategy()...")
        result = create_func()
        logger.info("   ✅ Instanciation réussie")
        
    except Exception as e:
        logger.info("   ❌ ERREUR CAPTURÉE: {e}")
        logger.info("\n📊 STACK TRACE COMPLÈTE:")
        traceback.print_exc()
        
        # Analyser la stack trace
        logger.info("\n🔍 ANALYSE STACK TRACE:")
        tb = traceback.format_exc()
        lines = tb.split('\n')
        
        for line in lines:
            if 'deque' in line and 'not defined' in line:
                logger.info("   🎯 LIGNE PROBLÈME: {line}")
            elif '.py' in line and ('strategies' in line or 'features' in line or 'core' in line):
                logger.info("   📄 Fichier impliqué: {line.strip()}")

def create_minimal_test_files():
    """Crée des fichiers de test minimaux pour isoler le problème"""
    
    logger.info("\n🔧 CRÉATION FICHIERS TEST MINIMAUX")
    print("="*45)
    
    # Test trend_strategy minimal
    minimal_trend = '''"""Test minimal trend_strategy"""
from collections import deque
import pandas as pd
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class TrendStrategy:
    def __init__(self, config=None):
        self.history = deque(maxlen=10)
        
def create_trend_strategy(config=None):
    return TrendStrategy(config)
'''
    
    test_path = Path("test_trend_minimal.py")
    with open(test_path, 'w') as f:
        f.write(minimal_trend)
    
    logger.info("Créé: {test_path}")
    
    # Test ce fichier minimal
    try:
        import test_trend_minimal
        strategy = test_trend_minimal.create_trend_strategy()
        logger.info("Test minimal RÉUSSI - Le problème n'est PAS dans deque basique")
        
        # Nettoyer
        test_path.unlink()
        del sys.modules['test_trend_minimal']
        
    except Exception as e:
        logger.error("Test minimal ÉCHOUÉ: {e}")
        traceback.print_exc()

def diagnostic_imports_dependency():
    """Diagnostic des dépendances d'imports problématiques"""
    
    logger.info("\n🔗 DIAGNOSTIC DÉPENDANCES IMPORTS")
    print("="*45)
    
    # Tester chaque import séparément
    dependencies = [
        ("pandas", "import pandas as pd"),
        ("numpy", "import numpy as np"), 
        ("collections.deque", "from collections import deque"),
        ("typing", "from typing import Dict, List, Optional"),
        ("dataclasses", "from dataclasses import dataclass"),
        ("enum", "from enum import Enum"),
    ]
    
    for name, import_stmt in dependencies:
        try:
            exec(import_stmt)
            logger.info("   ✅ {name}")
        except Exception as e:
            logger.info("   ❌ {name}: {e}")

def main():
    """Diagnostic complet"""
    
    logger.info("🚨 DIAGNOSTIC APPROFONDI: name 'deque' is not defined")
    logger.info("🎯 OBJECTIF: Trouver LE fichier responsable")
    print()
    
    # 1. Test dépendances de base
    diagnostic_imports_dependency()
    
    # 2. Test fichier minimal
    create_minimal_test_files()
    
    # 3. Vérifier tous les imports deque
    check_deque_imports()
    
    # 4. Test étape par étape
    if not diagnostic_step_by_step():
        logger.info("\n❌ PROBLÈME TROUVÉ dans le test étape par étape")
    
    # 5. Trace précise de l'erreur
    trace_import_error()
    
    logger.info("\n🎯 DIAGNOSTIC TERMINÉ")
    logger.info("📋 Si l'erreur persiste, vérifiez la stack trace ci-dessus")

if __name__ == "__main__":
    main()