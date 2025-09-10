#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Diagnostic Prix TWS vs API
Diagnostique pourquoi les prix TWS et API sont differents
"""

import os
import sys
import asyncio
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def diagnostic_prix_tws_vs_api():
    """Diagnostique les differences de prix"""
    
    print("MIA_IA_SYSTEM - DIAGNOSTIC PRIX TWS vs API")
    print("=" * 60)
    print("Analyse des differences de prix entre TWS et API")
    print("=" * 60)

    try:
        from core.ibkr_connector import IBKRConnector
        
        # Configuration
        ibkr = IBKRConnector()
        ibkr.host = "127.0.0.1"
        ibkr.port = 7496  # TWS LIVE
        ibkr.client_id = 1
        ibkr.timeout = 15
        
        print("\n1. CONNEXION ET RECUPERATION DONNEES")
        print("=" * 40)
        
        await ibkr.connect()
        
        if not await ibkr.is_connected():
            print("ECHEC: Impossible de se connecter")
            return False
            
        print("SUCCES: Connexion etablie")
        
        # 2. ANALYSE DONNEES ES
        print("\n2. ANALYSE DONNEES ES")
        print("=" * 40)
        
        # Test multiple pour voir la variabilite
        for i in range(5):
            print(f"\nTest {i+1}/5:")
            
            data = await ibkr.get_market_data("ES")
            if data:
                prix = data.get('last', 0)
                volume = data.get('volume', 0)
                bid = data.get('bid', 0)
                ask = data.get('ask', 0)
                timestamp = data.get('timestamp', 'N/A')
                source = data.get('source', 'N/A')
                
                print(f"   Prix: {prix}")
                print(f"   Volume: {volume}")
                print(f"   Bid: {bid}")
                print(f"   Ask: {ask}")
                print(f"   Timestamp: {timestamp}")
                print(f"   Source: {source}")
                
                # Verification coherence
                if bid and ask and prix:
                    spread = ask - bid
                    mid_price = (bid + ask) / 2
                    print(f"   Spread: {spread}")
                    print(f"   Mid-price: {mid_price}")
                    
                    if abs(prix - mid_price) > 10:
                        print(f"   ALERTE: Prix loin du mid-price!")
            else:
                print("   ATTENTION: Aucune donnee")
            
            await asyncio.sleep(1)  # Pause 1 seconde
        
        # 3. VERIFICATION CONTRAT
        print("\n3. VERIFICATION CONTRAT")
        print("=" * 40)
        
        try:
            # Essayer de recuperer les details du contrat
            contract_info = await ibkr.get_contract_details("ES")
            if contract_info:
                print("DETAILS CONTRAT:")
                print(f"   Symbole: {contract_info.get('symbol', 'N/A')}")
                print(f"   Exchange: {contract_info.get('exchange', 'N/A')}")
                print(f"   Type: {contract_info.get('secType', 'N/A')}")
                print(f"   Expiration: {contract_info.get('lastTradingDay', 'N/A')}")
                print(f"   Local Symbol: {contract_info.get('localSymbol', 'N/A')}")
                print(f"   Multiplier: {contract_info.get('multiplier', 'N/A')}")
            else:
                print("ATTENTION: Impossible de recuperer les details du contrat")
        except Exception as e:
            print(f"ERREUR details contrat: {e}")
        
        # 4. POSSIBLES CAUSES
        print("\n4. POSSIBLES CAUSES")
        print("=" * 40)
        
        print("DIFFERENCES DE PRIX POSSIBLES:")
        print("1. Contrat different (ESZ4 vs ESF5 vs ESU5)")
        print("2. Delai de mise a jour (TWS vs API)")
        print("3. Source de donnees differente")
        print("4. Mode de donnees (realtime vs delayed)")
        print("5. Cache vs donnees fraiches")
        print("6. Probleme de synchronisation")
        
        # 5. SOLUTIONS
        print("\n5. SOLUTIONS")
        print("=" * 40)
        
        print("SOLUTIONS PROPOSEES:")
        print("1. Verifier le contrat exact dans TWS")
        print("2. Forcer les donnees real-time")
        print("3. Vider le cache")
        print("4. Synchroniser les timestamps")
        print("5. Utiliser le meme contrat que TWS")
        
        # 6. SCRIPT DE CORRECTION
        print("\n6. SCRIPT DE CORRECTION")
        print("=" * 40)
        
        script_correction = '''#!/usr/bin/env python3
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
'''
        
        with open("corriger_prix_tws.py", "w") as f:
            f.write(script_correction)
        
        print("Script de correction cree: corriger_prix_tws.py")
        
        await ibkr.disconnect()
        return True
        
    except Exception as e:
        print(f"ERREUR GENERALE: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(diagnostic_prix_tws_vs_api())
    
    print("\nRESUME:")
    print("=" * 40)
    print("Les prix peuvent differer pour plusieurs raisons")
    print("Verifiez le contrat exact dans TWS")
    print("Puis testez avec: python corriger_prix_tws.py")





