"""
Tests End-to-End du Kill Switch
==============================

Tests complets du système de sécurité avec scénarios réels.
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch

from core.safety_kill_switch import (
    SafetyKillSwitch,
    KillSwitchState,
    KillSwitchReason,
    TelemetryData,
    KillSwitchConfig,
)


class TestKillSwitchE2E:
    """Tests end-to-end du kill switch"""
    
    @pytest.fixture
    def kill_switch(self):
        """Instance du kill switch pour les tests"""
        config = {
            'daily_loss_limit': -1000.0,
            'dtc_down_timeout_seconds': 30,
            'vix_spike_threshold': 30.0,
            'order_rejections_threshold': 10,
            'stale_data_thresholds': {
                'm1_max_seconds': 30.0,
                'm30_max_seconds': 300.0,
                'vix_max_seconds': 300.0,
                'menthorq_max_periods': 2.0
            }
        }
        return SafetyKillSwitch(config)
    
    @pytest.fixture
    def mock_components(self):
        """Composants mockés pour les tests"""
        trading_executor = Mock()
        trading_executor.flatten_all = Mock(return_value=True)
        trading_executor.set_paper_mode = Mock()
        trading_executor.get_trading_state = Mock(return_value={
            'pnl_day': 0.0,
            'pnl_session': 0.0,
            'drawdown': 0.0,
            'rejections_last_5m': 0
        })
        
        market_snapshot = Mock()
        market_snapshot.get_latest_snapshot = Mock(return_value={
            'm1_last_update': datetime.now(timezone.utc),
            'm30_last_update': datetime.now(timezone.utc),
            'vix_last_update': datetime.now(timezone.utc),
            'vix_value': 20.0,
            'menthorq_last_update': datetime.now(timezone.utc)
        })
        
        session_manager = Mock()
        session_manager.get_session_state = Mock(return_value={
            'is_active': True,
            'session_type': 'us_session'
        })
        
        sierra_router = Mock()
        sierra_router.health_check = Mock(return_value={
            'dtc_connected': True,
            'latency_ms': 50.0
        })
        
        return {
            'trading_executor': trading_executor,
            'market_snapshot': market_snapshot,
            'session_manager': session_manager,
            'sierra_router': sierra_router
        }
    
    def test_normal_operation(self, kill_switch, mock_components):
        """Test fonctionnement normal du kill switch"""
        # Injecter les composants
        kill_switch.set_components(**mock_components)
        
        # Télémétrie normale
        telemetry = TelemetryData(
            pnl_day=100.0,
            dtc_route_up=True,
            m1_stale_seconds=5.0,
            vix_value=20.0,
            session_active=True
        )
        
        # Mise à jour
        changed = kill_switch.update(telemetry)
        
        # Vérifications
        assert not changed
        assert kill_switch.current_state == KillSwitchState.NORMAL
        assert kill_switch.can_trade()
        assert kill_switch.can_enter_positions()
        assert kill_switch.can_exit_positions()
    
    def test_daily_loss_limit_trigger(self, kill_switch, mock_components):
        """Test déclenchement par limite de perte journalière"""
        kill_switch.set_components(**mock_components)
        
        # Télémétrie avec perte critique
        telemetry = TelemetryData(
            pnl_day=-1500.0,  # Au-dessus du seuil de -1000
            dtc_route_up=True,
            m1_stale_seconds=5.0,
            vix_value=20.0
        )
        
        # Mise à jour
        changed = kill_switch.update(telemetry)
        
        # Vérifications
        assert changed
        assert kill_switch.current_state == KillSwitchState.HALT_TRADING
        assert kill_switch.current_reason == KillSwitchReason.DAILY_LOSS_LIMIT
        assert not kill_switch.can_trade()
        assert not kill_switch.can_enter_positions()
        assert kill_switch.can_exit_positions()  # Peut toujours sortir
        
        # Vérifier que flatten_all a été appelé
        mock_components['trading_executor'].flatten_all.assert_called_once()
    
    def test_dtc_route_down_trigger(self, kill_switch, mock_components):
        """Test déclenchement par route DTC down"""
        kill_switch.set_components(**mock_components)
        
        # Télémétrie avec DTC down
        telemetry = TelemetryData(
            pnl_day=100.0,
            dtc_route_up=False,
            last_dtc_heartbeat=datetime.now(timezone.utc) - timedelta(seconds=60),
            m1_stale_seconds=5.0,
            vix_value=20.0
        )
        
        # Mise à jour
        changed = kill_switch.update(telemetry)
        
        # Vérifications
        assert changed
        assert kill_switch.current_state == KillSwitchState.PAPER_MODE
        assert kill_switch.current_reason == KillSwitchReason.DTC_ROUTE_DOWN
        assert not kill_switch.can_trade()
        assert not kill_switch.can_enter_positions()
        assert kill_switch.can_exit_positions()
        
        # Vérifier que paper_mode a été activé
        mock_components['trading_executor'].set_paper_mode.assert_called_with(True)
    
    def test_stale_data_critical_trigger(self, kill_switch, mock_components):
        """Test déclenchement par données stale critiques"""
        kill_switch.set_components(**mock_components)
        
        # Télémétrie avec données stale
        telemetry = TelemetryData(
            pnl_day=100.0,
            dtc_route_up=True,
            m1_stale_seconds=60.0,  # Au-dessus du seuil de 30s
            m30_stale_seconds=5.0,
            vix_stale_seconds=5.0,
            vix_value=20.0
        )
        
        # Mise à jour
        changed = kill_switch.update(telemetry)
        
        # Vérifications
        assert changed
        assert kill_switch.current_state == KillSwitchState.HALT_ENTRIES
        assert kill_switch.current_reason == KillSwitchReason.STALE_DATA_CRITICAL
        assert not kill_switch.can_enter_positions()
        assert kill_switch.can_exit_positions()
    
    def test_vix_spike_trigger(self, kill_switch, mock_components):
        """Test déclenchement par VIX spike"""
        kill_switch.set_components(**mock_components)
        
        # Télémétrie avec VIX spike
        telemetry = TelemetryData(
            pnl_day=100.0,
            dtc_route_up=True,
            m1_stale_seconds=5.0,
            vix_value=35.0,  # Au-dessus du seuil de 30
            session_active=True,
            session_type="us_session"
        )
        
        # Mise à jour
        changed = kill_switch.update(telemetry)
        
        # Vérifications
        assert changed
        assert kill_switch.current_state == KillSwitchState.HALT_ENTRIES
        assert kill_switch.current_reason == KillSwitchReason.VIX_SPIKE
        assert not kill_switch.can_enter_positions()
        assert kill_switch.can_exit_positions()
    
    def test_order_rejections_trigger(self, kill_switch, mock_components):
        """Test déclenchement par rejets d'ordres répétés"""
        kill_switch.set_components(**mock_components)
        
        # Télémétrie avec rejets excessifs
        telemetry = TelemetryData(
            pnl_day=100.0,
            dtc_route_up=True,
            m1_stale_seconds=5.0,
            vix_value=20.0,
            rejections_last_5m=15  # Au-dessus du seuil de 10
        )
        
        # Mise à jour
        changed = kill_switch.update(telemetry)
        
        # Vérifications
        assert changed
        assert kill_switch.current_state == KillSwitchState.HALT_TRADING
        assert kill_switch.current_reason == KillSwitchReason.ORDER_REJECTIONS
        assert not kill_switch.can_trade()
        assert not kill_switch.can_enter_positions()
        assert kill_switch.can_exit_positions()
    
    def test_menthorq_stale_trigger(self, kill_switch, mock_components):
        """Test déclenchement par MenthorQ stale"""
        kill_switch.set_components(**mock_components)
        
        # Télémétrie avec MenthorQ stale
        telemetry = TelemetryData(
            pnl_day=100.0,
            dtc_route_up=True,
            m1_stale_seconds=5.0,
            vix_value=20.0,
            menthorq_stale_seconds=150.0  # Au-dessus du seuil (2 * 60s)
        )
        
        # Mise à jour
        changed = kill_switch.update(telemetry)
        
        # Vérifications
        assert changed
        assert kill_switch.current_state == KillSwitchState.HALT_ENTRIES
        assert kill_switch.current_reason == KillSwitchReason.MENTHORQ_STALE
        assert not kill_switch.can_enter_positions()
        assert kill_switch.can_exit_positions()
    
    def test_system_overload_trigger(self, kill_switch, mock_components):
        """Test déclenchement par surcharge système"""
        kill_switch.set_components(**mock_components)
        
        # Télémétrie avec hard rules excessifs
        telemetry = TelemetryData(
            pnl_day=100.0,
            dtc_route_up=True,
            m1_stale_seconds=5.0,
            vix_value=20.0,
            hard_rule_hits=8  # Au-dessus du seuil de 5
        )
        
        # Mise à jour
        changed = kill_switch.update(telemetry)
        
        # Vérifications
        assert changed
        assert kill_switch.current_state == KillSwitchState.HALT_ENTRIES
        assert kill_switch.current_reason == KillSwitchReason.SYSTEM_OVERLOAD
        assert not kill_switch.can_enter_positions()
        assert kill_switch.can_exit_positions()
    
    def test_emergency_stop(self, kill_switch, mock_components):
        """Test arrêt d'urgence"""
        kill_switch.set_components(**mock_components)
        
        # Arrêt d'urgence
        kill_switch.emergency_stop()
        
        # Vérifications
        assert kill_switch.current_state == KillSwitchState.EMERGENCY
        assert kill_switch.current_reason == KillSwitchReason.MANUAL_OVERRIDE
        assert not kill_switch.can_trade()
        assert not kill_switch.can_enter_positions()
        assert not kill_switch.can_exit_positions()  # Emergency bloque tout
    
    def test_manual_reset(self, kill_switch, mock_components):
        """Test reset manuel"""
        kill_switch.set_components(**mock_components)
        
        # Activer le kill switch
        telemetry = TelemetryData(pnl_day=-1500.0)
        kill_switch.update(telemetry)
        assert kill_switch.current_state == KillSwitchState.HALT_TRADING
        
        # Reset manuel
        kill_switch.reset("test_reset")
        
        # Vérifications
        assert kill_switch.current_state == KillSwitchState.NORMAL
        assert kill_switch.current_reason is None
        assert kill_switch.can_trade()
        assert kill_switch.can_enter_positions()
        assert kill_switch.can_exit_positions()
        
        # Vérifier que paper_mode a été désactivé
        mock_components['trading_executor'].set_paper_mode.assert_called_with(False)
    
    def test_flatten_failure_fallback(self, kill_switch, mock_components):
        """Test fallback en cas d'échec de flatten_all"""
        # Configurer flatten_all pour échouer
        mock_components['trading_executor'].flatten_all.return_value = False
        
        kill_switch.set_components(**mock_components)
        
        # Télémétrie critique
        telemetry = TelemetryData(pnl_day=-1500.0)
        changed = kill_switch.update(telemetry)
        
        # Vérifications
        assert changed
        # Devrait basculer en PAPER_MODE si flatten_all échoue
        assert kill_switch.current_state == KillSwitchState.PAPER_MODE
        assert kill_switch.current_reason == KillSwitchReason.DTC_ROUTE_DOWN
    
    def test_activation_history(self, kill_switch, mock_components):
        """Test historique des activations"""
        kill_switch.set_components(**mock_components)
        
        # Plusieurs activations
        telemetry1 = TelemetryData(pnl_day=-1500.0)
        kill_switch.update(telemetry1)
        
        kill_switch.reset("test")
        
        telemetry2 = TelemetryData(vix_value=35.0, session_active=True, session_type="us_session")
        kill_switch.update(telemetry2)
        
        # Vérifier l'historique
        history = kill_switch.get_activation_history()
        assert len(history) >= 2
        
        # Vérifier le contenu
        assert history[-1]['reason'] == KillSwitchReason.VIX_SPIKE.value
        assert history[-2]['reason'] == KillSwitchReason.DAILY_LOSS_LIMIT.value
    
    def test_health_summary(self, kill_switch, mock_components):
        """Test résumé de santé"""
        kill_switch.set_components(**mock_components)
        
        # Activer le kill switch
        telemetry = TelemetryData(pnl_day=-1500.0)
        kill_switch.update(telemetry)
        
        # Obtenir le résumé
        summary = kill_switch.get_health_summary()
        
        # Vérifications
        assert summary['current_state'] == KillSwitchState.HALT_TRADING.value
        assert summary['current_reason'] == KillSwitchReason.DAILY_LOSS_LIMIT.value
        assert not summary['can_trade']
        assert not summary['can_enter_positions']
        assert summary['can_exit_positions']
        assert 'counters' in summary
        assert 'config' in summary
    
    @pytest.mark.asyncio
    async def test_monitoring_loop(self, kill_switch, mock_components):
        """Test boucle de surveillance"""
        kill_switch.set_components(**mock_components)
        
        # Mock de la collecte de télémétrie
        with patch.object(kill_switch, '_collect_telemetry') as mock_collect:
            mock_collect.return_value = TelemetryData(
                pnl_day=100.0,
                dtc_route_up=True,
                m1_stale_seconds=5.0,
                vix_value=20.0
            )
            
            # Démarrer la surveillance (court laps de temps pour le test)
            kill_switch.config.check_interval_seconds = 0.1
            
            # Lancer la surveillance en arrière-plan
            monitoring_task = asyncio.create_task(kill_switch.start_monitoring())
            
            # Attendre un peu
            await asyncio.sleep(0.3)
            
            # Arrêter la surveillance
            monitoring_task.cancel()
            
            try:
                await monitoring_task
            except asyncio.CancelledError:
                pass
            
            # Vérifier que la collecte a été appelée
            assert mock_collect.call_count >= 2


