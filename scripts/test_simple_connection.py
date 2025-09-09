#!/usr/bin/env python3
"""
Test Simple Connection - MIA_IA_SYSTEM
======================================
Test simple pour vérifier la connexion API.
"""

import time
from ib_insync import IB, Stock

def test_simple_connection():
    """Test connexion simple"""
    print("🚀 TEST CONNEXION SIMPLE")
    print("=" * 50)
    
    # Connexion TWS
    ib = IB()
    
    try:
        print("1️⃣ Connexion TWS...")
        ib.connect('127.0.0.1', 7496, clientId=999)
        print("✅ Connexion TWS OK")
        
        # 2. Test SPY (visible dans votre capture)
        print("\n2️⃣ Test SPY...")
        spy_contract = Stock('SPY', 'SMART', 'USD')
        ib.qualifyContracts(spy_contract)
        spy_ticker = ib.reqMktData(spy_contract)
        
        print("   ⏳ Attente données SPY...")
        time.sleep(3)
        
        if spy_ticker.marketPrice():
            print(f"✅ Prix SPY: {spy_ticker.marketPrice()}")
            print("🎉 SUCCÈS ! API fonctionne !")
        else:
            print("❌ Pas de prix SPY")
        
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
        test_simple_connection()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


