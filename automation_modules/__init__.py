#!/usr/bin/env python3
"""
🏗️ AUTOMATION MODULES - MIA_IA_SYSTEM
Division d'automation_main en modules spécialisés

Modules:
- config_manager.py : Gestion de la configuration
- confluence_calculator.py : Calcul de confluence
- trading_engine.py : Moteur de trading principal
- risk_manager.py : Gestion des risques
- performance_tracker.py : Suivi des performances
- sierra_connector.py : Connexion Sierra Charts
- order_manager.py : Gestion des ordres
- sierra_optimizer.py : Optimisation latence Sierra Charts
- sierra_config.py : Configuration optimisée Sierra Charts
- optimized_trading_system.py : Système de trading optimisé
"""

from .config_manager import AutomationConfig
from .confluence_calculator import EnhancedConfluenceCalculator
from .trading_engine import MIAAutomationSystem
from .risk_manager import RiskManager
from .performance_tracker import TradingStats, PerformanceTracker
from .sierra_connector import SierraConnector, OrderSide, OrderType, OrderStatus, SierraOrder, SierraPosition
from .order_manager import OrderManager, TradingSignal, OrderRequest
from .sierra_optimizer import SierraOptimizer, LatencyConfig
from .sierra_config import SierraOptimizedConfig, TradingStrategyConfig, create_optimized_sierra_config, create_trading_strategy_config
from .optimized_trading_system import OptimizedTradingSystem, TradingDecision

__all__ = [
    'AutomationConfig',
    'EnhancedConfluenceCalculator', 
    'MIAAutomationSystem',
    'RiskManager',
    'TradingStats',
    'PerformanceTracker',
    'SierraConnector',
    'OrderSide',
    'OrderType',
    'OrderStatus',
    'SierraOrder',
    'SierraPosition',
    'OrderManager',
    'TradingSignal',
    'OrderRequest',
    'SierraOptimizer',
    'LatencyConfig',
    'SierraOptimizedConfig',
    'TradingStrategyConfig',
    'create_optimized_sierra_config',
    'create_trading_strategy_config',
    'OptimizedTradingSystem',
    'TradingDecision'
] 