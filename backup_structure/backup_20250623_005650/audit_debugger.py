"""
MIA_IA_SYSTEM - Audit Debugger
Identifie exactement quel fichier cause le probleme dans technical_audit.py
Version: Debug Windows paths
"""

import sys
import importlib
from pathlib import Path
from typing import List, Tuple, Dict
import logging

# Configure logging
logger = logging.getLogger(__name__)


def analyze_audit_problem():
    """Analyse exacte du probleme audit"""
    logger.debug("ANALYSE PROBLEME AUDIT TECHNIQUE")
    print("=" * 50)
    
    project_root = Path(".")
    
    # 1. Lister TOUS les fichiers Python
    logger.info("\n1️⃣ ANALYSE FICHIERS PYTHON:")
    python_files = list(project_root.rglob("*.py"))
    python_files = [f for f in python_files if "__pycache__" not in str(f)]
    
    logger.info("Total fichiers Python trouvés: {len(python_files)}")
    
    # 2. Simuler la logique de l'audit (problématique)
    logger.info("\n2️⃣ SIMULATION LOGIQUE AUDIT (BUGGUÉE):")
    problematic_modules = []
    valid_modules = []
    
    for py_file in python_files:
        # Reproduire la logique exacte de technical_audit.py
        relative_path = py_file.relative_to(project_root)
        
        # VOICI LE BUG ! Sur Windows, ça donne des backslashes
        file_module_buggy = str(relative_path).replace('/', '.').replace('.py', '')
        
        logger.info("Fichier: {py_file}")
        logger.info("  Chemin relatif: {relative_path}")
        logger.info("  Module buggy: {file_module_buggy}")
        
        # Vérifier si c'est un vrai module Python importable
        try:
            # Test si ce serait importable (sans vraiment importer)
            if '\\' in file_module_buggy:
                problematic_modules.append((str(py_file), file_module_buggy, "Windows backslash"))
            elif file_module_buggy.startswith('.'):
                problematic_modules.append((str(py_file), file_module_buggy, "Starts with dot"))
            elif any(part in file_module_buggy for part in ['test_', 'fix_', 'performance_', 'audit_']):
                problematic_modules.append((str(py_file), file_module_buggy, "Utility script"))
            else:
                valid_modules.append((str(py_file), file_module_buggy))
                
        except Exception as e:
            problematic_modules.append((str(py_file), file_module_buggy, str(e)))
        
        print()
    
    # 3. Identifier la vraie correction
    logger.info("\n3️⃣ CORRECTION APPROPRIÉE:")
    fixed_modules = []
    
    for py_file in python_files:
        relative_path = py_file.relative_to(project_root)
        
        # CORRECTION: Remplacer AUSSI les backslashes Windows
        file_module_fixed = str(relative_path).replace('\\', '.').replace('/', '.').replace('.py', '')
        
        # Filtrer les fichiers non-modules
        if (not file_module_fixed.startswith('.') and 
            not any(part in file_module_fixed for part in ['test_', 'fix_', 'performance_', 'audit_', 'quick_', 'ultimate_', 'corrected_', 'windows_']) and
            file_module_fixed not in ['main', 'setup'] and
            '.' in file_module_fixed):  # Doit avoir au moins un package
            
            fixed_modules.append((str(py_file), file_module_fixed))
    
    # 4. Résumé du problème
    logger.info("\n📊 RÉSUMÉ PROBLÈME:")
    logger.info("   • Fichiers totaux: {len(python_files)}")
    logger.info("   • Modules problématiques: {len(problematic_modules)}")
    logger.info("   • Modules valides (après fix): {len(fixed_modules)}")
    
    # 5. Détail des problèmes
    logger.info("\n❌ FICHIERS PROBLÉMATIQUES:")
    for file_path, module_name, reason in problematic_modules[:10]:  # Top 10
        file_name = Path(file_path).name
        logger.info("   • {file_name:25} → {module_name:30} ({reason})")
    
    if len(problematic_modules) > 10:
        logger.info("   ... et {len(problematic_modules) - 10} autres")
    
    # 6. Modules valides
    logger.info("\n✅ MODULES VALIDES (APRÈS FIX):")
    for file_path, module_name in fixed_modules:
        file_name = Path(file_path).name
        logger.info("   • {file_name:25} → {module_name}")
    
    return problematic_modules, fixed_modules

