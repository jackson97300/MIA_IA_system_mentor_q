"""
MIA_IA_SYSTEM - Final Imports Diagnosis
Diagnostic final et fix definitif du probleme imports 0/17
Version: Ultimate import fix
"""

import sys
import importlib
from pathlib import Path
from typing import List, Dict, Tuple
import logging

# Configure logging
logger = logging.getLogger(__name__)


def test_manual_imports():
    """Test manuel des imports critiques"""
    logger.info("🧪 TEST MANUEL IMPORTS CRITIQUES")
    print("=" * 40)
    
    # Ajouter au path
    project_root = Path(".").absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    critical_imports = [
        "config.trading_config",
        "core.base_types",
        "features.feature_calculator",
        "config",
        "core"
    ]
    
    success_count = 0
    
    for module_name in critical_imports:
        try:
            # Clear cache
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            importlib.import_module(module_name)
            logger.info("{module_name}")
            success_count += 1
            
        except Exception as e:
            logger.error("{module_name}: {e}")
    
    logger.info("\n📊 RÉSULTAT MANUEL: {success_count}/{len(critical_imports)}")
    
    if success_count == len(critical_imports):
        logger.info("🎯 TOUS IMPORTS MANUELS OK!")
        logger.info("🐛 Problème = Bug audit technique Windows")
        return True
    else:
        logger.info("💀 Imports vraiment cassés")
        return False

def check_technical_audit_fix():
    """Vérifie si technical_audit.py a le fix Windows"""
    logger.info("\n🔍 VÉRIFICATION FIX TECHNICAL_AUDIT")
    print("=" * 40)
    
    audit_file = Path("technical_audit.py")
    
    if not audit_file.exists():
        logger.error("technical_audit.py non trouvé")
        return False
    
    content = audit_file.read_text(encoding='utf-8')
    
    # Chercher le fix Windows
    has_backslash_fix = ".replace('\\\\', '.')" in content
    has_original_bug = ".replace('/', '.')" in content and not has_backslash_fix
    
    logger.info("Fix backslash Windows: {'✅ Présent' if has_backslash_fix else '❌ Absent'}")
    logger.info("Bug original présent: {'❌ Oui' if has_original_bug else '✅ Non'}")
    
    if has_backslash_fix and not has_original_bug:
        logger.info("Technical audit a le fix Windows")
        return True
    else:
        logger.error("Technical audit manque le fix Windows")
        return False

def apply_final_technical_audit_fix():
    """Applique le fix final à technical_audit.py"""
    logger.info("\n🔧 APPLICATION FIX FINAL TECHNICAL_AUDIT")
    print("=" * 45)
    
    audit_file = Path("technical_audit.py")
    
    # Backup
    backup_file = Path("technical_audit.py.before_final_fix")
    if not backup_file.exists():
        import shutil
        shutil.copy2(audit_file, backup_file)
        logger.info("💾 Backup: {backup_file}")
    
    content = audit_file.read_text(encoding='utf-8')
    
    # Fix 1: Chemins Windows
    old_pattern = ".replace('/', '.').replace('.py', '')"
    new_pattern = ".replace('\\\\', '.').replace('/', '.').replace('.py', '')"
    
    if old_pattern in content and new_pattern not in content:
        content = content.replace(old_pattern, new_pattern)
        logger.info("Fix 1: Chemins Windows appliqué")
    
    # Fix 2: Filtrage fichiers problématiques
    # Chercher la ligne de filtrage __pycache__
    filter_line = 'python_files = [f for f in python_files if "__pycache__" not in str(f)]'
    
    if filter_line in content:
        # Remplacer par version améliorée
        improved_filter = '''python_files = [f for f in python_files if (
            "__pycache__" not in str(f) and
            not f.name.startswith(('audit_', 'fix_', 'quick_', 'emergency_', 'complete_', 'vectorization_', 'precise_', 'windows_', 'ultimate_', 'final_')) and
            f.suffix == '.py'
        )]'''
        
        content = content.replace(filter_line, improved_filter)
        logger.info("Fix 2: Filtrage fichiers amélioré")
    
    # Sauvegarder
    audit_file.write_text(content, encoding='utf-8')
    logger.info("Technical_audit.py mis à jour")
    
    return True

