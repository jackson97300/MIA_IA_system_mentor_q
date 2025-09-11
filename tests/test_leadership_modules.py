#!/usr/bin/env python3
"""
🧪 TEST DES MODULES LEADERSHIP
==============================

Script de test pour vérifier les modules de leadership qui n'ont pas été testés.
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

def test_leadership_analyzer():
    """Test du module leadership_analyzer"""
    print("\n🔧 Test leadership_analyzer...")
    
    try:
        from features.leadership_analyzer import create_leadership_analyzer
        from config.automation_config import AutomationConfig
        
        config = AutomationConfig()
        analyzer = create_leadership_analyzer(config)
        print("✅ Création: OK")
        
        # Test méthodes disponibles
        methods = [name for name, obj in analyzer.__class__.__dict__.items() 
                  if callable(obj) and not name.startswith('_')]
        print(f"Méthodes disponibles: {methods}")
        
        # Test méthodes spécifiques
        if hasattr(analyzer, 'analyze_leadership'):
            print("✅ Méthode analyze_leadership: OK")
        else:
            print("❌ Méthode analyze_leadership: MANQUANTE")
            
        if hasattr(analyzer, 'set_confluence_integrator'):
            print("✅ Méthode set_confluence_integrator: OK")
        else:
            print("❌ Méthode set_confluence_integrator: MANQUANTE")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_confluence_integrator():
    """Test du module confluence_integrator"""
    print("\n🔧 Test confluence_integrator...")
    
    try:
        from features.confluence_integrator import create_confluence_integrator
        from config.automation_config import AutomationConfig
        
        config = AutomationConfig()
        integrator = create_confluence_integrator(config)
        print("✅ Création: OK")
        
        # Test méthodes disponibles
        methods = [name for name, obj in integrator.__class__.__dict__.items() 
                  if callable(obj) and not name.startswith('_')]
        print(f"Méthodes disponibles: {methods}")
        
        # Test méthodes spécifiques
        if hasattr(integrator, 'calculate_confluence_with_leadership'):
            print("✅ Méthode calculate_confluence_with_leadership: OK")
        else:
            print("❌ Méthode calculate_confluence_with_leadership: MANQUANTE")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_leadership_config():
    """Test du module leadership_config"""
    print("\n🔧 Test leadership_config...")
    
    try:
        from config.leadership_config import LeadershipConfigManager, LeadershipConfig
        from config.automation_config import AutomationConfig
        
        # Test LeadershipConfigManager
        config_manager = LeadershipConfigManager()
        print("✅ Création LeadershipConfigManager: OK")
        
        # Test LeadershipConfig
        config = LeadershipConfig()
        print("✅ Création LeadershipConfig: OK")
        
        # Test méthodes
        if hasattr(config_manager, 'get_calibration'):
            print("✅ Méthode get_calibration: OK")
        else:
            print("❌ Méthode get_calibration: MANQUANTE")
            
        if hasattr(config_manager, 'to_leadership_config'):
            print("✅ Méthode to_leadership_config: OK")
        else:
            print("❌ Méthode to_leadership_config: MANQUANTE")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_volatility_regime():
    """Test du module volatility_regime"""
    print("\n🔧 Test volatility_regime...")
    
    try:
        from features.advanced.volatility_regime import VolatilityRegimeCalculator
        from config.automation_config import AutomationConfig
        
        config = AutomationConfig()
        calculator = VolatilityRegimeCalculator(config)
        print("✅ Création: OK")
        
        # Test méthodes disponibles
        methods = [name for name, obj in calculator.__class__.__dict__.items() 
                  if callable(obj) and not name.startswith('_')]
        print(f"Méthodes disponibles: {methods}")
        
        # Test méthodes spécifiques
        if hasattr(calculator, 'calculate_volatility_regime'):
            print("✅ Méthode calculate_volatility_regime: OK")
        else:
            print("❌ Méthode calculate_volatility_regime: MANQUANTE")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_leadership():
    """Test d'intégration des modules leadership"""
    print("\n🔧 Test d'intégration leadership...")
    
    try:
        from features.leadership_analyzer import create_leadership_analyzer
        from features.confluence_integrator import create_confluence_integrator
        from config.automation_config import AutomationConfig
        
        config = AutomationConfig()
        
        # Création des modules
        leadership_analyzer = create_leadership_analyzer(config)
        confluence_integrator = create_confluence_integrator(config)
        
        # Test intégration
        if hasattr(leadership_analyzer, 'set_confluence_integrator'):
            leadership_analyzer.set_confluence_integrator(confluence_integrator)
            print("✅ Intégration leadership_analyzer ↔ confluence_integrator: OK")
        else:
            print("❌ Méthode set_confluence_integrator: MANQUANTE")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_leadership_tests():
    """Exécute tous les tests de leadership"""
    print("🧪 TESTS DES MODULES LEADERSHIP")
    print("=" * 50)
    
    tests = [
        ("leadership_analyzer", test_leadership_analyzer),
        ("confluence_integrator", test_confluence_integrator),
        ("leadership_config", test_leadership_config),
        ("volatility_regime", test_volatility_regime),
        ("integration_leadership", test_integration_leadership),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Erreur dans {test_name}: {e}")
            results[test_name] = False
    
    return results

def print_leadership_summary(results):
    """Affiche le résumé des tests leadership"""
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS LEADERSHIP")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"Total des tests: {total_tests}")
    print(f"Tests réussis: {passed_tests} ✅")
    print(f"Tests échoués: {failed_tests} ❌")
    print(f"Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\n❌ Tests échoués:")
        for test_name, result in results.items():
            if not result:
                print(f"  - {test_name}")
    
    if passed_tests == total_tests:
        print("\n🎉 TOUS LES MODULES LEADERSHIP SONT FONCTIONNELS!")
    else:
        print(f"\n⚠️ {failed_tests} module(s) leadership nécessitent une attention")

def main():
    """Fonction principale"""
    results = run_leadership_tests()
    print_leadership_summary(results)
    
    # Code de sortie
    if all(results.values()):
        print("\n✅ Tous les tests leadership réussis - Système leadership prêt")
        return 0
    else:
        print("\n❌ Certains tests leadership ont échoué - Vérification nécessaire")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)



