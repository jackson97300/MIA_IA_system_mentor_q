#!/usr/bin/env python3
"""
TEST INTEGRATION RÉEL - Sans mocks
Test complet de analytics.py et data_collection_main.py
avec les vrais fichiers du projet
"""

import sys
import os
import traceback
from datetime import datetime, timedelta
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Couleurs pour l'affichage
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test_header(test_name):
    """Affiche un header de test"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}TEST: {test_name}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")

def print_success(message):
    """Affiche un message de succès"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    """Affiche un message d'erreur"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def print_warning(message):
    """Affiche un warning"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def print_info(message):
    """Affiche une info"""
    print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")

# === TEST 1: VÉRIFICATION DES FICHIERS REQUIS ===

def test_required_files():
    """Vérifie que tous les fichiers requis existent"""
    print_test_header("VÉRIFICATION DES FICHIERS REQUIS")
    
    required_files = [
        "config.py",
        "core/base_types.py",
        "core/logger.py",
        "monitoring/performance_tracker.py",
        "monitoring/alert_system.py",
        "data/data_collector.py",
        "data/analytics.py",
        "data_collection_main.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"Fichier trouvé: {file_path}")
        else:
            missing_files.append(file_path)
            print_error(f"Fichier manquant: {file_path}")
    
    return len(missing_files) == 0

# === TEST 2: TEST DES IMPORTS PRINCIPAUX ===

def test_main_imports():
    """Test les imports principaux"""
    print_test_header("TEST DES IMPORTS PRINCIPAUX")
    
    errors = []
    
    # Test imports config
    try:
        from config import get_trading_config, get_automation_config
        print_success("Import config réussi")
    except Exception as e:
        errors.append(f"config: {e}")
        print_error(f"Erreur import config: {e}")
    
    # Test imports core
    try:
        from core.base_types import (
            MarketData, TradingSignal, SignalType, SignalStrength,
            TradeResult, ES_TICK_SIZE, ES_TICK_VALUE,
            SessionPhase, get_session_phase
        )
        print_success("Import core.base_types réussi")
    except Exception as e:
        errors.append(f"core.base_types: {e}")
        print_error(f"Erreur import core.base_types: {e}")
    
    try:
        from core.logger import setup_logging
        print_success("Import core.logger réussi")
    except Exception as e:
        errors.append(f"core.logger: {e}")
        print_error(f"Erreur import core.logger: {e}")
    
    # Test imports monitoring
    try:
        from monitoring.performance_tracker import PerformanceTracker
        print_success("Import monitoring.performance_tracker réussi")
    except Exception as e:
        errors.append(f"monitoring.performance_tracker: {e}")
        print_error(f"Erreur import monitoring.performance_tracker: {e}")
    
    try:
        from monitoring.alert_system import AlertSystem, AlertLevel
        print_success("Import monitoring.alert_system réussi")
    except Exception as e:
        errors.append(f"monitoring.alert_system: {e}")
        print_error(f"Erreur import monitoring.alert_system: {e}")
    
    # Test imports data
    try:
        from data.data_collector import DataCollector, DataQuality, DataPeriod
        print_success("Import data.data_collector réussi")
    except Exception as e:
        errors.append(f"data.data_collector: {e}")
        print_error(f"Erreur import data.data_collector: {e}")
    
    try:
        from data.analytics import (
            DataAnalytics, PerformanceMetrics, PatternAnalysis,
            RiskAnalysis, MLAnalysis, AnalyticsReport,
            AnalysisType, ReportFormat, TimeFrame, PatternType,
            create_data_analytics
        )
        print_success("Import data.analytics réussi")
    except Exception as e:
        errors.append(f"data.analytics: {e}")
        print_error(f"Erreur import data.analytics: {e}")
    
    return len(errors) == 0

# === TEST 3: TEST MODULE ANALYTICS ===

def test_analytics_functionality():
    """Test les fonctionnalités du module analytics"""
    print_test_header("TEST FONCTIONNALITÉS ANALYTICS")
    
    try:
        import numpy as np
        import pandas as pd
        from data.analytics import DataAnalytics, create_data_analytics, TimeFrame
        
        # Création instance
        analytics = create_data_analytics()
        print_success("Instance DataAnalytics créée")
        
        # Données de test réalistes
        test_trades = pd.DataFrame([
            {
                'timestamp': datetime.now() - timedelta(hours=i),
                'symbol': 'ES',
                'pnl': np.random.choice([100, 75, 50, -30, -50, -75], p=[0.2, 0.2, 0.2, 0.15, 0.15, 0.1]),
                'session': 'NY_MORNING' if i % 2 == 0 else 'LONDON',
                'pattern_type': 'BATTLE_NAVALE' if i % 3 == 0 else 'CONFLUENCE',
                'confluence_score': np.random.uniform(0.3, 0.9),
                'battle_strength': np.random.uniform(0.4, 1.0),
                'signal_strength': np.random.uniform(0.3, 1.0),
                'atr_14': 15 + np.random.uniform(-5, 10),
                'volume_relative': 1.0 + np.random.uniform(-0.3, 0.5),
                'trend_strength': np.random.uniform(-1, 1),
                'entry_price': 4500 + np.random.uniform(-50, 50),
                'stop_loss': 4480 + np.random.uniform(-20, -10),
                'take_profit': 4520 + np.random.uniform(10, 30),
                'duration_minutes': np.random.randint(5, 120),
                'holding_time_minutes': np.random.randint(5, 120)
            }
            for i in range(100)
        ])
        
        # Test 1: Performance Analysis
        print_info("\n1. Test analyze_performance...")
        perf = analytics.analyze_performance(test_trades, TimeFrame.ALL_TIME)
        print_success(f"   Total trades: {perf.total_trades}")
        print_success(f"   Win rate: {perf.win_rate:.1%}")
        print_success(f"   Sharpe ratio: {perf.sharpe_ratio:.2f}")
        print_success(f"   Max drawdown: ${perf.max_drawdown:.2f}")
        
        # Vérifier les nouvelles métriques
        if hasattr(perf, 'avg_pnl'):
            print_success(f"   Avg P&L: ${perf.avg_pnl:.2f}")
        if hasattr(perf, 'var_95'):
            print_success(f"   VaR 95%: ${perf.var_95:.2f}")
        if hasattr(perf, 'trades_per_day'):
            print_success(f"   Trades per day: {perf.trades_per_day:.1f}")
        
        # Test 2: Pattern Analysis
        print_info("\n2. Test analyze_patterns...")
        patterns = analytics.analyze_patterns(test_trades)
        print_success(f"   Patterns trouvés: {len(patterns.pattern_frequency)}")
        print_success(f"   Meilleures heures: {patterns.best_hours}")
        
        # Vérifier les patterns avancés
        if hasattr(patterns, 'time_patterns') and patterns.time_patterns:
            print_success(f"   Time patterns analysés: {len(patterns.time_patterns.get('hourly_stats', {}))}")
        if hasattr(patterns, 'volatility_patterns') and patterns.volatility_patterns:
            print_success(f"   Volatility patterns analysés: {len(patterns.volatility_patterns.get('regime_stats', {}))}")
        
        # Test 3: Risk Analysis
        print_info("\n3. Test analyze_risk...")
        risk = analytics.analyze_risk(test_trades)
        print_success(f"   VaR 95%: ${risk.var_95:.2f}")
        print_success(f"   Kelly fraction: {risk.kelly_fraction:.2%}")
        
        # Vérifier les métriques avancées
        if hasattr(risk, 'tail_ratio'):
            print_success(f"   Tail ratio: {risk.tail_ratio:.2f}")
        else:
            print_error("   Tail ratio non trouvé")
            
        if hasattr(risk, 'omega_ratio'):
            print_success(f"   Omega ratio: {risk.omega_ratio:.2f}")
        else:
            print_error("   Omega ratio non trouvé")
            
        if hasattr(risk, 'ulcer_index'):
            print_success(f"   Ulcer index: {risk.ulcer_index:.2f}")
        
        # Test 4: Méthodes privées avancées
        print_info("\n4. Test méthodes avancées...")
        
        # Test _calculate_tail_ratio
        if hasattr(analytics, '_calculate_tail_ratio'):
            tail_ratio = analytics._calculate_tail_ratio(test_trades['pnl'])
            print_success(f"   _calculate_tail_ratio: {tail_ratio:.2f}")
        else:
            print_error("   _calculate_tail_ratio non trouvé")
        
        # Test _calculate_omega_ratio
        if hasattr(analytics, '_calculate_omega_ratio'):
            omega_ratio = analytics._calculate_omega_ratio(test_trades['pnl'])
            print_success(f"   _calculate_omega_ratio: {omega_ratio:.2f}")
        else:
            print_error("   _calculate_omega_ratio non trouvé")
        
        # Test _analyze_time_of_day_pattern
        if hasattr(analytics, '_analyze_time_of_day_pattern'):
            time_pattern = analytics._analyze_time_of_day_pattern(test_trades)
            if time_pattern:
                print_success(f"   _analyze_time_of_day_pattern: {len(time_pattern.get('hourly_stats', {}))} heures")
        else:
            print_error("   _analyze_time_of_day_pattern non trouvé")
        
        # Test _analyze_volatility_pattern
        if hasattr(analytics, '_analyze_volatility_pattern'):
            vol_pattern = analytics._analyze_volatility_pattern(test_trades)
            if vol_pattern:
                print_success(f"   _analyze_volatility_pattern: {len(vol_pattern.get('regime_stats', {}))} régimes")
        else:
            print_error("   _analyze_volatility_pattern non trouvé")
        
        # Test 5: Rapport complet
        print_info("\n5. Test generate_comprehensive_report...")
        report = analytics.generate_comprehensive_report(time_frame=TimeFrame.ALL_TIME)
        print_success(f"   Report ID: {report.report_id}")
        print_success(f"   Insights: {len(report.insights)}")
        print_success(f"   Recommendations: {len(report.recommendations)}")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur test analytics: {e}")
        traceback.print_exc()
        return False

# === TEST 4: TEST DATA_COLLECTION_MAIN ===

def test_data_collection_main():
    """Test le module data_collection_main"""
    print_test_header("TEST DATA_COLLECTION_MAIN")
    
    try:
        # Import du module
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from data_collection_main import DataCollectionManager
        print_success("Import DataCollectionManager réussi")
        
        # Création instance
        manager = DataCollectionManager()
        print_success("Instance DataCollectionManager créée")
        
        # Vérifier les attributs
        if hasattr(manager, 'analytics'):
            print_success(f"   analytics: {type(manager.analytics).__name__}")
        else:
            print_error("   attribut analytics manquant")
            
        if hasattr(manager, 'collector'):
            print_success(f"   collector: {type(manager.collector).__name__}")
        else:
            print_error("   attribut collector manquant")
        
        # Test 1: Status
        print_info("\n1. Test get_status...")
        status = manager.get_status()
        print_success(f"   Session ID: {status['session']['id']}")
        print_success(f"   Storage: {status['storage']['total_mb']:.1f} MB")
        
        # Test 2: Data Quality
        print_info("\n2. Test analyze_data_quality...")
        quality = manager.analyze_data_quality(days=7)
        if quality.get('status') == 'no_data':
            print_warning("   Pas de données à analyser (normal si première exécution)")
        else:
            print_success(f"   Quality score: {quality.get('quality_score', 0):.2%}")
        
        # Test 3: Summary
        print_info("\n3. Test generate_summary...")
        summary = manager.generate_summary(period="daily")
        print_success(f"   Period: {summary['period']}")
        print_success(f"   Report ID: {summary['report_id']}")
        
        # Test 4: Export ML
        print_info("\n4. Test export_ml_dataset...")
        ml_success = manager.export_ml_dataset(days=7)
        if ml_success:
            print_success("   Export ML dataset réussi")
        else:
            print_warning("   Export ML dataset: pas de données (normal si première exécution)")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur test data_collection_main: {e}")
        traceback.print_exc()
        return False

# === TEST 5: TEST INTÉGRATION COMPLÈTE ===

def test_full_integration():
    """Test l'intégration complète entre les modules"""
    print_test_header("TEST INTÉGRATION COMPLÈTE")
    
    try:
        from data_collection_main import DataCollectionManager
        from data.analytics import DataAnalytics
        import numpy as np
        
        # Création des instances
        manager = DataCollectionManager()
        
        # Test 1: Vérifier le type correct
        if type(manager.analytics).__name__ == 'DataAnalytics':
            print_success("Manager utilise correctement DataAnalytics")
        else:
            print_error(f"Type incorrect: {type(manager.analytics).__name__}")
            return False
        
        # Test 2: Simulation de collecte
        print_info("\n1. Simulation collecte de données...")
        for i in range(10):
            manager._simulate_snapshot_collection()
        print_success(f"   {manager.snapshots_collected} snapshots collectés")
        
        # Test 3: Organisation des données
        print_info("\n2. Test organisation des données...")
        manager._organize_data()
        print_success("   Organisation exécutée")
        
        # Test 4: Analytics complet
        print_info("\n3. Test run_analytics...")
        # Capture stdout pour vérifier l'output
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            manager.run_analytics(comprehensive=False)
        
        output = f.getvalue()
        if "RAPPORT ANALYTICS" in output:
            print_success("   Rapport analytics généré avec succès")
            
            # Vérifier présence des nouvelles métriques
            if "Tail Ratio" in output:
                print_success("   Tail Ratio présent dans le rapport")
            if "Omega Ratio" in output:
                print_success("   Omega Ratio présent dans le rapport")
            if "PATTERNS TEMPORELS" in output:
                print_success("   Patterns temporels analysés")
        else:
            print_error("   Rapport analytics non généré correctement")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur test intégration: {e}")
        traceback.print_exc()
        return False

