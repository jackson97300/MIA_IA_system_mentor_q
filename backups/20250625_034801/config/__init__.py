"""
config/__init__.py

MODULE CONFIGURATION COMPLET - MIA_IA_SYSTEM
Exports centralisés pour tous les fichiers de configuration
Version: Phase 3 - Automation & ML Integration

FICHIERS INTÉGRÉS :
├── trading_config.py       # ✅ Configuration centralisée existante
├── sierra_config.py        # ✅ Configuration Sierra Chart existante  
├── automation_config.py    # 🆕 Configuration automation & live trading
└── ml_config.py           # 🆕 Configuration ML progressive

OBJECTIFS :
- Exports propres et sécurisés (pas d'imports cassés)
- Compatibilité backward avec code existant
- Integration nouvelle architecture automation/ML
- Fonctions utilitaires pour accès rapide configurations
- Gestion globale et centralisée des configs

USAGE :
```python
from config import get_trading_config, get_automation_config, get_ml_config
from config import TradingConfig, AutomationConfig, MLConfig
```
"""

import logging
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
    logging.warning(f"trading_config.py non disponible: {e}")
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
        
        # Enums
        DataProvider,
        OrderProvider,
        ContractType,
        SessionType,
        
        # Factory functions
        create_paper_trading_config as create_sierra_paper_config,
        create_live_trading_config as create_sierra_live_config,
        create_data_collection_config as create_sierra_data_config,
        
        # Global functions - avec alias pour éviter conflits
        get_sierra_config,
        set_sierra_config
    )
    SIERRA_CONFIG_AVAILABLE = True
except ImportError as e:
    logging.warning(f"sierra_config.py non disponible: {e}")
    SIERRA_CONFIG_AVAILABLE = False
    # Définitions fallback
    SierraIBKRConfig = None
    get_sierra_config = lambda: {}

# === AUTOMATION CONFIG (NOUVEAU) ===
try:
    from .automation_config import (
        # Classes principales
        AutomationConfig,
        AutomationTradingConfig,
        AutomationRiskConfig,
        DataCollectionConfig,
        MonitoringConfig,
        IBKRConnectionConfig,
        MLConfig as AutomationMLConfig,  # Alias pour éviter conflit
        
        # Enums
        AutomationMode,
        TradingSession,
        AlertLevel,
        DataGranularity,
        
        # Factory functions
        create_conservative_config,
        create_data_collection_config as create_automation_data_config,
        create_paper_trading_config as create_automation_paper_config,
        
        # Global functions
        get_automation_config,
        set_automation_config,
        get_trading_config as get_automation_trading_config,  # Alias
        get_risk_config as get_automation_risk_config,        # Alias
        get_monitoring_config
    )
    AUTOMATION_CONFIG_AVAILABLE = True
except ImportError as e:
    logging.warning(f"automation_config.py non disponible: {e}")
    AUTOMATION_CONFIG_AVAILABLE = False
    # Définitions fallback
    AutomationConfig = None
    get_automation_config = lambda: {}

# === ML CONFIG (NOUVEAU) ===
try:
    from .ml_config import (
        # Classes principales
        MLConfig,
        BattleNavaleFeatureConfig,
        ModelConfig,
        TrainingConfig as MLTrainingConfig,  # Alias pour éviter conflit
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
        
        # Global functions
        get_ml_config,
        set_ml_config,
        get_battle_navale_features_config,
        get_model_config,
        get_training_config as get_ml_training_config,  # Alias
        
        # Utilities
        sync_with_automation_config
    )
    ML_CONFIG_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ml_config.py non disponible: {e}")
    ML_CONFIG_AVAILABLE = False
    # Définitions fallback
    MLConfig = None
    get_ml_config = lambda: {}

# === VERSION ET MÉTADONNÉES ===
__version__ = "3.0.0"
__author__ = "MIA_IA_SYSTEM"

# Logger
logger = logging.getLogger(__name__)

# === FONCTIONS UTILITAIRES GLOBALES ===

