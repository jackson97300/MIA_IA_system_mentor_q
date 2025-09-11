"""
MIA_IA_SYSTEM - Constants Configuration
Centralisation de toutes les constantes et magic numbers
Version: Production Ready

Ce fichier centralise TOUTES les constantes utilisées dans le système
pour éviter les magic numbers et faciliter la maintenance.
"""

from enum import Enum
from typing import Dict, Any

# === TRADING CONSTANTS ===

# Contract Specifications
ES_FUTURES = {
    'symbol': 'ES',
    'name': 'E-mini S&P 500',
    'tick_size': 0.25,
    'tick_value': 12.50,
    'multiplier': 50,
    'margin_initial': 13200,
    'margin_maintenance': 12000,
    'trading_hours': {
        'sunday_open': '18:00',
        'friday_close': '17:00',
        'daily_open': '09:30',
        'daily_close': '16:00'
    }
}

MES_FUTURES = {
    'symbol': 'MES',
    'name': 'Micro E-mini S&P 500',
    'tick_size': 0.25,
    'tick_value': 1.25,
    'multiplier': 5,
    'margin_initial': 1320,
    'margin_maintenance': 1200,
    'trading_hours': ES_FUTURES['trading_hours']  # Mêmes horaires
}

# === SIGNAL GENERATION THRESHOLDS ===

# Confidence Thresholds par mode
CONFIDENCE_THRESHOLDS = {
    'data_collection': {
        'min_battle_navale': 0.35,
        'min_confluence': 0.35,
        'min_pattern_strength': 0.30,
        'min_regime_confidence': 0.30
    },
    'paper_trading': {
        'min_battle_navale': 0.65,
        'min_confluence': 0.50,
        'min_pattern_strength': 0.55,
        'min_regime_confidence': 0.60
    },
    'live_trading': {
        'min_battle_navale': 0.75,
        'min_confluence': 0.65,
        'min_pattern_strength': 0.70,
        'min_regime_confidence': 0.70
    },
    'conservative': {
        'min_battle_navale': 0.80,
        'min_confluence': 0.70,
        'min_pattern_strength': 0.75,
        'min_regime_confidence': 0.75
    }
}

# Pattern Detection Thresholds
PATTERN_THRESHOLDS = {
    'gamma_pin': {
        'min_gamma_exposure': 0.7,
        'min_distance_percentage': 0.002,  # 0.2%
        'max_distance_points': 10.0
    },
    'headfake': {
        'min_volume_spike': 1.5,  # 150% du volume moyen
        'min_reversal_ticks': 4,
        'max_time_seconds': 300  # 5 minutes
    },
    'microstructure': {
        'min_anomaly_score': 0.6,
        'min_imbalance_ratio': 0.7,
        'min_absorption_score': 0.65
    }
}

# === RISK MANAGEMENT CONSTANTS ===

# Position Sizing
POSITION_SIZING = {
    'min_position_size': 1,
    'max_position_size': {
        'data_collection': 3,
        'paper_trading': 2,
        'live_trading': 1,
        'conservative': 1
    },
    'kelly_fraction': {
        'aggressive': 0.25,
        'moderate': 0.20,
        'conservative': 0.15
    }
}

# Risk Limits par mode
RISK_LIMITS = {
    'data_collection': {
        'daily_loss_limit': 5000.0,
        'max_daily_trades': 100,
        'stop_loss_ticks': 20,
        'take_profit_ticks': 40,
        'max_risk_per_trade': 500.0
    },
    'paper_trading': {
        'daily_loss_limit': 1000.0,
        'max_daily_trades': 20,
        'stop_loss_ticks': 12,
        'take_profit_ticks': 24,
        'max_risk_per_trade': 200.0
    },
    'live_trading': {
        'daily_loss_limit': 500.0,
        'max_daily_trades': 10,
        'stop_loss_ticks': 8,
        'take_profit_ticks': 16,
        'max_risk_per_trade': 100.0
    },
    'conservative': {
        'daily_loss_limit': 300.0,
        'max_daily_trades': 5,
        'stop_loss_ticks': 6,
        'take_profit_ticks': 12,
        'max_risk_per_trade': 75.0
    }
}

# Stop Loss & Take Profit Rules
STOP_TAKE_PROFIT_RULES = {
    'min_risk_reward_ratio': 1.2,
    'breakeven_trigger_ticks': 8,
    'trailing_stop_activation_ticks': 12,
    'trailing_stop_distance_ticks': 6,
    'max_stop_loss_ticks': 20,
    'emergency_stop_ticks': 40
}

# === PERFORMANCE TARGETS ===

