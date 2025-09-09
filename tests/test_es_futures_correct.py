#!/usr/bin/env python3
"""
Test récupération données ES futures avec le bon conid
"""

import sys
import time
import json
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

def test_es_futures_data():
    """Tester la récupération des données ES futures avec le bon conid"""
    
    print("📊 Test récupération données ES futures (E-mini S&P 500)")
    print("=" * 70)
    
    # Configuration
    config = IBKRBetaConfig()
    connector = IBKRBetaConnector(config)
    
    try:
        # 1. Connexion et authentification
        print("1️⃣ Connexion au gateway...")
        if not connector.connect():
            print("❌ Impossible de se connecter au gateway")
            return False
        
        print("2️⃣ Vérification authentification...")
        if not connector.config.authenticated:
            print("⚠️ Non authentifié - tentative d'authentification...")
            if not connector.authenticate():
                print("❌ Authentification échouée")
                return False
        
        # 3. Recherche spécifique ES futures
        print("3️⃣ Recherche contrats ES futures...")
        
        # Essayer différentes méthodes de recherche
        search_terms = [
            ("ES", "FUT"),
            ("ES1!", "FUT"),  # ES futures front month
            ("ESZ4", "FUT"),  # ES December 2024
            ("ESM4", "FUT"),  # ES March 2024
        ]
        
        es_conid = None
        for symbol, secType in search_terms:
            print(f"   🔍 Recherche: {symbol} ({secType})...")
            contracts = connector.search_contract(symbol, secType)
            
            if contracts:
                print(f"   ✅ {len(contracts)} contrat(s) trouvé(s)")
                
                # Filtrer les vrais contrats ES futures
                for contract in contracts:
                    contract_info = contract.get('companyHeader', '') or contract.get('description', '') or contract.get('symbol', '')
                    if 'ES' in str(contract_info) and 'future' in str(contract_info).lower():
                        es_conid = str(contract.get("conid"))
                        print(f"   🎯 Contrat ES futures trouvé: {contract_info}")
                        print(f"   📋 Conid: {es_conid}")
                        break
                
                if es_conid and es_conid != "-1":
                    break
        
        if not es_conid or es_conid == "-1":
            print("❌ Aucun contrat ES futures valide trouvé")
            print("💡 Tentative avec conid connu pour ES...")
            
            # Conid connu pour ES futures (à ajuster selon votre compte)
            known_es_conids = [
                "265598",  # ES futures example
                "265599",  # ES futures example
                "265600",  # ES futures example
            ]
            
            for conid in known_es_conids:
                print(f"   🔍 Test avec conid: {conid}")
                market_data = connector.get_market_data(conid, ["31", "84"])  # bid, last
                if market_data and market_data.get("conid") != "-1":
                    es_conid = conid
                    print(f"   ✅ Conid valide trouvé: {es_conid}")
                    break
        
        if not es_conid or es_conid == "-1":
            print("❌ Impossible de trouver un conid valide pour ES futures")
            return False
        
        print(f"📋 Utilisation du contrat ES: {es_conid}")
        
        # 4. Récupération données historiques (OHLC)
        print("\n4️⃣ Récupération données historiques ES (OHLC)...")
        
        # Test avec différentes périodes
        periods = [
            ("1d", "1min", "1 jour - 1 minute"),
            ("5d", "5min", "5 jours - 5 minutes"),
        ]
        
        for period, bar, description in periods:
            print(f"\n   📈 {description}...")
            historical_data = connector.get_historical_data(es_conid, period, bar)
            
            if historical_data:
                print(f"   ✅ {len(historical_data)} barres récupérées")
                
                # Afficher les 3 premières barres
                for i, bar_data in enumerate(historical_data[:3]):
                    print(f"      Barre {i+1}: {bar_data}")
            else:
                print(f"   ❌ Aucune donnée pour {description}")
        
        # 5. Récupération données temps réel (prix actuels)
        print("\n5️⃣ Récupération données temps réel ES...")
        
        # Champs pour les données de marché
        fields = [
            "31",  # bid
            "83",  # ask  
            "84",  # last
            "86",  # volume
            "87",  # high
            "88",  # low
            "89",  # open
            "90"   # close
        ]
        
        market_data = connector.get_market_data(es_conid, fields)
        
        if market_data:
            print("✅ Données de marché récupérées")
            print(f"   Données: {json.dumps(market_data, indent=2)}")
            
            # Afficher les prix de manière lisible
            if isinstance(market_data, list) and len(market_data) > 0:
                data = market_data[0]
                print(f"   📊 Prix ES:")
                print(f"      Bid: {data.get('31', 'N/A')}")
                print(f"      Ask: {data.get('83', 'N/A')}")
                print(f"      Last: {data.get('84', 'N/A')}")
                print(f"      Volume: {data.get('86', 'N/A')}")
                print(f"      High: {data.get('87', 'N/A')}")
                print(f"      Low: {data.get('88', 'N/A')}")
                print(f"      Open: {data.get('89', 'N/A')}")
                print(f"      Close: {data.get('90', 'N/A')}")
        else:
            print("❌ Impossible de récupérer les données de marché")
        
        print("\n🎉 Test terminé avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False
        
    finally:
        connector.disconnect()

if __name__ == "__main__":
    success = test_es_futures_data()
    if not success:
        print("\n💡 Solutions possibles:")
        print("   1. Vérifiez que vous êtes connecté sur https://localhost:5000/")
        print("   2. Vérifiez que vous avez des permissions pour ES futures")
        print("   3. Vérifiez que le marché est ouvert")
        print("   4. Essayez de rechercher manuellement le conid ES dans TWS")
        sys.exit(1)

