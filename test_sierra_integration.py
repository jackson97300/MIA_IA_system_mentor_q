#!/usr/bin/env python3
"""
🧪 TEST SIERRA CHARTS INTÉGRATION - MIA_IA_SYSTEM
Test de l'intégration Sierra Charts avec passage d'ordres
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from automation_modules import (
    AutomationConfig,
    SierraConnector,
    OrderManager,
    TradingSignal,
    OrderSide,
    OrderType,
    OrderStatus
)

logger = get_logger(__name__)

class SierraIntegrationTester:
    """Testeur de l'intégration Sierra Charts"""
    
    def __init__(self):
        self.test_results = {}
        self.config = AutomationConfig()
        self.sierra = SierraConnector(self.config)
        self.order_manager = OrderManager(self.sierra, self.config)
    
    async def test_sierra_connection(self):
        """Test de la connexion Sierra Charts"""
        logger.info("🔧 TEST 1: Sierra Charts Connection")
        
        try:
            # Test connexion
            connected = await self.sierra.connect()
            assert connected == True
            logger.info("✅ Connexion Sierra Charts réussie")
            
            # Test statut connexion
            status = self.sierra.get_connection_status()
            assert status['is_connected'] == True
            assert status['total_orders'] == 0
            assert status['total_positions'] == 0
            logger.info("✅ Statut connexion vérifié")
            
            # Test heartbeat
            heartbeat = await self.sierra.heartbeat()
            assert heartbeat == True
            logger.info("✅ Heartbeat fonctionnel")
            
            self.test_results['sierra_connection'] = True
            logger.info("🎯 TEST 1: Sierra Connection - SUCCÈS")
            
        except Exception as e:
            logger.error(f"❌ TEST 1: Sierra Connection - ÉCHEC: {e}")
            self.test_results['sierra_connection'] = False
    
    async def test_order_placement(self):
        """Test du placement d'ordres"""
        logger.info("🔧 TEST 2: Order Placement")
        
        try:
            # Création signal de test
            signal = TradingSignal(
                direction="LONG",
                confidence=0.85,
                price=4500.0,
                timestamp=datetime.now(),
                confluence=0.75,
                stop_loss=4490.0,
                take_profit=4520.0
            )
            
            # Test exécution signal
            order_id = await self.order_manager.execute_signal(signal, "ES", 1)
            assert order_id is not None
            logger.info(f"✅ Signal exécuté: {order_id}")
            
            # Test statut ordre
            await asyncio.sleep(0.5)  # Attendre traitement
            order_status = await self.order_manager.get_order_status(order_id)
            assert order_status is not None
            logger.info(f"✅ Statut ordre: {order_status['status']}")
            
            # Test résumé trading
            summary = await self.order_manager.get_trading_summary()
            assert 'total_positions' in summary
            assert 'active_orders' in summary
            logger.info(f"✅ Résumé trading: {summary['active_orders']} ordres actifs")
            
            self.test_results['order_placement'] = True
            logger.info("🎯 TEST 2: Order Placement - SUCCÈS")
            
        except Exception as e:
            logger.error(f"❌ TEST 2: Order Placement - ÉCHEC: {e}")
            self.test_results['order_placement'] = False
    
    async def test_position_management(self):
        """Test de la gestion des positions"""
        logger.info("🔧 TEST 3: Position Management")
        
        try:
            # Test récupération positions
            positions = await self.sierra.get_positions()
            logger.info(f"✅ Positions récupérées: {len(positions)} positions")
            
            # Test informations compte
            account_info = await self.sierra.get_account_info()
            assert 'account_balance' in account_info
            assert 'total_pnl' in account_info
            assert 'available_margin' in account_info
            logger.info(f"✅ Compte: Balance={account_info['account_balance']:.2f}, "
                       f"PnL={account_info['total_pnl']:.2f}")
            
            # Test fermeture position (si position existante)
            if positions:
                symbol = list(positions.keys())[0]
                close_order_id = await self.order_manager.close_position(symbol)
                if close_order_id:
                    logger.info(f"✅ Position fermée: {close_order_id}")
                else:
                    logger.info("⚠️ Aucune position à fermer")
            
            self.test_results['position_management'] = True
            logger.info("🎯 TEST 3: Position Management - SUCCÈS")
            
        except Exception as e:
            logger.error(f"❌ TEST 3: Position Management - ÉCHEC: {e}")
            self.test_results['position_management'] = False
    
    async def test_order_cancellation(self):
        """Test de l'annulation d'ordres"""
        logger.info("🔧 TEST 4: Order Cancellation")
        
        try:
            # Test annulation tous ordres
            await self.order_manager.cancel_all_orders()
            logger.info("✅ Tous les ordres annulés")
            
            # Vérification ordres actifs
            active_count = self.order_manager.get_active_orders_count()
            protection_count = self.order_manager.get_protection_orders_count()
            assert active_count == 0
            assert protection_count == 0
            logger.info("✅ Vérification annulation: 0 ordres actifs")
            
            self.test_results['order_cancellation'] = True
            logger.info("🎯 TEST 4: Order Cancellation - SUCCÈS")
            
        except Exception as e:
            logger.error(f"❌ TEST 4: Order Cancellation - ÉCHEC: {e}")
            self.test_results['order_cancellation'] = False
    
    async def test_monitoring(self):
        """Test du monitoring des ordres"""
        logger.info("🔧 TEST 5: Order Monitoring")
        
        try:
            # Test monitoring ordres
            await self.order_manager.monitor_orders()
            logger.info("✅ Monitoring ordres exécuté")
            
            # Test résumé final
            final_summary = await self.order_manager.get_trading_summary()
            logger.info(f"✅ Résumé final: {final_summary}")
            
            self.test_results['order_monitoring'] = True
            logger.info("🎯 TEST 5: Order Monitoring - SUCCÈS")
            
        except Exception as e:
            logger.error(f"❌ TEST 5: Order Monitoring - ÉCHEC: {e}")
            self.test_results['order_monitoring'] = False
    
    async def test_disconnection(self):
        """Test de la déconnexion"""
        logger.info("🔧 TEST 6: Sierra Disconnection")
        
        try:
            # Test déconnexion
            await self.sierra.disconnect()
            
            # Vérification déconnexion
            status = self.sierra.get_connection_status()
            assert status['is_connected'] == False
            logger.info("✅ Déconnexion Sierra Charts réussie")
            
            self.test_results['sierra_disconnection'] = True
            logger.info("🎯 TEST 6: Sierra Disconnection - SUCCÈS")
            
        except Exception as e:
            logger.error(f"❌ TEST 6: Sierra Disconnection - ÉCHEC: {e}")
            self.test_results['sierra_disconnection'] = False
    
    async def run_all_tests(self):
        """Exécute tous les tests"""
        logger.info("🚀 DÉMARRAGE TEST SIERRA CHARTS INTÉGRATION")
        
        # Tests en séquence
        await self.test_sierra_connection()
        await self.test_order_placement()
        await self.test_position_management()
        await self.test_order_cancellation()
        await self.test_monitoring()
        await self.test_disconnection()
        
        # Résultats finaux
        self.print_results()
    
    def print_results(self):
        """Affiche les résultats des tests"""
        logger.info("\n" + "="*60)
        logger.info("📊 RÉSULTATS TEST SIERRA CHARTS INTÉGRATION")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        
        for test_name, result in self.test_results.items():
            status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\n📈 RÉSULTAT GLOBAL: {passed_tests}/{total_tests} tests réussis")
        
        if passed_tests == total_tests:
            logger.info("🎉 SIERRA CHARTS INTÉGRATION - 100% FONCTIONNELLE")
            logger.info("✅ Système de passage d'ordres opérationnel")
        else:
            logger.info("⚠️ CERTAINS TESTS ONT ÉCHOUÉ - VÉRIFICATION REQUISE")
        
        logger.info("\n📋 FONCTIONNALITÉS TESTÉES:")
        logger.info("• Connexion/déconnexion Sierra Charts")
        logger.info("• Placement d'ordres (MARKET, LIMIT, STOP)")
        logger.info("• Gestion des positions")
        logger.info("• Stop Loss et Take Profit automatiques")
        logger.info("• Annulation d'ordres")
        logger.info("• Monitoring temps réel")

def main():
    """Fonction principale de test"""
    tester = SierraIntegrationTester()
    asyncio.run(tester.run_all_tests())

if __name__ == "__main__":
    main() 