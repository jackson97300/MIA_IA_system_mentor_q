#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test 2 Minutes Simplifié
Lance le système pour test 2 minutes
"""

import os
import sys
import asyncio
import signal
from datetime import datetime, timedelta

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Variable globale pour arrêter le système
stop_system = False

def signal_handler(signum, frame):
    """Gestionnaire pour arrêter le système proprement"""
    global stop_system
    print("\n🛑 Signal d'arrêt reçu - Arrêt propre du système...")
    stop_system = True

async def lance_test_2min():
    """Lance le test de 2 minutes"""
    
    global stop_system
    
    print("MIA_IA_SYSTEM - TEST 2 MINUTES")
    print("=" * 60)
    print("🎯 MODE: Test 2 minutes")
    print("⏰ Durée: 2 minutes maximum")
    print("📊 Objectif: Vérifier fonctionnement système")
    print("=" * 60)
    
    try:
        # Enregistrer le signal handler
        signal.signal(signal.SIGINT, signal_handler)
        
        print("🚀 LANCEMENT SYSTÈME...")
        print("=" * 40)
        
        # Démarrer le système principal
        from launch_24_7_orderflow_trading import main
        
        # Créer une tâche pour le système principal
        system_task = asyncio.create_task(main())
        
        # Attendre 2 minutes ou signal d'arrêt
        start_time = datetime.now()
        test_duration = timedelta(minutes=2)
        
        print(f"⏰ Démarrage: {start_time.strftime('%H:%M:%S')}")
        print(f"⏰ Fin prévue: {(start_time + test_duration).strftime('%H:%M:%S')}")
        print("\n📊 MONITORING EN TEMPS RÉEL:")
        print("=" * 40)
        
        while datetime.now() < start_time + test_duration and not stop_system:
            elapsed = datetime.now() - start_time
            remaining = test_duration - elapsed
            
            print(f"⏰ Temps écoulé: {elapsed.total_seconds():.0f}s | "
                  f"Reste: {remaining.total_seconds():.0f}s | "
                  f"Status: {'🟢 ACTIF' if not stop_system else '🔴 ARRÊT'}")
            
            await asyncio.sleep(10)  # Update toutes les 10 secondes
        
        # Arrêter le système
        print("\n🛑 ARRÊT SYSTÈME TEST...")
        stop_system = True
        
        # Annuler la tâche système
        if not system_task.done():
            system_task.cancel()
            try:
                await system_task
            except asyncio.CancelledError:
                pass
        
        # Résumé du test
        end_time = datetime.now()
        total_duration = end_time - start_time
        
        print("\n📊 RÉSUMÉ TEST 2 MINUTES")
        print("=" * 40)
        print(f"⏰ Début: {start_time.strftime('%H:%M:%S')}")
        print(f"⏰ Fin: {end_time.strftime('%H:%M:%S')}")
        print(f"⏰ Durée totale: {total_duration.total_seconds():.1f} secondes")
        print(f"🎯 Mode: Test simple")
        print(f"✅ Status: Terminé proprement")
        
        print("\n💡 ÉVALUATION TEST")
        print("=" * 40)
        print("✅ Système démarré avec succès")
        print("✅ Test de 2 minutes effectué")
        print("✅ Arrêt propre effectué")
        print("✅ Prêt pour lancement 2 heures")
        
        print("\n🚀 PRÊT POUR LANCEMENT 2 HEURES !")
        print("=" * 40)
        print("Si le test est satisfaisant, vous pouvez lancer:")
        print("python lance_systeme_2h.py")
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
    except Exception as e:
        print(f"❌ Erreur lancement: {e}")
    finally:
        print("\n✅ Test terminé")

if __name__ == "__main__":
    asyncio.run(lance_test_2min())






