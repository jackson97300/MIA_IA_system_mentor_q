#!/usr/bin/env python3
"""
🎯 Test ES Alternative - Approches multiples
Script qui teste différentes approches pour récupérer les données ES
"""

import sys
import requests
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from urllib3.exceptions import InsecureRequestWarning
import warnings

# Supprimer les warnings SSL pour localhost
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def test_es_alternative():
    """Test d'approches alternatives pour ES"""
    print("🎯 Test ES Alternative - Approches multiples")
    print("="*60)
    print(f"🕐 Timestamp: {datetime.now()}")
    
    # ConID ES Sep19'25
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
        
        # 2. Test 1: Données historiques (alternative)
        print(f"\n📊 Test 1: Données historiques ES Sep19'25")
        
        # Date actuelle
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        
        hist_response = session.get(
            f"{base_url}/iserver/marketdata/history",
            params={
                "conid": ES_SEP25_CONID,
                "exchange": "CME",
                "period": "1d",
                "bar": "1min",
                "startTime": start_date,
                "endTime": end_date
            },
            timeout=15
        )
        
        print(f"   Status: {hist_response.status_code}")
        
        if hist_response.status_code == 200:
            hist_data = hist_response.json()
            print(f"   ✅ Données historiques récupérées")
            print(f"   Données: {json.dumps(hist_data, indent=2)}")
        else:
            print(f"   ❌ Erreur historiques: {hist_response.status_code}")
            print(f"   Détails: {hist_response.text}")
        
        # 3. Test 2: Essayer avec un ConID différent (ES Dec24'24)
        print(f"\n📊 Test 2: Test avec ES Dec24'24")
        
        # ConID ES Dec24'24 (plus proche)
        ES_DEC24_CONID = 495512563  # Trouvé dans TRSRV
        
        subscribe_data = {
            "conids": [ES_DEC24_CONID],
            "fields": ["31", "83", "84", "86", "6", "7", "8", "9"]
        }
        
        subscribe_response = session.post(
            f"{base_url}/iserver/marketdata/snapshot",
            json=subscribe_data,
            timeout=15
        )
        
        print(f"   Status: {subscribe_response.status_code}")
        
        if subscribe_response.status_code == 200:
            print("✅ Souscription ES Dec24'24 réussie")
            
            time.sleep(3)
            
            market_response = session.get(
                f"{base_url}/iserver/marketdata/snapshot",
                params={
                    "conids": ES_DEC24_CONID,
                    "fields": "31,83,84,86,6,7,8,9"
                },
                timeout=15
            )
            
            if market_response.status_code == 200:
                data = market_response.json()
                print(f"   ✅ Données ES Dec24'24 récupérées")
                print(f"   Données: {json.dumps(data, indent=2)}")
            else:
                print(f"   ❌ Erreur récupération: {market_response.status_code}")
        else:
            print(f"   ❌ Erreur souscription: {subscribe_response.status_code}")
        
        # 4. Test 3: Vérifier les permissions de données
        print(f"\n📊 Test 3: Vérification permissions")
        
        permissions_response = session.get(
            f"{base_url}/iserver/account/permissions",
            timeout=15
        )
        
        print(f"   Status: {permissions_response.status_code}")
        
        if permissions_response.status_code == 200:
            permissions_data = permissions_response.json()
            print(f"   ✅ Permissions récupérées")
            print(f"   Permissions: {json.dumps(permissions_data, indent=2)}")
        else:
            print(f"   ❌ Erreur permissions: {permissions_response.status_code}")
        
        # 5. Test 4: Vérifier le statut du serveur
        print(f"\n📊 Test 4: Statut serveur")
        
        server_response = session.get(
            f"{base_url}/iserver/server/status",
            timeout=15
        )
        
        print(f"   Status: {server_response.status_code}")
        
        if server_response.status_code == 200:
            server_data = server_response.json()
            print(f"   ✅ Statut serveur récupéré")
            print(f"   Statut: {json.dumps(server_data, indent=2)}")
        else:
            print(f"   ❌ Erreur statut: {server_response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_es_alternative()

