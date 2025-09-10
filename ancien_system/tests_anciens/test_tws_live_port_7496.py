#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test TWS LIVE Port 7496
Test connexion TWS en mode LIVE sur le port 7496
"""

import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_tws_live_7496():
    """Test TWS LIVE sur port 7496"""
    
    print("MIA_IA_SYSTEM - TEST TWS LIVE PORT 7496")
    print("=" * 50)
    print("Test connexion TWS en mode LIVE")
    print("Port: 7496 (TWS LIVE)")
    print("=" * 50)

    try:
        from core.ibkr_connector import IBKRConnector
        
        # Configuration TWS LIVE
        ibkr = IBKRConnector()
        ibkr.host = "127.0.0.1"
        ibkr.port = 7496  # Port TWS LIVE
        ibkr.client_id = 1
        ibkr.timeout = 15
        
        print("Connexion TWS LIVE (port 7496)...")
        print("Client ID: 1")
        print("Timeout: 15 secondes")
        
        await ibkr.connect()
        
        if await ibkr.is_connected():
            print("SUCCES: Connexion TWS LIVE etablie!")
            
            # Test donnees ES
            data = await ibkr.get_market_data("ES")
            if data:
                prix = data.get('last', 0)
                volume = data.get('volume', 0)
                bid = data.get('bid', 0)
                ask = data.get('ask', 0)
                
                print("SUCCES: Donnees ES recuperees")
                print(f"   Prix: {prix}")
                print(f"   Volume: {volume}")
                print(f"   Bid: {bid}")
                print(f"   Ask: {ask}")
                
                # Verification prix normal
                if 6000 < prix < 6500:
                    print("SUCCES: Prix ES normal (mode LIVE)")
                    print("Le systeme est pret pour le trading")
                else:
                    print(f"ATTENTION: Prix anormal: {prix}")
                    print("Verifiez la configuration TWS")
            else:
                print("ATTENTION: Aucune donnee ES")
            
            await ibkr.disconnect()
            return True
        else:
            print("ECHEC: Impossible de se connecter")
            return False
            
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_tws_live_7496())
    
    if success:
        print("\nSUCCES: Test TWS LIVE reussi")
        print("Le systeme peut maintenant trader")
    else:
        print("\nECHEC: Test TWS LIVE echoue")
        print("Verifiez la configuration TWS")





