#!/usr/bin/env python3
"""
🧪 TEST DATA QUALITY VALIDATOR - MIA_IA_SYSTEM
==============================================

Test du DataQualityValidator avec système de pause explicite.

Author: MIA_IA_SYSTEM
Date: Janvier 2025
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.data_quality_validator import create_data_quality_validator
from core.logger import get_logger

logger = get_logger(__name__)

async def test_data_quality_validator():
    """Test complet du DataQualityValidator"""
    
    logger.info("🧪 Test DataQualityValidator...")
    
    try:
        validator = create_data_quality_validator()
        
        # Test 1: Données valides
        logger.info("📊 Test 1: Données valides...")
        valid_data = {
            'vix_level': 24.5,
            'put_call_ratio': 0.85,
            'gamma_exposure': 75e9,
            'data_timestamp': '2025-01-15T10:30:00Z',
            'data_source': 'ibkr_real'
        }
        
        report = await validator.validate_spx_data(valid_data)
        logger.info(f"   Qualité: {report.quality_level.value}")
        logger.info(f"   Valide pour trading: {report.is_valid_for_trading}")
        logger.info(f"   Score: {report.validation_score:.2f}")
        logger.info(f"   Âge: {report.data_age_hours:.1f}h")
        
        # Test 2: Données corrompues (fallback)
        logger.info("📊 Test 2: Données corrompues (fallback)...")
        corrupted_data = {
            'vix_level': 24.5,
            'put_call_ratio': 0.85,
            'gamma_exposure': 75e9,
            'data_source': 'fallback_simulated'
        }
        
        report = await validator.validate_spx_data(corrupted_data)
        logger.info(f"   Qualité: {report.quality_level.value}")
        logger.info(f"   Valide pour trading: {report.is_valid_for_trading}")
        logger.info(f"   Message pause: {report.pause_message}")
        logger.info(f"   Raison pause: {report.pause_reason.value if report.pause_reason else 'None'}")
        
        # Test 3: Données expirées
        logger.info("📊 Test 3: Données expirées...")
        expired_data = {
            'vix_level': 24.5,
            'put_call_ratio': 0.85,
            'gamma_exposure': 75e9,
            'data_timestamp': '2025-01-14T10:30:00Z',  # 24h plus tôt
            'data_source': 'ibkr_real'
        }
        
        report = await validator.validate_spx_data(expired_data)
        logger.info(f"   Qualité: {report.quality_level.value}")
        logger.info(f"   Valide pour trading: {report.is_valid_for_trading}")
        logger.info(f"   Message pause: {report.pause_message}")
        
        # Test 4: Données avec valeurs suspectes
        logger.info("📊 Test 4: Données avec valeurs suspectes...")
        suspicious_data = {
            'vix_level': 150,  # VIX trop élevé
            'put_call_ratio': 15,  # Ratio trop élevé
            'gamma_exposure': 75e9,
            'data_timestamp': '2025-01-15T10:30:00Z',
            'data_source': 'ibkr_real'
        }
        
        report = await validator.validate_spx_data(suspicious_data)
        logger.info(f"   Qualité: {report.quality_level.value}")
        logger.info(f"   Valide pour trading: {report.is_valid_for_trading}")
        logger.info(f"   Avertissements: {report.warnings}")
        
        # Test 5: Données manquantes
        logger.info("📊 Test 5: Données manquantes...")
        missing_data = {
            'vix_level': 24.5,
            # put_call_ratio manquant
            'gamma_exposure': 75e9,
            'data_source': 'ibkr_real'
        }
        
        report = await validator.validate_spx_data(missing_data)
        logger.info(f"   Qualité: {report.quality_level.value}")
        logger.info(f"   Valide pour trading: {report.is_valid_for_trading}")
        logger.info(f"   Erreurs: {report.errors}")
        
        # Test 6: Statut de pause
        logger.info("📊 Test 6: Statut de pause...")
        pause_status = validator.get_pause_status()
        logger.info(f"   En pause: {pause_status.is_paused}")
        if pause_status.is_paused:
            logger.info(f"   Raison: {pause_status.pause_reason.value}")
            logger.info(f"   Message: {pause_status.pause_message}")
        
        # Test 7: Résumé des validations
        logger.info("📊 Test 7: Résumé des validations...")
        summary = validator.get_validation_summary()
        logger.info(f"   Total validations: {summary['total_validations']}")
        logger.info(f"   Score moyen: {summary['average_score']:.2f}")
        logger.info(f"   Distribution qualité: {summary['quality_distribution']}")
        
        # Test 8: Vérification pause
        logger.info("📊 Test 8: Vérification pause...")
        is_paused = await validator.check_pause_status()
        logger.info(f"   Doit rester en pause: {is_paused}")
        
        logger.info("✅ Test DataQualityValidator terminé avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur test DataQualityValidator: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_data_quality_validator())
