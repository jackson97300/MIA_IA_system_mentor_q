#!/usr/bin/env python3
"""
🔍 TEST FEATURES ULTRA SIMPLE - MIA_IA_SYSTEM
Test ultra-simple pour identifier les erreurs exactes
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger

logger = get_logger(__name__)

def test_feature_calculator_ultra_simple():
    """Test ultra-simple du feature calculator"""
    logger.info("🔧 TEST 1: Feature Calculator Ultra Simple")
    
    try:
        # Test 1: Import
        from features.feature_calculator import CONFLUENCE_WEIGHTS, TRADING_THRESHOLDS
        logger.info("✅ Import réussi")
        
        # Test 2: Validation des poids
        total_weight = sum(CONFLUENCE_WEIGHTS.values())
        logger.info(f"✅ Poids total: {total_weight:.3f}")
        
        # Test 3: Validation des seuils
        logger.info(f"✅ Seuils: {TRADING_THRESHOLDS}")
        
        # Test 4: Création calculateur
        from features.feature_calculator import FeatureCalculator
        calculator = FeatureCalculator()
        logger.info("✅ FeatureCalculator créé")
        
        # Test 5: Création résultat
        from features.feature_calculator import FeatureCalculationResult
        import pandas as pd
        
        test_result = FeatureCalculationResult(
            timestamp=pd.Timestamp.now(),
            gamma_levels_proximity=0.8,
            volume_confirmation=0.7,
            vwap_trend_signal=0.6,
            sierra_pattern_strength=0.9,
            mtf_confluence_score=0.8,
            smart_money_strength=0.7,
            order_book_imbalance=0.5,
            options_flow_bias=0.6
        )
        logger.info("✅ FeatureCalculationResult créé")
        
        # Test 6: Calcul confluence
        confluence_score = calculator._calculate_confluence_score(test_result)
        logger.info(f"✅ Score confluence: {confluence_score:.3f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 1: Feature Calculator - ERREUR: {e}")
        traceback.print_exc()
        return False

def test_order_book_imbalance_ultra_simple():
    """Test ultra-simple du order book imbalance"""
    logger.info("🔧 TEST 2: Order Book Imbalance Ultra Simple")
    
    try:
        # Test 1: Import
        from features.order_book_imbalance import OrderBookLevel, OrderBookSnapshot
        logger.info("✅ Import réussi")
        
        # Test 2: Création données
        import pandas as pd
        
        bids = [
            OrderBookLevel(price=4500.0, size=100),
            OrderBookLevel(price=4499.75, size=150),
            OrderBookLevel(price=4499.5, size=200)
        ]
        logger.info("✅ Bids créés")
        
        asks = [
            OrderBookLevel(price=4500.25, size=120),
            OrderBookLevel(price=4500.5, size=180),
            OrderBookLevel(price=4500.75, size=250)
        ]
        logger.info("✅ Asks créés")
        
        # Test 3: Création snapshot
        order_book = OrderBookSnapshot(
            timestamp=pd.Timestamp.now(),
            bids=bids,
            asks=asks
        )
        logger.info("✅ OrderBookSnapshot créé")
        
        # Test 4: Calcul imbalance
        from features.order_book_imbalance import calculate_order_book_imbalance_feature
        imbalance = calculate_order_book_imbalance_feature(order_book)
        logger.info(f"✅ Imbalance: {imbalance:.3f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 2: Order Book Imbalance - ERREUR: {e}")
        traceback.print_exc()
        return False

def run_ultra_simple_tests():
    """Exécute les tests ultra-simples"""
    logger.info("🚀 DÉMARRAGE TEST FEATURES ULTRA SIMPLE")
    
    tests = [
        test_feature_calculator_ultra_simple,
        test_order_book_imbalance_ultra_simple
    ]
    
    results = {}
    for test in tests:
        results[test.__name__] = test()
    
    # Résultats
    logger.info("\n" + "="*60)
    logger.info("📊 RÉSULTATS TEST FEATURES ULTRA SIMPLE")
    logger.info("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n📈 RÉSULTAT: {passed_tests}/{total_tests} tests réussis")

def main():
    """Fonction principale"""
    run_ultra_simple_tests()

if __name__ == "__main__":
    main() 