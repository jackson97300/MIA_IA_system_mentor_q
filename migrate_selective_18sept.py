#!/usr/bin/env python3
"""
Migration sélective pour le 18 septembre
- Chart 3 du 18 septembre
- Chart 10 du 18 septembre
- unified_20250918_v9.jsonl → unified_20250918.jsonl
"""

import os
import shutil
import datetime

def get_month_name(month_num: str) -> str:
    """Convertit le numéro de mois en nom français"""
    month_names = {
        "01": "JANVIER", "02": "FEVRIER", "03": "MARS", "04": "AVRIL",
        "05": "MAI", "06": "JUIN", "07": "JUILLET", "08": "AOUT",
        "09": "SEPTEMBRE", "10": "OCTOBRE", "11": "NOVEMBRE", "12": "DECEMBRE"
    }
    return month_names.get(month_num, "INCONNU")

def get_organized_path(base_dir: str, ymd: str) -> str:
    """Génère le chemin organisé pour une date"""
    year = ymd[:4]
    month_num = ymd[4:6]
    month_name = get_month_name(month_num)
    
    return os.path.join(base_dir, "DATA_SIERRA_CHART", f"DATA_{year}", month_name, ymd)

def ensure_directory_exists(path: str) -> None:
    """Crée le répertoire s'il n'existe pas"""
    os.makedirs(path, exist_ok=True)
    print(f"✅ Répertoire créé/vérifié: {path}")

def migrate_selective_18sept(base_dir: str = "."):
    """Migration sélective pour le 18 septembre"""
    
    date = "20250918"
    print(f"=== MIGRATION SÉLECTIVE - {date} ===")
    
    # Créer la structure de dossiers
    organized_path = get_organized_path(base_dir, date)
    ensure_directory_exists(organized_path)
    ensure_directory_exists(os.path.join(organized_path, "CHART_3"))
    ensure_directory_exists(os.path.join(organized_path, "CHART_10"))
    
    # Fichiers à migrer
    files_to_migrate = [
        # Chart 3
        ("chart_3_atr_20250918.jsonl", "CHART_3"),
        ("chart_3_basedata_20250918.jsonl", "CHART_3"),
        ("chart_3_cumulative_delta_20250918.jsonl", "CHART_3"),
        ("chart_3_depth_20250918.jsonl", "CHART_3"),
        ("chart_3_nbcv_20250918.jsonl", "CHART_3"),
        ("chart_3_pvwap_20250918.jsonl", "CHART_3"),
        ("chart_3_quote_20250918.jsonl", "CHART_3"),
        ("chart_3_trade_20250918.jsonl", "CHART_3"),
        ("chart_3_trade_summary_20250918.jsonl", "CHART_3"),
        ("chart_3_vix_20250918.jsonl", "CHART_3"),
        ("chart_3_vva_20250918.jsonl", "CHART_3"),
        ("chart_3_vwap_20250918.jsonl", "CHART_3"),
        
        # Chart 10
        ("chart_10_menthorq_20250918.jsonl", "CHART_10"),
        
        # Unified (spécial)
        ("unified_20250918_v9.jsonl", "UNIFIED")
    ]
    
    results = {
        "migrated": 0,
        "skipped": 0,
        "errors": []
    }
    
    print(f"\n📁 Migration de {len(files_to_migrate)} fichiers...")
    
    for filename, category in files_to_migrate:
        source_path = os.path.join(base_dir, filename)
        
        if not os.path.exists(source_path):
            print(f"  ⚠️  {filename} n'existe pas, ignoré")
            results["skipped"] += 1
            continue
        
        # Chemin de destination
        if category == "UNIFIED":
            # Renommer unified_20250918_v9.jsonl → unified_20250918.jsonl
            dest_filename = "unified_20250918.jsonl"
            dest_path = os.path.join(organized_path, dest_filename)
        else:
            dest_path = os.path.join(organized_path, category, filename)
        
        try:
            if os.path.exists(dest_path):
                print(f"  ⚠️  {filename} existe déjà, ignoré")
                results["skipped"] += 1
            else:
                shutil.move(source_path, dest_path)
                print(f"  ✅ {filename} → {dest_path}")
                results["migrated"] += 1
                
        except Exception as e:
            error_msg = f"Erreur migration {filename}: {e}"
            print(f"  ❌ {error_msg}")
            results["errors"].append(error_msg)
    
    print(f"\n=== RÉSULTATS ===")
    print(f"✅ Fichiers migrés: {results['migrated']}")
    print(f"⚠️  Fichiers ignorés: {results['skipped']}")
    print(f"❌ Erreurs: {len(results['errors'])}")
    
    if results['errors']:
        print(f"\n❌ ERREURS:")
        for error in results['errors']:
            print(f"  - {error}")
    
    if results['migrated'] > 0:
        print(f"\n🎉 Migration sélective terminée avec succès!")
        print(f"📁 Structure créée: {organized_path}")
        print(f"📊 Fichiers organisés dans CHART_3/, CHART_10/, et unified_20250918.jsonl")

def main():
    migrate_selective_18sept()

if __name__ == "__main__":
    main()


