#!/usr/bin/env python3
"""
Configuration IBKR pour compte live - MIA_IA_SYSTEM
"""
from typing import Dict, Any

# Configuration IBKR Compte Live
IBKR_LIVE_CONFIG = {
    'host': '127.0.0.1',
    'port': 7496,  # Port TWS live
    'client_id': 1,
    'timeout': 30,
    'account_id': '',  # Sera rempli automatiquement
    'paper_trading': False,  # Mode live
    'real_market_data': True,
    
    # Sécurité - Lecture seule recommandée
    'read_only': True,  # IMPORTANT: Pas de trading accidentel
    'enable_trading': False,  # Désactivé par défaut
    
    # Données marché
    'market_data_type': 1,  # 1=Live, 2=Frozen, 3=Delayed
    'enable_tick_data': True,
    'enable_historical_data': True,
    
    # Symboles par défaut
    'default_symbols': ['ES', 'NQ', 'YM'],
    'default_exchange': 'CME',
    
    # Risk Management
    'max_position_size': 1,  # Contrats max
    'max_daily_loss': 1000,  # $ max perte quotidienne
    'stop_loss_ticks': 10,  # Ticks max perte
    
    # Connexion
    'auto_reconnect': True,
    'reconnect_interval': 5,
    'max_reconnect_attempts': 3,
    
    # Logging
    'log_level': 'INFO',
    'log_api_calls': True,
    'log_market_data': False,  # Trop volumineux
}

# Configuration pour MIA_IA_SYSTEM
MIA_IA_SYSTEM_IBKR_CONFIG = {
    'ibkr': IBKR_LIVE_CONFIG,
    
    # Intégration avec le système
    'enable_battle_navale': True,
    'enable_confluence_analyzer': True,
    'enable_risk_manager': True,
    
    # Données requises
    'required_data': {
        'market_data': True,
        'historical_data': True,
        'account_data': True,
        'options_flow': False,  # Optionnel pour débuter
    },
    
    # Performance
    'data_update_interval': 1,  # Secondes
    'signal_generation_interval': 5,  # Secondes
    'risk_check_interval': 10,  # Secondes
}

def get_ibkr_config() -> Dict[str, Any]:
    """Retourne la configuration IBKR pour MIA_IA_SYSTEM"""
    return MIA_IA_SYSTEM_IBKR_CONFIG

def validate_config(config: Dict[str, Any]) -> bool:
    """Valide la configuration IBKR"""
    required_keys = ['host', 'port', 'client_id', 'timeout']
    
    for key in required_keys:
        if key not in config['ibkr']:
            print(f"❌ Configuration manquante: {key}")
            return False
    
    if config['ibkr']['port'] != 7496:
        print("⚠️ Attention: Port 7496 recommandé pour compte live")
    
    if not config['ibkr']['read_only']:
        print("⚠️ ATTENTION: Mode trading activé - Risque financier !")
    
    return True

if __name__ == "__main__":
    config = get_ibkr_config()
    if validate_config(config):
        print("✅ Configuration IBKR Live validée")
        print(f"📡 Host: {config['ibkr']['host']}:{config['ibkr']['port']}")
        print(f"🔒 Read-Only: {config['ibkr']['read_only']}")
    else:
        print("❌ Configuration IBKR Live invalide") 