
# -*- coding: utf-8 -*-
"""
create_options_snapshot_gex_v3.py

Améliorations intégrées :
1) Validation GEX (_validate_gex_data) avec tolérance adaptative
2) Normalisation GEX dynamique basée sur notional total
3) Logging détaillé avec rotation des logs
4) Gestion d'erreurs robuste avec fallbacks

Rappels / Hypothèses :
- GEX_i = gamma_i * S^2 * OI_i * contract_multiplier (gamma par $1 de sous-jacent)
- Signe GEX : issu de l'hypothèse côté dealer (short -1 par défaut / long +1)
"""

import os
import json
import csv
import asyncio
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from logging.handlers import RotatingFileHandler

from ibkr_connector3 import IBKRConnector

# --------------------------------- Logging ------------------------------------
logger = logging.getLogger("snapshot_gex")

# Configuration logging avec rotation
def setup_logging():
    """Configure le logging avec rotation des fichiers"""
    if not logger.handlers:
        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        console_handler.setFormatter(console_formatter)
        
        # Handler fichier avec rotation
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'snapshot_gex.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        
        # Configuration logger
        logger.setLevel(logging.DEBUG)
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

setup_logging()

DEFAULT_SNAPSHOT_DIR = "data/options_snapshots"

CONFIG = {
    "SPX": {
        "expiry": "20250919",
        "fallback_strikes": [4500, 4600, 4700, 4800, 4900],
        "vol_index": "VIX",
        "strike_step": 25,
    },
    "NDX": {
        "expiry": "20250919",
        "fallback_strikes": [18000, 18500, 19000, 19500, 20000],
        "vol_index": "VXN",
        "strike_step": 100,
    },
}

