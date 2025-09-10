#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - MenthorQ + Orderflow Bundle Strategies
6 stratégies spécialisées basées sur les données MenthorQ et orderflow

Version: Production Ready v1.0
Performance: <1ms par stratégie
Responsabilité: Patterns MenthorQ avancés (0DTE, GEX, HVL, D1, etc.)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple

# Chaque stratégie retourne un dict signal standard, p.ex.:
# {
#   "strategy": <str>, "side": "LONG"|"SHORT", "confidence": float,
#   "entry": float, "stop": float, "targets": [float, ...],
#   "reason": <str>, "metadata": {...}
# }
# Si les données requises manquent, la stratégie retourne None (tolérante).


# ========= 1) 0DTE_WALL_SWEEP_REVERSAL =========
@dataclass
class ZeroDTEWallSweepReversal:
    name: str = "zero_dte_wall_sweep_reversal"
    requires: tuple = ("menthorq", "orderflow", "price")
    params: dict = None

    def __post_init__(self):
        self.params = self.params or {
            "max_dist_ticks": 8,
            "min_wick_ticks": 6,
            "atr_mult_sl": 1.0,
            "min_conf": 0.64
        }

    def should_run(self, ctx): 
        return "menthorq" in ctx and "orderflow" in ctx and "price" in ctx

    def generate(self, ctx):
        if not self.should_run(ctx):
            return None
        m = ctx["menthorq"]; of = ctx["orderflow"]; price = ctx["price"]["last"]
        walls = m.get("zero_dte", {})  # {"call": x, "put": x, "gamma_wall": x}
        if not walls:
            return None

        wick = ctx.get("basedata", {}).get("last_wick_ticks", 0)
        if wick < self.params["min_wick_ticks"] or not of.get("delta_flip", False):
            return None

        # mur 0DTE le plus proche
        candidates = [(k, v) for k, v in walls.items() if isinstance(v, (int, float))]
        if not candidates:
            return None
        wall_name, wall_price = min(candidates, key=lambda kv: abs(price - kv[1]))

        tick = ctx.get("tick_size", 0.25)
        atr = max(ctx.get("atr", 4*tick), 2*tick)
        dist_ticks = abs(price - wall_price) / max(tick, 1e-9)
        if dist_ticks > self.params["max_dist_ticks"]:
            return None

        absorption = of.get("absorption")
        if not absorption or "side" not in absorption:
            return None

        # balayage au-dessus d'un CALL 0DTE absorbé → SHORT ; sous un PUT 0DTE absorbé → LONG
        if wall_name == "call" and absorption["side"] == "BUY":
            entry = price
            sl = wall_price + self.params["atr_mult_sl"]*atr
            tps = [entry - 4*tick, entry - 8*tick]
            return {"strategy": self.name, "side": "SHORT", "confidence": 0.66,
                    "entry": entry, "stop": sl, "targets": tps,
                    "reason": f"Sweep + absorption BUY near 0DTE CALL ({wall_price})",
                    "metadata": {"wall": wall_name, "wall_price": wall_price, "wick": wick}}

        if wall_name == "put" and absorption["side"] == "SELL":
            entry = price
            sl = wall_price - self.params["atr_mult_sl"]*atr
            tps = [entry + 4*tick, entry + 8*tick]
            return {"strategy": self.name, "side": "LONG", "confidence": 0.66,
                    "entry": entry, "stop": sl, "targets": tps,
                    "reason": f"Sweep + absorption SELL near 0DTE PUT ({wall_price})",
                    "metadata": {"wall": wall_name, "wall_price": wall_price, "wick": wick}}
        return None


