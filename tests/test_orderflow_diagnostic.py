#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC ORDERFLOW - MIA_IA_SYSTEM
Script de diagnostic pour identifier les problèmes OrderFlow
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from features.orderflow_analyzer import OrderFlowAnalyzer, OrderFlowData

logger = get_logger(__name__)

async def test_orderflow_analyzer():
    """Test de l'analyseur OrderFlow avec différentes données"""
    logger.info("🔍 DIAGNOSTIC ORDERFLOW ANALYZER")
    logger.info("=" * 50)
    
    # Configuration de test
    class TestConfig:
        def get_orderflow_config(self):
            return {
                "lookback_periods": 100,
                "volume_threshold": 200,
                "delta_threshold": 50
            }
        
        def get_level2_config(self):
            return {
                "enable_level2": True,
                "depth_levels": 5
            }
    
    config = TestConfig()
    
    # Initialiser l'analyseur
    analyzer = OrderFlowAnalyzer(config)
    logger.info("✅ OrderFlow Analyzer initialisé")
    
    # Test 1: Données valides
    logger.info("\n🧪 TEST 1: Données valides")
    valid_market_data = {
        "timestamp": datetime.now(),
        "symbol": "ES",
        "price": 6456.75,
        "volume": 442,
        "delta": 298,
        "bid_volume": 265,
        "ask_volume": 177,
        "mode": "live_real",
        "level2": {
            "best_bid": 6456.50,
            "best_ask": 6457.00,
            "bid_depth": {},
            "ask_depth": {}
        },
        "footprint": {
            "buy_volume": 177,
            "sell_volume": 265,
            "footprint_score": 0.3,
            "patterns": []
        }
    }
    
    try:
        signal = await analyzer.analyze_orderflow_data(valid_market_data)
        if signal:
            logger.info("✅ Test 1 RÉUSSI - Signal généré")
            logger.info(f"  📊 Type: {signal.signal_type}")
            logger.info(f"  🎯 Confiance: {signal.confidence:.3f}")
        else:
            logger.warning("⚠️ Test 1 - Aucun signal généré")
    except Exception as e:
        logger.error(f"❌ Test 1 ÉCHOUÉ: {e}")
        import traceback
        logger.error(f"📊 Traceback: {traceback.format_exc()}")
    
    # Test 2: Données avec volume 0
    logger.info("\n🧪 TEST 2: Volume 0")
    zero_volume_data = {
        "timestamp": datetime.now(),
        "symbol": "ES",
        "price": 6456.75,
        "volume": 0,  # Volume 0
        "delta": 0,
        "bid_volume": 0,
        "ask_volume": 0,
        "mode": "live_real",
        "level2": {},
        "footprint": {}
    }
    
    try:
        signal = await analyzer.analyze_orderflow_data(zero_volume_data)
        if signal:
            logger.info("✅ Test 2 RÉUSSI - Signal généré malgré volume 0")
        else:
            logger.info("✅ Test 2 - Aucun signal (comportement attendu)")
    except Exception as e:
        logger.error(f"❌ Test 2 ÉCHOUÉ: {e}")
        import traceback
        logger.error(f"📊 Traceback: {traceback.format_exc()}")
    
    # Test 3: Données manquantes
    logger.info("\n🧪 TEST 3: Données manquantes")
    missing_data = {
        "timestamp": datetime.now(),
        "symbol": "ES",
        "price": 6456.75
        # Volume, delta, bid_volume, ask_volume manquants
    }
    
    try:
        signal = await analyzer.analyze_orderflow_data(missing_data)
        if signal:
            logger.info("✅ Test 3 RÉUSSI - Signal généré avec données manquantes")
        else:
            logger.info("✅ Test 3 - Aucun signal (comportement attendu)")
    except Exception as e:
        logger.error(f"❌ Test 3 ÉCHOUÉ: {e}")
        import traceback
        logger.error(f"📊 Traceback: {traceback.format_exc()}")
    
    # Test 4: Extraction directe OrderFlowData
    logger.info("\n🧪 TEST 4: Extraction OrderFlowData")
    try:
        orderflow_data = analyzer._extract_orderflow_data(valid_market_data)
        if orderflow_data:
            logger.info("✅ Test 4 RÉUSSI - OrderFlowData extrait")
            logger.info(f"  📊 Volume: {orderflow_data.volume}")
            logger.info(f"  📈 Delta: {orderflow_data.delta}")
            logger.info(f"  💰 Bid Volume: {orderflow_data.bid_volume}")
            logger.info(f"  💰 Ask Volume: {orderflow_data.ask_volume}")
        else:
            logger.error("❌ Test 4 ÉCHOUÉ - OrderFlowData non extrait")
    except Exception as e:
        logger.error(f"❌ Test 4 ÉCHOUÉ: {e}")
        import traceback
        logger.error(f"📊 Traceback: {traceback.format_exc()}")
    
    logger.info("\n🔍 DIAGNOSTIC TERMINÉ")

if __name__ == "__main__":
    asyncio.run(test_orderflow_analyzer())

