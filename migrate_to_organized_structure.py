#!/usr/bin/env python3
"""
Script de migration vers la structure organisée
Migre tous les fichiers existants vers la nouvelle structure DATA_SIERRA_CHART
"""

import os
import shutil
import glob
import datetime
from typing import List, Dict
import argparse

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

def categorize_file(filename: str) -> str:
    """Détermine la catégorie d'un fichier"""
    if "chart_3_" in filename:
        return "CHART_3"
    elif "chart_8_" in filename:
        return "CHART_8"
    elif "chart_10_" in filename:
        return "CHART_10"
    elif filename.startswith("unified_"):
        return "UNIFIED"
    else:
        return "OTHER"

def extract_date_from_filename(filename: str) -> str:
    """Extrait la date d'un nom de fichier"""
    # Chercher le pattern YYYYMMDD
    import re
    match = re.search(r'(\d{8})', filename)
    if match:
        return match.group(1)
    return None

def migrate_files(base_dir: str, dry_run: bool = False) -> Dict[str, any]:
    """Migre tous les fichiers vers la nouvelle structure"""
    
    # Patterns de fichiers à migrer
    patterns = [
        "chart_3_*.jsonl",
        "chart_8_*.jsonl", 
        "chart_10_*.jsonl",
        "unified_*.jsonl"
    ]
    
    results = {
        "total_found": 0,
        "total_migrated": 0,
        "total_skipped": 0,
        "errors": [],
        "migrations": []
    }
    
    # Trouver tous les fichiers
    all_files = []
    for pattern in patterns:
        files = glob.glob(os.path.join(base_dir, pattern))
        all_files.extend(files)
    
    results["total_found"] = len(all_files)
    
    print(f"📁 {len(all_files)} fichiers trouvés à migrer")
    
    # Grouper par date
    files_by_date = {}
    for file_path in all_files:
        filename = os.path.basename(file_path)
        date = extract_date_from_filename(filename)
        
        if date:
            if date not in files_by_date:
                files_by_date[date] = []
            files_by_date[date].append(file_path)
        else:
            results["errors"].append(f"Impossible d'extraire la date de: {filename}")
    
    print(f"📅 {len(files_by_date)} dates différentes trouvées")
    
    # Migrer chaque date
    for date, files in files_by_date.items():
        print(f"\n📅 Migration date {date} ({len(files)} fichiers)")
        
        # Créer la structure de dossiers
        organized_path = get_organized_path(base_dir, date)
        
        if not dry_run:
            ensure_directory_exists(organized_path)
            ensure_directory_exists(os.path.join(organized_path, "CHART_3"))
            ensure_directory_exists(os.path.join(organized_path, "CHART_8"))
            ensure_directory_exists(os.path.join(organized_path, "CHART_10"))
        
        # Migrer chaque fichier
        for file_path in files:
            filename = os.path.basename(file_path)
            category = categorize_file(filename)
            
            if category == "UNIFIED":
                dest_path = os.path.join(organized_path, filename)
            else:
                dest_path = os.path.join(organized_path, category, filename)
            
            try:
                if dry_run:
                    print(f"  🔍 [DRY RUN] {filename} → {dest_path}")
                    results["total_migrated"] += 1
                else:
                    if os.path.exists(dest_path):
                        print(f"  ⚠️  {filename} existe déjà, ignoré")
                        results["total_skipped"] += 1
                    else:
                        shutil.move(file_path, dest_path)
                        print(f"  ✅ {filename} → {dest_path}")
                        results["total_migrated"] += 1
                
                results["migrations"].append({
                    "source": file_path,
                    "dest": dest_path,
                    "category": category,
                    "date": date
                })
                
            except Exception as e:
                error_msg = f"Erreur migration {filename}: {e}"
                print(f"  ❌ {error_msg}")
                results["errors"].append(error_msg)
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Migration vers structure organisée")
    parser.add_argument("--base-dir", type=str, default=".", help="Répertoire de base")
    parser.add_argument("--dry-run", action="store_true", help="Simulation sans déplacement")
    parser.add_argument("--date", type=str, help="Migrer seulement une date spécifique (YYYYMMDD)")
    
    args = parser.parse_args()
    
    print("=== MIGRATION VERS STRUCTURE ORGANISÉE ===")
    print(f"Répertoire de base: {args.base_dir}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'MIGRATION RÉELLE'}")
    print()
    
    if args.date:
        # Migration d'une date spécifique
        print(f"📅 Migration date spécifique: {args.date}")
        # TODO: Implémenter migration date spécifique
    else:
        # Migration complète
        results = migrate_files(args.base_dir, args.dry_run)
        
        print(f"\n=== RÉSULTATS ===")
        print(f"📊 Fichiers trouvés: {results['total_found']}")
        print(f"✅ Fichiers migrés: {results['total_migrated']}")
        print(f"⚠️  Fichiers ignorés: {results['total_skipped']}")
        print(f"❌ Erreurs: {len(results['errors'])}")
        
        if results['errors']:
            print(f"\n❌ ERREURS:")
            for error in results['errors']:
                print(f"  - {error}")
        
        if not args.dry_run and results['total_migrated'] > 0:
            print(f"\n✅ Migration terminée avec succès!")
            print(f"📁 Nouvelle structure créée dans: DATA_SIERRA_CHART/")
        elif args.dry_run:
            print(f"\n🔍 Simulation terminée. Utilisez sans --dry-run pour migrer réellement.")

if __name__ == "__main__":
    main()


