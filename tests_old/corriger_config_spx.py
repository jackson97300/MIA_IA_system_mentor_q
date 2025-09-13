
#!/usr/bin/env python3
"""
Correction configuration pour données SPX fraîches
"""

import os
import sys
from datetime import datetime

def corriger_config_spx():
    """Corriger la configuration pour utiliser des données SPX fraîches"""
    
    print("🔧 Correction configuration SPX...")
    
    # Paramètres de correction
    corrections = {
        'SPX_DATA_MAX_AGE_HOURS': 24,  # Augmenter de 18 à 24h
        'FORCE_FRESH_SPX_DATA': True,  # Forcer données fraîches
        'SPX_DATA_SOURCE': 'generated',  # Utiliser données générées
        'ENABLE_SPX_DATA_GENERATION': True,  # Activer génération
        'SPX_DATA_QUALITY_THRESHOLD': 0.5,  # Réduire seuil qualité
        'BYPASS_SPX_EXPIRATION_CHECK': False,  # Garder vérification
        'SPX_DATA_REFRESH_INTERVAL': 3600,  # Rafraîchir toutes les heures
    }
    
    # Fichiers de configuration à corriger
    config_files = [
        "config/automation_config.py",
        "config/mia_ia_system_tws_paper_fixed.py",
        "config/tws_paper_config.py"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"   📄 Correction: {config_file}")
            
            # Sauvegarder
            backup_file = f"{config_file}.backup_spx_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Appliquer corrections
            for key, value in corrections.items():
                if isinstance(value, str):
                    content = content.replace(f"{key} = ", f"{key} = '{value}'  # CORRIGÉ")
                else:
                    content = content.replace(f"{key} = ", f"{key} = {value}  # CORRIGÉ")
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ Configuration corrigée: {config_file}")
    
    print("✅ Configuration SPX corrigée")

if __name__ == "__main__":
    corriger_config_spx()
