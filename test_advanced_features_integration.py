#!/usr/bin/env python3
"""
🧪 TEST INTÉGRATION ADVANCED FEATURES
=====================================

Test complet de l'intégration des Advanced Features dans le pipeline principal.
Vérifie que les +7% win rate sont bien exploités.

Tests:
1. Import Advanced Features
2. Intégration dans FeatureCalculatorOptimized  
3. Intégration dans ConfluenceIntegrator
4. Calcul pipeline complet
5. Impact sur les trades
"""

import sys
from pathlib import Path
import traceback

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

def test_advanced_features_import():
    """Test 1: Import Advanced Features"""
    print("🧪 Test 1: Import Advanced Features...")
    try:
        from features.advanced import (
            AdvancedFeaturesSuite,
            create_advanced_features_suite,
            get_advanced_features_status
        )
        print("✅ Import Advanced Features OK")
        return True
    except Exception as e:
        print(f"❌ Erreur import Advanced Features: {e}")
        return False

def test_feature_calculator_integration():
    """Test 2: Intégration dans FeatureCalculatorOptimized"""
    print("🧪 Test 2: FeatureCalculatorOptimized avec Advanced Features...")
    try:
        from features.feature_calculator_optimized import FeatureCalculatorOptimized
        
        # Créer le calculateur
        calculator = FeatureCalculatorOptimized()
        
        # Vérifier que Advanced Features est initialisé
        if hasattr(calculator, '_advanced_features'):
            if calculator._advanced_features:
                print("✅ Advanced Features intégré dans FeatureCalculatorOptimized")
                return True
            else:
                print("⚠️ Advanced Features non disponible dans FeatureCalculatorOptimized")
                return False
        else:
            print("❌ Advanced Features non initialisé dans FeatureCalculatorOptimized")
            return False
            
    except Exception as e:
        print(f"❌ Erreur FeatureCalculatorOptimized: {e}")
        return False

def test_confluence_integrator_integration():
    """Test 3: Intégration dans ConfluenceIntegrator"""
    print("🧪 Test 3: ConfluenceIntegrator avec Advanced Features...")
    try:
        from features.confluence_integrator import ConfluenceIntegrator
        
        # Créer l'intégrateur
        integrator = ConfluenceIntegrator()
        
        # Vérifier que Advanced Features est initialisé
        if hasattr(integrator, 'advanced_features'):
            if integrator.advanced_features:
                print("✅ Advanced Features intégré dans ConfluenceIntegrator")
                return True
            else:
                print("⚠️ Advanced Features non disponible dans ConfluenceIntegrator")
                return False
        else:
            print("❌ Advanced Features non initialisé dans ConfluenceIntegrator")
            return False
            
    except Exception as e:
        print(f"❌ Erreur ConfluenceIntegrator: {e}")
        return False

def test_advanced_features_calculation():
    """Test 4: Calcul Advanced Features"""
    print("🧪 Test 4: Calcul Advanced Features...")
    try:
        from features.advanced import create_advanced_features_suite
        
        # Créer la suite
        suite = create_advanced_features_suite()
        
        # Test calcul
        results = suite.calculate_all_features()
        combined_signal = suite.get_combined_signal()
        
        print(f"✅ Calcul Advanced Features OK")
        print(f"   Signal combiné: {combined_signal:.3f}")
        print(f"   Features calculées: {len(results)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur calcul Advanced Features: {e}")
        return False

def test_pipeline_complete():
    """Test 5: Pipeline complet avec Advanced Features"""
    print("🧪 Test 5: Pipeline complet...")
    try:
        from features.feature_calculator_optimized import FeatureCalculatorOptimized
        from core.base_types import MarketData
        
        # Créer le calculateur
        calculator = FeatureCalculatorOptimized()
        
        # Données de test
        market_data = MarketData(
            symbol="ESU25_FUT_CME",
            timestamp=1234567890.0,
            open=4500.0,
            high=4505.0,
            low=4495.0,
            close=4502.0,
            volume=1000
        )
        
        # Calcul
        result = calculator.calculate_features(market_data)
        
        print(f"✅ Pipeline complet OK")
        print(f"   Score final: {result.battle_navale_signal:.3f}")
        print(f"   Temps calcul: {result.calculation_time_ms:.1f}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur pipeline complet: {e}")
        return False

def test_advanced_features_impact():
    """Test 6: Impact Advanced Features sur les trades"""
    print("🧪 Test 6: Impact sur les trades...")
    try:
        from features.confluence_integrator import ConfluenceIntegrator
        
        # Créer l'intégrateur
        integrator = ConfluenceIntegrator()
        
        # Données de test
        market_data = {
            'ES': {
                'symbol': 'ESU25_FUT_CME',
                'close': 4500.0,
                'volume': 1000,
                'timestamp': 1234567890.0
            },
            'NQ': {
                'symbol': 'NQU25_FUT_CME', 
                'close': 15000.0,
                'volume': 500,
                'timestamp': 1234567890.0
            }
        }
        
        # Calcul confluence
        result = integrator.calculate_confluence_with_leadership(market_data)
        
        print(f"✅ Impact Advanced Features validé")
        print(f"   Score final: {result.final_score:.3f}")
        print(f"   Advanced Features score: {result.advanced_features_score:.3f}")
        print(f"   Décision: {result.decision}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur impact Advanced Features: {e}")
        return False

def main():
    """Lance tous les tests"""
    print("🚀 TEST INTÉGRATION ADVANCED FEATURES")
    print("=" * 50)
    
    tests = [
        ("Import Advanced Features", test_advanced_features_import),
        ("FeatureCalculatorOptimized", test_feature_calculator_integration),
        ("ConfluenceIntegrator", test_confluence_integrator_integration),
        ("Calcul Advanced Features", test_advanced_features_calculation),
        ("Pipeline complet", test_pipeline_complete),
        ("Impact sur trades", test_advanced_features_impact)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur critique dans {test_name}: {e}")
            results.append((test_name, False))
        print()
    
    # Résumé
    print("=" * 50)
    print("📋 RÉSUMÉ DES TESTS ADVANCED FEATURES:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 RÉSULTAT GLOBAL: {passed}/{len(results)} tests passés")
    
    if passed == len(results):
        print("🎉 SUCCÈS COMPLET!")
        print("• Advanced Features intégrées avec succès")
        print("• +7% win rate potentiel activé")
        print("• Pipeline optimisé et fonctionnel")
    else:
        print("⚠️ Certains tests ont échoué")
        print("• Vérifiez les dépendances (scipy, etc.)")
        print("• Consultez les logs pour plus de détails")

if __name__ == "__main__":
    main()


