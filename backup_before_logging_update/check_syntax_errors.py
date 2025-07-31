#!/usr/bin/env python3
"""
Script pour vérifier les erreurs de syntaxe dans les fichiers Python
"""

import ast
import os
from pathlib import Path

def check_syntax(filepath):
    """Vérifie la syntaxe d'un fichier Python"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Essayer de parser le fichier
        ast.parse(content)
        return True, None
        
    except SyntaxError as e:
        return False, {
            'line': e.lineno,
            'offset': e.offset,
            'text': e.text,
            'msg': e.msg
        }
    except Exception as e:
        return False, {'msg': str(e)}

def show_file_context(filepath, error_line):
    """Affiche le contexte autour de l'erreur"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"\n📄 Contenu de {filepath} autour de la ligne {error_line}:")
        print("=" * 60)
        
        # Afficher 5 lignes avant et après
        start = max(0, error_line - 6)
        end = min(len(lines), error_line + 5)
        
        for i in range(start, end):
            line_num = i + 1
            prefix = ">>>" if line_num == error_line else "   "
            print(f"{prefix} {line_num:4d}: {lines[i].rstrip()}")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"Erreur lecture fichier: {e}")

def main():
    """Vérifie les fichiers critiques"""
    print("🔍 Vérification des erreurs de syntaxe...")
    print("=" * 80)
    
    # Fichiers critiques à vérifier
    critical_files = [
        'core/__init__.py',
        'config/__init__.py',
        'ml/__init__.py',
        'data/__init__.py',
        'strategies/__init__.py',
        'execution/__init__.py',
        'monitoring/__init__.py',
        'performance/__init__.py',
    ]
    
    errors_found = []
    
    for filepath in critical_files:
        if os.path.exists(filepath):
            print(f"\n📋 Vérification: {filepath}")
            success, error = check_syntax(filepath)
            
            if not success:
                print(f"❌ ERREUR DE SYNTAXE!")
                if error:
                    if 'line' in error:
                        print(f"   Ligne {error['line']}: {error['msg']}")
                        show_file_context(filepath, error['line'])
                    else:
                        print(f"   Erreur: {error['msg']}")
                
                errors_found.append((filepath, error))
            else:
                print(f"✅ Syntaxe OK")
    
    # Résumé
    print("\n" + "=" * 80)
    if errors_found:
        print(f"❌ {len(errors_found)} fichiers avec erreurs:")
        for filepath, _ in errors_found:
            print(f"  - {filepath}")
    else:
        print("✅ Aucune erreur de syntaxe trouvée!")
    
    # Proposition de correction pour core/__init__.py
    if any('core/__init__.py' in f for f, _ in errors_found):
        print("\n💡 CORRECTION SUGGÉRÉE pour core/__init__.py:")
        print("Après la ligne 'if sys.platform == \"win32\":', ajoutez:")
        print("    pass  # Configuration UTF-8 supprimée")

if __name__ == "__main__":
    main()