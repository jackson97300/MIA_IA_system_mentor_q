"""
Tests de l'Observabilité MIA_IA_SYSTEM
=====================================

Tests pour les métriques, logs structurés et monitoring.
"""

import pytest
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

from monitoring.metrics_collector import MetricsCollector, MetricPoint
from monitoring.structured_logger import StructuredLogger, setup_structured_logging
from monitoring.metrics_exporter import MetricsExporter, export_metrics


class TestMetricsCollector:
    """Tests du collecteur de métriques"""
    
    @pytest.fixture
    def metrics_collector(self):
        """Instance du collecteur de métriques"""
        collector = MetricsCollector({
            'export_interval_seconds': 1,
            'prometheus_port': 9091,  # Port différent pour les tests
            'csv_export_path': tempfile.mkdtemp()
        })
        # Reset pour éviter les interférences entre tests
        collector.counters.clear()
        collector.gauges.clear()
        collector.histograms.clear()
        collector.metrics.clear()
        return collector
    
    def test_counter_increment(self, metrics_collector):
        """Test incrémentation de compteur"""
        metrics_collector.increment_counter('test_counter', 5.0)
        
        assert metrics_collector.counters['test_counter'] == 5.0
        
        metrics_collector.increment_counter('test_counter', 3.0)
        assert metrics_collector.counters['test_counter'] == 8.0
    
    def test_gauge_set(self, metrics_collector):
        """Test définition de jauge"""
        metrics_collector.set_gauge('test_gauge', 42.0)
        
        assert metrics_collector.gauges['test_gauge'] == 42.0
        
        metrics_collector.set_gauge('test_gauge', 100.0)
        assert metrics_collector.gauges['test_gauge'] == 100.0
    
    def test_histogram_observe(self, metrics_collector):
        """Test observation d'histogramme"""
        metrics_collector.observe_histogram('test_histogram', 10.0)
        metrics_collector.observe_histogram('test_histogram', 20.0)
        metrics_collector.observe_histogram('test_histogram', 30.0)
        
        values = metrics_collector.histograms['test_histogram']
        assert len(values) == 3
        assert values == [10.0, 20.0, 30.0]
    
    def test_metric_storage(self, metrics_collector):
        """Test stockage des métriques"""
        metrics_collector.increment_counter('test_counter', 1.0, {'label1': 'value1'})
        
        metrics = metrics_collector.metrics['test_counter']
        assert len(metrics) == 1
        
        metric_point = metrics[0]
        assert metric_point.name == 'test_counter'
        assert metric_point.value == 1.0
        assert metric_point.labels == {'label1': 'value1'}
        assert metric_point.tags['type'] == 'counter'
    
    def test_specialized_metrics(self, metrics_collector):
        """Test des métriques spécialisées"""
        # Signal
        metrics_collector.record_signal_generated('battle_navale', 'BUY', 0.75)
        
        # Trade
        metrics_collector.record_trade_executed('battle_navale', 'BUY', 'WIN', 100.0)
        
        # Kill switch
        metrics_collector.record_kill_switch_activation('daily_loss_limit')
        
        # PnL
        metrics_collector.update_pnl(500.0, 200.0)
        
        # Latence
        metrics_collector.update_data_latency('m1', 0.5)
        
        # Vérifications
        assert metrics_collector.counters['signals_generated'] == 1.0
        assert metrics_collector.counters['trades_executed'] == 1.0
        assert metrics_collector.counters['kill_switch_activations'] == 1.0
        assert metrics_collector.gauges['pnl_day'] == 500.0  # PnL jour
        assert metrics_collector.gauges['data_latency'] == 0.5
    
    def test_get_summary(self, metrics_collector):
        """Test résumé des métriques"""
        # Ajouter quelques métriques
        metrics_collector.increment_counter('test_counter', 10.0)
        metrics_collector.set_gauge('test_gauge', 42.0)
        metrics_collector.observe_histogram('test_histogram', 15.0)
        
        summary = metrics_collector.get_summary()
        
        assert 'timestamp' in summary
        assert summary['counters']['test_counter'] == 10.0
        assert summary['gauges']['test_gauge'] == 42.0
        assert summary['histograms']['test_histogram']['count'] == 1
        assert summary['histograms']['test_histogram']['avg'] == 15.0
        assert summary['total_metrics_points'] > 0
    
    def test_export_csv(self, metrics_collector):
        """Test export CSV"""
        # Ajouter des métriques
        metrics_collector.increment_counter('test_counter', 5.0)
        metrics_collector.set_gauge('test_gauge', 10.0)
        
        # Export
        csv_file = metrics_collector.export_csv()
        
        assert Path(csv_file).exists()
        
        # Vérifier le contenu
        with open(csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) >= 3  # Header + 2 métriques
            assert 'timestamp,name,value,labels,tags,type' in lines[0]
    
    def test_export_json(self, metrics_collector):
        """Test export JSON"""
        # Ajouter des métriques
        metrics_collector.increment_counter('test_counter', 5.0)
        metrics_collector.set_gauge('test_gauge', 10.0)
        
        # Export
        json_file = metrics_collector.export_json()
        
        assert Path(json_file).exists()
        
        # Vérifier le contenu
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert 'timestamp' in data
            assert 'counters' in data
            assert 'gauges' in data
            assert data['counters']['test_counter'] == 5.0
            assert data['gauges']['test_gauge'] == 10.0


