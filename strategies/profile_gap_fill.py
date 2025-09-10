#!/usr/bin/env python3
"""
Stratégie Profile Gap Fill
Détecte les entrées dans les zones LVN (Low Volume Node) et génère des signaux
de comblement vers les niveaux HVN/POC.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple


@dataclass
class ProfileGapFill:
    """
    Stratégie de comblement basée sur les profils de volume.
    
    Logique:
    - Détecte une entrée dans une zone LVN (Low Volume Node)
    - Évite les zones avec absorption (défense)
    - Génère un signal de comblement vers HVN/POC
    """
    name: str = "profile_gap_fill"
    requires: tuple = ("vva", "orderflow", "price")
    params: dict = None

    def __post_init__(self):
        self.params = self.params or {
            "atr_mult_sl": 1.0,           # Multiplicateur ATR pour stop loss
            "min_conf": 0.6               # Confiance minimale requise
        }

    def should_run(self, ctx: Dict[str, Any]) -> bool:
        """
        Vérifie si tous les prérequis sont disponibles.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            True si la stratégie peut s'exécuter
        """
        return all(k in ctx for k in ("vva", "orderflow", "price"))

    def _in_lvn(self, ctx: Dict[str, Any]) -> Tuple[bool, Optional[Tuple[float, float]]]:
        """
        Vérifie si le prix est dans une zone LVN.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            (True si dans LVN, (lvn_low, lvn_high) ou None)
        """
        # Heuristique minimaliste: ctx["vva"] peut exposer lvn_low/lvn_high
        vva = ctx["vva"]
        price = ctx["price"]["last"]
        lvn_low = vva.get("lvn_low")
        lvn_high = vva.get("lvn_high")
        
        if lvn_low is None or lvn_high is None:
            return False, None
            
        return lvn_low < price < lvn_high, (lvn_low, lvn_high)

    def generate(self, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Génère un signal de comblement après entrée en LVN.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            Signal de trading ou None
        """
        if not self.should_run(ctx):
            return None
            
        ok, band = self._in_lvn(ctx)
        if not ok:
            return None

        of = ctx["orderflow"]
        price = ctx["price"]["last"]
        vpoc = ctx["vva"].get("vpoc")
        
        # Éviter les zones avec absorption (défense)
        if of.get("absorption"):
            return None

        tick = ctx.get("tick_size", 0.25)
        atr = max(ctx.get("atr", 4*tick), 2*tick)
        lvn_low, lvn_high = band

        # Sens = vers le HVN/POC le plus proche
        conf = 0.63
        
        # Signal LONG: entrée côté bas → LONG vers comblement
        if price - lvn_low < lvn_high - price:
            entry = price
            sl = lvn_low - self.params["atr_mult_sl"]*atr
            # Target vers le haut de la LVN ou VPOC si plus haut
            target1 = lvn_high
            if vpoc and vpoc > lvn_high:
                target1 = vpoc
            targets = [target1, target1 + 4*tick]  # 2 targets progressifs
                
            return {
                "strategy": self.name,
                "side": "LONG",
                "confidence": conf,
                "entry": entry,
                "stop": sl,
                "targets": targets,
                "reason": "Entrée LVN → gap fill vers HVN/POC",
                "metadata": {"lvn_range": (lvn_low, lvn_high)}
            }
        else:
            # Signal SHORT: entrée côté haut → SHORT vers comblement
            entry = price
            sl = lvn_high + self.params["atr_mult_sl"]*atr
            # Target vers le bas de la LVN ou VPOC si plus bas
            target1 = lvn_low
            if vpoc and vpoc < lvn_low:
                target1 = vpoc
            targets = [target1, target1 - 4*tick]  # 2 targets progressifs
                
            return {
                "strategy": self.name,
                "side": "SHORT",
                "confidence": conf,
                "entry": entry,
                "stop": sl,
                "targets": targets,
                "reason": "Entrée LVN → gap fill vers HVN/POC",
                "metadata": {"lvn_range": (lvn_low, lvn_high)}
            }
