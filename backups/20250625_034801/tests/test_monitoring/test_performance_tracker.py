"""
Tests pour le Performance Tracker MIA_IA_SYSTEM
Validation complète du monitoring de performance Battle Navale
"""

import unittest
import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, call
import pandas as pd
import numpy as np
from collections import defaultdict
import time

# Imports du système MIA_IA_SYSTEM
import sys
import logging

# Configure logging
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from monitoring.performance_tracker import PerformanceTracker
from monitoring.live_monitor import LiveMonitor
from core.battle_navale import BattleNavale
from config.automation_config import PERFORMANCE_CONFIG


class TestPerformanceTracker(unittest.TestCase):
    """Tests complets pour le Performance Tracker"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Configuration test
        self.test_config = {
            'data_path': self.temp_dir,
            'tracking_interval': 1,  # 1 seconde pour tests rapides
            'metrics': {
                'latency_threshold_ms': 10,
                'memory_threshold_mb': 512,
                'cpu_threshold_percent': 80,
                'success_rate_threshold': 0.75,
                'drawdown_threshold': 0.05
            },
            'battle_navale': {
                'track_confluence_performance': True,
                'track_pattern_success': True,
                'track_feature_importance': True,
                'track_regime_accuracy': True
            },
            'alerts': {
                'performance_degradation': True,
                'system_lag': True,
                'trading_anomalies': True
            }
        }
        
        # Mock des dépendances
        self.mock_battle_navale = Mock(spec=BattleNavale)
        self.mock_live_monitor = Mock(spec=LiveMonitor)
        
        # Création du performance tracker
        self.performance_tracker = PerformanceTracker(
            config=self.test_config,
            battle_navale=self.mock_battle_navale,
            live_monitor=self.mock_live_monitor
        )
        
        # Données de test - Trades historiques
        self.sample_trades = [
            {
                'timestamp': '2025-06-23T10:30:15.123Z',
                'trade_id': 'TRADE_001',
                'symbol': 'EURUSD',
                'action': 'BUY',
                'entry_price': 1.0890,
                'exit_price': 1.0920,
                'quantity': 10000,
                'pnl': 300.0,
                'result': 'WIN',
                'duration_minutes': 15,
                'battle_navale': {
                    'signal_type': 'VIKINGS_ATTACK',
                    'pattern': 'elite_pattern_2',
                    'confluence_score': 0.87,
                    'features': [0.65, -0.23, 1.42, 0.78, -0.91, 2.15, 0.33, -1.67],
                    'execution_latency_ms': 2.3
                }
            },
            {
                'timestamp': '2025-06-23T11:45:30.456Z',
                'trade_id': 'TRADE_002',
                'symbol': 'GBPUSD',
                'action': 'SELL',
                'entry_price': 1.2650,
                'exit_price': 1.2620,
                'quantity': 8000,
                'pnl': 240.0,
                'result': 'WIN',
                'duration_minutes': 25,
                'battle_navale': {
                    'signal_type': 'DEFENSEURS_HOLD',
                    'pattern': 'elite_pattern_1',
                    'confluence_score': 0.82,
                    'features': [0.45, -0.67, 0.92, 1.23, -0.45, 1.78, 0.12, -0.89],
                    'execution_latency_ms': 1.8
                }
            },
            {
                'timestamp': '2025-06-23T13:20:45.789Z',
                'trade_id': 'TRADE_003',
                'symbol': 'EURUSD',
                'action': 'BUY',
                'entry_price': 1.0895,
                'exit_price': 1.0875,
                'quantity': 12000,
                'pnl': -240.0,
                'result': 'LOSS',
                'duration_minutes': 8,
                'battle_navale': {
                    'signal_type': 'VIKINGS_ATTACK',
                    'pattern': 'elite_pattern_3',
                    'confluence_score': 0.71,
                    'features': [0.23, -0.89, 0.67, 0.34, -1.23, 1.45, 0.78, -0.56],
                    'execution_latency_ms': 4.1
                }
            }
        ]
        
        # Métriques système de test
        self.sample_system_metrics = {
            'cpu_usage': 45.2,
            'memory_usage_mb': 256.7,
            'disk_usage_gb': 12.3,
            'network_latency_ms': 1.5,
            'active_connections': 3
        }
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_performance_tracker_initialization(self):
        """Test : Initialisation correcte du Performance Tracker"""
        # Vérifier l'initialisation
        self.assertIsNotNone(self.performance_tracker)
        self.assertEqual(self.performance_tracker.config, self.test_config)
        self.assertTrue(self.performance_tracker.battle_navale_tracking)
        
        # Vérifier création des structures de données
        self.assertIsInstance(self.performance_tracker.trades_history, list)
        self.assertIsInstance(self.performance_tracker.system_metrics, dict)
        self.assertIsInstance(self.performance_tracker.battle_navale_metrics, dict)
        
        # Vérifier métriques Battle Navale initialisées
        bn_metrics = self.performance_tracker.battle_navale_metrics
        self.assertIn('pattern_success_rates', bn_metrics)
        self.assertIn('confluence_performance', bn_metrics)
        self.assertIn('feature_importance_history', bn_metrics)
    
    def test_trade_performance_tracking(self):
        """Test : Tracking des performances de trading"""
        # Ajouter les trades de test
        for trade in self.sample_trades:
            self.performance_tracker.add_trade(trade)
        
        # Calculer métriques de performance
        metrics = self.performance_tracker.calculate_trading_metrics()
        
        # Vérifications générales
        self.assertIn('total_trades', metrics)
        self.assertIn('win_rate', metrics)
        self.assertIn('total_pnl', metrics)
        self.assertIn('average_pnl_per_trade', metrics)
        self.assertIn('max_drawdown', metrics)
        
        # Vérifications spécifiques
        self.assertEqual(metrics['total_trades'], 3)
        self.assertAlmostEqual(metrics['win_rate'], 2/3, places=2)  # 2 wins sur 3 trades
        self.assertEqual(metrics['total_pnl'], 300.0)  # 300 + 240 - 240
        self.assertAlmostEqual(metrics['average_pnl_per_trade'], 100.0, places=1)
    
    def test_battle_navale_pattern_tracking(self):
        """Test : Tracking des performances par pattern Battle Navale"""
        # Ajouter trades avec différents patterns
        for trade in self.sample_trades:
            self.performance_tracker.add_trade(trade)
        
        # Calculer métriques par pattern
        pattern_metrics = self.performance_tracker.calculate_pattern_performance()
        
        # Vérifications
        self.assertIn('elite_pattern_1', pattern_metrics)
        self.assertIn('elite_pattern_2', pattern_metrics)
        self.assertIn('elite_pattern_3', pattern_metrics)
        
        # Pattern 1 (1 trade, 1 win)
        pattern_1 = pattern_metrics['elite_pattern_1']
        self.assertEqual(pattern_1['total_trades'], 1)
        self.assertEqual(pattern_1['wins'], 1)
        self.assertEqual(pattern_1['win_rate'], 1.0)
        
        # Pattern 2 (1 trade, 1 win)
        pattern_2 = pattern_metrics['elite_pattern_2']
        self.assertEqual(pattern_2['total_trades'], 1)
        self.assertEqual(pattern_2['wins'], 1)
        self.assertEqual(pattern_2['win_rate'], 1.0)
        
        # Pattern 3 (1 trade, 1 loss)
        pattern_3 = pattern_metrics['elite_pattern_3']
        self.assertEqual(pattern_3['total_trades'], 1)
        self.assertEqual(pattern_3['wins'], 0)
        self.assertEqual(pattern_3['win_rate'], 0.0)
    
    def test_confluence_score_performance(self):
        """Test : Performance en fonction du score de confluence"""
        # Ajouter trades
        for trade in self.sample_trades:
            self.performance_tracker.add_trade(trade)
        
        # Analyser performance par confluence
        confluence_analysis = self.performance_tracker.analyze_confluence_performance()
        
        # Vérifications
        self.assertIn('high_confluence', confluence_analysis)  # >0.8
        self.assertIn('medium_confluence', confluence_analysis)  # 0.6-0.8
        self.assertIn('low_confluence', confluence_analysis)  # <0.6
        
        # High confluence (0.87, 0.82) - 2 trades, 2 wins
        high_conf = confluence_analysis['high_confluence']
        self.assertEqual(high_conf['trades'], 2)
        self.assertEqual(high_conf['wins'], 2)
        self.assertEqual(high_conf['win_rate'], 1.0)
        
        # Medium confluence (0.71) - 1 trade, 0 wins
        medium_conf = confluence_analysis['medium_confluence']
        self.assertEqual(medium_conf['trades'], 1)
        self.assertEqual(medium_conf['wins'], 0)
        self.assertEqual(medium_conf['win_rate'], 0.0)
    
    def test_execution_latency_tracking(self):
        """Test : Tracking de la latence d'exécution"""
        # Ajouter trades
        for trade in self.sample_trades:
            self.performance_tracker.add_trade(trade)
        
        # Calculer métriques de latence
        latency_metrics = self.performance_tracker.calculate_latency_metrics()
        
        # Vérifications
        self.assertIn('average_latency_ms', latency_metrics)
        self.assertIn('max_latency_ms', latency_metrics)
        self.assertIn('min_latency_ms', latency_metrics)
        self.assertIn('latency_under_threshold_rate', latency_metrics)
        
        # Calculs attendus (2.3, 1.8, 4.1)
        expected_avg = (2.3 + 1.8 + 4.1) / 3
        self.assertAlmostEqual(latency_metrics['average_latency_ms'], expected_avg, places=1)
        self.assertEqual(latency_metrics['max_latency_ms'], 4.1)
        self.assertEqual(latency_metrics['min_latency_ms'], 1.8)
        
        # 2 sur 3 trades sous le seuil de 10ms
        self.assertAlmostEqual(latency_metrics['latency_under_threshold_rate'], 1.0, places=1)
    
    def test_feature_importance_tracking(self):
        """Test : Tracking de l'importance des features Battle Navale"""
        # Mock de l'analyse d'importance des features
        self.mock_battle_navale.calculate_feature_importance.return_value = [
            0.15, 0.08, 0.22, 0.18, 0.12, 0.09, 0.07, 0.09
        ]
        
        # Ajouter trades et calculer importance
        for trade in self.sample_trades:
            self.performance_tracker.add_trade(trade)
        
        importance_analysis = self.performance_tracker.analyze_feature_importance()
        
        # Vérifications
        self.assertEqual(len(importance_analysis['current_importance']), 8)
        self.assertIn('importance_changes', importance_analysis)
        self.assertIn('top_features', importance_analysis)
        
        # Vérifier que la feature 3 (index 2) est la plus importante (0.22)
        top_features = importance_analysis['top_features']
        self.assertEqual(top_features[0]['feature_index'], 2)
        self.assertEqual(top_features[0]['importance'], 0.22)
    
    def test_system_performance_monitoring(self):
        """Test : Monitoring des performances système"""
        # Ajouter métriques système
        self.performance_tracker.add_system_metrics(self.sample_system_metrics)
        
        # Calculer métriques système
        system_perf = self.performance_tracker.calculate_system_performance()
        
        # Vérifications
        self.assertIn('cpu_usage', system_perf)
        self.assertIn('memory_usage_mb', system_perf)
        self.assertIn('network_latency_ms', system_perf)
        self.assertIn('system_health_score', system_perf)
        
        # Valeurs attendues
        self.assertEqual(system_perf['cpu_usage'], 45.2)
        self.assertEqual(system_perf['memory_usage_mb'], 256.7)
        self.assertEqual(system_perf['network_latency_ms'], 1.5)
        
        # Score de santé système (basé sur seuils)
        self.assertGreater(system_perf['system_health_score'], 0.8)  # Bonnes performances
    
    def test_performance_alerts(self):
        """Test : Système d'alertes de performance"""
        # Ajouter trade avec latence élevée
        bad_trade = self.sample_trades[0].copy()
        bad_trade['battle_navale']['execution_latency_ms'] = 15.0  # Au-dessus du seuil
        
        alerts = self.performance_tracker.check_performance_alerts(bad_trade)
        
        # Vérifier alerte de latence
        latency_alerts = [a for a in alerts if a['type'] == 'high_latency']
        self.assertEqual(len(latency_alerts), 1)
        self.assertEqual(latency_alerts[0]['severity'], 'WARNING')
        
        # Test alerte faible confluence
        low_conf_trade = self.sample_trades[0].copy()
        low_conf_trade['battle_navale']['confluence_score'] = 0.45  # Très faible
        
        alerts = self.performance_tracker.check_performance_alerts(low_conf_trade)
        conf_alerts = [a for a in alerts if a['type'] == 'low_confluence']
        self.assertEqual(len(conf_alerts), 1)
    
    def test_drawdown_calculation(self):
        """Test : Calcul du drawdown maximum"""
        # Créer série de trades avec drawdown
        drawdown_trades = [
            {'pnl': 100, 'timestamp': '2025-06-23T10:00:00Z'},
            {'pnl': 200, 'timestamp': '2025-06-23T10:15:00Z'},
            {'pnl': -150, 'timestamp': '2025-06-23T10:30:00Z'},  # Début drawdown
            {'pnl': -200, 'timestamp': '2025-06-23T10:45:00Z'},  # Max drawdown
            {'pnl': -100, 'timestamp': '2025-06-23T11:00:00Z'},
            {'pnl': 50, 'timestamp': '2025-06-23T11:15:00Z'},    # Fin drawdown
        ]
        
        for trade in drawdown_trades:
            self.performance_tracker.add_trade(trade)
        
        drawdown_analysis = self.performance_tracker.calculate_drawdown()
        
        # Vérifications
        self.assertIn('max_drawdown', drawdown_analysis)
        self.assertIn('current_drawdown', drawdown_analysis)
        self.assertIn('drawdown_duration', drawdown_analysis)
        
        # Max drawdown devrait être autour de -350 depuis le pic de 300
        self.assertLess(drawdown_analysis['max_drawdown'], -300)
    
    def test_real_time_performance_monitoring(self):
        """Test : Monitoring de performance temps réel"""
        # Simuler monitoring temps réel
        with patch('time.time') as mock_time:
            mock_time.return_value = 1000.0
            
            # Démarrer monitoring
            self.performance_tracker.start_real_time_monitoring()
            
            # Simuler quelques cycles
            for i in range(5):
                mock_time.return_value = 1000.0 + i
                
                # Ajouter métriques
                metrics = self.sample_system_metrics.copy()
                metrics['cpu_usage'] = 50 + i * 5  # CPU qui augmente
                self.performance_tracker.add_system_metrics(metrics)
                
                # Process monitoring cycle
                self.performance_tracker.process_monitoring_cycle()
            
            # Arrêter monitoring
            self.performance_tracker.stop_real_time_monitoring()
        
        # Vérifier historique collecté
        metrics_history = self.performance_tracker.get_metrics_history()
        self.assertEqual(len(metrics_history), 5)
        self.assertEqual(metrics_history[-1]['cpu_usage'], 70)  # 50 + 4*5
    
    def test_performance_regression_detection(self):
        """Test : Détection de régression de performance"""
        # Ajouter période de bonnes performances
        good_period_start = datetime.now() - timedelta(days=7)
        for i in range(10):
            trade = {
                'timestamp': (good_period_start + timedelta(hours=i)).isoformat(),
                'pnl': 100 + i * 10,  # Performances croissantes
                'result': 'WIN',
                'battle_navale': {
                    'execution_latency_ms': 2.0,
                    'confluence_score': 0.85
                }
            }
            self.performance_tracker.add_trade(trade)
        
        # Ajouter période de mauvaises performances
        bad_period_start = datetime.now() - timedelta(days=1)
        for i in range(5):
            trade = {
                'timestamp': (bad_period_start + timedelta(hours=i)).isoformat(),
                'pnl': -50 - i * 20,  # Performances dégradées
                'result': 'LOSS',
                'battle_navale': {
                    'execution_latency_ms': 8.0,
                    'confluence_score': 0.65
                }
            }
            self.performance_tracker.add_trade(trade)
        
        # Détecter régression
        regression_analysis = self.performance_tracker.detect_performance_regression()
        
        # Vérifications
        self.assertTrue(regression_analysis['regression_detected'])
        self.assertIn('pnl_decline', regression_analysis)
        self.assertIn('latency_increase', regression_analysis)
        self.assertIn('confluence_decline', regression_analysis)
    
    def test_battle_navale_signal_quality_tracking(self):
        """Test : Tracking de la qualité des signaux Battle Navale"""
        # Mock données de qualité des signaux
        signal_quality_data = [
            {
                'timestamp': datetime.now(),
                'signal_type': 'VIKINGS_ATTACK',
                'quality_score': 0.92,
                'pattern_strength': 8.5,
                'market_conditions': 'TRENDING'
            },
            {
                'timestamp': datetime.now(),
                'signal_type': 'DEFENSEURS_HOLD',
                'quality_score': 0.78,
                'pattern_strength': 6.2,
                'market_conditions': 'RANGING'
            }
        ]
        
        # Ajouter données de qualité
        for signal_data in signal_quality_data:
            self.performance_tracker.track_signal_quality(signal_data)
        
        # Analyser qualité des signaux
        quality_analysis = self.performance_tracker.analyze_signal_quality()
        
        # Vérifications
        self.assertIn('average_quality_score', quality_analysis)
        self.assertIn('quality_by_signal_type', quality_analysis)
        self.assertIn('quality_trend', quality_analysis)
        
        # Scores par type de signal
        by_type = quality_analysis['quality_by_signal_type']
        self.assertIn('VIKINGS_ATTACK', by_type)
        self.assertIn('DEFENSEURS_HOLD', by_type)
        self.assertEqual(by_type['VIKINGS_ATTACK']['avg_quality'], 0.92)
        self.assertEqual(by_type['DEFENSEURS_HOLD']['avg_quality'], 0.78)
    
    def test_performance_export_and_reporting(self):
        """Test : Export et rapports de performance"""
        # Ajouter données de test
        for trade in self.sample_trades:
            self.performance_tracker.add_trade(trade)
        
        self.performance_tracker.add_system_metrics(self.sample_system_metrics)
        
        # Générer rapport complet
        report = self.performance_tracker.generate_performance_report(
            period_days=1,
            include_charts=False  # Pas de graphiques pour les tests
        )
        
        # Vérifications structure rapport
        self.assertIn('summary', report)
        self.assertIn('trading_performance', report)
        self.assertIn('battle_navale_analysis', report)
        self.assertIn('system_performance', report)
        self.assertIn('recommendations', report)
        
        # Vérifier contenu trading
        trading_perf = report['trading_performance']
        self.assertEqual(trading_perf['total_trades'], 3)
        self.assertAlmostEqual(trading_perf['win_rate'], 0.67, places=2)
        
        # Export en JSON
        json_report = self.performance_tracker.export_performance_data('json')
        self.assertIsInstance(json_report, str)
        parsed_report = json.loads(json_report)
        self.assertIn('metadata', parsed_report)
        self.assertIn('performance_data', parsed_report)
    
    def test_performance_comparison(self):
        """Test : Comparaison de performances entre périodes"""
        # Période 1 (semaine dernière)
        period1_start = datetime.now() - timedelta(days=14)
        for i in range(10):
            trade = {
                'timestamp': (period1_start + timedelta(hours=i*2)).isoformat(),
                'pnl': 80 + i * 5,
                'result': 'WIN' if i % 3 != 0 else 'LOSS',
                'battle_navale': {
                    'confluence_score': 0.75 + i * 0.01,
                    'execution_latency_ms': 3.0
                }
            }
            self.performance_tracker.add_trade(trade)
        
        # Période 2 (cette semaine)
        period2_start = datetime.now() - timedelta(days=7)
        for i in range(10):
            trade = {
                'timestamp': (period2_start + timedelta(hours=i*2)).isoformat(),
                'pnl': 120 + i * 8,
                'result': 'WIN' if i % 2 == 0 else 'LOSS',
                'battle_navale': {
                    'confluence_score': 0.80 + i * 0.015,
                    'execution_latency_ms': 2.5
                }
            }
            self.performance_tracker.add_trade(trade)
        
        # Comparer périodes
        comparison = self.performance_tracker.compare_periods(
            period1_days=14,
            period2_days=7
        )
        
        # Vérifications
        self.assertIn('period1_metrics', comparison)
        self.assertIn('period2_metrics', comparison)
        self.assertIn('improvements', comparison)
        self.assertIn('degradations', comparison)
        
        # Vérifier améliorations détectées
        improvements = comparison['improvements']
        self.assertIn('average_pnl', improvements)  # PnL plus élevé période 2
        self.assertIn('execution_latency', improvements)  # Latence réduite


