"""
config/__init__.py - CORRIGÉ
Module Configuration Complet - MIA_IA_SYSTEM
Version: Phase 3 - Automation & ML Integration

CORRECTIONS APPLIQUÉES:
- Gestion d'erreur améliorée pour imports manquants
- Logging au lieu de print
- Protection contre les imports circulaires
"""

import sys
import logging

if sys.platform == "win32":

# Configure logging
logger = logging.getLogger(__name__)

from typing import Dict, List, Optional, Any, Union

# === CORE TRADING CONFIG (EXISTANT) ===
try:
    from .trading_config import (
        # Classes principales
        TradingConfig,
        SymbolConfig,
        RiskManagementConfig,
        FeatureConfig,
        
        # Enums
        TradingMode,
        DataSource,
        ExecutionMode,
        RiskLevel,
        
        # Factory functions
        create_default_config,
        create_paper_trading_config,
        create_live_trading_config,
        
        # Global functions
        get_trading_config,
        set_trading_config,
        get_risk_config,
        get_feature_config
    )
    TRADING_CONFIG_AVAILABLE = True
except ImportError as e:
    logger.warning(f"trading_config.py non disponible: {e}")
    TRADING_CONFIG_AVAILABLE = False
    # Définitions fallback pour éviter erreurs
    TradingConfig = None
    get_trading_config = lambda: {}

# === SIERRA CHART CONFIG (EXISTANT) ===
try:
    from .sierra_config import (
        # Classes principales
        SierraIBKRConfig,
        SierraChartConfig,
        IBKRConfig,
        ContractConfig,
        SecurityConfig,
        
        # Factory functions
        create_sierra_paper_config,
        create_sierra_live_config,
        create_sierra_data_config,
        get_sierra_config,
        set_sierra_config
    )
    SIERRA_CONFIG_AVAILABLE = True
    
    # Import des enums séparément pour gérer les erreurs
    try:
        from .sierra_config import DataProvider, OrderProvider, ContractType, SessionType
    except ImportError:
        logger.warning("Certains enums sierra_config non disponibles")
        # Définir des enums fallback si nécessaire
        from enum import Enum
        
        class DataProvider(Enum):
            IBKR = "ibkr"
            SIERRA = "sierra"
            
        class OrderProvider(Enum):
            IBKR = "ibkr"
            SIERRA = "sierra"
            
except ImportError as e:
    logger.warning(f"sierra_config.py non disponible: {e}")
    SIERRA_CONFIG_AVAILABLE = False
    SierraIBKRConfig = None
    get_sierra_config = lambda: None

# === AUTOMATION CONFIG (NOUVEAU) ===
try:
    from .automation_config import (
        # Classes principales
        AutomationConfig,
        AutomationTradingConfig,
        AutomationRiskConfig,
        DataCollectionConfig,
        IBKRConnectionConfig,
        
        # Factory functions
        create_conservative_config,
        create_automation_data_config,
        create_automation_paper_config,
        get_automation_config,
        set_automation_config,
        get_monitoring_config
    )
    AUTOMATION_CONFIG_AVAILABLE = True
    
    # Import des enums séparément
    try:
        from .automation_config import (
            AutomationMode,
            TradingSession,
            AlertLevel,
            DataGranularity,
            MonitoringConfig  # Ajouter si manquant
        )
    except ImportError as e:
        logger.warning(f"Certains enums automation_config non disponibles: {e}")
        # Définir MonitoringConfig si manquant
        from dataclasses import dataclass
        
        @dataclass
        class MonitoringConfig:
            enable_monitoring: bool = True
            monitoring_interval_seconds: int = 5
        
except ImportError as e:
    logger.warning(f"automation_config.py non disponible: {e}")
    AUTOMATION_CONFIG_AVAILABLE = False
    AutomationConfig = None
    get_automation_config = lambda: {}

