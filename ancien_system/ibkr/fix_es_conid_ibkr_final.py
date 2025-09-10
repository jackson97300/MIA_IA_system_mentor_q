#!/usr/bin/env python3
"""
🔧 Fix ES ConID - Solution Finale IBKR
Script qui résout définitivement le problème de ConID incorrect
Basé sur l'analyse des erreurs persistantes et les solutions IBKR
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

def get_known_es_conids():
    """Récupérer les ConIDs connus pour ES futures"""
    print("\n📋 Récupération des ConIDs ES connus...")
    
    # ConIDs connus pour ES futures (basés sur la documentation IBKR)
    # Ces valeurs peuvent être trouvées via TWS ou documentation officielle
    known_conids = [
        # ES September 2025 (ESU25) - ConIDs possibles
        265598,  # Testé précédemment (était AAPL)
        265599,  # Testé précédemment (erreur 500)
        265600,  # Testé précédemment (erreur 500)
        265601,  # Testé précédemment (erreur 500)
        265602,  # Testé précédemment (erreur 500)
        
        # Autres ConIDs possibles pour ES futures
        11004968,   # Trouvé dans la recherche (CME)
        182880167,  # Trouvé dans la recherche (NYSE)
        458401474,  # Trouvé dans la recherche (MEXI)
        1254464,    # Trouvé dans la recherche (SBF)
        
        # ConIDs supplémentaires à tester
        1000000,    # Plage basse
        2000000,    # Plage basse
        3000000,    # Plage basse
        4000000,    # Plage basse
        5000000,    # Plage basse
    ]
    
    return known_conids

def test_conid_directly(session, base_url, conid):
    """Tester un ConID directement"""
    print(f"\n🔍 Test direct ConID: {conid}")
    
    try:
        # Récupérer les détails du contrat
        details_response = session.get(
            f"{base_url}/iserver/secdef/info",
            params={"conid": conid},
            timeout=15
        )
        
        if details_response.status_code == 200:
            contract_data = details_response.json()
            
            # Analyser les détails
            symbol = contract_data.get('symbol')
            secType = contract_data.get('secType')
            exchange = contract_data.get('exchange')
            currency = contract_data.get('currency')
            localSymbol = contract_data.get('localSymbol')
            expiry = contract_data.get('expiry')
            lastTradeDateOrContractMonth = contract_data.get('lastTradeDateOrContractMonth')
            description = contract_data.get('description')
            
            print(f"   Symbol: {symbol}")
            print(f"   SecType: {secType}")
            print(f"   Exchange: {exchange}")
            print(f"   Currency: {currency}")
            print(f"   LocalSymbol: {localSymbol}")
            print(f"   Expiry: {expiry}")
            print(f"   LastTradeDate: {lastTradeDateOrContractMonth}")
            print(f"   Description: {description}")
            
            # Vérifier si c'est ES Sep19'25
            is_es_sep25 = False
            
            if symbol == "ES" and secType == "FUT":
                print(f"   ✅ Future ES détecté")
                
                # Vérifier l'expiration
                if expiry and "202509" in str(expiry):
                    is_es_sep25 = True
                    print(f"   📅 Expiration September 2025 détectée")
                
                if lastTradeDateOrContractMonth and "202509" in str(lastTradeDateOrContractMonth):
                    is_es_sep25 = True
                    print(f"   📅 LastTradeDate September 2025 détectée")
                
                if localSymbol and "ESU25" in str(localSymbol).upper():
                    is_es_sep25 = True
                    print(f"   📅 LocalSymbol ESU25 détecté")
                
                if description and "sep" in str(description).lower() and "2025" in str(description):
                    is_es_sep25 = True
                    print(f"   📅 Description September 2025 détectée")
                
                if is_es_sep25:
                    print(f"   🎯 ES Sep19'25 CONFIRMÉ!")
                    return contract_data
                else:
                    print(f"   ⚠️ Future ES mais pas Sep19'25")
            else:
                print(f"   ❌ Pas un future ES")
            
            return contract_data
        else:
            print(f"   ❌ Erreur détails: {details_response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def test_market_data_for_conid(session, base_url, conid):
    """Tester les données de marché pour un ConID"""
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

def search_es_futures_alternative(session, base_url):
    """Recherche alternative ES futures"""
    print(f"\n🔄 Recherche alternative ES futures...")
    
    # Méthode alternative: Recherche avec différents paramètres
    search_params_list = [
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
    
    for i, params in enumerate(search_params_list):
        print(f"\n🔍 Test {i+1}: {params}")
        
        try:
            search_response = session.get(
                f"{base_url}/iserver/secdef/search",
                params=params,
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
                            'search_params': params
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
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return all_contracts

def main():
    """Fonction principale"""
    print("🚀 Fix ES ConID - Solution Finale IBKR")
    print("="*60)
    print(f"🕐 Timestamp: {datetime.now()}")
    
    # 1. Authentification
    session, base_url = authenticate_ibkr()
    if not session:
        print("❌ Impossible de s'authentifier")
        return
    
    # 2. Test des ConIDs connus directement
    print(f"\n🎯 Test des ConIDs connus directement...")
    known_conids = get_known_es_conids()
    
    for conid in known_conids:
        print(f"\n" + "="*60)
        print(f"🎯 TEST CONID DIRECT: {conid}")
        print("="*60)
        
        # Tester le ConID directement
        contract_data = test_conid_directly(session, base_url, conid)
        
        if contract_data:
            symbol = contract_data.get('symbol')
            secType = contract_data.get('secType')
            
            # Si c'est un future ES, tester les données de marché
            if symbol == "ES" and secType == "FUT":
                print(f"\n📊 Test données de marché pour ES future...")
                prices = test_market_data_for_conid(session, base_url, conid)
                
                if prices:
                    print(f"\n🎉 SUCCÈS! Prix ES récupérés:")
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
    
    # 3. Si pas de succès avec les ConIDs connus, essayer la recherche alternative
    print(f"\n🔄 Aucun ConID connu fonctionnel, essai recherche alternative...")
    contracts = search_es_futures_alternative(session, base_url)
    
    if contracts:
        print(f"\n📋 {len(contracts)} contrats ES trouvés, test des détails...")
        
        for contract in contracts:
            conid = contract['conid']
            description = contract['description']
            
            print(f"\n📋 Test ConID: {conid} - {description}")
            
            # Récupérer les détails complets
            contract_data = test_conid_directly(session, base_url, conid)
            
            if contract_data:
                symbol = contract_data.get('symbol')
                secType = contract_data.get('secType')
                
                # Si c'est un future ES, tester les données de marché
                if symbol == "ES" and secType == "FUT":
                    prices = test_market_data_for_conid(session, base_url, conid)
                    
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
    print(f"  - API Client Portal Gateway défaillante")
    
    print(f"\n💡 Solutions recommandées:")
    print(f"  1. Vérifier que TWS/Gateway est bien connecté")
    print(f"  2. Vérifier les permissions de données de marché")
    print(f"  3. Essayer avec l'API TWS classique (ib_insync)")
    print(f"  4. Contacter le support IBKR")
    
    print(f"\n👋 Script terminé")

if __name__ == "__main__":
    main()

