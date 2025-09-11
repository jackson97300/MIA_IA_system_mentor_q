#!/usr/bin/env python3
"""
Analyse des données de Volume Profile (VVA) dans les fichiers chart_3, chart_4 et chart_10
"""

import json
import pandas as pd
from collections import defaultdict
import numpy as np

def analyze_vva_data(file_path, chart_name):
    """Analyse les données VVA d'un fichier"""
    print(f"\n{'='*60}")
    print(f"📊 ANALYSE VOLUME PROFILE - {chart_name}")
    print(f"{'='*60}")
    
    vva_data = []
    total_lines = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                total_lines += 1
                if line.strip():
                    try:
                        data = json.loads(line.strip())
                        if data.get('type') == 'vva':
                            vva_data.append(data)
                    except json.JSONDecodeError:
                        continue
        
        print(f"📁 Fichier: {file_path}")
        print(f"📈 Total lignes: {total_lines:,}")
        print(f"🎯 Données VVA trouvées: {len(vva_data)}")
        
        if not vva_data:
            print("❌ Aucune donnée VVA trouvée")
            return None
        
        # Analyse des données VVA
        df = pd.DataFrame(vva_data)
        
        print(f"\n📊 STATISTIQUES VVA:")
        print(f"   • VAH (Volume Area High): {df['vah'].mean():.2f} ± {df['vah'].std():.2f}")
        print(f"   • VAL (Volume Area Low): {df['val'].mean():.2f} ± {df['val'].std():.2f}")
        print(f"   • VPOC (Volume Point of Control): {df['vpoc'].mean():.2f} ± {df['vpoc'].std():.2f}")
        
        # Analyse des valeurs nulles
        null_vah = (df['vah'] == 0).sum()
        null_val = (df['val'] == 0).sum()
        null_vpoc = (df['vpoc'] == 0).sum()
        null_pvah = (df['pvah'] == 0).sum()
        null_pval = (df['pval'] == 0).sum()
        null_ppoc = (df['ppoc'] == 0).sum()
        
        print(f"\n🔍 VALEURS NULLES:")
        print(f"   • VAH = 0: {null_vah}/{len(df)} ({null_vah/len(df)*100:.1f}%)")
        print(f"   • VAL = 0: {null_val}/{len(df)} ({null_val/len(df)*100:.1f}%)")
        print(f"   • VPOC = 0: {null_vpoc}/{len(df)} ({null_vpoc/len(df)*100:.1f}%)")
        print(f"   • PVAH = 0: {null_pvah}/{len(df)} ({null_pvah/len(df)*100:.1f}%)")
        print(f"   • PVAL = 0: {null_pval}/{len(df)} ({null_pval/len(df)*100:.1f}%)")
        print(f"   • PPOC = 0: {null_ppoc}/{len(df)} ({null_ppoc/len(df)*100:.1f}%)")
        
        # Analyse des IDs
        unique_ids = df['id_curr'].nunique()
        print(f"\n🆔 IDS UNIQUES: {unique_ids}")
        
        # Échantillon de données
        print(f"\n📋 ÉCHANTILLON DE DONNÉES:")
        for i, row in df.head(3).iterrows():
            print(f"   Bar {row['i']}: VAH={row['vah']:.2f}, VAL={row['val']:.2f}, VPOC={row['vpoc']:.2f}")
        
        return df
        
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        return None

def compare_charts():
    """Compare les données VVA entre les 3 charts"""
    print(f"\n{'='*80}")
    print(f"🔄 COMPARAISON VOLUME PROFILE ENTRE CHARTS")
    print(f"{'='*80}")
    
    files = [
        ("chart_3_20250910.jsonl", "CHART 3"),
        ("chart_4_20250910.jsonl", "CHART 4"), 
        ("chart_10_20250910.jsonl", "CHART 10")
    ]
    
    results = {}
    
    for file_path, chart_name in files:
        df = analyze_vva_data(file_path, chart_name)
        if df is not None:
            results[chart_name] = df
    
    if len(results) > 1:
        print(f"\n📊 COMPARAISON RÉSUMÉE:")
        print(f"{'Chart':<10} {'VVA Count':<12} {'VAH Avg':<12} {'VAL Avg':<12} {'VPOC Avg':<12}")
        print(f"{'-'*60}")
        
        for chart_name, df in results.items():
            vah_avg = df['vah'].mean() if (df['vah'] != 0).any() else 0
            val_avg = df['val'].mean() if (df['val'] != 0).any() else 0
            vpoc_avg = df['vpoc'].mean() if (df['vpoc'] != 0).any() else 0
            
            print(f"{chart_name:<10} {len(df):<12} {vah_avg:<12.2f} {val_avg:<12.2f} {vpoc_avg:<12.2f}")

if __name__ == "__main__":
    compare_charts()
