#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Lancement FORCE TRADING
Désactive complètement la vérification des options SPX
"""

import os
import sys
import json
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def force_trading_config():
    """Configuration qui force le trading"""
    
    print("🚀 MIA_IA_SYSTEM - FORCE TRADING")
    print("=" * 60)
    
    try:
        # Modifier directement les fichiers de configuration
        import config.automation_config as auto_config
        
        # Configuration TWS
        auto_config.IBKR_HOST = "127.0.0.1"
        auto_config.IBKR_PORT = 7497
        auto_config.IBKR_CLIENT_ID = 1
        auto_config.USE_IB_INSYNC = True
        
        # FORCER LE TRADING - Désactiver toutes les vérifications options
        auto_config.SPX_OPTIONS_ENABLED = False
        auto_config.SKIP_OPTIONS_VALIDATION = True
        auto_config.FORCE_TRADING = True
        auto_config.OPTIONS_DATA_REQUIRED = False
        auto_config.ENABLE_OPTIONS_VALIDATION = False
        
        # Redistribuer les poids des features (sans options)
        auto_config.FEATURE_WEIGHTS = {
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
        }
        
        print("✅ Configuration FORCE TRADING appliquée")
        print(f"   Host: {auto_config.IBKR_HOST}")
        print(f"   Port: {auto_config.IBKR_PORT} (TWS)")
        print(f"   Client ID: {auto_config.IBKR_CLIENT_ID}")
        print(f"   Options SPX: ❌ Désactivé")
        print(f"   Force Trading: ✅ Oui")
        print(f"   Skip Validation: ✅ Oui")
        
        print("\n📊 Features (redistribuées):")
        for feature, weight in auto_config.FEATURE_WEIGHTS.items():
            if weight > 0:
                print(f"   {feature}: {weight:.1%}")
        
        # Modifier aussi le fichier de session pour ignorer les options
        session_config = {
            "session": "london_force_trading",
            "description": "Session Londres - Force Trading (sans options)",
            "trading_enabled": True,
            "data_source": "live_data",
            "options_required": False,
            "force_trading": True,
            "skip_options_validation": True
        }
        
        # Sauvegarder la configuration de session
        os.makedirs("config", exist_ok=True)
        with open("config/force_trading_session.json", "w") as f:
            json.dump(session_config, f, indent=2)
        
        print(f"\n💾 Configuration session sauvegardée")
        print("🎉 Lancement MIA_IA_SYSTEM avec FORCE TRADING...")
        
        # Lancer le système principal
        from launch_24_7_orderflow_trading import main
        main()
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        print("💡 Vérifiez que tous les modules sont installés")
    except Exception as e:
        print(f"❌ Erreur lancement: {e}")
        print("💡 Vérifiez la configuration")

if __name__ == "__main__":
    force_trading_config()






