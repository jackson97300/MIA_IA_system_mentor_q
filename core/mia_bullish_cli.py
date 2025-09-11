#!/usr/bin/env python3
"""
CLI: compute bullish score from either raw dumper events OR unified snapshots
and append derived events (type: mia_bullish).
Usage:
  python mia_bullish_cli.py --in D:/MIA_IA_system/mia_unified_YYYYMMDD.jsonl --out D:/MIA_IA_system/mia_unified_YYYYMMDD_bull.jsonl
"""
import argparse, json
from pathlib import Path
from mia_bullish import BullishScorer, feed_unified_snapshot  # <= le helper ajouté


def _derive_nbcv_metrics(ev: dict) -> dict | None:
    """Dérive un événement nbcv_metrics depuis nbcv_footprint si possible."""
    if ev.get("type") != "nbcv_footprint":
        return None
    dr = ev.get("delta_ratio")
    bull = 1 if ev.get("pressure_bullish") else 0
    bear = 1 if ev.get("pressure_bearish") else 0
    if dr is None and not bull and not bear:
        return None
    return {
        "t": ev.get("t"),
        "type": "nbcv_metrics",
        "chart": ev.get("chart"),
        "i": ev.get("i"),
        "delta_ratio": dr,
        "pressure_bullish": bull,
        "pressure_bearish": bear,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", required=True)
    ap.add_argument("--out", dest="outfile", required=True)
    ap.add_argument("--no-vix", action="store_true", help="Do not use VIX factor")
    ap.add_argument("--passthrough", action="store_true",
                    help="Forward input lines to out (useful if input is unified)")
    args = ap.parse_args()

    scorer = BullishScorer(chart_id=3, use_vix=(not args.no_vix))
    in_path = Path(args.infile)
    out_path = Path(args.outfile)

    state = {}  # pour l'index barre si manquant

    with in_path.open("r", encoding="utf-8") as fi, out_path.open("w", encoding="utf-8") as fo:
        for line in fi:
            try:
                ev = json.loads(line)
            except Exception:
                continue

            if args.passthrough:
                fo.write(line)  # facultatif : on recopie l'entrée

            derived = None

            # Voie 1: format BRUT (dumper) -> direct
            d1 = scorer.ingest(ev)
            if d1 is not None:
                derived = d1

            # Dérivation: footprint -> metrics (pour activer le scorer si metrics absent)
            if derived is None:
                metrics = _derive_nbcv_metrics(ev)
                if metrics is not None:
                    d1b = scorer.ingest(metrics)
                    if d1b is not None:
                        derived = d1b

            # Voie 2: format UNIFIÉ (snapshot) -> adapter puis ingérer
            if derived is None and ev.get("data_type") == "unified_market_snapshot":
                d2 = feed_unified_snapshot(scorer, ev, state)
                if d2 is not None:
                    derived = d2

            if derived is not None:
                fo.write(json.dumps(derived, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()