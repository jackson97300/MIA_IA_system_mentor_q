#!/usr/bin/env python3
"""
Débogage du format des prix ES
Pourquoi 231.19 au lieu de 6481.25 ?
"""

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

def debug_es_price_format():
    """Déboguer le format des prix ES"""
    
    print("🔍 Débogage format prix ES")
    print("Prix attendu: ~6481.25")
    print("Prix reçu: 231.19")
    print("=" * 60)
    
    config = IBKRBetaConfig()
    connector = IBKRBetaConnector(config)
    
    try:
        if not connector.connect() or not connector.authenticate():
            print("❌ Connexion échouée")
            return
        
        print("✅ Connecté et authentifié")
        
        # Test avec le conid 265598
        es_conid = "265598"
        print(f"\n🔍 Test détaillé conid: {es_conid}")
        
        # 1. Test données brutes
        print("\n1️⃣ Données brutes...")
        fields = ["31", "83", "84", "86", "87", "88", "89", "90"]
        market_data = connector.get_market_data(es_conid, fields)
        
        if market_data and isinstance(market_data, list) and len(market_data) > 0:
            data = market_data[0]
            print("✅ Données brutes reçues:")
            for field, value in data.items():
                print(f"   {field}: {value} (type: {type(value)})")
            
            # 2. Analyse des prix
            print("\n2️⃣ Analyse des prix...")
            bid = data.get('31')
            ask = data.get('83')
            last = data.get('84')
            
            print(f"   Bid (31): {bid}")
            print(f"   Ask (83): {ask}")
            print(f"   Last (84): {last}")
            
            # 3. Test conversion
            print("\n3️⃣ Test conversions...")
            if bid:
                try:
                    bid_float = float(bid)
                    print(f"   Bid converti: {bid_float}")
                    
                    # Test différentes conversions
                    conversions = [
                        ("Normal", bid_float),
                        ("x10", bid_float * 10),
                        ("x25", bid_float * 25),
                        ("x28", bid_float * 28),  # 6481.25 / 231.19 ≈ 28
                        ("x50", bid_float * 50),
                        ("x100", bid_float * 100),
                    ]
                    
                    print("   Conversions possibles:")
                    for name, value in conversions:
                        if 6000 <= value <= 7000:
                            print(f"      {name}: {value} 🎯 (PRIX ES CORRECT!)")
                        else:
                            print(f"      {name}: {value}")
                            
                except ValueError:
                    print(f"   ❌ Bid non convertible: {bid}")
            
            # 4. Test données historiques
            print("\n4️⃣ Test données historiques...")
            historical = connector.get_historical_data(es_conid, "1d", "1min")
            if historical and len(historical) > 0:
                print(f"   ✅ {len(historical)} barres historiques")
                
                # Analyser les prix historiques
                prices = []
                for bar in historical[-5:]:  # 5 dernières barres
                    close = bar.get('c')
                    if close:
                        prices.append(float(close))
                
                if prices:
                    print(f"   Prix historiques (5 dernières): {prices}")
                    print(f"   Prix min: {min(prices)}")
                    print(f"   Prix max: {max(prices)}")
                    print(f"   Prix moyen: {sum(prices)/len(prices):.2f}")
                    
                    # Test conversion historique
                    if min(prices) < 1000:  # Si prix < 1000, probablement besoin conversion
                        print("   ⚠️ Prix historiques semblent bas - conversion nécessaire")
                        converted_prices = [p * 28 for p in prices]
                        print(f"   Prix convertis (x28): {converted_prices}")
            else:
                print("   ❌ Pas de données historiques")
            
            # 5. Recherche d'autres conids
            print("\n5️⃣ Recherche autres conids...")
            test_conids = ["265599", "265600", "265601", "265602"]
            
            for test_conid in test_conids:
                print(f"   Test conid: {test_conid}")
                test_data = connector.get_market_data(test_conid, ["31"])
                
                if test_data and isinstance(test_data, list) and len(test_data) > 0:
                    test_bid = test_data[0].get('31')
                    if test_bid and test_bid != "-1":
                        try:
                            test_price = float(test_bid)
                            print(f"      Bid: {test_price}")
                            
                            if 6000 <= test_price <= 7000:
                                print(f"      🎯 CONID ES CORRECT TROUVÉ: {test_conid}")
                                return test_conid
                        except ValueError:
                            pass
                else:
                    print(f"      Pas de données")
        
        print("\n💡 Conclusions:")
        print("   1. Le conid 265598 retourne des données")
        print("   2. Le prix 231.19 pourrait être correct mais mal formaté")
        print("   3. Possible problème de conversion ou d'échelle")
        print("   4. Vérifiez dans TWS le vrai conid ES")
        
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None
    finally:
        connector.disconnect()

def test_price_conversion(conid):
    """Tester la conversion de prix"""
    print(f"\n🧪 Test conversion prix pour conid: {conid}")
    
    config = IBKRBetaConfig()
    connector = IBKRBetaConnector(config)
    
    try:
        if not connector.connect() or not connector.authenticate():
            return False
        
        # Récupérer données
        market_data = connector.get_market_data(conid, ["31", "84"])
        historical = connector.get_historical_data(conid, "1d", "1min")
        
        if market_data and historical:
            data = market_data[0]
            bid = float(data.get('31', 0))
            
            print(f"   Prix brut: {bid}")
            
            # Test conversion x28
            converted_bid = bid * 28
            print(f"   Prix converti (x28): {converted_bid}")
            
            if 6000 <= converted_bid <= 7000:
                print(f"   ✅ Conversion x28 donne prix ES correct!")
                return True
            else:
                print(f"   ❌ Conversion x28 incorrecte")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ Erreur test conversion: {e}")
        return False
    finally:
        connector.disconnect()

if __name__ == "__main__":
    # Déboguer le format des prix
    debug_es_price_format()
    
    # Test conversion avec conid 265598
    print("\n" + "="*60)
    if test_price_conversion("265598"):
        print("\n🎉 Le conid 265598 est correct avec conversion x28!")
        print("💡 Utilisez: prix_es = prix_brut * 28")
    else:
        print("\n❌ Le conid 265598 nécessite une autre conversion")

