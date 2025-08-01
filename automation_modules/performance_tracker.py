#!/usr/bin/env python3
"""
📊 PERFORMANCE TRACKER - MIA_IA_SYSTEM
Suivi des performances trading en temps réel
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger

logger = get_logger(__name__)

@dataclass
class TradingStats:
    """Statistiques trading temps réel"""
    
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    daily_pnl: float = 0.0
    max_drawdown: float = 0.0
    current_positions: int = 0
    
    signals_generated: int = 0
    signals_filtered: int = 0
    ml_approved: int = 0
    ml_rejected: int = 0
    gamma_optimized: int = 0
    
    start_time: datetime = field(default_factory=datetime.now)
    last_trade_time: Optional[datetime] = None
    
    @property
    def win_rate(self) -> float:
        """Calcul win rate"""
        if self.total_trades == 0:
            return 0.0
        return (self.winning_trades / self.total_trades) * 100
    
    @property
    def profit_factor(self) -> float:
        """Calcul profit factor"""
        if self.losing_trades == 0:
            return float('inf') if self.winning_trades > 0 else 0.0
        
        avg_win = self.total_pnl / max(self.winning_trades, 1)
        avg_loss = abs(self.total_pnl) / max(self.losing_trades, 1)
        
        return avg_win / avg_loss if avg_loss > 0 else 0.0
    
    @property
    def trading_duration(self) -> timedelta:
        """Durée trading"""
        return datetime.now() - self.start_time

class PerformanceTracker:
    """Tracker de performance optimisé"""
    
    def __init__(self):
        self.stats = TradingStats()
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
    def add_trade(self, pnl: float, is_win: bool) -> None:
        """Ajoute un trade aux statistiques"""
        self.stats.total_trades += 1
        self.stats.total_pnl += pnl
        self.stats.daily_pnl += pnl
        self.stats.last_trade_time = datetime.now()
        
        if is_win:
            self.stats.winning_trades += 1
        else:
            self.stats.losing_trades += 1
            
        # Mise à jour drawdown
        if pnl < 0:
            self.stats.max_drawdown = min(self.stats.max_drawdown, pnl)
            
        logger.info(f"📊 Trade ajouté: PnL={pnl:.2f}, Win={is_win}, "
                   f"Total={self.stats.total_trades}, WinRate={self.stats.win_rate:.1f}%")
    
    def add_signal(self, filtered: bool = False, ml_approved: bool = False, 
                   gamma_optimized: bool = False) -> None:
        """Ajoute un signal aux statistiques"""
        self.stats.signals_generated += 1
        
        if filtered:
            self.stats.signals_filtered += 1
            
        if ml_approved:
            self.stats.ml_approved += 1
        else:
            self.stats.ml_rejected += 1
            
        if gamma_optimized:
            self.stats.gamma_optimized += 1
    
    def reset_daily_stats(self) -> None:
        """Reset des stats quotidiennes"""
        self.stats.daily_pnl = 0.0
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        logger.info("🔄 Stats quotidiennes resetées")
    
    def get_summary(self) -> dict:
        """Retourne un résumé des performances"""
        return {
            'total_trades': self.stats.total_trades,
            'win_rate': self.stats.win_rate,
            'profit_factor': self.stats.profit_factor,
            'total_pnl': self.stats.total_pnl,
            'daily_pnl': self.stats.daily_pnl,
            'max_drawdown': self.stats.max_drawdown,
            'trading_duration': str(self.stats.trading_duration),
            'signals_generated': self.stats.signals_generated,
            'signals_filtered': self.stats.signals_filtered,
            'ml_approval_rate': (self.stats.ml_approved / max(self.stats.signals_generated, 1)) * 100,
            'gamma_optimized': self.stats.gamma_optimized
        } 