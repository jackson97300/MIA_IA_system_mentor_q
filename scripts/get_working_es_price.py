#!/usr/bin/env python3
"""
💰 Récupération finale des prix ES Futures
Script qui souscrit aux données de marché et récupère les vrais prix
"""

import sys
import requests
import json
import time
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def subscribe_market_data(conid):
    """Souscrire aux données de marché pour un ConID"""
    base_url = "https://localhost:5000/v1/api"
    
    try:
        # Souscrire aux données de marché
        subscribe_response = requests.post(
            f"{base_url}/iserver/marketdata/snapshot",
            json={
                "conids": [conid],
                "fields": ["31", "83", "84", "86", "6", "7", "8", "9"]
            },
            verify=False,
            timeout=10
        )
        
        if subscribe_response.status_code == 200:
            print(f"  ✅ Souscription réussie pour ConID {conid}")
            return True
        else:
            print(f"  ❌ Erreur souscription {subscribe_response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur souscription: {e}")
        return False

def get_market_data_with_subscription(conid):
    """Récupérer les données de marché avec souscription"""
    base_url = "https://localhost:5000/v1/api"
    
    try:
        # 1. Souscrire aux données
        if not subscribe_market_data(conid):
            return None
        
        # 2. Attendre un peu pour que les données arrivent
        time.sleep(2)
        
        # 3. Récupérer les données
        market_response = requests.get(
            f"{base_url}/iserver/marketdata/snapshot",
            params={
                "conids": str(conid),
                "fields": "31,83,84,86,6,7,8,9"
            },
            verify=False,
            timeout=10
        )
        
        if market_response.status_code == 200:
            data = market_response.json()
            if data and isinstance(data, list) and len(data) > 0:
                return data[0]
        
        return None
        
    except Exception as e:
        print(f"  ❌ Erreur récupération: {e}")
        return None

def parse_market_data(market_data):
    """Parser les données de marché"""
    if not market_data:
        return None
    
    prices = {
        'bid': None,
        'ask': None,
        'last': None,
        'volume': None,
        'high': None,
        'low': None,
        'open': None,
        'close': None
    }
    
    # Analyser la structure des données
    print(f"  🔍 Structure des données: {json.dumps(market_data, indent=2)}")
    
    # Méthode 1: Chercher directement dans les champs
    for key, value in market_data.items():
        if key == '31' and value:
            prices['bid'] = value
        elif key == '83' and value:
            prices['ask'] = value
        elif key == '84' and value:
            prices['last'] = value
        elif key == '86' and value:
            prices['volume'] = value
        elif key == '6' and value:
            prices['high'] = value
        elif key == '7' and value:
            prices['low'] = value
        elif key == '8' and value:
            prices['open'] = value
        elif key == '9' and value:
            prices['close'] = value
    
    # Méthode 2: Si les données sont dans une structure imbriquée
    if not any([prices['bid'], prices['ask'], prices['last']]):
        for key, value in market_data.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        field_id = item.get('f')
                        field_value = item.get('v')
                        if field_id == '31':
                            prices['bid'] = field_value
                        elif field_id == '83':
                            prices['ask'] = field_value
                        elif field_id == '84':
                            prices['last'] = field_value
                        elif field_id == '86':
                            prices['volume'] = field_value
    
    return prices

def display_price(conid, prices):
    """Afficher le prix de manière formatée"""
    if not prices:
        return False
    
    print(f"\n" + "="*60)
    print(f"💰 PRIX ES FUTURES")
    print(f"="*60)
    print(f"🕐 Timestamp: {datetime.now()}")
    print(f"🆔 ConID: {conid}")
    print(f"-"*60)
    print(f"💰 Bid:     {prices['bid']:>10}")
    print(f"💰 Ask:     {prices['ask']:>10}")
    print(f"💰 Last:    {prices['last']:>10}")
    
    if prices['ask'] and prices['bid']:
        try:
            spread = float(prices['ask']) - float(prices['bid'])
            print(f"📊 Spread:  {spread:>10.2f}")
        except:
            pass
    
    print(f"-"*60)
    print(f"📈 Open:    {prices['open']:>10}")
    print(f"📈 High:    {prices['high']:>10}")
    print(f"📈 Low:     {prices['low']:>10}")
    print(f"📈 Close:   {prices['close']:>10}")
    print(f"-"*60)
    print(f"📊 Volume:  {prices['volume']:>10}")
    print(f"="*60)
    
    # Calculer la valeur en dollars
    if prices['last']:
        try:
            last_price = float(prices['last'])
            dollar_value = last_price * 50  # Multiplicateur ES
            tick_value = 12.50  # Valeur tick ES
            print(f"💵 Valeur contrat: ${dollar_value:,.2f}")
            print(f"💵 Valeur tick: ${tick_value}")
        except:
            pass
    
    print()
    return True

