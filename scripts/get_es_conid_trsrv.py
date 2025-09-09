#!/usr/bin/env python3
"""
🎯 Get ES ConID - Méthode TRSRV IBKR
Script qui utilise l'endpoint /trsrv/futures pour récupérer facilement le ConID d'ES futures
Basé sur la méthode recommandée par IBKR
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

def get_es_futures_trsrv(session, base_url):
    """Récupérer les contrats ES futures via l'endpoint TRSRV"""
    print(f"\n📋 Récupération des contrats ES futures via TRSRV...")
    
    try:
        # Utiliser l'endpoint TRSRV comme recommandé
        trsrv_response = session.get(
            f"{base_url}/trsrv/futures",
            params={"symbols": "ES"},
            timeout=15
        )
        
        print(f"   Status: {trsrv_response.status_code}")
        
        if trsrv_response.status_code == 200:
            data = trsrv_response.json()
            print(f"   Données reçues: {json.dumps(data, indent=2)}")
            
            # Analyser la réponse
            if isinstance(data, dict) and "ES" in data:
                es_contracts = data["ES"]
                print(f"   ✅ {len(es_contracts)} contrats ES trouvés")
                
                return es_contracts
            else:
                print(f"   ⚠️ Format de réponse inattendu")
                return []
        else:
            print(f"   ❌ Erreur TRSRV: {trsrv_response.status_code}")
            if trsrv_response.status_code == 500:
                print(f"   Détails: {trsrv_response.text}")
            return []
            
    except Exception as e:
        print(f"   ❌ Exception TRSRV: {e}")
        return []

def find_es_sep25_contract(contracts):
    """Trouver le contrat ES September 2025"""
    print(f"\n🎯 Recherche ES Sep19'25 parmi {len(contracts)} contrats...")
    
    es_sep25_candidates = []
    
    for contract in contracts:
        conid = contract.get('conid')
        symbol = contract.get('symbol')
        expiration_date = contract.get('expirationDate')
        ltd = contract.get('ltd')
        underlying_conid = contract.get('underlyingConid')
        
        print(f"\n🔍 ConID: {conid}")
        print(f"   Symbol: {symbol}")
        print(f"   ExpirationDate: {expiration_date}")
        print(f"   LTD: {ltd}")
        print(f"   UnderlyingConid: {underlying_conid}")
        
        # Vérifier si c'est ES Sep19'25
        if (symbol == "ES" and 
            expiration_date and "202509" in str(expiration_date)):
            print(f"   🎯 ES Sep19'25 TROUVÉ!")
            es_sep25_candidates.append(contract)
        else:
            print(f"   ❌ Pas ES Sep19'25")
    
    return es_sep25_candidates

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

def main():
    """Fonction principale"""
    print("🚀 Get ES ConID - Méthode TRSRV IBKR")
    print("="*60)
    print(f"🕐 Timestamp: {datetime.now()}")
    
    # 1. Authentification
    session, base_url = authenticate_ibkr()
    if not session:
        print("❌ Impossible de s'authentifier")
        return
    
    # 2. Récupérer les contrats ES futures via TRSRV
    contracts = get_es_futures_trsrv(session, base_url)
    
    if not contracts:
        print("❌ Aucun contrat ES trouvé via TRSRV")
        return
    
    # 3. Trouver ES Sep19'25
    es_sep25_candidates = find_es_sep25_contract(contracts)
    
    if not es_sep25_candidates:
        print("❌ Aucun contrat ES Sep19'25 trouvé")
        print("📋 Contrats ES disponibles:")
        for contract in contracts:
            conid = contract.get('conid')
            expiry = contract.get('expiry')
            print(f"   ConID: {conid}, Expiry: {expiry}")
        return
    
    # 4. Tester les candidats ES Sep19'25
    print(f"\n🎯 {len(es_sep25_candidates)} candidats ES Sep19'25 trouvés!")
    
    for candidate in es_sep25_candidates:
        conid = candidate['conid']
        expiration_date = candidate['expirationDate']
        ltd = candidate['ltd']
        
        print(f"\n" + "="*60)
        print(f"🎯 TEST CANDIDAT ES Sep19'25")
        print("="*60)
        print(f"   ConID: {conid}")
        print(f"   ExpirationDate: {expiration_date}")
        print(f"   LTD: {ltd}")
        
        # Tester les données de marché
        prices = test_market_data_for_conid(session, base_url, conid)
        
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
            
            print(f"\n✅ ConID ES Sep19'25 trouvé: {conid}")
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
