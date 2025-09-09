#!/usr/bin/env python3
"""
🔧 SIERRA CHART ORDER ROUTER
============================

Envoi d'ordres vers Sierra Chart via DTC (uniquement pour TRADING).
La market data reste gérée par le .cpp -> jsonl.

Architecture:
- Data: MIA_Chart_Dumper_patched.cpp → mia_unified_YYYYMMDD.jsonl
- Trading: DTC Sierra Chart (ports ES: 11099, NQ: 11100)
"""

from dataclasses import dataclass
import socket
import logging
from typing import Optional, Dict, Any, Union
from datetime import datetime
from config.sierra_trading_ports import get_sierra_trading_config

# === CONFIGURATION ===

logger = logging.getLogger(__name__)

@dataclass
class OrderResult:
    """Résultat d'un ordre"""
    ok: bool
    order_id: Optional[str]
    status: str
    raw: Optional[bytes] = None
    error: Optional[str] = None
    timestamp: Optional[datetime] = None

@dataclass
class OrderRequest:
    """Requête d'ordre"""
    symbol: str
    side: str  # "BUY" ou "SELL"
    qty: float
    order_type: str = "MKT"  # "MKT", "LMT", "STP"
    price: Optional[float] = None
    stop_price: Optional[float] = None

class SierraOrderRouter:
    """
    Routeur d'ordres vers Sierra Chart via DTC.
    
    Utilise les ports configurés:
    - ES: 11099 (DTC), 11098 (Historical)
    - NQ: 11100 (DTC), 11097 (Historical)
    """
    
    def __init__(self):
        self.cfg = get_sierra_trading_config()
        self.connections: Dict[str, socket.socket] = {}
        logger.info(f"🔧 Sierra Order Router initialisé - ES: {self.cfg.es_dtc_port}, NQ: {self.cfg.nq_dtc_port}")
    
    def _port_for_symbol(self, symbol: str) -> int:
        """Retourne le port DTC pour un symbole"""
        return self.cfg.get_port_by_symbol(symbol)
    
    def _get_connection(self, symbol: str) -> socket.socket:
        """Obtient ou crée une connexion pour un symbole"""
        if symbol not in self.connections:
            port = self._port_for_symbol(symbol)
            sock = socket.create_connection((self.cfg.host, port), timeout=5.0)
            self.connections[symbol] = sock
            logger.info(f"🔗 Connexion DTC établie: {symbol} -> {self.cfg.host}:{port}")
        return self.connections[symbol]
    
    def _send_dtc(self, symbol: str, payload: bytes, timeout: float = 3.0) -> bytes:
        """Envoie un message DTC et retourne la réponse"""
        try:
            sock = self._get_connection(symbol)
            sock.sendall(payload)
            sock.settimeout(timeout)
            response = sock.recv(4096)
            return response
        except Exception as e:
            logger.error(f"❌ Erreur DTC pour {symbol}: {e}")
            # Nettoyer la connexion en cas d'erreur
            if symbol in self.connections:
                try:
                    self.connections[symbol].close()
                except:
                    pass
                del self.connections[symbol]
            raise
    
    def _build_dtc_order(self, order: OrderRequest) -> bytes:
        """
        Construit le message DTC pour un ordre.
        
        TODO: Remplacer par ton encodeur DTC réel (structs/frames)
        """
        # Placeholder - remplace par ton encodeur DTC interne
        order_msg = f"DTC_NEW_ORDER|{order.symbol}|{order.side}|{order.qty}|{order.order_type}"
        if order.price:
            order_msg += f"|{order.price}"
        if order.stop_price:
            order_msg += f"|{order.stop_price}"
        
        return order_msg.encode('utf-8') + b'\x00'  # DTC termine par \x00
    
    def _build_dtc_cancel(self, symbol: str, order_id: str) -> bytes:
        """Construit le message DTC pour annuler un ordre"""
        # Placeholder - remplace par ton encodeur DTC interne
        cancel_msg = f"DTC_CANCEL_ORDER|{symbol}|{order_id}"
        return cancel_msg.encode('utf-8') + b'\x00'
    
    def _parse_dtc_response(self, response: bytes) -> Dict[str, Any]:
        """
        Parse la réponse DTC.
        
        TODO: Remplacer par ton parseur DTC réel
        """
        # Placeholder - remplace par ton parseur DTC interne
        try:
            text = response.decode('utf-8').strip('\x00')
            parts = text.split('|')
            return {
                'order_id': parts[1] if len(parts) > 1 else "SIM-123",
                'status': parts[2] if len(parts) > 2 else "ACCEPTED",
                'raw': response
            }
        except:
            return {
                'order_id': "SIM-123",
                'status': "ACCEPTED",
                'raw': response
            }
    
    def send_market_order(self, symbol: str, side: str, qty: float) -> OrderResult:
        """Envoie un ordre au marché"""
        try:
            order = OrderRequest(symbol=symbol, side=side, qty=qty, order_type="MKT")
            payload = self._build_dtc_order(order)
            raw_response = self._send_dtc(symbol, payload)
            parsed = self._parse_dtc_response(raw_response)
            
            logger.info(f"📈 Ordre MKT envoyé: {symbol} {side} {qty} -> {parsed['order_id']}")
            
            return OrderResult(
                ok=True,
                order_id=parsed['order_id'],
                status=parsed['status'],
                raw=raw_response,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"❌ Erreur ordre MKT {symbol}: {e}")
            return OrderResult(
                ok=False,
                order_id=None,
                status="ERROR",
                error=str(e),
                timestamp=datetime.now()
            )
    
    def send_limit_order(self, symbol: str, side: str, qty: float, price: float) -> OrderResult:
        """Envoie un ordre limite"""
        try:
            order = OrderRequest(symbol=symbol, side=side, qty=qty, order_type="LMT", price=price)
            payload = self._build_dtc_order(order)
            raw_response = self._send_dtc(symbol, payload)
            parsed = self._parse_dtc_response(raw_response)
            
            logger.info(f"📊 Ordre LMT envoyé: {symbol} {side} {qty} @ {price} -> {parsed['order_id']}")
            
            return OrderResult(
                ok=True,
                order_id=parsed['order_id'],
                status=parsed['status'],
                raw=raw_response,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"❌ Erreur ordre LMT {symbol}: {e}")
            return OrderResult(
                ok=False,
                order_id=None,
                status="ERROR",
                error=str(e),
                timestamp=datetime.now()
            )
    
    def send_stop_order(self, symbol: str, side: str, qty: float, stop_price: float) -> OrderResult:
        """Envoie un ordre stop"""
        try:
            order = OrderRequest(symbol=symbol, side=side, qty=qty, order_type="STP", stop_price=stop_price)
            payload = self._build_dtc_order(order)
            raw_response = self._send_dtc(symbol, payload)
            parsed = self._parse_dtc_response(raw_response)
            
            logger.info(f"🛑 Ordre STP envoyé: {symbol} {side} {qty} @ {stop_price} -> {parsed['order_id']}")
            
            return OrderResult(
                ok=True,
                order_id=parsed['order_id'],
                status=parsed['status'],
                raw=raw_response,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"❌ Erreur ordre STP {symbol}: {e}")
            return OrderResult(
                ok=False,
                order_id=None,
                status="ERROR",
                error=str(e),
                timestamp=datetime.now()
            )
    
    def cancel_order(self, symbol: str, order_id: str) -> OrderResult:
        """Annule un ordre"""
        try:
            payload = self._build_dtc_cancel(symbol, order_id)
            raw_response = self._send_dtc(symbol, payload)
            parsed = self._parse_dtc_response(raw_response)
            
            logger.info(f"❌ Ordre annulé: {symbol} {order_id} -> {parsed['status']}")
            
            return OrderResult(
                ok=True,
                order_id=order_id,
                status=parsed['status'],
                raw=raw_response,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"❌ Erreur annulation {symbol} {order_id}: {e}")
            return OrderResult(
                ok=False,
                order_id=order_id,
                status="ERROR",
                error=str(e),
                timestamp=datetime.now()
            )
    
    def health_check(self) -> Dict[str, bool]:
        """Vérifie la santé des connexions DTC"""
        health = {}
        
        for symbol in ["ESU25_FUT_CME", "NQU25_FUT_CME"]:
            try:
                port = self._port_for_symbol(symbol)
                # Test de connexion simple
                with socket.create_connection((self.cfg.host, port), timeout=2.0) as test_sock:
                    health[symbol] = True
                    logger.debug(f"✅ Health check OK: {symbol} -> {port}")
            except Exception as e:
                health[symbol] = False
                logger.warning(f"⚠️ Health check FAIL: {symbol} -> {port}: {e}")
        
        return health
    
    def close_all_connections(self):
        """Ferme toutes les connexions"""
        for symbol, sock in self.connections.items():
            try:
                sock.close()
                logger.info(f"🔌 Connexion fermée: {symbol}")
            except:
                pass
        self.connections.clear()
    
    def __del__(self):
        """Nettoyage automatique"""
        self.close_all_connections()

