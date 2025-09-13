#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Diagnostic Donnees Anormales ES
Diagnostique les donnees anormales d'ES (prix 6518)
"""

import os
import sys
import asyncio
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def diagnostic_donnees_anormales():
    """Diagnostique les donnees anormales d'ES"""
    
    print("MIA_IA_SYSTEM - DIAGNOSTIC DONNEES ANORMALES ES")
    print("=" * 60)
    print("Probleme detecte: Prix ES 6518.0 (anormalement eleve)")
    print("Plus haut historique ES: ~6475")
    print("=" * 60)

    try:
        from core.ibkr_connector import IBKRConnector
        
        # Configuration
        ibkr = IBKRConnector()
        ibkr.host = "127.0.0.1"
        ibkr.port = 7497
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
        
        # Test donnees actuelles
        data_current = await ibkr.get_market_data("ES")
        
        if data_current:
            print("DONNEES ACTUELLES ES:")
            print(f"   Prix: {data_current.get('last', 'N/A')}")
            print(f"   Volume: {data_current.get('volume', 'N/A')}")
            print(f"   Bid: {data_current.get('bid', 'N/A')}")
            print(f"   Ask: {data_current.get('ask', 'N/A')}")
            print(f"   Mode: {data_current.get('mode', 'N/A')}")
            print(f"   Source: {data_current.get('source', 'N/A')}")
            
            # Verification anormalite
            prix = data_current.get('last')
            if prix and prix > 6500:
                print(f"\nALERTE: Prix anormalement eleve: {prix}")
                print("Cela peut indiquer:")
                print("- Donnees simulees/fictives")
                print("- Mauvais contrat (futur lointain)")
                print("- Probleme de configuration")
                print("- Donnees en cache corrompues")
        
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
                print(f"   Multiplier: {contract_info.get('multiplier', 'N/A')}")
            else:
                print("ATTENTION: Impossible de recuperer les details du contrat")
        except Exception as e:
            print(f"ERREUR details contrat: {e}")
        
        # 4. TEST DONNEES HISTORIQUES
        print("\n4. TEST DONNEES HISTORIQUES")
        print("=" * 40)
        
        try:
            # Essayer de recuperer des donnees historiques
            hist_data = await ibkr.get_historical_data("ES", "1 D", "1 min")
            if hist_data:
                print(f"Donnees historiques recuperees: {len(hist_data)} points")
                
                # Analyser les prix historiques
                if len(hist_data) > 0:
                    prix_min = min([d.get('close', 0) for d in hist_data])
                    prix_max = max([d.get('close', 0) for d in hist_data])
                    print(f"   Prix min: {prix_min}")
                    print(f"   Prix max: {prix_max}")
                    
                    if prix_max > 6500:
                        print("ALERTE: Prix historiques aussi anormaux!")
                    else:
                        print("Prix historiques semblent normaux")
            else:
                print("ATTENTION: Aucune donnee historique")
        except Exception as e:
            print(f"ERREUR donnees historiques: {e}")
        
        # 5. VERIFICATION MODE SIMULATION
        print("\n5. VERIFICATION MODE SIMULATION")
        print("=" * 40)
        
        try:
            # Verifier si on est en mode simulation
            account_info = await ibkr.get_account_info()
            if account_info:
                print("INFO COMPTE:")
                print(f"   Type: {account_info.get('accountType', 'N/A')}")
                print(f"   Mode: {account_info.get('mode', 'N/A')}")
                
                if 'paper' in str(account_info).lower():
                    print("ATTENTION: Compte paper detecte")
                    print("Les donnees peuvent etre simulees")
            else:
                print("ATTENTION: Impossible de recuperer les infos compte")
        except Exception as e:
            print(f"ERREUR infos compte: {e}")
        
        # 6. SOLUTIONS PROPOSEES
        print("\n6. SOLUTIONS PROPOSEES")
        print("=" * 40)
        
        print("PROBLEME IDENTIFIE: Donnees anormales (prix 6518)")
        print("\nSOLUTIONS:")
        print("1. Verifier le contrat ES (doit etre ESZ4 ou ESF5)")
        print("2. S'assurer que TWS est en mode LIVE (pas paper)")
        print("3. Vider le cache des donnees")
        print("4. Redemarrer TWS")
        print("5. Verifier la connexion aux donnees de marche")
        
        # 7. SCRIPT DE CORRECTION
        print("\n7. SCRIPT DE CORRECTION")
        print("=" * 40)
        
        script_correction = '''#!/usr/bin/env python3
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
'''
        
        with open("corriger_donnees_es.py", "w") as f:
            f.write(script_correction)
        
        print("Script de correction cree: corriger_donnees_es.py")
        
        await ibkr.disconnect()
        return True
        
    except Exception as e:
        print(f"ERREUR GENERALE: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(diagnostic_donnees_anormales())
    
    print("\nRESUME:")
    print("=" * 40)
    print("Le prix ES de 6518 est anormalement eleve")
    print("Cela indique un probleme de donnees")
    print("Suivez les solutions proposees")
    print("Puis testez avec: python corriger_donnees_es.py")





