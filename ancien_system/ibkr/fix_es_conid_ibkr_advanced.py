#!/usr/bin/env python3
"""
🔧 Fix ES ConID - Méthode Avancée IBKR
Script qui résout le problème de ConID incorrect en utilisant les méthodes officielles IBKR
Basé sur l'analyse des erreurs et les meilleures pratiques de la documentation
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
        # Vérifier le statut d'authentification
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
        
        print("❌ Authentification requise - Ouvrir https://localhost:5000/sso/Dispatcher")
        return None, None
        
    except Exception as e:
        print(f"❌ Erreur authentification: {e}")
        return None, None

def search_es_futures_advanced(session, base_url):
    """Recherche ES futures avec méthode avancée basée sur la documentation IBKR"""
    print("\n🔍 Recherche ES futures - Méthode avancée IBKR")
    print("="*60)
    
    # Méthodes de recherche basées sur la documentation IBKR officielle
    search_methods = [
        # Méthode 1: Recherche avec lastTradeDateOrContractMonth (recommandée par IBKR)
        {
            "name": "ES avec lastTradeDateOrContractMonth 202509",
            "params": {
                "symbol": "ES",
                "secType": "FUT",
                "exchange": "GLOBEX",
                "currency": "USD",
                "lastTradeDateOrContractMonth": "202509"
            }
        },
        # Méthode 2: Recherche avec expiry (alternative)
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
        # Méthode 3: Recherche avec localSymbol (convention IBKR)
        {
            "name": "ES avec localSymbol ESU25",
            "params": {
                "symbol": "ES",
                "secType": "FUT",
                "exchange": "GLOBEX",
                "currency": "USD",
                "localSymbol": "ESU25"  # ES September 2025
            }
        },
        # Méthode 4: Recherche simple mais avec filtrage
        {
            "name": "ES simple avec filtrage",
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
                    localSymbol = contract.get('localSymbol')
                    
                    # Filtrer les contrats ES
                    if symbol == "ES":
                        contract_info = {
                            'conid': conid,
                            'symbol': symbol,
                            'description': description,
                            'secType': secType,
                            'exchange': exchange,
                            'currency': currency,
                            'localSymbol': localSymbol,
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
                            print(f"        LocalSymbol: {localSymbol}")
            else:
                print(f"   ❌ Erreur: {search_response.status_code}")
                if search_response.status_code == 500:
                    print(f"   Détails: {search_response.text}")
                    
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return all_contracts

def get_contract_details_advanced(session, base_url, conid):
    """Récupérer les détails complets d'un contrat avec analyse avancée"""
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
            
            # Analyser les détails
            symbol = contract_data.get('symbol')
            secType = contract_data.get('secType')
            exchange = contract_data.get('exchange')
            currency = contract_data.get('currency')
            localSymbol = contract_data.get('localSymbol')
            expiry = contract_data.get('expiry')
            lastTradeDateOrContractMonth = contract_data.get('lastTradeDateOrContractMonth')
            
            print(f"   Symbol: {symbol}")
            print(f"   SecType: {secType}")
            print(f"   Exchange: {exchange}")
            print(f"   Currency: {currency}")
            print(f"   LocalSymbol: {localSymbol}")
            print(f"   Expiry: {expiry}")
            print(f"   LastTradeDate: {lastTradeDateOrContractMonth}")
            
            return contract_data
        else:
            print(f"❌ Erreur détails: {details_response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Exception détails: {e}")
        return None

def test_market_data_advanced(session, base_url, conid):
    """Tester les données de marché avec méthode avancée"""
    print(f"\n📊 Test données de marché ConID: {conid}")
    
    try:
        # 1. Souscrire aux données (POST)
        print("📡 Souscription aux données...")
        
        subscribe_response = session.post(
            f"{base_url}/iserver/marketdata/snapshot",
            json={
                "conids": [conid],
                "fields": ["31", "83", "84", "86", "6", "7", "8", "9"]
            },
            timeout=15
        )
        
        print(f"   Souscription status: {subscribe_response.status_code}")
        
        if subscribe_response.status_code == 200:
            print("✅ Souscription réussie")
            
            # 2. Attendre un peu
            time.sleep(3)
            
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

def analyze_contracts_advanced(contracts):
    """Analyser les contrats avec logique avancée"""
    print(f"\n🎯 Analyse avancée de {len(contracts)} contrats...")
    
    es_futures = []
    es_sep25_candidates = []
    
    for contract in contracts:
        conid = contract['conid']
        description = contract['description']
        secType = contract['secType']
        localSymbol = contract.get('localSymbol', '')
        
        print(f"\n🔍 ConID: {conid}")
        print(f"   Description: {description}")
        print(f"   Type: {secType}")
        print(f"   LocalSymbol: {localSymbol}")
        
        # Vérifier si c'est un future ES
        if secType == "FUT":
            es_futures.append(contract)
            print(f"   ✅ Future ES détecté")
            
            # Vérifier si c'est Sep19'25 par plusieurs critères
            is_sep25 = False
            
            # Critère 1: Description
            if description:
                desc_lower = description.lower()
                if "sep" in desc_lower and "2025" in desc_lower:
                    is_sep25 = True
                    print(f"   📅 ES Sep19'25 détecté par description")
            
            # Critère 2: LocalSymbol (convention IBKR)
            if localSymbol and "ESU25" in localSymbol.upper():
                is_sep25 = True
                print(f"   📅 ES Sep19'25 détecté par localSymbol")
            
            # Critère 3: ConID connu (si on a des références)
            known_es_sep25_conids = [
                # Ajouter ici les ConIDs connus pour ES Sep19'25
                # Ces valeurs peuvent être trouvées via TWS ou documentation
            ]
            
            if conid in known_es_sep25_conids:
                is_sep25 = True
                print(f"   📅 ES Sep19'25 détecté par ConID connu")
            
            if is_sep25:
                es_sep25_candidates.append(contract)
                print(f"   🎯 ES Sep19'25 CANDIDAT CONFIRMÉ!")
        else:
            print(f"   ❌ Pas un future")
    
    return es_futures, es_sep25_candidates

