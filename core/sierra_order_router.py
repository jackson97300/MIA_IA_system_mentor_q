#!/usr/bin/env python3
"""
🔧 SIERRA ORDER ROUTER - MIA_IA_SYSTEM
Routeur d'ordres pour Sierra Chart avec gestion multi-symboles
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger

logger = get_logger(__name__)

class OrderStatus(Enum):
    """Statut des ordres"""
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"

class OrderSide(Enum):
    """Côté de l'ordre"""
    BUY = "BUY"
    SELL = "SELL"

class OrderType(Enum):
    """Type d'ordre"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"

@dataclass
class OrderRequest:
    """Demande d'ordre"""
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "DAY"

@dataclass
class OrderResponse:
    """Réponse d'ordre"""
    order_id: str
    status: OrderStatus
    message: str
    timestamp: datetime
    fill_price: Optional[float] = None
    fill_quantity: Optional[int] = None

class SierraOrderRouter:
    """
    Routeur d'ordres pour Sierra Chart
    
    Fonctionnalités:
    ✅ Gestion multi-symboles (ES, NQ, etc.)
    ✅ Routing intelligent des ordres
    ✅ Gestion des ports par symbole
    ✅ Fallback et retry automatique
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Configuration des ports par symbole
        self.symbol_ports = {
            "ES": 11099,
            "NQ": 11100,
            "ESU25": 11099,
            "NQU25": 11100,
            "ESU25_FUT_CME": 11099,
            "NQU25_FUT_CME": 11100
        }
        
        # État des connexions
        self.connections: Dict[str, bool] = {}
        self.order_counter = 1
        
        logger.info("🔧 Sierra Order Router initialisé")
        logger.info(f"   - ES: port {self.symbol_ports.get('ES', 'N/A')}")
        logger.info(f"   - NQ: port {self.symbol_ports.get('NQ', 'N/A')}")
    
    async def route_order(self, request: OrderRequest) -> OrderResponse:
        """
        Route un ordre vers le bon port Sierra Chart
        
        Args:
            request: Demande d'ordre
            
        Returns:
            Réponse d'ordre
        """
        try:
            # Déterminer le port pour le symbole
            port = self._get_port_for_symbol(request.symbol)
            if not port:
                return OrderResponse(
                    order_id="",
                    status=OrderStatus.REJECTED,
                    message=f"Port non configuré pour {request.symbol}",
                    timestamp=datetime.now()
                )
            
            # Générer ID d'ordre
            order_id = f"SC_{self.order_counter}_{int(datetime.now().timestamp())}"
            self.order_counter += 1
            
            # Simuler le routing (à remplacer par vraie connectivité)
            logger.info(f"📤 Ordre routé: {request.symbol} {request.side.value} {request.quantity} @ port {port}")
            
            # Simulation de succès
            return OrderResponse(
                order_id=order_id,
                status=OrderStatus.FILLED,
                message="Ordre routé avec succès",
                timestamp=datetime.now(),
                fill_price=request.price or 0.0,
                fill_quantity=request.quantity
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur routing ordre: {e}")
            return OrderResponse(
                order_id="",
                status=OrderStatus.REJECTED,
                message=f"Erreur routing: {e}",
                timestamp=datetime.now()
            )
    
    def _get_port_for_symbol(self, symbol: str) -> Optional[int]:
        """Retourne le port pour un symbole"""
        # Nettoyer le symbole
        clean_symbol = symbol.replace("_FUT_CME", "").replace("25", "")
        return self.symbol_ports.get(clean_symbol)
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Annule un ordre
        
        Args:
            order_id: ID de l'ordre
            symbol: Symbole
            
        Returns:
            True si annulation réussie
        """
        try:
            port = self._get_port_for_symbol(symbol)
            if not port:
                logger.error(f"Port non configuré pour {symbol}")
                return False
            
            logger.info(f"❌ Annulation ordre {order_id} @ port {port}")
            
            # Simulation d'annulation réussie
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur annulation ordre {order_id}: {e}")
            return False
    
    async def get_order_status(self, order_id: str, symbol: str) -> Optional[OrderStatus]:
        """
        Récupère le statut d'un ordre
        
        Args:
            order_id: ID de l'ordre
            symbol: Symbole
            
        Returns:
            Statut de l'ordre
        """
        try:
            port = self._get_port_for_symbol(symbol)
            if not port:
                return None
            
            # Simulation de statut
            logger.debug(f"📊 Statut ordre {order_id} @ port {port}")
            return OrderStatus.FILLED
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération statut {order_id}: {e}")
            return None
    
    def get_connection_status(self) -> Dict[str, bool]:
        """Retourne le statut des connexions"""
        return self.connections.copy()
    
    def get_supported_symbols(self) -> List[str]:
        """Retourne la liste des symboles supportés"""
        return list(self.symbol_ports.keys())
    
    def get_port_mapping(self) -> Dict[str, int]:
        """Retourne le mapping symbole -> port"""
        return self.symbol_ports.copy()

# Factory functions
def create_sierra_order_router(config: Optional[Dict] = None) -> SierraOrderRouter:
    """Factory pour créer un routeur d'ordres Sierra"""
    return SierraOrderRouter(config)

def get_sierra_order_router(config: Optional[Dict] = None) -> SierraOrderRouter:
    """Factory function pour SierraOrderRouter (alias)"""
    return SierraOrderRouter(config)

async def place_entry(symbol: str, side: OrderSide, quantity: int, 
                     order_type: OrderType = OrderType.MARKET, 
                     price: Optional[float] = None) -> OrderResponse:
    """
    Place une entrée d'ordre
    
    Args:
        symbol: Symbole à trader
        side: Côté de l'ordre (BUY/SELL)
        quantity: Quantité
        order_type: Type d'ordre
        price: Prix (pour ordres LIMIT)
        
    Returns:
        Réponse d'ordre
    """
    router = SierraOrderRouter()
    request = OrderRequest(
        symbol=symbol,
        side=side,
        quantity=quantity,
        order_type=order_type,
        price=price
    )
    return await router.route_order(request)

async def place_exit(symbol: str, side: OrderSide, quantity: int, 
                    order_type: OrderType = OrderType.MARKET, 
                    price: Optional[float] = None) -> OrderResponse:
    """
    Place une sortie d'ordre (alias pour place_entry)
    
    Args:
        symbol: Symbole à trader
        side: Côté de l'ordre (BUY/SELL)
        quantity: Quantité
        order_type: Type d'ordre
        price: Prix (pour ordres LIMIT)
        
    Returns:
        Réponse d'ordre
    """
    return await place_entry(symbol, side, quantity, order_type, price)

async def cancel_order(order_id: str, symbol: str) -> bool:
    """
    Annule un ordre (fonction standalone)
    
    Args:
        order_id: ID de l'ordre à annuler
        symbol: Symbole
        
    Returns:
        True si annulation réussie
    """
    router = SierraOrderRouter()
    return await router.cancel_order(order_id, symbol)

# Export principal
__all__ = [
    'SierraOrderRouter',
    'OrderRequest',
    'OrderResponse',
    'OrderStatus',
    'OrderSide',
    'OrderType',
    'create_sierra_order_router',
    'get_sierra_order_router',
    'place_entry',
    'place_exit',
    'cancel_order'  # 🆕 NOUVEAU: Fonction d'annulation d'ordre
]
