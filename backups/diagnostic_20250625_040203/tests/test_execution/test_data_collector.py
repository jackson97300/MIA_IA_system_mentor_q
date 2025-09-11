"""
Tests pour le Data Collector MIA_IA_SYSTEM
Validation complète du système de collection de données Battle Navale
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

# Imports du système MIA_IA_SYSTEM
import sys
import logging

# Configure logging
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from data.data_collector import DataCollector
from data.market_data_feed import MarketDataFeed
from core.battle_navale import BattleNavale
from config.automation_config import DATA_COLLECTION_CONFIG


class TestDataCollector(unittest.TestCase):
    """Tests complets pour le Data Collector"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Configuration test
        self.test_config = {
            'data_path': self.temp_dir,
            'sources': {
                'ibkr_market_data': True,
                'sierra_chart_data': True,
                'battle_navale_signals': True,
                'system_metrics': True,
                'performance_data': True
            },
            'storage': {
                'format': 'json',
                'compression': 'gzip',
                'retention_days': 30
            },
            'real_time': True,
            'snapshot_frequency': 'every_trade'
        }
        
        # Mock des dépendances
        self.mock_battle_navale = Mock(spec=BattleNavale)
        self.mock_market_feed = Mock(spec=MarketDataFeed)
        
        # Création du collector avec config test
        self.data_collector = DataCollector(
            config=self.test_config,
            battle_navale=self.mock_battle_navale,
            market_feed=self.mock_market_feed
        )
        
        # Données de test
        self.sample_trade_data = {
            'timestamp': '2025-06-23T14:30:15.123Z',
            'trade_id': 'TRADE_20250623_143015_001',
            'symbol': 'EURUSD',
            'action': 'BUY',
            'quantity': 10000,
            'price': 1.0891,
            'battle_navale': {
                'signal_type': 'VIKINGS_ATTACK',
                'pattern': 'elite_pattern_2',
                'confluence_score': 0.87,
                'features': [0.65, -0.23, 1.42, 0.78, -0.91, 2.15, 0.33, -1.67],
                'market_regime': 'TRENDING',
                'strength': 'HIGH'
            }
        }
        
        self.sample_signal_data = {
            'timestamp': '2025-06-23T14:29:45.678Z',
            'signal_id': 'SIG_20250623_142945_001',
            'symbol': 'EURUSD',
            'battle_navale_analysis': {
                'primary_pattern': 'elite_pattern_2',
                'confluence_score': 0.83,
                'vikings_defenseurs_mode': 'VIKINGS_DOMINANT'
            }
        }
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_data_collector_initialization(self):
        """Test : Initialisation correcte du Data Collector"""
        # Vérifier l'initialisation
        self.assertIsNotNone(self.data_collector)
        self.assertEqual(self.data_collector.config, self.test_config)
        self.assertTrue(self.data_collector.sources['ibkr_market_data'])
        self.assertTrue(self.data_collector.sources['battle_navale_signals'])
        
        # Vérifier création des dossiers
        expected_dirs = [
            'snapshots/daily',
            'snapshots/archive', 
            'live/current_session',
            'live/streaming',
            'processed',
            'backups/hourly'
        ]
        
        for dir_path in expected_dirs:
            full_path = os.path.join(self.temp_dir, dir_path)
            self.assertTrue(os.path.exists(full_path), f"Dossier manquant: {dir_path}")
    
    def test_connection_validation(self):
        """Test : Validation des connexions sources données"""
        # Mock des réponses de connexion
        self.mock_market_feed.test_ibkr_connection.return_value = True
        self.mock_market_feed.test_sierra_connection.return_value = True
        
        # Test validation connexions
        connections = self.data_collector.validate_connections()
        
        self.assertTrue(connections['ibkr'])
        self.assertTrue(connections['sierra'])
        self.mock_market_feed.test_ibkr_connection.assert_called_once()
        self.mock_market_feed.test_sierra_connection.assert_called_once()
    
    def test_connection_failure_handling(self):
        """Test : Gestion des échecs de connexion"""
        # Mock échec connexion IBKR
        self.mock_market_feed.test_ibkr_connection.return_value = False
        self.mock_market_feed.test_sierra_connection.return_value = True
        
        connections = self.data_collector.validate_connections()
        
        self.assertFalse(connections['ibkr'])
        self.assertTrue(connections['sierra'])
        
        # Vérifier que les alertes sont levées
        with self.assertLogs(level='ERROR') as log:
            self.data_collector.validate_connections()
            self.assertIn('IBKR connection failed', str(log.output))
    
    def test_trade_snapshot_collection(self):
        """Test : Collection des snapshots de trades"""
        # Mock des données Battle Navale
        self.mock_battle_navale.get_current_analysis.return_value = {
            'signal_type': 'VIKINGS_ATTACK',
            'pattern': 'elite_pattern_2',
            'confluence_score': 0.87,
            'features': [0.65, -0.23, 1.42, 0.78, -0.91, 2.15, 0.33, -1.67]
        }
        
        # Mock des données marché
        self.mock_market_feed.get_market_data.return_value = {
            'bid': 1.0890,
            'ask': 1.0892,
            'volume': 1250000,
            'volatility': 0.0145
        }
        
        # Collecter snapshot
        snapshot = self.data_collector.collect_trade_snapshot(self.sample_trade_data)
        
        # Vérifications
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot['trade_id'], 'TRADE_20250623_143015_001')
        self.assertEqual(snapshot['symbol'], 'EURUSD')
        self.assertIn('battle_navale', snapshot)
        self.assertIn('market_context', snapshot)
        self.assertEqual(len(snapshot['battle_navale']['features']), 8)
    
    def test_signal_snapshot_collection(self):
        """Test : Collection des snapshots de signaux"""
        # Mock données signal Battle Navale
        self.mock_battle_navale.generate_signal_snapshot.return_value = {
            'primary_pattern': 'elite_pattern_2',
            'confluence_score': 0.83,
            'features': [0.65, -0.23, 1.42, 0.78, -0.91, 2.15, 0.33, -1.67],
            'vikings_defenseurs_mode': 'VIKINGS_DOMINANT'
        }
        
        # Collecter snapshot signal
        snapshot = self.data_collector.collect_signal_snapshot(
            symbol='EURUSD',
            timeframe='5min'
        )
        
        # Vérifications
        self.assertIsNotNone(snapshot)
        self.assertIn('battle_navale_analysis', snapshot)
        self.assertIn('features_snapshot', snapshot)
        self.assertEqual(snapshot['symbol'], 'EURUSD')
        self.assertEqual(len(snapshot['features_snapshot']['raw_features']), 8)
    
    def test_data_storage_json(self):
        """Test : Stockage des données en format JSON"""
        # Stocker données
        result = self.data_collector.store_data(
            data=self.sample_trade_data,
            data_type='trade',
            timestamp=datetime.now()
        )
        
        self.assertTrue(result)
        
        # Vérifier fichier créé
        today = datetime.now().strftime('%Y-%m-%d')
        file_path = os.path.join(
            self.temp_dir, 
            'snapshots', 
            'daily', 
            today, 
            'trades.json'
        )
        
        self.assertTrue(os.path.exists(file_path))
        
        # Vérifier contenu
        with open(file_path, 'r') as f:
            stored_data = json.load(f)
            self.assertEqual(stored_data[0]['trade_id'], 'TRADE_20250623_143015_001')
    
    def test_data_storage_compression(self):
        """Test : Compression des données stockées"""
        # Configuration avec compression
        self.data_collector.config['storage']['compression'] = 'gzip'
        
        # Stocker données volumineuses
        large_data = {
            'trades': [self.sample_trade_data for _ in range(1000)],
            'timestamp': datetime.now().isoformat()
        }
        
        result = self.data_collector.store_data(
            data=large_data,
            data_type='bulk_trades',
            compress=True
        )
        
        self.assertTrue(result)
        
        # Vérifier fichier compressé existe
        today = datetime.now().strftime('%Y-%m-%d')
        file_path = os.path.join(
            self.temp_dir,
            'snapshots',
            'daily', 
            today,
            'bulk_trades.json.gz'
        )
        
        self.assertTrue(os.path.exists(file_path))
    
    def test_real_time_data_streaming(self):
        """Test : Streaming de données temps réel"""
        # Mock stream de données
        mock_stream_data = [
            {'timestamp': datetime.now(), 'symbol': 'EURUSD', 'price': 1.0891},
            {'timestamp': datetime.now(), 'symbol': 'EURUSD', 'price': 1.0892},
            {'timestamp': datetime.now(), 'symbol': 'EURUSD', 'price': 1.0893}
        ]
        
        self.mock_market_feed.get_real_time_stream.return_value = iter(mock_stream_data)
        
        # Démarrer streaming
        self.data_collector.start_real_time_collection()
        
        # Simuler réception données
        collected_data = []
        for data in self.data_collector.real_time_stream:
            collected_data.append(data)
            if len(collected_data) >= 3:
                break
        
        # Vérifications
        self.assertEqual(len(collected_data), 3)
        self.assertEqual(collected_data[0]['symbol'], 'EURUSD')
        self.assertAlmostEqual(collected_data[2]['price'], 1.0893)
    
    def test_data_validation(self):
        """Test : Validation de l'intégrité des données"""
        # Données valides
        valid_data = self.sample_trade_data.copy()
        is_valid = self.data_collector.validate_data(valid_data, 'trade')
        self.assertTrue(is_valid)
        
        # Données invalides - champs manquants
        invalid_data = self.sample_trade_data.copy()
        del invalid_data['symbol']
        is_valid = self.data_collector.validate_data(invalid_data, 'trade')
        self.assertFalse(is_valid)
        
        # Données invalides - features incomplètes
        invalid_features = self.sample_trade_data.copy()
        invalid_features['battle_navale']['features'] = [0.65, -0.23]  # Seulement 2 features au lieu de 8
        is_valid = self.data_collector.validate_data(invalid_features, 'trade')
        self.assertFalse(is_valid)
    
    def test_data_quality_monitoring(self):
        """Test : Monitoring de la qualité des données"""
        # Stocker quelques données avec différents niveaux de qualité
        good_data = self.sample_trade_data.copy()
        poor_data = self.sample_trade_data.copy()
        poor_data['battle_navale']['features'] = [None, None, 1.42, 0.78, None, 2.15, 0.33, None]
        
        self.data_collector.store_data(good_data, 'trade')
        self.data_collector.store_data(poor_data, 'trade')
        
        # Calculer métriques qualité
        quality_metrics = self.data_collector.calculate_data_quality()
        
        self.assertIn('completeness_score', quality_metrics)
        self.assertIn('missing_data_rate', quality_metrics)
        self.assertLessEqual(quality_metrics['completeness_score'], 1.0)
        self.assertGreaterEqual(quality_metrics['missing_data_rate'], 0.0)
    
    def test_backup_and_archival(self):
        """Test : Backup et archivage des données"""
        # Stocker des données de test
        for i in range(5):
            test_data = self.sample_trade_data.copy()
            test_data['trade_id'] = f'TRADE_TEST_{i:03d}'
            self.data_collector.store_data(test_data, 'trade')
        
        # Effectuer backup
        backup_result = self.data_collector.backup_data('hourly')
        self.assertTrue(backup_result)
        
        # Vérifier backup créé
        backup_dir = os.path.join(self.temp_dir, 'backups', 'hourly')
        self.assertTrue(os.path.exists(backup_dir))
        
        # Test archivage (données anciennes)
        old_date = datetime.now() - timedelta(days=100)
        archive_result = self.data_collector.archive_old_data(cutoff_date=old_date)
        self.assertTrue(archive_result)
    
    def test_performance_tracking(self):
        """Test : Tracking des performances de collection"""
        # Mesurer performance collection
        start_time = datetime.now()
        
        # Collecter beaucoup de données
        for i in range(100):
            test_data = self.sample_trade_data.copy()
            test_data['trade_id'] = f'PERF_TEST_{i:03d}'
            self.data_collector.store_data(test_data, 'trade')
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Calculer métriques
        performance_metrics = self.data_collector.get_performance_metrics()
        
        self.assertIn('collection_rate_per_second', performance_metrics)
        self.assertIn('average_latency_ms', performance_metrics)
        self.assertIn('storage_efficiency', performance_metrics)
        
        # Vérifier performance acceptable
        self.assertLess(duration, 5.0)  # Moins de 5 secondes pour 100 trades
        self.assertLess(performance_metrics['average_latency_ms'], 50)  # <50ms par trade
    
    def test_error_handling_and_recovery(self):
        """Test : Gestion d'erreurs et récupération"""
        # Test erreur stockage (espace disque insuffisant)
        with patch('os.path.exists', return_value=False):
            with patch('os.makedirs', side_effect=OSError("No space left")):
                result = self.data_collector.store_data(self.sample_trade_data, 'trade')
                self.assertFalse(result)
        
        # Test récupération après erreur
        self.data_collector.recover_from_error()
        
        # Vérifier que la collection peut reprendre
        result = self.data_collector.store_data(self.sample_trade_data, 'trade')
        self.assertTrue(result)
    
    def test_battle_navale_integration(self):
        """Test : Intégration spécifique Battle Navale"""
        # Mock données Battle Navale complexes
        self.mock_battle_navale.get_current_analysis.return_value = {
            'signal_type': 'VIKINGS_ATTACK',
            'primary_pattern': 'elite_pattern_2',
            'secondary_patterns': ['support_pattern_a', 'momentum_pattern_x'],
            'confluence_levels': {
                'technical': 0.85,
                'fundamental': 0.72,
                'sentiment': 0.91,
                'overall': 0.83
            },
            'vikings_defenseurs': {
                'mode': 'VIKINGS_DOMINANT',
                'strength': 8.5,
                'momentum': 'INCREASING'
            },
            'features': [0.65, -0.23, 1.42, 0.78, -0.91, 2.15, 0.33, -1.67],
            'feature_importance': [0.15, 0.08, 0.22, 0.18, 0.12, 0.09, 0.07, 0.09]
        }
        
        # Collecter snapshot Battle Navale
        snapshot = self.data_collector.collect_battle_navale_snapshot('EURUSD')
        
        # Vérifications spécifiques Battle Navale
        self.assertEqual(snapshot['signal_type'], 'VIKINGS_ATTACK')
        self.assertEqual(len(snapshot['features']), 8)
        self.assertEqual(len(snapshot['feature_importance']), 8)
        self.assertIn('vikings_defenseurs', snapshot)
        self.assertEqual(snapshot['vikings_defenseurs']['mode'], 'VIKINGS_DOMINANT')
    
    def test_ml_dataset_preparation(self):
        """Test : Préparation des datasets pour ML"""
        # Stocker données variées pour ML
        for i in range(20):
            trade_data = self.sample_trade_data.copy()
            trade_data['trade_id'] = f'ML_TRADE_{i:03d}'
            # Varier les features et résultats
            trade_data['battle_navale']['features'] = [
                np.random.normal(0, 1) for _ in range(8)
            ]
            trade_data['result'] = 'WIN' if i % 2 == 0 else 'LOSS'
            self.data_collector.store_data(trade_data, 'trade')
        
        # Préparer dataset ML
        features_df, labels_df = self.data_collector.prepare_ml_dataset(
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now()
        )
        
        # Vérifications
        self.assertIsInstance(features_df, pd.DataFrame)
        self.assertIsInstance(labels_df, pd.DataFrame)
        self.assertEqual(len(features_df), 20)
        self.assertEqual(len(labels_df), 20)
        self.assertEqual(features_df.shape[1], 8)  # 8 features Battle Navale


