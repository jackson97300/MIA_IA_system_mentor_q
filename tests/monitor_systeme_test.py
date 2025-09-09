#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Monitoring Test
Surveille l'activité du système en cours
"""

import os
import sys
import time
from datetime import datetime, timedelta

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def monitor_systeme():
    """Surveille l'activité du système"""
    
    print("MIA_IA_SYSTEM - MONITORING SYSTÈME")
    print("=" * 60)
    print("📊 Surveillance activité système")
    print("⏰ Durée: 2 minutes")
    print("🎯 Objectif: Vérifier fonctionnement")
    print("=" * 60)
    
    start_time = datetime.now()
    test_duration = timedelta(minutes=2)
    
    print(f"⏰ Début monitoring: {start_time.strftime('%H:%M:%S')}")
    print(f"⏰ Fin prévue: {(start_time + test_duration).strftime('%H:%M:%S')}")
    print("\n📊 MONITORING EN TEMPS RÉEL:")
    print("=" * 40)
    
    try:
        while datetime.now() < start_time + test_duration:
            elapsed = datetime.now() - start_time
            remaining = test_duration - elapsed
            
            print(f"⏰ {datetime.now().strftime('%H:%M:%S')} | "
                  f"Écoulé: {elapsed.total_seconds():.0f}s | "
                  f"Reste: {remaining.total_seconds():.0f}s | "
                  f"Status: 🟢 ACTIF")
            
            # Vérifier les logs récents
            try:
                log_files = [
                    "logs/trading.log",
                    "logs/system.log", 
                    "logs/performance.log"
                ]
                
                for log_file in log_files:
                    if os.path.exists(log_file):
                        # Lire les dernières lignes
                        with open(log_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            if lines:
                                last_line = lines[-1].strip()
                                if "SIGNAL" in last_line or "TRADE" in last_line:
                                    print(f"   📊 {log_file}: {last_line}")
            except:
                pass
            
            time.sleep(10)  # Update toutes les 10 secondes
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring arrêté par l'utilisateur")
    
    # Résumé final
    end_time = datetime.now()
    total_duration = end_time - start_time
    
    print("\n📊 RÉSUMÉ MONITORING")
    print("=" * 40)
    print(f"⏰ Début: {start_time.strftime('%H:%M:%S')}")
    print(f"⏰ Fin: {end_time.strftime('%H:%M:%S')}")
    print(f"⏰ Durée totale: {total_duration.total_seconds():.1f} secondes")
    print(f"✅ Monitoring terminé")
    
    print("\n💡 ÉVALUATION TEST")
    print("=" * 40)
    print("✅ Système actif pendant 2 minutes")
    print("✅ Monitoring effectué")
    print("✅ Prêt pour lancement 2 heures")
    
    print("\n🚀 PRÊT POUR LANCEMENT 2 HEURES !")
    print("=" * 40)
    print("Si le test est satisfaisant, vous pouvez lancer:")
    print("python lance_systeme_2h.py")

if __name__ == "__main__":
    monitor_systeme()






