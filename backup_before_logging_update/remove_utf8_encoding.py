#!/usr/bin/env python3
"""
Script pour SUPPRIMER la configuration UTF-8 problématique de tous les fichiers
Cette configuration cause des crashes avec "I/O operation on closed file"
"""

import os
import re
from pathlib import Path

# Patterns à supprimer
PATTERNS_TO_REMOVE = [
    # Pattern 1: Version avec io.TextIOWrapper
    r'# Configuration encodage UTF-8\s*\nimport sys\s*\nimport io\s*\nif sys\.platform == "win32":\s*\n\s*sys\.stdout = io\.TextIOWrapper\(sys\.stdout\.buffer, encoding=\'utf-8\'\)\s*\n\s*sys\.stderr = io\.TextIOWrapper\(sys\.stderr\.buffer, encoding=\'utf-8\'\)\s*\n*',
    
    # Pattern 2: Version avec commentaires
    r'# Configuration encodage UTF-8[^\n]*\nimport sys[^\n]*\nimport io[^\n]*\nif sys\.platform[^\n]*:[^\n]*\n[^\n]*sys\.stdout[^\n]*\n[^\n]*sys\.stderr[^\n]*\n*',
    
    # Pattern 3: Version multi-lignes
    r'#.*?Configuration.*?UTF-8.*?\n.*?import sys.*?\n.*?import io.*?\n.*?if.*?sys\.platform.*?\n.*?sys\.stdout.*?\n.*?sys\.stderr.*?\n+',
]

def clean_file(filepath):
    """Nettoie un fichier Python"""
    try:
        # Lire le fichier
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Appliquer tous les patterns
        for pattern in PATTERNS_TO_REMOVE:
            content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
        
        # Si modifié, sauvegarder
        if content != original_content:
            # Créer backup
            backup_path = filepath.with_suffix('.py.bak_utf8')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Sauvegarder version nettoyée
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Nettoyé: {filepath}")
            return True
        
    except Exception as e:
        print(f"❌ Erreur sur {filepath}: {e}")
    
    return False

def main():
    """Nettoie tous les fichiers Python du projet"""
    print("🧹 Nettoyage de la configuration UTF-8 problématique...")
    print("=" * 60)
    
    cleaned_count = 0
    error_count = 0
    
    # Parcourir tous les fichiers .py
    for filepath in Path('.').rglob('*.py'):
        # Ignorer les backups et ce script
        if '.bak' in str(filepath) or 'remove_utf8' in str(filepath):
            continue
            
        try:
            if clean_file(filepath):
                cleaned_count += 1
        except Exception as e:
            error_count += 1
            print(f"❌ Erreur: {filepath} - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 RÉSUMÉ:")
    print(f"  - Fichiers nettoyés: {cleaned_count}")
    print(f"  - Erreurs: {error_count}")
    print(f"\n💡 Les backups ont été créés avec l'extension .py.bak_utf8")
    print("🎯 Vous pouvez maintenant relancer automation_main.py")

if __name__ == "__main__":
    main()