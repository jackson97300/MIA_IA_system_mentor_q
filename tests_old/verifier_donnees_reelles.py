
#!/usr/bin/env python3
"""
Vérification données ES réelles
"""

import os
import sys
from datetime import datetime

def verifier_donnees_reelles():
    """Vérifier que le système utilise des données réelles"""
    
    print("🔍 Vérification données ES réelles...")
    
    # Vérifier la configuration
    config_files = [
        "config/automation_config.py",
        "config/mia_ia_system_tws_paper_fixed.py"
    ]
    
    real_data_detected = False
    
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'SIMULATION_MODE = False' in content:
                    print(f"✅ {config_file}: Mode simulation désactivé")
                    real_data_detected = True
                else:
                    print(f"❌ {config_file}: Mode simulation encore actif")
                
                if 'USE_REAL_DATA = True' in content:
                    print(f"✅ {config_file}: Données réelles activées")
                    real_data_detected = True
                else:
                    print(f"❌ {config_file}: Données réelles non activées")
                    
            except Exception as e:
                print(f"⚠️ Erreur vérification {config_file}: {e}")
    
    return real_data_detected

if __name__ == "__main__":
    success = verifier_donnees_reelles()
    if success:
        print("\n✅ Configuration données réelles détectée")
    else:
        print("\n❌ Configuration données réelles non trouvée")
