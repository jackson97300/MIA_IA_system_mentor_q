#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Diagnostic Complet API TWS
Diagnostic complet pour comprendre pourquoi l'API ne recupere aucune donnee
"""

import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def diagnostic_complet_api_tws():
    """Diagnostic complet de l'API TWS"""
    
    print("MIA_IA_SYSTEM - DIAGNOSTIC COMPLET API TWS")
    print("=" * 60)
    print("Diagnostic complet pour comprendre le probleme")
    print("=" * 60)

    try:
        from core.ibkr_connector import IBKRConnector
        
        # Configuration TWS LIVE
        ibkr = IBKRConnector()
        ibkr.host = "127.0.0.1"
        ibkr.port = 7496  # TWS LIVE
        ibkr.client_id = 1
        ibkr.timeout = 15
        
        print("\n1. TEST CONNEXION BASIQUE")
        print("=" * 30)
        
        await ibkr.connect()
        
        if not await ibkr.is_connected():
            print("ECHEC: Impossible de se connecter")
            return False
            
        print("SUCCES: Connexion etablie")
        
        # 2. TEST METHODES DISPONIBLES
        print("\n2. TEST METHODES DISPONIBLES")
        print("=" * 30)
        
        # Vérifier les méthodes disponibles
        methods = [method for method in dir(ibkr) if not method.startswith('_')]
        print(f"Methodes disponibles: {len(methods)}")
        
        # Méthodes importantes
        important_methods = ['get_market_data', 'is_connected', 'connect', 'disconnect']
        for method in important_methods:
            if hasattr(ibkr, method):
                print(f"   {method}: DISPONIBLE")
            else:
                print(f"   {method}: MANQUANT")
        
        # 3. TEST DONNEES SIMPLES
        print("\n3. TEST DONNEES SIMPLES")
        print("=" * 30)
        
        # Test avec des symboles très basiques
        basic_symbols = ["AAPL", "MSFT", "SPY"]
        
        for symbol in basic_symbols:
            print(f"\nTest {symbol}:")
            
            try:
                # Test direct de la méthode
                if hasattr(ibkr, 'get_market_data'):
                    data = await ibkr.get_market_data(symbol)
                    
                    if data:
                        print(f"   SUCCES: Donnees recuperees")
                        print(f"   Type: {type(data)}")
                        print(f"   Contenu: {data}")
                    else:
                        print(f"   ECHEC: Aucune donnee")
                else:
                    print(f"   ERREUR: Methode get_market_data non disponible")
                    
            except Exception as e:
                print(f"   ERREUR: {e}")
        
        # 4. TEST CONTRAT SPECIFIQUE
        print("\n4. TEST CONTRAT SPECIFIQUE")
        print("=" * 30)
        
        try:
            # Essayer de créer un contrat manuellement
            from ib_insync import Contract
            
            contract = Contract()
            contract.symbol = "ES"
            contract.secType = "FUT"
            contract.exchange = "CME"
            contract.currency = "USD"
            contract.lastTradingDay = "20250919"
            
            print("Contrat cree manuellement:")
            print(f"   Symbol: {contract.symbol}")
            print(f"   Type: {contract.secType}")
            print(f"   Exchange: {contract.exchange}")
            print(f"   Expiration: {contract.lastTradingDay}")
            
            # Test avec le contrat
            if hasattr(ibkr, 'client') and ibkr.client:
                print("Client ib_insync disponible")
                
                # Essayer de récupérer les données du contrat
                try:
                    # Test avec reqMktData
                    ibkr.client.reqMktData(1, contract, "", False, False, [])
                    await asyncio.sleep(2)
                    
                    # Vérifier si des données sont arrivées
                    print("Requete MktData envoyee")
                    
                except Exception as e:
                    print(f"ERREUR reqMktData: {e}")
            else:
                print("Client ib_insync non disponible")
                
        except Exception as e:
            print(f"ERREUR contrat: {e}")
        
        # 5. VERIFICATION CONFIGURATION TWS
        print("\n5. VERIFICATION CONFIGURATION TWS")
        print("=" * 30)
        
        print("CONFIGURATION REQUISE DANS TWS:")
        print("1. File > Global Configuration")
        print("2. API > Settings")
        print("3. Enable ActiveX and Socket Clients: OUI")
        print("4. Port: 7496 (LIVE)")
        print("5. Allow connections from localhost: OUI")
        print("6. Read-Only API: NON")
        print("7. Download open orders on connection: OUI")
        print("8. Include FX positions in portfolio: OUI")
        
        # 6. TEST ALTERNATIF
        print("\n6. TEST ALTERNATIF")
        print("=" * 30)
        
        try:
            # Essayer d'accéder directement au client ib_insync
            if hasattr(ibkr, 'client') and ibkr.client:
                print("Acces direct au client ib_insync")
                
                # Vérifier l'état du client
                print(f"   Connecte: {ibkr.client.isConnected()}")
                print(f"   Host: {ibkr.client.host}")
                print(f"   Port: {ibkr.client.port}")
                print(f"   ClientId: {ibkr.client.clientId}")
                
                # Test simple
                try:
                    # Essayer de récupérer des informations de compte
                    account_info = ibkr.client.accountSummary()
                    print(f"   Comptes: {len(account_info)}")
                except Exception as e:
                    print(f"   ERREUR accountSummary: {e}")
            else:
                print("Client ib_insync non accessible")
                
        except Exception as e:
            print(f"ERREUR acces direct: {e}")
        
        # 7. SOLUTIONS PROPOSEES
        print("\n7. SOLUTIONS PROPOSEES")
        print("=" * 30)
        
        print("PROBLEMES POSSIBLES:")
        print("1. API non activee dans TWS")
        print("2. Mauvais port (7496 vs 7497)")
        print("3. Client ID en conflit")
        print("4. Donnees de marche non disponibles")
        print("5. Compte en mode read-only")
        print("6. Problème de permissions")
        
        print("\nSOLUTIONS:")
        print("1. Redemarrer TWS")
        print("2. Verifier la configuration API")
        print("3. Essayer un autre Client ID")
        print("4. Verifier les donnees de marche")
        print("5. Tester avec TWS Paper (port 7497)")
        
        await ibkr.disconnect()
        return True
        
    except Exception as e:
        print(f"ERREUR GENERALE: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(diagnostic_complet_api_tws())
    
    print("\nRESUME:")
    print("=" * 40)
    print("Diagnostic termine")
    print("Verifiez la configuration TWS")
    print("Puis testez avec TWS Paper si necessaire")





