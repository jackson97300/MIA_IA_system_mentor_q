#!/usr/bin/env python3
"""
Script pour corriger TOUTES les erreurs d'import restantes
"""

import os
from pathlib import Path
import re

def fix_all_remaining_imports():
    """Corrige toutes les erreurs d'import restantes"""
    
    project_root = Path("D:/MIA_IA_system")
    
    # Fix 1: alert_system.py - MIMEText et MimeMultipart
    alert_system_path = project_root / "monitoring/alert_system.py"
    if alert_system_path.exists():
        print("📄 Correction: monitoring/alert_system.py")
        with open(alert_system_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup
        with open(alert_system_path.with_suffix('.py.backup_final'), 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Corriger les imports email
        content = re.sub(r'from email\.mime\.text import MIMEText', 
                        'from email.mime.text import MIMEText', content)
        content = re.sub(r'from email\.mime\.multipart import MimeMultipart', 
                        'from email.mime.multipart import MIMEMultipart', content)
        content = re.sub(r'MIMEText\(', 'MIMEText(', content)
        content = re.sub(r'MimeMultipart\(', 'MIMEMultipart(', content)
        
        # Corriger le logger non défini
        if "logger.warning(f\"Email functionality disabled: {e}\")" in content:
            # Ajouter la définition du logger si elle n'existe pas
            if "logger = logging.getLogger(__name__)" not in content:
                # Trouver où insérer le logger (après les imports)
                import_section_end = content.find("try:")
                if import_section_end > 0:
                    before = content[:import_section_end]
                    after = content[import_section_end:]
                    content = before + "\nlogger = logging.getLogger(__name__)\n\n" + after
        
        with open(alert_system_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Corrigé MIMEText et MIMEMultipart")
    
    # Fix 2: simple_model.py - Ajouter SimpleLinearPredictor dans la définition de classe
    simple_model_path = project_root / "ml/simple_model.py"
    if simple_model_path.exists():
        print("\n📄 Correction: ml/simple_model.py")
        with open(simple_model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si la classe existe, sinon la créer
        if "class SimpleLinearPredictor" not in content:
            # Ajouter une implémentation basique
            class_def = '''
class SimpleLinearPredictor:
    """Prédicteur linéaire simple pour ML"""
    
    def __init__(self, model_type: ModelType = ModelType.LINEAR_REGRESSION):
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.is_fitted = False
        
    def fit(self, X, y):
        """Entraîne le modèle"""
        from sklearn.preprocessing import StandardScaler
        from sklearn.linear_model import LinearRegression
        
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = LinearRegression()
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        
    def predict(self, X):
        """Prédit avec le modèle"""
        if not self.is_fitted:
            raise ValueError("Model not fitted yet")
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
'''
            # Insérer après ModelType enum
            if "class ModelType" in content:
                parts = content.split("class ModelType")
                # Trouver la fin de l'enum
                enum_end = parts[1].find("\n\n")
                if enum_end > 0:
                    content = parts[0] + "class ModelType" + parts[1][:enum_end] + "\n" + class_def + parts[1][enum_end:]
            else:
                content += class_def
        
        with open(simple_model_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Ajouté SimpleLinearPredictor")
    
    # Fix 3: data_processor.py - Ajouter create_data_processor
    data_processor_path = project_root / "ml/data_processor.py"
    if data_processor_path.exists():
        print("\n📄 Correction: ml/data_processor.py")
        with open(data_processor_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "def create_data_processor" not in content:
            # Ajouter la fonction factory
            factory_func = '''
def create_data_processor():
    """Factory function pour créer un MLDataProcessor"""
    return MLDataProcessor()
'''
            content += factory_func
        
        with open(data_processor_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Ajouté create_data_processor")
    
    # Fix 4: features/__init__.py - Ajouter OPTIMIZED_CALCULATOR_AVAILABLE
    features_init = project_root / "features/__init__.py"
    if features_init.exists():
        print("\n📄 Correction: features/__init__.py")
        with open(features_init, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "OPTIMIZED_CALCULATOR_AVAILABLE" not in content:
            # Ajouter après les imports
            addition = '''
# Vérifier si la version optimisée est disponible
OPTIMIZED_CALCULATOR_AVAILABLE = False
try:
    from .feature_calculator_optimized import FeatureCalculatorOptimized
    OPTIMIZED_CALCULATOR_AVAILABLE = True
except ImportError:
    pass
'''
            # Insérer après le logger
            if "logger = logging.getLogger(__name__)" in content:
                content = content.replace(
                    "logger = logging.getLogger(__name__)",
                    "logger = logging.getLogger(__name__)" + addition
                )
            else:
                content = addition + content
        
        with open(features_init, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Ajouté OPTIMIZED_CALCULATOR_AVAILABLE")
    
    # Fix 5: base_types.py - Ajouter OrderType
    base_types_path = project_root / "core/base_types.py"
    if base_types_path.exists():
        print("\n📄 Correction: core/base_types.py")
        with open(base_types_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "class OrderType" not in content:
            # Ajouter OrderType enum
            order_type_def = '''
class OrderType(Enum):
    """Types d'ordres"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
'''
            # Insérer après les autres enums
            if "class SignalType(Enum):" in content:
                parts = content.split("class SignalType(Enum):")
                # Trouver la fin de l'enum
                enum_end = parts[1].find("\nclass ")
                if enum_end > 0:
                    content = parts[0] + "class SignalType(Enum):" + parts[1][:enum_end] + "\n" + order_type_def + "\n" + parts[1][enum_end:]
                else:
                    content = content + "\n" + order_type_def
        
        with open(base_types_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Ajouté OrderType")
    
    # Fix 6: strategies/__init__.py - Ajouter create_signal_generator à l'export
    strategies_init = project_root / "strategies/__init__.py"
    if strategies_init.exists():
        print("\n📄 Correction: strategies/__init__.py")
        with open(strategies_init, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # S'assurer que create_signal_generator est dans __all__
        if "'create_signal_generator'" not in content and "create_signal_generator" in content:
            content = content.replace(
                "__all__.extend(['SignalGenerator',",
                "__all__.extend(['SignalGenerator', 'create_signal_generator',"
            )
        
        with open(strategies_init, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Exporté create_signal_generator")
    
    # Fix 7: Créer des fichiers config manquants
    ml_config_path = project_root / "config/ml_config.py"
    if not ml_config_path.exists():
        print("\n📄 Création: config/ml_config.py")
        ml_config_content = '''"""
Configuration ML pour MIA_IA_SYSTEM
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class MLConfig:
    """Configuration pour le machine learning"""
    model_type: str = "linear"
    train_test_split: float = 0.8
    validation_split: float = 0.2
    max_epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    early_stopping_patience: int = 10

def get_ml_config() -> MLConfig:
    """Retourne la configuration ML"""
    return MLConfig()
'''
        with open(ml_config_path, 'w', encoding='utf-8') as f:
            f.write(ml_config_content)
        print("  ✅ Créé ml_config.py")
    
    sierra_config_path = project_root / "config/sierra_config.py"
    if not sierra_config_path.exists():
        print("\n📄 Création: config/sierra_config.py")
        sierra_config_content = '''"""
Configuration Sierra Chart pour MIA_IA_SYSTEM
"""

from dataclasses import dataclass

@dataclass
class SierraConfig:
    """Configuration pour Sierra Chart"""
    host: str = "127.0.0.1"
    port: int = 11099
    username: str = ""
    password: str = ""
    historical_data_port: int = 11097
    update_frequency_ms: int = 100

def get_sierra_config() -> SierraConfig:
    """Retourne la configuration Sierra Chart"""
    return SierraConfig()
'''
        with open(sierra_config_path, 'w', encoding='utf-8') as f:
            f.write(sierra_config_content)
        print("  ✅ Créé sierra_config.py")
    
    print("\n" + "=" * 60)
    print("✅ Toutes les corrections appliquées !")
    print("\n📦 Installer les dernières dépendances manquantes :")
    print("pip install seaborn")

if __name__ == "__main__":
    fix_all_remaining_imports()