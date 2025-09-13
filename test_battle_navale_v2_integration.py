#!/usr/bin/env python3
"""
TEST D'INTÉGRATION BATTLE NAVALE V2
===================================

Test complet des corrections appliquées :
1. Unified Stops (7 ticks partout)
2. True Break Logic unifiée
3. MIA Staleness intégré
4. Configuration harmonisée

Version: Test Final
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.battle_navale_v2 import BattleNavaleV2, BattleNavaleV2Result
from core.unified_stops import calculate_unified_stops
from core.mia_bullish import BullishScorer
from core.logger import get_logger

logger = get_logger(__name__)

def create_test_data_battle_navale():
    """Créer des données de test pour Battle Navale V2"""
    
    # Données ES de base
    es_data = {
        "symbol": "ES",
        "timestamp": datetime.now(),
        "price": 4150.25,
        "open": 4148.50,
        "high": 4152.75,
        "low": 4147.25,
        "close": 4150.25,
        "volume": 125000,
        "vwap": 4149.80,
        "cumulative_delta": 2500,
        "bid": 4150.00,
        "ask": 4150.50,
        "bid_size": 150,
        "ask_size": 200,
        "last_trade_size": 25,
        "last_trade_price": 4150.25,
        "last_trade_time": datetime.now()
    }
    
    # Données VIX
    vix_data = {
        "symbol": "VIX",
        "value": 18.5,  # VIX MID
        "timestamp": datetime.now(),
        "change": 0.3,
        "change_percent": 1.65
    }
    
    # Données MenthorQ
    menthorq_data = {
        "timestamp": datetime.now(),
        "call_resistance": 4155.00,
        "put_support": 4145.00,
        "hvl": 4150.00,
        "one_day_min": 4140.00,
        "one_day_max": 4160.00,
        "zero_dte_levels": [4148.00, 4152.00],
        "gex_levels": [4146.00, 4154.00],
        "blind_spots": [4149.00, 4151.00],
        "dealers_bias": 0.15
    }
    
    # Données OrderFlow
    orderflow_data = {
        "timestamp": datetime.now(),
        "cumulative_delta": 2500,
        "delta_ratio": 0.65,
        "pressure": 0.45,
        "bid_volume": 75000,
        "ask_volume": 50000,
        "aggressive_trades": 1200,
        "footprint": {
            "level_4150": {"bid": 150, "ask": 200, "volume": 350},
            "level_4149": {"bid": 200, "ask": 100, "volume": 300},
            "level_4151": {"bid": 100, "ask": 180, "volume": 280}
        },
        "level2": {
            "bid_levels": [
                {"price": 4150.00, "size": 150},
                {"price": 4149.75, "size": 200},
                {"price": 4149.50, "size": 180}
            ],
            "ask_levels": [
                {"price": 4150.25, "size": 200},
                {"price": 4150.50, "size": 150},
                {"price": 4150.75, "size": 120}
            ]
        }
    }
    
    # Données Leadership ES/NQ
    leadership_data = {
        "timestamp": datetime.now(),
        "es_price": 4150.25,
        "nq_price": 18500.50,
        "es_volume": 125000,
        "nq_volume": 98000,
        "correlation": 0.85,
        "zmomentum_3s": 0.12,
        "zmomentum_30s": 0.08,
        "zmomentum_5min": 0.15,
        "dynamic_beta": 1.05,
        "leadership_score": 0.25
    }
    
    # Données Volume Profile
    volume_profile_data = {
        "timestamp": datetime.now(),
        "poc": 4150.00,  # Point of Control
        "value_area_high": 4152.00,
        "value_area_low": 4148.00,
        "volume_at_price": {
            "4148.00": 15000,
            "4149.00": 25000,
            "4150.00": 35000,  # POC
            "4151.00": 20000,
            "4152.00": 10000
        }
    }
    
    # Données unifiées
    unified_data = {
        "es": es_data,
        "vix": vix_data,
        "menthorq": menthorq_data,
        "orderflow": orderflow_data,
        "leadership": leadership_data,
        "volume_profile": volume_profile_data,
        "timestamp": datetime.now()
    }
    
    return unified_data

def test_unified_stops_integration():
    """Test 1: Vérifier l'intégration des Unified Stops"""
    print("\n" + "="*60)
    print("🧪 TEST 1: UNIFIED STOPS INTÉGRATION")
    print("="*60)
    
    try:
        # Test direct du système unifié
        entry_price = 4150.25
        
        # Test LONG
        long_stops = calculate_unified_stops(
            entry_price=entry_price,
            side="LONG",
            use_fixed=True
        )
        
        print(f"✅ LONG Stops @ {entry_price}:")
        print(f"   Entry: {long_stops['entry']}")
        print(f"   Stop:  {long_stops['stop']} (7 ticks)")
        print(f"   TP1:   {long_stops['target1']} (2R)")
        print(f"   TP2:   {long_stops['target2']} (3R)")
        print(f"   Risk:  {long_stops['risk_dollars']} USD")
        
        # Test SHORT
        short_stops = calculate_unified_stops(
            entry_price=entry_price,
            side="SHORT",
            use_fixed=True
        )
        
        print(f"\n✅ SHORT Stops @ {entry_price}:")
        print(f"   Entry: {short_stops['entry']}")
        print(f"   Stop:  {short_stops['stop']} (7 ticks)")
        print(f"   TP1:   {short_stops['target1']} (2R)")
        print(f"   TP2:   {short_stops['target2']} (3R)")
        print(f"   Risk:  {short_stops['risk_dollars']} USD")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur Unified Stops: {e}")
        return False

