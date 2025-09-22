#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MenthorQDecisionEngine - Moteur de décision MenthorQ intégré
Version finale avec gates sélectifs et scoring complet
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple

@dataclass
class MQParams:
    tick_size: float = 0.25

    # ---- Proximité MenthorQ ----
    prox_buckets: Tuple[int, int, int, int, int] = (2, 4, 8, 16, 32)
    prox_scores:  Tuple[float, float, float, float, float] = (1.0, 0.7, 0.4, 0.1, 0.05)

    # ---- Weights fusion ----
    w_mq: float = 0.55
    w_of: float = 0.30
    w_ctx: float = 0.15

    # ---- Seuils de décision ----
    th_extreme: float = 0.90
    th_strong:  float = 0.75
    th_moder:   float = 0.60
    th_weak:    float = 0.45

    # ---- Bonuses (alerts unifier) ----
    confluence_bonus_max: float = 0.15
    cluster_bonus: float = 0.05
    cluster_strong_bonus: float = 0.10

    # ==== GATES BLOQUANTS (SÉLECTIFS) ====
    # MIA gate (strict) : longs si ≥ +0.20, shorts si ≤ −0.20
    mia_long_thr: float = 0.20
    mia_short_thr: float = -0.20
    
    # Leadership/correlation (PAS DE VETO - juste avertissement)
    corr_avoid_abs: float = 0.80       # |cc| > 0.8 → éviter contre-tendance

    # OrderFlow gate: confirmations minimales requises (adaptatif selon VIX)
    of_min_conf_by_band: Dict[str, int] = None  # Adaptatif selon VIX

    # ==== Adaptation VIX ====
    wick_tol_by_band: Dict[str, int] = None
    buffers_by_band: Dict[str, Dict[str, int]] = None
    vix_mult: Dict[str, float] = None

    # ==== Stops/TP (E/U/L) ====
    unified_stop_ticks: int = 7       # stop "unifié" (ancienne logique)
    entry_offset_ticks: int = 4       # entrée à ±4 ticks du niveau
    rr_default: float = 1.2

    def __post_init__(self):
        if self.wick_tol_by_band is None:
            self.wick_tol_by_band = {"LOW":3, "MID":5, "HIGH":7, "EXTREME":7}
        if self.buffers_by_band is None:
            self.buffers_by_band = {
                "LOW":     {"vwap":1, "profile":1},
                "MID":     {"vwap":2, "profile":2},
                "HIGH":    {"vwap":3, "profile":3},
                "EXTREME": {"vwap":4, "profile":4},
            }
        if self.vix_mult is None:
            self.vix_mult = {"LOW":1.05, "MID":1.00, "HIGH":0.90, "EXTREME":0.85}
        if self.of_min_conf_by_band is None:
            self.of_min_conf_by_band = {"LOW":2, "MID":2, "HIGH":3, "EXTREME":3}

