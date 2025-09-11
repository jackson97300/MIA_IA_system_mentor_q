"""
MIA_IA_SYSTEM - Data Collection Risk Configuration
Paramètres de risque spécifiques pour les différents modes de trading
Version: Production Ready

Ce module définit les paramètres de risque adaptés pour :
- DATA_COLLECTION : Paramètres permissifs pour maximiser les trades
- PAPER_TRADING : Paramètres standards pour validation
- LIVE_TRADING : Paramètres stricts pour trading réel
"""

from typing import Dict, Any
from dataclasses import dataclass

# === PARAMÈTRES RISK PAR MODE ===

# Mode Data Collection - TRÈS PERMISSIF pour collecter maximum de données
DATA_COLLECTION_RISK_PARAMS = {
    # Position sizing
    'max_position_size': 2,              # Positions simultanées
    'position_size_base': 1.0,           # Taille de base
    'position_size_max': 1.0,            # Pas de scaling
    
    # Limites quotidiennes
    'daily_loss_limit': 5000.0,          # Limite très haute
    'max_daily_trades': 100,             # Beaucoup de trades
    'daily_profit_target': 10000.0,      # Target très haute
    'stop_trading_on_target': False,     # Continue après target
    
    # Limites par trade
    'max_risk_per_trade': 500.0,         # Risk élevé acceptable
    'stop_loss_ticks': 20,               # Stop large
    'take_profit_ticks': 40,             # TP large
    
    # Seuils de signal - TRÈS BAS
    'min_confidence_threshold': 0.35,     # Seuil bas pour plus de signaux
    'min_confluence_score': 0.35,         # Confluence basse
    'min_battle_navale_signal': 0.55,     # Battle navale permissif
    
    # Kelly Criterion
    'use_kelly_sizing': False,            # Pas de Kelly en collection
    'kelly_fraction': 0.1,               
    'max_kelly_size': 1.0,
    
    # Protection et filtres - DÉSACTIVÉS
    'enable_time_filters': False,         # Pas de filtre horaire
    'enable_regime_filters': False,       # Pas de filtre régime
    'enable_drawdown_protection': False,  # Pas de protection DD
    'enable_correlation_filter': False,   # Pas de filtre corrélation
    
    # Modes spéciaux
    'force_long_only': False,
    'force_short_only': False,
    'data_collection_mode': True,         # FLAG IMPORTANT
    'golden_rule_strict': False,          # Pas strict sur règle d'or
    
    # Paramètres ML
    'capture_all_signals': True,          # Capturer TOUS les signaux
    'capture_rejected_signals': True,     # Même les rejetés
    'enhanced_snapshots': True            # Snapshots détaillés
}

# Mode Paper Trading - PARAMÈTRES STANDARDS
PAPER_TRADING_RISK_PARAMS = {
    # Position sizing
    'max_position_size': 2,
    'position_size_base': 1.0,
    'position_size_max': 2.0,
    
    # Limites quotidiennes
    'daily_loss_limit': 1000.0,          # $1000 limite standard
    'max_daily_trades': 20,              # 20 trades max
    'daily_profit_target': 500.0,        # Target raisonnable
    'stop_trading_on_target': False,
    
    # Limites par trade
    'max_risk_per_trade': 200.0,
    'stop_loss_ticks': 12,               # 3 points ES
    'take_profit_ticks': 24,             # 6 points ES
    
    # Seuils de signal - STANDARDS
    'min_confidence_threshold': 0.60,     # Seuil standard
    'min_confluence_score': 0.50,         # Confluence moyenne
    'min_battle_navale_signal': 0.65,     # Battle navale standard
    
    # Kelly Criterion
    'use_kelly_sizing': True,
    'kelly_fraction': 0.25,              # 25% Kelly conservateur
    'max_kelly_size': 2.0,
    
    # Protection et filtres
    'enable_time_filters': True,
    'enable_regime_filters': True,
    'enable_drawdown_protection': True,
    'enable_correlation_filter': True,
    
    # Modes spéciaux
    'force_long_only': False,
    'force_short_only': False,
    'data_collection_mode': False,
    'golden_rule_strict': True,           # Strict sur règle d'or
    
    # Paramètres ML
    'capture_all_signals': True,
    'capture_rejected_signals': False,
    'enhanced_snapshots': False
}

