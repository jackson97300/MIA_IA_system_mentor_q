#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse des dernières lignes collectées - Vérification des anomalies persistantes
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
import statistics

def analyze_latest_data():
    file_path = "chart_3_20250904.jsonl"
    
    if not Path(file_path).exists():
        print(f"❌ Fichier non trouvé: {file_path}")
        return
    
    print("🔍 ANALYSE DES DERNIÈRES LIGNES COLLECTÉES - SYSTÈME MIA")
    print("=" * 70)
    
    # Compter le nombre total de lignes
    total_lines = sum(1 for _ in open(file_path, 'r', encoding='utf-8'))
    print(f"📊 Total lignes dans le fichier: {total_lines:,}")
    
    # Analyser les 1000 dernières lignes
    start_line = max(0, total_lines - 1000)
    print(f"🔍 Analyse des lignes {start_line:,} à {total_lines:,} (1000 dernières)")
    
    data_types = defaultdict(list)
    coherence_issues = []
    vix_data = []
    quote_issues = []
    vva_issues = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < start_line:
                continue
                
            try:
                data = json.loads(line.strip())
                data_type = data.get('type', 'NO_TYPE')
                data_types[data_type].append(data)
                
                # Vérifications spécifiques
                if data_type == 'vix':
                    vix_data.append(data)
                
                if data_type == 'quote' and 'bid' in data and 'ask' in data:
                    if data['bid'] >= data['ask']:
                        quote_issues.append({
                            'line': i + 1,
                            'bid': data['bid'],
                            'ask': data['ask'],
                            'timestamp': data.get('t', 'N/A')
                        })
                
                if data_type == 'vva' and 'vah' in data and 'val' in data:
                    if data['vah'] < data['val']:
                        vva_issues.append({
                            'line': i + 1,
                            'vah': data['vah'],
                            'val': data['val'],
                            'timestamp': data.get('t', 'N/A')
                        })
                        
            except Exception as e:
                coherence_issues.append(f"Ligne {i+1}: Erreur parsing - {e}")
    
    # Résumé des données récentes
    print(f"\n📋 RÉPARTITION DES DERNIÈRES DONNÉES:")
    total_recent = sum(len(data) for data in data_types.values())
    
    for data_type, data_list in sorted(data_types.items(), key=lambda x: len(x[1]), reverse=True):
        percentage = (len(data_list) / total_recent) * 100 if total_recent > 0 else 0
        print(f"   📈 {data_type}: {len(data_list):,} ({percentage:.1f}%)")
    
    # Analyse VIX récente
    print(f"\n🌊 ANALYSE VIX RÉCENTE:")
    if vix_data:
        print(f"   ✅ VIX trouvé: {len(vix_data)} enregistrements")
        for vix in vix_data:
            if 'last' in vix:
                print(f"      📊 Valeur: {vix['last']}, Timestamp: {vix.get('t', 'N/A')}")
    else:
        print("   ❌ Aucun VIX dans les dernières données")
    
    # Analyse des anomalies persistantes
    print(f"\n⚠️  ANALYSE DES ANOMALIES PERSISTANTES:")
    
    # Quotes bid >= ask
    if quote_issues:
        print(f"   📈 Quotes bid >= ask: {len(quote_issues)} problèmes détectés")
        for issue in quote_issues[:3]:  # Afficher les 3 premiers
            print(f"      ❌ Ligne {issue['line']}: bid={issue['bid']} >= ask={issue['ask']}")
        if len(quote_issues) > 3:
            print(f"      ... et {len(quote_issues) - 3} autres")
    else:
        print("   ✅ Aucun problème de spread détecté dans les dernières données")
    
    # VVA VAH < VAL
    if vva_issues:
        print(f"   📉 VVA VAH < VAL: {len(vva_issues)} problèmes détectés")
        for issue in vva_issues:
            print(f"      ❌ Ligne {issue['line']}: VAH={issue['vah']} < VAL={issue['val']}")
    else:
        print("   ✅ Aucun problème VVA détecté dans les dernières données")
    
    # Autres erreurs
    if coherence_issues:
        print(f"   🔧 Erreurs de parsing: {len(coherence_issues)} détectées")
        for issue in coherence_issues[:3]:
            print(f"      ❌ {issue}")
    
    # Évaluation de la tendance
    print(f"\n🎯 ÉVALUATION DE LA TENDANCE:")
    
    if len(quote_issues) == 0 and len(vva_issues) == 0:
        print("   🎉 EXCELLENT! Aucune anomalie dans les dernières données")
        print("   📈 Les corrections semblent avoir résolu les problèmes")
    elif len(quote_issues) < 3 and len(vva_issues) < 2:
        print("   ✅ BONNE amélioration! Réduction significative des anomalies")
        print("   📉 Les problèmes persistent mais sont moins fréquents")
    else:
        print("   ⚠️  ATTENTION! Anomalies toujours présentes")
        print("   🔧 Des corrections supplémentaires sont nécessaires")
    
    # Recommandations
    print(f"\n🚀 RECOMMANDATIONS:")
    if len(quote_issues) == 0 and len(vva_issues) == 0:
        print("   🎯 Maintenir la qualité actuelle")
        print("   📊 Monitoring continu pour détecter toute régression")
    else:
        print("   🔧 Continuer les corrections des anomalies persistantes")
        print("   📈 Analyser les patterns des anomalies restantes")
    
    print(f"\n" + "=" * 70)

if __name__ == "__main__":
    analyze_latest_data()







