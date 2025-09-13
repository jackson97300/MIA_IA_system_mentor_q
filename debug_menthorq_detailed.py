#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic détaillé MenthorQ First Method
========================================
Trace exactement où la méthode s'arrête et pourquoi.
"""

import sys
import json
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

def debug_menthorq_detailed():
    """Diagnostic détaillé de la méthode MenthorQ First"""
    
    print("🔍 DIAGNOSTIC DÉTAILLÉ MENTHORQ FIRST METHOD")
    print("=" * 60)
    
    try:
        # 1. Import et initialisation
        print("1️⃣ Import et initialisation...")
        from core.menthorq_first_method import MenthorQFirstMethod
        method = MenthorQFirstMethod()
        print("✅ Méthode initialisée")
        
        # 2. Données de test avec niveaux MenthorQ proches du prix
        print("\n2️⃣ Données de test...")
        
        es_data = {
            "t": 1694563200.0,
            "basedata": {
                "open": 4499.75,
                "high": 4500.25,
                "low": 4499.50,
                "close": 4500.0,  # Prix actuel
                "volume": 1000
            },
            "quote": {
                "bid": 4499.75,
                "ask": 4500.25,
                "mid": 4500.0
            },
            "menthorq": {
                "gamma_wall": {
                    "call_resistance_1": 4500.25,  # TRÈS PROCHE du prix (1 tick)
                    "call_resistance_2": 4500.50,
                    "put_support_1": 4499.75,      # TRÈS PROCHE du prix (1 tick)
                    "put_support_2": 4499.50
                },
                "hvl": {
                    "high_volume_level_1": 4500.0,  # EXACTEMENT le prix
                    "high_volume_level_2": 4499.75
                },
                "gex_levels": {
                    "call_gex_1": 4500.25,  # TRÈS PROCHE du prix (1 tick)
                    "put_gex_1": 4499.75
                }
            },
            "nbcv": {
                "net_buying_volume": 200
            },
            "cumulative_delta": {
                "delta": 150
            },
            "vix": {
                "value": 18.5  # VIX bas pour test
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
            },
            "menthorq": {
                "gamma_wall": {
                    "call_resistance_1": 15000.25,
                    "put_support_1": 14999.75
                },
                "hvl": {
                    "high_volume_level_1": 15000.0
                },
                "gex_levels": {
                    "call_gex_1": 15000.25,
                    "put_gex_1": 14999.75
                }
            }
        }
        
        print("✅ Données de test créées")
        print(f"   - Prix ES: {es_data['basedata']['close']}")
        print(f"   - Niveaux MenthorQ proches: {es_data['menthorq']['gamma_wall']}")
        print(f"   - VIX: {es_data['vix']['value']}")
        
        # 3. Test direct de MenthorQDistanceTrader
        print("\n3️⃣ Test MenthorQDistanceTrader...")
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
        
        print("   🔍 Appel decide_mq_distance_integrated...")
        mq_result = mq_trader.decide_mq_distance_integrated(es_data, nq_data, test_config)
        
        if mq_result:
            print(f"   ✅ MenthorQDistanceTrader retourne:")
            print(f"      - Action: {mq_result.get('action', 'N/A')}")
            print(f"      - Confiance: {mq_result.get('confidence', 0.0):.3f}")
            print(f"      - Dealers Bias: {mq_result.get('dealers_bias_score', 0.0):.3f}")
            print(f"      - Level Price: {mq_result.get('level_price', 'N/A')}")
        else:
            print("   ❌ MenthorQDistanceTrader retourne None")
        
        # 4. Test des composants individuels
        print("\n4️⃣ Test des composants individuels...")
        
        # Test MenthorQProcessor
        print("\n   🔍 Test MenthorQProcessor...")
        from features.menthorq_processor import MenthorQProcessor
        mq_processor = MenthorQProcessor()
        
        # Test de calcul de distance (méthode correcte)
        try:
            # Vérifier les méthodes disponibles
            methods = [method for method in dir(mq_processor) if not method.startswith('_')]
            print(f"   📋 Méthodes disponibles: {methods[:5]}...")
            
            # Test avec la méthode correcte si elle existe
            if hasattr(mq_processor, 'analyze_levels'):
                distance_result = mq_processor.analyze_levels(
                    es_data.get('menthorq', {}),
                    es_data['basedata']['close']
                )
                print(f"   ✅ Analyse des niveaux: {distance_result}")
            else:
                print("   ⚠️ Méthode analyze_levels non trouvée")
                
        except Exception as e:
            print(f"   ❌ Erreur test MenthorQProcessor: {e}")
        
        # Test BullishScorer
        print("\n   🔍 Test BullishScorer...")
        from core.mia_bullish import BullishScorer
        bullish_scorer = BullishScorer()
        
        bullish_score = bullish_scorer.calculate_bullish_score(es_data)
        print(f"   ✅ Score Bullish: {bullish_score:.3f}")
        
        # 5. Test de la méthode complète
        print("\n5️⃣ Test de la méthode complète...")
        result = method.analyze_menthorq_first_opportunity(es_data, nq_data)
        
        print(f"✅ Analyse terminée")
        print(f"   - Signal: {result.signal_type}")
        print(f"   - Confiance: {result.confidence:.3f}")
        print(f"   - Score MenthorQ: {result.menthorq_score:.3f}")
        print(f"   - Score Orderflow: {result.orderflow_score:.3f}")
        print(f"   - Score Structure: {result.structure_score:.3f}")
        print(f"   - Score Final: {result.final_score:.3f}")
        
        # 6. Audit data
        if hasattr(result, 'audit_data') and result.audit_data:
            print(f"\n6️⃣ Audit Data:")
            for key, value in result.audit_data.items():
                print(f"   - {key}: {value}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_menthorq_detailed()