PERFORMANCE_METRICS = {
    'target_win_rate': 0.60,  # 60%
    'min_acceptable_win_rate': 0.55,
    'target_profit_factor': 1.5,
    'min_profit_factor': 1.3,
    'target_sharpe_ratio': 1.5,
    'min_sharpe_ratio': 1.0,
    'max_drawdown_percent': 10.0,  # 10%
    'daily_profit_target': 500.0,
    'weekly_profit_target': 2000.0,
    'monthly_profit_target': 8000.0
}

# Latency Targets (millisecondes)
LATENCY_TARGETS = {
    'max_signal_generation_ms': 50,
    'max_feature_calculation_ms': 20,
    'max_order_execution_ms': 100,
    'max_end_to_end_ms': 200,
    'warning_latency_ms': 150,
    'critical_latency_ms': 300,
    'analysis_frequency_ms': 1000  # 1 seconde
}

# === FEATURE CALCULATION CONSTANTS ===

# Feature Weights pour confluence
FEATURE_WEIGHTS = {
    'battle_navale_signal': 0.25,
    'gamma_pin_strength': 0.15,
    'market_regime_alignment': 0.15,
    'headfake_signal': 0.10,
    'microstructure_score': 0.10,
    'volume_confirmation': 0.10,
    'trend_strength': 0.10,
    'session_context': 0.05
}

# Lookback Periods
LOOKBACK_PERIODS = {
    'vwap_period': 390,  # Minutes dans session régulière
    'trend_period': 20,   # Barres pour trend
    'volume_average': 20,  # Barres pour volume moyen
    'atr_period': 14,     # ATR standard
    'momentum_period': 10  # Momentum
}

# === BATTLE NAVALE CONSTANTS ===

BATTLE_NAVALE_PARAMS = {
    'min_base_quality': 0.5,
    'min_base_size_ticks': 4,
    'max_base_size_ticks': 20,
    'min_touches_for_validation': 2,
    'golden_rule_lookback_bars': 10,
    'trend_continuation_threshold': 0.7,
    'vikings_dominance_threshold': 0.65,
    'base_formation_time_min': 5,  # minutes
    'base_formation_time_max': 60  # minutes
}

# === MONITORING & ALERTS ===

MONITORING_PARAMS = {
    'health_check_interval_seconds': 60,
    'performance_update_interval_seconds': 300,  # 5 minutes
    'position_sync_interval_seconds': 10,
    'heartbeat_interval_seconds': 30,
    'metric_history_size': 1000,
    'alert_cooldown_seconds': 300  # 5 minutes entre alertes similaires
}

ALERT_THRESHOLDS = {
    'cpu_usage_warning': 80,  # %
    'cpu_usage_critical': 95,
    'memory_usage_warning': 80,
    'memory_usage_critical': 95,
    'disk_space_warning_gb': 5,
    'disk_space_critical_gb': 1,
    'consecutive_errors_warning': 5,
    'consecutive_errors_critical': 10,
    'loss_alert_threshold': 100.0,  # $
    'drawdown_alert_percent': 5.0
}

# === ML CONSTANTS ===

ML_PARAMETERS = {
    'min_training_samples': 1000,
    'max_training_samples': 10000,
    'train_test_split': 0.2,
    'cross_validation_folds': 5,
    'feature_importance_threshold': 0.05,
    'model_accuracy_threshold': 0.65,
    'retraining_frequency_trades': 500,
    'model_decay_days': 30,
    'max_features_to_use': 8,
    'random_state': 42  # Pour reproductibilité
}

# === DATA COLLECTION CONSTANTS ===

DATA_PARAMS = {
    'snapshot_compression': True,
    'snapshot_format': 'parquet',
    'max_snapshots_per_file': 1000,
    'data_retention_days': 90,
    'backup_frequency_hours': 24,
    'min_data_quality_score': 0.8,
    'outlier_z_score_threshold': 3.0,
    'missing_data_threshold_percent': 5.0
}

# === SIERRA CHART CONSTANTS ===

SIERRA_PARAMS = {
    'order_timeout_seconds': 30,
    'order_confirmation_timeout_ms': 5000,
    'max_order_retries': 3,
    'retry_delay_ms': 1000,
    'position_mismatch_tolerance': 0,
    'price_tolerance_ticks': 2,
    'max_slippage_ticks': 3
}

# === SESSION TIMING CONSTANTS ===

TRADING_SESSIONS = {
    'asian': {
        'start': '18:00',
        'end': '03:00',
        'volatility_multiplier': 0.7
    },
    'london': {
        'start': '03:00',
        'end': '09:30',
        'volatility_multiplier': 1.2
    },
    'ny_morning': {
        'start': '09:30',
        'end': '12:00',
        'volatility_multiplier': 1.5
    },
    'lunch': {
        'start': '12:00',
        'end': '14:00',
        'volatility_multiplier': 0.8
    },
    'ny_afternoon': {
        'start': '14:00',
        'end': '16:00',
        'volatility_multiplier': 1.3
    },
    'close': {
        'start': '15:45',
        'end': '16:15',
        'volatility_multiplier': 1.8
    }
}

