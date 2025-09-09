#!/usr/bin/env python3
"""
🔍 Diagnostic des données ES Futures IBKR
Script pour analyser la vraie structure des données reçues
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def debug_ibkr_data():
    """Diagnostic complet des données IBKR"""
    print("🔍 Diagnostic des données IBKR ES Futures")
    print("="*50)
    
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
            return
        
        auth_data = auth_response.json()
        print(f"✅ Authentifié: {auth_data.get('authenticated')}")
        print(f"✅ Connecté: {auth_data.get('connected')}")
        
        # 2. Rechercher les contrats ES avec plus de détails
        print("\n🔍 Recherche détaillée contrats ES...")
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
        
        if search_response.status_code == 200:
            contracts = search_response.json()
            print(f"📋 {len(contracts)} contrats trouvés")
            
            if contracts:
                print("\n📊 Détails des contrats:")
                for i, contract in enumerate(contracts[:3]):
                    print(f"\n--- Contrat {i+1} ---")
                    print(f"ConID: {contract.get('conid')}")
                    print(f"Symbole: {contract.get('localSymbol')}")
                    print(f"Description: {contract.get('description')}")
                    print(f"Exchange: {contract.get('exchange')}")
                    print(f"Type: {contract.get('secType')}")
                    print(f"Devise: {contract.get('currency')}")
                    print(f"Classe: {contract.get('tradingClass')}")
                    print(f"Expiration: {contract.get('expiry')}")
                    print(f"Strike: {contract.get('strike')}")
                    print(f"Multiplicateur: {contract.get('multiplier')}")
                    print(f"Tous les champs: {json.dumps(contract, indent=2)}")
                
                # 3. Tester différents champs de données de marché
                first_conid = str(contracts[0].get("conid"))
                print(f"\n📈 Test données de marché pour ConID: {first_conid}")
                
                # Test avec différents champs
                field_sets = [
                    ["31", "83", "84", "86"],  # bid, ask, last, volume
                    ["31", "83", "84"],        # bid, ask, last
                    ["84"],                    # last seulement
                    ["31", "83"],              # bid, ask seulement
                    ["6", "7", "8", "9"],      # high, low, open, close
                    ["86"]                     # volume seulement
                ]
                
                for i, fields in enumerate(field_sets):
                    print(f"\n--- Test {i+1}: Champs {fields} ---")
                    
                    market_response = requests.get(
                        f"{base_url}/iserver/marketdata/snapshot",
                        params={
                            "conids": first_conid,
                            "fields": ",".join(fields)
                        },
                        verify=False,
                        timeout=10
                    )
                    
                    if market_response.status_code == 200:
                        market_data = market_response.json()
                        print(f"Status: {market_response.status_code}")
                        print(f"Données brutes: {json.dumps(market_data, indent=2)}")
                        
                        if market_data and isinstance(market_data, list) and len(market_data) > 0:
                            tick_data = market_data[0]
                            print(f"ConID reçu: {tick_data.get('conid')}")
                            print(f"ConID attendu: {first_conid}")
                            
                            # Analyser la structure des données
                            for key, value in tick_data.items():
                                print(f"  {key}: {value} (type: {type(value)})")
                        else:
                            print("⚠️ Aucune donnée dans la réponse")
                    else:
                        print(f"❌ Erreur {market_response.status_code}")
                
                # 4. Tester avec un contrat spécifique (ESM25 - March 2025)
                print(f"\n🎯 Test avec contrat spécifique ESM25...")
                
                # Chercher spécifiquement ESM25
                esm25_response = requests.get(
                    f"{base_url}/iserver/secdef/search",
                    params={
                        "symbol": "ESM25",
                        "name": "true",
                        "secType": "FUT"
                    },
                    verify=False,
                    timeout=10
                )
                
                if esm25_response.status_code == 200:
                    esm25_contracts = esm25_response.json()
                    print(f"Contrats ESM25 trouvés: {len(esm25_contracts)}")
                    
                    if esm25_contracts:
                        esm25_conid = str(esm25_contracts[0].get("conid"))
                        print(f"ConID ESM25: {esm25_conid}")
                        
                        # Test données ESM25
                        esm25_market_response = requests.get(
                            f"{base_url}/iserver/marketdata/snapshot",
                            params={
                                "conids": esm25_conid,
                                "fields": "31,83,84,86"
                            },
                            verify=False,
                            timeout=10
                        )
                        
                        if esm25_market_response.status_code == 200:
                            esm25_data = esm25_market_response.json()
                            print(f"Données ESM25: {json.dumps(esm25_data, indent=2)}")
                        else:
                            print(f"❌ Erreur données ESM25: {esm25_market_response.status_code}")
                
                # 5. Vérifier les permissions de données de marché
                print(f"\n🔐 Vérification permissions...")
                permissions_response = requests.get(
                    f"{base_url}/iserver/account/permissions",
                    verify=False,
                    timeout=10
                )
                
                if permissions_response.status_code == 200:
                    permissions = permissions_response.json()
                    print(f"Permissions: {json.dumps(permissions, indent=2)}")
                else:
                    print(f"❌ Erreur permissions: {permissions_response.status_code}")
                
            else:
                print("❌ Aucun contrat ES trouvé")
        else:
            print(f"❌ Erreur recherche contrats: {search_response.status_code}")
    
    except Exception as e:
        print(f"❌ Erreur diagnostic: {e}")
        import traceback
        traceback.print_exc()

def test_alternative_endpoints():
    """Tester des endpoints alternatifs"""
    print("\n🔄 Test endpoints alternatifs...")
    print("="*50)
    
    base_url = "https://localhost:5000/v1/api"
    
    # Endpoints à tester
    endpoints = [
        "/iserver/marketdata/unsubscribeall",
        "/iserver/marketdata/history",
        "/iserver/account/trades",
        "/iserver/account/positions"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n📡 Test {endpoint}...")
            response = requests.get(
                f"{base_url}{endpoint}",
                verify=False,
                timeout=5
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Réponse: {json.dumps(data, indent=2)[:200]}...")
        except Exception as e:
            print(f"❌ Erreur: {e}")

def main():
    """Fonction principale"""
    print("🚀 Diagnostic complet IBKR ES Futures")
    print("="*50)
    
    # Diagnostic principal
    debug_ibkr_data()
    
    # Test endpoints alternatifs
    test_alternative_endpoints()
    
    print("\n👋 Diagnostic terminé")

if __name__ == "__main__":
    main()

