#!/usr/bin/env python3
"""
Script pour remplacer automatiquement les print() par logging
dans tous les fichiers Python du projet MIA_IA_SYSTEM

Usage:
    python scripts/fix_print_statements.py [--dry-run] [--backup]
    
Options:
    --dry-run : Affiche les changements sans modifier les fichiers
    --backup  : Crée une sauvegarde .bak avant modification
"""

import os
import re
import sys
import shutil
import argparse
import logging
from pathlib import Path
from typing import List, Tuple, Dict

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Patterns de remplacement
REPLACEMENTS = {
    # print avec emoji warning
    r'print\s*\(\s*f?"⚠️\s*([^"]+)"\s*\)': r'logger.warning("\1")',
    r"print\s*\(\s*f?'⚠️\s*([^']+)'\s*\)": r'logger.warning("\1")',
    
    # print avec emoji error
    r'print\s*\(\s*f?"❌\s*([^"]+)"\s*\)': r'logger.error("\1")',
    r"print\s*\(\s*f?'❌\s*([^']+)'\s*\)": r'logger.error("\1")',
    
    # print avec emoji success
    r'print\s*\(\s*f?"✅\s*([^"]+)"\s*\)': r'logger.info("\1")',
    r"print\s*\(\s*f?'✅\s*([^']+)'\s*\)": r'logger.info("\1")',
    
    # print avec emoji info
    r'print\s*\(\s*f?"🔍\s*([^"]+)"\s*\)': r'logger.debug("\1")',
    r"print\s*\(\s*f?'🔍\s*([^']+)'\s*\)": r'logger.debug("\1")',
    
    # print générique avec f-string
    r'print\s*\(\s*f"([^"]+)"\s*\)': r'logger.info("\1")',
    r"print\s*\(\s*f'([^']+)'\s*\)": r'logger.info("\1")',
    
    # print générique simple
    r'print\s*\(\s*"([^"]+)"\s*\)': r'logger.info("\1")',
    r"print\s*\(\s*'([^']+)'\s*\)": r'logger.info("\1")',
}

# Fichiers à exclure
EXCLUDE_PATTERNS = [
    '**/venv/**',
    '**/__pycache__/**',
    '**/.git/**',
    '**/build/**',
    '**/dist/**',
    '**/*.egg-info/**',
]

def should_process_file(filepath: Path) -> bool:
    """Détermine si un fichier doit être traité"""
    # Vérifier les patterns d'exclusion
    for pattern in EXCLUDE_PATTERNS:
        if filepath.match(pattern):
            return False
    
    # Traiter uniquement les fichiers Python
    return filepath.suffix == '.py'

def find_print_statements(content: str) -> List[Tuple[int, str]]:
    """Trouve tous les print statements dans le contenu"""
    print_statements = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if 'print(' in line and not line.strip().startswith('#'):
            print_statements.append((i + 1, line.strip()))
    
    return print_statements

def fix_print_statements(content: str) -> Tuple[str, int]:
    """Remplace les print() par logging approprié"""
    modified_content = content
    changes_count = 0
    
    # Appliquer chaque pattern de remplacement
    for pattern, replacement in REPLACEMENTS.items():
        new_content, count = re.subn(pattern, replacement, modified_content)
        changes_count += count
        modified_content = new_content
    
    return modified_content, changes_count

def ensure_logging_import(content: str) -> str:
    """S'assure que logging est importé"""
    if 'import logging' not in content:
        # Trouver où insérer l'import
        lines = content.split('\n')
        insert_index = 0
        
        # Après les docstrings
        in_docstring = False
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                if not in_docstring:
                    in_docstring = True
                else:
                    insert_index = i + 1
                    break
        
        # Après les imports existants
        for i in range(insert_index, len(lines)):
            if lines[i].startswith('import ') or lines[i].startswith('from '):
                insert_index = i + 1
            elif lines[i].strip() and not lines[i].startswith('#'):
                break
        
        # Insérer l'import logging
        lines.insert(insert_index, 'import logging')
        lines.insert(insert_index + 1, '')
        lines.insert(insert_index + 2, '# Configure logging')
        lines.insert(insert_index + 3, 'logger = logging.getLogger(__name__)')
        lines.insert(insert_index + 4, '')
        
        return '\n'.join(lines)
    
    # Vérifier si logger est défini
    if 'logger = logging.getLogger' not in content:
        lines = content.split('\n')
        
        # Trouver où logging est importé
        for i, line in enumerate(lines):
            if 'import logging' in line:
                # Ajouter logger après l'import
                lines.insert(i + 1, '')
                lines.insert(i + 2, '# Configure logging')
                lines.insert(i + 3, 'logger = logging.getLogger(__name__)')
                break
        
        return '\n'.join(lines)
    
    return content

def process_file(filepath: Path, dry_run: bool = False, backup: bool = False) -> Dict[str, any]:
    """Traite un fichier Python"""
    result = {
        'filepath': str(filepath),
        'processed': False,
        'changes': 0,
        'print_statements': [],
        'error': None
    }
    
    try:
        # Lire le contenu
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Trouver les print statements
        print_statements = find_print_statements(original_content)
        result['print_statements'] = print_statements
        
        if not print_statements:
            return result
        
        # Corriger les print statements
        modified_content, changes = fix_print_statements(original_content)
        result['changes'] = changes
        
        if changes > 0:
            # Ajouter import logging si nécessaire
            modified_content = ensure_logging_import(modified_content)
            
            if not dry_run:
                # Backup si demandé
                if backup:
                    backup_path = filepath.with_suffix(filepath.suffix + '.bak')
                    shutil.copy2(filepath, backup_path)
                
                # Écrire le fichier modifié
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
            
            result['processed'] = True
        
    except Exception as e:
        result['error'] = str(e)
        logger.error(f"Erreur traitement {filepath}: {e}")
    
    return result

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Remplace print() par logging dans les fichiers Python')
    parser.add_argument('--dry-run', action='store_true', help='Affiche les changements sans modifier')
    parser.add_argument('--backup', action='store_true', help='Crée des backups .bak')
    parser.add_argument('--path', default='.', help='Chemin du projet (défaut: répertoire courant)')
    args = parser.parse_args()
    
    # Trouver tous les fichiers Python
    project_path = Path(args.path)
    if not project_path.exists():
        logger.error(f"Chemin invalide: {project_path}")
        sys.exit(1)
    
    python_files = []
    for filepath in project_path.rglob('*.py'):
        if should_process_file(filepath):
            python_files.append(filepath)
    
    logger.info(f"Trouvé {len(python_files)} fichiers Python à analyser")
    
    if args.dry_run:
        logger.info("MODE DRY-RUN : Aucun fichier ne sera modifié")
    
    # Traiter chaque fichier
    total_changes = 0
    files_modified = 0
    
    for filepath in python_files:
        result = process_file(filepath, args.dry_run, args.backup)
        
        if result['print_statements']:
            logger.info(f"\n{filepath}:")
            for line_num, statement in result['print_statements']:
                logger.info(f"  Ligne {line_num}: {statement}")
            
            if result['processed']:
                logger.info(f"  → {result['changes']} changements appliqués")
                total_changes += result['changes']
                files_modified += 1
    
    # Résumé
    logger.info("\n" + "="*60)
    logger.info(f"RÉSUMÉ:")
    logger.info(f"  Fichiers analysés: {len(python_files)}")
    logger.info(f"  Fichiers modifiés: {files_modified}")
    logger.info(f"  Total changements: {total_changes}")
    
    if args.dry_run:
        logger.info("\nPour appliquer les changements, relancez sans --dry-run")

if __name__ == "__main__":
    main()