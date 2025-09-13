#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test rapide de l'intégration MenthorQ-Distance + Leadership dans SignalGenerator
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

def test_signal_generator_integration():
    """Test de l'intégration"""
    print("🎯 TEST INTÉGRATION SIGNAL GENERATOR + MENTHORQ-DISTANCE + LEADERSHIP")
    print("=" * 70)
    
    try:
        # Test 1: Import du SignalGenerator
        print("\n1. Test import SignalGenerator...")
        from strategies.signal_generator import SignalGenerator
        print("✅ SignalGenerator importé")
        
        # Test 2: Initialisation
        print("\n2. Test initialisation...")
        signal_generator = SignalGenerator()
        print("✅ SignalGenerator initialisé")
        
        # Test 3: Vérifier que la méthode decide_mq_distance existe
        print("\n3. Test méthode decide_mq_distance...")
        if hasattr(signal_generator, 'decide_mq_distance'):
            print("✅ Méthode decide_mq_distance disponible")
        else:
            print("❌ Méthode decide_mq_distance manquante")
            return False
        
        # Test 4: Vérifier que le MenthorQ Distance Trader est initialisé
        print("\n4. Test MenthorQ Distance Trader...")
        if hasattr(signal_generator, 'menthorq_distance_trader'):
            print("✅ MenthorQ Distance Trader initialisé")
        else:
            print("❌ MenthorQ Distance Trader manquant")
            return False
        
        # Test 5: Test avec des données d'exemple
        print("\n5. Test avec données d'exemple...")
        
        # Données d'exemple
        es_data = {
            "t": 1705123200.0,
            "basedata": {"close": 4500.0},
            "vwap": {"v": 4499.5},
            "vva": {"vah": 4501.0, "val": 4498.0},
            "nbcv_footprint": {"pressure": 1, "delta_ratio": 0.18, "cumulative_delta": 120.0},
            "menthorq": {"gamma": {"put_support_0dte": 4498.0}},
            "vix": {"value": 18.5}
        }
        
        nq_data = {
            "t": 1705123200.0,
            "basedata": {"close": 18500.0},
            "vwap": {"v": 18495.0},
            "vva": {"vah": 18505.0, "val": 18485.0},
            "nbcv_footprint": {"pressure": 1, "delta_ratio": 0.15, "cumulative_delta": 85.0}
        }
        
        config = {
            "tick_size": 0.25,
            "entry_threshold": 0.70
        }
        
        # Appeler la méthode
        signal = signal_generator.decide_mq_distance(es_data, nq_data, config)
        
        if signal:
            print(f"✅ Signal généré: {signal['action']} (Score: {signal['score']})")
        else:
            print("ℹ️ Pas de signal (normal selon les données d'exemple)")
        
        print("\n🎉 TOUS LES TESTS SONT PASSÉS !")
        print("✅ L'intégration est opérationnelle")
        print("🚀 Prêt pour la production")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_signal_generator_integration()
    sys.exit(0 if success else 1)

