#!/usr/bin/env python3
"""
Script pour corriger les imports circulaires et l'enum ModelType
"""

import os
from pathlib import Path

def fix_circular_and_enum():
    """Corrige les imports circulaires et l'enum ModelType"""
    
    project_root = Path("D:/MIA_IA_system")
    
    # Fix 1: ml_config.py - Supprimer l'import circulaire
    ml_config_path = project_root / "config/ml_config.py"
    print("📄 Correction: config/ml_config.py")
    
    ml_config_content = '''"""
Configuration ML pour MIA_IA_SYSTEM
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum

class ValidationMethod(Enum):
    """Méthodes de validation (copie locale pour éviter import circulaire)"""
    HOLDOUT = "holdout"
    CROSS_VALIDATION = "cross_validation"
    TIME_SERIES_SPLIT = "time_series_split"

@dataclass
class MLConfig:
    """Configuration pour le machine learning"""
    # Model settings
    model_type: str = "linear"
    model_params: Dict[str, Any] = None
    
    # Training settings
    train_test_split: float = 0.8
    validation_split: float = 0.2
    validation_method: str = "holdout"
    n_splits: int = 5
    
    # Training parameters
    max_epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    early_stopping_patience: int = 10
    
    # Feature settings
    feature_columns: List[str] = None
    target_column: str = "signal_quality"
    
    # Performance thresholds
    min_accuracy: float = 0.65
    min_profit_factor: float = 1.5
    
    def __post_init__(self):
        if self.model_params is None:
            self.model_params = {}
        if self.feature_columns is None:
            self.feature_columns = [
                'delta_ratio', 'volume_imbalance', 'bid_ask_spread',
                'trade_intensity', 'regime_trend_strength', 'vwap_distance'
            ]

def get_ml_config() -> MLConfig:
    """Retourne la configuration ML"""
    return MLConfig()
'''
    
    with open(ml_config_path, 'w', encoding='utf-8') as f:
        f.write(ml_config_content)
    print("  ✅ Supprimé import circulaire")
    
    # Fix 2: simple_model.py - Corriger ModelType enum
    simple_model_path = project_root / "ml/simple_model.py"
    print("\n📄 Correction: ml/simple_model.py")
    
    # Lire le contenu actuel pour préserver ce qui fonctionne
    with open(simple_model_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chercher la définition de ModelType
    if "class ModelType" in content:
        # Extraire tout avant ModelType
        before_modeltype = content.split("class ModelType")[0]
        
        # Nouvelle définition complète
        new_content = before_modeltype + '''class ModelType(Enum):
    """Types de modèles ML disponibles"""
    LINEAR_REGRESSION = "linear_regression"
    LOGISTIC_REGRESSION = "logistic_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    SVM = "svm"

class SimpleLinearPredictor:
    """Prédicteur linéaire simple pour ML Battle Navale"""
    
    def __init__(self, model_type: ModelType = ModelType.LINEAR_REGRESSION):
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.is_fitted = False
        self.feature_names = []
        
    def fit(self, X, y, feature_names=None):
        """Entraîne le modèle"""
        from sklearn.preprocessing import StandardScaler
        from sklearn.linear_model import LinearRegression, LogisticRegression
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
        
        # Sauvegarder les noms de features
        if feature_names:
            self.feature_names = feature_names
        
        # Scaler les données
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Créer le modèle selon le type
        if self.model_type == ModelType.LINEAR_REGRESSION:
            self.model = LinearRegression()
        elif self.model_type == ModelType.LOGISTIC_REGRESSION:
            self.model = LogisticRegression(max_iter=1000)
        elif self.model_type == ModelType.RANDOM_FOREST:
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif self.model_type == ModelType.GRADIENT_BOOSTING:
            self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        else:
            # Par défaut, regression linéaire
            self.model = LinearRegression()
        
        # Entraîner
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        return self
        
    def predict(self, X):
        """Prédit avec le modèle"""
        if not self.is_fitted:
            raise ValueError("Model not fitted yet")
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X):
        """Prédit les probabilités (pour classification)"""
        if not self.is_fitted:
            raise ValueError("Model not fitted yet")
        if not hasattr(self.model, 'predict_proba'):
            # Si pas de predict_proba, utiliser predict
            predictions = self.predict(X)
            # Convertir en probabilités fictives
            return np.column_stack([1 - predictions, predictions])
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)

def create_battle_navale_model(model_type: ModelType = ModelType.LINEAR_REGRESSION):
    """Factory function pour créer un modèle Battle Navale"""
    return SimpleLinearPredictor(model_type=model_type)

# Ajouter au __all__ si nécessaire
__all__ = ['SimpleLinearPredictor', 'ModelType', 'create_battle_navale_model']
'''
    else:
        # Si ModelType n'existe pas, créer tout
        new_content = content + '''
from enum import Enum
import numpy as np

class ModelType(Enum):
    """Types de modèles ML disponibles"""
    LINEAR_REGRESSION = "linear_regression"
    LOGISTIC_REGRESSION = "logistic_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    SVM = "svm"

''' + new_content.split('class SimpleLinearPredictor')[1] if 'class SimpleLinearPredictor' in new_content else ''
    
    with open(simple_model_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("  ✅ Corrigé ModelType enum et SimpleLinearPredictor")
    
    # Fix 3: Nettoyer les imports dans base_types si nécessaire
    base_types_path = project_root / "core/base_types.py"
    if base_types_path.exists():
        print("\n📄 Vérification: core/base_types.py")
        with open(base_types_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # S'assurer que OrderType est bien défini
        if "class OrderType(Enum):" not in content and "OrderType" in content:
            # Ajouter après SignalType
            order_type_def = '''
class OrderType(Enum):
    """Types d'ordres de trading"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    MOC = "moc"  # Market on Close
    LOC = "loc"  # Limit on Close
'''
            # Insérer après SignalType
            if "class SignalType(Enum):" in content:
                parts = content.split("class SignalType(Enum):")
                if len(parts) == 2:
                    # Trouver la fin de SignalType
                    lines = parts[1].split('\n')
                    enum_end = 0
                    for i, line in enumerate(lines):
                        if line.strip() and not line.startswith(' ') and i > 0:
                            enum_end = i
                            break
                    
                    before = parts[0] + "class SignalType(Enum):" + '\n'.join(lines[:enum_end])
                    after = '\n'.join(lines[enum_end:])
                    content = before + '\n' + order_type_def + '\n' + after
            
            with open(base_types_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("  ✅ Ajouté OrderType")
    
    print("\n" + "=" * 60)
    print("✅ Imports circulaires et enums corrigés !")

if __name__ == "__main__":
    fix_circular_and_enum()