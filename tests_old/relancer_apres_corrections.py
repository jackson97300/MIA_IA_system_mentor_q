
#!/usr/bin/env python3
"""
Relance automatique MIA_IA_SYSTEM après corrections
"""

import os
import sys
import time
import subprocess
from datetime import datetime

def relancer_systeme():
    """Relancer le système après corrections"""
    
    print("🚀 Relance automatique MIA_IA_SYSTEM...")
    
    # 1. Exécuter les corrections
    print("\n📋 Exécution des corrections...")
    
    corrections = [
        "python corriger_ohlc_auto.py",
        "python optimiser_tws.py", 
        "python verifier_volumes.py"
    ]
    
    for correction in corrections:
        try:
            print(f"   🔧 Exécution: {correction}")
            result = subprocess.run(correction, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ Succès: {correction}")
            else:
                print(f"   ⚠️ Erreur: {correction}")
        except Exception as e:
            print(f"   ❌ Exception: {correction} - {e}")
    
    # 2. Attendre un peu
    print("\n⏰ Attente 10 secondes...")
    time.sleep(10)
    
    # 3. Relancer le système
    print("\n🚀 Relance du système...")
    
    restart_commands = [
        "python lance_mia_ia_tws.py",
        "python launch_24_7_orderflow_trading.py"
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
    
    print("\n✅ Relance automatique terminée")

if __name__ == "__main__":
    relancer_systeme()
