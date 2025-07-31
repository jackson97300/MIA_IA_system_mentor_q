#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Core Trading Types
Types communs pour éviter imports circulaires entre modules execution
Version: v1.1 - Correction valeurs enum pour cohérence avec OrderManager

Ce module contient les types de base utilisés par tous les modules
d'exécution pour éviter les dépendances circulaires.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

class TradingMode(Enum):
    """Mode de trading unifié pour tout le système"""
    # ✅ CORRECTION: Valeurs en minuscules pour cohérence avec OrderManager
    DATA_COLLECTION = "data_collection"  # Était "DATA_COLLECTION"
    PAPER = "paper"                      # Était "PAPER"  
    LIVE = "live"                        # Était "LIVE"
    BACKTEST = "backtest"                # Était "BACKTEST"

class Position(Enum):
    """Position unifié pour tout le système"""
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"
    PENDING = "PENDING"

class AutomationStatus(Enum):
    """Statut automation unifié"""
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    ERROR = "ERROR"

# Export control
__all__ = [
    'TradingMode',
    'Position', 
    'AutomationStatus'
]

# Version info
__version__ = "1.1.0"