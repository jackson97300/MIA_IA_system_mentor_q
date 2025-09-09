#!/usr/bin/env python3
"""
Test simple des données ES après authentification
"""

import requests
import json
import urllib3

# Désactiver les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_es_simple():
    """Test simple des données ES"""
    print("=== TEST SIMPLE DONNÉES ES ===")
    
    base_url = "https://localhost:5000/v1/api"
    
    # Test 1: Vérifier l'authentification
    print("🔐 Vérification de l'authentification...")
    try:
        response = requests.get(f"{base_url}/iserver/auth/status", verify=False, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Contenu: {response.text}")
        
        if response.status_code == 200:
            print("✅ Authentification OK")
        else:
            print("❌ Authentification requise")
            print("💡 Connectez-vous sur https://localhost:5000")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    print()
    
    # Test 2: Récupérer les données ES
    print("📊 Récupération des données ES...")
    try:
        # Demander un snapshot pour ES
        snapshot_data = {
            "conid": "ES",  # E-mini S&P 500
            "fields": ["31", "84", "86", "87", "88"]  # Volume, Bid, Ask, Last, High, Low
        }
        
        response = requests.post(
            f"{base_url}/iserver/marketdata/snapshot",
            json=snapshot_data,
            verify=False,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Données ES récupérées:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur données ES: {e}")
    
    print()
    
    # Test 3: Historique OHLC
    print("📈 Historique OHLC pour ES...")
    try:
        history_data = {
            "conid": "ES",
            "exchange": "CME",
            "period": "1min",
            "bar": "1min",
            "outsideRth": False
        }
        
        response = requests.post(
            f"{base_url}/iserver/marketdata/history",
            json=history_data,
            verify=False,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Historique OHLC récupéré:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur historique: {e}")
    
    print()
    print("🎉 Test terminé !")

if __name__ == "__main__":
    test_es_simple()













