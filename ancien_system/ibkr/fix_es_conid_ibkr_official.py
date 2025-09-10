#!/usr/bin/env python3
"""
🔧 Fix ES ConID - Méthode Officielle IBKR
Script qui utilise les méthodes officielles IBKR pour trouver le bon ConID d'ES futures
Basé sur la documentation IBKR et les solutions Reddit
"""

import sys
import requests
import json
import time
from pathlib import Path
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning
import warnings

# Supprimer les warnings SSL pour localhost
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def authenticate_ibkr():
    """Authentification IBKR Client Portal Gateway"""
    print("🔐 Authentification IBKR...")
    
    base_url = "https://localhost:5000/v1/api"
    session = requests.Session()
    session.verify = False
    
    try:
        # 1. Vérifier le statut d'authentification
        auth_response = session.get(
            f"{base_url}/iserver/auth/status",
            timeout=10
        )
        
        if auth_response.status_code != 200:
            print(f"❌ Erreur authentification: {auth_response.status_code}")
            return None, None
        
        auth_data = auth_response.json()
        
        if auth_data.get('authenticated'):
            print("✅ Déjà authentifié")
            return session, base_url
        
        # 2. Si pas authentifié, essayer de s'authentifier
        print("🔑 Tentative d'authentification...")
        
        # Vérifier si une session existe
        session_response = session.get(
            f"{base_url}/iserver/validate",
            timeout=10
        )
        
        if session_response.status_code == 200:
            session_data = session_response.json()
            if session_data.get('authenticated'):
                print("✅ Authentification réussie")
                return session, base_url
        
        print("❌ Authentification requise - Ouvrir https://localhost:5000/sso/Dispatcher")
        return None, None
        
    except Exception as e:
        print(f"❌ Erreur authentification: {e}")
        return None, None

def search_es_futures_official(session, base_url):
    """Recherche ES futures avec méthode officielle IBKR"""
    print("\n🔍 Recherche ES futures - Méthode officielle IBKR")
    print("="*60)
    
    # Méthode 1: Recherche avec paramètres spécifiques pour futures
    search_methods = [
        {
            "name": "ES FUT GLOBEX USD",
            "params": {
                "symbol": "ES",
                "secType": "FUT",
                "exchange": "GLOBEX",
                "currency": "USD"
            }
        },
        {
            "name": "ES FUT CME USD", 
            "params": {
                "symbol": "ES",
                "secType": "FUT",
                "exchange": "CME",
                "currency": "USD"
            }
        },
        {
            "name": "ES avec expiry 202509",
            "params": {
                "symbol": "ES",
                "secType": "FUT",
                "exchange": "GLOBEX",
                "currency": "USD",
                "expiry": "202509"
            }
        },
        {
            "name": "ES simple",
            "params": {
                "symbol": "ES"
            }
        }
    ]
    
    all_contracts = []
    
    for method in search_methods:
        print(f"\n🔍 Test: {method['name']}")
        print(f"   Paramètres: {method['params']}")
        
        try:
            search_response = session.get(
                f"{base_url}/iserver/secdef/search",
                params=method['params'],
                timeout=15
            )
            
            print(f"   Status: {search_response.status_code}")
            
            if search_response.status_code == 200:
                contracts = search_response.json()
                print(f"   Résultats: {len(contracts)} contrats")
                
                for contract in contracts:
                    conid = contract.get('conid')
                    symbol = contract.get('symbol')
                    description = contract.get('description')
                    secType = contract.get('secType')
                    exchange = contract.get('exchange')
                    currency = contract.get('currency')
                    
                    # Filtrer les contrats ES
                    if symbol == "ES":
                        contract_info = {
                            'conid': conid,
                            'symbol': symbol,
                            'description': description,
                            'secType': secType,
                            'exchange': exchange,
                            'currency': currency,
                            'search_method': method['name']
                        }
                        
                        # Éviter les doublons
                        if not any(c['conid'] == conid for c in all_contracts):
                            all_contracts.append(contract_info)
                            
                            print(f"     ✅ ConID: {conid}")
                            print(f"        Description: {description}")
                            print(f"        Type: {secType}")
                            print(f"        Exchange: {exchange}")
                            print(f"        Currency: {currency}")
            else:
                print(f"   ❌ Erreur: {search_response.status_code}")
                if search_response.status_code == 500:
                    print(f"   Détails: {search_response.text}")
                    
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return all_contracts

