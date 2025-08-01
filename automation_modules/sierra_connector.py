#!/usr/bin/env python3
"""
📊 SIERRA CONNECTOR - MIA_IA_SYSTEM
Connexion et gestion Sierra Charts pour passage d'ordres
"""

import sys
import asyncio
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger

logger = get_logger(__name__)

class OrderType(Enum):
    """Types d'ordres Sierra Charts"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"

class OrderSide(Enum):
    """Côtés d'ordres"""
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    """Statuts d'ordres"""
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"

@dataclass
class SierraOrder:
    """Ordre Sierra Charts"""
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    filled_price: Optional[float] = None
    timestamp: datetime = None
    commission: float = 0.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class SierraPosition:
    """Position Sierra Charts"""
    symbol: str
    quantity: int
    avg_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class SierraConnector:
    """Connecteur Sierra Charts optimisé"""
    
    def __init__(self, config):
        self.config = config
        self.is_connected = False
        self.connection_time = None
        self.last_heartbeat = None
        
        # Gestion des ordres et positions
        self.orders: Dict[str, SierraOrder] = {}
        self.positions: Dict[str, SierraPosition] = {}
        self.order_counter = 0
        
        # Configuration contrats
        self.contracts = {
            'ES': {
                'tick_value': 12.50,
                'tick_size': 0.25,
                'margin': 5000.0,
                'commission': 2.50
            },
            'MES': {
                'tick_value': 1.25,
                'tick_size': 0.25,
                'margin': 500.0,
                'commission': 0.25
            }
        }
        
        logger.info("✅ Sierra Connector initialisé")
    
    async def connect(self) -> bool:
        """Connexion à Sierra Charts"""
        try:
            logger.info("🔌 Connexion à Sierra Charts...")
            
            # Simulation connexion (remplacer par vraie API)
            await asyncio.sleep(1)  # Simulation délai connexion
            
            self.is_connected = True
            self.connection_time = datetime.now()
            self.last_heartbeat = datetime.now()
            
            logger.info("✅ Connexion Sierra Charts établie")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion Sierra Charts: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self) -> None:
        """Déconnexion de Sierra Charts"""
        try:
            logger.info("🔌 Déconnexion Sierra Charts...")
            
            # Annuler tous les ordres en attente
            await self.cancel_all_orders()
            
            self.is_connected = False
            logger.info("✅ Déconnexion Sierra Charts réussie")
            
        except Exception as e:
            logger.error(f"❌ Erreur déconnexion: {e}")
    
    async def place_order(self, symbol: str, side: OrderSide, quantity: int, 
                         order_type: OrderType = OrderType.MARKET, 
                         price: Optional[float] = None,
                         stop_price: Optional[float] = None) -> Optional[str]:
        """Place un ordre sur Sierra Charts"""
        try:
            if not self.is_connected:
                logger.error("❌ Non connecté à Sierra Charts")
                return None
            
            # Validation
            if symbol not in self.contracts:
                logger.error(f"❌ Symbole non supporté: {symbol}")
                return None
            
            if quantity <= 0:
                logger.error(f"❌ Quantité invalide: {quantity}")
                return None
            
            # Génération ID ordre
            order_id = f"SC_{self.order_counter}_{int(time.time())}"
            self.order_counter += 1
            
            # Création ordre
            order = SierraOrder(
                order_id=order_id,
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                stop_price=stop_price
            )
            
            # Simulation placement ordre
            await self._simulate_order_placement(order)
            
            # Stockage ordre
            self.orders[order_id] = order
            
            logger.info(f"📈 Ordre placé: {order_id} - {side.value} {quantity} {symbol}")
            return order_id
            
        except Exception as e:
            logger.error(f"❌ Erreur placement ordre: {e}")
            return None
    
    async def _simulate_order_placement(self, order: SierraOrder) -> None:
        """Simule le placement d'ordre (remplacer par vraie API)"""
        try:
            # Simulation délai placement
            await asyncio.sleep(0.1)
            
            # Simulation remplissage (80% de chance de remplissage immédiat pour MARKET)
            if order.order_type == OrderType.MARKET:
                if self._random_fill(0.8):
                    order.status = OrderStatus.FILLED
                    order.filled_quantity = order.quantity
                    order.filled_price = self._get_market_price(order.symbol)
                    order.commission = self.contracts[order.symbol]['commission']
                    
                    # Mise à jour position
                    await self._update_position(order)
                    
                    logger.info(f"✅ Ordre rempli: {order.order_id} @ {order.filled_price:.2f}")
                else:
                    order.status = OrderStatus.PENDING
                    logger.info(f"⏳ Ordre en attente: {order.order_id}")
            else:
                order.status = OrderStatus.PENDING
                logger.info(f"⏳ Ordre limite placé: {order.order_id}")
                
        except Exception as e:
            logger.error(f"❌ Erreur simulation placement: {e}")
            order.status = OrderStatus.REJECTED
    
    async def cancel_order(self, order_id: str) -> bool:
        """Annule un ordre"""
        try:
            if order_id not in self.orders:
                logger.error(f"❌ Ordre non trouvé: {order_id}")
                return False
            
            order = self.orders[order_id]
            
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
                logger.warning(f"⚠️ Ordre déjà {order.status.value}: {order_id}")
                return False
            
            # Simulation annulation
            await asyncio.sleep(0.05)
            order.status = OrderStatus.CANCELLED
            
            logger.info(f"❌ Ordre annulé: {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur annulation ordre: {e}")
            return False
    
    async def cancel_all_orders(self) -> None:
        """Annule tous les ordres en attente"""
        try:
            pending_orders = [order_id for order_id, order in self.orders.items() 
                            if order.status == OrderStatus.PENDING]
            
            for order_id in pending_orders:
                await self.cancel_order(order_id)
            
            logger.info(f"❌ {len(pending_orders)} ordres annulés")
            
        except Exception as e:
            logger.error(f"❌ Erreur annulation tous ordres: {e}")
    
    async def get_order_status(self, order_id: str) -> Optional[OrderStatus]:
        """Récupère le statut d'un ordre"""
        try:
            if order_id not in self.orders:
                return None
            
            return self.orders[order_id].status
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération statut: {e}")
            return None
    
    async def get_positions(self) -> Dict[str, SierraPosition]:
        """Récupère toutes les positions"""
        try:
            return self.positions.copy()
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération positions: {e}")
            return {}
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Récupère les informations du compte"""
        try:
            # Simulation données compte
            total_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
            total_margin = sum(self.contracts[pos.symbol]['margin'] * abs(pos.quantity) 
                              for pos in self.positions.values())
            
            return {
                'account_balance': 10000.0,  # Simulation
                'available_margin': 10000.0 - total_margin,
                'total_pnl': total_pnl,
                'total_positions': len(self.positions),
                'connection_status': self.is_connected,
                'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération compte: {e}")
            return {}
    
    async def _update_position(self, order: SierraOrder) -> None:
        """Met à jour les positions après remplissage d'ordre"""
        try:
            symbol = order.symbol
            quantity_change = order.filled_quantity
            
            if order.side == OrderSide.SELL:
                quantity_change = -quantity_change
            
            if symbol in self.positions:
                # Mise à jour position existante
                pos = self.positions[symbol]
                old_quantity = pos.quantity
                old_avg_price = pos.avg_price
                
                new_quantity = old_quantity + quantity_change
                
                if new_quantity == 0:
                    # Position fermée
                    realized_pnl = (order.filled_price - old_avg_price) * old_quantity
                    pos.realized_pnl += realized_pnl
                    del self.positions[symbol]
                    logger.info(f"📉 Position fermée: {symbol}, PnL: {realized_pnl:.2f}")
                else:
                    # Mise à jour position
                    new_avg_price = ((old_quantity * old_avg_price) + 
                                   (quantity_change * order.filled_price)) / new_quantity
                    pos.quantity = new_quantity
                    pos.avg_price = new_avg_price
                    pos.timestamp = datetime.now()
            else:
                # Nouvelle position
                if quantity_change != 0:
                    self.positions[symbol] = SierraPosition(
                        symbol=symbol,
                        quantity=quantity_change,
                        avg_price=order.filled_price
                    )
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour position: {e}")
    
    def _random_fill(self, probability: float) -> bool:
        """Simule un remplissage aléatoire"""
        import random
        return random.random() < probability
    
    def _get_market_price(self, symbol: str) -> float:
        """Simule le prix de marché"""
        import random
        base_price = 4500.0 if symbol == 'ES' else 450.0
        return base_price + random.uniform(-2.0, 2.0)
    
    async def heartbeat(self) -> bool:
        """Vérification connexion"""
        try:
            if not self.is_connected:
                return False
            
            self.last_heartbeat = datetime.now()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur heartbeat: {e}")
            return False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Retourne le statut de connexion"""
        return {
            'is_connected': self.is_connected,
            'connection_time': self.connection_time.isoformat() if self.connection_time else None,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'total_orders': len(self.orders),
            'total_positions': len(self.positions)
        } 