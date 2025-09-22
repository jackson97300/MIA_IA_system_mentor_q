#!/usr/bin/env python3
"""
Script de correction des doublons dans les fichiers JSONL générés par MIA_Dumper_G3_Core.cpp
"""

import json
import os
from collections import defaultdict
from datetime import datetime

def fix_duplicates_in_file(file_path):
    """Corrige les doublons dans un fichier JSONL"""
    print(f"🔧 Traitement de {file_path}...")
    
    # Lire toutes les lignes
    lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                lines.append((line_num, data))
            except json.JSONDecodeError as e:
                print(f"⚠️  Erreur JSON ligne {line_num}: {e}")
                continue
    
    # Grouper par clé (sym, t, i)
    grouped = defaultdict(list)
    for line_num, data in lines:
        key = (data.get('sym'), data.get('t'), data.get('i'))
        grouped[key].append((line_num, data))
    
    # Identifier et corriger les doublons
    duplicates_found = 0
    corrected_lines = []
    
    for key, entries in grouped.items():
        if len(entries) > 1:
            duplicates_found += len(entries) - 1
            print(f"🔍 Doublons trouvés pour {key}: {len(entries)} entrées")
            
            # Stratégie de correction : garder la dernière entrée (plus récente)
            # ou celle avec les valeurs les plus récentes
            best_entry = entries[-1]  # Dernière entrée par défaut
            
            # Alternative : garder celle avec les valeurs les plus élevées (plus récentes)
            if data.get('type') in ['vva', 'atr', 'nbcv']:
                # Pour les indicateurs, garder celle avec les valeurs les plus récentes
                best_entry = max(entries, key=lambda x: (
                    x[1].get('vah', 0) + x[1].get('val', 0) + x[1].get('vpoc', 0) +
                    x[1].get('pvah', 0) + x[1].get('pval', 0) + x[1].get('ppoc', 0)
                ))
            
            corrected_lines.append(best_entry[1])
            print(f"✅ Gardé: ligne {best_entry[0]}")
        else:
            corrected_lines.append(entries[0][1])
    
    # Sauvegarder le fichier corrigé
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.rename(file_path, backup_path)
    print(f"💾 Sauvegarde créée: {backup_path}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        for data in corrected_lines:
            f.write(json.dumps(data) + '\n')
    
    print(f"✅ Fichier corrigé: {file_path}")
    print(f"📊 Doublons supprimés: {duplicates_found}")
    return duplicates_found

def main():
    """Fonction principale"""
    print("🚀 DÉBUT DE LA CORRECTION DES DOUBLONS")
    print("=" * 50)
    
    # Fichiers à traiter
    files_to_fix = [
        "chart_3_vva_20250916.jsonl",
        "chart_3_atr_20250916.jsonl", 
        "chart_3_nbcv_20250916.jsonl",
        "chart_3_cumulative_delta_20250916.jsonl",
        "chart_3_pvwap_20250916.jsonl",
        "chart_3_trade_summary_20250916.jsonl",
        "chart_3_vwap_20250916.jsonl",
        "chart_3_basedata_20250916.jsonl",
        "chart_3_trade_20250916.jsonl",
        "chart_3_depth_20250916.jsonl",
        "chart_3_quote_20250916.jsonl"
    ]
    
    total_duplicates = 0
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            duplicates = fix_duplicates_in_file(file_path)
            total_duplicates += duplicates
            print()
        else:
            print(f"⚠️  Fichier non trouvé: {file_path}")
    
    print("=" * 50)
    print(f"🎉 CORRECTION TERMINÉE")
    print(f"📊 Total des doublons supprimés: {total_duplicates}")
    print("💡 Relancez validate_g3_outputs.py pour vérifier les corrections")

if __name__ == "__main__":
    main()
