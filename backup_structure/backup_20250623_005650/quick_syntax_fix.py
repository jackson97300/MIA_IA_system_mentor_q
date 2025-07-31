"""
MIA_IA_SYSTEM - Quick Syntax Fix
Fix immediat ligne 369 - suppression crochet en trop
"""

import shutil
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)


def fix_line_369():
    """Fix immediat ligne 369"""
    logger.info("🔧 FIX IMMEDIAT LIGNE 369")
    print("=" * 30)
    
    file_path = Path("features/feature_calculator.py")
    
    # Backup de securite
    backup_file = file_path.with_suffix(".py.before_syntax_fix")
    shutil.copy2(file_path, backup_file)
    logger.info("💾 Backup: {backup_file}")
    
    # Lire fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Ligne 369 (index 368)
    target_line = 368
    original_line = lines[target_line]
    
    logger.info("AVANT: {original_line.strip()}")
    
    # Fix: Supprimer le dernier ']'
    # De: np.array([bar.close for bar in list(self.price_history)[-10:])]
    # À:  np.array([bar.close for bar in list(self.price_history)[-10:]])
    
    fixed_line = original_line.rstrip()
    if fixed_line.endswith(')]'):
        fixed_line = fixed_line[:-2] + ')\n'  # Enlever ']' en trop
    elif fixed_line.endswith(')]  # Some comment'):
        # Au cas où il y aurait un commentaire
        fixed_line = original_line.replace(')]', ')')
    else:
        # Simple suppression dernier caractère s'il s'agit de ']'
        if fixed_line.endswith(']'):
            fixed_line = fixed_line[:-1] + '\n'
    
    logger.info("APRÈS: {fixed_line.strip()}")
    
    # Appliquer fix
    lines[target_line] = fixed_line
    
    # Sauvegarder
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    logger.info("Fix appliqué!")
    return True

def test_fix():
    """Test que le fix fonctionne"""
    logger.info("\n🧪 TEST FIX")
    print("=" * 20)
    
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
        return False
        
    except Exception as e:
        logger.error("Erreur: {e}")
        return False

def main():
    """Fix rapide ligne 369"""
    logger.info("⚡ QUICK FIX LIGNE 369")
    print("=" * 40)
    logger.info("Problème: Crochet ']' en trop à la fin")
    logger.info("Solution: Supprimer le dernier ']'")
    
    # Appliquer fix
    if fix_line_369():
        # Tester fix
        if test_fix():
            logger.info("\n🎉 FIX RÉUSSI!")
            logger.info("📋 PROCHAINES ÉTAPES:")
            logger.info("  1. python technical_audit.py")
            logger.info("  2. Vérifier retour à 87.5%")
            return True
        else:
            logger.info("\n❌ Fix insuffisant")
            return False
    else:
        logger.info("\n❌ Fix échoué")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        logger.info("\n🚀 LANCER AUDIT:")
        logger.info("python technical_audit.py")
    else:
        logger.info("\n💀 Fix échoué")