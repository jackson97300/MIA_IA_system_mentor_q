#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Lancement Direct
Lance le système directement pour test
"""

import os
import sys
import time
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def lance_systeme_direct():
    """Lance le système directement"""
    
    print("MIA_IA_SYSTEM - LANCEMENT DIRECT")
    print("=" * 60)
    print("🎯 MODE: Test direct")
    print("⏰ Durée: 2 minutes maximum")
    print("📊 Objectif: Vérifier fonctionnement système")
    print("=" * 60)
    
    try:
        print("🚀 LANCEMENT SYSTÈME...")
        print("=" * 40)
        
        start_time = datetime.now()
        print(f"⏰ Démarrage: {start_time.strftime('%H:%M:%S')}")
        
        # Lancer directement le système principal
        from launch_24_7_orderflow_trading import main
        
        print("✅ Système lancé avec succès !")
        print("⏰ Le système va tourner pendant 2 minutes...")
        print("🛑 Appuyez sur Ctrl+C pour arrêter")
        
        # Lancer le système
        main()
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
    except Exception as e:
        print(f"❌ Erreur lancement: {e}")
    finally:
        end_time = datetime.now()
        duration = end_time - start_time
        print(f"\n📊 Durée totale: {duration.total_seconds():.1f} secondes")
        print("✅ Test terminé")

if __name__ == "__main__":
    lance_systeme_direct()






