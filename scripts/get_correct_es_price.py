#!/usr/bin/env python3
"""
💰 Récupération du vrai prix ES (6481.50)
Script qui utilise la bonne méthode pour récupérer les prix ES corrects
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def get_correct_es_price():
    """Récupérer le vrai prix ES"""
    print("💰 Récupération prix ES correct (6481.50)")
    print("="*50)
    
    base_url = "https://localhost:5000/v1/api"
    
    # ConID correct pour ES March 2025
    es_conid = "265598"
    
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
        
        # 2. Récupérer les données de marché ES avec la bonne méthode
        print(f"\n📈 Récupération données ES (ConID: {es_conid})...")
        
        # Méthode 1: Snapshot avec souscription
        print(f"\n🔍 Méthode 1: Snapshot avec souscription")
        
        # D'abord souscrire
        subscribe_response = requests.post(
            f"{base_url}/iserver/marketdata/snapshot",
            json={
                "conids": [es_conid],
                "fields": ["31", "83", "84", "86"]
            },
            verify=False,
            timeout=10
        )
        
        print(f"  Souscription status: {subscribe_response.status_code}")
        
        if subscribe_response.status_code == 200:
            # Attendre un peu
            import time
            time.sleep(3)
            
            # Récupérer les données
            market_response = requests.get(
                f"{base_url}/iserver/marketdata/snapshot",
                params={
                    "conids": es_conid,
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
                        
                        # Vérifier si le prix est correct (autour de 6481.50)
                        if prices.get('last'):
                            last_price = float(prices['last'])
                            print(f"  📊 Prix ES récupéré: {last_price}")
                            
                            # Vérifier si c'est proche de 6481.50
                            expected_price = 6481.50
                            difference = abs(last_price - expected_price)
                            
                            if difference < 100:  # Tolérance de 100 points
                                print(f"  ✅ Prix cohérent avec ES (6481.50)!")
                                return prices
                            else:
                                print(f"  ⚠️ Prix différent de ES: {last_price} vs {expected_price}")
                                print(f"  📊 Différence: {difference:.2f} points")
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
        
        # Méthode 2: Essayer avec un autre ConID
        print(f"\n🔍 Méthode 2: Test avec ConID alternatif")
        
        # Essayer le ConID suivant
        alt_conid = "265599"  # ES June 2025
        
        market_response = requests.get(
            f"{base_url}/iserver/marketdata/snapshot",
            params={
                "conids": alt_conid,
                "fields": "31,83,84,86"
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
                
                if prices.get('last'):
                    last_price = float(prices['last'])
                    print(f"  📊 Prix ES alternatif: {last_price}")
                    
                    expected_price = 6481.50
                    difference = abs(last_price - expected_price)
                    
                    if difference < 100:
                        print(f"  ✅ Prix cohérent avec ES (6481.50)!")
                        return prices
        
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None

def display_es_price(prices):
    """Afficher le prix ES"""
    if not prices:
        return
    
    print(f"\n" + "="*60)
    print(f"💰 PRIX ES FUTURES")
    print(f"="*60)
    print(f"🕐 Timestamp: {datetime.now()}")
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
    print("🚀 Récupération prix ES correct")
    print("="*50)
    
    # Récupérer les prix
    prices = get_correct_es_price()
    
    # Afficher les résultats
    if prices:
        display_es_price(prices)
        print(f"\n✅ Prix ES récupéré avec succès!")
        
        # Vérifier la cohérence
        if prices.get('last'):
            last_price = float(prices['last'])
            expected = 6481.50
            diff = abs(last_price - expected)
            
            if diff < 10:
                print(f"🎯 Prix parfaitement cohérent!")
            elif diff < 50:
                print(f"✅ Prix cohérent (différence: {diff:.2f})")
            else:
                print(f"⚠️ Prix différent de {expected} (différence: {diff:.2f})")
    else:
        print(f"\n❌ Impossible de récupérer le prix ES")
        print(f"🔧 Problèmes possibles:")
        print(f"  - ConID incorrect")
        print(f"  - Heures de trading")
        print(f"  - Problème API IBKR")
        print(f"  - Permissions de données de marché")
    
    print(f"\n👋 Script terminé")

if __name__ == "__main__":
    main()

