#!/usr/bin/env python3
"""
🔍 Recherche ConID ES Sep19'25 - Web API IBKR
Script qui utilise l'API Web IBKR pour trouver le ConID correct
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def find_es_sep25_conid_web_api():
    """Trouver le ConID ES Sep19'25 via Web API IBKR"""
    print("🔍 Recherche ConID ES Sep19'25 - Web API IBKR")
    print("="*60)
    
    base_url = "https://localhost:5000/v1/api"
    
    # Créer une session avec SSL désactivé
    session = requests.Session()
    session.verify = False
    
    try:
        # 1. Vérifier l'authentification
        print("🔐 Vérification authentification...")
        auth_response = session.get(
            f"{base_url}/iserver/auth/status",
            timeout=10
        )
        
        if auth_response.status_code != 200:
            print("❌ Problème d'authentification")
            return None
        
        auth_data = auth_response.json()
        if not auth_data.get('authenticated'):
            print("❌ Non authentifié")
            return None
        
        print("✅ Authentifié")
        
        # 2. Rechercher tous les futures ES sur GLOBEX
        print(f"\n📈 Recherche futures ES sur GLOBEX...")
        
        search_response = session.get(
            f"{base_url}/iserver/secdef/search",
            params={
                "symbol": "ES",
                "secType": "FUT",
                "exchange": "GLOBEX"
            },
            timeout=10
        )
        
        print(f"  Status: {search_response.status_code}")
        
        if search_response.status_code == 200:
            contracts = search_response.json()
            print(f"  Résultats: {len(contracts)} contrats trouvés")
            
            # Afficher tous les contrats pour debug
            print(f"\n📋 Liste des contrats ES trouvés:")
            for i, contract in enumerate(contracts):
                conid = contract.get('conid')
                symbol = contract.get('symbol')
                description = contract.get('description')
                secType = contract.get('secType')
                exchange = contract.get('exchange')
                expiry = contract.get('expiry')
                currency = contract.get('currency')
                
                print(f"    {i+1}. ConID: {conid}")
                print(f"       Symbol: {symbol}")
                print(f"       Description: {description}")
                print(f"       Type: {secType}")
                print(f"       Exchange: {exchange}")
                print(f"       Expiry: {expiry}")
                print(f"       Currency: {currency}")
                
                # Chercher ES Sep19'25 (expiry = 202509)
                if (symbol == "ES" and 
                    secType == "FUT" and
                    exchange == "GLOBEX" and
                    expiry == "202509"):
                    print(f"       ✅ CONTRAT ES Sep19'25 TROUVÉ!")
                    return conid
                
                print()
        else:
            print(f"  ❌ Erreur {search_response.status_code}")
            print(f"  Response: {search_response.text}")
        
        # 3. Si pas trouvé, essayer avec CME
        print(f"\n🔍 Essai avec exchange CME...")
        
        search_response = session.get(
            f"{base_url}/iserver/secdef/search",
            params={
                "symbol": "ES",
                "secType": "FUT",
                "exchange": "CME"
            },
            timeout=10
        )
        
        print(f"  Status: {search_response.status_code}")
        
        if search_response.status_code == 200:
            contracts = search_response.json()
            print(f"  Résultats: {len(contracts)} contrats trouvés")
            
            for i, contract in enumerate(contracts):
                conid = contract.get('conid')
                symbol = contract.get('symbol')
                description = contract.get('description')
                secType = contract.get('secType')
                exchange = contract.get('exchange')
                expiry = contract.get('expiry')
                currency = contract.get('currency')
                
                print(f"    {i+1}. ConID: {conid}")
                print(f"       Symbol: {symbol}")
                print(f"       Description: {description}")
                print(f"       Type: {secType}")
                print(f"       Exchange: {exchange}")
                print(f"       Expiry: {expiry}")
                print(f"       Currency: {currency}")
                
                # Chercher ES Sep19'25 (expiry = 202509)
                if (symbol == "ES" and 
                    secType == "FUT" and
                    exchange == "CME" and
                    expiry == "202509"):
                    print(f"       ✅ CONTRAT ES Sep19'25 TROUVÉ!")
                    return conid
                
                print()
        else:
            print(f"  ❌ Erreur {search_response.status_code}")
        
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_contract_details(conid):
    """Récupérer les détails du contrat"""
    if not conid:
        return None
    
    print(f"\n📋 Détails du contrat ConID: {conid}")
    print("="*50)
    
    base_url = "https://localhost:5000/v1/api"
    session = requests.Session()
    session.verify = False
    
    try:
        # Récupérer les détails du contrat
        details_response = session.get(
            f"{base_url}/iserver/secdef/info",
            params={"conid": conid},
            timeout=10
        )
        
        print(f"Status: {details_response.status_code}")
        
        if details_response.status_code == 200:
            contract_data = details_response.json()
            print(f"Détails: {json.dumps(contract_data, indent=2)}")
            return contract_data
        else:
            print(f"❌ Erreur {details_response.status_code}")
            return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_market_data(conid):
    """Tester les données de marché pour le ConID"""
    if not conid:
        return None
    
    print(f"\n📊 Test données de marché pour ConID: {conid}")
    print("="*50)
    
    base_url = "https://localhost:5000/v1/api"
    session = requests.Session()
    session.verify = False
    
    try:
        # 1. Souscrire aux données
        print(f"📡 Souscription aux données...")
        
        subscribe_response = session.post(
            f"{base_url}/iserver/marketdata/snapshot",
            json={
                "conids": [conid],
                "fields": ["31", "83", "84", "86"]
            },
            timeout=10
        )
        
        print(f"  Souscription status: {subscribe_response.status_code}")
        
        if subscribe_response.status_code == 200:
            import time
            time.sleep(3)  # Attendre que les données arrivent
            
            # 2. Récupérer les données
            market_response = session.get(
                f"{base_url}/iserver/marketdata/snapshot",
                params={
                    "conids": conid,
                    "fields": "31,83,84,86"
                },
                timeout=10
            )
            
            print(f"  Récupération status: {market_response.status_code}")
            
            if market_response.status_code == 200:
                data = market_response.json()
                print(f"  Données reçues: {json.dumps(data, indent=2)}")
                
                if isinstance(data, list) and len(data) > 0:
                    tick_data = data[0]
                    
                    # Analyser les données
                    prices = {}
                    for key, value in tick_data.items():
                        if key == '31':
                            prices['bid'] = value
                        elif key == '83':
                            prices['ask'] = value
                        elif key == '84':
                            prices['last'] = value
                        elif key == '86':
                            prices['volume'] = value
                    
                    if prices:
                        print(f"  💰 Prix trouvés:")
                        for price_type, value in prices.items():
                            print(f"    {price_type}: {value}")
                        
                        # Vérifier si le prix est réaliste pour ES
                        if prices.get('last'):
                            last_price = float(prices['last'])
                            print(f"  📊 Prix last: {last_price}")
                            
                            # Le prix ES devrait être autour de 6481
                            if 6000 <= last_price <= 7000:
                                print(f"  ✅ Prix réaliste pour ES!")
                                return prices
                            else:
                                print(f"  ⚠️ Prix suspect: {last_price}")
                        else:
                            print(f"  ⚠️ Pas de prix last")
                    else:
                        print(f"  ⚠️ Aucun prix trouvé")
                else:
                    print(f"  ⚠️ Pas de données dans la réponse")
            else:
                print(f"  ❌ Erreur récupération: {market_response.status_code}")
        else:
            print(f"  ❌ Erreur souscription: {subscribe_response.status_code}")
        
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def display_results(conid, contract_details, prices):
    """Afficher les résultats complets"""
    print(f"\n" + "="*70)
    print(f"🎯 RÉSULTATS FINAUX - ES Sep19'25")
    print(f"="*70)
    print(f"🕐 Timestamp: {datetime.now()}")
    print(f"🔢 ConID: {conid}")
    print(f"-"*70)
    
    if contract_details:
        print(f"📋 Détails du contrat:")
        print(f"   Symbol: {contract_details.get('symbol', 'N/A')}")
        print(f"   Description: {contract_details.get('description', 'N/A')}")
        print(f"   Exchange: {contract_details.get('exchange', 'N/A')}")
        print(f"   Currency: {contract_details.get('currency', 'N/A')}")
        print(f"   Expiry: {contract_details.get('expiry', 'N/A')}")
        print(f"   SecType: {contract_details.get('secType', 'N/A')}")
    
    if prices:
        print(f"\n💰 Prix de marché:")
        print(f"   Bid:     {prices.get('bid', 'N/A'):>10}")
        print(f"   Ask:     {prices.get('ask', 'N/A'):>10}")
        print(f"   Last:    {prices.get('last', 'N/A'):>10}")
        print(f"   Volume:  {prices.get('volume', 'N/A'):>10}")
        
        # Calculer le spread
        if prices.get('ask') and prices.get('bid'):
            try:
                spread = float(prices['ask']) - float(prices['bid'])
                print(f"   Spread:  {spread:>10.2f}")
            except:
                pass
        
        # Calculer la valeur en dollars
        if prices.get('last'):
            try:
                last_price = float(prices['last'])
                dollar_value = last_price * 50  # Multiplicateur ES
                tick_value = 12.50  # Valeur tick ES
                print(f"   Valeur contrat: ${dollar_value:,.2f}")
                print(f"   Valeur tick: ${tick_value}")
            except:
                pass
        
        # Vérifier la cohérence avec TWS
        if prices.get('bid') and prices.get('ask'):
            bid_price = float(prices['bid'])
            ask_price = float(prices['ask'])
            
            expected_bid = 6481.00
            expected_ask = 6481.25
            
            bid_diff = abs(bid_price - expected_bid)
            ask_diff = abs(ask_price - expected_ask)
            
            print(f"\n📊 Comparaison avec TWS:")
            print(f"   TWS Bid/Ask: {expected_bid}/{expected_ask}")
            print(f"   API Bid/Ask: {bid_price}/{ask_price}")
            print(f"   Diff Bid: {bid_diff:.2f}")
            print(f"   Diff Ask: {ask_diff:.2f}")
            
            if bid_diff < 1 and ask_diff < 1:
                print(f"   🎯 Prix parfaitement cohérent!")
            elif bid_diff < 10 and ask_diff < 10:
                print(f"   ✅ Prix cohérent")
            else:
                print(f"   ⚠️ Prix différent")
    
    print(f"="*70)

