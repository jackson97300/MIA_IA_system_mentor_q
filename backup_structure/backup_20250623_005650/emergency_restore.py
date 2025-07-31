"""
MIA_IA_SYSTEM - Emergency Restore
Restauration d'urgence apres regression critique
Version: Recovery from vectorization damage
"""

import shutil
from pathlib import Path
from typing import List, Tuple
import logging

# Configure logging
logger = logging.getLogger(__name__)


def find_backup_files():
    """Trouve tous les fichiers de backup"""
    logger.debug("RECHERCHE FICHIERS BACKUP")
    print("=" * 40)
    
    project_root = Path(".")
    
    # Chercher fichiers backup
    backup_patterns = [
        "*.before_vectorization*",
        "*.original",
        "*.backup"
    ]
    
    found_backups = []
    
    for pattern in backup_patterns:
        backups = list(project_root.rglob(pattern))
        found_backups.extend(backups)
    
    logger.info("Fichiers backup trouvés: {len(found_backups)}")
    for backup in found_backups:
        logger.info("  • {backup}")
    
    return found_backups

def restore_from_backups():
    """Restaure fichiers depuis backups"""
    logger.info("\n🔄 RESTAURATION DEPUIS BACKUPS")
    print("=" * 40)
    
    backups = find_backup_files()
    
    if not backups:
        logger.error("Aucun backup trouvé!")
        return False
    
    restored_count = 0
    
    for backup_file in backups:
        # Déterminer fichier original
        original_name = str(backup_file)
        
        # Patterns de backup à nettoyer
        patterns_to_remove = [
            '.before_vectorization',
            '.before_vectorization_' + str(int(backup_file.stat().st_mtime)),
            '.original',
            '.backup'
        ]
        
        original_path = None
        for pattern in patterns_to_remove:
            if pattern in original_name:
                original_path = Path(original_name.replace(pattern, ''))
                break
        
        if original_path and original_path.exists():
            try:
                # Backup du fichier cassé
                broken_backup = original_path.with_suffix(f'.py.broken_{int(backup_file.stat().st_mtime)}')
                shutil.copy2(original_path, broken_backup)
                
                # Restaurer depuis backup
                shutil.copy2(backup_file, original_path)
                logger.info("Restauré: {original_path}")
                logger.info("   Backup cassé: {broken_backup}")
                
                restored_count += 1
                
            except Exception as e:
                logger.error("Erreur restauration {original_path}: {e}")
    
    logger.info("\n📊 RESTAURATION: {restored_count} fichiers restaurés")
    return restored_count > 0

def verify_restoration():
    """Vérifie que la restauration a fonctionné"""
    logger.info("\n🧪 VÉRIFICATION RESTAURATION")
    print("=" * 40)
    
    # Test imports critiques
    import sys
    project_root = Path(".").absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    critical_imports = [
        "config.trading_config",
        "core.base_types",
        "config",
        "core"
    ]
    
    success_count = 0
    
    for module_name in critical_imports:
        try:
            # Clear cache
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            __import__(module_name)
            logger.info("{module_name}")
            success_count += 1
            
        except Exception as e:
            logger.error("{module_name}: {e}")
    
    # Test fonctionnalité
    try:
        from config import get_trading_config
        from core import MarketData, ES_TICK_SIZE
        
        config = get_trading_config()
        logger.info("Config test: {config.trading_mode.value}")
        logger.info("Core test: ES_TICK_SIZE = {ES_TICK_SIZE}")
        
        functionality_ok = True
        
    except Exception as e:
        logger.error("Functionality test: {e}")
        functionality_ok = False
    
    # Résumé
    logger.info("\n📊 VÉRIFICATION:")
    logger.info("   • Imports: {success_count}/{len(critical_imports)}")
    logger.info("   • Fonctionnalité: {'OK' if functionality_ok else 'ERROR'}")
    
    overall_ok = success_count == len(critical_imports) and functionality_ok
    
    if overall_ok:
        logger.info("RESTAURATION RÉUSSIE!")
        return True
    else:
        logger.error("RESTAURATION INCOMPLÈTE")
        return False

