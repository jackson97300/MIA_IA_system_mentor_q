#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Scanner Symboles TWS
Scanne tous les symboles disponibles dans TWS et leurs prix
"""

import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def scanner_symboles_tws():
    """Scanne tous les symboles disponibles dans TWS"""
    
    print("MIA_IA_SYSTEM - SCANNER SYMBOLES TWS")
    print("=" * 60)
    print("Scan de tous les symboles disponibles dans TWS")
    print("Recherche du contrat ES Sept19 (6469.25)")
    print("=" * 60)

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
        
        # 2. SCAN SYMBOLES ES
        print("\n2. SCAN SYMBOLES ES")
        print("=" * 30)
        
        # Liste des symboles ES possibles
        es_symbols = [
            "ES", "ESU5", "ESZ4", "ESF5", "ESH5", "ESM5", "ESJ5", "ESK5", "ESN5", "ESQ5",
            "ESU4", "ESZ3", "ESF4", "ESH4", "ESM4", "ESJ4", "ESK4", "ESN4", "ESQ4",
            "ESU3", "ESZ2", "ESF3", "ESH3", "ESM3", "ESJ3", "ESK3", "ESN3", "ESQ3"
        ]
        
        found_symbols = []
        target_price = 6469.25
        
        for symbol in es_symbols:
            print(f"\nTest: {symbol}")
            
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
                    
                    # Vérifier si c'est le bon prix
                    difference = abs(prix - target_price)
                    
                    if difference < 10:
                        print(f"   *** MATCH TROUVE! *** (diff: {difference})")
                        found_symbols.append({
                            'symbol': symbol,
                            'price': prix,
                            'difference': difference,
                            'volume': volume,
                            'bid': bid,
                            'ask': ask
                        })
                    elif difference < 100:
                        print(f"   Prix proche (diff: {difference})")
                        found_symbols.append({
                            'symbol': symbol,
                            'price': prix,
                            'difference': difference,
                            'volume': volume,
                            'bid': bid,
                            'ask': ask
                        })
                else:
                    print(f"   Aucune donnee")
                    
            except Exception as e:
                print(f"   Erreur: {e}")
            
            # Pause pour éviter de surcharger TWS
            await asyncio.sleep(0.5)
        
        # 3. SCAN SYMBOLES GENERAUX
        print("\n3. SCAN SYMBOLES GENERAUX")
        print("=" * 30)
        
        # Autres symboles à tester
        other_symbols = [
            "SPX", "SPY", "QQQ", "IWM", "VIX", "NQ", "YM", "RTY", "CL", "GC", "SI", "ZB", "ZN", "ZF"
        ]
        
        for symbol in other_symbols:
            print(f"\nTest: {symbol}")
            
            try:
                data = await ibkr.get_market_data(symbol)
                
                if data:
                    prix = data.get('last', 0)
                    volume = data.get('volume', 0)
                    
                    print(f"   Prix: {prix}")
                    print(f"   Volume: {volume}")
                    
                    # Vérifier si c'est proche du prix ES
                    difference = abs(prix - target_price)
                    
                    if difference < 100:
                        print(f"   Prix proche ES (diff: {difference})")
                        found_symbols.append({
                            'symbol': symbol,
                            'price': prix,
                            'difference': difference,
                            'volume': volume,
                            'bid': data.get('bid', 0),
                            'ask': data.get('ask', 0)
                        })
                else:
                    print(f"   Aucune donnee")
                    
            except Exception as e:
                print(f"   Erreur: {e}")
            
            await asyncio.sleep(0.3)
        
        # 4. RESULTATS
        print("\n4. RESULTATS DU SCAN")
        print("=" * 30)
        
        if found_symbols:
            print(f"Symboles trouves: {len(found_symbols)}")
            print("\nSymboles par difference de prix:")
            
            # Trier par différence
            found_symbols.sort(key=lambda x: x['difference'])
            
            for i, symbol_info in enumerate(found_symbols[:10]):  # Top 10
                print(f"{i+1}. {symbol_info['symbol']}: {symbol_info['price']} (diff: {symbol_info['difference']})")
                print(f"   Volume: {symbol_info['volume']}, Bid: {symbol_info['bid']}, Ask: {symbol_info['ask']}")
            
            # Meilleur match
            best_match = found_symbols[0]
            print(f"\nMEILLEUR MATCH: {best_match['symbol']}")
            print(f"Prix: {best_match['price']} (diff: {best_match['difference']})")
            
            if best_match['difference'] < 5:
                print("SUCCES: Symbole exact trouve!")
                return True
            else:
                print("ATTENTION: Aucun symbole exact trouve")
                print("Utilisez le meilleur match disponible")
                
        else:
            print("AUCUN SYMBOLE TROUVE")
            print("Verifiez la connexion TWS et les donnees")
        
        # 5. SAUVEGARDE RESULTATS
        print("\n5. SAUVEGARDE RESULTATS")
        print("=" * 30)
        
        if found_symbols:
            import json
            from datetime import datetime
            
            results = {
                "timestamp": datetime.now().isoformat(),
                "target_price": target_price,
                "symbols_found": found_symbols,
                "best_match": found_symbols[0] if found_symbols else None
            }
            
            with open("symboles_tws_scan.json", "w") as f:
                json.dump(results, f, indent=2)
            
            print("Resultats sauvegardes dans: symboles_tws_scan.json")
        
        await ibkr.disconnect()
        return len(found_symbols) > 0
        
    except Exception as e:
        print(f"ERREUR GENERALE: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(scanner_symboles_tws())
    
    if success:
        print("\nSUCCES: Scan termine")
        print("Consultez les resultats ci-dessus")
        print("Fichier de resultats: symboles_tws_scan.json")
    else:
        print("\nECHEC: Probleme lors du scan")
        print("Verifiez la connexion TWS")





