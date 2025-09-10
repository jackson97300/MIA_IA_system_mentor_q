#!/usr/bin/env python3
"""
Test de connexion au Gateway IBKR BETA
"""

import requests
import time
import urllib3

# Désactiver les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_gateway():
    print("=== TEST CONNEXION GATEWAY IBKR ===")
    
    gateway_url = "https://localhost:5000"
    api_base = f"{gateway_url}/v1/api"
    
    print(f"Gateway URL: {gateway_url}")
    print(f"API Base: {api_base}")
    print()
    
    # Test de base
    print("🔍 Test de connexion de base...")
    try:
        response = requests.get(gateway_url, verify=False, timeout=10)
        print(f"✅ Réponse HTTP: {response.status_code}")
        print(f"Contenu: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Erreur connexion de base: {e}")
        return False
    
    print()
    
    # Test API
    print("🔍 Test API IBKR...")
    try:
        response = requests.get(f"{api_base}/iserver/auth/status", verify=False, timeout=10)
        print(f"✅ Réponse API: {response.status_code}")
        print(f"Contenu: {response.text}")
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return False
    
    print()
    
    # Test autres endpoints
    endpoints = [
        "/iserver/account",
        "/iserver/accounts",
        "/iserver/marketdata/snapshot",
        "/iserver/portfolio/accounts"
    ]
    
    print("🔍 Test des endpoints...")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{api_base}{endpoint}", verify=False, timeout=5)
            print(f"  {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"  {endpoint}: ❌ {e}")
    
    print()
    print("✅ Test terminé")
    return True

def monitor_gateway():
    """Surveiller le gateway en continu"""
    print("=== SURVEILLANCE GATEWAY ===")
    print("Appuyez sur Ctrl+C pour arrêter")
    print()
    
    gateway_url = "https://localhost:5000/v1/api/iserver/auth/status"
    
    try:
        while True:
            try:
                response = requests.get(gateway_url, verify=False, timeout=5)
                if response.status_code == 200:
                    print(f"✅ Gateway OK - {time.strftime('%H:%M:%S')}")
                else:
                    print(f"⚠️ Gateway répond mais erreur {response.status_code} - {time.strftime('%H:%M:%S')}")
            except Exception as e:
                print(f"❌ Gateway non accessible - {time.strftime('%H:%M:%S')}")
            
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n🛑 Surveillance arrêtée")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor_gateway()
    else:
        test_gateway()













