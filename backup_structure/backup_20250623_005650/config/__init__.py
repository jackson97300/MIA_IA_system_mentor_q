"""
MIA_IA_SYSTEM - Configuration Package
Exports propres pour éviter les imports cassés
"""

from .trading_config import (
    TradingConfig,
    SymbolConfig,
    RiskManagementConfig,
    FeatureConfig,
    TradingMode,
    DataSource,
    ExecutionMode,
    RiskLevel,
    create_default_config,
    create_paper_trading_config,
    create_live_trading_config,
    get_trading_config,
    set_trading_config,
    get_risk_config,
    get_feature_config
)

__all__ = [
    'TradingConfig',
    'SymbolConfig', 
    'RiskManagementConfig',
    'FeatureConfig',
    'TradingMode',
    'DataSource',
    'ExecutionMode',
    'RiskLevel',
    'create_default_config',
    'create_paper_trading_config',
    'create_live_trading_config',
    'get_trading_config',
    'set_trading_config',
    'get_risk_config',
    'get_feature_config'
]
