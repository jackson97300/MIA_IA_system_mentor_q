#!/usr/bin/env python3
"""
Test du système de tracking du régime VIX dans les décisions de trading
"""

import sys
from pathlib import Path
import time
from datetime import datetime, timezone, timedelta
sys.path.insert(0, str(Path(__file__).parent))

from core.vix_regime_tracker import (
    VIXRegimeTracker, 
    VIXRegime, 
    TradingDecisionType,
    create_vix_regime_tracker
)

def test_vix_regime_tracker():
    """Test du système de tracking du régime VIX"""
    print("🚀 === TEST TRACKING RÉGIME VIX ===\n")
    
    # Test 1: Création du tracker
    print("🎯 Test 1: Création du tracker VIX")
    tracker = create_vix_regime_tracker(max_history_size=100)
    print(f"✅ Tracker créé: {tracker}")
    
    # Test 2: Simulation d'évolution VIX normale
    print("\n🎯 Test 2: Simulation d'évolution VIX normale")
    
    # Simuler une évolution VIX normale
    vix_levels_normal = [18.5, 19.2, 20.1, 21.5, 22.8, 24.2, 25.1, 26.3, 27.8, 29.2]
    
    for i, vix_level in enumerate(vix_levels_normal):
        snapshot = tracker.update_vix_level(vix_level, context={"simulation": True, "step": i+1})
        print(f"   VIX {i+1}: {vix_level:.1f} ({snapshot.regime.value}) - Tendance: {snapshot.volatility_trend}")
        time.sleep(0.1)  # Petite pause pour simuler le temps
    
    print(f"✅ {len(vix_levels_normal)} niveaux VIX normaux simulés")
    
    # Test 3: Simulation d'un spike VIX
    print("\n🎯 Test 3: Simulation d'un spike VIX")
    
    # Simuler un spike VIX (transition vers HIGH_VIX)
    vix_levels_spike = [30.5, 35.2, 42.8, 48.5, 52.1, 55.8, 58.2, 60.5, 62.8, 65.1]
    
    for i, vix_level in enumerate(vix_levels_spike):
        snapshot = tracker.update_vix_level(vix_level, context={"simulation": True, "spike": True, "step": i+1})
        print(f"   VIX Spike {i+1}: {vix_level:.1f} ({snapshot.regime.value}) - Changement: {snapshot.change_percent:+.1f}%")
        time.sleep(0.1)
    
    print(f"✅ {len(vix_levels_spike)} niveaux VIX spike simulés")
    
    # Test 4: Simulation d'un crash VIX
    print("\n🎯 Test 4: Simulation d'un crash VIX")
    
    # Simuler un crash VIX (retour vers NORMAL)
    vix_levels_crash = [58.2, 52.1, 45.8, 38.5, 32.2, 28.1, 24.5, 21.8, 19.2, 16.5]
    
    for i, vix_level in enumerate(vix_levels_crash):
        snapshot = tracker.update_vix_level(vix_level, context={"simulation": True, "crash": True, "step": i+1})
        print(f"   VIX Crash {i+1}: {vix_level:.1f} ({snapshot.regime.value}) - Changement: {snapshot.change_percent:+.1f}%")
        time.sleep(0.1)
    
    print(f"✅ {len(vix_levels_crash)} niveaux VIX crash simulés")
    
    # Test 5: Simulation de décisions de trading
    print("\n🎯 Test 5: Simulation de décisions de trading")
    
    # Simuler des décisions de trading dans différents régimes
    trading_scenarios = [
        (TradingDecisionType.SIGNAL_GENERATED, "success", 0.3, {"signal_strength": 0.8}),
        (TradingDecisionType.POSITION_OPENED, "success", 0.2, {"position_size": 2}),
        (TradingDecisionType.SIGNAL_BLOCKED, "neutral", 0.7, {"reason": "high_vix"}),
        (TradingDecisionType.RISK_ADJUSTED, "success", 0.5, {"risk_reduction": 0.3}),
        (TradingDecisionType.POSITION_CLOSED, "success", 0.1, {"pnl": 150.0}),
        (TradingDecisionType.SIZING_MODIFIED, "success", 0.4, {"size_reduction": 0.5}),
        (TradingDecisionType.SIGNAL_GENERATED, "failure", 0.6, {"signal_strength": 0.4}),
        (TradingDecisionType.POSITION_OPENED, "failure", 0.8, {"position_size": 1}),
    ]
    
    for i, (decision_type, outcome, vix_impact, context) in enumerate(trading_scenarios):
        decision = tracker.record_trading_decision(decision_type, outcome, vix_impact, context)
        print(f"   Décision {i+1}: {decision_type.value} ({outcome}) - Impact VIX: {vix_impact:.1f}")
        time.sleep(0.05)
    
    print(f"✅ {len(trading_scenarios)} décisions de trading simulées")
    
    # Test 6: Démarrage du monitoring automatique
    print("\n🎯 Test 6: Démarrage du monitoring automatique")
    success = tracker.start_monitoring(check_interval_seconds=2)
    print(f"✅ Monitoring démarré: {success}")
    
    if not success:
        print("❌ Impossible de démarrer le monitoring - arrêt du test")
        return
    
    # Test 7: Surveillance pendant quelques cycles
    print("\n🎯 Test 7: Surveillance pendant 8 secondes")
    print("   (Le monitoring va analyser les tendances VIX)")
    
    for i in range(4):  # 4 cycles de 2 secondes = 8 secondes
        time.sleep(2)
        summary = tracker.get_vix_summary()
        print(f"   Cycle {i+1}: {summary['total_snapshots']} snapshots, {summary['total_transitions']} transitions, {summary['alerts_generated']} alertes")
    
    # Test 8: Résumé VIX
    print("\n🎯 Test 8: Résumé VIX")
    summary = tracker.get_vix_summary()
    print(f"✅ Résumé VIX:")
    print(f"   - VIX actuel: {summary['current_vix_level']:.2f}")
    print(f"   - Régime actuel: {summary['current_regime']}")
    print(f"   - Total snapshots: {summary['total_snapshots']}")
    print(f"   - Total transitions: {summary['total_transitions']}")
    print(f"   - Total décisions: {summary['total_decisions']}")
    print(f"   - Alertes générées: {summary['alerts_generated']}")
    print(f"   - Monitoring actif: {summary['monitoring_active']}")
    
    # Test 9: Performance par régime
    print("\n🎯 Test 9: Performance par régime")
    regime_performance = tracker.get_regime_performance()
    print(f"✅ Performance par régime:")
    for regime_name, perf in regime_performance.items():
        print(f"   - {regime_name}:")
        print(f"     * Décisions: {perf['total_decisions']}")
        print(f"     * Taux de succès: {perf['success_rate']:.1%}")
        print(f"     * VIX moyen: {perf['avg_vix_level']:.2f}")
        print(f"     * VIX min/max: {perf['min_vix_level']:.2f}/{perf['max_vix_level']:.2f}")
        print(f"     * Impact moyen: {perf['avg_decision_impact']:.2f}")
    
    # Test 10: Transitions récentes
    print("\n🎯 Test 10: Transitions récentes")
    recent_transitions = tracker.get_recent_transitions(5)
    print(f"✅ Transitions récentes ({len(recent_transitions)}):")
    for transition in recent_transitions:
        print(f"   - {transition['timestamp']}: {transition['from_regime']} → {transition['to_regime']}")
        print(f"     Type: {transition['transition_type']}")
        print(f"     VIX: {transition['vix_level']:.2f}")
        print(f"     Impact: {transition['impact_score']:.2f}")
        print(f"     Implications: {', '.join(transition['trading_implications'][:2])}")
    
    # Test 11: Alertes récentes
    print("\n🎯 Test 11: Alertes récentes")
    recent_alerts = tracker.get_recent_alerts(10)
    print(f"✅ Alertes récentes ({len(recent_alerts)}):")
    for alert in recent_alerts:
        print(f"   - {alert['timestamp']}: {alert['severity'].upper()} - {alert['message']}")
        print(f"     Régime: {alert['regime']}")
    
    # Test 12: Export des données
    print("\n🎯 Test 12: Export des données")
    try:
        exported_data = tracker.export_vix_data('json')
        print(f"✅ Données VIX exportées: {len(exported_data)} caractères")
        print(f"   (Format JSON avec résumé, performance, transitions, alertes)")
    except Exception as e:
        print(f"❌ Erreur export: {e}")
    
    # Test 13: Arrêt du monitoring
    print("\n🎯 Test 13: Arrêt du monitoring")
    tracker.stop_monitoring()
    time.sleep(2)  # Attendre l'arrêt
    
    final_summary = tracker.get_vix_summary()
    print(f"✅ Monitoring arrêté: {not final_summary['monitoring_active']}")
    
    # Test 14: Statistiques finales
    print("\n🎯 Test 14: Statistiques finales")
    print(f"✅ Résumé du test:")
    print(f"   - Snapshots VIX: {final_summary['total_snapshots']}")
    print(f"   - Transitions détectées: {final_summary['total_transitions']}")
    print(f"   - Décisions enregistrées: {final_summary['total_decisions']}")
    print(f"   - Alertes générées: {final_summary['alerts_generated']}")
    print(f"   - Régimes VIX testés: {len([r for r in regime_performance.values() if r['total_decisions'] > 0])}")
    print(f"   - Durée du test: ~{len(vix_levels_normal + vix_levels_spike + vix_levels_crash) * 0.1:.1f}s")
    
    print(f"\n🎉 Test du tracking VIX terminé!")
    print(f"📊 Le système de tracking VIX est {'✅ OPÉRATIONNEL' if final_summary['total_snapshots'] > 0 else '❌ NON FONCTIONNEL'}")

if __name__ == "__main__":
    test_vix_regime_tracker()

