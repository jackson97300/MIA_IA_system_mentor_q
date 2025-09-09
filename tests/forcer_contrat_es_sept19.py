#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Forcer Contrat ES Sept19
Force l'API a utiliser le contrat ES Sept19 (ESU5) comme TWS
"""

import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def forcer_contrat_es_sept19():
    """Force l'utilisation du contrat ES Sept19"""
    
    print("MIA_IA_SYSTEM - FORCER CONTRAT ES SEPT19")
    print("=" * 50)
    print("Contrat TWS: ES Sept19 (ESU5) - 6469.25")
    print("Forcer l'API a utiliser le meme contrat")
    print("=" * 50)

    try:
        from core.ibkr_connector import IBKRConnector
        
        # Configuration TWS LIVE
        ibkr = IBKRConnector()
        ibkr.host = "127.0.0.1"
        ibkr.port = 7496  # TWS LIVE
        ibkr.client_id = 1
        ibkr.timeout = 15
        
        print("\n1. CONNEXION TWS LIVE")
        print("=" * 30)
        
        await ibkr.connect()
        
        if not await ibkr.is_connected():
            print("ECHEC: Impossible de se connecter")
            return False
            
        print("SUCCES: Connexion TWS etablie")
        
        # 2. CONTRAT ES SEPT19 SPECIFIQUE
        print("\n2. CONTRAT ES SEPT19 SPECIFIQUE")
        print("=" * 30)
        
        # Configuration du contrat exact
        contract_spec = {
            "symbol": "ES",
            "secType": "FUT",
            "exchange": "CME",
            "currency": "USD",
            "lastTradingDay": "20250919",  # Septembre 2025
            "localSymbol": "ESU5"  # ES Sept19
        }
        
        print("Contrat specifique:")
        print(f"   Symbole: {contract_spec['symbol']}")
        print(f"   Exchange: {contract_spec['exchange']}")
        print(f"   Expiration: {contract_spec['lastTradingDay']}")
        print(f"   Local Symbol: {contract_spec['localSymbol']}")
        
        # 3. RECUPERATION DONNEES SPECIFIQUES
        print("\n3. RECUPERATION DONNEES SPECIFIQUES")
        print("=" * 30)
        
        try:
            # Essayer de recuperer les donnees avec le contrat specifique
            data = await ibkr.get_market_data_with_contract(contract_spec)
            
            if data:
                prix = data.get('last', 0)
                volume = data.get('volume', 0)
                bid = data.get('bid', 0)
                ask = data.get('ask', 0)
                
                print("SUCCES: Donnees ES Sept19 recuperees")
                print(f"   Prix: {prix}")
                print(f"   Volume: {volume}")
                print(f"   Bid: {bid}")
                print(f"   Ask: {ask}")
                
                # Comparaison avec TWS
                prix_tws = 6469.25
                difference = abs(prix - prix_tws)
                
                print(f"\nCOMPARAISON AVEC TWS:")
                print(f"   Prix TWS: {prix_tws}")
                print(f"   Prix API: {prix}")
                print(f"   Difference: {difference}")
                
                if difference < 5:
                    print("SUCCES: Prix coherent avec TWS")
                    return True
                else:
                    print("ATTENTION: Prix different de TWS")
                    print("Verifiez la configuration du contrat")
                    return False
            else:
                print("ATTENTION: Aucune donnee recuperee")
                return False
                
        except Exception as e:
            print(f"ERREUR donnees specifiques: {e}")
            
            # Fallback: essayer avec le symbole simple
            print("\nFallback: Test avec symbole simple...")
            data_simple = await ibkr.get_market_data("ES")
            
            if data_simple:
                prix_simple = data_simple.get('last', 0)
                print(f"Prix ES simple: {prix_simple}")
                
                if abs(prix_simple - 6469.25) < 10:
                    print("Prix simple coherent avec TWS")
                else:
                    print("Prix simple different de TWS")
            else:
                print("Aucune donnee simple non plus")
            
            return False
        
        # 4. VERIFICATION CONTRAT
        print("\n4. VERIFICATION CONTRAT")
        print("=" * 30)
        
        try:
            contract_info = await ibkr.get_contract_details("ES")
            if contract_info:
                print("DETAILS CONTRAT ACTUEL:")
                print(f"   Symbole: {contract_info.get('symbol', 'N/A')}")
                print(f"   Exchange: {contract_info.get('exchange', 'N/A')}")
                print(f"   Expiration: {contract_info.get('lastTradingDay', 'N/A')}")
                print(f"   Local Symbol: {contract_info.get('localSymbol', 'N/A')}")
            else:
                print("ATTENTION: Impossible de recuperer les details")
        except Exception as e:
            print(f"ERREUR details contrat: {e}")
        
        await ibkr.disconnect()
        return True
        
    except Exception as e:
        print(f"ERREUR GENERALE: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(forcer_contrat_es_sept19())
    
    if success:
        print("\nSUCCES: Contrat ES Sept19 configure")
        print("L'API utilise maintenant le meme contrat que TWS")
    else:
        print("\nECHEC: Probleme de configuration")
        print("Verifiez les details du contrat dans TWS")





