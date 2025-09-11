#!/usr/bin/env python3
import json
from collections import defaultdict

def analyze_chart_data(filename, chart_num):
    print(f'=== ANALYSE CHART {chart_num} ===')
    types_count = defaultdict(int)
    chart_sources = defaultdict(int)
    total_lines = 0
    
    with open(filename, 'r') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                total_lines += 1
                
                # Compter les types
                data_type = data.get('type', 'unknown')
                types_count[data_type] += 1
                
                # Compter les sources de chart
                chart = data.get('chart', 'unknown')
                chart_sources[chart] += 1
                
            except json.JSONDecodeError:
                continue
    
    print(f'Total lignes: {total_lines}')
    print(f'Types de données:')
    for t, c in sorted(types_count.items()):
        print(f'  {t}: {c}')
    
    print(f'Sources de chart:')
    for c, count in sorted(chart_sources.items(), key=lambda x: (isinstance(x[0], str), x[0])):
        print(f'  Chart {c}: {count}')
    
    return types_count, chart_sources

# Analyser les fichiers
chart3_types, chart3_sources = analyze_chart_data('chart_3_20250910.jsonl', 3)
chart4_types, chart4_sources = analyze_chart_data('chart_4_20250910.jsonl', 4)

print('\n=== RÉFLEXION ARCHITECTURALE ===')
print('Problèmes identifiés:')
print('1. Chart 3 collecte TOUT (3, 4, 8, 10) - violation du principe de responsabilité unique')
print('2. Duplication excessive des données (même timestamp, séquences multiples)')
print('3. Un seul gros fichier par chart au lieu de fichiers spécialisés')
print('4. Chart 8 (VIX) ne collecte que le prix, mais Chart 3 le fait aussi')
