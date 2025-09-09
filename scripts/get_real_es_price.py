#!/usr/bin/env python3
"""
💰 Récupération des vrais prix ES Futures
Script simple et direct pour obtenir les prix actuels
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def get_es_price():
    """Récupérer le prix ES actuel"""
    print("💰 Récupération prix ES Futures")
    print("="*40)
    
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
        
        # 2. Rechercher le contrat ES actuel (front month)
        print("\n🔍 Recherche contrat ES actuel...")
        search_response = requests.get(
            f"{base_url}/iserver/secdef/search",
            params={
                "symbol": "ES",
                "name": "true",
                "secType": "FUT"
            },
            verify=False,
            timeout=10
        )
        
        if search_response.status_code != 200:
            print("❌ Erreur recherche contrats")
            return None
        
        contracts = search_response.json()
        if not contracts:
            print("❌ Aucun contrat ES trouvé")
            return None
        
        # Prendre le premier contrat (front month)
        contract = contracts[0]
        conid = str(contract.get("conid"))
        symbol = contract.get("localSymbol", "ES")
        
        print(f"✅ Contrat trouvé: {symbol} (ConID: {conid})")
        
        # 3. Récupérer les données de marché
        print(f"\n📈 Récupération données de marché...")
        
        # Essayer différentes combinaisons de champs
        field_combinations = [
            "31,83,84,86",  # bid, ask, last, volume
            "84",           # last seulement
            "31,83,84",     # bid, ask, last
            "6,7,8,9"       # high, low, open, close
        ]
        
        market_data = None
        
        for fields in field_combinations:
            print(f"  Test champs: {fields}")
            
            market_response = requests.get(
                f"{base_url}/iserver/marketdata/snapshot",
                params={
                    "conids": conid,
                    "fields": fields
                },
                verify=False,
                timeout=10
            )
            
            if market_response.status_code == 200:
                data = market_response.json()
                if data and isinstance(data, list) and len(data) > 0:
                    market_data = data[0]
                    print(f"  ✅ Données reçues")
                    break
                else:
                    print(f"  ⚠️ Pas de données")
            else:
                print(f"  ❌ Erreur {market_response.status_code}")
        
        if not market_data:
            print("❌ Impossible de récupérer les données de marché")
            return None
        
        # 4. Analyser et afficher les données
        print(f"\n📊 Analyse des données reçues:")
        print(f"ConID: {market_data.get('conid')}")
        print(f"Timestamp: {market_data.get('_updated', 'N/A')}")
        
        # Essayer de parser les données selon différentes structures
        price_data = {
            'symbol': symbol,
            'conid': conid,
            'timestamp': datetime.now(),
            'bid': None,
            'ask': None,
            'last': None,
            'volume': None,
            'high': None,
            'low': None,
            'open': None,
            'close': None
        }
        
        # Méthode 1: Chercher directement dans les champs
        for key, value in market_data.items():
            if key == '31' and value:
                price_data['bid'] = value
            elif key == '83' and value:
                price_data['ask'] = value
            elif key == '84' and value:
                price_data['last'] = value
            elif key == '86' and value:
                price_data['volume'] = value
            elif key == '6' and value:
                price_data['high'] = value
            elif key == '7' and value:
                price_data['low'] = value
            elif key == '8' and value:
                price_data['open'] = value
            elif key == '9' and value:
                price_data['close'] = value
        
        # Méthode 2: Si les données sont dans une structure imbriquée
        if not any([price_data['bid'], price_data['ask'], price_data['last']]):
            print("🔍 Tentative parsing structure imbriquée...")
            for key, value in market_data.items():
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            field_id = item.get('f')
                            field_value = item.get('v')
                            if field_id == '31':
                                price_data['bid'] = field_value
                            elif field_id == '83':
                                price_data['ask'] = field_value
                            elif field_id == '84':
                                price_data['last'] = field_value
                            elif field_id == '86':
                                price_data['volume'] = field_value
        
        # 5. Afficher les résultats
        print(f"\n" + "="*50)
        print(f"💰 PRIX ES FUTURES - {symbol}")
        print(f"="*50)
        print(f"🕐 Timestamp: {price_data['timestamp']}")
        print(f"🆔 ConID: {price_data['conid']}")
        print(f"-"*50)
        print(f"💰 Bid:     {price_data['bid']:>10}")
        print(f"💰 Ask:     {price_data['ask']:>10}")
        print(f"💰 Last:    {price_data['last']:>10}")
        
        if price_data['ask'] and price_data['bid']:
            spread = float(price_data['ask']) - float(price_data['bid'])
            print(f"📊 Spread:  {spread:>10.2f}")
        
        print(f"-"*50)
        print(f"📈 Open:    {price_data['open']:>10}")
        print(f"📈 High:    {price_data['high']:>10}")
        print(f"📈 Low:     {price_data['low']:>10}")
        print(f"📈 Close:   {price_data['close']:>10}")
        print(f"-"*50)
        print(f"📊 Volume:  {price_data['volume']:>10}")
        print(f"="*50)
        
        # Calculer la valeur en dollars
        if price_data['last']:
            try:
                last_price = float(price_data['last'])
                dollar_value = last_price * 50  # Multiplicateur ES
                tick_value = 12.50  # Valeur tick ES
                print(f"💵 Valeur contrat: ${dollar_value:,.2f}")
                print(f"💵 Valeur tick: ${tick_value}")
            except:
                pass
        
        # 6. Afficher les données brutes pour debug
        print(f"\n🔍 Données brutes reçues:")
        print(json.dumps(market_data, indent=2))
        
        return price_data
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Fonction principale"""
    print("🚀 Récupération prix ES Futures")
    print("="*40)
    
    price_data = get_es_price()
    
    if price_data:
        print(f"\n✅ Prix récupéré avec succès!")
    else:
        print(f"\n❌ Échec récupération prix")
    
    print(f"\n👋 Script terminé")

if __name__ == "__main__":
    main()