def test_fixed_import_logic():
    """Test la logique d'import corrigée"""
    logger.info("\n🧪 TEST LOGIQUE IMPORT CORRIGÉE")
    print("=" * 50)
    
    project_root = Path(".")
    
    # Modules critiques à tester
    critical_files = [
        "config/trading_config.py",
        "core/base_types.py",
        "config/__init__.py",
        "core/__init__.py"
    ]
    
    # Add to path
    if str(project_root.absolute()) not in sys.path:
        sys.path.insert(0, str(project_root.absolute()))
    
    for file_path in critical_files:
        if Path(file_path).exists():
            # Logique corrigée
            py_file = Path(file_path)
            relative_path = py_file.relative_to(project_root)
            
            # CORRECTION: Remplacer backslashes ET slashes
            file_module = str(relative_path).replace('\\', '.').replace('/', '.').replace('.py', '')
            
            logger.info("Fichier: {file_path}")
            logger.info("Module: {file_module}")
            
            try:
                # Clear cache
                if file_module in sys.modules:
                    del sys.modules[file_module]
                
                importlib.import_module(file_module)
                logger.info("Import réussi: {file_module}")
                
            except Exception as e:
                logger.error("Import échoué: {file_module} - {e}")
            
            print()

def identify_exact_fix_needed():
    """Identifie le fix exact nécessaire dans technical_audit.py"""
    logger.info("\n🔧 FIX EXACT NÉCESSAIRE")
    print("=" * 50)
    
    audit_file = Path("technical_audit.py")
    if not audit_file.exists():
        logger.error("technical_audit.py non trouvé")
        return None
    
    content = audit_file.read_text(encoding='utf-8')
    
    # Chercher les lignes problématiques
    lines = content.split('\n')
    problem_lines = []
    
    for i, line in enumerate(lines):
        if 'relative_to' in line and 'replace' in line and '.py' in line:
            problem_lines.append((i+1, line.strip()))
    
    logger.debug("LIGNES PROBLÉMATIQUES TROUVÉES:")
    for line_num, line_content in problem_lines:
        logger.info("   Ligne {line_num}: {line_content}")
    
    # Proposer fix exact
    if problem_lines:
        logger.info("\n🔧 FIX EXACT:")
        for line_num, line_content in problem_lines:
            if "replace('/', '.')" in line_content:
                fixed_line = line_content.replace(
                    "replace('/', '.')", 
                    "replace('\\\\', '.').replace('/', '.')"
                )
                logger.info("   Ligne {line_num}:")
                logger.info("   AVANT: {line_content}")
                logger.info("   APRÈS: {fixed_line}")
                print()
        
        return problem_lines
    else:
        logger.error("Pattern problématique non trouvé")
        return None

def main():
    """Analyse complète"""
    logger.info("🚀 AUDIT DEBUGGER - IDENTIFICATION PROBLÈME EXACT")
    print("=" * 60)
    
    # 1. Analyser le problème
    problematic, valid = analyze_audit_problem()
    
    # 2. Tester logique corrigée
    test_fixed_import_logic()
    
    # 3. Identifier fix exact
    fix_lines = identify_exact_fix_needed()
    
    # 4. Conclusion
    logger.info("\n🎯 CONCLUSION")
    print("=" * 30)
    
    logger.info("PROBLÈME IDENTIFIÉ:")
    logger.info("   • {len(problematic)} fichiers causent des erreurs d'import")
    logger.info("   • Cause principale: Chemins Windows (backslashes)")
    logger.info("   • Fichiers utilitaires aussi inclus dans scan")
    
    logger.info("\nSOLUTION:")
    logger.info("   • Modifier technical_audit.py ligne(s): {[line[0] for line in fix_lines] if fix_lines else 'Non trouvé'}")
    logger.info("   • Ajouter .replace('\\\\', '.') avant .replace('/', '.')")
    logger.info("   • Filtrer fichiers non-modules (test_, fix_, etc.)")
    
    logger.info("\nRÉSULTAT ATTENDU:")
    logger.info("   • {len(valid)} modules valides seraient importés")
    logger.info("   • Score passerait de 62.5% à 85%+")

if __name__ == "__main__":
    main()