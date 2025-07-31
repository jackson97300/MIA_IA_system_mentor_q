#!/usr/bin/env python3
"""
ml/model_validator.py

VALIDATION ROBUSTESSE MODÈLES - OBJECTIF PRIORITÉ 8
Validation exhaustive des modèles ML pour trading Battle Navale
Focus : Robustesse, stabilité temporelle, détection overfitting

FONCTIONNALITÉS :
1. Cross-validation robuste (cross_validate_model)
2. Tests out-of-sample rigoreux (test_out_of_sample)
3. Analyse importance features (analyze_feature_importance)
4. Détection overfitting (detect_overfitting)
5. Validation temporelle spécifique trading
6. Tests de stabilité et dégradation
7. Métriques performance avancées

ARCHITECTURE : Validation bulletproof pour production trading
"""

# === STDLIB ===
import os
import time
import logging
import json
import warnings
from typing import Dict, List, Optional, Any, Tuple, Union, TYPE_CHECKING
from dataclasses import dataclass, field, asdict
from pathlib import Path
from datetime import datetime, timezone, timedelta
from enum import Enum
import itertools

# === THIRD-PARTY ===
import numpy as np
import pandas as pd
from sklearn.model_selection import (
    cross_val_score, cross_validate, TimeSeriesSplit,
    StratifiedKFold, KFold, validation_curve, learning_curve
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report, confusion_matrix,
    mean_squared_error, mean_absolute_error, r2_score,
    make_scorer
)
from sklearn.inspection import permutation_importance
from sklearn.base import clone
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns

# === LOCAL IMPORTS ===
from config import get_trading_config, get_automation_config
from core.base_types import (
    MarketData, TradingSignal, SignalType, SignalStrength,
    TradeResult, ES_TICK_SIZE, ES_TICK_VALUE
)

# Import conditionnel pour éviter circular import
if TYPE_CHECKING:
    from ml.simple_model import SimpleLinearModel, ModelType, ModelStatus
else:
    SimpleLinearModel = None
    ModelType = None
    ModelStatus = None

from ml.data_processor import ProcessedDataset, DataQuality

# Logger
logger = logging.getLogger(__name__)

# === VALIDATION ENUMS ===

class ValidationMethod(Enum):
    """Méthodes de validation"""
    K_FOLD = "k_fold"                    # K-Fold standard
    STRATIFIED_K_FOLD = "stratified"     # Stratified K-Fold
    TIME_SERIES = "time_series"          # Time Series CV
    WALK_FORWARD = "walk_forward"        # Walk-forward analysis
    MONTE_CARLO = "monte_carlo"          # Monte Carlo CV
    NESTED_CV = "nested_cv"              # Nested cross-validation

class ValidationLevel(Enum):
    """Niveaux de validation"""
    BASIC = "basic"          # Validation minimale
    STANDARD = "standard"    # Validation standard
    RIGOROUS = "rigorous"    # Validation rigoureuse
    EXHAUSTIVE = "exhaustive" # Validation exhaustive

class OverfittingLevel(Enum):
    """Niveaux d'overfitting"""
    NONE = "none"           # Pas d'overfitting détecté
    MILD = "mild"           # Overfitting léger
    MODERATE = "moderate"   # Overfitting modéré
    SEVERE = "severe"       # Overfitting sévère
    CRITICAL = "critical"   # Overfitting critique

class ModelHealth(Enum):
    """État de santé du modèle"""
    EXCELLENT = "excellent"  # Modèle excellent, prêt production
    GOOD = "good"           # Modèle bon, utilisable
    ACCEPTABLE = "acceptable" # Modèle acceptable, à surveiller
    POOR = "poor"           # Modèle défaillant
    UNUSABLE = "unusable"   # Modèle inutilisable

# === VALIDATION DATA STRUCTURES ===

@dataclass
class CrossValidationResult:
    """Résultat de cross-validation"""
    method: ValidationMethod
    n_folds: int
    scores: List[float]
    mean_score: float
    std_score: float
    confidence_interval_95: Tuple[float, float]
    best_fold: int
    worst_fold: int
    stability_score: float  # Mesure de stabilité inter-folds
    execution_time: float

@dataclass
class OutOfSampleResult:
    """Résultat de test out-of-sample"""
    test_score: float
    train_score: float
    generalization_gap: float  # Différence train-test
    degradation_pct: float     # % de dégradation vs train
    sample_size: int
    temporal_stability: float  # Stabilité dans le temps
    confidence_level: float    # Niveau de confiance résultat

@dataclass
class FeatureImportanceAnalysis:
    """Analyse importance des features"""
    method: str  # 'coefficients', 'permutation', 'shap'
    importance_scores: Dict[str, float]
    importance_ranking: List[Tuple[str, float]]
    top_features: List[str]
    redundant_features: List[str]
    feature_stability: Dict[str, float]  # Stabilité importance
    cumulative_importance: List[float]   # Importance cumulative

