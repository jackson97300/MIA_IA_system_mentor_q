#!/usr/bin/env python3
"""
Test SPX Final - MIA_IA_SYSTEM
===============================
Test final SPX avec Client ID 999.
"""

import time
from ib_insync import IB, Stock, Option

def test_spx_final():
    """Test SPX final"""
    print("🚀 TEST SPX FINAL")
    print("=" * 50)
    
    # Connexion TWS Real avec Client ID 999
    ib = IB()
    
    try:
        print("1️⃣ Connexion TWS Real (Client ID 999)...")
        ib.connect('127.0.0.1', 7496, clientId=999)
        print("✅ Connexion TWS Real OK")
        
        # 2. Test SPX Index
        print("\n2️⃣ Test SPX Index...")
        spx_index = Stock('SPX', 'CBOE', 'USD')
        ib.qualifyContracts(spx_index)
        spx_ticker = ib.reqMktData(spx_index)
        
        print("   ⏳ Attente données SPX Index...")
        time.sleep(5)
        
        if spx_ticker.marketPrice():
            print(f"✅ Prix SPX Index: {spx_ticker.marketPrice()}")
        else:
            print("❌ Pas de prix SPX Index")
            
        if spx_ticker.bid:
            print(f"✅ Bid SPX Index: {spx_ticker.bid}")
        else:
            print("❌ Pas de bid SPX Index")
            
        if spx_ticker.ask:
            print(f"✅ Ask SPX Index: {spx_ticker.ask}")
        else:
            print("❌ Pas de ask SPX Index")
        
        # 3. Test SPX Options
        print("\n3️⃣ Test SPX Options...")
        try:
            # Test SPX Call Option
            spx_call = Option('SPX', '202412', 4500, 'C', 'CBOE')
            ib.qualifyContracts(spx_call)
            print("✅ Contrat SPX Call qualifié")
            
            spx_call_ticker = ib.reqMktData(spx_call)
            time.sleep(3)
            
            if spx_call_ticker.marketPrice():
                print(f"✅ Prix SPX Call: {spx_call_ticker.marketPrice()}")
            else:
                print("❌ Pas de prix SPX Call")
                
        except Exception as e:
            print(f"❌ Erreur SPX Options: {e}")
        
        # 4. Test SPY
        print("\n4️⃣ Test SPY...")
        try:
            spy_contract = Stock('SPY', 'SMART', 'USD')
            ib.qualifyContracts(spy_contract)
            spy_ticker = ib.reqMktData(spy_contract)
            time.sleep(3)
            
            if spy_ticker.marketPrice():
                print(f"✅ Prix SPY: {spy_ticker.marketPrice()}")
            else:
                print("❌ Pas de prix SPY")
                
        except Exception as e:
            print(f"❌ Erreur SPY: {e}")
        
        # 5. Résumé final
        print("\n5️⃣ RÉSUMÉ FINAL")
        print("=" * 30)
        
        spx_data_available = (spx_ticker.marketPrice() or spx_ticker.bid or spx_ticker.ask)
        
        if spx_data_available:
            print("✅ SPX Index: FONCTIONNEL")
            print("🎉 SUCCÈS ! SPX fonctionne !")
            print("\n💡 Votre système MIA_IA_SYSTEM peut fonctionner !")
        else:
            print("❌ SPX Index: MANQUANT")
            print("💡 Vérifiez les souscriptions OPRA")
        
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
        test_spx_final()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


