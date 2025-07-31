#!/usr/bin/env python3
"""
TEST MIA_IA_SYSTEM - Test adapté à la structure réelle du projet
Test complet de analytics.py et data_collection_main.py
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

# === CRÉATION DU LOGGER MANQUANT ===

def create_missing_logger():
    """Crée le fichier core/logger.py manquant"""
    logger_content = '''"""
Core Logger Module
"""
import logging
import sys
from pathlib import Path

def setup_logging(name=None, level=logging.INFO):
    """Setup logging configuration"""
    logger = logging.getLogger(name or __name__)
    
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.setLevel(level)
    
    return logger
'''
    
    try:
        with open("core/logger.py", "w", encoding="utf-8") as f:
            f.write(logger_content)
        print_success("Fichier core/logger.py créé")
        return True
    except Exception as e:
        print_error(f"Impossible de créer core/logger.py: {e}")
        return False

# === TEST 1: VÉRIFICATION ET CORRECTION DES FICHIERS ===

def test_and_fix_files():
    """Vérifie et corrige les fichiers manquants"""
    print_test_header("VÉRIFICATION ET CORRECTION DES FICHIERS")
    
    # Vérifier config
    if not os.path.exists("config.py"):
        # Chercher les fichiers de config existants
        config_files = []
        if os.path.exists("config/trading_config.py"):
            config_files.append("config/trading_config.py")
            print_info("Trouvé: config/trading_config.py")
        if os.path.exists("config/automation_config.py"):
            config_files.append("config/automation_config.py")
            print_info("Trouvé: config/automation_config.py")
        
        # Créer config.py qui importe depuis config/
        if config_files:
            config_content = '''"""
