#!/usr/bin/env python3
"""
📈 ORDER MANAGER - MIA_IA_SYSTEM
Gestion intelligente des ordres avec Sierra Charts
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger
from .sierra_connector import SierraConnector
from .sierra_dtc_connector import OrderSide, OrderType
from enum import Enum

class BrokerType(Enum):
    """Type de broker"""
    SIERRA_CHART = "sierra_chart"
    SIMULATED = "simulated"

class OrderStatus(Enum):
    """Statut des ordres"""
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"

logger = get_logger(__name__)

@dataclass
class TradingSignal:
    """Signal de trading"""
    direction: str  # "LONG" ou "SHORT"
    confidence: float
    price: float
    timestamp: datetime
    confluence: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

@dataclass
class OrderRequest:
    """Demande d'ordre"""
    signal: TradingSignal
    symbol: str
    quantity: int
    order_type: OrderType
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class OrderManager:
    """Gestionnaire d'ordres intelligent"""
    
    def __init__(self, sierra_connector: SierraConnector, config):
        self.sierra = sierra_connector
        self.config = config
        self.active_orders: Dict[str, Dict[str, Any]] = {}
        self.order_history: List[Dict[str, Any]] = []
        
        # Gestion des stop loss et take profit
        self.stop_orders: Dict[str, str] = {}  # order_id -> stop_order_id
        self.take_profit_orders: Dict[str, str] = {}  # order_id -> tp_order_id
        
        logger.info("✅ Order Manager initialisé")
    
    async def execute_signal(self, signal: TradingSignal, symbol: str, 
                           quantity: int) -> Optional[str]:
        """Exécute un signal de trading"""
        try:
            logger.info(f"🎯 Exécution signal: {signal.direction} {symbol} x{quantity}")
            
            # Validation signal
            if not self._validate_signal(signal):
                logger.error("❌ Signal invalide")
                return None
            
            # Détermination côté ordre
            side = OrderSide.BUY if signal.direction == "LONG" else OrderSide.SELL
            
            # Création demande d'ordre
            order_request = OrderRequest(
                signal=signal,
                symbol=symbol,
                quantity=quantity,
                order_type=OrderType.MARKET,  # Ordre marché par défaut
                price=signal.price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit
            )
            
            # Placement ordre principal
            order_id = await self._place_main_order(order_request, side)
            if not order_id:
                logger.error("❌ Échec placement ordre principal")
                return None
            
            # Placement ordres de protection (stop loss, take profit)
            await self._place_protection_orders(order_request, order_id)
            
            logger.info(f"✅ Signal exécuté: {order_id}")
            return order_id
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution signal: {e}")
            return None
    
    async def _place_main_order(self, order_request: OrderRequest, side: OrderSide) -> Optional[str]:
        """Place l'ordre principal"""
        try:
            # Placement ordre
            order_id = await self.sierra.place_order(
                symbol=order_request.symbol,
                side=side,
                quantity=order_request.quantity,
                order_type=order_request.order_type,
                price=order_request.price
            )
            
            if order_id:
                # Enregistrement ordre actif
                self.active_orders[order_id] = {
                    'order_request': order_request,
                    'side': side,
                    'timestamp': datetime.now(),
                    'status': 'PENDING'
                }
                
                logger.info(f"📈 Ordre principal placé: {order_id}")
                return order_id
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur placement ordre principal: {e}")
            return None
    
    async def _place_protection_orders(self, order_request: OrderRequest, main_order_id: str) -> None:
        """Place les ordres de protection (stop loss, take profit)"""
        try:
            if order_request.stop_loss:
                await self._place_stop_loss(order_request, main_order_id)
            
            if order_request.take_profit:
                await self._place_take_profit(order_request, main_order_id)
                
        except Exception as e:
            logger.error(f"❌ Erreur placement ordres protection: {e}")
    
    async def _place_stop_loss(self, order_request: OrderRequest, main_order_id: str) -> None:
        """Place un ordre stop loss"""
        try:
            # Détermination côté stop loss (opposé à l'ordre principal)
            main_side = OrderSide.BUY if order_request.signal.direction == "LONG" else OrderSide.SELL
            stop_side = OrderSide.SELL if main_side == OrderSide.BUY else OrderSide.BUY
            
            # Placement ordre stop
            stop_order_id = await self.sierra.place_order(
                symbol=order_request.symbol,
                side=stop_side,
                quantity=order_request.quantity,
                order_type=OrderType.STOP,
                stop_price=order_request.stop_loss
            )
            
            if stop_order_id:
                self.stop_orders[main_order_id] = stop_order_id
                logger.info(f"🛡️ Stop loss placé: {stop_order_id} @ {order_request.stop_loss}")
            
        except Exception as e:
            logger.error(f"❌ Erreur placement stop loss: {e}")
    
    async def _place_take_profit(self, order_request: OrderRequest, main_order_id: str) -> None:
        """Place un ordre take profit"""
        try:
            # Détermination côté take profit (opposé à l'ordre principal)
            main_side = OrderSide.BUY if order_request.signal.direction == "LONG" else OrderSide.SELL
            tp_side = OrderSide.SELL if main_side == OrderSide.BUY else OrderSide.BUY
            
            # Placement ordre take profit
            tp_order_id = await self.sierra.place_order(
                symbol=order_request.symbol,
                side=tp_side,
                quantity=order_request.quantity,
                order_type=OrderType.LIMIT,
                price=order_request.take_profit
            )
            
            if tp_order_id:
                self.take_profit_orders[main_order_id] = tp_order_id
                logger.info(f"🎯 Take profit placé: {tp_order_id} @ {order_request.take_profit}")
            
        except Exception as e:
            logger.error(f"❌ Erreur placement take profit: {e}")
    
    def _validate_signal(self, signal: TradingSignal) -> bool:
        """Valide un signal de trading"""
        try:
            # Vérifications de base
            if signal.direction not in ["LONG", "SHORT"]:
                logger.error(f"❌ Direction invalide: {signal.direction}")
                return False
            
            if not (0.0 <= signal.confidence <= 1.0):
                logger.error(f"❌ Confiance invalide: {signal.confidence}")
                return False
            
            if signal.price <= 0:
                logger.error(f"❌ Prix invalide: {signal.price}")
                return False
            
            # Vérification seuil de confiance
            if signal.confidence < self.config.min_signal_confidence:
                logger.warning(f"⚠️ Confiance insuffisante: {signal.confidence}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur validation signal: {e}")
            return False
    
    async def close_position(self, symbol: str, quantity: int = None) -> Optional[str]:
        """Ferme une position"""
        try:
            # Récupération positions actuelles
            positions = await self.sierra.get_positions()
            
            if symbol not in positions:
                logger.warning(f"⚠️ Aucune position pour {symbol}")
                return None
            
            position = positions[symbol]
            close_quantity = quantity if quantity else abs(position.quantity)
            
            # Détermination côté de fermeture
            side = OrderSide.SELL if position.quantity > 0 else OrderSide.BUY
            
            # Placement ordre de fermeture
            order_id = await self.sierra.place_order(
                symbol=symbol,
                side=side,
                quantity=close_quantity,
                order_type=OrderType.MARKET
            )
            
            if order_id:
                logger.info(f"📉 Position fermée: {order_id} - {symbol} x{close_quantity}")
                return order_id
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur fermeture position: {e}")
            return None
    
    async def cancel_all_orders(self) -> None:
        """Annule tous les ordres actifs"""
        try:
            # Annulation ordres principaux
            for order_id in list(self.active_orders.keys()):
                await self.sierra.cancel_order(order_id)
                if order_id in self.active_orders:
                    del self.active_orders[order_id]
            
            # Annulation ordres de protection
            for stop_order_id in self.stop_orders.values():
                await self.sierra.cancel_order(stop_order_id)
            
            for tp_order_id in self.take_profit_orders.values():
                await self.sierra.cancel_order(tp_order_id)
            
            # Nettoyage
            self.stop_orders.clear()
            self.take_profit_orders.clear()
            
            logger.info("❌ Tous les ordres annulés")
            
        except Exception as e:
            logger.error(f"❌ Erreur annulation tous ordres: {e}")
    
    async def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le statut d'un ordre"""
        try:
            status = await self.sierra.get_order_status(order_id)
            
            if status:
                return {
                    'order_id': order_id,
                    'status': status.value,
                    'active': order_id in self.active_orders,
                    'has_stop_loss': order_id in self.stop_orders,
                    'has_take_profit': order_id in self.take_profit_orders
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération statut: {e}")
            return None
    
    async def get_trading_summary(self) -> Dict[str, Any]:
        """Récupère un résumé du trading"""
        try:
            # Récupération données Sierra
            positions = await self.sierra.get_positions()
            account_info = await self.sierra.get_account_info()
            
            # Calculs
            total_positions = len(positions)
            total_active_orders = len(self.active_orders)
            total_stop_orders = len(self.stop_orders)
            total_tp_orders = len(self.take_profit_orders)
            
            return {
                'total_positions': total_positions,
                'active_orders': total_active_orders,
                'stop_loss_orders': total_stop_orders,
                'take_profit_orders': total_tp_orders,
                'account_balance': account_info.get('account_balance', 0.0),
                'total_pnl': account_info.get('total_pnl', 0.0),
                'available_margin': account_info.get('available_margin', 0.0),
                'connection_status': account_info.get('connection_status', False)
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération résumé: {e}")
            return {}
    
    async def monitor_orders(self) -> None:
        """Surveille les ordres actifs"""
        try:
            for order_id in list(self.active_orders.keys()):
                status = await self.sierra.get_order_status(order_id)
                
                if status == OrderStatus.FILLED:
                    # Ordre rempli - nettoyage
                    logger.info(f"✅ Ordre rempli: {order_id}")
                    if order_id in self.active_orders:
                        del self.active_orders[order_id]
                    
                    # Annulation ordres de protection si nécessaire
                    if order_id in self.stop_orders:
                        stop_id = self.stop_orders[order_id]
                        await self.sierra.cancel_order(stop_id)
                        del self.stop_orders[order_id]
                    
                    if order_id in self.take_profit_orders:
                        tp_id = self.take_profit_orders[order_id]
                        await self.sierra.cancel_order(tp_id)
                        del self.take_profit_orders[order_id]
                
                elif status == OrderStatus.CANCELLED:
                    # Ordre annulé - nettoyage
                    logger.info(f"❌ Ordre annulé: {order_id}")
                    if order_id in self.active_orders:
                        del self.active_orders[order_id]
                
                elif status == OrderStatus.REJECTED:
                    # Ordre rejeté - nettoyage
                    logger.error(f"❌ Ordre rejeté: {order_id}")
                    if order_id in self.active_orders:
                        del self.active_orders[order_id]
            
        except Exception as e:
            logger.error(f"❌ Erreur monitoring ordres: {e}")
    
    def get_active_orders_count(self) -> int:
        """Retourne le nombre d'ordres actifs"""
        return len(self.active_orders)
    
    def get_protection_orders_count(self) -> int:
        """Retourne le nombre d'ordres de protection"""
        return len(self.stop_orders) + len(self.take_profit_orders)

# Factory function
def create_order_manager(sierra_connector=None, config=None):
    """Factory pour créer un gestionnaire d'ordres"""
    return OrderManager(sierra_connector, config) 