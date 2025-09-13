#!/usr/bin/env python3
"""
🧪 TEST MIGRATION ENUMS - MIA_IA_SYSTEM
=======================================

Script de test pour vérifier que la migration des enums centralisés
fonctionne correctement sans casser le système existant.

TESTS EFFECTUÉS :
1. Import du module centralisé core.enums
2. Vérification des enums dans les fichiers migrés
3. Test de compatibilité avec les anciens imports
4. Validation des valeurs et méthodes
"""

import sys
from pathlib import Path
import traceback

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

def test_centralized_enums():
    """Test du module centralisé core.enums"""
    print("🔧 Test du module centralisé core.enums...")
    
    try:
        from core.enums import (
            AlertLevel, AlertSeverity, AlertCategory,
            PerformanceMetric, PerformancePeriod,
            ComponentStatus, MetricType
        )
        
        # Test AlertLevel
        assert AlertLevel.INFO.value == "info"
        assert AlertLevel.WARNING.value == "warning"
        assert AlertLevel.CRITICAL.value == "critical"
        assert AlertLevel.EMERGENCY.value == "emergency"
        
        # Test AlertSeverity
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.ERROR.value == "error"
        assert AlertSeverity.CRITICAL.value == "critical"
        
        # Test des méthodes utilitaires
        assert AlertLevel.from_string("warning") == AlertLevel.WARNING
        assert AlertSeverity.from_string("critical") == AlertSeverity.CRITICAL
        
        print("✅ Module centralisé core.enums : OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur module centralisé : {e}")
        traceback.print_exc()
        return False

def test_migrated_files():
    """Test des fichiers migrés"""
    print("\n🔄 Test des fichiers migrés...")
    
    test_files = [
        "core.menthorq_staleness_monitor",
        "monitoring.performance_tracker", 
        "scripts.analyze_performance",
        "performance.automation_metrics",
        "monitoring.live_monitor"
    ]
    
    success_count = 0
    
    for module_name in test_files:
        try:
            print(f"  📁 Test {module_name}...")
            
            # Import du module
            module = __import__(module_name, fromlist=['AlertLevel', 'AlertSeverity'])
            
            # Test des enums
            if hasattr(module, 'AlertLevel'):
                alert_level = module.AlertLevel
                assert alert_level.INFO.value == "info"
                assert alert_level.CRITICAL.value == "critical"
                print(f"    ✅ AlertLevel : OK")
            
            if hasattr(module, 'AlertSeverity'):
                alert_severity = module.AlertSeverity
                assert alert_severity.INFO.value == "info"
                assert alert_severity.CRITICAL.value == "critical"
                print(f"    ✅ AlertSeverity : OK")
            
            success_count += 1
            
        except Exception as e:
            print(f"    ❌ Erreur {module_name} : {e}")
            traceback.print_exc()
    
    print(f"\n📊 Résultat : {success_count}/{len(test_files)} fichiers migrés OK")
    return success_count == len(test_files)

def test_enum_usage():
    """Test d'utilisation des enums dans le contexte réel"""
    print("\n🎯 Test d'utilisation des enums...")
    
    try:
        # Test avec core.menthorq_staleness_monitor
        from core.menthorq_staleness_monitor import AlertLevel
        
        # Simulation d'utilisation
        alert_level = AlertLevel.CRITICAL
        assert alert_level.value == "critical"
        
        # Test avec monitoring.performance_tracker
        from monitoring.performance_tracker import AlertLevel as PTAlertLevel
        assert PTAlertLevel.WARNING.value == "warning"
        
        # Test avec performance.automation_metrics
        from performance.automation_metrics import AlertSeverity
        assert AlertSeverity.EMERGENCY.value == "emergency"
        
        print("✅ Utilisation des enums : OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur utilisation enums : {e}")
        traceback.print_exc()
        return False

def test_enum_compatibility():
    """Test de compatibilité avec les anciens imports"""
    print("\n🔄 Test de compatibilité...")
    
    try:
        # Test que les anciens imports fonctionnent toujours
        from core.menthorq_staleness_monitor import AlertLevel as MQAlertLevel
        from monitoring.performance_tracker import AlertLevel as PTAlertLevel
        from scripts.analyze_performance import AlertLevel as SAAlertLevel
        
        # Vérification que tous pointent vers les mêmes valeurs
        assert MQAlertLevel.INFO.value == PTAlertLevel.INFO.value
        assert PTAlertLevel.INFO.value == SAAlertLevel.INFO.value
        
        # Test des méthodes de conversion
        from core.enums import AlertLevel
        assert AlertLevel.from_string("warning") == AlertLevel.WARNING
        assert AlertLevel.from_string("invalid") == AlertLevel.INFO  # Fallback
        
        print("✅ Compatibilité : OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur compatibilité : {e}")
        traceback.print_exc()
        return False

def test_enum_serialization():
    """Test de sérialisation/désérialisation"""
    print("\n💾 Test de sérialisation...")
    
    try:
        from core.enums import AlertLevel, serialize_enum, deserialize_enum
        
        # Test sérialisation
        alert = AlertLevel.CRITICAL
        serialized = serialize_enum(alert)
        
        assert serialized['enum_type'] == 'AlertLevel'
        assert serialized['value'] == 'critical'
        assert serialized['name'] == 'CRITICAL'
        
        # Test désérialisation
        deserialized = deserialize_enum(serialized)
        assert deserialized == AlertLevel.CRITICAL
        
        print("✅ Sérialisation : OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur sérialisation : {e}")
        traceback.print_exc()
        return False

def main():
    """Fonction principale de test"""
    print("🧪 DÉMARRAGE DES TESTS DE MIGRATION ENUMS")
    print("=" * 50)
    
    tests = [
        ("Module centralisé", test_centralized_enums),
        ("Fichiers migrés", test_migrated_files),
        ("Utilisation enums", test_enum_usage),
        ("Compatibilité", test_enum_compatibility),
        ("Sérialisation", test_enum_serialization)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur critique dans {test_name} : {e}")
            results.append((test_name, False))
    
    # Résumé final
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 RÉSULTAT FINAL : {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 MIGRATION RÉUSSIE ! Tous les tests passent.")
        print("✅ Le système est prêt pour la phase de nettoyage.")
        return True
    else:
        print("⚠️  MIGRATION PARTIELLE. Vérifiez les erreurs ci-dessus.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