def get_contract_details(session, base_url, conid):
    """Récupérer les détails complets d'un contrat"""
    print(f"\n📋 Détails complets ConID: {conid}")
    
    try:
        details_response = session.get(
            f"{base_url}/iserver/secdef/info",
            params={"conid": conid},
            timeout=15
        )
        
        if details_response.status_code == 200:
            contract_data = details_response.json()
            print(f"✅ Détails récupérés")
            return contract_data
        else:
            print(f"❌ Erreur détails: {details_response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Exception détails: {e}")
        return None

def test_market_data_subscription(session, base_url, conid):
    """Tester la souscription aux données de marché"""
    print(f"\n📊 Test données de marché ConID: {conid}")
    
    try:
        # 1. Souscrire aux données (POST)
        print("📡 Souscription aux données...")
        
        subscribe_response = session.post(
            f"{base_url}/iserver/marketdata/snapshot",
            json={
                "conids": [conid],
                "fields": ["31", "83", "84", "86", "6", "7", "8", "9"]  # bid, ask, last, volume, high, low, open, close
            },
            timeout=15
        )
        
        print(f"   Souscription status: {subscribe_response.status_code}")
        
        if subscribe_response.status_code == 200:
            print("✅ Souscription réussie")
            
            # 2. Attendre un peu
            time.sleep(2)
            
            # 3. Récupérer les données (GET)
            print("📊 Récupération des données...")
            
            market_response = session.get(
                f"{base_url}/iserver/marketdata/snapshot",
                params={
                    "conids": conid,
                    "fields": "31,83,84,86,6,7,8,9"
                },
                timeout=15
            )
            
            print(f"   Récupération status: {market_response.status_code}")
            
            if market_response.status_code == 200:
                data = market_response.json()
                print(f"   Données reçues: {json.dumps(data, indent=2)}")
                
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
                        elif key == '6':
                            prices['high'] = value
                        elif key == '7':
                            prices['low'] = value
                        elif key == '8':
                            prices['open'] = value
                        elif key == '9':
                            prices['close'] = value
                    
                    if prices:
                        print(f"   💰 Prix trouvés:")
                        for price_type, value in prices.items():
                            print(f"     {price_type}: {value}")
                        
                        # Vérifier si le prix est réaliste pour ES
                        if prices.get('last'):
                            last_price = float(prices['last'])
                            print(f"   📊 Prix last: {last_price}")
                            
                            # Le prix ES devrait être autour de 6481
                            if 6000 <= last_price <= 7000:
                                print(f"   ✅ Prix réaliste pour ES!")
                                return prices
                            else:
                                print(f"   ⚠️ Prix suspect: {last_price}")
                        else:
                            print(f"   ⚠️ Pas de prix last")
                    else:
                        print(f"   ⚠️ Aucun prix trouvé")
                else:
                    print(f"   ⚠️ Pas de données dans la réponse")
            else:
                print(f"   ❌ Erreur récupération: {market_response.status_code}")
        else:
            print(f"   ❌ Erreur souscription: {subscribe_response.status_code}")
        
        return None
        
    except Exception as e:
        print(f"❌ Exception données: {e}")
        return None

def find_es_sep25_contract(contracts):
    """Trouver le contrat ES September 2025"""
    print(f"\n🎯 Recherche ES Sep19'25 parmi {len(contracts)} contrats...")
    
    es_futures = []
    es_sep25_candidates = []
    
    for contract in contracts:
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
            if description:
                desc_lower = description.lower()
                if "sep" in desc_lower and "2025" in desc_lower:
                    print(f"   🎯 ES Sep19'25 TROUVÉ!")
                    es_sep25_candidates.append(contract)
                elif "sep" in desc_lower:
                    print(f"   📅 ES September détecté")
                elif "2025" in desc_lower:
                    print(f"   📅 ES 2025 détecté")
        else:
            print(f"   ❌ Pas un future")
    
    return es_futures, es_sep25_candidates

