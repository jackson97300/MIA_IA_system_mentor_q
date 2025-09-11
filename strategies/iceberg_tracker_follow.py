#!/usr/bin/env python3
"""
Stratégie Iceberg Tracker Follow
Détecte les icebergs (ordres cachés) et génère des signaux de suivi
dans la direction de l'iceberg.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class IcebergTrackerFollow:
    """
    Stratégie de suivi basée sur les icebergs.
    
    Logique:
    - Détecte un iceberg (ordre caché) dans le carnet d'ordres
    - Génère un signal de suivi dans la direction de l'iceberg
    - Place le stop loss au niveau de l'iceberg
    """
    name: str = "iceberg_tracker_follow"
    requires: tuple = ("orderflow", "depth", "price")
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
        return all(k in ctx for k in ("orderflow", "price"))

    def generate(self, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Génère un signal de suivi d'iceberg.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            Signal de trading ou None
        """
        if not self.should_run(ctx):
            return None
            
        of = ctx["orderflow"]
        price = ctx["price"]["last"]
        
        # Vérifier la présence d'un iceberg
        ice = of.get("iceberg")
        if not ice or "side" not in ice:
            return None

        tick = ctx.get("tick_size", 0.25)
        atr = max(ctx.get("atr", 4*tick), 2*tick)
        lvl = ice.get("price", price)

        # Signal LONG: suivre l'iceberg acheteur
        if ice["side"] == "BUY":
            entry = price
            sl = lvl - self.params["atr_mult_sl"]*atr
            tps = [entry + 4*tick, entry + 8*tick]
            
            return {
                "strategy": self.name,
                "side": "LONG",
                "confidence": 0.65,
                "entry": entry,
                "stop": sl,
                "targets": tps,
                "reason": "Suivi d'iceberg acheteur",
                "metadata": {"level": lvl}
            }
            
        # Signal SHORT: suivre l'iceberg vendeur
        if ice["side"] == "SELL":
            entry = price
            sl = lvl + self.params["atr_mult_sl"]*atr
            tps = [entry - 4*tick, entry - 8*tick]
            
            return {
                "strategy": self.name,
                "side": "SHORT",
                "confidence": 0.65,
                "entry": entry,
                "stop": sl,
                "targets": tps,
                "reason": "Suivi d'iceberg vendeur",
                "metadata": {"level": lvl}
            }
            
        return None

