#!/usr/bin/env python3
import json
from pathlib import Path

INPUT = 'chart_3_combined_rebuilt_20250911.jsonl'

try:
	from core.mia_bullish import BullishScorer
except Exception as e:
	print(f"Erreur import BullishScorer: {e}")
	raise


def maybe_emit_metrics(ev):
	"""Crée un évènement nbcv_metrics dérivé depuis nbcv_footprint si utile."""
	if ev.get('type') != 'nbcv_footprint':
		return None
	dr = ev.get('delta_ratio')
	bull = ev.get('pressure_bullish')
	bear = ev.get('pressure_bearish')
	if dr is None and not bull and not bear:
		return None
	return {
		"t": ev.get("t"),
		"type": "nbcv_metrics",
		"chart": ev.get("chart"),
		"i": ev.get("i"),
		"delta_ratio": dr,
		"pressure_bullish": 1 if bull else 0,
		"pressure_bearish": 1 if bear else 0
	}


def main():
	scorer = BullishScorer(chart_id=3, use_vix=False)
	in_path = Path(INPUT)
	if not in_path.exists():
		print(f"Fichier introuvable: {INPUT}")
		return

	produced = 0
	checked = 0
	first_examples = []

	with in_path.open('r', encoding='utf-8') as f:
		for line in f:
			checked += 1
			try:
				ev = json.loads(line)
			except Exception:
				continue

			out = scorer.ingest(ev)
			if out is not None and out.get('type') == 'mia_bullish':
				produced += 1
				if len(first_examples) < 5:
					first_examples.append(out)

			# Injecter un metrics dérivé si footprint contient déjà les champs
			alt = maybe_emit_metrics(ev)
			if alt is not None:
				out2 = scorer.ingest(alt)
				if out2 is not None and out2.get('type') == 'mia_bullish':
					produced += 1
					if len(first_examples) < 5:
						first_examples.append(out2)

	print(f"Lignes lues: {checked}")
	print(f"mia_bullish produits: {produced}")
	for ex in first_examples:
		print(json.dumps(ex, ensure_ascii=False))


if __name__ == '__main__':
	main()
