#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de nettoyage des anciennes références de leadership

Ce script met à jour tous les imports et références aux anciens modules de leadership
pour utiliser le nouveau module leadership_zmom.py
"""

import os
import re
from pathlib import Path

def find_and_replace_in_file(file_path, old_pattern, new_pattern):
    """Remplace un pattern dans un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_pattern in content:
            new_content = content.replace(old_pattern, new_pattern)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Mis à jour: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"❌ Erreur avec {file_path}: {e}")
        return False

def cleanup_leadership_references():
    """Nettoie toutes les références aux anciens modules de leadership"""
    
    print("🧹 NETTOYAGE DES ANCIENNES RÉFÉRENCES DE LEADERSHIP")
    print("=" * 60)
    
    # Patterns à remplacer
    replacements = [
        # Imports
        ("from features.leadership_zmom import", "from features.leadership_zmom import"),
        ("from features.leadership_zmom import", "from features.leadership_zmom import"),
        ("from features.leadership_zmom import", "from features.leadership_zmom import"),
        ("from features.leadership_zmom import", "from features.leadership_zmom import"),
        
        # Classes
        ("LeadershipZMom", "LeadershipZMom"),
        ("LeadershipZMom", "LeadershipZMom"),
        ("LeadershipZMom", "LeadershipZMom"),
        ("LeadershipZMom", "LeadershipZMom"),
        
        # Fonctions
        ("LeadershipZMom", "LeadershipZMom"),
        ("LeadershipZMom", "LeadershipZMom"),
        ("LeadershipZMom", "LeadershipZMom"),
    ]
    
    # Dossiers à traiter (exclure tests_old, archive, backup)
    base_dir = Path(".")
    exclude_dirs = {"tests_old", "archive", "backup", "__pycache__", ".git", "venv"}
    
    files_updated = 0
    
    # Parcourir tous les fichiers Python
    for py_file in base_dir.rglob("*.py"):
        # Ignorer les dossiers exclus
        if any(part in exclude_dirs for part in py_file.parts):
            continue
            
        file_updated = False
        for old_pattern, new_pattern in replacements:
            if find_and_replace_in_file(py_file, old_pattern, new_pattern):
                file_updated = True
        
        if file_updated:
            files_updated += 1
    
    print(f"\n📊 RÉSULTATS:")
    print(f"✅ {files_updated} fichiers mis à jour")
    print("✅ Nettoyage terminé")
    
    return files_updated

def verify_cleanup():
    """Vérifie que le nettoyage a bien fonctionné"""
    
    print("\n🔍 VÉRIFICATION DU NETTOYAGE")
    print("=" * 40)
    
    # Vérifier qu'il n'y a plus de références aux anciens modules
    old_modules = [
        "leadership_analyzer",
        "leadership_engine", 
        "leadership_filter_enhanced",
        "leadership_validator"
    ]
    
    base_dir = Path(".")
    exclude_dirs = {"tests_old", "archive", "backup", "__pycache__", ".git", "venv"}
    
    remaining_refs = []
    
    for py_file in base_dir.rglob("*.py"):
        if any(part in exclude_dirs for part in py_file.parts):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for module in old_modules:
                if f"features.{module}" in content:
                    remaining_refs.append((py_file, module))
        except Exception:
            continue
    
    if remaining_refs:
        print("⚠️ Références restantes trouvées:")
        for file_path, module in remaining_refs:
            print(f"   {file_path} -> {module}")
    else:
        print("✅ Aucune référence aux anciens modules trouvée")
    
    return len(remaining_refs) == 0

def main():
    """Fonction principale"""
    
    print("🎯 MIGRATION VERS LEADERSHIP_ZMOM")
    print("=" * 50)
    
    # Étape 1: Nettoyage
    files_updated = cleanup_leadership_references()
    
    # Étape 2: Vérification
    cleanup_success = verify_cleanup()
    
    # Résumé
    print(f"\n📋 RÉSUMÉ:")
    print(f"✅ Fichiers mis à jour: {files_updated}")
    print(f"✅ Nettoyage réussi: {'Oui' if cleanup_success else 'Non'}")
    
    if cleanup_success:
        print("\n🎉 MIGRATION TERMINÉE AVEC SUCCÈS!")
        print("✅ Tous les imports pointent maintenant vers leadership_zmom.py")
        print("✅ Le système est prêt pour la production")
    else:
        print("\n⚠️ MIGRATION PARTIELLE")
        print("🔧 Vérifiez manuellement les références restantes")
    
    return cleanup_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


