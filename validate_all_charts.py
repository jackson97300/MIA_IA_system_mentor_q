#!/usr/bin/env python3
"""
Script de validation pour TOUS les charts (3 et 9)
Vérifie que tous les fichiers JSONL sont générés correctement pour ES et NQ
"""

import os
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path

def validate_chart_collection(chart_number, date_str):
    """
    Valide la collecte d'un chart spécifique
    
    Args:
        chart_number: Numéro du chart (3 ou 9)
        date_str: Date au format YYYYMMDD
    """
    
    print(f"🔍 VALIDATION CHART {chart_number} - {date_str}")
    print("=" * 60)
    
    # Chemin de base
    base_path = Path("D:/MIA_IA_system/DATA_SIERRA_CHART")
    
    # Construire le chemin de la date
    year = date_str[:4]
    month_names = ["JANVIER", "FEVRIER", "MARS", "AVRIL", "MAI", "JUIN",
                   "JUILLET", "AOUT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE", "DECEMBRE"]
    month = month_names[int(date_str[4:6]) - 1]
    
    chart_path = base_path / f"DATA_{year}" / month / date_str / f"CHART_{chart_number}"
    
    if not chart_path.exists():
        print(f"❌ ERREUR: Répertoire Chart {chart_number} non trouvé: {chart_path}")
        return False
    
    print(f"📁 Répertoire Chart {chart_number}: {chart_path}")
    
    # Liste des fichiers attendus
    expected_files = [
        f"chart_{chart_number}_basedata_{date_str}.jsonl",
        f"chart_{chart_number}_depth_{date_str}.jsonl", 
        f"chart_{chart_number}_quote_{date_str}.jsonl",
        f"chart_{chart_number}_trade_{date_str}.jsonl",
        f"chart_{chart_number}_trade_summary_{date_str}.jsonl",
        f"chart_{chart_number}_vwap_{date_str}.jsonl",
        f"chart_{chart_number}_vva_{date_str}.jsonl",
        f"chart_{chart_number}_pvwap_{date_str}.jsonl",
        f"chart_{chart_number}_nbcv_{date_str}.jsonl",
        f"chart_{chart_number}_cumulative_delta_{date_str}.jsonl",
        f"chart_{chart_number}_atr_{date_str}.jsonl",
        f"chart_{chart_number}_vix_{date_str}.jsonl",
        f"chart_{chart_number}_correlation_{date_str}.jsonl",
        f"chart_{chart_number}_menthorq_gamma_{date_str}.jsonl",
        f"chart_{chart_number}_menthorq_blind_spots_{date_str}.jsonl",
        f"chart_{chart_number}_correlation_unified_{date_str}.jsonl"
    ]
    
    # Validation des fichiers
    results = {}
    total_files = len(expected_files)
    found_files = 0
    files_with_data = 0
    
    for filename in expected_files:
        file_path = chart_path / filename
        
        if file_path.exists():
            found_files += 1
            file_size = file_path.stat().st_size
            line_count = count_lines(file_path)
            
            if file_size > 0:
                files_with_data += 1
            
            results[filename] = {
                "exists": True,
                "size": file_size,
                "lines": line_count,
                "has_data": file_size > 0,
                "status": "✅" if file_size > 0 else "⚠️"
            }
            
            status_icon = "✅" if file_size > 0 else "⚠️"
            print(f"{status_icon} {filename:<45} | {file_size:>8} bytes | {line_count:>6} lines")
        else:
            results[filename] = {
                "exists": False,
                "size": 0,
                "lines": 0,
                "has_data": False,
                "status": "❌"
            }
            print(f"❌ {filename:<45} | {'MISSING':>8} | {'0':>6} lines")
    
    print("\n" + "=" * 60)
    print(f"📊 RÉSUMÉ CHART {chart_number}: {found_files}/{total_files} fichiers trouvés, {files_with_data} avec données")
    
    # Validation du contenu des fichiers avec données
    if files_with_data > 0:
        print(f"\n🔍 VALIDATION DU CONTENU CHART {chart_number}:")
        validate_file_content(chart_path, results)
    
    return {
        "chart": chart_number,
        "total_files": total_files,
        "found_files": found_files,
        "files_with_data": files_with_data,
        "results": results
    }

def count_lines(file_path):
    """Compte le nombre de lignes dans un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except:
        return 0

def validate_file_content(chart_path, results):
    """Valide le contenu des fichiers JSONL"""
    
    for filename, file_info in results.items():
        if file_info["has_data"]:
            file_path = chart_path / filename
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
                symbol = first_json.get("sym", "UNKNOWN")
                chart = first_json.get("chart", "UNKNOWN")
                print(f"✅ {filename}: {symbol} Chart {chart} - Structure JSON valide")
                
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
    else:
        date_str = datetime.now().strftime("%Y%m%d")
    
    print(f"🚀 VALIDATION COMPLÈTE - TOUS LES CHARTS - {date_str}")
    print("=" * 80)
    
    # Valider Chart 3 (ES)
    chart3_results = validate_chart_collection(3, date_str)
    
    print("\n" + "=" * 80)
    
    # Valider Chart 9 (NQ)
    chart9_results = validate_chart_collection(9, date_str)
    
    print("\n" + "=" * 80)
    print("🎯 RÉSUMÉ GLOBAL")
    print("=" * 80)
    
    # Comparaison des résultats
    print(f"📊 CHART 3 (ES): {chart3_results['files_with_data']}/{chart3_results['total_files']} fichiers avec données")
    print(f"📊 CHART 9 (NQ): {chart9_results['files_with_data']}/{chart9_results['total_files']} fichiers avec données")
    
    # Diagnostic
    if chart3_results['files_with_data'] > chart9_results['files_with_data']:
        print(f"\n⚠️  DIAGNOSTIC: Chart 9 a moins de données que Chart 3")
        print(f"   - Chart 3: {chart3_results['files_with_data']} fichiers avec données")
        print(f"   - Chart 9: {chart9_results['files_with_data']} fichiers avec données")
        print(f"   - Différence: {chart3_results['files_with_data'] - chart9_results['files_with_data']} fichiers")
        
        print(f"\n💡 RECOMMANDATIONS:")
        print(f"   1. Vérifier que MIA_Dumper_G3_Unifier.cpp est activé sur Chart 9")
        print(f"   2. Vérifier que toutes les études sont ajoutées sur Chart 9")
        print(f"   3. Vérifier que les Study IDs sont corrects sur Chart 9")
        print(f"   4. Attendre quelques minutes pour que les données se génèrent")
    elif chart3_results['files_with_data'] == chart9_results['files_with_data']:
        print(f"\n✅ PARFAIT: Chart 3 et Chart 9 ont le même nombre de fichiers avec données")
    else:
        print(f"\n🤔 INATTENDU: Chart 9 a plus de données que Chart 3")
    
    # Succès global
    total_success = (chart3_results['files_with_data'] == chart3_results['total_files'] and 
                    chart9_results['files_with_data'] == chart9_results['total_files'])
    
    if total_success:
        print(f"\n🎉 VALIDATION RÉUSSIE - Collecte complète sur tous les charts!")
        sys.exit(0)
    else:
        print(f"\n⚠️  VALIDATION PARTIELLE - Vérifiez la configuration")
        sys.exit(1)

if __name__ == "__main__":
    main()

