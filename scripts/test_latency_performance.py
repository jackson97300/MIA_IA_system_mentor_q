#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test Performance Latence
[PLUG] DIAGNOSTIC COMPLET LATENCE SYSTÈME

🔧 TESTS APPLIQUÉS :
- ✅ Test latence Battle Navale
- ✅ Test latence Confluence Analyzer
- ✅ Test latence IBKR connection
- ✅ Test latence end-to-end
- ✅ Benchmark performance

Author: MIA_IA_SYSTEM
Version: 1.0.0
Date: Juillet 2025
"""

import asyncio
import time
import statistics
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Local imports
from core.logger import get_logger
from core.ibkr_connector import IBKRConnector
from core.battle_navale import BattleNavaleAnalyzer
from features.confluence_analyzer import ConfluenceAnalyzer
from config.latency_optimization_config import (
    DEFAULT_LATENCY_CONFIG, 
    LATENCY_TARGETS_BY_STRATEGY,
    is_latency_acceptable
)

logger = get_logger(__name__)

# === LATENCY TEST CLASS ===

class LatencyPerformanceTester:
    """Testeur de performance latence complet"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.latency_config = DEFAULT_LATENCY_CONFIG
        self.results = {}
        self.test_iterations = self.config.get('test_iterations', 100)
        
        # Initialize components
        self.ibkr_connector = None
        self.battle_navale = None
        self.confluence_analyzer = None
        
    async def initialize_components(self):
        """Initialise les composants pour les tests"""
        try:
            # Initialize IBKR connector
            self.ibkr_connector = IBKRConnector(self.config.get('ibkr_config', {}))
            
            # Initialize analyzers
            self.battle_navale = BattleNavaleAnalyzer()
            self.confluence_analyzer = ConfluenceAnalyzer()
            
            logger.info("✅ Composants initialisés pour tests latence")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation composants: {e}")
            return False
    
    async def test_battle_navale_latency(self) -> Dict[str, Any]:
        """Test latence Battle Navale"""
        logger.info("🔍 Test latence Battle Navale...")
        
        latencies = []
        sample_data = self._generate_sample_market_data()
        
        for i in range(self.test_iterations):
            start_time = time.time()
            
            try:
                # Test Battle Navale analysis
                result = await self.battle_navale.analyze_market_structure(sample_data)
                
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur test Battle Navale iteration {i}: {e}")
                continue
        
        return self._calculate_latency_stats(latencies, 'battle_navale')
    
    async def test_confluence_analyzer_latency(self) -> Dict[str, Any]:
        """Test latence Confluence Analyzer"""
        logger.info("🔍 Test latence Confluence Analyzer...")
        
        latencies = []
        sample_data = self._generate_sample_market_data()
        
        for i in range(self.test_iterations):
            start_time = time.time()
            
            try:
                # Test Confluence analysis
                result = await self.confluence_analyzer.analyze_confluence(sample_data)
                
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur test Confluence iteration {i}: {e}")
                continue
        
        return self._calculate_latency_stats(latencies, 'confluence_analyzer')
    
    async def test_ibkr_connection_latency(self) -> Dict[str, Any]:
        """Test latence connexion IBKR"""
        logger.info("🔍 Test latence connexion IBKR...")
        
        latencies = []
        
        for i in range(min(self.test_iterations, 20)):  # Limiter tests IBKR
            start_time = time.time()
            
            try:
                # Test connection
                connected = await self.ibkr_connector.connect()
                
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
                
                # Disconnect for next test
                await self.ibkr_connector.disconnect()
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur test IBKR iteration {i}: {e}")
                continue
        
        return self._calculate_latency_stats(latencies, 'ibkr_connection')
    
    async def test_market_data_latency(self) -> Dict[str, Any]:
        """Test latence récupération données marché"""
        logger.info("🔍 Test latence données marché...")
        
        latencies = []
        
        # Connect first
        await self.ibkr_connector.connect()
        
        for i in range(min(self.test_iterations, 30)):  # Limiter tests
            start_time = time.time()
            
            try:
                # Test market data retrieval
                market_data = await self.ibkr_connector.get_market_data('ES')
                
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur test données marché iteration {i}: {e}")
                continue
        
        await self.ibkr_connector.disconnect()
        return self._calculate_latency_stats(latencies, 'market_data')
    
    async def test_end_to_end_latency(self) -> Dict[str, Any]:
        """Test latence end-to-end complète"""
        logger.info("🔍 Test latence end-to-end...")
        
        latencies = []
        sample_data = self._generate_sample_market_data()
        
        for i in range(self.test_iterations):
            start_time = time.time()
            
            try:
                # Test complete pipeline
                # 1. Battle Navale
                battle_result = await self.battle_navale.analyze_market_structure(sample_data)
                
                # 2. Confluence
                confluence_result = await self.confluence_analyzer.analyze_confluence(sample_data)
                
                # 3. Signal generation (simulated)
                signal_strength = (battle_result.get('signal_strength', 0) + 
                                 confluence_result.get('confluence_score', 0)) / 2
                
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur test end-to-end iteration {i}: {e}")
                continue
        
        return self._calculate_latency_stats(latencies, 'end_to_end')
    
    def _calculate_latency_stats(self, latencies: List[float], test_name: str) -> Dict[str, Any]:
        """Calcule les statistiques de latence"""
        if not latencies:
            return {
                'test_name': test_name,
                'avg_latency_ms': 0,
                'min_latency_ms': 0,
                'max_latency_ms': 0,
                'median_latency_ms': 0,
                'std_deviation_ms': 0,
                'success_rate': 0,
                'total_tests': 0
            }
        
        return {
            'test_name': test_name,
            'avg_latency_ms': statistics.mean(latencies),
            'min_latency_ms': min(latencies),
            'max_latency_ms': max(latencies),
            'median_latency_ms': statistics.median(latencies),
            'std_deviation_ms': statistics.stdev(latencies) if len(latencies) > 1 else 0,
            'success_rate': len(latencies) / self.test_iterations * 100,
            'total_tests': len(latencies)
        }
    
    def _generate_sample_market_data(self) -> Dict[str, Any]:
        """Génère des données marché d'exemple"""
        return {
            'symbol': 'ES',
            'timestamp': datetime.now(),
            'open': 4500.0,
            'high': 4510.0,
            'low': 4490.0,
            'close': 4505.0,
            'volume': 100000,
            'vwap': 4502.5,
            'price_data': pd.DataFrame({
                'timestamp': pd.date_range(start=datetime.now() - timedelta(hours=1), 
                                         periods=60, freq='1min'),
                'open': np.random.uniform(4490, 4510, 60),
                'high': np.random.uniform(4510, 4520, 60),
                'low': np.random.uniform(4480, 4500, 60),
                'close': np.random.uniform(4490, 4510, 60),
                'volume': np.random.randint(1000, 10000, 60)
            })
        }
    
    async def run_complete_latency_test(self) -> Dict[str, Any]:
        """Exécute le test de latence complet"""
        logger.info("🚀 Démarrage test performance latence complet...")
        
        # Initialize components
        if not await self.initialize_components():
            return {'error': 'Échec initialisation composants'}
        
        # Run all tests
        tests = [
            self.test_battle_navale_latency(),
            self.test_confluence_analyzer_latency(),
            self.test_ibkr_connection_latency(),
            self.test_market_data_latency(),
            self.test_end_to_end_latency()
        ]
        
        results = {}
        for test in tests:
            result = await test
            results[result['test_name']] = result
        
        # Calculate overall performance
        overall_stats = self._calculate_overall_performance(results)
        results['overall_performance'] = overall_stats
        
        self.results = results
        return results
    
    def _calculate_overall_performance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule les statistiques de performance globales"""
        total_latency = sum(result.get('avg_latency_ms', 0) for result in results.values())
        avg_latency = total_latency / len(results) if results else 0
        
        # Check against targets
        targets = LATENCY_TARGETS_BY_STRATEGY['day_trading']
        is_acceptable = is_latency_acceptable(avg_latency, 'day_trading')
        
        return {
            'total_avg_latency_ms': avg_latency,
            'target_latency_ms': targets['max_total_latency_ms'],
            'is_acceptable': is_acceptable,
            'performance_grade': self._calculate_performance_grade(avg_latency),
            'recommendations': self._generate_recommendations(results)
        }
    
    def _calculate_performance_grade(self, avg_latency: float) -> str:
        """Calcule la note de performance"""
        if avg_latency <= 100:
            return "A+ (Excellent)"
        elif avg_latency <= 150:
            return "A (Très bon)"
        elif avg_latency <= 200:
            return "B (Bon)"
        elif avg_latency <= 250:
            return "C (Acceptable)"
        else:
            return "D (Problématique)"
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Génère des recommandations d'optimisation"""
        recommendations = []
        
        for test_name, result in results.items():
            avg_latency = result.get('avg_latency_ms', 0)
            
            if test_name == 'battle_navale' and avg_latency > 25:
                recommendations.append("🔧 Optimiser Battle Navale: Réduire complexité calculs")
            
            elif test_name == 'confluence_analyzer' and avg_latency > 20:
                recommendations.append("🔧 Optimiser Confluence: Cache multi-timeframe")
            
            elif test_name == 'ibkr_connection' and avg_latency > 50:
                recommendations.append("🔧 Optimiser IBKR: Connection pooling, keepalive")
            
            elif test_name == 'end_to_end' and avg_latency > 150:
                recommendations.append("🔧 Optimiser pipeline: Parallélisation, cache intelligent")
        
        if not recommendations:
            recommendations.append("✅ Performance optimale - Aucune optimisation requise")
        
        return recommendations
    
    def print_results(self):
        """Affiche les résultats de manière formatée"""
        if not self.results:
            logger.warning("⚠️ Aucun résultat à afficher")
            return
        
        print("\n" + "="*60)
        print("📊 RÉSULTATS TEST PERFORMANCE LATENCE")
        print("="*60)
        
        for test_name, result in self.results.items():
            if test_name == 'overall_performance':
                continue
                
            print(f"\n🔍 {test_name.upper().replace('_', ' ')}:")
            print(f"   ⏱️  Latence moyenne: {result['avg_latency_ms']:.2f}ms")
            print(f"   📈 Latence min/max: {result['min_latency_ms']:.2f}ms / {result['max_latency_ms']:.2f}ms")
            print(f"   📊 Médiane: {result['median_latency_ms']:.2f}ms")
            print(f"   🎯 Taux succès: {result['success_rate']:.1f}%")
        
        if 'overall_performance' in self.results:
            overall = self.results['overall_performance']
            print(f"\n🏆 PERFORMANCE GLOBALE:")
            print(f"   ⏱️  Latence totale: {overall['total_avg_latency_ms']:.2f}ms")
            print(f"   🎯 Cible: {overall['target_latency_ms']}ms")
            print(f"   ✅ Acceptable: {overall['is_acceptable']}")
            print(f"   📊 Note: {overall['performance_grade']}")
            
            print(f"\n💡 RECOMMANDATIONS:")
            for rec in overall['recommendations']:
                print(f"   {rec}")

# === MAIN TEST FUNCTION ===

async def main():
    """Fonction principale de test"""
    print("🚀 MIA_IA_SYSTEM - Test Performance Latence")
    print("="*50)
    
    # Configuration test
    config = {
        'test_iterations': 50,  # Réduire pour test rapide
        'ibkr_config': {
            'host': '127.0.0.1',
            'port': 7497,
            'client_id': 999
        }
    }
    
    # Create tester
    tester = LatencyPerformanceTester(config)
    
    try:
        # Run complete test
        results = await tester.run_complete_latency_test()
        
        # Display results
        tester.print_results()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"data/performance/latency_test_results_{timestamp}.json"
        
        import json
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Résultats sauvegardés: {results_file}")
        
    except Exception as e:
        logger.error(f"❌ Erreur test performance: {e}")
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 