def test_known_es_contracts():
    """Tester les contrats ES connus"""
    print("🎯 Test des contrats ES connus")
    print("="*50)
    
    # ConID des contrats ES futures trouvés
    es_contracts = [
        {"conid": "265598", "name": "ES March 2025"},
        {"conid": "265599", "name": "ES June 2025"},
        {"conid": "265600", "name": "ES September 2025"},
        {"conid": "265601", "name": "ES December 2025"},
        {"conid": "265602", "name": "ES March 2026"}
    ]
    
    working_contracts = []
    
    for contract in es_contracts:
        conid = contract["conid"]
        name = contract["name"]
        
        print(f"\n🔍 Test {name} (ConID: {conid})")
        
        # Récupérer les données avec souscription
        market_data = get_market_data_with_subscription(conid)
        
        if market_data:
            prices = parse_market_data(market_data)
            
            if prices and any([prices['bid'], prices['ask'], prices['last']]):
                print(f"✅ Prix trouvés!")
                working_contracts.append((conid, name, prices))
                display_price(conid, prices)
            else:
                print(f"⚠️ Pas de prix dans les données")
        else:
            print(f"❌ Pas de données de marché")
    
    return working_contracts

def unsubscribe_all():
    """Se désabonner de toutes les données de marché"""
    base_url = "https://localhost:5000/v1/api"
    
    try:
        response = requests.get(
            f"{base_url}/iserver/marketdata/unsubscribeall",
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Désabonnement réussi")
        else:
            print(f"⚠️ Erreur désabonnement: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur désabonnement: {e}")

def main():
    """Fonction principale"""
    print("🚀 Récupération prix ES Futures avec souscription")
    print("="*60)
    
    # 1. Vérifier l'authentification
    print("🔐 Vérification authentification...")
    base_url = "https://localhost:5000/v1/api"
    
    try:
        auth_response = requests.get(
            f"{base_url}/iserver/auth/status",
            verify=False,
            timeout=10
        )
        
        if auth_response.status_code != 200:
            print("❌ Problème d'authentification")
            return
        
        auth_data = auth_response.json()
        if not auth_data.get('authenticated'):
            print("❌ Non authentifié")
            return
        
        print("✅ Authentifié")
        
    except Exception as e:
        print(f"❌ Erreur authentification: {e}")
        return
    
    # 2. Tester les contrats ES connus
    working_contracts = test_known_es_contracts()
    
    # 3. Résumé
    if working_contracts:
        print(f"\n✅ {len(working_contracts)} contrats avec prix trouvés!")
        print(f"🎯 Contrats ES fonctionnels:")
        
        for conid, name, prices in working_contracts:
            print(f"  - {name} (ConID: {conid})")
            if prices['last']:
                print(f"    Prix actuel: {prices['last']}")
    else:
        print(f"\n❌ Aucun contrat avec prix trouvé")
        print(f"🔧 Problèmes possibles:")
        print(f"  - Permissions de données de marché insuffisantes")
        print(f"  - Heures de trading (marché fermé)")
        print(f"  - ConID incorrects")
    
    # 4. Nettoyer les souscriptions
    print(f"\n🧹 Nettoyage des souscriptions...")
    unsubscribe_all()
    
    print(f"\n👋 Script terminé")

if __name__ == "__main__":
    main()
