"""
MIA_IA_SYSTEM - Test Runner Principal
Exécution de tous les tests du système
Version: Production Ready
Performance: Validation complète système
"""

import sys
import unittest
import time
import os
from pathlib import Path
from datetime import datetime
import traceback

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger

logger = get_logger(__name__)


class TestRunner:
    """Runner principal pour tous les tests"""
    
    def __init__(self):
        """Initialisation du runner"""
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.start_time = None
        self.end_time = None
    
    def run_core_tests(self):
        """Exécuter tests core modules"""
        logger.info("🧪 Démarrage tests core modules...")
        
        try:
            from tests.test_core import run_core_tests
            success = run_core_tests()
            self.test_results['core'] = success
            logger.info("✅ Tests core modules terminés")
            return success
        except Exception as e:
            logger.error(f"❌ Erreur tests core: {e}")
            self.test_results['core'] = False
            return False
    
    def run_strategy_tests(self):
        """Exécuter tests stratégies"""
        logger.info("🧪 Démarrage tests stratégies...")
        
        try:
            from tests.test_strategies import run_strategy_tests
            success = run_strategy_tests()
            self.test_results['strategies'] = success
            logger.info("✅ Tests stratégies terminés")
            return success
        except Exception as e:
            logger.error(f"❌ Erreur tests stratégies: {e}")
            self.test_results['strategies'] = False
            return False
    
    def run_feature_tests(self):
        """Exécuter tests features"""
        logger.info("🧪 Démarrage tests features...")
        
        try:
            from tests.test_features import run_feature_tests
            success = run_feature_tests()
            self.test_results['features'] = success
            logger.info("✅ Tests features terminés")
            return success
        except Exception as e:
            logger.error(f"❌ Erreur tests features: {e}")
            self.test_results['features'] = False
            return False
    
    def run_ml_tests(self):
        """Exécuter tests ML"""
        logger.info("🧪 Démarrage tests ML...")
        
        try:
            # Test ML Ensemble Filter
            from tests.test_ml.test_ensemble_filter import run_ensemble_filter_tests
            ensemble_success = run_ensemble_filter_tests()
            
            # Test Gamma Cycles
            from tests.test_ml.test_gamma_cycles import run_gamma_cycles_tests
            gamma_success = run_gamma_cycles_tests()
            
            # Test autres modules ML
            from tests.test_ml.test_simple_model import TestSimpleModel
            from tests.test_ml.test_data_processor import TestDataProcessor
            from tests.test_ml.test_model_validator import TestModelValidator
            
            # Créer suite de tests ML
            ml_suite = unittest.TestSuite()
            ml_suite.addTest(unittest.makeSuite(TestSimpleModel))
            ml_suite.addTest(unittest.makeSuite(TestDataProcessor))
            ml_suite.addTest(unittest.makeSuite(TestModelValidator))
            
            # Exécuter tests ML
            runner = unittest.TextTestRunner(verbosity=1)
            ml_result = runner.run(ml_suite)
            ml_success = ml_result.wasSuccessful()
            
            # Résultat global ML
            ml_overall_success = ensemble_success and gamma_success and ml_success
            self.test_results['ml'] = ml_overall_success
            logger.info("✅ Tests ML terminés")
            return ml_overall_success
            
        except Exception as e:
            logger.error(f"❌ Erreur tests ML: {e}")
            self.test_results['ml'] = False
            return False
    
    def run_monitoring_tests(self):
        """Exécuter tests monitoring"""
        logger.info("🧪 Démarrage tests monitoring...")
        
        try:
            from tests.test_monitoring.test_performance_tracker import TestPerformanceTracker
            from tests.test_monitoring.test_live_monitor import TestLiveMonitor
            from tests.test_monitoring.test_discord_notifier import TestDiscordNotifier
            from tests.test_monitoring.test_alert_system import TestAlertSystem
            
            # Créer suite de tests monitoring
            monitoring_suite = unittest.TestSuite()
            monitoring_suite.addTest(unittest.makeSuite(TestPerformanceTracker))
            monitoring_suite.addTest(unittest.makeSuite(TestLiveMonitor))
            monitoring_suite.addTest(unittest.makeSuite(TestDiscordNotifier))
            monitoring_suite.addTest(unittest.makeSuite(TestAlertSystem))
            
            # Exécuter tests monitoring
            runner = unittest.TextTestRunner(verbosity=1)
            monitoring_result = runner.run(monitoring_suite)
            monitoring_success = monitoring_result.wasSuccessful()
            
            self.test_results['monitoring'] = monitoring_success
            logger.info("✅ Tests monitoring terminés")
            return monitoring_success
            
        except Exception as e:
            logger.error(f"❌ Erreur tests monitoring: {e}")
            self.test_results['monitoring'] = False
            return False
    
    def run_execution_tests(self):
        """Exécuter tests execution"""
        logger.info("🧪 Démarrage tests execution...")
        
        try:
            from tests.test_execution.test_simple_trader import TestSimpleTrader
            from tests.test_execution.test_trade_snapshotter import TestTradeSnapshotter
            from tests.test_execution.test_data_collector import TestDataCollector
            
            # Créer suite de tests execution
            execution_suite = unittest.TestSuite()
            execution_suite.addTest(unittest.makeSuite(TestSimpleTrader))
            execution_suite.addTest(unittest.makeSuite(TestTradeSnapshotter))
            execution_suite.addTest(unittest.makeSuite(TestDataCollector))
            
            # Exécuter tests execution
            runner = unittest.TextTestRunner(verbosity=1)
            execution_result = runner.run(execution_suite)
            execution_success = execution_result.wasSuccessful()
            
            self.test_results['execution'] = execution_success
            logger.info("✅ Tests execution terminés")
            return execution_success
            
        except Exception as e:
            logger.error(f"❌ Erreur tests execution: {e}")
            self.test_results['execution'] = False
            return False
    
    def run_import_tests(self):
        """Exécuter tests imports"""
        logger.info("🧪 Démarrage tests imports...")
        
        try:
            from tests.test_imports import quick_import_test
            import_success = quick_import_test()
            
            self.test_results['imports'] = import_success
            logger.info("✅ Tests imports terminés")
            return import_success
            
        except Exception as e:
            logger.error(f"❌ Erreur tests imports: {e}")
            self.test_results['imports'] = False
            return False
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        logger.info("🚀 DÉMARRAGE TESTS COMPLETS MIA_IA_SYSTEM")
        logger.info("=" * 60)
        
        self.start_time = time.time()
        
        # Tests par catégorie
        test_categories = [
            ("Imports", self.run_import_tests),
            ("Core Modules", self.run_core_tests),
            ("Features", self.run_feature_tests),
            ("Strategies", self.run_strategy_tests),
            ("ML Modules", self.run_ml_tests),
            ("Monitoring", self.run_monitoring_tests),
            ("Execution", self.run_execution_tests)
        ]
        
        results = {}
        
        for category_name, test_function in test_categories:
            logger.info(f"\n📋 {category_name.upper()}")
            logger.info("-" * 40)
            
            try:
                success = test_function()
                results[category_name] = success
                
                if success:
                    logger.info(f"✅ {category_name}: SUCCÈS")
                else:
                    logger.error(f"❌ {category_name}: ÉCHEC")
                    
            except Exception as e:
                logger.error(f"❌ {category_name}: ERREUR - {e}")
                results[category_name] = False
        
        self.end_time = time.time()
        self.test_results = results
        
        # Résultats finaux
        self.print_final_results()
        
        return all(results.values())
    
    def print_final_results(self):
        """Afficher résultats finaux"""
        logger.info("\n" + "=" * 60)
        logger.info("🏆 RÉSULTATS FINAUX DES TESTS")
        logger.info("=" * 60)
        
        total_time = self.end_time - self.start_time
        
        # Compter succès/échecs
        passed = sum(1 for success in self.test_results.values() if success)
        failed = len(self.test_results) - passed
        
        logger.info(f"⏱️  Temps total: {total_time:.2f} secondes")
        logger.info(f"📊 Tests réussis: {passed}/{len(self.test_results)}")
        logger.info(f"📊 Tests échoués: {failed}/{len(self.test_results)}")
        
        logger.info("\n📋 DÉTAIL PAR CATÉGORIE:")
        for category, success in self.test_results.items():
            status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
            logger.info(f"  {category}: {status}")
        
        if all(self.test_results.values()):
            logger.info("\n🎉 TOUS LES TESTS ONT RÉUSSI !")
            logger.info("🚀 SYSTÈME PRÊT POUR PRODUCTION !")
        else:
            logger.info("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
            logger.info("🔧 Vérifiez les erreurs ci-dessus")
        
        logger.info("=" * 60)


def main():
    """Fonction principale"""
    logger.info("🧪 MIA_IA_SYSTEM - Test Runner Principal")
    logger.info("Version: Production Ready")
    logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Créer et exécuter le runner
    runner = TestRunner()
    overall_success = runner.run_all_tests()
    
    # Code de sortie
    if overall_success:
        print("\n🎉 TOUS LES TESTS ONT RÉUSSI !")
        sys.exit(0)
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        sys.exit(1)


if __name__ == "__main__":
    main() 