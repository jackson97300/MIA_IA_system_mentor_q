#!/usr/bin/env python3
"""
📋 CONFIG MANAGER - MIA_IA_SYSTEM
Gestion centralisée de la configuration automation
"""

import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger

logger = get_logger(__name__)

@dataclass
class AutomationConfig:
    """Configuration automation optimisée"""
    
    # Trading Parameters
    max_position_size: int = 2
    daily_loss_limit: float = 500.0
    min_signal_confidence: float = 0.70
    trading_start_hour: int = 9
    trading_end_hour: int = 16
    position_risk_percent: float = 1.0
    max_daily_trades: int = 20
    
    # Risk Management
    stop_loss_ticks: int = 8
    take_profit_ratio: float = 2.0
    
    # ML & Analysis
    ml_ensemble_enabled: bool = True
    ml_min_confidence: float = 0.65
    gamma_cycles_enabled: bool = True
    
    # Confluence Settings
    confluence_threshold: float = 0.25
    confluence_adaptive: bool = True
    
    # Monitoring
    performance_update_interval: int = 60
    health_check_interval: int = 30
    
    # IBKR Connection
    ibkr_host: str = "127.0.0.1"
    ibkr_port: int = 7497
    ibkr_client_id: int = 1
    
    # Logging
    log_level: str = "INFO"
    log_to_file: bool = True
    
    def validate(self) -> bool:
        """Valide la configuration"""
        try:
            assert 0 < self.max_position_size <= 10
            assert self.daily_loss_limit > 0
            assert 0.5 <= self.min_signal_confidence <= 1.0
            assert 0 <= self.trading_start_hour <= 23
            assert 0 <= self.trading_end_hour <= 23
            assert 0 < self.position_risk_percent <= 5.0
            assert self.max_daily_trades > 0
            assert self.stop_loss_ticks > 0
            assert self.take_profit_ratio > 1.0
            assert 0.5 <= self.ml_min_confidence <= 1.0
            assert 0.1 <= self.confluence_threshold <= 1.0
            
            logger.info("✅ Configuration validée")
            return True
            
        except AssertionError as e:
            logger.error(f"❌ Configuration invalide: {e}")
            return False 