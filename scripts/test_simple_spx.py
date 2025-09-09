#!/usr/bin/env python3
"""
Test Simple SPX - MIA_IA_SYSTEM
================================
Test ultra-simple pour SPX seulement.
"""

import time
from ib_insync import IB, Stock

def test_simple_spx():
    """Test SPX ultra-simple"""
    print("🚀 TEST SPX ULTRA-SIMPLE")
    print("=" * 50)
    
    ib = IB()
    
    try:
        print("1️⃣ Connexion TWS...")
        ib.connect('127.0.0.1', 7497, clientId=9999)
        print("✅ Connexion OK")
        
        # 2. Test SPX seulement
        print("\n2️⃣ Test SPX Index...")
        contract = Stock('SPX', 'SMART', 'USD')
        
        print("   Demande SPX...")
        ticker = ib.reqMktData(contract)
        time.sleep(5)  # Attendre plus longtemps
        
        print(f"   Ticker: {ticker}")
        print(f"   Market Price: {ticker.marketPrice()}")
        print(f"   Bid: {ticker.bid}")
        print(f"   Ask: {ticker.ask}")
        
        if ticker.marketPrice() and ticker.marketPrice() > 0:
            print(f"✅ SPX Prix: ${ticker.marketPrice():.2f}")
            print("🎉 SUCCÈS SPX !")
        else:
            print("❌ SPX non disponible")
            print("   Vérifiez bundle API")
        
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
        test_simple_spx()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


