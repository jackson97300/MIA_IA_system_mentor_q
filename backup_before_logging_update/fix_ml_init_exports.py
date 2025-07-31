#!/usr/bin/env python3
"""
Correction des exports dans ml/__init__.py
"""

import shutil
from pathlib import Path

def fix_ml_init():
    """Vérifie et corrige les exports dans ml/__init__.py"""
    
    init_path = Path("ml/__init__.py")
    backup_path = init_path.with_suffix('.py.backup_exports')
    
    # Backup
    shutil.copy2(init_path, backup_path)
    print(f"Backup créé: {backup_path}")
    
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si SimpleLinearModel est bien importé
    if "from .simple_model import SimpleLinearModel" not in content:
        print("❌ SimpleLinearModel n'est pas importé dans __init__.py")
        
        # Trouver où ajouter l'import
        if "from .simple_model import" in content:
            # Ajouter à l'import existant
            content = content.replace(
                "from .simple_model import (",
                "from .simple_model import (\n    SimpleLinearModel,  # Classe principale"
            )
            print("✅ Ajouté SimpleLinearModel à l'import existant")
    
    # Vérifier si SimpleLinearModel est dans __all__
    if "'SimpleLinearModel'" not in content:
        print("❌ SimpleLinearModel n'est pas dans __all__")
        
        # Ajouter à __all__
        if "__all__ = [" in content:
            # Trouver la section SIMPLE MODEL dans __all__
            lines = content.split('\n')
            new_lines = []
            added = False
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                
                # Ajouter après le commentaire "# === SIMPLE MODEL ==="
                if "# === SIMPLE MODEL ===" in line and not added:
                    # Chercher les prochaines lignes
                    for j in range(i+1, min(i+5, len(lines))):
                        if "'SimpleLinearModel'" not in lines[j]:
                            new_lines.append("    'SimpleLinearModel',")
                            added = True
                            print("✅ Ajouté SimpleLinearModel à __all__")
                            break
            
            content = '\n'.join(new_lines)
    
    # Écrire le fichier corrigé
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ ml/__init__.py corrigé")

def test_ml_imports():
    """Test que tous les imports ML fonctionnent"""
    
    print("\n" + "="*60)
    print("TEST DES IMPORTS ML")
    print("="*60)
    
    try:
        # Nettoyer cache
        import sys
        if 'ml' in sys.modules:
            del sys.modules['ml']
        
        # Test imports individuels
        from ml import SimpleLinearModel
        print("✅ SimpleLinearModel importé")
        
        from ml import ModelTrainer
        print("✅ ModelTrainer importé")
        
        from ml import ModelValidator
        print("✅ ModelValidator importé")
        
        from ml import create_signal_classifier, create_battle_navale_trainer
        print("✅ Factory functions importées")
        
        print("\n🎉 Tous les composants ML sont accessibles!")
        return True
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        return False

if __name__ == "__main__":
    fix_ml_init()
    test_ml_imports()