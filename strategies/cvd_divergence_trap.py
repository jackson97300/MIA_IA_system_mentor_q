#!/usr/bin/env python3
"""
Stratégie CVD Divergence Trap
Détecte les divergences CVD (Cumulative Volume Delta) et génère des signaux
de piège (trap) avec retour vers les niveaux de valeur.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class CvdDivergenceTrap:
    """
    Stratégie de piège basée sur les divergences CVD.
    
    Logique:
    - Détecte une divergence CVD (prix vs volume)
    - Utilise l'absorption comme hint de direction
    - Génère un signal de retour vers VWAP/VPOC
    """
    name: str = "cvd_divergence_trap"
    requires: tuple = ("orderflow", "vva", "vwap", "price")
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
        return all(k in ctx for k in ("orderflow", "price", "vva", "vwap"))

    def generate(self, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Génère un signal de piège après divergence CVD.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            Signal de trading ou None
        """
        if not self.should_run(ctx):
            return None
            
        of = ctx["orderflow"]
        price = ctx["price"]["last"]
        
        # Vérifier la divergence CVD
        if not of.get("cvd_divergence", False):
            return None

        # Jouer retour vers vwap/vpoc après fake HG/LW
        vwap = ctx["vwap"].get("vwap")
        vpoc = ctx["vva"].get("vpoc")
        tick = ctx.get("tick_size", 0.25)
        atr = max(ctx.get("atr", 4*tick), 2*tick)

        # Heuristique direction: si divergence sur high → short ; sur low → long
        # On utilise absorption side comme hint si dispo
        side_hint = (of.get("absorption") or {}).get("side")

        # Signal SHORT: divergence en haut + absorption BUY
        if side_hint == "BUY":
            entry = price
            sl = entry + self.params["atr_mult_sl"]*atr
            tps = [x for x in (vwap, vpoc) if x]
            
            return {
                "strategy": self.name,
                "side": "SHORT",
                "confidence": 0.62,
                "entry": entry,
                "stop": sl,
                "targets": tps or [entry - 6*tick],
                "reason": "CVD divergence (top trap) + absorption BUY",
                "metadata": {"vwap": vwap, "vpoc": vpoc}
            }
            
        # Signal LONG: divergence en bas + absorption SELL
        if side_hint == "SELL":
            entry = price
            sl = entry - self.params["atr_mult_sl"]*atr
            tps = [x for x in (vwap, vpoc) if x]
            
            return {
                "strategy": self.name,
                "side": "LONG",
                "confidence": 0.62,
                "entry": entry,
                "stop": sl,
                "targets": tps or [entry + 6*tick],
                "reason": "CVD divergence (bottom trap) + absorption SELL",
                "metadata": {"vwap": vwap, "vpoc": vpoc}
            }
            
        return None