# ========= 2) GAMMA_WALL_BREAK_AND_GO =========
@dataclass
class GammaWallBreakAndGo:
    name: str = "gamma_wall_break_and_go"
    requires: tuple = ("menthorq", "orderflow", "quotes", "price", "vwap")
    params: dict = None

    def __post_init__(self):
        self.params = self.params or {
            "need_flip": True,          # préférer un contexte gamma_flip
            "need_burst_speed": True,   # delta_burst + quotes speed_up
            "atr_mult_sl": 1.0,
            "min_conf": 0.68
        }

    def should_run(self, ctx):
        return all(k in ctx for k in ("menthorq", "orderflow", "quotes", "price"))

    def generate(self, ctx):
        if not self.should_run(ctx):
            return None
        m = ctx["menthorq"]; of = ctx["orderflow"]; q = ctx["quotes"]; price = ctx["price"]["last"]
        gamma_wall = (m.get("zero_dte", {}) or {}).get("gamma_wall") or m.get("gamma_wall_0dte")
        if not gamma_wall:
            return None

        if self.params["need_flip"] and not m.get("gamma_flip", False):
            return None
        if self.params["need_burst_speed"] and not (of.get("delta_burst", False) and q.get("speed_up", False)):
            return None

        vwap = ctx.get("vwap", {}).get("vwap", price)
        tick = ctx.get("tick_size", 0.25)
        atr = max(ctx.get("atr", 4*tick), 2*tick)

        # Up-break
        if price > gamma_wall and price > vwap:
            entry = price
            sl = gamma_wall - self.params["atr_mult_sl"]*atr
            tps = [ctx.get("vwap", {}).get("sd2_up", entry + 6*tick)]
            return {"strategy": self.name, "side": "LONG", "confidence": 0.7,
                    "entry": entry, "stop": sl, "targets": [t for t in tps if t],
                    "reason": f"Break & go au-dessus du gamma wall {gamma_wall}",
                    "metadata": {"gamma_wall": gamma_wall}}

        # Down-break
        if price < gamma_wall and price < vwap:
            entry = price
            sl = gamma_wall + self.params["atr_mult_sl"]*atr
            tps = [ctx.get("vwap", {}).get("sd2_dn", entry - 6*tick)]
            return {"strategy": self.name, "side": "SHORT", "confidence": 0.7,
                    "entry": entry, "stop": sl, "targets": [t for t in tps if t],
                    "reason": f"Break & go en-dessous du gamma wall {gamma_wall}",
                    "metadata": {"gamma_wall": gamma_wall}}
        return None


# ========= 3) HVL_MAGNET_FADE =========
@dataclass
class HVLMagnetFade:
    name: str = "hvl_magnet_fade"
    requires: tuple = ("menthorq", "orderflow", "price", "vwap", "vva")
    params: dict = None

    def __post_init__(self):
        self.params = self.params or {
            "max_dist_ticks": 10,
            "avoid_burst": True,
            "atr_mult_sl": 1.0,
            "min_conf": 0.62
        }

    def should_run(self, ctx):
        return all(k in ctx for k in ("menthorq", "orderflow", "price"))

    def generate(self, ctx):
        m = ctx["menthorq"]; of = ctx["orderflow"]; price = ctx["price"]["last"]
        hvl = m.get("hvl")
        if not hvl:
            return None
        tick = ctx.get("tick_size", 0.25)
        dist_ticks = abs(price - hvl) / max(tick, 1e-9)
        if dist_ticks > self.params["max_dist_ticks"]:
            return None
        if self.params["avoid_burst"] and of.get("delta_burst", False):
            return None

        stacked = of.get("stacked_imbalance", {})
        if stacked and stacked.get("rows", 0) >= 3:
            return None

        atr = max(ctx.get("atr", 4*tick), 2*tick)
        vwap = ctx.get("vwap", {}).get("vwap", price)

        if price > hvl:
            entry = price; sl = hvl + self.params["atr_mult_sl"]*atr
            tps = [hvl, max(vwap, hvl - 4*tick)]
            return {"strategy": self.name, "side": "SHORT", "confidence": 0.63,
                    "entry": entry, "stop": sl, "targets": [t for t in tps if t],
                    "reason": f"Retour vers HVL ({hvl}) après extension haute"}
        if price < hvl:
            entry = price; sl = hvl - self.params["atr_mult_sl"]*atr
            tps = [hvl, min(vwap, hvl + 4*tick)]
            return {"strategy": self.name, "side": "LONG", "confidence": 0.63,
                    "entry": entry, "stop": sl, "targets": [t for t in tps if t],
                    "reason": f"Retour vers HVL ({hvl}) après extension basse"}
        return None


