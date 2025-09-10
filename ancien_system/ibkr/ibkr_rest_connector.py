#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Connecteur API REST IBKR
Connecteur moderne pour l'API REST IBKR (alternative à TWS/Gateway)
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# === TYPES ET ENUMS ===

class IBKRConnectionStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

@dataclass
class IBKRMarketData:
    """Données de marché IBKR"""
    symbol: str
    price: float
    bid: float
    ask: float
    volume: int
    timestamp: datetime
    exchange: str = "CME"
    currency: str = "USD"

@dataclass
class IBKRPosition:
    """Position IBKR"""
    symbol: str
    quantity: int
    avg_price: float
    market_value: float
    unrealized_pnl: float
    currency: str = "USD"

@dataclass
class IBKROrder:
    """Ordre IBKR"""
    order_id: int
    symbol: str
    side: str  # "BUY" ou "SELL"
    quantity: int
    order_type: str  # "MKT", "LMT", etc.
    status: str
    filled_quantity: int = 0
    avg_fill_price: float = 0.0

# === CONNECTEUR API REST IBKR ===

class IBKRRestConnector:
    """
    CONNECTEUR API REST IBKR - VERSION MODERNE
    
    🔧 AVANTAGES :
    - Pas besoin de TWS/Gateway
    - API REST stable et moderne
    - Authentification OAuth/JWT
    - Endpoints spécialisés trading
    - Documentation complète disponible
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialisation connecteur API REST IBKR"""
        self.config = config or {}
        
        # Configuration API REST
        self.base_url = self.config.get('ibkr_rest_url', 'https://api.ibkr.com')
        self.api_version = self.config.get('api_version', 'v1')
        self.client_id = self.config.get('client_id', '')
        self.access_token = self.config.get('access_token', '')
        
        # État connexion
        self.connection_status = IBKRConnectionStatus.DISCONNECTED
        self.is_connected_flag = False
        self.last_connection_attempt = None
        
        # Session requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MIA_IA_SYSTEM/3.0.0',
            'Content-Type': 'application/json'
        })
        
        # Cache données
        self.market_data_cache: Dict[str, IBKRMarketData] = {}
        self.positions_cache: Dict[str, IBKRPosition] = {}
        self.orders_cache: Dict[int, IBKROrder] = {}
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms entre requêtes
        
    def _rate_limit(self):
        """Rate limiting pour respecter les limites API"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Effectuer une requête API REST"""
        self._rate_limit()
        
        url = f"{self.base_url}/{self.api_version}/{endpoint}"
        
        # Ajouter headers d'authentification
        if self.access_token:
            self.session.headers['Authorization'] = f'Bearer {self.access_token}'
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur requête API REST: {e}")
            return {}
    
    async def connect(self) -> bool:
        """Connexion à l'API REST IBKR"""
        print("🔗 Connexion API REST IBKR...")
        
        self.connection_status = IBKRConnectionStatus.CONNECTING
        self.last_connection_attempt = datetime.now()
        
        try:
            # Test connexion avec endpoint echo
            test_response = self._make_request('GET', 'echo/https')
            
            if test_response:
                self.connection_status = IBKRConnectionStatus.CONNECTED
                self.is_connected_flag = True
                print("✅ Connexion API REST IBKR réussie !")
                return True
            else:
                self.connection_status = IBKRConnectionStatus.ERROR
                print("❌ Échec connexion API REST IBKR")
                return False
                
        except Exception as e:
            self.connection_status = IBKRConnectionStatus.ERROR
            print(f"❌ Erreur connexion: {e}")
            return False
    
    async def disconnect(self):
        """Déconnexion API REST IBKR"""
        print("🔌 Déconnexion API REST IBKR...")
        
        self.connection_status = IBKRConnectionStatus.DISCONNECTED
        self.is_connected_flag = False
        self.session.close()
        
        print("✅ Déconnexion API REST IBKR terminée")
    
    def is_connected(self) -> bool:
        """Vérifier si connecté"""
        return self.is_connected_flag
    
    # === ENDPOINTS TRADING ===
    
    async def get_account_info(self) -> Dict:
        """Récupérer informations compte"""
        if not self.is_connected():
            return {}
        
        try:
            # Endpoint: /iserver/account
            response = self._make_request('POST', 'iserver/account')
            return response
        except Exception as e:
            print(f"❌ Erreur récupération compte: {e}")
            return {}
    
    async def get_positions(self) -> List[IBKRPosition]:
        """Récupérer positions"""
        if not self.is_connected():
            return []
        
        try:
            # Endpoint: /iserver/portfolio/positions
            response = self._make_request('GET', 'iserver/portfolio/positions')
            
            positions = []
            for pos_data in response.get('positions', []):
                position = IBKRPosition(
                    symbol=pos_data.get('symbol', ''),
                    quantity=pos_data.get('position', 0),
                    avg_price=pos_data.get('avgPrice', 0.0),
                    market_value=pos_data.get('marketValue', 0.0),
                    unrealized_pnl=pos_data.get('unrealizedPnL', 0.0),
                    currency=pos_data.get('currency', 'USD')
                )
                positions.append(position)
                self.positions_cache[position.symbol] = position
            
            return positions
            
        except Exception as e:
            print(f"❌ Erreur récupération positions: {e}")
            return []
    
    async def get_market_data(self, symbol: str) -> Optional[IBKRMarketData]:
        """Récupérer données de marché"""
        if not self.is_connected():
            return None
        
        try:
            # Endpoint: /iserver/marketdata/snapshot
            params = {
                'conids': symbol,
                'fields': '31,84,86'  # Bid, Ask, Last
            }
            
            response = self._make_request('GET', 'iserver/marketdata/snapshot', params=params)
            
            if response and 'data' in response:
                data = response['data'][0]
                
                market_data = IBKRMarketData(
                    symbol=symbol,
                    price=data.get('31', 0.0),  # Last price
                    bid=data.get('84', 0.0),    # Bid
                    ask=data.get('86', 0.0),    # Ask
                    volume=data.get('7762', 0), # Volume
                    timestamp=datetime.now(),
                    exchange="CME",
                    currency="USD"
                )
                
                self.market_data_cache[symbol] = market_data
                return market_data
            
            return None
            
        except Exception as e:
            print(f"❌ Erreur récupération market data: {e}")
            return None
    
    async def place_order(self, order: IBKROrder) -> bool:
        """Placer un ordre"""
        if not self.is_connected():
            return False
        
        try:
            # Endpoint: /iserver/order
            order_data = {
                'acctId': self.client_id,
                'conid': order.symbol,
                'orderType': order.order_type,
                'side': order.side,
                'quantity': order.quantity,
                'tif': 'DAY'
            }
            
            response = self._make_request('POST', 'iserver/order', json=order_data)
            
            if response and 'order_id' in response:
                order.order_id = response['order_id']
                self.orders_cache[order.order_id] = order
                print(f"✅ Ordre placé: {order.order_id}")
                return True
            else:
                print("❌ Échec placement ordre")
                return False
                
        except Exception as e:
            print(f"❌ Erreur placement ordre: {e}")
            return False
    
    async def get_orders(self) -> List[IBKROrder]:
        """Récupérer ordres"""
        if not self.is_connected():
            return []
        
        try:
            # Endpoint: /iserver/orders
            response = self._make_request('GET', 'iserver/orders')
            
            orders = []
            for order_data in response.get('orders', []):
                order = IBKROrder(
                    order_id=order_data.get('orderId', 0),
                    symbol=order_data.get('conid', ''),
                    side=order_data.get('side', ''),
                    quantity=order_data.get('quantity', 0),
                    order_type=order_data.get('orderType', ''),
                    status=order_data.get('status', ''),
                    filled_quantity=order_data.get('filledQuantity', 0),
                    avg_fill_price=order_data.get('avgFillPrice', 0.0)
                )
                orders.append(order)
                self.orders_cache[order.order_id] = order
            
            return orders
            
        except Exception as e:
            print(f"❌ Erreur récupération ordres: {e}")
            return []
    
    # === MÉTHODES UTILITAIRES ===
    
    def get_connection_status(self) -> IBKRConnectionStatus:
        """Obtenir statut connexion"""
        return self.connection_status
    
    def get_cached_market_data(self, symbol: str) -> Optional[IBKRMarketData]:
        """Obtenir données de marché en cache"""
        return self.market_data_cache.get(symbol)
    
    def get_cached_position(self, symbol: str) -> Optional[IBKRPosition]:
        """Obtenir position en cache"""
        return self.positions_cache.get(symbol)
    
    def clear_cache(self):
        """Vider le cache"""
        self.market_data_cache.clear()
        self.positions_cache.clear()
        self.orders_cache.clear()

# === FONCTIONS UTILITAIRES ===

def create_ibkr_rest_connector(config: Optional[Dict] = None) -> IBKRRestConnector:
    """Créer un connecteur API REST IBKR"""
    return IBKRRestConnector(config)

def test_ibkr_rest_connection():
    """Test connexion API REST IBKR"""
    print("🧪 Test connexion API REST IBKR...")
    
    config = {
        'ibkr_rest_url': 'https://api.ibkr.com',
        'api_version': 'v1',
        'client_id': 'test_client'
    }
    
    connector = create_ibkr_rest_connector(config)
    
    # Test connexion
    import asyncio
    success = asyncio.run(connector.connect())
    
    if success:
        print("✅ API REST IBKR opérationnelle")
        
        # Test récupération données
        account_info = asyncio.run(connector.get_account_info())
        if account_info:
            print("✅ Récupération compte réussie")
        
        asyncio.run(connector.disconnect())
        return True
    else:
        print("❌ API REST IBKR non accessible")
        return False

if __name__ == "__main__":
    test_ibkr_rest_connection()
















