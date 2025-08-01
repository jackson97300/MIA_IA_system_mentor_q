#!/usr/bin/env python3
"""
🛡️ RISK MANAGER - MIA_IA_SYSTEM
Gestion centralisée des risques trading
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger

logger = get_logger(__name__)

class RiskManager:
    """Gestionnaire de risques optimisé"""
    
    def __init__(self, config):
        self.config = config
        self.daily_loss = 0.0
        self.daily_trades = 0
        self.current_positions = 0
        self.last_reset = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
    def check_daily_loss_limit(self) -> bool:
        """Vérifie la limite de perte quotidienne"""
        if self.daily_loss >= self.config.daily_loss_limit:
            logger.warning(f"⚠️ Limite de perte quotidienne atteinte: {self.daily_loss:.2f}")
            return False
        return True
    
    def check_daily_trade_limit(self) -> bool:
        """Vérifie la limite de trades quotidiens"""
        if self.daily_trades >= self.config.max_daily_trades:
            logger.warning(f"⚠️ Limite de trades quotidiens atteinte: {self.daily_trades}")
            return False
        return True
    
    def check_position_limit(self) -> bool:
        """Vérifie la limite de positions"""
        if self.current_positions >= self.config.max_position_size:
            logger.warning(f"⚠️ Limite de positions atteinte: {self.current_positions}")
            return False
        return True
    
    def check_signal_confidence(self, signal_confidence: float) -> bool:
        """Vérifie la confiance du signal"""
        if signal_confidence < self.config.min_signal_confidence:
            logger.warning(f"⚠️ Confiance signal insuffisante: {signal_confidence:.3f}")
            return False
        return True
    
    def check_trading_hours(self) -> bool:
        """Vérifie les heures de trading"""
        now = datetime.now()
        current_hour = now.hour
        
        if not (self.config.trading_start_hour <= current_hour <= self.config.trading_end_hour):
            logger.warning(f"⚠️ Hors heures de trading: {current_hour}h")
            return False
        return True
    
    def add_trade_result(self, pnl: float) -> None:
        """Ajoute le résultat d'un trade"""
        self.daily_trades += 1
        self.daily_loss += abs(pnl) if pnl < 0 else 0
        
        logger.info(f"📊 Trade ajouté au risk manager: PnL={pnl:.2f}, "
                   f"Daily Loss={self.daily_loss:.2f}, Trades={self.daily_trades}")
    
    def add_position(self) -> None:
        """Ajoute une position"""
        self.current_positions += 1
        logger.info(f"📈 Position ajoutée: {self.current_positions}")
    
    def remove_position(self) -> None:
        """Retire une position"""
        self.current_positions = max(0, self.current_positions - 1)
        logger.info(f"📉 Position retirée: {self.current_positions}")
    
    def reset_daily_stats(self) -> None:
        """Reset des stats quotidiennes"""
        self.daily_loss = 0.0
        self.daily_trades = 0
        self.last_reset = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        logger.info("🔄 Stats quotidiennes risk manager resetées")
    
    def calculate_position_size(self, account_balance: float, risk_percent: float = None) -> int:
        """Calcule la taille de position optimale"""
        if risk_percent is None:
            risk_percent = self.config.position_risk_percent
            
        risk_amount = account_balance * (risk_percent / 100)
        position_size = max(1, int(risk_amount / 100))  # Simplifié
        
        return min(position_size, self.config.max_position_size)
    
    def calculate_stop_loss(self, entry_price: float, signal_direction: str) -> float:
        """Calcule le stop loss"""
        ticks = self.config.stop_loss_ticks
        tick_value = 12.50  # ES tick value
        
        if signal_direction == "LONG":
            return entry_price - (ticks * 0.25)
        else:
            return entry_price + (ticks * 0.25)
    
    def calculate_take_profit(self, entry_price: float, stop_loss: float, signal_direction: str) -> float:
        """Calcule le take profit"""
        risk = abs(entry_price - stop_loss)
        reward = risk * self.config.take_profit_ratio
        
        if signal_direction == "LONG":
            return entry_price + reward
        else:
            return entry_price - reward
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des risques"""
        return {
            'daily_loss': self.daily_loss,
            'daily_trades': self.daily_trades,
            'current_positions': self.current_positions,
            'daily_loss_limit': self.config.daily_loss_limit,
            'max_daily_trades': self.config.max_daily_trades,
            'max_position_size': self.config.max_position_size,
            'risk_percent': self.config.position_risk_percent
        } 