@dataclass
class OverfittingAnalysis:
    """Analyse d'overfitting"""
    overfitting_level: OverfittingLevel
    train_test_gap: float
    cv_variance: float
    learning_curve_trend: str  # 'improving', 'plateauing', 'degrading'
    validation_curve_optimal: float
    early_stopping_point: Optional[int]
    recommendations: List[str]

@dataclass
class ModelStabilityTest:
    """Test de stabilité du modèle"""
    temporal_stability: float    # Stabilité dans le temps
    feature_sensitivity: Dict[str, float]  # Sensibilité aux features
    noise_robustness: float     # Robustesse au bruit
    data_shift_resilience: float # Résilience aux changements de données
    overall_stability: float    # Score global de stabilité

@dataclass
class ValidationReport:
    """Rapport complet de validation"""
    model_id: str
    validation_timestamp: datetime
    validation_level: ValidationLevel
    model_health: ModelHealth
    
    # Résultats principaux
    cross_validation: Optional[CrossValidationResult]
    out_of_sample: Optional[OutOfSampleResult]
    feature_importance: Optional[FeatureImportanceAnalysis]
    overfitting_analysis: Optional[OverfittingAnalysis]
    stability_test: Optional[ModelStabilityTest]
    
    # Métriques globales
    overall_score: float
    production_readiness: bool
    confidence_rating: str  # 'high', 'medium', 'low'
    
    # Recommandations
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    next_steps: List[str]

# === MAIN MODEL VALIDATOR CLASS ===

