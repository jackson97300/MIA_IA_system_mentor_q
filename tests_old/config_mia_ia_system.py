# Configuration MIA_IA_SYSTEM - ES Futures
# Fichier de configuration pour le trading ES

# Configuration IBKR
IBKR_CONFIG = {
    'host': '127.0.0.1',
    'port': 7497,  # TWS Paper Trading
    'client_id': 999,
    'timeout': 30
}

# Configuration ES Futures
ES_CONFIG = {
    'symbol': 'ES',
    'date': '20250919',  # ESU25
    'exchange': 'CME',
    'contract': 'ESU25'
}

# Configuration Market Data
MARKET_DATA_CONFIG = {
    'enable_streaming': True,
    'auto_subscribe': True,
    'subscription': 'CME Real-Time (NP,L2)'
}

# Statut: En attente d'activation ESU25 dans TWS
# Action requise: Ajouter ESU25 dans Market Data de TWS
