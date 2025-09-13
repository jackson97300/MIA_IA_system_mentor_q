#!/usr/bin/env python3
"""
🔧 CRÉATION DONNÉES SPX UTILISABLES - SESSION ASIATIQUE
=======================================================

Crée des données SPX directement utilisables par le système
en contournant les limitations de session.

Author: MIA_IA_SYSTEM
Date: Janvier 2025
"""

import asyncio
import sys
import json
import csv
from pathlib import Path
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from typing import List, Optional

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger

logger = get_logger(__name__)

@dataclass
class SPXSnapshot:
    """Structure de données SPX compatible avec le système"""
    vix_level: float
    put_call_ratio: float
    put_call_volume_ratio: float
    call_volume: int
    put_volume: int
    call_oi: int
    put_oi: int
    gamma_exposure: float
    dealer_position: str
    gamma_flip_level: float
    pin_levels: List[int]
    unusual_activity: bool
    estimated_dealer_hedging: str
    timestamp: datetime
    data_source: str

def create_working_spx_data():
    """Crée des données SPX directement utilisables"""
    
    logger.info("🔧 Création données SPX utilisables...")
    
    # Créer plusieurs snapshots avec des timestamps différents
    snapshots = []
    
    # Snapshot 1 - 2h ago
    snapshot1 = SPXSnapshot(
        vix_level=20.5,
        put_call_ratio=0.85,
        put_call_volume_ratio=0.80,
        call_volume=25000,
        put_volume=20000,
        call_oi=1000000,
        put_oi=800000,
        gamma_exposure=75e9,
        dealer_position='neutral',
        gamma_flip_level=5400.0,
        pin_levels=[5400, 5450, 5500],
        unusual_activity=False,
        estimated_dealer_hedging='neutral',
        timestamp=datetime.now(timezone.utc) - timedelta(hours=2),
        data_source='asian_session_test'
    )
    snapshots.append(snapshot1)
    
    # Snapshot 2 - 1h ago
    snapshot2 = SPXSnapshot(
        vix_level=21.2,
        put_call_ratio=0.88,
        put_call_volume_ratio=0.82,
        call_volume=28000,
        put_volume=23000,
        call_oi=1100000,
        put_oi=850000,
        gamma_exposure=78e9,
        dealer_position='slightly_long',
        gamma_flip_level=5410.0,
        pin_levels=[5400, 5450, 5500, 5550],
        unusual_activity=False,
        estimated_dealer_hedging='slight_buying',
        timestamp=datetime.now(timezone.utc) - timedelta(hours=1),
        data_source='asian_session_test'
    )
    snapshots.append(snapshot2)
    
    # Snapshot 3 - 30min ago
    snapshot3 = SPXSnapshot(
        vix_level=19.8,
        put_call_ratio=0.82,
        put_call_volume_ratio=0.78,
        call_volume=22000,
        put_volume=18000,
        call_oi=950000,
        put_oi=750000,
        gamma_exposure=72e9,
        dealer_position='slightly_short',
        gamma_flip_level=5390.0,
        pin_levels=[5380, 5400, 5450, 5500],
        unusual_activity=True,
        estimated_dealer_hedging='slight_selling',
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=30),
        data_source='asian_session_test'
    )
    snapshots.append(snapshot3)
    
    return snapshots

