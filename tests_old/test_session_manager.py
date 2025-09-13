#!/usr/bin/env python3
"""
🧪 TEST SESSION MANAGER - MIA_IA_SYSTEM
=======================================

Test simple du SessionManager sans problème d'import.

Author: MIA_IA_SYSTEM
Date: Janvier 2025
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.session_manager import create_session_manager
from core.logger import get_logger

logger = get_logger(__name__)

async def test_session_manager():
    """Test du SessionManager"""
    logger.info("🧪 Test SessionManager...")
    
    try:
        manager = create_session_manager()
        
        # Test détection session actuelle
        current_session = manager.get_current_session()
        logger.info(f"Session actuelle: {current_session.value}")
        
        # Test configuration session
        config = manager.get_session_config(current_session)
        logger.info(f"Configuration: {config.description}")
        logger.info(f"Trading activé: {config.trading_enabled}")
        logger.info(f"Source données: {config.data_source.value}")
        
        # Test validation données
        is_valid, warnings = manager.validate_data_for_session(5.0)
        logger.info(f"Validation données 5h: Valide={is_valid}, Warnings={warnings}")
        
        # Test état session
        state = manager.get_session_state()
        logger.info(f"État session: {state.data_quality}")
        
        # Test résumé
        summary = manager.get_session_summary()
        logger.info(f"Résumé: {summary['session_description']}")
        
        # Test toutes les sessions
        logger.info("📊 Test toutes les sessions:")
        for session_type in manager.session_configs.keys():
            config = manager.get_session_config(session_type)
            logger.info(f"  - {session_type.value}: {config.description}")
            logger.info(f"    Trading: {config.trading_enabled}, Source: {config.data_source.value}")
            logger.info(f"    Position: {config.position_size_multiplier}x, Risque: {config.risk_multiplier}x")
        
        logger.info("✅ Test SessionManager terminé avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur test SessionManager: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_session_manager())

