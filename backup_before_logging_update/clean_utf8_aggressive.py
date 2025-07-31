#!/usr/bin/env python3
"""
Nettoyage AGRESSIF de tous les problèmes UTF-8
Supprime TOUTE tentative de modification de sys.stdout/stderr
"""

import os
import re
from pathlib import Path

def clean_file_aggressive(filepath):
    """Nettoie un fichier de manière agressive"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Nouvelles lignes sans les problèmes
        new_lines = []
        skip_next = 0
        
        for i, line in enumerate(lines):
            if skip_next > 0:
                skip_next -= 1
                continue
            
            # Détecter les lignes problématiques
            if any(problem in line for problem in [
                'io.TextIOWrapper',
                'sys.stdout =',
                'sys.stderr =',
                'sys.stdout.buffer',
                'sys.stderr.buffer',
                'reconfigure(encoding',
                'codecs.getwriter',
                'Configuration encodage UTF-8'
            ]):
                # Regarder les lignes avant/après pour supprimer le bloc entier
                if i > 0 and 'import' in lines[i-1]:
                    # Supprimer aussi les imports associés
                    new_lines.pop()  # Enlever le dernier import ajouté
                
                # Chercher combien de lignes sauter
                if 'if sys.platform' in line or 'if hasattr' in line:
                    # C'est un bloc conditionnel, trouver la fin
                    indent = len(line) - len(line.lstrip())
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j]
                        if next_line.strip() and (len(next_line) - len(next_line.lstrip())) <= indent:
                            break
                        j += 1
                    skip_next = j - i - 1
                
                continue
            
            # Ignorer aussi les imports inutiles
            if line.strip() == 'import io' or line.strip() == 'import codecs':
                # Vérifier si utilisé ailleurs
                remaining_content = ''.join(lines[i+1:])
                if 'io.' not in remaining_content or 'codecs.' not in remaining_content:
                    continue
            
            new_lines.append(line)
        
        # Écrire le fichier nettoyé
        new_content = ''.join(new_lines)
        
        # Supprimer les lignes vides multiples
        new_content = re.sub(r'\n\n\n+', '\n\n', new_content)
        
        # Sauvegarder
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur sur {filepath}: {e}")
        return False

def main():
    """Nettoie TOUS les fichiers Python"""
    print("🔥 NETTOYAGE AGRESSIF UTF-8")
    print("=" * 80)
    print("⚠️  Ce script va supprimer TOUTES les modifications de sys.stdout/stderr")
    print("=" * 80)
    
    # Confirmation
    response = input("\nContinuer ? (oui/non): ")
    if response.lower() != 'oui':
        print("Annulé.")
        return
    
    cleaned = 0
    errors = 0
    
    # Parcourir TOUS les fichiers
    for root, dirs, files in os.walk('.'):
        # Ignorer certains dossiers
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'venv', '.venv', 'backups'}]
        
        for file in files:
            if file.endswith('.py') and 'utf8' not in file and 'clean' not in file:
                filepath = Path(root) / file
                
                try:
                    # Vérifier si le fichier a un problème
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if any(p in content for p in ['io.TextIOWrapper', 'sys.stdout =', 'sys.stderr =']):
                        print(f"🧹 Nettoyage: {filepath}")
                        if clean_file_aggressive(filepath):
                            cleaned += 1
                        else:
                            errors += 1
                
                except Exception as e:
                    errors += 1
                    print(f"❌ Erreur lecture {filepath}: {e}")
    
    print("\n" + "=" * 80)
    print(f"✅ Terminé!")
    print(f"  - Fichiers nettoyés: {cleaned}")
    print(f"  - Erreurs: {errors}")
    print("\n🎯 Testez maintenant avec: python test_basic.py")

if __name__ == "__main__":
    main()