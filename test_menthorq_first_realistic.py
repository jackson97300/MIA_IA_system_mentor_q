#!/usr/bin/env python3
"""
TEST MENTHORQ FIRST AVEC DONNÉES RÉALISTES
==========================================

Test avec des données qui devraient déclencher des signaux
"""

import sys
import os
import time
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.menthorq_first_method import MenthorQFirstMethod
from core.logger import get_logger

logger = get_logger(__name__)

def create_realistic_test_data():
    """Créer des données de test réalistes qui devraient déclencher des signaux"""
    
    # Données ES avec prix proche d'un niveau MenthorQ
    es_data = {
        "symbol": "ES",
        "timestamp": datetime.now(),
        "price": 4150.25,
        "open": 4148.50,
        "high": 4152.75,
        "low": 4147.25,
        "close": 4150.25,
        "volume": 125000,
        "vwap": 4149.80,  # VWAP proche du prix pour biais positif
        "cumulative_delta": 2500,  # Delta positif
        "bid": 4150.00,
        "ask": 4150.50,
        "bid_size": 150,
        "ask_size": 200,
        "last_trade_size": 25,
        "last_trade_price": 4150.25,
        "last_trade_time": datetime.now(),
        
        # Données VIX
        "vix": {
            "value": 18.5,  # VIX MID
            "timestamp": datetime.now()
        },
        
        # Données MenthorQ - PRIX TRÈS PROCHE D'UN NIVEAU
        "menthorq": {
            "timestamp": datetime.now(),
            "call_resistance": 4150.50,  # TRÈS PROCHE du prix actuel (4150.25)
            "put_support": 4145.00,
            "hvl": 4150.00,
            "one_day_min": 4140.00,
            "one_day_max": 4160.00,
            "zero_dte_levels": [4148.00, 4152.00],
            "gex_levels": [4146.00, 4154.00],
            "blind_spots": [4149.00, 4151.00],
            "dealers_bias": 0.15
        },
        
        # Données OrderFlow favorables
        "orderflow": {
            "timestamp": datetime.now(),
            "cumulative_delta": 2500,  # Delta positif
            "delta_ratio": 0.65,  # Ratio favorable
            "pressure": 0.45,
            "bid_volume": 75000,
            "ask_volume": 50000,
            "aggressive_trades": 1200,
            "footprint": {
                "level_4150": {"bid": 150, "ask": 200, "volume": 350},
                "level_4149": {"bid": 200, "ask": 100, "volume": 300},
                "level_4151": {"bid": 100, "ask": 180, "volume": 280}
            }
        },
        
        # Données Leadership favorables
        "leadership": {
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
            "leadership_score": 0.25  # Score positif
        }
    }
    
    # Données NQ (identique à ES pour simplicité)
    nq_data = es_data.copy()
    nq_data["symbol"] = "NQ"
    
    return es_data, nq_data

def test_menthorq_first_realistic():
    """Test MenthorQ First avec des données réalistes"""
    print("🚀 TEST MENTHORQ FIRST AVEC DONNÉES RÉALISTES")
    print("="*60)
    
    try:
        # Créer les données de test
        es_data, nq_data = create_realistic_test_data()
        
        print("📊 Données de test créées:")
        print(f"   ES Price: {es_data['price']}")
        print(f"   MenthorQ Call Res: {es_data['menthorq']['call_resistance']}")
        print(f"   Distance: {abs(es_data['price'] - es_data['menthorq']['call_resistance']):.2f} points")
        print(f"   VIX: {es_data['vix']['value']}")
        print(f"   VWAP: {es_data['vwap']}")
        print(f"   Cumulative Delta: {es_data['cumulative_delta']}")
        
        # Créer instance MenthorQ First
        mq_first = MenthorQFirstMethod()
        
        # Analyse complète
        start_time = time.perf_counter()
        result = mq_first.analyze_menthorq_first_opportunity(es_data, nq_data)
        analysis_time = time.perf_counter() - start_time
        
        print(f"\n✅ Analyse terminée en {analysis_time*1000:.1f}ms")
        print(f"   Action: {result.action}")
        print(f"   Score: {result.score:.3f}")
        print(f"   MQ Score: {result.mq_score:.3f}")
        print(f"   OF Score: {result.of_score:.3f}")
        print(f"   MIA Score: {result.mia_bullish:.3f}")
        print(f"   VIX Regime: {result.vix_regime}")
        print(f"   Level: {result.mq_level}")
        print(f"   E/U/L: {result.eul}")
        
        # Statistiques
        print(f"\n📊 Statistiques:")
        for key, value in mq_first.stats.items():
            print(f"   {key}: {value}")
        
        # Audit data
        if result.audit_data:
            print(f"\n🔍 Audit Data:")
            for key, value in result.audit_data.items():
                if isinstance(value, dict):
                    print(f"   {key}: {len(value)} éléments")
                else:
                    print(f"   {key}: {value}")
        
        # Vérification des scores
        if result.score > 0:
            print(f"\n🎉 SUCCÈS ! Score généré: {result.score:.3f}")
            return True
        else:
            print(f"\n⚠️ ATTENTION ! Score toujours à zéro")
            print("🔍 Vérifions les étapes de la chaîne...")
            
            # Test étape par étape
            test_step_by_step(mq_first, es_data, nq_data)
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step_by_step(mq_first, es_data, nq_data):
    """Test étape par étape pour identifier le problème"""
    print("\n🔍 TEST ÉTAPE PAR ÉTAPE:")
    
    try:
        # 1. Test trigger MenthorQ
        print("\n1️⃣ Test trigger MenthorQ...")
        menthorq_result = mq_first.menthorq_trader.decide_mq_distance_integrated(es_data, nq_data)
        print(f"   Résultat: {menthorq_result}")
        
        if not menthorq_result or menthorq_result.get('action') == 'NO_SIGNAL':
            print("   ❌ Pas de trigger MenthorQ - C'est le problème principal !")
            return
        
        # 2. Test MIA Bullish
        print("\n2️⃣ Test MIA Bullish...")
        ok_mia, mia_score = mq_first._check_mia_bullish_gate(es_data, menthorq_result)
        print(f"   MIA Score: {mia_score:.3f}, OK: {ok_mia}")
        
        # 3. Test Leadership
        print("\n3️⃣ Test Leadership...")
        leadership_gate = mq_first._check_leadership_gate(es_data, nq_data, menthorq_result)
        print(f"   Leadership Gate: {leadership_gate}")
        
        # 4. Test OrderFlow
        print("\n4️⃣ Test OrderFlow...")
        orderflow_score = mq_first._validate_orderflow(es_data, menthorq_result)
        print(f"   OrderFlow Score: {orderflow_score:.3f}")
        
        # 5. Test Structure
        print("\n5️⃣ Test Structure...")
        structure_score = mq_first._analyze_structure_context(es_data, menthorq_result)
        print(f"   Structure Score: {structure_score:.3f}")
        
    except Exception as e:
        print(f"❌ Erreur dans test étape par étape: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    success = test_menthorq_first_realistic()
    if success:
        print("\n🎉 TEST RÉUSSI ! MenthorQ First génère des signaux !")
    else:
        print("\n⚠️ TEST PARTIEL - Vérifiez les logs ci-dessus")
    
    sys.exit(0 if success else 1)
