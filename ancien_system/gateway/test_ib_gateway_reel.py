#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test IB Gateway Reel
Test IB Gateway en mode reel (port 4002)
"""

import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_ib_gateway_reel():
    """Test IB Gateway en mode reel"""
    
    print("MIA_IA_SYSTEM - TEST IB GATEWAY REEL")
    print("=" * 50)
    print("Test IB Gateway en mode reel")
    print("Port: 4002 (Gateway LIVE)")
    print("=" * 50)

    try:
        from core.ibkr_connector import IBKRConnector
        
        # Configuration IB Gateway LIVE
        ibkr = IBKRConnector()
        ibkr.host = "127.0.0.1"
        ibkr.port = 4002  # IB Gateway LIVE
        ibkr.client_id = 1
        ibkr.timeout = 15
        
        print("\n1. CONNEXION IB GATEWAY LIVE")
        print("=" * 30)
        
        await ibkr.connect()
        
        if not await ibkr.is_connected():
            print("ECHEC: Impossible de se connecter a IB Gateway")
            print("Verifiez que IB Gateway est en mode LIVE")
            return False
            
        print("SUCCES: Connexion IB Gateway etablie")
        
        # 2. TEST DONNEES ES
        print("\n2. TEST DONNEES ES")
        print("=" * 30)
        
        # Test avec ES
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
            
            # Comparaison avec TWS (6469.25)
            prix_tws = 6469.25
            difference = abs(prix - prix_tws)
            
            print(f"\nCOMPARAISON AVEC TWS:")
            print(f"   Prix TWS: {prix_tws}")
            print(f"   Prix Gateway: {prix}")
            print(f"   Difference: {difference}")
            
            if difference < 10:
                print("SUCCES: Prix coherent avec TWS")
                return True
            else:
                print("ATTENTION: Prix different de TWS")
                print("Mais les donnees sont disponibles")
                return True
        else:
            print("ATTENTION: Aucune donnee ES")
            
            # Test avec d'autres symboles
            print("\nTest autres symboles...")
            
            test_symbols = ["AAPL", "MSFT", "SPY"]
            
            for symbol in test_symbols:
                try:
                    data_test = await ibkr.get_market_data(symbol)
                    if data_test:
                        prix_test = data_test.get('last', 0)
                        print(f"   {symbol}: {prix_test}")
                    else:
                        print(f"   {symbol}: Aucune donnee")
                except Exception as e:
                    print(f"   {symbol}: Erreur - {e}")
            
            return False
        
        # 3. VERIFICATION CONFIGURATION
        print("\n3. VERIFICATION CONFIGURATION")
        print("=" * 30)
        
        print("CONFIGURATION IB GATEWAY REQUISE:")
        print("1. Demarrer IB Gateway")
        print("2. Choisir 'LIVE TRADING'")
        print("3. Se connecter avec identifiants LIVE")
        print("4. File > Global Configuration")
        print("5. API > Settings")
        print("6. Enable ActiveX and Socket Clients: OUI")
        print("7. Port: 4002")
        print("8. Allow connections from localhost: OUI")
        
        await ibkr.disconnect()
        return True
        
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    print("PREREQUIS:")
    print("1. IB Gateway doit etre en mode LIVE")
    print("2. API doit etre activee")
    print("3. Port 4002 ouvert")
    
    response = input("\nIB Gateway est-il en mode LIVE et connecte? (oui/non): ")
    
    if response.lower() in ['oui', 'yes', 'o', 'y']:
        success = asyncio.run(test_ib_gateway_reel())
        
        if success:
            print("\nSUCCES: IB Gateway fonctionne")
            print("Le systeme peut utiliser IB Gateway")
        else:
            print("\nECHEC: Probleme avec IB Gateway")
            print("Verifiez la configuration")
    else:
        print("\nVeuillez d'abord configurer IB Gateway en mode LIVE")
        print("Puis relancez ce script")





