#!/usr/bin/env python3
"""
Script de validation pour la collecte complète du Graphique 3
Vérifie que tous les fichiers JSONL sont générés correctement
"""

import os
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path

def validate_g3_collection(date_str=None):
    """
    Valide la collecte complète du Graphique 3
    
    Args:
        date_str: Date au format YYYYMMDD (défaut: aujourd'hui)
    """
    
    if date_str is None:
        date_str = datetime.now().strftime("%Y%m%d")
    
    print(f"🔍 VALIDATION COLLECTE GRAPHIQUE 3 - {date_str}")
    print("=" * 60)
    
    # Chemin de base
    base_path = Path("D:/MIA_IA_system/DATA_SIERRA_CHART")
    
    # Construire le chemin de la date
    year = date_str[:4]
    month_names = ["JANVIER", "FEVRIER", "MARS", "AVRIL", "MAI", "JUIN",
                   "JUILLET", "AOUT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE", "DECEMBRE"]
    month = month_names[int(date_str[4:6]) - 1]
    
    chart_path = base_path / f"DATA_{year}" / month / date_str / "CHART_3"
    
    if not chart_path.exists():
        print(f"❌ ERREUR: Répertoire Chart 3 non trouvé: {chart_path}")
        return False
    
    print(f"📁 Répertoire Chart 3: {chart_path}")
    
    # Liste des fichiers attendus
    expected_files = [
        "chart_3_basedata_{}.jsonl",
        "chart_3_depth_{}.jsonl", 
        "chart_3_quote_{}.jsonl",
        "chart_3_trade_{}.jsonl",
        "chart_3_trade_summary_{}.jsonl",
        "chart_3_vwap_{}.jsonl",
        "chart_3_vva_{}.jsonl",
        "chart_3_pvwap_{}.jsonl",
        "chart_3_nbcv_{}.jsonl",
        "chart_3_cumulative_delta_{}.jsonl",
        "chart_3_atr_{}.jsonl",
        "chart_3_vix_{}.jsonl",
        "chart_3_correlation_{}.jsonl",
        "chart_3_menthorq_gamma_{}.jsonl",
        "chart_3_menthorq_blind_spots_{}.jsonl",
        "chart_3_correlation_unified_{}.jsonl"
    ]
    
    # Validation des fichiers
    results = {}
    total_files = len(expected_files)
    found_files = 0
    
    for file_pattern in expected_files:
        filename = file_pattern.format(date_str)
        file_path = chart_path / filename
        
        if file_path.exists():
            found_files += 1
            file_size = file_path.stat().st_size
            line_count = count_lines(file_path)
            
            results[filename] = {
                "exists": True,
                "size": file_size,
                "lines": line_count,
                "status": "✅"
            }
            
            print(f"✅ {filename:<35} | {file_size:>8} bytes | {line_count:>6} lines")
        else:
            results[filename] = {
                "exists": False,
                "size": 0,
                "lines": 0,
                "status": "❌"
            }
            print(f"❌ {filename:<35} | {'MISSING':>8} | {'0':>6} lines")
    
    print("\n" + "=" * 60)
    print(f"📊 RÉSUMÉ: {found_files}/{total_files} fichiers trouvés")
    
    # Validation du contenu des fichiers
    if found_files > 0:
        print("\n🔍 VALIDATION DU CONTENU:")
        validate_file_content(chart_path, date_str, results)
    
    # Recommandations
    print("\n💡 RECOMMANDATIONS:")
    if found_files < total_files:
        print("⚠️  Certains fichiers manquent - vérifiez la configuration Sierra Chart")
        print("⚠️  Assurez-vous que MIA_Dumper_G3_Unifier.cpp est activé sur Chart 3")
    else:
        print("✅ Tous les fichiers sont présents - collecte complète réussie!")
    
    return found_files == total_files

def count_lines(file_path):
    """Compte le nombre de lignes dans un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except:
        return 0

def validate_file_content(chart_path, date_str, results):
    """Valide le contenu des fichiers JSONL"""
    
    # Fichiers prioritaires à valider
    priority_files = [
        "chart_3_basedata_{}.jsonl",
        "chart_3_vwap_{}.jsonl", 
        "chart_3_menthorq_gamma_{}.jsonl",
        "chart_3_menthorq_blind_spots_{}.jsonl"
    ]
    
    for file_pattern in priority_files:
        filename = file_pattern.format(date_str)
        file_path = chart_path / filename
        
        if results[filename]["exists"] and results[filename]["lines"] > 0:
            validate_jsonl_structure(file_path, filename)

def validate_jsonl_structure(file_path, filename):
    """Valide la structure JSONL d'un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if not lines:
            print(f"⚠️  {filename}: Fichier vide")
            return
        
        # Valider les premières et dernières lignes
        first_line = lines[0].strip()
        last_line = lines[-1].strip() if len(lines) > 1 else first_line
        
        # Parser JSON
        try:
            first_json = json.loads(first_line)
            last_json = json.loads(last_line)
            
            # Vérifications de base
            required_fields = ["t", "sym", "type", "chart"]
            missing_fields = [field for field in required_fields if field not in first_json]
            
            if missing_fields:
                print(f"⚠️  {filename}: Champs manquants: {missing_fields}")
            else:
                print(f"✅ {filename}: Structure JSON valide")
                
        except json.JSONDecodeError as e:
            print(f"❌ {filename}: Erreur JSON - {e}")
            
    except Exception as e:
        print(f"❌ {filename}: Erreur de lecture - {e}")

def main():
    """Fonction principale"""
    import sys
    
    date_str = None
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    
    success = validate_g3_collection(date_str)
    
    if success:
        print("\n🎉 VALIDATION RÉUSSIE - Collecte complète du Graphique 3!")
        sys.exit(0)
    else:
        print("\n❌ VALIDATION ÉCHOUÉE - Vérifiez la configuration")
        sys.exit(1)

if __name__ == "__main__":
    main()


