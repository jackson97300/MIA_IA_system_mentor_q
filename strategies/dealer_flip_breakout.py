#!/usr/bin/env python3
"""
Stratégie Dealer Flip Breakout
Détecte les breakouts après un flip gamma des dealers et génère des signaux
de continuation dans la direction de la cassure.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class DealerFlipBreakout:
    """
    Stratégie de breakout basée sur le flip gamma des dealers.
    
    Logique:
    - Détecte le flip gamma (changement de position des dealers)
    - Confirme le breakout avec delta burst et accélération des quotes
    - Génère un signal de continuation vers les niveaux VWAP SD
    """
    name: str = "dealer_flip_breakout"
    requires: tuple = ("menthorq", "vwap", "vva", "orderflow", "quotes", "price")
    params: dict = None

    def __post_init__(self):
        self.params = self.params or {
            "confirm_burst": True,          # Exiger un delta burst
            "need_quotes_speed": True,      # Exiger l'accélération des quotes
            "atr_mult_sl": 1.0,            # Multiplicateur ATR pour stop loss
            "min_conf": 0.65               # Confiance minimale requise
        }

    def should_run(self, ctx: Dict[str, Any]) -> bool:
        """
        Vérifie si tous les prérequis sont disponibles.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            True si la stratégie peut s'exécuter
        """
        return all(k in ctx for k in ("menthorq", "vwap", "vva", "orderflow", "quotes", "price"))

    def _break_dir(self, ctx: Dict[str, Any]) -> str:
        """
        Détermine la direction du breakout basée sur la position vs VWAP.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            "LONG" ou "SHORT"
        """
        # Direction = sens du flip (gamma_flip True => tendance sur cassures)
        return "LONG" if ctx["price"]["last"] >= ctx["vwap"].get("vwap", ctx["price"]["last"]) else "SHORT"

    def _level(self, ctx: Dict[str, Any]) -> Optional[float]:
        """
        Détermine le niveau de breakout (VWAP ou VPOC).
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            Niveau de breakout ou None
        """
        # Break sur VWAP ou VPOC
        vwap = ctx["vwap"].get("vwap")
        vpoc = ctx["vva"].get("vpoc")
        
        if vwap and vpoc:
            # Choisir le plus proche du prix comme trigger
            price = ctx["price"]["last"]
            return vwap if abs(price - vwap) < abs(price - vpoc) else vpoc
            
        return vwap or ctx["vva"].get("vpoc")

    def generate(self, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Génère un signal de breakout après flip gamma.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            Signal de trading ou None
        """
        if not self.should_run(ctx):
            return None
            
        # Vérifier le flip gamma
        if not ctx["menthorq"].get("gamma_flip", False):
            return None

        of = ctx["orderflow"]
        quotes = ctx["quotes"]
        
        # Confirmer le momentum
        if self.params["confirm_burst"] and not of.get("delta_burst", False):
            return None
        if self.params["need_quotes_speed"] and not quotes.get("speed_up", False):
            return None

        level = self._level(ctx)
        if not level:
            return None

        price = ctx["price"]["last"]
        direction = self._break_dir(ctx)
        tick = ctx.get("tick_size", 0.25)
        atr = max(ctx.get("atr", 4*tick), 2*tick)

        # Signal LONG: breakout au-dessus du niveau
        if direction == "LONG" and price > level:
            entry = price
            sl = level - self.params["atr_mult_sl"]*atr
            tps = [
                ctx["vwap"].get("sd1_up", entry+4*tick),
                ctx["vwap"].get("sd2_up", entry+8*tick)
            ]
            conf = 0.7
            
            return {
                "strategy": self.name,
                "side": "LONG",
                "confidence": conf,
                "entry": entry,
                "stop": sl,
                "targets": [tp for tp in tps if tp],
                "reason": "Gamma flip + breakout confirmé",
                "metadata": {"level": level}
            }
            
        # Signal SHORT: breakdown en-dessous du niveau
        if direction == "SHORT" and price < level:
            entry = price
            sl = level + self.params["atr_mult_sl"]*atr
            tps = [
                ctx["vwap"].get("sd1_dn", entry-4*tick),
                ctx["vwap"].get("sd2_dn", entry-8*tick)
            ]
            conf = 0.7
            
            return {
                "strategy": self.name,
                "side": "SHORT",
                "confidence": conf,
                "entry": entry,
                "stop": sl,
                "targets": [tp for tp in tps if tp],
                "reason": "Gamma flip + breakdown confirmé",
                "metadata": {"level": level}
            }
            
        return None


