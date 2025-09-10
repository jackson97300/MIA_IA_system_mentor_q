
#!/usr/bin/env python3
"""
Configuration TWS optimisée pour MIA_IA_SYSTEM
"""

import os
import sys
from datetime import datetime

def configurer_tws_optimise():
    """Configurer TWS pour performance optimale"""
    
    print("🔧 Configuration TWS optimisée...")
    
    # Paramètres de connexion optimisés
    config_optimisations = {
        'IBKR_HOST': '127.0.0.1',
        'IBKR_PORT': 7497,
        'IBKR_CLIENT_ID': 1,
        'IBKR_TIMEOUT': 60,  # Augmenté de 30 à 60
        'IBKR_RETRY_ATTEMPTS': 5,  # Augmenté de 3 à 5
        'IBKR_RETRY_DELAY': 10,  # Augmenté de 5 à 10
        'IBKR_HEARTBEAT_INTERVAL': 30,  # Nouveau paramètre
        'IBKR_CONNECTION_TIMEOUT': 120,  # Nouveau paramètre
        'IBKR_MAX_RECONNECT_ATTEMPTS': 10,  # Nouveau paramètre
        'IBKR_RECONNECT_DELAY': 15,  # Nouveau paramètre
        'ENABLE_CONNECTION_MONITORING': True,  # Nouveau paramètre
        'CONNECTION_HEALTH_CHECK_INTERVAL': 30,  # Nouveau paramètre
        'AUTO_RECONNECT_ON_FAILURE': True,  # Nouveau paramètre
        'LOG_CONNECTION_EVENTS': True,  # Nouveau paramètre
        'VALIDATE_CONNECTION_BEFORE_TRADE': True,  # Nouveau paramètre
    }
    
    # Fichiers de configuration à mettre à jour
    config_files = [
        "config/mia_ia_system_tws_paper_fixed.py",
        "config/tws_paper_config.py",
        "config/ibkr_config.py",
        "config/automation_config.py"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"   📄 Mise à jour: {config_file}")
            
            # Sauvegarder l'ancienne config
            backup_file = f"{config_file}.backup_optimisation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Appliquer les optimisations
            for key, value in config_optimisations.items():
                if isinstance(value, str):
                    content = content.replace(f"{key} = ", f"{key} = '{value}'  # OPTIMISÉ")
                else:
                    content = content.replace(f"{key} = ", f"{key} = {value}  # OPTIMISÉ")
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ Configuration optimisée: {config_file}")
    
    print("✅ Configuration TWS optimisée terminée")

if __name__ == "__main__":
    configurer_tws_optimise()
