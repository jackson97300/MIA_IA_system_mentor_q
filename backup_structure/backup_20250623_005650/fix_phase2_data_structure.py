"""
MIA_IA_SYSTEM - Fix Phase 2 Data Structure Issues
Correction des problèmes d'attributs entre MarketData et OrderFlowData
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

def test_battle_navale_corrected():
    """Test méthode signature Battle Navale - CORRIGÉ"""
    logger.debug("TEST BATTLE NAVALE - STRUCTURE CORRIGÉE")
    
    # Création analyzer
    analyzer = create_battle_navale_analyzer()
    
    # Market data correct
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4500.0,
        high=4510.0, 
        low=4495.0,
        close=4505.0,
        volume=2000
    )
    
    # Order flow correct avec tous les attributs requis
    order_flow = OrderFlowData(
        timestamp=market_data.timestamp,
        symbol="ES",  # Ajout du symbol requis
        cumulative_delta=150.0,  # Attribut requis dans OrderFlowData
        bid_volume=800,
        ask_volume=1200,
        aggressive_buys=60,
        aggressive_sells=40
    )
    
    # Vérification des attributs disponibles
    logger.info("📊 MarketData attributes: {[attr for attr in dir(market_data) if not attr.startswith('_')]}")
    logger.info("📊 OrderFlowData attributes: {[attr for attr in dir(order_flow) if not attr.startswith('_')]}")
    logger.info("📊 OrderFlow net_delta: {order_flow.net_delta}")  # Doit fonctionner
    
    # Test analyse avec les deux objets corrects
    start_time = time.perf_counter()
    result = analyzer.analyze_battle_navale(market_data, order_flow)
    calc_time = (time.perf_counter() - start_time) * 1000
    
    # Validations
    assert calc_time < 2.0, f"Battle navale trop lent: {calc_time:.2f}ms"
    assert hasattr(result, 'battle_navale_signal'), "Signal manquant"
    assert 0.0 <= result.battle_navale_signal <= 1.0, "Signal hors range"
    
    logger.info("Battle navale: {calc_time:.2f}ms")
    logger.info("Signal: {result.battle_navale_signal:.2f}")
    
    return True

def test_market_regime_detector_corrected():
    """Test détection régime marché - CORRIGÉ"""
    logger.debug("TEST MARKET REGIME DETECTOR - STRUCTURE CORRIGÉE")
    
    # Création détecteur
    detector = create_market_regime_detector()
    
    # Simulation trend haussier pour historique avec MarketData correct
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
        
        # Alimentation historique avec MarketData seulement
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
    
    # Structure data as dict (pas d'objet MarketData ici)
    structure_data = {
        'vwap_slope': 0.7,  # Trend fort
        'vwap_price': 4505.0,
        'poc_price': 4507.0
    }
    
    # ES/NQ data as dict
    es_nq_data = {
        'es_price': 4508.0,
        'nq_price': 4508.0 * 4.5,
        'correlation': 0.85
    }
    
    # Test analyse régime avec les bons paramètres
    start_time = time.perf_counter()
    regime_data = detector.analyze_market_regime(
        market_data=current_data,  # MarketData object
        structure_data=structure_data,  # Dict
        es_nq_data=es_nq_data  # Dict
    )
    analysis_time = (time.perf_counter() - start_time) * 1000
    
    # Validations
    assert analysis_time < 3.0, f"Regime detection trop lent: {analysis_time:.2f}ms"
    assert regime_data.regime_confidence > 0.0, "Confidence nulle"
    assert regime_data.regime is not None, "Aucun régime détecté"
    
    logger.info("Regime analysis: {analysis_time:.2f}ms")
    logger.info("Regime detected: {regime_data.regime.value}")
    logger.info("Confidence: {regime_data.regime_confidence:.2f}")
    
    return True

def test_feature_calculator_corrected():
    """Test calcul 8 features + confluence - CORRIGÉ"""
    logger.debug("TEST FEATURE CALCULATOR - STRUCTURE CORRIGÉE")
    
    calculator = create_feature_calculator()
    
    # Market data correct
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES", 
        open=4500.0, 
        high=4510.0, 
        low=4495.0, 
        close=4505.0, 
        volume=1800
    )
    
    # OrderFlow data correct (optionnel pour features)
    order_flow = OrderFlowData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        cumulative_delta=50.0,
        bid_volume=800,
        ask_volume=1000,
        aggressive_buys=45,
        aggressive_sells=30
    )
    
    # Options data correct
    options_data = OptionsData(
        timestamp=pd.Timestamp.now(),
        call_wall=4520.0, 
        put_wall=4480.0, 
        net_gamma=2.5,
        call_volume=1200, 
        put_volume=800
    )
    
    # Structure data correct
    structure_data = MarketStructureData(
        timestamp=pd.Timestamp.now(),
        poc_price=4501.0, 
        vah_price=4515.0, 
        val_price=4485.0,
        vwap_price=4502.0, 
        vwap_slope=0.3
    )
    
    # Sierra patterns as dict
    sierra_patterns = {
        'battle_navale_signal': 0.8,
        'base_quality': 0.7,
        'trend_continuation': 0.9,
        'battle_strength': 0.75
    }
    
    # Test calcul avec les bons types
    start_time = time.perf_counter()
    result = calculator.calculate_all_features(
        market_data=market_data,  # MarketData object
        options_data=options_data,  # OptionsData object  
        structure_data=structure_data,  # MarketStructureData object
        sierra_patterns=sierra_patterns,  # Dict
        order_flow=order_flow  # OrderFlowData object (optionnel)
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

def test_strategies_corrected():
    """Test strategies trend + range - CORRIGÉ"""
    logger.debug("TEST STRATEGIES - STRUCTURE CORRIGÉE")
    
    # Création strategies
    trend_strategy = create_trend_strategy()
    range_strategy = create_range_strategy()
    
    # Market data correct
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES", 
        open=4500.0, 
        high=4510.0, 
        low=4495.0, 
        close=4505.0, 
        volume=2000
    )
    
    # Features mock avec structure correcte
    from features.feature_calculator import FeatureCalculationResult, SignalQuality
    features = FeatureCalculationResult(
        timestamp=pd.Timestamp.now(),
        confluence_score=0.82,
        signal_quality=SignalQuality.STRONG
    )
    
    # Structure data as dict (pas MarketData)
    structure_data = {
        'vwap_slope': 0.4,
        'vwap_price': 4502.0,
        'poc_price': 4501.0
    }
    
    # Sierra patterns as dict
    sierra_patterns = {
        'long_down_up_bar': 0.8,
        'battle_navale_signal': 0.75,
        'base_quality': 0.7
    }
    
    # Simulation historique pour Dow structure avec MarketData correct
    for i in range(35):
        test_bar = MarketData(
            timestamp=pd.Timestamp.now() - pd.Timedelta(minutes=35-i),
            symbol="ES",
            open=4480.0 + i * 0.5, 
            high=4485.0 + i * 0.5,
            low=4475.0 + i * 0.5, 
            close=4482.0 + i * 0.5, 
            volume=1500
        )
        trend_strategy.price_history.append(test_bar)
        range_strategy.price_history.append(test_bar)
    
    # Test trend strategy avec les bons paramètres
    trend_signal = trend_strategy.analyze_trend_signal(
        features=features,  # FeatureCalculationResult object
        market_data=market_data,  # MarketData object
        structure_data=structure_data,  # Dict
        sierra_patterns=sierra_patterns  # Dict
    )
    
    logger.info("Trend signal: {'Generated' if trend_signal else 'None'}")
    
    if trend_signal:
        logger.info("   • Type: {trend_signal.signal_type.value}")
        logger.info("   • Direction: {trend_signal.direction.value}")
        logger.info("   • R:R: {trend_signal.risk_reward_ratio():.2f}")
    
    return True

def test_strategy_selector_corrected():
    """Test orchestration complète - CORRIGÉ"""
    logger.debug("TEST STRATEGY SELECTOR - STRUCTURE CORRIGÉE")
    
    # Création selector
    selector = create_strategy_selector()
    
    # Trading context complet avec structures correctes
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES", 
        open=4500.0, 
        high=4510.0, 
        low=4495.0, 
        close=4505.0, 
        volume=2000
    )
    
    # Tous les data en dict (pas d'objets MarketData dans les dicts)
    structure_data = {
        'vwap_price': 4502.0, 
        'vwap_slope': 0.4,
        'poc_price': 4501.0, 
        'vah_price': 4515.0, 
        'val_price': 4485.0,
        'put_wall': 4480.0, 
        'call_wall': 4520.0
    }
    
    sierra_patterns = {
        'long_down_up_bar': 0.8, 
        'battle_navale_signal': 0.75,
        'base_quality': 0.7, 
        'trend_continuation': 0.9
    }
    
    es_nq_data = {
        'es_price': 4505.0, 
        'nq_price': 4505.0 * 4.5, 
        'correlation': 0.8
    }
    
    # TradingContext avec les bons types
    context = TradingContext(
        timestamp=pd.Timestamp.now(),
        market_data=market_data,  # MarketData object
        structure_data=structure_data,  # Dict
        sierra_patterns=sierra_patterns,  # Dict
        es_nq_data=es_nq_data,  # Dict
        execution_mode=ExecutionMode.PAPER_TRADING
    )
    
    # Alimentation historique pour régime avec MarketData correct
    for i in range(40):
        test_bar = MarketData(
            timestamp=pd.Timestamp.now() - pd.Timedelta(minutes=40-i),
            symbol="ES", 
            open=4480.0 + i * 0.6, 
            high=4485.0 + i * 0.6,
            low=4475.0 + i * 0.6, 
            close=4482.0 + i * 0.6, 
            volume=1500
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

def run_corrected_phase2_tests():
    """Runner principal tests Phase 2 corrigés"""
    logger.info("🚀 PHASE 2 INTEGRATION TESTS - VERSION CORRIGÉE")
    print("=" * 60)
    
    tests = [
        ("Battle Navale Corrected", test_battle_navale_corrected),
        ("Market Regime Detector Corrected", test_market_regime_detector_corrected),
        ("Feature Calculator Corrected", test_feature_calculator_corrected), 
        ("Strategies Corrected", test_strategies_corrected),
        ("Strategy Selector Corrected", test_strategy_selector_corrected),
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
    logger.info("\n{'='*60}")
    logger.info("📊 PHASE 2 CORRECTED TEST SUMMARY")
    
    passed = sum(1 for _, status in results if status == "PASS")
    total = len(results)
    
    for test_name, status in results:
        symbol = "✅" if status == "PASS" else "❌"
        logger.info("{symbol} {test_name}: {status}")
    
    logger.info("\n🎯 RESULTS: {passed}/{total} tests passed")
    logger.info("⏱️ Total time: {total_time:.2f}ms")
    
    if passed == total:
        logger.info("\n🎉 ALL PHASE 2 CORRECTED TESTS PASSED!")
        logger.info("PHASE 2 INTEGRATION COMPLETE") 
        logger.info("🚀 READY FOR PHASE 3")
        logger.info("📊 Data structure issues fixed!")
    else:
        logger.info("\n💀 {total - passed} TESTS STILL FAILING")
    
    return passed == total

if __name__ == "__main__":
    success = run_corrected_phase2_tests()
    exit(0 if success else 1)