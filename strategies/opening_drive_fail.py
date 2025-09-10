#!/usr/bin/env python3
"""
Stratégie Opening Drive Fail
Détecte les échecs de drive d'ouverture près des murs gamma et génère
des signaux de fade vers VWAP.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class OpeningDriveFail:
    """
    Stratégie de fade basée sur les échecs de drive d'ouverture.
    
    Logique:
    - Détecte un drive d'ouverture qui s'essouffle près d'un mur gamma
    - Confirme avec VIX en hausse et absence de delta burst
    - Génère un signal de fade vers VWAP
    """
    name: str = "opening_drive_fail"
    requires: tuple = ("session", "menthorq", "vwap", "vix", "orderflow", "price")
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
        return all(k in ctx for k in ("session", "menthorq", "vwap", "vix", "orderflow", "price"))

    def generate(self, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Génère un signal de fade après échec de drive d'ouverture.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            Signal de trading ou None
        """
        if not self.should_run(ctx):
            return None
            
        # Vérifier que c'est la session d'ouverture
        if ctx["session"].get("label") != "OPEN":
            return None
        if not ctx["session"].get("time_ok", True):
            return None

        m = ctx["menthorq"]
        of = ctx["orderflow"]
        vix = ctx["vix"]
        vwap = ctx["vwap"]
        price = ctx["price"]["last"]
        
        # Vérifier la présence d'un mur gamma
        wall = m.get("nearest_wall")
        if not wall: 
            return None

        # Drive échoue si stall near wall + delta s'aplatit + VIX en hausse
        stall = not of.get("delta_burst", False)
        if not (stall and vix.get("rising", False)):
            return None

        tick = ctx.get("tick_size", 0.25)
        atr = max(ctx.get("atr", 4*tick), 2*tick)

        # Signal SHORT: fade vers VWAP après échec sur mur CALL
        if wall["type"] == "CALL":
            entry = price
            sl = wall["price"] + self.params["atr_mult_sl"]*atr
            tps = [vwap.get("vwap", entry - 6*tick)]
            
            return {
                "strategy": self.name,
                "side": "SHORT",
                "confidence": 0.63,
                "entry": entry,
                "stop": sl,
                "targets": tps,
                "reason": "Opening drive fail sur CALL wall (fade vers VWAP)",
                "metadata": {"wall": wall, "vix_rising": vix.get("rising", False)}
            }
            
        # Signal LONG: revert vers VWAP après échec sur mur PUT
        if wall["type"] == "PUT":
            entry = price
            sl = wall["price"] - self.params["atr_mult_sl"]*atr
            tps = [vwap.get("vwap", entry + 6*tick)]
            
            return {
                "strategy": self.name,
                "side": "LONG",
                "confidence": 0.63,
                "entry": entry,
                "stop": sl,
                "targets": tps,
                "reason": "Opening drive fail sur PUT wall (revert vers VWAP)",
                "metadata": {"wall": wall, "vix_rising": vix.get("rising", False)}
            }
            
        return None
