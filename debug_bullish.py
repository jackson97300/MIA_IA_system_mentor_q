#!/usr/bin/env python3
import json
from collections import defaultdict

# Analyser le fichier combiné
bars = defaultdict(dict)
types_found = set()

with open('chart_3_combined_20250911.jsonl', 'r') as f:
    for line in f:
        try:
            ev = json.loads(line.strip())
            ev_type = ev.get('type')
            chart = ev.get('chart')
            i = ev.get('i')
            
            types_found.add(ev_type)
            
            if chart == 3 and i is not None:
                bars[i][ev_type] = ev
                
        except:
            continue

print("Types d'événements trouvés:", sorted(types_found))
print(f"Nombre de barres: {len(bars)}")

# Vérifier les conditions pour les premières barres
for i in sorted(bars.keys())[:5]:
    bar = bars[i]
    print(f"\nBarre {i}:")
    print(f"  basedata: {'close' in bar.get('basedata', {})}")
    print(f"  vwap: {'v' in bar.get('vwap', {})}")
    print(f"  nbcv_footprint: {'delta_ratio' in bar.get('nbcv_footprint', {})}")
    
    # Vérifier les valeurs
    if 'basedata' in bar:
        print(f"    close: {bar['basedata'].get('c')}")
    if 'vwap' in bar:
        print(f"    vwap: {bar['vwap'].get('v')}")
    if 'nbcv_footprint' in bar:
        print(f"    delta_ratio: {bar['nbcv_footprint'].get('delta_ratio')}")
        print(f"    pressure: {bar['nbcv_footprint'].get('pressure')}")

# Compter les barres complètes
complete_bars = 0
for i, bar in bars.items():
    if ('basedata' in bar and 'vwap' in bar and 'nbcv_footprint' in bar):
        complete_bars += 1

print(f"\nBarres complètes (basedata + vwap + nbcv_footprint): {complete_bars}")
