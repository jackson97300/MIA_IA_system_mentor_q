#!/usr/bin/env python3
"""
Script pour trouver TOUS les fichiers avec des problèmes UTF-8
"""

import os
from pathlib import Path

def check_file(filepath):
    """Vérifie si un fichier contient la configuration problématique"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Rechercher différentes variantes du problème
        problematic_patterns = [
            'io.TextIOWrapper',
            'sys.stdout.buffer',
            'sys.stderr.buffer',
            'sys.stdout =',
            'sys.stderr =',
            'reconfigure(encoding',
            'codecs.getwriter'
        ]
        
        found_issues = []
        for pattern in problematic_patterns:
            if pattern in content:
                # Trouver la ligne
                for i, line in enumerate(content.split('\n'), 1):
                    if pattern in line:
                        found_issues.append((i, line.strip(), pattern))
        
        return found_issues
        
    except Exception as e:
        return None

def main():
    """Recherche dans tous les fichiers Python"""
    print("🔍 Recherche des problèmes UTF-8...")
    print("=" * 80)
    
    all_issues = {}
    
    # Parcourir TOUS les dossiers
    for root, dirs, files in os.walk('.'):
        # Ignorer certains dossiers
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'venv', '.venv'}]
        
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                issues = check_file(filepath)
                
                if issues:
                    all_issues[str(filepath)] = issues
    
    # Afficher les résultats
    if all_issues:
        print(f"\n❌ Trouvé {len(all_issues)} fichiers avec des problèmes UTF-8:\n")
        
        for filepath, issues in all_issues.items():
            print(f"\n📄 {filepath}:")
            for line_num, line, pattern in issues:
                print(f"   Ligne {line_num}: {line[:80]}...")
                print(f"   Pattern trouvé: '{pattern}'")
    else:
        print("\n✅ Aucun problème UTF-8 trouvé!")
    
    print("\n" + "=" * 80)
    
    # Suggérer les fichiers à corriger en priorité
    if all_issues:
        print("\n🎯 Fichiers à corriger en PRIORITÉ:")
        priority_files = []
        
        for filepath in all_issues.keys():
            if any(x in filepath for x in ['core', 'config', 'strategies', 'execution', 'ml', 'data']):
                priority_files.append(filepath)
        
        for f in priority_files[:10]:  # Top 10
            print(f"  - {f}")

if __name__ == "__main__":
    main()