#!/usr/bin/env python3
"""
Script pour ajouter la classe Position manquante dans base_types.py
"""

import sys
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)


# Code à ajouter
POSITION_CLASS_CODE = '''
@dataclass
class Position:
    """Position de trading active"""
    id: str
    symbol: str
    side: str  # "long" ou "short"
    
    # Quantités
    quantity: int
    entry_price: float
    current_price: float
    
    # Risk management
    stop_loss: float
    take_profit: float
    
    # Timestamps
    entry_time: pd.Timestamp
    exit_time: Optional[pd.Timestamp] = None
    
    # État
    status: str = "open"  # open, closed, pending
    
    # P&L
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    
    # Metadata
    signal_id: Optional[str] = None
    strategy: Optional[str] = None
    
    @property
    def is_profitable(self) -> bool:
        """Position profitable"""
        return self.unrealized_pnl > 0
    
    @property
    def risk_amount(self) -> float:
        """Montant risqué en dollars"""
        if self.side == "long":
            risk_ticks = (self.entry_price - self.stop_loss) / ES_TICK_SIZE
        else:
            risk_ticks = (self.stop_loss - self.entry_price) / ES_TICK_SIZE
        return risk_ticks * ES_TICK_VALUE * self.quantity
    
    def update_pnl(self, current_price: float):
        """Met à jour le P&L"""
        self.current_price = current_price
        if self.side == "long":
            price_diff = current_price - self.entry_price
        else:
            price_diff = self.entry_price - current_price
        
        self.unrealized_pnl = (price_diff / ES_TICK_SIZE) * ES_TICK_VALUE * self.quantity

@dataclass
class OrderType:
    """Types d'ordres supportés"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

@dataclass  
class OrderStatus:
    """Statuts possibles d'un ordre"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
'''

def add_position_class():
    """Ajoute la classe Position à base_types.py"""
    
    # Chemin du fichier
    base_types_path = Path("core/base_types.py")
    
    if not base_types_path.exists():
        logger.error("Fichier {base_types_path} non trouvé!")
        return False
    
    # Lire le contenu actuel
    with open(base_types_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si Position existe déjà
    if "class Position" in content:
        logger.info("La classe Position existe déjà")
        return True
    
    # Trouver où insérer (après TradingSignal)
    insert_pos = content.find("@dataclass\nclass SystemState:")
    
    if insert_pos == -1:
        # Sinon, ajouter à la fin avant les exceptions
        insert_pos = content.find("# === EXCEPTIONS ===")
    
    if insert_pos == -1:
        logger.warning("Position d'insertion non trouvée, ajout à la fin")
        content += "\n\n" + POSITION_CLASS_CODE
    else:
        # Insérer le code
        content = content[:insert_pos] + POSITION_CLASS_CODE + "\n\n" + content[insert_pos:]
    
    # Sauvegarder
    with open(base_types_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info("Classe Position ajoutée avec succès!")
    return True

if __name__ == "__main__":
    add_position_class()