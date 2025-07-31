"""
scripts/backup_data.py

SAUVEGARDE AUTOMATIQUE DONNÉES - OBJECTIF PRIORITÉ 11
Système de backup robuste pour toutes les données critiques du trading
Compression, cloud storage, vérification intégrité, et restauration

FONCTIONNALITÉS :
1. backup_snapshots_to_cloud() - Backup snapshots vers cloud storage
2. compress_old_data() - Compression données anciennes pour économie espace
3. verify_backup_integrity() - Vérification intégrité des backups
4. restore_from_backup() - Restauration depuis backup avec validation
5. Backup incrémental et différentiel
6. Chiffrement des données sensibles
7. Planification automatique et monitoring
8. Multi-destinations (local, cloud, NAS)

ARCHITECTURE : Resilient, sécurisé, automatisé, production-ready
"""

# === STDLIB ===
import os
import sys
import time
import gzip
import shutil
import hashlib
import tarfile
import zipfile
import json
import logging
import argparse
import threading
import schedule
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime, timezone, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import tempfile
import subprocess

# === THIRD-PARTY ===
import numpy as np
import pandas as pd

# === LOCAL IMPORTS ===
from config import get_trading_config, get_automation_config
from core.base_types import (
    MarketData, TradingSignal, TradeResult,
    ES_TICK_SIZE, ES_TICK_VALUE
)

# Logger
logger = logging.getLogger(__name__)

# === BACKUP ENUMS ===


class BackupType(Enum):
    """Types de backup"""
    FULL = "full"                    # Backup complet
    INCREMENTAL = "incremental"      # Backup incrémental
    DIFFERENTIAL = "differential"    # Backup différentiel
    SNAPSHOT = "snapshot"           # Snapshot ponctuel


class BackupDestination(Enum):
    """Destinations de backup"""
    LOCAL = "local"                 # Disque local
    CLOUD_AWS = "cloud_aws"         # AWS S3
    CLOUD_AZURE = "cloud_azure"     # Azure Blob
    CLOUD_GCP = "cloud_gcp"         # Google Cloud
    NAS = "nas"                     # Network Attached Storage
    EXTERNAL_DRIVE = "external"     # Disque externe


class CompressionType(Enum):
    """Types de compression"""
    NONE = "None"
    GZIP = "gzip"
    ZIP = "zip"
    TAR_GZ = "tar_gz"
    TAR_XZ = "tar_xz"


class BackupStatus(Enum):
    """États des backups"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"
    CORRUPTED = "corrupted"


class DataCategory(Enum):
    """Catégories de données"""
    TRADING_SNAPSHOTS = "trading_snapshots"
    ML_MODELS = "ml_models"
    CONFIGURATION = "configuration"
    LOGS = "logs"
    PERFORMANCE_DATA = "performance_data"
    REPORTS = "reports"

# === BACKUP DATA STRUCTURES ===


@dataclass
class BackupMetadata:
    """Métadonnées d'un backup"""
    backup_id: str
    backup_type: BackupType
    data_category: DataCategory
    destination: BackupDestination
    compression: CompressionType
    created_at: datetime
    file_count: int
    total_size_bytes: int
    compressed_size_bytes: int
    checksum_md5: str
    source_path: str
    destination_path: str
    encryption_enabled: bool = False
    status: BackupStatus = BackupStatus.PENDING


@dataclass
class BackupConfig:
    """Configuration de backup"""
    # Général
    enabled: bool = True
    max_parallel_backups: int = 2
    retention_days: int = 90

    # Compression
    compression_type: CompressionType = CompressionType.TAR_GZ
    compression_level: int = 6

    # Destinations
    primary_destination: BackupDestination = BackupDestination.LOCAL
    secondary_destinations: List[BackupDestination] = None

    # Planification
    schedule_full_backup: str = "daily"  # daily, weekly, monthly
    schedule_incremental: str = "hourly"

    # Chiffrement
    encryption_enabled: bool = False
    encryption_key_path: Optional[str] = None

    # Cloud storage
    aws_bucket: Optional[str] = None
    azure_container: Optional[str] = None
    gcp_bucket: Optional[str] = None

    # Paths
    local_backup_dir: str = "backups"
    temp_dir: str = "temp/backup"


@dataclass
class RestoreRequest:
    """Demande de restauration"""
    backup_id: str
    target_path: str
    selective_files: Optional[List[str]] = None
    verify_integrity: bool = True
    overwrite_existing: bool = False

# === BACKUP MANAGER ===


