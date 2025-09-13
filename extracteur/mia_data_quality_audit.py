
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIA Data Quality Audit
----------------------
Scan the project root for Sierra dump outputs (chart_3/4/8/10*.jsonl[.gz]),
validate & profile records, and emit a JSON + Markdown report.

Usage:
    python mia_data_quality_audit.py --root . --out ./_dq --max-lines 0

- root: directory to scan (default: current dir)
- out: output directory for reports (default: ./_dq)
- max-lines: limit per file (0 = no limit), helpful for quick runs
"""
import argparse
import json
import gzip
import os
import re
import sys
import math
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict, Counter

def open_maybe_gzip(path):
    path = str(path)
    if path.lower().endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return open(path, "r", encoding="utf-8", errors="replace")

ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$")

def to_iso_utc(ts):
    """
    Convert supported timestamp formats to ISO8601 UTC string (*Z* suffix).
    Supports epoch seconds/ms and ISO8601 (with/without Z).
    Returns (iso_str, ok:bool).
    """
    if ts is None:
        return None, False
    try:
        if isinstance(ts, (int, float)):
            # epoch seconds or ms
            t = float(ts)
            if t > 1e12:  # ms
                t = t / 1000.0
            dt = datetime.utcfromtimestamp(t).replace(tzinfo=timezone.utc)
            return dt.isoformat().replace("+00:00","Z"), True
        if isinstance(ts, str):
            # Already ISO with Z?
            if ISO_RE.match(ts):
                return ts, True
            # Try parse ISO and force UTC
            try:
                if ts.endswith("Z"):
                    ts = ts[:-1] + "+00:00"
                dt = datetime.fromisoformat(ts).astimezone(timezone.utc)
                return dt.isoformat().replace("+00:00","Z"), True
            except Exception:
                return None, False
    except Exception:
        return None, False
    return None, False

def safe_float(x):
    try:
        return float(x)
    except Exception:
        return None

def summarize_numeric(vals):
    vals = [v for v in vals if isinstance(v, (int, float)) and not (isinstance(v,float) and (math.isnan(v) or math.isinf(v)))]
    if not vals:
        return None
    vals.sort()
    n = len(vals)
    q50 = vals[n//2] if n%2==1 else 0.5*(vals[n//2-1]+vals[n//2])
    return {
        "count": n,
        "min": vals[0],
        "p25": vals[int(0.25*(n-1))] if n>3 else vals[0],
        "median": q50,
        "p75": vals[int(0.75*(n-1))] if n>3 else vals[-1],
        "max": vals[-1]
    }

def chart_kind_from_name(name: str):
    m = re.search(r"chart_(\d+)_", name)
    if not m:
        return None
    return int(m.group(1))

def expected_keys_for_chart(chart_no: int):
    # Soft expectations; audit will just warn if missing.
    base = {"symbol","ts","price","bid","ask","bid_volume","ask_volume"}  # common orderflow-ish
    if chart_no == 3:
        return {"symbol","ts","last_price","bid","ask","bid_volume","ask_volume","delta","seq"}
    if chart_no == 4:
        return {"symbol","ts","VAL","POC","VAH","vwap","session"}
    if chart_no == 8:
        return {"ts","vix"}
    if chart_no == 10:
        return {"symbol","ts","dealers_bias","gamma_support","gamma_resistance","gex","hvl","blind_spots"}
    return base

def check_logical_constraints(chart_no: int, obj: dict, issues: list):
    # Run per-record logical checks; append to issues list if violation.
    if chart_no == 4:
        # VAL <= POC <= VAH
        VAL = safe_float(obj.get("VAL"))
        POC = safe_float(obj.get("POC"))
        VAH = safe_float(obj.get("VAH"))
        if None not in (VAL,POC,VAH):
            if not (VAL <= POC <= VAH):
                issues.append("profile_order_violation")  # VALUE-AREA order broken
        # VWAP sanity range vs price (if present)
        vwap = safe_float(obj.get("vwap"))
        price = safe_float(obj.get("last_price") or obj.get("price"))
        if vwap is not None and price is not None:
            if abs(vwap - price) > 10_000:  # absurd difference guard
                issues.append("vwap_out_of_range")
    elif chart_no == 8:
        vix = safe_float(obj.get("vix"))
        if vix is not None:
            if not (5 <= vix <= 150):
                issues.append("vix_out_of_bounds")
    elif chart_no == 10:
        # bias & scores in [-1,1]
        for k in ("dealers_bias","gex","gamma_support","gamma_resistance"):
            v = safe_float(obj.get(k))
            if v is not None and not (-10 <= v <= 10):  # allow wider range for levels if they are raw points
                issues.append(f"{k}_suspicious_range")
    else:
        # chart 3 default checks
        price = safe_float(obj.get("last_price") or obj.get("price"))
        bid = safe_float(obj.get("bid")); ask = safe_float(obj.get("ask"))
        if None not in (bid, ask) and bid > ask:
            issues.append("bid_gt_ask")
        if price is not None and None not in (bid, ask):
            if not (bid <= price <= ask):
                # not always true on prints, but flag as soft issue
                issues.append("price_outside_bbo")

def scan_file(path: Path, max_lines: int = 0):
    stats = {
        "path": str(path),
        "chart": chart_kind_from_name(path.name),
        "lines_total": 0,
        "lines_valid_json": 0,
        "lines_with_ts": 0,
        "lines_with_symbol": 0,
        "invalid_json": 0,
        "missing_keys": Counter(),
        "issues": Counter(),
        "first_ts": None,
        "last_ts": None,
        "monotonic_ts_violations": 0,
        "dupe_keys": 0,
        "symbols": Counter(),
        "prices": [],
    }
    seen = set()
    last_ts_val = None

    expected = expected_keys_for_chart(stats["chart"] or -1)

    with open_maybe_gzip(path) as f:
        for i, line in enumerate(f, start=1):
            if max_lines and i > max_lines:
                break
            s = line.strip()
            if not s:
                continue
            stats["lines_total"] += 1
            try:
                obj = json.loads(s)
                stats["lines_valid_json"] += 1
            except Exception:
                stats["invalid_json"] += 1
                continue

            # Timestamp normalization
            ts_raw = obj.get("ts") or obj.get("timestamp") or obj.get("ts_ns")
            iso, ok = to_iso_utc(ts_raw)
            if ok:
                obj["ts"] = iso
                stats["lines_with_ts"] += 1
                # monotonic check per file (soft: allow equal)
                try:
                    cur = datetime.fromisoformat(iso.replace("Z","+00:00")).timestamp()
                    if last_ts_val is not None and cur < last_ts_val - 1e-6:
                        stats["monotonic_ts_violations"] += 1
                    last_ts_val = cur
                except Exception:
                    pass
                if stats["first_ts"] is None:
                    stats["first_ts"] = iso
                stats["last_ts"] = iso

            # Symbol presence
            sym = obj.get("symbol")
            if sym:
                stats["lines_with_symbol"] += 1
                stats["symbols"][str(sym)] += 1

            # Expected keys
            for k in expected:
                if k not in obj:
                    stats["missing_keys"][k] += 1

            # Logical constraints
            issues = []
            check_logical_constraints(stats["chart"] or -1, obj, issues)
            for it in issues:
                stats["issues"][it] += 1

            # Dupe detection (coarse)
            key = (obj.get("symbol"), obj.get("ts"), obj.get("seq") or obj.get("md_update_id"))
            if key in seen:
                stats["dupe_keys"] += 1
            else:
                seen.add(key)

            # Price sampling
            pv = obj.get("last_price") or obj.get("price")
            if isinstance(pv, (int,float)) or (isinstance(pv,str) and pv.replace(".","",1).isdigit()):
                try:
                    stats["prices"].append(float(pv))
                except Exception:
                    pass

    # Summaries
    price_summary = summarize_numeric(stats["prices"])
    stats["price_summary"] = price_summary
    stats.pop("prices", None)
    stats["missing_keys"] = dict(stats["missing_keys"])
    stats["issues"] = dict(stats["issues"])
    stats["symbols"] = dict(stats["symbols"])
    return stats

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Directory to scan (project root)")
    ap.add_argument("--out", default="./_dq", help="Output directory for reports")
    ap.add_argument("--max-lines", type=int, default=0, help="Max lines per file (0 = no limit)")
    args = ap.parse_args()

    root = Path(args.root)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    patterns = ["chart_3_*.jsonl", "chart_3_*.jsonl.gz",
                "chart_4_*.jsonl", "chart_4_*.jsonl.gz",
                "chart_8_*.jsonl", "chart_8_*.jsonl.gz",
                "chart_10_*.jsonl", "chart_10_*.jsonl.gz"]

    files = []
    for pat in patterns:
        files.extend(root.glob(pat))

    files = sorted(files)
    if not files:
        print("⚠️  No matching files found at:", root)
        print("   Expected patterns:", ", ".join(patterns))
        sys.exit(0)

    all_stats = []
    agg = defaultdict(int)
    per_chart = defaultdict(lambda: defaultdict(int))

    for fp in files:
        st = scan_file(fp, max_lines=args.max_lines)
        all_stats.append(st)
        # aggregate
        for k in ("lines_total","lines_valid_json","invalid_json","lines_with_ts",
                  "lines_with_symbol","monotonic_ts_violations","dupe_keys"):
            agg[k] += st.get(k,0)
            per_chart[st["chart"]][k] += st.get(k,0)

    # Write JSON report
    report = {
        "root": str(root.resolve()),
        "generated_at": datetime.utcnow().isoformat()+"Z",
        "files_scanned": len(files),
        "aggregate": dict(agg),
        "per_chart_aggregate": {str(k): dict(v) for k,v in per_chart.items()},
        "files": all_stats,
    }
    json_path = out / "data_quality_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Write Markdown report
    md = []
    md.append(f"# MIA Data Quality Report\n")
    md.append(f"- Root: `{report['root']}`")
    md.append(f"- Generated: `{report['generated_at']}`")
    md.append(f"- Files scanned: **{report['files_scanned']}**\n")
    md.append("## Aggregate\n")
    for k,v in agg.items():
        md.append(f"- **{k}**: {v}")
    md.append("\n## Per-Chart Aggregate\n")
    for chart, vals in per_chart.items():
        md.append(f"### Chart {chart}")
        for k,v in vals.items():
            md.append(f"- {k}: {v}")
        md.append("")
    md.append("\n## Files\n")
    for st in all_stats:
        md.append(f"### {st['path']} (chart {st['chart']})")
        md.append(f"- lines_total: {st['lines_total']} | valid_json: {st['lines_valid_json']} | invalid_json: {st['invalid_json']}")
        md.append(f"- with_ts: {st['lines_with_ts']} | with_symbol: {st['lines_with_symbol']}")
        if st.get("first_ts") and st.get("last_ts"):
            md.append(f"- time span: {st['first_ts']} → {st['last_ts']}")
        if st.get("monotonic_ts_violations"):
            md.append(f"- ⚠️ monotonic_ts_violations: {st['monotonic_ts_violations']}")
        if st.get("dupe_keys"):
            md.append(f"- ⚠️ duplicate keys (symbol,ts,seq/md_update_id): {st['dupe_keys']}")
        if st.get("issues"):
            md.append(f"- issues: {json.dumps(st['issues'], ensure_ascii=False)}")
        if st.get("missing_keys"):
            # only print the top few
            mk = dict(sorted(st["missing_keys"].items(), key=lambda x: -x[1])[:8])
            if mk:
                md.append(f"- missing_keys (top): {json.dumps(mk, ensure_ascii=False)}")
        ps = st.get("price_summary")
        if ps: md.append(f"- price_summary: {ps}")
        md.append("")
    md_path = out / "data_quality_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print("✅ Data quality audit complete.")
    print("JSON:", json_path)
    print("MD  :", md_path)

if __name__ == "__main__":
    main()
