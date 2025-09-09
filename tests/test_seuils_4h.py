#!/usr/bin/env python3
"""
🧪 TEST SEUILS MIA - 4 HEURES
================================

Script pour tester plusieurs seuils pendant 4 heures
avec enregistrement complet des logs
"""

import sys
import asyncio
import time
from pathlib import Path
from datetime import datetime, timedelta

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

async def test_seuils_4h():
    """Test des seuils pendant 4 heures"""
    print("🧪 TEST SEUILS MIA - 4 HEURES")
    print("=" * 50)
    print("🎯 Test de plusieurs seuils avec enregistrement logs")
    print("⏰ Durée: 4 heures")
    print("📊 Logs: Enregistrement complet")
    print("=" * 50)
    
    # Créer le dossier de logs pour ce test
    test_log_dir = Path("logs/test_seuils_4h")
    test_log_dir.mkdir(exist_ok=True)
    
    # Timestamp de début
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=4)
    
    print(f"🚀 Début: {start_time.strftime('%H:%M:%S')}")
    print(f"⏰ Fin prévue: {end_time.strftime('%H:%M:%S')}")
    print(f"📁 Logs: {test_log_dir}")
    
    try:
        # Import du lanceur principal
        from launch_24_7 import MIAOrchestrator
        
        print("\n🔧 Configuration test seuils...")
        
        # Créer l'orchestrateur en mode simulation pour tests
        orchestrator = MIAOrchestrator(
            live_trading=False,     # Mode paper trading
            simulation_mode=True    # Mode simulation pour tests
        )
        
        print("✅ Orchestrateur créé en mode test")
        print("🔧 Test de plusieurs seuils...")
        
        # Démarrer l'orchestrateur
        await orchestrator.start()
        
        # Boucle de test pendant 4 heures
        while datetime.now() < end_time:
            elapsed = datetime.now() - start_time
            remaining = end_time - datetime.now()
            
            print(f"\n⏰ Temps écoulé: {elapsed}")
            print(f"⏰ Temps restant: {remaining}")
            print(f"📊 Statut: Test en cours...")
            
            # Attendre 5 minutes avant prochaine vérification
            await asyncio.sleep(300)  # 5 minutes
        
        print(f"\n✅ Test terminé après 4 heures")
        print(f"📁 Logs sauvegardés dans: {test_log_dir}")
        
    except KeyboardInterrupt:
        print("\n🛑 Test arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
    finally:
        if 'orchestrator' in locals():
            await orchestrator.stop()
        print("✅ Test terminé")

def main():
    """Fonction principale"""
    try:
        asyncio.run(test_seuils_4h())
    except KeyboardInterrupt:
        print("\n🛑 Test arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")

if __name__ == "__main__":
    main()





