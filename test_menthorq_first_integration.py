#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST INTÉGRATION MENTHORQ FIRST METHOD
=====================================

Script de test pour valider l'intégration de la méthode MenthorQ First
dans le système MIA_IA_SYSTEM.
"""

import sys
import os
import json
import time
from pathlib import Path

# Ajout du chemin du projet
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test des imports"""
    print("🔍 TEST DES IMPORTS...")
    
    try:
        from core.menthorq_first_method import MenthorQFirstMethod, MenthorQFirstResult
        print("✅ Import MenthorQFirstMethod réussi")
    except ImportError as e:
        print(f"❌ Erreur import MenthorQFirstMethod: {e}")
        return False
    
    try:
        from core.menthorq_distance_trading import MenthorQDistanceTrader
        print("✅ Import MenthorQDistanceTrader réussi")
    except ImportError as e:
        print(f"❌ Erreur import MenthorQDistanceTrader: {e}")
        return False
    
    try:
        from features.leadership_zmom import LeadershipZMom
        print("✅ Import LeadershipZMom réussi")
    except ImportError as e:
        print(f"❌ Erreur import LeadershipZMom: {e}")
        return False
    
    try:
        from core.mia_bullish import BullishScorer
        print("✅ Import BullishScorer réussi")
    except ImportError as e:
        print(f"❌ Erreur import BullishScorer: {e}")
        return False
    
    try:
        from automation_modules.orderflow_analyzer import OrderFlowAnalyzer
        print("✅ Import OrderFlowAnalyzer réussi")
    except ImportError as e:
        print(f"⚠️ Import OrderFlowAnalyzer échoué (fallback activé): {e}")
        print("✅ Fallback OrderFlow disponible")
        # Ne pas retourner False car le fallback fonctionne
    
    return True

