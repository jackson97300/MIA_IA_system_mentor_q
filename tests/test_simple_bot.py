#!/usr/bin/env python3
"""
🧪 TEST SIMPLE BOT - MIA_IA_SYSTEM
===================================

Script simple pour tester le bot sans les erreurs d'indentation complexes
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.ibkr_connector import IBKRConnector

logger = get_logger(__name__)

async def test_simple_bot():
    """Test simple du bot en mode simulation"""
    
    print("🧪 TEST SIMPLE BOT - MODE SIMULATION")
    print("=" * 50)
    
    try:
        # Connexion IBKR en mode simulation
        connector = IBKRConnector(
            host='127.0.0.1',
            port=7497,
            client_id=100,
            mode='SIMULATION'
        )
        
        print("🔌 Connexion IBKR (simulation)...")
        if await connector.connect():
            print("✅ Connexion IBKR réussie")
            print("🎭 Mode: SIMULATION - Données simulées")
            
            # Test données ES
            print("\n📊 Test données ES...")
            es_data = await connector.get_market_data('ES')
            if es_data:
                print(f"✅ ES: {es_data.get('last', 'N/A')} (Vol: {es_data.get('volume', 0)})")
            else:
                print("❌ Pas de données ES")
            
            # Test données NQ
            print("\n📊 Test données NQ...")
            nq_data = await connector.get_market_data('NQ')
            if nq_data:
                print(f"✅ NQ: {nq_data.get('last', 'N/A')} (Vol: {nq_data.get('volume', 0)})")
            else:
                print("❌ Pas de données NQ")
            
            # Test options SPX
            print("\n📊 Test options SPX...")
            spx_data = await connector.get_spx_options_data()
            if spx_data:
                print(f"✅ SPX: Put/Call {spx_data.get('put_call_ratio', 'N/A')}")
                print(f"✅ Gamma: {spx_data.get('gamma_exposure', 'N/A')}")
            else:
                print("❌ Pas de données SPX")
            
            print("\n🎯 DIAGNOSTIC COMPLET:")
            print("✅ Connexion IBKR: OK")
            print("✅ Données ES: OK" if es_data else "❌ Données ES: ÉCHEC")
            print("✅ Données NQ: OK" if nq_data else "❌ Données NQ: ÉCHEC")
            print("✅ Options SPX: OK" if spx_data else "❌ Options SPX: ÉCHEC")
            
        else:
            print("❌ Échec connexion IBKR")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        if 'connector' in locals():
            await connector.disconnect()
            print("✅ Déconnexion IBKR")

if __name__ == "__main__":
    try:
        asyncio.run(test_simple_bot())
    except KeyboardInterrupt:
        print("\n👋 Arrêt du test")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")





