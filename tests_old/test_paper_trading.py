#!/usr/bin/env python3
"""
Test du Paper Trading IBKR
"""

import requests
import json
import urllib3

# Désactiver les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_paper_trading():
    """Test du Paper Trading"""
    print("=== TEST PAPER TRADING IBKR ===")
    
    base_url = "https://localhost:5000/v1/api"
    
    # Test 1: Vérifier l'authentification
    print("🔐 Vérification de l'authentification...")
    try:
        response = requests.get(f"{base_url}/iserver/auth/status", verify=False, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            auth_data = response.json()
            print("✅ Authentification OK")
            print(f"Authentifié: {auth_data.get('authenticated', False)}")
            print(f"Connecté: {auth_data.get('connected', False)}")
        else:
            print("❌ Authentification requise")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    print()
    
    # Test 2: Vérifier les comptes (Paper Trading)
    print("💰 Vérification des comptes Paper Trading...")
    try:
        response = requests.get(f"{base_url}/iserver/accounts", verify=False, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            accounts = response.json()
            print("✅ Comptes récupérés:")
            for account in accounts:
                print(f"  - {account}")
                
            # Vérifier s'il y a un compte Paper Trading
            paper_accounts = [acc for acc in accounts if "PAPER" in str(acc).upper()]
            if paper_accounts:
                print("✅ Compte Paper Trading détecté")
            else:
                print("⚠️ Aucun compte Paper Trading détecté")
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur comptes: {e}")
    
    print()
    
    # Test 3: Données ES en Paper Trading
    print("📊 Données ES en Paper Trading...")
    try:
        # Récupérer les données ES
        response = requests.get(f"{base_url}/iserver/marketdata/snapshot?conids=ES", verify=False, timeout=10)
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
    
    # Test 4: Positions Paper Trading
    print("📈 Positions Paper Trading...")
    try:
        response = requests.get(f"{base_url}/iserver/portfolio/positions", verify=False, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            positions = response.json()
            print("✅ Positions récupérées:")
            if positions:
                for pos in positions:
                    print(f"  - {pos}")
            else:
                print("  Aucune position ouverte")
        else:
            print(f"❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur positions: {e}")
    
    print()
    print("🎉 Test Paper Trading terminé !")

if __name__ == "__main__":
    test_paper_trading()













