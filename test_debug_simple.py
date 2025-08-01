#!/usr/bin/env python3
"""
🔍 TEST DEBUG SIMPLE - MIA_IA_SYSTEM
Test de debug pour identifier le problème exact
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

print("🚀 DÉMARRAGE TEST DEBUG")

try:
    print("1. Test import logger...")
    from core.logger import get_logger
    print("✅ Logger importé")
    
    print("2. Test import feature calculator...")
    from features.feature_calculator import CONFLUENCE_WEIGHTS, TRADING_THRESHOLDS
    print("✅ Feature calculator importé")
    
    print("3. Test validation poids...")
    total_weight = sum(CONFLUENCE_WEIGHTS.values())
    print(f"✅ Poids total: {total_weight:.3f}")
    
    print("4. Test validation seuils...")
    print(f"✅ Seuils: {TRADING_THRESHOLDS}")
    
    print("5. Test création FeatureCalculator...")
    from features.feature_calculator import FeatureCalculator
    calculator = FeatureCalculator()
    print("✅ FeatureCalculator créé")
    
    print("6. Test création FeatureCalculationResult...")
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
    print("✅ FeatureCalculationResult créé")
    
    print("7. Test calcul confluence...")
    confluence_score = calculator._calculate_confluence_score(test_result)
    print(f"✅ Score confluence: {confluence_score:.3f}")
    
    print("8. Test import order book...")
    from features.order_book_imbalance import OrderBookLevel, OrderBookSnapshot
    from core.base_types import MarketData
    print("✅ Order book importé")
    
    print("9. Test création order book data...")
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
    print("✅ Order book data créé")
    
    print("10. Test création snapshot...")
    order_book = OrderBookSnapshot(
        timestamp=pd.Timestamp.now(),
        bids=bids,
        asks=asks
    )
    print("✅ Snapshot créé")
    
    print("11. Test création MarketData...")
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4500.0,
        high=4505.0,
        low=4495.0,
        close=4502.0,
        volume=1500
    )
    print("✅ MarketData créé")
    
    print("12. Test calcul imbalance...")
    from features.order_book_imbalance import calculate_order_book_imbalance_feature
    imbalance = calculate_order_book_imbalance_feature(market_data, order_book)
    print(f"✅ Imbalance: {imbalance:.3f}")
    
    print("\n🎉 TOUS LES TESTS RÉUSSIS!")
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    print("Traceback complet:")
    traceback.print_exc() 