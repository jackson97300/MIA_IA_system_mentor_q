#!/usr/bin/env python3
"""
Script de test et correction des imports ML
"""

import sys
import traceback
from pathlib import Path

# Test 1: Import simple_model seul
print("Test 1: Import simple_model...")
try:
    from ml.simple_model import SimpleLinearModel
    print("✅ SimpleLinearModel importé avec succès")
except Exception as e:
    print(f"❌ Erreur import SimpleLinearModel: {e}")
    traceback.print_exc()

# Test 2: Import model_validator seul
print("\nTest 2: Import model_validator...")
try:
    from ml.model_validator import ModelValidator
    print("✅ ModelValidator importé avec succès")
except Exception as e:
    print(f"❌ Erreur import ModelValidator: {e}")
    traceback.print_exc()

# Test 3: Import model_trainer seul
print("\nTest 3: Import model_trainer...")
try:
    # Avant l'import, on doit s'assurer que SimpleLinearModel est disponible
    import ml.simple_model
    from ml.model_trainer import ModelTrainer
    print("✅ ModelTrainer importé avec succès")
except Exception as e:
    print(f"❌ Erreur import ModelTrainer: {e}")
    traceback.print_exc()

# Test 4: Vérifier la ligne problématique dans model_trainer.py
print("\nTest 4: Analyse du problème dans model_trainer.py...")
model_trainer_path = Path("ml/model_trainer.py")
if model_trainer_path.exists():
    with open(model_trainer_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Chercher la ligne problématique
    for i, line in enumerate(lines, 1):
        if "SimpleMLModel = SimpleLinearModel" in line and i < 210:
            print(f"Ligne {i}: {line.strip()}")
            print("⚠️ Cette ligne tente de créer un alias AVANT l'import de SimpleLinearModel")
            
            # Vérifier les imports avant cette ligne
            print("\nImports trouvés avant cette ligne:")
            for j in range(max(0, i-50), i):
                if "from ml.simple_model import" in lines[j] or "import SimpleLinearModel" in lines[j]:
                    print(f"  Ligne {j+1}: {lines[j].strip()}")

# Solution proposée
print("\n" + "="*60)
print("SOLUTION PROPOSÉE:")
print("="*60)
print("""
Le problème est que dans model_trainer.py, la ligne:
    SimpleMLModel = SimpleLinearModel

apparaît AVANT l'import de SimpleLinearModel.

Pour corriger, il faut soit:
1. Déplacer cette ligne APRÈS les imports
2. Importer SimpleLinearModel avant de créer l'alias
3. Supprimer cet alias si non nécessaire

Voici la correction à appliquer dans model_trainer.py:
""")

print("""
# Au début du fichier, après les imports ML Components:
from ml.simple_model import SimpleLinearModel, ModelType, ModelStatus, create_signal_classifier
from ml.data_processor import MLDataProcessor, ProcessedDataset, create_battle_navale_processor
from ml.model_validator import ModelValidator, ValidationLevel, create_rigorous_validator

# PUIS, après ces imports, créer l'alias si nécessaire:
SimpleMLModel = SimpleLinearModel  # Alias pour compatibilité
""")

# Test 5: Essayer d'importer le module ML complet avec la correction
print("\nTest 5: Import complet du module ML...")
try:
    # Forcer le rechargement des modules
    if 'ml' in sys.modules:
        del sys.modules['ml']
    if 'ml.model_trainer' in sys.modules:
        del sys.modules['ml.model_trainer']
    
    import ml
    print("✅ Module ML importé avec succès!")
except Exception as e:
    print(f"❌ Erreur import module ML: {e}")
    traceback.print_exc()