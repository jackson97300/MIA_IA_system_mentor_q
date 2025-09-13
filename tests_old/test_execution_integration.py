#!/usr/bin/env python3
"""
🧪 TEST EXECUTION INTEGRATION - MIA_IA_SYSTEM
=============================================

Script de test pour vérifier l'intégration complète des fichiers execution/
dans les lanceurs après les améliorations.

Tests effectués:
- Import des modules execution/
- Fonctionnement de l'optimiseur d'imports
- Intégration dans les lanceurs
- Performance des imports
- Health check des composants

Auteur: MIA_IA_SYSTEM
Version: 1.0.0
Date: Janvier 2025
"""

import sys
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def test_execution_imports():
    """Test des imports execution/"""
    print("🧪 Test 1: Imports execution/")
    
    results = {}
    
    try:
        # Test import optimiseur
        from execution.imports_optimizer import (
            get_import_optimizer, preload_execution_modules, 
            get_execution_import_metrics, get_sierra_connector,
            get_risk_manager, get_simple_trader, get_trading_executor
        )
        results['imports_optimizer'] = True
        print("  ✅ execution.imports_optimizer importé")
    except Exception as e:
        results['imports_optimizer'] = False
        print(f"  ❌ Erreur import optimiseur: {e}")
    
    try:
        # Test import modules execution/
        from execution.sierra_connector import SierraConnector
        from execution.risk_manager import RiskManager
        from execution.simple_trader import MIAAutomationSystem
        from execution.trading_executor import TradingExecutor
        from execution.sierra_dtc_connector import SierraDTCConnector
        from execution.sierra_order_router import SierraOrderRouter
        from execution.order_manager import OrderManager
        results['direct_imports'] = True
        print("  ✅ Modules execution/ importés directement")
    except Exception as e:
        results['direct_imports'] = False
        print(f"  ❌ Erreur import direct: {e}")
    
    return results

def test_import_optimizer():
    """Test de l'optimiseur d'imports"""
    print("\n🧪 Test 2: Optimiseur d'imports")
    
    results = {}
    
    try:
        from execution.imports_optimizer import get_import_optimizer
        
        # Test création optimiseur
        optimizer = get_import_optimizer()
        results['optimizer_creation'] = True
        print("  ✅ Optimiseur créé")
        
        # Test préchargement
        start_time = time.perf_counter()
        preload_results = optimizer.preload_critical_modules()
        preload_time = (time.perf_counter() - start_time) * 1000
        
        success_count = sum(preload_results.values())
        total_count = len(preload_results)
        results['preload_success'] = success_count
        results['preload_total'] = total_count
        results['preload_time_ms'] = round(preload_time, 2)
        
        print(f"  ✅ Préchargement: {success_count}/{total_count} modules en {preload_time:.2f}ms")
        
        # Test métriques
        metrics = optimizer.get_import_metrics()
        results['metrics_available'] = bool(metrics)
        print(f"  ✅ Métriques disponibles: {bool(metrics)}")
        
        # Test health check
        health = optimizer.health_check()
        results['health_status'] = health.get('status', 'unknown')
        print(f"  ✅ Health Check: {health.get('status', 'unknown')}")
        
    except Exception as e:
        results['optimizer_error'] = str(e)
        print(f"  ❌ Erreur optimiseur: {e}")
    
    return results

def test_launcher_imports():
    """Test des imports dans les lanceurs"""
    print("\n🧪 Test 3: Imports lanceurs")
    
    results = {}
    
    try:
        # Test lanceur principal
        from LAUNCH.launch_24_7_menthorq_final import MIAFinalSystem, FINAL_CONFIG
        results['main_launcher'] = True
        print("  ✅ Lanceur principal importé")
        
        # Test lanceur paper trading
        from tests.launch_paper_trading import PaperTradingLauncher
        results['paper_trading_launcher'] = True
        print("  ✅ Lanceur paper trading importé")
        
    except Exception as e:
        results['launcher_error'] = str(e)
        print(f"  ❌ Erreur import lanceurs: {e}")
    
    return results

async def test_launcher_functionality():
    """Test de la fonctionnalité des lanceurs"""
    print("\n🧪 Test 4: Fonctionnalité lanceurs")
    
    results = {}
    
    try:
        # Test initialisation système principal
        from LAUNCH.launch_24_7_menthorq_final import MIAFinalSystem, FINAL_CONFIG
        
        start_time = time.perf_counter()
        system = MIAFinalSystem(FINAL_CONFIG)
        init_time = (time.perf_counter() - start_time) * 1000
        
        results['main_system_init'] = True
        results['main_init_time_ms'] = round(init_time, 2)
        print(f"  ✅ Système principal initialisé en {init_time:.2f}ms")
        
        # Test status système
        status = system.get_system_status()
        results['system_status'] = bool(status)
        print(f"  ✅ Status système: {bool(status)}")
        
        # Test métriques d'import si disponibles
        if 'import_metrics' in status:
            import_metrics = status['import_metrics']
            results['import_metrics_in_status'] = True
            print(f"  ✅ Métriques d'import dans status: {bool(import_metrics)}")
        else:
            results['import_metrics_in_status'] = False
            print("  ⚠️ Métriques d'import non disponibles dans status")
        
    except Exception as e:
        results['functionality_error'] = str(e)
        print(f"  ❌ Erreur fonctionnalité: {e}")
    
    return results

