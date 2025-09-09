#!/usr/bin/env python3
"""
🧪 TEST SIERRA ORDER ROUTER
============================

Tests pour le routeur d'ordres Sierra Chart via DTC.
"""

import pytest
import socket
from unittest.mock import Mock, patch, MagicMock
from core.sierra_order_router import (
    SierraOrderRouter, 
    OrderResult, 
    OrderRequest,
    get_sierra_order_router,
    place_entry,
    place_exit,
    cancel_order
)
from config.sierra_trading_ports import get_sierra_trading_config

class TestSierraOrderRouter:
    """Tests pour SierraOrderRouter"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.router = SierraOrderRouter()
        self.config = get_sierra_trading_config()
    
    def test_initialization(self):
        """Test d'initialisation"""
        assert self.router.cfg is not None
        assert self.router.cfg.es_dtc_port == 11099
        assert self.router.cfg.nq_dtc_port == 11100
        assert len(self.router.connections) == 0
    
    def test_port_for_symbol(self):
        """Test de récupération des ports par symbole"""
        # Test ES
        es_port = self.router._port_for_symbol("ESU25_FUT_CME")
        assert es_port == 11099
        
        # Test NQ
        nq_port = self.router._port_for_symbol("NQU25_FUT_CME")
        assert nq_port == 11100
        
        # Test symbole invalide
        with pytest.raises(ValueError):
            self.router._port_for_symbol("INVALID")
    
    @patch('socket.create_connection')
    def test_health_check_success(self, mock_create_connection):
        """Test health check réussi"""
        # Mock connexion réussie
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        
        health = self.router.health_check()
        
        assert health["ESU25_FUT_CME"] is True
        assert health["NQU25_FUT_CME"] is True
    
    @patch('socket.create_connection')
    def test_health_check_failure(self, mock_create_connection):
        """Test health check échoué"""
        # Mock connexion échouée
        mock_create_connection.side_effect = socket.error("Connection failed")
        
        health = self.router.health_check()
        
        assert health["ESU25_FUT_CME"] is False
        assert health["NQU25_FUT_CME"] is False
    
    def test_build_dtc_order(self):
        """Test construction message DTC ordre"""
        order = OrderRequest(
            symbol="ESU25_FUT_CME",
            side="BUY",
            qty=1.0,
            order_type="MKT"
        )
        
        payload = self.router._build_dtc_order(order)
        
        assert isinstance(payload, bytes)
        assert b"DTC_NEW_ORDER" in payload
        assert b"ESU25_FUT_CME" in payload
        assert b"BUY" in payload
        assert b"1.0" in payload
        assert payload.endswith(b'\x00')  # DTC termine par \x00
    
    def test_build_dtc_cancel(self):
        """Test construction message DTC annulation"""
        payload = self.router._build_dtc_cancel("ESU25_FUT_CME", "ORDER123")
        
        assert isinstance(payload, bytes)
        assert b"DTC_CANCEL_ORDER" in payload
        assert b"ESU25_FUT_CME" in payload
        assert b"ORDER123" in payload
        assert payload.endswith(b'\x00')
    
    def test_parse_dtc_response(self):
        """Test parsing réponse DTC"""
        # Test réponse valide
        response = b"DTC_RESPONSE|ORDER123|ACCEPTED\x00"
        parsed = self.router._parse_dtc_response(response)
        
        assert parsed['order_id'] == "ORDER123"
        assert parsed['status'] == "ACCEPTED"
        assert parsed['raw'] == response
    
    @patch.object(SierraOrderRouter, '_send_dtc')
    def test_send_market_order_success(self, mock_send_dtc):
        """Test envoi ordre marché réussi"""
        # Mock réponse DTC
        mock_response = b"DTC_RESPONSE|ORDER123|ACCEPTED\x00"
        mock_send_dtc.return_value = mock_response
        
        result = self.router.send_market_order("ESU25_FUT_CME", "BUY", 1.0)
        
        assert result.ok is True
        assert result.order_id == "ORDER123"
        assert result.status == "ACCEPTED"
        assert result.error is None
        assert result.timestamp is not None
    
    @patch.object(SierraOrderRouter, '_send_dtc')
    def test_send_market_order_failure(self, mock_send_dtc):
        """Test envoi ordre marché échoué"""
        # Mock erreur DTC
        mock_send_dtc.side_effect = Exception("DTC Error")
        
        result = self.router.send_market_order("ESU25_FUT_CME", "BUY", 1.0)
        
        assert result.ok is False
        assert result.order_id is None
        assert result.status == "ERROR"
        assert "DTC Error" in result.error
    
    @patch.object(SierraOrderRouter, '_send_dtc')
    def test_send_limit_order(self, mock_send_dtc):
        """Test envoi ordre limite"""
        mock_response = b"DTC_RESPONSE|ORDER456|ACCEPTED\x00"
        mock_send_dtc.return_value = mock_response
        
        result = self.router.send_limit_order("ESU25_FUT_CME", "BUY", 1.0, 4500.0)
        
        assert result.ok is True
        assert result.order_id == "ORDER456"
        assert result.status == "ACCEPTED"
    
    @patch.object(SierraOrderRouter, '_send_dtc')
    def test_send_stop_order(self, mock_send_dtc):
        """Test envoi ordre stop"""
        mock_response = b"DTC_RESPONSE|ORDER789|ACCEPTED\x00"
        mock_send_dtc.return_value = mock_response
        
        result = self.router.send_stop_order("ESU25_FUT_CME", "SELL", 1.0, 4400.0)
        
        assert result.ok is True
        assert result.order_id == "ORDER789"
        assert result.status == "ACCEPTED"
    
    @patch.object(SierraOrderRouter, '_send_dtc')
    def test_cancel_order(self, mock_send_dtc):
        """Test annulation ordre"""
        mock_response = b"DTC_RESPONSE|ORDER123|CANCELLED\x00"
        mock_send_dtc.return_value = mock_response
        
        result = self.router.cancel_order("ESU25_FUT_CME", "ORDER123")
        
        assert result.ok is True
        assert result.order_id == "ORDER123"
        assert result.status == "CANCELLED"
    
    def test_close_all_connections(self):
        """Test fermeture connexions"""
        # Mock connexions
        mock_sock1 = MagicMock()
        mock_sock2 = MagicMock()
        self.router.connections = {
            "ESU25_FUT_CME": mock_sock1,
            "NQU25_FUT_CME": mock_sock2
        }
        
        self.router.close_all_connections()
        
        mock_sock1.close.assert_called_once()
        mock_sock2.close.assert_called_once()
        assert len(self.router.connections) == 0

