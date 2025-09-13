#!/usr/bin/env python3
"""
TEST MENTHORQ SIMPLE
====================

Test simple pour générer un signal MenthorQ
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

def create_simple_test_data():
    """Créer des données de test simples"""
    
    # Données ES avec prix EXACTEMENT sur un niveau MenthorQ
    es_data = {
        "symbol": "ES",
        "timestamp": datetime.now(),
        "price": 4150.25,
        "open": 4148.50,
        "high": 4151.50,  # Réduire la mèche haute pour respecter la tolérance (5 ticks = 1.25 points)
        "low": 4147.25,
        "close": 4150.25,
        "volume": 125000,
        "vwap": 4150.5,  # VWAP au-dessus du prix (bearish pour signal SHORT)
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
        
        # Données MenthorQ - FORMAT CORRECT POUR _mq_gex_score
        "menthorq": {
            "call_resistance": {
                "call_resistance_1": 4150.25,  # EXACTEMENT le même prix !
                "call_resistance_2": 4155.00
            },
            "put_support": {
                "put_support_1": 4145.00,
                "put_support_2": 4140.00
            },
            "hvl": {
                "hvl_1": 4150.00,
                "hvl_2": 4148.00
            },
            "one_day_min": {
                "one_day_min_1": 4140.00
            },
            "one_day_max": {
                "one_day_max_1": 4160.00
            },
            "zero_dte_levels": {
                "zero_dte_1": 4148.00,
                "zero_dte_2": 4152.00
            },
            "gex_levels": {
                "gex_1": 4146.00,
                "gex_2": 4154.00
            },
            "blind_spots": {
                "blind_spot_1": 4149.00,
                "blind_spot_2": 4151.00
            },
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

def test_menthorq_simple():
    """Test simple MenthorQ"""
    print("🚀 TEST MENTHORQ SIMPLE")
    print("="*40)
    
    try:
        # Créer les données de test
        es_data, nq_data = create_simple_test_data()
        
        print("📊 Données de test:")
        print(f"   ES Price: {es_data['price']}")
        print(f"   MenthorQ Call Res: {es_data['menthorq']['call_resistance']['call_resistance_1']}")
        print(f"   Distance: {abs(es_data['price'] - es_data['menthorq']['call_resistance']['call_resistance_1']):.2f} points")
        print(f"   VIX: {es_data['vix']['value']}")
        
        # Créer instance MenthorQDistanceTrader
        mq_trader = MenthorQDistanceTrader()
        
        # Charger la configuration MenthorQ First et la convertir en dictionnaire
        from config.config_loader import load_config_file
        config_ns = load_config_file("config/menthorq_first_method.json", "menthorq_first_method")
        
        # Convertir SimpleNamespace en dictionnaire pour compatibilité
        def namespace_to_dict(ns):
            if hasattr(ns, '__dict__'):
                return {k: namespace_to_dict(v) for k, v in ns.__dict__.items()}
            return ns
        
        config = namespace_to_dict(config_ns)
        
        print(f"\n🔧 Test du trigger MenthorQ...")
        
        # DEBUG: Vérifier le format des données MenthorQ
        print(f"\n🔍 DEBUG - Format des données MenthorQ:")
        print(f"   Type: {type(es_data.get('menthorq', {}))}")
        print(f"   Contenu: {es_data.get('menthorq', {})}")
        
        # DEBUG: Vérifier chaque niveau
        mq_data = es_data.get('menthorq', {})
        for level_type, levels in mq_data.items():
            if level_type != 'dealers_bias':
                print(f"   {level_type}: {type(levels)} = {levels}")
        
        # DEBUG: Vérifier ce qui est passé à _mq_gex_score
        print(f"\n🔍 DEBUG - Données passées à _mq_gex_score:")
        print(f"   Price: {es_data.get('price', 0)}")
        print(f"   MQ Levels: {es_data.get('menthorq', {})}")
        print(f"   Tick: 0.25")
        print(f"   Config: {type(mq_trader.config)}")
        
        # Test direct du trigger avec configuration MenthorQ First
        print(f"🔍 DEBUG - Configuration passée au code: {type(config)}")
        print(f"🔍 DEBUG - Configuration keys: {list(config.keys()) if hasattr(config, 'keys') else 'N/A'}")
        result = mq_trader.decide_mq_distance_integrated(es_data, nq_data, config)
        
        print(f"   Résultat: {result}")
        
        if result is None:
            print("   ❌ PROBLÈME: Le trigger retourne toujours None")
            print("   🔍 Vérifions la configuration...")
            
            # Vérifier la configuration
            print(f"   Config type: {type(mq_trader.config)}")
            print(f"   Config: {mq_trader.config}")
            
            # Essayer avec une config par défaut
            print(f"\n🔧 Test avec config par défaut...")
            result2 = mq_trader.decide_mq_distance_integrated(es_data, nq_data, {})
            print(f"   Résultat avec config vide: {result2}")
            
        else:
            print(f"   ✅ SUCCÈS: Trigger fonctionne")
            print(f"   Action: {result.get('action', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            print(f"   Score: {result.get('score', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_menthorq_simple()
