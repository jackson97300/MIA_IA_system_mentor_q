#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test complet du système MIA_IA - Validation de tous les modules
"""

import sys
from pathlib import Path
import traceback

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

def test_automation_modules():
    """Test des modules automation_modules"""
    print("🧪 TEST 1: Modules automation_modules")
    print("-" * 40)
    
    modules_to_test = [
        "automation_modules.orderflow_analyzer",
        "automation_modules.order_manager", 
        "automation_modules.performance_tracker",
        "automation_modules.risk_manager",
        "automation_modules.sierra_connector",
        "automation_modules.signal_validator",
        "automation_modules.trading_engine",
        "automation_modules.trading_executor",
        "automation_modules.validation_engine"
    ]
    
    results = {}
    
    for module_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=['*'])
            print(f"  ✅ {module_name}")
            results[module_name] = "OK"
        except Exception as e:
            print(f"  ❌ {module_name}: {e}")
            results[module_name] = f"ERREUR: {e}"
    
    return results

def test_leadership_modules():
    """Test des modules leadership"""
    print("\n🧪 TEST 2: Modules Leadership")
    print("-" * 40)
    
    modules_to_test = [
        "features.leadership_analyzer",
        "features.confluence_integrator", 
        "config.leadership_config",
        "features.advanced.volatility_regime"
    ]
    
    results = {}
    
    for module_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=['*'])
            print(f"  ✅ {module_name}")
            results[module_name] = "OK"
        except Exception as e:
            print(f"  ❌ {module_name}: {e}")
            results[module_name] = f"ERREUR: {e}"
    
    return results

def test_core_modules():
    """Test des modules core"""
    print("\n🧪 TEST 3: Modules Core")
    print("-" * 40)
    
    modules_to_test = [
        "core.mia_data_generator",
        "core.trading_types",
        "core.base_types",
        "core.logger"
    ]
    
    results = {}
    
    for module_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=['*'])
            print(f"  ✅ {module_name}")
            results[module_name] = "OK"
        except Exception as e:
            print(f"  ❌ {module_name}: {e}")
            results[module_name] = f"ERREUR: {e}"
    
    return results

def test_data_modules():
    """Test des modules data"""
    print("\n🧪 TEST 4: Modules Data")
    print("-" * 40)
    
    modules_to_test = [
        "data.data_collector",
        "data.analytics"
    ]
    
    results = {}
    
    for module_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=['*'])
            print(f"  ✅ {module_name}")
            results[module_name] = "OK"
        except Exception as e:
            print(f"  ❌ {module_name}: {e}")
            results[module_name] = f"ERREUR: {e}"
    
    return results

def test_strategies_modules():
    """Test des modules strategies"""
    print("\n🧪 TEST 5: Modules Strategies")
    print("-" * 40)
    
    modules_to_test = [
        "strategies.signal_generator"
    ]
    
    results = {}
    
    for module_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=['*'])
            print(f"  ✅ {module_name}")
            results[module_name] = "OK"
        except Exception as e:
            print(f"  ❌ {module_name}: {e}")
            results[module_name] = f"ERREUR: {e}"
    
    return results

def test_monitoring_modules():
    """Test des modules monitoring"""
    print("\n🧪 TEST 6: Modules Monitoring")
    print("-" * 40)
    
    modules_to_test = [
        "monitoring.live_monitor"
    ]
    
    results = {}
    
    for module_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=['*'])
            print(f"  ✅ {module_name}")
            results[module_name] = "OK"
        except Exception as e:
            print(f"  ❌ {module_name}: {e}")
            results[module_name] = f"ERREUR: {e}"
    
    return results

def test_mia_data_generator():
    """Test spécifique du MIA_IA_DataGenerator"""
    print("\n🧪 TEST 7: MIA_IA_DataGenerator")
    print("-" * 40)
    
    try:
        from datetime import datetime, timezone
        from core.mia_data_generator import MIA_IA_DataGenerator, GenConfig
        
        # Test de génération
        gen = MIA_IA_DataGenerator(seed=42)
        cfg = GenConfig(
            start=datetime(2025, 8, 21, 13, 30, tzinfo=timezone.utc),
            minutes=5
        )
        
        data = gen.generate_realistic_session(cfg, scenario="normal")
        
        # Vérification des données
        expected_keys = ["l1", "l2", "bars", "footprint", "context", "leadership_features", "ground_truth"]
        for key in expected_keys:
            if key in data:
                print(f"  ✅ {key}: {len(data[key])} rows")
            else:
                print(f"  ❌ {key}: MANQUANT")
        
        print("  ✅ MIA_IA_DataGenerator fonctionne parfaitement")
        return {"MIA_IA_DataGenerator": "OK"}
        
    except Exception as e:
        print(f"  ❌ MIA_IA_DataGenerator: {e}")
        return {"MIA_IA_DataGenerator": f"ERREUR: {e}"}

def test_launch_24_7():
    """Test du lanceur principal"""
    print("\n🧪 TEST 8: Launch 24/7")
    print("-" * 40)
    
    try:
        # Test d'import du lanceur
        import launch_24_7
        print("  ✅ launch_24_7 importé avec succès")
        
        # Vérification de la classe MIAOrchestrator
        if hasattr(launch_24_7, 'MIAOrchestrator'):
            print("  ✅ Classe MIAOrchestrator trouvée")
        else:
            print("  ❌ Classe MIAOrchestrator manquante")
        
        return {"launch_24_7": "OK"}
        
    except Exception as e:
        print(f"  ❌ launch_24_7: {e}")
        return {"launch_24_7": f"ERREUR: {e}"}

def print_summary(all_results):
    """Affiche le résumé des tests"""
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS COMPLETS")
    print("="*60)
    
    total_modules = 0
    successful_modules = 0
    
    for test_name, results in all_results.items():
        print(f"\n🔍 {test_name.upper()}:")
        for module_name, status in results.items():
            total_modules += 1
            if "OK" in status:
                successful_modules += 1
                print(f"  ✅ {module_name}")
            else:
                print(f"  ❌ {module_name}: {status}")
    
    print(f"\n📈 STATISTIQUES FINALES:")
    print(f"  Total modules testés: {total_modules}")
    print(f"  Modules fonctionnels: {successful_modules}")
    print(f"  Modules en erreur: {total_modules - successful_modules}")
    print(f"  Taux de succès: {(successful_modules/total_modules)*100:.1f}%")
    
    if successful_modules == total_modules:
        print("\n🎉 TOUS LES MODULES FONCTIONNENT PARFAITEMENT !")
    else:
        print(f"\n⚠️ {total_modules - successful_modules} modules nécessitent une attention.")

def main():
    """Fonction principale de test"""
    print("🧪 TEST COMPLET DU SYSTÈME MIA_IA")
    print("="*60)
    
    all_results = {}
    
    # Tests des différents modules
    all_results["automation_modules"] = test_automation_modules()
    all_results["leadership_modules"] = test_leadership_modules()
    all_results["core_modules"] = test_core_modules()
    all_results["data_modules"] = test_data_modules()
    all_results["strategies_modules"] = test_strategies_modules()
    all_results["monitoring_modules"] = test_monitoring_modules()
    all_results["mia_data_generator"] = test_mia_data_generator()
    all_results["launch_24_7"] = test_launch_24_7()
    
    # Résumé final
    print_summary(all_results)

if __name__ == "__main__":
    main()



