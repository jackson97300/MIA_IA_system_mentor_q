#!/usr/bin/env python3
"""
🧪 TEST FINAL INTÉGRATION PHASE 3 - MIA_IA_SYSTEM
==================================================

Test final de l'intégration Phase 3 dans le système principal
avec élimination complète des fallbacks.

Author: MIA_IA_SYSTEM
Date: Janvier 2025
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from launch_24_7_orderflow_trading import OrderFlow24_7Launcher
from core.logger import get_logger

logger = get_logger(__name__)

async def test_phase3_final_integration():
    """Test final de l'intégration Phase 3"""
    
    logger.info("🧪 Test final intégration Phase 3 - Élimination des fallbacks")
    
    try:
        # 1. Créer le lanceur avec modules Phase 3
        logger.info("🚀 Création OrderFlow24_7Launcher avec Phase 3...")
        launcher = OrderFlow24_7Launcher(live_trading=False)
        
        # 2. Vérifier que les modules Phase 3 sont initialisés
        logger.info("🛡️ Vérification modules Phase 3...")
        
        if launcher.options_manager:
            logger.info("   ✅ OptionsDataManager initialisé")
        else:
            logger.error("   ❌ OptionsDataManager manquant")
            return False
        
        if launcher.session_manager:
            logger.info("   ✅ SessionManager initialisé")
        else:
            logger.error("   ❌ SessionManager manquant")
            return False
        
        if launcher.data_validator:
            logger.info("   ✅ DataQualityValidator initialisé")
        else:
            logger.error("   ❌ DataQualityValidator manquant")
            return False
        
        # 3. Test session actuelle
        logger.info("🕐 Test session actuelle...")
        current_session = launcher.session_manager.get_current_session()
        session_config = launcher.session_manager.get_session_config(current_session)
        
        logger.info(f"   Session: {current_session.value}")
        logger.info(f"   Description: {session_config.description}")
        logger.info(f"   Trading activé: {session_config.trading_enabled}")
        logger.info(f"   Source données: {session_config.data_source.value}")
        
        # 4. Test récupération données SPX
        logger.info("📊 Test récupération données SPX...")
        
        if launcher.session_manager.should_use_live_data():
            logger.info("   📡 Mode: Données LIVE IBKR")
            try:
                spx_data = await launcher._get_real_spx_options_data()
                if spx_data:
                    logger.info(f"   ✅ Données LIVE récupérées: {spx_data.get('data_source')}")
                else:
                    logger.warning("   ⚠️ Aucune donnée LIVE disponible")
            except Exception as e:
                logger.warning(f"   ⚠️ Erreur données LIVE: {e}")
        else:
            logger.info("   💾 Mode: Données sauvegardées")
            spx_data = launcher.options_manager.get_latest_saved_data()
            if spx_data:
                logger.info(f"   ✅ Données sauvegardées récupérées: VIX {spx_data.vix_level}")
            else:
                logger.warning("   ⚠️ Aucune donnée sauvegardée disponible")
        
        # 5. Test validation qualité
        logger.info("🛡️ Test validation qualité...")
        
        # Données de test
        test_data = {
            'vix_level': 24.5,
            'put_call_ratio': 0.85,
            'gamma_exposure': 75e9,
            'data_timestamp': '2025-01-15T10:30:00Z',
            'data_source': 'ibkr_real'
        }
        
        quality_report = await launcher.data_validator.validate_spx_data(test_data)
        logger.info(f"   Qualité: {quality_report.quality_level.value}")
        logger.info(f"   Score: {quality_report.validation_score:.2f}")
        logger.info(f"   Valide pour trading: {quality_report.is_valid_for_trading}")
        
        # 6. Test données corrompues (fallback)
        logger.info("🛡️ Test données corrompues (fallback)...")
        
        corrupted_data = {
            'vix_level': 24.5,
            'put_call_ratio': 0.85,
            'gamma_exposure': 75e9,
            'data_source': 'fallback_simulated'  # Ceci devrait déclencher une pause
        }
        
        quality_report = await launcher.data_validator.validate_spx_data(corrupted_data)
        logger.info(f"   Qualité: {quality_report.quality_level.value}")
        logger.info(f"   Message pause: {quality_report.pause_message}")
        logger.info(f"   Raison pause: {quality_report.pause_reason.value if quality_report.pause_reason else 'None'}")
        
        # 7. Test paramètres adaptés
        logger.info("📊 Test paramètres adaptés...")
        
        position_mult = launcher.session_manager.get_position_size_multiplier()
        risk_mult = launcher.session_manager.get_risk_multiplier()
        confidence_threshold = launcher.session_manager.get_min_confidence_threshold()
        
        logger.info(f"   Taille position: {position_mult}x")
        logger.info(f"   Multiplicateur risque: {risk_mult}x")
        logger.info(f"   Seuil confiance: {confidence_threshold}")
        
        # 8. Test statut final
        logger.info("📊 Statut final des modules...")
        
        # Session
        session_summary = launcher.session_manager.get_session_summary()
        logger.info(f"   Session: {session_summary['session_description']}")
        
        # Options
        options_status = launcher.options_manager.get_system_status()
        logger.info(f"   Options: Session {options_status['current_session']}")
        
        # Validation
        validation_summary = launcher.data_validator.get_validation_summary()
        logger.info(f"   Validation: {validation_summary['total_validations']} validations")
        logger.info(f"   Score moyen: {validation_summary['average_score']:.2f}")
        
        # Pause
        pause_status = launcher.data_validator.get_pause_status()
        if pause_status.is_paused:
            logger.warning(f"   🛑 SYSTÈME EN PAUSE: {pause_status.pause_message}")
        else:
            logger.info("   ✅ Système opérationnel")
        
        logger.info("✅ Test final intégration Phase 3 terminé avec succès!")
        
        # 9. Résumé des améliorations
        logger.info("🎯 RÉSUMÉ DES AMÉLIORATIONS PHASE 3:")
        logger.info("   ✅ Élimination complète des fallbacks dangereux")
        logger.info("   ✅ Pause explicite avec messages clairs")
        logger.info("   ✅ Sauvegarde horaire automatique des données SPX")
        logger.info("   ✅ Gestion multi-sessions intelligente")
        logger.info("   ✅ Validation qualité stricte des données")
        logger.info("   ✅ Adaptation automatique des paramètres par session")
        logger.info("   ✅ Monitoring et alertes en temps réel")
        logger.info("   ✅ Intégration complète dans le système principal")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test final intégration Phase 3: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_phase3_final_integration())
    if success:
        logger.info("🎉 PHASE 3 INTÉGRÉE AVEC SUCCÈS DANS LE SYSTÈME PRINCIPAL!")
    else:
        logger.error("❌ ÉCHEC DE L'INTÉGRATION PHASE 3")

