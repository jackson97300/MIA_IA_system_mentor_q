#!/usr/bin/env python3
"""
Relance système avec données ES réelles - Version Définitive
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def relancer_donnees_reelles_definitif():
    """Relance définitive avec données ES réelles"""
    
    print("🚀 RELANCE DÉFINITIVE AVEC DONNÉES ES RÉELLES")
    print("=" * 50)
    
    # 1. Vérification
    print("\n🔍 Étape 1: Vérification configuration")
    try:
        result = subprocess.run("python verifier_donnees_reelles_definitif.py", 
                              shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ Erreurs: {result.stderr}")
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")
    
    # 2. Test connexion
    print("\n🧪 Étape 2: Test connexion réelle")
    try:
        result = subprocess.run("python test_connexion_reelle_definitif.py", 
                              shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ Erreurs: {result.stderr}")
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    
    # 3. Attendre
    print("\n⏰ Attente 10 secondes...")
    time.sleep(10)
    
    # 4. Relancer système
    print("\n🚀 Étape 3: Relance système")
    restart_commands = [
        "python launch_24_7_orderflow_trading.py",
        "python lance_mia_ia_tws.py"
    ]
    
    for command in restart_commands:
        if os.path.exists(command.split()[1]):
            try:
                print(f"   🚀 Lancement: {command}")
                subprocess.Popen(command, shell=True)
                print(f"   ✅ Système relancé: {command}")
                break
            except Exception as e:
                print(f"   ❌ Erreur relance: {command} - {e}")
    
    print("\n✅ Relance avec données réelles terminée")

if __name__ == "__main__":
    relancer_donnees_reelles_definitif()
