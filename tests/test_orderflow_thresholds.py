#!/usr/bin/env python3
"""
🧪 TEST SEUILS ORDERFLOW OPTIMISÉS
Vérifie que les seuils sont bien réduits pour la stratégie leadership
"""

import sys
import asyncio
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from automation_modules.orderflow_analyzer import OrderFlowAnalyzer, OrderFlowData
from automation_modules.config_manager import AutomationConfig
from core.logger import get_logger

logger = get_logger(__name__)

async def test_orderflow_thresholds():
    """Test des seuils OrderFlow optimisés"""
    
    logger.info("🧪 TEST SEUILS ORDERFLOW OPTIMISÉS")
    logger.info("=" * 50)
    
    # Configuration
    config = AutomationConfig()
    
    # Créer l'analyzer
    analyzer = OrderFlowAnalyzer(config)
    
    # Test avec données faibles (qui seraient rejetées avant)
    test_data = OrderFlowData(
        timestamp=asyncio.get_event_loop().time(),
        symbol="ES",
        price=6450.0,
        volume=60,  # Volume faible
        delta=5.0,  # Delta faible
        bid_volume=30,
        ask_volume=30,
        level2_data={},
        footprint_data={},
        mode="test"
    )
    
    logger.info(f"📊 Données de test:")
    logger.info(f"   Volume: {test_data.volume}")
    logger.info(f"   Delta: {test_data.delta}")
    logger.info(f"   Bid/Ask: {test_data.bid_volume}/{test_data.ask_volume}")
    
    # Analyser
    try:
        signal = await analyzer.analyze_orderflow_data({
            'price': test_data.price,
            'volume': test_data.volume,
            'delta': test_data.delta,
            'bid_volume': test_data.bid_volume,
            'ask_volume': test_data.ask_volume,
            'mode': 'test'
        })
        
        if signal:
            logger.info("✅ SIGNAL GÉNÉRÉ AVEC SUCCÈS!")
            logger.info(f"   Type: {signal.signal_type}")
            logger.info(f"   Confiance: {signal.confidence:.3f}")
            logger.info(f"   Raison: {signal.reasoning}")
        else:
            logger.info("❌ AUCUN SIGNAL GÉNÉRÉ")
            
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")
    
    logger.info("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_orderflow_thresholds())

