#!/usr/bin/env python3
"""
⚡ SIERRA CONFIG - MIA_IA_SYSTEM
Configuration optimisée pour Sierra Charts avec latence minimale
"""

import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger

logger = get_logger(__name__)

@dataclass
class SierraOptimizedConfig:
    """Configuration optimisée Sierra Charts"""
    
    # Connexion optimisée
    enable_ultra_low_latency: bool = True
    connection_timeout: float = 0.1
    heartbeat_interval: float = 1.0
    retry_attempts: int = 3
    
    # Pré-allocation ordres
    pre_allocate_orders: bool = True
    cache_size: int = 10
    symbols_to_cache: list = None
    
    # Optimisation performance
    batch_orders: bool = False
    max_batch_size: int = 5
    batch_delay: float = 0.01
    
    # Contrats supportés
    supported_contracts: Dict[str, Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.symbols_to_cache is None:
            self.symbols_to_cache = ['ES', 'MES']
        
        if self.supported_contracts is None:
            self.supported_contracts = {
                'ES': {
                    'tick_value': 12.50,
                    'tick_size': 0.25,
                    'margin': 5000.0,
                    'commission': 2.50,
                    'min_qty': 1,
                    'max_qty': 100
                },
                'MES': {
                    'tick_value': 1.25,
                    'tick_size': 0.25,
                    'margin': 500.0,
                    'commission': 0.25,
                    'min_qty': 1,
                    'max_qty': 1000
                }
            }

@dataclass
class TradingStrategyConfig:
    """Configuration stratégies trading"""
    
    # Scalping (latence critique)
    scalping_enabled: bool = True
    scalping_max_latency: float = 20.0  # ms
    scalping_min_confidence: float = 0.85
    
    # Day Trading
    day_trading_enabled: bool = True
    day_trading_max_latency: float = 50.0  # ms
    day_trading_min_confidence: float = 0.75
    
    # Swing Trading
    swing_trading_enabled: bool = True
    swing_trading_max_latency: float = 100.0  # ms
    swing_trading_min_confidence: float = 0.70
    
    # Position Trading
    position_trading_enabled: bool = True
    position_trading_max_latency: float = 200.0  # ms
    position_trading_min_confidence: float = 0.65

def create_optimized_sierra_config() -> SierraOptimizedConfig:
    """Crée une configuration Sierra Charts optimisée"""
    return SierraOptimizedConfig(
        enable_ultra_low_latency=True,
        pre_allocate_orders=True,
        batch_orders=False,  # Désactivé pour latence minimale
        connection_timeout=0.1,
        retry_attempts=3
    )

def create_trading_strategy_config() -> TradingStrategyConfig:
    """Crée une configuration stratégies trading"""
    return TradingStrategyConfig(
        scalping_enabled=True,
        day_trading_enabled=True,
        swing_trading_enabled=True,
        position_trading_enabled=True
    )

def get_contract_info(symbol: str) -> Dict[str, Any]:
    """Récupère les informations d'un contrat"""
    config = SierraOptimizedConfig()
    return config.supported_contracts.get(symbol, {})

def validate_latency_for_strategy(strategy: str, latency: float) -> bool:
    """Valide si la latence est acceptable pour une stratégie"""
    strategy_config = TradingStrategyConfig()
    
    if strategy == "scalping":
        return latency <= strategy_config.scalping_max_latency
    elif strategy == "day_trading":
        return latency <= strategy_config.day_trading_max_latency
    elif strategy == "swing_trading":
        return latency <= strategy_config.swing_trading_max_latency
    elif strategy == "position_trading":
        return latency <= strategy_config.position_trading_max_latency
    
    return True

def get_optimization_recommendations(latency: float) -> list:
    """Retourne des recommandations d'optimisation basées sur la latence"""
    recommendations = []
    
    if latency > 50:
        recommendations.append("🔧 Activer mode ultra-low latency")
        recommendations.append("🔧 Augmenter pré-allocation ordres")
    
    if latency > 100:
        recommendations.append("⚠️ Considérer IBKR pour scalping")
        recommendations.append("🔧 Optimiser connexion réseau")
    
    if latency < 20:
        recommendations.append("✅ Latence optimale - Aucune action requise")
    
    return recommendations 