class TestPerformanceTrackerIntegration(unittest.TestCase):
    """Tests d'intégration avec monitoring temps réel"""
    
    def setUp(self):
        """Setup pour tests d'intégration"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = PERFORMANCE_CONFIG.copy()
        self.config['data_path'] = self.temp_dir
    
    def tearDown(self):
        """Nettoyage"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('monitoring.live_monitor.LiveMonitor')
    @patch('core.battle_navale.BattleNavale')
    def test_integration_with_live_monitor(self, mock_battle_navale_class, mock_live_monitor_class):
        """Test : Intégration avec le monitoring temps réel"""
        # Setup mocks
        mock_battle_navale = mock_battle_navale_class.return_value
        mock_live_monitor = mock_live_monitor_class.return_value
        
        # Créer tracker intégré
        tracker = PerformanceTracker(
            config=self.config,
            battle_navale=mock_battle_navale,
            live_monitor=mock_live_monitor
        )
        
        # Simuler session de monitoring
        tracker.start_integrated_monitoring()
        
        # Simuler quelques événements
        mock_live_monitor.get_current_metrics.return_value = {
            'system_health': 0.95,
            'active_trades': 2,
            'pending_signals': 1
        }
        
        # Process quelques cycles
        for _ in range(3):
            tracker.process_monitoring_cycle()
        
        tracker.stop_integrated_monitoring()
        
        # Vérifier intégration fonctionnelle
        self.assertTrue(mock_live_monitor.get_current_metrics.called)


if __name__ == '__main__':
    # Configuration des tests
    unittest.TestLoader.sortTestMethodsUsing = None
    
    # Suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPerformanceTracker)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPerformanceTrackerIntegration))
    
    # Exécution avec rapport détaillé
    runner = unittest.TextTestRunner(
        verbosity=2,
        buffer=True,
        failfast=False
    )
    
    logger.info("🧪 DÉMARRAGE DES TESTS PERFORMANCE TRACKER")
    print("=" * 50)
    
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        logger.info("TOUS LES TESTS PERFORMANCE TRACKER RÉUSSIS !")
    else:
        logger.error("{len(result.failures)} ÉCHECS, {len(result.errors)} ERREURS")
        
    logger.info("📊 Tests exécutés: {result.testsRun}")
    logger.info("⏱️  Temps d'exécution: {result.stop_time - result.start_time:.2f}s")
    logger.info("\n🎯 MÉTRIQUES BATTLE NAVALE VALIDÉES :")
    logger.info("   • Performance par pattern elite")
    logger.info("   • Analyse confluence scores")
    logger.info("   • Tracking latence <10ms")
    logger.info("   • Détection régression automatique")