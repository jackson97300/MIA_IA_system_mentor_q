# Auto-generated module: mia_bullish
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Deque, Tuple
from collections import deque
import math

def clip01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x

@dataclass
class _BarCache:
    close: Optional[float] = None
    vwap: Optional[float] = None
    up1: Optional[float] = None
    dn1: Optional[float] = None
    vah: Optional[float] = None
    val: Optional[float] = None
    delta_ratio: Optional[float] = None
    pressure: Optional[int] = None  # -1 / 0 / 1
    cumdelta: Optional[float] = None
    t: Optional[float] = None  # timestamp (Sierra double), optional

class BullishScorer:
    def __init__(self, chart_id: int = 3, use_vix: bool = True):
        self.chart_id = chart_id
        self.use_vix = use_vix
        self.vix_value: Optional[float] = None
        self.cum_hist: Deque[Tuple[int, float]] = deque(maxlen=16)  # (i, cumdelta)
        self.bars: Dict[int, _BarCache] = {}

    def ingest(self, ev: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        ev_type = ev.get("type")
        chart = ev.get("chart") or ev.get("graph")
        if ev_type is None:
            return None
        # vix updates
        if self.use_vix and ev_type in ("vix", "vix_close"):
            last = ev.get("last") or ev.get("close") or ev.get("vix")
            if isinstance(last, (int, float)) and last > 0:
                self.vix_value = float(last)
            return None
        # only chart
        if chart != self.chart_id:
            return None
        i = ev.get("i")
        if i is None:
            return None
        bar = self.bars.get(i) or _BarCache()
        if "t" in ev and bar.t is None:
            try:
                bar.t = float(ev["t"])
            except Exception:
                pass
        if ev_type == "basedata":
            c = ev.get("c")
            if isinstance(c, (int, float)):
                bar.close = float(c)
        elif ev_type == "nbcv_footprint":
            # Fallback: utiliser le close du nbcv_footprint si basedata n'est pas disponible
            if bar.close is None:
                # Essayer de déduire le close du dernier trade ou du mid
                # Pour l'instant, on utilise une valeur par défaut
                pass
        elif ev_type == "vwap":
            v = ev.get("v")
            if isinstance(v, (int, float)):
                bar.vwap = float(v)
            up1 = ev.get("up1")
            dn1 = ev.get("dn1")
            if isinstance(up1, (int, float)):
                bar.up1 = float(up1)
            if isinstance(dn1, (int, float)):
                bar.dn1 = float(dn1)
        elif ev_type == "vva":
            vah = ev.get("vah")
            val = ev.get("val")
            if isinstance(vah, (int, float)):
                bar.vah = float(vah)
            if isinstance(val, (int, float)):
                bar.val = float(val)
        elif ev_type == "nbcv_footprint":
            cd = ev.get("cumulative_delta")
            if isinstance(cd, (int, float)):
                bar.cumdelta = float(cd)
                self._append_cum_hist(int(i), float(cd))
        elif ev_type in ("nbcv_metrics", "nbcv_footprint"):
            dr = ev.get("delta_ratio")
            if isinstance(dr, (int, float)):
                bar.delta_ratio = float(dr)
            bull = int(ev.get("pressure_bullish") == 1)
            bear = int(ev.get("pressure_bearish") == 1)
            bar.pressure = 1 if bull and not bear else (-1 if bear and not bull else 0)
        self.bars[i] = bar
        return self._maybe_compute(i)

    def _append_cum_hist(self, idx: int, cd: float) -> None:
        if len(self.cum_hist) == 0 or idx > self.cum_hist[-1][0]:
            self.cum_hist.append((idx, cd))
        elif idx == self.cum_hist[-1][0]:
            self.cum_hist[-1] = (idx, cd)

    def _cum_slope_score(self) -> float:
        if len(self.cum_hist) < 3:
            return 0.5
        xs = list(range(len(self.cum_hist)))
        ys = [v for _, v in self.cum_hist]
        xm = sum(xs) / len(xs)
        ym = sum(ys) / len(ys)
        num = sum((x - xm) * (y - ym) for x, y in zip(xs, ys))
        den = sum((x - xm) ** 2 for x in xs) or 1.0
        slope = num / den
        norm = abs(ym) * 0.05 + 50.0
        return clip01(slope / norm)

    def _maybe_compute(self, i: int) -> Optional[Dict[str, Any]]:
        bar = self.bars.get(i)
        if not bar:
            return None
        # Utiliser VWAP comme fallback pour close si nécessaire
        close_price = bar.close if bar.close is not None else bar.vwap
        if close_price is None or bar.vwap is None or bar.delta_ratio is None:
            return None
        # 1) Order-Flow
        of_core = 1.0 if bar.pressure == 1 else 0.0
        of_bonus = clip01(((bar.delta_ratio or 0.0) - 0.08) / (0.50 - 0.08))
        OF_score = 0.7 * of_core + 0.3 * of_bonus
        # 2) VWAP position
        if bar.up1 is not None and bar.vwap is not None:
            band = max(1e-9, abs(bar.up1 - bar.vwap))
        else:
            band = max(1e-9, abs(bar.vwap) * 0.002)
        z = (close_price - bar.vwap) / band
        VWAP_score = clip01(0.5 + 0.5 * math.tanh(z))
        # 3) VVA
        if bar.vah is not None and bar.val is not None:
            if close_price > bar.vah:
                VVA_score = 0.9; pos = "above_VAH"
            elif close_price < bar.val:
                VVA_score = 0.2; pos = "below_VAL"
            else:
                VVA_score = 0.6; pos = "inside_VA"
        else:
            VVA_score = 0.5; pos = "no_VA"
        # 4) Cum delta trend
        CD_score = self._cum_slope_score()
        # 5) VIX factor
        if self.use_vix and isinstance(self.vix_value, (int, float)):
            vix = float(self.vix_value)
            if vix <= 12:   vix_factor = 0.95
            elif vix <= 25: vix_factor = 1.00
            elif vix <= 35: vix_factor = 0.95
            else:           vix_factor = 0.85
        else:
            vix_factor = 1.0
        score = (0.35 * OF_score +
                 0.25 * VWAP_score +
                 0.20 * VVA_score +
                 0.20 * CD_score) * vix_factor
        score = round(clip01(score), 3)
        
        # Calcul staleness des données
        import time
        current_time = time.time()
        staleness_ms = None
        staleness_status = "OK"
        
        if bar.t is not None:
            # Convertir timestamp Sierra/Excel vers epoch si nécessaire
            if bar.t > 10000:  # Sierra/Excel days format
                EXCEL_EPOCH_OFFSET_DAYS = 25569
                SECONDS_PER_DAY = 86400.0
                data_timestamp = (bar.t - EXCEL_EPOCH_OFFSET_DAYS) * SECONDS_PER_DAY
            else:
                data_timestamp = bar.t
            
            staleness_ms = (current_time - data_timestamp) * 1000
            
            # Déterminer le statut selon la staleness
            if staleness_ms > 5000:  # > 5 secondes
                staleness_status = "STALE"
            elif staleness_ms > 2100:  # > 2.1 secondes
                staleness_status = "OLD"
            else:
                staleness_status = "OK"
        
        # Logger la staleness si problématique
        try:
            from core.logger import get_logger
            logger = get_logger(__name__)
            
            if staleness_status != "OK":
                logger.warning(f"🕐 MIA Staleness: {staleness_status} - "
                             f"asof={staleness_ms:.1f}ms, score={score}, "
                             f"pressure={bar.pressure}, pos={pos}")
            else:
                logger.debug(f"✅ MIA Fresh: asof={staleness_ms:.1f}ms → {staleness_status}")
                
        except Exception:
            # Fallback silencieux si logger non disponible
            pass
        
        return {
            "t": bar.t,
            "chart": self.chart_id,
            "type": "mia_bullish",
            "i": i,
            "score": score,
            "pressure": bar.pressure,
            "dr": round(bar.delta_ratio, 4) if bar.delta_ratio is not None else None,
            "pos": pos,
            "close": close_price,
            "vwap": bar.vwap,
            "staleness_ms": round(staleness_ms, 1) if staleness_ms is not None else None,
            "staleness_status": staleness_status
        }
    
    def calculate_bullish_score(self, market_data: Dict) -> float:
        """
        Méthode publique pour calculer le score MIA Bullish
        avec logging de staleness intégré
        
        Args:
            market_data: Données de marché (dict avec OHLC, VWAP, etc.)
            
        Returns:
            float: Score MIA Bullish (-1 à +1, bidirectionnel)
        """
        try:
            # Convertir les données en événement pour ingest
            ev = {
                "type": "basedata",
                "chart": self.chart_id,
                "i": market_data.get("bar_index", 1),
                "close": market_data.get("close", 0),
                "t": market_data.get("timestamp")
            }
            
            # Ajouter VWAP si disponible
            if "vwap" in market_data:
                ev.update({
                    "type": "vwap",
                    "value": market_data["vwap"]
                })
            
            # Ajouter VVA si disponible
            if "vva" in market_data:
                vva = market_data["vva"]
                ev.update({
                    "type": "vva",
                    "vah": vva.get("vah"),
                    "val": vva.get("val")
                })
            
            # Ajouter OrderFlow si disponible
            if "nbcv_footprint" in market_data:
                nbcv = market_data["nbcv_footprint"]
                ev.update({
                    "pressure": nbcv.get("pressure", 0),
                    "delta_ratio": nbcv.get("delta_ratio", 0),
                    "cumulative_delta": nbcv.get("cumulative_delta", 0)
                })
            
            # Ingérer les données
            result = self.ingest(ev)
            
            if result and result.get("type") == "mia_bullish":
                score = result.get("score", 0.5)
                staleness_ms = result.get("staleness_ms")
                staleness_status = result.get("staleness_status", "UNKNOWN")
                
                # Logging spécifique pour l'utilisation dans les stratégies
                try:
                    from core.logger import get_logger
                    logger = get_logger(f"{__name__}.calculate_bullish_score")
                    
                    if staleness_status != "OK":
                        logger.warning(f"🕐 MIA Strategy Usage: {staleness_status} data - "
                                     f"asof={staleness_ms:.1f}ms, returning score={score}")
                    else:
                        logger.debug(f"✅ MIA Strategy Usage: Fresh data - "
                                   f"asof={staleness_ms:.1f}ms, score={score}")
                                   
                except Exception:
                    pass
                
                # Convertir en score bidirectionnel (-1 à +1)
                # Score original est [0,1], on le convertit en [-1,+1]
                bidirectional_score = (score - 0.5) * 2
                return round(bidirectional_score, 3)
            
            return 0.0
            
        except Exception as e:
            try:
                from core.logger import get_logger
                logger = get_logger(f"{__name__}.calculate_bullish_score")
                logger.error(f"❌ Erreur calcul MIA Bullish: {e}")
            except Exception:
                pass
            return 0.0

# --- HELPER POUR SNAPSHOTS UNIFIÉS ---

def feed_unified_snapshot(scorer: "BullishScorer", ev: dict, state: dict) -> dict | None:
    """
    Adapte un snapshot de type:
      {"timestamp": ..., "symbol": "...", "data_type": "unified_market_snapshot",
       "charts": [3], "bar_index": 1234 or None, "market_data": {...}}
    en une séquence d'évènements "bruts" pour BullishScorer.ingest().
    Retourne le dernier event dérivé (mia_bullish) si disponible.
    """
    if ev.get("data_type") != "unified_market_snapshot":
        return None

    md = ev.get("market_data") or {}
    charts = ev.get("charts") or []
    if 3 not in charts:
        return None

    # bar index (si pas fourni, on incrémente localement)
    bi = ev.get("bar_index")
    if bi is None:
        bi = state.setdefault("_i", -1) + 1
        state["_i"] = bi

    t = ev.get("timestamp")
    derived = None

    def push(e):
        nonlocal derived
        d = scorer.ingest(e)
        if d is not None:
            derived = d

    # --- basedata ---
    bd = md.get("basedata") or md.get("bd") or {}
    c = bd.get("close") or bd.get("c")
    if isinstance(c, (int, float)):
        push({"t": t, "type": "basedata", "chart": 3, "i": bi, "c": float(c)})

    # --- VWAP + bandes ---
    vwap = md.get("vwap") or {}
    v = vwap.get("v") or vwap.get("VWAP") or vwap.get("vwap")
    if isinstance(v, (int, float)):
        up1 = vwap.get("up1") or vwap.get("sigma1_up") or vwap.get("+1")
        dn1 = vwap.get("dn1") or vwap.get("sigma1_dn") or vwap.get("-1")
        push({
            "t": t, "type": "vwap", "chart": 3, "i": bi,
            "v": float(v),
            "up1": float(up1) if isinstance(up1, (int, float)) else None,
            "dn1": float(dn1) if isinstance(dn1, (int, float)) else None
        })

    # --- VVA (VAH/VAL) ---
    vva = md.get("vva") or {}
    vah = vva.get("vah") or vva.get("VAH")
    val = vva.get("val") or vva.get("VAL")
    if isinstance(vah, (int, float)) or isinstance(val, (int, float)):
        push({
            "t": t, "type": "vva", "chart": 3, "i": bi,
            "vah": float(vah) if isinstance(vah, (int, float)) else None,
            "val": float(val) if isinstance(val, (int, float)) else None
        })

    # --- NBCV metrics / footprint ---
    nbcv = md.get("nbcv") or {}
    metrics = nbcv.get("metrics") or nbcv
    dr = metrics.get("delta_ratio") or metrics.get("dr")
    bull = metrics.get("pressure_bullish") or metrics.get("bull") or 0
    bear = metrics.get("pressure_bearish") or metrics.get("bear") or 0
    if isinstance(dr, (int, float)) or bull or bear:
        push({
            "t": t, "type": "nbcv_metrics", "chart": 3, "i": bi,
            "delta_ratio": float(dr) if isinstance(dr, (int, float)) else None,
            "pressure_bullish": 1 if bull else 0,
            "pressure_bearish": 1 if bear else 0
        })

    fp = nbcv.get("footprint") or {}
    cd = fp.get("cumulative_delta") or fp.get("cumdelta") or fp.get("cum_delta")
    if isinstance(cd, (int, float)):
        push({
            "t": t, "type": "nbcv_footprint", "chart": 3, "i": bi,
            "cumulative_delta": float(cd)
        })

    # --- VIX (si snapshot l'expose) ---
    vix = (md.get("vix") or {}).get("close") or md.get("vix_close") or md.get("vix")
    if isinstance(vix, (int, float)):
        scorer.ingest({"t": t, "type": "vix_close", "close": float(vix), "chart": 8, "i": bi})

    return derived