class TestStructuredLogger:
    """Tests du logger structuré"""
    
    @pytest.fixture
    def structured_logger(self):
        """Instance du logger structuré"""
        return StructuredLogger('test_logger', {
            'log_level': 'INFO',
            'enable_metrics': True
        })
    
    def test_basic_logging(self, structured_logger):
        """Test logging de base"""
        with patch.object(structured_logger.logger, 'info') as mock_info:
            structured_logger.info("Test message", key1="value1", key2="value2")
            
            mock_info.assert_called_once()
            call_args = mock_info.call_args[1]
            assert call_args['message'] == "Test message"
            assert call_args['key1'] == "value1"
            assert call_args['key2'] == "value2"
            assert call_args['level'] == "INFO"
    
    def test_specialized_logging(self, structured_logger):
        """Test logging spécialisé"""
        with patch.object(structured_logger.logger, 'info') as mock_info:
            structured_logger.log_signal('battle_navale', 'BUY', 0.75)
            
            mock_info.assert_called_once()
            call_args = mock_info.call_args[1]
            assert call_args['strategy'] == 'battle_navale'
            assert call_args['side'] == 'BUY'
            assert call_args['confidence'] == 0.75
            assert call_args['event_type'] == 'signal_generated'
    
    def test_log_counts(self, structured_logger):
        """Test compteurs de logs"""
        # Initialiser les compteurs
        structured_logger.reset_log_counts()
        
        # Générer des logs
        structured_logger.info("Info message")
        structured_logger.warning("Warning message")
        structured_logger.error("Error message")
        
        counts = structured_logger.get_log_counts()
        assert counts['INFO'] == 1
        assert counts['WARNING'] == 1
        assert counts['ERROR'] == 1
        assert counts['DEBUG'] == 0
        assert counts['CRITICAL'] == 0
    
    def test_log_context(self, structured_logger):
        """Test contexte de logging"""
        from monitoring.structured_logger import log_context
        
        with patch.object(structured_logger.logger, 'info') as mock_info:
            with log_context(structured_logger, 'test_operation', param1='value1'):
                pass
            
            # Vérifier les deux appels (début et fin)
            assert mock_info.call_count == 2
            
            # Vérifier le premier appel (début)
            start_call = mock_info.call_args_list[0][1]
            assert start_call['operation'] == 'test_operation'
            assert start_call['event_type'] == 'operation_start'
            
            # Vérifier le deuxième appel (fin)
            end_call = mock_info.call_args_list[1][1]
            assert end_call['operation'] == 'test_operation'
            assert end_call['event_type'] == 'performance'
            assert 'duration' in end_call
    
    def test_log_context_with_error(self, structured_logger):
        """Test contexte de logging avec erreur"""
        from monitoring.structured_logger import log_context

        with patch.object(structured_logger.logger, 'info') as mock_info:
            with patch.object(structured_logger.logger, 'error') as mock_error:
                try:
                    with log_context(structured_logger, 'test_operation'):
                        raise ValueError("Test error")
                except ValueError:
                    pass  # Attendu
                
                # Vérifier les appels
                mock_info.assert_called_once()  # Début
                mock_error.assert_called_once()  # Erreur
                
                # Vérifier l'appel d'erreur
                error_call = mock_error.call_args[1]
                assert error_call['operation'] == 'test_operation'
                assert error_call['event_type'] == 'operation_error'
                assert 'duration' in error_call


