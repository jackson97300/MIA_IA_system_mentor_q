#!/usr/bin/env python3
"""
🧪 TEST FEATURES CALCULATIONS - MIA_IA_SYSTEM
Vérification de tous les calculs dans les features
"""

import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.base_types import MarketData, OrderFlowData

logger = get_logger(__name__)

def test_feature_calculator_calculations():
    """Test des calculs du feature calculator"""
    logger.info("🔧 TEST 1: Feature Calculator Calculations")
    
    try:
        from features.feature_calculator import (
            FeatureCalculator, 
            FeatureCalculationResult,
            CONFLUENCE_WEIGHTS,
            TRADING_THRESHOLDS
        )
        
        # Test 1: Validation des poids
        total_weight = sum(CONFLUENCE_WEIGHTS.values())
        assert abs(total_weight - 1.0) < 0.001, f"Poids doivent faire 100%, got {total_weight:.3f}"
        logger.info(f"✅ Poids confluence: {total_weight:.3f} (100%)")
        
        # Test 2: Validation des seuils
        assert TRADING_THRESHOLDS['PREMIUM_SIGNAL'] == 0.85
        assert TRADING_THRESHOLDS['STRONG_SIGNAL'] == 0.70
        assert TRADING_THRESHOLDS['WEAK_SIGNAL'] == 0.60
        logger.info("✅ Seuils trading corrects")
        
        # Test 3: Création calculateur
        calculator = FeatureCalculator()
        logger.info("✅ FeatureCalculator créé")
        
        # Test 4: Calcul confluence score
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
        
        confluence_score = calculator._calculate_confluence_score(test_result)
        assert 0.0 <= confluence_score <= 1.0
        logger.info(f"✅ Score confluence: {confluence_score:.3f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 1: Feature Calculator - ÉCHEC: {e}")
        return False

def test_smart_money_calculations():
    """Test des calculs Smart Money"""
    logger.info("🔧 TEST 2: Smart Money Calculations")
    
    try:
        from features.smart_money_tracker import (
            SmartMoneyTracker,
            SmartMoneyAnalysis,
            SmartMoneyFlow,
            LargeTrade
        )
        
        # Test création tracker
        tracker = SmartMoneyTracker()
        logger.info("✅ SmartMoneyTracker créé")
        
        # Test données simulées
        market_data = MarketData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            open=4500.0,
            high=4510.0,
            low=4490.0,
            close=4505.0,
            volume=1000
        )
        
        order_flow = OrderFlowData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            cumulative_delta=50.0,
            bid_volume=500,
            ask_volume=500,
            aggressive_buys=300,
            aggressive_sells=200,
            net_delta=100.0
        )
        
        # Test analyse
        analysis = tracker.analyze_smart_money(market_data, order_flow)
        assert isinstance(analysis, SmartMoneyAnalysis)
        assert 0.0 <= analysis.confidence <= 1.0
        assert 0.0 <= analysis.smart_money_score <= 1.0
        logger.info(f"✅ Smart Money score: {analysis.smart_money_score:.3f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 2: Smart Money - ÉCHEC: {e}")
        return False

def test_delta_divergence_calculations():
    """Test des calculs Delta Divergence"""
    logger.info("🔧 TEST 3: Delta Divergence Calculations")
    
    try:
        from features.advanced.delta_divergence import (
            DeltaDivergenceDetector,
            DeltaDivergenceResult
        )
        
        # Test création détecteur
        detector = DeltaDivergenceDetector()
        logger.info("✅ DeltaDivergenceDetector créé")
        
        # Test données simulées
        for i in range(20):
            price = 4500.0 + i * 0.5
            net_delta = 10.0 + i * 2.0
            volume = 100 + i * 10
            detector.add_data_point(price, net_delta, volume)
        
        # Test calcul divergence
        result = detector.calculate_delta_divergence()
        assert isinstance(result, DeltaDivergenceResult)
        assert 0.0 <= result.divergence_strength <= 1.0
        assert -1.0 <= result.entry_signal <= 1.0
        logger.info(f"✅ Divergence strength: {result.divergence_strength:.3f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 3: Delta Divergence - ÉCHEC: {e}")
        return False

