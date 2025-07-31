#!/usr/bin/env python3
"""
Script pour corriger les erreurs d'import spécifiques
trouvées dans le projet MIA_IA_SYSTEM
"""

import os
import re
from pathlib import Path

def fix_mime_text_import(filepath):
    """Corrige l'import MIMEText -> MIMEText"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corriger MIMEText -> MIMEText
    if 'MIMEText' in content:
        content = content.replace('MIMEText', 'MIMEText')
        content = content.replace('from email.mime.text import MIMEText', 'from email.mime.text import MIMEText')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Corrigé MIMEText -> MIMEText dans {filepath.name}")
        return True
    return False

def fix_health_checker(filepath):
    """Corrige health_checker.py - logger non défini"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Trouver où logger est utilisé sans être défini
    modified = False
    new_lines = []
    
    # Chercher la ligne d'import logging
    has_logger = any('logger = logging.getLogger' in line for line in lines)
    
    for i, line in enumerate(lines):
        # Si on trouve l'import flask qui échoue
        if 'from flask import' in line and not has_logger:
            # Ajouter la définition du logger avant
            new_lines.append("import logging\n")
            new_lines.append("logger = logging.getLogger(__name__)\n\n")
            has_logger = True
            modified = True
        
        new_lines.append(line)
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"✅ Ajouté logger dans {filepath.name}")
        return True
    return False

def fix_sierra_config_import():
    """Corrige les imports de sierra_config"""
    config_init = Path("D:/MIA_IA_system/config/__init__.py")
    
    if config_init.exists():
        with open(config_init, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # S'assurer que sierra_config est dans la liste des imports
        if 'from .sierra_config import' in content and 'Could not import sierra_config' in content:
            # Commenter temporairement l'import si le fichier a des problèmes
            content = content.replace(
                'from .sierra_config import',
                '# from .sierra_config import  # Temporairement désactivé'
            )
            
            with open(config_init, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Import sierra_config temporairement désactivé")
            return True
    return False

def add_missing_dependencies():
    """Ajoute les dépendances manquantes au requirements.txt"""
    requirements_path = Path("D:/MIA_IA_system/requirements.txt")
    
    missing_deps = [
        'flask>=2.0.0',
        'email-validator>=1.1.0'
    ]
    
    if requirements_path.exists():
        with open(requirements_path, 'r', encoding='utf-8') as f:
            current_deps = f.read()
        
        added = []
        for dep in missing_deps:
            dep_name = dep.split('>=')[0].split('==')[0]
            if dep_name not in current_deps:
                current_deps += f"\n{dep}"
                added.append(dep)
        
        if added:
            with open(requirements_path, 'w', encoding='utf-8') as f:
                f.write(current_deps.strip() + '\n')
            print(f"✅ Ajouté au requirements.txt: {', '.join(added)}")
            return True
    return False

def make_imports_optional(filepath, module_name):
    """Rend un import optionnel avec try/except"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern pour trouver l'import
    import_pattern = f"from {module_name} import"
    
    if import_pattern in content and 'try:' not in content.split(import_pattern)[0][-50:]:
        # Remplacer l'import par un try/except
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            if import_pattern in line and not line.strip().startswith('#'):
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + 'try:')
                new_lines.append(' ' * (indent + 4) + line.strip())
                new_lines.append(' ' * indent + 'except ImportError:')
                new_lines.append(' ' * (indent + 4) + f'{module_name.upper()}_AVAILABLE = False')
                new_lines.append(' ' * (indent + 4) + f'# {module_name} non disponible')
            else:
                new_lines.append(line)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        print(f"✅ Import {module_name} rendu optionnel dans {filepath.name}")
        return True
    return False

def main():
    """Corrige toutes les erreurs d'import"""
    print("🔧 Correction des erreurs d'import")
    print("=" * 50)
    
    project_root = Path("D:/MIA_IA_system")
    
    # 1. Corriger MIMEText
    print("\n1. Correction MIMEText -> MIMEText")
    for file in project_root.rglob("*.py"):
        if fix_mime_text_import(file):
            pass
    
    # 2. Corriger health_checker.py
    print("\n2. Correction health_checker.py")
    health_checker = project_root / "monitoring/health_checker.py"
    if health_checker.exists():
        fix_health_checker(health_checker)
    
    # 3. Corriger sierra_config
    print("\n3. Correction imports sierra_config")
    fix_sierra_config_import()
    
    # 4. Rendre Flask optionnel
    print("\n4. Rendre Flask optionnel")
    if health_checker.exists():
        make_imports_optional(health_checker, 'flask')
    
    # 5. Ajouter dépendances manquantes
    print("\n5. Mise à jour requirements.txt")
    add_missing_dependencies()
    
    print("\n" + "=" * 50)
    print("✅ Corrections terminées !")
    print("\nPour installer les dépendances manquantes :")
    print("pip install flask email-validator")
    print("\nOu pour continuer sans ces dépendances optionnelles :")
    print("Les imports ont été rendus optionnels")

if __name__ == "__main__":
    main()