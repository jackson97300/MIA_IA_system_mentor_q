#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Polygon.io Data Adapter
Alternative premium à IBKR avec données complètes
"""

import asyncio
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

from core.logger import get_logger
from core.base_types import MarketData, OrderFlowData

logger = get_logger(__name__)

@dataclass
class PolygonConfig:
    """Configuration Polygon.io"""
    api_key: str = ""
    plan: str = "developer"  # starter, developer, professional
    base_url: str = "https://api.polygon.io"
    
    # Plans et limites
    plans = {
        "starter": {"monthly_cost": 29, "requests_per_minute": 5},
        "developer": {"monthly_cost": 99, "requests_per_minute": 10},
        "professional": {"monthly_cost": 299, "requests_per_minute": 25}
    }

class PolygonDataAdapter:
    """
    Adaptateur Polygon.io pour MIA_IA_SYSTEM
    Alternative premium avec données complètes
    """
    
    def __init__(self, config: PolygonConfig):
        self.config = config
        self.connected = False
        self.client = None
        
        # Cache et rate limiting
        self.market_data_cache: Dict[str, MarketData] = {}
        self.last_request_time = {}
        self.request_count = 0
        
    async def connect(self) -> bool:
        """Connexion Polygon.io"""
        try:
            from polygon import RESTClient
            
            self.client = RESTClient(self.config.api_key)
            
            # Test connexion
            ticker = self.client.get_last_trade("AAPL")
            logger.info(f"✅ Polygon.io connecté: {ticker.price}")
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion Polygon: {e}")
            return False
    
    async def get_es_futures_data(self, timeframe: str = "1min", limit: int = 100) -> Optional[pd.DataFrame]:
        """Récupère données ES futures complètes"""
        try:
            if not self.connected:
                await self.connect()
            
            # ES futures - données complètes
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            
            bars = self.client.get_aggs(
                ticker="ES",
                multiplier=1,
                timespan=timeframe,
                from_=start_date.strftime("%Y-%m-%d"),
                to=end_date.strftime("%Y-%m-%d"),
                limit=limit,
                adjusted=True
            )
            
            # Conversion DataFrame avec données enrichies
            data = []
            for bar in bars:
                data.append({
                    'timestamp': pd.to_datetime(bar.timestamp, unit='ms'),
                    'open': bar.open,
                    'high': bar.high,
                    'low': bar.low,
                    'close': bar.close,
                    'volume': bar.volume,
                    'vwap': bar.vwap if hasattr(bar, 'vwap') else None,
                    'transactions': bar.transactions if hasattr(bar, 'transactions') else None
                })
            
            df = pd.DataFrame(data)
            logger.info(f"✅ Données ES récupérées: {len(df)} barres")
            return df
            
        except Exception as e:
            logger.error(f"❌ Erreur données ES: {e}")
            return None
    
    async def get_real_time_market_data(self, symbol: str = "ES") -> Optional[MarketData]:
        """Données temps réel avec bid/ask"""
        try:
            if not self.connected:
                await self.connect()
            
            # Dernier trade
            last_trade = self.client.get_last_trade(symbol)
            
            # Dernier quote (bid/ask)
            last_quote = self.client.get_last_quote(symbol)
            
            market_data = MarketData(
                timestamp=pd.Timestamp.now(),
                symbol=symbol,
                open=last_trade.price,
                high=last_trade.price,
                low=last_trade.price,
                close=last_trade.price,
                volume=last_trade.size,
                bid=last_quote.bid_price if last_quote else last_trade.price - 0.25,
                ask=last_quote.ask_price if last_quote else last_trade.price + 0.25
            )
            
            self.market_data_cache[symbol] = market_data
            return market_data
            
        except Exception as e:
            logger.error(f"❌ Erreur market data temps réel: {e}")
            return None
    
    async def get_options_chain_complete(self, symbol: str = "SPX") -> Dict[str, Any]:
        """Options chain complète avec gamma analysis"""
        try:
            if not self.connected:
                await self.connect()
            
            # Options chain complète
            options_chain = self.client.get_options_chain(
                underlying_asset=symbol,
                strike_price=None,
                contract_type=None,
                expiration_date=None,
                limit=1000
            )
            
            # Analyse gamma levels
            gamma_analysis = self._analyze_gamma_levels(options_chain)
            
            return {
                'options_chain': options_chain,
                'gamma_analysis': gamma_analysis,
                'total_volume': sum(opt.volume for opt in options_chain if hasattr(opt, 'volume')),
                'expiration_dates': list(set(opt.expiration_date for opt in options_chain))
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur options chain: {e}")
            return {}
    
    def _analyze_gamma_levels(self, options_chain) -> Dict[str, Any]:
        """Analyse gamma levels pour Battle Navale"""
        try:
            # Groupement par strike
            strikes = {}
            for opt in options_chain:
                strike = opt.strike_price
                if strike not in strikes:
                    strikes[strike] = {'calls': [], 'puts': []}
                
                if opt.contract_type == 'call':
                    strikes[strike]['calls'].append(opt)
                else:
                    strikes[strike]['puts'].append(opt)
            
            # Calcul gamma exposure
            gamma_data = {
                'call_wall': None,
                'put_wall': None,
                'gamma_exposure': 0.0,
                'high_gamma_levels': []
            }
            
            # Trouver call/put walls
            max_call_volume = 0
            max_put_volume = 0
            
            for strike, data in strikes.items():
                call_volume = sum(opt.volume for opt in data['calls'] if hasattr(opt, 'volume'))
                put_volume = sum(opt.volume for opt in data['puts'] if hasattr(opt, 'volume'))
                
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
    
    async def get_order_flow_data(self, symbol: str = "ES") -> Optional[OrderFlowData]:
        """Données order flow (si disponible)"""
        try:
            if not self.connected:
                await self.connect()
            
            # Trades récents pour order flow
            trades = self.client.get_trades(
                symbol,
                timestamp=None,
                order=None,
                sort=None,
                limit=100
            )
            
            # Analyse order flow
            buy_volume = 0
            sell_volume = 0
            
            for trade in trades:
                if hasattr(trade, 'conditions'):
                    # Déterminer si achat/vente basé sur conditions
                    if 'buy' in str(trade.conditions).lower():
                        buy_volume += trade.size
                    else:
                        sell_volume += trade.size
            
            order_flow = OrderFlowData(
                timestamp=pd.Timestamp.now(),
                symbol=symbol,
                buy_volume=buy_volume,
                sell_volume=sell_volume,
                net_flow=buy_volume - sell_volume,
                imbalance=(buy_volume - sell_volume) / (buy_volume + sell_volume) if (buy_volume + sell_volume) > 0 else 0
            )
            
            return order_flow
            
        except Exception as e:
            logger.error(f"❌ Erreur order flow: {e}")
            return None
    
    async def get_historical_data(self, symbol: str = "ES", days: int = 30) -> Optional[pd.DataFrame]:
        """Données historiques complètes"""
        try:
            if not self.connected:
                await self.connect()
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            bars = self.client.get_aggs(
                ticker=symbol,
                multiplier=1,
                timespan="day",
                from_=start_date.strftime("%Y-%m-%d"),
                to=end_date.strftime("%Y-%m-%d"),
                adjusted=True
            )
            
            data = []
            for bar in bars:
                data.append({
                    'date': pd.to_datetime(bar.timestamp, unit='ms'),
                    'open': bar.open,
                    'high': bar.high,
                    'low': bar.low,
                    'close': bar.close,
                    'volume': bar.volume,
                    'vwap': bar.vwap if hasattr(bar, 'vwap') else None
                })
            
            df = pd.DataFrame(data)
            logger.info(f"✅ Historique {symbol}: {len(df)} jours")
            return df
            
        except Exception as e:
            logger.error(f"❌ Erreur historique: {e}")
            return None

# Configuration par défaut
DEFAULT_POLYGON_CONFIG = PolygonConfig(
    api_key="YOUR_POLYGON_KEY",
    plan="developer"
)

async def test_polygon_connection():
    """Test connexion Polygon.io"""
    logger.info("🔧 Test connexion Polygon.io...")
    
    adapter = PolygonDataAdapter(DEFAULT_POLYGON_CONFIG)
    success = await adapter.connect()
    
    if success:
        # Test données ES
        es_data = await adapter.get_es_futures_data()
        if es_data is not None:
            logger.info(f"✅ Données ES: {len(es_data)} barres")
        
        # Test market data temps réel
        market_data = await adapter.get_real_time_market_data()
        if market_data:
            logger.info(f"✅ Market data: {market_data.close} (bid: {market_data.bid}, ask: {market_data.ask})")
        
        # Test options
        options_data = await adapter.get_options_chain_complete()
        if options_data:
            logger.info(f"✅ Options data: {len(options_data.get('options_chain', []))} contrats")
    
    return success

if __name__ == "__main__":
    asyncio.run(test_polygon_connection())
















