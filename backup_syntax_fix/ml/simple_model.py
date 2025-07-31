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
import logging
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
logger = logging.getLogger(__name__)

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
        Entraînement sur snapshots collectés par trade_snapshotter
        
        Args:
            data: DataFrame avec snapshots formatés
            
        Returns:
            TrainingResult avec métriques de performance
        """
        start_time = time.time()
        
        try:
            logger.info("Début entraînement sur snapshots...")
            
            # Validation des données d'entrée
            if data.empty:
                return TrainingResult(
                    success=False,
                    training_samples=0,
                    features_count=0,
                    training_duration=0.0,
                    error_message="Dataset vide fourni"
                )
            
            # Préparation features et targets
            features_df, target_series = self._prepare_training_data(data)
            
            if features_df.empty or len(target_series) == 0:
                return TrainingResult(
                    success=False,
                    training_samples=0,
                    features_count=0,
                    training_duration=0.0,
                    error_message="Aucune feature valide extraite"
                )
            
            # Split train/test
            X_train, X_test, y_train, y_test = train_test_split(
                features_df, target_series,
                test_size=(1 - self.config.train_size),
                random_state=self.config.random_state,
                stratify=target_series if self.model_type == ModelType.SIGNAL_CLASSIFIER else None
            )
            
            # Normalisation features
            if self.config.normalize_features:
                self.scaler = StandardScaler()
                X_train_scaled = self.scaler.fit_transform(X_train)
                X_test_scaled = self.scaler.transform(X_test)
            else:
                X_train_scaled = X_train
                X_test_scaled = X_test
            
            # Création et entraînement du modèle
            self.model = self._create_model()
            self.model.fit(X_train_scaled, y_train)
            
            # Prédictions sur test set
            y_pred = self.model.predict(X_test_scaled)
            
            # Calcul des métriques
            performance = self._calculate_performance(y_test, y_pred, X_test_scaled)
            
            # Cross-validation si demandée
            if self.config.validation_method == ValidationMethod.CROSS_VALIDATION:
                cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
                performance.validation_scores = cv_scores.tolist()
                logger.info(f"CV Scores: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
            
            # Feature importance pour linear models
            if hasattr(self.model, 'coef_'):
                importance_dict = {}
                coefficients = self.model.coef_
                if len(coefficients.shape) > 1:  # Multi-class
                    coefficients = np.abs(coefficients).mean(axis=0)
                
                for i, feature in enumerate(features_df.columns):
                    importance_dict[feature] = float(np.abs(coefficients[i]))
                
                performance.feature_importance = importance_dict
            
            # Sauvegarde cache training
            self.training_data = features_df
            self.target_data = target_series
            self.feature_names = list(features_df.columns)
            self.performance = performance
            self.status = ModelStatus.TRAINED
            
            training_duration = time.time() - start_time
            
            # Sauvegarde modèle
            model_path = self._save_model()
            
            logger.info(f"Entraînement réussi: {len(X_train)} samples, {len(features_df.columns)} features")
            logger.info(f"Performance: Accuracy={performance.accuracy:.3f}, F1={performance.f1_score:.3f}")
            
            return TrainingResult(
                success=True,
                model_performance=performance,
                training_samples=len(X_train),
                features_count=len(features_df.columns),
                training_duration=training_duration,
                model_path=model_path
            )
            
        except Exception as e:
            error_msg = f"Erreur entraînement: {str(e)}"
            logger.error(error_msg)
            return TrainingResult(
                success=False,
                training_samples=0,
                features_count=0,
                training_duration=time.time() - start_time,
                error_message=error_msg
            )
    
    def predict_signal_quality(self, features: Dict[str, Any]) -> float:
        """
        Prédiction qualité d'un signal Battle Navale
        
        Args:
            features: Dictionnaire des features calculées
            
        Returns:
            Score qualité entre 0.0 et 1.0 (1.0 = excellente qualité)
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
        
        try:
            validation_report = {
                "model_type": self.model_type.value,
                "training_timestamp": datetime.now(timezone.utc).isoformat(),
                "overall_performance": {},
                "detailed_metrics": asdict(self.performance),
                "quality_assessment": {},
                "recommendations": [],
                "production_readiness": {}
            }
            
            # Overall performance summary
            perf = self.performance
            validation_report["overall_performance"] = {
                "accuracy": perf.accuracy,
                "precision": perf.precision,
                "recall": perf.recall,
                "f1_score": perf.f1_score,
                "model_quality": "excellent" if perf.f1_score > 0.8 else 
                               "good" if perf.f1_score > 0.7 else
                               "acceptable" if perf.f1_score > 0.6 else "poor"
            }
            
            # Quality assessment
            quality_checks = []
            
            if perf.accuracy > 0.75:
                quality_checks.append("✅ Accuracy satisfaisante")
            else:
                quality_checks.append("❌ Accuracy insuffisante (<75%)")
            
            if perf.f1_score > 0.7:
                quality_checks.append("✅ F1-Score acceptable")
            else:
                quality_checks.append("❌ F1-Score faible")
            
            if len(perf.validation_scores) > 0:
                cv_mean = np.mean(perf.validation_scores)
                cv_std = np.std(perf.validation_scores)
                if cv_std < 0.1:
                    quality_checks.append("✅ Modèle stable (faible variance CV)")
                else:
                    quality_checks.append("⚠️ Modèle instable (haute variance CV)")
            
            validation_report["quality_assessment"]["checks"] = quality_checks
            
            # Recommendations
            recommendations = []
            
            if perf.accuracy < 0.7:
                recommendations.append("Améliorer la qualité des features")
                recommendations.append("Considérer plus de données d'entraînement")
            
            if perf.precision < 0.7:
                recommendations.append("Réduire les faux positifs - ajuster threshold")
            
            if perf.recall < 0.7:
                recommendations.append("Améliorer détection signaux positifs")
            
            if len(perf.feature_importance) > 0:
                top_features = sorted(perf.feature_importance.items(), 
                                    key=lambda x: x[1], reverse=True)[:3]
                recommendations.append(f"Features les plus importantes: {[f[0] for f in top_features]}")
            
            validation_report["recommendations"] = recommendations
            
            # Production readiness
            ready_for_prod = (
                perf.accuracy > 0.7 and 
                perf.f1_score > 0.65 and
                len(perf.validation_scores) > 0 and
                np.std(perf.validation_scores) < 0.15
            )
            
            validation_report["production_readiness"] = {
                "ready": ready_for_prod,
                "confidence_level": "high" if ready_for_prod and perf.f1_score > 0.8 else
                                  "medium" if ready_for_prod else "low",
                "suggested_usage": "production" if ready_for_prod else "paper_trading_only"
            }
            
            if ready_for_prod:
                self.status = ModelStatus.VALIDATED
                logger.info("Modèle validé pour production")
            
            return validation_report
            
        except Exception as e:
            logger.error(f"Erreur validation modèle: {e}")
            return {
                "status": "error",
                "message": f"Erreur lors de la validation: {str(e)}",
                "recommendations": ["Vérifier intégrité du modèle", "Re-entraîner si nécessaire"]
            }
    
    def update_model_weights(self, new_data: pd.DataFrame) -> bool:
        """
        Mise à jour incrémentale des poids du modèle
        
        Args:
            new_data: Nouvelles données pour mise à jour
            
        Returns:
            True si mise à jour réussie, False sinon
        """
        if self.status == ModelStatus.UNTRAINED:
            logger.warning("Impossible de mettre à jour un modèle non entraîné")
            return False
        
        try:
            logger.info("Début mise à jour incrémentale du modèle...")
            
            # Préparation nouvelles données
            new_features, new_targets = self._prepare_training_data(new_data)
            
            if new_features.empty:
                logger.warning("Aucune nouvelle feature valide pour mise à jour")
                return False
            
            # Vérification compatibilité features
            if not all(feature in new_features.columns for feature in self.feature_names):
                logger.error("Features incompatibles pour mise à jour")
                return False
            
            # Normalisation nouvelles données
            new_features_ordered = new_features[self.feature_names]
            if self.scaler is not None:
                new_features_scaled = self.scaler.transform(new_features_ordered)
            else:
                new_features_scaled = new_features_ordered.values
            
            # Update via partial_fit pour models supportés
            if hasattr(self.model, 'partial_fit'):
                self.model.partial_fit(new_features_scaled, new_targets)
                logger.info(f"Mise à jour partielle: {len(new_features)} nouveaux échantillons")
            else:
                # Re-training complet avec nouvelles données ajoutées
                if self.training_data is not None and self.target_data is not None:
                    # Combinaison ancien + nouveau
                    combined_features = pd.concat([self.training_data, new_features_ordered], 
                                                ignore_index=True)
                    combined_targets = pd.concat([self.target_data, new_targets], 
                                               ignore_index=True)
                    
                    # Re-entraînement
                    if self.scaler is not None:
                        combined_features_scaled = self.scaler.fit_transform(combined_features)
                    else:
                        combined_features_scaled = combined_features.values
                    
                    self.model.fit(combined_features_scaled, combined_targets)
                    
                    # Mise à jour cache
                    self.training_data = combined_features
                    self.target_data = combined_targets
                    
                    logger.info(f"Re-entraînement complet: {len(combined_features)} échantillons totaux")
                else:
                    logger.error("Pas de données d'entraînement en cache pour re-training")
                    return False
            
            # Sauvegarde modèle mis à jour
            self._save_model()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur mise à jour modèle: {e}")
            return False
    
    # === MÉTHODES PRIVÉES ===
    
    def _create_default_config(self) -> ModelConfig:
        """Création configuration par défaut selon type de modèle"""
        
        default_features = [
            # Battle Navale core features
            "battle_strength", "base_quality", "confluence_score",
            
            # Market structure features  
            "distance_to_vah", "distance_to_val", "distance_to_poc",
            "volume_profile_strength", "trend_alignment",
            
            # Technical features
            "rsi_divergence", "momentum_strength", "volatility_regime",
            
            # Session features
            "session_phase", "volume_relative", "time_of_day"
        ]
        
        if self.model_type == ModelType.SIGNAL_CLASSIFIER:
            return ModelConfig(
                model_type=self.model_type,
                algorithm="logistic",
                features_to_use=default_features,
                target_variable="signal_profitable",
                validation_method=ValidationMethod.CROSS_VALIDATION,
                regularization_strength=1.0,
                handle_imbalanced=True
            )
        else:  # Regression types
            return ModelConfig(
                model_type=self.model_type,
                algorithm="linear",
                features_to_use=default_features,
                target_variable="signal_quality_score", 
                validation_method=ValidationMethod.TRAIN_TEST_SPLIT,
                regularization_strength=0.1
            )
    
    def _create_model(self) -> Union[LogisticRegression, LinearRegression]:
        """Création du modèle selon configuration"""
        
        if self.config.algorithm == "logistic":
            return LogisticRegression(
                random_state=self.config.random_state,
                max_iter=self.config.max_iter,
                C=1.0/self.config.regularization_strength if self.config.regularization_strength > 0 else 1.0,
                class_weight='balanced' if self.config.handle_imbalanced else None
            )
        elif self.config.algorithm == "linear":
            return LinearRegression()
        else:
            logger.warning(f"Algorithme non supporté: {self.config.algorithm}, utilisation LogisticRegression")
            return LogisticRegression(random_state=self.config.random_state)
    
    def _prepare_training_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Préparation données d'entraînement depuis snapshots"""
        
        # Extraction features depuis snapshots
        features_list = []
        targets_list = []
        
        for idx, row in data.iterrows():
            try:
                # Features Battle Navale (simulation - adapter selon vraie structure)
                features = {
                    "battle_strength": row.get("battle_strength", 0.5),
                    "base_quality": row.get("base_quality", 0.5),
                    "confluence_score": row.get("confluence_score", 0.5),
                    "distance_to_vah": row.get("distance_to_vah", 0.0),
                    "distance_to_val": row.get("distance_to_val", 0.0), 
                    "distance_to_poc": row.get("distance_to_poc", 0.0),
                    "volume_profile_strength": row.get("volume_profile_strength", 0.5),
                    "trend_alignment": row.get("trend_alignment", 0.5),
                    "rsi_divergence": row.get("rsi_divergence", 0.0),
                    "momentum_strength": row.get("momentum_strength", 0.5),
                    "volatility_regime": row.get("volatility_regime", 0.5),
                    "session_phase": row.get("session_phase", 0.5),
                    "volume_relative": row.get("volume_relative", 1.0),
                    "time_of_day": row.get("time_of_day", 0.5)
                }
                
                # Target selon type de modèle
                if self.model_type == ModelType.SIGNAL_CLASSIFIER:
                    # Classification: signal profitable ou non
                    target = 1 if row.get("trade_pnl", 0) > 0 else 0
                else:
                    # Régression: score qualité basé sur performance
                    pnl = row.get("trade_pnl", 0)
                    max_favorable = row.get("max_favorable_excursion", 0)
                    # Score qualité 0-1 basé sur ratio performance
                    target = min(1.0, max(0.0, (pnl + max_favorable) / (2 * ES_TICK_VALUE)))
                
                features_list.append(features)
                targets_list.append(target)
                
            except Exception as e:
                logger.warning(f"Erreur traitement ligne {idx}: {e}")
                continue
        
        if not features_list:
            return pd.DataFrame(), pd.Series()
        
        features_df = pd.DataFrame(features_list)
        targets_series = pd.Series(targets_list)
        
        # Nettoyage données
        features_df = features_df.fillna(0.0)
        features_df = features_df.select_dtypes(include=[np.number])
        
        return features_df, targets_series
    
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

# === FACTORY FUNCTIONS ===

def create_signal_classifier() -> SimpleLinearModel:
    """Factory pour modèle classification signaux"""
    return SimpleLinearPredictor(ModelType.SIGNAL_CLASSIFIER)

def create_profitability_predictor() -> SimpleLinearModel:
    """Factory pour prédicteur profitabilité"""
    return SimpleLinearPredictor(ModelType.PROFITABILITY_PREDICTOR)

def create_signal_strength_model() -> SimpleLinearModel:
    """Factory pour modèle force signal"""
    return SimpleLinearPredictor(ModelType.SIGNAL_STRENGTH)

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
    logger.info("Training Success: {result.success}")
    logger.info("Samples: {result.training_samples}, Features: {result.features_count}")
    
    # Test prédiction
    test_features = {
        "battle_strength": 0.8,
        "base_quality": 0.9,
        "confluence_score": 0.7
    }
    quality = model.predict_signal_quality(test_features)
    logger.info("Signal Quality: {quality:.3f}")
    
    # Test validation
    validation = model.validate_model_performance()
    logger.info("Validation: {validation['overall_performance']}")
    
    logger.info("=== TEST TERMINÉ ===")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_simple_model()