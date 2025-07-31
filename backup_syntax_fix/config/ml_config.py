"""
config/ml_config.py

CONFIGURATION ML COMPLÈTE - MIA_IA_SYSTEM
Configuration centralisée pour tous les composants ML Battle Navale
Intégration avec ModelTrainer, SimpleLinearModel, DataProcessor, Validator

RESPONSABILITÉS :
- Configuration modèles ML (hyperparamètres, types)
- Configuration training (modes, validation, seuils)
- Configuration features Battle Navale (8 features + market)
- Configuration data processing (normalisation, splits)
- Configuration validation (cross-val, out-of-sample)
- Configuration déploiement (staging, production)
- Paths et stockage ML
- Factory functions pour configs spécialisées

INTÉGRATION : Native avec automation_config.py, complément ML spécialisé
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime, timezone, timedelta
from ml.model_validator import ValidationMethod
# Imports ML module components (avec fallback si pas disponible)
try:
    from ml.simple_model import ModelType, ModelStatus, ValidationMethod
    from ml.model_trainer import TrainingMode, ModelStage, ValidationLevel
    from ml.data_processor import DataQuality, FeatureType, ScalingMethod, SplitMethod
    ML_COMPONENTS_AVAILABLE = True
except ImportError:
    # Définitions fallback si module ML pas encore complet
    class ModelType(Enum):
        SIGNAL_CLASSIFIER = "signal_classifier"
        PROFITABILITY_PREDICTOR = "profitability"
        SIGNAL_STRENGTH = "signal_strength"
        EXIT_TIMING = "exit_timing"
    
    class TrainingMode(Enum):
        INITIAL = "initial"
        INCREMENTAL = "incremental" 
        RETRAIN = "retrain"
        CONTINUOUS = "continuous"
        EXPERIMENTAL = "experimental"
    
    class ValidationLevel(Enum):
        BASIC = "basic"
        RIGOROUS = "rigorous"
        COMPREHENSIVE = "comprehensive"
    
    ML_COMPONENTS_AVAILABLE = False

logger = logging.getLogger(__name__)

# === ML CONFIG ENUMS ===

class MLEnvironment(Enum):
    """Environnements ML"""
    DEVELOPMENT = "development"      # Développement/test
    RESEARCH = "research"           # Recherche/expérimentation
    STAGING = "staging"             # Pre-production
    PRODUCTION = "production"       # Production live
    BACKTESTING = "backtesting"     # Backtesting historique

class TrainingStrategy(Enum):
    """Stratégies d'entraînement"""
    BATCH_LEARNING = "batch"        # Training par batches
    ONLINE_LEARNING = "online"      # Training continu
    MINI_BATCH = "mini_batch"       # Mini-batches
    SCHEDULED = "scheduled"         # Training planifié
    EVENT_DRIVEN = "event_driven"   # Training déclenché par événements

class PerformanceObjective(Enum):
    """Objectifs de performance"""
    ACCURACY = "accuracy"           # Maximiser précision
    PRECISION = "precision"         # Maximiser precision
    RECALL = "recall"              # Maximiser recall
    F1_SCORE = "f1_score"          # Équilibre precision/recall
    PROFIT_OPTIMIZATION = "profit"  # Optimisation profit
    RISK_ADJUSTED = "risk_adjusted" # Performance ajustée risque

# === BATTLE NAVALE FEATURES CONFIG ===

