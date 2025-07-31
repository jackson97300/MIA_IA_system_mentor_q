#!/usr/bin/env python3
"""
Correction manuelle directe du fichier ml/__init__.py
"""

import shutil
from pathlib import Path

def manual_fix_init():
    """Correction manuelle directe de __init__.py"""
    
    init_path = Path("ml/__init__.py")
    backup_path = init_path.with_suffix('.py.backup_manual')
    
    print("CORRECTION MANUELLE DE ml/__init__.py")
    print("=" * 80)
    
    # Backup
    shutil.copy2(init_path, backup_path)
    print(f"Backup créé: {backup_path}")
    
    # Lire le fichier
    with open(init_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Chercher la ligne qui importe depuis simple_model
    new_lines = []
    import_found = False
    in_simple_model_import = False
    
    for i, line in enumerate(lines):
        # Détecter le début de l'import simple_model
        if "from .simple_model import" in line:
            import_found = True
            in_simple_model_import = True
            
            # Si c'est un import sur une ligne
            if ")" in line:
                # Import complet sur une ligne
                if "SimpleLinearModel" not in line:
                    # Ajouter SimpleLinearModel
                    if "(" in line:
                        # Format avec parenthèses
                        line = line.replace("import (", "import (\n    SimpleLinearModel,\n    ")
                    else:
                        # Format simple
                        parts = line.split("import ")
                        if len(parts) == 2:
                            imports = parts[1].strip()
                            line = f"{parts[0]}import SimpleLinearModel, {imports}"
                    print("✅ Ajouté SimpleLinearModel à l'import")
                in_simple_model_import = False
        
        # Si on est dans un import multi-lignes
        elif in_simple_model_import and not line.strip().startswith("#"):
            # Vérifier si c'est la première ligne après "import ("
            if i > 0 and "import (" in lines[i-1]:
                # Ajouter SimpleLinearModel en premier
                new_lines.append("    SimpleLinearModel,\n")
                print("✅ Ajouté SimpleLinearModel en première position")
                in_simple_model_import = False
            elif ")" in line:
                # Fin de l'import
                in_simple_model_import = False
        
        new_lines.append(line)
    
    # Si on n'a pas trouvé d'import simple_model, l'ajouter
    if not import_found:
        # Chercher où l'ajouter (après les imports de dataclasses par exemple)
        for i, line in enumerate(new_lines):
            if "# === SIMPLE MODEL" in line:
                # Ajouter l'import après ce commentaire
                new_lines.insert(i+1, "from .simple_model import SimpleLinearModel\n")
                print("✅ Ajouté import SimpleLinearModel")
                break
    
    # Maintenant, vérifier __all__
    in_all = False
    all_start_index = -1
    
    for i, line in enumerate(new_lines):
        if "__all__ = [" in line:
            in_all = True
            all_start_index = i
        elif in_all and "]" in line:
            # Fin de __all__
            # Vérifier si SimpleLinearModel est dedans
            all_content = ''.join(new_lines[all_start_index:i+1])
            if "'SimpleLinearModel'" not in all_content and '"SimpleLinearModel"' not in all_content:
                # L'ajouter
                # Chercher où l'insérer (après un autre export simple_model)
                for j in range(all_start_index, i):
                    if "'ModelType'" in new_lines[j] or '"ModelType"' in new_lines[j]:
                        # Ajouter après ModelType
                        new_lines.insert(j+1, "    'SimpleLinearModel',\n")
                        print("✅ Ajouté 'SimpleLinearModel' à __all__")
                        break
            in_all = False
    
    # Écrire le fichier corrigé
    with open(init_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("\n✅ Fichier corrigé!")

def verify_fix():
    """Vérifier que la correction fonctionne"""
    
    print("\n" + "=" * 80)
    print("VÉRIFICATION")
    print("=" * 80)
    
    # Afficher le contenu pertinent du fichier
    with open("ml/__init__.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier l'import
    if "from .simple_model import" in content:
        start = content.find("from .simple_model import")
        end = content.find("\n", start)
        if ")" in content[start:]:
            # Import multi-lignes
            end = content.find(")", start) + 1
        import_section = content[start:end]
        print("Import simple_model:")
        print(import_section)
        
        if "SimpleLinearModel" in import_section:
            print("✅ SimpleLinearModel est importé")
        else:
            print("❌ SimpleLinearModel n'est PAS importé")
    
    # Test final
    print("\nTest import...")
    try:
        # Nettoyer cache
        import sys
        for module in list(sys.modules.keys()):
            if module.startswith('ml'):
                del sys.modules[module]
        
        # Test
        import ml
        from ml import SimpleLinearModel
        print("✅ Import réussi!")
        print(f"Type: {type(SimpleLinearModel)}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def show_manual_instructions():
    """Instructions pour correction manuelle si nécessaire"""
    
    print("\n" + "=" * 80)
    print("INSTRUCTIONS MANUELLES (si le script échoue)")
    print("=" * 80)
    print("""
1. Ouvrez ml/__init__.py dans votre éditeur

2. Trouvez la section qui commence par:
   from .simple_model import (

3. Ajoutez SimpleLinearModel en PREMIÈRE position:
   from .simple_model import (
       SimpleLinearModel,    # <-- AJOUTER CETTE LIGNE
       ModelType,
       ModelStatus,
       ...
   )

4. Trouvez la section __all__ = [

5. Après 'ModelType', ajoutez:
   'ModelType',
   'SimpleLinearModel',    # <-- AJOUTER CETTE LIGNE

6. Sauvegardez le fichier

7. Testez avec:
   python -c "import ml; from ml import SimpleLinearModel; print('✅ OK!')"
""")

if __name__ == "__main__":
    # Appliquer la correction
    manual_fix_init()
    
    # Vérifier
    if verify_fix():
        print("\n🎉 SUCCÈS! Le problème est résolu!")
        print("\nVous pouvez maintenant utiliser:")
        print('python -c "import config; import core; import features; import strategies; import execution; import monitoring; import ml; import data; import performance; print(\'✅ Tous les imports fonctionnent !\')"')
    else:
        print("\n⚠️ La correction automatique a échoué.")
        show_manual_instructions()