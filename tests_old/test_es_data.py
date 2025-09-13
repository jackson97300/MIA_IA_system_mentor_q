#!/usr/bin/env python3
"""
Test récupération données ES futures avec OHLC, volume et prix
"""

import sys
import time
import json
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

def test_es_data_retrieval():
    """Tester la récupération des données ES futures"""
    
    print("📊 Test récupération données ES futures (OHLC, Volume, Prix)")
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
        
        # 3. Recherche du contrat ES futures
        print("3️⃣ Recherche contrat ES futures...")
        es_contracts = connector.search_contract("ES", "FUT")
        
        if not es_contracts:
            print("❌ Aucun contrat ES futures trouvé")
            return False
        
        print(f"✅ {len(es_contracts)} contrat(s) ES trouvé(s)")
        
        # Afficher les contrats trouvés
        for i, contract in enumerate(es_contracts[:3]):  # Afficher les 3 premiers
            print(f"   Contrat {i+1}: {contract}")
        
        # Prendre le premier contrat ES
        es_conid = str(es_contracts[0].get("conid"))
        print(f"📋 Utilisation du contrat: {es_conid}")
        
        # 4. Récupération données historiques (OHLC)
        print("\n4️⃣ Récupération données historiques ES (OHLC)...")
        
        # Différentes périodes à tester
        periods = [
            ("1d", "1min", "1 jour - 1 minute"),
            ("5d", "5min", "5 jours - 5 minutes"),
            ("1m", "1hour", "1 mois - 1 heure")
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
        else:
            print("❌ Impossible de récupérer les données de marché")
        
        # 6. Test WebSocket pour données temps réel
        print("\n6️⃣ Test WebSocket pour données temps réel...")
        if connector.connect_websocket():
            print("✅ WebSocket connecté")
            
            # S'abonner aux données ES
            def market_data_callback(data):
                print(f"📊 Données temps réel reçues: {data}")
            
            if connector.subscribe_market_data(es_conid, fields, market_data_callback):
                print("✅ Abonnement aux données ES activé")
                print("   Attente de données temps réel (10 secondes)...")
                time.sleep(10)
            else:
                print("❌ Échec abonnement WebSocket")
        else:
            print("❌ Impossible de connecter le WebSocket")
        
        print("\n🎉 Test terminé avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False
        
    finally:
        connector.disconnect()

if __name__ == "__main__":
    success = test_es_data_retrieval()
    if not success:
        print("\n💡 Solutions possibles:")
        print("   1. Vérifiez que vous êtes connecté sur https://localhost:5000/")
        print("   2. Vérifiez que vous avez des permissions pour ES futures")
        print("   3. Vérifiez que le marché est ouvert")
        sys.exit(1)





