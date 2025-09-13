#!/usr/bin/env python3
import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def corriger_donnees_es():
    try:
        from core.ibkr_connector import IBKRConnector
        
        # Configuration avec contrat specifique
        ibkr = IBKRConnector()
        ibkr.host = "127.0.0.1"
        ibkr.port = 7497
        ibkr.client_id = 1
        
        await ibkr.connect()
        
        # Forcer le bon contrat ES
        contract_spec = {
            "symbol": "ES",
            "secType": "FUT",
            "exchange": "CME",
            "currency": "USD",
            "lastTradingDay": "20241219",  # Decembre 2024
            "localSymbol": "ESZ4"
        }
        
        data = await ibkr.get_market_data_with_contract(contract_spec)
        
        if data:
            prix = data.get('last', 0)
            if 6000 < prix < 6500:
                print(f"SUCCES: Prix ES normal: {prix}")
                return True
            else:
                print(f"ALERTE: Prix toujours anormal: {prix}")
                return False
                
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(corriger_donnees_es())
