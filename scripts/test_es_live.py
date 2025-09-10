#!/usr/bin/env python3
"""
🎯 Test ES Live - Session Asiatique
Script simple pour tester le ConID ES Sep19'25 en temps réel
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

def test_es_conid_direct():
    """Test direct du ConID ES Sep19'25"""
    print("🎯 Test ES Sep19'25 - Session Asiatique")
    print("="*60)
    print(f"🕐 Timestamp: {datetime.now()}")
    
    # ConID ES Sep19'25 trouvé via TRSRV
    ES_SEP25_CONID = 637533641
    
    base_url = "https://localhost:5000/v1/api"
    session = requests.Session()
    session.verify = False
    
    try:
        # 1. Vérifier l'authentification
        print("🔐 Vérification authentification...")
        auth_response = session.get(f"{base_url}/iserver/auth/status", timeout=10)
        
        if auth_response.status_code != 200:
            print(f"❌ Erreur authentification: {auth_response.status_code}")
            return
        
        auth_data = auth_response.json()
        if not auth_data.get('authenticated'):
            print("❌ Authentification requise")
            return
        
        print("✅ Authentifié")
        
        # 2. Récupérer les détails du contrat
        print(f"\n📋 Détails contrat ConID: {ES_SEP25_CONID}")
        details_response = session.get(
            f"{base_url}/iserver/secdef/info",
            params={"conid": ES_SEP25_CONID},
            timeout=15
        )
        
        if details_response.status_code == 200:
            contract_data = details_response.json()
            print(f"✅ Détails contrat récupérés:")
            print(f"   Symbol: {contract_data.get('symbol')}")
            print(f"   SecType: {contract_data.get('secType')}")
            print(f"   Exchange: {contract_data.get('exchange')}")
            print(f"   Currency: {contract_data.get('currency')}")
            print(f"   LocalSymbol: {contract_data.get('localSymbol')}")
            print(f"   Expiry: {contract_data.get('expiry')}")
        else:
            print(f"❌ Erreur détails: {details_response.status_code}")
            return
        
        # 3. Test souscription données (POST)
        print(f"\n📡 Test souscription données...")
        subscribe_data = {
            "conids": [ES_SEP25_CONID],
            "fields": ["31", "83", "84", "86", "6", "7", "8", "9"]
        }
        
        print(f"   Données envoyées: {json.dumps(subscribe_data, indent=2)}")
        
        subscribe_response = session.post(
            f"{base_url}/iserver/marketdata/snapshot",
            json=subscribe_data,
            timeout=15
        )
        
        print(f"   Status: {subscribe_response.status_code}")
        print(f"   Réponse: {subscribe_response.text}")
        
        if subscribe_response.status_code == 200:
            print("✅ Souscription réussie")
            
            # 4. Attendre et récupérer les données
            print(f"\n⏳ Attente 5 secondes...")
            time.sleep(5)
            
            print(f"📊 Récupération données...")
            market_response = session.get(
                f"{base_url}/iserver/marketdata/snapshot",
                params={
                    "conids": ES_SEP25_CONID,
                    "fields": "31,83,84,86,6,7,8,9"
                },
                timeout=15
            )
            
            print(f"   Status: {market_response.status_code}")
            
            if market_response.status_code == 200:
                data = market_response.json()
                print(f"   Données reçues: {json.dumps(data, indent=2)}")
                
                if isinstance(data, list) and len(data) > 0:
                    tick_data = data[0]
                    
                    # Analyser les prix
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
                        print(f"\n🎉 SUCCÈS! Prix ES Sep19'25 récupérés:")
                        print(f"   Bid:     {prices.get('bid', 'N/A'):>10}")
                        print(f"   Ask:     {prices.get('ask', 'N/A'):>10}")
                        print(f"   Last:    {prices.get('last', 'N/A'):>10}")
                        print(f"   Volume:  {prices.get('volume', 'N/A'):>10}")
                        print(f"   High:    {prices.get('high', 'N/A'):>10}")
                        print(f"   Low:     {prices.get('low', 'N/A'):>10}")
                        print(f"   Open:    {prices.get('open', 'N/A'):>10}")
                        print(f"   Close:   {prices.get('close', 'N/A'):>10}")
                        
                        # Comparaison avec TWS
                        if prices.get('bid') and prices.get('ask'):
                            bid_price = float(prices['bid'])
                            ask_price = float(prices['ask'])
                            
                            print(f"\n📊 Comparaison avec TWS:")
                            print(f"   API Bid/Ask: {bid_price}/{ask_price}")
                            print(f"   TWS attendu: ~6481.00/~6481.25")
                            
                            if 6480 <= bid_price <= 6482 and 6480 <= ask_price <= 6482:
                                print(f"   🎯 Prix cohérent avec TWS!")
                            else:
                                print(f"   ⚠️ Prix différent de TWS")
                    else:
                        print(f"   ⚠️ Aucun prix trouvé dans les données")
                else:
                    print(f"   ⚠️ Pas de données dans la réponse")
            else:
                print(f"   ❌ Erreur récupération: {market_response.status_code}")
                print(f"   Détails: {market_response.text}")
        else:
            print(f"❌ Erreur souscription: {subscribe_response.status_code}")
            print(f"Détails: {subscribe_response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_es_conid_direct()