# ------------------------------ Utils -----------------------------------------
def _now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def _ensure_dirs(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def _safe_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None

def _safe_int(x: Any) -> int:
    try:
        if x is None:
            return 0
        return int(x)
    except Exception:
        return 0

def _round_to_step(x: float, step: float) -> float:
    if step <= 0:
        return x
    return round(x / step) * step

def _compute_dynamic_strikes(underlying_price: float, step: int, window: int) -> List[float]:
    if underlying_price is None or underlying_price <= 0:
        return []
    atm = _round_to_step(underlying_price, step)
    strikes = [atm + i * step for i in range(-window, window + 1)]
    return [s for s in strikes if s > 0]

def _normalize_option_row(symbol: str, expiry: str, raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "symbol": symbol,
        "expiry": expiry,
        "strike": raw.get("strike"),
        "type": raw.get("type"),  # "C" ou "P"
        "bid": _safe_float(raw.get("bid")),
        "ask": _safe_float(raw.get("ask")),
        "last": _safe_float(raw.get("last")),
        "volume": _safe_int(raw.get("volume")),
        "open_interest": _safe_int(raw.get("open_interest")),
        "delta": _safe_float(raw.get("delta")) or 0.0,
        "gamma": _safe_float(raw.get("gamma")) or 0.0,
        "theta": _safe_float(raw.get("theta")) or 0.0,
        "vega": _safe_float(raw.get("vega")) or 0.0,
        "iv": _safe_float(raw.get("iv")),
    }

def _aggregate_by_strike(options: List[Dict[str, Any]]) -> Dict[float, Dict[str, int]]:
    agg: Dict[float, Dict[str, int]] = {}
    for o in options:
        k = float(o["strike"]) if o.get("strike") is not None else None
        if k is None:
            continue
        d = agg.setdefault(k, {"C": 0, "P": 0, "total": 0})
        t = o.get("type")
        oi = _safe_int(o.get("open_interest"))
        if t == "C":
            d["C"] += oi
        elif t == "P":
            d["P"] += oi
        d["total"] = d["C"] + d["P"]
    return dict(sorted(agg.items(), key=lambda x: x[0]))

def _compute_max_pain(oi_by_strike: Dict[float, Dict[str, int]]) -> Optional[float]:
    if not oi_by_strike:
        return None
    strikes = sorted(oi_by_strike.keys())

    def loss_at_price(price: float) -> float:
        loss = 0.0
        for k, d in oi_by_strike.items():
            calls_oi = d.get("C", 0)
            puts_oi = d.get("P", 0)
            loss += max(0.0, price - k) * calls_oi
            loss += max(0.0, k - price) * puts_oi
        return loss

    best_strike, best_loss = None, None
    for price in strikes:
        l = loss_at_price(price)
        if best_loss is None or l < best_loss:
            best_loss = l
            best_strike = price
    return best_strike

# ------------------------------ GEX -------------------------------------------
def _validate_gex_data(gex_data: Dict[str, Any]) -> bool:
    """Valide la cohérence des données GEX avec tolérance adaptative."""
    if not gex_data:
        return False
    magnitude = gex_data.get("gex_total_magnitude", 0.0)
    signed = gex_data.get("gex_total_signed", 0.0)
    dealer_sign = gex_data.get("dealer_sign_assumption", -1)
    
    # Validations de base
    if magnitude is None or magnitude <= 0:
        return False
    if signed is None or dealer_sign not in (-1, 1):
        return False
    
    # Tolérance adaptative plus généreuse
    # Pour de très grandes valeurs, tolérance relative plus large
    if magnitude > 1e12:  # Très grandes valeurs
        tolerance = max(1e-2, 1e-2 * magnitude)
    elif magnitude > 1e9:  # Grandes valeurs
        tolerance = max(1e-3, 1e-3 * magnitude)
    else:  # Valeurs normales
        tolerance = max(1e-4, 1e-4 * magnitude)
    
    if abs(signed) - magnitude > tolerance:
        logger.warning(f"GEX validation échouée: signed={signed}, magnitude={magnitude}, tolerance={tolerance}")
        return False
    return True

def _compute_gex(options: List[Dict[str, Any]],
                 underlying_price: Optional[float],
                 contract_multiplier: int,
                 dealer_sign: int) -> Optional[Dict[str, Any]]:
    if not options or not underlying_price or underlying_price <= 0:
        return None

    S2 = underlying_price * underlying_price
    gex_total = 0.0
    gex_calls = 0.0
    gex_puts = 0.0
    by_strike: Dict[float, float] = {}
    
    # Calcul du notional total pour normalisation dynamique
    total_notional = 0.0
    for o in options:
        strike = _safe_float(o.get("strike"))
        oi = _safe_int(o.get("open_interest"))
        if strike and oi:
            total_notional += strike * oi

    for o in options:
        gamma = _safe_float(o.get("gamma"))
        oi = _safe_int(o.get("open_interest"))
        k = _safe_float(o.get("strike"))
        if gamma is None or gamma == 0 or oi == 0 or k is None:
            continue
        gex_i = gamma * S2 * oi * contract_multiplier  # magnitude
        if o.get("type") == "C":
            gex_calls += gex_i
        elif o.get("type") == "P":
            gex_puts += gex_i
        by_strike[k] = by_strike.get(k, 0.0) + gex_i

    gex_mag = gex_calls + gex_puts
    gex_signed = dealer_sign * gex_mag  # signe hypothétique

    # Normalisation dynamique basée sur notional total
    if total_notional > 0:
        normalization_factor = max(1e6, total_notional / 1e6)
        gex_signed_normalized = gex_signed / normalization_factor
        gex_mag_normalized = gex_mag / normalization_factor
    else:
        normalization_factor = 1e6  # Fallback
        gex_signed_normalized = gex_signed / normalization_factor
        gex_mag_normalized = gex_mag / normalization_factor

    out = {
        "contract_multiplier": contract_multiplier,
        "dealer_sign_assumption": dealer_sign,
        "gex_total_magnitude": gex_mag,
        "gex_total_signed": gex_signed,
        "gex_calls_magnitude": gex_calls,
        "gex_puts_magnitude": gex_puts,
        "gex_by_strike": dict(sorted(by_strike.items(), key=lambda x: x[0])),
        "normalized": {
            "normalization_factor": normalization_factor,
            "total_notional": total_notional,
            "gex_total_signed_normalized": gex_signed_normalized,
            "gex_total_magnitude_normalized": gex_mag_normalized,
            # Garder aussi l'ancienne normalisation pour compatibilité
            "per_million": 1_000_000.0,
            "gex_total_signed_per_million": gex_signed / 1_000_000.0 if gex_signed else 0.0,
            "gex_total_magnitude_per_million": gex_mag / 1_000_000.0 if gex_mag else 0.0,
        }
    }
    
    if not _validate_gex_data(out):
        logger.warning("GEX invalide (magnitude/signed incohérents) → Ignoré.")
        return None
    return out

# ------------------------------ Analysis --------------------------------------
def _analysis_block(symbol: str,
                    options: List[Dict[str, Any]],
                    vol_index_value: Optional[float],
                    underlying_price: Optional[float],
                    contract_multiplier: int,
                    dealer_sign: int) -> Dict[str, Any]:
    calls_oi = sum(o["open_interest"] for o in options if o.get("type") == "C")
    puts_oi  = sum(o["open_interest"] for o in options if o.get("type") == "P")
    total_oi = calls_oi + puts_oi

    calls_vol = sum(o["volume"] for o in options if o.get("type") == "C")
    puts_vol  = sum(o["volume"] for o in options if o.get("type") == "P")

    ivs_all = [o["iv"] for o in options if _safe_float(o.get("iv")) is not None]
    ivs_calls = [o["iv"] for o in options if o.get("type") == "C" and _safe_float(o.get("iv")) is not None]
    ivs_puts  = [o["iv"] for o in options if o.get("type") == "P" and _safe_float(o.get("iv")) is not None]

    iv_avg = round(sum(ivs_all) / len(ivs_all), 4) if ivs_all else None
    iv_calls_avg = round(sum(ivs_calls) / len(ivs_calls), 4) if ivs_calls else None
    iv_puts_avg  = round(sum(ivs_puts)  / len(ivs_puts), 4)  if ivs_puts else None
    iv_skew = round((iv_puts_avg - iv_calls_avg), 4) if (iv_calls_avg is not None and iv_puts_avg is not None) else None

    pcr_oi = round(puts_oi / calls_oi, 4) if calls_oi > 0 else None
    pcr_volume = round(puts_vol / calls_vol, 4) if calls_vol > 0 else None

    oi_by_strike = _aggregate_by_strike(options)
    max_pain = _compute_max_pain(oi_by_strike)

    # --- GEX ---
    gex = _compute_gex(options, underlying_price, contract_multiplier, dealer_sign)
    if gex:
        gex_signed = gex.get("gex_total_signed", 0.0)
        gex_calls = gex.get("gex_calls_magnitude", 0.0)
        gex_puts = gex.get("gex_puts_magnitude", 0.0)
        gex_normalized = gex.get("normalized", {}).get("gex_total_signed_normalized", 0.0)
        total_notional = gex.get("normalized", {}).get("total_notional", 0.0)
        
        logger.info(f"📈 GEX {symbol}: {gex_signed:+.2e} ({'short' if dealer_sign==-1 else 'long'} gamma)")
        logger.info(f"   Calls: {gex_calls:+.2e}, Puts: {gex_puts:+.2e}")
        logger.info(f"   Normalized: {gex_normalized:+.4f}, Notional: {total_notional:+.2e}")
    else:
        logger.warning(f"⚠️  GEX {symbol}: non calculable ou invalide.")

    analysis = {
        "timestamp": datetime.now().isoformat(),
        "underlying_price": underlying_price,
        "put_call_ratio_oi": pcr_oi,
        "put_call_ratio_volume": pcr_volume,
        "implied_volatility_avg": iv_avg,
        "iv_calls_avg": iv_calls_avg,
        "iv_puts_avg": iv_puts_avg,
        "iv_skew_puts_minus_calls": iv_skew,
        "open_interest": {
            "calls_oi": calls_oi,
            "puts_oi": puts_oi,
            "total_oi": total_oi
        },
        "oi_by_strike": oi_by_strike,
        "max_pain": max_pain,
        "gex": gex,  # bloc GEX (None si invalide)
    }
    if symbol.upper() == "SPX":
        analysis["vix"] = vol_index_value
    elif symbol.upper() == "NDX":
        analysis["vxn"] = vol_index_value
    else:
        analysis["vol_index"] = vol_index_value
    return analysis

# ------------------------------ I/O -------------------------------------------
async def _create_csv_snapshot(outdir: str, symbol: str, expiry: str, options: List[Dict[str, Any]]) -> Optional[str]:
    if not options:
        return None
    _ensure_dirs(outdir)
    path = os.path.join(outdir, f"{symbol.lower()}_snapshot_{_now_stamp()}.csv")
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "symbol","expiry","strike","option_type",
            "bid","ask","last","volume","open_interest",
            "delta","gamma","theta","vega","iv","timestamp"
        ])
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for opt in options:
            w.writerow([
                symbol, expiry, opt["strike"], opt["type"],
                opt["bid"], opt["ask"], opt["last"], opt["volume"], opt["open_interest"],
                opt["delta"], opt["gamma"], opt["theta"], opt["vega"], opt["iv"], stamp
            ])
    return path

