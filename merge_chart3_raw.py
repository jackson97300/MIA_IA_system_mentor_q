#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fusionne les JSONL bruts du Chart 3 (vwap, nbcv_metrics, nbcv_footprint, basedata, vva, vix…)
en un seul flux trié par 't' pour alimenter le scorer mia_bullish.
- K-way merge (heapq), lecture streaming -> memory safe
- Filtre uniquement les types utiles
"""

import argparse, json, gzip, heapq, glob
from pathlib import Path
from typing import List, Tuple, Optional, IO

ALLOWED_TYPES = {
	"basedata", "vwap", "pvwap", "vva", "vix",
	"nbcv_footprint", "nbcv_metrics"
}

def open_any(p: Path, mode="rt", encoding="utf-8") -> IO:
	s = str(p)
	if s.lower().endswith(".gz"):
		return gzip.open(s, mode, encoding=encoding)
	return open(s, mode, encoding=encoding)

def iter_valid_events(path: Path):
	"""Itère lignes JSON valides et utiles (Chart 3 + type autorisé + 't')."""
	with open_any(path, "rt") as f:
		for raw in f:
			raw = raw.strip()
			if not raw:
				continue
			try:
				ev = json.loads(raw)
			except Exception:
				continue
			if ev.get("chart") != 3:
				continue
			t = ev.get("t")
			etype = ev.get("type")
			if t is None or etype not in ALLOWED_TYPES:
				continue
			yield float(t), raw

def kway_merge(paths: List[Path], out_path: Path) -> Tuple[int, dict]:
	"""Fusionne par 't' croissant. Retourne (nb_lignes, stats_par_type)."""
	# Prépare un itérateur par fichier
	iters = [iter_valid_events(p) for p in paths]
	heap: List[Tuple[float, int, str]] = []  # (t, idx_fichier, raw_line)

	# amorçage
	for idx, it in enumerate(iters):
		try:
			t, raw = next(it)
			heap.append((t, idx, raw))
		except StopIteration:
			pass
	heapq.heapify(heap)

	out_path.parent.mkdir(parents=True, exist_ok=True)
	stats = {"total": 0}
	with open_any(out_path, "wt") as fo:
		while heap:
			t, idx, raw = heapq.heappop(heap)
			# sortie
			fo.write(raw + "\n")
			stats["total"] += 1
			try:
				etype = json.loads(raw).get("type")
				stats[etype] = stats.get(etype, 0) + 1
			except Exception:
				pass
			# recharge depuis la même source
			try:
				nt, nraw = next(iters[idx])
				heapq.heappush(heap, (nt, idx, nraw))
			except StopIteration:
				pass
	return stats["total"], stats

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--glob", nargs="+",
					default=[r"D:\MIA_IA_system\chart_3_*.jsonl",
							r"D:\MIA_IA_system\chart_3_*.jsonl.gz"],
					help="Patterns des fichiers bruts à fusionner")
	ap.add_argument("--out", default=r"D:\MIA_IA_system\chart_3_combined_full.jsonl",
					help="Fichier de sortie fusionné")
	args = ap.parse_args()

	files = []
	for g in args.glob:
		files.extend(sorted(Path(p) for p in glob.glob(g)))
	if not files:
		print("Aucun fichier trouvé. Vérifie les patterns --glob.", flush=True)
		return

	total, stats = kway_merge(files, Path(args.out))
	print(f"Écrit: {total} lignes -> {args.out}")
	print("Stats:", {k: v for k, v in sorted(stats.items())})

if __name__ == "__main__":
	main()
