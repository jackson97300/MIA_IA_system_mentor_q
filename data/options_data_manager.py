#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Options Data Manager
Gestion des données SPX options avec sauvegarde automatique
"""

import os
import json
import csv
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from core.logger import get_logger
logger = get_logger(__name__)

class DataSource(Enum):
    """Sources de données"""
    IBKR_REAL = "ibkr_real"
    SAVED_DATA = "saved_data"
    MOCK_DATA = "mock_data"

class DataQualityLevel(Enum):
    """Niveaux de qualité des données"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    CORRUPTED = "corrupted"

@dataclass
class OptionsDataSnapshot:
    """Snapshot de données SPX options"""
    timestamp: datetime
    data_source: DataSource
    spx_data: Dict[str, Any]
    quality_level: DataQualityLevel
    file_path: Optional[str] = None

@dataclass
class DataQualityReport:
    """Rapport de qualité des données"""
    timestamp: datetime
    quality_level: DataQualityLevel
    data_age_minutes: float
    completeness_score: float
    freshness_score: float
    recommendations: List[str]

class OptionsDataManager:
    """Gestionnaire de données SPX options"""
    
    def __init__(self, data_dir: str = "data/options_snapshots"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.hourly_dir = self.data_dir / "hourly"
        self.final_dir = self.data_dir / "final"
        self.hourly_dir.mkdir(exist_ok=True)
        self.final_dir.mkdir(exist_ok=True)
        
        logger.info(f"📊 OptionsDataManager initialisé: {self.data_dir}")
    
    def save_hourly_snapshot(self, spx_data: Dict[str, Any], data_source: DataSource) -> bool:
        """Sauvegarde snapshot horaire"""
        try:
            timestamp = datetime.now()
            filename = f"spx_hourly_{timestamp.strftime('%Y%m%d_%H')}.csv"
            filepath = self.hourly_dir / filename
            
            # Convertir en DataFrame et sauvegarder
            df = pd.DataFrame([{
                'timestamp': timestamp.isoformat(),
                'data_source': data_source.value,
                'spx_data': json.dumps(spx_data)
            }])
            
            df.to_csv(filepath, index=False)
            logger.info(f"✅ Snapshot horaire sauvegardé: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde horaire: {e}")
            return False
    
    def save_final_snapshot(self, spx_data: Dict[str, Any], data_source: DataSource) -> bool:
        """Sauvegarde snapshot final"""
        try:
            timestamp = datetime.now()
            filename = f"spx_final_{timestamp.strftime('%Y%m%d')}.csv"
            filepath = self.final_dir / filename
            
            # Convertir en DataFrame et sauvegarder
            df = pd.DataFrame([{
                'timestamp': timestamp.isoformat(),
                'data_source': data_source.value,
                'spx_data': json.dumps(spx_data)
            }])
            
            df.to_csv(filepath, index=False)
            logger.info(f"✅ Snapshot final sauvegardé: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde final: {e}")
            return False
    
    def get_latest_saved_data(self) -> Optional[Dict[str, Any]]:
        """Récupère les dernières données sauvegardées"""
        try:
            # Chercher dans les snapshots JSON (priorité)
            snapshot_files = list(self.data_dir.glob("spx_snapshot_*.json"))
            if snapshot_files:
                # Prendre le plus récent
                latest_file = max(snapshot_files, key=lambda x: x.stat().st_mtime)
                
                with open(latest_file, 'r', encoding='utf-8') as f:
                    spx_data = json.load(f)
                
                logger.info(f"✅ Données SPX récupérées: {latest_file.name}")
                return spx_data
            
            # Fallback: chercher dans les snapshots finaux
            final_files = list(self.final_dir.glob("spx_final_*.csv"))
            if not final_files:
                return None
            
            # Prendre le plus récent
            latest_file = max(final_files, key=lambda x: x.stat().st_mtime)
            
            df = pd.read_csv(latest_file)
            if df.empty:
                return None
            
            # Récupérer la dernière ligne
            latest_row = df.iloc[-1]
            spx_data = json.loads(latest_row['spx_data'])
            
            logger.info(f"✅ Données récupérées: {latest_file.name}")
            return spx_data
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération données: {e}")
            return None
    
    def validate_data_freshness(self, max_age_minutes: float = 60) -> DataQualityReport:
        """Valide la fraîcheur des données"""
        try:
            latest_data = self.get_latest_saved_data()
            if not latest_data:
                return DataQualityReport(
                    timestamp=datetime.now(),
                    quality_level=DataQualityLevel.POOR,
                    data_age_minutes=float('inf'),
                    completeness_score=0.0,
                    freshness_score=0.0,
                    recommendations=["Aucune donnée disponible"]
                )
            
            # Calculer l'âge des données
            data_timestamp = datetime.fromisoformat(latest_data.get('timestamp', datetime.now().isoformat()))
            age_minutes = (datetime.now() - data_timestamp).total_seconds() / 60
            
            # Évaluer la qualité
            if age_minutes <= 30:
                quality = DataQualityLevel.EXCELLENT
                freshness_score = 1.0
            elif age_minutes <= 60:
                quality = DataQualityLevel.GOOD
                freshness_score = 0.8
            elif age_minutes <= 120:
                quality = DataQualityLevel.ACCEPTABLE
                freshness_score = 0.6
            else:
                quality = DataQualityLevel.POOR
                freshness_score = 0.3
            
            recommendations = []
            if age_minutes > max_age_minutes:
                recommendations.append("Données trop anciennes")
            
            return DataQualityReport(
                timestamp=datetime.now(),
                quality_level=quality,
                data_age_minutes=age_minutes,
                completeness_score=0.9,  # Estimation
                freshness_score=freshness_score,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur validation fraîcheur: {e}")
            return DataQualityReport(
                timestamp=datetime.now(),
                quality_level=DataQualityLevel.CORRUPTED,
                data_age_minutes=float('inf'),
                completeness_score=0.0,
                freshness_score=0.0,
                recommendations=[f"Erreur validation: {e}"]
            )

    def load_latest_spx_snapshot(self, max_age_hours: float = 24) -> tuple[Optional[Dict[str, Any]], str]:
        """
        Charge le snapshot SPX le plus récent
        
        Args:
            max_age_hours: Âge maximum en heures
            
        Returns:
            (snapshot_data, status) où status = "FRESH", "STALE", "NO_FILE", "ERROR"
        """
        try:
            # Chercher tous les fichiers snapshot
            snapshot_files = list(self.data_dir.glob("spx_snapshot_*.json"))
            if not snapshot_files:
                logger.warning("⚠️ Aucun fichier snapshot SPX trouvé")
                return None, "NO_FILE"
            
            # Prendre le plus récent
            latest_file = max(snapshot_files, key=lambda x: x.stat().st_mtime)
            
            # Charger le JSON
            with open(latest_file, 'r', encoding='utf-8') as f:
                snapshot = json.load(f)
            
            # Vérifier la fraîcheur
            asof_str = snapshot.get("asof", "")
            if not asof_str:
                logger.warning("⚠️ Timestamp manquant dans le snapshot")
                return snapshot, "STALE"
            
            # Parser le timestamp
            try:
                if asof_str.endswith('Z'):
                    asof_str = asof_str.replace('Z', '+00:00')
                asof = datetime.fromisoformat(asof_str)
                age_hours = (datetime.now(asof.tzinfo) - asof).total_seconds() / 3600.0
            except Exception as e:
                logger.error(f"❌ Erreur parsing timestamp: {e}")
                return snapshot, "STALE"
            
            # Déterminer le statut
            if age_hours <= max_age_hours:
                status = "FRESH"
                logger.info(f"✅ Snapshot SPX chargé ({status}) - âge: {age_hours:.1f}h")
            else:
                status = "STALE"
                logger.warning(f"⚠️ Snapshot SPX chargé ({status}) - âge: {age_hours:.1f}h")
            
            return snapshot, status
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement snapshot SPX: {e}")
            return None, "ERROR"

    def save_spx_snapshot(self, spx_data: Dict[str, Any]) -> bool:
        """
        Sauvegarde un snapshot SPX au format JSON
        
        Args:
            spx_data: Données SPX à sauvegarder
            
        Returns:
            True si succès, False sinon
        """
        try:
            timestamp = datetime.now()
            filename = f"spx_snapshot_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.data_dir / filename
            
            # Ajouter le timestamp si pas présent
            if 'asof' not in spx_data:
                spx_data['asof'] = timestamp.isoformat()
            
            # Sauvegarder en JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(spx_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Snapshot SPX sauvegardé: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde snapshot SPX: {e}")
            return False

    def save_spx_data(self, spx_data: Dict[str, Any]) -> bool:
        """
        Méthode de compatibilité pour l'injection SPX
        
        Args:
            spx_data: Données SPX à sauvegarder
            
        Returns:
            True si succès, False sinon
        """
        return self.save_spx_snapshot(spx_data)

# Instance globale
OPTIONS_DATA_MANAGER = OptionsDataManager()

# Exports
__all__ = [
    'OptionsDataManager',
    'OptionsDataSnapshot',
    'DataQualityReport',
    'DataSource',
    'DataQualityLevel',
    'OPTIONS_DATA_MANAGER'
]
