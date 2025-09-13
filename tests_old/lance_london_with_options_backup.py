#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Lancement Session London avec Options Backup
Utilise les données options sauvegardées du 11 août pour la session London
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.logger import get_logger
from data.options_data_manager import OPTIONS_DATA_MANAGER

logger = get_logger(__name__)

def load_options_backup():
    """Charger les données options sauvegardées"""
    backup_path = Path("data/backups/options_spx_20250811_152715")
    
    if not backup_path.exists():
        logger.error("❌ Backup options non trouvé")
        return None
    
    # Charger les données finales
    final_file = backup_path / "options_snapshots" / "spx_final_20250811.json"
    
    if final_file.exists():
        try:
            with open(final_file, 'r') as f:
                data = json.load(f)
            logger.info(f"✅ Données options chargées: {final_file}")
            return data
        except Exception as e:
            logger.error(f"❌ Erreur chargement: {e}")
            return None
    else:
        logger.error(f"❌ Fichier final non trouvé: {final_file}")
        return None

def create_session_config(options_data):
    """Créer la configuration de session avec les données options"""
    
    session_config = {
        "session_info": {
            "session": "LONDON",
            "start_time": datetime.now().isoformat(),
            "options_source": "backup_20250811",
            "valid_until": "2025-08-12T15:30:00"
        },
        "options_data": options_data,
        "trading_config": {
            "session": "london",
            "focus": "Trend continuation",
            "risk_level": "High",
            "volume": "Elevé",
            "key_levels": [
                "Gamma Exposure",
                "Pin Risk", 
                "Dealer Positioning"
            ]
        },
        "gamma_levels_proximity": {
            "enabled": True,
            "source": "backup",
            "weight": 0.28  # 28% comme dans le système
        }
    }
    
    return session_config

def save_session_config(config):
    """Sauvegarder la configuration de session"""
    session_dir = Path("data/preparation/sessions_20250812")
    session_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = session_dir / "london_session_config.json"
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"✅ Configuration session sauvegardée: {config_file}")
    return config_file

def launch_london_session():
    """Lancer la session London avec options backup"""
    
    logger.info("🚀 Lancement Session London avec Options Backup")
    
    # 1. Charger les données options sauvegardées
    options_data = load_options_backup()
    if not options_data:
        logger.error("❌ Impossible de charger les données options")
        return False
    
    # 2. Créer la configuration de session
    session_config = create_session_config(options_data)
    
    # 3. Sauvegarder la configuration
    config_file = save_session_config(session_config)
    
    # 4. Lancer le système principal avec la configuration
    logger.info("🎯 Lancement du système principal...")
    
    # Importer et lancer le système principal
    try:
        from launch_24_7_orderflow_trading import main
        
        # Passer les arguments pour le mode London avec options
        sys.argv = [
            'launch_24_7_orderflow_trading.py',
            '--live',  # Mode paper trading
            '--session', 'london',
            '--options-backup', str(config_file)
        ]
        
        main()
        
    except ImportError as e:
        logger.error(f"❌ Erreur import système principal: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur lancement: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = launch_london_session()
    
    if success:
        logger.info("✅ Session London lancée avec succès avec options backup")
    else:
        logger.error("❌ Échec lancement session London")
        sys.exit(1)






