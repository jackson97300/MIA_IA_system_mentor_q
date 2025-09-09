#!/usr/bin/env python3
"""
🔍 Recherche ConID ES Sep19'25 - Méthode correcte
Script qui utilise la méthode officielle IBKR pour trouver le ConID
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def find_es_sep25_conid_correct():
    """Trouver le ConID ES Sep19'25 avec la méthode correcte"""
    print("🔍 Recherche ConID ES Sep19'25 - Méthode correcte")
    print("="*60)
    
    base_url = "https://localhost:5000/v1/api"
    
    try:
        # 1. Vérifier l'authentification
        print("🔐 Vérification authentification...")
        auth_response = requests.get(
            f"{base_url}/iserver/auth/status",
            verify=False,
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
        
        # 2. Recherche avec les paramètres corrects pour ES Sep19'25
        print(f"\n📈 Recherche ES Sep19'25 avec paramètres corrects...")
        
        # Méthode 1: Recherche avec symbol ES et secType FUT
        print(f"\n🔍 Méthode 1: Recherche ES FUT")
        
        search_response = requests.get(
            f"{base_url}/iserver/secdef/search",
            params={
                "symbol": "ES",
                "secType": "FUT",
                "exchange": "GLOBEX",
                "currency": "USD"
            },
            verify=False,
            timeout=10
        )
        
        print(f"  Status: {search_response.status_code}")
        
        if search_response.status_code == 200:
            data = search_response.json()
            print(f"  Résultats: {len(data)} contrats trouvés")
            
            for i, contract in enumerate(data):
                conid = contract.get('conid')
                symbol = contract.get('symbol')
                description = contract.get('description')
                secType = contract.get('secType')
                exchange = contract.get('exchange')
                currency = contract.get('currency')
                
                print(f"    {i+1}. ConID: {conid}")
                print(f"       Symbol: {symbol}")
                print(f"       Description: {description}")
                print(f"       Type: {secType}")
                print(f"       Exchange: {exchange}")
                print(f"       Currency: {currency}")
                
                # Chercher ES Sep19'25
                if (symbol == "ES" and 
                    "Sep" in str(description) and 
                    "2025" in str(description) and
                    secType == "FUT" and
                    exchange == "GLOBEX" and
                    currency == "USD"):
                    print(f"       ✅ CONTRAT ES Sep19'25 TROUVÉ!")
                    return conid
                
                print()
        else:
            print(f"  ❌ Erreur {search_response.status_code}")
        
        # Méthode 2: Recherche avec CME au lieu de GLOBEX
        print(f"\n🔍 Méthode 2: Recherche ES FUT avec CME")
        
        search_response = requests.get(
            f"{base_url}/iserver/secdef/search",
            params={
                "symbol": "ES",
                "secType": "FUT",
                "exchange": "CME",
                "currency": "USD"
            },
            verify=False,
            timeout=10
        )
        
        print(f"  Status: {search_response.status_code}")
        
        if search_response.status_code == 200:
            data = search_response.json()
            print(f"  Résultats: {len(data)} contrats trouvés")
            
            for i, contract in enumerate(data):
                conid = contract.get('conid')
                symbol = contract.get('symbol')
                description = contract.get('description')
                secType = contract.get('secType')
                exchange = contract.get('exchange')
                currency = contract.get('currency')
                
                print(f"    {i+1}. ConID: {conid}")
                print(f"       Symbol: {symbol}")
                print(f"       Description: {description}")
                print(f"       Type: {secType}")
                print(f"       Exchange: {exchange}")
                print(f"       Currency: {currency}")
                
                # Chercher ES Sep19'25
                if (symbol == "ES" and 
                    "Sep" in str(description) and 
                    "2025" in str(description) and
                    secType == "FUT" and
                    exchange == "CME" and
                    currency == "USD"):
                    print(f"       ✅ CONTRAT ES Sep19'25 TROUVÉ!")
                    return conid
                
                print()
        else:
            print(f"  ❌ Erreur {search_response.status_code}")
        
        # Méthode 3: Recherche avec date spécifique
        print(f"\n🔍 Méthode 3: Recherche avec date 202509")
        
        search_response = requests.get(
            f"{base_url}/iserver/secdef/search",
            params={
                "symbol": "ES",
                "secType": "FUT",
                "exchange": "GLOBEX",
                "currency": "USD",
                "lastTradeDateOrContractMonth": "202509"
            },
            verify=False,
            timeout=10
        )
        
        print(f"  Status: {search_response.status_code}")
        
        if search_response.status_code == 200:
            data = search_response.json()
            print(f"  Résultats: {len(data)} contrats trouvés")
            
            for i, contract in enumerate(data):
                conid = contract.get('conid')
                symbol = contract.get('symbol')
                description = contract.get('description')
                secType = contract.get('secType')
                exchange = contract.get('exchange')
                currency = contract.get('currency')
                
                print(f"    {i+1}. ConID: {conid}")
                print(f"       Symbol: {symbol}")
                print(f"       Description: {description}")
                print(f"       Type: {secType}")
                print(f"       Exchange: {exchange}")
                print(f"       Currency: {currency}")
                
                if (symbol == "ES" and 
                    secType == "FUT" and
                    exchange == "GLOBEX" and
                    currency == "USD"):
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

def test_conid_with_market_data(conid):
    """Tester le ConID avec des données de marché"""
    if not conid:
        return None
    
    print(f"\n📊 Test données de marché pour ConID: {conid}")
    print("="*50)
    
    base_url = "https://localhost:5000/v1/api"
    
    try:
        # D'abord souscrire aux données
        print(f"📡 Souscription aux données...")
        
        subscribe_response = requests.post(
            f"{base_url}/iserver/marketdata/snapshot",
            json={
                "conids": [conid],
                "fields": ["31", "83", "84", "86"]
            },
            verify=False,
            timeout=10
        )
        
        print(f"  Souscription status: {subscribe_response.status_code}")
        
        if subscribe_response.status_code == 200:
            import time
            time.sleep(3)  # Attendre que les données arrivent
            
            # Récupérer les données
            market_response = requests.get(
                f"{base_url}/iserver/marketdata/snapshot",
                params={
                    "conids": conid,
                    "fields": "31,83,84,86"
                },
                verify=False,
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

def display_es_price(prices, conid):
    """Afficher le prix ES"""
    if not prices:
        return
    
    print(f"\n" + "="*60)
    print(f"💰 PRIX ES Sep19'25 @GLOBEX")
    print(f"="*60)
    print(f"🕐 Timestamp: {datetime.now()}")
    print(f"🔢 ConID: {conid}")
    print(f"-"*60)
    print(f"💰 Bid:     {prices.get('bid', 'N/A'):>10}")
    print(f"💰 Ask:     {prices.get('ask', 'N/A'):>10}")
    print(f"💰 Last:    {prices.get('last', 'N/A'):>10}")
    print(f"📊 Volume:  {prices.get('volume', 'N/A'):>10}")
    print(f"-"*60)
    
    # Calculer le spread
    if prices.get('ask') and prices.get('bid'):
        try:
            spread = float(prices['ask']) - float(prices['bid'])
            print(f"📊 Spread:  {spread:>10.2f}")
        except:
            pass
    
    # Calculer la valeur en dollars
    if prices.get('last'):
        try:
            last_price = float(prices['last'])
            dollar_value = last_price * 50  # Multiplicateur ES
            tick_value = 12.50  # Valeur tick ES
            print(f"💵 Valeur contrat: ${dollar_value:,.2f}")
            print(f"💵 Valeur tick: ${tick_value}")
        except:
            pass
    
    print(f"="*60)

def main():
    """Fonction principale"""
    print("🚀 Recherche ConID ES Sep19'25 - Méthode correcte")
    print("="*60)
    
    # Trouver le ConID
    conid = find_es_sep25_conid_correct()
    
    if conid:
        print(f"\n✅ ConID trouvé: {conid}")
        
        # Tester avec les données de marché
        prices = test_conid_with_market_data(conid)
        
        if prices:
            display_es_price(prices, conid)
            print(f"\n🎯 SUCCÈS! Prix ES Sep19'25 récupérés avec succès!")
            
            # Vérifier la cohérence avec TWS (6481.00/6481.25)
            if prices.get('bid') and prices.get('ask'):
                bid_price = float(prices['bid'])
                ask_price = float(prices['ask'])
                
                expected_bid = 6481.00
                expected_ask = 6481.25
                
                bid_diff = abs(bid_price - expected_bid)
                ask_diff = abs(ask_price - expected_ask)
                
                if bid_diff < 1 and ask_diff < 1:
                    print(f"🎯 Prix parfaitement cohérent avec TWS!")
                elif bid_diff < 10 and ask_diff < 10:
                    print(f"✅ Prix cohérent avec TWS")
                else:
                    print(f"⚠️ Prix différent de TWS (6481.00/6481.25)")
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