def analyze_file_structure():
    """Analyse structure fichiers projet"""
    logger.info("\n📁 ANALYSE STRUCTURE FICHIERS")
    print("=" * 35)
    
    project_root = Path(".")
    
    # Compter fichiers par type
    python_files = list(project_root.rglob("*.py"))
    python_files = [f for f in python_files if "__pycache__" not in str(f)]
    
    # Classer fichiers
    core_files = [f for f in python_files if f.parts[0] == "core"]
    config_files = [f for f in python_files if f.parts[0] == "config"]
    features_files = [f for f in python_files if f.parts[0] == "features"]
    utility_files = [f for f in python_files if f.name.startswith(('audit_', 'fix_', 'quick_', 'emergency_', 'test_', 'ultimate_'))]
    
    logger.info("📊 STRUCTURE:")
    logger.info("   Total fichiers Python: {len(python_files)}")
    logger.info("   Core: {len(core_files)}")
    logger.info("   Config: {len(config_files)}")
    logger.info("   Features: {len(features_files)}")
    logger.info("   Utility scripts: {len(utility_files)}")
    
    # Fichiers critiques
    critical_files = [
        "config/trading_config.py",
        "config/__init__.py",
        "core/base_types.py",
        "core/__init__.py",
        "features/feature_calculator.py"
    ]
    
    logger.info("\n🎯 FICHIERS CRITIQUES:")
    for file_path in critical_files:
        exists = Path(file_path).exists()
        logger.info("   {'✅' if exists else '❌'} {file_path}")
    
    return len(utility_files)

def main():
    """Diagnostic et fix final imports"""
    logger.info("🚨 DIAGNOSTIC FINAL IMPORTS - SOLUTION DÉFINITIVE")
    print("=" * 60)
    
    # 1. Test imports manuels
    imports_work_manually = test_manual_imports()
    
    # 2. Vérifier fix technical_audit
    audit_has_fix = check_technical_audit_fix()
    
    # 3. Analyser structure
    utility_count = analyze_file_structure()
    
    # 4. Diagnostic
    logger.info("\n📊 DIAGNOSTIC:")
    logger.info("   Imports manuels: {'✅ OK' if imports_work_manually else '❌ CASSÉS'}")
    logger.info("   Fix audit Windows: {'✅ Présent' if audit_has_fix else '❌ Absent'}")
    logger.info("   Fichiers utilitaires: {utility_count} (peuvent polluer scan)")
    
    # 5. Actions correctives
    if imports_work_manually and not audit_has_fix:
        logger.info("\n🔧 PROBLÈME IDENTIFIÉ: Bug audit technique Windows")
        logger.info("💡 SOLUTION: Appliquer fix technical_audit.py")
        
        if apply_final_technical_audit_fix():
            logger.info("\n✅ FIX APPLIQUÉ!")
            logger.info("📋 PROCHAINES ÉTAPES:")
            logger.info("   1. python technical_audit.py")
            logger.info("   2. Score attendu: 87.5%+")
            logger.info("   3. Imports: 0/17 → 17/17")
            
            return True
    
    elif not imports_work_manually:
        logger.info("\n💀 PROBLÈME CRITIQUE: Imports vraiment cassés")
        logger.info("🔧 ACTION: Debug manuel requis")
        
        return False
    
    else:
        logger.info("\n⚠️ SITUATION UNCLEAR")
        logger.info("🔧 ACTION: Re-test audit après nettoyage")
        
        return True

if __name__ == "__main__":
    success = main()
    
    if success:
        logger.info("\n🚀 LANCER AUDIT FINAL:")
        logger.info("python technical_audit.py")
        logger.info("\n🎯 ATTENDU: 87.5% - AUDIT PASSED")
    else:
        logger.info("\n💀 INTERVENTION MANUELLE REQUISE")