# Mode Live Trading - PARAMÈTRES STRICTS
LIVE_TRADING_RISK_PARAMS = {
    # Position sizing - CONSERVATEUR
    'max_position_size': 1,              # 1 position max
    'position_size_base': 1.0,           # MES seulement au début
    'position_size_max': 1.0,            # Pas de scaling initial
    
    # Limites quotidiennes - STRICTES
    'daily_loss_limit': 500.0,           # $500 max loss
    'max_daily_trades': 10,              # 10 trades max
    'daily_profit_target': 300.0,        # Target modeste
    'stop_trading_on_target': True,      # Stop sur target
    
    # Limites par trade - SERRÉES
    'max_risk_per_trade': 100.0,         # $100 max risk
    'stop_loss_ticks': 8,                # 2 points ES
    'take_profit_ticks': 16,             # 4 points ES
    
    # Seuils de signal - STRICTS
    'min_confidence_threshold': 0.70,     # Seuil élevé
    'min_confluence_score': 0.65,         # Confluence haute
    'min_battle_navale_signal': 0.75,     # Battle navale strict
    
    # Kelly Criterion - CONSERVATEUR
    'use_kelly_sizing': True,
    'kelly_fraction': 0.15,              # 15% Kelly très conservateur
    'max_kelly_size': 1.0,               # Pas de leverage
    
    # Protection et filtres - TOUS ACTIFS
    'enable_time_filters': True,
    'enable_regime_filters': True,
    'enable_drawdown_protection': True,
    'enable_correlation_filter': True,
    
    # Protections supplémentaires LIVE
    'max_consecutive_losses': 3,         # Stop après 3 pertes
    'pause_after_big_loss': True,        # Pause si grosse perte
    'big_loss_threshold': 150.0,         # Seuil grosse perte
    'require_confirmation': True,         # Double confirmation signals
    
    # Modes spéciaux
    'force_long_only': False,
    'force_short_only': False,
    'data_collection_mode': False,
    'golden_rule_strict': True,           # TRÈS strict
    
    # Paramètres ML
    'capture_all_signals': False,
    'capture_rejected_signals': False,
    'enhanced_snapshots': False,
    
    # Kill switch
    'enable_kill_switch': True,
    'kill_switch_loss': 300.0,           # Kill à -$300
    'kill_switch_drawdown': 0.15         # Kill à -15% drawdown
}

# === FONCTION HELPER ===

def get_risk_params_for_mode(mode: str) -> Dict[str, Any]:
    """
    Retourne les paramètres de risque appropriés selon le mode
    
    Args:
        mode: "DATA_COLLECTION", "PAPER" ou "LIVE"
        
    Returns:
        Dict avec tous les paramètres de risque
    """
    mode = mode.upper()
    
    if mode == "DATA_COLLECTION":
        return DATA_COLLECTION_RISK_PARAMS.copy()
    elif mode == "PAPER" or mode == "PAPER_TRADING":
        return PAPER_TRADING_RISK_PARAMS.copy()
    elif mode == "LIVE" or mode == "LIVE_TRADING":
        return LIVE_TRADING_RISK_PARAMS.copy()
    else:
        # Par défaut, retourner paper trading (sécurité)
        return PAPER_TRADING_RISK_PARAMS.copy()

# === VALIDATION ===

def validate_risk_params(params: Dict[str, Any]) -> bool:
    """Valide la cohérence des paramètres de risque"""
    try:
        # Vérifications de base
        assert params['max_position_size'] > 0
        assert params['daily_loss_limit'] > 0
        assert params['max_daily_trades'] > 0
        assert params['stop_loss_ticks'] > 0
        assert params['take_profit_ticks'] > params['stop_loss_ticks']
        
        # Vérifications de cohérence
        assert 0 < params['min_confidence_threshold'] <= 1
        assert 0 < params['min_confluence_score'] <= 1
        assert 0 < params['min_battle_navale_signal'] <= 1
        
        # Kelly sizing
        if params.get('use_kelly_sizing', False):
            assert 0 < params['kelly_fraction'] <= 1
            assert params['max_kelly_size'] >= params['position_size_base']
        
        return True
        
    except AssertionError:
        return False
    except KeyError:
        return False

# === EXPORT POUR COMPATIBILITÉ ===

# Alias pour import direct
RiskParameters = DATA_COLLECTION_RISK_PARAMS  # Default

__all__ = [
    'DATA_COLLECTION_RISK_PARAMS',
    'PAPER_TRADING_RISK_PARAMS', 
    'LIVE_TRADING_RISK_PARAMS',
    'get_risk_params_for_mode',
    'validate_risk_params'
]