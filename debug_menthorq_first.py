#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour MenthorQ First Method
===============================================
Trace exactement où la méthode s'arrête et pourquoi.
"""

import sys
import json
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

def debug_menthorq_first():
    """Diagnostic complet de la méthode MenthorQ First"""
    
    print("🔍 DIAGNOSTIC MENTHORQ FIRST METHOD")
    print("=" * 50)
    
    try:
        # 1. Test d'import
        print("1️⃣ Test d'import...")
        from core.menthorq_first_method import MenthorQFirstMethod
        print("✅ Import réussi")
        
        # 2. Test d'initialisation
        print("\n2️⃣ Test d'initialisation...")
        method = MenthorQFirstMethod()
        print("✅ Initialisation réussi")
        
        # 3. Test de configuration
        print("\n3️⃣ Test de configuration...")
        config_path = "config/menthorq_first_method.json"
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"✅ Configuration chargée: {config_path}")
            print(f"   - enter_eff: {config.get('menthorq_first_method', {}).get('enter_eff', 'N/A')}")
            print(f"   - mq_tolerance_ticks: {config.get('menthorq_first_method', {}).get('mq_tolerance_ticks', 'N/A')}")
        else:
            print(f"❌ Configuration non trouvée: {config_path}")
            return
        
        # 4. Test avec données simples
        print("\n4️⃣ Test avec données simples...")
        
        # Données ES minimales
        es_data = {
            "t": 1694563200.0,
            "basedata": {
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
                    "call_resistance_1": 4501.0,
                    "call_resistance_2": 4502.0,
                    "put_support_1": 4499.0,
                    "put_support_2": 4498.0
                },
                "hvl": {
                    "high_volume_level_1": 4500.5,
                    "high_volume_level_2": 4499.5
                },
                "gex_levels": {
                    "call_gex_1": 4501.5,
                    "put_gex_1": 4498.5
                }
            },
            "nbcv": {
                "net_buying_volume": 200
            },
            "cumulative_delta": {
                "delta": 150
            },
            "vix": {
                "close": 18.5
            }
        }
        
        # Données NQ minimales
        nq_data = {
            "t": 1694563200.0,
            "basedata": {
                "close": 15000.0,
                "volume": 800
            },
            "quote": {
                "bid": 14999.5,
                "ask": 15000.5,
                "mid": 15000.0
            },
            "menthorq": {
                "gamma_wall": {
                    "call_resistance_1": 15001.0,
                    "call_resistance_2": 15002.0,
                    "put_support_1": 14999.0,
                    "put_support_2": 14998.0
                },
                "hvl": {
                    "high_volume_level_1": 15000.5,
                    "high_volume_level_2": 14999.5
                },
                "gex_levels": {
                    "call_gex_1": 15001.5,
                    "put_gex_1": 14998.5
                }
            },
            "nbcv": {
                "net_buying_volume": 180
            },
            "cumulative_delta": {
                "delta": 120
            }
        }
        
        print("✅ Données de test créées")
        print(f"   - Prix ES: {es_data['basedata']['close']}")
        print(f"   - Prix NQ: {nq_data['basedata']['close']}")
        print(f"   - VIX: {es_data['vix']['close']}")
        
        # 5. Test d'analyse
        print("\n5️⃣ Test d'analyse...")
        result = method.analyze_trading_opportunity(es_data, nq_data)
        
        print(f"✅ Analyse terminée")
        print(f"   - Signal: {result.signal}")
        print(f"   - Confiance: {result.confidence:.3f}")
        print(f"   - Score MenthorQ: {result.menthorq_score:.3f}")
        print(f"   - Score Orderflow: {result.orderflow_score:.3f}")
        print(f"   - Score Structure: {result.structure_score:.3f}")
        print(f"   - Score Final: {result.final_score:.3f}")
        
        # 6. Diagnostic détaillé
        print("\n6️⃣ Diagnostic détaillé...")
        
        # Test direct de MenthorQDistanceTrader
        print("\n   🔍 Test MenthorQDistanceTrader...")
        from core.menthorq_distance_trading import MenthorQDistanceTrader
        mq_trader = MenthorQDistanceTrader()
        
        # Configuration de test
        test_config = {
            "tick_size": 0.25,
            "mq_tolerance_ticks": {"gamma_wall": 10, "hvl": 10, "gex": 10},
            "mia_threshold": 0.20,
            "entry_threshold": 0.30,
            "weights": {"mq": 0.55, "of": 0.30, "structure": 0.15}
        }
        
        mq_result = mq_trader.decide_mq_distance_integrated(es_data, nq_data, test_config)
        
        if mq_result:
            print(f"   ✅ MenthorQDistanceTrader retourne: {mq_result.get('action', 'N/A')}")
            print(f"   - Confiance: {mq_result.get('confidence', 0.0):.3f}")
            print(f"   - Dealers Bias: {mq_result.get('dealers_bias_score', 0.0):.3f}")
        else:
            print("   ❌ MenthorQDistanceTrader retourne None")
        
        # 7. Test des composants individuels
        print("\n7️⃣ Test des composants individuels...")
        
        # Test MenthorQProcessor
        print("\n   🔍 Test MenthorQProcessor...")
        from features.menthorq_processor import MenthorQProcessor
        mq_processor = MenthorQProcessor()
        
        # Test de calcul de distance
        distance_result = mq_processor.calculate_level_distances(
            es_data.get('menthorq', {}),
            es_data['basedata']['close']
        )
        
        if distance_result:
            print(f"   ✅ Distance calculée: {distance_result}")
        else:
            print("   ❌ Aucune distance calculée")
        
        # Test BullishScorer
        print("\n   🔍 Test BullishScorer...")
        from core.mia_bullish import BullishScorer
        bullish_scorer = BullishScorer()
        
        bullish_score = bullish_scorer.calculate_bullish_score(es_data)
        print(f"   ✅ Score Bullish: {bullish_score:.3f}")
        
        # Test LeadershipZMom
        print("\n   🔍 Test LeadershipZMom...")
        from features.leadership_zmom import LeadershipZMom
        leadership = LeadershipZMom()
        
        # Simuler quelques updates
        for i in range(5):
            t = 1694563200.0 + i
            es_price = 4500.0 + i * 0.25
            nq_price = 15000.0 + i * 0.5
            snap = leadership.update_prices(t, es_price, nq_price)
            if snap:
                print(f"   ✅ Leadership LS: {snap.ls:.3f} (t={t})")
                break
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_menthorq_first()
