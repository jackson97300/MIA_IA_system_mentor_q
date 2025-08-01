#!/usr/bin/env python3
"""
🚀 OPTIMIZED TRADING SYSTEM - MIA_IA_SYSTEM
Système de trading optimisé avec Sierra Charts (14.74ms latence)
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
from .sierra_connector import SierraConnector, OrderSide, OrderType, OrderStatus
from .sierra_optimizer import SierraOptimizer, LatencyConfig
from .order_manager import OrderManager, TradingSignal, OrderRequest
from .sierra_config import SierraOptimizedConfig, TradingStrategyConfig, validate_latency_for_strategy

logger = get_logger(__name__)

@dataclass
class TradingDecision:
    """Décision de trading optimisée"""
    signal: TradingSignal
    strategy: str  # "scalping", "day_trading", "swing_trading", "position_trading"
    expected_latency: float
    confidence: float
    risk_level: str  # "low", "medium", "high"
    execution_priority: int  # 1-5 (1 = highest)

class OptimizedTradingSystem:
    """Système de trading optimisé avec Sierra Charts"""
    
    def __init__(self, automation_config):
        self.config = automation_config
        self.sierra_config = SierraOptimizedConfig()
        self.strategy_config = TradingStrategyConfig()
        
        # Initialisation composants optimisés
        self.sierra = SierraConnector(self.config)
        self.latency_config = LatencyConfig()
        self.optimizer = SierraOptimizer(self.sierra, self.latency_config)
        self.order_manager = OrderManager(self.sierra, self.config)
        
        # Métriques de performance
        self.total_trades = 0
        self.successful_trades = 0
        self.avg_latency = 0.0
        self.latency_history = []
        
        # Statut système
        self.is_optimized = False
        self.last_optimization = None
        
        logger.info("🚀 Optimized Trading System initialisé")
    
    async def initialize_system(self) -> bool:
        """Initialise le système avec optimisation"""
        try:
            logger.info("🔧 Initialisation système optimisé...")
            
            # Connexion Sierra Charts
            connected = await self.sierra.connect()
            if not connected:
                logger.error("❌ Échec connexion Sierra Charts")
                return False
            
            # Optimisation connexion
            optimized = await self.optimizer.optimize_connection()
            if not optimized:
                logger.error("❌ Échec optimisation connexion")
                return False
            
            self.is_optimized = True
            self.last_optimization = datetime.now()
            
            # Test latence optimisée
            latency = await self._test_current_latency()
            self._update_latency_metrics(latency)
            
            logger.info(f"✅ Système optimisé - Latence: {latency:.2f}ms")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation: {e}")
            return False
    
    async def execute_trading_decision(self, decision: TradingDecision) -> Optional[str]:
        """Exécute une décision de trading optimisée"""
        try:
            # Validation latence pour stratégie
            if not validate_latency_for_strategy(decision.strategy, decision.expected_latency):
                logger.warning(f"⚠️ Latence {decision.expected_latency:.2f}ms trop élevée pour {decision.strategy}")
                return None
            
            # Mesure latence réelle
            start_time = datetime.now()
            
            # Exécution ordre optimisé
            order_id = await self.order_manager.execute_signal(
                signal=decision.signal,
                symbol=decision.signal.symbol if hasattr(decision.signal, 'symbol') else 'ES',
                quantity=decision.signal.quantity if hasattr(decision.signal, 'quantity') else 1
            )
            
            # Calcul latence réelle
            end_time = datetime.now()
            actual_latency = (end_time - start_time).total_seconds() * 1000
            self._update_latency_metrics(actual_latency)
            
            if order_id:
                self.total_trades += 1
                logger.info(f"⚡ Ordre exécuté: {order_id} - Latence: {actual_latency:.2f}ms")
                
                # Validation performance
                if actual_latency <= self._get_max_latency_for_strategy(decision.strategy):
                    self.successful_trades += 1
                    logger.info(f"✅ Performance optimale pour {decision.strategy}")
                else:
                    logger.warning(f"⚠️ Latence élevée: {actual_latency:.2f}ms")
                
                return order_id
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution décision: {e}")
            return None
    
    async def execute_scalping_trade(self, signal: TradingSignal) -> Optional[str]:
        """Exécute un trade de scalping (latence critique)"""
        try:
            decision = TradingDecision(
                signal=signal,
                strategy="scalping",
                expected_latency=15.0,  # 15ms cible
                confidence=signal.confidence,
                risk_level="high",
                execution_priority=1
            )
            
            return await self.execute_trading_decision(decision)
            
        except Exception as e:
            logger.error(f"❌ Erreur scalping: {e}")
            return None
    
    async def execute_day_trading_trade(self, signal: TradingSignal) -> Optional[str]:
        """Exécute un trade de day trading"""
        try:
            decision = TradingDecision(
                signal=signal,
                strategy="day_trading",
                expected_latency=30.0,  # 30ms acceptable
                confidence=signal.confidence,
                risk_level="medium",
                execution_priority=2
            )
            
            return await self.execute_trading_decision(decision)
            
        except Exception as e:
            logger.error(f"❌ Erreur day trading: {e}")
            return None
    
    async def execute_swing_trading_trade(self, signal: TradingSignal) -> Optional[str]:
        """Exécute un trade de swing trading"""
        try:
            decision = TradingDecision(
                signal=signal,
                strategy="swing_trading",
                expected_latency=50.0,  # 50ms acceptable
                confidence=signal.confidence,
                risk_level="medium",
                execution_priority=3
            )
            
            return await self.execute_trading_decision(decision)
            
        except Exception as e:
            logger.error(f"❌ Erreur swing trading: {e}")
            return None
    
    async def execute_position_trading_trade(self, signal: TradingSignal) -> Optional[str]:
        """Exécute un trade de position trading"""
        try:
            decision = TradingDecision(
                signal=signal,
                strategy="position_trading",
                expected_latency=100.0,  # 100ms acceptable
                confidence=signal.confidence,
                risk_level="low",
                execution_priority=4
            )
            
            return await self.execute_trading_decision(decision)
            
        except Exception as e:
            logger.error(f"❌ Erreur position trading: {e}")
            return None
    
    async def monitor_and_optimize(self) -> Dict[str, Any]:
        """Surveille et optimise les performances en temps réel"""
        try:
            # Test latence actuelle
            current_latency = await self._test_current_latency()
            
            # Optimisation automatique si nécessaire
            optimization_result = await self.optimizer.optimize_performance()
            
            # Mise à jour métriques
            self._update_latency_metrics(current_latency)
            
            # Surveillance ordres
            await self.order_manager.monitor_orders()
            
            return {
                'current_latency': current_latency,
                'avg_latency': self.avg_latency,
                'optimization_applied': optimization_result.get('performance_improved', False),
                'total_trades': self.total_trades,
                'success_rate': self.successful_trades / max(self.total_trades, 1) * 100
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur monitoring: {e}")
            return {}
    
    async def _test_current_latency(self) -> float:
        """Teste la latence actuelle"""
        try:
            start_time = datetime.now()
            
            # Test ordre optimisé
            order_id = await self.optimizer.place_optimized_order(
                symbol='ES',
                side=OrderSide.BUY,
                quantity=1,
                order_type=OrderType.MARKET
            )
            
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
        
        # Calcul moyenne
        self.avg_latency = sum(self.latency_history) / len(self.latency_history)
    
    def _get_max_latency_for_strategy(self, strategy: str) -> float:
        """Retourne la latence maximale pour une stratégie"""
        if strategy == "scalping":
            return self.strategy_config.scalping_max_latency
        elif strategy == "day_trading":
            return self.strategy_config.day_trading_max_latency
        elif strategy == "swing_trading":
            return self.strategy_config.swing_trading_max_latency
        elif strategy == "position_trading":
            return self.strategy_config.position_trading_max_latency
        
        return 100.0  # Par défaut
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des performances"""
        return {
            'total_trades': self.total_trades,
            'successful_trades': self.successful_trades,
            'success_rate': self.successful_trades / max(self.total_trades, 1) * 100,
            'avg_latency': self.avg_latency,
            'min_latency': min(self.latency_history) if self.latency_history else 0,
            'max_latency': max(self.latency_history) if self.latency_history else 0,
            'is_optimized': self.is_optimized,
            'last_optimization': self.last_optimization.isoformat() if self.last_optimization else None
        }
    
    async def shutdown(self) -> None:
        """Arrêt propre du système"""
        try:
            logger.info("🔄 Arrêt système optimisé...")
            
            # Annulation tous ordres
            await self.order_manager.cancel_all_orders()
            
            # Déconnexion Sierra
            await self.sierra.disconnect()
            
            logger.info("✅ Système arrêté proprement")
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt: {e}") 