def try_alternative_search_methods(session, base_url):
    """Essayer des méthodes de recherche alternatives"""
    print(f"\n🔄 Méthodes de recherche alternatives...")
    
    # Méthode alternative 1: Recherche par symbole local
    print(f"\n🔍 Recherche par symbole local...")
    
    local_symbols = ["ESU25", "ESZ25", "ESH26", "ESM25"]  # Différentes expirations
    
    for local_symbol in local_symbols:
        print(f"   Test localSymbol: {local_symbol}")
        
        try:
            search_response = session.get(
                f"{base_url}/iserver/secdef/search",
                params={
                    "localSymbol": local_symbol,
                    "secType": "FUT"
                },
                timeout=15
            )
            
            if search_response.status_code == 200:
                contracts = search_response.json()
                if contracts:
                    print(f"     ✅ Trouvé: {len(contracts)} contrats")
                    for contract in contracts:
                        conid = contract.get('conid')
                        symbol = contract.get('symbol')
                        description = contract.get('description')
                        print(f"       ConID: {conid}, Symbol: {symbol}, Desc: {description}")
                        
                        if symbol == "ES":
                            return contract
                else:
                    print(f"     ❌ Aucun contrat trouvé")
            else:
                print(f"     ❌ Erreur: {search_response.status_code}")
                
        except Exception as e:
            print(f"     ❌ Exception: {e}")
    
    return None

def main():
    """Fonction principale"""
    print("🚀 Fix ES ConID - Méthode Avancée IBKR")
    print("="*60)
    print(f"🕐 Timestamp: {datetime.now()}")
    
    # 1. Authentification
    session, base_url = authenticate_ibkr()
    if not session:
        print("❌ Impossible de s'authentifier")
        return
    
    # 2. Recherche ES futures avancée
    contracts = search_es_futures_advanced(session, base_url)
    
    if not contracts:
        print("❌ Aucun contrat ES trouvé")
        return
    
    # 3. Analyser les contrats trouvés
    es_futures, es_sep25_candidates = analyze_contracts_advanced(contracts)
    
    # 4. Si pas de candidats ES Sep19'25, essayer les méthodes alternatives
    if not es_sep25_candidates:
        print(f"\n🔄 Aucun candidat ES Sep19'25 trouvé, essai méthodes alternatives...")
        alternative_contract = try_alternative_search_methods(session, base_url)
        
        if alternative_contract:
            es_sep25_candidates = [alternative_contract]
            print(f"✅ Contrat alternatif trouvé: {alternative_contract['conid']}")
    
    # 5. Tester les candidats
    if es_sep25_candidates:
        print(f"\n🎯 {len(es_sep25_candidates)} candidats ES Sep19'25 trouvés!")
        
        for candidate in es_sep25_candidates:
            conid = candidate['conid']
            print(f"\n" + "="*60)
            print(f"🎯 TEST CANDIDAT ES Sep19'25 - ConID: {conid}")
            print("="*60)
            
            # Récupérer les détails complets
            contract_data = get_contract_details_advanced(session, base_url, conid)
            
            # Tester les données de marché
            prices = test_market_data_advanced(session, base_url, conid)
            
            if prices:
                print(f"\n🎉 SUCCÈS! Prix ES Sep19'25 récupérés:")
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
                
                return  # Succès, on arrête
    
    # 6. Si toujours pas de succès, tester tous les futures ES
    if es_futures:
        print(f"\n🔍 Test de tous les {len(es_futures)} futures ES...")
        
        for contract in es_futures:
            conid = contract['conid']
            description = contract['description']
            
            print(f"\n📋 Test ConID: {conid} - {description}")
            
            # Récupérer les détails complets
            contract_data = get_contract_details_advanced(session, base_url, conid)
            
            # Tester les données de marché
            prices = test_market_data_advanced(session, base_url, conid)
            
            if prices:
                print(f"\n🎉 SUCCÈS! Prix ES récupérés avec ConID: {conid}")
                return  # Succès, on arrête
    
    print(f"\n❌ Aucun contrat ES avec données de marché trouvé")
    print(f"🔧 Problèmes possibles:")
    print(f"  - Contrat non disponible")
    print(f"  - Heures de trading")
    print(f"  - Permissions de données de marché")
    print(f"  - Problème API IBKR")
    print(f"  - ConID incorrect dans la recherche")
    
    print(f"\n👋 Script terminé")

if __name__ == "__main__":
    main()

