#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Vérifier et Utiliser Options Backup
Vérifie les données options sauvegardées et les prépare pour utilisation
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.logger import get_logger

logger = get_logger(__name__)

def check_available_backups():
    """Vérifier les sauvegardes disponibles"""
    backup_dir = Path("data/backups")
    
    if not backup_dir.exists():
        logger.error("❌ Répertoire backups non trouvé")
        return []
    
    # Chercher les sauvegardes options
    options_backups = []
    for item in backup_dir.iterdir():
        if item.is_dir() and "options_spx" in item.name:
            options_backups.append(item)
    
    return sorted(options_backups, key=lambda x: x.name, reverse=True)

def analyze_backup_quality(backup_path):
    """Analyser la qualité d'une sauvegarde"""
    logger.info(f"🔍 Analyse de la sauvegarde: {backup_path.name}")
    
    # Vérifier les fichiers disponibles
    files_found = []
    required_files = [
        "options_snapshots/spx_final_20250811.json",
        "options_snapshots/spx_final_20250811.csv",
        "metadata_options.txt"
    ]
    
    for required_file in required_files:
        file_path = backup_path / required_file
        if file_path.exists():
            files_found.append(required_file)
            logger.info(f"✅ {required_file}")
        else:
            logger.warning(f"⚠️ {required_file} - MANQUANT")
    
    # Calculer le score de qualité
    quality_score = len(files_found) / len(required_files)
    
    return {
        "backup_path": backup_path,
        "files_found": files_found,
        "quality_score": quality_score,
        "is_usable": quality_score >= 0.7  # 70% minimum
    }

def load_best_backup():
    """Charger la meilleure sauvegarde disponible"""
    backups = check_available_backups()
    
    if not backups:
        logger.error("❌ Aucune sauvegarde options trouvée")
        return None
    
    logger.info(f"📊 {len(backups)} sauvegardes trouvées")
    
    # Analyser chaque sauvegarde
    backup_analyses = []
    for backup in backups:
        analysis = analyze_backup_quality(backup)
        backup_analyses.append(analysis)
        logger.info(f"📈 {backup.name}: Score {analysis['quality_score']:.1%}")
    
    # Sélectionner la meilleure
    best_backup = max(backup_analyses, key=lambda x: x['quality_score'])
    
    if not best_backup['is_usable']:
        logger.error("❌ Aucune sauvegarde utilisable trouvée")
        return None
    
    logger.info(f"🎯 Meilleure sauvegarde: {best_backup['backup_path'].name}")
    return best_backup

def create_options_config(backup_analysis):
    """Créer la configuration options pour le système"""
    
    backup_path = backup_analysis['backup_path']
    
    # Charger les données JSON
    json_file = backup_path / "options_snapshots" / "spx_final_20250811.json"
    
    if not json_file.exists():
        logger.error(f"❌ Fichier JSON non trouvé: {json_file}")
        return None
    
    try:
        with open(json_file, 'r') as f:
            options_data = json.load(f)
        
        # Créer la configuration
        config = {
            "options_backup": {
                "enabled": True,
                "source": str(backup_path),
                "quality_score": backup_analysis['quality_score'],
                "files_available": backup_analysis['files_found'],
                "load_time": datetime.now().isoformat()
            },
            "gamma_levels_proximity": {
                "enabled": True,
                "source": "backup",
                "weight": 0.28,
                "data": options_data
            },
            "session_config": {
                "current_session": "london",
                "options_available": True,
                "backup_date": "2025-08-11",
                "valid_until": "2025-08-12T15:30:00"
            }
        }
        
        return config
        
    except Exception as e:
        logger.error(f"❌ Erreur chargement données: {e}")
        return None

def save_options_config(config):
    """Sauvegarder la configuration options"""
    config_dir = Path("data/preparation")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / "options_backup_config.json"
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"✅ Configuration options sauvegardée: {config_file}")
    return config_file

def main():
    """Fonction principale"""
    logger.info("🔍 Vérification des sauvegardes options...")
    
    # 1. Vérifier les sauvegardes disponibles
    backup_analysis = load_best_backup()
    if not backup_analysis:
        logger.error("❌ Impossible de trouver une sauvegarde utilisable")
        return False
    
    # 2. Créer la configuration options
    config = create_options_config(backup_analysis)
    if not config:
        logger.error("❌ Impossible de créer la configuration")
        return False
    
    # 3. Sauvegarder la configuration
    config_file = save_options_config(config)
    
    # 4. Afficher le résumé
    logger.info("📊 RÉSUMÉ CONFIGURATION OPTIONS:")
    logger.info(f"   📁 Source: {config['options_backup']['source']}")
    logger.info(f"   📈 Qualité: {config['options_backup']['quality_score']:.1%}")
    logger.info(f"   🎯 Gamma Levels: {'✅ Activé' if config['gamma_levels_proximity']['enabled'] else '❌ Désactivé'}")
    logger.info(f"   📊 Poids: {config['gamma_levels_proximity']['weight']*100}%")
    logger.info(f"   ⏰ Valide jusqu'à: {config['session_config']['valid_until']}")
    
    logger.info("✅ Configuration options prête pour utilisation!")
    logger.info(f"💡 Utilisez cette configuration avec: python lance_london_with_options_backup.py")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        sys.exit(1)






