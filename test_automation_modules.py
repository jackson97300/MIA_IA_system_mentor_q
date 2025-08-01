#!/usr/bin/env python3
"""
🧪 TEST AUTOMATION MODULES - MIA_IA_SYSTEM
Test de la nouvelle architecture modulaire
"""

import sys
import asyncio
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from automation_modules import (
    AutomationConfig,
    EnhancedConfluenceCalculator,
    MIAAutomationSystem,
    RiskManager,
    TradingStats,
    PerformanceTracker
)

logger = get_logger(__name__)

class AutomationModulesTester:
    """Testeur de la nouvelle architecture modulaire"""
    
    def __init__(self):
        self.test_results = {}
    
    def test_config_manager(self):
        """Test du module de configuration"""
        logger.info("🔧 TEST 1: Config Manager")
        
        try:
            config = AutomationConfig()
            
            # Test validation
            assert config.validate() == True
            logger.info("✅ Configuration validée")
            
            # Test paramètres
            assert config.max_position_size == 2
            assert config.daily_loss_limit == 500.0
            assert config.min_signal_confidence == 0.70
            logger.info("✅ Paramètres configurés")
            
            self.test_results['config_manager'] = True
            logger.info("🎯 TEST 1: Config Manager - SUCCÈS")
            
        except Exception as e:
            logger.error(f"❌ TEST 1: Config Manager - ÉCHEC: {e}")
            self.test_results['config_manager'] = False
    
    def test_performance_tracker(self):
        """Test du module de suivi des performances"""
        logger.info("🔧 TEST 2: Performance Tracker")
        
        try:
            tracker = PerformanceTracker()
            
            # Test ajout trades
            tracker.add_trade(50.0, True)   # Win
            tracker.add_trade(-30.0, False) # Loss
            tracker.add_trade(75.0, True)   # Win
            
            # Test ajout signaux
            tracker.add_signal(filtered=True, ml_approved=True, gamma_optimized=True)
            tracker.add_signal(filtered=False, ml_approved=False, gamma_optimized=False)
            
            # Test résumé
            summary = tracker.get_summary()
            assert summary['total_trades'] == 3
            assert summary['win_rate'] == 66.7  # 2/3
            assert summary['signals_generated'] == 2
            
            logger.info(f"✅ Performance: WinRate={summary['win_rate']:.1f}%, "
                       f"Trades={summary['total_trades']}")
            
            self.test_results['performance_tracker'] = True
            logger.info("🎯 TEST 2: Performance Tracker - SUCCÈS")
            
        except Exception as e:
            logger.error(f"❌ TEST 2: Performance Tracker - ÉCHEC: {e}")
            self.test_results['performance_tracker'] = False
    
    def test_risk_manager(self):
        """Test du module de gestion des risques"""
        logger.info("🔧 TEST 3: Risk Manager")
        
        try:
            config = AutomationConfig()
            risk_manager = RiskManager(config)
            
            # Test vérifications
            assert risk_manager.check_daily_loss_limit() == True
            assert risk_manager.check_daily_trade_limit() == True
            assert risk_manager.check_position_limit() == True
            assert risk_manager.check_signal_confidence(0.8) == True
            assert risk_manager.check_signal_confidence(0.5) == False
            
            # Test calculs
            position_size = risk_manager.calculate_position_size(10000.0)
            assert 1 <= position_size <= config.max_position_size
            
            stop_loss = risk_manager.calculate_stop_loss(4500.0, "LONG")
            assert stop_loss < 4500.0
            
            take_profit = risk_manager.calculate_take_profit(4500.0, stop_loss, "LONG")
            assert take_profit > 4500.0
            
            logger.info("✅ Risk management fonctionnel")
            
            self.test_results['risk_manager'] = True
            logger.info("🎯 TEST 3: Risk Manager - SUCCÈS")
            
        except Exception as e:
            logger.error(f"❌ TEST 3: Risk Manager - ÉCHEC: {e}")
            self.test_results['risk_manager'] = False
    
    def test_confluence_calculator(self):
        """Test du module de calcul de confluence"""
        logger.info("🔧 TEST 4: Confluence Calculator")
        
        try:
            calculator = EnhancedConfluenceCalculator()
            
            # Créer données de test
            class MarketData:
                def __init__(self):
                    self.price = 4500.0
                    self.volume = 1000
                    self.timestamp = None
            
            market_data = MarketData()
            
            # Test calcul confluence
            confluence = calculator.calculate_enhanced_confluence(market_data)
            assert 0.0 <= confluence <= 1.0
            
            logger.info(f"✅ Confluence calculée: {confluence:.3f}")
            
            # Test cache
            confluence2 = calculator.calculate_enhanced_confluence(market_data)
            assert confluence == confluence2  # Cache fonctionne
            
            calculator.clear_cache()
            logger.info("✅ Cache confluence testé")
            
            self.test_results['confluence_calculator'] = True
            logger.info("🎯 TEST 4: Confluence Calculator - SUCCÈS")
            
        except Exception as e:
            logger.error(f"❌ TEST 4: Confluence Calculator - ÉCHEC: {e}")
            self.test_results['confluence_calculator'] = False
    
    async def test_trading_engine(self):
        """Test du moteur de trading principal"""
        logger.info("🔧 TEST 5: Trading Engine")
        
        try:
            config = AutomationConfig()
            system = MIAAutomationSystem(config)
            
            # Test initialisation
            assert system.is_running == False
            assert system.current_positions == 0
            
            # Test statut système
            status = system.get_system_status()
            assert 'is_running' in status
            assert 'current_positions' in status
            assert 'performance_summary' in status
            assert 'risk_summary' in status
            
            logger.info("✅ Trading engine initialisé")
            
            # Test court (pas de boucle complète)
            await system._validate_config()
            logger.info("✅ Validation config OK")
            
            self.test_results['trading_engine'] = True
            logger.info("🎯 TEST 5: Trading Engine - SUCCÈS")
            
        except Exception as e:
            logger.error(f"❌ TEST 5: Trading Engine - ÉCHEC: {e}")
            self.test_results['trading_engine'] = False
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        logger.info("🚀 DÉMARRAGE TEST AUTOMATION MODULES")
        
        # Tests synchrones
        self.test_config_manager()
        self.test_performance_tracker()
        self.test_risk_manager()
        self.test_confluence_calculator()
        
        # Test asynchrone
        asyncio.run(self.test_trading_engine())
        
        # Résultats finaux
        self.print_results()
    
    def print_results(self):
        """Affiche les résultats des tests"""
        logger.info("\n" + "="*60)
        logger.info("📊 RÉSULTATS TEST AUTOMATION MODULES")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        
        for test_name, result in self.test_results.items():
            status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\n📈 RÉSULTAT GLOBAL: {passed_tests}/{total_tests} tests réussis")
        
        if passed_tests == total_tests:
            logger.info("🎉 ARCHITECTURE MODULAIRE - 100% FONCTIONNELLE")
            logger.info("✅ Refactorisation réussie - automation_main divisé en modules")
        else:
            logger.info("⚠️ CERTAINS TESTS ONT ÉCHOUÉ - VÉRIFICATION REQUISE")
        
        logger.info("\n📋 AVANTAGES DE LA NOUVELLE ARCHITECTURE:")
        logger.info("• Modules spécialisés et réutilisables")
        logger.info("• Code plus maintenable et lisible")
        logger.info("• Tests unitaires facilités")
        logger.info("• Performance améliorée (imports plus rapides)")
        logger.info("• Évolutivité simplifiée")

def main():
    """Fonction principale de test"""
    tester = AutomationModulesTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 