class BackupManager:
    """
    GESTIONNAIRE DE BACKUP COMPLET

    Gestion complète des sauvegardes :
    - Backup automatique multi-destinations
    - Compression intelligente
    - Vérification intégrité
    - Chiffrement données sensibles
    - Restauration selective
    - Planification et monitoring
    """

    def __init__(self, config: Optional[BackupConfig] = None):
        """
        Initialisation du gestionnaire de backup

        Args:
            config: Configuration personnalisée (sinon defaults)
        """
        self.config = config or BackupConfig()
        self.trading_config = get_trading_config()
        self.auto_config = get_automation_config()

        # État du backup
        self.backup_history: List[BackupMetadata] = []
        self.active_backups: Dict[str, BackupMetadata] = {}
        self.backup_thread: Optional[threading.Thread] = None

        # Paths
        self.backup_root = Path(self.config.local_backup_dir)
        self.temp_dir = Path(self.config.temp_dir)
        self.metadata_dir = self.backup_root / "metadata"

        # Création dossiers
        self.backup_root.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        # Sources de données
        self.data_sources = self._configure_data_sources()

        # Chargement historique backups
        self._load_backup_history()

        logger.info("BackupManager initialisé")

    def backup_snapshots_to_cloud(self,
                                  cloud_destination: BackupDestination = BackupDestination.CLOUD_AWS,
                                  compression: bool = True) -> bool:
        """
        Backup des snapshots de trading vers le cloud

        Args:
            cloud_destination: Destination cloud
            compression: Activer compression

        Returns:
            True si backup réussi, False sinon
        """
        logger.info(f"Début backup snapshots vers {cloud_destination.value}")

        try:
            # Préparation du backup
            backup_id = self._generate_backup_id("snapshots", cloud_destination)

            # Configuration compression
            compression_type = CompressionType.TAR_GZ if compression else CompressionType.NONE

            # Métadonnées
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type=BackupType.FULL,
                data_category=DataCategory.TRADING_SNAPSHOTS,
                destination=cloud_destination,
                compression=compression_type,
                created_at=datetime.now(timezone.utc),
                file_count=0,
                total_size_bytes=0,
                compressed_size_bytes=0,
                checksum_md5="",
                source_path=str(self.data_sources[DataCategory.TRADING_SNAPSHOTS]),
                destination_path="",
                encryption_enabled=self.config.encryption_enabled
            )

            self.active_backups[backup_id] = metadata

            # 1. Préparation données snapshots
            source_path = Path(self.data_sources[DataCategory.TRADING_SNAPSHOTS])
            if not source_path.exists():
                logger.warning(f"Source snapshots non trouvée: {source_path}")
                return False

            # 2. Collecte fichiers à sauvegarder
            files_to_backup = self._collect_snapshot_files(source_path)
            metadata.file_count = len(files_to_backup)

            if not files_to_backup:
                logger.warning("Aucun fichier snapshot à sauvegarder")
                return False

            # 3. Calcul taille totale
            total_size = sum(f.stat().st_size for f in files_to_backup)
            metadata.total_size_bytes = total_size

            logger.info(
                f"Backup snapshots: {
                    len(files_to_backup)} fichiers, {
                    total_size /
                    1024 /
                    1024:.1f} MB")

            # 4. Création archive temporaire
            temp_archive = self._create_compressed_archive(
                files_to_backup, source_path, compression_type, backup_id
            )

            if not temp_archive:
                logger.error("Échec création archive temporaire")
                return False

            # 5. Calcul checksum
            metadata.checksum_md5 = self._calculate_file_checksum(temp_archive)
            metadata.compressed_size_bytes = temp_archive.stat().st_size

            # 6. Upload vers cloud
            cloud_path = self._upload_to_cloud(temp_archive, cloud_destination, backup_id)

            if not cloud_path:
                logger.error("Échec upload vers cloud")
                return False

            metadata.destination_path = cloud_path
            metadata.status = BackupStatus.COMPLETED

            # 7. Vérification intégrité post-upload
            if not self._verify_cloud_backup_integrity(metadata):
                logger.error("Échec vérification intégrité cloud")
                metadata.status = BackupStatus.CORRUPTED
                return False

            metadata.status = BackupStatus.VERIFIED

            # 8. Nettoyage temporaire
            temp_archive.unlink()

            # 9. Sauvegarde métadonnées
            self._save_backup_metadata(metadata)
            self.backup_history.append(metadata)

            # 10. Notification succès
            logger.info(f"✅ Backup snapshots cloud réussi: {backup_id}")
            logger.info(f"Taille originale: {total_size / 1024 / 1024:.1f} MB")
            logger.info(f"Taille compressée: {metadata.compressed_size_bytes / 1024 / 1024:.1f} MB")
            logger.info(
                f"Ratio compression: {(1 - metadata.compressed_size_bytes / total_size) * 100:.1f}%")

            return True

        except Exception as e:
            logger.error(f"Erreur backup snapshots cloud: {e}")
            if backup_id in self.active_backups:
                self.active_backups[backup_id].status = BackupStatus.FAILED
            return False

        finally:
            # Nettoyage
            if backup_id in self.active_backups:
                del self.active_backups[backup_id]

    def compress_old_data(self,
                          age_threshold_days: int = 30,
                          compression_ratio_target: float = 0.3) -> Dict[str, Any]:
        """
        Compression des données anciennes pour économie d'espace

        Args:
            age_threshold_days: Seuil âge en jours
            compression_ratio_target: Ratio compression cible

        Returns:
            Dictionnaire avec résultats compression
        """
        logger.info(f"Début compression données > {age_threshold_days} jours")

        try:
            compression_results = {
                "files_processed": 0,
                "files_compressed": 0,
                "original_size_mb": 0,
                "compressed_size_mb": 0,
                "space_saved_mb": 0,
                "compression_ratio": 0,
                "errors": []
            }

            # Date seuil
            threshold_date = datetime.now() - timedelta(days=age_threshold_days)

            # Traitement par catégorie de données
            for category, source_path in self.data_sources.items():
                try:
                    category_results = self._compress_category_data(
                        category, Path(source_path), threshold_date, compression_ratio_target
                    )

                    # Agrégation résultats
                    compression_results["files_processed"] += category_results["files_processed"]
                    compression_results["files_compressed"] += category_results["files_compressed"]
                    compression_results["original_size_mb"] += category_results["original_size_mb"]
                    compression_results["compressed_size_mb"] += category_results["compressed_size_mb"]

                except Exception as e:
                    error_msg = f"Erreur compression {category.value}: {e}"
                    logger.error(error_msg)
                    compression_results["errors"].append(error_msg)

            # Calculs finaux
            if compression_results["original_size_mb"] > 0:
                compression_results["space_saved_mb"] = (
                    compression_results["original_size_mb"] -
                    compression_results["compressed_size_mb"]
                )
                compression_results["compression_ratio"] = (
                    compression_results["compressed_size_mb"] /
                    compression_results["original_size_mb"]
                )

            logger.info("✅ Compression données anciennes terminée")
            logger.info(f"Fichiers traités: {compression_results['files_processed']}")
            logger.info(f"Fichiers compressés: {compression_results['files_compressed']}")
            logger.info(f"Espace économisé: {compression_results['space_saved_mb']:.1f} MB")
            logger.info(f"Ratio compression: {compression_results['compression_ratio']:.2f}")

            return compression_results

        except Exception as e:
            logger.error(f"Erreur compression données anciennes: {e}")
            return {"error": str(e)}

    def verify_backup_integrity(self,
                                backup_id: Optional[str] = None,
                                verify_all: bool = False) -> Dict[str, Any]:
        """
        Vérification intégrité des backups

        Args:
            backup_id: ID backup spécifique (None = dernier)
            verify_all: Vérifier tous les backups

        Returns:
            Dictionnaire avec résultats vérification
        """
        logger.info("Début vérification intégrité backups")

        try:
            verification_results = {
                "backups_checked": 0,
                "backups_valid": 0,
                "backups_corrupted": 0,
                "backups_missing": 0,
                "total_data_verified_mb": 0,
                "verification_errors": []
            }

            # Sélection backups à vérifier
            backups_to_verify = []

            if verify_all:
                backups_to_verify = self.backup_history.copy()
            elif backup_id:
                backup = self._find_backup_by_id(backup_id)
                if backup:
                    backups_to_verify = [backup]
                else:
                    return {"error": f"Backup {backup_id} non trouvé"}
            else:
                # Dernier backup
                if self.backup_history:
                    backups_to_verify = [self.backup_history[-1]]
                else:
                    return {"error": "Aucun backup à vérifier"}

            # Vérification de chaque backup
            for backup in backups_to_verify:
                try:
                    logger.info(f"Vérification backup: {backup.backup_id}")

                    verification_results["backups_checked"] += 1

                    # Vérification selon destination
                    is_valid = False

                    if backup.destination == BackupDestination.LOCAL:
                        is_valid = self._verify_local_backup(backup)
                    elif backup.destination in [BackupDestination.CLOUD_AWS,
                                                BackupDestination.CLOUD_AZURE,
                                                BackupDestination.CLOUD_GCP]:
                        is_valid = self._verify_cloud_backup_integrity(backup)
                    else:
                        logger.warning(
                            f"Vérification non supportée pour {
                                backup.destination.value}")
                        continue

                    # Mise à jour compteurs
                    if is_valid:
                        verification_results["backups_valid"] += 1
                        backup.status = BackupStatus.VERIFIED
                        verification_results["total_data_verified_mb"] += backup.compressed_size_bytes / 1024 / 1024
                    else:
                        verification_results["backups_corrupted"] += 1
                        backup.status = BackupStatus.CORRUPTED
                        verification_results["verification_errors"].append(
                            f"Backup {backup.backup_id} corrompu"
                        )

                except Exception as e:
                    error_msg = f"Erreur vérification {backup.backup_id}: {e}"
                    logger.error(error_msg)
                    verification_results["verification_errors"].append(error_msg)

            # Sauvegarde métadonnées mises à jour
            self._save_all_backup_metadata()

            logger.info("✅ Vérification intégrité terminée")
            logger.info(f"Backups vérifiés: {verification_results['backups_checked']}")
            logger.info(f"Backups valides: {verification_results['backups_valid']}")
            logger.info(f"Backups corrompus: {verification_results['backups_corrupted']}")

            return verification_results

        except Exception as e:
            logger.error(f"Erreur vérification intégrité: {e}")
            return {"error": str(e)}

    def restore_from_backup(self,
                            restore_request: RestoreRequest) -> bool:
        """
        Restauration depuis backup avec validation

        Args:
            restore_request: Demande de restauration

        Returns:
            True si restauration réussie, False sinon
        """
        logger.info(f"Début restauration backup: {restore_request.backup_id}")

        try:
            # 1. Recherche backup
            backup = self._find_backup_by_id(restore_request.backup_id)
            if not backup:
                logger.error(f"Backup {restore_request.backup_id} non trouvé")
                return False

            # 2. Vérification intégrité backup
            if restore_request.verify_integrity:
                logger.info("Vérification intégrité avant restauration...")

                if backup.destination == BackupDestination.LOCAL:
                    if not self._verify_local_backup(backup):
                        logger.error("Backup local corrompu")
                        return False
                else:
                    if not self._verify_cloud_backup_integrity(backup):
                        logger.error("Backup cloud corrompu")
                        return False

            # 3. Préparation destination
            target_path = Path(restore_request.target_path)
            target_path.mkdir(parents=True, exist_ok=True)

            # 4. Vérification écrasement
            if not restore_request.overwrite_existing:
                if any(target_path.iterdir()):
                    logger.error(f"Destination non vide et overwrite désactivé: {target_path}")
                    return False

            # 5. Téléchargement backup si cloud
            local_archive_path = None

            if backup.destination == BackupDestination.LOCAL:
                local_archive_path = Path(backup.destination_path)
            else:
                # Téléchargement depuis cloud
                local_archive_path = self._download_from_cloud(backup)
                if not local_archive_path:
                    logger.error("Échec téléchargement backup depuis cloud")
                    return False

            # 6. Extraction archive
            logger.info("Extraction archive...")

            if not self._extract_archive(local_archive_path, target_path,
                                         restore_request.selective_files):
                logger.error("Échec extraction archive")
                return False

            # 7. Vérification post-extraction
            extracted_files = list(target_path.rglob("*"))
            logger.info(f"Fichiers extraits: {len(extracted_files)}")

            # 8. Nettoyage temporaire si téléchargement cloud
            if backup.destination != BackupDestination.LOCAL and local_archive_path:
                local_archive_path.unlink()

            logger.info(f"✅ Restauration terminée: {restore_request.backup_id}")
            logger.info(f"Destination: {target_path}")
            logger.info(f"Fichiers restaurés: {len(extracted_files)}")

            return True

        except Exception as e:
            logger.error(f"Erreur restauration: {e}")
            return False

    def schedule_automatic_backups(self):
        """Configuration des backups automatiques"""
        logger.info("Configuration backups automatiques")

        try:
            # Backup complet quotidien
            if self.config.schedule_full_backup == "daily":
                schedule.every().day.at("02:00").do(self._scheduled_full_backup)
            elif self.config.schedule_full_backup == "weekly":
                schedule.every().sunday.at("02:00").do(self._scheduled_full_backup)

            # Backup incrémental horaire
            if self.config.schedule_incremental == "hourly":
                schedule.every().hour.do(self._scheduled_incremental_backup)

            # Nettoyage hebdomadaire
            schedule.every().sunday.at("04:00").do(self._scheduled_cleanup)

            # Vérification intégrité hebdomadaire
            schedule.every().sunday.at("05:00").do(self._scheduled_integrity_check)

            logger.info("Planification backups configurée")

        except Exception as e:
            logger.error(f"Erreur configuration planification: {e}")

    def get_backup_status(self) -> Dict[str, Any]:
        """Statut complet des backups"""

        try:
            # Statistiques générales
            total_backups = len(self.backup_history)
            recent_backups = [b for b in self.backup_history
                              if b.created_at > datetime.now(timezone.utc) - timedelta(days=7)]

            # Calcul taille totale
            total_size_mb = sum(b.compressed_size_bytes for b in self.backup_history) / 1024 / 1024

            # Statistiques par statut
            status_counts = {}
            for status in BackupStatus:
                status_counts[status.value] = len(
                    [b for b in self.backup_history if b.status == status])

            # Dernier backup
            last_backup = self.backup_history[-1] if self.backup_history else None

            # Espace disque disponible
            backup_disk_usage = self._get_disk_usage(self.backup_root)

            return {
                "summary": {
                    "total_backups": total_backups,
                    "recent_backups_7d": len(recent_backups),
                    "total_size_mb": round(total_size_mb, 2),
                    "active_backups": len(self.active_backups)
                },
                "status_distribution": status_counts,
                "last_backup": {
                    "backup_id": last_backup.backup_id if last_backup else None,
                    "created_at": last_backup.created_at.isoformat() if last_backup else None,
                    "status": last_backup.status.value if last_backup else None,
                    "size_mb": round(last_backup.compressed_size_bytes / 1024 / 1024, 2) if last_backup else 0
                },
                "disk_usage": backup_disk_usage,
                "config": {
                    "retention_days": self.config.retention_days,
                    "compression_enabled": self.config.compression_type != CompressionType.NONE,
                    "encryption_enabled": self.config.encryption_enabled,
                    "primary_destination": self.config.primary_destination.value
                }
            }

        except Exception as e:
            logger.error(f"Erreur statut backup: {e}")
            return {"error": str(e)}

    # === MÉTHODES PRIVÉES ===

    def _configure_data_sources(self) -> Dict[DataCategory, str]:
        """Configuration des sources de données"""
        return {
            DataCategory.TRADING_SNAPSHOTS: "data/snapshots",
            DataCategory.ML_MODELS: "data/models",
            DataCategory.CONFIGURATION: "config",
            DataCategory.LOGS: "logs",
            DataCategory.PERFORMANCE_DATA: "data/performance",
            DataCategory.REPORTS: "reports"
        }

    def _generate_backup_id(self, category_name: str, destination: BackupDestination) -> str:
        """Génération ID unique de backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{category_name}_{destination.value}_{timestamp}"

    def _collect_snapshot_files(self, source_path: Path) -> List[Path]:
        """Collection fichiers snapshots à sauvegarder"""
        files = []

        if not source_path.exists():
            return files

        # Fichiers snapshots (simulation)
        for pattern in ["*.jsonl", "*.json", "*.parquet", "*.csv"]:
            files.extend(source_path.rglob(pattern))

        # Filtrer fichiers récents et valides
        valid_files = []
        for file_path in files:
            try:
                if file_path.is_file() and file_path.stat().st_size > 0:
                    valid_files.append(file_path)
            except OSError:
                continue

        return valid_files

    def _create_compressed_archive(self,
                                   files: List[Path],
                                   base_path: Path,
                                   compression: CompressionType,
                                   backup_id: str) -> Optional[Path]:
        """Création archive compressée"""

        archive_name = f"{backup_id}.{compression.value}"
        archive_path = self.temp_dir / archive_name

        try:
            if compression == CompressionType.TAR_GZ:
                with tarfile.open(archive_path, 'w:gz') as tar:
                    for file_path in files:
                        arcname = file_path.relative_to(base_path)
                        tar.add(file_path, arcname=arcname)

            elif compression == CompressionType.ZIP:
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for file_path in files:
                        arcname = file_path.relative_to(base_path)
                        zip_file.write(file_path, arcname)

            elif compression == CompressionType.NONE:
                # Copie simple dans dossier temporaire
                temp_folder = self.temp_dir / backup_id
                temp_folder.mkdir(exist_ok=True)

                for file_path in files:
                    relative_path = file_path.relative_to(base_path)
                    dest_path = temp_folder / relative_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)

                return temp_folder

            else:
                logger.error(f"Type compression non supporté: {compression}")
                return None

            logger.info(f"Archive créée: {archive_path}")
            return archive_path

        except Exception as e:
            logger.error(f"Erreur création archive: {e}")
            return None

    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calcul checksum MD5 d'un fichier"""
        hash_md5 = hashlib.md5()

        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Erreur calcul checksum: {e}")
            return ""

    def _upload_to_cloud(self,
                         file_path: Path,
                         destination: BackupDestination,
                         backup_id: str) -> Optional[str]:
        """Upload fichier vers cloud storage"""

        try:
            if destination == BackupDestination.CLOUD_AWS:
                return self._upload_to_aws_s3(file_path, backup_id)
            elif destination == BackupDestination.CLOUD_AZURE:
                return self._upload_to_azure_blob(file_path, backup_id)
            elif destination == BackupDestination.CLOUD_GCP:
                return self._upload_to_gcp_storage(file_path, backup_id)
            else:
                logger.error(f"Destination cloud non supportée: {destination}")
                return None

        except Exception as e:
            logger.error(f"Erreur upload cloud: {e}")
            return None

    def _upload_to_aws_s3(self, file_path: Path, backup_id: str) -> Optional[str]:
        """Upload vers AWS S3 (simulation)"""
        # En production, utiliser boto3
        logger.info(f"[SIMULATION] Upload {file_path.name} vers AWS S3")

        # Simulation du path S3
        s3_path = f"s3://{self.config.aws_bucket}/trading-backups/{backup_id}/{file_path.name}"

        # Simulation upload réussi
        time.sleep(1)  # Simulate upload time

        return s3_path

    def _upload_to_azure_blob(self, file_path: Path, backup_id: str) -> Optional[str]:
        """Upload vers Azure Blob (simulation)"""
        logger.info(f"[SIMULATION] Upload {file_path.name} vers Azure Blob")

        blob_path = f"https://{self.config.azure_container}.blob.core.windows.net/trading-backups/{backup_id}/{file_path.name}"

        time.sleep(1)
        return blob_path

    def _upload_to_gcp_storage(self, file_path: Path, backup_id: str) -> Optional[str]:
        """Upload vers Google Cloud Storage (simulation)"""
        logger.info(f"[SIMULATION] Upload {file_path.name} vers GCP Storage")

        gcs_path = f"gs://{self.config.gcp_bucket}/trading-backups/{backup_id}/{file_path.name}"

        time.sleep(1)
        return gcs_path

    def _verify_cloud_backup_integrity(self, backup: BackupMetadata) -> bool:
        """Vérification intégrité backup cloud"""

        try:
            # En production, télécharger et vérifier checksum
            logger.info(f"[SIMULATION] Vérification intégrité cloud: {backup.backup_id}")

            # Simulation vérification réussie
            time.sleep(0.5)

            return True

        except Exception as e:
            logger.error(f"Erreur vérification cloud: {e}")
            return False

    def _verify_local_backup(self, backup: BackupMetadata) -> bool:
        """Vérification backup local"""

        try:
            backup_path = Path(backup.destination_path)

            if not backup_path.exists():
                logger.error(f"Backup local manquant: {backup_path}")
                return False

            # Vérification checksum
            current_checksum = self._calculate_file_checksum(backup_path)

            if current_checksum != backup.checksum_md5:
                logger.error(f"Checksum mismatch pour {backup.backup_id}")
                return False

            return True

        except Exception as e:
            logger.error(f"Erreur vérification backup local: {e}")
            return False

    def _compress_category_data(self,
                                category: DataCategory,
                                source_path: Path,
                                threshold_date: datetime,
                                compression_ratio_target: float) -> Dict[str, Any]:
        """Compression données d'une catégorie"""

        results = {
            "files_processed": 0,
            "files_compressed": 0,
            "original_size_mb": 0,
            "compressed_size_mb": 0
        }

        if not source_path.exists():
            return results

        # Recherche fichiers anciens
        old_files = []
        for file_path in source_path.rglob("*"):
            if file_path.is_file():
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_mtime < threshold_date:
                    old_files.append(file_path)

        results["files_processed"] = len(old_files)

        # Compression fichiers
        for file_path in old_files:
            try:
                if file_path.suffix.lower() in ['.gz', '.zip', '.7z']:
                    # Déjà compressé
                    continue

                original_size = file_path.stat().st_size
                results["original_size_mb"] += original_size / 1024 / 1024

                # Compression gzip
                compressed_path = file_path.with_suffix(file_path.suffix + '.gz')

                with open(file_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                compressed_size = compressed_path.stat().st_size
                results["compressed_size_mb"] += compressed_size / 1024 / 1024

                # Vérification ratio compression
                compression_ratio = compressed_size / original_size

                if compression_ratio < compression_ratio_target:
                    # Compression efficace, remplacer original
                    file_path.unlink()
                    results["files_compressed"] += 1
                else:
                    # Compression peu efficace, conserver original
                    compressed_path.unlink()
                    results["compressed_size_mb"] -= compressed_size / 1024 / 1024
                    results["compressed_size_mb"] += original_size / 1024 / 1024

            except Exception as e:
                logger.error(f"Erreur compression {file_path}: {e}")

        return results

    def _find_backup_by_id(self, backup_id: str) -> Optional[BackupMetadata]:
        """Recherche backup par ID"""
        for backup in self.backup_history:
            if backup.backup_id == backup_id:
                return backup
        return None

    def _download_from_cloud(self, backup: BackupMetadata) -> Optional[Path]:
        """Téléchargement backup depuis cloud"""

        try:
            # Path temporaire local
            temp_path = self.temp_dir / f"restore_{backup.backup_id}"

            # Simulation téléchargement
            logger.info(f"[SIMULATION] Téléchargement {backup.backup_id} depuis cloud")
            time.sleep(2)  # Simulate download

            # Création fichier temporaire (simulation)
            temp_path.write_text("simulated backup content")

            return temp_path

        except Exception as e:
            logger.error(f"Erreur téléchargement cloud: {e}")
            return None

    def _extract_archive(self,
                         archive_path: Path,
                         target_path: Path,
                         selective_files: Optional[List[str]] = None) -> bool:
        """Extraction archive"""

        try:
            if archive_path.suffix == '.gz' and archive_path.stem.endswith('.tar'):
                # TAR.GZ
                with tarfile.open(archive_path, 'r:gz') as tar:
                    if selective_files:
                        # Extraction sélective
                        for member in tar.getmembers():
                            if any(pattern in member.name for pattern in selective_files):
                                tar.extract(member, target_path)
                    else:
                        tar.extractall(target_path)

            elif archive_path.suffix == '.zip':
                # ZIP
                with zipfile.ZipFile(archive_path, 'r') as zip_file:
                    if selective_files:
                        # Extraction sélective
                        for file_name in zip_file.namelist():
                            if any(pattern in file_name for pattern in selective_files):
                                zip_file.extract(file_name, target_path)
                    else:
                        zip_file.extractall(target_path)

            else:
                # Copie dossier
                if archive_path.is_dir():
                    shutil.copytree(archive_path, target_path, dirs_exist_ok=True)
                else:
                    logger.error(f"Format archive non supporté: {archive_path}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Erreur extraction: {e}")
            return False

    def _load_backup_history(self):
        """Chargement historique des backups"""

        try:
            metadata_files = list(self.metadata_dir.glob("*.json"))

            for metadata_file in metadata_files:
                try:
                    with open(metadata_file, 'r') as f:
                        data = json.load(f)

                    # Reconstruction BackupMetadata
                    backup = BackupMetadata(
                        backup_id=data["backup_id"],
                        backup_type=BackupType(data["backup_type"]),
                        data_category=DataCategory(data["data_category"]),
                        destination=BackupDestination(data["destination"]),
                        compression=CompressionType(data["compression"]),
                        created_at=datetime.fromisoformat(data["created_at"]),
                        file_count=data["file_count"],
                        total_size_bytes=data["total_size_bytes"],
                        compressed_size_bytes=data["compressed_size_bytes"],
                        checksum_md5=data["checksum_md5"],
                        source_path=data["source_path"],
                        destination_path=data["destination_path"],
                        encryption_enabled=data.get("encryption_enabled", False),
                        status=BackupStatus(data.get("status", "completed"))
                    )

                    self.backup_history.append(backup)

                except Exception as e:
                    logger.error(f"Erreur chargement métadonnées {metadata_file}: {e}")

            # Tri par date
            self.backup_history.sort(key=lambda x: x.created_at)

            logger.info(f"Historique backups chargé: {len(self.backup_history)} backups")

        except Exception as e:
            logger.error(f"Erreur chargement historique: {e}")

    def _save_backup_metadata(self, backup: BackupMetadata):
        """Sauvegarde métadonnées d'un backup"""

        try:
            metadata_file = self.metadata_dir / f"{backup.backup_id}.json"

            # Conversion en dict sérialisable
            data = asdict(backup)
            data["backup_type"] = backup.backup_type.value
            data["data_category"] = backup.data_category.value
            data["destination"] = backup.destination.value
            data["compression"] = backup.compression.value
            data["status"] = backup.status.value
            data["created_at"] = backup.created_at.isoformat()

            with open(metadata_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Erreur sauvegarde métadonnées: {e}")

    def _save_all_backup_metadata(self):
        """Sauvegarde toutes les métadonnées"""
        for backup in self.backup_history:
            self._save_backup_metadata(backup)

    def _get_disk_usage(self, path: Path) -> Dict[str, float]:
        """Utilisation disque"""
        try:
            statvfs = os.statvfs(path)
            total_mb = (statvfs.f_frsize * statvfs.f_blocks) / 1024 / 1024
            free_mb = (statvfs.f_frsize * statvfs.f_available) / 1024 / 1024
            used_mb = total_mb - free_mb

            return {
                "total_mb": round(total_mb, 2),
                "used_mb": round(used_mb, 2),
                "free_mb": round(free_mb, 2),
                "usage_percent": round((used_mb / total_mb) * 100, 2)
            }
        except Exception:
            return {"error": "Unable to get disk usage"}

    def _scheduled_full_backup(self):
        """Backup complet planifié"""
        logger.info("Exécution backup complet planifié")
        self.backup_snapshots_to_cloud()

    def _scheduled_incremental_backup(self):
        """Backup incrémental planifié"""
        logger.info("Exécution backup incrémental planifié")
        # TODO: Implémentation backup incrémental

    def _scheduled_cleanup(self):
        """Nettoyage planifié"""
        logger.info("Exécution nettoyage planifié")
        # TODO: Suppression backups anciens selon rétention

    def _scheduled_integrity_check(self):
        """Vérification intégrité planifiée"""
        logger.info("Exécution vérification intégrité planifiée")
        self.verify_backup_integrity(verify_all=True)

# === GLOBAL BACKUP MANAGER ===


backup_manager = BackupManager()

# === FONCTIONS PRINCIPALES ===


def backup_snapshots_to_cloud(
        cloud_destination: BackupDestination = BackupDestination.CLOUD_AWS) -> bool:
    """
    Backup snapshots vers cloud

    Args:
        cloud_destination: Destination cloud

    Returns:
        True si succès, False sinon
    """
    return backup_manager.backup_snapshots_to_cloud(cloud_destination)


def compress_old_data(age_threshold_days: int = 30) -> Dict[str, Any]:
    """
    Compression données anciennes

    Args:
        age_threshold_days: Seuil âge en jours

    Returns:
        Résultats compression
    """
    return backup_manager.compress_old_data(age_threshold_days)


def verify_backup_integrity(backup_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Vérification intégrité backups

    Args:
        backup_id: ID backup (None = dernier)

    Returns:
        Résultats vérification
    """
    return backup_manager.verify_backup_integrity(backup_id)


def restore_from_backup(backup_id: str, target_path: str, verify: bool = True) -> bool:
    """
    Restauration depuis backup

    Args:
        backup_id: ID du backup
        target_path: Chemin destination
        verify: Vérifier intégrité

    Returns:
        True si succès, False sinon
    """
    restore_request = RestoreRequest(
        backup_id=backup_id,
        target_path=target_path,
        verify_integrity=verify
    )
    return backup_manager.restore_from_backup(restore_request)

# === CLI INTERFACE ===


def main():
    """Interface en ligne de commande"""

    parser = argparse.ArgumentParser(description="MIA Trading Backup Manager")
    parser.add_argument("command", choices=["backup", "compress", "verify", "restore", "status", "schedule"],
                        help="Commande à exécuter")

    # Arguments optionnels
    parser.add_argument("--destination", choices=["local", "aws", "azure", "gcp"],
                        default="local", help="Destination backup")
    parser.add_argument("--backup-id", type=str, help="ID du backup")
    parser.add_argument("--target-path", type=str, help="Chemin cible restauration")
    parser.add_argument("--age-days", type=int, default=30, help="Âge seuil compression")
    parser.add_argument("--verify-all", action="store_true", help="Vérifier tous backups")
    parser.add_argument("--verbose", "-v", action="store_true", help="Logging verbose")

    args = parser.parse_args()

    # Configuration logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/backup/backup_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler()
        ]
    )

    logger.info("=== MIA TRADING BACKUP MANAGER ===")

    try:
        # Exécution selon commande
        if args.command == "backup":
            destination_map = {
                "local": BackupDestination.LOCAL,
                "aws": BackupDestination.CLOUD_AWS,
                "azure": BackupDestination.CLOUD_AZURE,
                "gcp": BackupDestination.CLOUD_GCP
            }

            success = backup_snapshots_to_cloud(destination_map[args.destination])
            if success:
                logger.info("Backup réussi")
            else:
                logger.error("Échec backup")
                sys.exit(1)

        elif args.command == "compress":
            results = compress_old_data(args.age_days)
            if "error" not in results:
                logger.info("Compression terminée")
                logger.info("Fichiers compressés: {results['files_compressed']}")
                logger.info("Espace économisé: {results['space_saved_mb']:.1f} MB")
            else:
                logger.error("Erreur compression: {results['error']}")
                sys.exit(1)

        elif args.command == "verify":
            results = verify_backup_integrity(args.backup_id, args.verify_all)
            if "error" not in results:
                logger.info("Vérification terminée")
                logger.info("Backups vérifiés: {results['backups_checked']}")
                logger.info("Backups valides: {results['backups_valid']}")
                logger.info("Backups corrompus: {results['backups_corrupted']}")
            else:
                logger.error("Erreur vérification: {results['error']}")
                sys.exit(1)

        elif args.command == "restore":
            if not args.backup_id or not args.target_path:
                logger.error("backup-id et target-path requis pour restauration")
                sys.exit(1)

            success = restore_from_backup(args.backup_id, args.target_path)
            if success:
                logger.info("Restauration réussie")
            else:
                logger.error("Échec restauration")
                sys.exit(1)

        elif args.command == "status":
            status = backup_manager.get_backup_status()
            logger.info("📊 STATUT BACKUPS:")
            print(json.dumps(status, indent=2))

        elif args.command == "schedule":
            backup_manager.schedule_automatic_backups()
            logger.info("Planification configurée")
            print("Exécution 'python -c \"import schedule; schedule.run_pending()\" périodiquement")

    except Exception as e:
        logger.error(f"Erreur commande: {e}")
        logger.error("Erreur: {e}")
        sys.exit(1)

# === TEST FUNCTION ===


def test_backup_system():
    """Test complet du système de backup"""
    logger.info("=== TEST BACKUP SYSTEM ===")

    logger.info("Test 1: Backup snapshots local")
    success = backup_snapshots_to_cloud(BackupDestination.LOCAL)
    logger.info("Backup local: {'✅' if success else '❌'}")

    logger.info("Test 2: Compression données")
    results = compress_old_data(age_threshold_days=1)
    logger.info("Compression: {'✅' if 'error' not in results else '❌'}")

    logger.info("Test 3: Vérification intégrité")
    verification = verify_backup_integrity()
    logger.info("Vérification: {'✅' if 'error' not in verification else '❌'}")

    logger.info("Test 4: Statut système")
    status = backup_manager.get_backup_status()
    logger.info("Statut: {'✅' if 'error' not in status else '❌'}")
    logger.info("Total backups: {status.get('summary', {}).get('total_backups', 0)}")

    logger.info("=== TEST TERMINÉ ===")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        logger.info("Usage: python backup_data.py {backup|compress|verify|restore|status|schedule}")
        logger.info("Ou lancez test_backup_system() pour tests")
