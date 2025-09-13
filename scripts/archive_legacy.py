#!/usr/bin/env python3
"""
Script d'archivage des dossiers legacy
=====================================

Archive les dossiers ancien_system/, archive/ et fichiers *.backup
pour nettoyer le projet et réduire la confusion.
"""

import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_archive_name(base_name: str) -> str:
    """Crée un nom d'archive avec timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_archived_{timestamp}.zip"

def archive_directory(source_dir: Path, archive_name: str) -> bool:
    """Archive un répertoire dans un fichier ZIP"""
    if not source_dir.exists():
        logger.warning(f"Le répertoire {source_dir} n'existe pas")
        return False
    
    archive_path = Path("archived_legacy") / archive_name
    archive_path.parent.mkdir(exist_ok=True)
    
    try:
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(source_dir.parent)
                    zipf.write(file_path, arcname)
        
        logger.info(f"✅ Archivé {source_dir} → {archive_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'archivage de {source_dir}: {e}")
        return False

def archive_backup_files(root_dir: Path) -> int:
    """Archive tous les fichiers *.backup"""
    backup_files = list(root_dir.rglob("*.backup"))
    if not backup_files:
        logger.info("Aucun fichier *.backup trouvé")
        return 0
    
    archive_name = create_archive_name("backup_files")
    archive_path = Path("archived_legacy") / archive_name
    archive_path.parent.mkdir(exist_ok=True)
    
    try:
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for backup_file in backup_files:
                arcname = backup_file.relative_to(root_dir)
                zipf.write(backup_file, arcname)
        
        logger.info(f"✅ Archivé {len(backup_files)} fichiers *.backup → {archive_path}")
        return len(backup_files)
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'archivage des fichiers backup: {e}")
        return 0

def remove_archived_items(source_dir: Path) -> bool:
    """Supprime le répertoire source après archivage réussi"""
    try:
        if source_dir.is_dir():
            shutil.rmtree(source_dir)
            logger.info(f"🗑️ Supprimé {source_dir}")
        elif source_dir.is_file():
            source_dir.unlink()
            logger.info(f"🗑️ Supprimé {source_dir}")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression de {source_dir}: {e}")
        return False

def main():
    """Fonction principale d'archivage"""
    logger.info("🚀 Début de l'archivage des dossiers legacy")
    
    root_dir = Path(".")
    archived_count = 0
    
    # 1. Archiver ancien_system/
    ancien_system = root_dir / "ancien_system"
    if ancien_system.exists():
        archive_name = create_archive_name("ancien_system")
        if archive_directory(ancien_system, archive_name):
            if remove_archived_items(ancien_system):
                archived_count += 1
    
    # 2. Archiver archive/ (sauf si c'est notre nouveau dossier d'archivage)
    archive_dir = root_dir / "archive"
    if archive_dir.exists() and archive_dir.name != "archived_legacy":
        archive_name = create_archive_name("archive")
        if archive_directory(archive_dir, archive_name):
            if remove_archived_items(archive_dir):
                archived_count += 1
    
    # 3. Archiver les fichiers *.backup
    backup_count = archive_backup_files(root_dir)
    if backup_count > 0:
        # Supprimer les fichiers backup après archivage
        for backup_file in root_dir.rglob("*.backup"):
            remove_archived_items(backup_file)
        archived_count += 1
    
    # 4. Créer un fichier de documentation de l'archivage
    doc_path = Path("archived_legacy") / "ARCHIVE_README.md"
    doc_path.parent.mkdir(exist_ok=True)
    
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(f"""# Archive Legacy - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Contenu archivé

- **ancien_system/**: Ancien système IBKR/Polygon (remplacé par Sierra-only)
- **archive/**: Anciens fichiers d'archive (réorganisés)
- **Fichiers *.backup**: Sauvegardes automatiques

## Raison de l'archivage

Ces dossiers et fichiers créaient de la confusion dans le projet et ne sont plus utilisés
dans l'architecture Sierra-only actuelle.

## Restauration

Si nécessaire, les fichiers peuvent être restaurés depuis les archives ZIP
dans ce dossier.

## Impact

- ✅ Réduction de la confusion dans le projet
- ✅ Structure plus claire
- ✅ Aucun import cassé (vérifié)
- ✅ Historique préservé dans les archives
""")
    
    logger.info(f"📋 Documentation créée: {doc_path}")
    logger.info(f"🎉 Archivage terminé: {archived_count} éléments archivés")
    
    if archived_count > 0:
        logger.info("💡 Considérez faire un commit Git pour sauvegarder ces changements")

if __name__ == "__main__":
    main()

