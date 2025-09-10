#!/usr/bin/env python3
"""
Débogage format prix IBKR
Vérifier pourquoi multiplication par 25.030 nécessaire
"""

import sys
import json
import requests
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

def test_direct_api_call():
    """Test appel API direct pour vérifier format"""
    
    print("🔍 Test appel API direct IBKR")
    print("=" * 50)
    
    # URL directe IBKR Client Portal Gateway
    base_url = "https://localhost:5000/v1/api"
    
    # Headers pour ignorer SSL
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'MIA_IA_SYSTEM'
    }
    
    try:
        # Test 1: Vérifier si l'API répond
        print("1️⃣ Test connexion API...")
        response = requests.get(f"{base_url}/tickle", headers=headers, verify=False)
        
        if response.status_code == 200:
            print("✅ API accessible")
            print(f"   Réponse: {response.text}")
        else:
            print(f"❌ API non accessible: {response.status_code}")
            return False
        
        # Test 2: Vérifier session
        print("\n2️⃣ Test session...")
        session_response = requests.get(f"{base_url}/iserver/auth/status", headers=headers, verify=False)
        
        if session_response.status_code == 200:
            session_data = session_response.json()
            print(f"   Status session: {session_data}")
            
            if session_data.get('authenticated'):
                print("✅ Session authentifiée")
            else:
                print("❌ Session non authentifiée")
                return False
        else:
            print(f"❌ Erreur session: {session_response.status_code}")
            return False
        
        # Test 3: Rechercher contrat ES
        print("\n3️⃣ Recherche contrat ES...")
        search_data = {
            "symbol": "ES",
            "name": True,
            "secType": "FUT"
        }
        
        search_response = requests.post(
            f"{base_url}/iserver/secdef/search", 
            json=search_data, 
            headers=headers, 
            verify=False
        )
        
        if search_response.status_code == 200:
            contracts = search_response.json()
            print(f"   Contrats trouvés: {len(contracts)}")
            
            for i, contract in enumerate(contracts[:5]):  # 5 premiers
                print(f"   {i+1}. {contract}")
        else:
            print(f"❌ Erreur recherche: {search_response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test API: {e}")
        return False

def test_price_fields():
    """Tester différents champs de prix"""
    
    print("\n🔍 Test champs prix différents")
    print("=" * 50)
    
    config = IBKRBetaConfig()
    connector = IBKRBetaConnector(config)
    
    try:
        if not connector.connect() or not connector.authenticate():
            print("❌ Connexion échouée")
            return
        
        print("✅ Connecté et authentifié")
        
        # Conid ES
        es_conid = "265598"
        
        # Test différents champs de prix
        price_fields = [
            ["31"],           # Bid
            ["83"],           # Ask  
            ["84"],           # Last
            ["31", "83"],     # Bid + Ask
            ["31", "83", "84"], # Bid + Ask + Last
            ["86"],           # Volume
            ["87"],           # High
            ["88"],           # Low
            ["89"],           # Open
            ["90"],           # Close
        ]
        
        for fields in price_fields:
            print(f"\n   Test champs: {fields}")
            
            market_data = connector.get_market_data(es_conid, fields)
            
            if market_data and isinstance(market_data, list) and len(market_data) > 0:
                data = market_data[0]
                print(f"      Données: {data}")
                
                # Analyser les valeurs
                for field in fields:
                    value = data.get(field)
                    if value and value != "-1":
                        try:
                            float_val = float(value)
                            print(f"      {field}: {float_val}")
                            
                            # Test différentes conversions
                            conversions = [
                                ("Normal", float_val),
                                ("x10", float_val * 10),
                                ("x25", float_val * 25),
                                ("x50", float_val * 50),
                                ("x100", float_val * 100),
                            ]
                            
                            for name, conv_val in conversions:
                                if 6000 <= conv_val <= 7000:
                                    print(f"         {name}: {conv_val} 🎯 (PRIX ES!)")
                                elif 200 <= conv_val <= 300:
                                    print(f"         {name}: {conv_val} ⚠️ (Prix suspect)")
                        except ValueError:
                            print(f"      {field}: {value} (non numérique)")
            else:
                print(f"      ❌ Pas de données")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test prix: {e}")
        return False
    finally:
        connector.disconnect()

def check_ibkr_documentation():
    """Vérifier la documentation IBKR"""
    
    print("\n📚 Vérification documentation IBKR")
    print("=" * 50)
    
    print("🔍 Points à vérifier:")
    print("   1. Format des prix dans Client Portal Gateway")
    print("   2. Échelle des prix pour futures")
    print("   3. Différence entre TWS et Gateway")
    print("   4. Champs de données disponibles")
    
    print("\n💡 Hypothèses possibles:")
    print("   - Prix en points vs prix en dollars")
    print("   - Échelle différente pour futures")
    print("   - Bug dans l'API BETA")
    print("   - Configuration incorrecte")
    
    print("\n🔧 Solutions à tester:")
    print("   1. Vérifier si prix en points (1 point = $50)")
    print("   2. Tester avec TWS au lieu de Gateway")
    print("   3. Vérifier documentation IBKR officielle")
    print("   4. Contacter support IBKR")

def main():
    """Fonction principale"""
    
    print("🚀 Débogage format prix IBKR")
    print("Problème: multiplication par 25.030 nécessaire")
    print("=" * 60)
    
    # Test 1: Appel API direct
    if test_direct_api_call():
        print("\n✅ API directe fonctionne")
    else:
        print("\n❌ API directe échoue")
    
    # Test 2: Champs prix
    if test_price_fields():
        print("\n✅ Test champs prix terminé")
    else:
        print("\n❌ Test champs prix échoue")
    
    # Test 3: Documentation
    check_ibkr_documentation()
    
    print("\n💡 Recommandations:")
    print("   1. Vérifier si le prix 231.19 est en points")
    print("   2. Si oui: 231.19 * 50 = 11,559.50 (trop haut)")
    print("   3. Vérifier si c'est un bug de l'API BETA")
    print("   4. Tester avec TWS classique si possible")

if __name__ == "__main__":
    main()