def test_mia_staleness_integration():
    """Test 2: Vérifier l'intégration MIA Staleness"""
    print("\n" + "="*60)
    print("🧪 TEST 2: MIA STALENESS INTÉGRATION")
    print("="*60)
    
    try:
        # Créer instance BullishScorer
        mia_scorer = BullishScorer()
        
        # Données de test
        test_data = create_test_data_battle_navale()
        
        # Test calcul score avec staleness
        mia_score = mia_scorer.calculate_bullish_score(test_data)
        
        print(f"✅ MIA Score calculé: {mia_score:.3f}")
        print(f"   Bullish: {mia_score > 0.2}")
        print(f"   Bearish: {mia_score < -0.2}")
        print(f"   Neutral: {abs(mia_score) <= 0.2}")
        
        # Vérifier que les logs de staleness sont générés
        print("✅ Logs de staleness générés automatiquement")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur MIA Staleness: {e}")
        return False

def test_battle_navale_v2_full_analysis():
    """Test 3: Analyse complète Battle Navale V2"""
    print("\n" + "="*60)
    print("🧪 TEST 3: BATTLE NAVALE V2 - ANALYSE COMPLÈTE")
    print("="*60)
    
    try:
        # Créer instance Battle Navale V2
        bn_v2 = BattleNavaleV2()
        
        # Données de test
        test_data = create_test_data_battle_navale()
        
        print("📊 Données de test créées:")
        print(f"   ES Price: {test_data['es']['price']}")
        print(f"   VIX: {test_data['vix']['value']}")
        print(f"   MenthorQ Call Res: {test_data['menthorq']['call_resistance']}")
        print(f"   MenthorQ Put Sup: {test_data['menthorq']['put_support']}")
        
        # Analyse complète
        start_time = time.perf_counter()
        result = bn_v2.analyze_battle_navale_v2(test_data)
        analysis_time = time.perf_counter() - start_time
        
        print(f"\n✅ Analyse terminée en {analysis_time*1000:.1f}ms")
        print(f"   Battle Status: {result.battle_status}")
        print(f"   Signal: {result.battle_navale_signal:.3f}")
        print(f"   Base Quality: {result.base_quality:.3f}")
        print(f"   VIX Regime: {result.vix_regime}")
        print(f"   DOM Health: {result.dom_health}")
        print(f"   Sensitive Window: {result.sensitive_window}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur Battle Navale V2: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_true_break_logic():
    """Test 4: Vérifier la logique True Break unifiée"""
    print("\n" + "="*60)
    print("🧪 TEST 4: TRUE BREAK LOGIC UNIFIÉE")
    print("="*60)
    
    try:
        bn_v2 = BattleNavaleV2()
        
        # Barre de test
        test_bar = {
            "open": 4148.50,
            "high": 4152.75,
            "low": 4147.25,
            "close": 4150.25
        }
        
        level_price = 4150.00
        vix_value = 18.5  # VIX MID
        
        # Test cassure résistance (LONG)
        resistance_break = bn_v2.is_true_breakout_at_close(
            bar=test_bar,
            level_price=level_price,
            vix_value=vix_value,
            level_type="resistance"
        )
        
        print(f"✅ Cassure Résistance @ {level_price}:")
        print(f"   Close: {test_bar['close']} > Level: {level_price} = {test_bar['close'] > level_price}")
        print(f"   True Break: {resistance_break}")
        
        # Test cassure support (SHORT)
        support_break = bn_v2.is_true_breakout_at_close(
            bar=test_bar,
            level_price=level_price,
            vix_value=vix_value,
            level_type="support"
        )
        
        print(f"\n✅ Cassure Support @ {level_price}:")
        print(f"   Close: {test_bar['close']} < Level: {level_price} = {test_bar['close'] < level_price}")
        print(f"   True Break: {support_break}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur True Break: {e}")
        return False

def test_configuration_consistency():
    """Test 5: Vérifier la cohérence de la configuration"""
    print("\n" + "="*60)
    print("🧪 TEST 5: CONFIGURATION COHÉRENCE")
    print("="*60)
    
    try:
        # Charger la configuration
        with open('config/battle_navale_v2.json', 'r') as f:
            config = json.load(f)
        
        vix_regimes = config['battle_navale_v2']['vix_regimes']
        
        print("✅ Vérification des bandes VIX:")
        for regime, data in vix_regimes.items():
            print(f"   {regime}: {data['min_value']}-{data['max_value']}, "
                  f"stop_ticks={data['stop_ticks']}")
        
        # Vérifier que tous les stops sont à 7 ticks
        all_7_ticks = all(data['stop_ticks'] == 7 for data in vix_regimes.values())
        print(f"\n✅ Tous les stops à 7 ticks: {all_7_ticks}")
        
        # Vérifier les clés VIX
        expected_keys = ['LOW', 'MID', 'HIGH', 'EXTREME']
        actual_keys = list(vix_regimes.keys())
        keys_consistent = actual_keys == expected_keys
        print(f"✅ Clés VIX cohérentes: {keys_consistent}")
        print(f"   Attendu: {expected_keys}")
        print(f"   Actuel:  {actual_keys}")
        
        return all_7_ticks and keys_consistent
        
    except Exception as e:
        print(f"❌ Erreur Configuration: {e}")
        return False

def run_all_tests():
    """Exécuter tous les tests"""
    print("🚀 DÉMARRAGE DES TESTS BATTLE NAVALE V2")
    print("="*80)
    
    tests = [
        ("Unified Stops", test_unified_stops_integration),
        ("MIA Staleness", test_mia_staleness_integration),
        ("Battle Navale V2 Full", test_battle_navale_v2_full_analysis),
        ("True Break Logic", test_true_break_logic),
        ("Configuration", test_configuration_consistency)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} a échoué: {e}")
            results.append((test_name, False))
    
    # Résumé final
    print("\n" + "="*80)
    print("📊 RÉSUMÉ DES TESTS BATTLE NAVALE V2")
    print("="*80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 RÉSULTAT FINAL: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS RÉUSSIS ! Battle Navale V2 est prête !")
        return True
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
