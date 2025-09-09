#!/usr/bin/env python3
"""
TEST CONNEXION FORCEE - DONNEES REELLES
MIA_IA_SYSTEM - Forcer connexion IBKR reelle
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.ibkr_connector import IBKRConnector

async def test_connexion_forcee():
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 7497,  # ✅ CORRECTION: TWS Paper Trading (FONCTIONNE)
        'ibkr_client_id': 999,
        'connection_timeout': 60,
        'simulation_mode': False,
        'require_real_data': True,
        'fallback_to_saved_data': False
    }
    
    print("🔗 Tentative connexion forcée...")
    connector = IBKRConnector(config)
    
    try:
        success = await connector.connect()
        
        if success:
            print("✅ Connexion IBKR RÉELLE réussie!")
            
            # Test données marché
            market_data = await connector.get_market_data("ES")
            if market_data:
                print("✅ Données marché réelles récupérées")
                print(f"   📈 Prix: {market_data.get('price', 'N/A')}")
                print(f"   📊 Volume: {market_data.get('volume', 'N/A')}")
                print("📊 Source: IBKR (données réelles)")
            else:
                print("❌ Erreur récupération données marché")
                return False
            
            await connector.disconnect()
            return True
        else:
            print("❌ Échec connexion IBKR")
            print("🔧 Vérifier configuration TWS")
            return False
            
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connexion_forcee())
    if success:
        print("\n🎉 CONNEXION IBKR RÉELLE RÉUSSIE!")
        print("🚀 Prêt pour trading avec données réelles")
    else:
        print("\n❌ CONNEXION IBKR ÉCHOUÉE")
        print("🔧 Corriger configuration TWS")
