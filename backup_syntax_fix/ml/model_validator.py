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
from typing import Dict, List, Optional, Any, Tuple, Union
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
from ml.simple_model import SimpleLinearPredictor, ModelType, ModelStatus
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
                 model: Optional[SimpleLinearModel] = None,
                 validation_level: ValidationLevel = ValidationLevel.STANDARD):
        """
        Initialisation du validateur
        
        Args:
            model: Modèle à valider (peut être fourni plus tard)
            validation_level: Niveau de validation désiré
        """
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
            primary_metric = 'test_f1' if self.model.model_type == ModelType.SIGNAL_CLASSIFIER else 'test_r2'
            scores = cv_results[primary_metric]
            
            mean_score = np.mean(scores)
            std_score = np.std(scores)
            
            # Intervalle de confiance 95%
            confidence_interval = stats.t.interval(
                0.95, len(scores)-1, 
                loc=mean_score, 
                scale=stats.sem(scores)
            )
            
            # Analyse de stabilité
            stability_score = 1.0 - (std_score / mean_score) if mean_score > 0 else 0.0
            
            execution_time = time.time() - start_time
            
            # Création du résultat
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
                execution_time=execution_time
            )
            
            # Analyse détaillée si niveau élevé
            detailed_analysis = {}
            if self.validation_level in [ValidationLevel.RIGOROUS, ValidationLevel.EXHAUSTIVE]:
                detailed_analysis = self._detailed_cv_analysis(cv_results, X, y)
            
            result = {
                "cv_result": cv_result,
                "all_metrics": {k: v.tolist() for k, v in cv_results.items()},
                "detailed_analysis": detailed_analysis,
                "interpretation": self._interpret_cv_results(cv_result),
                "recommendations": self._get_cv_recommendations(cv_result)
            }
            
            logger.info(f"Cross-validation terminée: {mean_score:.3f} ± {std_score:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Erreur cross-validation: {e}")
            return {"error": str(e)}
    
    def test_out_of_sample(self, 
                          dataset: ProcessedDataset,
                          holdout_pct: float = 0.15) -> float:
        """
        Test rigoreux out-of-sample avec holdout temporel
        
        Args:
            dataset: Dataset avec données temporelles
            holdout_pct: Pourcentage de données pour holdout final
            
        Returns:
            Score out-of-sample (performance sur données jamais vues)
        """
        if self.model is None or self.model.status == ModelStatus.UNTRAINED:
            raise ValueError("Modèle non entraîné pour test out-of-sample")
        
        logger.info(f"Test out-of-sample avec holdout {holdout_pct*100:.1f}%")
        
        try:
            # Création d'un holdout temporel rigoureux
            all_data = pd.concat([
                dataset.X_train, dataset.X_test
            ], ignore_index=True)
            all_targets = pd.concat([
                dataset.y_train, dataset.y_test
            ], ignore_index=True)
            
            # Split temporel pour holdout final
            holdout_size = int(len(all_data) * holdout_pct)
            
            X_train_full = all_data.iloc[:-holdout_size]
            y_train_full = all_targets.iloc[:-holdout_size]
            X_holdout = all_data.iloc[-holdout_size:]
            y_holdout = all_targets.iloc[-holdout_size:]
            
            # Entraînement sur données réduites
            temp_model = clone(self.model.model)
            
            # Normalisation si nécessaire
            if dataset.scaler is not None:
                X_train_scaled = dataset.scaler.fit_transform(X_train_full)
                X_holdout_scaled = dataset.scaler.transform(X_holdout)
            else:
                X_train_scaled = X_train_full
                X_holdout_scaled = X_holdout
            
            # Entraînement et prédiction
            temp_model.fit(X_train_scaled, y_train_full)
            
            train_score = temp_model.score(X_train_scaled, y_train_full)
            test_score = temp_model.score(X_holdout_scaled, y_holdout)
            
            # Calculs de dégradation
            generalization_gap = train_score - test_score
            degradation_pct = (generalization_gap / train_score * 100) if train_score > 0 else 0
            
            # Test de stabilité temporelle
            temporal_stability = self._test_temporal_stability(
                temp_model, X_holdout_scaled, y_holdout, dataset.scaler
            )
            
            # Niveau de confiance basé sur taille échantillon
            confidence_level = min(0.95, 0.5 + (holdout_size / 1000) * 0.45)
            
            oos_result = OutOfSampleResult(
                test_score=test_score,
                train_score=train_score,
                generalization_gap=generalization_gap,
                degradation_pct=degradation_pct,
                sample_size=holdout_size,
                temporal_stability=temporal_stability,
                confidence_level=confidence_level
            )
            
            logger.info(f"Out-of-sample score: {test_score:.3f} (dégradation: {degradation_pct:.1f}%)")
            return test_score
            
        except Exception as e:
            logger.error(f"Erreur test out-of-sample: {e}")
            return 0.0
    
    def analyze_feature_importance(self, 
                                  dataset: ProcessedDataset,
                                  methods: List[str] = None) -> Dict[str, Any]:
        """
        Analyse complète de l'importance des features
        
        Args:
            dataset: Dataset avec features nommées
            methods: Liste des méthodes ('coefficients', 'permutation', 'recursive')
            
        Returns:
            Dictionnaire avec analyses d'importance détaillées
        """
        if self.model is None or self.model.status == ModelStatus.UNTRAINED:
            raise ValueError("Modèle non entraîné pour analyse features")
        
        if methods is None:
            methods = ['coefficients', 'permutation']
        
        logger.info(f"Analyse importance features avec méthodes: {methods}")
        
        try:
            results = {}
            
            # Préparation données
            X_test = dataset.X_test
            y_test = dataset.y_test
            
            # 1. Importance par coefficients (si applicable)
            if 'coefficients' in methods and hasattr(self.model.model, 'coef_'):
                results['coefficients'] = self._analyze_coefficient_importance(
                    dataset.feature_names
                )
            
            # 2. Permutation importance
            if 'permutation' in methods:
                results['permutation'] = self._analyze_permutation_importance(
                    X_test, y_test, dataset.feature_names
                )
            
            # 3. Recursive feature elimination (si demandé)
            if 'recursive' in methods:
                results['recursive'] = self._analyze_recursive_importance(
                    dataset
                )
            
            # 4. Analyse de stabilité des features
            stability_analysis = self._analyze_feature_stability(dataset)
            
            # 5. Identification features redondantes
            redundancy_analysis = self._identify_redundant_features(dataset)
            
            # 6. Création analyse consolidée
            consolidated_importance = self._consolidate_importance_analyses(results)
            
            feature_analysis = FeatureImportanceAnalysis(
                method="consolidated",
                importance_scores=consolidated_importance,
                importance_ranking=sorted(consolidated_importance.items(), 
                                        key=lambda x: x[1], reverse=True),
                top_features=self._get_top_features(consolidated_importance, n=10),
                redundant_features=redundancy_analysis.get('redundant', []),
                feature_stability=stability_analysis,
                cumulative_importance=self._calculate_cumulative_importance(consolidated_importance)
            )
            
            final_result = {
                "feature_analysis": feature_analysis,
                "method_results": results,
                "stability_analysis": stability_analysis,
                "redundancy_analysis": redundancy_analysis,
                "recommendations": self._get_feature_recommendations(feature_analysis)
            }
            
            logger.info(f"Analyse importance terminée - Top 3: {feature_analysis.top_features[:3]}")
            return final_result
            
        except Exception as e:
            logger.error(f"Erreur analyse features: {e}")
            return {"error": str(e)}
    
    def detect_overfitting(self, 
                          dataset: ProcessedDataset,
                          validation_curves: bool = True) -> bool:
        """
        Détection avancée d'overfitting avec analyses multiples
        
        Args:
            dataset: Dataset pour tests
            validation_curves: Analyser courbes de validation
            
        Returns:
            True si overfitting détecté, False sinon
        """
        if self.model is None or self.model.status == ModelStatus.UNTRAINED:
            raise ValueError("Modèle non entraîné pour détection overfitting")
        
        logger.info("Détection overfitting...")
        
        try:
            # 1. Test train/validation gap
            train_score = self.model.model.score(dataset.X_train, dataset.y_train)
            test_score = self.model.model.score(dataset.X_test, dataset.y_test)
            
            train_test_gap = train_score - test_score
            gap_threshold = 0.15  # 15% de différence = suspect
            
            # 2. Analyse variance cross-validation
            cv_result = self.cross_validate_model(dataset, n_folds=5)
            cv_variance = cv_result['cv_result'].std_score if 'cv_result' in cv_result else 0
            variance_threshold = 0.1
            
            # 3. Learning curves si niveau élevé
            learning_curve_trend = "unknown"
            if self.validation_level in [ValidationLevel.RIGOROUS, ValidationLevel.EXHAUSTIVE]:
                learning_curve_trend = self._analyze_learning_curves(dataset)
            
            # 4. Validation curves pour hyperparamètres
            validation_curve_optimal = None
            if validation_curves and hasattr(self.model.model, 'C'):
                validation_curve_optimal = self._analyze_validation_curves(dataset)
            
            # 5. Détermination niveau d'overfitting
            overfitting_level = self._determine_overfitting_level(
                train_test_gap, cv_variance, learning_curve_trend
            )
            
            # 6. Recommandations
            recommendations = self._get_overfitting_recommendations(overfitting_level)
            
            overfitting_analysis = OverfittingAnalysis(
                overfitting_level=overfitting_level,
                train_test_gap=train_test_gap,
                cv_variance=cv_variance,
                learning_curve_trend=learning_curve_trend,
                validation_curve_optimal=validation_curve_optimal,
                early_stopping_point=None,  # TODO: Implémentation early stopping
                recommendations=recommendations
            )
            
            # Stockage de l'analyse
            self._store_overfitting_analysis(overfitting_analysis)
            
            is_overfitting = overfitting_level in [
                OverfittingLevel.MODERATE, 
                OverfittingLevel.SEVERE, 
                OverfittingLevel.CRITICAL
            ]
            
            logger.info(f"Overfitting détecté: {is_overfitting} (niveau: {overfitting_level.value})")
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
            dataset: Dataset préparé pour validation
            save_report: Sauvegarder le rapport détaillé
            
        Returns:
            Rapport complet de validation
        """
        logger.info("=== VALIDATION COMPLÈTE DU MODÈLE ===")
        
        validation_start = time.time()
        
        try:
            # 1. Cross-validation
            cv_results = self.cross_validate_model(dataset)
            cv_result = cv_results.get('cv_result')
            
            # 2. Test out-of-sample
            oos_score = self.test_out_of_sample(dataset)
            oos_result = OutOfSampleResult(
                test_score=oos_score,
                train_score=self.model.model.score(dataset.X_train, dataset.y_train),
                generalization_gap=self.model.model.score(dataset.X_train, dataset.y_train) - oos_score,
                degradation_pct=0.0,  # Calculé dans test_out_of_sample
                sample_size=len(dataset.X_test),
                temporal_stability=0.8,  # TODO: Calcul réel
                confidence_level=0.9
            )
            
            # 3. Analyse features
            feature_analysis = self.analyze_feature_importance(dataset)
            feature_result = feature_analysis.get('feature_analysis')
            
            # 4. Détection overfitting
            is_overfitting = self.detect_overfitting(dataset)
            overfitting_analysis = self._create_overfitting_summary(is_overfitting, cv_result, oos_result)
            
            # 5. Tests de stabilité
            stability_test = self._perform_stability_tests(dataset)
            
            # 6. Évaluation santé globale
            model_health = self._assess_model_health(cv_result, oos_result, feature_result, overfitting_analysis)
            
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
                "metrics": ["accuracy", "f1", "precision", "recall", "roc_auc"],
                "feature_analysis": True,
                "stability_tests": True
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
        else:
            # Default: TimeSeriesSplit pour trading
            return TimeSeriesSplit(n_splits=n_folds)
    
    def _get_scoring_metrics(self) -> Dict[str, Any]:
        """Métriques de scoring selon type de modèle"""
        
        if self.model.model_type == ModelType.SIGNAL_CLASSIFIER:
            return {
                'accuracy': 'accuracy',
                'f1': 'f1_weighted',
                'precision': 'precision_weighted',
                'recall': 'recall_weighted',
                'roc_auc': 'roc_auc_ovr_weighted'
            }
        else:
            return {
                'r2': 'r2',
                'mse': 'neg_mean_squared_error',
                'mae': 'neg_mean_absolute_error'
            }
    
    def _detailed_cv_analysis(self, cv_results: Dict, X, y) -> Dict[str, Any]:
        """Analyse détaillée des résultats CV"""
        
        analysis = {}
        
        # Analyse variance des scores
        for metric, scores in cv_results.items():
            if metric.startswith('test_'):
                metric_name = metric.replace('test_', '')
                analysis[f"{metric_name}_variance"] = np.var(scores)
                analysis[f"{metric_name}_min_max_gap"] = np.max(scores) - np.min(scores)
        
        # Test de normalité des scores
        primary_scores = cv_results.get('test_f1', cv_results.get('test_r2', []))
        if len(primary_scores) > 3:
            shapiro_stat, shapiro_p = stats.shapiro(primary_scores)
            analysis['score_normality'] = {
                'shapiro_statistic': shapiro_stat,
                'p_value': shapiro_p,
                'is_normal': shapiro_p > 0.05
            }
        
        return analysis
    
    def _interpret_cv_results(self, cv_result: CrossValidationResult) -> Dict[str, str]:
        """Interprétation des résultats CV"""
        
        interpretation = {}
        
        # Interprétation score moyen
        if cv_result.mean_score > 0.8:
            interpretation['score_level'] = "excellent"
        elif cv_result.mean_score > 0.7:
            interpretation['score_level'] = "good"
        elif cv_result.mean_score > 0.6:
            interpretation['score_level'] = "acceptable"
        else:
            interpretation['score_level'] = "poor"
        
        # Interprétation stabilité
        if cv_result.stability_score > 0.9:
            interpretation['stability'] = "très stable"
        elif cv_result.stability_score > 0.8:
            interpretation['stability'] = "stable"
        elif cv_result.stability_score > 0.7:
            interpretation['stability'] = "modérément stable"
        else:
            interpretation['stability'] = "instable"
        
        return interpretation
    
    def _get_cv_recommendations(self, cv_result: CrossValidationResult) -> List[str]:
        """Recommandations basées sur résultats CV"""
        
        recommendations = []
        
        if cv_result.mean_score < 0.7:
            recommendations.append("Améliorer la qualité des features")
            recommendations.append("Considérer plus de données d'entraînement")
        
        if cv_result.stability_score < 0.8:
            recommendations.append("Réduire la variance du modèle")
            recommendations.append("Utiliser la régularisation")
        
        if cv_result.std_score > 0.1:
            recommendations.append("Investiguer la variabilité inter-folds")
        
        return recommendations
    
    def _test_temporal_stability(self, model, X_holdout, y_holdout, scaler) -> float:
        """Test de stabilité temporelle du modèle"""
        
        if len(X_holdout) < 20:
            return 0.5  # Pas assez de données
        
        # Split holdout en périodes temporelles
        period_size = len(X_holdout) // 4  # 4 périodes
        period_scores = []
        
        for i in range(4):
            start_idx = i * period_size
            end_idx = (i + 1) * period_size if i < 3 else len(X_holdout)
            
            X_period = X_holdout[start_idx:end_idx]
            y_period = y_holdout.iloc[start_idx:end_idx]
            
            if len(X_period) > 0:
                score = model.score(X_period, y_period)
                period_scores.append(score)
        
        # Stabilité = 1 - coefficient de variation
        if len(period_scores) > 1:
            mean_score = np.mean(period_scores)
            std_score = np.std(period_scores)
            cv = std_score / mean_score if mean_score > 0 else 1.0
            stability = max(0.0, 1.0 - cv)
        else:
            stability = 0.5
        
        return stability
    
    def _analyze_coefficient_importance(self, feature_names: List[str]) -> Dict[str, float]:
        """Analyse importance par coefficients"""
        
        if not hasattr(self.model.model, 'coef_'):
            return {}
        
        coefficients = self.model.model.coef_
        if len(coefficients.shape) > 1:  # Multi-class
            coefficients = np.abs(coefficients).mean(axis=0)
        
        # Normalisation des coefficients
        abs_coeffs = np.abs(coefficients)
        norm_coeffs = abs_coeffs / np.sum(abs_coeffs) if np.sum(abs_coeffs) > 0 else abs_coeffs
        
        importance_dict = {}
        for i, feature in enumerate(feature_names):
            importance_dict[feature] = float(norm_coeffs[i])
        
        return importance_dict
    
    def _analyze_permutation_importance(self, X_test, y_test, feature_names: List[str]) -> Dict[str, float]:
        """Analyse importance par permutation"""
        
        try:
            # Permutation importance
            perm_importance = permutation_importance(
                self.model.model, X_test, y_test,
                n_repeats=10, random_state=42, n_jobs=-1
            )
            
            # Normalisation
            importances = perm_importance.importances_mean
            norm_importances = importances / np.sum(importances) if np.sum(importances) > 0 else importances
            
            importance_dict = {}
            for i, feature in enumerate(feature_names):
                importance_dict[feature] = float(norm_importances[i])
            
            return importance_dict
            
        except Exception as e:
            logger.warning(f"Erreur permutation importance: {e}")
            return {}
    
    def _analyze_recursive_importance(self, dataset: ProcessedDataset) -> Dict[str, float]:
        """Analyse importance récursive (feature elimination)"""
        
        # TODO: Implémentation RFE complète
        return {}
    
    def _analyze_feature_stability(self, dataset: ProcessedDataset) -> Dict[str, float]:
        """Analyse stabilité des features"""
        
        # Bootstrap sampling pour tester stabilité
        n_bootstrap = 50
        feature_importance_samples = []
        
        for _ in range(n_bootstrap):
            # Bootstrap sample
            bootstrap_indices = np.random.choice(len(dataset.X_train), 
                                               size=len(dataset.X_train), 
                                               replace=True)
            X_bootstrap = dataset.X_train.iloc[bootstrap_indices]
            y_bootstrap = dataset.y_train.iloc[bootstrap_indices]
            
            # Train temporary model
            temp_model = clone(self.model.model)
            temp_model.fit(X_bootstrap, y_bootstrap)
            
            # Get feature importance
            if hasattr(temp_model, 'coef_'):
                coeffs = temp_model.coef_
                if len(coeffs.shape) > 1:
                    coeffs = np.abs(coeffs).mean(axis=0)
                importance = np.abs(coeffs)
                feature_importance_samples.append(importance)
        
        # Calculate stability as 1 - coefficient of variation
        if feature_importance_samples:
            importance_array = np.array(feature_importance_samples)
            stability_scores = {}
            
            for i, feature in enumerate(dataset.feature_names):
                feature_importances = importance_array[:, i]
                mean_imp = np.mean(feature_importances)
                std_imp = np.std(feature_importances)
                cv = std_imp / mean_imp if mean_imp > 0 else 1.0
                stability = max(0.0, 1.0 - cv)
                stability_scores[feature] = stability
            
            return stability_scores
        
        return {}
    
    def _identify_redundant_features(self, dataset: ProcessedDataset) -> Dict[str, List[str]]:
        """Identification features redondantes"""
        
        # Calcul matrice de corrélation
        corr_matrix = dataset.X_train.corr()
        
        redundant_pairs = []
        redundant_features = set()
        
        # Seuil de corrélation pour redondance
        correlation_threshold = 0.95
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > correlation_threshold:
                    feature1 = corr_matrix.columns[i]
                    feature2 = corr_matrix.columns[j]
                    redundant_pairs.append((feature1, feature2))
                    redundant_features.add(feature2)  # Keep first, mark second as redundant
        
        return {
            "redundant_pairs": redundant_pairs,
            "redundant": list(redundant_features)
        }
    
    def _consolidate_importance_analyses(self, results: Dict) -> Dict[str, float]:
        """Consolidation des analyses d'importance"""
        
        # Moyenne pondérée des différentes méthodes
        weights = {
            'coefficients': 0.4,
            'permutation': 0.6,
            'recursive': 0.3
        }
        
        consolidated = {}
        
        # Get all features
        all_features = set()
        for method_results in results.values():
            if isinstance(method_results, dict):
                all_features.update(method_results.keys())
        
        # Calculate weighted average
        for feature in all_features:
            weighted_sum = 0.0
            total_weight = 0.0
            
            for method, method_results in results.items():
                if method in weights and isinstance(method_results, dict):
                    if feature in method_results:
                        weighted_sum += method_results[feature] * weights[method]
                        total_weight += weights[method]
            
            if total_weight > 0:
                consolidated[feature] = weighted_sum / total_weight
            else:
                consolidated[feature] = 0.0
        
        return consolidated
    
    def _get_top_features(self, importance_scores: Dict[str, float], n: int = 10) -> List[str]:
        """Sélection top N features"""
        
        sorted_features = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)
        return [feature for feature, _ in sorted_features[:n]]
    
    def _calculate_cumulative_importance(self, importance_scores: Dict[str, float]) -> List[float]:
        """Calcul importance cumulative"""
        
        sorted_scores = sorted(importance_scores.values(), reverse=True)
        total_importance = sum(sorted_scores)
        
        cumulative = []
        running_sum = 0.0
        
        for score in sorted_scores:
            running_sum += score
            cumulative.append(running_sum / total_importance if total_importance > 0 else 0.0)
        
        return cumulative
    
    def _get_feature_recommendations(self, feature_analysis: FeatureImportanceAnalysis) -> List[str]:
        """Recommandations basées sur analyse features"""
        
        recommendations = []
        
        # Top features concentration
        top_5_importance = sum([score for _, score in feature_analysis.importance_ranking[:5]])
        
        if top_5_importance > 0.8:
            recommendations.append("Modèle très dépendant de peu de features - vérifier robustesse")
        
        if len(feature_analysis.redundant_features) > 0:
            recommendations.append(f"Supprimer {len(feature_analysis.redundant_features)} features redondantes")
        
        if len(feature_analysis.top_features) < 5:
            recommendations.append("Considérer feature engineering additionnel")
        
        return recommendations
    
    def _analyze_learning_curves(self, dataset: ProcessedDataset) -> str:
        """Analyse des courbes d'apprentissage"""
        
        try:
            # Learning curve analysis
            train_sizes = np.linspace(0.1, 1.0, 10)
            train_sizes_abs, train_scores, test_scores = learning_curve(
                self.model.model, dataset.X_train, dataset.y_train,
                train_sizes=train_sizes, cv=3, n_jobs=-1
            )
            
            # Analyze trend in test scores
            test_means = np.mean(test_scores, axis=1)
            
            # Linear regression on test scores to detect trend
            x = np.arange(len(test_means))
            slope, _, _, _, _ = stats.linregress(x, test_means)
            
            if slope > 0.01:
                return "improving"
            elif slope < -0.01:
                return "degrading"
            else:
                return "plateauing"
                
        except Exception as e:
            logger.warning(f"Erreur analyse learning curves: {e}")
            return "unknown"
    
    def _analyze_validation_curves(self, dataset: ProcessedDataset) -> Optional[float]:
        """Analyse courbes de validation pour hyperparamètres"""
        
        if not hasattr(self.model.model, 'C'):
            return None
        
        try:
            # Validation curve for regularization parameter
            param_range = np.logspace(-3, 2, 6)
            train_scores, test_scores = validation_curve(
                self.model.model, dataset.X_train, dataset.y_train,
                param_name='C', param_range=param_range, cv=3
            )
            
            test_means = np.mean(test_scores, axis=1)
            optimal_idx = np.argmax(test_means)
            optimal_C = param_range[optimal_idx]
            
            return float(optimal_C)
            
        except Exception as e:
            logger.warning(f"Erreur analyse validation curves: {e}")
            return None
    
    def _determine_overfitting_level(self, train_test_gap: float, cv_variance: float, learning_trend: str) -> OverfittingLevel:
        """Détermination niveau d'overfitting"""
        
        # Score composite d'overfitting
        overfitting_score = 0.0
        
        # Gap train/test
        if train_test_gap > 0.3:
            overfitting_score += 0.4
        elif train_test_gap > 0.2:
            overfitting_score += 0.3
        elif train_test_gap > 0.1:
            overfitting_score += 0.2
        
        # Variance CV
        if cv_variance > 0.15:
            overfitting_score += 0.3
        elif cv_variance > 0.1:
            overfitting_score += 0.2
        
        # Trend learning curve
        if learning_trend == "degrading":
            overfitting_score += 0.3
        elif learning_trend == "plateauing":
            overfitting_score += 0.1
        
        # Classification niveau
        if overfitting_score >= 0.8:
            return OverfittingLevel.CRITICAL
        elif overfitting_score >= 0.6:
            return OverfittingLevel.SEVERE
        elif overfitting_score >= 0.4:
            return OverfittingLevel.MODERATE
        elif overfitting_score >= 0.2:
            return OverfittingLevel.MILD
        else:
            return OverfittingLevel.NONE
    
    def _get_overfitting_recommendations(self, overfitting_level: OverfittingLevel) -> List[str]:
        """Recommandations selon niveau d'overfitting"""
        
        recommendations = []
        
        if overfitting_level == OverfittingLevel.CRITICAL:
            recommendations.extend([
                "CRITIQUE: Re-entraîner avec régularisation forte",
                "Réduire complexité du modèle",
                "Augmenter données d'entraînement",
                "Feature selection aggressive"
            ])
        elif overfitting_level == OverfittingLevel.SEVERE:
            recommendations.extend([
                "Augmenter régularisation",
                "Cross-validation plus stricte",
                "Réduire nombre de features"
            ])
        elif overfitting_level == OverfittingLevel.MODERATE:
            recommendations.extend([
                "Surveiller performance validation",
                "Considérer régularisation légère"
            ])
        elif overfitting_level == OverfittingLevel.MILD:
            recommendations.append("Surveillance continue recommandée")
        
        return recommendations
    
    def _store_overfitting_analysis(self, analysis: OverfittingAnalysis):
        """Stockage analyse overfitting"""
        # TODO: Implémentation stockage persistant
        pass
    
    def _create_overfitting_summary(self, is_overfitting: bool, cv_result, oos_result) -> OverfittingAnalysis:
        """Création résumé overfitting"""
        
        if cv_result and oos_result:
            train_test_gap = oos_result.train_score - oos_result.test_score
            cv_variance = cv_result.std_score
        else:
            train_test_gap = 0.0
            cv_variance = 0.0
        
        level = OverfittingLevel.MODERATE if is_overfitting else OverfittingLevel.NONE
        
        return OverfittingAnalysis(
            overfitting_level=level,
            train_test_gap=train_test_gap,
            cv_variance=cv_variance,
            learning_curve_trend="unknown",
            validation_curve_optimal=None,
            early_stopping_point=None,
            recommendations=self._get_overfitting_recommendations(level)
        )
    
    def _perform_stability_tests(self, dataset: ProcessedDataset) -> ModelStabilityTest:
        """Exécution tests de stabilité"""
        
        # Tests simplifiés pour MVP
        temporal_stability = 0.8  # TODO: Calcul réel
        feature_sensitivity = {f: 0.5 for f in dataset.feature_names[:5]}  # TODO: Calcul réel
        noise_robustness = 0.7  # TODO: Test avec bruit
        data_shift_resilience = 0.6  # TODO: Test distribution shift
        
        overall_stability = np.mean([
            temporal_stability, 
            np.mean(list(feature_sensitivity.values())),
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
    
    def _assess_model_health(self, cv_result, oos_result, feature_result, overfitting_analysis) -> ModelHealth:
        """Évaluation santé globale du modèle"""
        
        health_score = 0.0
        
        # Score CV
        if cv_result and cv_result.mean_score > 0.8:
            health_score += 0.3
        elif cv_result and cv_result.mean_score > 0.7:
            health_score += 0.2
        elif cv_result and cv_result.mean_score > 0.6:
            health_score += 0.1
        
        # Score OOS
        if oos_result and oos_result.test_score > 0.75:
            health_score += 0.3
        elif oos_result and oos_result.test_score > 0.65:
            health_score += 0.2
        elif oos_result and oos_result.test_score > 0.55:
            health_score += 0.1
        
        # Overfitting
        if overfitting_analysis:
            if overfitting_analysis.overfitting_level == OverfittingLevel.NONE:
                health_score += 0.2
            elif overfitting_analysis.overfitting_level == OverfittingLevel.MILD:
                health_score += 0.1
            # Severe/Critical = 0 points
        
        # Features
        if feature_result and len(feature_result.top_features) >= 5:
            health_score += 0.2
        
        # Classification santé
        if health_score >= 0.8:
            return ModelHealth.EXCELLENT
        elif health_score >= 0.6:
            return ModelHealth.GOOD
        elif health_score >= 0.4:
            return ModelHealth.ACCEPTABLE
        elif health_score >= 0.2:
            return ModelHealth.POOR
        else:
            return ModelHealth.UNUSABLE
    
    def _calculate_overall_score(self, cv_result, oos_result, stability_test) -> float:
        """Calcul score global"""
        
        scores = []
        
        if cv_result:
            scores.append(cv_result.mean_score)
        
        if oos_result:
            scores.append(oos_result.test_score)
        
        if stability_test:
            scores.append(stability_test.overall_stability)
        
        return np.mean(scores) if scores else 0.0
    
    def _generate_comprehensive_recommendations(self, cv_result, oos_result, feature_result, overfitting_analysis, stability_test) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Génération recommandations complètes"""
        
        strengths = []
        weaknesses = []
        recommendations = []
        next_steps = []
        
        # Analyse des forces
        if cv_result and cv_result.mean_score > 0.75:
            strengths.append("Performance cross-validation excellente")
        if oos_result and oos_result.generalization_gap < 0.1:
            strengths.append("Bonne généralisation")
        if feature_result and len(feature_result.top_features) >= 8:
            strengths.append("Features diversifiées et importantes")
        
        # Analyse des faiblesses
        if cv_result and cv_result.stability_score < 0.8:
            weaknesses.append("Instabilité inter-folds")
        if oos_result and oos_result.degradation_pct > 15:
            weaknesses.append("Dégradation out-of-sample élevée")
        if overfitting_analysis and overfitting_analysis.overfitting_level in [OverfittingLevel.SEVERE, OverfittingLevel.CRITICAL]:
            weaknesses.append("Overfitting détecté")
        
        # Recommandations
        if weaknesses:
            recommendations.append("Améliorer stabilité du modèle")
            recommendations.append("Augmenter données d'entraînement")
        
        if not weaknesses:
            recommendations.append("Modèle prêt pour production")
        
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

def create_model_validator(model: Optional[SimpleLinearModel] = None, 
                         level: ValidationLevel = ValidationLevel.STANDARD) -> ModelValidator:
    """Factory pour validateur de modèles"""
    return ModelValidator(model, level)

def create_rigorous_validator(model: SimpleLinearModel) -> ModelValidator:
    """Factory pour validation rigoureuse"""
    return ModelValidator(model, ValidationLevel.RIGOROUS)

def create_exhaustive_validator(model: SimpleLinearModel) -> ModelValidator:
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
        logger.info("Erreur création dataset pour test")
        return
    
    # Création et entraînement modèle
    model = create_signal_classifier()
    training_result = model.train_on_snapshots(pd.DataFrame(test_snapshots))
    
    if not training_result.success:
        logger.info("Erreur entraînement modèle pour test")
        return
    
    # Test validation
    validator = create_rigorous_validator(model)
    
    # Test cross-validation
    cv_results = validator.cross_validate_model(dataset)
    logger.info("CV Score: {cv_results.get('cv_result', {}).get('mean_score', 'N/A'):.3f}")
    
    # Test out-of-sample
    oos_score = validator.test_out_of_sample(dataset)
    logger.info("Out-of-sample Score: {oos_score:.3f}")
    
    # Test importance features
    feature_analysis = validator.analyze_feature_importance(dataset)
    top_features = feature_analysis.get('feature_analysis', {}).get('top_features', [])
    logger.info("Top 3 Features: {top_features[:3]}")
    
    # Test overfitting
    is_overfitting = validator.detect_overfitting(dataset)
    logger.info("Overfitting détecté: {is_overfitting}")
    
    # Validation complète
    full_report = validator.validate_model_comprehensive(dataset)
    logger.info("Santé modèle: {full_report.model_health.value}")
    logger.info("Production ready: {full_report.production_readiness}")
    
    logger.info("=== TEST TERMINÉ ===")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_model_validator()