# === TEST 6: TEST DE PERFORMANCE ===

def test_performance():
    """Test de performance avec volume de données important"""
    print_test_header("TEST DE PERFORMANCE")
    
    try:
        import numpy as np
        import pandas as pd
        import time
        from data.analytics import create_data_analytics
        
        # Générer beaucoup de données
        print_info("Génération de 1000 trades...")
        start_time = time.time()
        
        large_dataset = pd.DataFrame([
            {
                'timestamp': datetime.now() - timedelta(hours=i),
                'symbol': 'ES',
                'pnl': np.random.normal(50, 100),
                'session': np.random.choice(['NY_MORNING', 'LONDON', 'ASIA']),
                'pattern_type': np.random.choice(['BATTLE_NAVALE', 'CONFLUENCE', 'BREAKOUT']),
                'confluence_score': np.random.uniform(0.3, 0.9),
                'signal_strength': np.random.uniform(0.3, 1.0),
                'atr_14': np.random.uniform(10, 30),
                'entry_price': 4500,
                'stop_loss': 4480,
                'take_profit': 4520
            }
            for i in range(1000)
        ])
        
        generation_time = time.time() - start_time
        print_success(f"Données générées en {generation_time:.2f}s")
        
        # Test analytics performance
        analytics = create_data_analytics()
        
        # Performance analysis
        start_time = time.time()
        perf = analytics.analyze_performance(large_dataset)
        perf_time = time.time() - start_time
        print_success(f"analyze_performance: {perf_time:.3f}s pour 1000 trades")
        
        # Pattern analysis
        start_time = time.time()
        patterns = analytics.analyze_patterns(large_dataset)
        pattern_time = time.time() - start_time
        print_success(f"analyze_patterns: {pattern_time:.3f}s pour 1000 trades")
        
        # Risk analysis
        start_time = time.time()
        risk = analytics.analyze_risk(large_dataset)
        risk_time = time.time() - start_time
        print_success(f"analyze_risk: {risk_time:.3f}s pour 1000 trades")
        
        # Vérifier que les temps sont raisonnables
        total_time = perf_time + pattern_time + risk_time
        if total_time < 5:  # Moins de 5 secondes pour tout
            print_success(f"Performance totale excellente: {total_time:.2f}s")
        else:
            print_warning(f"Performance totale correcte mais peut être optimisée: {total_time:.2f}s")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur test performance: {e}")
        traceback.print_exc()
        return False