@dataclass
class BattleNavaleFeatureConfig:
    """Configuration features Battle Navale (vos 8 features + market)"""
    
    # Vos 8 features Battle Navale principales
    battle_navale_features: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'vwap_trend_signal': {
            'enabled': True,
            'weight': 1.0,
            'scaling': 'standard',
            'description': 'Signal tendance VWAP Battle Navale'
        },
        'sierra_pattern_strength': {
            'enabled': True,
            'weight': 1.0,
            'scaling': 'standard', 
            'description': 'Force pattern Sierra Chart'
        },
        'dow_trend_regime': {
            'enabled': True,
            'weight': 1.0,
            'scaling': 'standard',
            'description': 'Régime tendance Dow Theory'
        },
        'gamma_levels_proximity': {
            'enabled': True,
            'weight': 1.0,
            'scaling': 'standard',
            'description': 'Proximité niveaux gamma'
        },
        'level_proximity': {
            'enabled': True,
            'weight': 1.0,
            'scaling': 'standard',
            'description': 'Proximité niveaux clés'
        },
        'es_nq_correlation': {
            'enabled': True,
            'weight': 0.8,
            'scaling': 'standard',
            'description': 'Corrélation ES/NQ'
        },
        'volume_confirmation': {
            'enabled': True,
            'weight': 1.0,
            'scaling': 'standard',
            'description': 'Confirmation volume'
        },
        'options_flow_bias': {
            'enabled': True,
            'weight': 0.9,
            'scaling': 'standard',
            'description': 'Biais flux options'
        }
    })
    
    # Features marché complémentaires
    market_features: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'market_volatility': {
            'enabled': True,
            'weight': 0.7,
            'scaling': 'robust',
            'description': 'Volatilité marché actuelle'
        },
        'session_time': {
            'enabled': True,
            'weight': 0.6,
            'scaling': 'none',
            'description': 'Heure session trading'
        },
        'bid_ask_spread': {
            'enabled': True,
            'weight': 0.5,
            'scaling': 'standard',
            'description': 'Écart bid-ask'
        },
        'recent_price_momentum': {
            'enabled': True,
            'weight': 0.8,
            'scaling': 'standard',
            'description': 'Momentum prix récent'
        }
    })
    
    # Configuration feature engineering
    feature_engineering: Dict[str, Any] = field(default_factory=lambda: {
        'polynomial_features': False,          # Features polynomiales
        'interaction_features': True,          # Features interaction
        'rolling_statistics': True,           # Statistiques mobiles
        'lag_features': False,                # Features décalées
        'technical_indicators': True,         # Indicateurs techniques
        'correlation_features': False         # Features corrélation
    })
    
    # Validation features
    feature_validation: Dict[str, Any] = field(default_factory=lambda: {
        'check_missing_values': True,
        'check_infinite_values': True,
        'check_feature_variance': True,
        'min_variance_threshold': 0.01,
        'max_correlation_threshold': 0.95,
        'feature_importance_threshold': 0.001
    })
    
    def get_enabled_features(self) -> List[str]:
        """Récupération features activées"""
        enabled = []
        
        # Battle Navale features
        for name, config in self.battle_navale_features.items():
            if config.get('enabled', True):
                enabled.append(name)
        
        # Market features
        for name, config in self.market_features.items():
            if config.get('enabled', True):
                enabled.append(name)
        
        return enabled
    
    def get_feature_weights(self) -> Dict[str, float]:
        """Récupération poids features"""
        weights = {}
        
        # Battle Navale weights
        for name, config in self.battle_navale_features.items():
            if config.get('enabled', True):
                weights[name] = config.get('weight', 1.0)
        
        # Market weights
        for name, config in self.market_features.items():
            if config.get('enabled', True):
                weights[name] = config.get('weight', 1.0)
        
        return weights

# === MODEL CONFIGURATION ===