# === ML CONFIG (NOUVEAU) ===
try:
    from .ml_config import (
        # Classes principales
        MLConfig,
        BattleNavaleFeatureConfig,
        ModelConfig,
        MLTrainingConfig,
        DeploymentConfig,
        MLPathsConfig,
        
        # Enums
        MLEnvironment,
        TrainingStrategy,
        PerformanceObjective,
        
        # Factory functions
        create_development_ml_config,
        create_research_ml_config,
        create_production_ml_config,
        create_conservative_ml_config,
        get_ml_config,
        set_ml_config,
        get_battle_navale_features_config,
        get_model_config,
        get_ml_training_config
    )
    ML_CONFIG_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ml_config.py non disponible: {e}")
    ML_CONFIG_AVAILABLE = False
    MLConfig = None
    get_ml_config = lambda: {}

# === DATA COLLECTION RISK CONFIG ===
try:
    from .data_collection_risk_config import (
        DATA_COLLECTION_RISK_PARAMS,
        PAPER_TRADING_RISK_PARAMS,
        LIVE_TRADING_RISK_PARAMS,
        get_risk_params_for_mode,
        validate_risk_params
    )
    RISK_CONFIG_AVAILABLE = True
except ImportError as e:
    logger.warning(f"data_collection_risk_config.py non disponible: {e}")
    RISK_CONFIG_AVAILABLE = False

# === FONCTIONS UTILITAIRES GLOBALES ===

def get_all_configs() -> Dict[str, Any]:
    """Retourne toutes les configurations actives"""
    configs = {}
    
    if TRADING_CONFIG_AVAILABLE:
        configs['trading'] = get_trading_config()
    
    if SIERRA_CONFIG_AVAILABLE:
        configs['sierra'] = get_sierra_config()
    
    if AUTOMATION_CONFIG_AVAILABLE:
        configs['automation'] = get_automation_config()
        
    if ML_CONFIG_AVAILABLE:
        configs['ml'] = get_ml_config()
    
    return configs

def validate_all_configs() -> bool:
    """Valide la cohérence de toutes les configurations"""
    try:
        configs = get_all_configs()
        
        # Vérifications de base
        if not configs:
            logger.error("Aucune configuration disponible")
            return False
        
        # Validation trading config
        if 'trading' in configs and configs['trading']:
            trading_config = configs['trading']
            if hasattr(trading_config, 'validate'):
                if not trading_config.validate():
                    logger.error("Trading config invalide")
                    return False
        
        logger.info("✅ Toutes les configurations sont valides")
        return True
        
    except Exception as e:
        logger.error(f"Erreur validation configurations: {e}")
        return False

def setup_configs_for_environment(env: str = "development") -> Dict[str, Any]:
    """Configure le système pour un environnement spécifique"""
    logger.info(f"Configuration pour environnement: {env}")
    
    configs = {}
    
    # Trading config
    if TRADING_CONFIG_AVAILABLE:
        if env == "production":
            configs['trading'] = create_live_trading_config()
        else:
            configs['trading'] = create_paper_trading_config()
    
    # Automation config
    if AUTOMATION_CONFIG_AVAILABLE:
        if env == "production":
            configs['automation'] = create_conservative_config()
        else:
            configs['automation'] = create_automation_paper_config()
    
    # ML config
    if ML_CONFIG_AVAILABLE:
        if env == "production":
            configs['ml'] = create_production_ml_config()
        elif env == "research":
            configs['ml'] = create_research_ml_config()
        else:
            configs['ml'] = create_development_ml_config()
    
    return configs

def get_config_summary() -> Dict[str, Any]:
    """Résumé de l'état des configurations"""
    return {
        'version': __version__,
        'modules_available': {
            'trading': TRADING_CONFIG_AVAILABLE,
            'sierra': SIERRA_CONFIG_AVAILABLE,
            'automation': AUTOMATION_CONFIG_AVAILABLE,
            'ml': ML_CONFIG_AVAILABLE,
            'risk': RISK_CONFIG_AVAILABLE
        },
        'total_modules': sum([
            TRADING_CONFIG_AVAILABLE,
            SIERRA_CONFIG_AVAILABLE,
            AUTOMATION_CONFIG_AVAILABLE,
            ML_CONFIG_AVAILABLE,
            RISK_CONFIG_AVAILABLE
        ])
    }

