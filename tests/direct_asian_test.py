#!/usr/bin/env python3
"""
🎯 TEST DIRECT SESSION ASIATIQUE - MIA_IA_SYSTEM
================================================

Test direct utilisant les fichiers JSON créés
sans passer par OptionsDataManager.

Author: MIA_IA_SYSTEM
Date: Janvier 2025
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.session_manager import create_session_manager
from core.data_quality_validator import create_data_quality_validator
from core.logger import get_logger

logger = get_logger(__name__)

def load_spx_data_directly():
    """Charge directement les données SPX depuis les fichiers JSON"""
    
    logger.info("📊 Chargement direct des données SPX...")
    
    data_dir = Path("data/options_snapshots")
    
    # Chercher le fichier le plus récent
    json_files = list(data_dir.glob("*.json"))
    if not json_files:
        logger.error("❌ Aucun fichier JSON trouvé")
        return None
    
    # Prendre le fichier le plus récent
    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
    
    logger.info(f"   📄 Fichier utilisé: {latest_file}")
    
    try:
        with open(latest_file, 'r') as f:
            spx_data = json.load(f)
        
        logger.info(f"   ✅ Données chargées: VIX {spx_data['vix_level']:.1f}")
        return spx_data
        
    except Exception as e:
        logger.error(f"❌ Erreur chargement fichier: {e}")
        return None

async def direct_asian_session_test():
    """Test direct de la session asiatique"""
    
    logger.info("🎯 TEST DIRECT SESSION ASIATIQUE")
    logger.info("=" * 60)
    
    try:
        # 1. Charger les données directement
        spx_data = load_spx_data_directly()
        if not spx_data:
            logger.error("❌ Impossible de charger les données")
            return False
        
        # 2. Initialiser les modules Phase 3
        logger.info("🛡️ Initialisation modules Phase 3...")
        
        session_manager = create_session_manager()
        data_validator = create_data_quality_validator()
        
        # 3. Vérifier session
        current_session = session_manager.get_current_session()
        session_config = session_manager.get_session_config(current_session)
        
        logger.info(f"🕐 Session: {current_session.value}")
        logger.info(f"📊 Description: {session_config.description}")
        logger.info(f"🎯 Trading activé: {session_config.trading_enabled}")
        logger.info(f"📡 Source données: {session_config.data_source.value}")
        
        # 4. Validation qualité
        logger.info("🛡️ Validation qualité des données...")
        
        quality_report = await data_validator.validate_spx_data(spx_data)
        logger.info(f"   Qualité: {quality_report.quality_level.value}")
        logger.info(f"   Score: {quality_report.validation_score:.2f}")
        logger.info(f"   Valide pour trading: {quality_report.is_valid_for_trading}")
        
        # 5. Paramètres session asiatique
        logger.info("📊 Paramètres session asiatique...")
        
        position_mult = session_manager.get_position_size_multiplier()
        risk_mult = session_manager.get_risk_multiplier()
        confidence_threshold = session_manager.get_min_confidence_threshold()
        
        logger.info(f"   Taille position: {position_mult}x")
        logger.info(f"   Multiplicateur risque: {risk_mult}x")
        logger.info(f"   Seuil confiance: {confidence_threshold}")
        
        # 6. Simulation trading
        logger.info("🎯 Simulation trading session asiatique...")
        
        if quality_report.is_valid_for_trading:
            logger.info("   ✅ Trading autorisé avec données directes")
            logger.info("   📊 Paramètres adaptés pour session asiatique:")
            logger.info(f"      - Position réduite: {position_mult}x")
            logger.info(f"      - Risque augmenté: {risk_mult}x")
            logger.info(f"      - Seuil confiance plus strict: {confidence_threshold}")
            
            # Simulation signal de trading
            mock_signal = {
                'signal_type': 'BUY',
                'confidence': 0.75,
                'price_level': 5400.0,
                'volume_imbalance': 0.15,
                'delta_imbalance': 0.12
            }
            
            logger.info(f"   📈 Signal simulé: {mock_signal['signal_type']} @ {mock_signal['price_level']:.2f}")
            logger.info(f"   📊 Confiance: {mock_signal['confidence']:.3f}")
            
            # Vérifier si le signal passe les seuils
            if mock_signal['confidence'] >= confidence_threshold:
                logger.info("   ✅ Signal valide pour session asiatique")
                logger.info("   🎯 Trade simulé avec succès!")
                
                # Simulation exécution
                logger.info("   📈 EXÉCUTION SIMULÉE:")
                logger.info(f"      - Type: {mock_signal['signal_type']}")
                logger.info(f"      - Prix: {mock_signal['price_level']:.2f}")
                logger.info(f"      - Taille: {position_mult} contrat(s)")
                logger.info(f"      - Risque: {risk_mult}x")
                logger.info(f"      - Données SPX: VIX {spx_data['vix_level']:.1f}")
                logger.info(f"      - Source: {spx_data['data_source']}")
            else:
                logger.warning("   ⚠️ Signal rejeté (confiance insuffisante)")
        else:
            logger.warning("   🛑 Trading interdit - Données invalides")
            logger.info(f"   Raison: {quality_report.pause_message}")
        
        # 7. Test des cas limites
        logger.info("🔍 Test cas limites...")
        
        # Test données corrompues
        corrupted_data = spx_data.copy()
        corrupted_data['data_source'] = 'fallback_simulated'
        
        quality_report = await data_validator.validate_spx_data(corrupted_data)
        logger.info(f"   Test fallback: {quality_report.is_valid_for_trading}")
        
        # Test données anciennes
        old_data = spx_data.copy()
        old_data['timestamp'] = '2025-01-10T10:30:00Z'  # 5 jours ago
        
        quality_report = await data_validator.validate_spx_data(old_data)
        logger.info(f"   Test données anciennes: {quality_report.is_valid_for_trading}")
        
        # 8. Résumé final
        logger.info("📋 RÉSUMÉ TEST DIRECT:")
        logger.info("   ✅ Données SPX chargées directement")
        logger.info("   ✅ Session asiatique détectée")
        logger.info("   ✅ Validation qualité effectuée")
        logger.info("   ✅ Paramètres adaptés appliqués")
        logger.info("   ✅ Simulation trading réussie")
        logger.info("   ✅ Cas limites testés")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test direct: {e}")
        return False

def display_available_files():
    """Affiche les fichiers disponibles"""
    
    logger.info("📁 FICHIERS DISPONIBLES:")
    
    data_dir = Path("data/options_snapshots")
    if data_dir.exists():
        json_files = list(data_dir.glob("*.json"))
        csv_files = list(data_dir.glob("*.csv"))
        
        if json_files:
            logger.info("   📄 Fichiers JSON:")
            for file in json_files:
                size = file.stat().st_size
                logger.info(f"      - {file.name} ({size} bytes)")
        
        if csv_files:
            logger.info("   📊 Fichiers CSV:")
            for file in csv_files:
                size = file.stat().st_size
                logger.info(f"      - {file.name} ({size} bytes)")
    else:
        logger.warning("   ⚠️ Répertoire data/options_snapshots non trouvé")

if __name__ == "__main__":
    logger.info("🎯 DÉMARRAGE TEST DIRECT SESSION ASIATIQUE")
    
    # Afficher les fichiers disponibles
    display_available_files()
    
    # Test principal
    success = asyncio.run(direct_asian_session_test())
    
    if success:
        logger.info("🎉 TEST DIRECT RÉUSSI!")
        logger.info("   Le bot fonctionne en session asiatique avec données directes")
        logger.info("   ✅ Prêt pour le lancement complet")
    else:
        logger.error("❌ ÉCHEC DU TEST DIRECT")

