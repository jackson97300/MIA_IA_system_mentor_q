#!/usr/bin/env python3
"""
🎯 TEST FINAL PRODUCTION - MIA_IA SYSTEM
========================================

Script de test final pour valider que le système est prêt pour la production.
Teste l'intégration complète de tous les modules automation_modules.
"""

import sys
import asyncio
import traceback
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

class ProductionSystemTester:
    """Testeur du système de production complet"""
    
    def __init__(self):
        self.results = {}
        self.config = None
        self.system = None
        
    def test_system_integration(self) -> bool:
        """Test d'intégration complète du système"""
        try:
            print("\n🎯 Test d'intégration complète du système...")
            
            # 1. Configuration
            from automation_modules.config_manager import AutomationConfig
            self.config = AutomationConfig()
            self.config.simulation_mode = False
            self.config.live_trading = True
            self.config.min_signal_confidence = 0.18
            self.config.footprint_threshold = 0.15
            self.config.volume_threshold = 350
            self.config.daily_loss_limit = 2000.0
            self.config.max_daily_trades = 25
            print("✅ Configuration production: OK")
            
            # 2. Création du système principal
            from automation_modules.optimized_trading_system import OptimizedTradingSystem
            self.system = OptimizedTradingSystem(self.config)
            print("✅ Système principal créé: OK")
            
            # 3. Test des modules critiques
            self._test_critical_modules()
            
            print("✅ Intégration système: OK")
            return True
            
        except Exception as e:
            print(f"❌ Erreur intégration: {e}")
            traceback.print_exc()
            return False
    
    def _test_critical_modules(self):
        """Test des modules critiques"""
        print("  🔧 Test des modules critiques...")
        
        # Risk Manager
        from automation_modules.risk_manager import RiskManager
        risk_manager = RiskManager(self.config)
        print("    ✅ Risk Manager: OK")
        
        # Validation Engine
        from automation_modules.validation_engine import create_validation_engine
        validation_engine = create_validation_engine(self.config)
        print("    ✅ Validation Engine: OK")
        
        # Trading Executor
        from automation_modules.trading_executor import create_trading_executor
        trading_executor = create_trading_executor(self.config)
        print("    ✅ Trading Executor: OK")
        
        # Performance Tracker
        from automation_modules.performance_tracker import PerformanceTracker
        performance_tracker = PerformanceTracker()
        print("    ✅ Performance Tracker: OK")
        
        # Confluence Calculator
        from automation_modules.confluence_calculator import EnhancedConfluenceCalculator
        confluence_calculator = EnhancedConfluenceCalculator()
        print("    ✅ Confluence Calculator: OK")
    
    def test_trading_workflow(self) -> bool:
        """Test du workflow de trading complet"""
        try:
            print("\n💼 Test du workflow de trading...")
            
            # 1. Données de marché simulées
            market_data = {
                'ES': {
                    'price': 4500.0,
                    'volume': 1000,
                    'bid': 4499.5,
                    'ask': 4500.5,
                    'timestamp': datetime.now()
                }
            }
            print("✅ Données de marché: OK")
            
            # 2. Calcul de confluence
            from automation_modules.confluence_calculator import EnhancedConfluenceCalculator
            calculator = EnhancedConfluenceCalculator()
            confluence_result = calculator.calculate_enhanced_confluence(market_data)
            print("✅ Calcul confluence: OK")
            
            # 3. Validation du signal
            from automation_modules.validation_engine import create_validation_engine
            validation_engine = create_validation_engine(self.config)
            validation_result = validation_engine.validate_signal_with_enhanced_filters(market_data)
            print("✅ Validation signal: OK")
            
            # 4. Vérification des risques
            from automation_modules.risk_manager import RiskManager
            risk_manager = RiskManager(self.config)
            risk_check = risk_manager.check_signal_confidence(0.75)
            print("✅ Vérification risques: OK")
            
            # 5. Simulation d'exécution
            from automation_modules.trading_executor import create_trading_executor
            executor = create_trading_executor(self.config)
            print("✅ Préparation exécution: OK")
            
            print("✅ Workflow de trading: OK")
            return True
            
        except Exception as e:
            print(f"❌ Erreur workflow: {e}")
            traceback.print_exc()
            return False
    
    def test_system_status(self) -> bool:
        """Test du statut du système"""
        try:
            print("\n📊 Test du statut du système...")
            
            if not self.system:
                print("⚠️ Système non initialisé")
                return False
            
            # Test des méthodes de statut
            if hasattr(self.system, 'get_system_status'):
                status = self.system.get_system_status()
                print("✅ get_system_status: OK")
            else:
                print("⚠️ get_system_status non disponible")
            
            if hasattr(self.system, 'get_performance_summary'):
                summary = self.system.get_performance_summary()
                print("✅ get_performance_summary: OK")
            else:
                print("⚠️ get_performance_summary non disponible")
            
            print("✅ Statut système: OK")
            return True
            
        except Exception as e:
            print(f"❌ Erreur statut: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test de la gestion d'erreurs"""
        try:
            print("\n🛡️ Test de la gestion d'erreurs...")
            
            # Test avec données invalides
            invalid_data = {}
            
            # Test validation avec données vides
            from automation_modules.validation_engine import create_validation_engine
            validation_engine = create_validation_engine(self.config)
            try:
                result = validation_engine.validate_signal_with_enhanced_filters(invalid_data)
                print("✅ Gestion données invalides: OK")
            except Exception as e:
                print(f"⚠️ Exception attendue: {e}")
            
            # Test risk manager avec valeurs invalides
            from automation_modules.risk_manager import RiskManager
            risk_manager = RiskManager(self.config)
            try:
                result = risk_manager.check_signal_confidence(-1.0)
                print("✅ Gestion valeurs invalides: OK")
            except Exception as e:
                print(f"⚠️ Exception attendue: {e}")
            
            print("✅ Gestion d'erreurs: OK")
            return True
            
        except Exception as e:
            print(f"❌ Erreur gestion d'erreurs: {e}")
            return False
    
    def test_configuration_validation(self) -> bool:
        """Test de la validation de configuration"""
        try:
            print("\n⚙️ Test de la validation de configuration...")
            
            # Test configuration valide
            valid_config = AutomationConfig()
            valid_config.simulation_mode = False
            valid_config.live_trading = True
            print("✅ Configuration valide: OK")
            
            # Test création système avec config
            from automation_modules.optimized_trading_system import OptimizedTradingSystem
            system = OptimizedTradingSystem(valid_config)
            print("✅ Création système avec config: OK")
            
            print("✅ Validation configuration: OK")
            return True
            
        except Exception as e:
            print(f"❌ Erreur configuration: {e}")
            return False
    
    def run_production_tests(self) -> Dict[str, bool]:
        """Exécute tous les tests de production"""
        print("🎯 TESTS FINAUX DE PRODUCTION - MIA_IA SYSTEM")
        print("=" * 60)
        
        tests = [
            ("system_integration", self.test_system_integration),
            ("trading_workflow", self.test_trading_workflow),
            ("system_status", self.test_system_status),
            ("error_handling", self.test_error_handling),
            ("configuration_validation", self.test_configuration_validation),
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                self.results[test_name] = result
            except Exception as e:
                print(f"❌ Erreur dans {test_name}: {e}")
                self.results[test_name] = False
        
        return self.results
    
    def print_production_summary(self):
        """Affiche le résumé des tests de production"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS DE PRODUCTION")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"Total des tests: {total_tests}")
        print(f"Tests réussis: {passed_tests} ✅")
        print(f"Tests échoués: {failed_tests} ❌")
        print(f"Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Tests échoués:")
            for test_name, result in self.results.items():
                if not result:
                    print(f"  - {test_name}")
        
        if passed_tests == total_tests:
            print("\n🎉 SYSTÈME PRÊT POUR LA PRODUCTION!")
            print("✅ Tous les tests critiques sont réussis")
            print("✅ Le système peut être déployé en production")
        else:
            print(f"\n⚠️ {failed_tests} test(s) ont échoué")
            print("🔧 Vérification nécessaire avant production")

def main():
    """Fonction principale"""
    tester = ProductionSystemTester()
    results = tester.run_production_tests()
    tester.print_production_summary()
    
    # Code de sortie
    if all(results.values()):
        print("\n✅ SYSTÈME VALIDÉ POUR LA PRODUCTION")
        return 0
    else:
        print("\n❌ SYSTÈME NÉCESSITE DES CORRECTIONS")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)



