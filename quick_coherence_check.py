#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérification rapide de la cohérence des données MIA
"""

import json
from collections import defaultdict

def quick_coherence_check():
    file_path = "chart_3_20250904.jsonl"
    
    print("🔍 VÉRIFICATION RAPIDE DE COHÉRENCE - SYSTÈME MIA")
    print("=" * 60)
    
    data_types = defaultdict(list)
    coherence_issues = []
    
    # Analyser les 2000 premières lignes
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 2000:
                break
                
            try:
                data = json.loads(line.strip())
                data_type = data.get('type', 'NO_TYPE')
                data_types[data_type].append(data)
                
                # Vérifications rapides
                if data_type == 'quote' and 'bid' in data and 'ask' in data:
                    if data['bid'] >= data['ask']:
                        coherence_issues.append(f"Quote bid>=ask: {data['bid']} >= {data['ask']}")
                
                if data_type == 'vix' and 'last' in data:
                    if data['last'] <= 0 or data['last'] > 200:
                        coherence_issues.append(f"VIX invalide: {data['last']}")
                        
            except:
                continue
    
    # Résumé des données
    print(f"📊 Types de données détectés: {len(data_types)}")
    total_records = sum(len(data) for data in data_types.values())
    print(f"📊 Total enregistrements: {total_records:,}")
    
    # Détails par type
    print(f"\n📋 RÉPARTITION DES DONNÉES:")
    for data_type, data_list in sorted(data_types.items(), key=lambda x: len(x[1]), reverse=True):
        percentage = (len(data_list) / total_records) * 100
        print(f"   📈 {data_type}: {len(data_list):,} ({percentage:.1f}%)")
    
    # Vérifications spécifiques
    print(f"\n🔍 VÉRIFICATIONS DE COHÉRENCE:")
    
    # VIX
    vix_count = len(data_types.get('vix', []))
    vix_diag_count = len(data_types.get('vix_diag', []))
    print(f"   🌊 VIX: {vix_count} enregistrements ✅")
    print(f"   ⚠️  VIX_DIAG: {vix_diag_count} diagnostics")
    
    # Quotes
    quotes = data_types.get('quote', [])
    if quotes:
        print(f"   📈 Quotes: {len(quotes):,} enregistrements")
    
    # Depth
    depth = data_types.get('depth', [])
    if depth:
        print(f"   🏗️  Depth: {len(depth)} enregistrements")
    
    # Problèmes détectés
    if coherence_issues:
        print(f"\n⚠️  PROBLÈMES DÉTECTÉS ({len(coherence_issues)}):")
        for issue in coherence_issues[:5]:
            print(f"   ❌ {issue}")
        if len(coherence_issues) > 5:
            print(f"   ... et {len(coherence_issues) - 5} autres")
    else:
        print(f"\n✅ AUCUN PROBLÈME DE COHÉRENCE DÉTECTÉ!")
    
    # Évaluation globale
    print(f"\n🎯 ÉVALUATION GLOBALE:")
    if len(coherence_issues) == 0:
        print("   🎉 EXCELLENT! Données parfaitement cohérentes")
    elif len(coherence_issues) < 3:
        print("   ✅ BONNE cohérence, quelques anomalies mineures")
    else:
        print("   ⚠️  ATTENTION: plusieurs problèmes détectés")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    quick_coherence_check()







