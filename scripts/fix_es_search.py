#!/usr/bin/env python3
"""
🔧 Correction recherche contrats ES Futures
Script pour trouver les vrais contrats ES avec les bons paramètres
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def find_real_es_contracts():
    """Trouver les vrais contrats ES"""
    print("🔧 Recherche des vrais contrats ES Futures")
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
            return None
        
        auth_data = auth_response.json()
        if not auth_data.get('authenticated'):
            print("❌ Non authentifié")
            return None
        
        print("✅ Authentifié")
        
        # 2. Essayer différentes méthodes de recherche
        search_methods = [
            # Méthode 1: Recherche simple ES
            {
                "name": "Recherche ES simple",
                "params": {"symbol": "ES", "secType": "FUT"}
            },
            # Méthode 2: Recherche avec exchange
            {
                "name": "Recherche ES + CME",
                "params": {"symbol": "ES", "secType": "FUT", "exchange": "CME"}
            },
            # Méthode 3: Recherche avec nom complet
            {
                "name": "Recherche E-mini S&P 500",
                "params": {"symbol": "E-mini S&P 500", "secType": "FUT"}
            },
            # Méthode 4: Recherche avec symbole local
            {
                "name": "Recherche ESM25",
                "params": {"symbol": "ESM25", "secType": "FUT"}
            },
            # Méthode 5: Recherche avec symbole local
            {
                "name": "Recherche ESH25",
                "params": {"symbol": "ESH25", "secType": "FUT"}
            },
            # Méthode 6: Recherche sans secType
            {
                "name": "Recherche ES sans type",
                "params": {"symbol": "ES"}
            },
            # Méthode 7: Recherche avec currency
            {
                "name": "Recherche ES + USD",
                "params": {"symbol": "ES", "secType": "FUT", "currency": "USD"}
            }
        ]
        
        found_contracts = []
        
        for method in search_methods:
            print(f"\n🔍 {method['name']}...")
            
            try:
                search_response = requests.get(
                    f"{base_url}/iserver/secdef/search",
                    params=method['params'],
                    verify=False,
                    timeout=10
                )
                
                if search_response.status_code == 200:
                    contracts = search_response.json()
                    print(f"  📋 {len(contracts)} contrats trouvés")
                    
                    # Filtrer les contrats valides (ConID > 0)
                    valid_contracts = []
                    for contract in contracts:
                        conid = contract.get("conid")
                        if conid and str(conid) != "-1" and str(conid) != "0":
                            valid_contracts.append(contract)
                    
                    print(f"  ✅ {len(valid_contracts)} contrats valides")
                    
                    if valid_contracts:
                        found_contracts.extend(valid_contracts)
                        print(f"  📊 Premier contrat valide:")
                        first_valid = valid_contracts[0]
                        print(f"    ConID: {first_valid.get('conid')}")
                        print(f"    Symbole: {first_valid.get('localSymbol')}")
                        print(f"    Description: {first_valid.get('description')}")
                        print(f"    Exchange: {first_valid.get('exchange')}")
                        print(f"    Type: {first_valid.get('secType')}")
                        print(f"    Devise: {first_valid.get('currency')}")
                    else:
                        print(f"  ⚠️ Aucun contrat valide")
                        
                        # Afficher les premiers contrats pour debug
                        if contracts:
                            print(f"  🔍 Aperçu des contrats trouvés:")
                            for i, contract in enumerate(contracts[:3]):
                                print(f"    {i+1}. ConID: {contract.get('conid')}, Type: {contract.get('secType')}, Symbole: {contract.get('localSymbol')}")
                else:
                    print(f"  ❌ Erreur {search_response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Erreur: {e}")
        
        # 3. Essayer une recherche directe par ConID connu
        print(f"\n🎯 Test avec ConID connu...")
        
        # ConID typiques pour ES futures (à ajuster selon votre compte)
        known_conids = [
            "265598",  # ES March 2025
            "265599",  # ES June 2025
            "265600",  # ES September 2025
            "265601",  # ES December 2025
            "265602",  # ES March 2026
        ]
        
        for conid in known_conids:
            print(f"  Test ConID: {conid}")
            
            try:
                # Essayer de récupérer les données directement
                market_response = requests.get(
                    f"{base_url}/iserver/marketdata/snapshot",
                    params={
                        "conids": conid,
                        "fields": "31,83,84,86"
                    },
                    verify=False,
                    timeout=10
                )
                
                if market_response.status_code == 200:
                    data = market_response.json()
                    if data and isinstance(data, list) and len(data) > 0:
                        tick_data = data[0]
                        if tick_data.get('conid') != -1:
                            print(f"    ✅ ConID {conid} valide!")
                            print(f"    Données: {tick_data}")
                            found_contracts.append({
                                "conid": conid,
                                "localSymbol": f"ES_{conid}",
                                "description": f"ES Futures ConID {conid}",
                                "exchange": "CME",
                                "secType": "FUT",
                                "currency": "USD"
                            })
                        else:
                            print(f"    ⚠️ ConID {conid} invalide")
                    else:
                        print(f"    ❌ Pas de données pour ConID {conid}")
                else:
                    print(f"    ❌ Erreur {market_response.status_code} pour ConID {conid}")
                    
            except Exception as e:
                print(f"    ❌ Erreur test ConID {conid}: {e}")
        
        # 4. Afficher les résultats
        if found_contracts:
            print(f"\n✅ {len(found_contracts)} contrats ES valides trouvés!")
            print(f"\n📋 Liste des contrats:")
            
            for i, contract in enumerate(found_contracts):
                print(f"\n--- Contrat {i+1} ---")
                print(f"ConID: {contract.get('conid')}")
                print(f"Symbole: {contract.get('localSymbol')}")
                print(f"Description: {contract.get('description')}")
                print(f"Exchange: {contract.get('exchange')}")
                print(f"Type: {contract.get('secType')}")
                print(f"Devise: {contract.get('currency')}")
            
            return found_contracts
        else:
            print(f"\n❌ Aucun contrat ES valide trouvé")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_market_data(contracts):
    """Tester les données de marché pour les contrats trouvés"""
    if not contracts:
        return
    
    print(f"\n📈 Test données de marché pour les contrats trouvés")
    print("="*50)
    
    base_url = "https://localhost:5000/v1/api"
    
    for i, contract in enumerate(contracts[:3]):  # Tester les 3 premiers
        conid = str(contract.get("conid"))
        symbol = contract.get("localSymbol", "ES")
        
        print(f"\n🔍 Test contrat {i+1}: {symbol} (ConID: {conid})")
        
        try:
            market_response = requests.get(
                f"{base_url}/iserver/marketdata/snapshot",
                params={
                    "conids": conid,
                    "fields": "31,83,84,86"
                },
                verify=False,
                timeout=10
            )
            
            if market_response.status_code == 200:
                data = market_response.json()
                if data and isinstance(data, list) and len(data) > 0:
                    tick_data = data[0]
                    print(f"  ✅ Données reçues")
                    print(f"  ConID: {tick_data.get('conid')}")
                    print(f"  Timestamp: {tick_data.get('_updated')}")
                    print(f"  Données brutes: {json.dumps(tick_data, indent=2)}")
                    
                    # Essayer de parser les prix
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
                    
                    if prices:
                        print(f"  💰 Prix extraits:")
                        for price_type, value in prices.items():
                            print(f"    {price_type}: {value}")
                    else:
                        print(f"  ⚠️ Aucun prix extrait")
                else:
                    print(f"  ❌ Pas de données")
            else:
                print(f"  ❌ Erreur {market_response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Erreur: {e}")

def main():
    """Fonction principale"""
    print("🚀 Correction recherche contrats ES")
    print("="*50)
    
    # Trouver les contrats
    contracts = find_real_es_contracts()
    
    # Tester les données de marché
    if contracts:
        test_market_data(contracts)
        print(f"\n✅ Recherche terminée avec succès!")
    else:
        print(f"\n❌ Aucun contrat trouvé")
    
    print(f"\n👋 Script terminé")

if __name__ == "__main__":
    main()

