#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyseur de distribution des données par graphique
Vérifie ce qui est collecté sur chaque chart
"""

import json
import sys
from collections import defaultdict, Counter

def analyze_chart_distribution(input_file):
    """Analyse la distribution des données par chart"""
    
    print("📊 ANALYSE DE DISTRIBUTION PAR GRAPHIQUE")
    print("=" * 60)
    
    # Compteurs par chart et type de données
    chart_data = defaultdict(lambda: defaultdict(int))
    chart_types = defaultdict(set)
    chart_studies = defaultdict(set)
    
    total_entries = 0
    debug_lines = 0
    
    print("📖 Analyse des données...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
                
            # Ignorer les lignes de debug
            if line.startswith("DEBUG") or line.startswith("SKIP"):
                debug_lines += 1
                continue
                
            try:
                entry = json.loads(line)
                total_entries += 1
                
                # Identifier le chart
                chart = entry.get('chart', 'unknown')
                data_type = entry.get('type', 'unknown')
                study_id = entry.get('study_id')
                
                # Compter par chart et type
                chart_data[chart][data_type] += 1
                chart_types[chart].add(data_type)
                
                if study_id is not None:
                    chart_studies[chart].add(study_id)
                
            except json.JSONDecodeError:
                debug_lines += 1
                continue
            
            # Afficher le progrès
            if line_num % 100000 == 0:
                print(f"   Traité {line_num} lignes...")
    
    # Affichage des résultats
    print(f"\n📈 RÉPARTITION PAR GRAPHIQUE:")
    print(f"   • Total entrées: {total_entries}")
    print(f"   • Lignes debug: {debug_lines}")
    print()
    
    for chart in sorted(chart_data.keys(), key=lambda x: str(x)):
        print(f"🎯 GRAPH {chart}:")
        print(f"   • Types de données: {len(chart_types[chart])}")
        print(f"   • Studies utilisées: {sorted(chart_studies[chart])}")
        print(f"   • Entrées totales: {sum(chart_data[chart].values())}")
        print()
        
        # Détail par type de données
        for data_type, count in sorted(chart_data[chart].items(), key=lambda x: x[1], reverse=True):
            print(f"   ✅ {data_type}: {count} entrées")
        print()
    
    # Analyse des doublons
    print(f"🔍 ANALYSE DES DOUBLONS:")
    
    # Trouver les types présents sur plusieurs charts
    type_to_charts = defaultdict(set)
    for chart, types in chart_types.items():
        for data_type in types:
            type_to_charts[data_type].add(chart)
    
    duplicates = {data_type: charts for data_type, charts in type_to_charts.items() if len(charts) > 1}
    
    if duplicates:
        print(f"   ⚠️  Types présents sur plusieurs charts:")
        for data_type, charts in duplicates.items():
            print(f"      • {data_type}: Charts {sorted(charts)}")
    else:
        print(f"   ✅ Aucun doublon détecté")
    
    print()
    
    # Recommandations
    print(f"💡 RECOMMANDATIONS:")
    
    # Vérifier si tout est sur un seul chart
    single_chart_types = {data_type: charts for data_type, charts in type_to_charts.items() if len(charts) == 1}
    
    if len(single_chart_types) == len(type_to_charts):
        print(f"   ✅ Chaque type de données est sur un seul chart")
    else:
        print(f"   ⚠️  Certains types sont dupliqués sur plusieurs charts")
    
    # Identifier le chart principal
    chart_totals = {chart: sum(data.values()) for chart, data in chart_data.items()}
    main_chart = max(chart_totals, key=chart_totals.get)
    print(f"   📊 Chart principal: {main_chart} ({chart_totals[main_chart]} entrées)")
    
    # Vérifier la complétude
    expected_types = {
        'basedata', 'vwap', 'volume_profile', 'vva', 'vap', 
        'numbers_bars_calculated_values_graph3', 'numbers_bars_calculated_values_graph4',
        'trade', 'depth', 'quote', 'vix', 'ohlc_graph4', 'vwap_current', 'pvwap'
    }
    
    all_types = set()
    for types in chart_types.values():
        all_types.update(types)
    
    missing_types = expected_types - all_types
    if missing_types:
        print(f"   ❌ Types manquants: {missing_types}")
    else:
        print(f"   ✅ Tous les types attendus sont présents")
    
    return chart_data, chart_types, chart_studies

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_chart_data_distribution.py <input_jsonl_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    results = analyze_chart_distribution(input_file)
