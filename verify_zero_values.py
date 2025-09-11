#!/usr/bin/env python3
"""
Vérification générale des valeurs à 0 par graph et subgraph
"""

import json
from collections import defaultdict

def analyze_zero_values(file_path, chart_name):
    """Analyse les valeurs à 0 dans un fichier"""
    print(f"\n{'='*80}")
    print(f"🔍 VÉRIFICATION VALEURS À 0 - {chart_name}")
    print(f"{'='*80}")
    
    zero_values = defaultdict(list)
    total_lines = 0
    data_types = defaultdict(int)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                total_lines += 1
                if line.strip():
                    try:
                        data = json.loads(line.strip())
                        data_type = data.get('type', 'unknown')
                        data_types[data_type] += 1
                        
                        # Analyser les champs numériques
                        for key, value in data.items():
                            if isinstance(value, (int, float)) and value == 0:
                                zero_values[key].append({
                                    'line': line_num,
                                    'type': data_type,
                                    'chart': data.get('chart', 'unknown'),
                                    'study_id': data.get('study_id', 'N/A'),
                                    'subgraph': data.get('subgraph', 'N/A'),
                                    'sg': data.get('sg', 'N/A')
                                })
                    except json.JSONDecodeError:
                        continue
        
        print(f"📁 Fichier: {file_path}")
        print(f"📈 Total lignes: {total_lines:,}")
        
        # Afficher les types de données
        print(f"\n📊 TYPES DE DONNÉES:")
        for dtype, count in sorted(data_types.items()):
            print(f"   • {dtype}: {count:,}")
        
        # Analyser les valeurs à 0
        if zero_values:
            print(f"\n❌ VALEURS À 0 DÉTECTÉES:")
            for field, occurrences in zero_values.items():
                print(f"\n🔸 Champ '{field}': {len(occurrences)} occurrences")
                
                # Grouper par type de données
                by_type = defaultdict(list)
                for occ in occurrences:
                    by_type[occ['type']].append(occ)
                
                for dtype, occs in by_type.items():
                    print(f"   📋 Type '{dtype}': {len(occs)} occurrences")
                    
                    # Grouper par chart/study/subgraph
                    by_chart = defaultdict(list)
                    for occ in occs:
                        chart_key = f"Chart {occ['chart']}"
                        if occ['study_id'] != 'N/A':
                            chart_key += f" Study {occ['study_id']}"
                        if occ['subgraph'] != 'N/A':
                            chart_key += f" SG {occ['subgraph']}"
                        elif occ['sg'] != 'N/A':
                            chart_key += f" SG {occ['sg']}"
                        by_chart[chart_key].append(occ)
                    
                    for chart_key, chart_occs in by_chart.items():
                        print(f"      • {chart_key}: {len(chart_occs)} occurrences")
                        if len(chart_occs) <= 5:  # Afficher les détails si peu d'occurrences
                            for occ in chart_occs[:3]:
                                print(f"        - Ligne {occ['line']}: {occ}")
                        else:
                            print(f"        - Premières 3 lignes: {[occ['line'] for occ in chart_occs[:3]]}")
        else:
            print(f"\n✅ Aucune valeur à 0 détectée")
        
        return zero_values, data_types
        
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {file_path}")
        return None, None
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        return None, None

def main():
    """Analyse principale"""
    files = [
        ("chart_3_20250910.jsonl", "CHART 3"),
        ("chart_4_20250910.jsonl", "CHART 4"), 
        ("chart_10_20250910.jsonl", "CHART 10")
    ]
    
    all_results = {}
    
    for file_path, chart_name in files:
        zero_vals, data_types = analyze_zero_values(file_path, chart_name)
        if zero_vals is not None:
            all_results[chart_name] = {
                'zero_values': zero_vals,
                'data_types': data_types
            }
    
    # Résumé global
    print(f"\n{'='*100}")
    print(f"📋 RÉSUMÉ GLOBAL - VALEURS À 0")
    print(f"{'='*100}")
    
    global_zero_fields = defaultdict(list)
    
    for chart_name, results in all_results.items():
        for field, occurrences in results['zero_values'].items():
            global_zero_fields[field].extend([(chart_name, len(occurrences))])
    
    if global_zero_fields:
        print(f"\n🔍 CHAMPS AVEC VALEURS À 0:")
        for field, chart_counts in global_zero_fields.items():
            total_zeros = sum(count for _, count in chart_counts)
            print(f"\n📌 '{field}': {total_zeros} occurrences total")
            for chart_name, count in chart_counts:
                print(f"   • {chart_name}: {count} occurrences")
    else:
        print(f"\n✅ Aucune valeur à 0 détectée dans tous les fichiers")

if __name__ == "__main__":
    main()
