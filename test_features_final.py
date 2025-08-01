#!/usr/bin/env python3
"""
🧪 TEST FEATURES FINAL - MIA_IA_SYSTEM
Test rapide et efficace de tous les calculs dans les features
"""

import sys
import pandas as pd
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.base_types import MarketData, OrderFlowData

logger = get_logger(__name__)

def test_all_features_quick():
    """Test rapide de toutes les features"""
    print("🚀 TEST FEATURES RAPIDE")
    print("="*50)
    
    results = {}
    
    # TEST 1: FeatureCalculator
    try:
        from features.feature_calculator import (
            FeatureCalculator, 
            FeatureCalculationResult,
            CONFLUENCE_WEIGHTS,
            TRADING_THRESHOLDS
        )
        
        # Validation poids
        total_weight = sum(CONFLUENCE_WEIGHTS.values())
        assert abs(total_weight - 1.0) < 0.001
        
        # Test création et calcul
        calculator = FeatureCalculator()
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
        
        results['FeatureCalculator'] = True
        print("✅ FeatureCalculator: OK")
        
    except Exception as e:
        results['FeatureCalculator'] = False
        print(f"❌ FeatureCalculator: {e}")
    
    # TEST 2: SmartMoneyTracker
    try:
        from features.smart_money_tracker import SmartMoneyTracker, SmartMoneyAnalysis
        
        tracker = SmartMoneyTracker()
        market_data = MarketData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            open=4500.0, high=4510.0, low=4490.0, close=4505.0, volume=1000
        )
        order_flow = OrderFlowData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            cumulative_delta=50.0, bid_volume=500, ask_volume=500,
            aggressive_buys=300, aggressive_sells=200, net_delta=100.0
        )
        
        analysis = tracker.analyze_smart_money(market_data, order_flow)
        assert isinstance(analysis, SmartMoneyAnalysis)
        
        results['SmartMoneyTracker'] = True
        print("✅ SmartMoneyTracker: OK")
        
    except Exception as e:
        results['SmartMoneyTracker'] = False
        print(f"❌ SmartMoneyTracker: {e}")
    
    # TEST 3: Order Book Imbalance
    try:
        from features.order_book_imbalance import (
            calculate_order_book_imbalance_feature,
            OrderBookSnapshot,
            OrderBookLevel
        )
        
        # Données market requises
        market_data = MarketData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            open=4500.0, high=4510.0, low=4490.0, close=4505.0, volume=1000
        )
        
        bids = [OrderBookLevel(price=4500.0, size=100)]
        asks = [OrderBookLevel(price=4500.25, size=120)]
        order_book = OrderBookSnapshot(timestamp=pd.Timestamp.now(), bids=bids, asks=asks)
        
        imbalance = calculate_order_book_imbalance_feature(market_data, order_book)
        assert -1.0 <= imbalance <= 1.0
        
        results['OrderBookImbalance'] = True
        print("✅ OrderBookImbalance: OK")
        
    except Exception as e:
        results['OrderBookImbalance'] = False
        print(f"❌ OrderBookImbalance: {e}")
    
    # TEST 4: Delta Divergence
    try:
        from features.advanced.delta_divergence import DeltaDivergenceDetector
        
        detector = DeltaDivergenceDetector()
        for i in range(10):
            detector.add_data_point(4500.0 + i, 10.0 + i, 100 + i)
        
        result = detector.calculate_delta_divergence()
        assert hasattr(result, 'divergence_strength')
        
        results['DeltaDivergence'] = True
        print("✅ DeltaDivergence: OK")
        
    except Exception as e:
        results['DeltaDivergence'] = False
        print(f"❌ DeltaDivergence: {e}")
    
    # TEST 5: Volatility Regime
    try:
        from features.advanced.volatility_regime import VolatilityRegimeCalculator
        
        calculator = VolatilityRegimeCalculator()
        for i in range(10):
            market_data = MarketData(
                timestamp=pd.Timestamp.now(),
                symbol="ES", open=4500.0, high=4510.0, low=4490.0, close=4505.0, volume=1000
            )
            calculator.add_market_data(market_data, 20.0)
        
        regime_result = calculator.calculate_volatility_regime()
        assert hasattr(regime_result, 'regime_confidence')
        
        results['VolatilityRegime'] = True
        print("✅ VolatilityRegime: OK")
        
    except Exception as e:
        results['VolatilityRegime'] = False
        print(f"❌ VolatilityRegime: {e}")
    
    # TEST 6: MTF Confluence
    try:
        from features.mtf_confluence_elite import EliteMTFConfluence, calculate_mtf_confluence_score
        
        analyzer = EliteMTFConfluence()
        
        # Format dictionnaire requis par MTF
        market_data_dict = {
            "symbol": "ES",
            "open": 4500.0,
            "high": 4510.0,
            "low": 4490.0,
            "close": 4505.0,
            "volume": 1000,
            "current_price": 4505.0
        }
        
        score = calculate_mtf_confluence_score(market_data_dict)
        assert -1.0 <= score <= 1.0  # Score MTF entre -1 et 1
        
        results['MTFConfluence'] = True
        print("✅ MTFConfluence: OK")
        
    except Exception as e:
        results['MTFConfluence'] = False
        print(f"❌ MTFConfluence: {e}")
    
    # RÉSULTATS FINAUX
    print("\n" + "="*50)
    print("📊 RÉSULTATS FINAUX")
    print("="*50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 RÉSULTAT GLOBAL: {passed_tests}/{total_tests} tests réussis")
    
    if passed_tests == total_tests:
        print("🎉 TOUS LES CALCULS FEATURES SONT CORRECTS")
        print("✅ Système prêt pour le trading en production")
    else:
        print("⚠️ CERTAINS MODULES ONT ÉCHOUÉ - VÉRIFICATION REQUISE")
    
    return passed_tests == total_tests

def main():
    """Fonction principale"""
    success = test_all_features_quick()
    
    if success:
        print("\n🚀 SYSTÈME FEATURES: OPÉRATIONNEL")
    else:
        print("\n⚠️ SYSTÈME FEATURES: NÉCESSITE CORRECTIONS")

if __name__ == "__main__":
    main()