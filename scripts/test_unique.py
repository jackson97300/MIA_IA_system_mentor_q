#!/usr/bin/env python3
"""
Test Unique - MIA_IA_SYSTEM
===========================
Test unique avec Client ID unique.
"""

import time
import random
from ib_insync import IB, Future

def test_unique():
    """Test unique"""
    # Client ID unique basé sur le temps
    client_id = int(time.time() % 1000) + 100
    
    print(f"🚀 TEST UNIQUE (Client ID: {client_id})")
    print("=" * 50)
    
    # Connexion TWS Real
    ib = IB()
    
    try:
        print(f"1️⃣ Connexion TWS Real (Client ID: {client_id})...")
        ib.connect('127.0.0.1', 7496, clientId=client_id)
        print("✅ Connexion TWS Real OK")
        
        # 2. Test ES Futures (déjà confirmé)
        print("\n2️⃣ Test ES Futures...")
        es_contract = Future('ES', '202412', 'CME')
        ib.qualifyContracts(es_contract)
        es_ticker = ib.reqMktData(es_contract)
        
        print("   ⏳ Attente données ES...")
        time.sleep(3)
        
        if es_ticker.marketPrice():
            print(f"✅ Prix ES: {es_ticker.marketPrice()}")
            print("🎉 SUCCÈS ! ES Futures fonctionne !")
        else:
            print("❌ Pas de prix ES")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n3️⃣ Déconnexion...")
        ib.disconnect()
        print("✅ Déconnexion propre")

if __name__ == "__main__":
    try:
        test_unique()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


