# Configuration IBKR - MIA_IA_SYSTEM
# ===================================

# Configuration IB Gateway
IB_GATEWAY_CONFIG = {
    'host': '127.0.0.1',
    'port': 4001,
    'client_id': 1,
    'timeout': 10,
    'max_retries': 3,
    'reconnect_delay': 5
}

# Configuration données souscrites
MARKET_DATA_CONFIG = {
    # CME Level 2 - $11/mois
    'cme_level2': {
        'enabled': True,
        'symbols': ['ES', 'NQ', 'HE'],
        'depth_levels': 10,
        'cost': 11.00
    },
    
    # OPRA Level 1 - $1.50/mois
    'opra_level1': {
        'enabled': True,
        'symbols': ['SPX', 'SPY', 'QQQ'],
        'greeks_enabled': True,
        'cost': 1.50
    }
}

# Configuration Order Book Imbalance
ORDER_BOOK_CONFIG = {
    'min_imbalance_threshold': 0.1,
    'max_imbalance_threshold': 0.3,
    'depth_levels': 5,
    'weight_decay': 0.8
}

# Configuration Options Greeks
OPTIONS_CONFIG = {
    'greeks_calculation': True,
    'implied_volatility': True,
    'put_call_ratio': True,
    'gamma_exposure': True
}

# Configuration monitoring
MONITORING_CONFIG = {
    'check_interval': 30,  # secondes
    'alert_threshold': 0.15,
    'performance_threshold': 0.5,  # secondes
    'max_errors': 5
}

# Coûts totaux
TOTAL_COST = {
    'cme_level2': 11.00,
    'opra_level1': 1.50,
    'total_monthly': 12.50,
    'free_threshold': 20.00  # USD de commissions/mois
}

# Messages de configuration
CONFIG_MESSAGES = {
    'success': "✅ Configuration IBKR réussie",
    'error_connection': "❌ Erreur connexion IB Gateway",
    'error_level2': "❌ Erreur CME Level 2",
    'error_options': "❌ Erreur OPRA Options",
    'performance_excellent': "✅ Performance : EXCELLENTE",
    'performance_good': "✅ Performance : BONNE",
    'performance_poor': "⚠️ Performance : À AMÉLIORER"
} 