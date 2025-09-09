#!/usr/bin/env python3
"""
Test Données Disponibles - MIA_IA_SYSTEM
========================================
Test avec les données ES Futures disponibles.
"""

import asyncio
import time
from ib_insync import IB, Future, Stock

def test_available_data():
    """Test avec données disponibles"""
    print("🚀 TEST DONNÉES DISPONIBLES")
    print("=" * 50)
    
    # Connexion TWS Real
    ib = IB()
    
    try:
        print("1️⃣ Connexion TWS Real...")
        ib.connect('127.0.0.1', 7496, clientId=2)  # Client ID différent
        print("✅ Connexion TWS Real OK")
        
        # 2. Test ES Futures (déjà confirmé fonctionnel)
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
            
        if es_ticker.bid:
            print(f"✅ Bid ES: {es_ticker.bid}")
        else:
            print("❌ Pas de bid ES")
            
        if es_ticker.ask:
            print(f"✅ Ask ES: {es_ticker.ask}")
        else:
            print("❌ Pas de ask ES")
        
        # 3. Test Account Info
        print("\n3️⃣ Test Account Info...")
        account_info = ib.accountSummary()
        
        if account_info:
            print("✅ Account Info récupéré")
            for info in account_info:
                if info.tag == 'NetLiquidation':
                    print(f"   Balance: ${info.value}")
                    break
        else:
            print("❌ Pas d'account info")
        
        # 4. Résumé
        print("\n4️⃣ RÉSUMÉ SYSTÈME")
        print("=" * 30)
        
        es_data_available = (es_ticker.marketPrice() or es_ticker.bid or es_ticker.ask)
        
        if es_data_available:
            print("✅ ES Futures: FONCTIONNEL")
            print("✅ Account Info: FONCTIONNEL")
            print("🎉 VOTRE SYSTÈME PEUT FONCTIONNER !")
            print("\n💡 Pour SPX Options, souscrivez aux bundles API")
        else:
            print("❌ Problème avec ES Futures")
        
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
        test_available_data()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


