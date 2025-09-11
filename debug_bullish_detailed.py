#!/usr/bin/env python3
import json
from core.mia_bullish import BullishScorer

# Créer un scorer pour debug
scorer = BullishScorer(chart_id=3, use_vix=True)

# Lire le fichier combiné et tester chaque ligne
with open('chart_3_combined_20250911.jsonl', 'r') as f:
    for i, line in enumerate(f):
        if i > 100:  # Limiter à 100 lignes pour debug
            break
            
        try:
            ev = json.loads(line.strip())
            ev_type = ev.get('type')
            chart = ev.get('chart')
            
            print(f"Ligne {i}: type={ev_type}, chart={chart}")
            
            if chart == 3:
                result = scorer.ingest(ev)
                if result:
                    print(f"  -> SCORE GÉNÉRÉ: {result}")
                    break
                else:
                    print(f"  -> Pas de score (données insuffisantes)")
                    
        except Exception as e:
            print(f"Erreur ligne {i}: {e}")
            continue

# Afficher l'état du scorer
print(f"\nÉtat du scorer:")
print(f"  Nombre de barres: {len(scorer.bars)}")
for i, bar in list(scorer.bars.items())[:3]:
    print(f"  Barre {i}: close={bar.close}, vwap={bar.vwap}, delta_ratio={bar.delta_ratio}, pressure={bar.pressure}")
