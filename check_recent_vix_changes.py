#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérification des changements récents dans la collecte VIX
Après compilation réussie du code corrigé
"""

import json
from pathlib import Path
from datetime import datetime

def check_recent_vix_changes():
    file_path = "chart_3_20250904.jsonl"
    
    if not Path(file_path).exists():
        print(f"❌ Fichier non trouvé: {file_path}")
        return
    
    print(f"🔍 Vérification des changements récents VIX dans {file_path}")
    print("=" * 70)
    
    # Lire les 100 dernières lignes
    recent_lines = []
    total_lines = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            total_lines += 1
            recent_lines.append(line.strip())
            if len(recent_lines) > 100:
                recent_lines.pop(0)  # Garder seulement les 100 dernières
    
    print(f"📊 Total des lignes dans le fichier: {total_lines:,}")
    print(f"🔍 Analyse des {len(recent_lines)} dernières lignes")
    
    # Analyser les types de données récents
    recent_types = {}
    vix_records = []
    vix_diag_records = []
    
    for i, line in enumerate(recent_lines):
        try:
            data = json.loads(line)
            data_type = data.get('type', 'NO_TYPE')
            recent_types[data_type] = recent_types.get(data_type, 0) + 1
            
            # Collecter les enregistrements VIX
            if data_type == 'vix':
                vix_records.append(data)
            elif data_type == 'vix_diag':
                vix_diag_records.append(data)
                
        except:
            continue
    
    print(f"\n📋 Types de données dans les dernières lignes:")
    for data_type, count in sorted(recent_types.items()):
        print(f"   {data_type}: {count}")
    
    # Analyse spécifique VIX
    print(f"\n🔍 ANALYSE VIX - Dernières lignes:")
    print(f"   Enregistrements VIX: {len(vix_records)}")
    print(f"   Diagnostics VIX: {len(vix_diag_records)}")
    
    if vix_records:
        print(f"\n✅ VIX collecté avec succès (exemples):")
        for i, vix in enumerate(vix_records[-3:], 1):  # 3 derniers
            print(f"   {i}. {vix}")
    else:
        print(f"\n⚠️  Aucun VIX collecté dans les dernières lignes")
    
    if vix_diag_records:
        print(f"\n⚠️  Diagnostics VIX (exemples):")
        for i, diag in enumerate(vix_diag_records[-3:], 1):  # 3 derniers
            print(f"   {i}. {diag}")
    
    # Vérifier s'il y a des changements par rapport à l'analyse précédente
    print(f"\n🔄 COMPARAISON AVEC L'ANALYSE PRÉCÉDENTE:")
    
    # Lire le rapport précédent
    if Path('report.md').exists():
        with open('report.md', 'r', encoding='utf-8') as f:
            report_content = f.read()
            
        if 'vix_diag: 936' in report_content:
            print(f"   📊 Rapport précédent: 936 vix_diag détectés")
            
            if len(vix_diag_records) < 936:
                print(f"   🎉 AMÉLIORATION: Moins de vix_diag dans les dernières lignes!")
                print(f"   💡 Cela suggère que la collecte VIX fonctionne mieux")
            else:
                print(f"   ⚠️  Même niveau de vix_diag - vérifier la configuration")
        else:
            print(f"   📊 Rapport précédent: Pas de données VIX claires")
    else:
        print(f"   📊 Aucun rapport précédent trouvé")
    
    # Recommandations
    print(f"\n💡 RECOMMANDATIONS:")
    if len(vix_records) > 0:
        print(f"   ✅ La collecte VIX semble fonctionner!")
        print(f"   📊 Vérifier que vous obtenez des valeurs VIX réelles")
        print(f"   🔧 Si c'est nouveau, la compilation a résolu le problème")
    elif len(vix_diag_records) > 0:
        print(f"   ⚠️  Toujours des diagnostics VIX")
        print(f"   🔧 Vérifier que le graphique 8 est ouvert avec VIX_CGI[M]")
        print(f"   📊 Vérifier que Sierra Chart a accès au graphique 8")
    else:
        print(f"   ❓ Aucune donnée VIX trouvée")
        print(f"   🔧 Vérifier que l'étude est active sur le graphique ES")
        print(f"   📊 Vérifier que Input[14] = 1 (Export VIX activé)")
    
    print(f"\n" + "=" * 70)
    print(f"🎯 Analyse terminée - {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    check_recent_vix_changes()







