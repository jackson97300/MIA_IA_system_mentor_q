#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérification de la structure du fichier
"""

import json
from pathlib import Path

def check_file_structure():
    file_path = "chart_3_20250904.jsonl"
    
    if not Path(file_path).exists():
        print(f"❌ Fichier non trouvé: {file_path}")
        return
    
    print(f"🔍 Vérification de la structure de {file_path}")
    print("=" * 60)
    
    # Vérifier les premières lignes
    print("📋 Premières lignes du fichier:")
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 5:  # Afficher seulement les 5 premières lignes
                break
            try:
                data = json.loads(line.strip())
                print(f"Ligne {i+1}: {data.get('type', 'NO_TYPE')} - {list(data.keys())}")
            except:
                print(f"Ligne {i+1}: ERREUR JSON")
    
    print("\n🔍 Recherche de tous les types de données:")
    type_counts = {}
    total_lines = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            total_lines += 1
            try:
                data = json.loads(line.strip())
                data_type = data.get('type', 'NO_TYPE')
                type_counts[data_type] = type_counts.get(data_type, 0) + 1
            except:
                type_counts['ERROR'] = type_counts.get('ERROR', 0) + 1
    
    print(f"📊 Total des lignes: {total_lines:,}")
    print("📋 Types de données trouvés:")
    for data_type, count in sorted(type_counts.items()):
        print(f"   {data_type}: {count:,}")
    
    print("\n🔍 Recherche spécifique VIX:")
    vix_found = False
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if '"vix"' in line.lower() or '"type":"vix"' in line:
                print(f"   VIX trouvé à la ligne {i+1}: {line[:100]}...")
                vix_found = True
                break
    
    if not vix_found:
        print("   ❌ Aucune référence VIX trouvée dans le fichier")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_file_structure()







