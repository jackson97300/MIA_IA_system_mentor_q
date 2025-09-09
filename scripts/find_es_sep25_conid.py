#!/usr/bin/env python3
"""
🔍 Recherche du ConID ES Sep19'25 @CME
Script qui trouve le bon ConID pour le contrat ES September 2025
"""

import sys
import requests
import json
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def find_es_sep25_conid():
    """Trouver le ConID pour ES Sep19'25 @CME"""
    print("🔍 Recherche ConID ES Sep19'25 @CME")
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
        
        # 2. Rechercher les contrats ES
        print(f"\n📈 Recherche contrats ES...")
        
        # Essayer différentes recherches
        search_terms = [
            "ES",
            "ES Sep",
            "ES Sep19",
            "ES Sep19'25",
            "ES Sep19'25 @CME"
        ]
        
        for search_term in search_terms:
            print(f"\n🔍 Recherche: '{search_term}'")
            
            search_response = requests.get(
                f"{base_url}/iserver/secdef/search",
                params={
                    "symbol": search_term,
                    "secType": "FUT",
                    "exchange": "CME"
                },
                verify=False,
                timeout=10
            )
            
            print(f"  Status: {search_response.status_code}")
            
            if search_response.status_code == 200:
                data = search_response.json()
                print(f"  Résultats: {len(data)} contrats trouvés")
                
                for i, contract in enumerate(data):
                    conid = contract.get('conid')
                    symbol = contract.get('symbol')
                    description = contract.get('description')
                    secType = contract.get('secType')
                    exchange = contract.get('exchange')
                    
                    print(f"    {i+1}. ConID: {conid}")
                    print(f"       Symbol: {symbol}")
                    print(f"       Description: {description}")
                    print(f"       Type: {secType}")
                    print(f"       Exchange: {exchange}")
                    
                    # Vérifier si c'est ES Sep19'25
                    if (symbol == "ES" and 
                        "Sep" in str(description) and 
                        "2025" in str(description) and
                        secType == "FUT" and
                        exchange == "CME"):
                        print(f"       ✅ CONTRAT TROUVÉ!")
                        return conid
                    
                    print()
            else:
                print(f"  ❌ Erreur {search_response.status_code}")
        
        # 3. Essayer avec des ConIDs connus pour ES
        print(f"\n🔍 Test avec ConIDs ES connus...")
        
        known_es_conids = [
            "265598",  # ES March 2025
            "265599",  # ES June 2025
            "265600",  # ES September 2025 (probable)
            "265601",  # ES December 2025
            "265602",  # ES March 2026
        ]
        
        for conid in known_es_conids:
            print(f"\n🔍 Test ConID: {conid}")
            
            # Récupérer les détails du contrat
            contract_response = requests.get(
                f"{base_url}/iserver/secdef/info",
                params={"conid": conid},
                verify=False,
                timeout=10
            )
            
            if contract_response.status_code == 200:
                contract_data = contract_response.json()
                print(f"  Détails: {json.dumps(contract_data, indent=2)}")
                
                # Vérifier si c'est ES Sep19'25
                symbol = contract_data.get('symbol')
                description = contract_data.get('description')
                secType = contract_data.get('secType')
                exchange = contract_data.get('exchange')
                
                if (symbol == "ES" and 
                    "Sep" in str(description) and 
                    "2025" in str(description) and
                    secType == "FUT" and
                    exchange == "CME"):
                    print(f"  ✅ CONTRAT ES Sep19'25 TROUVÉ!")
                    return conid
            else:
                print(f"  ❌ Erreur {contract_response.status_code}")
        
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_conid_with_market_data(conid):
    """Tester le ConID avec des données de marché"""
    if not conid:
        return None
    
    print(f"\n📊 Test données de marché pour ConID: {conid}")
    print("="*50)
    
    base_url = "https://localhost:5000/v1/api"
    
    try:
        # Essayer de récupérer les données de marché
        market_response = requests.get(
            f"{base_url}/iserver/marketdata/snapshot",
            params={
                "conids": conid,
                "fields": "31,83,84,86"
            },
            verify=False,
            timeout=10
        )
        
        print(f"Status: {market_response.status_code}")
        
        if market_response.status_code == 200:
            data = market_response.json()
            print(f"Données reçues: {json.dumps(data, indent=2)}")
            
            if isinstance(data, list) and len(data) > 0:
                tick_data = data[0]
                
                # Analyser les données
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
                    print(f"💰 Prix trouvés:")
                    for price_type, value in prices.items():
                        print(f"  {price_type}: {value}")
                    
                    # Vérifier si le prix est réaliste pour ES
                    if prices.get('last'):
                        last_price = float(prices['last'])
                        print(f"📊 Prix last: {last_price}")
                        
                        # Le prix ES devrait être autour de 6481
                        if 6000 <= last_price <= 7000:
                            print(f"✅ Prix réaliste pour ES!")
                            return prices
                        else:
                            print(f"⚠️ Prix suspect: {last_price}")
                    else:
                        print(f"⚠️ Pas de prix last")
                else:
                    print(f"⚠️ Aucun prix trouvé")
            else:
                print(f"⚠️ Pas de données dans la réponse")
        else:
            print(f"❌ Erreur {market_response.status_code}")
        
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def main():
    """Fonction principale"""
    print("🚀 Recherche ConID ES Sep19'25 @CME")
    print("="*50)
    
    # Trouver le ConID
    conid = find_es_sep25_conid()
    
    if conid:
        print(f"\n✅ ConID trouvé: {conid}")
        
        # Tester avec les données de marché
        prices = test_conid_with_market_data(conid)
        
        if prices:
            print(f"\n🎯 SUCCÈS! Prix ES Sep19'25 récupérés:")
            print(f"   Bid: {prices.get('bid', 'N/A')}")
            print(f"   Ask: {prices.get('ask', 'N/A')}")
            print(f"   Last: {prices.get('last', 'N/A')}")
            print(f"   Volume: {prices.get('volume', 'N/A')}")
        else:
            print(f"\n⚠️ ConID trouvé mais pas de données de marché")
    else:
        print(f"\n❌ ConID non trouvé")
        print(f"🔧 Problèmes possibles:")
        print(f"  - Contrat non disponible")
        print(f"  - Problème de recherche")
        print(f"  - Heures de trading")
    
    print(f"\n👋 Script terminé")

if __name__ == "__main__":
    main()

