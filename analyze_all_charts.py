#!/usr/bin/env python3
"""
Analyse complète des 3 fichiers chart_3, chart_4 et chart_10
"""

import json
import pandas as pd
from collections import defaultdict, Counter
import numpy as np

def analyze_file(file_path, chart_name):
    """Analyse complète d'un fichier"""
    print(f"\n{'='*80}")
    print(f"📊 ANALYSE COMPLÈTE - {chart_name}")
    print(f"{'='*80}")
    
    data_by_type = defaultdict(list)
    total_lines = 0
    zero_values = defaultdict(list)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                total_lines += 1
                if line.strip():
                    try:
                        data = json.loads(line.strip())
                        data_type = data.get('type', 'unknown')
                        data_by_type[data_type].append(data)
                        
                        # Analyser les valeurs à 0
                        for key, value in data.items():
                            if isinstance(value, (int, float)) and value == 0:
                                zero_values[key].append({
                                    'line': line_num,
                                    'type': data_type,
                                    'chart': data.get('chart', 'unknown'),
                                    'study_id': data.get('study_id', 'N/A'),
                                    'subgraph': data.get('subgraph', 'N/A'),
                                    'sg': data.get('sg', 'N/A')
                                })
                    except json.JSONDecodeError:
                        continue
        
        print(f"📁 Fichier: {file_path}")
        print(f"📈 Total lignes: {total_lines:,}")
        
        # Statistiques par type
        print(f"\n📊 TYPES DE DONNÉES:")
        for dtype, count in sorted(data_by_type.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {dtype}: {len(count):,}")
        
        # Analyse des valeurs à 0
        if zero_values:
            print(f"\n❌ VALEURS À 0 DÉTECTÉES:")
            for field, occurrences in zero_values.items():
                print(f"\n🔸 Champ '{field}': {len(occurrences)} occurrences")
                
                # Grouper par type
                by_type = defaultdict(list)
                for occ in occurrences:
                    by_type[occ['type']].append(occ)
                
                for dtype, occs in by_type.items():
                    print(f"   📋 Type '{dtype}': {len(occs)} occurrences")
                    
                    # Grouper par chart/study/subgraph
                    by_chart = defaultdict(list)
                    for occ in occs:
                        chart_key = f"Chart {occ['chart']}"
                        if occ['study_id'] != 'N/A':
                            chart_key += f" Study {occ['study_id']}"
                        if occ['subgraph'] != 'N/A':
                            chart_key += f" SG {occ['subgraph']}"
                        elif occ['sg'] != 'N/A':
                            chart_key += f" SG {occ['sg']}"
                        by_chart[chart_key].append(occ)
                    
                    for chart_key, chart_occs in by_chart.items():
                        print(f"      • {chart_key}: {len(chart_occs)} occurrences")
                        if len(chart_occs) <= 3:
                            for occ in chart_occs:
                                print(f"        - Ligne {occ['line']}")
                        else:
                            print(f"        - Premières 3 lignes: {[occ['line'] for occ in chart_occs[:3]]}")
        else:
            print(f"\n✅ Aucune valeur à 0 détectée")
        
        # Analyse spécifique par type
        analyze_specific_types(data_by_type, chart_name)
        
        return data_by_type, zero_values
        
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {file_path}")
        return None, None
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        return None, None

def analyze_specific_types(data_by_type, chart_name):
    """Analyse spécifique par type de données"""
    
    # Analyse VVA (Volume Profile)
    if 'vva' in data_by_type:
        vva_data = data_by_type['vva']
        print(f"\n📊 ANALYSE VOLUME PROFILE (VVA):")
        print(f"   • Total VVA: {len(vva_data)}")
        
        if vva_data:
            df = pd.DataFrame(vva_data)
            
            # Statistiques
            print(f"   • VAH (Volume Area High): {df['vah'].mean():.2f} ± {df['vah'].std():.2f}")
            print(f"   • VAL (Volume Area Low): {df['val'].mean():.2f} ± {df['val'].std():.2f}")
            print(f"   • VPOC (Volume Point of Control): {df['vpoc'].mean():.2f} ± {df['vpoc'].std():.2f}")
            
            # Valeurs nulles
            null_vah = (df['vah'] == 0).sum()
            null_val = (df['val'] == 0).sum()
            null_vpoc = (df['vpoc'] == 0).sum()
            null_pvah = (df['pvah'] == 0).sum()
            null_pval = (df['pval'] == 0).sum()
            null_ppoc = (df['ppoc'] == 0).sum()
            
            print(f"   • VAH = 0: {null_vah}/{len(df)} ({null_vah/len(df)*100:.1f}%)")
            print(f"   • VAL = 0: {null_val}/{len(df)} ({null_val/len(df)*100:.1f}%)")
            print(f"   • VPOC = 0: {null_vpoc}/{len(df)} ({null_vpoc/len(df)*100:.1f}%)")
            print(f"   • PVAH = 0: {null_pvah}/{len(df)} ({null_pvah/len(df)*100:.1f}%)")
            print(f"   • PVAL = 0: {null_pval}/{len(df)} ({null_pval/len(df)*100:.1f}%)")
            print(f"   • PPOC = 0: {null_ppoc}/{len(df)} ({null_ppoc/len(df)*100:.1f}%)")
            
            # IDs uniques
            unique_ids = df['id_curr'].nunique()
            print(f"   • IDs uniques: {unique_ids}")
    
    # Analyse VIX
    if 'vix' in data_by_type:
        vix_data = data_by_type['vix']
        print(f"\n📊 ANALYSE VIX:")
        print(f"   • Total VIX: {len(vix_data)}")
        
        if vix_data:
            df = pd.DataFrame(vix_data)
            print(f"   • VIX Last: {df['last'].mean():.2f} ± {df['last'].std():.2f}")
            print(f"   • Mode = 0: {(df['mode'] == 0).sum()}/{len(df)} ({(df['mode'] == 0).sum()/len(df)*100:.1f}%)")
            print(f"   • Study ID: {df['study'].iloc[0] if len(df) > 0 else 'N/A'}")
            print(f"   • Subgraph: {df['sg'].iloc[0] if len(df) > 0 else 'N/A'}")
    
    # Analyse NBCV
    if 'nbcv_metrics' in data_by_type:
        nbcv_data = data_by_type['nbcv_metrics']
        print(f"\n📊 ANALYSE NBCV METRICS:")
        print(f"   • Total NBCV: {len(nbcv_data)}")
        
        if nbcv_data:
            df = pd.DataFrame(nbcv_data)
            print(f"   • Pressure Bullish = 0: {(df['pressure_bullish'] == 0).sum()}/{len(df)} ({(df['pressure_bullish'] == 0).sum()/len(df)*100:.1f}%)")
            print(f"   • Pressure Bearish = 0: {(df['pressure_bearish'] == 0).sum()}/{len(df)} ({(df['pressure_bearish'] == 0).sum()/len(df)*100:.1f}%)")
    
    # Analyse Corrélation
    if 'correlation' in data_by_type:
        corr_data = data_by_type['correlation']
        print(f"\n📊 ANALYSE CORRÉLATION:")
        print(f"   • Total Corrélation: {len(corr_data)}")
        
        if corr_data:
            df = pd.DataFrame(corr_data)
            print(f"   • Valeur moyenne: {df['value'].mean():.6f} ± {df['value'].std():.6f}")
            print(f"   • Study ID: {df['study_id'].iloc[0] if len(df) > 0 else 'N/A'}")
            print(f"   • Subgraph: {df['sg'].iloc[0] if len(df) > 0 else 'N/A'}")
            print(f"   • Chart: {df['chart'].iloc[0] if len(df) > 0 else 'N/A'}")
    
    # Analyse MenthorQ
    if 'menthorq_level' in data_by_type:
        mq_data = data_by_type['menthorq_level']
        print(f"\n📊 ANALYSE MENTHORQ:")
        print(f"   • Total MenthorQ: {len(mq_data)}")
        
        if mq_data:
            df = pd.DataFrame(mq_data)
            level_types = df['level_type'].value_counts()
            print(f"   • Types de niveaux:")
            for level_type, count in level_types.items():
                print(f"     - {level_type}: {count}")
    
    # Analyse MenthorQ Diagnostics
    if 'menthorq_diag' in data_by_type:
        mq_diag = data_by_type['menthorq_diag']
        print(f"\n📊 ANALYSE MENTHORQ DIAGNOSTICS:")
        print(f"   • Total Diagnostics: {len(mq_diag)}")
        
        if mq_diag:
            df = pd.DataFrame(mq_diag)
            msg_counts = df['msg'].value_counts()
            print(f"   • Messages:")
            for msg, count in msg_counts.items():
                print(f"     - {msg}: {count}")

def main():
    """Analyse principale"""
    files = [
        ("chart_3_20250910.jsonl", "CHART 3"),
        ("chart_4_20250910.jsonl", "CHART 4"), 
        ("chart_10_20250910.jsonl", "CHART 10")
    ]
    
    all_results = {}
    
    for file_path, chart_name in files:
        data_by_type, zero_values = analyze_file(file_path, chart_name)
        if data_by_type is not None:
            all_results[chart_name] = {
                'data_by_type': data_by_type,
                'zero_values': zero_values
            }
    
    # Résumé global
    print(f"\n{'='*100}")
    print(f"📋 RÉSUMÉ GLOBAL")
    print(f"{'='*100}")
    
    # Comparaison des types de données
    print(f"\n📊 COMPARAISON DES TYPES DE DONNÉES:")
    all_types = set()
    for chart_name, results in all_results.items():
        all_types.update(results['data_by_type'].keys())
    
    print(f"{'Type':<20} {'Chart 3':<12} {'Chart 4':<12} {'Chart 10':<12}")
    print(f"{'-'*60}")
    
    for dtype in sorted(all_types):
        counts = []
        for chart_name in ["CHART 3", "CHART 4", "CHART 10"]:
            if chart_name in all_results:
                count = len(all_results[chart_name]['data_by_type'].get(dtype, []))
                counts.append(f"{count:,}")
            else:
                counts.append("0")
        
        print(f"{dtype:<20} {counts[0]:<12} {counts[1]:<12} {counts[2]:<12}")
    
    # Résumé des problèmes
    print(f"\n🚨 PROBLÈMES IDENTIFIÉS:")
    
    # Volume Profile
    if "CHART 3" in all_results and 'vva' in all_results["CHART 3"]['data_by_type']:
        vva_data = all_results["CHART 3"]['data_by_type']['vva']
        if vva_data:
            df = pd.DataFrame(vva_data)
            val_zero = (df['val'] == 0).sum()
            if val_zero == len(df):
                print(f"   🔴 CHART 3: Volume Profile VAL toujours à 0 ({val_zero}/{len(df)})")
    
    # VIX Mode
    if "CHART 3" in all_results and 'vix' in all_results["CHART 3"]['data_by_type']:
        vix_data = all_results["CHART 3"]['data_by_type']['vix']
        if vix_data:
            df = pd.DataFrame(vix_data)
            mode_zero = (df['mode'] == 0).sum()
            if mode_zero == len(df):
                print(f"   🔴 CHART 3: VIX Mode toujours à 0 ({mode_zero}/{len(df)})")
    
    # NBCV Pressure Bearish
    for chart_name in ["CHART 3", "CHART 4"]:
        if chart_name in all_results and 'nbcv_metrics' in all_results[chart_name]['data_by_type']:
            nbcv_data = all_results[chart_name]['data_by_type']['nbcv_metrics']
            if nbcv_data:
                df = pd.DataFrame(nbcv_data)
                bearish_zero = (df['pressure_bearish'] == 0).sum()
                if bearish_zero == len(df):
                    print(f"   🔴 {chart_name}: NBCV Pressure Bearish toujours à 0 ({bearish_zero}/{len(df)})")
    
    # MenthorQ Diagnostics
    if "CHART 10" in all_results and 'menthorq_diag' in all_results["CHART 10"]['data_by_type']:
        mq_diag = all_results["CHART 10"]['data_by_type']['menthorq_diag']
        if mq_diag:
            df = pd.DataFrame(mq_diag)
            no_value = (df['msg'] == 'no_value').sum()
            if no_value > 0:
                print(f"   🟡 CHART 10: MenthorQ {no_value} diagnostics 'no_value'")

if __name__ == "__main__":
    main()
