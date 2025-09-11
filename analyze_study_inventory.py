#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from collections import defaultdict, Counter

def analyze_study_inventory(filename):
    """Analyse l'inventaire des études du Chart 3"""
    
    print(f"=== ANALYSE INVENTAIRE CHART 3 ===\n")
    
    studies = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                studies.append(json.loads(line))
    
    print(f"📊 **RÉSUMÉ GÉNÉRAL**")
    print(f"Total d'études détectées: {len(studies)}")
    print(f"Fichier analysé: {filename}\n")
    
    # === ANALYSE PAR TYPE D'ÉTUDE ===
    print("🔍 **ANALYSE PAR TYPE D'ÉTUDE**")
    
    # Catégorisation des études
    categories = {
        'VWAP': [],
        'Volume Value Area': [],
        'Numbers Bars (NBCV)': [],
        'VIX': [],
        'Edge Zones/Imbalance': [],
        'Alert Systems': [],
        'News/Time': [],
        'Trading': [],
        'Other': []
    }
    
    for study in studies:
        name = study['name'].lower()
        study_id = study['study_id']
        
        if 'vwap' in name:
            categories['VWAP'].append(study)
        elif 'volume value area' in name:
            categories['Volume Value Area'].append(study)
        elif 'numbers bars' in name:
            categories['Numbers Bars (NBCV)'].append(study)
        elif 'vix' in name:
            categories['VIX'].append(study)
        elif 'edge zones' in name or 'imbalance' in name:
            categories['Edge Zones/Imbalance'].append(study)
        elif '[as]' in name or '[av]' in name or 'alert' in name:
            categories['Alert Systems'].append(study)
        elif 'news' in name or '07.' in name or '08.' in name or '09.' in name:
            categories['News/Time'].append(study)
        elif 'trading' in name or 'position' in name or 'profit' in name:
            categories['Trading'].append(study)
        else:
            categories['Other'].append(study)
    
    for category, studies_list in categories.items():
        if studies_list:
            print(f"\n**{category}** ({len(studies_list)} études):")
            for study in studies_list:
                print(f"  - ID {study['study_id']:2d}: {study['name']}")
    
    # === ANALYSE DES SUBGRAPHS ===
    print(f"\n📈 **ANALYSE DES SUBGRAPHS**")
    
    total_subgraphs = sum(study['n_subgraphs'] for study in studies)
    avg_subgraphs = total_subgraphs / len(studies) if studies else 0
    
    print(f"Total de subgraphs: {total_subgraphs}")
    print(f"Moyenne par étude: {avg_subgraphs:.1f}")
    
    # Top 5 des études avec le plus de subgraphs
    top_subgraphs = sorted(studies, key=lambda x: x['n_subgraphs'], reverse=True)[:5]
    print(f"\nTop 5 des études avec le plus de subgraphs:")
    for study in top_subgraphs:
        print(f"  - {study['name']}: {study['n_subgraphs']} subgraphs")
    
    # === MAPPING POUR L'ARCHITECTURE MULTI-CHART ===
    print(f"\n🏗️ **MAPPING POUR L'ARCHITECTURE MULTI-CHART**")
    
    # Études importantes pour la collecte
    important_studies = {
        'VWAP': None,
        'Volume Value Area Current': None,
        'Volume Value Area Previous': None,
        'Numbers Bars Calculated Values': None,
        'VIX': None,
        'Cumulative Delta': None
    }
    
    for study in studies:
        name = study['name'].lower()
        study_id = study['study_id']
        
        if 'vwap' in name and 'alert' not in name:
            important_studies['VWAP'] = study_id
        elif 'volume value area' in name and 'previous' not in name:
            important_studies['Volume Value Area Current'] = study_id
        elif 'volume value area' in name and 'previous' in name:
            important_studies['Volume Value Area Previous'] = study_id
        elif 'numbers bars calculated values' in name:
            important_studies['Numbers Bars Calculated Values'] = study_id
        elif 'vix' in name:
            important_studies['VIX'] = study_id
        elif 'cumulative delta' in name:
            important_studies['Cumulative Delta'] = study_id
    
    print("Études importantes identifiées:")
    for name, study_id in important_studies.items():
        if study_id:
            print(f"  ✅ {name}: ID {study_id}")
        else:
            print(f"  ❌ {name}: Non trouvée")
    
    # === CONFIGURATION RECOMMANDÉE ===
    print(f"\n⚙️ **CONFIGURATION RECOMMANDÉE POUR MIA_Dumper_G3_Core**")
    
    config = {
        'VWAP Study ID': important_studies['VWAP'] or 22,  # VWAP par défaut
        'VVA Current Study ID': important_studies['Volume Value Area Current'] or 1,
        'VVA Previous Study ID': important_studies['Volume Value Area Previous'] or 2,
        'NBCV Study ID': important_studies['Numbers Bars Calculated Values'] or 33,
        'VIX Study ID': important_studies['VIX'] or 23,
        'Cumulative Delta Study ID': important_studies['Cumulative Delta'] or 32
    }
    
    print("Inputs recommandés:")
    for name, value in config.items():
        print(f"  {name}: {value}")
    
    # === ALERTES ET RECOMMANDATIONS ===
    print(f"\n🚨 **ALERTES ET RECOMMANDATIONS**")
    
    # Vérifier les conflits d'IDs
    study_ids = [study['study_id'] for study in studies]
    duplicates = [id for id in study_ids if study_ids.count(id) > 1]
    if duplicates:
        print(f"⚠️  IDs dupliqués détectés: {set(duplicates)}")
    else:
        print("✅ Aucun ID dupliqué détecté")
    
    # Vérifier les études manquantes
    missing = [name for name, study_id in important_studies.items() if not study_id]
    if missing:
        print(f"⚠️  Études importantes manquantes: {missing}")
    else:
        print("✅ Toutes les études importantes sont présentes")
    
    # Recommandations de nettoyage
    print(f"\n🧹 **RECOMMANDATIONS DE NETTOYAGE**")
    
    # Compter les études par type
    edge_zones_count = len(categories['Edge Zones/Imbalance'])
    alert_systems_count = len(categories['Alert Systems'])
    news_count = len(categories['News/Time'])
    
    if edge_zones_count > 10:
        print(f"⚠️  Trop d'études Edge Zones ({edge_zones_count}). Considérez la consolidation.")
    
    if alert_systems_count > 15:
        print(f"⚠️  Trop d'études Alert Systems ({alert_systems_count}). Considérez la consolidation.")
    
    if news_count > 5:
        print(f"⚠️  Trop d'études News ({news_count}). Considérez la consolidation.")
    
    print(f"\n📋 **RÉSUMÉ FINAL**")
    print(f"- {len(studies)} études au total")
    print(f"- {total_subgraphs} subgraphs au total")
    print(f"- Architecture multi-chart: {'✅ Prête' if not missing else '⚠️  Études manquantes'}")
    print(f"- Nettoyage recommandé: {'✅ Non nécessaire' if edge_zones_count <= 10 and alert_systems_count <= 15 else '⚠️  Recommandé'}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_study_inventory.py <fichier_inventaire.jsonl>")
        sys.exit(1)
    
    analyze_study_inventory(sys.argv[1])