def save_snapshots_to_files(snapshots: List[SPXSnapshot]):
    """Sauvegarde les snapshots dans différents formats"""
    
    logger.info("📊 Sauvegarde des snapshots...")
    
    # Créer le répertoire de données
    data_dir = Path("data/options_snapshots")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Sauvegarder en JSON (format principal)
    for i, snapshot in enumerate(snapshots):
        # Convertir en dictionnaire
        snapshot_dict = {
            'vix_level': snapshot.vix_level,
            'put_call_ratio': snapshot.put_call_ratio,
            'put_call_volume_ratio': snapshot.put_call_volume_ratio,
            'call_volume': snapshot.call_volume,
            'put_volume': snapshot.put_volume,
            'call_oi': snapshot.call_oi,
            'put_oi': snapshot.put_oi,
            'gamma_exposure': snapshot.gamma_exposure,
            'dealer_position': snapshot.dealer_position,
            'gamma_flip_level': snapshot.gamma_flip_level,
            'pin_levels': snapshot.pin_levels,
            'unusual_activity': snapshot.unusual_activity,
            'estimated_dealer_hedging': snapshot.estimated_dealer_hedging,
            'timestamp': snapshot.timestamp.isoformat(),
            'data_source': snapshot.data_source
        }
        
        # Fichier horaire
        hourly_file = data_dir / f"spx_hourly_{snapshot.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        with open(hourly_file, 'w') as f:
            json.dump(snapshot_dict, f, indent=2, default=str)
        
        logger.info(f"   ✅ Snapshot {i+1} sauvegardé: {hourly_file}")
    
    # 2. Sauvegarder le plus récent comme sauvegarde finale
    latest_snapshot = snapshots[-1]
    final_file = data_dir / f"spx_final_{datetime.now().strftime('%Y%m%d')}.json"
    
    final_dict = {
        'vix_level': latest_snapshot.vix_level,
        'put_call_ratio': latest_snapshot.put_call_ratio,
        'put_call_volume_ratio': latest_snapshot.put_call_volume_ratio,
        'call_volume': latest_snapshot.call_volume,
        'put_volume': latest_snapshot.put_volume,
        'call_oi': latest_snapshot.call_oi,
        'put_oi': latest_snapshot.put_oi,
        'gamma_exposure': latest_snapshot.gamma_exposure,
        'dealer_position': latest_snapshot.dealer_position,
        'gamma_flip_level': latest_snapshot.gamma_flip_level,
        'pin_levels': latest_snapshot.pin_levels,
        'unusual_activity': latest_snapshot.unusual_activity,
        'estimated_dealer_hedging': latest_snapshot.estimated_dealer_hedging,
        'timestamp': latest_snapshot.timestamp.isoformat(),
        'data_source': latest_snapshot.data_source
    }
    
    with open(final_file, 'w') as f:
        json.dump(final_dict, f, indent=2, default=str)
    
    logger.info(f"   ✅ Sauvegarde finale: {final_file}")
    
    # 3. Créer un fichier CSV pour compatibilité
    csv_file = data_dir / f"spx_data_{datetime.now().strftime('%Y%m%d')}.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'timestamp', 'vix_level', 'put_call_ratio', 'gamma_exposure',
            'dealer_position', 'gamma_flip_level', 'data_source'
        ])
        
        for snapshot in snapshots:
            writer.writerow([
                snapshot.timestamp.isoformat(),
                snapshot.vix_level,
                snapshot.put_call_ratio,
                snapshot.gamma_exposure,
                snapshot.dealer_position,
                snapshot.gamma_flip_level,
                snapshot.data_source
            ])
    
    logger.info(f"   ✅ Fichier CSV: {csv_file}")
    
    return snapshots

def create_mock_options_manager():
    """Crée un mock OptionsDataManager pour les tests"""
    
    logger.info("🔧 Création mock OptionsDataManager...")
    
    # Créer un fichier de configuration mock
    mock_config = {
        'data_directory': 'data/options_snapshots',
        'max_age_hours': 18.0,
        'hourly_backup_enabled': True,
        'final_backup_enabled': True
    }
    
    config_file = Path("data/mock_options_config.json")
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w') as f:
        json.dump(mock_config, f, indent=2)
    
    logger.info(f"   ✅ Configuration mock: {config_file}")
    
    return mock_config

async def test_data_retrieval():
    """Test la récupération des données créées"""
    
    logger.info("🧪 Test récupération des données...")
    
    try:
        # Importer OptionsDataManager
        from data.options_data_manager import create_options_data_manager
        
        # Créer une instance
        options_manager = create_options_data_manager()
        
        # Essayer de récupérer les données
        latest_data = options_manager.get_latest_saved_data()
        
        if latest_data:
            logger.info("✅ Données récupérées avec succès!")
            logger.info(f"   📈 VIX: {latest_data.vix_level:.1f}")
            logger.info(f"   📊 Put/Call Ratio: {latest_data.put_call_ratio:.3f}")
            logger.info(f"   💰 Gamma Exposure: ${latest_data.gamma_exposure/1e9:.1f}B")
            logger.info(f"   🕐 Timestamp: {latest_data.timestamp}")
            return True
        else:
            logger.warning("⚠️ Données non récupérables via OptionsDataManager")
            logger.info("   Utilisation des fichiers JSON directement")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur test récupération: {e}")
        return False

if __name__ == "__main__":
    logger.info("🔧 DÉMARRAGE CRÉATION DONNÉES SPX UTILISABLES")
    
    # 1. Créer les données
    snapshots = create_working_spx_data()
    
    # 2. Sauvegarder dans les fichiers
    save_snapshots_to_files(snapshots)
    
    # 3. Créer mock config
    create_mock_options_manager()
    
    # 4. Tester la récupération
    success = asyncio.run(test_data_retrieval())
    
    if success:
        logger.info("🎉 DONNÉES CRÉÉES ET RÉCUPÉRABLES!")
        logger.info("   Le système peut maintenant utiliser ces données")
    else:
        logger.info("⚠️ Données créées mais récupération limitée")
        logger.info("   Utiliser les fichiers JSON directement pour les tests")
    
    # 5. Afficher les fichiers créés
    logger.info("📁 FICHIERS CRÉÉS:")
    data_dir = Path("data/options_snapshots")
    for file in data_dir.glob("*.json"):
        logger.info(f"   📄 {file}")
    for file in data_dir.glob("*.csv"):
        logger.info(f"   📊 {file}")

