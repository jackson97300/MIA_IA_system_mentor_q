"""
Test du système d'intégrité des modules features
===============================================

Script de validation complète du monitoring d'intégrité.
"""

import time
import json
from features import (
    start_integrity_monitoring, 
    stop_integrity_monitoring, 
    get_integrity_status,
    get_features_status
)

def test_integrity_system():
    """Test complet du système d'intégrité"""
    print("🔍 TEST SYSTÈME INTÉGRITÉ FEATURES")
    print("=" * 50)
    
    # 1. Statut initial
    print("1. Statut initial des modules...")
    initial_status = get_features_status()
    print(f"   Modules disponibles: {initial_status['summary']['available_modules']}/{initial_status['summary']['total_modules']}")
    
    # 2. Démarrer le monitoring
    print("\n2. Démarrage monitoring d'intégrité...")
    start_success = start_integrity_monitoring()
    print(f"   Démarrage: {'✅' if start_success else '❌'}")
    
    if not start_success:
        print("❌ Impossible de démarrer le monitoring")
        return False
    
    # 3. Attendre les premières vérifications
    print("\n3. Attente des premières vérifications (8 secondes)...")
    time.sleep(8)
    
    # 4. Vérifier le statut d'intégrité
    print("\n4. Statut d'intégrité après vérifications...")
    integrity_status = get_integrity_status()
    
    if 'error' in integrity_status:
        print(f"   ❌ Erreur: {integrity_status['error']}")
        return False
    
    print(f"   Monitoring actif: {'✅' if integrity_status.get('monitoring_active') else '❌'}")
    
    # 5. Résumé de santé
    health_summary = integrity_status.get('health_summary', {})
    print(f"\n5. Résumé de santé:")
    print(f"   Santé globale: {health_summary.get('overall_health_percentage', 0):.1f}%")
    print(f"   Modules sains: {health_summary.get('healthy_modules', 0)}")
    print(f"   Modules dégradés: {health_summary.get('degraded_modules', 0)}")
    print(f"   Modules défaillants: {health_summary.get('failing_modules', 0)}")
    print(f"   Modules critiques: {health_summary.get('critical_modules', 0)}")
    
    # 6. Détail par module
    print(f"\n6. Détail par module:")
    module_health = integrity_status.get('module_health', {})
    
    for module_name, health in module_health.items():
        status_icon = {
            'HEALTHY': '✅',
            'DEGRADED': '⚠️',
            'FAILING': '❌',
            'CRITICAL': '🚨',
            'UNKNOWN': '❓'
        }.get(health.get('health_status', 'UNKNOWN'), '❓')
        
        success_rate = health.get('success_rate', 0)
        response_time = health.get('average_response_time_ms', 0)
        
        print(f"   {status_icon} {module_name}: {success_rate:.1%} succès, {response_time:.1f}ms")
    
    # 7. Vérification des seuils
    print(f"\n7. Vérification des seuils:")
    healthy_count = health_summary.get('healthy_modules', 0)
    total_count = health_summary.get('total_modules', 0)
    
    if total_count > 0:
        health_percentage = (healthy_count / total_count) * 100
        if health_percentage >= 80:
            print(f"   ✅ Excellent: {health_percentage:.1f}% de modules sains")
        elif health_percentage >= 60:
            print(f"   ⚠️ Acceptable: {health_percentage:.1f}% de modules sains")
        else:
            print(f"   ❌ Problématique: {health_percentage:.1f}% de modules sains")
    
    # 8. Arrêter le monitoring
    print(f"\n8. Arrêt du monitoring...")
    stop_success = stop_integrity_monitoring()
    print(f"   Arrêt: {'✅' if stop_success else '❌'}")
    
    # 9. Résultat final
    print(f"\n9. Résultat final:")
    if health_summary.get('overall_health_percentage', 0) >= 60:
        print("   ✅ Système d'intégrité fonctionnel")
        return True
    else:
        print("   ❌ Système d'intégrité nécessite des améliorations")
        return False

if __name__ == "__main__":
    success = test_integrity_system()
    print(f"\n{'='*50}")
    print(f"RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")