# === FONCTIONS SPÉCIALISÉES ===

def get_battle_navale_config() -> Dict[str, Any]:
    """Configuration spécifique Battle Navale"""
    config = {}
    
    if ML_CONFIG_AVAILABLE:
        config['features'] = get_battle_navale_features_config()
    
    if TRADING_CONFIG_AVAILABLE:
        trading_config = get_trading_config()
        if hasattr(trading_config, 'features'):
            config['thresholds'] = {
                'min_signal_confidence': trading_config.features.min_signal_confidence,
                'confluence_threshold': trading_config.features.confluence_threshold
            }
    
    return config

def get_production_config() -> Dict[str, Any]:
    """Configuration complète production"""
    return setup_configs_for_environment('production')

# === VERSION & METADATA ===

__version__ = "3.0.0"

# === EXPORTS ===

__all__ = ['__version__', 'get_config_summary']

# Exports Trading
if TRADING_CONFIG_AVAILABLE:
    __all__.extend([
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
    ])

# Exports Sierra
if SIERRA_CONFIG_AVAILABLE:
    __all__.extend([
        'SierraIBKRConfig',
        'SierraChartConfig',
        'IBKRConfig',
        'ContractConfig',
        'SecurityConfig',
        'DataProvider',
        'OrderProvider',
        'ContractType',
        'SessionType',
        'create_sierra_paper_config',
        'create_sierra_live_config',
        'create_sierra_data_config',
        'get_sierra_config',
        'set_sierra_config'
    ])

# Exports Automation
if AUTOMATION_CONFIG_AVAILABLE:
    __all__.extend([
        'AutomationConfig',
        'AutomationTradingConfig',
        'AutomationRiskConfig',
        'DataCollectionConfig',
        'MonitoringConfig',
        'IBKRConnectionConfig',
        'AutomationMode',
        'TradingSession',
        'AlertLevel',
        'DataGranularity',
        'create_conservative_config',
        'create_automation_data_config',
        'create_automation_paper_config',
        'get_automation_config',
        'set_automation_config',
        'get_monitoring_config'
    ])

# Exports ML
if ML_CONFIG_AVAILABLE:
    __all__.extend([
        'MLConfig',
        'BattleNavaleFeatureConfig',
        'ModelConfig',
        'MLTrainingConfig',
        'DeploymentConfig',
        'MLPathsConfig',
        'MLEnvironment',
        'TrainingStrategy',
        'PerformanceObjective',
        'create_development_ml_config',
        'create_research_ml_config',
        'create_production_ml_config',
        'create_conservative_ml_config',
        'get_ml_config',
        'set_ml_config',
        'get_battle_navale_features_config',
        'get_model_config',
        'get_ml_training_config'
    ])

# Exports Risk Config
if RISK_CONFIG_AVAILABLE:
    __all__.extend([
        'DATA_COLLECTION_RISK_PARAMS',
        'PAPER_TRADING_RISK_PARAMS',
        'LIVE_TRADING_RISK_PARAMS',
        'get_risk_params_for_mode',
        'validate_risk_params'
    ])

# Exports fonctions utilitaires
__all__.extend([
    'get_all_configs',
    'validate_all_configs',
    'setup_configs_for_environment',
    'get_battle_navale_config',
    'get_production_config',
    'TRADING_CONFIG_AVAILABLE',
    'SIERRA_CONFIG_AVAILABLE',
    'AUTOMATION_CONFIG_AVAILABLE',
    'ML_CONFIG_AVAILABLE',
    'RISK_CONFIG_AVAILABLE'
])

# === INITIALISATION MODULE ===

# Log au chargement
logger.info(f"📦 Module Configuration v{__version__} chargé")
summary = get_config_summary()
logger.info(f"📊 {summary['total_modules']}/5 modules disponibles")

# Afficher modules manquants
for module, available in summary['modules_available'].items():
    if not available:
        logger.warning(f"❌ Module {module} non disponible")

# Test automatique en mode debug
if __name__ == "__main__":
    logger.info("Test module configuration...")
    validate_all_configs()