# ========= 4) D1_EXTREME_TRAP =========
@dataclass
class D1ExtremeTrap:
    name: str = "d1_extreme_trap"
    requires: tuple = ("menthorq", "orderflow", "price", "vwap", "vva")
    params: dict = None

    def __post_init__(self):
        self.params = self.params or {
            "atr_mult_sl": 1.0,
            "min_conf": 0.62
        }

    def should_run(self, ctx):
        return all(k in ctx for k in ("menthorq", "orderflow", "price"))

    def generate(self, ctx):
        m = ctx["menthorq"]; of = ctx["orderflow"]; price = ctx["price"]["last"]
        d1max = m.get("d1max"); d1min = m.get("d1min")
        if not (d1max or d1min):
            return None
        if not of.get("cvd_divergence", False):
            return None

        tick = ctx.get("tick_size", 0.25)
        atr = max(ctx.get("atr", 4*tick), 2*tick)
        vwap = ctx.get("vwap", {}).get("vwap", price)
        vpoc = ctx.get("vva", {}).get("vpoc")

        if d1max and price > d1max:
            entry = price; sl = d1max + self.params["atr_mult_sl"]*atr
            tps = [x for x in (vwap, vpoc) if x]
            return {"strategy": self.name, "side": "SHORT", "confidence": 0.64,
                    "entry": entry, "stop": sl, "targets": tps or [entry - 6*tick],
                    "reason": f"Divergence CVD sur fake-out > 1d_max ({d1max})",
                    "metadata": {"d1max": d1max, "d1min": d1min}}
        if d1min and price < d1min:
            entry = price; sl = d1min - self.params["atr_mult_sl"]*atr
            tps = [x for x in (vwap, vpoc) if x]
            return {"strategy": self.name, "side": "LONG", "confidence": 0.64,
                    "entry": entry, "stop": sl, "targets": tps or [entry + 6*tick],
                    "reason": f"Divergence CVD sur fake-out < 1d_min ({d1min})",
                    "metadata": {"d1max": d1max, "d1min": d1min}}
        return None


# ========= 5) GEX_CLUSTER_MEAN_REVERT =========
@dataclass
class GexClusterMeanRevert:
    name: str = "gex_cluster_mean_revert"
    requires: tuple = ("menthorq", "orderflow", "price", "vwap", "vva")
    params: dict = None

    def __post_init__(self):
        self.params = self.params or {
            "cluster_span_ticks": 16,  # largeur max du cluster GEX
            "atr_mult_sl": 1.0,
            "min_conf": 0.62
        }

    def should_run(self, ctx):
        return all(k in ctx for k in ("menthorq", "price"))

    def _cluster_bounds(self, gex_levels, tick):
        if not gex_levels:
            return None
        lo, hi = min(gex_levels), max(gex_levels)
        return lo, hi, (hi - lo) / max(tick, 1e-9)

    def generate(self, ctx):
        m = ctx["menthorq"]; price = ctx["price"]["last"]
        gex_levels = m.get("gex_levels") or [
            x for k, x in m.items() if str(k).startswith("gex_") and isinstance(x, (int, float))
        ]
        if not gex_levels:
            return None

        tick = ctx.get("tick_size", 0.25)
        cl = self._cluster_bounds(gex_levels, tick)
        if not cl:
            return None
        lo, hi, span_ticks = cl
        if span_ticks > self.params["cluster_span_ticks"]:
            return None

        center = (lo + hi) / 2.0
        atr = max(ctx.get("atr", 4*tick), 2*tick)

        if price > hi:
            entry = price; sl = hi + self.params["atr_mult_sl"]*atr
            tps = [center]
            return {"strategy": self.name, "side": "SHORT", "confidence": 0.63,
                    "entry": entry, "stop": sl, "targets": tps,
                    "reason": f"Revert vers centre du cluster GEX [{lo:.2f}-{hi:.2f}]",
                    "metadata": {"cluster_lo": lo, "cluster_hi": hi, "center": center}}
        if price < lo:
            entry = price; sl = lo - self.params["atr_mult_sl"]*atr
            tps = [center]
            return {"strategy": self.name, "side": "LONG", "confidence": 0.63,
                    "entry": entry, "stop": sl, "targets": tps,
                    "reason": f"Revert vers centre du cluster GEX [{lo:.2f}-{hi:.2f}]",
                    "metadata": {"cluster_lo": lo, "cluster_hi": hi, "center": center}}
        return None


