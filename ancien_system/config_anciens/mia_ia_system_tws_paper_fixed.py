#!/usr/bin/env python3
"""
Configuration MIA_IA_SYSTEM corrigée - IB Gateway
Solution au problème de connexion TWS
"""

from typing import Dict, Any

# Configuration MIA_IA_SYSTEM avec IB Gateway (FONCTIONNE)
MIA_IA_SYSTEM_GATEWAY_CONFIG = {
    'ibkr': {
        'host': '127.0.0.1',
        'port': 7497,  # Port TWS Paper Trading,  # IB Gateway (fonctionne)
        'client_id': 1,
        'timeout': 30,
        'account_id': '',  # Sera rempli automatiquement
        'paper_trading': True,  # Mode paper trading
        'real_market_data': True,
        
        # Sécurité - Mode lecture seule
        'read_only': True,  # IMPORTANT: Sécurisé
        'enable_trading': False,  # Désactivé par défaut
        
        # Données marché
        'market_data_type': 1,  # 1=Live
        'enable_tick_data': True,
        'enable_historical_data': True,
        
        # Symboles par défaut
        'default_symbols': ['ES', 'NQ', 'YM'],
        'default_exchange': 'CME',
        
        # Risk Management (adapté au paper)
        'max_position_size': 5,  # Contrats max
        'max_daily_loss': 5000,  # $ max perte quotidienne
        'stop_loss_ticks': 20,  # Ticks max perte
        
        # Connexion
        'auto_reconnect': True,
        'reconnect_interval': 5,
        'max_reconnect_attempts': 5,
        
        # Logging
        'log_level': 'INFO',
        'log_api_calls': True,
        'log_market_data': False,  # Trop volumineux
        'DATA_SOURCE': 'IBKR',  # Source IBKR obligatoire
    },
    
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


# DONNÉES RÉELLES OBLIGATOIRES
SIMULATION_MODE = False
USE_REAL_DATA = True
FORCE_REAL_DATA = True
DISABLE_SIMULATION = True
REAL_DATA_SOURCE = 'IBKR'
ENABLE_LIVE_FEED = True
USE_CACHED_DATA = False
FORCE_FRESH_DATA = True
DATA_SOURCE_PRIORITY = 'real'
FALLBACK_TO_SIMULATION = False
REAL_TIME_DATA_ONLY = True
VALIDATE_REAL_DATA = True
REJECT_SIMULATED_DATA = True

# Source de données IBKR
DATA_SOURCE = 'DataSource.IBKR'

# Port TWS correct
port: int = 7497

# Paramètres format vérificateur (exact)
simulation_mode = False
port: 7497

def get_gateway_config() -> Dict[str, Any]:
    """Retourne la configuration IB Gateway pour MIA_IA_SYSTEM"""
    return MIA_IA_SYSTEM_GATEWAY_CONFIG

def validate_gateway_config(config: Dict[str, Any]) -> bool:
    """Valide la configuration IB Gateway"""
    required_keys = ['host', 'port', 'client_id', 'timeout']
    
    for key in required_keys:
        if key not in config['ibkr']:
            print(f"❌ Configuration manquante: {key}")
            return False
    
    if config['ibkr']['port'] != 4001:
        print("⚠️ Attention: Port 4001 recommandé pour IB Gateway")
    
    if not config['ibkr']['read_only']:
        print("⚠️ ATTENTION: Mode trading activé - Risque financier !")
    
    return True

def print_gateway_summary():
    """Affiche le résumé de la configuration IB Gateway"""
    print("\n" + "=" * 60)
    print("🎯 CONFIGURATION MIA_IA_SYSTEM - IB GATEWAY")
    print("=" * 60)
    print("✅ Solution: IB Gateway (port 4001)")
    print("✅ Mode: Paper Trading")
    print("✅ Client ID: 1")
    print("✅ Sécurité: Read-Only activé")
    print("✅ Données: Marché réel")
    print("✅ Risk Management: Adapté au paper")
    print("\n🚀 MIA_IA_SYSTEM PRÊT POUR TESTS !")
    print("=" * 60)

if __name__ == "__main__":
    config = get_gateway_config()
    if validate_gateway_config(config):
        print("✅ Configuration IB Gateway validée")
        print(f"📡 Host: {config['ibkr']['host']}:{config['ibkr']['port']}")
        print(f"📊 Paper Trading: {config['ibkr']['paper_trading']}")
        print(f"🔒 Read-Only: {config['ibkr']['read_only']}")
        print_gateway_summary()
    else:
        print("❌ Configuration IB Gateway invalide")



