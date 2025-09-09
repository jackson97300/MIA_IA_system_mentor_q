#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse en profondeur de la distribution VIX - Vérification de la persistance
"""

import json
from pathlib import Path
from collections import defaultdict

def deep_vix_analysis():
    file_path = "chart_3_20250904.jsonl"
    
    if not Path(file_path).exists():
        print(f"❌ Fichier non trouvé: {file_path}")
        return
    
    print("🔍 ANALYSE EN PROFONDEUR DE LA DISTRIBUTION VIX - SYSTÈME MIA")
    print("=" * 70)
    
    # Compter le nombre total de lignes
    total_lines = sum(1 for _ in open(file_path, 'r', encoding='utf-8'))
    print(f"📊 Total lignes dans le fichier: {total_lines:,}")
    
    # Analyser par sections de 1000 lignes
    section_size = 1000
    vix_distribution = defaultdict(int)
    vix_diag_distribution = defaultdict(int)
    vix_locations = []
    vix_diag_locations = []
    
    print(f"\n🔍 ANALYSE PAR SECTIONS DE {section_size:,} LIGNES:")
    print("-" * 50)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            try:
                data = json.loads(line.strip())
                data_type = data.get('type', 'NO_TYPE')
                
                # Identifier la section
                section = i // section_size
                
                if data_type == 'vix':
                    vix_distribution[section] += 1
                    vix_locations.append({
                        'line': i + 1,
                        'section': section,
                        'value': data.get('last', 'N/A'),
                        'timestamp': data.get('t', 'N/A')
                    })
                
                if data_type == 'vix_diag':
                    vix_diag_distribution[section] += 1
                    vix_diag_locations.append({
                        'line': i + 1,
                        'section': section,
                        'msg': data.get('msg', 'N/A'),
                        'timestamp': data.get('t', 'N/A')
                    })
                    
            except Exception as e:
                continue
    
    # Afficher la distribution par sections
    total_sections = (total_lines + section_size - 1) // section_size
    
    print(f"📊 DISTRIBUTION VIX PAR SECTIONS:")
    vix_total = 0
    for section in range(total_sections):
        vix_count = vix_distribution.get(section, 0)
        vix_diag_count = vix_diag_distribution.get(section, 0)
        vix_total += vix_count
        
        if vix_count > 0 or vix_diag_count > 0:
            start_line = section * section_size + 1
            end_line = min((section + 1) * section_size, total_lines)
            print(f"   Section {section}: Lignes {start_line:,}-{end_line:,}")
            print(f"      📈 VIX: {vix_count}, ⚠️  VIX_DIAG: {vix_diag_count}")
    
    # Résumé global
    print(f"\n📋 RÉSUMÉ GLOBAL VIX:")
    print(f"   🌊 Total VIX: {vix_total}")
    print(f"   ⚠️  Total VIX_DIAG: {len(vix_diag_locations)}")
    
    if vix_total == 0:
        print(f"   ❌ CRITIQUE: Aucun VIX trouvé dans tout le fichier!")
    elif vix_total < 10:
        print(f"   ⚠️  ATTENTION: Très peu de VIX ({vix_total})")
    else:
        print(f"   ✅ Normal: {vix_total} enregistrements VIX")
    
    # Analyser les emplacements VIX
    if vix_locations:
        print(f"\n📍 EMPLACEMENTS DES DONNÉES VIX:")
        for vix in vix_locations:
            print(f"   📍 Ligne {vix['line']:,} (Section {vix['section']}): VIX={vix['value']}")
    
    # Analyser les emplacements VIX_DIAG
    if vix_diag_locations:
        print(f"\n⚠️  EMPLACEMENTS DES VIX_DIAG:")
        for vix_diag in vix_diag_locations[:10]:  # Limiter à 10
            print(f"   ⚠️  Ligne {vix_diag['line']:,} (Section {vix_diag['section']}): {vix_diag['msg']}")
        if len(vix_diag_locations) > 10:
            print(f"   ... et {len(vix_diag_locations) - 10} autres")
    
    # Vérifier la continuité
    print(f"\n🔄 ANALYSE DE CONTINUITÉ:")
    if vix_total > 0:
        # Trouver la première et dernière occurrence VIX
        first_vix = min(vix_locations, key=lambda x: x['line'])
        last_vix = max(vix_locations, key=lambda x: x['line'])
        
        print(f"   📍 Premier VIX: Ligne {first_vix['line']:,} (Section {first_vix['section']})")
        print(f"   📍 Dernier VIX: Ligne {last_vix['line']:,} (Section {last_vix['section']})")
        
        # Calculer la distribution temporelle
        if last_vix['line'] - first_vix['line'] > 1000:
            print(f"   ⚠️  ATTENTION: Grand écart entre premier et dernier VIX")
            print(f"      Écart: {last_vix['line'] - first_vix['line']:,} lignes")
        else:
            print(f"   ✅ Distribution VIX relativement concentrée")
    else:
        print(f"   ❌ Aucun VIX pour analyser la continuité")
    
    # Recommandations
    print(f"\n🚀 RECOMMANDATIONS:")
    if vix_total == 0:
        print(f"   🚨 URGENT: Le VIX a complètement disparu!")
        print(f"   🔧 Vérifier le code C++ et la compilation")
        print(f"   📊 Contrôler les paramètres d'entrée")
    elif vix_total < 10:
        print(f"   ⚠️  Le VIX est très rare, vérifier la logique de collecte")
        print(f"   📈 Analyser pourquoi si peu d'enregistrements")
    else:
        print(f"   ✅ Distribution VIX normale")
    
    print(f"\n" + "=" * 70)

if __name__ == "__main__":
    deep_vix_analysis()







