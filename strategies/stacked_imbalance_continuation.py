#!/usr/bin/env python3
"""
Stratégie Stacked Imbalance Continuation
Détecte les stacked imbalances (déséquilibres empilés) et génère des signaux
de continuation dans la direction du déséquilibre.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class StackedImbalanceContinuation:
    """
    Stratégie de continuation basée sur les stacked imbalances.
    
    Logique:
    - Détecte un stacked imbalance significatif (min_rows)
    - Évite les trades contre VWAP fort
    - Génère un signal de continuation dans la direction du déséquilibre
    """
    name: str = "stacked_imbalance_continuation"
    requires: tuple = ("orderflow", "vwap", "price")
    params: dict = None

    def __post_init__(self):
        self.params = self.params or {
            "min_rows": 3,                 # Nombre minimum de rangées d'imbalance
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
        return all(k in ctx for k in ("orderflow", "vwap", "price"))

    def generate(self, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Génère un signal de continuation après stacked imbalance.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            Signal de trading ou None
        """
        if not self.should_run(ctx):
            return None
            
        of = ctx["orderflow"]
        vwap = ctx["vwap"]
        price = ctx["price"]["last"]
        
        # Vérifier le stacked imbalance
        si = of.get("stacked_imbalance", {})
        if not si or si.get("rows", 0) < self.params["min_rows"]:
            return None

        side = si.get("side")
        if not side:
            return None
            
        tick = ctx.get("tick_size", 0.25)
        atr = max(ctx.get("atr", 4*tick), 2*tick)

        # Filtre: éviter contre VWAP fort
        vwap_price = vwap.get("vwap", price)
        if side == "BUY" and price < vwap_price and abs(price - vwap_price) < 2*atr:
            return None
        if side == "SELL" and price > vwap_price and abs(price - vwap_price) < 2*atr:
            return None

        # Signal LONG: continuation après stacked ask imbalance
        if side == "BUY":
            entry = price
            sl = entry - self.params["atr_mult_sl"]*atr
            tps = [entry + 4*tick, entry + 8*tick]
            
            return {
                "strategy": self.name,
                "side": "LONG",
                "confidence": 0.62,
                "entry": entry,
                "stop": sl,
                "targets": tps,
                "reason": "Continuation après stacked ask imbalance",
                "metadata": {"rows": si.get("rows", 0)}
            }
            
        # Signal SHORT: continuation après stacked bid imbalance
        if side == "SELL":
            entry = price
            sl = entry + self.params["atr_mult_sl"]*atr
            tps = [entry - 4*tick, entry - 8*tick]
            
            return {
                "strategy": self.name,
                "side": "SHORT",
                "confidence": 0.62,
                "entry": entry,
                "stop": sl,
                "targets": tps,
                "reason": "Continuation après stacked bid imbalance",
                "metadata": {"rows": si.get("rows", 0)}
            }
            
        return None
