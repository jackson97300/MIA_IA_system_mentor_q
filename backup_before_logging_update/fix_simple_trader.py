#!/usr/bin/env python3
"""
Script pour corriger l'erreur de syntaxe dans simple_trader.py
Trouve et supprime le 'return' orphelin
"""

import re
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)


def fix_simple_trader():
    """Corrige l'erreur de syntaxe dans simple_trader.py"""
    
    file_path = Path("execution/simple_trader.py")
    
    if not file_path.exists():
        logger.error("Fichier {file_path} non trouvé!")
        return False
    
    # Lire le contenu
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Chercher le return orphelin autour de la ligne 1381
    fixed = False
    new_lines = []
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Chercher un 'return' seul sur une ligne en dehors d'une fonction
        if 1375 <= line_num <= 1385:  # Autour de la ligne 1381
            stripped = line.strip()
            if stripped == 'return':
                logger.info("Trouvé 'return' orphelin à la ligne {line_num} - Suppression")
                fixed = True
                continue  # Skip cette ligne
            elif stripped.startswith('return ') and line_num == 1381:
                # C'est peut-être un return avec valeur mais mal placé
                logger.warning("Return statement trouvé ligne {line_num}: {stripped}")
                # Le commenter
                new_lines.append(f"    # FIXME: {line}")
                fixed = True
                continue
        
        new_lines.append(line)
    
    if not fixed:
        # Recherche plus large
        logger.debug("Recherche étendue du return orphelin...")
        new_lines = []
        indent_level = 0
        in_function = False
        
        for i, line in enumerate(lines):
            # Détecter les fonctions
            if line.strip().startswith('def ') or line.strip().startswith('async def '):
                in_function = True
                indent_level = len(line) - len(line.lstrip())
            elif in_function and line.strip() and len(line) - len(line.lstrip()) <= indent_level:
                in_function = False
            
            # Si on trouve un return en dehors d'une fonction
            if line.strip() == 'return' and not in_function:
                logger.info("Trouvé 'return' orphelin à la ligne {i+1} - Suppression")
                fixed = True
                continue
            
            new_lines.append(line)
    
    if fixed:
        # Sauvegarder le fichier corrigé
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        logger.info("Fichier corrigé avec succès!")
        return True
    else:
        logger.error("Aucun 'return' orphelin trouvé")
        
        # Afficher le contexte autour de la ligne 1381
        logger.info("\n📋 Contexte autour de la ligne 1381:")
        for i in range(max(0, 1380-5), min(len(lines), 1381+5)):
            logger.info("{i+1}: {lines[i].rstrip()}")
        
        return False

def check_syntax():
    """Vérifie la syntaxe après correction"""
    import subprocess
    
    result = subprocess.run(
        ["python", "-m", "py_compile", "execution/simple_trader.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        logger.info("Syntaxe valide!")
        return True
    else:
        logger.error("Erreur de syntaxe:\n{result.stderr}")
        return False

if __name__ == "__main__":
    logger.info("🔧 Correction de simple_trader.py...")
    
    if fix_simple_trader():
        logger.info("\n🔍 Vérification de la syntaxe...")
        check_syntax()
    else:
        logger.info("\n💡 Solution alternative : Vérifier manuellement le fichier")
        logger.info("   Cherchez 'return' seul sur une ligne en dehors d'une fonction")