class TestDataCollectorIntegration(unittest.TestCase):
    """Tests d'intégration avec les autres composants"""
    
    def setUp(self):
        """Setup pour tests d'intégration"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Configuration réaliste
        self.integration_config = DATA_COLLECTION_CONFIG.copy()
        self.integration_config['data_path'] = self.temp_dir
    
    def tearDown(self):
        """Nettoyage"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('data.market_data_feed.MarketDataFeed')
    @patch('core.battle_navale.BattleNavale')
    def test_end_to_end_collection(self, mock_battle_navale_class, mock_market_feed_class):
        """Test : Collection end-to-end complète"""
        # Setup mocks
        mock_battle_navale = mock_battle_navale_class.return_value
        mock_market_feed = mock_market_feed_class.return_value
        
        mock_battle_navale.generate_signals.return_value = [
            {
                'signal_type': 'VIKINGS_ATTACK',
                'confidence': 0.87,
                'features': [0.65, -0.23, 1.42, 0.78, -0.91, 2.15, 0.33, -1.67]
            }
        ]
        
        mock_market_feed.get_market_data.return_value = {
            'EURUSD': {'bid': 1.0890, 'ask': 1.0892, 'volume': 1000000}
        }
        
        # Créer collector avec vraies dépendances mockées
        collector = DataCollector(
            config=self.integration_config,
            battle_navale=mock_battle_navale,
            market_feed=mock_market_feed
        )
        
        # Simuler session de trading
        collector.start_collection_session()
        
        # Simuler quelques cycles de collection
        for _ in range(5):
            collector.collect_market_cycle()
        
        collector.end_collection_session()
        
        # Vérifier que les données ont été collectées
        today = datetime.now().strftime('%Y-%m-%d')
        session_dir = os.path.join(self.temp_dir, 'snapshots', 'daily', today)
        self.assertTrue(os.path.exists(session_dir))


if __name__ == '__main__':
    # Configuration des tests
    unittest.TestLoader.sortTestMethodsUsing = None
    
    # Suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDataCollector)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDataCollectorIntegration))
    
    # Exécution avec rapport détaillé
    runner = unittest.TextTestRunner(
        verbosity=2,
        buffer=True,
        failfast=False
    )
    
    logger.info("🧪 DÉMARRAGE DES TESTS DATA COLLECTOR")
    print("=" * 50)
    
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        logger.info("TOUS LES TESTS DATA COLLECTOR RÉUSSIS !")
    else:
        logger.error("{len(result.failures)} ÉCHECS, {len(result.errors)} ERREURS")
        
    logger.info("📊 Tests exécutés: {result.testsRun}")
    logger.info("⏱️  Temps d'exécution: {result.stop_time - result.start_time:.2f}s")