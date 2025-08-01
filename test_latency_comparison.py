#!/usr/bin/env python3
"""
📊 TEST COMPARAISON LATENCE - MIA_IA_SYSTEM
Comparaison des performances IBKR vs Sierra Charts
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime
import time

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from automation_modules import (
    AutomationConfig,
    SierraConnector,
    SierraOptimizer,
    LatencyConfig
)

logger = get_logger(__name__)

class LatencyComparisonTester:
    """Testeur de comparaison de latence"""
    
    def __init__(self):
        self.test_results = {}
        self.config = AutomationConfig()
        self.sierra = SierraConnector(self.config)
        self.latency_config = LatencyConfig()
        self.optimizer = SierraOptimizer(self.sierra, self.latency_config)
        
        # Métriques de comparaison
        self.ibkr_latencies = []
        self.sierra_latencies = []
        self.sierra_optimized_latencies = []
    
    async def test_ibkr_latency(self):
        """Test de latence IBKR (simulation)"""
        logger.info("🔧 TEST 1: IBKR Latency (Simulation)")
        
        try:
            # Simulation latence IBKR direct
            latencies = []
            for i in range(10):
                start_time = time.time()
                
                # Simulation ordre IBKR
                await asyncio.sleep(0.015)  # 15ms latence typique IBKR
                
                end_time = time.time()
                latency = (end_time - start_time) * 1000
                latencies.append(latency)
            
            self.ibkr_latencies = latencies
            avg_latency = sum(latencies) / len(latencies)
            
            logger.info(f"✅ IBKR Latency - Moyenne: {avg_latency:.2f}ms")
            logger.info(f"   Min: {min(latencies):.2f}ms, Max: {max(latencies):.2f}ms")
            
            self.test_results['ibkr_latency'] = True
            
        except Exception as e:
            logger.error(f"❌ TEST 1: IBKR Latency - ÉCHEC: {e}")
            self.test_results['ibkr_latency'] = False
    
    async def test_sierra_standard_latency(self):
        """Test de latence Sierra Charts standard"""
        logger.info("🔧 TEST 2: Sierra Charts Standard Latency")
        
        try:
            # Connexion Sierra
            await self.sierra.connect()
            
            # Test latence standard
            latencies = []
            for i in range(10):
                start_time = time.time()
                
                # Placement ordre standard
                order_id = await self.sierra.place_order(
                    symbol='ES',
                    side='BUY',
                    quantity=1,
                    order_type='MARKET'
                )
                
                end_time = time.time()
                latency = (end_time - start_time) * 1000
                latencies.append(latency)
            
            self.sierra_latencies = latencies
            avg_latency = sum(latencies) / len(latencies)
            
            logger.info(f"✅ Sierra Standard - Moyenne: {avg_latency:.2f}ms")
            logger.info(f"   Min: {min(latencies):.2f}ms, Max: {max(latencies):.2f}ms")
            
            self.test_results['sierra_standard_latency'] = True
            
        except Exception as e:
            logger.error(f"❌ TEST 2: Sierra Standard - ÉCHEC: {e}")
            self.test_results['sierra_standard_latency'] = False
    
    async def test_sierra_optimized_latency(self):
        """Test de latence Sierra Charts optimisé"""
        logger.info("🔧 TEST 3: Sierra Charts Optimized Latency")
        
        try:
            # Optimisation connexion
            await self.optimizer.optimize_connection()
            
            # Test latence optimisée
            latencies = []
            for i in range(10):
                start_time = time.time()
                
                # Placement ordre optimisé
                order_id = await self.optimizer.place_optimized_order(
                    symbol='ES',
                    side='BUY',
                    quantity=1,
                    order_type='MARKET'
                )
                
                end_time = time.time()
                latency = (end_time - start_time) * 1000
                latencies.append(latency)
            
            self.sierra_optimized_latencies = latencies
            avg_latency = sum(latencies) / len(latencies)
            
            logger.info(f"✅ Sierra Optimized - Moyenne: {avg_latency:.2f}ms")
            logger.info(f"   Min: {min(latencies):.2f}ms, Max: {max(latencies):.2f}ms")
            
            self.test_results['sierra_optimized_latency'] = True
            
        except Exception as e:
            logger.error(f"❌ TEST 3: Sierra Optimized - ÉCHEC: {e}")
            self.test_results['sierra_optimized_latency'] = False
    
    async def test_batch_performance(self):
        """Test de performance en batch"""
        logger.info("🔧 TEST 4: Batch Performance")
        
        try:
            # Test placement batch
            orders = [
                {'symbol': 'ES', 'side': 'BUY', 'quantity': 1, 'order_type': 'MARKET'},
                {'symbol': 'MES', 'side': 'SELL', 'quantity': 2, 'order_type': 'MARKET'},
                {'symbol': 'ES', 'side': 'BUY', 'quantity': 1, 'order_type': 'LIMIT', 'price': 4500.0}
            ]
            
            start_time = time.time()
            results = await self.optimizer.batch_place_orders(orders)
            end_time = time.time()
            
            batch_latency = (end_time - start_time) * 1000
            avg_batch_latency = batch_latency / len(orders)
            
            logger.info(f"✅ Batch Performance - Total: {batch_latency:.2f}ms")
            logger.info(f"   Moyenne par ordre: {avg_batch_latency:.2f}ms")
            logger.info(f"   Ordres placés: {len([r for r in results if r])}/{len(orders)}")
            
            self.test_results['batch_performance'] = True
            
        except Exception as e:
            logger.error(f"❌ TEST 4: Batch Performance - ÉCHEC: {e}")
            self.test_results['batch_performance'] = False
    
    def analyze_performance_difference(self):
        """Analyse la différence de performance"""
        logger.info("📊 ANALYSE PERFORMANCE")
        
        if not all([self.ibkr_latencies, self.sierra_latencies, self.sierra_optimized_latencies]):
            logger.warning("⚠️ Données insuffisantes pour analyse")
            return
        
        # Calculs moyennes
        ibkr_avg = sum(self.ibkr_latencies) / len(self.ibkr_latencies)
        sierra_avg = sum(self.sierra_latencies) / len(self.sierra_latencies)
        sierra_opt_avg = sum(self.sierra_optimized_latencies) / len(self.sierra_optimized_latencies)
        
        # Différences
        sierra_overhead = sierra_avg - ibkr_avg
        optimization_improvement = sierra_avg - sierra_opt_avg
        final_overhead = sierra_opt_avg - ibkr_avg
        
        logger.info("\n" + "="*60)
        logger.info("📊 RÉSULTATS COMPARAISON LATENCE")
        logger.info("="*60)
        
        logger.info(f"IBKR Direct:           {ibkr_avg:.2f}ms")
        logger.info(f"Sierra Standard:       {sierra_avg:.2f}ms")
        logger.info(f"Sierra Optimized:      {sierra_opt_avg:.2f}ms")
        
        logger.info(f"\n📈 ANALYSE:")
        logger.info(f"Overhead Sierra Standard:  +{sierra_overhead:.2f}ms ({sierra_overhead/ibkr_avg*100:.1f}%)")
        logger.info(f"Amélioration Optimisation: -{optimization_improvement:.2f}ms ({optimization_improvement/sierra_avg*100:.1f}%)")
        logger.info(f"Overhead Final:            +{final_overhead:.2f}ms ({final_overhead/ibkr_avg*100:.1f}%)")
        
        # Recommandations
        logger.info(f"\n💡 RECOMMANDATIONS:")
        
        if final_overhead < 20:
            logger.info("✅ Latence acceptable - Sierra Charts recommandé")
            logger.info("   Avantages: Interface avancée, contrôle total")
        elif final_overhead < 50:
            logger.info("⚠️ Latence modérée - Utiliser selon stratégie")
            logger.info("   Considérer: Scalping = IBKR, Swing = Sierra")
        else:
            logger.info("❌ Latence élevée - IBKR recommandé")
            logger.info("   Pour: Trading haute fréquence, scalping")
        
        # Optimisations supplémentaires
        recommendations = self.optimizer.get_optimization_recommendations()
        if recommendations:
            logger.info(f"\n🔧 OPTIMISATIONS SUPPLÉMENTAIRES:")
            for rec in recommendations:
                logger.info(f"   • {rec}")
    
    async def run_all_tests(self):
        """Exécute tous les tests de comparaison"""
        logger.info("🚀 DÉMARRAGE TEST COMPARAISON LATENCE")
        
        # Tests en séquence
        await self.test_ibkr_latency()
        await self.test_sierra_standard_latency()
        await self.test_sierra_optimized_latency()
        await self.test_batch_performance()
        
        # Analyse finale
        self.analyze_performance_difference()
        
        # Nettoyage
        await self.sierra.disconnect()
        
        # Résultats finaux
        self.print_results()
    
    def print_results(self):
        """Affiche les résultats finaux"""
        logger.info("\n" + "="*60)
        logger.info("📊 RÉSULTATS FINAUX - COMPARAISON LATENCE")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        
        for test_name, result in self.test_results.items():
            status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\n📈 RÉSULTAT GLOBAL: {passed_tests}/{total_tests} tests réussis")
        
        if passed_tests == total_tests:
            logger.info("🎉 COMPARAISON LATENCE - TERMINÉE")
            logger.info("✅ Analyse de performance complète")
        else:
            logger.info("⚠️ CERTAINS TESTS ONT ÉCHOUÉ - VÉRIFICATION REQUISE")

def main():
    """Fonction principale de test"""
    tester = LatencyComparisonTester()
    asyncio.run(tester.run_all_tests())

if __name__ == "__main__":
    main() 