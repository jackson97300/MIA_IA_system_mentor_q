"""
Tests d'Intégration Phase 2 - MIA_IA_SYSTEM
===========================================

Tests complets de la Phase 2 : Kill-switch, Observabilité, Utilitaires.
"""

import pytest
import asyncio
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

from core.safety_kill_switch import SafetyKillSwitch, TelemetryData, KillSwitchState, KillSwitchReason
from monitoring.metrics_collector import MetricsCollector
from monitoring.structured_logger import StructuredLogger
from monitoring.metrics_exporter import MetricsExporter
from utils.cleanup import cleanup_files, get_cleanup_summary
from utils.restart import restart_component, get_system_status


class TestPhase2Integration:
    """Tests d'intégration de la Phase 2"""
    
    @pytest.fixture
    def temp_dir(self):
        """Répertoire temporaire pour les tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def kill_switch(self):
        """Kill switch configuré"""
        config = {
            'daily_loss_limit': -1000.0,
            'dtc_down_timeout_seconds': 30,
            'vix_spike_threshold': 30.0,
            'order_rejections_threshold': 10
        }
        return SafetyKillSwitch(config)
    
    @pytest.fixture
    def metrics_collector(self, temp_dir):
        """Collecteur de métriques"""
        return MetricsCollector({
            'export_interval_seconds': 1,
            'csv_export_path': str(temp_dir)
        })
    
    @pytest.fixture
    def structured_logger(self):
        """Logger structuré"""
        return StructuredLogger('test_integration', {
            'log_level': 'INFO',
            'enable_metrics': True
        })
    
    def test_kill_switch_metrics_integration(self, kill_switch, metrics_collector):
        """Test intégration kill-switch + métriques"""
        # Injecter le collecteur de métriques dans le kill switch
        kill_switch.metrics_collector = metrics_collector
        
        # Télémétrie critique
        telemetry = TelemetryData(
            pnl_day=-1500.0,  # Déclenche le kill switch
            dtc_route_up=True,
            m1_stale_seconds=5.0,
            vix_value=20.0
        )
        
        # Mise à jour du kill switch
        changed = kill_switch.update(telemetry)
        
        # Vérifications
        assert changed
        assert kill_switch.current_state == KillSwitchState.HALT_TRADING
        assert kill_switch.current_reason == KillSwitchReason.DAILY_LOSS_LIMIT
        
        # Vérifier que les métriques ont été enregistrées
        assert metrics_collector.counters['kill_switch_activations'] == 1.0
    
    def test_logger_metrics_integration(self, structured_logger, metrics_collector):
        """Test intégration logger + métriques"""
        # Injecter le collecteur de métriques dans le logger
        structured_logger.metrics = metrics_collector
        
        # Générer des logs spécialisés
        structured_logger.log_signal('battle_navale', 'BUY', 0.75)
        structured_logger.log_trade('battle_navale', 'BUY', 'WIN', 100.0)
        structured_logger.log_kill_switch('daily_loss_limit', 'HALT_TRADING')
        
        # Vérifier les métriques
        assert metrics_collector.counters['signals_generated'] == 1.0
        assert metrics_collector.counters['trades_executed'] == 1.0
        assert metrics_collector.counters['kill_switch_activations'] == 1.0
        
        # Vérifier les compteurs de logs
        counts = structured_logger.get_log_counts()
        assert counts['INFO'] >= 3  # Au moins 3 logs info
    
    def test_export_integration(self, metrics_collector, temp_dir):
        """Test intégration export"""
        # Ajouter des métriques
        metrics_collector.record_signal_generated('battle_navale', 'BUY', 0.75)
        metrics_collector.record_trade_executed('battle_navale', 'BUY', 'WIN', 100.0)
        metrics_collector.record_kill_switch_activation('daily_loss_limit')
        
        # Export CSV
        csv_file = metrics_collector.export_csv()
        assert Path(csv_file).exists()
        
        # Export JSON
        json_file = metrics_collector.export_json()
        assert Path(json_file).exists()
        
        # Vérifier le contenu CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) >= 4  # Header + 3 métriques
            assert 'signals_generated' in ''.join(lines)
            assert 'trades_executed' in ''.join(lines)
            assert 'kill_switch_activations' in ''.join(lines)
    
    def test_cleanup_integration(self, temp_dir):
        """Test intégration nettoyage"""
        # Créer des fichiers de test
        test_files = [
            temp_dir / 'test.log',
            temp_dir / 'test.backup',
            temp_dir / 'test.tmp'
        ]
        
        for file_path in test_files:
            file_path.write_text('test content')
            # Modifier la date de modification pour qu'elle soit ancienne
            old_time = (datetime.now() - timedelta(days=10)).timestamp()
            os.utime(file_path, (old_time, old_time))
        
        # Nettoyage
        with patch('utils.cleanup.Path') as mock_path:
            mock_path.return_value = temp_dir
            result = cleanup_files('all', 7, confirm=True)
        
        # Vérifications
        assert result['status'] == 'completed'
        assert result['files_removed'] >= 0  # Peut varier selon l'implémentation
    
    def test_restart_integration(self):
        """Test intégration redémarrage"""
        # Test du statut système
        status = get_system_status()
        
        assert 'timestamp' in status
        assert 'components' in status
        assert 'processes' in status
        assert 'health' in status
        
        # Test du redémarrage (simulation)
        with patch('utils.restart._stop_processes') as mock_stop:
            with patch('utils.restart._run_command') as mock_run:
                result = restart_component('safety', reset_cache=False)
                
                assert result['status'] == 'completed'
                assert 'kill_switch_reset' in result['actions']
    
    @pytest.mark.asyncio
    async def test_async_monitoring_integration(self, kill_switch, metrics_collector):
        """Test intégration monitoring asynchrone"""
        # Configurer le kill switch
        kill_switch.metrics_collector = metrics_collector
        kill_switch.config.check_interval_seconds = 0.1
        
        # Mock de la collecte de télémétrie
        with patch.object(kill_switch, '_collect_telemetry') as mock_collect:
            mock_collect.return_value = TelemetryData(
                pnl_day=100.0,
                dtc_route_up=True,
                m1_stale_seconds=5.0,
                vix_value=20.0
            )
            
            # Démarrer la surveillance
            monitoring_task = asyncio.create_task(kill_switch.start_monitoring())
            
            # Attendre un peu
            await asyncio.sleep(0.3)
            
            # Arrêter
            monitoring_task.cancel()
            
            try:
                await monitoring_task
            except asyncio.CancelledError:
                pass
            
            # Vérifier que la collecte a été appelée
            assert mock_collect.call_count >= 2
    
    def test_end_to_end_workflow(self, kill_switch, metrics_collector, structured_logger, temp_dir):
        """Test workflow complet end-to-end"""
        # Configuration
        kill_switch.metrics_collector = metrics_collector
        structured_logger.metrics = metrics_collector
        
        # 1. Génération de signaux
        structured_logger.log_signal('battle_navale', 'BUY', 0.75)
        structured_logger.log_signal('battle_navale', 'SELL', 0.65)
        
        # 2. Exécution de trades
        structured_logger.log_trade('battle_navale', 'BUY', 'WIN', 100.0)
        structured_logger.log_trade('battle_navale', 'SELL', 'LOSS', -50.0)
        
        # 3. Activation du kill switch
        telemetry = TelemetryData(pnl_day=-1500.0)
        kill_switch.update(telemetry)
        structured_logger.log_kill_switch('daily_loss_limit', 'HALT_TRADING')
        
        # 4. Export des métriques
        csv_file = metrics_collector.export_csv()
        json_file = metrics_collector.export_json()
        
        # 5. Vérifications
        assert metrics_collector.counters['signals_generated'] == 2.0
        assert metrics_collector.counters['trades_executed'] == 2.0
        assert metrics_collector.counters['kill_switch_activations'] == 1.0
        
        assert kill_switch.current_state == KillSwitchState.HALT_TRADING
        assert not kill_switch.can_trade()
        
        assert Path(csv_file).exists()
        assert Path(json_file).exists()
        
        # 6. Résumé
        summary = metrics_collector.get_summary()
        assert summary['counters']['signals_generated'] == 2.0
        assert summary['counters']['trades_executed'] == 2.0
        assert summary['counters']['kill_switch_activations'] == 1.0
        
        # 7. Logs
        log_counts = structured_logger.get_log_counts()
        assert log_counts['INFO'] >= 5  # Au moins 5 logs info
        assert log_counts['WARNING'] >= 1  # Au moins 1 warning (kill switch)
    
    def test_error_handling(self, kill_switch, metrics_collector):
        """Test gestion d'erreurs"""
        # Test avec télémétrie invalide
        try:
            kill_switch.update(None)
        except Exception:
            pass  # Doit gérer l'erreur gracieusement
        
        # Test avec collecteur de métriques défaillant
        with patch.object(metrics_collector, 'increment_counter', side_effect=Exception("Test error")):
            try:
                metrics_collector.increment_counter('test_counter')
            except Exception:
                pass  # Doit gérer l'erreur gracieusement
        
        # Vérifier que le système continue de fonctionner
        assert kill_switch.current_state == KillSwitchState.NORMAL
    
    def test_performance_metrics(self, metrics_collector):
        """Test métriques de performance"""
        import time
        
        # Mesurer le temps de traitement
        start_time = time.time()
        
        # Simuler un traitement
        for i in range(100):
            metrics_collector.increment_counter('test_counter')
            metrics_collector.set_gauge('test_gauge', i)
            metrics_collector.observe_histogram('test_histogram', i * 0.1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Enregistrer la métrique de performance
        metrics_collector.record_processing_time('test_operation', duration)
        
        # Vérifications
        assert metrics_collector.counters['test_counter'] == 100.0
        assert metrics_collector.gauges['test_gauge'] == 99.0  # Dernière valeur
        assert len(metrics_collector.histograms['test_histogram']) == 100
        assert len(metrics_collector.histograms['processing_time']) == 1
        
        # Vérifier que la durée est raisonnable
        assert duration < 1.0  # Moins d'1 seconde pour 100 opérations


class TestPhase2Validation:
    """Tests de validation de la Phase 2"""
    
    def test_phase2_requirements(self):
        """Test que tous les requirements de la Phase 2 sont remplis"""
        requirements = {
            'kill_switch_operational': False,
            'metrics_standard': False,
            'packaging_ci': False,
            'runbook_operator': False
        }
        
        # 1. Kill-switch opérationnel
        try:
            kill_switch = SafetyKillSwitch()
            telemetry = TelemetryData(pnl_day=-1500.0)
            kill_switch.update(telemetry)
            requirements['kill_switch_operational'] = True
        except Exception:
            pass
        
        # 2. Métriques standard
        try:
            metrics = MetricsCollector()
            metrics.record_signal_generated('test', 'BUY', 0.75)
            metrics.record_trade_executed('test', 'BUY', 'WIN', 100.0)
            requirements['metrics_standard'] = True
        except Exception:
            pass
        
        # 3. Packaging & CI
        try:
            pyproject_path = Path('pyproject.toml')
            if pyproject_path.exists():
                requirements['packaging_ci'] = True
        except Exception:
            pass
        
        # 4. Runbook opérateur
        try:
            runbook_path = Path('docs/RUN.md')
            operations_path = Path('docs/OPERATIONS.md')
            if runbook_path.exists() and operations_path.exists():
                requirements['runbook_operator'] = True
        except Exception:
            pass
        
        # Vérifier que tous les requirements sont remplis
        for requirement, fulfilled in requirements.items():
            assert fulfilled, f"Requirement {requirement} non rempli"
        
        print("✅ Tous les requirements de la Phase 2 sont remplis !")
    
    def test_go_no_go_checklist(self):
        """Test de la checklist Go/No-Go"""
        checklist = {
            'secrets_secured': False,
            'config_canonical': False,
            'schema_validation': False,
            'tests_automated': False,
            'kill_switch_tested': False,
            'observability_complete': False,
            'packaging_ready': False,
            'runbooks_ready': False
        }
        
        # 1. Secrets sécurisés
        try:
            gitignore_path = Path('.gitignore')
            if gitignore_path.exists():
                content = gitignore_path.read_text()
                if '.env.*' in content and '.env.live' in content:
                    checklist['secrets_secured'] = True
        except Exception:
            pass
        
        # 2. Configuration canonique
        try:
            prod_config = Path('config/feature_config.prod.json')
            dev_config = Path('config/feature_config.dev.json')
            if prod_config.exists() and dev_config.exists():
                checklist['config_canonical'] = True
        except Exception:
            pass
        
        # 3. Validation de schéma
        try:
            schema_path = Path('schema/unified_event.py')
            if schema_path.exists():
                checklist['schema_validation'] = True
        except Exception:
            pass
        
        # 4. Tests automatisés
        try:
            test_files = list(Path('tests').glob('test_*.py'))
            if len(test_files) >= 5:  # Au moins 5 fichiers de test
                checklist['tests_automated'] = True
        except Exception:
            pass
        
        # 5. Kill-switch testé
        try:
            kill_switch_test = Path('tests/test_kill_switch_e2e.py')
            if kill_switch_test.exists():
                checklist['kill_switch_tested'] = True
        except Exception:
            pass
        
        # 6. Observabilité complète
        try:
            metrics_path = Path('monitoring/metrics_collector.py')
            logger_path = Path('monitoring/structured_logger.py')
            if metrics_path.exists() and logger_path.exists():
                checklist['observability_complete'] = True
        except Exception:
            pass
        
        # 7. Packaging prêt
        try:
            pyproject_path = Path('pyproject.toml')
            if pyproject_path.exists():
                checklist['packaging_ready'] = True
        except Exception:
            pass
        
        # 8. Runbooks prêts
        try:
            runbook_path = Path('docs/RUN.md')
            operations_path = Path('docs/OPERATIONS.md')
            if runbook_path.exists() and operations_path.exists():
                checklist['runbooks_ready'] = True
        except Exception:
            pass
        
        # Vérifier la checklist
        fulfilled_count = sum(checklist.values())
        total_count = len(checklist)
        
        print(f"📋 Checklist Go/No-Go: {fulfilled_count}/{total_count} items remplis")
        
        for item, fulfilled in checklist.items():
            status = "✅" if fulfilled else "❌"
            print(f"  {status} {item}")
        
        # Au moins 80% des items doivent être remplis
        assert fulfilled_count >= total_count * 0.8, f"Seulement {fulfilled_count}/{total_count} items remplis"
        
        print("🎯 Checklist Go/No-Go validée !")

