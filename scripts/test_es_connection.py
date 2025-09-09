#!/usr/bin/env python3
"""
🧪 Test rapide connexion IBKR et récupération prix ES
Script simple pour vérifier que tout fonctionne
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def test_ibkr_connection():
    """Test simple de connexion IBKR"""
    print("🔌 Test connexion IBKR BETA...")
    
    # Configuration
    base_url = "https://localhost:5000/v1/api"
    
    try:
        # Test 1: Vérifier si le gateway est accessible
        print("📡 Test 1: Accessibilité du gateway...")
        response = requests.get(
            f"{base_url}/iserver/auth/status",
            verify=False,  # Ignorer les erreurs SSL pour localhost
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Authentifié: {data.get('authenticated', 'N/A')}")
            print(f"   Connecté: {data.get('connected', 'N/A')}")
            print("✅ Gateway accessible")
        else:
            print("❌ Gateway non accessible")
            return False
        
        # Test 2: Vérifier l'authentification
        print("\n🔐 Test 2: Statut authentification...")
        if data.get('authenticated'):
            print("✅ Utilisateur authentifié")
            
            # Test 3: Récupérer les informations du compte
            print("\n📊 Test 3: Informations du compte...")
            account_response = requests.get(
                f"{base_url}/iserver/account",
                verify=False,
                timeout=10
            )
            
            if account_response.status_code == 200:
                account_data = account_response.json()
                print(f"   Compte: {account_data.get('id', 'N/A')}")
                print(f"   Nom: {account_data.get('name', 'N/A')}")
                print("✅ Informations compte récupérées")
            else:
                print("❌ Impossible de récupérer les informations du compte")
            
            # Test 4: Rechercher les contrats ES
            print("\n🔍 Test 4: Recherche contrats ES...")
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
                print(f"   {len(contracts)} contrats ES trouvés")
                
                if contracts:
                    # Afficher les 3 premiers contrats
                    for i, contract in enumerate(contracts[:3]):
                        print(f"   {i+1}. {contract.get('localSymbol', 'N/A')} - {contract.get('description', 'N/A')}")
                        print(f"      ConID: {contract.get('conid', 'N/A')}")
                        print(f"      Exchange: {contract.get('exchange', 'N/A')}")
                    
                    # Test 5: Récupérer les données de marché pour le premier contrat
                    first_conid = str(contracts[0].get("conid"))
                    print(f"\n📈 Test 5: Données de marché pour {contracts[0].get('localSymbol', 'N/A')}...")
                    
                    market_response = requests.get(
                        f"{base_url}/iserver/marketdata/snapshot",
                        params={
                            "conids": first_conid,
                            "fields": "31,83,84,86"  # bid, ask, last, volume
                        },
                        verify=False,
                        timeout=10
                    )
                    
                    if market_response.status_code == 200:
                        market_data = market_response.json()
                        print(f"   Données reçues: {len(market_data) if isinstance(market_data, list) else 'N/A'}")
                        
                        if market_data and isinstance(market_data, list) and len(market_data) > 0:
                            tick_data = market_data[0]
                            print(f"   ConID: {tick_data.get('conid', 'N/A')}")
                            print(f"   Données: {tick_data}")
                            print("✅ Données de marché récupérées")
                        else:
                            print("⚠️ Aucune donnée de marché disponible")
                    else:
                        print(f"❌ Erreur données de marché: {market_response.status_code}")
                else:
                    print("❌ Aucun contrat ES trouvé")
            else:
                print(f"❌ Erreur recherche contrats: {search_response.status_code}")
        else:
            print("⚠️ Utilisateur non authentifié")
            print("🌐 Veuillez vous connecter sur https://localhost:5000")
            print("📝 Connectez-vous avec vos identifiants IBKR")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au gateway IBKR")
        print("🔧 Vérifiez que le Client Portal Gateway est démarré")
        print("📁 Allez dans le dossier clientportal.beta.gw et lancez run.bat")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Timeout de connexion")
        return False
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def display_es_info():
    """Afficher les informations sur les contrats ES"""
    print("\n" + "="*60)
    print("📋 INFORMATIONS CONTRATS ES FUTURES")
    print("="*60)
    print("📈 Symbole: ES (E-mini S&P 500)")
    print("🏢 Exchange: CME (Chicago Mercantile Exchange)")
    print("💰 Multiplicateur: 50")
    print("📏 Tick Size: 0.25")
    print("💵 Tick Value: $12.50")
    print("💳 Marge initiale: $13,200")
    print("💳 Marge maintenance: $12,000")
    print("🕐 Horaires trading (ET):")
    print("   - Dimanche: 18:00 - Vendredi 17:00")
    print("   - Session régulière: 09:30 - 16:00")
    print("="*60)

def main():
    """Fonction principale"""
    print("🚀 Test connexion IBKR et récupération prix ES")
    print("="*50)
    
    # Afficher les informations ES
    display_es_info()
    
    # Tester la connexion
    success = test_ibkr_connection()
    
    if success:
        print("\n✅ Tous les tests réussis!")
        print("🎯 Vous pouvez maintenant utiliser le script get_es_futures_prices.py")
    else:
        print("\n❌ Tests échoués")
        print("🔧 Vérifiez votre configuration IBKR")
    
    print("\n👋 Test terminé")

if __name__ == "__main__":
    main()