def clean_optimization_artifacts():
    """Nettoie les artefacts d'optimisation"""
    logger.info("\n🧹 NETTOYAGE ARTEFACTS OPTIMISATION")
    print("=" * 40)
    
    # Fichiers créés par les optimisations
    artifact_patterns = [
        "*vectorization_optimizer*",
        "*precise_vectorization*",
        "*performance_patch*",
        "*.broken_*"
    ]
    
    project_root = Path(".")
    cleaned_count = 0
    
    for pattern in artifact_patterns:
        artifacts = list(project_root.rglob(pattern))
        
        for artifact in artifacts:
            if artifact.exists() and artifact.is_file():
                try:
                    artifact.unlink()
                    logger.info("🗑️ Supprimé: {artifact}")
                    cleaned_count += 1
                except Exception as e:
                    logger.warning("Erreur suppression {artifact}: {e}")
    
    logger.info("📊 NETTOYAGE: {cleaned_count} artefacts supprimés")
    return cleaned_count

def emergency_restore_procedure():
    """Procédure complète de restauration d'urgence"""
    logger.info("🚨 PROCÉDURE RESTAURATION D'URGENCE")
    print("=" * 50)
    logger.info("OBJECTIF: Revenir à l'état stable 87.5%")
    
    # 1. Restaurer depuis backups
    if not restore_from_backups():
        logger.error("Restauration backup échouée")
        return False
    
    # 2. Vérifier restauration
    if not verify_restoration():
        logger.error("Vérification échouée")
        return False
    
    # 3. Nettoyer artefacts
    clean_optimization_artifacts()
    
    # 4. Instructions finales
    logger.info("\n🎯 RESTAURATION COMPLÈTE")
    print("=" * 30)
    logger.info("ACTIONS EFFECTUÉES:")
    logger.info("  ✅ Fichiers restaurés depuis backup")
    logger.info("  ✅ Imports vérifiés")
    logger.info("  ✅ Fonctionnalité testée")
    logger.info("  ✅ Artefacts nettoyés")
    
    logger.info("\nPROCHAINES ÉTAPES:")
    logger.info("  1. python technical_audit.py")
    logger.info("  2. Vérifier retour à 87.5%")
    logger.info("  3. NE PAS re-optimiser sans backup complet")
    
    return True

def create_analysis_report():
    """Crée rapport d'analyse de la régression"""
    logger.info("\n📋 RAPPORT ANALYSE RÉGRESSION")
    print("=" * 40)
    
    report = """
🚨 RÉGRESSION ANALYSIS REPORT

PROBLÈME:
  • Score: 87.5% → 37.5% (-50 points)
  • Imports: 17/17 → 9/17 (8 cassés)
  • Syntax: OK → ERROR

CAUSE PROBABLE:
  • Optimisation vectorisation trop agressive
  • Modification fonctions sans tests appropriés
  • Patterns regex incorrects
  • Imports NumPy mal injectés

LEÇONS APPRISES:
  1. TOUJOURS tester après chaque changement
  2. Optimisations par petits incréments
  3. Backup complet avant modifications
  4. Validation imports après changements

RECOMMANDATIONS FUTURES:
  • Score 87.5% est déjà EXCELLENT
  • Optimisations = bonus, pas critique
  • Priorité: Stabilité > Performance
  • Phase 3 possible avec 87.5%
"""
    
    report_file = Path("regression_analysis_report.txt")
    report_file.write_text(report, encoding='utf-8')
    
    logger.info("📄 Rapport sauvé: {report_file}")
    print(report)

def main():
    """Restauration d'urgence principale"""
    logger.info("🚨 EMERGENCY RESTORE - MIA_IA_SYSTEM")
    print("=" * 60)
    
    # Restauration d'urgence
    if emergency_restore_procedure():
        create_analysis_report()
        
        logger.info("\n✅ RESTAURATION D'URGENCE RÉUSSIE!")
        logger.info("🎯 Système devrait être de retour à 87.5%")
        
        return True
    else:
        logger.info("\n💀 RESTAURATION D'URGENCE ÉCHOUÉE")
        logger.info("🔧 Intervention manuelle requise")
        
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        logger.info("\n🚀 LANCER MAINTENANT:")
        logger.info("python technical_audit.py")
        logger.info("\n🎯 ATTENDU: Retour à 87.5% score")
    else:
        logger.info("\n💀 SYSTÈME EN PANNE - Debug manuel requis")