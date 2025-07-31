#!/usr/bin/env python3
"""
Vérification directe de ce qui est exporté dans les fichiers ML
"""

from pathlib import Path
import re

def check_simple_model_exports():
    """Vérifie ce qui est dans simple_model.py"""
    
    print("VÉRIFICATION DE simple_model.py")
    print("=" * 80)
    
    simple_model_path = Path("ml/simple_model.py")
    
    if not simple_model_path.exists():
        print("❌ Fichier ml/simple_model.py introuvable!")
        return None
    
    with open(simple_model_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chercher les classes définies
    class_pattern = r'^class\s+(\w+)'
    classes = re.findall(class_pattern, content, re.MULTILINE)
    
    print("Classes trouvées:")
    for cls in classes:
        if 'Simple' in cls:
            print(f"  ✓ {cls}")
    
    # Chercher les alias éventuels
    alias_pattern = r'^(\w+)\s*=\s*(\w+)\s*$'
    aliases = re.findall(alias_pattern, content, re.MULTILINE)
    
    if aliases:
        print("\nAlias trouvés:")
        for alias, original in aliases:
            if 'Simple' in alias or 'Simple' in original:
                print(f"  ✓ {alias} = {original}")
    
    # Chercher spécifiquement SimpleLinearModel et SimpleLinearPredictor
    has_linear_model = 'class SimpleLinearModel' in content
    has_linear_predictor = 'class SimpleLinearPredictor' in content
    has_predictor_alias = 'SimpleLinearPredictor = SimpleLinearModel' in content
    
    print(f"\nRésumé:")
    print(f"  - SimpleLinearModel défini: {has_linear_model}")
    print(f"  - SimpleLinearPredictor défini: {has_linear_predictor}")
    print(f"  - Alias SimpleLinearPredictor: {has_predictor_alias}")
    
    return {
        'classes': classes,
        'has_linear_model': has_linear_model,
        'has_linear_predictor': has_linear_predictor
    }

def check_init_imports():
    """Vérifie ce qui est importé dans __init__.py"""
    
    print("\n\nVÉRIFICATION DE ml/__init__.py")
    print("=" * 80)
    
    init_path = Path("ml/__init__.py")
    
    if not init_path.exists():
        print("❌ Fichier ml/__init__.py introuvable!")
        return
    
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chercher les imports depuis simple_model
    print("Imports depuis simple_model:")
    
    # Pattern pour import multi-lignes
    import_start = content.find("from .simple_model import")
    if import_start != -1:
        # Trouver la fin de l'import (parenthèse fermante ou fin de ligne)
        import_end = import_start
        paren_count = 0
        in_import = False
        
        for i, char in enumerate(content[import_start:], import_start):
            if char == '(':
                paren_count += 1
                in_import = True
            elif char == ')':
                paren_count -= 1
                if paren_count == 0 and in_import:
                    import_end = i + 1
                    break
            elif char == '\n' and not in_import:
                import_end = i
                break
        
        import_section = content[import_start:import_end]
        print(import_section)
        
        # Vérifier si SimpleLinearModel est importé
        if "SimpleLinearModel" in import_section:
            print("\n✓ SimpleLinearModel EST importé")
        else:
            print("\n❌ SimpleLinearModel N'EST PAS importé")
            
        if "SimpleLinearPredictor" in import_section:
            print("✓ SimpleLinearPredictor EST importé")
    
    # Chercher dans __all__
    print("\nContenu de __all__:")
    all_start = content.find("__all__ = [")
    if all_start != -1:
        all_end = content.find("]", all_start)
        all_section = content[all_start:all_end+1]
        
        if "SimpleLinearModel" in all_section:
            print("✓ SimpleLinearModel est dans __all__")
        else:
            print("❌ SimpleLinearModel n'est pas dans __all__")
            
        if "SimpleLinearPredictor" in all_section:
            print("✓ SimpleLinearPredictor est dans __all__")

def create_complete_fix():
    """Crée une correction complète basée sur l'analyse"""
    
    print("\n\nCRÉATION DE LA CORRECTION COMPLÈTE")
    print("=" * 80)
    
    # 1. Analyser simple_model.py
    simple_model_info = check_simple_model_exports()
    
    if not simple_model_info:
        return
    
    # 2. Déterminer quelle classe existe vraiment
    if simple_model_info['has_linear_model']:
        correct_name = "SimpleLinearModel"
        print(f"✓ Le nom correct est: {correct_name}")
    elif simple_model_info['has_linear_predictor']:
        correct_name = "SimpleLinearPredictor"
        print(f"✓ Le nom correct est: {correct_name}")
    else:
        print("❌ Aucune classe Simple* trouvée dans simple_model.py!")
        return
    
    # 3. Créer le script de correction
    fix_script = f'''#!/usr/bin/env python3
"""
Script de correction automatique généré
"""

import shutil
from pathlib import Path

def fix_all_files():
    """Corrige tous les fichiers pour utiliser {correct_name}"""
    
    # 1. Corriger ml/__init__.py
    init_path = Path("ml/__init__.py")
    backup_path = init_path.with_suffix('.py.backup_final')
    shutil.copy2(init_path, backup_path)
    
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # S'assurer que {correct_name} est importé
    if "from .simple_model import" in content and "{correct_name}" not in content:
        # Ajouter à l'import existant
        content = content.replace(
            "from .simple_model import (",
            "from .simple_model import (\\n    {correct_name},"
        )
    
    # S'assurer qu'il est dans __all__
    if "__all__ = [" in content and "'{correct_name}'" not in content:
        # Ajouter après un autre import de simple_model
        content = content.replace(
            "'ModelType',",
            "'ModelType',\\n    '{correct_name}',"
        )
    
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ ml/__init__.py corrigé")
    
    # 2. Corriger ml/model_trainer.py
    trainer_path = Path("ml/model_trainer.py")
    backup_path = trainer_path.with_suffix('.py.backup_final')
    shutil.copy2(trainer_path, backup_path)
    
    with open(trainer_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corriger l'import
    content = content.replace(
        "from ml.simple_model import SimpleLinearPredictor",
        "from ml.simple_model import {correct_name}"
    )
    
    # Corriger l'alias
    content = content.replace(
        "SimpleMLModel = SimpleLinearModel",
        "SimpleMLModel = {correct_name}"
    )
    
    with open(trainer_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ ml/model_trainer.py corrigé")
    
    # 3. Si nécessaire, créer un alias dans simple_model.py
    if "{correct_name}" == "SimpleLinearModel":
        # Ajouter alias pour SimpleLinearPredictor si utilisé ailleurs
        simple_path = Path("ml/simple_model.py")
        with open(simple_path, 'a', encoding='utf-8') as f:
            f.write("\\n\\n# Alias pour compatibilité\\nSimpleLinearPredictor = SimpleLinearModel\\n")
        print("✅ Alias ajouté dans simple_model.py")

if __name__ == "__main__":
    fix_all_files()
    print("\\n✅ Toutes les corrections appliquées!")
    print("\\nTestez avec:")
    print('python -c "import ml; from ml import {correct_name}; print(\\'✅ OK!\\')"')
'''
    
    # Sauvegarder le script
    fix_path = Path("fix_ml_final.py")
    with open(fix_path, 'w', encoding='utf-8') as f:
        f.write(fix_script)
    
    print(f"\n✅ Script de correction créé: {fix_path}")
    print("\nPour appliquer la correction:")
    print("python fix_ml_final.py")

if __name__ == "__main__":
    # 1. Vérifier simple_model.py
    check_simple_model_exports()
    
    # 2. Vérifier __init__.py
    check_init_imports()
    
    # 3. Créer la correction
    create_complete_fix()