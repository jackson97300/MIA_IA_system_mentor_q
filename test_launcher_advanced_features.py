#!/usr/bin/env python3
"""
🧪 TEST LANCEUR AVEC ADVANCED FEATURES
=====================================

Test rapide pour vérifier que le lanceur exploite bien les Advanced Features.
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

def test_launcher_imports():
    """Test 1: Imports du lanceur"""
    print("🧪 Test 1: Imports lanceur...")
    try:
        from launch_24_7 import Launch24_7System
        print("✅ Import lanceur OK")
        return True
    except Exception as e:
        print(f"❌ Erreur import lanceur: {e}")
        return False

def test_launcher_initialization():
    """Test 2: Initialisation du lanceur"""
    print("🧪 Test 2: Initialisation lanceur...")
    try:
        from launch_24_7 import Launch24_7System
        
        # Créer le système
        system = Launch24_7System()
        
        # Vérifier que Advanced Features est initialisé
        if hasattr(system, 'advanced_features'):
            if system.advanced_features:
                print("✅ Advanced Features initialisé dans le lanceur")
                return True
            else:
                print("⚠️ Advanced Features non disponible dans le lanceur")
                return False
        else:
            print("❌ Advanced Features non initialisé dans le lanceur")
            return False
            
    except Exception as e:
        print(f"❌ Erreur initialisation lanceur: {e}")
        return False

def test_advanced_features_status():
    """Test 3: Statut Advanced Features"""
    print("🧪 Test 3: Statut Advanced Features...")
    try:
        from features.advanced import get_advanced_features_status
        
        status = get_advanced_features_status()
        
        print(f"✅ Statut Advanced Features:")
        print(f"   Version: {status['version']}")
        print(f"   Features disponibles: {status['successful_imports']}/{status['total_features']}")
        print(f"   Taux de succès: {status['success_rate']}")
        print(f"   Impact projeté: {status['projected_impact']}")
        
        return status['successful_imports'] > 0
        
    except Exception as e:
        print(f"❌ Erreur statut Advanced Features: {e}")
        return False

def main():
    """Lance tous les tests"""
    print("🚀 TEST LANCEUR AVEC ADVANCED FEATURES")
    print("=" * 50)
    
    tests = [
        ("Import lanceur", test_launcher_imports),
        ("Initialisation lanceur", test_launcher_initialization),
        ("Statut Advanced Features", test_advanced_features_status)
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
    print("📋 RÉSUMÉ DES TESTS LANCEUR:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 RÉSULTAT GLOBAL: {passed}/{len(results)} tests passés")
    
    if passed == len(results):
        print("🎉 SUCCÈS COMPLET!")
        print("• Lanceur mis à jour avec Advanced Features")
        print("• +7% win rate potentiel activé")
        print("• Système prêt pour le trading optimisé")
    else:
        print("⚠️ Certains tests ont échoué")
        print("• Vérifiez les dépendances")
        print("• Consultez les logs pour plus de détails")

if __name__ == "__main__":
    main()