# ========= 6) CALL_PUT_CHANNEL_ROTATION =========
@dataclass
class CallPutChannelRotation:
    name: str = "call_put_channel_rotation"
    requires: tuple = ("menthorq", "orderflow", "price", "vwap", "vva")
    params: dict = None

    def __post_init__(self):
        self.params = self.params or {
            "min_channel_ticks": 20,   # largeur mini PUT↔CALL
            "avoid_burst": True,
            "atr_mult_sl": 1.0,
            "min_conf": 0.60
        }

    def should_run(self, ctx):
        return all(k in ctx for k in ("menthorq", "price", "vwap"))

    def generate(self, ctx):
        m = ctx["menthorq"]; price = ctx["price"]["last"]; vwap = ctx.get("vwap", {}).get("vwap", price)
        call = (m.get("zero_dte", {}) or {}).get("call") or m.get("call_resistance")
        put  = (m.get("zero_dte", {}) or {}).get("put")  or m.get("put_support")
        if not (call and put):
            return None

        tick = ctx.get("tick_size", 0.25)
        width_ticks = abs(call - put) / max(tick, 1e-9)
        if width_ticks < self.params["min_channel_ticks"]:
            return None

        of = ctx.get("orderflow", {})
        if self.params["avoid_burst"] and of.get("delta_burst", False):
            return None

        atr = max(ctx.get("atr", 4*tick), 2*tick)
        vpoc = ctx.get("vva", {}).get("vpoc") or vwap

        # Proche CALL → short vers centre
        if abs(price - call) / tick <= 6:
            entry = price; sl = call + self.params["atr_mult_sl"]*atr
            tps = [x for x in (vpoc, vwap) if x]
            return {"strategy": self.name, "side": "SHORT", "confidence": 0.61,
                    "entry": entry, "stop": sl, "targets": tps,
                    "reason": f"Rotation canal PUT↔CALL: fade CALL ({call}) → centre",
                    "metadata": {"call": call, "put": put, "channel_width": width_ticks}}

        # Proche PUT → long vers centre
        if abs(price - put) / tick <= 6:
            entry = price; sl = put - self.params["atr_mult_sl"]*atr
            tps = [x for x in (vpoc, vwap) if x]
            return {"strategy": self.name, "side": "LONG", "confidence": 0.61,
                    "entry": entry, "stop": sl, "targets": tps,
                    "reason": f"Rotation canal PUT↔CALL: fade PUT ({put}) → centre",
                    "metadata": {"call": call, "put": put, "channel_width": width_ticks}}

        return None


# ========= FAMILY TAGS FOR DEDUPLICATION =========
FAMILY_TAGS = {
    "zero_dte_wall_sweep_reversal": "REVERSAL",
    "gamma_wall_break_and_go": "BREAKOUT",
    "hvl_magnet_fade": "MEAN_REVERT",
    "d1_extreme_trap": "TRAP",
    "gex_cluster_mean_revert": "MEAN_REVERT",
    "call_put_channel_rotation": "RANGE_ROTATION",
    # Existing strategies
    "dealer_flip_breakout": "BREAKOUT",
    "vwap_band_squeeze_break": "BREAKOUT",
    "liquidity_sweep_reversal": "REVERSAL",
    "gamma_pin_reversion": "REVERSAL",
    "profile_gap_fill": "MEAN_REVERT",
    "cvd_divergence_trap": "TRAP",
    "stacked_imbalance_continuation": "CONTINUATION",
    "iceberg_tracker_follow": "FOLLOW",
    "opening_drive_fail": "REVERSAL",
    "es_nq_lead_lag_mirror": "CORRELATION",
}


def get_family_tag(strategy_name: str) -> str:
    """Retourne le tag de famille pour une stratégie"""
    return FAMILY_TAGS.get(strategy_name, "OTHER")


def deduplicate_by_family(pattern_signals: List[Tuple[float, Dict]]) -> List[Tuple[float, Dict]]:
    """
    Dédoublonne les signaux par famille, gardant le mieux noté de chaque famille
    
    Args:
        pattern_signals: Liste de (score, signal_dict)
        
    Returns:
        Liste dédoublonnée de (score, signal_dict)
    """
    best_per_family = {}
    
    for score, sig in pattern_signals:
        family = get_family_tag(sig["strategy"])
        if family not in best_per_family or score > best_per_family[family][0]:
            best_per_family[family] = (score, sig)
    
    return list(best_per_family.values())


# ========= EXPORT ALL STRATEGIES =========
MENTHORQ_STRATEGIES = [
    ZeroDTEWallSweepReversal(),
    GammaWallBreakAndGo(),
    HVLMagnetFade(),
    D1ExtremeTrap(),
    GexClusterMeanRevert(),
    CallPutChannelRotation(),
]
