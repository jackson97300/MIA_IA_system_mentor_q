#!/usr/bin/env python3
"""
Test SPX Options Après Souscription - MIA_IA_SYSTEM
===================================================
Test SPX Options après activation des souscriptions.
"""

import asyncio
import time
from ib_insync import IB, Option, Stock

def test_spx_after_subscription():
    """Test SPX Options après souscription"""
    
    print("🚀 TEST SPX OPTIONS APRÈS SOUSCRIPTION")
    print("=" * 50)
    
    # Connexion IB
    ib = IB()
    
    try:
        # 1. Connexion TWS
        print("\n1️⃣ Connexion TWS...")
        ib.connect('127.0.0.1', 7496, clientId=1)
        print("✅ Connexion TWS OK")
        
        # 2. Test SPX Index
        print("\n2️⃣ Test SPX Index...")
        spx_index = Stock('SPX', 'CBOE', 'USD')
        ib.qualifyContracts(spx_index)
        spx_ticker = ib.reqMktData(spx_index)
        
        time.sleep(3)
        
        if spx_ticker.marketPrice():
            print(f"✅ Prix SPX Index: {spx_ticker.marketPrice()}")
        else:
            print("❌ Pas de prix SPX Index")
        
        # 3. Test SPX Options
        print("\n3️⃣ Test SPX Options...")
        
        # SPX Call Option
        spx_call = Option('SPX', '202412', 4500, 'C', 'CBOE')
        ib.qualifyContracts(spx_call)
        spx_call_ticker = ib.reqMktData(spx_call)
        
        # SPX Put Option  
        spx_put = Option('SPX', '202412', 4500, 'P', 'CBOE')
        ib.qualifyContracts(spx_put)
        spx_put_ticker = ib.reqMktData(spx_put)
        
        time.sleep(5)
        
        # 4. Résultats SPX Call
        print("\n4️⃣ Résultats SPX Call:")
        if spx_call_ticker.marketPrice():
            print(f"✅ Prix SPX Call: {spx_call_ticker.marketPrice()}")
        else:
            print("❌ Pas de prix SPX Call")
            
        if spx_call_ticker.bid:
            print(f"✅ Bid SPX Call: {spx_call_ticker.bid}")
        else:
            print("❌ Pas de bid SPX Call")
            
        if spx_call_ticker.ask:
            print(f"✅ Ask SPX Call: {spx_call_ticker.ask}")
        else:
            print("❌ Pas de ask SPX Call")
        
        # 5. Résultats SPX Put
        print("\n5️⃣ Résultats SPX Put:")
        if spx_put_ticker.marketPrice():
            print(f"✅ Prix SPX Put: {spx_put_ticker.marketPrice()}")
        else:
            print("❌ Pas de prix SPX Put")
            
        if spx_put_ticker.bid:
            print(f"✅ Bid SPX Put: {spx_put_ticker.bid}")
        else:
            print("❌ Pas de bid SPX Put")
            
        if spx_put_ticker.ask:
            print(f"✅ Ask SPX Put: {spx_put_ticker.ask}")
        else:
            print("❌ Pas de ask SPX Put")
        
        # 6. Résumé
        print("\n📊 RÉSUMÉ SOUSCRIPTIONS")
        print("=" * 30)
        
        spx_data_available = (spx_call_ticker.marketPrice() or spx_call_ticker.bid or spx_call_ticker.ask or
                             spx_put_ticker.marketPrice() or spx_put_ticker.bid or spx_put_ticker.ask)
        
        if spx_data_available:
            print("✅ SPX Options: SOUSCRIPTION ACTIVE")
            print("🎉 SUCCÈS ! SPX Options fonctionne !")
            print("💰 Coût mensuel: ~$6.00")
        else:
            print("❌ SPX Options: SOUSCRIPTION MANQUANTE")
            print("💡 Activez OPRA Level 1 dans TWS")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        ib.disconnect()
        print("\n🔌 Connexion fermée")

if __name__ == "__main__":
    test_spx_after_subscription()