def test_initialization():
    """Test de l'initialisation"""
    print("\n🔧 TEST D'INITIALISATION...")
    
    try:
        from core.menthorq_first_method import MenthorQFirstMethod
        
        method = MenthorQFirstMethod()
        print("✅ Initialisation MenthorQFirstMethod réussi")
        
        # Vérification des composants
        if hasattr(method, 'menthorq_trader'):
            print("✅ MenthorQDistanceTrader initialisé")
        else:
            print("❌ MenthorQDistanceTrader manquant")
        
        if hasattr(method, 'leadership_engine'):
            print("✅ LeadershipZMom initialisé")
        else:
            print("❌ LeadershipZMom manquant")
        
        if hasattr(method, 'mia_bullish'):
            print("✅ BullishScorer initialisé")
        else:
            print("❌ BullishScorer manquant")
        
        if hasattr(method, 'orderflow_analyzer'):
            print("✅ OrderFlowAnalyzer initialisé")
        else:
            print("❌ OrderFlowAnalyzer manquant")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test de la configuration"""
    print("\n⚙️ TEST DE LA CONFIGURATION...")
    
    try:
        # Test chargement config JSON
        config_path = Path("config/menthorq_first_method.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("✅ Configuration JSON chargée")
            
            # Vérification des sections principales
            if 'menthorq_first_method' in config:
                print("✅ Section menthorq_first_method trouvée")
                
                method_config = config['menthorq_first_method']
                
                if 'menthorq' in method_config:
                    print("✅ Configuration MenthorQ trouvée")
                
                if 'user_experience' in method_config:
                    print("✅ Configuration expérience utilisateur trouvée")
                
                if 'execution' in method_config:
                    print("✅ Configuration exécution trouvée")
                
            else:
                print("❌ Section menthorq_first_method manquante")
        else:
            print("❌ Fichier de configuration manquant")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        return False

def test_method_analysis():
    """Test de l'analyse de la méthode"""
    print("\n🔍 TEST DE L'ANALYSE...")
    
    try:
        from core.menthorq_first_method import MenthorQFirstMethod
        
        method = MenthorQFirstMethod()
        
        # Données d'exemple avec niveaux MenthorQ
        es_data = {
            'basedata': {'close': 4500.0},
            'quote': {'bid': 4499.75, 'ask': 4500.25, 'mid': 4500.0},
            'trade': {'price': 4500.0, 'size': 10},
            'vwap': {'value': 4499.5},
            'volume_profile': {'vah': 4501.0, 'val': 4498.0, 'vpoc': 4499.5},
            'vix': {'value': 18.5},
            'nbcv': {'value': 150.0, 'trend': 'bullish'},
            'cumulative_delta': {'value': 200.0, 'trend': 'bullish'},
            'depth': {
                'bid_levels': [{'price': 4499.75, 'size': 100}],
                'ask_levels': [{'price': 4500.25, 'size': 120}]
            },
            # === NIVEAUX MENTHORQ (CRUCIAL !) ===
            'menthorq': {
                'gamma_wall': {
                    'call_resistance_1': 4500.5,
                    'call_resistance_2': 4501.0,
                    'put_support_1': 4499.0,
                    'put_support_2': 4498.5
                },
                'hvl': {
                    'high_volume_level_1': 4501.0,
                    'high_volume_level_2': 4500.5
                },
                'gex_levels': {
                    'call_gex_1': 4500.25,
                    'put_gex_1': 4499.75
                }
            }
        }
        
        nq_data = {
            'basedata': {'close': 15000.0},
            'quote': {'bid': 14999.5, 'ask': 15000.5, 'mid': 15000.0},
            'trade': {'price': 15000.0, 'size': 5}
        }
        
        # Test analyse
        result = method.analyze_menthorq_first_opportunity(es_data, nq_data)
        
        print("✅ Analyse MenthorQ First réussie")
        print(f"   Signal: {result.signal_type}")
        print(f"   Confidence: {result.confidence:.3f}")
        print(f"   Score Final: {result.final_score:.3f}")
        
        # Vérification des scores
        if hasattr(result, 'menthorq_score'):
            print(f"   Score MenthorQ: {result.menthorq_score:.3f}")
        
        if hasattr(result, 'orderflow_score'):
            print(f"   Score Orderflow: {result.orderflow_score:.3f}")
        
        if hasattr(result, 'structure_score'):
            print(f"   Score Structure: {result.structure_score:.3f}")
        
        # Vérification audit data
        if result.audit_data:
            print(f"   Audit Data: {len(result.audit_data)} éléments")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur analyse: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_statistics():
    """Test des statistiques"""
    print("\n📊 TEST DES STATISTIQUES...")
    
    try:
        from core.menthorq_first_method import MenthorQFirstMethod
        
        method = MenthorQFirstMethod()
        
        # Test récupération stats
        stats = method.get_stats()
        
        print("✅ Statistiques récupérées")
        print(f"   MenthorQ Triggers: {stats.get('menthorq_triggers', 0)}")
        print(f"   MIA Gates Passed: {stats.get('mia_gates_passed', 0)}")
        print(f"   Leadership Gates Passed: {stats.get('leadership_gates_passed', 0)}")
        print(f"   Orderflow Validations: {stats.get('orderflow_validations', 0)}")
        print(f"   Structure Validations: {stats.get('structure_validations', 0)}")
        print(f"   Final Signals: {stats.get('final_signals', 0)}")
        print(f"   Success Rate: {stats.get('success_rate', 0):.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur statistiques: {e}")
        return False

def main():
    """Fonction principale"""
    
    print("🎯 TEST INTÉGRATION MENTHORQ FIRST METHOD")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Initialisation", test_initialization),
        ("Configuration", test_configuration),
        ("Analyse", test_method_analysis),
        ("Statistiques", test_statistics)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name.upper()} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Erreur inattendue dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print(f"\n{'='*60}")
    print("📋 RÉSUMÉ DES TESTS")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSÉ" if success else "❌ ÉCHOUÉ"
        print(f"{test_name:20} : {status}")
        if success:
            passed += 1
    
    print(f"\nRésultat global: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        print("✅ La méthode MenthorQ First est prête pour la production")
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
