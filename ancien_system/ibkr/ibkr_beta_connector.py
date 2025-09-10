#!/usr/bin/env python3
"""
Adaptateur pour l'API BETA IBKR - Client Portal Gateway
Basé sur la documentation locale et les endpoints connus
"""

import requests
import json
import time
import websocket
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import logging

class IBKRBetaConfig:
    """Configuration pour l'API BETA IBKR"""
    
    def __init__(self):
        self.host = "localhost"
        self.port = 5000
        self.use_ssl = True
        self.base_url = f"https://{self.host}:{self.port}/v1/api"
        self.ws_url = f"wss://{self.host}:{self.port}/v1/api/ws"
        self.timeout = 30
        self.verify_ssl = False  # Pour éviter les erreurs SSL locales
        
        # Authentification
        self.authenticated = False
        self.session_id = None
        
        # WebSocket
        self.ws_connected = False
        self.ws_callbacks = {}

class IBKRBetaConnector:
    """Connecteur pour l'API BETA IBKR"""
    
    def __init__(self, config: Optional[IBKRBetaConfig] = None):
        self.config = config or IBKRBetaConfig()
        self.session = requests.Session()
        self.session.verify = self.config.verify_ssl
        
        # WebSocket
        self.ws = None
        self.ws_thread = None
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Cache pour les données
        self.market_data_cache = {}
        self.positions_cache = {}
        self.account_cache = {}
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
    
    def connect(self) -> bool:
        """Se connecter à l'API BETA IBKR"""
        try:
            self.logger.info("🔌 Connexion à l'API BETA IBKR...")
            
            # Vérifier si le gateway est accessible
            response = self.session.get(
                f"{self.config.base_url}/iserver/auth/status",
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                self.logger.info("✅ Gateway accessible")
                return True
            else:
                self.logger.error(f"❌ Gateway non accessible: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur de connexion: {e}")
            return False
    
    def authenticate(self) -> bool:
        """Authentification via navigateur web"""
        try:
            self.logger.info("🔐 Authentification IBKR BETA...")
            self.logger.info(f"🌐 Ouvrez votre navigateur et allez sur: https://{self.config.host}:{self.config.port}")
            self.logger.info("📝 Connectez-vous avec vos identifiants IBKR")
            
            # Vérifier le statut d'authentification
            max_attempts = 30
            for attempt in range(max_attempts):
                response = self.session.get(
                    f"{self.config.base_url}/iserver/auth/status",
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('authenticated'):
                        self.config.authenticated = True
                        self.logger.info("✅ Authentification réussie!")
                        return True
                
                self.logger.info(f"⏳ Tentative {attempt + 1}/{max_attempts} - En attente d'authentification...")
                time.sleep(2)
            
            self.logger.error("❌ Authentification échouée - délai dépassé")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Erreur d'authentification: {e}")
            return False
    
    def get_account_info(self) -> Optional[Dict]:
        """Récupérer les informations du compte"""
        try:
            if not self.config.authenticated:
                self.logger.error("❌ Non authentifié")
                return None
            
            response = self.session.get(
                f"{self.config.base_url}/iserver/account",
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                self.account_cache = data
                return data
            else:
                self.logger.error(f"❌ Erreur récupération compte: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Erreur get_account_info: {e}")
            return None
    
    def get_positions(self) -> List[Dict]:
        """Récupérer les positions"""
        try:
            if not self.config.authenticated:
                return []
            
            response = self.session.get(
                f"{self.config.base_url}/iserver/account/positions",
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                self.positions_cache = data
                return data
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Erreur get_positions: {e}")
            return []
    
    def get_market_data(self, conid: str, fields: List[str] = None) -> Optional[Dict]:
        """Récupérer les données de marché"""
        try:
            if not self.config.authenticated:
                return None
            
            # Champs par défaut pour ES futures
            if fields is None:
                fields = ["31", "83", "84", "86"]  # bid, ask, last, volume
            
            response = self.session.get(
                f"{self.config.base_url}/iserver/marketdata/snapshot",
                params={
                    "conids": conid,
                    "fields": ",".join(fields)
                },
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                self.market_data_cache[conid] = data
                return data
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Erreur get_market_data: {e}")
            return None
    
    def get_historical_data(self, conid: str, period: str = "1d", bar: str = "1min") -> List[Dict]:
        """Récupérer les données historiques"""
        try:
            if not self.config.authenticated:
                return []
            
            response = self.session.get(
                f"{self.config.base_url}/iserver/marketdata/history",
                params={
                    "conid": conid,
                    "period": period,
                    "bar": bar
                },
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Erreur get_historical_data: {e}")
            return []
    
    def search_contract(self, symbol: str, secType: str = "STK") -> List[Dict]:
        """Rechercher un contrat"""
        try:
            if not self.config.authenticated:
                return []
            
            response = self.session.get(
                f"{self.config.base_url}/iserver/secdef/search",
                params={
                    "symbol": symbol,
                    "name": "true",
                    "secType": secType
                },
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Erreur search_contract: {e}")
            return []
    
    def place_order(self, conid: str, order: Dict) -> Optional[Dict]:
        """Placer un ordre"""
        try:
            if not self.config.authenticated:
                return None
            
            # Préparer l'ordre
            order_data = {
                "conid": conid,
                "orderType": order.get("orderType", "LMT"),
                "side": order.get("side", "BUY"),
                "quantity": order.get("quantity", 1),
                "price": order.get("price", 0),
                "tif": order.get("tif", "DAY")
            }
            
            response = self.session.post(
                f"{self.config.base_url}/iserver/account/orders",
                json=order_data,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                self.logger.error(f"❌ Erreur place_order: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Erreur place_order: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Annuler un ordre"""
        try:
            if not self.config.authenticated:
                return False
            
            response = self.session.delete(
                f"{self.config.base_url}/iserver/account/orders/{order_id}",
                timeout=self.config.timeout
            )
            
            return response.status_code == 200
                
        except Exception as e:
            self.logger.error(f"❌ Erreur cancel_order: {e}")
            return False
    
    def get_orders(self) -> List[Dict]:
        """Récupérer les ordres"""
        try:
            if not self.config.authenticated:
                return []
            
            response = self.session.get(
                f"{self.config.base_url}/iserver/account/orders",
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Erreur get_orders: {e}")
            return []
    
    # WebSocket pour données temps réel
    def connect_websocket(self):
        """Se connecter au WebSocket pour données temps réel"""
        try:
            if not self.config.authenticated:
                self.logger.error("❌ Non authentifié pour WebSocket")
                return False
            
            self.ws = websocket.WebSocketApp(
                self.config.ws_url,
                on_open=self._on_ws_open,
                on_message=self._on_ws_message,
                on_error=self._on_ws_error,
                on_close=self._on_ws_close
            )
            
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur connect_websocket: {e}")
            return False
    
    def _on_ws_open(self, ws):
        """Callback WebSocket ouvert"""
        self.logger.info("🔌 WebSocket connecté")
        self.config.ws_connected = True
    
    def _on_ws_message(self, ws, message):
        """Callback WebSocket message"""
        try:
            data = json.loads(message)
            topic = data.get("topic", "")
            
            # Traiter selon le topic
            if topic.startswith("smd+"):  # Market Data
                conid = topic.split("+")[1]
                self._handle_market_data(conid, data)
            elif topic == "sor":  # Orders
                self._handle_orders_update(data)
            elif topic == "spl":  # PnL
                self._handle_pnl_update(data)
                
        except Exception as e:
            self.logger.error(f"❌ Erreur traitement message WebSocket: {e}")
    
    def _on_ws_error(self, ws, error):
        """Callback WebSocket erreur"""
        self.logger.error(f"❌ Erreur WebSocket: {error}")
    
    def _on_ws_close(self, ws, close_status_code, close_msg):
        """Callback WebSocket fermé"""
        self.logger.info("🔌 WebSocket fermé")
        self.config.ws_connected = False
    
    def subscribe_market_data(self, conid: str, fields: List[str] = None, callback: Callable = None):
        """S'abonner aux données de marché temps réel"""
        try:
            if not self.config.ws_connected:
                self.logger.error("❌ WebSocket non connecté")
                return False
            
            if fields is None:
                fields = ["31", "83", "84", "86"]  # bid, ask, last, volume
            
            # Enregistrer le callback
            if callback:
                self.config.ws_callbacks[f"smd+{conid}"] = callback
            
            # Envoyer la souscription
            message = f"smd+{conid}+{{\"fields\":{json.dumps(fields)}}}"
            self.ws.send(message)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur subscribe_market_data: {e}")
            return False
    
    def _handle_market_data(self, conid: str, data: Dict):
        """Traiter les données de marché reçues"""
        self.market_data_cache[conid] = data
        
        # Appeler le callback si défini
        callback = self.config.ws_callbacks.get(f"smd+{conid}")
        if callback:
            callback(data)
    
    def _handle_orders_update(self, data: Dict):
        """Traiter les mises à jour d'ordres"""
        self.logger.info(f"📋 Mise à jour ordres: {data}")
    
    def _handle_pnl_update(self, data: Dict):
        """Traiter les mises à jour PnL"""
        self.logger.info(f"💰 Mise à jour PnL: {data}")
    
    def disconnect(self):
        """Se déconnecter"""
        try:
            if self.ws:
                self.ws.close()
            
            if self.session:
                self.session.close()
            
            self.logger.info("🔌 Déconnexion terminée")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur déconnexion: {e}")

    def get_es_futures_conid(self) -> Optional[str]:
        """Obtenir le conid pour ES futures"""
        try:
            contracts = self.search_contract("ES", "FUT")
            if contracts:
                # Prendre le premier contrat ES trouvé
                return str(contracts[0].get("conid"))
            return None
        except Exception as e:
            self.logger.error(f"❌ Erreur recherche ES futures: {e}")
            return None

# Fonctions utilitaires pour MIA_IA
def get_es_futures_conid(connector: IBKRBetaConnector) -> Optional[str]:
    """Obtenir le conid pour ES futures"""
    try:
        contracts = connector.search_contract("ES", "FUT")
        if contracts:
            # Prendre le premier contrat ES trouvé
            return str(contracts[0].get("conid"))
        return None
    except Exception as e:
        print(f"❌ Erreur recherche ES futures: {e}")
        return None

def get_spx_options_conid(connector: IBKRBetaConnector, strike: float, expiry: str) -> Optional[str]:
    """Obtenir le conid pour SPX options"""
    try:
        # Recherche spécifique pour SPX options
        contracts = connector.search_contract("SPX", "OPT")
        if contracts:
            # Filtrer par strike et expiry
            for contract in contracts:
                if (contract.get("strike") == strike and 
                    contract.get("expiry") == expiry):
                    return str(contract.get("conid"))
        return None
    except Exception as e:
        print(f"❌ Erreur recherche SPX options: {e}")
        return None