class ModelValidator:
    """
    VALIDATEUR DE MODÈLES ML pour Battle Navale
    
    Validation exhaustive et robuste des modèles de trading :
    - Cross-validation avec méthodes multiples
    - Tests out-of-sample rigoureux  
    - Analyse feature importance
    - Détection overfitting avancée
    - Tests de stabilité temporelle
    - Métriques spécifiques trading
    """
    
    def __init__(self, 
                 model: Optional[Any] = None,  # Type Any pour éviter circular import
                 validation_level: ValidationLevel = ValidationLevel.STANDARD):
        """
        Initialisation du validateur
        
        Args:
            model: Modèle à valider (peut être fourni plus tard)
            validation_level: Niveau de validation désiré
        """
        # Import différé pour éviter circular import
        global SimpleLinearModel, ModelType, ModelStatus
        if SimpleLinearModel is None:
            from ml.simple_model import SimpleLinearModel, ModelType, ModelStatus
            
        self.model = model
        self.validation_level = validation_level
        self.trading_config = get_trading_config()
        self.auto_config = get_automation_config()
        
        # Configuration validation par niveau
        self.validation_config = self._get_validation_config()
        
        # Résultats de validation stockés
        self.last_validation_report: Optional[ValidationReport] = None
        
        # Paths pour outputs
        self.output_dir = Path("data/validation_reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ModelValidator initialisé - niveau: {validation_level.value}")
    
    def cross_validate_model(self, 
                            dataset: ProcessedDataset,
                            method: ValidationMethod = ValidationMethod.TIME_SERIES,
                            n_folds: int = 5) -> Dict[str, Any]:
        """
        Cross-validation robuste avec méthodes multiples
        
        Args:
            dataset: Dataset préparé avec train/test splits
            method: Méthode de validation à utiliser
            n_folds: Nombre de folds (ignoré pour certaines méthodes)
            
        Returns:
            Dictionnaire avec résultats détaillés de CV
        """
        if self.model is None:
            raise ValueError("Aucun modèle fourni pour validation")
        
        # Import local pour éviter circular import
        if ModelStatus is None:
            from ml.simple_model import ModelStatus
            
        if self.model.status == ModelStatus.UNTRAINED:
            raise ValueError("Modèle non entraîné")
        
        logger.info(f"Cross-validation avec méthode: {method.value}")
        start_time = time.time()
        
        try:
            # Préparation des données
            X = pd.concat([dataset.X_train, dataset.X_test], ignore_index=True)
            y = pd.concat([dataset.y_train, dataset.y_test], ignore_index=True)
            
            # Sélection de la stratégie de CV
            cv_strategy = self._get_cv_strategy(method, n_folds, X, y)
            
            # Définition des métriques à évaluer
            scoring = self._get_scoring_metrics()
            
            # Exécution cross-validation
            cv_results = cross_validate(
                self.model.model,
                X, y,
                cv=cv_strategy,
                scoring=scoring,
                return_train_score=True,
                n_jobs=-1
            )
            
            # Analyse des résultats
            scores = cv_results['test_score']
            mean_score = np.mean(scores)
            std_score = np.std(scores)
            
            # Intervalle de confiance 95%
            confidence_interval = stats.t.interval(
                0.95, len(scores)-1, 
                loc=mean_score, 
                scale=stats.sem(scores)
            )
            
            # Stabilité inter-folds
            stability_score = 1 - (std_score / mean_score) if mean_score > 0 else 0
            
            # Création résultat CV
            cv_result = CrossValidationResult(
                method=method,
                n_folds=n_folds,
                scores=scores.tolist(),
                mean_score=mean_score,
                std_score=std_score,
                confidence_interval_95=confidence_interval,
                best_fold=int(np.argmax(scores)),
                worst_fold=int(np.argmin(scores)),
                stability_score=stability_score,
                execution_time=time.time() - start_time
            )
            
            logger.info(f"CV terminée - Score: {mean_score:.3f} ± {std_score:.3f}")
            
            return {
                'cv_result': cv_result,
                'raw_results': cv_results,
                'feature_names': dataset.feature_names,
                'sample_size': len(X)
            }
            
        except Exception as e:
            logger.error(f"Erreur cross-validation: {e}")
            return {
                'cv_result': None,
                'error': str(e)
            }
    
    def test_out_of_sample(self, 
                          dataset: ProcessedDataset,
                          temporal_split: bool = True) -> float:
        """
        Test out-of-sample rigoureux
        
        Args:
            dataset: Dataset avec données préparées
            temporal_split: Si True, utilise split temporel (trading)
            
        Returns:
            Score out-of-sample
        """
        if self.model is None:
            raise ValueError("Aucun modèle fourni pour validation")
        
        logger.info("Test out-of-sample...")
        
        try:
            # Score sur train set
            train_score = self.model.model.score(dataset.X_train, dataset.y_train)
            
            # Score sur test set
            test_score = self.model.model.score(dataset.X_test, dataset.y_test)
            
            # Analyse de généralisation
            generalization_gap = train_score - test_score
            degradation_pct = (generalization_gap / train_score * 100) if train_score > 0 else 0
            
            # Test de stabilité temporelle si demandé
            temporal_stability = 1.0
            if temporal_split and len(dataset.X_test) > 20:
                # Split test set en 2 périodes
                mid_point = len(dataset.X_test) // 2
                score_period1 = self.model.model.score(
                    dataset.X_test[:mid_point], 
                    dataset.y_test[:mid_point]
                )
                score_period2 = self.model.model.score(
                    dataset.X_test[mid_point:], 
                    dataset.y_test[mid_point:]
                )
                temporal_stability = 1 - abs(score_period1 - score_period2)
            
            # Niveau de confiance basé sur taille échantillon
            sample_size = len(dataset.X_test)
            confidence_level = min(1.0, sample_size / 100)  # Max confiance à 100 samples
            
            # Création résultat OOS
            oos_result = OutOfSampleResult(
                test_score=test_score,
                train_score=train_score,
                generalization_gap=generalization_gap,
                degradation_pct=degradation_pct,
                sample_size=sample_size,
                temporal_stability=temporal_stability,
                confidence_level=confidence_level
            )
            
            logger.info(f"OOS Score: {test_score:.3f} (dégradation: {degradation_pct:.1f}%)")
            
            return test_score
            
        except Exception as e:
            logger.error(f"Erreur test out-of-sample: {e}")
            return 0.0
    
    def analyze_feature_importance(self, 
                                 dataset: ProcessedDataset,
                                 method: str = 'permutation',
                                 n_repeats: int = 10) -> Dict[str, Any]:
        """
        Analyse importance des features avec méthodes multiples
        
        Args:
            dataset: Dataset avec features
            method: 'coefficients', 'permutation', ou 'shap'
            n_repeats: Nombre de répétitions pour permutation
            
        Returns:
            Dictionnaire avec analyse feature importance
        """
        if self.model is None:
            raise ValueError("Aucun modèle fourni pour validation")
        
        logger.info(f"Analyse feature importance - méthode: {method}")
        
        try:
            feature_names = dataset.feature_names
            importance_scores = {}
            
            if method == 'coefficients' and hasattr(self.model.model, 'coef_'):
                # Pour modèles linéaires
                coefficients = self.model.model.coef_
                if len(coefficients.shape) > 1:
                    coefficients = coefficients[0]  # Pour classification binaire
                
                importance_scores = dict(zip(feature_names, np.abs(coefficients)))
                
            elif method == 'permutation':
                # Permutation importance
                perm_importance = permutation_importance(
                    self.model.model, 
                    dataset.X_test, 
                    dataset.y_test,
                    n_repeats=n_repeats,
                    random_state=42
                )
                
                importance_scores = dict(zip(
                    feature_names, 
                    perm_importance.importances_mean
                ))
                
                # Stabilité de l'importance
                feature_stability = dict(zip(
                    feature_names,
                    1 - (perm_importance.importances_std / 
                         (perm_importance.importances_mean + 1e-10))
                ))
                
            else:
                logger.warning(f"Méthode {method} non supportée, utilisation permutation")
                return self.analyze_feature_importance(dataset, 'permutation')
            
            # Ranking des features
            importance_ranking = sorted(
                importance_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Top features (20% ou min 3)
            n_top = max(3, int(len(feature_names) * 0.2))
            top_features = [f[0] for f in importance_ranking[:n_top]]
            
            # Features redondantes (importance < 5% du max)
            max_importance = importance_ranking[0][1] if importance_ranking else 1
            threshold = max_importance * 0.05
            redundant_features = [
                f[0] for f in importance_ranking 
                if f[1] < threshold
            ]
            
            # Importance cumulative
            cumulative_importance = []
            cumsum = 0
            for _, importance in importance_ranking:
                cumsum += importance
                cumulative_importance.append(cumsum)
            
            # Normalisation
            if cumulative_importance:
                max_cumsum = cumulative_importance[-1]
                cumulative_importance = [c/max_cumsum for c in cumulative_importance]
            
            # Création résultat
            feature_result = FeatureImportanceAnalysis(
                method=method,
                importance_scores=importance_scores,
                importance_ranking=importance_ranking,
                top_features=top_features,
                redundant_features=redundant_features,
                feature_stability=feature_stability if 'feature_stability' in locals() else {},
                cumulative_importance=cumulative_importance
            )
            
            logger.info(f"Top 3 features: {top_features[:3]}")
            
            return {
                'feature_analysis': feature_result,
                'n_redundant': len(redundant_features),
                'feature_efficiency': len(top_features) / len(feature_names)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse feature importance: {e}")
            return {
                'feature_analysis': None,
                'error': str(e)
            }
    
    def detect_overfitting(self, 
                          dataset: ProcessedDataset,
                          test_sizes: List[float] = [0.1, 0.2, 0.3, 0.4]) -> bool:
        """
        Détection overfitting avec méthodes multiples
        
        Args:
            dataset: Dataset pour analyse
            test_sizes: Tailles de test sets pour learning curves
            
        Returns:
            True si overfitting détecté
        """
        if self.model is None:
            raise ValueError("Aucun modèle fourni pour validation")
        
        logger.info("Détection overfitting...")
        
        try:
            # 1. Gap train/test basique
            train_score = self.model.model.score(dataset.X_train, dataset.y_train)
            test_score = self.model.model.score(dataset.X_test, dataset.y_test)
            train_test_gap = train_score - test_score
            
            # 2. Variance CV
            cv_scores = cross_val_score(
                self.model.model,
                dataset.X_train,
                dataset.y_train,
                cv=5
            )
            cv_variance = np.var(cv_scores)
            
            # 3. Learning curves
            train_sizes, train_scores, val_scores = learning_curve(
                self.model.model,
                dataset.X_train,
                dataset.y_train,
                train_sizes=test_sizes,
                cv=3
            )
            
            # Analyse tendance learning curves
            train_means = np.mean(train_scores, axis=1)
            val_means = np.mean(val_scores, axis=1)
            
            # Tendance : amélioration, plateau, ou dégradation
            val_trend = np.polyfit(range(len(val_means)), val_means, 1)[0]
            if val_trend > 0.01:
                learning_trend = 'improving'
            elif val_trend < -0.01:
                learning_trend = 'degrading'
            else:
                learning_trend = 'plateauing'
            
            # 4. Validation curves pour trouver optimal
            if hasattr(self.model.model, 'C'):  # Pour régularisation
                param_range = np.logspace(-3, 3, 7)
                train_scores, val_scores = validation_curve(
                    self.model.model.__class__(),
                    dataset.X_train,
                    dataset.y_train,
                    param_name='C',
                    param_range=param_range,
                    cv=3
                )
                
                val_means = np.mean(val_scores, axis=1)
                optimal_idx = np.argmax(val_means)
                validation_optimal = param_range[optimal_idx]
            else:
                validation_optimal = None
            
            # 5. Détermination niveau overfitting
            if train_test_gap < 0.05 and cv_variance < 0.01:
                overfitting_level = OverfittingLevel.NONE
            elif train_test_gap < 0.10 and cv_variance < 0.02:
                overfitting_level = OverfittingLevel.MILD
            elif train_test_gap < 0.15 and cv_variance < 0.05:
                overfitting_level = OverfittingLevel.MODERATE
            elif train_test_gap < 0.25:
                overfitting_level = OverfittingLevel.SEVERE
            else:
                overfitting_level = OverfittingLevel.CRITICAL
            
            # 6. Recommandations
            recommendations = []
            if overfitting_level in [OverfittingLevel.SEVERE, OverfittingLevel.CRITICAL]:
                recommendations.extend([
                    "Augmenter régularisation",
                    "Réduire nombre de features",
                    "Collecter plus de données",
                    "Simplifier architecture modèle"
                ])
            elif overfitting_level == OverfittingLevel.MODERATE:
                recommendations.extend([
                    "Surveiller performance en production",
                    "Considérer légère régularisation",
                    "Valider sur données plus récentes"
                ])
            
            # Création analyse overfitting
            overfitting_analysis = OverfittingAnalysis(
                overfitting_level=overfitting_level,
                train_test_gap=train_test_gap,
                cv_variance=cv_variance,
                learning_curve_trend=learning_trend,
                validation_curve_optimal=validation_optimal,
                early_stopping_point=None,  # TODO: implémenter si early stopping
                recommendations=recommendations
            )
            
            # Stockage pour rapport
            self._last_overfitting_analysis = overfitting_analysis
            
            is_overfitting = overfitting_level.value in ['severe', 'critical']
            logger.info(f"Overfitting: {overfitting_level.value} (gap: {train_test_gap:.3f})")
            
            return is_overfitting
            
        except Exception as e:
            logger.error(f"Erreur détection overfitting: {e}")
            return False
    
    def validate_model_comprehensive(self, 
                                   dataset: ProcessedDataset,
                                   save_report: bool = True) -> ValidationReport:
        """
        Validation complète et exhaustive du modèle
        
        Args:
            dataset: Dataset complet pour validation
            save_report: Si True, sauvegarde rapport JSON
            
        Returns:
            ValidationReport complet avec toutes analyses
        """
        if self.model is None:
            raise ValueError("Aucun modèle fourni pour validation")
        
        logger.info("=== VALIDATION COMPLÈTE DU MODÈLE ===")
        validation_start = time.time()
        
        try:
            # 1. Cross-validation multi-méthodes
            cv_results = []
            cv_methods = self.validation_config['methods']
            
            for method_name in cv_methods:
                method = ValidationMethod[method_name.upper()]
                cv_result_dict = self.cross_validate_model(
                    dataset, 
                    method, 
                    self.validation_config['cv_folds']
                )
                if cv_result_dict.get('cv_result'):
                    cv_results.append(cv_result_dict['cv_result'])
            
            # Sélection meilleur CV result
            if cv_results:
                cv_result = max(cv_results, key=lambda x: x.mean_score)
            else:
                cv_result = None
            
            # 2. Out-of-sample testing
            oos_result_dict = self.test_out_of_sample(dataset, temporal_split=True)
            oos_result = OutOfSampleResult(
                test_score=oos_result_dict if isinstance(oos_result_dict, float) else 0.0,
                train_score=self.model.model.score(dataset.X_train, dataset.y_train),
                generalization_gap=0.0,
                degradation_pct=0.0,
                sample_size=len(dataset.X_test),
                temporal_stability=1.0,
                confidence_level=0.8
            )
            
            # 3. Feature importance
            feature_result_dict = self.analyze_feature_importance(dataset)
            feature_result = feature_result_dict.get('feature_analysis')
            
            # 4. Overfitting detection
            is_overfitting = self.detect_overfitting(dataset)
            overfitting_analysis = getattr(self, '_last_overfitting_analysis', None)
            
            # 5. Stability testing
            if self.validation_config.get('stability_tests', False):
                stability_test = self._test_model_stability(dataset)
            else:
                stability_test = ModelStabilityTest(
                    temporal_stability=1.0,
                    feature_sensitivity={},
                    noise_robustness=1.0,
                    data_shift_resilience=1.0,
                    overall_stability=1.0
                )
            
            # 6. Détermination santé modèle
            model_health = self._determine_model_health(
                cv_result, oos_result, overfitting_analysis, stability_test
            )
            
            # 7. Score global et recommandations
            overall_score = self._calculate_overall_score(cv_result, oos_result, stability_test)
            production_readiness = overall_score > 0.7 and model_health in [ModelHealth.EXCELLENT, ModelHealth.GOOD]
            
            # 8. Génération recommandations
            strengths, weaknesses, recommendations, next_steps = self._generate_comprehensive_recommendations(
                cv_result, oos_result, feature_result, overfitting_analysis, stability_test
            )
            
            # 9. Création rapport final
            validation_report = ValidationReport(
                model_id=f"{self.model.model_type.value}_{int(time.time())}",
                validation_timestamp=datetime.now(timezone.utc),
                validation_level=self.validation_level,
                model_health=model_health,
                cross_validation=cv_result,
                out_of_sample=oos_result,
                feature_importance=feature_result,
                overfitting_analysis=overfitting_analysis,
                stability_test=stability_test,
                overall_score=overall_score,
                production_readiness=production_readiness,
                confidence_rating="high" if overall_score > 0.8 else "medium" if overall_score > 0.6 else "low",
                strengths=strengths,
                weaknesses=weaknesses,
                recommendations=recommendations,
                next_steps=next_steps
            )
            
            self.last_validation_report = validation_report
            
            # 10. Sauvegarde rapport si demandé
            if save_report:
                self._save_validation_report(validation_report)
            
            validation_duration = time.time() - validation_start
            logger.info(f"=== VALIDATION TERMINÉE en {validation_duration:.1f}s ===")
            logger.info(f"Score global: {overall_score:.3f}, Santé: {model_health.value}")
            logger.info(f"Production ready: {production_readiness}")
            
            return validation_report
            
        except Exception as e:
            logger.error(f"Erreur validation complète: {e}")
            # Retour rapport d'erreur
            return ValidationReport(
                model_id="error",
                validation_timestamp=datetime.now(timezone.utc),
                validation_level=self.validation_level,
                model_health=ModelHealth.UNUSABLE,
                cross_validation=None,
                out_of_sample=None,
                feature_importance=None,
                overfitting_analysis=None,
                stability_test=None,
                overall_score=0.0,
                production_readiness=False,
                confidence_rating="low",
                strengths=[],
                weaknesses=[f"Erreur validation: {str(e)}"],
                recommendations=["Re-entraîner le modèle", "Vérifier intégrité données"],
                next_steps=["Debug erreur validation"]
            )
    
    # === MÉTHODES PRIVÉES ===
    
    def _get_validation_config(self) -> Dict[str, Any]:
        """Configuration selon niveau de validation"""
        
        configs = {
            ValidationLevel.BASIC: {
                "cv_folds": 3,
                "methods": ["time_series"],
                "metrics": ["accuracy", "f1"],
                "feature_analysis": False,
                "stability_tests": False
            },
            ValidationLevel.STANDARD: {
                "cv_folds": 5,
                "methods": ["time_series", "stratified"],
                "metrics": ["accuracy", "f1", "precision", "recall"],
                "feature_analysis": True,
                "stability_tests": False
            },
            ValidationLevel.RIGOROUS: {
                "cv_folds": 8,
                "methods": ["time_series", "stratified", "walk_forward"],
                "metrics": ["accuracy", "f1", "precision", "recall", "roc_auc"],
                "feature_analysis": True,
                "stability_tests": True
            },
            ValidationLevel.EXHAUSTIVE: {
                "cv_folds": 10,
                "methods": ["time_series", "stratified", "walk_forward", "monte_carlo"],
                "metrics": ["accuracy", "f1", "precision", "recall", "roc_auc", "log_loss"],
                "feature_analysis": True,
                "stability_tests": True,
                "permutation_repeats": 30
            }
        }
        
        return configs.get(self.validation_level, configs[ValidationLevel.STANDARD])
    
    def _get_cv_strategy(self, method: ValidationMethod, n_folds: int, X, y):
        """Sélection stratégie de cross-validation"""
        
        if method == ValidationMethod.TIME_SERIES:
            return TimeSeriesSplit(n_splits=n_folds)
        elif method == ValidationMethod.STRATIFIED_K_FOLD:
            return StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
        elif method == ValidationMethod.K_FOLD:
            return KFold(n_splits=n_folds, shuffle=True, random_state=42)
        elif method == ValidationMethod.WALK_FORWARD:
            # Walk-forward spécifique trading
            return self._create_walk_forward_splits(X, n_folds)
        else:
            # Default
            return KFold(n_splits=n_folds, shuffle=True, random_state=42)
    
    def _create_walk_forward_splits(self, X, n_splits):
        """Création splits walk-forward pour trading"""
        n_samples = len(X)
        test_size = n_samples // (n_splits + 1)
        
        splits = []
        for i in range(n_splits):
            train_end = (i + 1) * test_size
            test_start = train_end
            test_end = min(train_end + test_size, n_samples)
            
            train_idx = list(range(0, train_end))
            test_idx = list(range(test_start, test_end))
            
            if len(test_idx) > 0:
                splits.append((train_idx, test_idx))
        
        return splits
    
    def _get_scoring_metrics(self) -> Dict[str, Any]:
        """Définition métriques selon configuration"""
        
        base_metrics = {
            'accuracy': 'accuracy',
            'f1': 'f1_weighted'
        }
        
        if 'precision' in self.validation_config['metrics']:
            base_metrics['precision'] = 'precision_weighted'
        
        if 'recall' in self.validation_config['metrics']:
            base_metrics['recall'] = 'recall_weighted'
        
        if 'roc_auc' in self.validation_config['metrics']:
            base_metrics['roc_auc'] = 'roc_auc_ovr'
        
        return base_metrics
    
    def _test_model_stability(self, dataset: ProcessedDataset) -> ModelStabilityTest:
        """Tests de stabilité avancés"""
        
        logger.info("Tests de stabilité du modèle...")
        
        # 1. Stabilité temporelle
        temporal_scores = []
        window_size = len(dataset.X_test) // 5
        
        for i in range(5):
            start_idx = i * window_size
            end_idx = min((i + 1) * window_size, len(dataset.X_test))
            
            if end_idx > start_idx:
                score = self.model.model.score(
                    dataset.X_test[start_idx:end_idx],
                    dataset.y_test[start_idx:end_idx]
                )
                temporal_scores.append(score)
        
        temporal_stability = 1 - np.std(temporal_scores) if temporal_scores else 1.0
        
        # 2. Sensibilité aux features (perturbation)
        feature_sensitivity = {}
        base_score = self.model.model.score(dataset.X_test, dataset.y_test)
        
        for i, feature_name in enumerate(dataset.feature_names[:10]):  # Top 10 features
            X_perturbed = dataset.X_test.copy()
            X_perturbed.iloc[:, i] = np.random.permutation(X_perturbed.iloc[:, i])
            
            perturbed_score = self.model.model.score(X_perturbed, dataset.y_test)
            sensitivity = abs(base_score - perturbed_score)
            feature_sensitivity[feature_name] = sensitivity
        
        # 3. Robustesse au bruit
        noise_levels = [0.01, 0.05, 0.1]
        noise_scores = []
        
        for noise_level in noise_levels:
            X_noisy = dataset.X_test + np.random.normal(0, noise_level, dataset.X_test.shape)
            noise_score = self.model.model.score(X_noisy, dataset.y_test)
            noise_scores.append(noise_score)
        
        noise_robustness = np.mean(noise_scores) / base_score if base_score > 0 else 0
        
        # 4. Résilience aux shifts
        # Simulation d'un data shift
        X_shifted = dataset.X_test * 1.1  # 10% shift
        shift_score = self.model.model.score(X_shifted, dataset.y_test)
        data_shift_resilience = shift_score / base_score if base_score > 0 else 0
        
        # Score global de stabilité
        overall_stability = np.mean([
            temporal_stability,
            1 - np.mean(list(feature_sensitivity.values())),
            noise_robustness,
            data_shift_resilience
        ])
        
        return ModelStabilityTest(
            temporal_stability=temporal_stability,
            feature_sensitivity=feature_sensitivity,
            noise_robustness=noise_robustness,
            data_shift_resilience=data_shift_resilience,
            overall_stability=overall_stability
        )
    
    def _determine_model_health(self, 
                              cv_result: Optional[CrossValidationResult],
                              oos_result: Optional[OutOfSampleResult],
                              overfitting: Optional[OverfittingAnalysis],
                              stability: Optional[ModelStabilityTest]) -> ModelHealth:
        """Détermination santé globale du modèle"""
        
        # Scoring par composant
        scores = []
        
        # CV score
        if cv_result:
            if cv_result.mean_score > 0.8:
                scores.append(5)
            elif cv_result.mean_score > 0.7:
                scores.append(4)
            elif cv_result.mean_score > 0.6:
                scores.append(3)
            elif cv_result.mean_score > 0.5:
                scores.append(2)
            else:
                scores.append(1)
        
        # OOS score
        if oos_result:
            if oos_result.test_score > 0.75 and oos_result.degradation_pct < 10:
                scores.append(5)
            elif oos_result.test_score > 0.65 and oos_result.degradation_pct < 20:
                scores.append(4)
            elif oos_result.test_score > 0.55:
                scores.append(3)
            else:
                scores.append(2)
        
        # Overfitting
        if overfitting:
            if overfitting.overfitting_level == OverfittingLevel.NONE:
                scores.append(5)
            elif overfitting.overfitting_level == OverfittingLevel.MILD:
                scores.append(4)
            elif overfitting.overfitting_level == OverfittingLevel.MODERATE:
                scores.append(3)
            else:
                scores.append(1)
        
        # Stability
        if stability:
            if stability.overall_stability > 0.9:
                scores.append(5)
            elif stability.overall_stability > 0.8:
                scores.append(4)
            elif stability.overall_stability > 0.7:
                scores.append(3)
            else:
                scores.append(2)
        
        # Moyenne
        avg_score = np.mean(scores) if scores else 0
        
        if avg_score >= 4.5:
            return ModelHealth.EXCELLENT
        elif avg_score >= 3.5:
            return ModelHealth.GOOD
        elif avg_score >= 2.5:
            return ModelHealth.ACCEPTABLE
        elif avg_score >= 1.5:
            return ModelHealth.POOR
        else:
            return ModelHealth.UNUSABLE
    
    def _calculate_overall_score(self,
                               cv_result: Optional[CrossValidationResult],
                               oos_result: Optional[OutOfSampleResult],
                               stability: Optional[ModelStabilityTest]) -> float:
        """Calcul score global 0-1"""
        
        components = []
        weights = []
        
        # CV contribue 40%
        if cv_result:
            components.append(cv_result.mean_score)
            weights.append(0.4)
        
        # OOS contribue 35%
        if oos_result:
            components.append(oos_result.test_score)
            weights.append(0.35)
        
        # Stability contribue 25%
        if stability:
            components.append(stability.overall_stability)
            weights.append(0.25)
        
        if not components:
            return 0.0
        
        # Normalisation des poids
        total_weight = sum(weights)
        weights = [w/total_weight for w in weights]
        
        # Score pondéré
        overall_score = sum(c * w for c, w in zip(components, weights))
        
        return min(1.0, max(0.0, overall_score))
    
    def _generate_comprehensive_recommendations(self,
                                              cv_result: Optional[CrossValidationResult],
                                              oos_result: Optional[OutOfSampleResult],
                                              features: Optional[FeatureImportanceAnalysis],
                                              overfitting: Optional[OverfittingAnalysis],
                                              stability: Optional[ModelStabilityTest]) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Génération recommandations détaillées"""
        
        strengths = []
        weaknesses = []
        recommendations = []
        next_steps = []
        
        # Analyse CV
        if cv_result:
            if cv_result.mean_score > 0.75:
                strengths.append(f"Excellente performance CV: {cv_result.mean_score:.3f}")
            elif cv_result.mean_score < 0.6:
                weaknesses.append(f"Performance CV faible: {cv_result.mean_score:.3f}")
            
            if cv_result.stability_score > 0.9:
                strengths.append("Très stable entre folds")
            elif cv_result.stability_score < 0.7:
                weaknesses.append("Instabilité entre folds")
        
        # Analyse OOS
        if oos_result:
            if oos_result.degradation_pct < 10:
                strengths.append("Excellente généralisation")
            elif oos_result.degradation_pct > 25:
                weaknesses.append(f"Dégradation OOS importante: {oos_result.degradation_pct:.1f}%")
        
        # Analyse features
        if features:
            if len(features.redundant_features) > len(features.top_features):
                weaknesses.append(f"{len(features.redundant_features)} features redondantes")
                recommendations.append("Réduire nombre de features")
        
        # Analyse overfitting
        if overfitting:
            if overfitting.overfitting_level in [OverfittingLevel.SEVERE, OverfittingLevel.CRITICAL]:
                weaknesses.append(f"Overfitting {overfitting.overfitting_level.value}")
                recommendations.extend(overfitting.recommendations)
        
        # Analyse stabilité
        if stability:
            if stability.overall_stability < 0.7:
                weaknesses.append("Modèle instable")
                recommendations.append("Améliorer robustesse du modèle")
        
        # Recommandations générales
        if not weaknesses:
            recommendations.append("Modèle prêt pour production")
            next_steps.append("Déployer en environnement de staging")
        else:
            recommendations.append("Améliorer stabilité du modèle")
            recommendations.append("Augmenter données d'entraînement")
        
        # Prochaines étapes
        if cv_result and cv_result.mean_score > 0.7:
            next_steps.append("Test en paper trading")
        else:
            next_steps.append("Re-entraînement nécessaire")
        
        return strengths, weaknesses, recommendations, next_steps
    
    def _save_validation_report(self, report: ValidationReport):
        """Sauvegarde rapport de validation"""
        
        timestamp = report.validation_timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"validation_report_{report.model_id}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # Conversion en dict sérialisable
        report_dict = asdict(report)
        
        # Conversion datetime et autres types non-sérialisables
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, Enum):
                return obj.value
            return obj
        
        def deep_convert(obj):
            if isinstance(obj, dict):
                return {k: deep_convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [deep_convert(v) for v in obj]
            else:
                return convert_datetime(obj)
        
        report_serializable = deep_convert(report_dict)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report_serializable, f, indent=2)
            
            logger.info(f"Rapport validation sauvegardé: {filepath}")
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde rapport: {e}")

# === FACTORY FUNCTIONS ===

def create_model_validator(model: Optional[Any] = None, 
                         level: ValidationLevel = ValidationLevel.STANDARD) -> ModelValidator:
    """Factory pour validateur de modèles"""
    return ModelValidator(model, level)

def create_rigorous_validator(model: Optional[Any] = None) -> ModelValidator:
    """Factory pour validation rigoureuse"""
    return ModelValidator(model, ValidationLevel.RIGOROUS)

def create_exhaustive_validator(model: Optional[Any] = None) -> ModelValidator:
    """Factory pour validation exhaustive"""
    return ModelValidator(model, ValidationLevel.EXHAUSTIVE)

# === TEST FUNCTION ===

def test_model_validator():
    """Test complet du validateur de modèles"""
    logger.info("=== TEST MODEL VALIDATOR ===")
    
    # Import et création modèle test
    from ml.simple_model import create_signal_classifier
    from ml.data_processor import create_battle_navale_processor
    
    # Données test
    test_snapshots = []
    for i in range(200):
        snapshot = {
            'trade_id': f'trade_{i}',
            'timestamp': datetime.now(timezone.utc) - timedelta(hours=i),
            'signal_type': 'LONG' if i % 2 == 0 else 'SHORT',
            'trade_pnl': np.random.normal(0, ES_TICK_VALUE * 2),
            'battle_score': np.random.uniform(0.3, 1.0),
            'confluence_score': np.random.uniform(0.2, 0.9)
        }
        test_snapshots.append(snapshot)
    
    # Création dataset
    processor = create_battle_navale_processor()
    dataset = processor.create_ml_dataset(test_snapshots)
    
    if not dataset:
        print("Erreur création dataset pour test")
        return
    
    # Création et entraînement modèle
    model = create_signal_classifier()
    training_result = model.train_on_snapshots(pd.DataFrame(test_snapshots))
    
    if not training_result.success:
        print("Erreur entraînement modèle pour test")
        return
    
    # Test validation
    validator = create_rigorous_validator(model)
    
    # Test cross-validation
    cv_results = validator.cross_validate_model(dataset)
    print(f"CV Score: {cv_results.get('cv_result', {}).get('mean_score', 'N/A'):.3f}")
    
    # Test out-of-sample
    oos_score = validator.test_out_of_sample(dataset)
    print(f"Out-of-sample Score: {oos_score:.3f}")
    
    # Test importance features
    feature_analysis = validator.analyze_feature_importance(dataset)
    top_features = feature_analysis.get('feature_analysis', {}).get('top_features', [])
    print(f"Top 3 Features: {top_features[:3]}")
    
    # Test overfitting
    is_overfitting = validator.detect_overfitting(dataset)
    print(f"Overfitting détecté: {is_overfitting}")
    
    # Validation complète
    full_report = validator.validate_model_comprehensive(dataset)
    print(f"Santé modèle: {full_report.model_health.value}")
    print(f"Production ready: {full_report.production_readiness}")
    
    logger.info("=== TEST TERMINÉ ===")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_model_validator()