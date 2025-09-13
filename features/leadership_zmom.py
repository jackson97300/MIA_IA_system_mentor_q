#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leadership Z-Momentum – Module unifié (remplace analyzer/engine/filter/validator)
===============================================================================
- LS = leadership NQ vs ES via Z-momentum vol-ajusté (3s/30s/5m), sans barres dédiées
- β dynamique (σ_NQ / σ_ES) borné
- Corrélation roulante (fiabilité)
- Gate & bonus (VIX + contratrend) + soft rules inspirées de tes filtres
- Export JSONL, ou usage live (update_from_unified_rows → snapshot/gates)

Ce module remplace:
  - leadership_analyzer.py (orchestration + confluence hook)
  - leadership_engine.py (fenêtres multi-TF & persistance)
  - leadership_filter_enhanced.py (blocage contra-trend, VIX)
  - leadership_validator.py (corr NaN-safe, risk multiplier)

© MIA_IA_SYSTEM
"""

from __future__ import annotations
import json, gzip, math, argparse, sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# Logger robuste (compat core.logger si dispo)
try:
    from core.logger import get_logger  # type: ignore
    logger = get_logger(__name__)
except Exception:
    import logging
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("features.leadership_zmom")

# ---------- Utilitaires I/O ----------
def _open_any(path: str):
    return gzip.open(path, "rt", encoding="utf-8") if path.endswith(".gz") else open(path, "r", encoding="utf-8")

def _write_any(path: str):
    return gzip.open(path, "wt", encoding="utf-8") if path.endswith(".gz") else open(path, "w", encoding="utf-8")

def _mid_price(row: Dict[str, Any]) -> Optional[float]:
    if not row: return None
    bd = row.get("basedata") or {}
    if "close" in bd and bd["close"] not in (None, 0): return float(bd["close"])
    qt = row.get("quote") or {}
    if "mid"   in qt and qt["mid"]   not in (None, 0): return float(qt["mid"])
    tr = row.get("trade") or {}
    if "price" in tr and tr["price"] not in (None, 0): return float(tr["price"])
    return None

def _ts_sec(row: Dict[str, Any]) -> Optional[float]:
    if not row: return None
    t = row.get("t") or row.get("timestamp") or row.get("time")
    if t is None: return None
    try: return float(t)
    except Exception: return None

# ---------- Cœur Z-momentum multi-horizons ----------
class _ZState:
    """Garde en mémoire les derniers prix (tick/time-driven) et calcule retours r^h & σ EMA."""
    def __init__(self, horizon_s: int, vol_win_n: int, ema_alpha: float = 0.2, clip: float = 3.0):
        self.h = float(horizon_s)
        self.win = int(vol_win_n)
        self.a = float(ema_alpha)
        self.clip = float(clip)
        self.prices: deque[Tuple[float, float]] = deque()  # (t_sec, price)
        self.rets: deque[float] = deque()
        self.var_ema: Optional[float] = None

    def update(self, t: float, p: float) -> None:
        self.prices.append((t, p))
        while self.prices and (t - self.prices[0][0]) > self.h:
            self.prices.popleft()
        if self.prices and (t - self.prices[0][0]) >= self.h:
            p_old = self.prices[0][1]
            r = math.log(p) - math.log(p_old) if (p and p_old) else 0.0
            self.rets.append(r)
            if len(self.rets) > self.win: self.rets.popleft()
            val = r * r
            self.var_ema = (self.a * val) + ((1 - self.a) * (self.var_ema if self.var_ema is not None else val))

    def z(self, eps: float = 1e-9) -> float:
        if not self.rets or self.var_ema is None: return 0.0
        sigma = math.sqrt(max(self.var_ema, eps))
        if sigma < 1e-12: return 0.0
        z = self.rets[-1] / sigma
        return max(-self.clip, min(self.clip, z))

class _RollCorr:
    """Corrélation roulante des retours 30s ES/NQ (qualité de leadership)."""
    def __init__(self, max_points: int = 300):
        self.es: deque[float] = deque()
        self.nq: deque[float] = deque()
        self.max_points = int(max_points)

    def update(self, r_es_30s: float, r_nq_30s: float) -> None:
        self.es.append(r_es_30s); self.nq.append(r_nq_30s)
        while len(self.es) > self.max_points:
            self.es.popleft(); self.nq.popleft()

    def corr(self) -> Optional[float]:
        n = len(self.es)
        if n < 10: return None
        mean_es = sum(self.es)/n
        mean_nq = sum(self.nq)/n
        cov = sum((self.es[i]-mean_es)*(self.nq[i]-mean_nq) for i in range(n))
        var_es = sum((self.es[i]-mean_es)**2 for i in range(n))
        var_nq = sum((self.nq[i]-mean_nq)**2 for i in range(n))
        if var_es <= 1e-18 or var_nq <= 1e-18: return 0.0
        c = cov / math.sqrt(var_es * var_nq)
        return max(-1.0, min(1.0, c))

@dataclass
class LSSnapshot:
    t: float
    ls: float
    beta: float
    z_es_3s: float; z_es_30s: float; z_es_5m: float
    z_nq_3s: float; z_nq_30s: float; z_nq_5m: float
    roll_corr_30s: Optional[float]

class LeadershipZMom:
    """
    Module unifié : calcule LS (NQ vs ES) et fournit gates/bonus contratrend avec VIX.
    Inspiré de tes modules Engine/Filter/Validator, consolidé.
    """
    def __init__(self,
                 horizons=(3, 30, 300),
                 alpha: float = 0.2,
                 corr_win_points: int = 300,
                 max_delay_ms: int = 200,
                 clip_z: float = 3.0):
        h3, h30, h300 = [int(x) for x in horizons]
        self.es3  = _ZState(h3,   120, ema_alpha=alpha, clip=clip_z)
        self.es30 = _ZState(h30,  600, ema_alpha=alpha, clip=clip_z)
        self.es300= _ZState(h300, 3600,ema_alpha=alpha, clip=clip_z)
        self.nq3  = _ZState(h3,   120, ema_alpha=alpha, clip=clip_z)
        self.nq30 = _ZState(h30,  600, ema_alpha=alpha, clip=clip_z)
        self.nq300= _ZState(h300, 3600,ema_alpha=alpha, clip=clip_z)

        self.beta: float = 1.3     # σ_NQ/σ_ES borne [0.8,1.6]
        self.LS_ema: Optional[float] = None
        self.alpha = float(alpha)  # lissage LS
        self.max_delay = float(max_delay_ms) / 1000.0
        self.corr = _RollCorr(corr_win_points)

    # ---- update & compute ----
    def update_prices(self, t: float, p_es: float, p_nq: float) -> LSSnapshot:
        # update Z-states
        for st, p in ((self.es3,p_es),(self.es30,p_es),(self.es300,p_es),
                      (self.nq3,p_nq),(self.nq30,p_nq),(self.nq300,p_nq)):
            st.update(t, p)

        # beta sur vol lente (5m)
        sig_es = math.sqrt(self.es300.var_ema) if self.es300.var_ema else None
        sig_nq = math.sqrt(self.nq300.var_ema) if self.nq300.var_ema else None
        if sig_es and sig_nq and sig_es > 1e-12:
            self.beta = max(0.8, min(1.6, sig_nq/sig_es))

        # z-scores & LS
        z_es_3,  z_nq_3   = self.es3.z(),  self.nq3.z()
        z_es_30, z_nq_30  = self.es30.z(), self.nq30.z()
        z_es_300,z_nq_300 = self.es300.z(),self.nq300.z()
        ls3   = z_nq_3   - self.beta*z_es_3
        ls30  = z_nq_30  - self.beta*z_es_30
        ls300 = z_nq_300 - self.beta*z_es_300
        LS    = 0.6*ls3 + 0.3*ls30 + 0.1*ls300
        self.LS_ema = (self.alpha*LS + (1-self.alpha)*(self.LS_ema if self.LS_ema is not None else LS))
        self.LS_ema = max(-2.0, min(2.0, self.LS_ema))

        # corr (ret 30s bruts)
        r_es_30 = self.es30.rets[-1] if self.es30.rets else 0.0
        r_nq_30 = self.nq30.rets[-1] if self.nq30.rets else 0.0
        self.corr.update(r_es_30, r_nq_30)
        rc = self.corr.corr()

        snap = LSSnapshot(
            t=float(round(t, 3)),
            ls=float(round(self.LS_ema, 4)),
            beta=float(round(self.beta, 4)),
            z_es_3s=round(z_es_3,3),   z_es_30s=round(z_es_30,3),   z_es_5m=round(z_es_300,3),
            z_nq_3s=round(z_nq_3,3),   z_nq_30s=round(z_nq_30,3),   z_nq_5m=round(z_nq_300,3),
            roll_corr_30s=None if rc is None else float(round(rc,4))
        )
        return snap

    def update_from_unified_rows(self, row_es: Dict[str,Any], row_nq: Dict[str,Any]) -> Optional[LSSnapshot]:
        if not row_es or not row_nq: return None
        te, tn = _ts_sec(row_es), _ts_sec(row_nq)
        if te is None or tn is None: return None
        if abs(te-tn) > self.max_delay:
            # décalage trop grand : ignorer ce pair
            return None
        p_es, p_nq = _mid_price(row_es), _mid_price(row_nq)
        if p_es is None or p_nq is None: return None
        t = max(te, tn)
        return self.update_prices(t, p_es, p_nq)

    # ---- Règles VIX & gates ----
    @staticmethod
    def vix_regime(vix: Optional[float]) -> str:
        if vix is None: return "MID"
        if vix >= 35: return "EXTREME"
        if vix >= 22: return "HIGH"
        if vix < 15:  return "LOW"
        return "MID"

    def gate_for_es(self, side: str, vix_value: Optional[float], roll_corr_floor: float = 0.30) -> Dict[str,Any]:
        """
        Gate de leadership pour ES avec veto/bonus basé sur VIX et corrélation
        
        Args:
            side: 'LONG' ou 'SHORT' (côté proposé par MenthorQ/GEX)
            vix_value: Valeur VIX actuelle
            roll_corr_floor: Seuil minimum de corrélation (défaut: 0.30)
            
        Returns:
            Dict: allow(bool), hard_block(bool), bonus(float), extra_of(int), reason(str)
            
        LOGIQUE LS (Leadership Score):
        - LS > 0 : NQ > ES (pro-risk) → FAVORISE LONG ES
        - LS < 0 : NQ < ES (risk-off) → FAVORISE SHORT ES
        - LS ≈ 0 : NQ ≈ ES (neutre) → Pas de biais directionnel
        
        VETO/BONUS:
        - Veto si LS très fort contre le signal (contratrend)
        - Bonus si LS aligné avec le signal (trend-following)
        - Adaptation selon régime VIX (LOW/MID/HIGH/EXTREME)
        """
        ls = self.LS_ema if self.LS_ema is not None else 0.0
        rc = self.corr.corr()
        regime = self.vix_regime(vix_value)

        if rc is not None and rc < roll_corr_floor:
            return {"allow": True, "hard_block": False, "bonus": 1.00, "extra_of": 0,
                    "reason": f"leadership ignoré (corr {rc:.2f} < {roll_corr_floor})", "regime": regime, "ls": ls}

        hard  = 1.25 if regime=="HIGH" or regime=="EXTREME" else 1.00
        thr   = 0.75 if regime=="HIGH" or regime=="EXTREME" else 0.50
        allow_long  = ls >= 0.0
        allow_short = ls <= 0.0

        hard_block = (abs(ls) >= hard) and ((side=="LONG" and ls<0) or (side=="SHORT" and ls>0))
        allow = (side=="LONG" and allow_long) or (side=="SHORT" and allow_short)
        bonus = 1.05 if abs(ls) >= thr else 1.00
        extra = 1 if (regime in ("HIGH","EXTREME") and abs(ls) < thr) else 0

        return {"allow": bool(allow and not hard_block),
                "hard_block": bool(hard_block),
                "bonus": float(bonus),
                "extra_of": int(extra),
                "reason": f"LS={ls:.2f} regime={regime} (thr={thr}, hard={hard})",
                "regime": regime,
                "ls": float(ls),
                "roll_corr_30s": None if rc is None else float(rc)}

# ---------- Exporter (batch) ----------
def export_ls_jsonl(es_path: str, nq_path: str, out_path: str,
                    horizons=(3,30,300), alpha=0.2, corr_win=300, max_delay_ms=200) -> None:
    mod = LeadershipZMom(horizons=horizons, alpha=alpha,
                         corr_win_points=corr_win, max_delay_ms=max_delay_ms)
    it_es = _open_any(es_path); it_nq = _open_any(nq_path)
    try:
        es_line = it_es.readline(); nq_line = it_nq.readline()
        with _write_any(out_path) as out:
            while es_line and nq_line:
                try:
                    row_es = json.loads(es_line); row_nq = json.loads(nq_line)
                except Exception:
                    es_line = it_es.readline(); nq_line = it_nq.readline(); continue
                snap = mod.update_from_unified_rows(row_es, row_nq)
                if snap:
                    out.write(json.dumps({
                        "t": snap.t, "ls": snap.ls, "beta": snap.beta,
                        "z_es": {"3s": snap.z_es_3s, "30s": snap.z_es_30s, "5m": snap.z_es_5m},
                        "z_nq": {"3s": snap.z_nq_3s, "30s": snap.z_nq_30s, "5m": snap.z_nq_5m},
                        "roll_corr_30s": snap.roll_corr_30s
                    }) + "\n")
                es_line = it_es.readline(); nq_line = it_nq.readline()
    finally:
        it_es.close(); it_nq.close()

# ---------- CLI ----------
def _main():
    ap = argparse.ArgumentParser(description="Leadership Z-Momentum unifié")
    sub = ap.add_subparsers(dest="cmd")

    s_exp = sub.add_parser("export", help="exporte leadership LS en JSONL(.gz)")
    s_exp.add_argument("--es", required=True)
    s_exp.add_argument("--nq", required=True)
    s_exp.add_argument("--out", required=True)
    s_exp.add_argument("--horizons", default="3,30,300")
    s_exp.add_argument("--alpha", type=float, default=0.2)
    s_exp.add_argument("--corr_win", type=int, default=300)
    s_exp.add_argument("--max_delay_ms", type=int, default=200)

    s_gate = sub.add_parser("gate", help="calcule gate/bonus pour un côté proposé (ES)")
    s_gate.add_argument("--es", required=True)
    s_gate.add_argument("--nq", required=True)
    s_gate.add_argument("--side", choices=["LONG","SHORT"], required=True)
    s_gate.add_argument("--vix", type=float, default=None)
    s_gate.add_argument("--horizons", default="3,30,300")
    s_gate.add_argument("--alpha", type=float, default=0.2)
    s_gate.add_argument("--corr_win", type=int, default=300)
    s_gate.add_argument("--max_delay_ms", type=int, default=200)

    args = ap.parse_args()
    if args.cmd == "export":
        h = tuple(int(x) for x in args.horizons.split(","))
        export_ls_jsonl(args.es, args.nq, args.out, h, args.alpha, args.corr_win, args.max_delay_ms)
    elif args.cmd == "gate":
        h = tuple(int(x) for x in args.horizons.split(","))
        mod = LeadershipZMom(horizons=h, alpha=args.alpha,
                             corr_win_points=args.corr_win, max_delay_ms=args.max_delay_ms)
        it_es = _open_any(args.es); it_nq = _open_any(args.nq)
        try:
            es_line = it_es.readline(); nq_line = it_nq.readline()
            gate_info = None; snap = None
            while es_line and nq_line:
                try:
                    row_es = json.loads(es_line); row_nq = json.loads(nq_line)
                except Exception:
                    es_line = it_es.readline(); nq_line = it_nq.readline(); continue
                snap = mod.update_from_unified_rows(row_es, row_nq)
                if snap: gate_info = mod.gate_for_es(args.side, args.vix)
                es_line = it_es.readline(); nq_line = it_nq.readline()
            print(json.dumps({
                "last_snapshot": None if not snap else snap.__dict__,
                "gate": gate_info
            }, ensure_ascii=False))
        finally:
            it_es.close(); it_nq.close()
    else:
        ap.print_help()

if __name__ == "__main__":
    _main()

