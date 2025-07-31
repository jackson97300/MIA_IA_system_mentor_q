#!/usr/bin/env python3
"""
Correction simple et directe pour exporter SimpleLinearModel dans ml/__init__.py
"""

import shutil
from pathlib import Path

def fix_simple_linear_model_export():
    """Ajoute SimpleLinearModel aux exports de ml/__init__.py"""
    
    init_file = Path("ml/__init__.py")
    
    # Backup
    backup_file = init_file.with_suffix('.py.backup_simple')
    shutil.copy2(init_file, backup_file)
    print(f"✅ Backup créé: {backup_file}")
    
    # Lire le fichier
    with open(init_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("\n🔍 Analyse du fichier ml/__init__.py...")
    
    # Chercher où SimpleLinearModel devrait être importé
    simple_model_import_line = None
    all_list_start = None
    
    for i, line in enumerate(lines):
        # Chercher l'import depuis simple_model
        if "from .simple_model import" in line:
            simple_model_import_line = i
            print(f"  Trouvé import simple_model ligne {i+1}")
            
        # Chercher le début de __all__
        if "__all__ = [" in line:
            all_list_start = i
            print(f"  Trouvé __all__ ligne {i+1}")
    
    # Correction 1: Vérifier que SimpleLinearModel est importé
    fixed_import = False
    if simple_model_import_line is not None:
        import_line = lines[simple_model_import_line]
        
        if "SimpleLinearModel" not in import_line:
            print("\n❌ SimpleLinearModel n'est pas importé")
            
            # Si c'est un import multi-lignes avec parenthèses
            if "(" in import_line:
                # Ajouter après la parenthèse
                lines[simple_model_import_line] = import_line.replace(
                    "from .simple_model import (",
                    "from .simple_model import (\n    # Classe principale\n    SimpleLinearModel,"
                )
            else:
                # Import simple ligne - le remplacer
                lines[simple_model_import_line] = "from .simple_model import SimpleLinearModel, ModelType, ModelStatus\n"
            
            fixed_import = True
            print("✅ Ajouté SimpleLinearModel à l'import")
    
    # Correction 2: Vérifier que SimpleLinearModel est dans __all__
    fixed_all = False
    if all_list_start is not None:
        # Chercher si SimpleLinearModel est déjà dans __all__
        found_in_all = False
        for i in range(all_list_start, len(lines)):
            if "'SimpleLinearModel'" in lines[i]:
                found_in_all = True
                break
            if "]" in lines[i]:  # Fin de __all__
                break
        
        if not found_in_all:
            print("\n❌ SimpleLinearModel n'est pas dans __all__")
            
            # Trouver où l'ajouter (après le commentaire SIMPLE MODEL)
            for i in range(all_list_start, len(lines)):
                if "# === SIMPLE MODEL ===" in lines[i] or "'SimpleLinearModel'" in lines[i-1]:
                    # Insérer à la ligne suivante
                    lines.insert(i+1, "    'SimpleLinearModel',\n")
                    fixed_all = True
                    print("✅ Ajouté SimpleLinearModel à __all__")
                    break
    
    # Écrire les modifications
    if fixed_import or fixed_all:
        with open(init_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("\n✅ Fichier ml/__init__.py corrigé!")
    else:
        print("\n✅ SimpleLinearModel semble déjà être correctement exporté")
    
    # Test
    print("\n🧪 Test de l'import...")
    try:
        import sys
        # Nettoyer le cache
        if 'ml' in sys.modules:
            del sys.modules['ml']
        if 'ml.simple_model' in sys.modules:
            del sys.modules['ml.simple_model']
        
        # Tester l'import
        from ml import SimpleLinearModel
        print("✅ SUCCESS: SimpleLinearModel peut être importé depuis ml!")
        
        # Tester aussi les autres composants
        from ml import ModelTrainer, ModelValidator
        print("✅ SUCCESS: ModelTrainer et ModelValidator aussi accessibles!")
        
        print("\n🎉 Tout fonctionne correctement!")
        
    except ImportError as e:
        print(f"\n❌ ERREUR: {e}")
        print("\nVérifiez manuellement ml/__init__.py")
        print("Assurez-vous que :")
        print("1. SimpleLinearModel est importé depuis .simple_model")
        print("2. 'SimpleLinearModel' est dans la liste __all__")

if __name__ == "__main__":
    fix_simple_linear_model_export()
    
    print("\n" + "="*60)
    print("Pour tester manuellement :")
    print("="*60)
    print('python -c "from ml import SimpleLinearModel; print(\'OK\')"')