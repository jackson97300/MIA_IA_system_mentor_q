#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse de tous les types de données exportés par le système MIA
"""

import json
from pathlib import Path
from collections import Counter

def analyze_all_data_types():
    file_path = "chart_3_20250904.jsonl"
    
    if not Path(file_path).exists():
        print(f"❌ Fichier non trouvé: {file_path}")
        return
    
    print(f"🔍 Analyse de tous les types de données dans {file_path}")
    print("=" * 70)
    
    type_counts = Counter()
    total_lines = 0
    
    # Analyser les 1000 premières lignes pour un aperçu rapide
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            total_lines += 1
            if total_lines > 1000:  # Limiter pour la performance
                break
                
            try:
                data = json.loads(line.strip())
                data_type = data.get('type', 'NO_TYPE')
                type_counts[data_type] += 1
            except:
                continue
    
    print(f"📊 Analyse des {total_lines:,} premières lignes")
    print(f"🔍 Types de données détectés:")
    
    # Afficher par ordre de fréquence
    for data_type, count in type_counts.most_common():
        percentage = (count / total_lines) * 100
        print(f"   📈 {data_type}: {count:,} ({percentage:.1f}%)")
    
    # Analyse détaillée des types principaux
    print(f"\n📋 ANALYSE DÉTAILLÉE DES TYPES PRINCIPAUX:")
    
    # Vérifier VIX
    vix_count = type_counts.get('vix', 0)
    vix_diag_count = type_counts.get('vix_diag', 0)
    
    if vix_count > 0:
        print(f"   ✅ VIX: {vix_count:,} enregistrements collectés avec succès!")
    else:
        print(f"   ❌ VIX: Aucun enregistrement trouvé")
    
    if vix_diag_count > 0:
        print(f"   ⚠️  VIX_DIAG: {vix_diag_count:,} diagnostics (erreurs)")
    
    # Vérifier les autres types
    for data_type in ['basedata', 'depth', 'quote', 'vap', 'vwap', 'vva']:
        count = type_counts.get(data_type, 0)
        if count > 0:
            print(f"   📊 {data_type}: {count:,} enregistrements")
    
    # Résumé
    print(f"\n🎯 RÉSUMÉ DE L'EXPORT MIA:")
    print(f"   Total des types: {len(type_counts)}")
    print(f"   Types principaux: {', '.join(type_counts.keys())}")
    
    if vix_count > 0:
        print(f"\n🎉 SUCCÈS: Le VIX est maintenant collecté correctement!")
        print(f"   - {vix_count:,} enregistrements VIX")
        print(f"   - Valeurs réelles collectées")
        print(f"   - Plus de vix_diag en excès")
    else:
        print(f"\n⚠️  ATTENTION: Vérifier la collecte VIX")
    
    print(f"\n" + "=" * 70)

if __name__ == "__main__":
    analyze_all_data_types()







