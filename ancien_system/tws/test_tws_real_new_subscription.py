#!/usr/bin/env python3
"""
Test TWS Real avec Nouvelle Souscription - MIA_IA_SYSTEM
========================================================
Test TWS réel avec bundle complet.
"""

import time
from ib_insync import IB, Stock, Future

def test_tws_real_new_subscription():
    """Test TWS réel avec nouvelle souscription"""
    print("🚀 TEST TWS RÉEL AVEC NOUVELLE SOUSCRIPTION")
    print("=" * 60)
    
    # Connexion TWS Real
    ib = IB()
    
    try:
        print("1️⃣ Connexion TWS Real...")
        ib.connect('127.0.0.1', 7496, clientId=9999)
        print("✅ Connexion TWS Real OK")
        
        # 2. Test ES Futures
        print("\n2️⃣ Test ES Futures...")
        es_contract = Future('ES', '202412', 'CME')
        ib.qualifyContracts(es_contract)
        es_ticker = ib.reqMktData(es_contract)
        
        print("   ⏳ Attente données ES...")
        time.sleep(3)
        
        if es_ticker.marketPrice():
            print(f"✅ Prix ES: {es_ticker.marketPrice()}")
        else:
            print("❌ Pas de prix ES")
        
        # 3. Test SPX Index
        print("\n3️⃣ Test SPX Index...")
        spx_contract = Stock('SPX', 'CBOE', 'USD')
        ib.qualifyContracts(spx_contract)
        spx_ticker = ib.reqMktData(spx_contract)
        
        print("   ⏳ Attente données SPX...")
        time.sleep(3)
        
        if spx_ticker.marketPrice():
            print(f"✅ Prix SPX: {spx_ticker.marketPrice()}")
        else:
            print("❌ Pas de prix SPX")
        
        # 4. Test SPY
        print("\n4️⃣ Test SPY...")
        spy_contract = Stock('SPY', 'SMART', 'USD')
        ib.qualifyContracts(spy_contract)
        spy_ticker = ib.reqMktData(spy_contract)
        
        print("   ⏳ Attente données SPY...")
        time.sleep(3)
        
        if spy_ticker.marketPrice():
            print(f"✅ Prix SPY: {spy_ticker.marketPrice()}")
        else:
            print("❌ Pas de prix SPY")
        
        # 5. Résumé final
        print("\n5️⃣ RÉSUMÉ FINAL")
        print("=" * 30)
        
        es_ok = es_ticker.marketPrice() is not None
        spx_ok = spx_ticker.marketPrice() is not None
        spy_ok = spy_ticker.marketPrice() is not None
        
        if es_ok and spx_ok and spy_ok:
            print("✅ ES Futures: FONCTIONNEL")
            print("✅ SPX Index: FONCTIONNEL")
            print("✅ SPY: FONCTIONNEL")
            print("🎉 SUCCÈS TOTAL ! Votre système MIA_IA_SYSTEM est prêt !")
        else:
            print("❌ Certaines données manquent")
            print(f"   ES: {'✅' if es_ok else '❌'}")
            print(f"   SPX: {'✅' if spx_ok else '❌'}")
            print(f"   SPY: {'✅' if spy_ok else '❌'}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n6️⃣ Déconnexion...")
        ib.disconnect()
        print("✅ Déconnexion propre")

if __name__ == "__main__":
    try:
        test_tws_real_new_subscription()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