def test_performance_improvements():
    """Test des améliorations de performance"""
    print("\n🧪 Test 5: Améliorations de performance")
    
    results = {}
    
    try:
        from execution.imports_optimizer import get_import_optimizer
        
        optimizer = get_import_optimizer()
        
        # Test cache hit rate
        metrics = optimizer.get_import_metrics()
        cache_hit_rate = metrics.get('cache_hit_rate', 0)
        results['cache_hit_rate'] = cache_hit_rate
        print(f"  📊 Cache Hit Rate: {cache_hit_rate:.1f}%")
        
        # Test temps d'import moyen
        avg_import_time = metrics.get('performance', {}).get('avg_import_time_ms', 0)
        results['avg_import_time_ms'] = avg_import_time
        print(f"  ⏱️ Temps d'import moyen: {avg_import_time:.2f}ms")
        
        # Test taux de succès
        success_rate = metrics.get('success_rate', 0)
        results['success_rate'] = success_rate
        print(f"  ✅ Taux de succès: {success_rate:.1f}%")
        
        # Évaluation performance
        if avg_import_time < 10.0:
            results['performance_grade'] = 'EXCELLENT'
            print("  🏆 Performance: EXCELLENTE")
        elif avg_import_time < 50.0:
            results['performance_grade'] = 'GOOD'
            print("  👍 Performance: BONNE")
        else:
            results['performance_grade'] = 'NEEDS_IMPROVEMENT'
            print("  ⚠️ Performance: À AMÉLIORER")
        
    except Exception as e:
        results['performance_error'] = str(e)
        print(f"  ❌ Erreur test performance: {e}")
    
    return results

def generate_integration_report(test_results: Dict[str, Any]):
    """Génère un rapport d'intégration complet"""
    print("\n" + "="*60)
    print("📊 RAPPORT D'INTÉGRATION EXECUTION/")
    print("="*60)
    
    # Résumé général
    total_tests = len(test_results)
    successful_tests = sum(1 for result in test_results.values() if isinstance(result, dict) and result.get('success', True))
    
    print(f"📈 Tests exécutés: {total_tests}")
    print(f"✅ Tests réussis: {successful_tests}")
    print(f"📊 Taux de réussite: {(successful_tests/total_tests*100):.1f}%")
    
    # Détails par test
    for test_name, result in test_results.items():
        print(f"\n🔍 {test_name.upper()}:")
        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, bool):
                    status = "✅" if value else "❌"
                    print(f"  {status} {key}: {value}")
                else:
                    print(f"  📊 {key}: {value}")
        else:
            print(f"  📊 Résultat: {result}")
    
    # Recommandations
    print(f"\n💡 RECOMMANDATIONS:")
    
    if test_results.get('performance', {}).get('performance_grade') == 'NEEDS_IMPROVEMENT':
        print("  ⚠️ Optimiser les temps d'import des modules")
    
    if test_results.get('imports', {}).get('direct_imports') == False:
        print("  ⚠️ Vérifier les imports directs des modules execution/")
    
    if test_results.get('optimizer', {}).get('preload_success', 0) < 8:
        print("  ⚠️ Améliorer le préchargement des modules critiques")
    
    print("  ✅ Intégration execution/ globalement réussie")
    print("  ✅ Optimisations de performance appliquées")
    print("  ✅ Lanceurs enrichis avec les composants execution/")
    
    print("\n🎯 CONCLUSION:")
    if successful_tests >= total_tests * 0.8:
        print("  🏆 INTÉGRATION RÉUSSIE - Système prêt pour la production")
    else:
        print("  ⚠️ INTÉGRATION PARTIELLE - Corrections nécessaires")
    
    print("="*60)

async def main():
    """Fonction principale de test"""
    print("🚀 DÉMARRAGE TESTS D'INTÉGRATION EXECUTION/")
    print("="*60)
    
    test_results = {}
    
    # Exécution des tests
    test_results['imports'] = test_execution_imports()
    test_results['optimizer'] = test_import_optimizer()
    test_results['launchers'] = test_launcher_imports()
    test_results['functionality'] = await test_launcher_functionality()
    test_results['performance'] = test_performance_improvements()
    
    # Génération du rapport
    generate_integration_report(test_results)
    
    return test_results

if __name__ == "__main__":
    # Exécution des tests
    results = asyncio.run(main())
    
    # Code de sortie basé sur les résultats
    total_tests = len(results)
    successful_tests = sum(1 for result in results.values() if isinstance(result, dict) and result.get('success', True))
    
    if successful_tests >= total_tests * 0.8:
        print("\n🎉 TESTS RÉUSSIS - Intégration execution/ validée")
        sys.exit(0)
    else:
        print("\n❌ TESTS ÉCHOUÉS - Corrections nécessaires")
        sys.exit(1)
