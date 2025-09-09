#!/usr/bin/env python3
"""
Test rapide des volumes ES/NQ en temps réel
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ib_insync import *

async def test_volumes_reels():
    """Test des volumes ES/NQ en temps réel"""
    print("🔍 TEST VOLUMES ES/NQ RÉELS")
    print("=" * 40)
    
    ib = IB()
    try:
        # Connexion
        print("🔌 Connexion IBKR...")
        await ib.connectAsync('127.0.0.1', 7496, clientId=99)
        print("✅ Connexion réussie")
        
        # ES Futures
        print("\n📊 TEST ES FUTURES:")
        es = Future('ES', '20251219', 'CME')
        ib.qualifyContracts(es)
        
        # Subscribe market data
        ticker = ib.reqMktData(es, '', False, False)
        await asyncio.sleep(2)
        
        print(f"ES Bid: {ticker.bid}")
        print(f"ES Ask: {ticker.ask}")
        print(f"ES Last: {ticker.last}")
        print(f"ES Volume: {ticker.volume}")
        print(f"ES High: {ticker.high}")
        print(f"ES Low: {ticker.low}")
        
        # NQ Futures
        print("\n📊 TEST NQ FUTURES:")
        nq = Future('NQ', '20251219', 'CME')
        ib.qualifyContracts(nq)
        
        ticker_nq = ib.reqMktData(nq, '', False, False)
        await asyncio.sleep(2)
        
        print(f"NQ Bid: {ticker_nq.bid}")
        print(f"NQ Ask: {ticker_nq.ask}")
        print(f"NQ Last: {ticker_nq.last}")
        print(f"NQ Volume: {ticker_nq.volume}")
        print(f"NQ High: {ticker_nq.high}")
        print(f"NQ Low: {ticker_nq.low}")
        
        # Test DOM
        print("\n📊 TEST DOM (Order Book):")
        dom = ib.reqMktDepth(es, numRows=5)
        await asyncio.sleep(1)
        
        if dom and dom.domBids and dom.domAsks:
            print("✅ DOM disponible")
            print(f"Bids: {[(bid.price, bid.size) for bid in dom.domBids[:3]]}")
            print(f"Asks: {[(ask.price, ask.size) for ask in dom.domAsks[:3]]}")
        else:
            print("❌ DOM non disponible")
        
        print("\n🎯 RÉSUMÉ:")
        print(f"ES Volume: {'✅ NON-NUL' if ticker.volume and ticker.volume > 0 else '❌ NUL'}")
        print(f"NQ Volume: {'✅ NON-NUL' if ticker_nq.volume and ticker_nq.volume > 0 else '❌ NUL'}")
        print(f"DOM: {'✅ DISPONIBLE' if dom and dom.domBids else '❌ INDISPONIBLE'}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        ib.disconnect()

if __name__ == "__main__":
    asyncio.run(test_volumes_reels())
