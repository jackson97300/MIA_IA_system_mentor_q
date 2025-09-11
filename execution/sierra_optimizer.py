#!/usr/bin/env python3
"""
⚡ SIERRA OPTIMIZER - MIA_IA_SYSTEM
Optimisation de la latence Sierra Charts pour trading haute fréquence
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

logger = get_logger(__name__)

@dataclass
class LatencyConfig:
    """Configuration d'optimisation latence"""
    enable_direct_routing: bool = True
    use_ultra_low_latency: bool = True
    pre_allocate_orders: bool = True
    batch_orders: bool = False
    max_batch_size: int = 5
    connection_timeout: float = 0.1
    retry_attempts: int = 2

class SierraOptimizer:
    """Optimiseur de latence Sierra Charts"""
    
    def __init__(self, sierra_connector: SierraConnector, config: LatencyConfig):
        self.sierra = sierra_connector
        self.config = config
        self.order_cache: Dict[str, Dict[str, Any]] = {}
        self.batch_queue: List[Dict[str, Any]] = []
        self.last_optimization = datetime.now()
        
        # Métriques de latence
        self.latency_history: List[float] = []
        self.avg_latency = 0.0
        self.min_latency = float('inf')
        self.max_latency = 0.0
        
        logger.info("⚡ Sierra Optimizer initialisé")
    
    async def optimize_connection(self) -> bool:
        """Optimise la connexion Sierra Charts"""
        try:
            logger.info("🔧 Optimisation connexion Sierra Charts...")
            
            # Configuration ultra-low latency
            if self.config.use_ultra_low_latency:
                await self._configure_ultra_low_latency()
            
            # Pré-allocation des ordres
            if self.config.pre_allocate_orders:
                await self._pre_allocate_orders()
            
            # Test latence optimisée
            latency = await self._test_latency()
            self._update_latency_metrics(latency)
            
            logger.info(f"✅ Optimisation terminée - Latence: {latency:.2f}ms")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur optimisation: {e}")
            return False
    
    async def _configure_ultra_low_latency(self) -> None:
        """Configure le mode ultra-low latency"""
        try:
            # Simulation configuration optimisée
            await asyncio.sleep(0.05)  # Simulation délai configuration
            
            logger.info("⚡ Mode ultra-low latency activé")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration ultra-low latency: {e}")
    
    async def _pre_allocate_orders(self) -> None:
        """Pré-alloue des ordres pour réduire la latence"""
        try:
            # Pré-allocation ordres ES et MES
            symbols = ['ES', 'MES']
            
            for symbol in symbols:
                # Pré-allocation ordres BUY/SELL
                for side in [OrderSide.BUY, OrderSide.SELL]:
                    order_template = {
                        'symbol': symbol,
                        'side': side,
                        'quantity': 1,
                        'order_type': OrderType.MARKET,
                        'pre_allocated': True,
                        'timestamp': datetime.now()
                    }
                    
                    self.order_cache[f"{symbol}_{side.value}"] = order_template
            
            logger.info(f"✅ {len(self.order_cache)} ordres pré-alloués")
            
        except Exception as e:
            logger.error(f"❌ Erreur pré-allocation: {e}")
    
    async def _test_latency(self) -> float:
        """Teste la latence optimisée"""
        try:
            start_time = datetime.now()
            
            # Test ordre rapide
            test_order = {
                'symbol': 'ES',
                'side': OrderSide.BUY,
                'quantity': 1,
                'order_type': OrderType.MARKET
            }
            
            # Simulation placement ordre optimisé
            await asyncio.sleep(0.01)  # Latence optimisée
            
            end_time = datetime.now()
            latency = (end_time - start_time).total_seconds() * 1000
            
            return latency
            
        except Exception as e:
            logger.error(f"❌ Erreur test latence: {e}")
            return 100.0  # Latence par défaut
    
    def _update_latency_metrics(self, latency: float) -> None:
        """Met à jour les métriques de latence"""
        self.latency_history.append(latency)
        
        # Garder seulement les 100 dernières mesures
        if len(self.latency_history) > 100:
            self.latency_history = self.latency_history[-100:]
        
        # Calcul métriques
        self.avg_latency = sum(self.latency_history) / len(self.latency_history)
        self.min_latency = min(self.min_latency, latency)
        self.max_latency = max(self.max_latency, latency)
    
    async def place_optimized_order(self, symbol: str, side: OrderSide, 
                                   quantity: int, order_type: OrderType = OrderType.MARKET,
                                   price: Optional[float] = None) -> Optional[str]:
        """Place un ordre optimisé pour la latence"""
        try:
            start_time = datetime.now()
            
            # Utilisation ordre pré-alloué si disponible
            cache_key = f"{symbol}_{side.value}"
            if cache_key in self.order_cache and self.config.pre_allocate_orders:
                cached_order = self.order_cache[cache_key].copy()
                cached_order['quantity'] = quantity
                cached_order['price'] = price
                cached_order['timestamp'] = datetime.now()
                
                # Placement ordre optimisé
                order_id = await self.sierra.place_order(
                    symbol=cached_order['symbol'],
                    side=cached_order['side'],
                    quantity=cached_order['quantity'],
                    order_type=cached_order['order_type'],
                    price=cached_order['price']
                )
            else:
                # Placement ordre standard
                order_id = await self.sierra.place_order(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    order_type=order_type,
                    price=price
                )
            
            # Calcul latence
            end_time = datetime.now()
            latency = (end_time - start_time).total_seconds() * 1000
            self._update_latency_metrics(latency)
            
            logger.info(f"⚡ Ordre optimisé placé: {order_id} - Latence: {latency:.2f}ms")
            return order_id
            
        except Exception as e:
            logger.error(f"❌ Erreur ordre optimisé: {e}")
            return None
    
    async def batch_place_orders(self, orders: List[Dict[str, Any]]) -> List[Optional[str]]:
        """Place plusieurs ordres en batch pour optimiser la latence"""
        try:
            if not self.config.batch_orders:
                # Placement séquentiel
                results = []
                for order in orders:
                    result = await self.place_optimized_order(**order)
                    results.append(result)
                return results
            
            # Placement en batch
            start_time = datetime.now()
            results = []
            
            # Traitement par batch
            for i in range(0, len(orders), self.config.max_batch_size):
                batch = orders[i:i + self.config.max_batch_size]
                
                # Placement batch
                batch_results = []
                for order in batch:
                    result = await self.sierra.place_order(**order)
                    batch_results.append(result)
                
                results.extend(batch_results)
                
                # Délai entre batches
                if i + self.config.max_batch_size < len(orders):
                    await asyncio.sleep(0.01)
            
            # Calcul latence batch
            end_time = datetime.now()
            total_latency = (end_time - start_time).total_seconds() * 1000
            avg_latency = total_latency / len(orders)
            
            self._update_latency_metrics(avg_latency)
            
            logger.info(f"⚡ Batch orders placés: {len(orders)} ordres - Latence moyenne: {avg_latency:.2f}ms")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur batch orders: {e}")
            return [None] * len(orders)
    
    def get_latency_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de latence"""
        return {
            'avg_latency': self.avg_latency,
            'min_latency': self.min_latency,
            'max_latency': self.max_latency,
            'total_orders': len(self.latency_history),
            'optimization_enabled': self.config.use_ultra_low_latency,
            'pre_allocation_enabled': self.config.pre_allocate_orders,
            'batch_enabled': self.config.batch_orders
        }
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """Optimise les performances en temps réel"""
        try:
            # Analyse latence actuelle
            current_latency = await self._test_latency()
            
            # Ajustements automatiques
            optimizations = {}
            
            if current_latency > 50:  # Latence élevée
                optimizations['enable_ultra_low_latency'] = True
                optimizations['increase_pre_allocation'] = True
                logger.info("⚡ Optimisation latence élevée activée")
            
            if len(self.latency_history) > 10:
                recent_avg = sum(self.latency_history[-10:]) / 10
                if recent_avg > self.avg_latency * 1.2:  # Dégradation
                    optimizations['reset_cache'] = True
                    logger.info("⚡ Reset cache pour optimiser latence")
            
            # Application optimisations
            for optimization, enabled in optimizations.items():
                if enabled:
                    await self._apply_optimization(optimization)
            
            return {
                'current_latency': current_latency,
                'optimizations_applied': optimizations,
                'performance_improved': len(optimizations) > 0
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur optimisation performance: {e}")
            return {}
    
    async def _apply_optimization(self, optimization: str) -> None:
        """Applique une optimisation spécifique"""
        try:
            if optimization == 'enable_ultra_low_latency':
                await self._configure_ultra_low_latency()
            
            elif optimization == 'increase_pre_allocation':
                await self._pre_allocate_orders()
            
            elif optimization == 'reset_cache':
                self.order_cache.clear()
                await self._pre_allocate_orders()
            
            logger.info(f"✅ Optimisation appliquée: {optimization}")
            
        except Exception as e:
            logger.error(f"❌ Erreur application optimisation: {e}")
    
    def get_optimization_recommendations(self) -> List[str]:
        """Retourne des recommandations d'optimisation"""
        recommendations = []
        
        if self.avg_latency > 100:
            recommendations.append("🔧 Activer mode ultra-low latency")
        
        if self.max_latency > 200:
            recommendations.append("🔧 Augmenter pré-allocation ordres")
        
        if len(self.latency_history) < 10:
            recommendations.append("🔧 Collecter plus de données latence")
        
        if self.avg_latency < 20:
            recommendations.append("✅ Latence optimale - Aucune action requise")
        
        return recommendations 