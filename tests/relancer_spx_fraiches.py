
#!/usr/bin/env python3
"""
Relance système avec données SPX fraîches
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def relancer_avec_spx_fraiches():
    """Relancer le système avec données SPX fraîches"""
    
    print("🚀 Relance avec données SPX fraîches...")
    
    # 1. Générer données SPX fraîches
    print("\n🔄 Étape 1: Génération données SPX fraîches")
    try:
        result = subprocess.run("python generer_spx_fraiches.py", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Données SPX fraîches générées")
        else:
            print(f"   ⚠️ Erreur génération: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Exception génération: {e}")
    
    # 2. Corriger configuration
    print("\n🔧 Étape 2: Correction configuration")
    try:
        result = subprocess.run("python corriger_config_spx.py", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Configuration corrigée")
        else:
            print(f"   ⚠️ Erreur configuration: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Exception configuration: {e}")
    
    # 3. Attendre un peu
    print("\n⏰ Attente 5 secondes...")
    time.sleep(5)
    
    # 4. Relancer le système
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
    
    print("\n✅ Relance avec SPX fraîches terminée")

if __name__ == "__main__":
    relancer_avec_spx_fraiches()
