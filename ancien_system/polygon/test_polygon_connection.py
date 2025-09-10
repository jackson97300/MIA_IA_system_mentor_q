#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test Connexion Polygon.io
Validation de la connexion avec la clé API Starter Plan
"""

import os
import requests
import json
from datetime import datetime
from typing import Dict, Any

# Configuration API
API_KEY = "wInzDiC4jEA4tgf4zfH98uRDRVbvPbcy"
BASE_URL = "https://api.polygon.io"

def test_api_connection():
    """Test de base de la connexion API"""
    print("🔧 TEST CONNEXION POLYGON.IO")
    print("=" * 50)
    
    # Test 1: Status API
    print("1️⃣ Test Status API...")
    try:
        url = f"{BASE_URL}/v1/marketstatus/now"
        response = requests.get(url, params={'apiKey': API_KEY})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data.get('status', 'Unknown')}")
            print(f"✅ Server Time: {data.get('serverTime', 'Unknown')}")
        else:
            print(f"❌ Erreur API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False
    
    return True

def test_options_data():
    """Test récupération données options SPX"""
    print("\n2️⃣ Test Données Options SPX...")
    
    try:
        # Récupérer options SPX
        url = f"{BASE_URL}/v3/reference/options/contracts"
        params = {
            'apiKey': API_KEY,
            'underlying_ticker': 'SPX',
            'limit': 10,
            'expiration_date.gte': '2025-09-01',
            'expiration_date.lte': '2025-10-31'
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"✅ Options SPX trouvées: {len(results)}")
            
            if results:
                option = results[0]
                print(f"✅ Exemple option:")
                print(f"   - Strike: {option.get('strike_price')}")
                print(f"   - Expiration: {option.get('expiration_date')}")
                print(f"   - Type: {option.get('contract_type')}")
                
            return True
        else:
            print(f"❌ Erreur options: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur options: {e}")
        return False

def test_stock_data():
    """Test récupération données actions (SPX)"""
    print("\n3️⃣ Test Données Actions SPX...")
    
    try:
        # Récupérer données SPX
        url = f"{BASE_URL}/v2/aggs/ticker/SPX/prev"
        params = {'apiKey': API_KEY}
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if results:
                tick = results[0]
                print(f"✅ SPX - Prix: ${tick.get('c', 'N/A')}")
                print(f"✅ SPX - Volume: {tick.get('v', 'N/A')}")
                print(f"✅ SPX - High: ${tick.get('h', 'N/A')}")
                print(f"✅ SPX - Low: ${tick.get('l', 'N/A')}")
                return True
            else:
                print("❌ Aucune donnée SPX trouvée")
                return False
        else:
            print(f"❌ Erreur SPX: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur SPX: {e}")
        return False

def test_rate_limits():
    """Test des limites du plan Starter"""
    print("\n4️⃣ Test Limites Plan Starter...")
    
    print("📊 Plan Starter Limits:")
    print("   - 5 calls/minute")
    print("   - Options différé 15min")
    print("   - Données historiques limitées")
    
    # Test multiple calls
    print("\n🔄 Test multiple calls...")
    success_count = 0
    
    for i in range(3):
        try:
            url = f"{BASE_URL}/v1/marketstatus/now"
            response = requests.get(url, params={'apiKey': API_KEY})
            
            if response.status_code == 200:
                success_count += 1
                print(f"   ✅ Call {i+1}: Succès")
            else:
                print(f"   ❌ Call {i+1}: Échec ({response.status_code})")
                
        except Exception as e:
            print(f"   ❌ Call {i+1}: Erreur ({e})")
    
    print(f"\n📊 Résultat: {success_count}/3 calls réussis")
    return success_count >= 2

def main():
    """Test principal"""
    print("🚀 VALIDATION POLYGON.IO STARTER PLAN")
    print("=" * 60)
    print(f"🔑 API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Connexion API", test_api_connection),
        ("Données Options", test_options_data),
        ("Données Actions", test_stock_data),
        ("Limites Plan", test_rate_limits)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur test {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ TESTS POLYGON.IO")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Tests réussis: {passed}/{len(results)}")
    
    if passed >= 3:
        print("🎉 POLYGON.IO STARTER PLAN VALIDÉ !")
        print("✅ Prêt pour intégration MIA_IA_SYSTEM")
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Vérifiez la configuration")

if __name__ == "__main__":
    main()











