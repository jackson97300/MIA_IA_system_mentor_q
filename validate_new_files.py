#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 VALIDATEUR DES NOUVEAUX FICHIERS CHART 3
Vérifie la présence et la validité des 3 nouveaux fichiers JSONL
"""

import os
import json
import glob
from datetime import datetime, timedelta
import sys

def validate_new_files():
    """Valide la présence des nouveaux fichiers Chart 3"""
    
    print("🔍 VALIDATION DES NOUVEAUX FICHIERS CHART 3")
    print("=" * 50)
    
    # Chemin de base
    base_path = "D:\\MIA_IA_system\\DATA_SIERRA_CHART"
    
    # Date d'aujourd'hui
    today = datetime.now()
    year = today.year
    month_names = ["JANVIER", "FEVRIER", "MARS", "AVRIL", "MAI", "JUIN",
                   "JUILLET", "AOUT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE", "DECEMBRE"]
    month_name = month_names[today.month - 1]
    date_str = today.strftime("%Y%m%d")
    
    # Chemin complet
    chart_path = f"{base_path}\\DATA_{year}\\{month_name}\\{date_str}\\CHART_3"
    
    print(f"📁 Chemin de validation: {chart_path}")
    print()
    
    # Fichiers à valider
    files_to_validate = [
        f"chart_3_menthorq_gamma_{date_str}.jsonl",
        f"chart_3_menthorq_blind_spots_{date_str}.jsonl",
        f"chart_3_correlation_unified_{date_str}.jsonl"
    ]
    
    results = {}
    
    for filename in files_to_validate:
        filepath = os.path.join(chart_path, filename)
        print(f"🔍 Validation: {filename}")
        
        if not os.path.exists(filepath):
            print(f"❌ FICHIER MANQUANT: {filepath}")
            results[filename] = {"status": "MISSING", "count": 0, "last_entry": None}
            continue
        
        # Vérifier la taille du fichier
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            print(f"⚠️  FICHIER VIDE: {filepath}")
            results[filename] = {"status": "EMPTY", "count": 0, "last_entry": None}
            continue
        
        # Compter les lignes et valider le JSON
        line_count = 0
        last_entry = None
        valid_json_count = 0
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    line_count += 1
                    
                    try:
                        data = json.loads(line)
                        valid_json_count += 1
                        
                        # Garder la dernière entrée valide
                        if line_num <= 10 or line_num % 100 == 0:  # Log des premières et quelques autres
                            last_entry = data
                            
                    except json.JSONDecodeError as e:
                        print(f"⚠️  JSON invalide ligne {line_num}: {e}")
        
        except Exception as e:
            print(f"❌ ERREUR LECTURE: {e}")
            results[filename] = {"status": "ERROR", "count": 0, "last_entry": None}
            continue
        
        # Résultats
        status = "✅ OK" if valid_json_count > 0 else "⚠️  AUCUNE DONNÉE VALIDE"
        print(f"   {status} - Lignes: {line_count}, JSON valides: {valid_json_count}")
        
        if last_entry:
            print(f"   📊 Dernière entrée: {last_entry.get('type', 'N/A')} - t={last_entry.get('t', 'N/A')}")
        
        results[filename] = {
            "status": "OK" if valid_json_count > 0 else "NO_VALID_DATA",
            "count": valid_json_count,
            "last_entry": last_entry
        }
        
        print()
    
    # Résumé
    print("📊 RÉSUMÉ DE LA VALIDATION")
    print("=" * 30)
    
    total_files = len(files_to_validate)
    ok_files = sum(1 for r in results.values() if r["status"] == "OK")
    missing_files = sum(1 for r in results.values() if r["status"] == "MISSING")
    error_files = sum(1 for r in results.values() if r["status"] in ["ERROR", "EMPTY", "NO_VALID_DATA"])
    
    print(f"📁 Fichiers attendus: {total_files}")
    print(f"✅ Fichiers OK: {ok_files}")
    print(f"❌ Fichiers manquants: {missing_files}")
    print(f"⚠️  Fichiers avec erreurs: {error_files}")
    
    if ok_files == total_files:
        print("\n🎉 TOUS LES FICHIERS SONT VALIDES !")
        return True
    else:
        print(f"\n⚠️  {total_files - ok_files} FICHIER(S) ONT DES PROBLÈMES")
        return False

def check_recent_activity():
    """Vérifie l'activité récente des fichiers"""
    
    print("\n🕐 VÉRIFICATION DE L'ACTIVITÉ RÉCENTE")
    print("=" * 40)
    
    base_path = "D:\\MIA_IA_system\\DATA_SIERRA_CHART"
    today = datetime.now()
    year = today.year
    month_names = ["JANVIER", "FEVRIER", "MARS", "AVRIL", "MAI", "JUIN",
                   "JUILLET", "AOUT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE", "DECEMBRE"]
    month_name = month_names[today.month - 1]
    date_str = today.strftime("%Y%m%d")
    
    chart_path = f"{base_path}\\DATA_{year}\\{month_name}\\{date_str}\\CHART_3"
    
    if not os.path.exists(chart_path):
        print(f"❌ Répertoire Chart 3 non trouvé: {chart_path}")
        return
    
    # Chercher tous les fichiers JSONL
    jsonl_files = glob.glob(os.path.join(chart_path, "*.jsonl"))
    
    if not jsonl_files:
        print("❌ Aucun fichier JSONL trouvé")
        return
    
    print(f"📁 Fichiers trouvés: {len(jsonl_files)}")
    
    for filepath in jsonl_files:
        filename = os.path.basename(filepath)
        try:
            mtime = os.path.getmtime(filepath)
            last_modified = datetime.fromtimestamp(mtime)
            time_diff = datetime.now() - last_modified
            
            if time_diff.total_seconds() < 300:  # Moins de 5 minutes
                status = "🟢 ACTIF"
            elif time_diff.total_seconds() < 1800:  # Moins de 30 minutes
                status = "🟡 RÉCENT"
            else:
                status = "🔴 ANCIEN"
            
            print(f"   {status} {filename} - Modifié: {last_modified.strftime('%H:%M:%S')} ({time_diff.total_seconds():.0f}s)")
            
        except Exception as e:
            print(f"   ❌ Erreur: {filename} - {e}")

if __name__ == "__main__":
    print("🚀 VALIDATEUR MIA UNIFIER v2.1 - NOUVEAUX FICHIERS CHART 3")
    print("=" * 60)
    
    # Validation principale
    success = validate_new_files()
    
    # Vérification de l'activité
    check_recent_activity()
    
    # Code de sortie
    sys.exit(0 if success else 1)

