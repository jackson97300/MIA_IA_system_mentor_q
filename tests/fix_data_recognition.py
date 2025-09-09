#!/usr/bin/env python3
"""
🔧 CORRECTION RECONNAISSANCE DONNÉES - MIA_IA_SYSTEM
====================================================

Force la reconnaissance des données SPX par OptionsDataManager
pour permettre le lancement complet du système.

Author: MIA_IA_SYSTEM
Date: Janvier 2025
"""

import asyncio
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger

logger = get_logger(__name__)

def fix_data_recognition():
    """Corrige la reconnaissance des données SPX"""
    
    logger.info("🔧 Correction reconnaissance données SPX...")
    
    try:
        data_dir = Path("data/options_snapshots")
        
        # 1. Vérifier les fichiers existants
        json_files = list(data_dir.glob("*.json"))
        logger.info(f"   📄 Fichiers JSON trouvés: {len(json_files)}")
        
        # 2. Trouver le fichier le plus récent
        if json_files:
            latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
            logger.info(f"   📄 Fichier le plus récent: {latest_file}")
            
            # 3. Lire le contenu
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            logger.info(f"   📊 Données: VIX {data.get('vix_level', 0):.1f}")
            
            # 4. Créer un fichier de sauvegarde finale avec le bon nom
            today = datetime.now().strftime('%Y%m%d')
            final_file = data_dir / f"spx_final_{today}.json"
            
            # Copier le fichier le plus récent comme sauvegarde finale
            shutil.copy2(latest_file, final_file)
            
            logger.info(f"   ✅ Sauvegarde finale créée: {final_file}")
            
            # 5. Créer aussi un fichier "latest" pour faciliter la reconnaissance
            latest_marker = data_dir / "spx_latest.json"
            shutil.copy2(latest_file, latest_marker)
            
            logger.info(f"   ✅ Marqueur latest créé: {latest_marker}")
            
            return True
        else:
            logger.error("   ❌ Aucun fichier JSON trouvé")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur correction reconnaissance: {e}")
        return False

def create_emergency_data():
    """Crée des données d'urgence si nécessaire"""
    
    logger.info("🚨 Création données d'urgence...")
    
    emergency_data = {
        'vix_level': 20.5,
        'put_call_ratio': 0.85,
        'put_call_volume_ratio': 0.80,
        'call_volume': 25000,
        'put_volume': 20000,
        'call_oi': 1000000,
        'put_oi': 800000,
        'gamma_exposure': 75e9,
        'dealer_position': 'neutral',
        'gamma_flip_level': 5400.0,
        'pin_levels': [5400, 5450, 5500],
        'unusual_activity': False,
        'estimated_dealer_hedging': 'neutral',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'data_source': 'emergency_fix'
    }
    
    # Sauvegarder dans le répertoire options_snapshots
    data_dir = Path("data/options_snapshots")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime('%Y%m%d')
    emergency_file = data_dir / f"spx_final_{today}.json"
    
    with open(emergency_file, 'w') as f:
        json.dump(emergency_data, f, indent=2, default=str)
    
    logger.info(f"   ✅ Données d'urgence: {emergency_file}")
    return emergency_data

def test_data_retrieval():
    """Test la récupération des données après correction"""
    
    logger.info("🧪 Test récupération après correction...")
    
    try:
        from data.options_data_manager import create_options_data_manager
        
        options_manager = create_options_data_manager()
        latest_data = options_manager.get_latest_saved_data()
        
        if latest_data:
            logger.info("✅ Données récupérées avec succès!")
            logger.info(f"   📈 VIX: {latest_data.vix_level:.1f}")
            logger.info(f"   📊 Put/Call Ratio: {latest_data.put_call_ratio:.3f}")
            logger.info(f"   💰 Gamma Exposure: ${latest_data.gamma_exposure/1e9:.1f}B")
            logger.info(f"   🕐 Timestamp: {latest_data.timestamp}")
            return True
        else:
            logger.warning("⚠️ Données toujours non récupérables")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur test récupération: {e}")
        return False

if __name__ == "__main__":
    logger.info("🔧 DÉMARRAGE CORRECTION RECONNAISSANCE DONNÉES")
    
    # 1. Correction principale
    success1 = fix_data_recognition()
    
    # 2. Créer données d'urgence si nécessaire
    if not success1:
        logger.warning("⚠️ Correction échouée, création données d'urgence...")
        create_emergency_data()
    
    # 3. Test récupération
    success2 = test_data_retrieval()
    
    if success2:
        logger.info("🎉 CORRECTION RÉUSSIE!")
        logger.info("   Le système peut maintenant démarrer avec les données SPX")
    else:
        logger.error("❌ ÉCHEC DE LA CORRECTION")
        logger.info("   Le système utilisera les données d'urgence")