def main():
    """Fonction principale"""
    print("🚀 Fix ES ConID - Méthode Officielle IBKR")
    print("="*60)
    print(f"🕐 Timestamp: {datetime.now()}")
    
    # 1. Authentification
    session, base_url = authenticate_ibkr()
    if not session:
        print("❌ Impossible de s'authentifier")
        return
    
    # 2. Recherche ES futures
    contracts = search_es_futures_official(session, base_url)
    
    if not contracts:
        print("❌ Aucun contrat ES trouvé")
        return
    
    # 3. Analyser les contrats trouvés
    es_futures, es_sep25_candidates = find_es_sep25_contract(contracts)
    
    if not es_futures:
        print("❌ Aucun future ES trouvé")
        return
    
    # 4. Si on a des candidats ES Sep19'25, les tester
    if es_sep25_candidates:
        print(f"\n🎯 {len(es_sep25_candidates)} candidats ES Sep19'25 trouvés!")
        
        for candidate in es_sep25_candidates:
            conid = candidate['conid']
            print(f"\n" + "="*60)
            print(f"🎯 TEST CANDIDAT ES Sep19'25 - ConID: {conid}")
            print("="*60)
            
            # Récupérer les détails complets
            contract_data = get_contract_details(session, base_url, conid)
            if contract_data:
                print(f"📋 Détails: {json.dumps(contract_data, indent=2)}")
            
            # Tester les données de marché
            prices = test_market_data_subscription(session, base_url, conid)
            
            if prices:
                print(f"\n🎉 SUCCÈS! Prix ES Sep19'25 récupérés:")
                print(f"   Bid:     {prices.get('bid', 'N/A'):>10}")
                print(f"   Ask:     {prices.get('ask', 'N/A'):>10}")
                print(f"   Last:    {prices.get('last', 'N/A'):>10}")
                print(f"   Volume:  {prices.get('volume', 'N/A'):>10}")
                print(f"   High:    {prices.get('high', 'N/A'):>10}")
                print(f"   Low:     {prices.get('low', 'N/A'):>10}")
                print(f"   Open:    {prices.get('open', 'N/A'):>10}")
                print(f"   Close:   {prices.get('close', 'N/A'):>10}")
                
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
                
                return  # Succès, on arrête
    
    # 5. Si pas de candidats ES Sep19'25, tester tous les futures ES
    print(f"\n🔍 Test de tous les {len(es_futures)} futures ES...")
    
    for contract in es_futures:
        conid = contract['conid']
        description = contract['description']
        
        print(f"\n📋 Test ConID: {conid} - {description}")
        
        # Récupérer les détails complets
        contract_data = get_contract_details(session, base_url, conid)
        if contract_data:
            symbol = contract_data.get('symbol')
            secType = contract_data.get('secType')
            exchange = contract_data.get('exchange')
            expiry = contract_data.get('expiry')
            
            print(f"   Symbol: {symbol}")
            print(f"   Type: {secType}")
            print(f"   Exchange: {exchange}")
            print(f"   Expiry: {expiry}")
            
            # Vérifier si c'est ES Sep19'25
            if (symbol == "ES" and 
                secType == "FUT" and
                expiry and "202509" in str(expiry)):
                print(f"   🎯 CONTRAT ES Sep19'25 TROUVÉ!")
                
                # Tester les données de marché
                prices = test_market_data_subscription(session, base_url, conid)
                
                if prices:
                    print(f"\n🎉 SUCCÈS! Prix ES Sep19'25 récupérés avec ConID: {conid}")
                    return  # Succès, on arrête
    
    print(f"\n❌ Aucun contrat ES Sep19'25 avec données de marché trouvé")
    print(f"🔧 Problèmes possibles:")
    print(f"  - Contrat non disponible")
    print(f"  - Heures de trading")
    print(f"  - Permissions de données de marché")
    print(f"  - Problème API IBKR")
    
    print(f"\n👋 Script terminé")

if __name__ == "__main__":
    main()

