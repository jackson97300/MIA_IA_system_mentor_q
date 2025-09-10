#!/usr/bin/env python3
"""
Test IBKR Diagnostic - MIA_IA_SYSTEM
=====================================
Test de diagnostic complet selon documentation IBKR.
"""

import time
import logging
from ib_insync import IB, Future, Stock

# Activer logs détaillés
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ib_insync')

def test_ibkr_diagnostic():
    """Test diagnostic complet IBKR"""
    print("🚀 TEST DIAGNOSTIC IBKR COMPLET")
    print("=" * 50)
    
    ib = IB()
    
    try:
        print("1️⃣ Connexion TWS...")
        ib.connect('127.0.0.1', 7497, clientId=9999)
        print("✅ Connexion OK")
        
        # 2. Test données compte
        print("\n2️⃣ Test données compte...")
        account = ib.accountSummary()
        if account:
            print("✅ Données compte disponibles")
            for item in account[:3]:  # Afficher 3 premiers
                print(f"   {item.tag}: {item.value}")
        else:
            print("❌ Pas de données compte")
        
        # 3. Test ES Futures
        print("\n3️⃣ Test ES Futures...")
        contract_es = Future('ES', '202412', 'CME')
        
        print("   Qualification contrat...")
        ib.qualifyContracts(contract_es)
        
        print("   Demande données ES...")
        ticker_es = ib.reqMktData(contract_es)
        time.sleep(5)  # Attendre plus longtemps
        
        print(f"   Ticker ES: {ticker_es}")
        print(f"   Market Price: {ticker_es.marketPrice()}")
        print(f"   Bid: {ticker_es.bid}")
        print(f"   Ask: {ticker_es.ask}")
        
        if ticker_es.marketPrice() and ticker_es.marketPrice() > 0:
            print(f"✅ ES Prix: ${ticker_es.marketPrice():.2f}")
        else:
            print("❌ ES non disponible")
        
        # 4. Test SPX Index
        print("\n4️⃣ Test SPX Index...")
        contract_spx = Stock('SPX', 'SMART', 'USD')
        
        print("   Qualification SPX...")
        ib.qualifyContracts(contract_spx)
        
        print("   Demande données SPX...")
        ticker_spx = ib.reqMktData(contract_spx)
        time.sleep(5)
        
        print(f"   Ticker SPX: {ticker_spx}")
        print(f"   Market Price: {ticker_spx.marketPrice()}")
        
        if ticker_spx.marketPrice() and ticker_spx.marketPrice() > 0:
            print(f"✅ SPX Prix: ${ticker_spx.marketPrice():.2f}")
        else:
            print("❌ SPX non disponible")
        
        # 5. Test SPY ETF
        print("\n5️⃣ Test SPY ETF...")
        contract_spy = Stock('SPY', 'SMART', 'USD')
        
        print("   Qualification SPY...")
        ib.qualifyContracts(contract_spy)
        
        print("   Demande données SPY...")
        ticker_spy = ib.reqMktData(contract_spy)
        time.sleep(5)
        
        print(f"   Ticker SPY: {ticker_spy}")
        print(f"   Market Price: {ticker_spy.marketPrice()}")
        
        if ticker_spy.marketPrice() and ticker_spy.marketPrice() > 0:
            print(f"✅ SPY Prix: ${ticker_spy.marketPrice():.2f}")
        else:
            print("❌ SPY non disponible")
        
        print("\n🎉 DIAGNOSTIC TERMINÉ !")
        
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
        test_ibkr_diagnostic()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


