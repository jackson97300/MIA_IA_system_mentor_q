
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIA Unified Viewer
------------------
Lit un ou plusieurs fichiers unifiés (JSONL ou JSONL.GZ) et imprime:
- Statistiques globales (buckets, présence des blocs, répartition)
- Profondeur DOM moyenne / max
- Anomalies détectées:
  * VVA: ordre VAH ≥ VPOC ≥ VAL violé
  * VWAP: inversion de bandes (up < dn) par niveau
- MenthorQ: compte total de niveaux par SG
- NBCV: buckets avec footprint/metrics/orderflow incomplets

Options:
  --csv-out <dir>  : écrit des CSVs sommaires (ex: vwap.csv, vva.csv, vix.csv, depth_summary.csv)
  --limit <N>      : ne lit que les N premières lignes pour tests rapides
  --quiet          : réduit la verbosité
Usage:
  python mia_unified_viewer.py --file D:\MIA_IA_system\unified_20250910.jsonl.gz --csv-out D:\MIA_IA_system\reports
"""

import os, sys, json, gzip, argparse, statistics
from collections import Counter, defaultdict

def open_maybe_gzip(path):
    if path.lower().endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "r", encoding="utf-8")

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=str, required=True, help="Chemin du fichier unified JSONL (.jsonl ou .jsonl.gz)")
    ap.add_argument("--limit", type=int, default=None, help="Limiter le nombre de lignes lues")
    ap.add_argument("--csv-out", type=str, default=None, help="Répertoire où écrire des CSV sommaires")
    ap.add_argument("--quiet", action="store_true")
    return ap.parse_args()

def write_csv_rows(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(",".join(header) + "\n")
        for r in rows:
            vals = [str(r.get(h,"")) for h in header]
            f.write(",".join(vals) + "\n")

def main():
    args = parse_args()
    p = args.file
    quiet = args.quiet

    present_counts = Counter()
    total_lines = 0
    vwap_inversion = Counter()  # per level name
    vva_violations = 0
    dom_levels_seen = []  # total levels per side per bucket
    dom_levels_max = 0
    menthorq_by_sg = Counter()
    nbcv_incomplete = 0

    # CSV accumulators
    rows_vwap = []
    rows_vva = []
    rows_vix  = []
    rows_depth = []  # one row per bucket with max lvl observed
    rows_stats = []

    with open_maybe_gzip(p) as f:
        for idx, line in enumerate(f, start=1):
            if args.limit and idx > args.limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            total_lines += 1
            t = obj.get("t")

            # Presence map
            for key in ("basedata","vwap","vva","pvwap","vix","quote","trade","depth","nbcv","menthorq","extra"):
                if obj.get(key) is not None and obj.get(key) != {}:
                    present_counts[key] += 1

            # VWAP sanity & CSV
            vwap = obj.get("vwap") or {}
            if vwap:
                # Count inversions per band
                for up,dn,label in [("up1","dn1","1"), ("up2","dn2","2"), ("up3","dn3","3")]:
                    u = vwap.get(up); d = vwap.get(dn)
                    if isinstance(u,(int,float)) and isinstance(d,(int,float)) and u < d:
                        vwap_inversion[label] += 1
                rows_vwap.append({
                    "t": t,
                    "v": vwap.get("v"),
                    "up1": vwap.get("up1"), "dn1": vwap.get("dn1"),
                    "up2": vwap.get("up2"), "dn2": vwap.get("dn2"),
                    "up3": vwap.get("up3"), "dn3": vwap.get("dn3"),
                })

            # VVA sanity & CSV
            vva = obj.get("vva") or {}
            if vva:
                vah = vva.get("vah"); vpoc = vva.get("vpoc"); val = vva.get("val")
                if all(isinstance(x,(int,float)) for x in (vah,vpoc,val)):
                    if not (vah >= vpoc >= val):
                        vva_violations += 1
                rows_vva.append({
                    "t": t, "vah": vah, "vpoc": vpoc, "val": val,
                    "pvah": vva.get("pvah"), "ppoc": vva.get("ppoc"), "pval": vva.get("pval")
                })

            # VIX CSV
            vix = obj.get("vix") or {}
            if vix:
                rows_vix.append({"t": t, "last": vix.get("last")})

            # Depth stats & CSV
            depth = obj.get("depth") or {}
            bid_lvls = len(depth.get("BID", []))
            ask_lvls = len(depth.get("ASK", []))
            dom_levels_seen.append(bid_lvls + ask_lvls)
            dom_levels_max = max(dom_levels_max, bid_lvls, ask_lvls)
            if depth:
                rows_depth.append({"t": t, "bid_levels": bid_lvls, "ask_levels": ask_lvls})

            # MenthorQ
            for lvl in obj.get("menthorq") or []:
                sg = lvl.get("sg")
                if sg is not None:
                    menthorq_by_sg[sg] += 1

            # NBCV completeness
            nbcv = obj.get("nbcv") or {}
            for i, entry in nbcv.items():
                missing = 0
                if "footprint" not in entry: missing += 1
                if "metrics" not in entry: missing += 1
                if "orderflow" not in entry: missing += 1
                if missing > 0:
                    nbcv_incomplete += 1
                    break  # bucket counted once for incompleteness

    # Derived stats
    mean_dom = statistics.mean(dom_levels_seen) if dom_levels_seen else 0.0
    max_dom  = max(dom_levels_seen) if dom_levels_seen else 0
    result = {
        "file": p,
        "buckets": total_lines,
        "presence_per_block": dict(present_counts),
        "dom_levels_mean_total": round(mean_dom, 2),
        "dom_levels_max_any_side": dom_levels_max,
        "dom_levels_max_total": max_dom,
        "vwap_band_inversions": {f"band_{k}": v for k,v in vwap_inversion.items()},
        "vva_order_violations": vva_violations,
        "menthorq_counts_by_sg": dict(sorted(menthorq_by_sg.items())),
        "nbcv_buckets_incomplete": nbcv_incomplete
    }

    if not quiet:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    # CSV export
    if args.csv_out:
        outdir = args.csv_out
        write_csv_rows(os.path.join(outdir, "vwap.csv"),
                       ["t","v","up1","dn1","up2","dn2","up3","dn3"],
                       rows_vwap)
        write_csv_rows(os.path.join(outdir, "vva.csv"),
                       ["t","vah","vpoc","val","pvah","ppoc","pval"],
                       rows_vva)
        write_csv_rows(os.path.join(outdir, "vix.csv"),
                       ["t","last"],
                       rows_vix)
        write_csv_rows(os.path.join(outdir, "depth_summary.csv"),
                       ["t","bid_levels","ask_levels"],
                       rows_depth)
        write_csv_rows(os.path.join(outdir, "run_stats.csv"),
                       list(result.keys()),
                       [result])
        if not quiet:
            print(f"CSV écrits dans: {outdir}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
