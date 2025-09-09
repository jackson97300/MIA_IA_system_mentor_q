#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - IBKR Web API REST Adapter
Remplacement TWS/Gateway par API REST moderne
"""

import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
import json

from core.logger import get_logger
from core.base_types import MarketData, OrderFlowData

logger = get_logger(__name__)

@dataclass
class IBKRWebAPIConfig:
    """Configuration IBKR Web API REST"""
    # Authentification
    api_key: str = ""
    api_secret: str = ""
    account_id: str = ""
    
    # Connexion
    base_url: str = "https://www.interactivebrokers.com/iserver"
    timeout: int = 30
    max_retries: int = 3
    
    # Options
    paper_trading: bool = True
    enable_trading: bool = False
    enable_market_data: bool = True

class IBKRWebAPIAdapter:
    """
    Adaptateur IBKR Web API REST pour MIA_IA_SYSTEM
    Remplace TWS/Gateway par API REST moderne
    """

    def __init__(self, config: IBKRWebAPIConfig):
        self.config = config
        self.connected = False
        self.session = None
        self.auth_token = None
        
        # Cache données
        self.market_data_cache: Dict[str, MarketData] = {}
        self.last_update = {}
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = datetime.now()

    async def connect(self) -> bool:
        """Connexion IBKR Web API REST"""
        try:
            # Créer session HTTP
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
            
            # Authentification (OAuth ou API Key)
            auth_success = await self._authenticate()
            if not auth_success:
                logger.error("❌ Échec authentification IBKR Web API")
                return False
            
            # Test connexion
            account_info = await self.get_account_info()
            if account_info:
                logger.info(f"✅ IBKR Web API connecté: {account_info.get('account_id', 'N/A')}")
                self.connected = True
                return True
            else:
                logger.error("❌ Impossible de récupérer les infos compte")
                return False

        except Exception as e:
            logger.error(f"❌ Erreur connexion IBKR Web API: {e}")
            return False

    async def _authenticate(self) -> bool:
        """Authentification IBKR Web API"""
        try:
            # Méthode 1: OAuth (si disponible)
            if self.config.api_key and self.config.api_secret:
                auth_url = f"{self.config.base_url}/auth/oauth/token"
                auth_data = {
                    "grant_type": "client_credentials",
                    "client_id": self.config.api_key,
                    "client_secret": self.config.api_secret
                }
                
                async with self.session.post(auth_url, json=auth_data) as response:
                    if response.status == 200:
                        auth_result = await response.json()
                        self.auth_token = auth_result.get("access_token")
                        logger.info("✅ Authentification OAuth réussie")
                        return True
            
            # Méthode 2: API Key simple (fallback)
            if self.config.api_key:
                self.auth_token = self.config.api_key
                logger.info("✅ Authentification API Key réussie")
                return True
            
            logger.error("❌ Aucune méthode d'authentification configurée")
            return False

        except Exception as e:
            logger.error(f"❌ Erreur authentification: {e}")
            return False

    async def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Optional[Dict]:
        """Faire une requête à l'IBKR Web API"""
        try:
            url = f"{self.config.base_url}{endpoint}"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            # Rate limiting
            await self._rate_limit()
            
            if method == "GET":
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"❌ Erreur GET {endpoint}: {response.status}")
                        return None
            
            elif method == "POST":
                async with self.session.post(url, headers=headers, json=data) as response:
                    if response.status in [200, 201]:
                        return await response.json()
                    else:
                        logger.error(f"❌ Erreur POST {endpoint}: {response.status}")
                        return None

        except Exception as e:
            logger.error(f"❌ Erreur requête {endpoint}: {e}")
            return None

    async def _rate_limit(self):
        """Rate limiting pour respecter les limites IBKR"""
        now = datetime.now()
        time_diff = (now - self.last_request_time).total_seconds()
        
        # Limite: 50 requêtes par minute
        if time_diff < 1.2:  # 60/50 = 1.2 secondes entre requêtes
            await asyncio.sleep(1.2 - time_diff)
        
        self.last_request_time = now
        self.request_count += 1

    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Informations compte via Web API"""
        try:
            endpoint = f"/account/{self.config.account_id}/summary"
            account_data = await self._make_request(endpoint)
            
            if account_data:
                return {
                    'account_id': self.config.account_id,
                    'available_funds': account_data.get('available_funds', 0.0),
                    'buying_power': account_data.get('buying_power', 0.0),
                    'equity': account_data.get('equity', 0.0),
                    'net_liquidation': account_data.get('net_liquidation', 0.0),
                    'status': 'ACTIVE'
                }
            
            return None

        except Exception as e:
            logger.error(f"❌ Erreur account info: {e}")
            return None

    async def get_market_data(self, symbol: str = "ES") -> Optional[MarketData]:
        """Données marché temps réel via Web API"""
        try:
            # Endpoint pour données ES futures
            endpoint = f"/market_data/{symbol}/snapshot"
            market_data = await self._make_request(endpoint)
            
            if market_data:
                data = MarketData(
                    timestamp=pd.Timestamp.now(),
                    symbol=symbol,
                    open=market_data.get('open', 0.0),
                    high=market_data.get('high', 0.0),
                    low=market_data.get('low', 0.0),
                    close=market_data.get('close', 0.0),
                    volume=market_data.get('volume', 0),
                    bid=market_data.get('bid', 0.0),
                    ask=market_data.get('ask', 0.0)
                )
                
                self.market_data_cache[symbol] = data
                return data
            
            return None

        except Exception as e:
            logger.error(f"❌ Erreur market data: {e}")
            return None

    async def get_es_futures_data(self, timeframe: str = "1min", limit: int = 100) -> Optional[pd.DataFrame]:
        """Données ES futures historiques via Web API"""
        try:
            # Endpoint pour données historiques
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            
            endpoint = f"/market_data/ES/history"
            params = {
                "period": "1d",
                "bar": timeframe,
                "outsideRth": True
            }
            
            historical_data = await self._make_request(endpoint)
            
            if historical_data and 'bars' in historical_data:
                data = []
                for bar in historical_data['bars']:
                    data.append({
                        'timestamp': pd.to_datetime(bar['t'], unit='ms'),
                        'open': bar['o'],
                        'high': bar['h'],
                        'low': bar['l'],
                        'close': bar['c'],
                        'volume': bar['v']
                    })
                
                df = pd.DataFrame(data)
                logger.info(f"✅ Données ES récupérées: {len(df)} barres")
                return df
            
            return None

        except Exception as e:
            logger.error(f"❌ Erreur données ES: {e}")
            return None

    async def get_options_chain(self, symbol: str = "SPX") -> Optional[Dict[str, Any]]:
        """Options chain SPX via Web API"""
        try:
            # Endpoint pour options chain
            endpoint = f"/market_data/{symbol}/options"
            options_data = await self._make_request(endpoint)
            
            if options_data:
                # Analyse gamma levels
                gamma_analysis = self._analyze_gamma_levels(options_data)
                
                return {
                    'options_chain': options_data,
                    'gamma_analysis': gamma_analysis,
                    'total_volume': sum(opt.get('volume', 0) for opt in options_data.get('options', [])),
                    'expiration_dates': list(set(opt.get('expiration') for opt in options_data.get('options', [])))
                }
            
            return None

        except Exception as e:
            logger.error(f"❌ Erreur options chain: {e}")
            return None

    def _analyze_gamma_levels(self, options_data: Dict) -> Dict[str, Any]:
        """Analyse gamma levels pour Battle Navale"""
        try:
            gamma_data = {
                'call_wall': None,
                'put_wall': None,
                'gamma_exposure': 0.0,
                'high_gamma_levels': []
            }
            
            # Analyse des options pour gamma levels
            if 'options' in options_data:
                strikes = {}
                for opt in options_data['options']:
                    strike = opt.get('strike')
                    if strike not in strikes:
                        strikes[strike] = {'calls': [], 'puts': []}
                    
                    if opt.get('type') == 'call':
                        strikes[strike]['calls'].append(opt)
                    else:
                        strikes[strike]['puts'].append(opt)
                
                # Trouver call/put walls
                max_call_volume = 0
                max_put_volume = 0
                
                for strike, data in strikes.items():
                    call_volume = sum(opt.get('volume', 0) for opt in data['calls'])
                    put_volume = sum(opt.get('volume', 0) for opt in data['puts'])
                    
                    if call_volume > max_call_volume:
                        max_call_volume = call_volume
                        gamma_data['call_wall'] = strike
                    
                    if put_volume > max_put_volume:
                        max_put_volume = put_volume
                        gamma_data['put_wall'] = strike
            
            return gamma_data

        except Exception as e:
            logger.error(f"❌ Erreur analyse gamma: {e}")
            return {}

    async def place_order(self, order_data: Dict) -> Optional[Dict]:
        """Placer un ordre via Web API"""
        try:
            if not self.config.enable_trading:
                logger.warning("⚠️ Trading désactivé - simulation d'ordre")
                return {
                    'order_id': f"SIM_{datetime.now().timestamp()}",
                    'status': 'SUBMITTED',
                    'filled_quantity': 0,
                    'avg_fill_price': 0.0
                }
            
            # Endpoint pour placer ordres
            endpoint = f"/account/{self.config.account_id}/orders"
            order_result = await self._make_request(endpoint, method="POST", data=order_data)
            
            if order_result:
                logger.info(f"✅ Ordre placé: {order_result.get('order_id')}")
                return order_result
            
            return None

        except Exception as e:
            logger.error(f"❌ Erreur placement ordre: {e}")
            return None

    async def get_positions(self) -> List[Dict]:
        """Positions actuelles via Web API"""
        try:
            endpoint = f"/account/{self.config.account_id}/positions"
            positions_data = await self._make_request(endpoint)
            
            if positions_data and 'positions' in positions_data:
                return positions_data['positions']
            
            return []

        except Exception as e:
            logger.error(f"❌ Erreur positions: {e}")
            return []

    async def disconnect(self):
        """Déconnexion Web API"""
        try:
            if self.session:
                await self.session.close()
            
            self.connected = False
            logger.info("✅ Déconnexion IBKR Web API")

        except Exception as e:
            logger.error(f"❌ Erreur déconnexion: {e}")

# Configuration par défaut
DEFAULT_IBKR_WEB_API_CONFIG = IBKRWebAPIConfig(
    api_key="YOUR_IBKR_API_KEY",
    api_secret="YOUR_IBKR_API_SECRET",
    account_id="YOUR_ACCOUNT_ID",
    paper_trading=True,
    enable_trading=False,
    enable_market_data=True
)

async def test_ibkr_web_api_connection():
    """Test connexion IBKR Web API REST"""
    logger.info("🔧 Test connexion IBKR Web API REST...")

    adapter = IBKRWebAPIAdapter(DEFAULT_IBKR_WEB_API_CONFIG)
    success = await adapter.connect()

    if success:
        # Test account info
        account_info = await adapter.get_account_info()
        if account_info:
            logger.info(f"✅ Account info: {account_info.get('account_id')}")

        # Test market data
        market_data = await adapter.get_market_data("ES")
        if market_data:
            logger.info(f"✅ Market data ES: {market_data.close}")

        # Test ES futures data
        es_data = await adapter.get_es_futures_data()
        if es_data is not None:
            logger.info(f"✅ Données ES: {len(es_data)} barres")

        await adapter.disconnect()

    return success

if __name__ == "__main__":
    asyncio.run(test_ibkr_web_api_connection())
















