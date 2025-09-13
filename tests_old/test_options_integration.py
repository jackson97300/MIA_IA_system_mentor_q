#!/usr/bin/env python3
"""
🧪 TEST INTÉGRATION OPTIONS DATA MANAGER
========================================

Test de l'intégration entre OptionsDataManager et SPXOptionsRetriever
pour vérifier la sauvegarde horaire et la récupération des données.

Author: MIA_IA_SYSTEM
Date: Janvier 2025
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from data.options_data_manager import create_options_data_manager
from features.spx_options_retriever import create_spx_options_retriever
from core.logger import get_logger

logger = get_logger(__name__)

async def test_options_integration():
    """Test complet de l'intégration options data manager"""
    
    logger.info("🧪 Test intégration OptionsDataManager + SPXOptionsRetriever")
    
    try:
        # 1. Créer le OptionsDataManager
        logger.info("📊 Création OptionsDataManager...")
        options_manager = create_options_data_manager()
        
        # 2. Créer le SPXOptionsRetriever (sans IBKR pour le test)
        logger.info("📊 Création SPXOptionsRetriever...")
        spx_retriever = create_spx_options_retriever()
        
        # 3. Test données simulées
        logger.info("📊 Test avec données simulées...")
        test_data = {
            'vix_level': 24.5,
            'put_call_ratio': 0.85,
            'put_call_volume_ratio': 0.92,
            'call_volume': 150000,
            'put_volume': 138000,
            'call_oi': 2500000,
            'put_oi': 2200000,
            'gamma_exposure': 75e9,
            'dealer_gamma_position': 'long_gamma',
            'gamma_flip_level': 4850.0,
            'nearby_pin_levels': [4800.0, 4850.0, 4900.0],
            'unusual_options_activity': False
        }
        
        # 4. Test sauvegarde automatique
        logger.info("💾 Test sauvegarde automatique...")
        await spx_retriever._save_spx_data_automatically(test_data)
        
        # 5. Test récupération données sauvegardées
        logger.info("📊 Test récupération données sauvegardées...")
        saved_data = spx_retriever.get_saved_spx_data()
        
        if saved_data:
            logger.info(f"✅ Données sauvegardées récupérées:")
            logger.info(f"   - VIX: {saved_data['vix_level']}")
            logger.info(f"   - Put/Call Ratio: {saved_data['put_call_ratio']}")
            logger.info(f"   - Gamma Exposure: {saved_data['gamma_exposure']}")
            logger.info(f"   - Âge: {saved_data.get('data_age_hours', 'N/A')}h")
            logger.info(f"   - Qualité: {saved_data.get('data_quality', 'N/A')}")
        else:
            logger.warning("⚠️ Aucune donnée sauvegardée trouvée")
        
        # 6. Test statut système
        logger.info("📊 Test statut système...")
        status = options_manager.get_system_status()
        logger.info(f"   - Session actuelle: {status['current_session']}")
        logger.info(f"   - Dernière sauvegarde horaire: {status['last_hourly_backup']}")
        logger.info(f"   - Dernière sauvegarde finale: {status['last_final_backup']}")
        
        # 7. Test validation fraîcheur
        logger.info("🔍 Test validation fraîcheur...")
        snapshot = options_manager.get_latest_saved_data()
        if snapshot:
            report = options_manager.validate_data_freshness(snapshot)
            logger.info(f"   - Fraîcheur: {report.freshness_level.value}")
            logger.info(f"   - Valide pour trading: {report.is_valid_for_trading}")
            logger.info(f"   - Avertissements: {report.warnings}")
            logger.info(f"   - Recommandations: {report.recommendations}")
        
        logger.info("✅ Test intégration terminé avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur test intégration: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_options_integration())

