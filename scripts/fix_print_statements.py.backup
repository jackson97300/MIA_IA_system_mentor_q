#!/usr/bin/env python3
"""
Script pour corriger les print statements Python 2 vers Python 3
"""

import re
import sys
from pathlib import Path

def fix_print_in_file(filepath):
    """Corrige les print statements dans un fichier"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern pour détecter print statements Python 2
    pattern = r'print\s+([^(].*?)$'
    replacement = r'print(\1)'
    
    # Remplacer
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    """Fonction principale"""
    if len(sys.argv) > 1:
        filepath = Path(sys.argv[1])
        if filepath.exists():
            if fix_print_in_file(filepath):
                print(f"✅ Corrigé: {filepath}")
            else:
                print(f"ℹ️ Aucun changement: {filepath}")
        else:
            print(f"❌ Fichier non trouvé: {filepath}")
    else:
        print("Usage: python fix_print_statements.py <fichier.py>")

if __name__ == "__main__":
    main()