@dataclass
class ModelConfig:
    """Configuration modèle ML"""
    
    # Type et architecture
    model_type: ModelType = ModelType.SIGNAL_CLASSIFIER
    algorithm: str = "logistic_regression"    # logistic_regression, linear_regression, ridge, lasso
    
    # Hyperparamètres
    hyperparameters: Dict[str, Any] = field(default_factory=lambda: {
        # Logistic Regression
        'C': 1.0,                    # Régularisation inverse
        'max_iter': 1000,            # Itérations maximum
        'solver': 'lbfgs',           # Solver optimisation
        'random_state': 42,          # Reproductibilité
        'class_weight': 'balanced',  # Gestion classes déséquilibrées
        
        # Linear Regression (si applicable)
        'fit_intercept': True,
        'normalize': False,
        
        # Ridge/Lasso (si applicable)
        'alpha': 1.0
    })
    
    # Configuration training
    validation_method: ValidationMethod = ValidationMethod.CROSS_VALIDATION
    cross_validation_folds: int = 5
    test_size: float = 0.2
    random_state: int = 42
    
    # Preprocessing
    feature_scaling: bool = True
    scaling_method: str = "standard"         # standard, robust, minmax
    handle_missing_values: bool = True
    outlier_detection: bool = True
    outlier_threshold: float = 3.0          # Z-score threshold
    
    # Seuils performance
    min_accuracy: float = 0.60              # Précision minimum acceptable
    target_accuracy: float = 0.70           # Précision cible
    min_precision: float = 0.65             # Precision minimum
    min_recall: float = 0.60                # Recall minimum
    min_f1_score: float = 0.62              # F1-score minimum
    
    def validate(self) -> bool:
        """Validation configuration modèle"""
        try:
            # Validation hyperparamètres
            if 'C' in self.hyperparameters and self.hyperparameters['C'] <= 0:
                logger.error("Hyperparamètre C doit être > 0")
                return False
            
            # Validation seuils
            if self.min_accuracy < 0.5 or self.min_accuracy > 1.0:
                logger.error("min_accuracy doit être entre 0.5 et 1.0")
                return False
            
            if self.test_size <= 0 or self.test_size >= 1:
                logger.error("test_size doit être entre 0 et 1")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur validation model config: {e}")
            return False

# === TRAINING CONFIGURATION ===

@dataclass
class TrainingConfig:
    """Configuration training ML"""
    
    # Modes et stratégies
    training_mode: TrainingMode = TrainingMode.INITIAL
    training_strategy: TrainingStrategy = TrainingStrategy.BATCH_LEARNING
    validation_level: ValidationLevel = ValidationLevel.RIGOROUS
    performance_objective: PerformanceObjective = PerformanceObjective.F1_SCORE
    
    # Données training
    min_training_samples: int = 200          # Échantillons minimum
    max_training_samples: int = 10000        # Échantillons maximum
    data_collection_period_days: int = 30    # Période collection données
    
    # Validation et testing
    cross_validation_enabled: bool = True
    cross_validation_folds: int = 5
    out_of_sample_testing: bool = True
    time_series_validation: bool = True
    walk_forward_analysis: bool = False      # Coûteux en calcul
    
    # Re-training
    auto_retrain_enabled: bool = False       # Désactivé par défaut
    retrain_frequency_trades: int = 1000     # Re-training tous les 1000 trades
    performance_degradation_threshold: float = 0.05  # 5% dégradation
    min_improvement_threshold: float = 0.02  # 2% amélioration minimum
    
    # Training avancé
    early_stopping: bool = True
    patience: int = 10                       # Patience early stopping
    learning_rate_adaptive: bool = False     # Learning rate adaptatif
    ensemble_methods: bool = False           # Méthodes ensemble
    
    def validate(self) -> bool:
        """Validation configuration training"""
        try:
            if self.min_training_samples < 50:
                logger.error("min_training_samples trop faible (<50)")
                return False
            
            if self.max_training_samples < self.min_training_samples * 2:
                logger.error("max_training_samples < 2x min")
                return False
            
            if self.cross_validation_folds < 3:
                logger.error("cross_validation_folds < 3")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur validation training config: {e}")
            return False

# === DEPLOYMENT CONFIGURATION ===

@dataclass 
class DeploymentConfig:
    """Configuration déploiement ML"""
    
    # Environnement
    target_environment: MLEnvironment = MLEnvironment.STAGING
    
    # Déploiement automatique
    auto_deploy_enabled: bool = False        # Sécurité - déploiement manuel
    min_performance_for_auto_deploy: float = 0.75
    staging_period_hours: int = 48           # Test staging 48h
    
    # A/B Testing
    ab_testing_enabled: bool = False
    ab_testing_traffic_split: float = 0.1   # 10% trafic nouveau modèle
    ab_testing_duration_hours: int = 168    # 1 semaine
    
    # Monitoring déploiement
    performance_monitoring: bool = True
    alert_on_performance_drop: bool = True
    alert_threshold: float = 0.05           # Alerte si chute 5%
    
    # Rollback
    auto_rollback_enabled: bool = True
    rollback_threshold: float = 0.10        # Rollback si chute 10%
    
    # Backup et versioning
    backup_previous_model: bool = True
    keep_model_versions: int = 5            # Garder 5 versions
    
    def validate(self) -> bool:
        """Validation configuration déploiement"""
        try:
            if self.ab_testing_traffic_split < 0 or self.ab_testing_traffic_split > 1:
                logger.error("ab_testing_traffic_split doit être entre 0 et 1")
                return False
            
            if self.min_performance_for_auto_deploy < 0.5:
                logger.error("min_performance_for_auto_deploy trop faible")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur validation deployment config: {e}")
            return False

