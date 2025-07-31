"""
MIA_IA_SYSTEM - Fix Syntax Error
Correction erreur syntaxe dans features/feature_calculator.py ligne 369
Version: Emergency syntax fix
"""

import shutil
from pathlib import Path
import re
import logging

# Configure logging
logger = logging.getLogger(__name__)


def diagnose_syntax_error():
    """Diagnostic precis erreur syntaxe"""
    logger.debug("DIAGNOSTIC ERREUR SYNTAXE")
    print("=" * 40)
    
    file_path = Path("features/feature_calculator.py")
    
    if not file_path.exists():
        logger.error("{file_path} non trouvé")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Afficher contexte autour ligne 369
        target_line = 369
        start_line = max(1, target_line - 5)
        end_line = min(len(lines), target_line + 5)
        
        logger.info("📍 CONTEXTE LIGNE {target_line}:")
        logger.info("Fichier: {file_path}")
        logger.info("Total lignes: {len(lines)}")
        print()
        
        for i in range(start_line - 1, end_line):
            line_num = i + 1
            line_content = lines[i].rstrip()
            marker = ">>> " if line_num == target_line else "    "
            logger.info("{marker}{line_num:3d}: {line_content}")
        
        # Analyser la ligne problématique
        if target_line <= len(lines):
            problem_line = lines[target_line - 1]
            logger.info("\n🔍 ANALYSE LIGNE {target_line}:")
            logger.info("Contenu: '{problem_line.strip()}'")
            
            # Compter parenthèses/crochets
            open_parens = problem_line.count('(')
            close_parens = problem_line.count(')')
            open_brackets = problem_line.count('[')
            close_brackets = problem_line.count(']')
            
            logger.info("Parenthèses: ( = {open_parens}, ) = {close_parens}")
            logger.info("Crochets: [ = {open_brackets}, ] = {close_brackets}")
            
            return {
                'file_path': file_path,
                'target_line': target_line,
                'problem_line': problem_line,
                'lines': lines,
                'open_parens': open_parens,
                'close_parens': close_parens,
                'open_brackets': open_brackets,
                'close_brackets': close_brackets
            }
        else:
            logger.error("Ligne {target_line} n'existe pas (fichier n'a que {len(lines)} lignes)")
            return None
            
    except Exception as e:
        logger.error("Erreur lecture fichier: {e}")
        return None

def restore_feature_calculator_from_backup():
    """Restaure feature_calculator depuis backup"""
    logger.info("\n🔄 RESTAURATION FEATURE_CALCULATOR")
    print("=" * 40)
    
    # Chercher backups disponibles
    feature_calc_backups = []
    for backup_file in Path(".").rglob("feature_calculator.py.before_vectorization*"):
        feature_calc_backups.append(backup_file)
    
    if not feature_calc_backups:
        logger.error("Aucun backup feature_calculator trouvé")
        return False
    
    # Prendre le backup le plus récent
    latest_backup = max(feature_calc_backups, key=lambda x: x.stat().st_mtime)
    logger.info("📄 Backup trouvé: {latest_backup}")
    
    original_file = Path("features/feature_calculator.py")
    
    try:
        # Backup du fichier cassé
        broken_backup = original_file.with_suffix(f".py.broken_syntax_{int(latest_backup.stat().st_mtime)}")
        shutil.copy2(original_file, broken_backup)
        logger.info("💾 Fichier cassé sauvé: {broken_backup}")
        
        # Restaurer depuis backup
        shutil.copy2(latest_backup, original_file)
        logger.info("Restauré: {original_file}")
        
        return True
        
    except Exception as e:
        logger.error("Erreur restauration: {e}")
        return False

