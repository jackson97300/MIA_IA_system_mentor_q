
#!/usr/bin/env python3
"""
Vérification volumes de données
"""

import os
import glob
import re
from datetime import datetime

def verifier_volumes():
    """Vérifier et corriger les volumes constants"""
    
    print("⚠️ Vérification volumes...")
    
    # Patterns de volumes constants
    volume_patterns = [
        r'volume: 192\.0',
        r'Volume: 192',
        r'volume constant',
        r'volume unchanged'
    ]
    
    # Fichiers à vérifier
    log_files = glob.glob("logs/*.log") + glob.glob("*.log")
    
    volume_issues = 0
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Compter les problèmes de volume
            for pattern in volume_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                volume_issues += len(matches)
            
            if volume_issues > 0:
                print(f"   ⚠️ {volume_issues} problèmes volume dans {log_file}")
        
        except Exception as e:
            print(f"   ⚠️ Erreur vérification {log_file}: {e}")
    
    if volume_issues == 0:
        print("✅ Aucun problème de volume détecté")
    else:
        print(f"⚠️ {volume_issues} problèmes de volume détectés")
        print("   💡 Recommandation: Vérifier source de données")
    
    return volume_issues == 0

if __name__ == "__main__":
    verifier_volumes()