# === PATHS ET STOCKAGE ===

@dataclass
class MLPathsConfig:
    """Configuration paths ML"""
    
    # Dossiers principaux
    ml_base_directory: str = "data/ml"
    models_directory: str = "data/models"
    training_data_directory: str = "data/snapshots"
    processed_data_directory: str = "data/ml_processed"
    
    # Sous-dossiers modèles
    trained_models_dir: str = "data/models/trained"
    staging_models_dir: str = "data/models/staging"
    production_models_dir: str = "data/models/production"
    backup_models_dir: str = "data/models/backup"
    experimental_models_dir: str = "data/models/experimental"
    
    # Dossiers données
    features_cache_dir: str = "data/ml/features_cache"
    datasets_dir: str = "data/ml/datasets"
    exports_dir: str = "data/ml/exports"
    
    # Logs ML
    ml_logs_directory: str = "logs/ml"
    training_logs_dir: str = "logs/ml/training"
    validation_logs_dir: str = "logs/ml/validation"
    deployment_logs_dir: str = "logs/ml/deployment"
    
    # Métadonnées
    metadata_directory: str = "data/ml/metadata"
    model_registry_file: str = "data/ml/metadata/model_registry.json"
    training_history_file: str = "data/ml/metadata/training_history.json"
    
    def create_directories(self):
        """Création de tous les dossiers ML"""
        directories = [
            self.ml_base_directory,
            self.models_directory,
            self.processed_data_directory,
            self.trained_models_dir,
            self.staging_models_dir,
            self.production_models_dir,
            self.backup_models_dir,
            self.experimental_models_dir,
            self.features_cache_dir,
            self.datasets_dir,
            self.exports_dir,
            self.ml_logs_directory,
            self.training_logs_dir,
            self.validation_logs_dir,
            self.deployment_logs_dir,
            self.metadata_directory
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        logger.info("Dossiers ML créés/vérifiés")

# === CONFIGURATION PRINCIPALE ML ===

@dataclass
class MLConfig:
    """Configuration ML complète"""
    
    # Métadonnées
    config_version: str = "1.0.0"
    environment: MLEnvironment = MLEnvironment.DEVELOPMENT
    created_timestamp: Optional[str] = None
    
    # Composants configuration
    features: BattleNavaleFeatureConfig = field(default_factory=BattleNavaleFeatureConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    deployment: DeploymentConfig = field(default_factory=DeploymentConfig)
    paths: MLPathsConfig = field(default_factory=MLPathsConfig)
    
    # Activation ML
    ml_enabled: bool = False                 # ML désactivé par défaut
    ml_components_available: bool = ML_COMPONENTS_AVAILABLE
    
    # Integration avec automation
    automation_integration: Dict[str, Any] = field(default_factory=lambda: {
        'signal_enhancement_enabled': False,  # Amélioration signaux
        'signal_weight_in_decision': 0.3,    # Poids ML dans décision (30%)
        'fallback_to_battle_navale': True,   # Fallback si ML fail
        'ml_confidence_threshold': 0.6,      # Seuil confiance ML
        'override_battle_navale': False      # Jamais override Battle Navale
    })
    
    def __post_init__(self):
        """Post-initialization"""
        if self.created_timestamp is None:
            self.created_timestamp = datetime.now(timezone.utc).isoformat()
        
        # Création dossiers
        self.paths.create_directories()
        
        # Validation
        if not self.validate():
            logger.warning("Configuration ML contient des erreurs")
    
    def validate(self) -> bool:
        """Validation complète configuration ML"""
        try:
            # Validation chaque composant
            if not self.model.validate():
                return False
            if not self.training.validate():
                return False
            if not self.deployment.validate():
                return False
            
            # Validations cross-component
            if self.ml_enabled and not self.ml_components_available:
                logger.warning("ML activé mais composants non disponibles")
            
            # Validation integration automation
            signal_weight = self.automation_integration.get('signal_weight_in_decision', 0)
            if signal_weight > 0.5:
                logger.warning("Poids ML > 50% - Battle Navale devient secondaire")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur validation ML config: {e}")
            return False
    
    def save_to_file(self, file_path: str):
        """Sauvegarde configuration vers fichier"""
        try:
            config_dict = self.to_dict()
            
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, default=str)
            
            logger.info(f"Configuration ML sauvée: {file_path}")
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde ML config: {e}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire"""
        def convert_value(obj):
            if hasattr(obj, '__dict__'):
                return {k: convert_value(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, (list, tuple)):
                return [convert_value(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: convert_value(v) for k, v in obj.items()}
            else:
                return obj
        
        return convert_value(self)
    
    def get_model_trainer_config(self) -> Dict[str, Any]:
        """Configuration pour ModelTrainer"""
        return {
            'min_samples_required': self.training.min_training_samples,
            'max_samples_per_training': self.training.max_training_samples,
            'model_type': self.model.model_type.value if hasattr(self.model.model_type, 'value') else self.model.model_type,
            'validation_level': self.training.validation_level.value if hasattr(self.training.validation_level, 'value') else self.training.validation_level,
            'auto_deploy_if_better': self.deployment.auto_deploy_enabled,
            'staging_period_hours': self.deployment.staging_period_hours,
            'performance_thresholds': {
                'min_accuracy': self.model.min_accuracy,
                'target_accuracy': self.model.target_accuracy,
                'min_precision': self.model.min_precision,
                'min_f1_score': self.model.min_f1_score
            }
        }

# === FACTORY FUNCTIONS ===

def create_development_ml_config() -> MLConfig:
    """Configuration ML développement"""
    config = MLConfig()
    config.environment = MLEnvironment.DEVELOPMENT
    config.ml_enabled = True
    
    # Training développement (plus permissif)
    config.model.min_accuracy = 0.55
    config.training.min_training_samples = 100
    config.training.auto_retrain_enabled = True
    
    # Déploiement développement
    config.deployment.auto_deploy_enabled = False
    config.deployment.staging_period_hours = 12
    
    return config

def create_research_ml_config() -> MLConfig:
    """Configuration ML recherche/expérimentation"""
    config = MLConfig()
    config.environment = MLEnvironment.RESEARCH
    config.ml_enabled = True
    
    # Training recherche (expérimental)
    config.training.walk_forward_analysis = True
    config.training.ensemble_methods = True
    config.model.algorithm = "ridge"  # Expérimentation
    
    # Features research
    config.features.feature_engineering['polynomial_features'] = True
    config.features.feature_engineering['lag_features'] = True
    
    return config

def create_production_ml_config() -> MLConfig:
    """Configuration ML production"""
    config = MLConfig()
    config.environment = MLEnvironment.PRODUCTION
    config.ml_enabled = True
    
    # Standards production élevés
    config.model.min_accuracy = 0.70
    config.model.target_accuracy = 0.75
    config.training.min_training_samples = 500
    
    # Sécurité production
    config.deployment.auto_deploy_enabled = False  # Déploiement manuel
    config.deployment.auto_rollback_enabled = True
    config.automation_integration['signal_weight_in_decision'] = 0.25  # 25% seulement
    
    return config

def create_conservative_ml_config() -> MLConfig:
    """Configuration ML conservatrice (recommandée début)"""
    config = MLConfig()
    config.ml_enabled = False  # Désactivé par défaut
    
    # Très conservateur
    config.model.min_accuracy = 0.75
    config.automation_integration['signal_weight_in_decision'] = 0.15  # 15% seulement
    config.automation_integration['override_battle_navale'] = False
    config.deployment.auto_deploy_enabled = False
    
    return config

def load_ml_config_from_file(file_path: str) -> MLConfig:
    """Chargement configuration ML depuis fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        
        # Reconstruction simplifiée (à améliorer selon besoins)
        config = MLConfig()
        
        # Mise à jour des valeurs depuis le dict
        if 'environment' in config_dict:
            config.environment = MLEnvironment(config_dict['environment'])
        
        if 'ml_enabled' in config_dict:
            config.ml_enabled = config_dict['ml_enabled']
        
        # TODO: Reconstruction complète des sous-objets si nécessaire
        
        logger.info(f"Configuration ML chargée: {file_path}")
        return config
        
    except Exception as e:
        logger.error(f"Erreur chargement ML config: {e}")
        raise

# === GLOBAL CONFIG MANAGEMENT ===

_global_ml_config: Optional[MLConfig] = None

def get_ml_config() -> MLConfig:
    """Récupération configuration ML globale"""
    global _global_ml_config
    if _global_ml_config is None:
        _global_ml_config = create_conservative_ml_config()
    return _global_ml_config

def set_ml_config(config: MLConfig):
    """Définition configuration ML globale"""
    global _global_ml_config
    _global_ml_config = config
    logger.info("Configuration ML globale mise à jour")

def get_battle_navale_features_config() -> BattleNavaleFeatureConfig:
    """Raccourci vers configuration features Battle Navale"""
    return get_ml_config().features

def get_model_config() -> ModelConfig:
    """Raccourci vers configuration modèle"""
    return get_ml_config().model

def get_training_config() -> TrainingConfig:
    """Raccourci vers configuration training"""
    return get_ml_config().training

# === INTEGRATION AVEC AUTOMATION_CONFIG ===

def sync_with_automation_config():
    """Synchronisation avec automation_config.py"""
    try:
        # Import conditionnel pour éviter dépendance circulaire
        from config.automation_config import get_automation_config
        
        auto_config = get_automation_config()
        ml_config = get_ml_config()
        
        # Synchronisation des paths
        if hasattr(auto_config, 'models_directory'):
            ml_config.paths.models_directory = auto_config.models_directory
        
        # Synchronisation environnement
        if hasattr(auto_config, 'environment'):
            if auto_config.environment == 'production':
                ml_config.environment = MLEnvironment.PRODUCTION
            elif auto_config.environment == 'development':
                ml_config.environment = MLEnvironment.DEVELOPMENT
        
        logger.info("Synchronisation ML config ↔ automation config OK")
        
    except ImportError:
        logger.warning("automation_config non disponible pour synchronisation")
    except Exception as e:
        logger.error(f"Erreur synchronisation configs: {e}")

# === TESTING & VALIDATION ===

def test_ml_config():
    """Test complet configuration ML"""
    logger.debug("Test ML config...")
    
    # Test config development
    dev_config = create_development_ml_config()
    logger.info("Config development: ML enabled = {dev_config.ml_enabled}")
    logger.info("Features count: {len(dev_config.features.get_enabled_features())}")
    
    # Test validation
    is_valid = dev_config.validate()
    logger.info("Validation: {is_valid}")
    
    # Test config production
    prod_config = create_production_ml_config()
    logger.info("Production: min_accuracy = {prod_config.model.min_accuracy}")
    
    # Test features Battle Navale
    features = prod_config.features.get_enabled_features()
    logger.info("Battle Navale features: {len([f for f in features if 'vwap' in f or 'sierra' in f])}")
    
    # Test serialization
    config_dict = dev_config.to_dict()
    logger.info("Serialization: {len(config_dict)} keys")
    
    # Test ModelTrainer config
    trainer_config = dev_config.get_model_trainer_config()
    logger.info("ModelTrainer config: {len(trainer_config)} params")
    
    # Test paths creation
    dev_config.paths.create_directories()
    logger.info("Paths creation: {dev_config.paths.ml_base_directory}")
    
    logger.info("🎯 ML config test COMPLETED")
    return True

if __name__ == "__main__":
    test_ml_config()