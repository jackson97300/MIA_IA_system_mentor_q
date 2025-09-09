#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test API Rapide
Test rapide de connexion API IBKR avec TWS
"""

import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_api_rapide():
    """Test rapide de connexion API IBKR"""
    
    print("MIA_IA_SYSTEM - TEST API RAPIDE")
    print("=" * 50)
    
    try:
        from core.ibkr_connector import IBKRConnector
        
        # Configuration pour TWS
        ibkr = IBKRConnector()
        ibkr.host = "127.0.0.1"
        ibkr.port = 7497  # Port TWS
        ibkr.client_id = 1
        ibkr.timeout = 15  # Timeout court
        
        print("Test connexion TWS (port 7497)...")
        print("Client ID: 1")
        print("Timeout: 15 secondes")
        
        await ibkr.connect()
        
        if await ibkr.is_connected():
            print("SUCCES: API connectee!")
            
            # Test donnees rapide
            try:
                data = await ibkr.get_market_data("ES")
                if data:
                    print("SUCCES: Donnees ES recuperees")
                    print(f"   Prix: {data.get('last', 'N/A')}")
                    print(f"   Volume: {data.get('volume', 'N/A')}")
                    print(f"   Bid: {data.get('bid', 'N/A')}")
                    print(f"   Ask: {data.get('ask', 'N/A')}")
                else:
                    print("ATTENTION: Aucune donnee ES")
            except Exception as e:
                print(f"ATTENTION: Erreur donnees ES: {e}")
            
            await ibkr.disconnect()
            return True
        else:
            print("ECHEC: API non connectee")
            return False
            
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api_rapide())
    
    if success:
        print("\nSUCCES: Test API reussi")
        print("Le systeme est pret pour le lancement")
    else:
        print("\nECHEC: Test API echoue")
        print("Verifiez la configuration API dans TWS")