def manual_fix_syntax():
    """Fix manuel de l'erreur syntaxe si possible"""
    logger.info("\n🔧 FIX MANUEL SYNTAXE")
    print("=" * 40)
    
    diagnosis = diagnose_syntax_error()
    if not diagnosis:
        return False
    
    file_path = diagnosis['file_path']
    lines = diagnosis['lines']
    target_line = diagnosis['target_line'] - 1  # Index 0
    
    if target_line >= len(lines):
        logger.error("Ligne cible hors limites")
        return False
    
    problem_line = lines[target_line]
    logger.debug("Ligne problématique: '{problem_line.strip()}'")
    
    # Tentatives de fix courants
    fixes_attempted = []
    
    # Fix 1: Remplacer ) par ] si déséquilibre
    if problem_line.count(')') > problem_line.count('(') and problem_line.count('[') > problem_line.count(']'):
        # Il y a probablement un ) qui devrait être ]
        fixed_line = problem_line
        
        # Chercher dernier ) et le remplacer par ]
        last_paren_pos = fixed_line.rfind(')')
        if last_paren_pos != -1:
            fixed_line = fixed_line[:last_paren_pos] + ']' + fixed_line[last_paren_pos + 1:]
            fixes_attempted.append(('Replace ) with ]', fixed_line))
    
    # Fix 2: Ajouter ] manquant
    if problem_line.count('[') > problem_line.count(']'):
        fixed_line = problem_line.rstrip() + ']'
        fixes_attempted.append(('Add missing ]', fixed_line))
    
    # Fix 3: Supprimer ) en trop
    if problem_line.count(')') > problem_line.count('('):
        fixed_line = problem_line
        last_paren_pos = fixed_line.rfind(')')
        if last_paren_pos != -1:
            fixed_line = fixed_line[:last_paren_pos] + fixed_line[last_paren_pos + 1:]
            fixes_attempted.append(('Remove extra )', fixed_line))
    
    if not fixes_attempted:
        logger.error("Aucun fix automatique possible")
        return False
    
    logger.info("🔧 {len(fixes_attempted)} fixes possibles:")
    for i, (description, fixed_line) in enumerate(fixes_attempted):
        logger.info("   {i+1}. {description}")
        logger.info("      '{fixed_line.strip()}'")
    
    # Appliquer le premier fix
    if fixes_attempted:
        description, fixed_line = fixes_attempted[0]
        
        # Backup original
        backup_file = file_path.with_suffix(f".py.before_manual_fix")
        shutil.copy2(file_path, backup_file)
        
        # Appliquer fix
        lines[target_line] = fixed_line
        
        # Sauvegarder
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        logger.info("Fix appliqué: {description}")
        logger.info("💾 Backup: {backup_file}")
        
        return True
    
    return False

def test_syntax_fix():
    """Test que le fix syntaxe fonctionne"""
    logger.info("\n🧪 TEST FIX SYNTAXE")
    print("=" * 40)
    
    file_path = Path("features/feature_calculator.py")
    
    try:
        # Test compilation
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        compile(source, str(file_path), 'exec')
        logger.info("Compilation: OK")
        
        # Test import
        import sys
        project_root = Path(".").absolute()
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # Clear cache
        if 'features.feature_calculator' in sys.modules:
            del sys.modules['features.feature_calculator']
        
        __import__('features.feature_calculator')
        logger.info("Import: OK")
        
        return True
        
    except SyntaxError as e:
        logger.error("Erreur syntaxe: {e}")
        logger.info("    Ligne {e.lineno}: {e.text}")
        return False
        
    except Exception as e:
        logger.error("Erreur: {e}")
        return False

def main():
    """Fix erreur syntaxe principal"""
    logger.info("🚨 FIX ERREUR SYNTAXE - features/feature_calculator.py")
    print("=" * 60)
    
    # 1. Diagnostic
    diagnosis = diagnose_syntax_error()
    
    if not diagnosis:
        logger.error("Impossible de diagnostiquer l'erreur")
        return False
    
    # 2. Tentative restauration backup
    logger.info("\n🔄 TENTATIVE 1: Restauration backup")
    if restore_feature_calculator_from_backup():
        if test_syntax_fix():
            logger.info("RESTAURATION BACKUP RÉUSSIE!")
            return True
        else:
            logger.error("Backup aussi cassé")
    
    # 3. Tentative fix manuel
    logger.info("\n🔧 TENTATIVE 2: Fix manuel")
    if manual_fix_syntax():
        if test_syntax_fix():
            logger.info("FIX MANUEL RÉUSSI!")
            return True
        else:
            logger.error("Fix manuel insuffisant")
    
    # 4. Solution de dernier recours
    logger.info("\n⚠️ SOLUTION DERNIER RECOURS")
    logger.info("Erreur critique non résolue automatiquement")
    logger.info("Action manuelle requise:")
    logger.info("  1. Ouvrir features/feature_calculator.py ligne 369")
    logger.info("  2. Corriger parenthèse/crochet")
    logger.info("  3. Sauvegarder")
    logger.info("  4. Re-tester audit")
    
    return False

if __name__ == "__main__":
    success = main()
    
    if success:
        logger.info("\n🚀 ERREUR CORRIGÉE - LANCER AUDIT:")
        logger.info("python technical_audit.py")
        logger.info("\n🎯 ATTENDU: Retour à 87.5%+")
    else:
        logger.info("\n💀 CORRECTION ÉCHOUÉE - Intervention manuelle")