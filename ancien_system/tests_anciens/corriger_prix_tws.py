#!/usr/bin/env python3
import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def corriger_prix_tws():
    try:
        from core.ibkr_connector import IBKRConnector
        
        # Configuration avec contrat specifique
        ibkr = IBKRConnector()
        ibkr.host = "127.0.0.1"
        ibkr.port = 7496
        ibkr.client_id = 1
        
        await ibkr.connect()
        
        # Forcer le contrat exact (a adapter selon TWS)
        contract_spec = {
            "symbol": "ES",
            "secType": "FUT",
            "exchange": "CME",
            "currency": "USD",
            "lastTradingDay": "20241219",  # Decembre 2024
            "localSymbol": "ESZ4"  # A verifier dans TWS
        }
        
        # Forcer les donnees real-time
        data = await ibkr.get_market_data_with_contract(contract_spec)
        
        if data:
            prix = data.get('last', 0)
            print(f"Prix ES corrige: {prix}")
            
            # Comparer avec TWS
            print("Comparez ce prix avec celui de TWS")
            return True
        else:
            print("Aucune donnee recuperee")
            return False
            
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(corriger_prix_tws())
