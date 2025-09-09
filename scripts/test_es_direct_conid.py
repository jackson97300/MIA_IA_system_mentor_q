#!/usr/bin/env python3
"""
🎯 Test direct ES Sep19'25 avec ConID
Script qui teste directement avec le ConID d'ES Sep19'25
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def test_es_direct_conid():
    """Tester directement avec le ConID d'ES Sep19'25"""
    print("🎯 Test direct ES Sep19'25 avec ConID")
    print("="*50)
    
    base_url = "https://localhost:5000/v1/api"
    
    # Créer une session avec SSL désactivé
    session = requests.Session()
    session.verify = False
    
    try:
        # 1. Vérifier l'authentification
        print("🔐 Vérification authentification...")
        auth_response = session.get(
            f"{base_url}/iserver/auth/status",
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
        
        # 2. Test avec différents ConIDs possibles pour ES Sep19'25
        print(f"\n🔍 Test avec différents ConIDs ES...")
        
        # ConIDs possibles pour ES Sep19'25 (basés sur les recherches précédentes)
        possible_conids = [
            "265598",  # ES March 2025
            "265599",  # ES June 2025
            "265600",  # ES September 2025 (probable)
            "265601",  # ES December 2025
            "265602",  # ES March 2026
        ]
        
        for conid in possible_conids:
            print(f"\n🔍 Test ConID: {conid}")
            
            # Test 1: Récupérer les détails du contrat
            print(f"  📋 Récupération détails...")
            
            details_response = session.get(
                f"{base_url}/iserver/secdef/info",
                params={"conid": conid},
                timeout=10
            )
            
            print(f"    Status: {details_response.status_code}")
            
            if details_response.status_code == 200:
                contract_data = details_response.json()
                print(f"    Détails: {json.dumps(contract_data, indent=2)}")
                
                # Vérifier si c'est ES Sep19'25
                symbol = contract_data.get('symbol')
                description = contract_data.get('description')
                secType = contract_data.get('secType')
                exchange = contract_data.get('exchange')
                expiry = contract_data.get('expiry')
                
                print(f"    Symbol: {symbol}")
                print(f"    Description: {description}")
                print(f"    Type: {secType}")
                print(f"    Exchange: {exchange}")
                print(f"    Expiry: {expiry}")
                
                # Vérifier si c'est ES Sep19'25
                if (symbol == "ES" and 
                    "Sep" in str(description) and 
                    "2025" in str(description) and
                    secType == "FUT"):
                    print(f"    ✅ CONTRAT ES Sep19'25 TROUVÉ!")
                    
                    # Test 2: Récupérer les données de marché
                    print(f"  📊 Test données de marché...")
                    
                    # D'abord souscrire
                    subscribe_response = session.post(
                        f"{base_url}/iserver/marketdata/snapshot",
                        json={
                            "conids": [conid],
                            "fields": ["31", "83", "84", "86"]
                        },
                        timeout=10
                    )
                    
                    print(f"    Souscription status: {subscribe_response.status_code}")
                    
                    if subscribe_response.status_code == 200:
                        import time
                        time.sleep(3)
                        
                        # Récupérer les données
                        market_response = session.get(
                            f"{base_url}/iserver/marketdata/snapshot",
                            params={
                                "conids": conid,
                                "fields": "31,83,84,86"
                            },
                            timeout=10
                        )
                        
                        print(f"    Récupération status: {market_response.status_code}")
                        
                        if market_response.status_code == 200:
                            data = market_response.json()
                            print(f"    Données: {json.dumps(data, indent=2)}")
                            
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
                                    print(f"    💰 Prix trouvés:")
                                    for price_type, value in prices.items():
                                        print(f"      {price_type}: {value}")
                                    
                                    # Vérifier si le prix est réaliste pour ES
                                    if prices.get('last'):
                                        last_price = float(prices['last'])
                                        print(f"    📊 Prix last: {last_price}")
                                        
                                        # Le prix ES devrait être autour de 6481
                                        if 6000 <= last_price <= 7000:
                                            print(f"    ✅ Prix réaliste pour ES!")
                                            return {
                                                'conid': conid,
                                                'contract': contract_data,
                                                'prices': prices
                                            }
                                        else:
                                            print(f"    ⚠️ Prix suspect: {last_price}")
                                    else:
                                        print(f"    ⚠️ Pas de prix last")
                                else:
                                    print(f"    ⚠️ Aucun prix trouvé")
                            else:
                                print(f"    ⚠️ Pas de données dans la réponse")
                        else:
                            print(f"    ❌ Erreur récupération: {market_response.status_code}")
                    else:
                        print(f"    ❌ Erreur souscription: {subscribe_response.status_code}")
                else:
                    print(f"    ⚠️ Pas ES Sep19'25")
            else:
                print(f"    ❌ Erreur détails: {details_response.status_code}")
        
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None

def display_final_results(result):
    """Afficher les résultats finaux"""
    if not result:
        return
    
    conid = result['conid']
    contract = result['contract']
    prices = result['prices']
    
    print(f"\n" + "="*70)
    print(f"🎯 RÉSULTATS FINAUX - ES Sep19'25")
    print(f"="*70)
    print(f"🕐 Timestamp: {datetime.now()}")
    print(f"🔢 ConID: {conid}")
    print(f"-"*70)
    
    if contract:
        print(f"📋 Détails du contrat:")
        print(f"   Symbol: {contract.get('symbol', 'N/A')}")
        print(f"   Description: {contract.get('description', 'N/A')}")
        print(f"   Exchange: {contract.get('exchange', 'N/A')}")
        print(f"   Currency: {contract.get('currency', 'N/A')}")
        print(f"   Expiry: {contract.get('expiry', 'N/A')}")
        print(f"   SecType: {contract.get('secType', 'N/A')}")
    
    if prices:
        print(f"\n💰 Prix de marché:")
        print(f"   Bid:     {prices.get('bid', 'N/A'):>10}")
        print(f"   Ask:     {prices.get('ask', 'N/A'):>10}")
        print(f"   Last:    {prices.get('last', 'N/A'):>10}")
        print(f"   Volume:  {prices.get('volume', 'N/A'):>10}")
        
        # Calculer le spread
        if prices.get('ask') and prices.get('bid'):
            try:
                spread = float(prices['ask']) - float(prices['bid'])
                print(f"   Spread:  {spread:>10.2f}")
            except:
                pass
        
        # Calculer la valeur en dollars
        if prices.get('last'):
            try:
                last_price = float(prices['last'])
                dollar_value = last_price * 50  # Multiplicateur ES
                tick_value = 12.50  # Valeur tick ES
                print(f"   Valeur contrat: ${dollar_value:,.2f}")
                print(f"   Valeur tick: ${tick_value}")
            except:
                pass
        
        # Vérifier la cohérence avec TWS
        if prices.get('bid') and prices.get('ask'):
            bid_price = float(prices['bid'])
            ask_price = float(prices['ask'])
            
            expected_bid = 6481.00
            expected_ask = 6481.25
            
            bid_diff = abs(bid_price - expected_bid)
            ask_diff = abs(ask_price - expected_ask)
            
            print(f"\n📊 Comparaison avec TWS:")
            print(f"   TWS Bid/Ask: {expected_bid}/{expected_ask}")
            print(f"   API Bid/Ask: {bid_price}/{ask_price}")
            print(f"   Diff Bid: {bid_diff:.2f}")
            print(f"   Diff Ask: {ask_diff:.2f}")
            
            if bid_diff < 1 and ask_diff < 1:
                print(f"   🎯 Prix parfaitement cohérent!")
            elif bid_diff < 10 and ask_diff < 10:
                print(f"   ✅ Prix cohérent")
            else:
                print(f"   ⚠️ Prix différent")
    
    print(f"="*70)

def main():
    """Fonction principale"""
    print("🚀 Test direct ES Sep19'25 avec ConID")
    print("="*50)
    
    # Tester avec les ConIDs
    result = test_es_direct_conid()
    
    if result:
        display_final_results(result)
        print(f"\n🎯 SUCCÈS! Prix ES Sep19'25 récupérés avec succès!")
        print(f"✅ ConID trouvé: {result['conid']}")
    else:
        print(f"\n❌ Aucun contrat ES Sep19'25 trouvé")
        print(f"🔧 Problèmes possibles:")
        print(f"  - Contrat non disponible")
        print(f"  - ConID incorrect")
        print(f"  - Heures de trading")
        print(f"  - Permissions de données de marché")
    
    print(f"\n👋 Script terminé")

if __name__ == "__main__":
    main()