class TestMetricsExporter:
    """Tests de l'exporteur de métriques"""
    
    @pytest.fixture
    def metrics_exporter(self):
        """Instance de l'exporteur"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer un collecteur isolé pour les tests
            from monitoring.metrics_collector import MetricsCollector
            isolated_collector = MetricsCollector({
                'export_interval_seconds': 1,
                'prometheus_port': 9092,
                'csv_export_path': temp_dir
            })
            
            exporter = MetricsExporter({
                'export_dir': temp_dir
            })
            # Remplacer le collecteur global par notre instance isolée
            exporter.metrics_collector = isolated_collector
            yield exporter
    
    def test_export_csv(self, metrics_exporter):
        """Test export CSV"""
        # Ajouter des métriques
        metrics_exporter.metrics_collector.increment_counter('test_counter', 5.0)
        metrics_exporter.metrics_collector.set_gauge('test_gauge', 10.0)
        
        # Export
        csv_file = metrics_exporter.export_csv()
        
        assert Path(csv_file).exists()
        
        # Vérifier le contenu
        with open(csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) >= 3  # Header + 2 métriques
            assert 'timestamp,name,value,labels,tags,type' in lines[0]
    
    def test_export_json(self, metrics_exporter):
        """Test export JSON"""
        # Ajouter des métriques
        metrics_exporter.metrics_collector.increment_counter('test_counter', 5.0)
        metrics_exporter.metrics_collector.set_gauge('test_gauge', 10.0)
        
        # Export
        json_file = metrics_exporter.export_json()
        
        assert Path(json_file).exists()
        
        # Vérifier le contenu
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert 'metadata' in data
            assert 'summary' in data
            assert 'counters' in data
            assert 'gauges' in data
            assert data['counters']['test_counter'] == 5.0
            assert data['gauges']['test_gauge'] == 10.0
    
    def test_export_all_formats(self, metrics_exporter):
        """Test export tous formats"""
        # Ajouter des métriques
        metrics_exporter.metrics_collector.increment_counter('test_counter', 5.0)
        
        # Export tous formats
        results = metrics_exporter.export_all_formats()
        
        assert 'csv' in results
        assert 'json' in results
        assert Path(results['csv']).exists()
        assert Path(results['json']).exists()
    
    def test_export_summary(self, metrics_exporter):
        """Test résumé des exports"""
        # Créer quelques fichiers d'export
        metrics_exporter.export_csv()
        metrics_exporter.export_json()
        
        # Obtenir le résumé
        summary = metrics_exporter.get_export_summary()
        
        assert 'export_dir' in summary
        assert 'total_files' in summary
        assert 'formats' in summary
        assert summary['formats']['csv'] >= 1
        assert summary['formats']['json'] >= 1


class TestIntegration:
    """Tests d'intégration"""
    
    def test_metrics_logger_integration(self):
        """Test intégration métriques-logger"""
        # Créer un logger avec métriques
        logger = StructuredLogger('test_integration', {
            'enable_metrics': True
        })
        
        # Reset des métriques pour éviter les interférences
        logger.metrics.counters.clear()
        logger.metrics.gauges.clear()
        
        # Générer des logs spécialisés
        logger.log_signal('battle_navale', 'BUY', 0.75)
        logger.log_trade('battle_navale', 'BUY', 'WIN', 100.0)
        logger.log_kill_switch('daily_loss_limit', 'HALT_TRADING')
        
        # Vérifier que les métriques ont été enregistrées
        metrics = logger.metrics
        assert metrics.counters['signals_generated'] == 1.0
        assert metrics.counters['trades_executed'] == 1.0
        assert metrics.counters['kill_switch_activations'] == 1.0
    
    def test_export_integration(self):
        """Test intégration export"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer un exporteur
            exporter = MetricsExporter({'export_dir': temp_dir})
            
            # Reset des métriques pour éviter les interférences
            exporter.metrics_collector.counters.clear()
            exporter.metrics_collector.gauges.clear()
            
            # Ajouter des métriques via le logger
            logger = StructuredLogger('test_export', {'enable_metrics': True})
            logger.log_signal('battle_navale', 'BUY', 0.75)
            logger.log_trade('battle_navale', 'BUY', 'WIN', 100.0)
            
            # Export
            csv_file = exporter.export_csv()
            json_file = exporter.export_json()
            
            # Vérifier les fichiers
            assert Path(csv_file).exists()
            assert Path(json_file).exists()
            
            # Vérifier le contenu JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert data['counters']['signals_generated'] == 1.0
                assert data['counters']['trades_executed'] == 1.0


class TestAsyncFeatures:
    """Tests des fonctionnalités asynchrones"""
    
    def test_auto_export_sync(self):
        """Test export automatique (version synchrone)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer un exporteur
            exporter = MetricsExporter({'export_dir': temp_dir})
            
            # Ajouter des métriques
            exporter.metrics_collector.increment_counter('test_counter', 1.0)
            
            # Test export manuel
            csv_file = exporter.export_csv()
            json_file = exporter.export_json()
            
            # Vérifier les fichiers
            assert Path(csv_file).exists()
            assert Path(json_file).exists()