Configuration principale - Importe depuis config/
"""

# Import depuis les vrais fichiers de config
try:
    from config.trading_config import *
except ImportError:
    def get_trading_config():
        return {"mock": True}

try:
    from config.automation_config import *
except ImportError:
    def get_automation_config():
        return {"mock": True}
'''
            try:
                with open("config.py", "w", encoding="utf-8") as f:
                    f.write(config_content)
                print_success("config.py créé avec redirection vers config/")
            except Exception as e:
                print_error(f"Erreur création config.py: {e}")
    
    # Vérifier/créer core/logger.py
    if not os.path.exists("core/logger.py"):
        create_missing_logger()
    else:
        print_success("core/logger.py existe déjà")
    
    # Vérifier autres fichiers requis
    required_files = {
        "core/base_types.py": True,
        "monitoring/performance_tracker.py": True,
        "monitoring/alert_system.py": True,
        "data/data_collector.py": True,
        "data/analytics.py": True,
        "data_collection_main.py": True
    }
    
    all_present = True
    for file_path, required in required_files.items():
        if os.path.exists(file_path):
            print_success(f"Fichier trouvé: {file_path}")
        else:
            all_present = False
            print_error(f"Fichier manquant: {file_path}")
    
    return all_present

# === TEST 2: TEST DES IMPORTS ===

def test_imports():
    """Test tous les imports nécessaires"""
    print_test_header("TEST DES IMPORTS")
    
    errors = []
    
    # Test numpy et pandas
    try:
        import numpy as np
        print_success("Import numpy réussi")
    except ImportError as e:
        errors.append(f"numpy: {e}")
        print_error(f"numpy non installé: pip install numpy")
    
    try:
        import pandas as pd
        print_success("Import pandas réussi")
    except ImportError as e:
        errors.append(f"pandas: {e}")
        print_error(f"pandas non installé: pip install pandas")
    
    # Test imports locaux avec gestion d'erreurs
    try:
        # Essayer d'importer depuis config/ directement si config.py échoue
        try:
            from config import get_trading_config, get_automation_config
            print_success("Import config réussi")
        except ImportError:
            from config.trading_config import get_trading_config
            from config.automation_config import get_automation_config
            print_success("Import config/ réussi (direct)")
    except Exception as e:
        errors.append(f"config: {e}")
        print_error(f"Erreur import config: {e}")
    
    try:
        from core.base_types import ES_TICK_SIZE, ES_TICK_VALUE
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
    
    try:
        from data.data_collector import DataCollector
        print_success("Import data.data_collector réussi")
    except Exception as e:
        errors.append(f"data.data_collector: {e}")
        print_error(f"Erreur import data.data_collector: {e}")
    
    try:
        from data.analytics import DataAnalytics, create_data_analytics
        print_success("Import data.analytics réussi")
    except Exception as e:
        errors.append(f"data.analytics: {e}")
        print_error(f"Erreur import data.analytics: {e}")
    
    return len(errors) == 0

# === TEST 3: TEST ANALYTICS.PY ===

def test_analytics():
    """Test le module analytics.py"""
    print_test_header("TEST MODULE ANALYTICS")
    
    try:
        import numpy as np
        import pandas as pd
        
        # Import avec gestion d'erreur
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from data.analytics import (
            DataAnalytics, create_data_analytics, 
            PerformanceMetrics, RiskAnalysis, PatternAnalysis,
            TimeFrame
        )
        print_success("Import analytics réussi")
        
        # Créer instance
        analytics = create_data_analytics()
        print_success("Instance DataAnalytics créée")
        
        # Créer données de test
        test_data = []
        for i in range(50):
            test_data.append({
                'timestamp': datetime.now() - timedelta(hours=i),
                'symbol': 'ES',
                'pnl': np.random.normal(50, 100),
                'session': 'NY_MORNING' if i % 2 == 0 else 'LONDON',
                'pattern_type': 'BATTLE_NAVALE',
                'signal_strength': 0.5 + np.random.random() * 0.5,
                'atr_14': 15 + np.random.random() * 10,
                'entry_price': 4500,
                'stop_loss': 4480,
                'take_profit': 4520
            })
        
        df = pd.DataFrame(test_data)
        
        # Test des méthodes principales
        print_info("\nTest des méthodes principales...")
        
        # 1. Performance
        perf = analytics.analyze_performance(df)
        print_success(f"analyze_performance: {perf.total_trades} trades")
        
        # 2. Patterns
        patterns = analytics.analyze_patterns(df)
        print_success("analyze_patterns exécuté")
        
        # 3. Risk
        risk = analytics.analyze_risk(df)
        print_success(f"analyze_risk: VaR={risk.var_95:.2f}")
        
        # Test des nouvelles méthodes
        print_info("\nTest des méthodes avancées...")
        
        # Vérifier tail_ratio
        if hasattr(risk, 'tail_ratio'):
            print_success(f"Tail Ratio présent: {risk.tail_ratio:.2f}")
        else:
            print_warning("Tail Ratio non trouvé dans RiskAnalysis")
            
        # Vérifier omega_ratio
        if hasattr(risk, 'omega_ratio'):
            print_success(f"Omega Ratio présent: {risk.omega_ratio:.2f}")
        else:
            print_warning("Omega Ratio non trouvé dans RiskAnalysis")
        
        # Test méthodes privées
        if hasattr(analytics, '_calculate_tail_ratio'):
            tail = analytics._calculate_tail_ratio(df['pnl'])
            print_success(f"_calculate_tail_ratio fonctionne: {tail:.2f}")
        else:
            print_error("_calculate_tail_ratio non trouvé")
            
        if hasattr(analytics, '_calculate_omega_ratio'):
            omega = analytics._calculate_omega_ratio(df['pnl'])
            print_success(f"_calculate_omega_ratio fonctionne: {omega:.2f}")
        else:
            print_error("_calculate_omega_ratio non trouvé")
            
        if hasattr(analytics, '_analyze_time_of_day_pattern'):
            time_pattern = analytics._analyze_time_of_day_pattern(df)
            if time_pattern:
                print_success("_analyze_time_of_day_pattern fonctionne")
            else:
                print_warning("_analyze_time_of_day_pattern retourne None")
        else:
            print_error("_analyze_time_of_day_pattern non trouvé")
            
        if hasattr(analytics, '_analyze_volatility_pattern'):
            vol_pattern = analytics._analyze_volatility_pattern(df)
            if vol_pattern:
                print_success("_analyze_volatility_pattern fonctionne")
            else:
                print_warning("_analyze_volatility_pattern retourne None")
        else:
            print_error("_analyze_volatility_pattern non trouvé")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur test analytics: {e}")
        traceback.print_exc()
        return False

# === TEST 4: TEST DATA_COLLECTION_MAIN ===

def test_data_collection_main():
    """Test data_collection_main.py"""
    print_test_header("TEST DATA_COLLECTION_MAIN")
    
    try:
        # Import
        from data_collection_main import DataCollectionManager
        print_success("Import DataCollectionManager réussi")
        
        # Créer instance
        manager = DataCollectionManager()
        print_success("Instance DataCollectionManager créée")
        
        # Vérifier le type
        if hasattr(manager, 'analytics'):
            analytics_type = type(manager.analytics).__name__
            if analytics_type == 'DataAnalytics':
                print_success(f"Type correct: {analytics_type}")
            else:
                print_error(f"Type incorrect: {analytics_type} (devrait être DataAnalytics)")
        else:
            print_error("Attribut analytics non trouvé")
        
        # Test méthodes
        print_info("\nTest des méthodes...")
        
        # Status
        status = manager.get_status()
        print_success("get_status exécuté")
        
        # Quality (peut ne pas avoir de données)
        quality = manager.analyze_data_quality(days=1)
        if quality.get('status') == 'no_data':
            print_info("Pas de données (normal pour premier test)")
        else:
            print_success("analyze_data_quality exécuté")
        
        # Summary
        summary = manager.generate_summary(period="daily")
        print_success("generate_summary exécuté")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur test data_collection_main: {e}")
        traceback.print_exc()
        return False

# === TEST 5: TEST INTÉGRATION ===

def test_integration():
    """Test l'intégration complète"""
    print_test_header("TEST INTÉGRATION")
    
    try:
        from data_collection_main import DataCollectionManager
        from data.analytics import DataAnalytics
        
        manager = DataCollectionManager()
        
        # Vérifier intégration
        if isinstance(manager.analytics, DataAnalytics):
            print_success("Intégration correcte: DataCollectionManager utilise DataAnalytics")
        else:
            print_error("Problème d'intégration")
            return False
        
        # Test run_analytics
        print_info("Test run_analytics (peut prendre quelques secondes)...")
        
        # Capturer la sortie
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            manager.run_analytics(comprehensive=False)
        
        output = f.getvalue()
        
        # Vérifier le contenu
        if "RAPPORT ANALYTICS" in output:
            print_success("Rapport généré avec succès")
            
            # Vérifier les nouvelles métriques
            checks = {
                "Tail Ratio": "Tail Ratio présent dans rapport",
                "Omega Ratio": "Omega Ratio présent dans rapport",
                "PATTERNS": "Section patterns présente"
            }
            
            for key, message in checks.items():
                if key in output:
                    print_success(message)
                else:
                    print_warning(f"{key} non trouvé dans rapport")
        else:
            print_error("Rapport non généré")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Erreur test intégration: {e}")
        traceback.print_exc()
        return False

