#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyseur de complétude des données MIA
Vérifie si toutes les données nécessaires sont collectées
"""

import json
import sys
from collections import defaultdict, Counter
from datetime import datetime

def analyze_data_completeness(input_file):
    """Analyse la complétude des données collectées"""
    
    print("🔍 ANALYSE DE COMPLÉTUDE DES DONNÉES MIA")
    print("=" * 60)
    
    # Compteurs par type de données
    data_types = Counter()
    chart_sources = Counter()
    study_ids = Counter()
    debug_lines = 0
    valid_entries = 0
    price_anomalies = 0
    
    # Données attendues selon votre spécification
    expected_data_types = {
        # Graph 3
        "basedata": "OHLCV + Bid/Ask Volume",
        "vwap": "VWAP + Bandes (Study ID=22)",
        "volume_profile": "POC/VAH/VAL (Study ID=0)",
        "vva": "Volume Value Area",
        "vap": "Volume à Prix",
        "numbers_bars_calculated_values_graph3": "NBCV Graph 3 (Study ID=33)",
        "trade": "Transactions (source: basedata)",
        
        # Graph 4
        "pvwap": "VWAP Previous (Study ID=13)",
        "ohlc_graph4": "OHLC Graph 4",
        "numbers_bars_calculated_values_graph4": "NBCV Graph 4 (Study ID=14)",
        "depth": "DOM 20 niveaux",
        "quote": "BIDASK temps réel",
        "vwap_current": "VWAP Current (Study ID=1)",
        "vwap_previous": "VWAP Previous (Study ID=13)",
        
        # Graph 8
        "vix": "VIX temps réel (Study ID=830)"
    }
    
    # Analyse des fichiers par chunks pour éviter les problèmes de mémoire
    print("📖 Lecture du fichier...")
    chunk_size = 10000
    processed_lines = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        while True:
            chunk = []
            for _ in range(chunk_size):
                line = f.readline()
                if not line:
                    break
                chunk.append(line.strip())
            
            if not chunk:
                break
                
            for line in chunk:
                processed_lines += 1
                if not line:
                    continue
                    
                # Compter les lignes de debug
                if line.startswith("DEBUG") or line.startswith("SKIP"):
                    debug_lines += 1
                    continue
                    
                try:
                    entry = json.loads(line)
                    valid_entries += 1
                    
                    # Analyser le type de données
                    data_type = entry.get("type", "unknown")
                    data_types[data_type] += 1
                    
                    # Analyser la source (chart)
                    chart = entry.get("chart", "unknown")
                    chart_sources[chart] += 1
                    
                    # Analyser les Study IDs
                    study_id = entry.get("study_id")
                    if study_id is not None:
                        study_ids[study_id] += 1
                    
                    # Détecter les anomalies de prix
                    price_fields = ["px", "bid", "ask", "o", "h", "l", "c", "price"]
                    for field in price_fields:
                        if field in entry:
                            price = entry[field]
                            if isinstance(price, (int, float)) and price > 100000:
                                price_anomalies += 1
                                break
                                
                except json.JSONDecodeError:
                    debug_lines += 1
                    continue
            
            # Afficher le progrès
            if processed_lines % 50000 == 0:
                print(f"   Traité {processed_lines} lignes...")
    
    line_num = processed_lines
    
    # Affichage des résultats
    print(f"📊 STATISTIQUES GÉNÉRALES:")
    print(f"   • Lignes totales: {line_num}")
    print(f"   • Entrées valides: {valid_entries}")
    print(f"   • Lignes debug: {debug_lines}")
    print(f"   • Anomalies prix: {price_anomalies}")
    print()
    
    print(f"📈 RÉPARTITION PAR CHART:")
    for chart, count in chart_sources.most_common():
        print(f"   • Chart {chart}: {count} entrées")
    print()
    
    print(f"🔬 TYPES DE DONNÉES COLLECTÉES:")
    for data_type, count in data_types.most_common():
        expected_desc = expected_data_types.get(data_type, "❓ Type non documenté")
        status = "✅" if data_type in expected_data_types else "⚠️"
        print(f"   {status} {data_type}: {count} entrées - {expected_desc}")
    print()
    
    print(f"🎯 STUDY IDs UTILISÉS:")
    for study_id, count in study_ids.most_common():
        print(f"   • Study ID {study_id}: {count} entrées")
    print()
    
    # Vérification de complétude
    print(f"✅ VÉRIFICATION DE COMPLÉTUDE:")
    missing_types = []
    for expected_type, description in expected_data_types.items():
        if expected_type in data_types:
            count = data_types[expected_type]
            print(f"   ✅ {expected_type}: {count} entrées - {description}")
        else:
            missing_types.append(expected_type)
            print(f"   ❌ {expected_type}: MANQUANT - {description}")
    
    print()
    if missing_types:
        print(f"⚠️  TYPES MANQUANTS: {', '.join(missing_types)}")
    else:
        print(f"🎉 TOUS LES TYPES DE DONNÉES SONT PRÉSENTS!")
    
    # Analyse spécifique des problèmes
    print(f"\n🔧 ANALYSE DES PROBLÈMES:")
    
    # Problème NBCV Graph 3
    nbcv_graph3 = data_types.get("numbers_bars_calculated_values_graph3", 0)
    if nbcv_graph3 == 0:
        print(f"   ❌ NBCV Graph 3: AUCUNE DONNÉE COLLECTÉE")
        print(f"      → Vérifier Study ID=33 et mapping des subgraphs")
    else:
        print(f"   ✅ NBCV Graph 3: {nbcv_graph3} entrées collectées")
    
    # Problème des prix anormaux
    if price_anomalies > 0:
        print(f"   ⚠️  Prix anormaux: {price_anomalies} entrées avec prix > 100000")
        print(f"      → Problème de normalisation des prix (NormalizePx)")
        print(f"      → Solution: Recompiler le DLL C++ et redémarrer Sierra Chart")
    
    # Problème des lignes debug
    if debug_lines > valid_entries * 0.1:  # Plus de 10% de debug
        print(f"   ⚠️  Trop de lignes debug: {debug_lines} ({debug_lines/(debug_lines+valid_entries)*100:.1f}%)")
        print(f"      → Nettoyer les messages DEBUG_NBCV_RESULT et autres")
    
    print(f"\n📋 RÉSUMÉ EXÉCUTIF:")
    print(f"   • Données collectées: {len(data_types)} types différents")
    print(f"   • Charts actifs: {len(chart_sources)}")
    print(f"   • Studies utilisées: {len(study_ids)}")
    print(f"   • Qualité: {'🟢 BONNE' if price_anomalies == 0 and len(missing_types) == 0 else '🟡 À AMÉLIORER'}")
    
    return {
        'data_types': dict(data_types),
        'chart_sources': dict(chart_sources),
        'study_ids': dict(study_ids),
        'missing_types': missing_types,
        'price_anomalies': price_anomalies,
        'debug_lines': debug_lines,
        'valid_entries': valid_entries
    }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_data_completeness.py <input_jsonl_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    results = analyze_data_completeness(input_file)
