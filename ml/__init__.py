"""
MIA_IA_SYSTEM - Machine Learning Module
Module ML complet pour trading Battle Navale automatisé
"""

from core.logger import get_logger

logger = get_logger(__name__)

__all__ = []

# === SIMPLE MODEL IMPORTS ===
try:
    from .simple_model import (
        SimpleLinearModel,
        SimpleLinearPredictor,  # Alias pour compatibilité
        ModelType,
        ModelStatus,
        ModelPerformance,
        ModelConfig,
        TrainingResult,
        create_signal_classifier,
        create_profitability_predictor,
        create_signal_strength_model,
        create_battle_navale_model,
        test_simple_model
    )
    __all__.extend([
        'SimpleLinearModel',
        'SimpleLinearPredictor',
        'ModelType',
        'ModelStatus',
        'ModelPerformance',
        'ModelConfig',
        'TrainingResult',
        'create_signal_classifier',
        'create_profitability_predictor',
        'create_signal_strength_model',
        'create_battle_navale_model',
        'test_simple_model'
    ])
except ImportError as e:
    logger.warning(f"Could not import simple_model: {e}")

# === DATA PROCESSOR IMPORTS ===
try:
    from .data_processor import (
        MLDataProcessor,
        ProcessedDataset,
        DataQualityReport,
        FeatureStats,
        ProcessingConfig,
        DataQuality,
        FeatureType,
        ScalingMethod,
        SplitMethod,
        create_ml_data_processor,
        create_battle_navale_processor,
        create_data_processor,  # Alias
        test_ml_data_processor
    )
    __all__.extend([
        'MLDataProcessor',
        'ProcessedDataset',
        'DataQualityReport',
        'FeatureStats',
        'ProcessingConfig',
        'DataQuality',
        'FeatureType',
        'ScalingMethod',
        'SplitMethod',
        'create_ml_data_processor',
        'create_battle_navale_processor',
        'create_data_processor',
        'test_ml_data_processor'
    ])
except ImportError as e:
    logger.warning(f"Could not import data_processor: {e}")

# === MODEL VALIDATOR IMPORTS ===
try:
    from .model_validator import (
        ModelValidator,
        ValidationReport,
        CrossValidationResult,
        OutOfSampleResult,
        FeatureImportanceAnalysis,
        OverfittingAnalysis,
        ModelStabilityTest,
        ValidationMethod,
        ValidationLevel,
        OverfittingLevel,
        ModelHealth,
        create_model_validator,
        create_rigorous_validator,
        create_exhaustive_validator,
        test_model_validator
    )
    __all__.extend([
        'ModelValidator',
        'ValidationReport',
        'CrossValidationResult',
        'OutOfSampleResult',
        'FeatureImportanceAnalysis',
        'OverfittingAnalysis',
        'ModelStabilityTest',
        'ValidationMethod',
        'ValidationLevel',
        'OverfittingLevel',
        'ModelHealth',
        'create_model_validator',
        'create_rigorous_validator',
        'create_exhaustive_validator',
        'test_model_validator'
    ])
except ImportError as e:
    logger.warning(f"Could not import model_validator: {e}")

# === MODEL TRAINER IMPORTS ===
try:
    from .model_trainer import (
        ModelTrainer,
        TrainingSession,
        TrainingConfig,
        ModelVersion,
        TrainingMode,
        ModelStage,
        TrainingStatus,
        PerformanceThreshold,
        create_model_trainer,
        create_battle_navale_trainer,
        train_model_from_recent_data,
        test_model_trainer
    )
    __all__.extend([
        'ModelTrainer',
        'TrainingSession',
        'TrainingConfig',
        'ModelVersion',
        'TrainingMode',
        'ModelStage',
        'TrainingStatus',
        'PerformanceThreshold',
        'create_model_trainer',
        'create_battle_navale_trainer',
        'train_model_from_recent_data',
        'test_model_trainer'
    ])
except ImportError as e:
    logger.warning(f"Could not import model_trainer: {e}")

# === ALIAS POUR COMPATIBILITÉ ===
# SimpleMLModel est un alias de SimpleLinearModel pour compatibilité
try:
    SimpleMLModel = SimpleLinearModel
    __all__.append('SimpleMLModel')
except:
    pass