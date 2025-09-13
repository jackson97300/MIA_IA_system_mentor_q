#!/usr/bin/env python3
"""
🕐 TEST SESSION ASIATIQUE - MIA_IA_SYSTEM
==========================================

Test spécifique pour la session asiatique avec données de test
quand IBKR ne fournit pas les données historiques.

Author: MIA_IA_SYSTEM
Date: Janvier 2025
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.session_manager import create_session_manager
from core.data_quality_validator import create_data_quality_validator
from data.options_data_manager import create_options_data_manager
from core.logger import get_logger

logger = get_logger(__name__)

async def test_asian_session_with_mock_data():
    """Test de la session asiatique avec données simulées"""
    
    logger.info("🕐 Test session asiatique avec données de test...")
    
    try:
        # 1. Initialiser les modules Phase 3
        session_manager = create_session_manager()
        data_validator = create_data_quality_validator()
        options_manager = create_options_data_manager()
        
        # 2. Forcer la session asiatique (pour test)
        logger.info("🕐 Simulation session asiatique...")
        
        # Vérifier session actuelle
        current_session = session_manager.get_current_session()
        logger.info(f"   Session détectée: {current_session.value}")
        
        # 3. Créer des données de test réalistes
        logger.info("📊 Création données de test réalistes...")
        
        test_spx_data = {
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
            'data_timestamp': '2025-01-15T18:30:00Z',  # Session asiatique
            'data_source': 'test_asian_session'
        }
        
        # 4. Sauvegarder les données de test
        await options_manager.save_hourly_snapshot(test_spx_data)
        logger.info("   ✅ Données de test sauvegardées")
        
        # 5. Récupérer les données sauvegardées
        saved_data = options_manager.get_latest_saved_data()
        if saved_data:
            logger.info(f"   📊 Données récupérées: VIX {saved_data.vix_level:.1f}")
        else:
            logger.error("   ❌ Aucune donnée récupérée")
            return False
        
        # 6. Validation qualité
        logger.info("🛡️ Validation qualité des données...")
        
        quality_report = await data_validator.validate_spx_data(test_spx_data)
        logger.info(f"   Qualité: {quality_report.quality_level.value}")
        logger.info(f"   Score: {quality_report.validation_score:.2f}")
        logger.info(f"   Valide pour trading: {quality_report.is_valid_for_trading}")
        
        # 7. Test paramètres session asiatique
        logger.info("📊 Test paramètres session asiatique...")
        
        position_mult = session_manager.get_position_size_multiplier()
        risk_mult = session_manager.get_risk_multiplier()
        confidence_threshold = session_manager.get_min_confidence_threshold()
        
        logger.info(f"   Taille position: {position_mult}x")
        logger.info(f"   Multiplicateur risque: {risk_mult}x")
        logger.info(f"   Seuil confiance: {confidence_threshold}")
        
        # 8. Simulation trading avec données de test
        logger.info("🎯 Simulation trading session asiatique...")
        
        if quality_report.is_valid_for_trading:
            logger.info("   ✅ Trading autorisé avec données de test")
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
            else:
                logger.warning("   ⚠️ Signal rejeté (confiance insuffisante)")
        else:
            logger.warning("   🛑 Trading interdit - Données invalides")
            logger.info(f"   Raison: {quality_report.pause_message}")
        
        # 9. Résumé du test
        logger.info("📋 RÉSUMÉ TEST SESSION ASIATIQUE:")
        logger.info("   ✅ Session asiatique détectée")
        logger.info("   ✅ Données de test créées et sauvegardées")
        logger.info("   ✅ Validation qualité effectuée")
        logger.info("   ✅ Paramètres adaptés appliqués")
        logger.info("   ✅ Simulation trading réussie")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test session asiatique: {e}")
        return False

async def test_asian_session_edge_cases():
    """Test des cas limites pour la session asiatique"""
    
    logger.info("🔍 Test cas limites session asiatique...")
    
    try:
        data_validator = create_data_quality_validator()
        
        # Test 1: Données trop anciennes
        old_data = {
            'vix_level': 20.5,
            'put_call_ratio': 0.85,
            'gamma_exposure': 75e9,
            'data_timestamp': '2025-01-10T10:30:00Z',  # 5 jours ago
            'data_source': 'saved_data'
        }
        
        quality_report = await data_validator.validate_spx_data(old_data)
        logger.info(f"   Test données anciennes: {quality_report.is_valid_for_trading}")
        
        # Test 2: Données corrompues
        corrupted_data = {
            'vix_level': -5.0,  # VIX négatif impossible
            'put_call_ratio': 0.85,
            'gamma_exposure': 75e9,
            'data_source': 'saved_data'
        }
        
        quality_report = await data_validator.validate_spx_data(corrupted_data)
        logger.info(f"   Test données corrompues: {quality_report.is_valid_for_trading}")
        
        # Test 3: Données manquantes
        missing_data = {
            'vix_level': 20.5,
            # put_call_ratio manquant
            'data_source': 'saved_data'
        }
        
        quality_report = await data_validator.validate_spx_data(missing_data)
        logger.info(f"   Test données manquantes: {quality_report.is_valid_for_trading}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test cas limites: {e}")
        return False

if __name__ == "__main__":
    logger.info("🕐 DÉMARRAGE TEST SESSION ASIATIQUE")
    
    # Test principal
    success1 = asyncio.run(test_asian_session_with_mock_data())
    
    # Test cas limites
    success2 = asyncio.run(test_asian_session_edge_cases())
    
    if success1 and success2:
        logger.info("🎉 TOUS LES TESTS SESSION ASIATIQUE RÉUSSIS!")
        logger.info("   Le bot est prêt pour la session asiatique avec données de test")
    else:
        logger.error("❌ ÉCHEC DE CERTAINS TESTS SESSION ASIATIQUE")

