#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Direct Statut Authentification IBKR
Vérification directe du statut d'authentification
"""

import requests
import json
import urllib3

# Désactiver les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_auth_status():
    """Test direct du statut d'authentification"""
    print("🔍 TEST DIRECT STATUT AUTHENTIFICATION IBKR")
    print("=" * 50)
    
    try:
        # Test 1: Statut d'authentification
        print("1️⃣ Test statut d'authentification...")
        response = requests.get('https://localhost:5000/v1/api/iserver/auth/status', 
                              verify=False, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Réponse JSON: {json.dumps(data, indent=2)}")
            
            authenticated = data.get('authenticated', False)
            print(f"   Authenticated: {authenticated}")
            
            if authenticated:
                print("✅ Authentification confirmée!")
            else:
                print("⚠️ Non authentifié")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
        
        print("\n2️⃣ Test informations compte...")
        response = requests.get('https://localhost:5000/v1/api/iserver/account', 
                              verify=False, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Réponse JSON: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
        
        print("\n3️⃣ Test positions...")
        response = requests.get('https://localhost:5000/v1/api/iserver/account/positions', 
                              verify=False, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Réponse JSON: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
        
        print("\n4️⃣ Test données marché ES...")
        # ConID pour ES futures
        es_conid = "13893091"
        response = requests.get(f'https://localhost:5000/v1/api/iserver/marketdata/snapshot?conids={es_conid}&fields=31,83,84,86', 
                              verify=False, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Réponse JSON: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
        
        print("\n5️⃣ Test données historiques ES...")
        response = requests.get(f'https://localhost:5000/v1/api/iserver/marketdata/history?conid={es_conid}&period=1d&bar=1min', 
                              verify=False, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Réponse JSON: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_auth_status()