def get_all_configs() -> Dict[str, Any]:
    """
    Récupération de toutes les configurations en une fois
    
    Returns:
        Dict avec toutes les configs disponibles
    """
    configs = {
        'module_info': {
            'version': __version__,
            'available_configs': {
                'trading_config': TRADING_CONFIG_AVAILABLE,
                'sierra_config': SIERRA_CONFIG_AVAILABLE,
                'automation_config': AUTOMATION_CONFIG_AVAILABLE,
                'ml_config': ML_CONFIG_AVAILABLE
            }
        }
    }
    
    # Ajout configs disponibles
    if TRADING_CONFIG_AVAILABLE:
        try:
            configs['trading'] = get_trading_config()
        except Exception as e:
            logger.warning(f"Erreur chargement trading config: {e}")
    
    if SIERRA_CONFIG_AVAILABLE:
        try:
            configs['sierra'] = get_sierra_config()
        except Exception as e:
            logger.warning(f"Erreur chargement sierra config: {e}")
    
    if AUTOMATION_CONFIG_AVAILABLE:
        try:
            configs['automation'] = get_automation_config()
        except Exception as e:
            logger.warning(f"Erreur chargement automation config: {e}")
    
    if ML_CONFIG_AVAILABLE:
        try:
            configs['ml'] = get_ml_config()
        except Exception as e:
            logger.warning(f"Erreur chargement ml config: {e}")
    
    return configs

def validate_all_configs() -> Dict[str, bool]:
    """
    Validation de toutes les configurations disponibles
    
    Returns:
        Dict avec status validation de chaque config
    """
    validation_results = {}
    
    # Validation trading config
    if TRADING_CONFIG_AVAILABLE:
        try:
            config = get_trading_config()
            # Assume validation method exists or basic check
            validation_results['trading'] = config is not None
        except Exception as e:
            validation_results['trading'] = False
            logger.error(f"Validation trading config failed: {e}")
    
    # Validation sierra config
    if SIERRA_CONFIG_AVAILABLE:
        try:
            config = get_sierra_config()
            validation_results['sierra'] = hasattr(config, 'validate') and config.validate()
        except Exception as e:
            validation_results['sierra'] = False
            logger.error(f"Validation sierra config failed: {e}")
    
    # Validation automation config
    if AUTOMATION_CONFIG_AVAILABLE:
        try:
            config = get_automation_config()
            validation_results['automation'] = hasattr(config, 'validate') and config.validate()
        except Exception as e:
            validation_results['automation'] = False
            logger.error(f"Validation automation config failed: {e}")
    
    # Validation ML config
    if ML_CONFIG_AVAILABLE:
        try:
            config = get_ml_config()
            validation_results['ml'] = hasattr(config, 'validate') and config.validate()
        except Exception as e:
            validation_results['ml'] = False
            logger.error(f"Validation ml config failed: {e}")
    
    return validation_results

def setup_configs_for_environment(environment: str = "development"):
    """
    Configuration automatique pour environnement spécifique
    
    Args:
        environment: development, staging, production
    """
    logger.info(f"Configuration pour environnement: {environment}")
    
    try:
        # Configuration automation selon environnement
        if AUTOMATION_CONFIG_AVAILABLE:
            automation_config = get_automation_config()
            if hasattr(automation_config, 'update_for_environment'):
                automation_config.update_for_environment(environment)
                set_automation_config(automation_config)
        
        # Configuration ML selon environnement
        if ML_CONFIG_AVAILABLE:
            if environment == "production":
                ml_config = create_production_ml_config()
            elif environment == "development":
                ml_config = create_development_ml_config()
            else:
                ml_config = create_conservative_ml_config()
            
            set_ml_config(ml_config)
        
        # Synchronisation configs
        if ML_CONFIG_AVAILABLE and AUTOMATION_CONFIG_AVAILABLE:
            sync_with_automation_config()
        
        logger.info(f"✅ Configuration {environment} appliquée")
        
    except Exception as e:
        logger.error(f"❌ Erreur setup environnement {environment}: {e}")

