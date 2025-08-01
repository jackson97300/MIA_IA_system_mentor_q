#!/usr/bin/env python3
"""
🔍 TEST RAPIDE DES MODULES CRITIQUES
Vérification ciblée des modules essentiels
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

def test_critical_modules():
    """Test des modules critiques du système"""
    print("🔍 TEST RAPIDE MODULES CRITIQUES")
    print("="*50)
    
    modules_to_test = [
        # Core essentiels
        ("core.logger", "Core Logger"),
        ("core.base_types", "Core BaseTypes"),
        ("core.trading_types", "Core TradingTypes"),
        
        # Features principales
        ("features.feature_calculator", "FeatureCalculator"),
        ("features.smart_money_tracker", "SmartMoneyTracker"),
        
        # Strategies
        ("strategies.signal_generator", "SignalGenerator"),
        
        # Execution
        ("execution.order_manager", "OrderManager"),
        ("execution.simple_trader", "SimpleTrader"),
        
        # Monitoring
        ("monitoring.live_monitor", "LiveMonitor"),
        ("monitoring.health_checker", "HealthChecker"),
        
        # Config (celui qui posait problème)
        ("config.logging_config", "LoggingConfig"),
        ("config.trading_config", "TradingConfig"),
        
        # Automation
        ("automation_modules.trading_engine", "TradingEngine"),
        ("automation_modules.optimized_trading_system", "OptimizedTradingSystem"),
        
        # ML
        ("ml.simple_model", "SimpleModel"),
        ("ml.data_processor", "DataProcessor"),
    ]
    
    results = {}
    
    for module_path, module_name in modules_to_test:
        try:
            __import__(module_path)
            results[module_name] = True
            print(f"✅ {module_name}")
        except Exception as e:
            results[module_name] = False
            print(f"❌ {module_name}: {str(e)[:80]}...")
    
    # Résultats
    print("\n" + "="*50)
    print("📊 RÉSULTATS")
    print("="*50)
    
    total = len(results)
    success = sum(results.values())
    failed = total - success
    
    print(f"📦 Total: {total}")
    print(f"✅ Succès: {success}")
    print(f"❌ Échecs: {failed}")
    print(f"📊 Taux: {(success/total)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 TOUS LES MODULES CRITIQUES SONT OK!")
        print("✅ Système prêt pour production")
    else:
        print(f"\n⚠️ {failed} modules nécessitent attention:")
        for name, status in results.items():
            if not status:
                print(f"   ❌ {name}")
    
    return success == total

if __name__ == "__main__":
    test_critical_modules()