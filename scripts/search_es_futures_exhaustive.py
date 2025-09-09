#!/usr/bin/env python3
"""
🔍 Recherche exhaustive ES Sep19'25
Script qui fait une recherche complète pour trouver le vrai ConID d'ES futures
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def search_es_futures_exhaustive():
    """Recherche exhaustive pour ES Sep19'25"""
    print("🔍 Recherche exhaustive ES Sep19'25")
    print("="*50)
    
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
        
        # 2. Recherche exhaustive avec différents paramètres
        print(f"\n📈 Recherche exhaustive ES futures...")
        
        # Différentes combinaisons de paramètres à tester
        search_combinations = [
            # Recherche simple ES
            {"symbol": "ES"},
            
            # ES avec secType FUT
            {"symbol": "ES", "secType": "FUT"},
            
            # ES avec exchange GLOBEX
            {"symbol": "ES", "exchange": "GLOBEX"},
            
            # ES avec exchange CME
            {"symbol": "ES", "exchange": "CME"},
            
            # ES FUT GLOBEX
            {"symbol": "ES", "secType": "FUT", "exchange": "GLOBEX"},
            
            # ES FUT CME
            {"symbol": "ES", "secType": "FUT", "exchange": "CME"},
            
            # ES avec currency USD
            {"symbol": "ES", "currency": "USD"},
            
            # ES FUT USD
            {"symbol": "ES", "secType": "FUT", "currency": "USD"},
            
            # ES FUT GLOBEX USD
            {"symbol": "ES", "secType": "FUT", "exchange": "GLOBEX", "currency": "USD"},
            
            # ES FUT CME USD
            {"symbol": "ES", "secType": "FUT", "exchange": "CME", "currency": "USD"},
        ]
        
        all_contracts = []
        
        for i, params in enumerate(search_combinations):
            print(f"\n🔍 Test {i+1}: {params}")
            
            search_response = session.get(
                f"{base_url}/iserver/secdef/search",
                params=params,
                timeout=10
            )
            
            print(f"  Status: {search_response.status_code}")
            
            if search_response.status_code == 200:
                contracts = search_response.json()
                print(f"  Résultats: {len(contracts)} contrats")
                
                for contract in contracts:
                    conid = contract.get('conid')
                    symbol = contract.get('symbol')
                    description = contract.get('description')
                    secType = contract.get('secType')
                    exchange = contract.get('exchange')
                    currency = contract.get('currency')
                    
                    # Ajouter à la liste si c'est un contrat ES
                    if symbol == "ES":
                        contract_info = {
                            'conid': conid,
                            'symbol': symbol,
                            'description': description,
                            'secType': secType,
                            'exchange': exchange,
                            'currency': currency,
                            'search_params': params
                        }
                        
                        # Éviter les doublons
                        if not any(c['conid'] == conid for c in all_contracts):
                            all_contracts.append(contract_info)
                            
                            print(f"    ✅ ConID: {conid}")
                            print(f"       Description: {description}")
                            print(f"       Type: {secType}")
                            print(f"       Exchange: {exchange}")
                            print(f"       Currency: {currency}")
            else:
                print(f"  ❌ Erreur {search_response.status_code}")
        
        # 3. Analyser tous les contrats trouvés
        print(f"\n📋 Analyse de {len(all_contracts)} contrats ES trouvés:")
        
        es_futures = []
        for contract in all_contracts:
            conid = contract['conid']
            description = contract['description']
            secType = contract['secType']
            
            print(f"\n🔍 ConID: {conid}")
            print(f"   Description: {description}")
            print(f"   Type: {secType}")
            
            # Vérifier si c'est un future ES
            if secType == "FUT":
                es_futures.append(contract)
                print(f"   ✅ Future ES détecté")
                
                # Vérifier si c'est Sep19'25
                if description and "Sep" in description and "2025" in description:
                    print(f"   🎯 ES Sep19'25 TROUVÉ!")
                    return contract
                elif description and "Sep" in description:
                    print(f"   📅 ES September détecté")
                elif description and "2025" in description:
                    print(f"   📅 ES 2025 détecté")
            else:
                print(f"   ❌ Pas un future")
        
        # 4. Si pas trouvé, essayer de récupérer les détails des futures ES
        print(f"\n🔍 Test détaillé des {len(es_futures)} futures ES...")
        
        for contract in es_futures:
            conid = contract['conid']
            print(f"\n📋 Détails ConID: {conid}")
            
            # Récupérer les détails complets
            details_response = session.get(
                f"{base_url}/iserver/secdef/info",
                params={"conid": conid},
                timeout=10
            )
            
            if details_response.status_code == 200:
                contract_data = details_response.json()
                print(f"  Détails: {json.dumps(contract_data, indent=2)}")
                
                # Vérifier si c'est ES Sep19'25
                symbol = contract_data.get('symbol')
                description = contract_data.get('description')
                secType = contract_data.get('secType')
                exchange = contract_data.get('exchange')
                expiry = contract_data.get('expiry')
                
                if (symbol == "ES" and 
                    "Sep" in str(description) and 
                    "2025" in str(description) and
                    secType == "FUT"):
                    print(f"  🎯 CONTRAT ES Sep19'25 TROUVÉ!")
                    return {
                        'conid': conid,
                        'contract_data': contract_data,
                        'search_info': contract
                    }
            else:
                print(f"  ❌ Erreur détails: {details_response.status_code}")
        
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_market_data_for_conid(conid):
    """Tester les données de marché pour un ConID"""
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
            time.sleep(3)
            
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
                print(f"  Données: {json.dumps(data, indent=2)}")
                
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

