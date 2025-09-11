#!/usr/bin/env python3
"""
Stratégie Liquidity Sweep Reversal
Détecte les balayages de liquidité (sweeps) avec absorption et génère
des signaux de retournement contrarien.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class LiquiditySweepReversal:
    """
    Stratégie de reversion basée sur les balayages de liquidité.
    
    Logique:
    - Détecte un wick important (sweep de liquidité)
    - Confirme le delta flip (changement de momentum)
    - Vérifie l'absorption (défense du niveau)
    - Génère un signal contrarien
    """
    name: str = "liquidity_sweep_reversal"
    requires: tuple = ("orderflow", "price", "basedata")
    params: dict = None

    def __post_init__(self):
        self.params = self.params or {
            "min_wick_ticks": 6,            # Wick minimum requis (en ticks)
            "atr_mult_sl": 1.0,            # Multiplicateur ATR pour stop loss
            "min_conf": 0.6                # Confiance minimale requise
        }

    def should_run(self, ctx: Dict[str, Any]) -> bool:
        """
        Vérifie si tous les prérequis sont disponibles.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            True si la stratégie peut s'exécuter
        """
        return all(k in ctx for k in ("orderflow", "price"))

    def generate(self, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Génère un signal de reversion après sweep de liquidité.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            Signal de trading ou None
        """
        if not self.should_run(ctx):
            return None
            
        of = ctx["orderflow"]
        price = ctx["price"]["last"]
        
        # Vérifier le wick (sweep de liquidité)
        wick = ctx.get("basedata", {}).get("last_wick_ticks", 0)
        delta_flip = of.get("delta_flip", False)
        absorption = of.get("absorption", {})

        # Conditions requises
        if wick < self.params["min_wick_ticks"] or not delta_flip or not absorption:
            return None

        tick = ctx.get("tick_size", 0.25)
        atr = max(ctx.get("atr", 4*tick), 2*tick)

        # Signal SHORT: rejet haut + absorption acheteuse (reversal short)
        if absorption["side"] == "BUY":
            entry = price
            sl = entry + self.params["atr_mult_sl"]*atr
            tps = [entry - 4*tick, entry - 8*tick]
            
            return {
                "strategy": self.name,
                "side": "SHORT",
                "confidence": 0.65,
                "entry": entry,
                "stop": sl,
                "targets": tps,
                "reason": "Sweep + absorption acheteuse (reversal short)",
                "metadata": {"wick_ticks": wick}
            }
            
        # Signal LONG: rejet bas + absorption vendeuse (reversal long)
        if absorption["side"] == "SELL":
            entry = price
            sl = entry - self.params["atr_mult_sl"]*atr
            tps = [entry + 4*tick, entry + 8*tick]
            
            return {
                "strategy": self.name,
                "side": "LONG",
                "confidence": 0.65,
                "entry": entry,
                "stop": sl,
                "targets": tps,
                "reason": "Sweep + absorption vendeuse (reversal long)",
                "metadata": {"wick_ticks": wick}
            }
            
        return None


