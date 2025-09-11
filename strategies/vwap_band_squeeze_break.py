#!/usr/bin/env python3
"""
Stratégie VWAP Band Squeeze Break
Détecte les compressions des bandes VWAP (squeeze) et génère des signaux
de breakout dans la direction de la cassure.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class VwapBandSqueezeBreak:
    """
    Stratégie de breakout basée sur les compressions de bandes VWAP.
    
    Logique:
    - Détecte une compression des bandes SD1 (squeeze)
    - Confirme le breakout avec delta burst et accélération des quotes
    - Génère un signal de continuation vers les niveaux SD2/SD3
    """
    name: str = "vwap_band_squeeze_break"
    requires: tuple = ("vwap", "orderflow", "quotes", "price")
    params: dict = None

    def __post_init__(self):
        self.params = self.params or {
            "sd_tight_thresh": 0.6,        # Seuil de compression SD1 (%)
            "atr_mult_sl": 1.0,           # Multiplicateur ATR pour stop loss
            "min_conf": 0.62               # Confiance minimale requise
        }

    def should_run(self, ctx: Dict[str, Any]) -> bool:
        """
        Vérifie si tous les prérequis sont disponibles.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            True si la stratégie peut s'exécuter
        """
        return all(k in ctx for k in ("vwap", "orderflow", "quotes", "price"))

    def generate(self, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Génère un signal de breakout après squeeze VWAP.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            Signal de trading ou None
        """
        if not self.should_run(ctx):
            return None
            
        v = ctx["vwap"]
        of = ctx["orderflow"]
        q = ctx["quotes"]
        price = ctx["price"]["last"]
        
        vwap = v.get("vwap")
        sd1u = v.get("sd1_up")
        sd1d = v.get("sd1_dn")
        
        if not all([vwap, sd1u, sd1d]):
            return None

        # Compression: bande SD1 étroite
        tight = (sd1u - sd1d) / max(abs(price), 1.0) < self.params["sd_tight_thresh"] / 100.0
        if not tight or not (of.get("delta_burst", False) and q.get("speed_up", False)):
            return None

        tick = ctx.get("tick_size", 0.25)
        atr = max(ctx.get("atr", 4*tick), 2*tick)

        # Signal LONG: breakout au-dessus de SD1
        if price > sd1u:
            entry = price
            sl = vwap - self.params["atr_mult_sl"]*atr
            tps = [
                v.get("sd2_up", entry + 6*tick),
                v.get("sd3_up", entry + 10*tick)
            ]
            
            return {
                "strategy": self.name,
                "side": "LONG",
                "confidence": 0.66,
                "entry": entry,
                "stop": sl,
                "targets": [tp for tp in tps if tp],
                "reason": "Squeeze SD1 + break up",
                "metadata": {"sd1_range": sd1u - sd1d}
            }
            
        # Signal SHORT: breakdown en-dessous de SD1
        if price < sd1d:
            entry = price
            sl = vwap + self.params["atr_mult_sl"]*atr
            tps = [
                v.get("sd2_dn", entry - 6*tick),
                v.get("sd3_dn", entry - 10*tick)
            ]
            
            return {
                "strategy": self.name,
                "side": "SHORT",
                "confidence": 0.66,
                "entry": entry,
                "stop": sl,
                "targets": [tp for tp in tps if tp],
                "reason": "Squeeze SD1 + break down",
                "metadata": {"sd1_range": sd1u - sd1d}
            }
            
        return None

