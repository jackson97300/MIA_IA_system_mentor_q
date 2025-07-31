#!/usr/bin/env python3
"""
Correction du problème d'import - SimpleLinearPredictor vs SimpleLinearModel
"""

import shutil
from pathlib import Path

def fix_import_mismatch():
    """Corrige le problème de nom d'import"""
    
    file_path = Path("ml/model_trainer.py")
    backup_path = file_path.with_suffix('.py.backup_import')
    
    print("CORRECTION DU PROBLÈME D'IMPORT")
    print("=" * 80)
    print("\nProblème identifié:")
    print("- Ligne 53: importe 'SimpleLinearPredictor'")
    print("- Ligne 199: utilise 'SimpleLinearModel'")
    print("Ces deux noms doivent correspondre!\n")
    
    # Backup
    shutil.copy2(file_path, backup_path)
    print(f"Backup créé: {backup_path}")
    
    # Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Option 1: Changer l'import pour inclure SimpleLinearModel
    # (SimpleLinearPredictor est peut-être un ancien nom ou un alias)
    
    # Chercher la ligne d'import
    old_import = "from ml.simple_model import SimpleLinearPredictor, ModelType, ModelStatus, create_signal_classifier"
    new_import = "from ml.simple_model import SimpleLinearModel, ModelType, ModelStatus, create_signal_classifier"
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        print("✅ Import corrigé: SimpleLinearPredictor → SimpleLinearModel")
    else:
        # Peut-être que le format est légèrement différent
        import re
        pattern = r'from ml\.simple_model import ([^,]+), ModelType, ModelStatus, create_signal_classifier'
        match = re.search(pattern, content)
        if match:
            old_line = match.group(0)
            new_line = f"from ml.simple_model import SimpleLinearModel, ModelType, ModelStatus, create_signal_classifier"
            content = content.replace(old_line, new_line)
            print(f"✅ Import corrigé: {match.group(1)} → SimpleLinearModel")
    
    # Option alternative: Si SimpleLinearPredictor est le bon nom, changer l'alias
    # Chercher et remplacer l'alias
    if "SimpleMLModel = SimpleLinearModel" in content:
        # Si on a changé l'import ci-dessus, cette ligne devrait maintenant fonctionner
        # Sinon, on peut la changer pour utiliser SimpleLinearPredictor
        if "SimpleLinearModel" not in content.split("SimpleMLModel = SimpleLinearModel")[0]:
            # SimpleLinearModel n'est pas importé, utiliser SimpleLinearPredictor
            content = content.replace(
                "SimpleMLModel = SimpleLinearModel",
                "SimpleMLModel = SimpleLinearPredictor  # Alias pour compatibilité"
            )
            print("✅ Alias corrigé: SimpleMLModel = SimpleLinearPredictor")
    
    # Écrire le fichier corrigé
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Fichier corrigé!")
    
    # Vérifier ce qui est réellement exporté par simple_model.py
    print("\n" + "=" * 80)
    print("VÉRIFICATION: Qu'est-ce qui est exporté par simple_model.py?")
    print("=" * 80)
    
    try:
        import ml.simple_model as sm
        exports = [name for name in dir(sm) if not name.startswith('_')]
        
        print("Exports trouvés dans simple_model.py:")
        for export in sorted(exports):
            if 'Simple' in export and 'Model' in export:
                print(f"  ✓ {export}")
        
        # Vérifier spécifiquement
        if hasattr(sm, 'SimpleLinearModel'):
            print("\n✅ SimpleLinearModel est bien exporté!")
        if hasattr(sm, 'SimpleLinearPredictor'):
            print("✅ SimpleLinearPredictor est aussi exporté!")
            
    except Exception as e:
        print(f"Impossible de vérifier les exports: {e}")
    
    return True

def test_import():
    """Test final de l'import"""
    
    print("\n" + "=" * 80)
    print("TEST FINAL")
    print("=" * 80)
    
    try:
        # Nettoyer cache
        import sys
        modules_to_remove = [m for m in sys.modules if m.startswith('ml')]
        for m in modules_to_remove:
            del sys.modules[m]
        
        # Test import
        import ml
        print("✅ Import ml réussi!")
        
        # Vérifier les composants
        from ml import ModelTrainer
        print("✅ ModelTrainer importé!")
        
        from ml import SimpleLinearModel
        print("✅ SimpleLinearModel importé!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if fix_import_mismatch():
        if test_import():
            print("\n🎉 SUCCÈS! Le module ML fonctionne maintenant!")
            print("\nPour confirmer:")
            print('python -c "import ml; print(\'✅ Module ML OK\')"')
        else:
            print("\n⚠️ L'import échoue encore. Vérifiez les noms dans simple_model.py")
    else:
        print("\n❌ Échec de la correction")