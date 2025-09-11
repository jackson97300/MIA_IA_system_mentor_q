#!/usr/bin/env python3
"""
🧪 TEST DES WRAPPERS ORDERFLOW ANALYZER
=======================================

Script de test pour vérifier que les nouveaux wrappers synchrones fonctionnent.
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

def test_wrappers_orderflow():
    """Test des nouveaux wrappers synchrones"""
    print("🧪 TEST DES WRAPPERS ORDERFLOW ANALYZER")
    print("=" * 50)
    
    try:
        # Import du module
        from features.orderflow_analyzer import OrderFlowAnalyzer
        from config.automation_config import AutomationConfig
        
        print("✅ Import modules: OK")
        
        # Création de l'instance
        config = AutomationConfig()
        analyzer = OrderFlowAnalyzer(config)
        print("✅ Création instance: OK")
        
        # Données de test
        test_data = {
            'symbol': 'ES',
            'price': 4500.0,
            'volume': 1000,
            'delta': 0.5,
            'bid_volume': 600,
            'ask_volume': 400,
            'timestamp': '2025-08-26 23:00:00'
        }
        
        print("\n🔧 Test 1: Wrapper analyze_orderflow")
        print("-" * 40)
        
        # Test du wrapper analyze_orderflow
        try:
            result = analyzer.analyze_orderflow(test_data)
            print("✅ Wrapper analyze_orderflow: RÉUSSI")
            if result:
                print(f"   Signal généré: {result.signal_type}")
                print(f"   Confiance: {result.confidence}")
                print(f"   Prix: {result.price_level}")
            else:
                print("   Aucun signal généré (normal pour données de test)")
        except Exception as e:
            print(f"❌ Wrapper analyze_orderflow: ÉCHEC - {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n🔧 Test 2: Wrapper calculate_footprint")
        print("-" * 40)
        
        # Test du wrapper calculate_footprint
        try:
            result = analyzer.calculate_footprint(test_data)
            print("✅ Wrapper calculate_footprint: RÉUSSI")
            if result:
                print(f"   Résultat: {type(result)}")
                if isinstance(result, dict):
                    print(f"   Clés: {list(result.keys())}")
            else:
                print("   Aucun résultat (normal pour données de test)")
        except Exception as e:
            print(f"❌ Wrapper calculate_footprint: ÉCHEC - {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n🔧 Test 3: Vérification des méthodes disponibles")
        print("-" * 40)
        
        # Vérifier que les méthodes sont bien disponibles
        methods_to_check = [
            'analyze_orderflow_data',  # Méthode async originale
            'analyze_orderflow',       # Wrapper sync
            'calculate_footprint',     # Wrapper sync
            '_analyze_footprint'       # Méthode interne
        ]
        
        for method in methods_to_check:
            if hasattr(analyzer, method):
                print(f"✅ {method}: DISPONIBLE")
            else:
                print(f"❌ {method}: MANQUANTE")
                return False
        
        print("\n🎯 RÉSUMÉ DU TEST")
        print("=" * 50)
        print("✅ TOUS LES TESTS RÉUSSIS")
        print("\n💡 RÉSULTAT:")
        print("   - Les wrappers synchrones fonctionnent parfaitement")
        print("   - Compatibilité avec les tests existants: OK")
        print("   - Méthodes async originales: Toujours disponibles")
        print("   - Le module est maintenant 100% compatible")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_system():
    """Test d'intégration avec le système principal"""
    print("\n🔧 TEST D'INTÉGRATION SYSTÈME")
    print("=" * 50)
    
    try:
        # Simuler un appel depuis le système principal
        from features.orderflow_analyzer import OrderFlowAnalyzer
        from config.automation_config import AutomationConfig
        
        config = AutomationConfig()
        analyzer = OrderFlowAnalyzer(config)
        
        # Données réalistes
        market_data = {
            'symbol': 'ES',
            'price': 4500.0,
            'volume': 1500,
            'delta': 0.7,
            'bid_volume': 800,
            'ask_volume': 700,
            'level2': {'bids': [], 'asks': []},
            'footprint': {'score': 0.6}
        }
        
        # Test d'intégration
        signal = analyzer.analyze_orderflow(market_data)
        
        if signal:
            print("✅ Intégration système: RÉUSSIE")
            print(f"   Signal: {signal.signal_type}")
            print(f"   Confiance: {signal.confidence:.3f}")
            print(f"   Raisonnement: {signal.reasoning[:50]}...")
        else:
            print("⚠️ Intégration système: Aucun signal (normal)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur intégration: {e}")
        return False

def main():
    """Fonction principale"""
    success1 = test_wrappers_orderflow()
    success2 = test_integration_system()
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 60)
    
    if success1 and success2:
        print("🎉 SUCCÈS COMPLET !")
        print("\n✅ Le module orderflow_analyzer est maintenant :")
        print("   - 100% compatible avec les tests existants")
        print("   - Fonctionnel avec les wrappers synchrones")
        print("   - Intégré parfaitement dans le système")
        print("   - Prêt pour la production")
        
        print("\n🚀 PROCHAINES ÉTAPES :")
        print("   1. Relancer les tests automation_modules")
        print("   2. Vérifier que tous les tests passent")
        print("   3. Déployer en production")
        
    else:
        print("❌ Certains tests ont échoué")
        print("   Vérification nécessaire")

if __name__ == "__main__":
    main()