def get_config_summary() -> Dict[str, Any]:
    """
    Résumé de toutes les configurations actives
    
    Returns:
        Résumé des configs principales
    """
    summary = {
        'timestamp': logging.Formatter().formatTime(logging.LogRecord(
            name='', level=0, pathname='', lineno=0, 
            msg='', args=(), exc_info=None
        )),
        'module_version': __version__,
        'available_modules': {
            'trading': TRADING_CONFIG_AVAILABLE,
            'sierra': SIERRA_CONFIG_AVAILABLE,
            'automation': AUTOMATION_CONFIG_AVAILABLE,
            'ml': ML_CONFIG_AVAILABLE
        }
    }
    
    # Informations principales de chaque config
    try:
        if TRADING_CONFIG_AVAILABLE:
            trading = get_trading_config()
            summary['trading_info'] = {
                'primary_symbol': getattr(trading, 'primary_symbol', 'N/A'),
                'trading_mode': getattr(trading, 'trading_mode', 'N/A'),
                'risk_level': getattr(trading, 'risk_level', 'N/A')
            }
        
        if AUTOMATION_CONFIG_AVAILABLE:
            automation = get_automation_config()
            summary['automation_info'] = {
                'automation_mode': getattr(automation.trading, 'automation_mode', 'N/A'),
                'daily_loss_limit': getattr(automation.risk, 'daily_loss_limit', 'N/A'),
                'monitoring_enabled': getattr(automation.monitoring, 'enable_live_monitoring', 'N/A')
            }
        
        if ML_CONFIG_AVAILABLE:
            ml = get_ml_config()
            summary['ml_info'] = {
                'ml_enabled': getattr(ml, 'ml_enabled', False),
                'environment': getattr(ml, 'environment', 'N/A'),
                'model_type': getattr(ml.model, 'model_type', 'N/A') if hasattr(ml, 'model') else 'N/A'
            }
    
    except Exception as e:
        logger.warning(f"Erreur génération summary: {e}")
    
    return summary

# === RACCOURCIS SPÉCIALISÉS ===

def get_battle_navale_config() -> Dict[str, Any]:
    """
    Configuration spécifique Battle Navale (agrégée)
    
    Returns:
        Config optimisée pour Battle Navale
    """
    config = {}
    
    # Features Battle Navale depuis ML config
    if ML_CONFIG_AVAILABLE:
        try:
            ml_config = get_ml_config()
            if hasattr(ml_config, 'features'):
                config['features'] = {
                    'enabled_features': ml_config.features.get_enabled_features(),
                    'feature_weights': ml_config.features.get_feature_weights(),
                    'battle_navale_features': ml_config.features.battle_navale_features
                }
        except Exception as e:
            logger.warning(f"Erreur Battle Navale features: {e}")
    
    # Configuration trading Battle Navale
    if AUTOMATION_CONFIG_AVAILABLE:
        try:
            auto_config = get_automation_config()
            config['trading'] = {
                'min_confidence': auto_config.trading.battle_navale_min_confidence,
                'confluence_validation': auto_config.trading.enable_confluence_validation,
                'min_confluence_score': auto_config.trading.min_confluence_score
            }
        except Exception as e:
            logger.warning(f"Erreur Battle Navale trading: {e}")
    
    return config

def get_production_config() -> Dict[str, Any]:
    """
    Configuration production complète
    
    Returns:
        Config prête pour production
    """
    return {
        'trading': get_trading_config() if TRADING_CONFIG_AVAILABLE else {},
        'sierra': get_sierra_config() if SIERRA_CONFIG_AVAILABLE else {},
        'automation': get_automation_config() if AUTOMATION_CONFIG_AVAILABLE else {},
        'ml': get_ml_config() if ML_CONFIG_AVAILABLE else {},
        'environment': 'production',
        'validation': validate_all_configs()
    }

