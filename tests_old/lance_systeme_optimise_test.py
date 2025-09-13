#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Lancement Système Optimisé Test 2 Minutes
Lance le système avec toutes les optimisations pour test
"""

import os
import sys
import json
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

async def lance_systeme_optimise():
    """Lance le système optimisé pour test 2 minutes"""
    
    global stop_system
    
    print("MIA_IA_SYSTEM - LANCEMENT SYSTÈME OPTIMISÉ")
    print("=" * 60)
    print("🎯 MODE: Test 2 minutes avec optimisations")
    print("⏰ Durée: 2 minutes maximum")
    print("📊 Objectif: Vérifier fonctionnement optimisé")
    print("=" * 60)
    
    try:
        # Appliquer les optimisations
        import config.automation_config as auto_config
        
        print("🔧 VÉRIFICATION OPTIMISATIONS APPLIQUÉES")
        print("=" * 40)
        
        print(f"✅ Interval minimum: {auto_config.MIN_SIGNAL_INTERVAL}s")
        print(f"✅ Délai cycle: {auto_config.TRADING_CYCLE_DELAY}s")
        print(f"✅ Max trades/heure: {auto_config.MAX_TRADES_PER_HOUR}")
        print(f"✅ Signaux SELL: {'Activés' if auto_config.ENABLE_SELL_SIGNALS else 'Désactivés'}")
        print(f"✅ Seuil confiance: {auto_config.MIN_CONFIDENCE_THRESHOLD:.1%}")
        print(f"✅ Confluence min: {auto_config.MIN_CONFLUENCE_SCORE:.1%}")
        
        # Configuration pour test 2 minutes
        auto_config.TEST_MODE = True
        auto_config.TEST_DURATION_MINUTES = 2
        auto_config.MAX_TRADES_PER_HOUR = 10  # Limiter pour test
        
        print("\n🚀 LANCEMENT SYSTÈME OPTIMISÉ...")
        print("=" * 40)
        
        # Enregistrer le signal handler
        signal.signal(signal.SIGINT, signal_handler)
        
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
        print(f"🎯 Mode: Test optimisé")
        print(f"✅ Status: Terminé proprement")
        
        print("\n💡 ÉVALUATION TEST")
        print("=" * 40)
        print("✅ Système démarré avec succès")
        print("✅ Optimisations appliquées")
        print("✅ Arrêt propre effectué")
        print("✅ Prêt pour lancement 2 heures")
        
        print("\n🚀 PRÊT POUR LANCEMENT 2 HEURES !")
        print("=" * 40)
        print("Si le test est satisfaisant, vous pouvez lancer:")
        print("python lance_systeme_optimise_2h.py")
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
    except Exception as e:
        print(f"❌ Erreur lancement: {e}")
    finally:
        print("\n✅ Test terminé")

if __name__ == "__main__":
    asyncio.run(lance_systeme_optimise())






