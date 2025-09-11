#!/usr/bin/env python3
"""
Script de reconstruction du fichier combined Chart 3
Fusionne tous les fichiers spécialisés dans l'ordre chronologique
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

def load_events_from_file(filepath):
    """Charge tous les événements d'un fichier JSONL"""
    events = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    events.append(event)
                except json.JSONDecodeError as e:
                    print(f"Erreur JSON ligne {line_num} dans {filepath}: {e}")
                    continue
    except FileNotFoundError:
        print(f"Fichier non trouvé: {filepath}")
        return []
    
    print(f"Chargé {len(events)} événements depuis {filepath}")
    return events

def main():
    # Fichiers à fusionner
    files_to_merge = [
        'chart_3_basedata_20250911.jsonl',
        'chart_3_vwap_20250911.jsonl', 
        'chart_3_nbcv_20250911.jsonl',
        'chart_3_cumulative_delta_20250911.jsonl',
        'chart_3_vva_20250911.jsonl',
        'chart_3_depth_20250911.jsonl',
        'chart_3_quote_20250911.jsonl'
    ]
    
    print("=== RECONSTRUCTION CHART 3 COMBINED ===")
    
    # Charger tous les événements
    all_events = []
    for filepath in files_to_merge:
        if Path(filepath).exists():
            events = load_events_from_file(filepath)
            all_events.extend(events)
        else:
            print(f"⚠️  Fichier manquant: {filepath}")
    
    print(f"Total événements chargés: {len(all_events)}")
    
    # Trier par timestamp puis par type (pour stabilité)
    def sort_key(event):
        t = event.get('t', 0)
        event_type = event.get('type', '')
        # Ordre de priorité des types pour même timestamp
        type_order = {
            'basedata': 0,
            'vwap': 1, 
            'nbcv_footprint': 2,
            'nbcv_metrics': 3,
            'vva': 4,
            'depth': 5,
            'quote': 6,
            'trade': 7
        }
        return (t, type_order.get(event_type, 999))
    
    all_events.sort(key=sort_key)
    
    # Statistiques par type
    type_counts = defaultdict(int)
    for event in all_events:
        type_counts[event.get('type', 'unknown')] += 1
    
    print("\n=== STATISTIQUES PAR TYPE ===")
    for event_type, count in sorted(type_counts.items()):
        print(f"{event_type}: {count}")
    
    # Vérifier les barres complètes
    bar_data = defaultdict(set)
    for event in all_events:
        if event.get('chart') == 3 and event.get('i') is not None:
            bar_idx = event['i']
            event_type = event.get('type')
            bar_data[bar_idx].add(event_type)
    
    complete_bars = 0
    for bar_idx, types in bar_data.items():
        if 'basedata' in types and 'vwap' in types and 'nbcv_footprint' in types:
            complete_bars += 1
    
    print(f"\n=== BARRES COMPLÈTES ===")
    print(f"Barres avec basedata + vwap + nbcv_footprint: {complete_bars}")
    print(f"Total barres uniques: {len(bar_data)}")
    
    # Écrire le fichier reconstruit
    output_file = 'chart_3_combined_rebuilt_20250911.jsonl'
    print(f"\n=== ÉCRITURE ===")
    print(f"Écriture vers: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for event in all_events:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
    
    print(f"✅ Fichier reconstruit: {output_file}")
    print(f"Total lignes écrites: {len(all_events)}")
    
    # Test rapide avec mia_bullish
    print(f"\n=== TEST MIA_BULLISH ===")
    print("Test du module sur les 100 premières lignes...")
    
    try:
        from core.mia_bullish import BullishScorer
        
        scorer = BullishScorer(chart_id=3, use_vix=False)
        bullish_events = 0
        
        with open(output_file, 'r') as f:
            for i, line in enumerate(f):
                if i >= 100:  # Test sur 100 lignes
                    break
                try:
                    event = json.loads(line.strip())
                    result = scorer.ingest(event)
                    if result and result.get('type') == 'mia_bullish':
                        bullish_events += 1
                except:
                    continue
        
        print(f"Événements mia_bullish générés: {bullish_events}")
        if bullish_events > 0:
            print("✅ Le module fonctionne correctement !")
        else:
            print("⚠️  Aucun score généré - vérifier les données")
            
    except ImportError as e:
        print(f"⚠️  Impossible d'importer mia_bullish: {e}")
    except Exception as e:
        print(f"⚠️  Erreur lors du test: {e}")

if __name__ == "__main__":
    main()
