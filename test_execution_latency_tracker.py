#!/usr/bin/env python3
"""
Test du système de tracking de latence d'exécution dans le pipeline de trading
"""

import sys
from pathlib import Path
import time
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).parent))

from core.execution_latency_tracker import (
    ExecutionLatencyTracker, 
    LatencyStage, 
    LatencyAlertType,
    create_execution_latency_tracker
)

def test_execution_latency_tracker():
    """Test du système de tracking de latence d'exécution"""
    print("🚀 === TEST TRACKING LATENCE EXÉCUTION ===\n")
    
    # Test 1: Création du tracker
    print("🎯 Test 1: Création du tracker de latence")
    tracker = create_execution_latency_tracker(max_history_size=100)
    print(f"✅ Tracker créé: {tracker}")
    
    # Test 2: Simulation d'un pipeline de trading complet
    print("\n🎯 Test 2: Simulation d'un pipeline de trading complet")
    
    # Démarrer un pipeline
    pipeline_id = tracker.start_pipeline(signal_type="BULLISH", symbol="ESZ5")
    print(f"   Pipeline démarré: {pipeline_id}")
    
    # Simuler les étapes du pipeline avec des latences réalistes
    stages_to_simulate = [
        (LatencyStage.SIGNAL_GENERATION, 45.0, True),
        (LatencyStage.MENTHORQ_PROCESSING, 85.0, True),
        (LatencyStage.BATTLE_NAVALE_ANALYSIS, 65.0, True),
        (LatencyStage.VIX_REGIME_CHECK, 20.0, True),
        (LatencyStage.LEADERSHIP_FILTER, 35.0, True),
        (LatencyStage.SCORE_CALCULATION, 25.0, True),
        (LatencyStage.RISK_MANAGEMENT, 90.0, True),
        (LatencyStage.ORDER_PREPARATION, 40.0, True),
        (LatencyStage.DTC_ROUTING, 180.0, True),
        (LatencyStage.ORDER_EXECUTION, 450.0, True),
        (LatencyStage.TRADE_CONFIRMATION, 80.0, True)
    ]
    
    for stage, simulated_duration_ms, success in stages_to_simulate:
        # Démarrer l'étape
        tracker.start_stage(stage, context={"simulated": True})
        
        # Simuler la durée de l'étape
        time.sleep(simulated_duration_ms / 1000.0)  # Convertir en secondes
        
        # Terminer l'étape
        tracker.end_stage(stage, success=success)
        print(f"   ✅ {stage.value}: {simulated_duration_ms:.1f}ms")
    
    # Terminer le pipeline
    pipeline_result = tracker.end_pipeline(success=True)
    print(f"   🏁 Pipeline terminé: {pipeline_result.total_duration_ms:.1f}ms total")
    
    # Test 3: Simulation d'un pipeline avec des problèmes de performance
    print("\n🎯 Test 3: Simulation d'un pipeline avec problèmes de performance")
    
    # Pipeline avec latence élevée
    pipeline_id_2 = tracker.start_pipeline(signal_type="BEARISH", symbol="NQZ5")
    
    # Simuler des étapes avec des problèmes
    problematic_stages = [
        (LatencyStage.SIGNAL_GENERATION, 120.0, True),  # 2.4x le seuil
        (LatencyStage.MENTHORQ_PROCESSING, 250.0, True),  # 2.5x le seuil
        (LatencyStage.BATTLE_NAVALE_ANALYSIS, 45.0, True),
        (LatencyStage.VIX_REGIME_CHECK, 15.0, True),
        (LatencyStage.LEADERSHIP_FILTER, 30.0, True),
        (LatencyStage.SCORE_CALCULATION, 20.0, True),
        (LatencyStage.RISK_MANAGEMENT, 80.0, True),
        (LatencyStage.ORDER_PREPARATION, 35.0, True),
        (LatencyStage.DTC_ROUTING, 600.0, True),  # 3x le seuil
        (LatencyStage.ORDER_EXECUTION, 1200.0, True),  # 2.4x le seuil
        (LatencyStage.TRADE_CONFIRMATION, 70.0, True)
    ]
    
    for stage, simulated_duration_ms, success in problematic_stages:
        tracker.start_stage(stage, context={"simulated": True, "problematic": True})
        time.sleep(simulated_duration_ms / 1000.0)
        tracker.end_stage(stage, success=success)
        print(f"   ⚠️ {stage.value}: {simulated_duration_ms:.1f}ms")
    
    pipeline_result_2 = tracker.end_pipeline(success=True)
    print(f"   🏁 Pipeline problématique terminé: {pipeline_result_2.total_duration_ms:.1f}ms total")
    
    # Test 4: Simulation d'un pipeline avec échec d'étape
    print("\n🎯 Test 4: Simulation d'un pipeline avec échec d'étape")
    
    pipeline_id_3 = tracker.start_pipeline(signal_type="NEUTRAL", symbol="ESZ5")
    
    # Simuler un échec à l'étape de risk management
    tracker.start_stage(LatencyStage.SIGNAL_GENERATION)
    time.sleep(0.05)
    tracker.end_stage(LatencyStage.SIGNAL_GENERATION, success=True)
    
    tracker.start_stage(LatencyStage.MENTHORQ_PROCESSING)
    time.sleep(0.08)
    tracker.end_stage(LatencyStage.MENTHORQ_PROCESSING, success=True)
    
    tracker.start_stage(LatencyStage.RISK_MANAGEMENT)
    time.sleep(0.12)
    tracker.end_stage(LatencyStage.RISK_MANAGEMENT, success=False, error_message="Risk limit exceeded")
    
    pipeline_result_3 = tracker.end_pipeline(success=False)
    print(f"   ❌ Pipeline avec échec terminé: {pipeline_result_3.total_duration_ms:.1f}ms total")
    
    # Test 5: Démarrage du monitoring automatique
    print("\n🎯 Test 5: Démarrage du monitoring automatique")
    success = tracker.start_monitoring(check_interval_seconds=2)
    print(f"✅ Monitoring démarré: {success}")
    
    if not success:
        print("❌ Impossible de démarrer le monitoring - arrêt du test")
        return
    
    # Test 6: Surveillance pendant quelques cycles
    print("\n🎯 Test 6: Surveillance pendant 8 secondes")
    print("   (Le monitoring va analyser les tendances de performance)")
    
    for i in range(4):  # 4 cycles de 2 secondes = 8 secondes
        time.sleep(2)
        summary = tracker.get_latency_summary()
        print(f"   Cycle {i+1}: {summary['total_measurements']} mesures, {summary['alerts_generated']} alertes")
    
    # Test 7: Résumé des latences
    print("\n🎯 Test 7: Résumé des latences")
    summary = tracker.get_latency_summary()
    print(f"✅ Résumé des latences:")
    print(f"   - Total mesures: {summary['total_measurements']}")
    print(f"   - Total pipelines: {summary['total_pipelines']}")
    print(f"   - Étapes surveillées: {summary['stages_monitored']}")
    print(f"   - Alertes générées: {summary['alerts_generated']}")
    print(f"   - Monitoring actif: {summary['monitoring_active']}")
    
    # Test 8: Performance par étape
    print("\n🎯 Test 8: Performance par étape")
    stage_performance = tracker.get_stage_performance()
    print(f"✅ Performance par étape:")
    for stage_name, perf in stage_performance.items():
        print(f"   - {stage_name}:")
        print(f"     * Mesures: {perf['total_measurements']}")
        print(f"     * Durée moyenne: {perf['avg_duration_ms']}ms")
        print(f"     * Durée min/max: {perf['min_duration_ms']}/{perf['max_duration_ms']}ms")
        print(f"     * P95: {perf['p95_duration_ms']}ms")
        print(f"     * Taux d'erreur: {perf['error_rate']:.1%}")
        print(f"     * Seuil: {perf['threshold_ms']}ms")
    
    # Test 9: Alertes récentes
    print("\n🎯 Test 9: Alertes récentes")
    recent_alerts = tracker.get_recent_alerts(10)
    print(f"✅ Alertes récentes ({len(recent_alerts)}):")
    for alert in recent_alerts:
        print(f"   - {alert['timestamp']}: {alert['severity'].upper()} - {alert['message']}")
        if alert['stage']:
            print(f"     Étape: {alert['stage']}")
    
    # Test 10: Export des métriques
    print("\n🎯 Test 10: Export des métriques")
    try:
        exported_metrics = tracker.export_metrics('json')
        print(f"✅ Métriques exportées: {len(exported_metrics)} caractères")
        print(f"   (Format JSON avec résumé, performance, alertes)")
    except Exception as e:
        print(f"❌ Erreur export: {e}")
    
    # Test 11: Arrêt du monitoring
    print("\n🎯 Test 11: Arrêt du monitoring")
    tracker.stop_monitoring()
    time.sleep(2)  # Attendre l'arrêt
    
    final_summary = tracker.get_latency_summary()
    print(f"✅ Monitoring arrêté: {not final_summary['monitoring_active']}")
    
    # Test 12: Statistiques finales
    print("\n🎯 Test 12: Statistiques finales")
    print(f"✅ Résumé du test:")
    print(f"   - Pipelines simulés: {final_summary['total_pipelines']}")
    print(f"   - Mesures de latence: {final_summary['total_measurements']}")
    print(f"   - Alertes générées: {final_summary['alerts_generated']}")
    print(f"   - Étapes surveillées: {final_summary['stages_monitored']}")
    print(f"   - Durée du test: ~{sum([stage[1] for stage in stages_to_simulate + problematic_stages]) / 1000:.1f}s")
    
    print(f"\n🎉 Test du tracking de latence terminé!")
    print(f"⚡ Le système de tracking de latence est {'✅ OPÉRATIONNEL' if final_summary['total_measurements'] > 0 else '❌ NON FONCTIONNEL'}")

if __name__ == "__main__":
    test_execution_latency_tracker()
