#!/usr/bin/env python3
"""
ml/simple_model.py

MODÈLE ML LINÉAIRE SIMPLE - OBJECTIF PRIORITÉ 6
Intégration parfaite avec architecture Battle Navale existante
Focus : Signal quality prediction via Linear Regression simple

FONCTIONNALITÉS :
1. Training sur snapshots Battle Navale
2. Prédiction qualité signal (0-1 score) 
3. Validation robuste performance
4. Update incrémental weights
5. Export/Import modèle trained
6. Métriques performance détaillées

ARCHITECTURE : Simple first, efficace, production-ready
"""

# === STDLIB ===
import os
import time
from core.logger import get_logger
import pickle
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from datetime import datetime, timezone
from enum import Enum

# === THIRD-PARTY ===
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score,
    classification_report, confusion_matrix
)
import joblib

# === LOCAL IMPORTS (respectant hiérarchie) ===
from config import get_automation_config, get_trading_config
from core.base_types import (
    MarketData, TradingSignal, SignalType, SignalStrength,
    TradeResult, ES_TICK_SIZE, ES_TICK_VALUE
)

# Logger
logger = get_logger(__name__)

# === ML MODEL ENUMS ===

class ModelType(Enum):
    """Types de modèles supportés"""
    SIGNAL_CLASSIFIER = "signal_classifier"     # Classification signal quality
    PROFITABILITY_PREDICTOR = "profitability"   # Prédiction profitable/non
    SIGNAL_STRENGTH = "signal_strength"         # Force du signal (0-1)
    EXIT_TIMING = "exit_timing"                 # Timing de sortie optimal

class ModelStatus(Enum):
    """États du modèle"""
    UNTRAINED = "untrained"
    TRAINING = "training"
    TRAINED = "trained"
    VALIDATED = "validated"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"

class ValidationMethod(Enum):
    """Méthodes de validation"""
    TRAIN_TEST_SPLIT = "train_test_split"
    CROSS_VALIDATION = "cross_validation"
    TIME_SERIES_SPLIT = "time_series_split"
    WALK_FORWARD = "walk_forward"

# === ML DATA STRUCTURES ===

@dataclass
class ModelPerformance:
    """Performance du modèle"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mse: float
    mae: float
    r2_score: float
    feature_importance: Dict[str, float]
    confusion_matrix: Optional[List[List[int]]] = None
    validation_scores: List[float] = field(default_factory=list)
    training_time: float = 0.0
    prediction_time_avg: float = 0.0
    
@dataclass 
class ModelConfig:
    """Configuration du modèle"""
    model_type: ModelType
    algorithm: str  # 'logistic', 'linear', 'ridge', 'lasso'
    features_to_use: List[str]
    target_variable: str
    validation_method: ValidationMethod
    train_size: float = 0.8
    random_state: int = 42
    regularization_strength: float = 1.0
    max_iter: int = 1000
    normalize_features: bool = True
    handle_imbalanced: bool = True

@dataclass
class TrainingResult:
    """Résultat d'entraînement"""
    success: bool
    model_performance: Optional[ModelPerformance]
    training_samples: int
    features_count: int
    training_duration: float
    model_path: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

# === MAIN MODEL CLASS ===