async def _create_json_snapshot(outdir: str,
                                symbol: str,
                                expiry: str,
                                options: List[Dict[str, Any]],
                                vol_index_value: Optional[float],
                                underlying_price: Optional[float],
                                contract_multiplier: int,
                                dealer_sign: int) -> Optional[str]:
    if not options:
        return None
    _ensure_dirs(outdir)
    path = os.path.join(outdir, f"{symbol.lower()}_snapshot_{_now_stamp()}.json")
    payload = {
        "snapshot_id": _now_stamp(),
        "symbol": symbol,
        "expiry": expiry,
        "timestamp": datetime.now().isoformat(),
        "options": options,
        "analysis": _analysis_block(symbol, options, vol_index_value, underlying_price, contract_multiplier, dealer_sign)
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return path

# ------------------------------ Fetchers --------------------------------------
async def _fetch_chain(conn: IBKRConnector, symbol: str, expiry: str, strikes: List[float]) -> List[Dict[str, Any]]:
    raw = []
    try:
        raw = await conn.get_options_chain(symbol, expiry, strikes)
    except Exception as e:
        logger.error(f"get_options_chain a échoué pour {symbol}: {e}")
        return []
    normalized = [_normalize_option_row(symbol, expiry, r) for r in (raw or [])]
    return normalized

async def _fetch_underlying_price(conn: IBKRConnector, symbol: str) -> Optional[float]:
    try:
        p = await conn.get_underlying_price(symbol)
        if p and p > 0:
            return float(p)
    except Exception as e:
        logger.info(f"get_underlying_price indisponible pour {symbol}: {e}")
    try:
        p = await conn.get_index_value(symbol)
        if p and p > 0:
            return float(p)
    except Exception as e:
        logger.info(f"get_index_value indisponible pour {symbol}: {e}")
    return None

async def _fetch_vol_index(conn: IBKRConnector, index_symbol: str) -> Optional[float]:
    try:
        return await conn.get_index_value(index_symbol)
    except Exception as e:
        logger.warning(f"Impossible de récupérer {index_symbol}: {e}")
        return None

# ------------------------------ Main flow -------------------------------------
async def generate_snapshots_for(conn: IBKRConnector,
                                 outdir: str,
                                 symbol: str,
                                 expiry: str,
                                 vol_index_symbol: str,
                                 strike_step: int,
                                 dynamic: bool,
                                 window: int,
                                 fallback_strikes: List[float],
                                 contract_multiplier: int,
                                 dealer_sign: int) -> Dict[str, Optional[str]]:
    logger.info(f"[{symbol}] Préparation des strikes …")
    underlying_price = await _fetch_underlying_price(conn, symbol)
    if dynamic and underlying_price:
        strikes = _compute_dynamic_strikes(underlying_price, strike_step, window)
        if not strikes:
            logger.warning(f"[{symbol}] Strikes dynamiques vides, utilisation du fallback.")
            strikes = fallback_strikes
    else:
        strikes = fallback_strikes

    if not strikes:
        logger.error(f"[{symbol}] Aucun strike disponible (dynamic={dynamic}). Skip.")
        return {"csv": None, "json": None, "analysis": None}

    logger.info(f"[{symbol}] Underlying={underlying_price} | Strikes={strikes[:3]}…{strikes[-3:]} (total={len(strikes)})")
    options = await _fetch_chain(conn, symbol, expiry, strikes)

    if not options:
        logger.warning(f"[{symbol}] Aucune option récupérée, snapshot non créé.")
        return {"csv": None, "json": None, "analysis": None}

    vol_index_value = await _fetch_vol_index(conn, vol_index_symbol)

    csv_path = await _create_csv_snapshot(outdir, symbol, expiry, options)
    json_path = await _create_json_snapshot(outdir, symbol, expiry, options, vol_index_value, underlying_price,
                                            contract_multiplier, dealer_sign)

    logger.info(f"[{symbol}] CSV :  {csv_path}")
    logger.info(f"[{symbol}] JSON : {json_path}")
    return {"csv": csv_path, "json": json_path, "analysis": json_path}

async def write_combined_summary(outdir: str,
                                 summaries: Dict[str, Dict[str, Any]]) -> str:
    data: Dict[str, Any] = {"timestamp": datetime.now().isoformat(), "symbols": {}}
    for symbol, paths in summaries.items():
        json_path = paths.get("json")
        if not json_path or not os.path.exists(json_path):
            data["symbols"][symbol] = {"status": "no_data"}
            continue
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            analysis = payload.get("analysis", {})
            data["symbols"][symbol] = {"status": "ok", "analysis": analysis}
        except Exception as e:
            data["symbols"][symbol] = {"status": f"error: {e}"}
    _ensure_dirs(outdir)
    combined_path = os.path.join(outdir, f"combined_summary_{_now_stamp()}.json")
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Résumé combiné créé: {combined_path}")
    return combined_path

async def run(symbols: List[str],
              outdir: str,
              dynamic: bool,
              window: int,
              contract_multiplier: int,
              dealer_sign: int) -> Tuple[Dict[str, Dict[str, Optional[str]]], Optional[str]]:
    conn = IBKRConnector("127.0.0.1", 7496)
    await conn.connect()
    try:
        tasks = []
        for sym in symbols:
            cfg = CONFIG.get(sym.upper())
            if not cfg:
                logger.warning(f"Symbole non supporté dans CONFIG: {sym}")
                continue
            tasks.append(
                generate_snapshots_for(
                    conn=conn,
                    outdir=outdir,
                    symbol=sym.upper(),
                    expiry=cfg["expiry"],
                    vol_index_symbol=cfg["vol_index"],
                    strike_step=cfg["strike_step"],
                    dynamic=dynamic,
                    window=window,
                    fallback_strikes=cfg["fallback_strikes"],
                    contract_multiplier=contract_multiplier,
                    dealer_sign=dealer_sign,
                )
            )
        results = await asyncio.gather(*tasks, return_exceptions=True)

        summaries: Dict[str, Dict[str, Optional[str]]] = {}
        for sym, res in zip(symbols, results):
            if isinstance(res, Exception):
                logger.error(f"Erreur pendant la génération pour {sym}: {res}")
                summaries[sym.upper()] = {"csv": None, "json": None}
            else:
                summaries[sym.upper()] = res  # type: ignore

        combined_path = await write_combined_summary(outdir, summaries)
        return summaries, combined_path
    finally:
        await conn.disconnect()

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Snapshots options SPX/NDX (CSV+JSON) avec analyses (incl. GEX v3 + validation + logs + rotation).")
    p.add_argument("--symbols", type=str, default="SPX,NDX", help="Ex: SPX,NDX")
    p.add_argument("--dynamic", action="store_true", help="Strikes dynamiques ATM ± window*step")
    p.add_argument("--window", type=int, default=5, help="Nombre de pas autour de l'ATM (dyn)")
    p.add_argument("--outdir", type=str, default=DEFAULT_SNAPSHOT_DIR, help="Dossier de sortie")
    p.add_argument("--gex-multiplier", type=int, default=100, help="Multiplicateur contrat (SPX/NDX=100)")
    dealer = p.add_mutually_exclusive_group()
    dealer.add_argument("--dealer-short", dest="dealer_short", action="store_true", help="Hypothèse dealers short gamma (signe -1) [défaut]")
    dealer.add_argument("--dealer-long", dest="dealer_short", action="store_false", help="Hypothèse dealers long gamma (signe +1)")
    p.set_defaults(dealer_short=True)
    return p.parse_args()

def main():
    args = parse_args()
    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    outdir = args.outdir
    dynamic = args.dynamic
    window = max(1, int(args.window))
    contract_multiplier = int(args.gex_multiplier)
    dealer_sign = -1 if args.dealer_short else +1

    logger.info("====================================================")
    logger.info("  Snapshots Options SPX/NDX - GEX v3 (amélioré)    ")
    logger.info("====================================================")
    logger.info(f"Symbols          : {symbols}")
    logger.info(f"Dynamic          : {dynamic} | Window: ±{window} pas")
    logger.info(f"OutDir           : {outdir}")
    logger.info(f"GEX multiplier   : {contract_multiplier}")
    logger.info(f"Dealer sign hypo : {dealer_sign} ({'short' if dealer_sign==-1 else 'long'})")
    logger.info("----------------------------------------------------")

    asyncio.run(
        run(symbols=symbols, outdir=outdir, dynamic=dynamic, window=window,
            contract_multiplier=contract_multiplier, dealer_sign=dealer_sign)
    )

if __name__ == "__main__":
    main()
