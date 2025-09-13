#!/usr/bin/env python3
"""
Test du dashboard de monitoring des scores avec traces par composant
"""

import sys
from pathlib import Path
import time
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).parent))

from core.score_monitoring_dashboard import (
    ScoreMonitoringDashboard, 
    DashboardAlert, 
    AlertType,
    create_score_monitoring_dashboard
)

# Mock des composants pour le test
class MockScoreResult:
    """Mock d'un résultat de score pour les tests"""
    def __init__(self, final_score: float, sentiment: str, components: list, calculation_time_ms: float = 50.0):
        self.final_score = final_score
        self.sentiment = sentiment
        self.components = components
        self.calculation_time_ms = calculation_time_ms
        self.timestamp = datetime.now(timezone.utc)

class MockComponentTrace:
    """Mock d'un composant de score pour les tests"""
    def __init__(self, name: str, score: float, weight: float, data_quality: str = "GOOD"):
        self.name = name
        self.score = score
        self.weight = weight
        self.data_quality = data_quality

def test_score_monitoring_dashboard():
    """Test du dashboard de monitoring des scores"""
    print("🚀 === TEST DASHBOARD MONITORING SCORES ===\n")
    
    # Test 1: Création du dashboard
    print("🎯 Test 1: Création du dashboard")
    dashboard = create_score_monitoring_dashboard(max_history_size=100)
    print(f"✅ Dashboard créé: {dashboard}")
    
    # Test 2: Ajout de résultats de scores simulés
    print("\n🎯 Test 2: Ajout de résultats de scores simulés")
    
    # Créer des composants simulés
    components_1 = [
        MockComponentTrace("MenthorQ", 0.75, 0.40, "GOOD"),
        MockComponentTrace("Battle Navale", 0.65, 0.35, "GOOD"),
        MockComponentTrace("VIX Regime", 0.80, 0.25, "GOOD")
    ]
    
    components_2 = [
        MockComponentTrace("MenthorQ", 0.45, 0.40, "FAIR"),
        MockComponentTrace("Battle Navale", 0.35, 0.35, "POOR"),
        MockComponentTrace("VIX Regime", 0.60, 0.25, "GOOD")
    ]
    
    components_3 = [
        MockComponentTrace("MenthorQ", 0.85, 0.40, "GOOD"),
        MockComponentTrace("Battle Navale", 0.90, 0.35, "GOOD"),
        MockComponentTrace("VIX Regime", 0.70, 0.25, "GOOD")
    ]
    
    # Créer des résultats de scores
    score_results = [
        MockScoreResult(0.73, "BULLISH", components_1, 45.0),
        MockScoreResult(0.45, "BEARISH", components_2, 55.0),
        MockScoreResult(0.82, "BULLISH", components_3, 40.0),
        MockScoreResult(0.15, "BEARISH", components_2, 60.0),  # Score très faible pour déclencher alerte
        MockScoreResult(0.95, "BULLISH", components_3, 35.0),  # Score très élevé pour déclencher alerte
    ]
    
    # Ajouter les résultats au dashboard
    for i, result in enumerate(score_results):
        dashboard.add_score_result(result)
        print(f"   Score {i+1} ajouté: {result.final_score:.3f} ({result.sentiment})")
        time.sleep(0.1)  # Petite pause pour simuler le temps
    
    print(f"✅ {len(score_results)} résultats de scores ajoutés")
    
    # Test 3: Démarrage du monitoring automatique
    print("\n🎯 Test 3: Démarrage du monitoring automatique")
    success = dashboard.start_monitoring(check_interval_seconds=2)
    print(f"✅ Monitoring démarré: {success}")
    
    if not success:
        print("❌ Impossible de démarrer le monitoring - arrêt du test")
        return
    
    # Test 4: Surveillance pendant quelques cycles
    print("\n🎯 Test 4: Surveillance pendant 10 secondes")
    print("   (Le monitoring va analyser les tendances et détecter les anomalies)")
    
    for i in range(5):  # 5 cycles de 2 secondes = 10 secondes
        time.sleep(2)
        summary = dashboard.get_dashboard_summary()
        print(f"   Cycle {i+1}: {summary['total_calculations']} calculs, {summary['alerts_generated']} alertes")
    
    # Test 5: Résumé du dashboard
    print("\n🎯 Test 5: Résumé du dashboard")
    summary = dashboard.get_dashboard_summary()
    print(f"✅ Résumé du dashboard:")
    print(f"   - Statut: {summary['status']}")
    print(f"   - Total calculs: {summary['total_calculations']}")
    print(f"   - Temps moyen: {summary['avg_calculation_time_ms']}ms")
    print(f"   - Alertes générées: {summary['alerts_generated']}")
    print(f"   - Problèmes qualité: {summary['data_quality_issues']}")
    print(f"   - Échecs composants: {summary['component_failures']}")
    print(f"   - Uptime: {summary['uptime_seconds']}s")
    print(f"   - Composants surveillés: {summary['components_monitored']}")
    
    # Test 6: Performance des composants
    print("\n🎯 Test 6: Performance des composants")
    component_perf = dashboard.get_component_performance()
    print(f"✅ Performance des composants:")
    for component_name, perf in component_perf.items():
        print(f"   - {component_name}:")
        print(f"     * Score moyen: {perf['avg_score']}")
        print(f"     * Écart type: {perf['score_std']}")
        print(f"     * Tendance: {perf['trend']}")
        print(f"     * Qualité données: {perf['data_quality']}")
    
    # Test 7: Alertes récentes
    print("\n🎯 Test 7: Alertes récentes")
    recent_alerts = dashboard.get_recent_alerts(10)
    print(f"✅ Alertes récentes ({len(recent_alerts)}):")
    for alert in recent_alerts:
        print(f"   - {alert['timestamp']}: {alert['severity'].upper()} - {alert['message']}")
        if alert['component']:
            print(f"     Composant: {alert['component']}")
    
    # Test 8: Tendances des scores
    print("\n🎯 Test 8: Tendances des scores")
    trends = dashboard.get_score_trends(hours=1)
    if 'error' not in trends:
        print(f"✅ Tendances des scores:")
        print(f"   - Période: {trends['period_hours']}h")
        print(f"   - Nombre de scores: {trends['score_count']}")
        print(f"   - Score moyen: {trends['avg_score']}")
        print(f"   - Score min/max: {trends['min_score']}/{trends['max_score']}")
        print(f"   - Écart type: {trends['score_std']}")
        print(f"   - Tendance: {trends['trend']}")
        print(f"   - Distribution sentiments: {trends['sentiment_distribution']}")
    else:
        print(f"⚠️ {trends['error']}")
    
    # Test 9: Export des données
    print("\n🎯 Test 9: Export des données")
    try:
        exported_data = dashboard.export_data('json')
        print(f"✅ Données exportées: {len(exported_data)} caractères")
        print(f"   (Format JSON avec résumé, performance, alertes, tendances)")
    except Exception as e:
        print(f"❌ Erreur export: {e}")
    
    # Test 10: Arrêt du monitoring
    print("\n🎯 Test 10: Arrêt du monitoring")
    dashboard.stop_monitoring()
    time.sleep(2)  # Attendre l'arrêt
    
    final_summary = dashboard.get_dashboard_summary()
    print(f"✅ Monitoring arrêté: {final_summary['status'] == 'inactive'}")
    
    # Test 11: Statistiques finales
    print("\n🎯 Test 11: Statistiques finales")
    print(f"✅ Résumé du test:")
    print(f"   - Résultats de scores ajoutés: {len(score_results)}")
    print(f"   - Cycles de monitoring: {final_summary['total_calculations']}")
    print(f"   - Alertes générées: {final_summary['alerts_generated']}")
    print(f"   - Problèmes détectés: {final_summary['data_quality_issues'] + final_summary['component_failures']}")
    print(f"   - Composants analysés: {final_summary['components_monitored']}")
    print(f"   - Durée du test: {final_summary['uptime_seconds']:.1f}s")
    
    print(f"\n🎉 Test du dashboard de monitoring terminé!")
    print(f"📊 Le système de monitoring des scores est {'✅ OPÉRATIONNEL' if final_summary['total_calculations'] > 0 else '❌ NON FONCTIONNEL'}")

if __name__ == "__main__":
    test_score_monitoring_dashboard()