# === COMMISSION & FEES ===

TRADING_COSTS = {
    'es_futures': {
        'commission_per_side': 2.25,
        'exchange_fee': 1.18,
        'nfa_fee': 0.02,
        'total_per_side': 3.45,
        'total_round_trip': 6.90
    },
    'mes_futures': {
        'commission_per_side': 0.62,
        'exchange_fee': 0.32,
        'nfa_fee': 0.02,
        'total_per_side': 0.96,
        'total_round_trip': 1.92
    }
}

# === VALIDATION CONSTANTS ===

VALIDATION_RULES = {
    'min_price_es': 1000.0,
    'max_price_es': 10000.0,
    'min_volume': 100,
    'max_spread_ticks': 2,
    'max_gap_percent': 2.0,  # 2% gap max
    'min_liquidity_volume': 500,
    'max_order_age_seconds': 60,
    'stale_data_threshold_seconds': 5
}

# === ERROR CODES ===

class ErrorCode(Enum):
    """Codes d'erreur standardisés"""
    SUCCESS = 0
    CONNECTION_ERROR = 1001
    DATA_ERROR = 1002
    VALIDATION_ERROR = 1003
    EXECUTION_ERROR = 2001
    RISK_LIMIT_ERROR = 2002
    POSITION_ERROR = 2003
    ORDER_REJECTED = 2004
    SYSTEM_ERROR = 3001
    CONFIG_ERROR = 3002
    CRITICAL_ERROR = 9999

# === HELPER FUNCTIONS ===

def get_risk_params_for_mode(mode: str) -> Dict[str, Any]:
    """Retourne les paramètres de risque pour un mode"""
    mode = mode.lower()
    if mode in RISK_LIMITS:
        return RISK_LIMITS[mode]
    return RISK_LIMITS['paper_trading']  # Default

def get_confidence_thresholds_for_mode(mode: str) -> Dict[str, float]:
    """Retourne les seuils de confiance pour un mode"""
    mode = mode.lower()
    if mode in CONFIDENCE_THRESHOLDS:
        return CONFIDENCE_THRESHOLDS[mode]
    return CONFIDENCE_THRESHOLDS['paper_trading']  # Default

def get_contract_specs(symbol: str) -> Dict[str, Any]:
    """Retourne les spécifications d'un contrat"""
    symbol = symbol.upper()
    if symbol == 'ES':
        return ES_FUTURES
    elif symbol == 'MES':
        return MES_FUTURES
    else:
        raise ValueError(f"Symbole non supporté: {symbol}")

def calculate_dollar_value(ticks: float, symbol: str = 'ES') -> float:
    """Calcule la valeur en dollars d'un mouvement en ticks"""
    specs = get_contract_specs(symbol)
    return ticks * specs['tick_value']

def calculate_ticks(price_change: float, symbol: str = 'ES') -> float:
    """Calcule le nombre de ticks pour un changement de prix"""
    specs = get_contract_specs(symbol)
    return price_change / specs['tick_size']

# === EXPORTS ===

__all__ = [
    # Contracts
    'ES_FUTURES',
    'MES_FUTURES',
    
    # Thresholds
    'CONFIDENCE_THRESHOLDS',
    'PATTERN_THRESHOLDS',
    
    # Risk
    'POSITION_SIZING',
    'RISK_LIMITS',
    'STOP_TAKE_PROFIT_RULES',
    
    # Performance
    'PERFORMANCE_METRICS',
    'LATENCY_TARGETS',
    
    # Features
    'FEATURE_WEIGHTS',
    'LOOKBACK_PERIODS',
    
    # Battle Navale
    'BATTLE_NAVALE_PARAMS',
    
    # Monitoring
    'MONITORING_PARAMS',
    'ALERT_THRESHOLDS',
    
    # ML
    'ML_PARAMETERS',
    
    # Data
    'DATA_PARAMS',
    
    # Sierra
    'SIERRA_PARAMS',
    
    # Sessions
    'TRADING_SESSIONS',
    
    # Costs
    'TRADING_COSTS',
    
    # Validation
    'VALIDATION_RULES',
    
    # Errors
    'ErrorCode',
    
    # Helper functions
    'get_risk_params_for_mode',
    'get_confidence_thresholds_for_mode',
    'get_contract_specs',
    'calculate_dollar_value',
    'calculate_ticks'
]