#!/usr/bin/env python3
"""
Validateur de données pour le système MIA IA
Vérifie que tous les fichiers nécessaires sont présents et valides
"""

import os
import json
import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """Valideur de données pour le système MIA IA"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        
    def get_month_name(self, month_num: str) -> str:
        """Convertit le numéro de mois en nom français"""
        month_names = {
            "01": "JANVIER", "02": "FEVRIER", "03": "MARS", "04": "AVRIL",
            "05": "MAI", "06": "JUIN", "07": "JUILLET", "08": "AOUT",
            "09": "SEPTEMBRE", "10": "OCTOBRE", "11": "NOVEMBRE", "12": "DECEMBRE"
        }
        return month_names.get(month_num, "INCONNU")
    
    def get_organized_data_path(self, ymd: str) -> str:
        """Génère le chemin organisé pour les données"""
        year = ymd[:4]
        month_num = ymd[4:6]
        month_name = self.get_month_name(month_num)
        
        return os.path.join(self.base_dir, "DATA_SIERRA_CHART", f"DATA_{year}", month_name, ymd)
    
    def get_required_files(self, ymd: str) -> Dict[str, List[str]]:
        """Retourne la liste des fichiers requis pour une date donnée"""
        organized_path = self.get_organized_data_path(ymd)
        
        return {
            "CHART_3": [
                f"chart_3_basedata_{ymd}.jsonl",
                f"chart_3_trade_{ymd}.jsonl",
                f"chart_3_quote_{ymd}.jsonl",
                f"chart_3_depth_{ymd}.jsonl",
                f"chart_3_nbcv_{ymd}.jsonl",
                f"chart_3_vwap_{ymd}.jsonl",
                f"chart_3_vva_{ymd}.jsonl",
                f"chart_3_pvwap_{ymd}.jsonl",
                f"chart_3_atr_{ymd}.jsonl",
                f"chart_3_cumulative_delta_{ymd}.jsonl",
                f"chart_3_vix_{ymd}.jsonl"
            ],
            "CHART_10": [
                f"chart_10_menthorq_{ymd}.jsonl"
            ],
            "UNIFIED": [
                f"unified_{ymd}.jsonl"
            ]
        }
    
    def check_file_exists(self, file_path: str) -> Tuple[bool, str]:
        """Vérifie si un fichier existe et retourne des infos"""
        if not os.path.exists(file_path):
            return False, "Fichier manquant"
        
        try:
            stat = os.stat(file_path)
            size_mb = stat.st_size / (1024 * 1024)
            
            if size_mb == 0:
                return False, "Fichier vide"
            
            return True, f"OK ({size_mb:.2f} MB)"
        except Exception as e:
            return False, f"Erreur: {e}"
    
    def validate_jsonl_file(self, file_path: str, max_lines: int = 10) -> Tuple[bool, str]:
        """Valide qu'un fichier JSONL est bien formé"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines_checked = 0
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        json.loads(line)
                        lines_checked += 1
                        if lines_checked >= max_lines:
                            break
                    except json.JSONDecodeError as e:
                        return False, f"JSON invalide ligne {lines_checked + 1}: {e}"
                
                if lines_checked == 0:
                    return False, "Aucune ligne JSON valide"
                
                return True, f"JSONL valide ({lines_checked} lignes vérifiées)"
                
        except Exception as e:
            return False, f"Erreur lecture: {e}"
    
    def validate_date(self, ymd: str) -> bool:
        """Valide le format de date YYYYMMDD"""
        try:
            datetime.datetime.strptime(ymd, "%Y%m%d")
            return True
        except ValueError:
            return False
    
    def validate_all_files(self, ymd: str) -> Dict[str, any]:
        """Valide tous les fichiers pour une date donnée"""
        if not self.validate_date(ymd):
            return {
                "valid": False,
                "error": f"Format de date invalide: {ymd}",
                "files": {}
            }
        
        organized_path = self.get_organized_data_path(ymd)
        required_files = self.get_required_files(ymd)
        
        results = {
            "valid": True,
            "date": ymd,
            "organized_path": organized_path,
            "files": {},
            "summary": {
                "total_required": 0,
                "total_found": 0,
                "total_valid": 0,
                "missing": [],
                "invalid": []
            }
        }
        
        # Vérifier chaque catégorie de fichiers
        for category, files in required_files.items():
            results["files"][category] = {}
            
            for filename in files:
                results["summary"]["total_required"] += 1
                
                if category == "UNIFIED":
                    file_path = os.path.join(organized_path, filename)
                else:
                    file_path = os.path.join(organized_path, category, filename)
                
                # Vérifier existence
                exists, exists_msg = self.check_file_exists(file_path)
                
                if not exists:
                    results["files"][category][filename] = {
                        "exists": False,
                        "message": exists_msg,
                        "path": file_path
                    }
                    results["summary"]["missing"].append(f"{category}/{filename}")
                    continue
                
                results["summary"]["total_found"] += 1
                
                # Vérifier validité JSONL
                is_valid, valid_msg = self.validate_jsonl_file(file_path)
                
                results["files"][category][filename] = {
                    "exists": True,
                    "valid": is_valid,
                    "message": f"{exists_msg} - {valid_msg}",
                    "path": file_path
                }
                
                if is_valid:
                    results["summary"]["total_valid"] += 1
                else:
                    results["summary"]["invalid"].append(f"{category}/{filename}")
                    results["valid"] = False
        
        return results
    
    def get_today_files_status(self) -> Dict[str, any]:
        """Vérifie les fichiers du jour"""
        today = datetime.datetime.now().strftime("%Y%m%d")
        return self.validate_all_files(today)
    
    def print_validation_report(self, results: Dict[str, any]) -> None:
        """Affiche un rapport de validation"""
        print(f"\n=== RAPPORT DE VALIDATION DES DONNÉES ===")
        print(f"Date: {results['date']}")
        print(f"Chemin organisé: {results['organized_path']}")
        print(f"Statut global: {'✅ VALIDE' if results['valid'] else '❌ INVALIDE'}")
        print()
        
        print(f"📊 RÉSUMÉ:")
        print(f"  - Fichiers requis: {results['summary']['total_required']}")
        print(f"  - Fichiers trouvés: {results['summary']['total_found']}")
        print(f"  - Fichiers valides: {results['summary']['total_valid']}")
        
        if results['summary']['missing']:
            print(f"  - Fichiers manquants: {len(results['summary']['missing'])}")
            for missing in results['summary']['missing']:
                print(f"    ❌ {missing}")
        
        if results['summary']['invalid']:
            print(f"  - Fichiers invalides: {len(results['summary']['invalid'])}")
            for invalid in results['summary']['invalid']:
                print(f"    ⚠️  {invalid}")
        
        print(f"\n📁 DÉTAIL PAR CATÉGORIE:")
        for category, files in results['files'].items():
            print(f"\n  {category}:")
            for filename, info in files.items():
                status = "✅" if info.get('valid', False) else ("⚠️" if info.get('exists', False) else "❌")
                print(f"    {status} {filename}: {info['message']}")

def main():
    """Fonction principale pour tester le validateur"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validateur de données MIA IA")
    parser.add_argument("--date", type=str, default="today", help="Date à valider (YYYYMMDD ou 'today')")
    parser.add_argument("--base-dir", type=str, default=".", help="Répertoire de base")
    
    args = parser.parse_args()
    
    # Résoudre la date
    if args.date.lower() == "today":
        ymd = datetime.datetime.now().strftime("%Y%m%d")
    else:
        ymd = args.date
    
    # Valider
    validator = DataValidator(args.base_dir)
    results = validator.validate_all_files(ymd)
    
    # Afficher le rapport
    validator.print_validation_report(results)
    
    # Code de sortie
    sys.exit(0 if results['valid'] else 1)

if __name__ == "__main__":
    import sys
    main()
