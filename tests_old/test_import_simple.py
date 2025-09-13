#!/usr/bin/env python3
"""
🧪 TEST D'IMPORT SIMPLE - AUTOMATION MODULES
===========================================

Test simple pour diagnostiquer les problèmes d'import des modules.
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

print("🔍 Test d'import des modules automation_modules...")
print("=" * 50)

# Test 1: Import du module principal
try:
    import automation_modules
    print("✅ Import automation_modules réussi")
except Exception as e:
    print(f"❌ Erreur import automation_modules: {e}")
    traceback.print_exc()

# Test 2: Import des classes principales
modules_to_test = [
    ("AutomationConfig", "config_manager"),
    ("EnhancedConfluenceCalculator", "confluence_calculator"),
    ("MIAAutomationSystem", "trading_engine"),
    ("RiskManager", "risk_manager"),
    ("PerformanceTracker", "performance_tracker"),
    ("OrderManager", "order_manager"),
    ("ValidationEngine", "validation_engine"),
    ("TradingExecutor", "trading_executor"),
    ("OptimizedTradingSystem", "optimized_trading_system"),
]

for class_name, module_name in modules_to_test:
    try:
        # Import direct du module
        module = __import__(f"execution.{module_name}", fromlist=[class_name])
        class_obj = getattr(module, class_name)
        print(f"✅ {class_name} ({module_name}) - OK")
    except Exception as e:
        print(f"❌ {class_name} ({module_name}) - Erreur: {e}")

# Test 3: Import des fonctions factory
factory_functions = [
    ("create_validation_engine", "validation_engine"),
    ("create_trading_executor", "trading_executor"),
]

for func_name, module_name in factory_functions:
    try:
        module = __import__(f"execution.{module_name}", fromlist=[func_name])
        func_obj = getattr(module, func_name)
        print(f"✅ {func_name} ({module_name}) - OK")
    except Exception as e:
        print(f"❌ {func_name} ({module_name}) - Erreur: {e}")

# Test 4: Import des enums Sierra
try:
    from execution.sierra_connector import OrderSide, OrderType, OrderStatus
    print("✅ Enums Sierra (OrderSide, OrderType, OrderStatus) - OK")
except Exception as e:
    print(f"❌ Enums Sierra - Erreur: {e}")

# Test 5: Import des fonctions Sierra
try:
    from config.sierra_config import create_optimized_sierra_config, create_trading_strategy_config
    print("✅ Fonctions Sierra config - OK")
except Exception as e:
    print(f"❌ Fonctions Sierra config - Erreur: {e}")

print("\n" + "=" * 50)
print("🏁 Test d'import terminé")



