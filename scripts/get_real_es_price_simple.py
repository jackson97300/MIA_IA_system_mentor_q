#!/usr/bin/env python3
"""
💰 Récupération des vrais prix ES - Version simple
Script qui récupère les prix ES réels depuis IBKR
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def get_real_es_price():
    """Récupérer le vrai prix ES"""
    print("💰 Récupération prix ES réel")
    print("="*40)
    
    base_url = "https://localhost:5000/v1/api"
    
    # ConID du contrat ES actuel (March 2025)
    es_conid = "265598"
    
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
        
        # 2. Récupérer les données de marché ES
        print(f"\n📈 Récupération données ES (ConID: {es_conid})...")
        
        # Essayer différentes méthodes
        methods = [
            # Méthode 1: Snapshot simple
            {
                "name": "Snapshot simple",
                "url": f"{base_url}/iserver/marketdata/snapshot",
                "params": {"conids": es_conid, "fields": "31,83,84,86"}
            },
            # Méthode 2: Snapshot avec plus de champs
            {
                "name": "Snapshot complet",
                "url": f"{base_url}/iserver/marketdata/snapshot",
                "params": {"conids": es_conid, "fields": "31,83,84,86,6,7,8,9"}
            },
            # Méthode 3: Historique récent
            {
                "name": "Historique 1 minute",
                "url": f"{base_url}/iserver/marketdata/history",
                "params": {"conid": es_conid, "period": "1d", "bar": "1min"}
            }
        ]
        
        for method in methods:
            print(f"\n🔍 Test: {method['name']}")
            
            try:
                response = requests.get(
                    method["url"],
                    params=method["params"],
                    verify=False,
                    timeout=10
                )
                
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  Données reçues: {json.dumps(data, indent=2)}")
                    
                    # Analyser les données
                    if isinstance(data, list) and len(data) > 0:
                        tick_data = data[0]
                        print(f"  ConID: {tick_data.get('conid')}")
                        
                        # Chercher les prix
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
                            print(f"  💰 Prix trouvés:")
                            for price_type, value in prices.items():
                                print(f"    {price_type}: {value}")
                            
                            # Vérifier si le prix est réaliste
                            if prices.get('last'):
                                last_price = float(prices['last'])
                                print(f"  📊 Prix ES: {last_price}")
                                
                                # Le prix ES devrait être autour de 6300-6400
                                if 6000 <= last_price <= 6500:
                                    print(f"  ✅ Prix réaliste!")
                                    return prices
                                else:
                                    print(f"  ⚠️ Prix suspect: {last_price}")
                            else:
                                print(f"  ⚠️ Pas de prix last")
                        else:
                            print(f"  ⚠️ Aucun prix trouvé")
                    else:
                        print(f"  ⚠️ Pas de données dans la réponse")
                else:
                    print(f"  ❌ Erreur {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Erreur: {e}")
        
        return None
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return None

def display_comparison(prices):
    """Afficher la comparaison avec le prix réel"""
    if not prices:
        return
    
    print(f"\n" + "="*60)
    print(f"💰 COMPARAISON PRIX ES")
    print(f"="*60)
    print(f"🕐 Timestamp: {datetime.now()}")
    print(f"-"*60)
    print(f"📊 Prix récupéré depuis IBKR:")
    print(f"  Bid:     {prices.get('bid', 'N/A')}")
    print(f"  Ask:     {prices.get('ask', 'N/A')}")
    print(f"  Last:    {prices.get('last', 'N/A')}")
    print(f"  Volume:  {prices.get('volume', 'N/A')}")
    print(f"-"*60)
    
    # Prix réel ES (approximatif)
    real_es_price = 6308.50  # Prix actuel approximatif
    print(f"📈 Prix réel ES (approximatif): {real_es_price}")
    
    if prices.get('last'):
        retrieved_price = float(prices['last'])
        difference = abs(retrieved_price - real_es_price)
        percentage = (difference / real_es_price) * 100
        
        print(f"📊 Différence: {difference:.2f} points ({percentage:.2f}%)")
        
        if difference < 10:
            print(f"✅ Prix cohérent!")
        elif difference < 50:
            print(f"⚠️ Prix proche mais à vérifier")
        else:
            print(f"❌ Prix très différent - problème détecté")
    
    print(f"="*60)

def main():
    """Fonction principale"""
    print("🚀 Vérification prix ES réel")
    print("="*40)
    
    # Récupérer les prix
    prices = get_real_es_price()
    
    # Afficher la comparaison
    if prices:
        display_comparison(prices)
        print(f"\n✅ Prix récupéré avec succès!")
    else:
        print(f"\n❌ Impossible de récupérer les prix")
        print(f"🔧 Problèmes possibles:")
        print(f"  - ConID incorrect")
        print(f"  - Heures de trading")
        print(f"  - Problème API IBKR")
    
    print(f"\n👋 Script terminé")

if __name__ == "__main__":
    main()

