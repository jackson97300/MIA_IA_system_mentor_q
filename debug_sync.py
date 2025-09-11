#!/usr/bin/env python3
import json
from collections import defaultdict

# Analyser la synchronisation des timestamps
timestamps = defaultdict(list)
bar_indices = defaultdict(list)

print("=== ANALYSE DE SYNCHRONISATION ===")

with open('chart_3_combined_20250911.jsonl', 'r') as f:
    for line_num, line in enumerate(f):
        if line_num > 1000:  # Limiter pour debug
            break
            
        try:
            ev = json.loads(line.strip())
            ev_type = ev.get('type')
            chart = ev.get('chart')
            t = ev.get('t')
            i = ev.get('i')
            
            if chart == 3 and t is not None and i is not None:
                timestamps[t].append((ev_type, i))
                bar_indices[i].append((ev_type, t))
                
        except:
            continue

print(f"Timestamps uniques: {len(timestamps)}")
print(f"Index de barres uniques: {len(bar_indices)}")

# Vérifier les premiers timestamps
print("\n=== PREMIERS TIMESTAMPS ===")
for t in sorted(timestamps.keys())[:5]:
    events = timestamps[t]
    print(f"t={t}: {events}")

# Vérifier les premiers index de barres
print("\n=== PREMIERS INDEX DE BARRES ===")
for i in sorted(bar_indices.keys())[:5]:
    events = bar_indices[i]
    print(f"i={i}: {events}")

# Trouver les barres avec basedata ET nbcv_footprint
print("\n=== BARRES COMPLÈTES ===")
complete_bars = 0
for i, events in bar_indices.items():
    types = [ev_type for ev_type, _ in events]
    if 'basedata' in types and 'nbcv_footprint' in types and 'vwap' in types:
        complete_bars += 1
        if complete_bars <= 3:  # Afficher les 3 premières
            print(f"Barre {i}: {types}")

print(f"\nTotal barres complètes: {complete_bars}")

# Vérifier la cohérence des timestamps par barre
print("\n=== VÉRIFICATION COHÉRENCE ===")
for i in sorted(bar_indices.keys())[:3]:
    events = bar_indices[i]
    types = [ev_type for ev_type, _ in events]
    timestamps_bar = [t for _, t in events]
    
    print(f"Barre {i}:")
    print(f"  Types: {types}")
    print(f"  Timestamps: {timestamps_bar}")
    print(f"  Cohérent: {len(set(timestamps_bar)) == 1}")
