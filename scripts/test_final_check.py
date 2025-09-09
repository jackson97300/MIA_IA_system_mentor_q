#!/usr/bin/env python3
"""
Test Final Check - MIA_IA_SYSTEM
=================================
Test final avec Client ID unique.
"""

import time
import random
from ib_insync import IB, Stock

def test_final_check():
    """Test final check"""
    # Client ID unique
    client_id = random.randint(1000, 9999)
    
    print(f"🚀 TEST FINAL CHECK (Client ID: {client_id})")
    print("=" * 50)
    
    # Connexion TWS
    ib = IB()
    
    try:
        print(f"1️⃣ Connexion TWS (Client ID: {client_id})...")
        ib.connect('127.0.0.1', 7496, clientId=client_id)
        print("✅ Connexion TWS OK")
        
        # 2. Test SPY (visible dans votre capture)
        print("\n2️⃣ Test SPY...")
        spy_contract = Stock('SPY', 'SMART', 'USD')
        ib.qualifyContracts(spy_contract)
        spy_ticker = ib.reqMktData(spy_contract)
        
        print("   ⏳ Attente données SPY...")
        time.sleep(5)
        
        if spy_ticker.marketPrice():
            print(f"✅ Prix SPY: {spy_ticker.marketPrice()}")
            print("🎉 SUCCÈS ! API fonctionne !")
            print("\n💡 Votre système MIA_IA_SYSTEM peut fonctionner !")
        else:
            print("❌ Pas de prix SPY")
            print("💡 Vérifiez les souscriptions API")
        
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
        test_final_check()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


