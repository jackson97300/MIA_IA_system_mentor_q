#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test Connexion IBKR Rapide Simple
Test rapide de connexion IBKR sans emojis
"""

import os
import sys
import asyncio
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_connexion_rapide():
    """Test rapide de connexion IBKR"""
    
    print("MIA_IA_SYSTEM - TEST CONNEXION IBKR RAPIDE")
    print("=" * 60)
    
    try:
        from core.ibkr_connector import IBKRConnector
        
        # Configuration rapide
        ibkr = IBKRConnector()
        ibkr.host = "127.0.0.1"
        ibkr.port = 7497  # TWS port
        ibkr.client_id = 1
        ibkr.timeout = 15  # Timeout reduit
        
        print("Connexion rapide TWS (port 7497)...")
        await ibkr.connect()
        
        if await ibkr.is_connected():
            print("SUCCES: Connexion reussie!")
            
            # Test donnees rapide
            data = await ibkr.get_market_data("ES")
            if data:
                print("SUCCES: Donnees ES recuperees")
                print(f"   Prix: {data.get('last', 'N/A')}")
                print(f"   Volume: {data.get('volume', 'N/A')}")
                print(f"   Bid: {data.get('bid', 'N/A')}")
                print(f"   Ask: {data.get('ask', 'N/A')}")
                print(f"   Mode: {data.get('mode', 'N/A')}")
            else:
                print("ATTENTION: Aucune donnee ES")
            
            await ibkr.disconnect()
            return True
        else:
            print("ECHEC: Connexion echouee")
            return False
            
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connexion_rapide())
    
    if success:
        print("\nSUCCES: Test connexion reussi")
        print("Le systeme est pret pour le lancement")
    else:
        print("\nECHEC: Test connexion echoue")
        print("Verifiez TWS/Gateway avant relance")






