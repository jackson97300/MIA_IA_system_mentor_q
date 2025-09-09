#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyseur de doublons et déduplicateur
Compare chart_3 et chart_4 pour éliminer les doublons
"""

import json
import sys
from collections import defaultdict, Counter
from datetime import datetime

def analyze_duplicates_between_charts():
    """Analyse les doublons entre chart_3 et chart_4"""
    
    print("🔍 ANALYSE DES DOUBLONS ENTRE CHART_3 ET CHART_4")
    print("=" * 60)
    
    # Dictionnaires pour stocker les données par chart
    chart3_data = defaultdict(list)
    chart4_data = defaultdict(list)
    
    # Compteurs
    chart3_total = 0
    chart4_total = 0
    chart3_debug = 0
    chart4_debug = 0
    
    print("📖 Analyse de chart_3_20250905.jsonl...")
    
    # Analyser chart_3
    with open("chart_3_20250905.jsonl", 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("DEBUG") or line.startswith("SKIP"):
                chart3_debug += 1
                continue
                
            try:
                entry = json.loads(line)
                chart3_total += 1
                
                data_type = entry.get('type', 'unknown')
                timestamp = entry.get('t')
                symbol = entry.get('sym', 'UNKNOWN')
                bar_index = entry.get('i') or entry.get('bar')
                
                # Créer une clé unique pour identifier les doublons
                key = f"{timestamp}_{symbol}_{bar_index}_{data_type}"
                chart3_data[data_type].append({
                    'key': key,
                    'timestamp': timestamp,
                    'symbol': symbol,
                    'bar_index': bar_index,
                    'chart': entry.get('chart', 3),
                    'data': entry
                })
                
            except json.JSONDecodeError:
                chart3_debug += 1
                continue
            
            if line_num % 100000 == 0:
                print(f"   Chart 3: {line_num} lignes traitées...")
    
    print(f"   ✅ Chart 3: {chart3_total} entrées, {chart3_debug} debug")
    
    print("\n📖 Analyse de chart_4_20250905.jsonl...")
    
    # Analyser chart_4
    with open("chart_4_20250905.jsonl", 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("DEBUG") or line.startswith("SKIP"):
                chart4_debug += 1
                continue
                
            try:
                entry = json.loads(line)
                chart4_total += 1
                
                data_type = entry.get('type', 'unknown')
                timestamp = entry.get('t')
                symbol = entry.get('sym', 'UNKNOWN')
                bar_index = entry.get('i') or entry.get('bar')
                
                # Créer une clé unique pour identifier les doublons
                key = f"{timestamp}_{symbol}_{bar_index}_{data_type}"
                chart4_data[data_type].append({
                    'key': key,
                    'timestamp': timestamp,
                    'symbol': symbol,
                    'bar_index': bar_index,
                    'chart': entry.get('chart', 4),
                    'data': entry
                })
                
            except json.JSONDecodeError:
                chart4_debug += 1
                continue
            
            if line_num % 100000 == 0:
                print(f"   Chart 4: {line_num} lignes traitées...")
    
    print(f"   ✅ Chart 4: {chart4_total} entrées, {chart4_debug} debug")
    
    # Analyser les doublons
    print(f"\n🔄 ANALYSE DES DOUBLONS:")
    
    all_types = set(chart3_data.keys()) | set(chart4_data.keys())
    duplicates_found = {}
    unique_chart3 = {}
    unique_chart4 = {}
    
    for data_type in all_types:
        chart3_entries = chart3_data.get(data_type, [])
        chart4_entries = chart4_data.get(data_type, [])
        
        # Créer des sets de clés pour chaque chart
        chart3_keys = {entry['key'] for entry in chart3_entries}
        chart4_keys = {entry['key'] for entry in chart4_entries}
        
        # Trouver les doublons (clés présentes dans les deux charts)
        duplicates = chart3_keys & chart4_keys
        
        if duplicates:
            duplicates_found[data_type] = {
                'count': len(duplicates),
                'chart3_total': len(chart3_entries),
                'chart4_total': len(chart4_entries),
                'duplicate_keys': list(duplicates)[:5]  # Afficher les 5 premiers
            }
        
        # Entrées uniques à chaque chart
        unique_chart3[data_type] = len(chart3_keys - chart4_keys)
        unique_chart4[data_type] = len(chart4_keys - chart3_keys)
    
    # Affichage des résultats
    print(f"\n📊 RÉSULTATS DE L'ANALYSE:")
    print(f"   • Types de données analysés: {len(all_types)}")
    print(f"   • Types avec doublons: {len(duplicates_found)}")
    print(f"   • Total Chart 3: {chart3_total} entrées")
    print(f"   • Total Chart 4: {chart4_total} entrées")
    
    if duplicates_found:
        print(f"\n⚠️  DOUBLONS DÉTECTÉS:")
        for data_type, info in duplicates_found.items():
            print(f"   • {data_type}:")
            print(f"     - Doublons: {info['count']}")
            print(f"     - Chart 3: {info['chart3_total']} entrées")
            print(f"     - Chart 4: {info['chart4_total']} entrées")
            print(f"     - Exemples: {info['duplicate_keys'][:3]}")
    else:
        print(f"\n✅ AUCUN DOUBLON DÉTECTÉ!")
    
    print(f"\n📈 DONNÉES UNIQUES PAR CHART:")
    for data_type in sorted(all_types):
        chart3_unique = unique_chart3.get(data_type, 0)
        chart4_unique = unique_chart4.get(data_type, 0)
        duplicates = duplicates_found.get(data_type, {}).get('count', 0)
        
        if chart3_unique > 0 or chart4_unique > 0 or duplicates > 0:
            print(f"   • {data_type}:")
            if chart3_unique > 0:
                print(f"     - Chart 3 unique: {chart3_unique}")
            if chart4_unique > 0:
                print(f"     - Chart 4 unique: {chart4_unique}")
            if duplicates > 0:
                print(f"     - Doublons: {duplicates}")
    
    return chart3_data, chart4_data, duplicates_found, unique_chart3, unique_chart4

def create_deduplicated_output(chart3_data, chart4_data, duplicates_found, output_file):
    """Crée un fichier de sortie sans doublons"""
    
    print(f"\n💾 CRÉATION DU FICHIER SANS DOUBLONS...")
    
    # Stratégie de déduplication: garder la version la plus récente ou la plus complète
    unified_data = {}
    
    # Traiter Chart 3
    for data_type, entries in chart3_data.items():
        for entry in entries:
            key = entry['key']
            if key not in unified_data:
                unified_data[key] = entry
            else:
                # Si doublon, garder la version la plus complète
                existing = unified_data[key]
                if len(str(entry['data'])) > len(str(existing['data'])):
                    unified_data[key] = entry
    
    # Traiter Chart 4
    for data_type, entries in chart4_data.items():
        for entry in entries:
            key = entry['key']
            if key not in unified_data:
                unified_data[key] = entry
            else:
                # Si doublon, garder la version la plus complète
                existing = unified_data[key]
                if len(str(entry['data'])) > len(str(existing['data'])):
                    unified_data[key] = entry
    
    # Convertir en liste et trier par timestamp
    clean_entries = list(unified_data.values())
    clean_entries.sort(key=lambda x: x['timestamp'])
    
    # Sauvegarder
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in clean_entries:
            f.write(json.dumps(entry['data'], ensure_ascii=False) + '\n')
    
    print(f"✅ Fichier sans doublons créé: {output_file}")
    print(f"   • {len(clean_entries)} entrées uniques")
    print(f"   • Doublons éliminés")
    print(f"   • Données triées par timestamp")
    
    return len(clean_entries)

def main():
    """Fonction principale"""
    
    # Analyser les doublons
    chart3_data, chart4_data, duplicates_found, unique_chart3, unique_chart4 = analyze_duplicates_between_charts()
    
    # Créer le fichier sans doublons
    output_file = "mia_deduplicated_clean.jsonl"
    count = create_deduplicated_output(chart3_data, chart4_data, duplicates_found, output_file)
    
    # Statistiques finales
    print(f"\n📋 RÉSUMÉ FINAL:")
    print(f"   • Fichier de sortie: {output_file}")
    print(f"   • Entrées uniques: {count}")
    print(f"   • Doublons éliminés: {len(duplicates_found)} types")
    print(f"   • Format: JSONL propre pour MIA")
    
    print(f"\n🎉 DÉDUPLICATION TERMINÉE!")

if __name__ == "__main__":
    main()