class SimpleLinearModel:
    """
    MODÈLE ML LINÉAIRE SIMPLE pour Battle Navale
    
    Objectif principal : Améliorer la qualité des signaux existants
    Approche : Linear first, complexity later
    Input : Features du système Battle Navale + Market structure
    Output : Signal quality score (0-1) ou classification binaire
    """
    
    def __init__(self, 
                 model_type: ModelType = ModelType.SIGNAL_CLASSIFIER,
                 config: Optional[ModelConfig] = None):
        """
        Initialisation du modèle simple
        
        Args:
            model_type: Type de modèle à créer
            config: Configuration personnalisée (sinon defaults)
        """
        self.model_type = model_type
        self.config = config or self._create_default_config()
        self.status = ModelStatus.UNTRAINED
        
        # Core ML components
        self.model: Optional[Union[LogisticRegression, LinearRegression]] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: List[str] = []
        self.performance: Optional[ModelPerformance] = None
        
        # Training data cache
        self.training_data: Optional[pd.DataFrame] = None
        self.target_data: Optional[pd.Series] = None
        
        # Paths for persistence
        self.trading_config = get_trading_config()
        self.auto_config = get_automation_config()
        self.models_dir = Path("data/models/trained")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"SimpleLinearModel initialisé: {model_type.value}")
    
    def train_on_snapshots(self, data: pd.DataFrame) -> TrainingResult:
        """
        Entraînement sur snapshots collectés par Battle Navale
        
        Args:
            data: DataFrame avec features et outcomes des trades
            
        Returns:
            TrainingResult avec métriques de performance
        """
        start_time = time.time()
        self.status = ModelStatus.TRAINING
        
        try:
            # Validation données
            if data.empty or len(data) < 20:
                return TrainingResult(
                    success=False,
                    model_performance=None,
                    training_samples=len(data),
                    features_count=0,
                    training_duration=0,
                    error_message="Données insuffisantes (min 20 échantillons)"
                )
            
            # Préparation features et target
            features_df, target_series = self._prepare_training_data(data)
            
            if features_df is None or target_series is None:
                return TrainingResult(
                    success=False,
                    model_performance=None,
                    training_samples=len(data),
                    features_count=0,
                    training_duration=time.time() - start_time,
                    error_message="Erreur préparation données"
                )
            
            # Stockage features utilisées
            self.feature_names = list(features_df.columns)
            
            # Split données
            X_train, X_test, y_train, y_test = train_test_split(
                features_df, target_series,
                test_size=1 - self.config.train_size,
                random_state=self.config.random_state,
                stratify=target_series if self.model_type == ModelType.SIGNAL_CLASSIFIER else None
            )
            
            # Normalisation si configurée
            if self.config.normalize_features:
                self.scaler = StandardScaler()
                X_train = self.scaler.fit_transform(X_train)
                X_test = self.scaler.transform(X_test)
            
            # Création et entraînement modèle
            self.model = self._create_model()
            self.model.fit(X_train, y_train)
            
            # Prédictions et évaluation
            y_pred = self.model.predict(X_test)
            self.performance = self._calculate_performance(y_test, y_pred, X_test)
            
            # Sauvegarde modèle
            model_path = self._save_model()
            
            # Mise à jour statut
            self.status = ModelStatus.TRAINED
            self.training_data = features_df
            self.target_data = target_series
            
            return TrainingResult(
                success=True,
                model_performance=self.performance,
                training_samples=len(features_df),
                features_count=len(self.feature_names),
                training_duration=time.time() - start_time,
                model_path=model_path
            )
            
        except Exception as e:
            logger.error(f"Erreur entraînement modèle: {e}")
            self.status = ModelStatus.UNTRAINED
            
            return TrainingResult(
                success=False,
                model_performance=None,
                training_samples=len(data),
                features_count=0,
                training_duration=time.time() - start_time,
                error_message=str(e)
            )
    
    def predict_signal_quality(self, features: Dict[str, float]) -> float:
        """
        Prédire la qualité d'un signal (0-1 score)
        
        Args:
            features: Dictionnaire des features Battle Navale
            
        Returns:
            Score de qualité entre 0 et 1
        """
        if self.status not in [ModelStatus.TRAINED, ModelStatus.VALIDATED, ModelStatus.PRODUCTION]:
            logger.warning("Modèle non entraîné, retour score par défaut 0.5")
            return 0.5
        
        try:
            # Conversion features en DataFrame
            features_df = pd.DataFrame([features])
            
            # Sélection features utilisées dans le training
            available_features = [f for f in self.feature_names if f in features_df.columns]
            if len(available_features) < len(self.feature_names) * 0.7:  # 70% minimum
                logger.warning(f"Features manquantes: {len(available_features)}/{len(self.feature_names)}")
                return 0.5
            
            # Ajout features manquantes avec valeurs par défaut
            for feature in self.feature_names:
                if feature not in features_df.columns:
                    features_df[feature] = 0.0  # Valeur par défaut
            
            # Réorganisation colonnes dans l'ordre training
            features_df = features_df[self.feature_names]
            
            # Normalisation si configurée
            if self.scaler is not None:
                features_scaled = self.scaler.transform(features_df)
            else:
                features_scaled = features_df.values
            
            # Prédiction
            if self.model_type == ModelType.SIGNAL_CLASSIFIER:
                # Probabilité de signal positif
                probabilities = self.model.predict_proba(features_scaled)
                quality_score = float(probabilities[0][1])  # Classe positive
            else:
                # Régression directe
                prediction = self.model.predict(features_scaled)
                quality_score = float(np.clip(prediction[0], 0.0, 1.0))
            
            return quality_score
            
        except Exception as e:
            logger.error(f"Erreur prédiction qualité signal: {e}")
            return 0.5  # Score neutre en cas d'erreur
    
    def validate_model_performance(self) -> Dict[str, Any]:
        """
        Validation robuste des performances du modèle
        
        Returns:
            Dictionnaire avec métriques détaillées et recommandations
        """
        if self.status == ModelStatus.UNTRAINED or self.performance is None:
            return {
                "status": "error",
                "message": "Modèle non entraîné",
                "recommendations": ["Entraîner le modèle avant validation"]
            }
        
        validation_results = {
            "model_type": self.model_type.value,
            "training_samples": len(self.training_data) if self.training_data is not None else 0,
            "features_used": self.feature_names,
            "performance_metrics": asdict(self.performance),
            "status": self.status.value,
            "recommendations": []
        }
        
        # Analyse performance
        if self.model_type == ModelType.SIGNAL_CLASSIFIER:
            # Pour classification
            if self.performance.accuracy < 0.55:
                validation_results["recommendations"].append("Accuracy trop faible (<55%), modèle peu fiable")
            if self.performance.precision < 0.5:
                validation_results["recommendations"].append("Précision faible, risque de faux positifs")
            if self.performance.f1_score < 0.5:
                validation_results["recommendations"].append("F1-score faible, équilibre precision/recall à améliorer")
        else:
            # Pour régression
            if self.performance.r2_score < 0.3:
                validation_results["recommendations"].append("R² faible (<0.3), modèle peu prédictif")
            if self.performance.mae > 0.3:
                validation_results["recommendations"].append("MAE élevée (>0.3), erreurs de prédiction importantes")
        
        # Validation cross-validation si possible
        if self.training_data is not None and len(self.training_data) >= 50:
            cv_scores = self._perform_cross_validation()
            validation_results["cross_validation"] = {
                "scores": cv_scores,
                "mean": np.mean(cv_scores),
                "std": np.std(cv_scores)
            }
            
            if np.std(cv_scores) > 0.1:
                validation_results["recommendations"].append("Variance CV élevée, modèle instable")
        
        # Score global
        validation_results["overall_performance"] = self._calculate_overall_score()
        
        # Mise à jour statut si validation OK
        if validation_results["overall_performance"] >= 0.6 and len(validation_results["recommendations"]) == 0:
            self.status = ModelStatus.VALIDATED
            validation_results["message"] = "Modèle validé et prêt pour production"
        else:
            validation_results["message"] = "Modèle nécessite amélioration avant production"
        
        return validation_results
    
    def _create_default_config(self) -> ModelConfig:
        """Création configuration par défaut selon type de modèle"""
        
        features_map = {
            ModelType.SIGNAL_CLASSIFIER: [
                "battle_strength", "base_quality", "confluence_score",
                "delta_pressure", "vwap_distance", "market_regime_encoded"
            ],
            ModelType.PROFITABILITY_PREDICTOR: [
                "battle_strength", "base_quality", "confluence_score",
                "volume_imbalance", "gamma_proximity", "vix_level"
            ],
            ModelType.SIGNAL_STRENGTH: [
                "battle_strength", "base_size", "volume_surge",
                "confluence_score", "time_of_day", "volatility"
            ],
            ModelType.EXIT_TIMING: [
                "position_pnl", "time_in_position", "volatility",
                "support_distance", "momentum", "volume_decline"
            ]
        }
        
        algorithm_map = {
            ModelType.SIGNAL_CLASSIFIER: "logistic",
            ModelType.PROFITABILITY_PREDICTOR: "logistic",
            ModelType.SIGNAL_STRENGTH: "linear",
            ModelType.EXIT_TIMING: "ridge"
        }
        
        target_map = {
            ModelType.SIGNAL_CLASSIFIER: "is_profitable",
            ModelType.PROFITABILITY_PREDICTOR: "trade_profitable",
            ModelType.SIGNAL_STRENGTH: "signal_quality",
            ModelType.EXIT_TIMING: "optimal_exit_time"
        }
        
        return ModelConfig(
            model_type=self.model_type,
            algorithm=algorithm_map.get(self.model_type, "linear"),
            features_to_use=features_map.get(self.model_type, []),
            target_variable=target_map.get(self.model_type, "outcome"),
            validation_method=ValidationMethod.TIME_SERIES_SPLIT
        )
    
    def _prepare_training_data(self, data: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[pd.Series]]:
        """Préparation des données pour entraînement"""
        
        try:
            # Sélection features configurées
            available_features = [f for f in self.config.features_to_use if f in data.columns]
            
            if len(available_features) < 3:
                logger.error(f"Features insuffisantes: {available_features}")
                return None, None
            
            features_df = data[available_features].copy()
            
            # Gestion valeurs manquantes
            features_df = features_df.fillna(0)
            
            # Target variable
            if self.config.target_variable not in data.columns:
                # Création target par défaut si manquante
                if 'trade_pnl' in data.columns:
                    target_series = (data['trade_pnl'] > 0).astype(int)
                else:
                    logger.error(f"Target variable '{self.config.target_variable}' non trouvée")
                    return None, None
            else:
                target_series = data[self.config.target_variable]
            
            # Filtrage lignes avec NaN dans target
            valid_rows = ~target_series.isna()
            features_df = features_df[valid_rows]
            target_series = target_series[valid_rows]
            
            return features_df, target_series
            
        except Exception as e:
            logger.error(f"Erreur préparation données: {e}")
            return None, None
    
    def _create_model(self):
        """Création du modèle selon configuration"""
        
        if self.config.algorithm == "logistic":
            return LogisticRegression(
                C=self.config.regularization_strength,
                max_iter=self.config.max_iter,
                random_state=self.config.random_state,
                class_weight='balanced' if self.config.handle_imbalanced else None
            )
        elif self.config.algorithm == "linear":
            return LinearRegression()
        elif self.config.algorithm == "ridge":
            from sklearn.linear_model import Ridge
            return Ridge(
                alpha=1.0 / self.config.regularization_strength,
                random_state=self.config.random_state
            )
        elif self.config.algorithm == "lasso":
            from sklearn.linear_model import Lasso
            return Lasso(
                alpha=1.0 / self.config.regularization_strength,
                random_state=self.config.random_state
            )
        else:
            # Default
            return LinearRegression()
    
    def _calculate_performance(self, y_true, y_pred, X_test) -> ModelPerformance:
        """Calcul métriques de performance"""
        
        performance = ModelPerformance(
            accuracy=0.0, precision=0.0, recall=0.0, f1_score=0.0,
            mse=0.0, mae=0.0, r2_score=0.0, feature_importance={}
        )
        
        if self.model_type == ModelType.SIGNAL_CLASSIFIER:
            # Métriques classification
            performance.accuracy = accuracy_score(y_true, y_pred)
            performance.precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
            performance.recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
            performance.f1_score = f1_score(y_true, y_pred, average='weighted', zero_division=0)
            
            # Confusion matrix
            cm = confusion_matrix(y_true, y_pred)
            performance.confusion_matrix = cm.tolist()
            
        else:
            # Métriques régression
            performance.mse = mean_squared_error(y_true, y_pred)
            performance.mae = mean_absolute_error(y_true, y_pred)
            performance.r2_score = r2_score(y_true, y_pred)
            
            # Conversion en métriques classification-like pour comparaison
            # Considérer prédiction "correcte" si dans 20% de la vraie valeur
            correct_predictions = np.abs(y_true - y_pred) < 0.2
            performance.accuracy = np.mean(correct_predictions)
            performance.f1_score = performance.accuracy  # Approximation
        
        return performance
    
    def _save_model(self) -> str:
        """Sauvegarde modèle et métadonnées"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        model_filename = f"simple_model_{self.model_type.value}_{timestamp}.joblib"
        model_path = self.models_dir / model_filename
        
        # Sauvegarde ensemble modèle + scaler + métadonnées
        model_bundle = {
            "model": self.model,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "config": self.config,
            "performance": self.performance,
            "model_type": self.model_type,
            "status": self.status,
            "timestamp": timestamp
        }
        
        joblib.dump(model_bundle, model_path)
        logger.info(f"Modèle sauvegardé: {model_path}")
        
        return str(model_path)
    
    def load_model(self, model_path: str) -> bool:
        """Chargement modèle sauvegardé"""
        try:
            model_bundle = joblib.load(model_path)
            
            self.model = model_bundle["model"]
            self.scaler = model_bundle["scaler"]
            self.feature_names = model_bundle["feature_names"]
            self.config = model_bundle["config"]
            self.performance = model_bundle["performance"]
            self.model_type = model_bundle["model_type"]
            self.status = ModelStatus.TRAINED
            
            logger.info(f"Modèle chargé depuis: {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur chargement modèle: {e}")
            return False
    
    def _perform_cross_validation(self, cv_folds: int = 5) -> List[float]:
        """Cross-validation pour validation robuste"""
        
        try:
            if self.training_data is None or self.target_data is None:
                return []
            
            # Scoring function selon type
            if self.model_type == ModelType.SIGNAL_CLASSIFIER:
                scoring = 'f1_weighted'
            else:
                scoring = 'r2'
            
            # Cross-validation
            scores = cross_val_score(
                self.model,
                self.training_data,
                self.target_data,
                cv=cv_folds,
                scoring=scoring
            )
            
            return scores.tolist()
            
        except Exception as e:
            logger.error(f"Erreur cross-validation: {e}")
            return []
    
    def _calculate_overall_score(self) -> float:
        """Score global de performance (0-1)"""
        
        if self.performance is None:
            return 0.0
        
        if self.model_type == ModelType.SIGNAL_CLASSIFIER:
            # Moyenne pondérée pour classification
            score = (
                self.performance.accuracy * 0.3 +
                self.performance.precision * 0.3 +
                self.performance.f1_score * 0.4
            )
        else:
            # Pour régression, normaliser R² (peut être négatif)
            r2_normalized = max(0, min(1, self.performance.r2_score))
            mae_normalized = max(0, 1 - self.performance.mae)  # Inverse de MAE
            
            score = (r2_normalized * 0.6 + mae_normalized * 0.4)
        
        return float(np.clip(score, 0.0, 1.0))

# === FACTORY FUNCTIONS ===

def create_signal_classifier() -> SimpleLinearModel:
    """Factory pour modèle classification signaux"""
    return SimpleLinearModel(ModelType.SIGNAL_CLASSIFIER)

def create_profitability_predictor() -> SimpleLinearModel:
    """Factory pour prédicteur profitabilité"""
    return SimpleLinearModel(ModelType.PROFITABILITY_PREDICTOR)

def create_signal_strength_model() -> SimpleLinearModel:
    """Factory pour modèle force signal"""
    return SimpleLinearModel(ModelType.SIGNAL_STRENGTH)

def create_battle_navale_model() -> SimpleLinearModel:
    """Factory pour modèle optimisé Battle Navale"""
    # Configuration spéciale pour Battle Navale
    config = ModelConfig(
        model_type=ModelType.SIGNAL_CLASSIFIER,
        algorithm="logistic",
        features_to_use=[
            "battle_strength",
            "base_quality", 
            "base_size",
            "volume_surge",
            "confluence_score",
            "delta_pressure",
            "vwap_distance",
            "market_regime_encoded",
            "gamma_proximity",
            "volatility"
        ],
        target_variable="is_profitable",
        validation_method=ValidationMethod.TIME_SERIES_SPLIT,
        train_size=0.8,
        normalize_features=True,
        handle_imbalanced=True
    )
    
    return SimpleLinearModel(ModelType.SIGNAL_CLASSIFIER, config)

# === ALIAS EXPORT ===
# Pour compatibilité avec anciens imports
SimpleLinearPredictor = SimpleLinearModel

# === TEST FUNCTION ===

def test_simple_model():
    """Test complet du modèle simple"""
    logger.info("=== TEST SIMPLE MODEL ===")
    
    # Création modèle test
    model = create_signal_classifier()
    
    # Données test simulées
    test_data = pd.DataFrame({
        "battle_strength": np.random.uniform(0, 1, 100),
        "base_quality": np.random.uniform(0, 1, 100),
        "confluence_score": np.random.uniform(0, 1, 100),
        "trade_pnl": np.random.normal(0, ES_TICK_VALUE, 100)
    })
    
    # Test entraînement
    result = model.train_on_snapshots(test_data)
    print(f"Training Success: {result.success}")
    print(f"Samples: {result.training_samples}, Features: {result.features_count}")
    
    # Test prédiction
    test_features = {
        "battle_strength": 0.8,
        "base_quality": 0.9,
        "confluence_score": 0.7
    }
    quality = model.predict_signal_quality(test_features)
    print(f"Signal Quality: {quality:.3f}")
    
    # Test validation
    validation = model.validate_model_performance()
    print(f"Validation: {validation['overall_performance']}")
    
    logger.info("=== TEST TERMINÉ ===")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_simple_model()