# === EXPORTS PRINCIPAUX ===

# Exports compatibilité backward (PRIORITÉ)
__all__ = [
    # === CORE TRADING (EXISTANT) ===
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

# Exports Sierra Chart (si disponible)
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

# Exports Automation (nouveaux)
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

# Exports ML (nouveaux)
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

# Exports fonctions utilitaires
__all__.extend([
    # Fonctions globales
    'get_all_configs',
    'validate_all_configs',
    'setup_configs_for_environment',
    'get_config_summary',
    
    # Fonctions spécialisées
    'get_battle_navale_config',
    'get_production_config',
    
    # Métadonnées
    '__version__',
    
    # Status modules
    'TRADING_CONFIG_AVAILABLE',
    'SIERRA_CONFIG_AVAILABLE', 
    'AUTOMATION_CONFIG_AVAILABLE',
    'ML_CONFIG_AVAILABLE'
])

# === INITIALISATION MODULE ===

def _initialize_config_module():
    """Initialisation du module configuration"""
    try:
        logger.info(f"📦 Module Configuration v{__version__} chargé")
        logger.info(f"📊 Modules disponibles:")
        logger.info(f"  - Trading Config: {'✅' if TRADING_CONFIG_AVAILABLE else '❌'}")
        logger.info(f"  - Sierra Config: {'✅' if SIERRA_CONFIG_AVAILABLE else '❌'}")
        logger.info(f"  - Automation Config: {'✅' if AUTOMATION_CONFIG_AVAILABLE else '❌'}")
        logger.info(f"  - ML Config: {'✅' if ML_CONFIG_AVAILABLE else '❌'}")
        
        # Validation configs disponibles
        if any([TRADING_CONFIG_AVAILABLE, SIERRA_CONFIG_AVAILABLE, 
                AUTOMATION_CONFIG_AVAILABLE, ML_CONFIG_AVAILABLE]):
            validation_results = validate_all_configs()
            valid_configs = sum(validation_results.values())
            total_configs = len(validation_results)
            logger.info(f"🔍 Validation: {valid_configs}/{total_configs} configs valides")
        
        # Synchronisation si ML et Automation disponibles
        if ML_CONFIG_AVAILABLE and AUTOMATION_CONFIG_AVAILABLE:
            try:
                sync_with_automation_config()
                logger.info("🔄 Synchronisation ML ↔ Automation OK")
            except Exception as e:
                logger.warning(f"⚠️  Synchronisation partielle: {e}")
    
    except Exception as e:
        logger.error(f"❌ Erreur initialisation module config: {e}")

# Initialisation automatique
_initialize_config_module()

# === TEST FUNCTION ===

def test_config_module():
    """Test complet du module configuration"""
    logger.debug("Test module configuration...")
    
    # Test disponibilité modules
    logger.info("Trading Config: {'✅' if TRADING_CONFIG_AVAILABLE else '❌'}")
    logger.info("Sierra Config: {'✅' if SIERRA_CONFIG_AVAILABLE else '❌'}")
    logger.info("Automation Config: {'✅' if AUTOMATION_CONFIG_AVAILABLE else '❌'}")
    logger.info("ML Config: {'✅' if ML_CONFIG_AVAILABLE else '❌'}")
    
    # Test fonctions utilitaires
    try:
        summary = get_config_summary()
        logger.info("Config summary: {len(summary)} éléments")
    except Exception as e:
        logger.error("Erreur config summary: {e}")
    
    try:
        all_configs = get_all_configs()
        logger.info("All configs: {len(all_configs)} modules")
    except Exception as e:
        logger.error("Erreur all configs: {e}")
    
    try:
        validation = validate_all_configs()
        valid_count = sum(validation.values())
        logger.info("Validation: {valid_count}/{len(validation)} configs valides")
    except Exception as e:
        logger.error("Erreur validation: {e}")
    
    logger.info("🎯 Test module configuration COMPLETED")
    return True

if __name__ == "__main__":
    test_config_module()