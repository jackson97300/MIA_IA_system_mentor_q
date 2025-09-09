#!/usr/bin/env python3
"""
📊 SIERRA MARKET DATA - Level 2 & Orderflow
Récupération données temps réel depuis Sierra Chart
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
from core.logger import get_logger

logger = get_logger(__name__)

@dataclass
class Level2Data:
    """Données Level 2 (Order Book)"""
    symbol: str
    timestamp: datetime
    bid_levels: List[Dict[str, float]] = field(default_factory=list)  # [{"price": 4500.25, "size": 100}, ...]
    ask_levels: List[Dict[str, float]] = field(default_factory=list)
    best_bid: float = 0.0
    best_ask: float = 0.0
    spread: float = 0.0
    total_bid_size: int = 0
    total_ask_size: int = 0
    imbalance_ratio: float = 0.0  # bid_size / (bid_size + ask_size)

@dataclass
class FootprintData:
    """Données Footprint (Volume par niveau)"""
    symbol: str
    timestamp: datetime
    price_levels: Dict[float, Dict[str, int]] = field(default_factory=dict)  # {4500.25: {"bid_vol": 200, "ask_vol": 150}}
    high_volume_nodes: List[float] = field(default_factory=list)
    value_area_high: float = 0.0
    value_area_low: float = 0.0
    point_of_control: float = 0.0  # Prix avec le plus de volume

@dataclass
class CumulativeDeltaData:
    """Données Cumulative Delta"""
    symbol: str
    timestamp: datetime
    current_delta: float = 0.0
    cumulative_delta: float = 0.0
    delta_divergence: bool = False
    delta_trend: str = "neutral"  # "bullish", "bearish", "neutral"

@dataclass
class SierraMarketData:
    """Données marché complètes Sierra Chart"""
    symbol: str
    timestamp: datetime
    price: float = 0.0
    volume: int = 0
    bid: float = 0.0
    ask: float = 0.0
    last_trade_size: int = 0
    level2: Optional[Level2Data] = None
    footprint: Optional[FootprintData] = None
    cumulative_delta: Optional[CumulativeDeltaData] = None

class SierraMarketDataCollector:
    """Collecteur données marché Sierra Chart"""
    
    def __init__(self, dtc_connector):
        self.dtc_connector = dtc_connector
        self.subscribed_symbols = set()
        
        # Historique données
        self.market_data_history: Dict[str, deque] = {}
        self.level2_history: Dict[str, deque] = {}
        self.footprint_history: Dict[str, deque] = {}
        self.delta_history: Dict[str, deque] = {}
        
        # Callbacks
        self.on_market_data: Optional[Callable] = None
        self.on_level2_update: Optional[Callable] = None
        self.on_footprint_update: Optional[Callable] = None
        
        # Stats
        self.stats = {
            'total_ticks': 0,
            'total_level2_updates': 0,
            'last_update_time': None,
            'data_latency_ms': 0.0
        }
        
        logger.info("📊 Sierra Market Data Collector initialisé")
    
    async def subscribe_market_data(self, symbol: str) -> bool:
        """Subscribe aux données marché"""
        try:
            if symbol in self.subscribed_symbols:
                logger.warning(f"⚠️ Déjà subscribed à {symbol}")
                return True
            
            # Demander Level 1 (prix/volume)
            try:
                if not await self.dtc_connector.request_market_data(symbol):
                    logger.warning(f"⚠️ Subscription Level 1 échouée: {symbol}")
                else:
                    logger.info(f"✅ Subscription Level 1 demandée: {symbol}")
            except Exception as e:
                logger.error(f"❌ Erreur Level 1 {symbol}: {e}")
            
            # Demander Level 2 (Order Book)
            try:
                if not await self._request_level2_data(symbol):
                    logger.warning(f"⚠️ Subscription Level 2 échouée: {symbol}")
                else:
                    logger.info(f"✅ Subscription Level 2 demandée: {symbol}")
            except Exception as e:
                logger.error(f"❌ Erreur Level 2 {symbol}: {e}")
            
            # Initialiser historiques
            self.market_data_history[symbol] = deque(maxlen=1000)
            self.level2_history[symbol] = deque(maxlen=500)
            self.footprint_history[symbol] = deque(maxlen=200)
            self.delta_history[symbol] = deque(maxlen=1000)
            
            self.subscribed_symbols.add(symbol)
            logger.info(f"✅ Subscribed à {symbol} (Level 1 + Level 2)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur subscription {symbol}: {e}")
            return False
    
    async def _request_level2_data(self, symbol: str) -> bool:
        """Demande données Level 2"""
        try:
            request = {
                "Type": 102,  # MARKET_DEPTH_REQUEST
                "RequestID": self.dtc_connector.request_id + 1,
                "Symbol": symbol,
                "Exchange": "CME",
                "NumLevels": 10  # 10 niveaux de profondeur
            }
            
            return await self.dtc_connector._send_dtc_message(request)
            
        except Exception as e:
            logger.error(f"❌ Erreur demande Level 2: {e}")
            return False
    
    def process_market_data_update(self, message: Dict[str, Any]) -> None:
        """Traite mise à jour données marché"""
        try:
            start_time = time.perf_counter()
            
            symbol = message.get("Symbol", "")
            if symbol not in self.subscribed_symbols:
                return
            
            # Créer données marché
            market_data = SierraMarketData(
                symbol=symbol,
                timestamp=datetime.now(),
                price=message.get("Last", 0.0),
                volume=message.get("Volume", 0),
                bid=message.get("Bid", 0.0),
                ask=message.get("Ask", 0.0),
                last_trade_size=message.get("LastSize", 0)
            )
            
            # Ajouter à l'historique
            self.market_data_history[symbol].append(market_data)
            
            # Calculer latence
            latency_ms = (time.perf_counter() - start_time) * 1000
            self.stats['data_latency_ms'] = latency_ms
            self.stats['total_ticks'] += 1
            self.stats['last_update_time'] = datetime.now()
            
            # Callback
            if self.on_market_data:
                self.on_market_data(market_data)
            
            logger.debug(f"📊 Market data: {symbol} @ {market_data.price:.2f} | Latency: {latency_ms:.1f}ms")
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement market data: {e}")
    
    def process_level2_update(self, message: Dict[str, Any]) -> None:
        """Traite mise à jour Level 2"""
        try:
            symbol = message.get("Symbol", "")
            if symbol not in self.subscribed_symbols:
                return
            
            # Parser niveaux bid/ask
            bid_levels = []
            ask_levels = []
            
            for i in range(10):  # 10 niveaux max
                bid_price = message.get(f"BidPrice{i}", 0.0)
                bid_size = message.get(f"BidSize{i}", 0)
                ask_price = message.get(f"AskPrice{i}", 0.0) 
                ask_size = message.get(f"AskSize{i}", 0)
                
                if bid_price > 0 and bid_size > 0:
                    bid_levels.append({"price": bid_price, "size": bid_size})
                
                if ask_price > 0 and ask_size > 0:
                    ask_levels.append({"price": ask_price, "size": ask_size})
            
            # Calculer métriques
            total_bid_size = sum(level["size"] for level in bid_levels)
            total_ask_size = sum(level["size"] for level in ask_levels)
            
            best_bid = bid_levels[0]["price"] if bid_levels else 0.0
            best_ask = ask_levels[0]["price"] if ask_levels else 0.0
            spread = best_ask - best_bid if best_bid > 0 and best_ask > 0 else 0.0
            
            imbalance_ratio = total_bid_size / (total_bid_size + total_ask_size) if (total_bid_size + total_ask_size) > 0 else 0.5
            
            # Créer Level2Data
            level2_data = Level2Data(
                symbol=symbol,
                timestamp=datetime.now(),
                bid_levels=bid_levels,
                ask_levels=ask_levels,
                best_bid=best_bid,
                best_ask=best_ask,
                spread=spread,
                total_bid_size=total_bid_size,
                total_ask_size=total_ask_size,
                imbalance_ratio=imbalance_ratio
            )
            
            # Ajouter à l'historique
            self.level2_history[symbol].append(level2_data)
            
            # Stats
            self.stats['total_level2_updates'] += 1
            
            # Callback
            if self.on_level2_update:
                self.on_level2_update(level2_data)
            
            logger.debug(f"📈 Level 2: {symbol} | Spread: {spread:.2f} | Imbalance: {imbalance_ratio:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement Level 2: {e}")
    
    def calculate_cumulative_delta(self, symbol: str, trade_data: Dict[str, Any]) -> Optional[CumulativeDeltaData]:
        """Calcule Cumulative Delta"""
        try:
            if symbol not in self.delta_history:
                return None
            
            # Déterminer si trade est buy ou sell
            trade_price = trade_data.get("Price", 0.0)
            trade_size = trade_data.get("Size", 0)
            
            # Récupérer dernier bid/ask
            latest_market_data = self.market_data_history[symbol][-1] if self.market_data_history[symbol] else None
            if not latest_market_data:
                return None
            
            # Logique: si trade >= ask = buy, si trade <= bid = sell
            if trade_price >= latest_market_data.ask:
                delta = trade_size  # Buy
            elif trade_price <= latest_market_data.bid:
                delta = -trade_size  # Sell
            else:
                delta = 0  # Inside spread, ambigu
            
            # Cumulative delta
            last_cumul = self.delta_history[symbol][-1].cumulative_delta if self.delta_history[symbol] else 0.0
            cumulative_delta = last_cumul + delta
            
            # Trend
            if len(self.delta_history[symbol]) >= 10:
                recent_deltas = [d.cumulative_delta for d in list(self.delta_history[symbol])[-10:]]
                if cumulative_delta > max(recent_deltas[:-1]):
                    trend = "bullish"
                elif cumulative_delta < min(recent_deltas[:-1]):
                    trend = "bearish" 
                else:
                    trend = "neutral"
            else:
                trend = "neutral"
            
            # Créer données
            delta_data = CumulativeDeltaData(
                symbol=symbol,
                timestamp=datetime.now(),
                current_delta=delta,
                cumulative_delta=cumulative_delta,
                delta_trend=trend
            )
            
            # Ajouter à l'historique
            self.delta_history[symbol].append(delta_data)
            
            return delta_data
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul delta: {e}")
            return None
    
    def get_latest_data(self, symbol: str) -> Optional[SierraMarketData]:
        """Récupère dernières données marché"""
        try:
            if symbol not in self.market_data_history or not self.market_data_history[symbol]:
                return None
            
            # Données de base
            latest_market = self.market_data_history[symbol][-1]
            
            # Level 2
            latest_level2 = self.level2_history[symbol][-1] if self.level2_history[symbol] else None
            
            # Delta
            latest_delta = self.delta_history[symbol][-1] if self.delta_history[symbol] else None
            
            # Combiner
            latest_market.level2 = latest_level2
            latest_market.cumulative_delta = latest_delta
            
            return latest_market
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération données: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques collector"""
        return {
            **self.stats,
            'subscribed_symbols': list(self.subscribed_symbols),
            'symbols_count': len(self.subscribed_symbols)
        }
