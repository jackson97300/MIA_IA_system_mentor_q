#!/usr/bin/env python3
"""
Vérification données ES réelles - Version Définitive
"""

import os
import sys
import re
from datetime import datetime

def verifier_donnees_reelles_definitif():
    """Vérification définitive des données réelles"""
    
    print("🔍 VÉRIFICATION DÉFINITIVE DONNÉES ES RÉELLES")
    print("=" * 50)
    
    # Fichiers à vérifier
    files_to_check = [
        "config/automation_config.py",
        "config/mia_ia_system_tws_paper_fixed.py",
        "core/ibkr_connector.py",
        "data/market_data_feed.py"
    ]
    
    all_ok = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"\n📄 Vérification: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Vérifications critiques
                checks = [
                    ("simulation_mode = False", "Mode simulation désactivé"),
                    ("USE_REAL_DATA = True", "Données réelles activées"),
                    ("FORCE_REAL_DATA = True", "Forçage données réelles"),
                    ("DataSource.IBKR", "Source IBKR configurée"),
                    ("port: 7497", "Port TWS correct"),
                ]
                
                file_ok = True
                for check, description in checks:
                    if check in content:
                        print(f"   ✅ {description}")
                    else:
                        print(f"   ❌ {description} - MANQUANT")
                        file_ok = False
                
                # Vérifications négatives (ne doivent PAS être présents)
                negative_checks = [
                    ("simulation_mode = True", "Mode simulation encore actif"),
                    ("DataSource.SIMULATION", "Source simulation détectée"),
                    ("USE_REAL_DATA = False", "Données réelles désactivées"),
                ]
                
                for check, description in negative_checks:
                    if check in content:
                        print(f"   ❌ {description} - PROBLÈME")
                        file_ok = False
                
                if not file_ok:
                    all_ok = False
                    
            except Exception as e:
                print(f"   ❌ Erreur vérification: {e}")
                all_ok = False
    
    return all_ok

if __name__ == "__main__":
    success = verifier_donnees_reelles_definitif()
    if success:
        print("\n✅ TOUTES LES VÉRIFICATIONS RÉUSSIES")
        print("✅ Données ES réelles configurées")
    else:
        print("\n❌ PROBLÈMES DÉTECTÉS")
        print("❌ Correction nécessaire")