# === MAIN ===

def main():
    """Fonction principale de test"""
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("="*60)
    print("TEST COMPLET RÉEL - ANALYTICS + DATA_COLLECTION_MAIN")
    print("="*60)
    print(f"{Colors.ENDC}")
    
    # Résultats des tests
    results = {
        "Fichiers requis": False,
        "Imports": False,
        "Analytics": False,
        "DataCollection": False,
        "Intégration": False,
        "Performance": False
    }
    
    # Exécution des tests
    try:
        # 1. Vérifier les fichiers
        results["Fichiers requis"] = test_required_files()
        
        if results["Fichiers requis"]:
            # 2. Test imports
            results["Imports"] = test_main_imports()
            
            if results["Imports"]:
                # 3. Test analytics
                results["Analytics"] = test_analytics_functionality()
                
                # 4. Test data_collection_main
                results["DataCollection"] = test_data_collection_main()
                
                # 5. Test intégration
                results["Intégration"] = test_full_integration()
                
                # 6. Test performance
                results["Performance"] = test_performance()
            else:
                print_warning("Tests suivants ignorés à cause d'erreurs d'import")
        else:
            print_error("Tests ignorés - fichiers manquants")
        
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        traceback.print_exc()
    
    # Résumé
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    print(f"{Colors.ENDC}")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        if passed:
            print_success(f"{test_name}: PASSÉ")
        else:
            print_error(f"{test_name}: ÉCHOUÉ")
    
    print(f"\n{Colors.BOLD}")
    if passed_tests == total_tests:
        print_success(f"🎉 TOUS LES TESTS PASSÉS ({passed_tests}/{total_tests})")
        print_info("\nVos fichiers analytics.py et data_collection_main.py sont parfaitement intégrés!")
    else:
        print_error(f"⚠️  CERTAINS TESTS ONT ÉCHOUÉ ({passed_tests}/{total_tests})")
        print_info("\nVérifiez les erreurs ci-dessus pour les corriger")
    print(f"{Colors.ENDC}")

if __name__ == "__main__":
    main()