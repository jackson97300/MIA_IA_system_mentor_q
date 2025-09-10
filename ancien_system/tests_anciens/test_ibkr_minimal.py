#!/usr/bin/env python3
"""
Script de test minimal IBKR
"""

from ib_insync import *

def test_ibkr_connection():
    """Test de connexion IBKR"""
    print("🚀 TEST CONNEXION IBKR")
    print("=" * 30)
    
    # 1. Connexion Paper
    ib = IB()
    try:
        ib.connect('127.0.0.1', 7497, clientId=7)
        print("✅ Connexion réussie")
        print(f"TWS time: {ib.reqCurrentTime()}")
        
        # 2. Test ES Futures
        print("\n📊 TEST ES FUTURES:")
        es = ContFuture('ES', exchange='GLOBEX')
        ib.qualifyContracts(es)
        
        # Quotes L1
        tkr_es = ib.reqMktData(es, '', False, False)
        ib.sleep(2)
        print(f"ES L1: Bid={tkr_es.bid}, Ask={tkr_es.ask}, Last={tkr_es.last}")
        
        # DOM L2
        try:
            dom = ib.reqMktDepth(es, numRows=10)
            ib.sleep(2)
            print(f"ES DOM Bids: {[(l.price, l.size) for l in dom[0].domBids[:3]]}")
            print(f"ES DOM Asks: {[(l.price, l.size) for l in dom[0].domAsks[:3]]}")
        except Exception as e:
            print(f"❌ DOM L2: {e}")
        
        # 3. Test SPX Options
        print("\n📈 TEST SPX OPTIONS:")
        opt = Option(symbol='SPX', lastTradeDateOrContractMonth='20250920',
                    strike=5000, right='C', exchange='SMART', currency='USD')
        ib.qualifyContracts(opt)
        
        tkr_opt = ib.reqMktData(opt, genericTickList='106', snapshot=False)
        ib.sleep(3)
        print(f"SPX Greeks: {tkr_opt.modelGreeks}")
        
        # 4. Test VIX
        print("\n📊 TEST VIX:")
        vix_idx = Index('VIX', 'CBOE')
        ib.qualifyContracts(vix_idx)
        tkr_vix = ib.reqMktData(vix_idx, '', False)
        ib.sleep(2)
        print(f"VIX spot: {tkr_vix.last}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("\n🔧 SOLUTIONS:")
        print("1. Vérifiez que TWS/Gateway est lancé")
        print("2. Vérifiez le port (7497 pour Paper)")
        print("3. Vérifiez les abonnements data")
        print("4. Changez clientId si nécessaire")
    
    finally:
        ib.disconnect()
        print("\n✅ Test terminé")

if __name__ == "__main__":
    test_ibkr_connection()







