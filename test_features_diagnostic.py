#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC FEATURES - MIA_IA_SYSTEM
Test de diagnostic pour identifier les problèmes dans les modules de features
"""

import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test des imports de base"""
    print("🔍 TEST 1: Imports de base")
    
    try:
        from core.logger import get_logger
        print("✅ core.logger importé")
    except Exception as e:
        print(f"❌ core.logger: {e}")
        return False
    
    try:
        from core.base_types import MarketData, OrderFlowData
        print("✅ core.base_types importé")
    except Exception as e:
        print(f"❌ core.base_types: {e}")
        return False
    
    return True

def test_feature_calculator_imports():
    """Test des imports feature_calculator"""
    print("\n🔍 TEST 2: Feature Calculator imports")
    
    try:
        from features.feature_calculator import (
            FeatureCalculator, 
            CONFLUENCE_WEIGHTS,
            TRADING_THRESHOLDS
        )
        print("✅ FeatureCalculator importé")
        print(f"✅ CONFLUENCE_WEIGHTS: {CONFLUENCE_WEIGHTS}")
        print(f"✅ TRADING_THRESHOLDS: {TRADING_THRESHOLDS}")
        
        # Test validation poids
        total_weight = sum(CONFLUENCE_WEIGHTS.values())
        print(f"✅ Total poids: {total_weight:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ FeatureCalculator: {e}")
        return False

def test_smart_money_imports():
    """Test des imports smart_money_tracker"""
    print("\n🔍 TEST 3: Smart Money imports")
    
    try:
        from features.smart_money_tracker import (
            SmartMoneyTracker,
            SmartMoneyAnalysis
        )
        print("✅ SmartMoneyTracker importé")
        
        # Test création tracker
        tracker = SmartMoneyTracker()
        print("✅ SmartMoneyTracker créé")
        
        return True
        
    except Exception as e:
        print(f"❌ SmartMoneyTracker: {e}")
        return False

def test_delta_divergence_imports():
    """Test des imports delta_divergence"""
    print("\n🔍 TEST 4: Delta Divergence imports")
    
    try:
        from features.advanced.delta_divergence import (
            DeltaDivergenceDetector,
            DeltaDivergenceResult
        )
        print("✅ DeltaDivergenceDetector importé")
        
        # Test création détecteur
        detector = DeltaDivergenceDetector()
        print("✅ DeltaDivergenceDetector créé")
        
        return True
        
    except Exception as e:
        print(f"❌ DeltaDivergenceDetector: {e}")
        return False

def test_volatility_regime_imports():
    """Test des imports volatility_regime"""
    print("\n🔍 TEST 5: Volatility Regime imports")
    
    try:
        from features.advanced.volatility_regime import (
            VolatilityRegimeCalculator,
            VolatilityRegimeResult
        )
        print("✅ VolatilityRegimeCalculator importé")
        
        # Test création calculateur
        calculator = VolatilityRegimeCalculator()
        print("✅ VolatilityRegimeCalculator créé")
        
        return True
        
    except Exception as e:
        print(f"❌ VolatilityRegimeCalculator: {e}")
        return False

def test_order_book_imbalance_imports():
    """Test des imports order_book_imbalance"""
    print("\n🔍 TEST 6: Order Book Imbalance imports")
    
    try:
        from features.order_book_imbalance import (
            calculate_order_book_imbalance_feature,
            OrderBookSnapshot
        )
        print("✅ OrderBookSnapshot importé")
        
        return True
        
    except Exception as e:
        print(f"❌ OrderBookSnapshot: {e}")
        return False

def test_mtf_confluence_imports():
    """Test des imports mtf_confluence_elite"""
    print("\n🔍 TEST 7: MTF Confluence imports")
    
    try:
        from features.mtf_confluence_elite import (
            calculate_mtf_confluence_score,
            EliteMTFConfluence
        )
        print("✅ EliteMTFConfluence importé")
        
        return True
        
    except Exception as e:
        print(f"❌ EliteMTFConfluence: {e}")
        return False

def run_diagnostic():
    """Exécute le diagnostic complet"""
    print("🚀 DÉMARRAGE DIAGNOSTIC FEATURES")
    print("="*50)
    
    tests = [
        test_imports,
        test_feature_calculator_imports,
        test_smart_money_imports,
        test_delta_divergence_imports,
        test_volatility_regime_imports,
        test_order_book_imbalance_imports,
        test_mtf_confluence_imports
    ]
    
    results = {}
    for test in tests:
        results[test.__name__] = test()
    
    # Résultats finaux
    print("\n" + "="*50)
    print("📊 RÉSULTATS DIAGNOSTIC")
    print("="*50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 RÉSULTAT GLOBAL: {passed_tests}/{total_tests} tests réussis")
    
    if passed_tests == total_tests:
        print("🎉 TOUS LES IMPORTS SONT CORRECTS")
    else:
        print("⚠️ CERTAINS IMPORTS ONT ÉCHOUÉ - CORRECTION REQUISE")

def main():
    """Fonction principale"""
    run_diagnostic()

if __name__ == "__main__":
    main() 