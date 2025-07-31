"""
MIA_IA_SYSTEM - Test Phase 2 Integration Complete
Test validation intégration complète business logic
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, Optional

# === IMPORTS PHASE 2 COMPOSANTS ===

# Core components
from core.base_types import MarketData, OrderFlowData
from core.battle_navale import create_battle_navale_analyzer

# Features package  
from features import (
import logging

# Configure logging
logger = logging.getLogger(__name__)

    create_feature_calculator,
    OptionsData, MarketStructureData, ESNQData,
    create_market_regime_detector, MarketRegimeDetector
)

# Strategies package
from strategies import (
    create_strategy_selector,
    TradingContext, ExecutionMode,
    create_trend_strategy, create_range_strategy
)

def test_battle_navale():
    """Test méthode signature Battle Navale - CORRIGÉ FINAL"""
    logger.debug("TEST BATTLE NAVALE")
    
    # Création analyzer
    analyzer = create_battle_navale_analyzer()
    
    # Market data test
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4500.0,
        high=4510.0, 
        low=4495.0,
        close=4505.0,
        volume=2000
    )
    
    # ✅ CORRECTION FINALE: OrderFlowData avec TOUS les arguments requis
    order_flow = OrderFlowData(
        timestamp=market_data.timestamp,
        symbol="ES",                    # ✅ REQUIS
        cumulative_delta=150.0,         # ✅ REQUIS
        bid_volume=800,                 # ✅ REQUIS
        ask_volume=1200,                # ✅ REQUIS
        aggressive_buys=60,             # ✅ REQUIS
        aggressive_sells=40,            # ✅ REQUIS
        # net_delta=150.0               # ✅ Optionnel - sera calculé automatiquement
    )
    
    # Test analyse
    start_time = time.perf_counter()
    result = analyzer.analyze_battle_navale(market_data, order_flow)
    calc_time = (time.perf_counter() - start_time) * 1000
    
    # Validations
    assert calc_time < 2.0, f"Battle navale trop lent: {calc_time:.2f}ms"
    assert hasattr(result, 'battle_navale_signal'), "Signal manquant"
    assert 0.0 <= result.battle_navale_signal <= 1.0, "Signal hors range"
    
    logger.info("Battle navale: {calc_time:.2f}ms")
    logger.info("Signal: {result.battle_navale_signal:.2f}")
    logger.info("Patterns détectés: {result.patterns_detected_count}")
    
    return True

def test_market_regime_detector():
    """Test détection régime marché"""
    logger.debug("TEST MARKET REGIME DETECTOR")
    
    # Création détecteur
    detector = create_market_regime_detector()
    
    # Simulation trend haussier pour historique
    for i in range(40):
        trend_price = 4480.0 + (i * 0.6)  # Trend up clair
        
        market_data = MarketData(
            timestamp=pd.Timestamp.now() - pd.Timedelta(minutes=40-i),
            symbol="ES",
            open=trend_price - 0.5,
            high=trend_price + 1.5,
            low=trend_price - 1.0,
            close=trend_price,
            volume=1500
        )
        
        # Alimentation historique
        detector.price_history.append(market_data)
    
    # Current market data pour analyse
    current_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4504.0,
        high=4510.0,
        low=4502.0,
        close=4508.0,
        volume=2000
    )
    
    # Structure data
    structure_data = {
        'vwap_slope': 0.7,  # Trend fort
        'vwap_price': 4505.0,
        'poc_price': 4507.0
    }
    
    # ES/NQ data
    es_nq_data = {
        'es_price': 4508.0,
        'nq_price': 4508.0 * 4.5,
        'correlation': 0.85
    }
    
    # Test analyse régime
    start_time = time.perf_counter()
    regime_data = detector.analyze_market_regime(
        market_data=current_data,
        structure_data=structure_data,
        es_nq_data=es_nq_data
    )
    analysis_time = (time.perf_counter() - start_time) * 1000
    
    # Validations
    assert analysis_time < 3.0, f"Regime detection trop lent: {analysis_time:.2f}ms"
    assert regime_data.regime_confidence > 0.0, "Confidence nulle"
    assert regime_data.regime is not None, "Aucun régime détecté"
    
    logger.info("Regime analysis: {analysis_time:.2f}ms")
    logger.info("Regime detected: {regime_data.regime.value}")
    logger.info("Confidence: {regime_data.regime_confidence:.2f}")
    logger.info("Preferred strategy: {regime_data.preferred_strategy}")
    logger.info("Allowed directions: {regime_data.allowed_directions}")
    logger.info("Position multiplier: {regime_data.position_sizing_multiplier:.2f}")
    
    # Test range detection
    logger.info("📊 Test Range Detection:")
    
    # Simulation range 4500-4515
    for i in range(20):
        if i % 4 == 0:  # Support test
            range_price = 4500.0 + np.random.normal(0, 0.5)
        elif i % 4 == 2:  # Resistance test
            range_price = 4515.0 + np.random.normal(0, 0.5)
        else:  # Dans le range
            range_price = 4507.5 + np.random.normal(0, 3)
        
        range_data = MarketData(
            timestamp=pd.Timestamp.now() + pd.Timedelta(minutes=i),
            symbol="ES", open=range_price, high=range_price+1,
            low=range_price-1, close=range_price, volume=1200
        )
        
        detector.price_history.append(range_data)
    
    # Test régime après range formation
    range_regime = detector.analyze_market_regime(market_data=range_data)
    logger.info("Range regime: {range_regime.regime.value}")
    
    if range_regime.range_analysis and range_regime.range_analysis.range_detected:
        range_info = range_regime.range_analysis
        logger.info("Range detected: {range_info.support_level:.1f}-{range_info.resistance_level:.1f}")
        logger.info("Range size: {range_info.range_size_ticks:.1f} ticks")
    
    return True

def test_feature_calculator():
    """Test calcul 8 features + confluence"""
    logger.debug("TEST FEATURE CALCULATOR")
    
    calculator = create_feature_calculator()
    
    # Data complet
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES", open=4500.0, high=4510.0, low=4495.0, close=4505.0, volume=1800
    )
    
    options_data = OptionsData(
        timestamp=pd.Timestamp.now(),
        call_wall=4520.0, put_wall=4480.0, net_gamma=2.5,
        call_volume=1200, put_volume=800
    )
    
    structure_data = MarketStructureData(
        timestamp=pd.Timestamp.now(),
        poc_price=4501.0, vah_price=4515.0, val_price=4485.0,
        vwap_price=4502.0, vwap_slope=0.3
    )
    
    sierra_patterns = {
        'battle_navale_signal': 0.8,
        'base_quality': 0.7,
        'trend_continuation': 0.9,
        'battle_strength': 0.75
    }
    
    # Test calcul
    start_time = time.perf_counter()
    result = calculator.calculate_all_features(
        market_data=market_data,
        options_data=options_data,
        structure_data=structure_data,
        sierra_patterns=sierra_patterns
    )
    calc_time = (time.perf_counter() - start_time) * 1000
    
    # Validations
    assert calc_time < 2.0, f"Features trop lent: {calc_time:.2f}ms"
    assert 0.0 <= result.confluence_score <= 1.0, "Confluence hors range"
    
    # Vérifier 8 features
    features_array = result.to_trading_features().to_array()
    assert len(features_array) == 8, f"Pas 8 features: {len(features_array)}"
    
    logger.info("Features: {calc_time:.2f}ms")
    logger.info("Confluence: {result.confluence_score:.3f}")
    logger.info("Signal quality: {result.signal_quality.value}")
    
    return True

def test_strategies():
    """Test strategies trend + range"""
    logger.debug("TEST STRATEGIES")
    
    # Création strategies
    trend_strategy = create_trend_strategy()
    range_strategy = create_range_strategy()
    
    # Market data
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES", open=4500.0, high=4510.0, low=4495.0, close=4505.0, volume=2000
    )
    
    # Features mock
    from features.feature_calculator import FeatureCalculationResult, SignalQuality
    features = FeatureCalculationResult(
        timestamp=pd.Timestamp.now(),
        confluence_score=0.82,
        signal_quality=SignalQuality.STRONG
    )
    
    # Structure data
    structure_data = {
        'vwap_slope': 0.4,
        'vwap_price': 4502.0,
        'poc_price': 4501.0
    }
    
    sierra_patterns = {
        'long_down_up_bar': 0.8,
        'battle_navale_signal': 0.75,
        'base_quality': 0.7
    }
    
    # Simulation historique pour Dow structure
    for i in range(35):
        test_bar = MarketData(
            timestamp=pd.Timestamp.now() - pd.Timedelta(minutes=35-i),
            symbol="ES",
            open=4480.0 + i * 0.5, high=4485.0 + i * 0.5,
            low=4475.0 + i * 0.5, close=4482.0 + i * 0.5, volume=1500
        )
        trend_strategy.price_history.append(test_bar)
        range_strategy.price_history.append(test_bar)
    
    # Test trend strategy
    trend_signal = trend_strategy.analyze_trend_signal(
        features=features, market_data=market_data, 
        structure_data=structure_data, sierra_patterns=sierra_patterns
    )
    
    # Test range strategy (besoin d'un range d'abord)
    # Simulation range 4500-4510
    for i in range(20):
        if i % 4 == 0:  # Test support
            range_price = 4500.0 + np.random.normal(0, 0.5)
        elif i % 4 == 2:  # Test résistance
            range_price = 4510.0 + np.random.normal(0, 0.5)
        else:
            range_price = 4505.0 + np.random.normal(0, 2)
        
        range_bar = MarketData(
            timestamp=pd.Timestamp.now() - pd.Timedelta(minutes=20-i),
            symbol="ES", open=range_price, high=range_price+1,
            low=range_price-1, close=range_price, volume=1200
        )
        range_strategy.price_history.append(range_bar)
    
    # Context pour range
    trend_context = {
        'vwap_slope': 0.1,  # Quasi flat pour range
        'dow_trend_direction': 'sideways',
        'trend_strength': 0.3
    }
    
    range_signal = range_strategy.analyze_range_signal(
        features=features, market_data=market_data,
        trend_context=trend_context, structure_data=structure_data,
        sierra_patterns=sierra_patterns
    )
    
    logger.info("Trend signal: {'Generated' if trend_signal else 'None'}")
    logger.info("Range signal: {'Generated' if range_signal else 'None'}")
    
    if trend_signal:
        logger.info("   • Type: {trend_signal.signal_type.value}")
        logger.info("   • Direction: {trend_signal.direction.value}")
        logger.info("   • R:R: {trend_signal.risk_reward_ratio():.2f}")
    
    if range_signal:
        logger.info("   • Type: {range_signal.signal_type.value}")
        logger.info("   • Direction: {range_signal.direction}")
        logger.info("   • R:R: {range_signal.risk_reward_ratio():.2f}")
    
    return True

def test_strategy_selector():
    """Test orchestration complète"""
    logger.debug("TEST STRATEGY SELECTOR")
    
    # Création selector
    selector = create_strategy_selector()
    
    # Trading context complet
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES", open=4500.0, high=4510.0, low=4495.0, close=4505.0, volume=2000
    )
    
    structure_data = {
        'vwap_price': 4502.0, 'vwap_slope': 0.4,
        'poc_price': 4501.0, 'vah_price': 4515.0, 'val_price': 4485.0,
        'put_wall': 4480.0, 'call_wall': 4520.0
    }
    
    sierra_patterns = {
        'long_down_up_bar': 0.8, 'battle_navale_signal': 0.75,
        'base_quality': 0.7, 'trend_continuation': 0.9
    }
    
    es_nq_data = {
        'es_price': 4505.0, 'nq_price': 4505.0 * 4.5, 'correlation': 0.8
    }
    
    context = TradingContext(
        timestamp=pd.Timestamp.now(),
        market_data=market_data,
        structure_data=structure_data,
        sierra_patterns=sierra_patterns,
        es_nq_data=es_nq_data,
        execution_mode=ExecutionMode.PAPER_TRADING
    )
    
    # Alimentation historique pour régime
    for i in range(40):
        test_bar = MarketData(
            timestamp=pd.Timestamp.now() - pd.Timedelta(minutes=40-i),
            symbol="ES", open=4480.0 + i * 0.6, high=4485.0 + i * 0.6,
            low=4475.0 + i * 0.6, close=4482.0 + i * 0.6, volume=1500
        )
        selector.regime_detector.price_history.append(test_bar)
        selector.trend_strategy.price_history.append(test_bar)
        selector.range_strategy.price_history.append(test_bar)
    
    # Analyse complète
    start_time = time.perf_counter()
    result = selector.analyze_and_select(context)
    analysis_time = (time.perf_counter() - start_time) * 1000
    
    # Validations
    assert analysis_time < 15.0, f"Orchestration trop lente: {analysis_time:.2f}ms"
    assert result.market_regime is not None, "Régime pas détecté"
    
    logger.info("Orchestration: {analysis_time:.2f}ms")
    logger.info("Régime: {result.market_regime.value}")
    logger.info("Stratégie: {result.selected_strategy.value}")
    logger.info("Confluence: {result.confluence_score:.3f}")
    logger.info("Décision: {result.final_decision.value}")
    
    if result.signal_generated:
        logger.info("Signal généré: {type(result.signal_data).__name__}")
    
    return True

def test_integration_complete():
    """Test intégration système complet"""
    logger.debug("TEST INTEGRATION COMPLETE")
    
    # Test pipeline complet : Battle Navale → Market Regime → Features → Strategies → Décision
    
    # 1. Battle Navale
    analyzer = create_battle_navale_analyzer()
    market_data = MarketData(
        timestamp=pd.Timestamp.now(), symbol="ES",
        open=4500.0, high=4510.0, low=4495.0, close=4505.0, volume=2000
    )
    
    battle_result = analyzer.analyze_battle_navale(market_data)
    sierra_patterns = analyzer.get_all_patterns()
    
    # 2. Market Regime Detection
    regime_detector = create_market_regime_detector()
    regime_data = regime_detector.analyze_market_regime(market_data=market_data)
    
    # 3. Features
    calculator = create_feature_calculator()
    features_result = calculator.calculate_all_features(
        market_data=market_data, sierra_patterns=sierra_patterns
    )
    
    # 4. Strategy Selector (intègre régime + strategies)
    selector = create_strategy_selector()
    context = TradingContext(
        timestamp=pd.Timestamp.now(), market_data=market_data,
        sierra_patterns=sierra_patterns, execution_mode=ExecutionMode.PAPER_TRADING
    )
    
    final_result = selector.analyze_and_select(context)
    
    # Validation pipeline complet
    assert sierra_patterns is not None, "Patterns Battle Navale manquants"
    assert regime_data.regime is not None, "Régime market non détecté"
    assert features_result.confluence_score >= 0.0, "Features invalides"
    assert final_result.market_regime is not None, "Régime final non détecté"
    
    logger.info("Pipeline Battle Navale → Market Regime → Features → Strategy → Décision")
    logger.info("Battle signal: {sierra_patterns.get('battle_navale_signal', 0):.2f}")
    logger.info("Market regime: {regime_data.regime.value} (conf: {regime_data.regime_confidence:.2f})")
    logger.info("Confluence: {features_result.confluence_score:.3f}")
    logger.info("Régime final: {final_result.market_regime.value}")
    logger.info("Décision finale: {final_result.final_decision.value}")
    
    return True

def run_phase2_tests():
    """Runner principal tests Phase 2"""
    logger.info("🚀 PHASE 2 INTEGRATION TESTS")
    print("=" * 50)
    
    tests = [
        ("Battle Navale", test_battle_navale),
        ("Market Regime Detector", test_market_regime_detector),
        ("Feature Calculator", test_feature_calculator), 
        ("Strategies", test_strategies),
        ("Strategy Selector", test_strategy_selector),
        ("Integration Complete", test_integration_complete)
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
    
    total_time = (time.perf_counter() - total_start) * 1000
    
    # Summary
    logger.info("\n{'='*50}")
    logger.info("📊 PHASE 2 TEST SUMMARY")
    
    passed = sum(1 for _, status in results if status == "PASS")
    total = len(results)
    
    for test_name, status in results:
        symbol = "✅" if status == "PASS" else "❌"
        logger.info("{symbol} {test_name}: {status}")
    
    logger.info("\n🎯 RESULTS: {passed}/{total} tests passed")
    logger.info("⏱️ Total time: {total_time:.2f}ms")
    
    if passed == total:
        logger.info("\n🎉 ALL PHASE 2 TESTS PASSED!")
        logger.info("PHASE 2 INTEGRATION COMPLETE") 
        logger.info("🚀 READY FOR PHASE 3")
        logger.info("📊 Components testés: Battle Navale, Market Regime, Features, Strategies, Orchestration")
    else:
        logger.info("\n💀 {total - passed} TESTS FAILED")
    
    return passed == total

if __name__ == "__main__":
    success = run_phase2_tests()
    exit(0 if success else 1)