def main():
    """Fonction principale"""
    print("🚀 Recherche ConID ES Sep19'25 - Web API IBKR")
    print("="*60)
    
    # 1. Trouver le ConID
    conid = find_es_sep25_conid_web_api()
    
    if conid:
        print(f"\n✅ ConID trouvé: {conid}")
        
        # 2. Récupérer les détails du contrat
        contract_details = get_contract_details(conid)
        
        # 3. Tester les données de marché
        prices = test_market_data(conid)
        
        # 4. Afficher les résultats
        display_results(conid, contract_details, prices)
        
        if prices:
            print(f"\n🎯 SUCCÈS! Prix ES Sep19'25 récupérés avec succès!")
        else:
            print(f"\n⚠️ ConID trouvé mais pas de données de marché")
            print(f"🔧 Problèmes possibles:")
            print(f"  - Heures de trading")
            print(f"  - Permissions de données de marché")
            print(f"  - Problème API IBKR")
    else:
        print(f"\n❌ ConID non trouvé")
        print(f"🔧 Problèmes possibles:")
        print(f"  - Contrat non disponible")
        print(f"  - Problème de recherche")
        print(f"  - Heures de trading")
        print(f"  - Paramètres de recherche incorrects")
    
    print(f"\n👋 Script terminé")

if __name__ == "__main__":
    main()

