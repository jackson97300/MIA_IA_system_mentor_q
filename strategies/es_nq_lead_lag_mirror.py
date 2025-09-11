#!/usr/bin/env python3
"""
Stratégie ES NQ Lead Lag Mirror
Détecte les décorrélations entre ES et NQ et génère des signaux d'alignement
basés sur le leader/lag pattern.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class EsNqLeadLagMirror:
    """
    Stratégie d'alignement basée sur les patterns lead/lag ES-NQ.
    
    Logique:
    - Détecte une décorrélation notable entre ES et NQ
    - Identifie le leader (ES ou NQ)
    - Génère un signal d'alignement dans la direction du leader
    """
    name: str = "es_nq_lead_lag_mirror"
    requires: tuple = ("correlation", "orderflow", "vwap", "price", "symbol")
    params: dict = None

    def __post_init__(self):
        self.params = self.params or {
            "corr_thresh": 0.35,           # Seuil de décorrélation (0.35 = 65% corrélation)
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
        return all(k in ctx for k in ("correlation", "orderflow", "vwap", "price", "symbol"))

    def generate(self, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Génère un signal d'alignement basé sur le lead/lag ES-NQ.
        
        Args:
            ctx: Contexte de trading
            
        Returns:
            Signal de trading ou None
        """
        if not self.should_run(ctx):
            return None
            
        corr = ctx["correlation"].get("es_nq", 1.0)
        leader = ctx["correlation"].get("leader")
        symbol = ctx["symbol"]
        
        # Vérifier la décorrélation
        if abs(corr) > (1 - self.params["corr_thresh"]):  # Besoin décorrélation notable
            return None
        if leader not in ("ES", "NQ"):
            return None

        price = ctx["price"]["last"]
        vwap = ctx["vwap"].get("vwap", price)
        of = ctx["orderflow"]
        tick = ctx.get("tick_size", 0.25)
        atr = max(ctx.get("atr", 4*tick), 2*tick)

        # Signal LONG: NQ leader up & on trade NQ
        if leader == "NQ" and symbol == "NQ" and price > vwap and of.get("delta_burst", False):
            entry = price
            sl = vwap - self.params["atr_mult_sl"]*atr
            tps = [entry + 6*tick, entry + 10*tick]
            
            return {
                "strategy": self.name,
                "side": "LONG",
                "confidence": 0.64,
                "entry": entry,
                "stop": sl,
                "targets": tps,
                "reason": "NQ leader up, décorrélation → alignement haussier",
                "metadata": {"leader": leader, "correlation": corr}
            }
            
        # Signal SHORT: ES leader down & on trade ES
        if leader == "ES" and symbol == "ES" and price < vwap and of.get("delta_burst", False):
            entry = price
            sl = vwap + self.params["atr_mult_sl"]*atr
            tps = [entry - 6*tick, entry - 10*tick]
            
            return {
                "strategy": self.name,
                "side": "SHORT",
                "confidence": 0.64,
                "entry": entry,
                "stop": sl,
                "targets": tps,
                "reason": "ES leader down, décorrélation → alignement baissier",
                "metadata": {"leader": leader, "correlation": corr}
            }
            
        return None

