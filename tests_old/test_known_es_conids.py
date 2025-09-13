#!/usr/bin/env python3
"""
Test avec des conids ES futures connus
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

def test_known_es_conids():
    """Tester des conids ES futures connus"""
    
    # Conids connus pour ES futures (à ajuster)
    known_conids = [
        "265598",  # ES futures example
        "265599",  # ES futures example  
        "265600",  # ES futures example
        "265601",  # ES futures example
        "265602",  # ES futures example
        "265603",  # ES futures example
        "265604",  # ES futures example
        "265605",  # ES futures example
        "265606",  # ES futures example
        "265607",  # ES futures example
        "265608",  # ES futures example
        "265609",  # ES futures example
        "265610",  # ES futures example
    ]
    
    config = IBKRBetaConfig()
    connector = IBKRBetaConnector(config)
    
    try:
        if not connector.connect() or not connector.authenticate():
            print("❌ Connexion échouée")
            return None
        
        print("🔍 Test des conids ES futures connus...")
        
        for conid in known_conids:
            print(f"\n   Test conid: {conid}")
            market_data = connector.get_market_data(conid, ["31", "84"])  # bid, last
            
            if market_data and market_data.get("conid") != "-1":
                print(f"   ✅ Conid {conid} valide!")
                print(f"   📊 Données: {market_data}")
                return conid
            else:
                print(f"   ❌ Conid {conid} invalide")
        
        print("\n❌ Aucun conid valide trouvé")
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None
    finally:
        connector.disconnect()

if __name__ == "__main__":
    es_conid = test_known_es_conids()
    if es_conid:
        print(f"\n🎉 Conid ES trouvé: {es_conid}")
    else:
        print("\n❌ Aucun conid ES trouvé")
        print("💡 Essayez de rechercher manuellement dans TWS")

