#!/usr/bin/env python3
"""
💰 Récupération prix ES Sep19'25 @CME
Script qui récupère le prix du contrat ES September 2025 exactement comme dans TWS
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def get_es_sep25_price():
    """Récupérer le prix ES Sep19'25 @CME"""
    print("💰 Récupération prix ES Sep19'25 @CME")
    print("="*50)
    
    base_url = "https://localhost:5000/v1/api"
    
    # ConID pour ES September 2025 (basé sur l'image TWS)
    es_sep25_conid = "265598"  # ES Sep19'25 @CME
    
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
        
        # 2. Récupérer les données ES Sep19'25
        print(f"\n📈 Récupération données ES Sep19'25 (ConID: {es_sep25_conid})...")
        
        # Méthode 1: Snapshot direct
        print(f"\n🔍 Méthode 1: Snapshot direct")
        
        market_response = requests.get(
            f"{base_url}/iserver/marketdata/snapshot",
            params={
                "conids": es_sep25_conid,
                "fields": "31,83,84,86,6,7,8,9"
            },
            verify=False,
            timeout=10
        )
        
        print(f"  Status: {market_response.status_code}")
        
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
                    elif key == '6':
                        prices['high'] = value
                    elif key == '7':
                        prices['low'] = value
                    elif key == '8':
                        prices['open'] = value
                    elif key == '9':
                        prices['close'] = value
                
                if prices:
                    print(f"  💰 Prix trouvés:")
                    for price_type, value in prices.items():
                        print(f"    {price_type}: {value}")
                    
                    # Vérifier si le prix correspond à TWS (6481.00/6481.25)
                    if prices.get('bid') and prices.get('ask'):
                        bid_price = float(prices['bid'])
                        ask_price = float(prices['ask'])
                        
                        print(f"  📊 Bid/Ask: {bid_price} / {ask_price}")
                        
                        # Vérifier si c'est proche de 6481.00/6481.25
                        expected_bid = 6481.00
                        expected_ask = 6481.25
                        
                        bid_diff = abs(bid_price - expected_bid)
                        ask_diff = abs(ask_price - expected_ask)
                        
                        if bid_diff < 10 and ask_diff < 10:
                            print(f"  ✅ Prix cohérent avec TWS!")
                            return prices
                        else:
                            print(f"  ⚠️ Prix différent de TWS:")
                            print(f"    Bid: {bid_price} vs {expected_bid} (diff: {bid_diff:.2f})")
                            print(f"    Ask: {ask_price} vs {expected_ask} (diff: {ask_diff:.2f})")
                    else:
                        print(f"  ⚠️ Pas de bid/ask")
                else:
                    print(f"  ⚠️ Aucun prix trouvé")
            else:
                print(f"  ⚠️ Pas de données dans la réponse")
        else:
            print(f"  ❌ Erreur {market_response.status_code}")
        
        # Méthode 2: Essayer avec souscription
        print(f"\n🔍 Méthode 2: Avec souscription")
        
        # Souscrire d'abord
        subscribe_response = requests.post(
            f"{base_url}/iserver/marketdata/snapshot",
            json={
                "conids": [es_sep25_conid],
                "fields": ["31", "83", "84", "86"]
            },
            verify=False,
            timeout=10
        )
        
        print(f"  Souscription status: {subscribe_response.status_code}")
        
        if subscribe_response.status_code == 200:
            import time
            time.sleep(2)
            
            # Récupérer après souscription
            market_response = requests.get(
                f"{base_url}/iserver/marketdata/snapshot",
                params={
                    "conids": es_sep25_conid,
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
                    
                    if prices.get('bid') and prices.get('ask'):
                        bid_price = float(prices['bid'])
                        ask_price = float(prices['ask'])
                        
                        print(f"  📊 Bid/Ask: {bid_price} / {ask_price}")
                        
                        expected_bid = 6481.00
                        expected_ask = 6481.25
                        
                        bid_diff = abs(bid_price - expected_bid)
                        ask_diff = abs(ask_price - expected_ask)
                        
                        if bid_diff < 10 and ask_diff < 10:
                            print(f"  ✅ Prix cohérent avec TWS!")
                            return prices
                        else:
                            print(f"  ⚠️ Prix différent de TWS")
        
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None

def display_es_sep25_price(prices):
    """Afficher le prix ES Sep19'25"""
    if not prices:
        return
    
    print(f"\n" + "="*60)
    print(f"💰 PRIX ES Sep19'25 @CME")
    print(f"="*60)
    print(f"🕐 Timestamp: {datetime.now()}")
    print(f"-"*60)
    print(f"💰 Bid:     {prices.get('bid', 'N/A'):>10}")
    print(f"💰 Ask:     {prices.get('ask', 'N/A'):>10}")
    print(f"💰 Last:    {prices.get('last', 'N/A'):>10}")
    print(f"📊 Volume:  {prices.get('volume', 'N/A'):>10}")
    
    if prices.get('high'):
        print(f"📈 High:    {prices.get('high'):>10}")
    if prices.get('low'):
        print(f"📉 Low:     {prices.get('low'):>10}")
    if prices.get('open'):
        print(f"🔓 Open:    {prices.get('open'):>10}")
    if prices.get('close'):
        print(f"🔒 Close:   {prices.get('close'):>10}")
    
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
    print("🚀 Récupération prix ES Sep19'25 @CME")
    print("="*50)
    
    # Récupérer les prix
    prices = get_es_sep25_price()
    
    # Afficher les résultats
    if prices:
        display_es_sep25_price(prices)
        print(f"\n✅ Prix ES Sep19'25 récupéré avec succès!")
        
        # Vérifier la cohérence avec TWS
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
        print(f"\n❌ Impossible de récupérer le prix ES Sep19'25")
        print(f"🔧 Problèmes possibles:")
        print(f"  - ConID incorrect")
        print(f"  - Heures de trading")
        print(f"  - Problème API IBKR")
        print(f"  - Permissions de données de marché")
    
    print(f"\n👋 Script terminé")

if __name__ == "__main__":
    main()

