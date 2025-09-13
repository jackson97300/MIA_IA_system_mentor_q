#!/usr/bin/env python3
"""
DEBUG TRIGGER MENTHORQ
======================

Test spécifique pour identifier pourquoi le trigger MenthorQ retourne None
"""

import sys
import os
import time
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.menthorq_distance_trading import MenthorQDistanceTrader
from core.logger import get_logger

logger = get_logger(__name__)

def create_debug_test_data():
    """Créer des données de test pour debug"""
    
    # Données ES avec prix TRÈS PROCHE d'un niveau MenthorQ
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
        "last_trade_time": datetime.now(),
        
        # Données VIX
        "vix": {
            "value": 18.5,
            "timestamp": datetime.now()
        },
        
        # Données MenthorQ - PRIX EXTRÊMEMENT PROCHE
        "menthorq": {
            "timestamp": datetime.now(),
            "call_resistance": 4150.30,  # SEULEMENT 0.05 points de distance !
            "put_support": 4145.00,
            "hvl": 4150.00,
            "one_day_min": 4140.00,
            "one_day_max": 4160.00,
            "zero_dte_levels": [4148.00, 4152.00],
            "gex_levels": [4146.00, 4154.00],
            "blind_spots": [4149.00, 4151.00],
            "dealers_bias": 0.15
        },
        
        # Données OrderFlow
        "orderflow": {
            "timestamp": datetime.now(),
            "cumulative_delta": 2500,
            "delta_ratio": 0.65,
            "pressure": 0.45,
            "bid_volume": 75000,
            "ask_volume": 50000,
            "aggressive_trades": 1200
        },
        
        # Données Leadership
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
            "leadership_score": 0.25
        }
    }
    
    # Données NQ
    nq_data = es_data.copy()
    nq_data["symbol"] = "NQ"
    
    return es_data, nq_data

def debug_menthorq_trigger():
    """Debug du trigger MenthorQ"""
    print("🔍 DEBUG TRIGGER MENTHORQ")
    print("="*50)
    
    try:
        # Créer les données de test
        es_data, nq_data = create_debug_test_data()
        
        print("📊 Données de test:")
        print(f"   ES Price: {es_data['price']}")
        print(f"   MenthorQ Call Res: {es_data['menthorq']['call_resistance']}")
        print(f"   Distance: {abs(es_data['price'] - es_data['menthorq']['call_resistance']):.2f} points")
        print(f"   VIX: {es_data['vix']['value']}")
        
        # Créer instance MenthorQDistanceTrader
        mq_trader = MenthorQDistanceTrader()
        
        print(f"\n🔧 Test du trigger MenthorQ...")
        
        # Test direct du trigger
        result = mq_trader.decide_mq_distance_integrated(es_data, nq_data)
        
        print(f"   Résultat: {result}")
        
        if result is None:
            print("   ❌ PROBLÈME: Le trigger retourne None")
            print("   🔍 Vérifions les étapes internes...")
            
            # Test des étapes internes
            debug_internal_steps(mq_trader, es_data, nq_data)
        else:
            print(f"   ✅ SUCCÈS: Trigger fonctionne")
            print(f"   Action: {result.get('action', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def debug_internal_steps(mq_trader, es_data, nq_data):
    """Debug des étapes internes du trigger MenthorQ"""
    print("\n🔍 DEBUG ÉTAPES INTERNES:")
    
    try:
        # 1. Test MQ Score
        print("\n1️⃣ Test MQ Score...")
        tick = 0.25  # ES tick size
        config = mq_trader.config
        print(f"   Config type: {type(config)}")
        print(f"   Config attributes: {dir(config)}")
        
        # Convertir config en dict si nécessaire
        if hasattr(config, '__dict__'):
            config_dict = config.__dict__
        else:
            config_dict = config
            
        mq_score = mq_trader._mq_gex_score(es_data, nq_data, tick, config_dict)
        print(f"   MQ Score: {mq_score}")
        
        # 2. Test MIA Bullish
        print("\n2️⃣ Test MIA Bullish...")
        mia_score = mq_trader._compute_mia_bullish_bidirectional(es_data, nq_data)
        print(f"   MIA Score: {mia_score}")
        
        # 3. Test Structure Score
        print("\n3️⃣ Test Structure Score...")
        structure_score = mq_trader._structure_score(es_data['price'], es_data['price'] * 0.25)  # 1 tick
        print(f"   Structure Score: {structure_score}")
        
        # 4. Test OrderFlow Score
        print("\n4️⃣ Test OrderFlow Score...")
        of_score = mq_trader._orderflow_score(es_data, nq_data)
        print(f"   OrderFlow Score: {of_score}")
        
        # 5. Test Leadership
        print("\n5️⃣ Test Leadership...")
        leadership = mq_trader._leadership_score(es_data, nq_data)
        print(f"   Leadership: {leadership}")
        
        # 6. Test VIX Regime
        print("\n6️⃣ Test VIX Regime...")
        vix_regime = mq_trader._vix_regime(es_data.get('vix', {}).get('value', 20))
        print(f"   VIX Regime: {vix_regime}")
        
        # 7. Test des seuils
        print("\n7️⃣ Test des seuils...")
        config = mq_trader.config
        print(f"   Seuil enter_eff: {config.get('menthorq', {}).get('thresholds', {}).get('enter_eff', 'N/A')}")
        print(f"   Seuil MIA long: {config.get('mia', {}).get('gate_long', 'N/A')}")
        print(f"   Seuil MIA short: {config.get('mia', {}).get('gate_short', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Erreur dans debug interne: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_menthorq_trigger()