class TestKillSwitchIntegration:
    """Tests d'intégration du kill switch avec les composants réels"""
    
    @pytest.fixture
    def real_components(self):
        """Composants réels pour les tests d'intégration"""
        # Ici on pourrait utiliser de vrais composants ou des mocks plus sophistiqués
        return {
            'trading_executor': Mock(),
            'market_snapshot': Mock(),
            'session_manager': Mock(),
            'sierra_router': Mock()
        }
    
    def test_integration_with_trading_executor(self, real_components):
        """Test intégration avec trading executor"""
        kill_switch = SafetyKillSwitch()
        kill_switch.set_components(**real_components)
        
        # Simuler un état de trading
        real_components['trading_executor'].get_trading_state.return_value = {
            'pnl_day': -500.0,
            'pnl_session': -200.0,
            'drawdown': 0.05,
            'rejections_last_5m': 3
        }
        
        # Collecter la télémétrie
        telemetry = kill_switch._collect_telemetry()
        
        # Vérifications
        assert telemetry.pnl_day == -500.0
        assert telemetry.pnl_session == -200.0
        assert telemetry.drawdown == 0.05
        assert telemetry.rejections_last_5m == 3
    
    def test_integration_with_market_snapshot(self, real_components):
        """Test intégration avec market snapshot"""
        kill_switch = SafetyKillSwitch()
        kill_switch.set_components(**real_components)
        
        # Simuler des données de snapshot
        now = datetime.now(timezone.utc)
        real_components['market_snapshot'].get_latest_snapshot.return_value = {
            'm1_last_update': now - timedelta(seconds=10),
            'm30_last_update': now - timedelta(seconds=5),
            'vix_last_update': now - timedelta(seconds=15),
            'vix_value': 25.0,
            'menthorq_last_update': now - timedelta(seconds=20)
        }
        
        # Collecter la télémétrie
        telemetry = kill_switch._collect_telemetry()
        
        # Vérifications
        assert telemetry.m1_stale_seconds >= 10
        assert telemetry.m30_stale_seconds >= 5
        assert telemetry.vix_stale_seconds >= 15
        assert telemetry.vix_value == 25.0
        assert telemetry.menthorq_stale_seconds >= 20
    
    def test_integration_with_sierra_router(self, real_components):
        """Test intégration avec sierra router"""
        kill_switch = SafetyKillSwitch()
        kill_switch.set_components(**real_components)
        
        # Simuler un état de connexion
        real_components['sierra_router'].health_check.return_value = {
            'dtc_connected': True,
            'latency_ms': 75.0
        }
        
        # Collecter la télémétrie
        telemetry = kill_switch._collect_telemetry()
        
        # Vérifications
        assert telemetry.dtc_route_up is True
        assert telemetry.dtc_latency_ms == 75.0
        assert telemetry.last_dtc_heartbeat is not None
    
    def test_integration_with_session_manager(self, real_components):
        """Test intégration avec session manager"""
        kill_switch = SafetyKillSwitch()
        kill_switch.set_components(**real_components)
        
        # Simuler un état de session
        real_components['session_manager'].get_session_state.return_value = {
            'is_active': True,
            'session_type': 'london_session'
        }
        
        # Collecter la télémétrie
        telemetry = kill_switch._collect_telemetry()
        
        # Vérifications
        assert telemetry.session_active is True
        assert telemetry.session_type == 'london_session'

