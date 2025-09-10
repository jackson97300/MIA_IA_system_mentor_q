#!/usr/bin/env python3
"""
Configuration TWS Paper Trading pour MIA_IA_SYSTEM
Port 7497 - Mode Paper Trading
"""

from typing import Dict, Any

# Configuration TWS Paper Trading
TWS_PAPER_CONFIG = {
    'ibkr': {
        'host': '127.0.0.1',
        'port': 7497,  # Port TWS Paper Trading
        'client_id': 1,
        'timeout': 30,
        'account_id': '',  # Sera rempli automatiquement
        'paper_trading': True,  # Mode paper trading
        'real_market_data': True,
        
        # Sécurité - Mode lecture seule pour débuter
        'read_only': True,  # IMPORTANT: Sécurisé
        'enable_trading': False,  # Désactivé par défaut
        
        # Données marché
        'market_data_type': 1,  # 1=Live
        'enable_tick_data': True,
        'enable_historical_data': True,
        
        # Symboles par défaut
        'default_symbols': ['ES', 'NQ', 'YM'],
        'default_exchange': 'CME',
        
        # Risk Management (plus permissif en paper)
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

def get_tws_paper_config() -> Dict[str, Any]:
    """Retourne la configuration TWS Paper Trading"""
    return TWS_PAPER_CONFIG

def validate_tws_paper_config(config: Dict[str, Any]) -> bool:
    """Valide la configuration TWS Paper Trading"""
    required_keys = ['host', 'port', 'client_id', 'timeout']
    
    for key in required_keys:
        if key not in config['ibkr']:
            print(f"❌ Configuration manquante: {key}")
            return False
    
    if config['ibkr']['port'] != 7497:
        print("⚠️ Attention: Port 7497 requis pour TWS Paper Trading")
        return False
    
    if not config['ibkr']['paper_trading']:
        print("⚠️ Attention: Mode Paper Trading requis")
        return False
    
    return True

def print_tws_paper_summary():
    """Affiche le résumé de la configuration TWS Paper"""
    print("\n" + "=" * 60)
    print("🎯 CONFIGURATION TWS PAPER TRADING")
    print("=" * 60)
    print("✅ Mode: Paper Trading")
    print("✅ port: 7497,  # Port TWS Paper Trading")
    print("✅ Client ID: 1")
    print("✅ Sécurité: Read-Only activé")
    print("✅ Données: Marché réel")
    print("✅ Risk Management: Adapté au paper")
    print("\n🚀 MIA_IA_SYSTEM PRÊT POUR TESTS PAPER !")
    print("=" * 60)

if __name__ == "__main__":
    config = get_tws_paper_config()
    if validate_tws_paper_config(config):
        print("✅ Configuration TWS Paper Trading validée")
        print(f"📡 Host: {config['ibkr']['host']}:{config['ibkr']['port']}")
        print(f"📊 Paper Trading: {config['ibkr']['paper_trading']}")
        print(f"🔒 Read-Only: {config['ibkr']['read_only']}")
        print_tws_paper_summary()
    else:
        print("❌ Configuration TWS Paper Trading invalide")




