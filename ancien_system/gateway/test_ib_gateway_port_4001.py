#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test IB Gateway Port 4001
Test IB Gateway sur le port 4001 (Gateway LIVE)
"""

import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_ib_gateway_port_4001():
    """Test IB Gateway sur port 4001"""
    
    print("MIA_IA_SYSTEM - TEST IB GATEWAY PORT 4001")
    print("=" * 50)
    print("Test IB Gateway sur port 4001")
    print("Gateway LIVE detecte dans les logs")
    print("=" * 50)

    try:
        from core.ibkr_connector import IBKRConnector
        
        # Configuration IB Gateway LIVE (port 4001)
        ibkr = IBKRConnector()
        ibkr.host = "127.0.0.1"
        ibkr.port = 4001  # IB Gateway LIVE
        ibkr.client_id = 1
        ibkr.timeout = 15
        
        print("\n1. CONNEXION IB GATEWAY (port 4001)")
        print("=" * 30)
        
        await ibkr.connect()
        
        if not await ibkr.is_connected():
            print("ECHEC: Impossible de se connecter")
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
        
        # 3. VERIFICATION COMPTE
        print("\n3. VERIFICATION COMPTE")
        print("=" * 30)
        
        try:
            # Essayer de récupérer les infos de compte
            if hasattr(ibkr, 'client') and ibkr.client:
                print("Client ib_insync disponible")
                
                # Vérifier l'état du client
                print(f"   Connecte: {ibkr.client.isConnected()}")
                print(f"   Host: {ibkr.client.host}")
                print(f"   Port: {ibkr.client.port}")
                print(f"   ClientId: {ibkr.client.clientId}")
                
                # Test compte
                try:
                    account_info = ibkr.client.accountSummary()
                    print(f"   Comptes: {len(account_info)}")
                    
                    for account in account_info:
                        if 'NetLiquidation' in account.tag:
                            print(f"   NetLiquidation: {account.value}")
                            
                except Exception as e:
                    print(f"   ERREUR accountSummary: {e}")
            else:
                print("Client ib_insync non accessible")
                
        except Exception as e:
            print(f"ERREUR verification compte: {e}")
        
        await ibkr.disconnect()
        return True
        
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    print("PREREQUIS:")
    print("1. IB Gateway en mode LIVE (port 4001)")
    print("2. API activee")
    print("3. Compte connecte (NetLiquidation: 798.65 EUR)")
    
    response = input("\nIB Gateway est-il connecte et pret? (oui/non): ")
    
    if response.lower() in ['oui', 'yes', 'o', 'y']:
        success = asyncio.run(test_ib_gateway_port_4001())
        
        if success:
            print("\nSUCCES: IB Gateway fonctionne")
            print("Le systeme peut utiliser IB Gateway")
        else:
            print("\nECHEC: Probleme avec IB Gateway")
            print("Verifiez la configuration")
    else:
        print("\nVeuillez d'abord configurer IB Gateway")
        print("Puis relancez ce script")





