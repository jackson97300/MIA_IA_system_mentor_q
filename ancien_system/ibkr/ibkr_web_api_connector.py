#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Connecteur API Web IBKR
Basé sur la documentation officielle IBKR Web API
"""

import asyncio
import aiohttp
import json
import time
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlencode

# === TYPES ET ENUMS ===

class IBKRWebAPIService(Enum):
    TRADING = "trading"
    ACCOUNT = "account"
    FLEX = "flex"
    MARKET_DATA = "market_data"

@dataclass
class IBKRWebAPIConfig:
    """Configuration API Web IBKR"""
    base_url: str = "https://api.ibkr.com"
    api_version: str = "v1"
    client_id: str = ""
    client_secret: str = ""
    access_token: str = ""
    refresh_token: str = ""
    redirect_uri: str = ""

@dataclass
class IBKRMarketData:
    """Données de marché IBKR Web API"""
    symbol: str
    price: float
    bid: float
    ask: float
    volume: int
    timestamp: datetime
    exchange: str = "CME"
    currency: str = "USD"

# === CONNECTEUR API WEB IBKR ===

class IBKRWebAPIConnector:
    """
    CONNECTEUR API WEB IBKR
    Basé sur la documentation officielle
    """
    
    def __init__(self, config: Optional[IBKRWebAPIConfig] = None):
        """Initialisation connecteur API Web"""
        self.config = config or IBKRWebAPIConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.connected = False
        self.access_token_expiry = None
        
        # Headers par défaut
        self.default_headers = {
            'User-Agent': 'MIA_IA_SYSTEM/3.0.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Cache
        self.market_data_cache: Dict[str, IBKRMarketData] = {}
        self.positions_cache: Dict[str, Any] = {}
        
    async def __aenter__(self):
        """Context manager entry"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.disconnect()
    
    async def connect(self) -> bool:
        """Connexion API Web IBKR"""
        print("🔗 Connexion API Web IBKR...")
        
        try:
            # Créer session HTTP
            self.session = aiohttp.ClientSession(
                headers=self.default_headers,
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Test connexion basique (sans authentification)
            success = await self._test_connection()
            
            if success:
                self.connected = True
                print("✅ API Web IBKR accessible")
                return True
            else:
                print("❌ API Web IBKR non accessible")
                return False
                
        except Exception as e:
            print(f"❌ Erreur connexion API Web: {e}")
            return False
    
    async def disconnect(self):
        """Déconnexion"""
        print("🔌 Déconnexion API Web IBKR...")
        
        if self.session:
            await self.session.close()
            self.session = None
        
        self.connected = False
        print("✅ API Web IBKR déconnectée")
    
    async def _test_connection(self) -> bool:
        """Test connexion basique"""
        try:
            # Endpoint echo (sans authentification)
            url = f"{self.config.base_url}/{self.config.api_version}/echo/https"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Echo API: {data.get('message', 'OK')}")
                    return True
                else:
                    print(f"❌ Echo API: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Erreur test connexion: {e}")
            return False
    
    async def authenticate_oauth(self) -> bool:
        """Authentification OAuth 1.0a"""
        print("🔐 Authentification OAuth IBKR...")
        
        try:
            # Étape 1: Obtenir request token
            request_token = await self._get_request_token()
            if not request_token:
                return False
            
            # Étape 2: Autorisation utilisateur
            auth_url = await self._get_authorization_url(request_token)
            print(f"🔗 URL d'autorisation: {auth_url}")
            print("⚠️ Ouvrez cette URL dans votre navigateur pour autoriser l'application")
            
            # Étape 3: Échanger contre access token
            verifier = input("Entrez le code de vérification: ")
            access_token = await self._exchange_for_access_token(request_token, verifier)
            
            if access_token:
                self.config.access_token = access_token
                print("✅ Authentification OAuth réussie")
                return True
            else:
                print("❌ Échec authentification OAuth")
                return False
                
        except Exception as e:
            print(f"❌ Erreur authentification: {e}")
            return False
    
    async def _get_request_token(self) -> Optional[str]:
        """Obtenir request token OAuth"""
        try:
            # Paramètres OAuth
            oauth_params = {
                'oauth_consumer_key': self.config.client_id,
                'oauth_nonce': str(int(time.time() * 1000)),
                'oauth_signature_method': 'HMAC-SHA256',
                'oauth_timestamp': str(int(time.time())),
                'oauth_version': '1.0'
            }
            
            # URL de base
            url = f"{self.config.base_url}/oauth/request_token"
            
            # Signature OAuth
            signature = self._create_oauth_signature('GET', url, oauth_params)
            oauth_params['oauth_signature'] = signature
            
            # Headers OAuth
            oauth_header = self._create_oauth_header(oauth_params)
            headers = {'Authorization': oauth_header}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.text()
                    # Parser response token
                    params = dict(item.split('=') for item in data.split('&'))
                    return params.get('oauth_token')
                else:
                    print(f"❌ Erreur request token: {response.status}")
                    return None
                    
        except Exception as e:
            print(f"❌ Erreur request token: {e}")
            return None
    
    async def _get_authorization_url(self, request_token: str) -> str:
        """Obtenir URL d'autorisation"""
        return f"{self.config.base_url}/oauth/authorize?oauth_token={request_token}"
    
    async def _exchange_for_access_token(self, request_token: str, verifier: str) -> Optional[str]:
        """Échanger request token contre access token"""
        try:
            # Paramètres OAuth
            oauth_params = {
                'oauth_consumer_key': self.config.client_id,
                'oauth_nonce': str(int(time.time() * 1000)),
                'oauth_signature_method': 'HMAC-SHA256',
                'oauth_timestamp': str(int(time.time())),
                'oauth_token': request_token,
                'oauth_verifier': verifier,
                'oauth_version': '1.0'
            }
            
            # URL de base
            url = f"{self.config.base_url}/oauth/access_token"
            
            # Signature OAuth
            signature = self._create_oauth_signature('POST', url, oauth_params)
            oauth_params['oauth_signature'] = signature
            
            # Headers OAuth
            oauth_header = self._create_oauth_header(oauth_params)
            headers = {'Authorization': oauth_header}
            
            async with self.session.post(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.text()
                    # Parser access token
                    params = dict(item.split('=') for item in data.split('&'))
                    return params.get('oauth_token')
                else:
                    print(f"❌ Erreur access token: {response.status}")
                    return None
                    
        except Exception as e:
            print(f"❌ Erreur access token: {e}")
            return None
    
    def _create_oauth_signature(self, method: str, url: str, params: Dict) -> str:
        """Créer signature OAuth"""
        # Paramètres triés
        sorted_params = sorted(params.items())
        param_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        # String à signer
        signature_base = f"{method}&{url}&{param_string}"
        
        # Clé de signature
        signing_key = f"{self.config.client_secret}&"
        
        # Signature HMAC-SHA256
        signature = hmac.new(
            signing_key.encode('utf-8'),
            signature_base.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def _create_oauth_header(self, params: Dict) -> str:
        """Créer header OAuth"""
        oauth_parts = [f'{k}="{v}"' for k, v in params.items()]
        return f'OAuth {", ".join(oauth_parts)}'
    
    # === DONNÉES DE MARCHÉ ===
    
    async def get_market_data(self, symbol: str) -> Optional[IBKRMarketData]:
        """Récupérer données de marché"""
        if not self.connected:
            return None
        
        try:
            # Endpoint market data snapshot
            url = f"{self.config.base_url}/{self.config.api_version}/iserver/marketdata/snapshot"
            params = {
                'conids': symbol,
                'fields': '31,84,86,7762'  # Last, Bid, Ask, Volume
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'data' in data and data['data']:
                        tick_data = data['data'][0]
                        
                        market_data = IBKRMarketData(
                            symbol=symbol,
                            price=tick_data.get('31', 0.0),  # Last
                            bid=tick_data.get('84', 0.0),    # Bid
                            ask=tick_data.get('86', 0.0),    # Ask
                            volume=tick_data.get('7762', 0), # Volume
                            timestamp=datetime.now()
                        )
                        
                        self.market_data_cache[symbol] = market_data
                        return market_data
                else:
                    print(f"❌ Erreur market data: {response.status}")
            
            return None
            
        except Exception as e:
            print(f"❌ Erreur market data: {e}")
            return None
    
    # === GESTION DE COMPTE ===
    
    async def get_account_info(self) -> Optional[Dict]:
        """Récupérer informations compte"""
        if not self.connected:
            return None
        
        try:
            url = f"{self.config.base_url}/{self.config.api_version}/iserver/account"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"❌ Erreur account info: {response.status}")
                    return None
                    
        except Exception as e:
            print(f"❌ Erreur account info: {e}")
            return None
    
    async def get_positions(self) -> List[Dict]:
        """Récupérer positions"""
        if not self.connected:
            return []
        
        try:
            url = f"{self.config.base_url}/{self.config.api_version}/iserver/portfolio/positions"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('positions', [])
                else:
                    print(f"❌ Erreur positions: {response.status}")
                    return []
                    
        except Exception as e:
            print(f"❌ Erreur positions: {e}")
            return []
    
    # === TRADING ===
    
    async def place_order(self, order_data: Dict) -> bool:
        """Placer un ordre"""
        if not self.connected:
            print("❌ Non connecté pour trading")
            return False
        
        try:
            url = f"{self.config.base_url}/{self.config.api_version}/iserver/order"
            
            async with self.session.post(url, json=order_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Ordre placé: {result}")
                    return True
                else:
                    print(f"❌ Erreur placement ordre: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Erreur placement ordre: {e}")
            return False
    
    # === MÉTHODES UTILITAIRES ===
    
    def is_connected(self) -> bool:
        """Vérifier si connecté"""
        return self.connected
    
    def get_cached_market_data(self, symbol: str) -> Optional[IBKRMarketData]:
        """Obtenir données en cache"""
        return self.market_data_cache.get(symbol)
    
    def clear_cache(self):
        """Vider le cache"""
        self.market_data_cache.clear()
        self.positions_cache.clear()

# === FONCTIONS UTILITAIRES ===

def create_ibkr_web_api_connector(config: Optional[IBKRWebAPIConfig] = None) -> IBKRWebAPIConnector:
    """Créer un connecteur API Web IBKR"""
    return IBKRWebAPIConnector(config)

async def test_ibkr_web_api():
    """Test API Web IBKR"""
    print("🧪 Test API Web IBKR...")
    
    config = IBKRWebAPIConfig(
        base_url="https://api.ibkr.com",
        api_version="v1"
    )
    
    async with create_ibkr_web_api_connector(config) as connector:
        if connector.is_connected():
            print("✅ API Web IBKR connectée")
            
            # Test market data
            market_data = await connector.get_market_data("ES")
            if market_data:
                print(f"✅ Market data ES: {market_data.price}")
            
            # Test account info
            account_info = await connector.get_account_info()
            if account_info:
                print(f"✅ Account info: {account_info.get('accountId', 'N/A')}")
            
            return True
        else:
            print("❌ Échec connexion API Web IBKR")
            return False

if __name__ == "__main__":
    asyncio.run(test_ibkr_web_api())
