class TestUtilityFunctions:
    """Tests pour les fonctions utilitaires"""
    
    @patch('core.sierra_order_router.get_sierra_order_router')
    def test_place_entry_success(self, mock_get_router):
        """Test place_entry réussi"""
        # Mock routeur
        mock_router = MagicMock()
        mock_result = OrderResult(ok=True, order_id="ORDER123", status="ACCEPTED")
        mock_router.send_market_order.return_value = mock_result
        mock_get_router.return_value = mock_router
        
        success, order_id = place_entry("ESU25_FUT_CME", "BUY", 1.0)
        
        assert success is True
        assert order_id == "ORDER123"
        mock_router.send_market_order.assert_called_once_with("ESU25_FUT_CME", "BUY", 1.0)
    
    @patch('core.sierra_order_router.get_sierra_order_router')
    def test_place_entry_failure(self, mock_get_router):
        """Test place_entry échoué"""
        # Mock routeur
        mock_router = MagicMock()
        mock_result = OrderResult(ok=False, order_id=None, status="ERROR", error="DTC Error")
        mock_router.send_market_order.return_value = mock_result
        mock_get_router.return_value = mock_router
        
        success, order_id = place_entry("ESU25_FUT_CME", "BUY", 1.0)
        
        assert success is False
        assert order_id is None
    
    @patch('core.sierra_order_router.get_sierra_order_router')
    def test_place_exit(self, mock_get_router):
        """Test place_exit"""
        # Mock routeur
        mock_router = MagicMock()
        mock_result = OrderResult(ok=True, order_id="ORDER456", status="ACCEPTED")
        mock_router.send_market_order.return_value = mock_result
        mock_get_router.return_value = mock_router
        
        success, order_id = place_exit("ESU25_FUT_CME", "SELL", 1.0)
        
        assert success is True
        assert order_id == "ORDER456"
        mock_router.send_market_order.assert_called_once_with("ESU25_FUT_CME", "SELL", 1.0)
    
    @patch('core.sierra_order_router.get_sierra_order_router')
    def test_cancel_order_success(self, mock_get_router):
        """Test cancel_order réussi"""
        # Mock routeur
        mock_router = MagicMock()
        mock_result = OrderResult(ok=True, order_id="ORDER123", status="CANCELLED")
        mock_router.cancel_order.return_value = mock_result
        mock_get_router.return_value = mock_router
        
        success = cancel_order("ESU25_FUT_CME", "ORDER123")
        
        assert success is True
        mock_router.cancel_order.assert_called_once_with("ESU25_FUT_CME", "ORDER123")
    
    @patch('core.sierra_order_router.get_sierra_order_router')
    def test_cancel_order_failure(self, mock_get_router):
        """Test cancel_order échoué"""
        # Mock routeur
        mock_router = MagicMock()
        mock_result = OrderResult(ok=False, order_id="ORDER123", status="ERROR", error="DTC Error")
        mock_router.cancel_order.return_value = mock_result
        mock_get_router.return_value = mock_router
        
        success = cancel_order("ESU25_FUT_CME", "ORDER123")
        
        assert success is False

class TestIntegration:
    """Tests d'intégration"""
    
    def test_singleton_router(self):
        """Test que get_sierra_order_router retourne la même instance"""
        router1 = get_sierra_order_router()
        router2 = get_sierra_order_router()
        
        assert router1 is router2
    
    def test_config_integration(self):
        """Test intégration avec la configuration"""
        router = get_sierra_order_router()
        config = get_sierra_trading_config()
        
        assert router.cfg is config
        assert router.cfg.es_dtc_port == 11099
        assert router.cfg.nq_dtc_port == 11100

if __name__ == "__main__":
    # Test simple sans pytest
    print("🧪 Test Sierra Order Router")
    
    router = SierraOrderRouter()
    print(f"✅ Router initialisé: ES={router.cfg.es_dtc_port}, NQ={router.cfg.nq_dtc_port}")
    
    # Test health check (sans connexion réelle)
    print("\n🏥 Health Check (simulé):")
    health = router.health_check()
    for symbol, status in health.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {symbol}: {status}")
    
    print("\n✅ Tests terminés")
