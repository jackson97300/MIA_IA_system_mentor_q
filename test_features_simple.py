#!/usr/bin/env python3
"""
🔍 TEST FEATURES SIMPLE - MIA_IA_SYSTEM
Test simple pour identifier les problèmes dans les calculs
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger

logger = get_logger(__name__)

def test_feature_calculator_basic():
    """Test basique du feature calculator"""
    logger.info("🔧 TEST 1: Feature Calculator Basic")
    
    try:
        from features.feature_calculator import CONFLUENCE_WEIGHTS, TRADING_THRESHOLDS
        
        # Test poids
        total_weight = sum(CONFLUENCE_WEIGHTS.values())
        logger.info(f"✅ Poids total: {total_weight:.3f}")
        
        # Test seuils
        logger.info(f"✅ Seuils: {TRADING_THRESHOLDS}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 1: Feature Calculator - ERREUR: {e}")
        traceback.print_exc()
        return False

def test_smart_money_basic():
    """Test basique du smart money"""
    logger.info("🔧 TEST 2: Smart Money Basic")
    
    try:
        from features.smart_money_tracker import SmartMoneyTracker
        
        tracker = SmartMoneyTracker()
        logger.info("✅ SmartMoneyTracker créé")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 2: Smart Money - ERREUR: {e}")
        traceback.print_exc()
        return False

def test_delta_divergence_basic():
    """Test basique du delta divergence"""
    logger.info("🔧 TEST 3: Delta Divergence Basic")
    
    try:
        from features.advanced.delta_divergence import DeltaDivergenceDetector
        
        detector = DeltaDivergenceDetector()
        logger.info("✅ DeltaDivergenceDetector créé")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 3: Delta Divergence - ERREUR: {e}")
        traceback.print_exc()
        return False

def test_volatility_regime_basic():
    """Test basique du volatility regime"""
    logger.info("🔧 TEST 4: Volatility Regime Basic")
    
    try:
        from features.advanced.volatility_regime import VolatilityRegimeCalculator
        
        calculator = VolatilityRegimeCalculator()
        logger.info("✅ VolatilityRegimeCalculator créé")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 4: Volatility Regime - ERREUR: {e}")
        traceback.print_exc()
        return False

def test_order_book_imbalance_basic():
    """Test basique du order book imbalance"""
    logger.info("🔧 TEST 5: Order Book Imbalance Basic")
    
    try:
        from features.order_book_imbalance import OrderBookSnapshot
        
        logger.info("✅ OrderBookSnapshot importé")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 5: Order Book Imbalance - ERREUR: {e}")
        traceback.print_exc()
        return False

def test_mtf_confluence_basic():
    """Test basique du mtf confluence"""
    logger.info("🔧 TEST 6: MTF Confluence Basic")
    
    try:
        from features.mtf_confluence_elite import EliteMTFConfluence
        
        analyzer = EliteMTFConfluence()
        logger.info("✅ EliteMTFConfluence créé")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 6: MTF Confluence - ERREUR: {e}")
        traceback.print_exc()
        return False

def run_simple_tests():
    """Exécute les tests simples"""
    logger.info("🚀 DÉMARRAGE TEST FEATURES SIMPLE")
    
    tests = [
        test_feature_calculator_basic,
        test_smart_money_basic,
        test_delta_divergence_basic,
        test_volatility_regime_basic,
        test_order_book_imbalance_basic,
        test_mtf_confluence_basic
    ]
    
    results = {}
    for test in tests:
        results[test.__name__] = test()
    
    # Résultats
    logger.info("\n" + "="*60)
    logger.info("📊 RÉSULTATS TEST FEATURES SIMPLE")
    logger.info("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n📈 RÉSULTAT: {passed_tests}/{total_tests} tests réussis")
    
    if passed_tests == total_tests:
        logger.info("🎉 TOUS LES IMPORTS FEATURES FONCTIONNENT")
    else:
        logger.info("⚠️ CERTAINS IMPORTS ONT ÉCHOUÉ")

def main():
    """Fonction principale"""
    run_simple_tests()

if __name__ == "__main__":
    main() 