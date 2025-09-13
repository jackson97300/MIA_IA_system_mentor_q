#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Lancement Session London SANS Options
Configuration optimisée pour trading sans données options SPX
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.logger import get_logger

logger = get_logger(__name__)

def create_no_options_config():
    """Créer la configuration sans options"""
    
    config = {
        "session_info": {
            "session": "LONDON_NO_OPTIONS",
            "start_time": datetime.now().isoformat(),
            "options_disabled": True,
            "reason": "Données options non disponibles/qualité insuffisante"
        },
        "feature_weights": {
            "volume_confirmation": 0.35,        # Renforcé
            "vwap_trend_signal": 0.22,          # Renforcé
            "sierra_pattern_strength": 0.22,    # Renforcé
            "smart_money_strength": 0.17,       # Renforcé
            "level_proximity": 0.10,            # Renforcé
            "es_nq_correlation": 0.10,          # Renforcé
            "order_book_imbalance": 0.21,       # Renforcé
            "session_context": 0.04,            # Renforcé
            "pullback_quality": 0.02,           # Renforcé
            # gamma_levels_proximity: DÉSACTIVÉ
            # options_flow_bias: DÉSACTIVÉ
        },
        "risk_management": {
            "risk_multiplier": 0.8,             # Réduit
            "signal_threshold": 0.75,           # Plus élevé
            "max_position_size": 0.7,           # Réduit
            "max_daily_loss": 400.0,            # Conservateur
            "max_trades_per_day": 15            # Réduit
        },
        "trading_config": {
            "session": "london",
            "focus": "Trend continuation (sans options)",
            "risk_level": "Moderate",           # Réduit de High
            "volume": "Elevé",
            "key_levels": [
                "VWAP Bands",
                "Volume Imbalance", 
                "Sierra Patterns",
                "Smart Money Flow"
            ]
        }
    }
    
    return config

def save_no_options_config(config):
    """Sauvegarder la configuration sans options"""
    config_dir = Path("data/preparation/sessions_20250812")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / "london_no_options_config.json"
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"✅ Configuration sans options sauvegardée: {config_file}")
    return config_file

def launch_london_no_options():
    """Lancer la session London sans options"""
    
    logger.info("🚀 Lancement Session London SANS Options")
    logger.warning("⚠️ ATTENTION: Trading sans données options SPX")
    logger.info("📊 Features renforcées: Volume, VWAP, Sierra, Smart Money")
    
    # 1. Créer la configuration sans options
    config = create_no_options_config()
    
    # 2. Sauvegarder la configuration
    config_file = save_no_options_config(config)
    
    # 3. Afficher le résumé
    logger.info("📊 CONFIGURATION SANS OPTIONS:")
    logger.info(f"   🎯 Session: {config['session_info']['session']}")
    logger.info(f"   ⚠️ Options: DÉSACTIVÉES")
    logger.info(f"   📈 Features actives: {len(config['feature_weights'])}")
    logger.info(f"   🛡️ Risk multiplier: {config['risk_management']['risk_multiplier']}")
    logger.info(f"   🎯 Signal threshold: {config['risk_management']['signal_threshold']}")
    logger.info(f"   💰 Max position: {config['risk_management']['max_position_size']*100}%")
    
    # 4. Lancer le système principal
    logger.info("🎯 Lancement du système principal...")
    
    try:
        # Modifier les arguments pour le mode sans options
        sys.argv = [
            'launch_24_7_orderflow_trading.py',
            '--live',  # Mode paper trading
            '--session', 'london',
            '--no-options',  # Nouveau flag
            '--config', str(config_file)
        ]
        
        # Importer et lancer
        from launch_24_7_orderflow_trading import main
        main()
        
    except ImportError as e:
        logger.error(f"❌ Erreur import système principal: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur lancement: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = launch_london_no_options()
    
    if success:
        logger.info("✅ Session London lancée avec succès SANS options")
        logger.info("💡 Le système utilise les features renforcées")
    else:
        logger.error("❌ Échec lancement session London")
        sys.exit(1)






