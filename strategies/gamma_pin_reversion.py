#!/usr/bin/env python3
"""
Stratégie Gamma Pin Reversion
Détecte les rejets de prix près des murs gamma (CALL/PUT) avec absorption
et génère des signaux de retournement contrarien.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class GammaPinReversion:
    """
    Stratégie de reversion basée sur les murs gamma et l'absorption.
    
    Logique:
    - Détecte quand le prix est proche d'un mur gamma (CALL/PUT)
    - Confirme l'absorption (défense du niveau)
    - Évite les stacked imbalances et delta bursts forts
    - Génère un signal contrarien vers VWAP/VPOC
    """
    name: str = "gamma_pin_reversion"
    requires: tuple = ("menthorq", "orderflow", "vwap", "vva", "price")
    params: dict = None

    def __post_init__(self):
        self.params = self.params or {
            "wall_dist_ticks_max": 8,      # Distance max au mur (en ticks)
            "atr_mult_sl": 1.25,           # Multiplicateur ATR pour stop loss
            "tp_chain": ("VWAP", "VPOC", "VA_EDGE"),  # Ordre des take profits
            "min_conf": 0.55               # Confiance minimale requise
        }

    def _get_tp_levels(self, ctx: Dict[str, Any]) -> List[float]:
        """
        Calcule les niveaux de take profit selon la chaîne configurée.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            Liste des niveaux de TP valides
        """
        vwap = ctx.get("vwap", {})
        vva = ctx.get("vva", {})
        price = ctx["price"]["last"]
        tps = []
        
        for k in self.params["tp_chain"]:
            if k == "VWAP" and vwap.get("vwap"):
                tps.append(vwap["vwap"])
            elif k == "VPOC" and vva.get("vpoc"):
                tps.append(vva["vpoc"])
            elif k == "VA_EDGE":
                # Proche edge opposé selon sens du trade
                # Pour l'instant, on skip cette logique complexe
                pass
                
        # Nettoyage: garder des TP du bon côté
        return [tp for tp in tps if tp and abs(tp - price) > 0.01]

    def should_run(self, ctx: Dict[str, Any]) -> bool:
        """
        Vérifie si tous les prérequis sont disponibles.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            True si la stratégie peut s'exécuter
        """
        return all(k in ctx for k in ("menthorq", "orderflow", "vwap", "vva", "price"))

    def generate(self, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Génère un signal de reversion basé sur les murs gamma.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            Signal de trading ou None
        """
        if not self.should_run(ctx):
            return None
            
        m = ctx["menthorq"]
        of = ctx["orderflow"]
        price = ctx["price"]["last"]
        
        # Vérification du mur gamma
        wall = m.get("nearest_wall")
        if not wall or wall.get("dist_ticks") is None:
            return None
            
        if wall["dist_ticks"] > self.params["wall_dist_ticks_max"]:
            return None

        # Pattern: proche mur + essoufflement (pas de stacked, pas de delta_burst) + absorption
        delta_burst = of.get("delta_burst", False)
        stacked = of.get("stacked_imbalance", {})
        absorption = of.get("absorption", {})

        # Éviter les poussées trop fortes
        if delta_burst:
            return None
        if stacked and stacked.get("rows", 0) >= 3:
            return None  # On évite de contrer une poussée claire

        if not absorption or "side" not in absorption:
            return None

        tick = ctx.get("tick_size", 0.25)
        atr = max(ctx.get("atr", 4 * tick), 2 * tick)

        # Signal LONG: rejet haussier du mur CALL avec absorption vendeuse
        if wall["type"] == "CALL" and absorption["side"] == "SELL":
            entry = price
            sl = wall["price"] - self.params["atr_mult_sl"] * atr
            tps = self._get_tp_levels(ctx)
            conf = 0.6
            
            if conf < self.params["min_conf"]:
                return None
                
            return {
                "strategy": self.name,
                "side": "LONG",
                "confidence": conf,
                "entry": entry,
                "stop": sl,
                "targets": tps or [entry + 4*tick],
                "reason": "Absorption vendeuse sur CALL wall proche, reversion",
                "metadata": {"wall": wall, "absorption": absorption}
            }

        # Signal SHORT: rejet baissier du mur PUT avec absorption acheteuse
        if wall["type"] == "PUT" and absorption["side"] == "BUY":
            entry = price
            sl = wall["price"] + self.params["atr_mult_sl"] * atr
            tps = self._get_tp_levels(ctx)
            conf = 0.6
            
            if conf < self.params["min_conf"]:
                return None
                
            return {
                "strategy": self.name,
                "side": "SHORT",
                "confidence": conf,
                "entry": entry,
                "stop": sl,
                "targets": tps or [entry - 4*tick],
                "reason": "Absorption acheteuse sur PUT wall proche, reversion",
                "metadata": {"wall": wall, "absorption": absorption}
            }
            
        return None
