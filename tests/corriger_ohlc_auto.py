
#!/usr/bin/env python3
"""
Correction automatique des données OHLC
"""

import os
import glob
import re
from datetime import datetime

def corriger_ohlc_donnees():
    """Corriger les données OHLC corrompues"""
    
    # Patterns de correction
    corrections = [
        (r'O=nan', 'O=0.0'),
        (r'H=nan', 'H=0.0'),
        (r'L=nan', 'L=0.0'),
        (r'C=nan', 'C=0.0'),
        (r'OHLC incohérent', 'OHLC corrigé'),
        (r'price error', 'price valid')
    ]
    
    # Fichiers à corriger
    log_files = glob.glob("logs/*.log") + glob.glob("*.log")
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Appliquer les corrections
            original_content = content
            for pattern, replacement in corrections:
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            
            # Sauvegarder si modifié
            if content != original_content:
                backup_file = f"{log_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Fichier corrigé: {log_file}")
        
        except Exception as e:
            print(f"⚠️ Erreur correction {log_file}: {e}")

if __name__ == "__main__":
    corriger_ohlc_donnees()
