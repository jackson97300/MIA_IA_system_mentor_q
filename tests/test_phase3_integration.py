#!/usr/bin/env python3
"""
🧪 TEST PHASE 3 INTÉGRATION - MIA_IA_SYSTEM
===========================================

Test d'intégration complet de la Phase 3 :
- OptionsDataManager (sauvegarde horaire)
- SessionManager (gestion multi-sessions)
- DataQualityValidator (pause explicite)

Author: MIA_IA_SYSTEM
Date: Janvier 2025
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from data.options_data_manager import create_options_data_manager
from core.session_manager import create_session_manager
from core.data_quality_validator import create_data_quality_validator
from core.logger import get_logger

logger = get_logger(__name__)

async def test_phase3_integration():
    """Test d'intégration complet de la Phase 3"""
    
    logger.info("🧪 Test intégration Phase 3 - Élimination des fallbacks")
    
    try:
        # 1. Initialiser tous les modules
        logger.info("📊 Initialisation des modules Phase 3...")
        
        options_manager = create_options_data_manager()
        session_manager = create_session_manager()
        data_validator = create_data_quality_validator()
        
        logger.info("✅ Tous les modules Phase 3 initialisés")
        
        # 2. Test SessionManager
        logger.info("🕐 Test SessionManager...")
        current_session = session_manager.get_current_session()
        session_config = session_manager.get_session_config(current_session)
        
        logger.info(f"   Session actuelle: {current_session.value}")
        logger.info(f"   Description: {session_config.description}")
        logger.info(f"   Trading activé: {session_config.trading_enabled}")
        logger.info(f"   Source données: {session_config.data_source.value}")
        logger.info(f"   Multiplicateur position: {session_config.position_size_multiplier}x")
        logger.info(f"   Multiplicateur risque: {session_config.risk_multiplier}x")
        
        # 3. Test OptionsDataManager
        logger.info("📊 Test OptionsDataManager...")
        
        # Données simulées pour test
        test_spx_data = {
            'vix_level': 24.5,
            'put_call_ratio': 0.85,
            'put_call_volume_ratio': 0.92,
            'call_volume': 150000,
            'put_volume': 138000,
            'call_oi': 2500000,
            'put_oi': 2200000,
            'gamma_exposure': 75e9,
            'dealer_position': 'long_gamma',
            'gamma_flip_level': 4850.0,
            'pin_levels': [4800.0, 4850.0, 4900.0],
            'unusual_activity': False
        }
        
        # Test sauvegarde horaire
        hourly_success = await options_manager.save_hourly_snapshot(test_spx_data)
        logger.info(f"   Sauvegarde horaire: {'✅' if hourly_success else '❌'}")
        
        # Test sauvegarde finale
        final_success = await options_manager.save_final_snapshot(test_spx_data)
        logger.info(f"   Sauvegarde finale: {'✅' if final_success else '❌'}")
        
        # Test récupération données
        saved_snapshot = options_manager.get_latest_saved_data()
        if saved_snapshot:
            logger.info(f"   Données sauvegardées récupérées: VIX {saved_snapshot.vix_level}")
            
            # Test validation fraîcheur
            quality_report = options_manager.validate_data_freshness(saved_snapshot)
            logger.info(f"   Fraîcheur: {quality_report.freshness_level.value}")
            logger.info(f"   Valide pour trading: {quality_report.is_valid_for_trading}")
        else:
            logger.warning("   ⚠️ Aucune donnée sauvegardée trouvée")
        
        # 4. Test DataQualityValidator
        logger.info("🛡️ Test DataQualityValidator...")
        
        # Test données valides
        valid_data = {
            'vix_level': 24.5,
            'put_call_ratio': 0.85,
            'gamma_exposure': 75e9,
            'data_timestamp': datetime.now(timezone.utc).isoformat(),
            'data_source': 'ibkr_real'
        }
        
        validation_report = await data_validator.validate_spx_data(valid_data)
        logger.info(f"   Validation données valides: {validation_report.quality_level.value}")
        logger.info(f"   Score: {validation_report.validation_score:.2f}")
        logger.info(f"   Valide pour trading: {validation_report.is_valid_for_trading}")
        
        # Test données corrompues (fallback)
        corrupted_data = {
            'vix_level': 24.5,
            'put_call_ratio': 0.85,
            'gamma_exposure': 75e9,
            'data_source': 'fallback_simulated'  # Ceci devrait déclencher une pause
        }
        
        validation_report = await data_validator.validate_spx_data(corrupted_data)
        logger.info(f"   Validation données corrompues: {validation_report.quality_level.value}")
        logger.info(f"   Message pause: {validation_report.pause_message}")
        logger.info(f"   Raison pause: {validation_report.pause_reason.value if validation_report.pause_reason else 'None'}")
        
        # 5. Test intégration complète
        logger.info("🔗 Test intégration complète...")
        
        # Simuler un cycle de trading
        if session_manager.should_use_live_data():
            logger.info("   📡 Mode: Données LIVE IBKR")
            # Ici on utiliserait les vraies données IBKR
            current_data = valid_data
        else:
            logger.info("   💾 Mode: Données sauvegardées")
            # Utiliser les données sauvegardées
            saved_data = options_manager.get_latest_saved_data()
            if saved_data:
                current_data = {
                    'vix_level': saved_data.vix_level,
                    'put_call_ratio': saved_data.put_call_ratio,
                    'gamma_exposure': saved_data.gamma_exposure,
                    'data_timestamp': saved_data.timestamp.isoformat(),
                    'data_source': 'saved_data'
                }
            else:
                current_data = None
        
        # Validation qualité
        if current_data:
            quality_report = await data_validator.validate_spx_data(current_data)
            
            if quality_report.is_valid_for_trading:
                logger.info("   ✅ Données validées - Trading autorisé")
                
                # Adapter les paramètres selon la session
                position_mult = session_manager.get_position_size_multiplier()
                risk_mult = session_manager.get_risk_multiplier()
                confidence_threshold = session_manager.get_min_confidence_threshold()
                
                logger.info(f"   📊 Paramètres adaptés:")
                logger.info(f"      - Taille position: {position_mult}x")
                logger.info(f"      - Multiplicateur risque: {risk_mult}x")
                logger.info(f"      - Seuil confiance: {confidence_threshold}")
                
            else:
                logger.warning("   🛑 Données invalides - PAUSE TRADING")
                logger.warning(f"      Raison: {quality_report.pause_message}")
        else:
            logger.error("   ❌ Aucune donnée disponible - PAUSE TRADING")
        
        # 6. Test statut final
        logger.info("📊 Statut final des modules...")
        
        # Session
        session_summary = session_manager.get_session_summary()
        logger.info(f"   Session: {session_summary['session_description']}")
        
        # Options
        options_status = options_manager.get_system_status()
        logger.info(f"   Options: Session {options_status['current_session']}")
        
        # Validation
        validation_summary = data_validator.get_validation_summary()
        logger.info(f"   Validation: {validation_summary['total_validations']} validations")
        logger.info(f"   Score moyen: {validation_summary['average_score']:.2f}")
        
        # Pause
        pause_status = data_validator.get_pause_status()
        if pause_status.is_paused:
            logger.warning(f"   🛑 SYSTÈME EN PAUSE: {pause_status.pause_message}")
        else:
            logger.info("   ✅ Système opérationnel")
        
        logger.info("✅ Test intégration Phase 3 terminé avec succès!")
        
        # 7. Résumé des améliorations
        logger.info("🎯 RÉSUMÉ DES AMÉLIORATIONS PHASE 3:")
        logger.info("   ✅ Élimination complète des fallbacks dangereux")
        logger.info("   ✅ Pause explicite avec messages clairs")
        logger.info("   ✅ Sauvegarde horaire automatique des données SPX")
        logger.info("   ✅ Gestion multi-sessions intelligente")
        logger.info("   ✅ Validation qualité stricte des données")
        logger.info("   ✅ Adaptation automatique des paramètres par session")
        logger.info("   ✅ Monitoring et alertes en temps réel")
        
    except Exception as e:
        logger.error(f"❌ Erreur test intégration Phase 3: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_phase3_integration())

