#!/usr/bin/env python3
"""
Test simple de connexion IBKR Gateway
"""

import requests
import json
import time
from datetime import datetime

def test_gateway_connection():
    """Test simple de connexion au Gateway"""
    
    print("🔧 TEST SIMPLE CONNEXION IBKR GATEWAY")
    print("=" * 50)
    print(f"⏰ Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Configuration
    base_url = "https://localhost:5000/v1/api"
    
    try:
        # Test 1: Vérifier si le Gateway répond
        print("\n1️⃣ Test réponse Gateway...")
        
        response = requests.get(
            f"{base_url}/iserver/auth/status",
            verify=False,  # Ignorer les erreurs SSL pour localhost
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Gateway accessible!")
            data = response.json()
            print(f"Données: {json.dumps(data, indent=2)}")
            
            # Vérifier l'authentification
            if data.get('authenticated'):
                print("✅ Déjà authentifié!")
                return True
            else:
                print("⚠️ Non authentifié - Authentification requise")
                print("🌐 Ouvrez: https://localhost:5000")
                print("📝 Connectez-vous avec vos identifiants IBKR")
                
                # Attendre l'authentification
                print("\n⏳ Attente de l'authentification...")
                for i in range(30):
                    time.sleep(2)
                    response = requests.get(
                        f"{base_url}/iserver/auth/status",
                        verify=False,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('authenticated'):
                            print("✅ Authentification réussie!")
                            return True
                    
                    print(f"Tentative {i+1}/30...")
                
                print("❌ Authentification échouée")
                return False
                
        else:
            print(f"❌ Gateway non accessible: {response.status_code}")
            print("🔧 Vérifiez que IBKR Gateway est démarré")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connexion refusée")
        print("🔧 Vérifiez que IBKR Gateway est démarré sur https://localhost:5000")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Timeout de connexion")
        print("🔧 Vérifiez la connectivité réseau")
        return False
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_market_data():
    """Test récupération données de marché"""
    
    print("\n2️⃣ Test données de marché...")
    
    base_url = "https://localhost:5000/v1/api"
    
    try:
        # Rechercher ES futures
        response = requests.get(
            f"{base_url}/iserver/secdef/search",
            params={
                "symbol": "ES",
                "name": "true",
                "secType": "FUT"
            },
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            contracts = response.json()
            print(f"✅ {len(contracts)} contrats ES trouvés")
            
            if contracts:
                # Prendre le premier contrat
                conid = contracts[0].get("conid")
                print(f"CONID ES: {conid}")
                
                # Récupérer les données de marché
                response = requests.get(
                    f"{base_url}/iserver/marketdata/snapshot",
                    params={
                        "conids": conid,
                        "fields": "31,83,84,86"  # bid, ask, last, volume
                    },
                    verify=False,
                    timeout=10
                )
                
                if response.status_code == 200:
                    market_data = response.json()
                    print("✅ Données de marché récupérées")
                    print(f"Données: {json.dumps(market_data, indent=2)}")
                    return True
                else:
                    print(f"❌ Erreur données marché: {response.status_code}")
                    return False
            else:
                print("❌ Aucun contrat ES trouvé")
                return False
        else:
            print(f"❌ Erreur recherche contrats: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test données: {e}")
        return False

def main():
    """Fonction principale"""
    
    print("🚀 Démarrage test simple IBKR...")
    
    # Test 1: Connexion
    if test_gateway_connection():
        print("\n✅ Connexion réussie!")
        
        # Test 2: Données de marché
        if test_market_data():
            print("\n🎉 TOUS LES TESTS RÉUSSIS!")
            print("🚀 MIA_IA_SYSTEM prêt pour la session Asie!")
        else:
            print("\n⚠️ Problème avec les données de marché")
    else:
        print("\n❌ Échec de la connexion")
        print("🔧 Vérifiez IBKR Gateway")

if __name__ == "__main__":
    main()

