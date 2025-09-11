
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIA Unified Stream Builder (enhanced)
-------------------------------------
Lit les fichiers JSONL spécialisés par chart/type (ex: chart_3_basedata_YYYYMMDD.jsonl)
et produit un flux unifié JSONL par buckets de temps.

Types supportés:
- basedata, vwap, vva, pvwap, vix, quote, trade, depth, nbcv, menthorq
- atr, hvn_lvn, vva_previous, cumulative_delta (nouveaux)

Ajouts:
- --menthorq-filter : applique un filtre optionnel (config.menthorq_runtime.should_emit_level)
- --only vwap,vva,atr,... : sélectionne uniquement certains blocs dans la sortie
- --gzip : écrit la sortie compressée (.gz)

Usage:
  python mia_unifier.py --indir "D:\\MIA_IA_system" --date today --tol 0.2 --gzip --only vwap,vva,atr,hvn_lvn
"""

import os, sys, json, glob, math, argparse, datetime, gzip, importlib
from collections import defaultdict

SUPPORTED_ONLY = {"basedata","vwap","vva","pvwap","vix","quote","trade","depth","nbcv","menthorq","extra","atr","hvn_lvn","vva_previous","cumulative_delta"}

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir", type=str, required=True, help="Dossier d'entrée (ex: D:\\MIA_IA_system)")
    ap.add_argument("--date", type=str, default="today", help="YYYYMMDD ou 'today' (heure locale machine)")
    ap.add_argument("--out", type=str, default=None, help="Fichier de sortie JSONL (sinon: <indir>\\unified_<date>.jsonl[.gz])")
    ap.add_argument("--tol", type=float, default=0.2, help="Tolérance de bucket (secondes, défaut 0.2)")
    ap.add_argument("--max_depth_levels", type=int, default=20, help="Max niveaux DOM par côté (défaut 20)")
    ap.add_argument("--menthorq-filter", action="store_true", help="Activer le filtre MenthorQ si disponible")
    ap.add_argument("--only", type=str, default=None, help="Liste séparée par virgules de sections à inclure (ex: vwap,vva,vix). Par défaut: tout")
    ap.add_argument("--gzip", action="store_true", help="Écrire en gzip (.gz)")
    ap.add_argument("--verbose", action="store_true")
    return ap.parse_args()

def resolve_date(s: str) -> str:
    if s.lower() == "today":
        return datetime.datetime.now().strftime("%Y%m%d")
    return s

def iter_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue

def list_inputs(indir: str, yyyymmdd: str):
    pat = os.path.join(indir, f"chart_*_{yyyymmdd}.jsonl")
    return sorted(glob.glob(pat))

def bucket_key(t_float: float, tol: float) -> float:
    secs = t_float * 86400.0
    return round(secs / tol) * tol

def ensure_vva_sanity(vva: dict):
    vah = vva.get("vah")
    vpoc = vva.get("vpoc")
    val = vva.get("val")
    if all(isinstance(x, (int, float)) and x > 0 for x in [vah, vpoc, val]):
        ordered = sorted([vah, vpoc, val], reverse=True)
        if [vah, vpoc, val] != ordered:
            vva["vah"], vva["vpoc"], vva["val"] = ordered
    return vva

def ensure_vwap_bands_sanity(vwap: dict):
    v = vwap.get("v")
    for k_up, k_dn in [("up1","dn1"), ("up2","dn2"), ("up3","dn3")]:
        up = vwap.get(k_up); dn = vwap.get(k_dn)
        if up is None or dn is None:
            continue
        if up < dn:
            vwap[k_up], vwap[k_dn] = dn, up
    return vwap

def load_menthorq_filter(enabled: bool):
    if not enabled:
        return None
    try:
        mod = importlib.import_module("config.menthorq_runtime")
        fn = getattr(mod, "should_emit_level", None)
        return fn
    except Exception:
        return None

def apply_menthorq_filter(levels, fn):
    if fn is None:
        return levels
    out = []
    for obj in levels:
        try:
            price = obj.get("price")
            symbol = obj.get("sym") or obj.get("symbol") or "ES"
            # 'kind' n'est pas explicite ici; on transmet 'level' + sg si utile
            ok = fn(symbol=symbol, price=price, sg=obj.get("sg"), raw=obj)
            if ok:
                out.append(obj)
        except Exception:
            # En cas d'erreur de filtre, fallback: conserver l'élément
            out.append(obj)
    return out

def unify(indir: str, yyyymmdd: str, out_path: str, tol: float, max_depth_levels: int, verbose: bool=False,
          only_set=None, menthorq_filter_enabled=False, gzip_enabled=False):
    paths = list_inputs(indir, yyyymmdd)
    if not paths:
        raise FileNotFoundError(f"Aucun fichier d'entrée pour la date {yyyymmdd} dans {indir}")

    buckets = defaultdict(lambda: {
        "t_sc": None,
        "records": {},
        "quotes": None,
        "trades": None,
        "depth": { "BID": {}, "ASK": {} },
        "nbcv": {},
        "menthorq_levels": [],
        "extra": []
    })

    n_lines = 0
    for p in paths:
        if verbose:
            print(f"Lecture: {p}", file=sys.stderr)
        for obj in iter_jsonl(p):
            n_lines += 1
            t = obj.get("t")
            if t is None:
                continue
            key = bucket_key(float(t), tol)
            b = buckets[key]
            if b["t_sc"] is None:
                b["t_sc"] = t

            typ = obj.get("type")
            if typ == "basedata":
                b["records"]["basedata"] = obj
            elif typ == "vwap":
                b["records"]["vwap"] = ensure_vwap_bands_sanity(dict(obj))
            elif typ == "vva":
                b["records"]["vva"] = ensure_vva_sanity(dict(obj))
            elif typ == "pvwap":
                b["records"]["pvwap"] = obj
            elif typ == "vix":
                b["records"]["vix"] = obj
            elif typ == "quote":
                b["quotes"] = obj
            elif typ == "trade":
                b["trades"] = obj
            elif typ == "depth":
                side = obj.get("side"); lvl = obj.get("lvl")
                if side in ("BID","ASK") and isinstance(lvl, int) and 1 <= lvl <= max_depth_levels:
                    b["depth"][side][lvl] = {"price": obj.get("price"), "size": obj.get("size")}
            elif typ in ("nbcv_footprint", "nbcv_metrics", "nbcv_orderflow"):
                i = obj.get("i", -1)
                entry = b["nbcv"].setdefault(i, {})
                if typ == "nbcv_footprint": entry["footprint"] = obj
                elif typ == "nbcv_metrics": entry["metrics"] = obj
                else: entry["orderflow"] = obj
            elif typ == "menthorq_level":
                b["menthorq_levels"].append(obj)
            elif typ == "atr":
                b["records"]["atr"] = obj
            elif typ == "hvn_lvn":
                b["records"]["hvn_lvn"] = obj
            elif typ == "vva_previous":
                b["records"]["vva_previous"] = obj
            elif typ == "cumulative_delta":
                b["records"]["cumulative_delta"] = obj
            else:
                b["extra"].append(obj)

    # MenthorQ filter (post-bucket)
    fn_filter = load_menthorq_filter(menthorq_filter_enabled)
    if fn_filter is not None:
        for b in buckets.values():
            b["menthorq_levels"] = apply_menthorq_filter(b["menthorq_levels"], fn_filter)

    # Writer (gzip/plain)
    if gzip_enabled and not out_path.endswith(".gz"):
        out_path = out_path + ".gz"

    opener = gzip.open if gzip_enabled else open
    mode = "wt" if gzip_enabled else "w"
    total_written = 0

    keys_sorted = sorted(buckets.keys())
    with opener(out_path, mode, encoding="utf-8") as out:
        for k in keys_sorted:
            b = buckets[k]
            unified = {}

            # Toujours inclure le temps
            unified["t"] = b["t_sc"]

            # Assemble blocs
            if (only_set is None) or ("basedata" in only_set):
                unified["basedata"] = b["records"].get("basedata")
            if (only_set is None) or ("vwap" in only_set):
                unified["vwap"] = b["records"].get("vwap")
            if (only_set is None) or ("vva" in only_set):
                unified["vva"] = b["records"].get("vva")
            if (only_set is None) or ("pvwap" in only_set):
                unified["pvwap"] = b["records"].get("pvwap")
            if (only_set is None) or ("vix" in only_set):
                unified["vix"] = b["records"].get("vix")
            if (only_set is None) or ("quote" in only_set):
                unified["quote"] = b["quotes"]
            if (only_set is None) or ("trade" in only_set):
                unified["trade"] = b["trades"]
            if (only_set is None) or ("depth" in only_set):
                unified["depth"] = {
                    "BID": [{"lvl": lvl, **vals} for lvl, vals in sorted(b["depth"]["BID"].items())],
                    "ASK": [{"lvl": lvl, **vals} for lvl, vals in sorted(b["depth"]["ASK"].items())],
                }
            if (only_set is None) or ("nbcv" in only_set):
                unified["nbcv"] = b["nbcv"]
            if (only_set is None) or ("menthorq" in only_set):
                unified["menthorq"] = b["menthorq_levels"]
            if (only_set is None) or ("atr" in only_set):
                unified["atr"] = b["records"].get("atr")
            if (only_set is None) or ("hvn_lvn" in only_set):
                unified["hvn_lvn"] = b["records"].get("hvn_lvn")
            if (only_set is None) or ("vva_previous" in only_set):
                unified["vva_previous"] = b["records"].get("vva_previous")
            if (only_set is None) or ("cumulative_delta" in only_set):
                unified["cumulative_delta"] = b["records"].get("cumulative_delta")
            if (only_set is None) or ("extra" in only_set):
                unified["extra"] = b["extra"]

            out.write(json.dumps(unified, ensure_ascii=False) + "\n")
            total_written += 1

    return {
        "inputs": len(paths),
        "lines_read": n_lines,
        "buckets": len(buckets),
        "written": total_written,
        "out": out_path,
        "gzip": gzip_enabled,
        "only": (sorted(only_set) if only_set else None),
        "menthorq_filter": bool(fn_filter)
    }

def main():
    args = parse_args()
    ymd = resolve_date(args.date)
    out_path = args.out or os.path.join(args.indir, f"unified_{ymd}.jsonl")

    only_set = None
    if args.only:
        only_set = set(s.strip().lower() for s in args.only.split(",")) - {""}
        unknown = sorted(only_set - SUPPORTED_ONLY)
        if unknown:
            raise ValueError(f"--only contient des clés non supportées: {unknown}. Clés valides: {sorted(SUPPORTED_ONLY)}")

    stats = unify(
        args.indir, ymd, out_path,
        tol=args.tol,
        max_depth_levels=args.max_depth_levels,
        verbose=args.verbose,
        only_set=only_set,
        menthorq_filter_enabled=args.menthorq_filter,
        gzip_enabled=args.gzip
    )
    print(json.dumps(stats, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
