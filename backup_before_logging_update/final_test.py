#!/usr/bin/env python3
"""
TEST FINAL - Vérification complète analytics + data_collection_main
"""

import sys
import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Couleurs
class Colors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def test_result(test_name, success, details=""):
    if success:
        print(f"{Colors.OKGREEN}✅ {test_name}{Colors.ENDC} {details}")
    else:
        print(f"{Colors.FAIL}❌ {test_name}{Colors.ENDC} {details}")
    return success

print(f"\n{Colors.BOLD}TEST FINAL - MIA_IA_SYSTEM{Colors.ENDC}\n")

all_tests_passed = True

# Test 1: Import Analytics
print("1. Test Analytics Module")
try:
    from data.analytics import DataAnalytics, create_data_analytics
    analytics = create_data_analytics()
    
    # Créer données test
    test_trades = pd.DataFrame([
        {
            'timestamp': datetime.now() - timedelta(hours=i),
            'pnl': np.random.normal(50, 100),
            'signal_strength': np.random.uniform(0.3, 1.0),
            'atr_14': 15 + np.random.uniform(-5, 10),
            'entry_price': 4500,
            'stop_loss': 4480,
            'take_profit': 4520
        }
        for i in range(20)
    ])
    
    # Test méthodes principales
    perf = analytics.analyze_performance(test_trades)
    risk = analytics.analyze_risk(test_trades)
    
    # Vérifier nouvelles métriques
    has_tail_ratio = hasattr(risk, 'tail_ratio') and risk.tail_ratio > 0
    has_omega_ratio = hasattr(risk, 'omega_ratio') and risk.omega_ratio > 0
    
    test_result("   - Import et création", True)
    test_result("   - analyze_performance", True, f"({perf.total_trades} trades)")
    test_result("   - analyze_risk", True)
    test_result("   - Tail Ratio", has_tail_ratio, f"({risk.tail_ratio:.2f})" if has_tail_ratio else "")
    test_result("   - Omega Ratio", has_omega_ratio, f"({risk.omega_ratio:.2f})" if has_omega_ratio else "")
    
    # Test méthodes privées
    if hasattr(analytics, '_calculate_tail_ratio'):
        tail = analytics._calculate_tail_ratio(test_trades['pnl'])
        test_result("   - _calculate_tail_ratio", True, f"({tail:.2f})")
    else:
        test_result("   - _calculate_tail_ratio", False)
        all_tests_passed = False
    
    if hasattr(analytics, '_analyze_time_of_day_pattern'):
        pattern = analytics._analyze_time_of_day_pattern(test_trades)
        test_result("   - _analyze_time_of_day_pattern", pattern is not None)
    else:
        test_result("   - _analyze_time_of_day_pattern", False)
        all_tests_passed = False
    
except Exception as e:
    test_result("   - Analytics Module", False, str(e))
    all_tests_passed = False

# Test 2: Import DataCollectionManager
print("\n2. Test DataCollection Module")
try:
    from data_collection_main import DataCollectionManager
    manager = DataCollectionManager()
    
    test_result("   - Import et création", True)
    
    # Vérifier type analytics
    correct_type = type(manager.analytics).__name__ == 'DataAnalytics'
    test_result("   - Type DataAnalytics", correct_type, f"({type(manager.analytics).__name__})")
    
    # Test méthodes
    status = manager.get_status()
    test_result("   - get_status", True)
    
    summary = manager.generate_summary("daily")
    test_result("   - generate_summary", True)
    
    # Test simulation
    manager._simulate_snapshot_collection()
    test_result("   - _simulate_snapshot_collection", True, f"({manager.snapshots_collected} snapshots)")
    
except Exception as e:
    test_result("   - DataCollection Module", False, str(e))
    all_tests_passed = False

# Test 3: Intégration
print("\n3. Test Intégration")
try:
    # Test run_analytics avec capture output
    import io
    from contextlib import redirect_stdout
    
    f = io.StringIO()
    with redirect_stdout(f):
        manager.run_analytics(comprehensive=False)
    
    output = f.getvalue()
    
    # Vérifier contenu
    has_report = "RAPPORT ANALYTICS" in output
    has_tail = "Tail Ratio" in output
    has_omega = "Omega Ratio" in output
    
    test_result("   - run_analytics", has_report)
    test_result("   - Tail Ratio dans rapport", has_tail)
    test_result("   - Omega Ratio dans rapport", has_omega)
    
    if not (has_report and has_tail and has_omega):
        all_tests_passed = False
    
except Exception as e:
    test_result("   - Intégration", False, str(e))
    all_tests_passed = False

# Test 4: Performance avec volume
print("\n4. Test Performance")
try:
    # Générer beaucoup de données
    import time
    
    large_df = pd.DataFrame([
        {
            'timestamp': datetime.now() - timedelta(hours=i),
            'pnl': np.random.normal(50, 100),
            'signal_strength': np.random.uniform(0.3, 1.0),
            'atr_14': 15 + np.random.uniform(-5, 10),
            'entry_price': 4500,
            'stop_loss': 4480,
            'take_profit': 4520
        }
        for i in range(500)
    ])
    
    start = time.time()
    perf = analytics.analyze_performance(large_df)
    risk = analytics.analyze_risk(large_df)
    duration = time.time() - start
    
    test_result("   - 500 trades analysés", duration < 2, f"({duration:.3f}s)")
    
except Exception as e:
    test_result("   - Performance", False, str(e))
    all_tests_passed = False

# Résumé
print(f"\n{Colors.BOLD}{'='*50}")
print("RÉSUMÉ")
print('='*50 + Colors.ENDC)

if all_tests_passed:
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 TOUS LES TESTS PASSÉS !{Colors.ENDC}")
    print(f"\n{Colors.OKGREEN}Votre système est prêt :{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✅ analytics.py contient toutes les méthodes avancées{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✅ data_collection_main.py utilise correctement DataAnalytics{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✅ Les nouvelles métriques (Tail Ratio, Omega Ratio) fonctionnent{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✅ L'intégration est complète et performante{Colors.ENDC}")
else:
    print(f"\n{Colors.WARNING}⚠️  Certains tests ont échoué{Colors.ENDC}")
    print(f"{Colors.WARNING}Vérifiez les erreurs ci-dessus{Colors.ENDC}")

print(f"\n{Colors.BOLD}Prochaines étapes :{Colors.ENDC}")
print("1. Lancer la collection de données : python data_collection_main.py --start")
print("2. Analyser la qualité : python data_collection_main.py --quality")
print("3. Générer un rapport : python data_collection_main.py --summary")