class MenthorQDecisionEngine:
    def __init__(self, params: MQParams = MQParams()):
        self.p = params

    # ---------- helpers ----------
    def _get_price(self, row: Dict[str, Any]) -> Optional[float]:
        bd = row.get("basedata") or {}
        tr = row.get("trade") or {}
        qt = row.get("quote") or {}
        price = bd.get("c") or tr.get("px")
        if price is None and ("bid" in qt and "ask" in qt):
            price = 0.5 * (qt["bid"] + qt["ask"])
        return float(price) if price is not None else None

    def _abs_ticks(self, a: float, b: float) -> float:
        return abs(a - b) / self.p.tick_size if self.p.tick_size > 0 else abs(a - b)

    def _bucket_score(self, dt_ticks: float) -> float:
        for thr, sc in zip(self.p.prox_buckets, self.p.prox_scores):
            if dt_ticks <= thr:
                return sc
        return 0.0

    def _level_weight(self, level_type: str) -> float:
        lt = (level_type or "").lower()
        if "gamma_wall" in lt or "0dte" in lt:
            return 0.25 if "gamma_wall" in lt else 0.20
        if "gex" in lt:   return 0.08
        if "blind" in lt: return 0.12
        if "hvl" in lt:   return 0.12
        if "call resistance" in lt or "put support" in lt: return 0.15
        if "gamma" in lt: return 0.10
        return 0.08

    # ---------- MenthorQ proximity ----------
    def _menthorq_proximity_score(self, levels: List[Dict[str, Any]], price: float) -> float:
        if not levels:
            return 0.0
        acc = 0.0
        for lv in levels:
            p = lv.get("price"); lt = lv.get("level_type","")
            if p is None: continue
            dt = self._abs_ticks(price, float(p))
            sc = self._bucket_score(dt)
            if sc <= 0.0: continue
            w = self._level_weight(lt)
            acc += w * sc
        # soft normalize
        base = max(0.0, min(1.0, acc/2.0))
        return base

    # ---------- OrderFlow score (and gate) ----------
    def _orderflow_score_and_gate(self, row: Dict[str,Any], vix_band: str = "MID") -> Tuple[float, bool, int]:
        of = row.get("orderflow") or row.get("nbcv") or {}
        # Heuristique simple: compte confirmations si dispos
        conf = 0
        if of.get("delta_burst"): conf += 1
        if of.get("delta_flip"):  conf += 1
        si = ((of.get("stacked_imbalance") or {}).get("ask_rows",0) > 0) or ((of.get("stacked_imbalance") or {}).get("bid_rows",0) > 0)
        if si: conf += 1
        ab = ((of.get("absorption") or {}).get("bid",False)) or ((of.get("absorption") or {}).get("ask",False))
        if ab: conf += 1

        # score: delta normalisé si fourni, sinon neutre 0.5
        score = 0.5
        delta = of.get("delta") or of.get("cum_delta")
        if isinstance(delta,(int,float)):
            dnorm = max(-1.0, min(1.0, float(delta)))
            score = 0.5 + 0.3 * dnorm

        # ✅ NOUVEAU - Gate adaptatif selon VIX
        min_conf_required = self.p.of_min_conf_by_band.get(vix_band, 2)
        gate_ok = (conf >= min_conf_required)
        return max(0.0,min(1.0,score)), gate_ok, conf

    # ---------- VIX regime ----------
    def _vix_band(self, vix_value: Optional[float]) -> str:
        if vix_value is None: return "MID"
        v = float(vix_value)
        if v < 15: return "LOW"
        if v < 22: return "MID"
        if v < 35: return "HIGH"
        return "EXTREME"

    # ---------- Gates: MIA (BLOQUANT) & Leadership (NON-BLOQUANT) ----------
    def _gate_mia(self, mia: Optional[float], side: Optional[str]) -> Tuple[bool,str]:
        if mia is None or side is None:
            return True,"no_mia_or_side"
        if side=="long" and mia < self.p.mia_long_thr:
            return False,f"mia_long {mia:.2f}<{self.p.mia_long_thr:.2f}"
        if side=="short" and mia > self.p.mia_short_thr:
            return False,f"mia_short {mia:.2f}>{self.p.mia_short_thr:.2f}"
        return True,"ok"

    def _gate_leadership(self, cc: Optional[float], ls: Optional[float], side: Optional[str]) -> Tuple[bool,str]:
        # ✅ PAS DE VETO BLOQUANT - Juste une vérification
        if side is None:
            return True,"no_side"
        
        # Vérification corrélation (avertissement, pas de blocage)
        if cc is not None and abs(cc) > self.p.corr_avoid_abs:
            # Éviter trades contre-tendance quand marchés très synchrones
            # Mais pas de blocage total - MenthorQ peut anticiper
            pass
        
        # ✅ TOUJOURS OK - Pas de veto leadership
        return True,"ok"

    # ---------- Structure buffers (VWAP/VP) ----------
    def _structure_penalty(self, row: Dict[str,Any], price: float, band: str) -> float:
        # pénalise si trop proche de VWAP/VAL/VAH/VPOC (évite d'entrer "dans l'aimant")
        buf = self.p.buffers_by_band.get(band, {"vwap":1,"profile":1})
        tick = self.p.tick_size
        penalty = 0.0
        vwap = ((row.get("vwap") or {}).get("v"))
        vva  = row.get("vva") or {}
        for ref,thr in (("vwap",buf["vwap"]),):
            if vwap is not None and self._abs_ticks(price, float(vwap)) <= thr:
                penalty -= 0.15
        for key in ("vpoc","val","vah"):
            lvl = vva.get(key)
            if lvl is not None and self._abs_ticks(price, float(lvl)) <= buf["profile"]:
                penalty -= 0.15
        return penalty

    # ---------- Wick tolerance (breakout vrai) ----------
    def _true_breakout(self, edge_price: float, ohlc: Dict[str,float], direction: str, band: str) -> bool:
        # direction: "up" (cassure haut) / "down" (cassure bas)
        tol_ticks = self.p.wick_tol_by_band.get(band, 5)
        t = self.p.tick_size
        o = float(ohlc.get("o", ohlc.get("open",0.0)))
        h = float(ohlc.get("h", ohlc.get("high",0.0)))
        l = float(ohlc.get("l", ohlc.get("low",0.0)))
        c = float(ohlc.get("c", ohlc.get("close",0.0)))
        if direction=="up":
            wick_below = max(0, int(round((edge_price - l)/t)))
            return (c >= edge_price + tol_ticks*t) and (wick_below <= tol_ticks)
        else:
            wick_above = max(0, int(round((h - edge_price)/t)))
            return (c <= edge_price - tol_ticks*t) and (wick_above <= tol_ticks)

    # ---------- E/U/L précis ----------
    def _eul_from_level(self, level_price: float, side: str) -> Dict[str,float]:
        t = self.p.tick_size
        off = self.p.entry_offset_ticks * t
        stop_ticks = self.p.unified_stop_ticks * t
        if side=="long":
            entry = level_price + off
            stop  = level_price - stop_ticks
            tp1   = entry + self.p.rr_default * (entry - stop)
        else:
            entry = level_price - off
            stop  = level_price + stop_ticks
            tp1   = entry - self.p.rr_default * (stop - entry)
        return {"entry":entry,"stop":stop,"tp1":tp1}

    # ---------- Label ----------
    def _label(self, conf: float) -> str:
        if conf >= self.p.th_extreme: return "Extreme"
        if conf >= self.p.th_strong:  return "Strong"
        if conf >= self.p.th_moder:   return "Moderate"
        if conf >= self.p.th_weak:    return "Weak"
        return "None"

    # ---------- Décision exécution ----------
    def _decide_execution(self, price: float, alerts: Dict[str,Any], band: str, of_gate_ok: bool) -> Dict[str,Any]:
        summary = (alerts or {}).get("summary") or {}
        nc = summary.get("nearest_cluster") or {}
        signals = summary.get("signals") or {}
        if not nc:
            return {"action":"flat","reason":"no_cluster"}

        status = nc.get("status")
        zmin = float(nc.get("zone_min", price))
        zmax = float(nc.get("zone_max", price))
        center = float(nc.get("center", (zmin+zmax)/2.0))
        def closer_to_top(px): return abs(px - zmax) <= abs(px - zmin)

        # Fades (inside) EXIGENT l'OrderFlow gate OK
        if status=="inside" and signals.get("cluster_confluence", False) and of_gate_ok:
            side = "short" if closer_to_top(price) else "long"
            level = zmax if side=="short" else zmin
            eul = self._eul_from_level(level, side)
            return {"action": side, **eul, "rationale":"fade_cluster_eul"}

        # Breakout/acceptation (besoin d'une vraie cassure selon wick tolerance)
        ohlc = (alerts.get("ohlc") or {})  # si tu veux lui fournir, sinon on lit basedata
        # fallback OHLC depuis basedata
        if not ohlc:
            # row-based not available here → laissée à la couche appelante si besoin
            pass

        if status == "above" and signals.get("cluster_strong", False):
            # exiger une vraie cassure vers le haut si OHLC dispo
            if ohlc and not self._true_breakout(zmax, ohlc, "up", band):
                return {"action":"flat","reason":"no_true_break_up"}
            side = "long"
            level = zmax
            eul = self._eul_from_level(level, side)
            return {"action": side, **eul, "rationale":"breakout_retest_eul"}

        if status == "below" and signals.get("cluster_strong", False):
            if ohlc and not self._true_breakout(zmin, ohlc, "down", band):
                return {"action":"flat","reason":"no_true_break_dn"}
            side = "short"
            level = zmin
            eul = self._eul_from_level(level, side)
            return {"action": side, **eul, "rationale":"breakout_retest_eul"}

        return {"action":"flat","reason":"no_pattern"}

    # ---------- Public ----------
    def process_unified_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        price = self._get_price(row)
        levels = row.get("menthorq_levels") or []
        alerts = row.get("alerts") or {}
        if price is None or not levels:
            return {"action":"flat","reason":"no_price_or_levels"}

        # Inputs contextuels
        corr = (row.get("correlation") or {}).get("cc")
        vix_value = (row.get("vix") or {}).get("value")
        band = self._vix_band(vix_value)

        # Scores de base
        mq_score = self._menthorq_proximity_score(levels, price)
        of_score, of_gate_ok, of_conf_ct = self._orderflow_score_and_gate(row, band)  # ✅ Passer VIX band
        ctx_penalty = self._structure_penalty(row, price, band)  # peut être négatif
        ctx_score = max(0.0, min(1.0, 0.5 + ctx_penalty))

        # Bonuses (alerts)
        bonus = 0.0
        if alerts.get("confluence_strength", 0.0) >= 0.7:
            bonus += min(self.p.confluence_bonus_max, 0.1 + 0.05*(alerts["confluence_strength"]>=0.9))
        summary = alerts.get("summary") or {}
        signals = summary.get("signals") or {}
        if signals.get("cluster_confluence"): bonus += self.p.cluster_bonus
        if signals.get("cluster_strong"):      bonus += self.p.cluster_strong_bonus

        # Fusion + adaptation VIX
        conf_raw = (self.p.w_mq * mq_score) + (self.p.w_of * of_score) + (self.p.w_ctx * ctx_score) + bonus
        confidence = max(0.0, min(1.0, conf_raw * self.p.vix_mult.get(band,1.0)))
        label = self._label(confidence)

        # Choix côté provisoire (pour gates MIA/Leadership)
        side_hint = None
        if summary.get("nearest_cluster"):
            status = summary["nearest_cluster"].get("status")
            if status=="inside":
                side_hint = "short" if abs(price - summary["nearest_cluster"]["zone_max"]) <= abs(price - summary["nearest_cluster"]["zone_min"]) else "long"
            elif status=="above": side_hint = "long"
            elif status=="below": side_hint = "short"

        # Gates BLOQUANTS (SÉLECTIFS)
        mia_val = (row.get("mia") or {}).get("score") if isinstance(row.get("mia"), dict) else row.get("mia")
        mia_ok, mia_reason = self._gate_mia(mia_val, side_hint)
        if not mia_ok: return {"action":"flat","reason":f"gate_mia:{mia_reason}"}

        # ✅ Leadership gate (NON-BLOQUANT)
        ls_val = (row.get("leadership") or {}).get("ls")
        lead_ok, lead_reason = self._gate_leadership(corr, ls_val, side_hint)
        # ✅ TOUJOURS OK - Pas de blocage leadership

        if not of_gate_ok:
            min_conf_required = self.p.of_min_conf_by_band.get(band, 2)
            return {"action":"flat","reason":f"gate_orderflow_conf<{min_conf_required} ({of_conf_ct})"}

        # Exécution (E/U/L précis) via cluster & VIX/wick tolerance
        plan = self._decide_execution(price, alerts, band, of_gate_ok)
        plan.update({"confidence": round(confidence,3), "label":label, "price":price, "vix_band":band})
        return plan
