#!/usr/bin/env python3
"""
Test Bundle API - MIA_IA_SYSTEM
================================
Test avec le nouveau bundle API.
"""

import time
from ib_insync import IB, Future, Stock

def test_bundle_api():
    """Test avec bundle API"""
    print("🚀 TEST BUNDLE API COMPLET")
    print("=" * 50)
    
    ib = IB()
    
    try:
        print("1️⃣ Connexion TWS Simulated...")
        ib.connect('127.0.0.1', 7497, clientId=9999)
        print("✅ Connexion OK")
        
        # 2. Test ES Futures
        print("\n2️⃣ Test ES Futures...")
        contract_es = Future('ES', '202412', 'CME')
        
        print("   Qualification ES...")
        ib.qualifyContracts(contract_es)
        
        ticker_es = ib.reqMktData(contract_es)
        time.sleep(3)
        
        if ticker_es.marketPrice() and ticker_es.marketPrice() > 0:
            print(f"✅ ES Prix: ${ticker_es.marketPrice():.2f}")
            print("🎉 SUCCÈS ES !")
        else:
            print("❌ ES non disponible")
        
        # 3. Test SPX Index
        print("\n3️⃣ Test SPX Index...")
        contract_spx = Stock('SPX', 'SMART', 'USD')
        
        print("   Qualification SPX...")
        ib.qualifyContracts(contract_spx)
        
        ticker_spx = ib.reqMktData(contract_spx)
        time.sleep(3)
        
        if ticker_spx.marketPrice() and ticker_spx.marketPrice() > 0:
            print(f"✅ SPX Prix: ${ticker_spx.marketPrice():.2f}")
            print("🎉 SUCCÈS SPX !")
        else:
            print("❌ SPX non disponible")
        
        # 4. Test SPY ETF
        print("\n4️⃣ Test SPY ETF...")
        contract_spy = Stock('SPY', 'SMART', 'USD')
        
        print("   Qualification SPY...")
        ib.qualifyContracts(contract_spy)
        
        ticker_spy = ib.reqMktData(contract_spy)
        time.sleep(3)
        
        if ticker_spy.marketPrice() and ticker_spy.marketPrice() > 0:
            print(f"✅ SPY Prix: ${ticker_spy.marketPrice():.2f}")
            print("🎉 SUCCÈS SPY !")
        else:
            print("❌ SPY non disponible")
        
        print("\n🎉 TEST BUNDLE API TERMINÉ !")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n5️⃣ Déconnexion...")
        ib.disconnect()
        print("✅ Déconnexion propre")

if __name__ == "__main__":
    try:
        test_bundle_api()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


