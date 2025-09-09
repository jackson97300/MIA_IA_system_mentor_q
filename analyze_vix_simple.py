#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse simple des données VIX
"""

import json
from pathlib import Path

def analyze_vix_data():
    file_path = "chart_3_20250904.jsonl"
    
    if not Path(file_path).exists():
        print(f"❌ Fichier non trouvé: {file_path}")
        return
    
    vix_records = []
    total_lines = 0
    
    print(f"🔍 Analyse des données VIX dans {file_path}")
    print("=" * 60)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            total_lines += 1
            
            if line_num % 10000 == 0:
                print(f"   Traité {line_num:,} lignes...")
            
            try:
                data = json.loads(line.strip())
                if data.get('type') == 'vix':
                    vix_records.append(data)
            except:
                continue
    
    print(f"\n📊 Résultats de l'analyse:")
    print(f"   Total des lignes: {total_lines:,}")
    print(f"   Enregistrements VIX: {len(vix_records)}")
    
    if vix_records:
        print(f"\n🔍 Premier enregistrement VIX:")
        first_vix = vix_records[0]
        for key, value in first_vix.items():
            print(f"   {key}: {value}")
        
        print(f"\n📈 Analyse des champs VIX:")
        for field in ['last', 'mode', 'chart', 'study', 'sg']:
            values = [r.get(field) for r in vix_records if r.get(field) is not None]
            if values:
                print(f"   {field}: min={min(values)}, max={max(values)}, unique={len(set(values))}")
        
        print(f"\n⚠️  Problèmes détectés:")
        mode_values = [r.get('mode') for r in vix_records]
        mode_counts = {}
        for mode in mode_values:
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        for mode, count in mode_counts.items():
            if mode == 0:
                print(f"   Mode 0: {count} fois (considéré comme invalide par l'analyseur)")
            else:
                print(f"   Mode {mode}: {count} fois")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    analyze_vix_data()







