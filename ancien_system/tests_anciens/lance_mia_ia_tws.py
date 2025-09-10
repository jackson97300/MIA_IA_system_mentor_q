#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Lancement avec TWS
Configuration optimisée pour TWS (port 7497)
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_tws_config():
    """Créer la configuration TWS pour MIA_IA_SYSTEM"""
    
    config = {
        "ibkr_connection": {
            "host": "127.0.0.1",
            "port": 7497,  # TWS
            "client_id": 1,
            "connection_timeout": 20,
            "use_ib_insync": True
        },
        "trading_config": {
            "symbol": "ES",
            "exchange": "CME",
            "sec_type": "FUT",
            "paper_trading": True,
            "session": "LONDON_NO_OPTIONS"  # Session sans options
        },
        "features_config": {
            "gamma_levels_proximity": 0.0,  # Désactivé (pas d'options)
            "volume_confirmation": 0.35,    # Renforcé
            "vwap_trend_signal": 0.22,      # Renforcé
            "sierra_pattern_strength": 0.22, # Renforcé
            "smart_money_strength": 0.17,   # Renforcé
            "level_proximity": 0.10,        # Renforcé
            "es_nq_correlation": 0.10,      # Renforcé
            "order_book_imbalance": 0.21,   # Renforcé
            "session_context": 0.04,        # Renforcé
            "pullback_quality": 0.02        # Renforcé
        },
        "session_info": {
            "start_time": datetime.now().isoformat(),
            "tws_connection": True,
            "options_disabled": True,
            "reason": "Session London sans données options SPX"
        }
    }
    
    return config

def save_config(config):
    """Sauvegarder la configuration"""
    config_file = "config/mia_ia_tws_config.json"
    
    # Créer le dossier config s'il n'existe pas
    os.makedirs("config", exist_ok=True)
    
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"💾 Configuration sauvegardée: {config_file}")
    return config_file

def launch_mia_ia_system():
    """Lancer MIA_IA_SYSTEM avec TWS"""
    
    print("🚀 MIA_IA_SYSTEM - LANCEMENT AVEC TWS")
    print("=" * 60)
    
    # Créer configuration TWS
    config = create_tws_config()
    config_file = save_config(config)
    
    print("\n🔧 Configuration TWS:")
    print(f"   Host: {config['ibkr_connection']['host']}")
    print(f"   Port: {config['ibkr_connection']['port']} (TWS)")
    print(f"   Client ID: {config['ibkr_connection']['client_id']}")
    print(f"   Paper Trading: {config['trading_config']['paper_trading']}")
    print(f"   Session: {config['trading_config']['session']}")
    
    print("\n📊 Features (sans options):")
    for feature, weight in config['features_config'].items():
        if weight > 0:
            print(f"   {feature}: {weight:.1%}")
    
    print("\n🎯 Lancement du système...")
    
    try:
        # Importer et lancer le système principal
        from launch_24_7_orderflow_trading import main
        
        # Modifier la configuration pour utiliser TWS
        import config.automation_config as auto_config
        
        # Sauvegarder l'ancienne config
        old_config = {
            "ibkr_host": getattr(auto_config, 'IBKR_HOST', '127.0.0.1'),
            "ibkr_port": getattr(auto_config, 'IBKR_PORT', 4002),
            "ibkr_client_id": getattr(auto_config, 'IBKR_CLIENT_ID', 1)
        }
        
        # Appliquer la nouvelle config TWS
        auto_config.IBKR_HOST = config['ibkr_connection']['host']
        auto_config.IBKR_PORT = config['ibkr_connection']['port']
        auto_config.IBKR_CLIENT_ID = config['ibkr_connection']['client_id']
        auto_config.USE_IB_INSYNC = config['ibkr_connection']['use_ib_insync']
        
        print("✅ Configuration TWS appliquée")
        print("🎉 Lancement MIA_IA_SYSTEM...")
        
        # Lancer le système
        main()
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        print("💡 Vérifiez que tous les modules sont installés")
    except Exception as e:
        print(f"❌ Erreur lancement: {e}")
        print("💡 Vérifiez la configuration")

if __name__ == "__main__":
    launch_mia_ia_system()






