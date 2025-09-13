#!/usr/bin/env python3
"""
Test du système de monitoring automatique de staleness MenthorQ
"""

import sys
from pathlib import Path
import time
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).parent))

from core.menthorq_staleness_monitor import (
    MenthorQStalenessMonitor, 
    MonitoringConfig, 
    AlertLevel,
    create_menthorq_staleness_monitor
)

def test_menthorq_staleness_monitor():
    """Test du système de monitoring automatique"""
    print("🚀 === TEST MONITORING AUTOMATIQUE STALENESS MENTHORQ ===\n")
    
    # Test 1: Création du moniteur
    print("🎯 Test 1: Création du moniteur")
    config = MonitoringConfig(
        check_interval_seconds=5,  # Check rapide pour le test
        alert_cooldown_seconds=10,  # Cooldown court pour le test
        max_alerts_per_hour=5,
        enable_discord_alerts=False,
        enable_email_alerts=False
    )
    
    monitor = create_menthorq_staleness_monitor(config)
    print(f"✅ Moniteur créé: {monitor}")
    
    # Test 2: Ajout de sources à surveiller
    print("\n🎯 Test 2: Ajout de sources à surveiller")
    monitor.add_monitored_source("ESZ5", "gamma_levels", 60)
    monitor.add_monitored_source("ESZ5", "blind_spots", 60)
    monitor.add_monitored_source("NQZ5", "gamma_levels", 60)
    monitor.add_monitored_source("NQZ5", "swing_levels", 60)
    
    print(f"✅ Sources ajoutées: {len(monitor.monitored_sources)}")
    for source in monitor.monitored_sources:
        print(f"   - {source['source_id']}")
    
    # Test 3: Ajout de callback d'alerte
    print("\n🎯 Test 3: Ajout de callback d'alerte")
    alert_count = 0
    
    def test_alert_callback(alert):
        nonlocal alert_count
        alert_count += 1
        print(f"🚨 Callback reçu: {alert.alert_level.value} - {alert.message}")
    
    monitor.add_alert_callback(test_alert_callback)
    print("✅ Callback d'alerte ajouté")
    
    # Test 4: Démarrage du monitoring
    print("\n🎯 Test 4: Démarrage du monitoring")
    success = monitor.start_monitoring()
    print(f"✅ Monitoring démarré: {success}")
    
    if not success:
        print("❌ Impossible de démarrer le monitoring - arrêt du test")
        return
    
    # Test 5: Surveillance pendant quelques cycles
    print("\n🎯 Test 5: Surveillance pendant 20 secondes")
    print("   (Le monitoring va vérifier la staleness toutes les 5 secondes)")
    
    for i in range(4):  # 4 cycles de 5 secondes = 20 secondes
        time.sleep(5)
        status = monitor.get_monitoring_status()
        print(f"   Cycle {i+1}: {status['total_checks']} checks, {status['alerts_sent']} alertes")
    
    # Test 6: Statut final
    print("\n🎯 Test 6: Statut final du monitoring")
    final_status = monitor.get_monitoring_status()
    print(f"✅ Statut final:")
    print(f"   - En cours: {final_status['is_running']}")
    print(f"   - Sources surveillées: {final_status['sources_monitored']}")
    print(f"   - Total checks: {final_status['total_checks']}")
    print(f"   - Alertes envoyées: {final_status['alerts_sent']}")
    print(f"   - Uptime: {final_status['uptime_seconds']:.1f}s")
    print(f"   - Callbacks reçus: {alert_count}")
    
    # Test 7: Alertes récentes
    print("\n🎯 Test 7: Alertes récentes")
    recent_alerts = monitor.get_recent_alerts(5)
    print(f"✅ Alertes récentes ({len(recent_alerts)}):")
    for alert in recent_alerts:
        print(f"   - {alert['timestamp']}: {alert['alert_level']} - {alert['message']}")
    
    # Test 8: Arrêt du monitoring
    print("\n🎯 Test 8: Arrêt du monitoring")
    monitor.stop_monitoring()
    time.sleep(2)  # Attendre l'arrêt
    
    final_status = monitor.get_monitoring_status()
    print(f"✅ Monitoring arrêté: {not final_status['is_running']}")
    
    # Test 9: Statistiques finales
    print("\n🎯 Test 9: Statistiques finales")
    print(f"✅ Résumé du test:")
    print(f"   - Sources configurées: {len(monitor.monitored_sources)}")
    print(f"   - Cycles de monitoring: {final_status['total_checks']}")
    print(f"   - Alertes générées: {final_status['alerts_sent']}")
    print(f"   - Callbacks exécutés: {alert_count}")
    print(f"   - Durée du test: {final_status['uptime_seconds']:.1f}s")
    
    print(f"\n🎉 Test du monitoring automatique terminé!")
    print(f"📊 Le système de monitoring est {'✅ OPÉRATIONNEL' if final_status['total_checks'] > 0 else '❌ NON FONCTIONNEL'}")

if __name__ == "__main__":
    test_menthorq_staleness_monitor()

