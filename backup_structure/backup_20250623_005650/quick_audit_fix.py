"""
Fix rapide pour probleme imports audit technique
Patch le technical_audit.py pour gerer correctement les chemins Windows
"""

import re
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)


def patch_technical_audit():
    """Patch technical_audit.py pour fix imports Windows"""
    logger.info("PATCH TECHNICAL AUDIT POUR WINDOWS")
    print("=" * 40)
    
    audit_file = Path("technical_audit.py")
    if not audit_file.exists():
        logger.info("[ERROR] technical_audit.py non trouve")
        return False
    
    # Lire contenu
    content = audit_file.read_text(encoding='utf-8')
    
    # Chercher ligne problematique
    # Pattern: file_module = str(py_file.relative_to(self.project_root)).replace('/', '.').replace('.py', '')
    
    old_pattern = r"file_module = str\(py_file\.relative_to\(self\.project_root\)\)\.replace\('/', '\.'\)\.replace\('\.py', ''\)"
    
    # Nouvelle version qui gere Windows
    new_code = """file_module = str(py_file.relative_to(self.project_root)).replace('\\\\', '.').replace('/', '.').replace('.py', '')"""
    
    # Remplacer
    if old_pattern in content:
        content = re.sub(old_pattern, new_code, content)
        logger.info("[PATCH] Pattern old trouve et remplace")
    else:
        # Chercher pattern alternatif
        alt_pattern = r"\.replace\('/', '\.'\)\.replace\('\.py', ''\)"
        if alt_pattern in content:
            content = content.replace("replace('/', '.')", "replace('\\\\', '.').replace('/', '.')")
            logger.info("[PATCH] Pattern alternatif trouve et remplace")
        else:
            logger.info("[WARNING] Pattern non trouve - patch manuel requis")
            return False
    
    # Sauvegarder
    backup_file = Path("technical_audit.py.backup")
    if not backup_file.exists():
        backup_file.write_text(audit_file.read_text(encoding='utf-8'), encoding='utf-8')
        logger.info("[BACKUP] Backup cree: technical_audit.py.backup")
    
    audit_file.write_text(content, encoding='utf-8')
    logger.info("[PATCHED] technical_audit.py patche pour Windows")
    
    return True

def verify_imports_manually():
    """Verification manuelle imports"""
    logger.info("\nVERIFICATION MANUELLE IMPORTS")
    print("=" * 40)
    
    import sys
    project_root = Path(".").absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    test_imports = [
        "config.trading_config",
        "core.base_types", 
        "config",
        "core"
    ]
    
    success_count = 0
    
    for module_name in test_imports:
        try:
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            __import__(module_name)
            logger.info("[OK] {module_name}")
            success_count += 1
            
        except Exception as e:
            logger.info("[ERROR] {module_name}: {e}")
    
    logger.info("\n[RESULT] {success_count}/{len(test_imports)} imports OK")
    
    if success_count == len(test_imports):
        logger.info("[SUCCESS] Tous imports fonctionnent!")
        logger.info("[ISSUE] Probleme dans audit technique, pas dans code")
        return True
    else:
        logger.info("[FAILED] Imports casses")
        return False

def main():
    """Fix rapide audit"""
    logger.info("FIX RAPIDE AUDIT IMPORTS")
    print("=" * 30)
    
    # 1. Verifier si imports fonctionnent vraiment
    imports_work = verify_imports_manually()
    
    if imports_work:
        logger.info("\n[DIAGNOSIS] Imports OK - Probleme dans audit")
        # 2. Patch audit
        patch_success = patch_technical_audit()
        
        if patch_success:
            logger.info("\n[SUCCESS] Audit patche!")
            logger.info("[NEXT] python technical_audit.py")
            return True
        else:
            logger.info("\n[FAILED] Patch echoue")
            return False
    else:
        logger.info("\n[DIAGNOSIS] Imports vraiment casses")
        logger.info("[ACTION] Utiliser: python windows_import_fixer.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)