# === INSTANCE GLOBALE ===

_sierra_router = None

def get_sierra_order_router() -> SierraOrderRouter:
    """Retourne l'instance globale du routeur Sierra"""
    global _sierra_router
    if _sierra_router is None:
        _sierra_router = SierraOrderRouter()
    return _sierra_router

# === FONCTIONS UTILITAIRES ===

def place_entry(symbol: str, side: str, qty: float) -> tuple[bool, Union[str, None]]:
    """
    Fonction utilitaire pour placer un ordre d'entrée
    
    Returns:
        (success: bool, order_id: str | None)
    """
    router = get_sierra_order_router()
    result = router.send_market_order(symbol, side, qty)
    
    if not result.ok:
        logger.error(f"❌ Échec ordre d'entrée {symbol}: {result.error}")
        return False, None
    
    return True, result.order_id

def place_exit(symbol: str, side: str, qty: float) -> tuple[bool, Union[str, None]]:
    """
    Fonction utilitaire pour placer un ordre de sortie
    
    Returns:
        (success: bool, order_id: str | None)
    """
    router = get_sierra_order_router()
    result = router.send_market_order(symbol, side, qty)
    
    if not result.ok:
        logger.error(f"❌ Échec ordre de sortie {symbol}: {result.error}")
        return False, None
    
    return True, result.order_id

def cancel_order(symbol: str, order_id: str) -> bool:
    """
    Fonction utilitaire pour annuler un ordre
    
    Returns:
        success: bool
    """
    router = get_sierra_order_router()
    result = router.cancel_order(symbol, order_id)
    
    if not result.ok:
        logger.error(f"❌ Échec annulation {symbol} {order_id}: {result.error}")
        return False
    
    return True

if __name__ == "__main__":
    # Test du routeur
    logging.basicConfig(level=logging.INFO)
    
    router = get_sierra_order_router()
    
    print("🔧 Test Sierra Order Router:")
    print(f"Configuration: {router.cfg.get_all_configs()}")
    
    print("\n🏥 Health Check:")
    health = router.health_check()
    for symbol, status in health.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {symbol}: {status}")
    
    print("\n🧪 Test ordre simulé (ne sera pas envoyé en mode test):")
    # Test simulé - ne pas exécuter en production sans Sierra Chart actif
    # result = router.send_market_order("ESU25_FUT_CME", "BUY", 1.0)
    # print(f"Résultat: {result}")
