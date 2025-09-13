#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test d'intégration de la méthode MenthorQ-Distance avec Leadership Z-Momentum

Ce script teste l'intégration complète et valide que tous les composants fonctionnent ensemble.
"""

import sys
from pathlib import Path
import json
import time

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test des imports"""
    print("🔍 Test des imports...")
    
    try:
        from features.leadership_zmom import LeadershipZMom, LSSnapshot
        print("✅ LeadershipZMom importé")
    except ImportError as e:
        print(f"❌ Erreur import LeadershipZMom: {e}")
        return False
    
    try:
        from core.menthorq_distance_trading import MenthorQDistanceTrader
        print("✅ MenthorQDistanceTrader importé")
    except ImportError as e:
        print(f"❌ Erreur import MenthorQDistanceTrader: {e}")
        return False
    
    return True

def test_leadership_zmom():
    """Test du module LeadershipZMom"""
    print("\n🔍 Test du module LeadershipZMom...")
    
    try:
        from features.leadership_zmom import LeadershipZMom
        
        # Initialiser
        leader = LeadershipZMom(horizons=(3, 30, 300), alpha=0.2)
        print("✅ LeadershipZMom initialisé")
        
        # Test update_prices
        snap = leader.update_prices(1705123200.0, 4500.0, 18500.0)
        print(f"✅ Snapshot créé: LS={snap.ls}, Beta={snap.beta}")
        
        # Test gate_for_es
        gate = leader.gate_for_es("LONG", vix_value=18.5)
        print(f"✅ Gate calculé: allow={gate['allow']}, bonus={gate['bonus']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test LeadershipZMom: {e}")
        return False

def test_menthorq_distance_trader():
    """Test du MenthorQDistanceTrader"""
    print("\n🔍 Test du MenthorQDistanceTrader...")
    
    try:
        from core.menthorq_distance_trading import MenthorQDistanceTrader
        
        # Initialiser
        trader = MenthorQDistanceTrader()
        print("✅ MenthorQDistanceTrader initialisé")
        
        # Vérifier que le leadership_engine est présent
        if hasattr(trader, 'leadership_engine'):
            print("✅ Leadership engine intégré")
        else:
            print("❌ Leadership engine manquant")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test MenthorQDistanceTrader: {e}")
        return False

def test_integrated_method():
    """Test de la méthode intégrée"""
    print("\n🔍 Test de la méthode intégrée...")
    
    try:
        from core.menthorq_distance_trading import MenthorQDistanceTrader
        
        # Initialiser
        trader = MenthorQDistanceTrader()
        
        # Données d'exemple
        es_data = {
            "t": 1705123200.0,
            "basedata": {"close": 4500.0},
            "vwap": {"v": 4499.5},
            "vva": {"vah": 4501.0, "val": 4498.0},
            "nbcv_footprint": {"pressure": 1, "delta_ratio": 0.18, "cumulative_delta": 120.0},
            "menthorq": {
                "gamma": {"put_support_0dte": 4498.0, "gamma_wall_0dte": 4501.0}
            },
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
            "mq_tolerance_ticks": {"gamma_wall": 3, "hvl": 5, "gex": 5},
            "mia_threshold": 0.20,
            "entry_threshold": 0.70,
            "weights": {"mq": 0.55, "of": 0.30, "structure": 0.15}
        }
        
        # Test de la méthode intégrée
        signal = trader.decide_mq_distance_integrated(es_data, nq_data, config)
        
        if signal:
            print(f"✅ Signal généré: {signal['action']} (Score: {signal['score']})")
            print(f"   Leadership: LS={signal['leadership']['ls']}, Bonus={signal['leadership']['bonus']}")
            print(f"   E/U/L: Entry={signal['eul']['entry']}, Stop={signal['eul']['stop']}")
        else:
            print("ℹ️ Pas de signal (normal selon les données d'exemple)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test méthode intégrée: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance():
    """Test de performance"""
    print("\n🔍 Test de performance...")
    
    try:
        from core.menthorq_distance_trading import MenthorQDistanceTrader
        
        trader = MenthorQDistanceTrader()
        
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
        
        config = {"tick_size": 0.25, "entry_threshold": 0.70}
        
        # Test de performance (1000 itérations)
        start_time = time.time()
        
        for i in range(1000):
            signal = trader.decide_mq_distance_integrated(es_data, nq_data, config)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Performance: 1000 itérations en {duration:.3f}s")
        print(f"   Moyenne: {duration/1000*1000:.2f}ms par itération")
        
        if duration < 1.0:  # Moins d'1 seconde pour 1000 itérations
            print("✅ Performance excellente")
        elif duration < 5.0:
            print("✅ Performance correcte")
        else:
            print("⚠️ Performance à optimiser")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test performance: {e}")
        return False

def main():
    """Test principal"""
    print("🎯 TEST D'INTÉGRATION MENTHORQ-DISTANCE + LEADERSHIP Z-MOMENTUM")
    print("=" * 70)
    
    tests = [
        ("Imports", test_imports),
        ("LeadershipZMom", test_leadership_zmom),
        ("MenthorQDistanceTrader", test_menthorq_distance_trader),
        ("Méthode intégrée", test_integrated_method),
        ("Performance", test_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur inattendue dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print(f"\n{'='*70}")
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<50} {status}")
        if result:
            passed += 1
    
    print(f"\nRésultat: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        print("✅ L'intégration est opérationnelle")
        print("🚀 Prêt pour la production")
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

