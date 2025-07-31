#!/usr/bin/env python3
"""
Analyse et correction définitive de model_trainer.py
"""

import shutil
from pathlib import Path

def analyze_model_trainer():
    """Analyse le fichier model_trainer.py pour trouver le problème"""
    
    file_path = Path("ml/model_trainer.py")
    
    print("ANALYSE DE model_trainer.py")
    print("=" * 80)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Trouver les lignes importantes
    import_lines = []
    alias_line = None
    ml_imports_start = None
    
    for i, line in enumerate(lines):
        # Chercher les imports de ML
        if "from ml.simple_model import" in line:
            import_lines.append((i+1, line.strip()))
            if ml_imports_start is None:
                ml_imports_start = i
        elif "from ml.data_processor import" in line:
            import_lines.append((i+1, line.strip()))
        elif "from ml.model_validator import" in line:
            import_lines.append((i+1, line.strip()))
        
        # Chercher l'alias problématique
        if "SimpleMLModel = SimpleLinearModel" in line and i < 250:
            alias_line = (i+1, line.strip())
    
    print("Imports ML trouvés:")
    for line_num, content in import_lines:
        print(f"  Ligne {line_num}: {content}")
    
    print(f"\nAlias problématique:")
    if alias_line:
        print(f"  Ligne {alias_line[0]}: {alias_line[1]}")
    
    if alias_line and import_lines:
        if alias_line[0] < import_lines[0][0]:
            print("\n❌ PROBLÈME: L'alias est AVANT les imports ML!")
            return True, alias_line[0] - 1, ml_imports_start
    
    return False, None, None

def fix_model_trainer_definitely():
    """Correction définitive du problème"""
    
    file_path = Path("ml/model_trainer.py")
    backup_path = file_path.with_suffix('.py.backup2')
    
    # Backup
    shutil.copy2(file_path, backup_path)
    print(f"\nBackup créé: {backup_path}")
    
    # Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Stratégie: 
    # 1. Supprimer la ligne SimpleMLModel = SimpleLinearModel où qu'elle soit
    # 2. L'ajouter APRÈS la section "# ML Components integration"
    
    new_lines = []
    removed_line = None
    ml_imports_section_end = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Supprimer l'alias problématique
        if "SimpleMLModel = SimpleLinearModel" in line:
            print(f"Suppression ligne {i+1}: {line.strip()}")
            removed_line = line.strip()
            i += 1
            continue
        
        # Détecter la fin de la section ML imports
        if "from ml.model_validator import" in line:
            ml_imports_section_end = i + 1
        
        new_lines.append(line)
        i += 1
    
    # Si on a trouvé la section ML imports, ajouter l'alias après
    if ml_imports_section_end and removed_line:
        # Insérer après les imports ML
        insert_pos = ml_imports_section_end
        
        # Ajouter une ligne vide si nécessaire
        if insert_pos < len(new_lines) and new_lines[insert_pos].strip():
            new_lines.insert(insert_pos, "\n")
            insert_pos += 1
        
        # Ajouter l'alias avec commentaire
        new_lines.insert(insert_pos, "# Alias pour compatibilité avec __init__.py\n")
        new_lines.insert(insert_pos + 1, f"{removed_line}\n")
        
        print(f"\nAlias réinséré après la ligne {ml_imports_section_end}")
    
    # Si on n'a pas trouvé où l'insérer, chercher "# Logger"
    elif removed_line:
        for i, line in enumerate(new_lines):
            if line.strip().startswith("# Logger") or line.strip().startswith("logger ="):
                # Insérer avant le logger
                new_lines.insert(i, "\n# Alias pour compatibilité\n")
                new_lines.insert(i + 1, f"{removed_line}\n")
                new_lines.insert(i + 2, "\n")
                print(f"\nAlias inséré avant le logger (ligne {i+1})")
                break
    
    # Écrire le fichier corrigé
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("\n✅ Fichier corrigé!")

def verify_fix():
    """Vérifier que la correction fonctionne"""
    
    print("\n" + "=" * 80)
    print("VÉRIFICATION DE LA CORRECTION")
    print("=" * 80)
    
    # Tester l'import
    try:
        # Nettoyer les imports en cache
        import sys
        modules_to_remove = [m for m in sys.modules if m.startswith('ml')]
        for m in modules_to_remove:
            del sys.modules[m]
        
        # Tester
        import ml
        print("✅ Import ml réussi!")
        
        # Vérifier que les composants sont disponibles
        from ml import SimpleLinearModel, ModelTrainer, ModelValidator
        print("✅ Tous les composants ML importés avec succès!")
        
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 1. Analyser le problème
    has_problem, alias_line, imports_start = analyze_model_trainer()
    
    if has_problem:
        print("\n" + "=" * 80)
        print("APPLICATION DE LA CORRECTION")
        print("=" * 80)
        
        # 2. Appliquer la correction
        fix_model_trainer_definitely()
        
        # 3. Vérifier
        if verify_fix():
            print("\n🎉 SUCCÈS! Le module ML est maintenant fonctionnel!")
        else:
            print("\n⚠️ La correction n'a pas résolu le problème.")
            print("Vérifiez manuellement ml/model_trainer.py")
    else:
        print("\n✅ Pas de problème détecté dans l'ordre des imports")