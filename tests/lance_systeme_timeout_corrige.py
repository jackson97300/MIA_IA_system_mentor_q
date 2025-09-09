#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Lancement Timeout Corrigé
Lance le système avec timeout réduit
"""

import os
import sys
import asyncio
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def lance_systeme_timeout_corrige():
    """Lance le système avec timeout corrigé"""
    
    print("MIA_IA_SYSTEM - LANCEMENT TIMEOUT CORRIGÉ")
    print("=" * 60)
    print("🔧 Timeout réduit à 30s")
    print("🎯 Port TWS 7497 confirmé")
    print("=" * 60)
    
    try:
        # Configuration optimisée
        import config.automation_config as auto_config
        
        # Réduire timeout
        auto_config.IBKR_TIMEOUT = 30  # 30 secondes au lieu de 60
        auto_config.IBKR_HOST = "127.0.0.1"
        auto_config.IBKR_PORT = 7497  # TWS confirmé actif
        auto_config.IBKR_CLIENT_ID = 1
        
        print("✅ Configuration timeout appliquée:")
        print(f"   Host: {auto_config.IBKR_HOST}")
        print(f"   Port: {auto_config.IBKR_PORT}")
        print(f"   Client ID: {auto_config.IBKR_CLIENT_ID}")
        print(f"   Timeout: {auto_config.IBKR_TIMEOUT}s")
        
        print("\n🚀 LANCEMENT SYSTÈME...")
        print("=" * 40)
        
        start_time = datetime.now()
        print(f"⏰ Démarrage: {start_time.strftime('%H:%M:%S')}")
        
        # Lancer le système principal
        from launch_24_7_orderflow_trading import main
        
        print("✅ Système lancé avec succès !")
        print("⏰ Timeout réduit - Connexion plus rapide")
        print("🛑 Appuyez sur Ctrl+C pour arrêter")
        
        # Lancer le système
        await main()
        
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
    asyncio.run(lance_systeme_timeout_corrige())






