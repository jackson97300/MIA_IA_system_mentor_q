#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de la chaîne complète decide_mq_distance_integrated
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_full_chain():
    """Test de la chaîne complète"""
    
    print("🔍 TEST CHAÎNE COMPLÈTE decide_mq_distance_integrated")
    print("=" * 60)
    
    try:
        from core.menthorq_distance_trading import MenthorQDistanceTrader
        
        # Créer une instance
        trader = MenthorQDistanceTrader()
        
        # Données de test complètes
        es_data = {
            "t": 1694563200.0,
            "basedata": {
                "open": 4499.75,
                "high": 4500.25,
                "low": 4499.50,
                "close": 4500.0,
                "volume": 1000
            },
            "quote": {
                "bid": 4499.75,
                "ask": 4500.25,
                "mid": 4500.0
            },
            "menthorq": {
                "gamma_wall": {
                    "call_resistance_1": 4500.25,  # 1 tick au-dessus
                    "put_support_1": 4499.75       # 1 tick en dessous
                }
            },
            "nbcv_footprint": {
                "pressure": 1,
                "delta_ratio": 0.2,
                "cumulative_delta": 150
            },
            "cumulative_delta": 150,
            "vix": {
                "value": 18.5
            },
            "vwap": {
                "value": 4500.5
            },
            "vva": {
                "value": 0.5
            }
        }
        
        nq_data = {
            "t": 1694563200.0,
            "basedata": {
                "close": 15000.0
            },
            "quote": {
                "bid": 14999.5,
                "ask": 15000.5,
                "mid": 15000.0
            }
        }
        
        config = {
            "tick_size": 0.25,
            "mq_tolerance_ticks": {"gamma_wall": 10, "hvl": 10, "gex": 10},
            "mia_threshold": 0.001,
            "entry_threshold": 0.30,
            "weights": {"mq": 0.55, "of": 0.30, "structure": 0.15}
        }
        
        print("📊 Données de test:")
        print(f"   - Prix ES: {es_data['basedata']['close']}")
        print(f"   - Niveaux MenthorQ: {es_data['menthorq']}")
        print(f"   - VIX: {es_data['vix']['value']}")
        
        # Test étape par étape
        print("\n🔍 TEST ÉTAPE PAR ÉTAPE:")
        
        # 1. Test _mq_gex_score
        print("\n1️⃣ Test _mq_gex_score...")
        mq_result = trader._mq_gex_score(
            price=es_data["basedata"]["close"],
            mq_levels=es_data["menthorq"],
            tick=config["tick_size"],
            config=config
        )
        
        if mq_result:
            print(f"   ✅ MQ Score: {mq_result}")
        else:
            print("   ❌ MQ Score: None")
            return
        
        # 2. Test _compute_mia_bullish_bidirectional
        print("\n2️⃣ Test _compute_mia_bullish_bidirectional...")
        try:
            mia_score = trader._compute_mia_bullish_bidirectional(es_data)
            print(f"   ✅ MIA Score: {mia_score}")
            print(f"   🔍 DEBUG MIA:")
            print(f"      - Close: {es_data.get('basedata', {}).get('close')}")
            print(f"      - VWAP: {es_data.get('vwap', {})}")
            print(f"      - VWAP value: {es_data.get('vwap', {}).get('value')}")
            print(f"      - Différence: {es_data.get('basedata', {}).get('close') - es_data.get('vwap', {}).get('value')}")
            print(f"      - VWAP Score: {(es_data.get('basedata', {}).get('close') - es_data.get('vwap', {}).get('value')) / es_data.get('vwap', {}).get('value')}")
        except Exception as e:
            print(f"   ❌ MIA Score erreur: {e}")
        
        # 3. Test _orderflow_score
        print("\n3️⃣ Test _orderflow_score...")
        try:
            of_score = trader._orderflow_score(es_data, 0)
            print(f"   ✅ OrderFlow Score: {of_score}")
        except Exception as e:
            print(f"   ❌ OrderFlow Score erreur: {e}")
        
        # 4. Test _structure_score
        print("\n4️⃣ Test _structure_score...")
        try:
            struct_score = trader._structure_score(
                es_data.get("vwap", {}),
                es_data.get("vva", {}),
                es_data.get("basedata", {}).get("close"),
                config["tick_size"]
            )
            print(f"   ✅ Structure Score: {struct_score}")
        except Exception as e:
            print(f"   ❌ Structure Score erreur: {e}")
        
        # 5. Test complet
        print("\n5️⃣ Test complet decide_mq_distance_integrated...")
        result = trader.decide_mq_distance_integrated(es_data, nq_data, config)
        
        if result:
            print(f"   ✅ Résultat complet: {result}")
        else:
            print("   ❌ Résultat complet: None")
            print("   🔍 DEBUG ÉTAPES DÉTAILLÉES:")
            
            # Test étape par étape pour identifier où ça bloque
            print("      - Étape 1: MQ Score...")
            mq_test = trader._mq_gex_score(
                price=es_data.get("basedata", {}).get("close"),
                mq_levels=es_data.get("menthorq", {}),
                tick=config["tick_size"],
                config=config
            )
            print(f"        MQ Result: {mq_test}")
            
            print("      - Étape 2: MIA Score...")
            mia_test = trader._compute_mia_bullish_bidirectional(es_data)
            print(f"        MIA Score: {mia_test}")
            print(f"        MIA Threshold: {config['mia_threshold']}")
            print(f"        Side: {mq_test['side'] if mq_test else 'None'}")
            
            if mq_test and mq_test['side']:
                side = mq_test['side']
                if side == "LONG":
                    check_result = mia_test >= config['mia_threshold']
                    print(f"        LONG Check: {mia_test} >= {config['mia_threshold']} = {check_result}")
                    if not check_result:
                        print(f"        ❌ BLOQUÉ: MIA trop faible pour LONG")
                elif side == "SHORT":
                    check_result = mia_test <= -config['mia_threshold']
                    print(f"        SHORT Check: {mia_test} <= {-config['mia_threshold']} = {check_result}")
                    if not check_result:
                        print(f"        ❌ BLOQUÉ: MIA trop faible pour SHORT")
            
            print("      - Étape 3: Leadership...")
            try:
                snap = trader.leadership_engine.update_from_unified_rows(es_data, nq_data)
                vix_val = es_data.get("vix", {}).get("value")
                gate = trader.leadership_engine.gate_for_es(side=side, vix_value=vix_val)
                print(f"        Leadership Gate: {gate}")
            except Exception as e:
                print(f"        Leadership Error: {e}")
            
            print("      - Étape 4: OrderFlow...")
            try:
                of_test = trader._orderflow_score(es_data, 0)
                print(f"        OrderFlow Result: {of_test}")
            except Exception as e:
                print(f"        OrderFlow Error: {e}")
            
            # Debug des conditions d'arrêt
            print("\n🔍 DEBUG CONDITIONS D'ARRÊT:")
            
            # Vérifier les conditions dans decide_mq_distance_integrated
            if not mq_result or mq_result["side"] is None:
                print("   ❌ Condition 1: mq_result None ou side None")
            else:
                print("   ✅ Condition 1: mq_result OK")
                
            # Vérifier MIA
            try:
                mia_score = trader._compute_mia_bullish_bidirectional(es_data)
                if abs(mia_score) < config["mia_threshold"]:
                    print(f"   ❌ Condition 2: MIA {mia_score} < {config['mia_threshold']}")
                else:
                    print(f"   ✅ Condition 2: MIA {mia_score} >= {config['mia_threshold']}")
            except Exception as e:
                print(f"   ❌ Condition 2: MIA erreur {e}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_chain()
