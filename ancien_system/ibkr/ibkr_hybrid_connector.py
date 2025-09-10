#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Connecteur Hybride IBKR
Combine TWS/Gateway (trading) + API REST (données complémentaires)
"""

import asyncio
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# === TYPES ET ENUMS ===

class IBKRDataSource(Enum):
    TWS = "tws"           # TWS/Gateway pour trading
    REST_API = "rest"     # API REST pour données
    HYBRID = "hybrid"     # Combinaison des deux

@dataclass
class IBKRMarketData:
    """Données de marché IBKR"""
    symbol: str
    price: float
    bid: float
    ask: float
    volume: int
    timestamp: datetime
    source: IBKRDataSource
    exchange: str = "CME"
    currency: str = "USD"

# === CONNECTEUR HYBRIDE IBKR ===

class IBKRHybridConnector:
    """
    CONNECTEUR HYBRIDE IBKR - VERSION OPTIMALE
    
    🔧 STRATÉGIE :
    - TWS/Gateway : Trading en temps réel
    - API REST : Données complémentaires, historique, analytics
    - Fallback automatique entre sources
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialisation connecteur hybride"""
        self.config = config or {}
        
        # Configuration TWS
        self.tws_host = self.config.get('tws_host', '127.0.0.1')
        self.tws_port = self.config.get('tws_port', 4002)  # IB Gateway Paper
        self.tws_client_id = self.config.get('tws_client_id', 999)
        
        # Configuration API REST
        self.rest_base_url = self.config.get('rest_base_url', 'https://api.ibkr.com')
        self.rest_api_version = self.config.get('rest_api_version', 'v1')
        self.rest_access_token = self.config.get('rest_access_token', '')
        
        # État connexions
        self.tws_connected = False
        self.rest_connected = False
        self.hybrid_mode = True
        
        # Session requests pour API REST
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MIA_IA_SYSTEM/3.0.0',
            'Content-Type': 'application/json'
        })
        
        # Cache données
        self.market_data_cache: Dict[str, IBKRMarketData] = {}
        self.positions_cache: Dict[str, Any] = {}
        self.orders_cache: Dict[int, Any] = {}
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1
        
    def _rate_limit(self):
        """Rate limiting pour API REST"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    async def connect_tws(self) -> bool:
        """Connexion TWS/Gateway"""
        print("🔗 Connexion TWS/Gateway...")
        
        try:
            from ib_insync import IB
            
            self.ib_client = IB()
            self.ib_client.connect(
                self.tws_host, 
                self.tws_port, 
                clientId=self.tws_client_id, 
                timeout=30
            )
            
            if self.ib_client.isConnected():
                self.tws_connected = True
                print("✅ TWS/Gateway connecté")
                return True
            else:
                print("❌ Échec connexion TWS")
                return False
                
        except Exception as e:
            print(f"❌ Erreur connexion TWS: {e}")
            return False
    
    async def connect_rest_api(self) -> bool:
        """Connexion API REST"""
        print("🔗 Connexion API REST IBKR...")
        
        try:
            # Test endpoint echo (sans authentification)
            self._rate_limit()
            response = self.session.get(
                f"{self.rest_base_url}/{self.rest_api_version}/echo/https",
                timeout=10
            )
            
            if response.status_code == 200:
                self.rest_connected = True
                print("✅ API REST IBKR connectée")
                return True
            else:
                print(f"❌ API REST non accessible: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur connexion API REST: {e}")
            return False
    
    async def connect(self) -> bool:
        """Connexion hybride"""
        print("🚀 Connexion hybride IBKR...")
        
        # Connexion TWS (prioritaire pour trading)
        tws_success = await self.connect_tws()
        
        # Connexion API REST (complémentaire)
        rest_success = await self.connect_rest_api()
        
        # État global
        if tws_success or rest_success:
            print("✅ Connexion hybride établie")
            print(f"   - TWS: {'✅' if tws_success else '❌'}")
            print(f"   - API REST: {'✅' if rest_success else '❌'}")
            return True
        else:
            print("❌ Aucune connexion disponible")
            return False
    
    async def disconnect(self):
        """Déconnexion"""
        print("🔌 Déconnexion hybride...")
        
        # Déconnexion TWS
        if self.tws_connected and hasattr(self, 'ib_client'):
            try:
                self.ib_client.disconnect()
                print("✅ TWS déconnecté")
            except:
                pass
        
        # Déconnexion API REST
        if self.rest_connected:
            try:
                self.session.close()
                print("✅ API REST déconnectée")
            except:
                pass
        
        self.tws_connected = False
        self.rest_connected = False
    
    def is_connected(self) -> bool:
        """Vérifier si connecté"""
        return self.tws_connected or self.rest_connected
    
    # === DONNÉES DE MARCHÉ ===
    
    async def get_market_data(self, symbol: str) -> Optional[IBKRMarketData]:
        """Récupérer données de marché (TWS prioritaire)"""
        if not self.is_connected():
            return None
        
        # Essayer TWS d'abord (temps réel)
        if self.tws_connected:
            try:
                from ib_insync import Contract
                
                # Créer contrat ES
                contract = Contract(
                    symbol='ES',
                    secType='FUT',
                    exchange='CME',
                    currency='USD'
                )
                
                # Récupérer données
                self.ib_client.reqMktData(contract)
                await asyncio.sleep(1)  # Attendre données
                
                ticker = self.ib_client.ticker(contract)
                if ticker and ticker.marketPrice():
                    market_data = IBKRMarketData(
                        symbol=symbol,
                        price=ticker.marketPrice(),
                        bid=ticker.bid,
                        ask=ticker.ask,
                        volume=ticker.volume if ticker.volume else 0,
                        timestamp=datetime.now(),
                        source=IBKRDataSource.TWS
                    )
                    
                    self.market_data_cache[symbol] = market_data
                    return market_data
                    
            except Exception as e:
                print(f"⚠️ Erreur TWS market data: {e}")
        
        # Fallback API REST
        if self.rest_connected:
            try:
                return await self._get_rest_market_data(symbol)
            except Exception as e:
                print(f"⚠️ Erreur API REST market data: {e}")
        
        return None
    
    async def _get_rest_market_data(self, symbol: str) -> Optional[IBKRMarketData]:
        """Récupérer données via API REST"""
        try:
            # Endpoint market data snapshot
            params = {
                'conids': symbol,
                'fields': '31,84,86'  # Last, Bid, Ask
            }
            
            self._rate_limit()
            response = self.session.get(
                f"{self.rest_base_url}/{self.rest_api_version}/iserver/marketdata/snapshot",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    tick_data = data['data'][0]
                    
                    market_data = IBKRMarketData(
                        symbol=symbol,
                        price=tick_data.get('31', 0.0),  # Last
                        bid=tick_data.get('84', 0.0),    # Bid
                        ask=tick_data.get('86', 0.0),    # Ask
                        volume=tick_data.get('7762', 0), # Volume
                        timestamp=datetime.now(),
                        source=IBKRDataSource.REST_API
                    )
                    
                    self.market_data_cache[symbol] = market_data
                    return market_data
            
            return None
            
        except Exception as e:
            print(f"❌ Erreur API REST: {e}")
            return None
    
    # === TRADING (TWS uniquement) ===
    
    async def place_order(self, order_data: Dict) -> bool:
        """Placer un ordre (TWS uniquement)"""
        if not self.tws_connected:
            print("❌ TWS non connecté pour trading")
            return False
        
        try:
            from ib_insync import Order, Contract
            
            # Créer contrat
            contract = Contract(
                symbol=order_data.get('symbol', 'ES'),
                secType='FUT',
                exchange='CME',
                currency='USD'
            )
            
            # Créer ordre
            order = Order()
            order.action = order_data.get('side', 'BUY')
            order.totalQuantity = order_data.get('quantity', 1)
            order.orderType = order_data.get('order_type', 'MKT')
            
            # Placer ordre
            trade = self.ib_client.placeOrder(contract, order)
            
            if trade.orderStatus.status == 'Submitted':
                print(f"✅ Ordre placé: {trade.order.orderId}")
                return True
            else:
                print(f"❌ Échec ordre: {trade.orderStatus.status}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur placement ordre: {e}")
            return False
    
    async def get_positions(self) -> List[Dict]:
        """Récupérer positions (TWS prioritaire)"""
        if not self.is_connected():
            return []
        
        # Essayer TWS d'abord
        if self.tws_connected:
            try:
                positions = self.ib_client.positions()
                return [
                    {
                        'symbol': pos.contract.symbol,
                        'quantity': pos.position,
                        'avg_price': pos.avgCost,
                        'market_value': pos.marketValue,
                        'unrealized_pnl': pos.unrealizedPnL,
                        'source': 'TWS'
                    }
                    for pos in positions
                ]
            except Exception as e:
                print(f"⚠️ Erreur TWS positions: {e}")
        
        # Fallback API REST
        if self.rest_connected:
            try:
                return await self._get_rest_positions()
            except Exception as e:
                print(f"⚠️ Erreur API REST positions: {e}")
        
        return []
    
    async def _get_rest_positions(self) -> List[Dict]:
        """Récupérer positions via API REST"""
        try:
            self._rate_limit()
            response = self.session.get(
                f"{self.rest_base_url}/{self.rest_api_version}/iserver/portfolio/positions",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return [
                    {
                        'symbol': pos.get('symbol', ''),
                        'quantity': pos.get('position', 0),
                        'avg_price': pos.get('avgPrice', 0.0),
                        'market_value': pos.get('marketValue', 0.0),
                        'unrealized_pnl': pos.get('unrealizedPnL', 0.0),
                        'source': 'API REST'
                    }
                    for pos in data.get('positions', [])
                ]
            
            return []
            
        except Exception as e:
            print(f"❌ Erreur API REST positions: {e}")
            return []
    
    # === DONNÉES COMPLÉMENTAIRES (API REST) ===
    
    async def get_account_analytics(self) -> Dict:
        """Analytics compte via API REST"""
        if not self.rest_connected:
            return {}
        
        try:
            # Endpoints analytics
            analytics = {}
            
            # Performance historique
            self._rate_limit()
            response = self.session.get(
                f"{self.rest_base_url}/{self.rest_api_version}/iserver/account/pnl/pa",
                timeout=10
            )
            
            if response.status_code == 200:
                analytics['pnl'] = response.json()
            
            # Positions détaillées
            self._rate_limit()
            response = self.session.get(
                f"{self.rest_base_url}/{self.rest_api_version}/iserver/portfolio/positions",
                timeout=10
            )
            
            if response.status_code == 200:
                analytics['positions'] = response.json()
            
            return analytics
            
        except Exception as e:
            print(f"❌ Erreur analytics: {e}")
            return {}
    
    # === MÉTHODES UTILITAIRES ===
    
    def get_connection_status(self) -> Dict:
        """Obtenir statut connexions"""
        return {
            'tws_connected': self.tws_connected,
            'rest_connected': self.rest_connected,
            'hybrid_mode': self.hybrid_mode
        }
    
    def get_cached_market_data(self, symbol: str) -> Optional[IBKRMarketData]:
        """Obtenir données en cache"""
        return self.market_data_cache.get(symbol)
    
    def clear_cache(self):
        """Vider le cache"""
        self.market_data_cache.clear()
        self.positions_cache.clear()
        self.orders_cache.clear()

# === FONCTIONS UTILITAIRES ===

def create_ibkr_hybrid_connector(config: Optional[Dict] = None) -> IBKRHybridConnector:
    """Créer un connecteur hybride IBKR"""
    return IBKRHybridConnector(config)

async def test_hybrid_connection():
    """Test connexion hybride"""
    print("🧪 Test connexion hybride IBKR...")
    
    config = {
        'tws_host': '127.0.0.1',
        'tws_port': 4002,  # IB Gateway Paper
        'tws_client_id': 999,
        'rest_base_url': 'https://api.ibkr.com',
        'rest_api_version': 'v1'
    }
    
    connector = create_ibkr_hybrid_connector(config)
    
    # Test connexion
    success = await connector.connect()
    
    if success:
        print("✅ Connexion hybride réussie")
        
        # Test market data
        market_data = await connector.get_market_data('ES')
        if market_data:
            print(f"✅ Market data: {market_data.price} (source: {market_data.source.value})")
        
        # Test positions
        positions = await connector.get_positions()
        print(f"✅ Positions: {len(positions)} trouvées")
        
        await connector.disconnect()
        return True
    else:
        print("❌ Échec connexion hybride")
        return False

if __name__ == "__main__":
    asyncio.run(test_hybrid_connection())
















