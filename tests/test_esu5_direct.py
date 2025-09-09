#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test ESU5 Direct
Test direct du symbole ESU5 (ES Sept19)
"""

import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_esu5_direct():
    """Test direct du symbole ESU5"""
    
    print("MIA_IA_SYSTEM - TEST ESU5 DIRECT")
    print("=" * 50)
    print("Test direct du symbole ESU5 (ES Sept19)")
    print("Prix TWS attendu: 6469.25")
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
        
        # 2. TEST SYMBOLES DIFFERENTS
        print("\n2. TEST SYMBOLES DIFFERENTS")
        print("=" * 30)
        
        symbols_to_test = ["ES", "ESU5", "ESZ4", "ESF5"]
        
        for symbol in symbols_to_test:
            print(f"\nTest symbole: {symbol}")
            
            try:
                data = await ibkr.get_market_data(symbol)
                
                if data:
                    prix = data.get('last', 0)
                    volume = data.get('volume', 0)
                    bid = data.get('bid', 0)
                    ask = data.get('ask', 0)
                    
                    print(f"   Prix: {prix}")
                    print(f"   Volume: {volume}")
                    print(f"   Bid: {bid}")
                    print(f"   Ask: {ask}")
                    
                    # Comparaison avec TWS
                    prix_tws = 6469.25
                    difference = abs(prix - prix_tws)
                    
                    if difference < 5:
                        print(f"   SUCCES: Prix coherent avec TWS (diff: {difference})")
                        print(f"   SYMBOLE CORRECT TROUVE: {symbol}")
                        return True
                    else:
                        print(f"   ATTENTION: Prix different (diff: {difference})")
                else:
                    print(f"   ATTENTION: Aucune donnee pour {symbol}")
                    
            except Exception as e:
                print(f"   ERREUR {symbol}: {e}")
        
        # 3. TEST AVEC SYMBOLE COMPLET
        print("\n3. TEST SYMBOLE COMPLET")
        print("=" * 30)
        
        try:
            # Essayer avec le symbole complet
            data_complet = await ibkr.get_market_data("ESU5")
            
            if data_complet:
                prix_complet = data_complet.get('last', 0)
                print(f"Prix ESU5 complet: {prix_complet}")
                
                if abs(prix_complet - 6469.25) < 10:
                    print("SUCCES: Prix ESU5 coherent")
                    return True
                else:
                    print("ATTENTION: Prix ESU5 different")
            else:
                print("Aucune donnee ESU5")
                
        except Exception as e:
            print(f"ERREUR ESU5 complet: {e}")
        
        # 4. VERIFICATION CONTRAT ACTUEL
        print("\n4. VERIFICATION CONTRAT ACTUEL")
        print("=" * 30)
        
        try:
            # Test avec le contrat par defaut
            data_defaut = await ibkr.get_market_data("ES")
            
            if data_defaut:
                prix_defaut = data_defaut.get('last', 0)
                print(f"Prix ES par defaut: {prix_defaut}")
                
                # Analyser la difference
                prix_tws = 6469.25
                difference = abs(prix_defaut - prix_tws)
                
                print(f"Difference avec TWS: {difference}")
                
                if difference < 50:
                    print("Prix proche de TWS (contrat different mais acceptable)")
                else:
                    print("Prix tres different de TWS")
                    
        except Exception as e:
            print(f"ERREUR contrat par defaut: {e}")
        
        await ibkr.disconnect()
        return False
        
    except Exception as e:
        print(f"ERREUR GENERALE: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_esu5_direct())
    
    if success:
        print("\nSUCCES: Symbole correct trouve")
        print("L'API peut maintenant utiliser le bon contrat")
    else:
        print("\nECHEC: Aucun symbole coherent trouve")
        print("Verifiez la configuration dans TWS")





