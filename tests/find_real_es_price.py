#!/usr/bin/env python3
"""
Trouver le vrai conid ES avec le bon prix (~6481.25)
"""

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

def find_real_es_conid():
    """Trouver le vrai conid ES avec le bon prix"""
    
    print("🔍 Recherche du vrai conid ES (prix ~6481.25)")
    print("=" * 60)
    
    # Conids à tester (plus large gamme)
    test_conids = [
        # Conids ES futures possibles
        "265598",  # Testé (231.19 - incorrect)
        "265599",  # À tester
        "265600",  # À tester
        "265601",  # À tester
        "265602",  # À tester
        "265603",  # À tester
        "265604",  # À tester
        "265605",  # À tester
        "265606",  # À tester
        "265607",  # À tester
        "265608",  # À tester
        "265609",  # À tester
        "265610",  # À tester
        
        # Conids alternatifs (plus larges)
        "265590", "265591", "265592", "265593", "265594", "265595", "265596", "265597",
        "265611", "265612", "265613", "265614", "265615", "265616", "265617", "265618", "265619", "265620",
        
        # Conids plus récents
        "265621", "265622", "265623", "265624", "265625", "265626", "265627", "265628", "265629", "265630",
        "265631", "265632", "265633", "265634", "265635", "265636", "265637", "265638", "265639", "265640",
    ]
    
    config = IBKRBetaConfig()
    connector = IBKRBetaConnector(config)
    
    try:
        if not connector.connect() or not connector.authenticate():
            print("❌ Connexion échouée")
            return None
        
        print("✅ Connecté et authentifié")
        print("\n🔍 Test des conids pour prix ES correct...")
        
        valid_candidates = []
        
        for conid in test_conids:
            print(f"\n   Test conid: {conid}")
            
            # Test prix
            fields = ["31", "84"]  # bid, last
            market_data = connector.get_market_data(conid, fields)
            
            if market_data and isinstance(market_data, list) and len(market_data) > 0:
                data = market_data[0]
                bid = data.get('31')
                last = data.get('84')
                
                if bid and bid != "-1":
                    try:
                        bid_price = float(bid)
                        print(f"   Bid: {bid_price}")
                        
                        # Vérifier si le prix est dans la plage ES normale
                        if 6000 <= bid_price <= 7000:
                            print(f"   🎯 CANDIDAT ES TROUVÉ! Prix: {bid_price}")
                            valid_candidates.append({
                                'conid': conid,
                                'bid': bid_price,
                                'last': float(last) if last and last != "-1" else None
                            })
                        elif 200 <= bid_price <= 300:
                            print(f"   ⚠️ Prix suspect (231.19-like): {bid_price}")
                        else:
                            print(f"   Prix hors plage: {bid_price}")
                            
                    except ValueError:
                        print(f"   ❌ Prix invalide: {bid}")
                else:
                    print(f"   ❌ Pas de prix bid")
            else:
                print(f"   ❌ Pas de données")
        
        if valid_candidates:
            print(f"\n🎉 {len(valid_candidates)} candidat(s) ES trouvé(s)!")
            for i, candidate in enumerate(valid_candidates):
                print(f"   Candidat {i+1}: Conid {candidate['conid']}, Bid: {candidate['bid']}")
            
            # Retourner le meilleur candidat
            return valid_candidates[0]['conid']
        else:
            print("\n❌ Aucun candidat ES trouvé")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None
    finally:
        connector.disconnect()

def test_es_contract_details(conid):
    """Tester les détails du contrat ES"""
    print(f"\n🧪 Test détails contrat: {conid}")
    print("=" * 50)
    
    config = IBKRBetaConfig()
    connector = IBKRBetaConnector(config)
    
    try:
        if not connector.connect() or not connector.authenticate():
            return False
        
        # Test données complètes
        fields = ["31", "83", "84", "86", "87", "88", "89", "90"]  # bid, ask, last, volume, high, low, open, close
        market_data = connector.get_market_data(conid, fields)
        
        if market_data and isinstance(market_data, list) and len(market_data) > 0:
            data = market_data[0]
            print("✅ Données complètes:")
            print(f"   Bid: {data.get('31')}")
            print(f"   Ask: {data.get('83')}")
            print(f"   Last: {data.get('84')}")
            print(f"   Volume: {data.get('86')}")
            print(f"   High: {data.get('87')}")
            print(f"   Low: {data.get('88')}")
            print(f"   Open: {data.get('89')}")
            print(f"   Close: {data.get('90')}")
            
            # Test historique
            historical = connector.get_historical_data(conid, "1d", "1min")
            if historical:
                print(f"\n📈 Historique: {len(historical)} barres")
                if len(historical) > 0:
                    last_bar = historical[-1]
                    print(f"   Dernière barre: O={last_bar.get('o')}, H={last_bar.get('h')}, L={last_bar.get('l')}, C={last_bar.get('c')}, V={last_bar.get('v')}")
            
            return True
        else:
            print("❌ Pas de données")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        connector.disconnect()

if __name__ == "__main__":
    # Rechercher le vrai conid ES
    real_es_conid = find_real_es_conid()
    
    if real_es_conid:
        print(f"\n🎉 Vrai conid ES trouvé: {real_es_conid}")
        
        # Test complet
        if test_es_contract_details(real_es_conid):
            print(f"\n✅ Le conid {real_es_conid} est le vrai ES!")
            print(f"💡 Utilisez ce conid: {real_es_conid}")
        else:
            print(f"\n⚠️ Le conid {real_es_conid} a des problèmes")
    else:
        print("\n❌ Aucun vrai conid ES trouvé")
        print("💡 Le conid 265598 pourrait être correct mais avec données anormales")
        print("💡 Vérifiez dans TWS le vrai conid ES")