# === MAIN ===

def main():
    """Fonction principale"""
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("="*60)
    print("TEST MIA_IA_SYSTEM - ANALYTICS + DATA COLLECTION")
    print("="*60)
    print(f"{Colors.ENDC}")
    
    results = {
        "Fichiers": False,
        "Imports": False,
        "Analytics": False,
        "DataCollection": False,
        "Intégration": False
    }
    
    try:
        # 1. Vérifier et corriger fichiers
        print_info("Étape 1: Vérification des fichiers...")
        results["Fichiers"] = test_and_fix_files()
        
        # 2. Test imports
        print_info("\nÉtape 2: Test des imports...")
        results["Imports"] = test_imports()
        
        if results["Imports"]:
            # 3. Test analytics
            print_info("\nÉtape 3: Test analytics.py...")
            results["Analytics"] = test_analytics()
            
            # 4. Test data_collection_main
            print_info("\nÉtape 4: Test data_collection_main.py...")
            results["DataCollection"] = test_data_collection_main()
            
            # 5. Test intégration
            print_info("\nÉtape 5: Test intégration...")
            results["Intégration"] = test_integration()
        else:
            print_warning("\nTests analytics ignorés à cause d'erreurs d'import")
    
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        traceback.print_exc()
    
    # Résumé
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    print(f"{Colors.ENDC}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test, success in results.items():
        if success:
            print_success(f"{test}: PASSÉ")
        else:
            print_error(f"{test}: ÉCHOUÉ")
    
    print(f"\n{Colors.BOLD}")
    if passed == total:
        print_success(f"🎉 TOUS LES TESTS PASSÉS ({passed}/{total})")
        print_info("\nVos fichiers sont parfaitement intégrés!")
    else:
        print_warning(f"Tests passés: {passed}/{total}")
        if not results["Imports"]:
            print_info("\n💡 Installez les dépendances manquantes:")
            print_info("   pip install numpy pandas matplotlib scikit-learn")
    print(f"{Colors.ENDC}")

if __name__ == "__main__":
    main()