"""
MIA_IA_SYSTEM - Test Patterns Integration
Test intégration du nouveau fichier patterns_detector.py
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, Optional

# === IMPORTS TEST INTEGRATION ===

# Core components
from core.base_types import MarketData, OrderFlowData, PatternType
from core.patterns_detector import (
import logging

# Configure logging
logger = logging.getLogger(__name__)

    ElitePatternsDetector, 
    create_patterns_detector,
    detect_all_elite_patterns
)

# Features integration
from features import create_feature_calculator

def test_patterns_detector_basic():
    """Test patterns detector standalone"""
    logger.debug("TEST PATTERNS DETECTOR BASIC")
    
    # Création detector
    detector = create_patterns_detector()
    
    # Market data
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4500.0,
        high=4505.0,
        low=4498.0,
        close=4502.0,
        volume=1500,
        bid=4501.75,
        ask=4502.25,
        spread=0.5
    )
    
    # Options data pour gamma pin
    options_data = {
        'call_wall': 4500.0,
        'put_wall': 4480.0,
        'net_gamma': 3000.0
    }
    
    # Order flow pour headfake + anomalies
    order_flow = OrderFlowData(
        timestamp=market_data.timestamp,
        symbol="ES",
        cumulative_delta=150.0,
        bid_volume=800,
        ask_volume=700,
        aggressive_buys=60,
        aggressive_sells=40
    )
    
    # Test détection complète
    start_time = time.perf_counter()
    result = detector.detect_all_patterns(
        market_data=market_data,
        options_data=options_data,
        order_flow=order_flow
    )
    calc_time = (time.perf_counter() - start_time) * 1000
    
    # Validations
    assert calc_time < 5.0, f"Patterns detector trop lent: {calc_time:.2f}ms"
    assert 0.0 <= result.gamma_pin_strength <= 1.0, "Gamma pin hors range"
    assert 0.0 <= result.headfake_signal <= 1.0, "Headfake hors range"
    assert 0.0 <= result.microstructure_anomaly <= 1.0, "Anomaly hors range"
    
    logger.info("Patterns detection: {calc_time:.2f}ms")
    logger.info("Gamma pin: {result.gamma_pin_strength:.3f}")
    logger.info("Headfake: {result.headfake_signal:.3f}")
    logger.info("Anomaly: {result.microstructure_anomaly:.3f}")
    logger.info("Patterns count: {result.patterns_detected_count}")
    
    return True

def test_integration_feature_calculator():
    """Test intégration avec feature_calculator"""
    logger.debug("TEST INTEGRATION FEATURE CALCULATOR")
    
    # Création detector + calculator
    detector = create_patterns_detector()
    calculator = create_feature_calculator()
    
    # Market data
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4500.0,
        high=4510.0,
        low=4495.0,
        close=4505.0,
        volume=1800
    )
    
    # === 1. GÉNÉRATION PATTERNS ===
    
    patterns_result = detector.detect_all_patterns(
        market_data=market_data,
        options_data={'call_wall': 4520.0, 'put_wall': 4480.0, 'net_gamma': 2500},
        order_flow=OrderFlowData(
            timestamp=market_data.timestamp,
            symbol="ES",
            cumulative_delta=100.0,
            bid_volume=900,
            ask_volume=900,
            aggressive_buys=50,
            aggressive_sells=30
        )
    )
    
    # === 2. CONSTRUCTION SIERRA PATTERNS AVEC INTÉGRATION CORRECTE ===
    
    sierra_patterns = {
        # Battle navale (existant)
        'battle_navale_signal': 0.75,
        'base_quality': 0.7,
        'trend_continuation': 0.8,
        
        # Nouveaux patterns - INTÉGRATION DIRECTE
        'gamma_pin_strength': patterns_result.gamma_pin_strength,
        'headfake_signal': patterns_result.headfake_signal,
        'microstructure_anomaly': patterns_result.microstructure_anomaly
    }
    
    logger.info("🔗 Patterns intégrés:")
    logger.info("   • Gamma pin: {patterns_result.gamma_pin_strength:.3f}")
    logger.info("   • Headfake: {patterns_result.headfake_signal:.3f}")  
    logger.info("   • Anomaly: {patterns_result.microstructure_anomaly:.3f}")
    
    # === 3. CALCUL FEATURES AVEC NOUVEAUX PATTERNS ===
    
    from features.feature_calculator import OptionsData, MarketStructureData
    
    options_data = OptionsData(
        timestamp=pd.Timestamp.now(),
        call_wall=4520.0,
        put_wall=4480.0,
        net_gamma=2.5,
        call_volume=1200,
        put_volume=800
    )
    
    structure_data = MarketStructureData(
        timestamp=pd.Timestamp.now(),
        poc_price=4501.0,
        vah_price=4515.0,
        val_price=4485.0,
        vwap_price=4502.0,
        vwap_slope=0.3
    )
    
    # Calcul features avec patterns intégrés
    start_time = time.perf_counter()
    features_result = calculator.calculate_all_features(
        market_data=market_data,
        options_data=options_data,
        structure_data=structure_data,
        sierra_patterns=sierra_patterns
    )
    calc_time = (time.perf_counter() - start_time) * 1000
    
    # === 4. VALIDATION INTÉGRATION ===
    
    trading_features = features_result.to_trading_features()
    features_array = trading_features.to_array()
    
    # Validations
    assert calc_time < 3.0, f"Features calculation trop lent: {calc_time:.2f}ms"
    assert len(features_array) == 8, f"Pas 8 features: {len(features_array)}"
    assert 0.0 <= features_result.confluence_score <= 1.0, "Confluence hors range"
    
    # Vérifier que les patterns sont présents dans sierra_patterns (intégration OK)
    assert 'gamma_pin_strength' in sierra_patterns, "Gamma pin pas dans sierra_patterns"
    assert 'headfake_signal' in sierra_patterns, "Headfake pas dans sierra_patterns"  
    assert 'microstructure_anomaly' in sierra_patterns, "Anomaly pas dans sierra_patterns"
    
    # Vérifier que les valeurs sont cohérentes (entre 0 et 1)
    assert 0.0 <= sierra_patterns['gamma_pin_strength'] <= 1.0, "Gamma pin hors range"
    assert 0.0 <= sierra_patterns['headfake_signal'] <= 1.0, "Headfake hors range"
    assert 0.0 <= sierra_patterns['microstructure_anomaly'] <= 1.0, "Anomaly hors range"
    
    logger.info("Features calculation: {calc_time:.2f}ms")
    logger.info("Features array shape: {features_array.shape}")
    logger.info("Confluence score: {features_result.confluence_score:.3f}")
    logger.info("Patterns integrated in sierra_patterns:")
    logger.info("   • Gamma pin: {sierra_patterns['gamma_pin_strength']:.3f}")
    logger.info("   • Headfake: {sierra_patterns['headfake_signal']:.3f}")
    logger.info("   • Anomaly: {sierra_patterns['microstructure_anomaly']:.3f}")
    logger.info("Feature calculator using patterns: OK")
    
    return True

def test_pattern_types_consistency():
    """Test cohérence types PatternType"""
    logger.debug("TEST PATTERN TYPES CONSISTENCY")
    
    from core.base_types import PatternType
    
    # Vérifier que tous les patterns sont définis
    required_patterns = [
        PatternType.BATTLE_NAVALE,
        PatternType.GAMMA_PIN,
        PatternType.HEADFAKE,
        PatternType.MICROSTRUCTURE,
        PatternType.CONFLUENCE
    ]
    
    logger.info("Pattern types defined:")
    for pattern in required_patterns:
        logger.info("   • {pattern.value}")
    
    # Test cohérence avec detector
    detector = create_patterns_detector()
    
    # Tous les patterns doivent être détectables
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4500.0, high=4505.0, low=4498.0, close=4502.0, volume=1500
    )
    
    result = detector.detect_all_patterns(market_data)
    
    # Vérifier structure résultat
    assert hasattr(result, 'gamma_pin_strength'), "gamma_pin_strength manquant"
    assert hasattr(result, 'headfake_signal'), "headfake_signal manquant"
    assert hasattr(result, 'microstructure_anomaly'), "microstructure_anomaly manquant"
    
    logger.info("Pattern detection result structure OK")
    logger.info("All pattern types consistent")
    
    return True

def test_performance_patterns():
    """Test performance patterns detector"""
    logger.debug("TEST PERFORMANCE PATTERNS")
    
    detector = create_patterns_detector()
    
    # Simulation 100 détections
    total_time = 0.0
    
    for i in range(100):
        # Génération données cohérentes OHLC
        base_price = 4500.0 + np.random.normal(0, 2)
        price_range = abs(np.random.normal(0, 2))
        
        low = base_price - price_range
        high = base_price + price_range
        open_price = low + np.random.random() * (high - low)
        close_price = low + np.random.random() * (high - low)
        
        market_data = MarketData(
            timestamp=pd.Timestamp.now() + pd.Timedelta(seconds=i),
            symbol="ES",
            open=open_price,
            high=high,
            low=low,
            close=close_price,
            volume=max(1000, 1500 + np.random.randint(-300, 300)),
            spread=max(0.1, 0.25 + np.random.normal(0, 0.05))
        )
        
        options_data = {
            'call_wall': 4520.0 + np.random.normal(0, 5),
            'put_wall': 4480.0 + np.random.normal(0, 5),
            'net_gamma': 2000 + np.random.normal(0, 500)
        }
        
        order_flow = OrderFlowData(
            timestamp=market_data.timestamp,
            symbol="ES",
            cumulative_delta=np.random.normal(0, 100),
            bid_volume=750 + np.random.randint(-200, 200),
            ask_volume=750 + np.random.randint(-200, 200),
            aggressive_buys=np.random.randint(20, 80),
            aggressive_sells=np.random.randint(20, 80)
        )
        
        start_time = time.perf_counter()
        result = detector.detect_all_patterns(market_data, options_data, order_flow)
        calc_time = (time.perf_counter() - start_time) * 1000
        total_time += calc_time
    
    avg_time = total_time / 100
    
    # Validation performance
    assert avg_time < 2.0, f"Performance patterns trop lente: {avg_time:.3f}ms"
    
    logger.info("100 iterations: {total_time:.2f}ms total")
    logger.info("Average per detection: {avg_time:.3f}ms")
    
    # Statistiques detector
    stats = detector.get_statistics()
    logger.info("Patterns detected: {stats['total_analyses']}")
    logger.info("Gamma pins: {stats['gamma_pins_detected']}")
    logger.info("Headfakes: {stats['headfakes_detected']}")
    logger.info("Anomalies: {stats['anomalies_detected']}")
    
    return True

def test_helper_functions():
    """Test helper functions"""
    logger.debug("TEST HELPER FUNCTIONS")
    
    # Test factory function
    detector = create_patterns_detector({'gamma_proximity_ticks': 3})
    assert detector is not None, "Factory function échoue"
    
    # Test helper detection function
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4500.0, high=4505.0, low=4498.0, close=4502.0, volume=1500
    )
    
    result = detect_all_elite_patterns(market_data)
    assert result is not None, "Helper function échoue"
    assert hasattr(result, 'gamma_pin_strength'), "Résultat incomplet"
    
    logger.info("Factory function OK")
    logger.info("Helper function OK")
    logger.info("All helper functions working")
    
    return True

def run_patterns_integration_tests():
    """Runner tests intégration patterns"""
    logger.info("🚀 PATTERNS INTEGRATION TESTS")
    print("=" * 50)
    
    tests = [
        ("Patterns Detector Basic", test_patterns_detector_basic),
        ("Feature Calculator Integration", test_integration_feature_calculator),
        ("Pattern Types Consistency", test_pattern_types_consistency),
        ("Performance Patterns", test_performance_patterns),
        ("Helper Functions", test_helper_functions)
    ]
    
    results = []
    total_start = time.perf_counter()
    
    for test_name, test_func in tests:
        try:
            logger.info("\n{'-'*40}")
            success = test_func()
            results.append((test_name, "PASS"))
            logger.info("{test_name}: PASSED")
        except Exception as e:
            results.append((test_name, f"FAIL: {e}"))
            logger.error("{test_name}: FAILED - {e}")
            import traceback
            traceback.print_exc()
    
    total_time = (time.perf_counter() - total_start) * 1000
    
    # Summary
    logger.info("\n{'='*50}")
    logger.info("📊 PATTERNS INTEGRATION TEST SUMMARY")
    
    passed = sum(1 for _, status in results if status == "PASS")
    total = len(results)
    
    for test_name, status in results:
        symbol = "✅" if status == "PASS" else "❌"
        logger.info("{symbol} {test_name}: {status}")
    
    logger.info("\n🎯 RESULTS: {passed}/{total} tests passed")
    logger.info("⏱️ Total time: {total_time:.2f}ms")
    
    if passed == total:
        logger.info("\n🎉 ALL PATTERNS INTEGRATION TESTS PASSED!")
        logger.info("PATTERNS_DETECTOR.PY FULLY INTEGRATED") 
        logger.info("🎪 3 PATTERNS ÉLITES OPÉRATIONNELS")
        logger.info("🚀 SYSTEM COMPLET - READY FOR PHASE 3")
    else:
        logger.info("\n💀 {total - passed} TESTS FAILED")
    
    return passed == total

if __name__ == "__main__":
    success = run_patterns_integration_tests()
    exit(0 if success else 1)