def display_results(result):
    """Afficher les résultats"""
    if not result:
        return
    
    print(f"\n" + "="*70)
    print(f"🎯 RÉSULTATS FINAUX - ES Sep19'25")
    print(f"="*70)
    print(f"🕐 Timestamp: {datetime.now()}")
    
    if 'conid' in result:
        conid = result['conid']
        print(f"🔢 ConID: {conid}")
        
        if 'contract_data' in result:
            contract = result['contract_data']
            print(f"-"*70)
            print(f"📋 Détails du contrat:")
            print(f"   Symbol: {contract.get('symbol', 'N/A')}")
            print(f"   Description: {contract.get('description', 'N/A')}")
            print(f"   Exchange: {contract.get('exchange', 'N/A')}")
            print(f"   Currency: {contract.get('currency', 'N/A')}")
            print(f"   Expiry: {contract.get('expiry', 'N/A')}")
            print(f"   SecType: {contract.get('secType', 'N/A')}")
        
        if 'prices' in result:
            prices = result['prices']
            print(f"\n💰 Prix de marché:")
            print(f"   Bid:     {prices.get('bid', 'N/A'):>10}")
            print(f"   Ask:     {prices.get('ask', 'N/A'):>10}")
            print(f"   Last:    {prices.get('last', 'N/A'):>10}")
            print(f"   Volume:  {prices.get('volume', 'N/A'):>10}")
            
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
    print("🚀 Recherche exhaustive ES Sep19'25")
    print("="*50)
    
    # Recherche exhaustive
    result = search_es_futures_exhaustive()
    
    if result:
        print(f"\n✅ ConID trouvé: {result.get('conid')}")
        
        # Tester les données de marché
        conid = result.get('conid')
        if conid:
            prices = test_market_data_for_conid(conid)
            if prices:
                result['prices'] = prices
        
        # Afficher les résultats
        display_results(result)
        
        if 'prices' in result:
            print(f"\n🎯 SUCCÈS! Prix ES Sep19'25 récupérés avec succès!")
        else:
            print(f"\n⚠️ ConID trouvé mais pas de données de marché")
    else:
        print(f"\n❌ Aucun contrat ES Sep19'25 trouvé")
        print(f"🔧 Problèmes possibles:")
        print(f"  - Contrat non disponible")
        print(f"  - Problème de recherche")
        print(f"  - Heures de trading")
        print(f"  - Permissions de données de marché")
    
    print(f"\n👋 Script terminé")

if __name__ == "__main__":
    main()