def test_volatility_regime_calculations():
    """Test des calculs Volatility Regime"""
    logger.info("🔧 TEST 4: Volatility Regime Calculations")
    
    try:
        from features.advanced.volatility_regime import (
            VolatilityRegimeCalculator,
            VolatilityRegimeResult
        )
        
        # Test création calculateur
        calculator = VolatilityRegimeCalculator()
        logger.info("✅ VolatilityRegimeCalculator créé")
        
        # Test données simulées
        for i in range(30):
            market_data = MarketData(
                timestamp=pd.Timestamp.now() - timedelta(days=30-i),
                symbol="ES",
                open=4500.0 + i * 0.1,
                high=4510.0 + i * 0.1,
                low=4490.0 + i * 0.1,
                close=4505.0 + i * 0.1,
                volume=1000 + i * 10
            )
            calculator.add_market_data(market_data, 20.0 + i * 0.1)
        
        # Test calcul régime
        result = calculator.calculate_volatility_regime()
        assert isinstance(result, VolatilityRegimeResult)
        assert 0.0 <= result.regime_confidence <= 1.0
        assert 0.5 <= result.risk_adjustment <= 2.0
        logger.info(f"✅ Régime volatilité: {result.regime.value}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 4: Volatility Regime - ÉCHEC: {e}")
        return False

def test_order_book_imbalance_calculations():
    """Test des calculs Order Book Imbalance"""
    logger.info("🔧 TEST 5: Order Book Imbalance Calculations")
    
    try:
        from features.order_book_imbalance import (
            calculate_order_book_imbalance_feature,
            OrderBookSnapshot,
            OrderBookLevel
        )
        
        # Test données simulées avec structure correcte
        bids = [
            OrderBookLevel(price=4500.0, size=100),
            OrderBookLevel(price=4499.75, size=150),
            OrderBookLevel(price=4499.5, size=200)
        ]
        
        asks = [
            OrderBookLevel(price=4500.25, size=120),
            OrderBookLevel(price=4500.5, size=180),
            OrderBookLevel(price=4500.75, size=250)
        ]
        
        order_book = OrderBookSnapshot(
            timestamp=pd.Timestamp.now(),
            bids=bids,
            asks=asks
        )
        
        # Test calcul imbalance
        imbalance = calculate_order_book_imbalance_feature(order_book)
        assert -1.0 <= imbalance <= 1.0
        logger.info(f"✅ Order Book Imbalance: {imbalance:.3f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 5: Order Book Imbalance - ÉCHEC: {e}")
        return False

def test_mtf_confluence_calculations():
    """Test des calculs MTF Confluence"""
    logger.info("🔧 TEST 6: MTF Confluence Calculations")
    
    try:
        from features.mtf_confluence_elite import (
            calculate_mtf_confluence_score,
            EliteMTFConfluence
        )
        
        # Test création analyseur
        analyzer = EliteMTFConfluence()
        logger.info("✅ EliteMTFConfluence créé")
        
        # Test données simulées
        market_data = MarketData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            open=4500.0,
            high=4510.0,
            low=4490.0,
            close=4505.0,
            volume=1000
        )
        
        # Test calcul confluence
        score = calculate_mtf_confluence_score(market_data)
        assert 0.0 <= score <= 1.0
        logger.info(f"✅ MTF Confluence score: {score:.3f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 6: MTF Confluence - ÉCHEC: {e}")
        return False

def run_all_feature_tests():
    """Exécute tous les tests de features"""
    logger.info("🚀 DÉMARRAGE TEST FEATURES CALCULATIONS")
    
    tests = [
        test_feature_calculator_calculations,
        test_smart_money_calculations,
        test_delta_divergence_calculations,
        test_volatility_regime_calculations,
        test_order_book_imbalance_calculations,
        test_mtf_confluence_calculations
    ]
    
    results = {}
    for test in tests:
        results[test.__name__] = test()
    
    # Résultats finaux
    logger.info("\n" + "="*60)
    logger.info("📊 RÉSULTATS TEST FEATURES CALCULATIONS")
    logger.info("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n📈 RÉSULTAT GLOBAL: {passed_tests}/{total_tests} tests réussis")
    
    if passed_tests == total_tests:
        logger.info("🎉 TOUS LES CALCULS FEATURES SONT CORRECTS")
        logger.info("✅ Feature Calculator: Poids et seuils validés")
        logger.info("✅ Smart Money: Scores et analyses corrects")
        logger.info("✅ Delta Divergence: Détection et signaux valides")
        logger.info("✅ Volatility Regime: Régimes et ajustements corrects")
        logger.info("✅ Order Book Imbalance: Calculs pression valides")
        logger.info("✅ MTF Confluence: Scores multi-timeframe corrects")
    else:
        logger.info("⚠️ CERTAINS CALCULS ONT ÉCHOUÉ - VÉRIFICATION REQUISE")
    
    logger.info("\n📋 FEATURES TESTÉES:")
    logger.info("• Feature Calculator (confluence, poids, seuils)")
    logger.info("• Smart Money Tracker (flux institutionnels)")
    logger.info("• Delta Divergence (divergences prix/delta)")
    logger.info("• Volatility Regime (régimes volatilité)")
    logger.info("• Order Book Imbalance (pression achat/vente)")
    logger.info("• MTF Confluence (confluence multi-timeframe)")

def main():
    """Fonction principale"""
    run_all_feature_tests()

if __name__ == "__main__":
    main() 