#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Lancement sans options SPX
Évite la pause due aux données options expirées
"""

import os
import sys
import json
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_no_options_config():
    """Créer la configuration sans options"""
    
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
            "session": "LONDON_NO_OPTIONS"
        },
        "features_config": {
            "gamma_levels_proximity": 0.0,  # Désactivé
            "volume_confirmation": 0.40,    # Renforcé
            "vwap_trend_signal": 0.25,      # Renforcé
            "sierra_pattern_strength": 0.25, # Renforcé
            "smart_money_strength": 0.20,   # Renforcé
            "level_proximity": 0.12,        # Renforcé
            "es_nq_correlation": 0.12,      # Renforcé
            "order_book_imbalance": 0.25,   # Renforcé
            "session_context": 0.05,        # Renforcé
            "pullback_quality": 0.03        # Renforcé
        },
        "options_config": {
            "spx_options_enabled": False,   # Désactivé
            "skip_options_validation": True, # Ignorer validation
            "force_trading": True           # Forcer trading
        },
        "session_info": {
            "start_time": datetime.now().isoformat(),
            "tws_connection": True,
            "options_disabled": True,
            "reason": "Trading sans options SPX - Session London"
        }
    }
    
    return config

def launch_mia_ia_no_options():
    """Lancer MIA_IA_SYSTEM sans options"""
    
    print("🚀 MIA_IA_SYSTEM - LANCEMENT SANS OPTIONS")
    print("=" * 60)
    
    # Créer configuration
    config = create_no_options_config()
    
    print("\n🔧 Configuration TWS (sans options):")
    print(f"   Host: {config['ibkr_connection']['host']}")
    print(f"   Port: {config['ibkr_connection']['port']} (TWS)")
    print(f"   Client ID: {config['ibkr_connection']['client_id']}")
    print(f"   Options SPX: {'❌ Désactivé' if not config['options_config']['spx_options_enabled'] else '✅ Activé'}")
    print(f"   Force Trading: {'✅ Oui' if config['options_config']['force_trading'] else '❌ Non'}")
    
    print("\n📊 Features (redistribuées):")
    for feature, weight in config['features_config'].items():
        if weight > 0:
            print(f"   {feature}: {weight:.1%}")
    
    print("\n🎯 Lancement du système...")
    
    try:
        # Modifier la configuration pour désactiver les options
        import config.automation_config as auto_config
        
        # Configuration TWS
        auto_config.IBKR_HOST = config['ibkr_connection']['host']
        auto_config.IBKR_PORT = config['ibkr_connection']['port']
        auto_config.IBKR_CLIENT_ID = config['ibkr_connection']['client_id']
        auto_config.USE_IB_INSYNC = config['ibkr_connection']['use_ib_insync']
        
        # Désactiver les options
        auto_config.SPX_OPTIONS_ENABLED = False
        auto_config.SKIP_OPTIONS_VALIDATION = True
        auto_config.FORCE_TRADING = True
        
        # Redistribuer les poids des features
        auto_config.FEATURE_WEIGHTS = config['features_config']
        
        print("✅ Configuration appliquée (sans options)")
        print("🎉 Lancement MIA_IA_SYSTEM...")
        
        # Lancer le système principal
        from launch_24_7_orderflow_trading import main
        main()
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
    except Exception as e:
        print(f"❌ Erreur lancement: {e}")

if __name__ == "__main__":
    launch_mia_ia_no_options()






