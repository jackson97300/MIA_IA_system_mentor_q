#!/usr/bin/env python3
"""
Test IB Ultra Rapide - MIA_IA_SYSTEM
=====================================

Test ultra-rapide pour obtenir les prix ES en 30 secondes max.

USAGE:
python scripts/test_ib_ultra_rapide.py
"""

import sys
import os
import asyncio
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

async def test_ib_ultra_rapide():
    """Test ultra-rapide avec ib_insync direct"""
    
    print("⚡ TEST ULTRA RAPIDE IBKR")
    print("=" * 35)
    print(f"⏰ Début: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # Import direct ib_insync
        from ib_insync import IB, Future, Stock
        
        # 1. Connexion directe
        print("\n1️⃣ Connexion directe...")
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if ib.isConnected():
            print("✅ Connexion directe OK")
        else:
            print("❌ Échec connexion directe")
            return
        
        # 2. Test ES Futures
        print("\n2️⃣ Test ES Futures...")
        contract = Future('ES', '202412', 'CME')
        ib.qualifyContracts(contract)
        
        # 3. Demande données temps réel
        print("\n3️⃣ Demande données ES...")
        ticker = ib.reqMktData(contract)
        
        # Attendre max 10 secondes
        print("   ⏳ Attente données...")
        for i in range(10):
            await asyncio.sleep(1)
            if ticker.marketPrice() or ticker.bid or ticker.ask:
                break
            print(f"   ⏳ {i+1}/10 secondes...")
        
        # 4. Affichage résultats
        print("\n4️⃣ Résultats ES:")
        if ticker.marketPrice():
            print(f"✅ Prix ES: {ticker.marketPrice()}")
        else:
            print("❌ Pas de prix ES")
            
        if ticker.bid:
            print(f"✅ Bid ES: {ticker.bid}")
        else:
            print("❌ Pas de bid ES")
            
        if ticker.ask:
            print(f"✅ Ask ES: {ticker.ask}")
        else:
            print("❌ Pas de ask ES")
            
        if ticker.last:
            print(f"✅ Last ES: {ticker.last}")
        else:
            print("❌ Pas de last ES")
        
        # 5. Test SPY pour comparaison
        print("\n5️⃣ Test SPY (comparaison):")
        spy_contract = Stock('SPY', 'SMART', 'USD')
        ib.qualifyContracts(spy_contract)
        spy_ticker = ib.reqMktData(spy_contract)
        
        await asyncio.sleep(3)
        
        if spy_ticker.marketPrice():
            print(f"✅ Prix SPY: {spy_ticker.marketPrice()}")
        else:
            print("❌ Pas de prix SPY")
        
        # 6. Test Account Info
        print("\n6️⃣ Test Account Info:")
        try:
            account = ib.accountSummary()
            if account:
                print("✅ Account Info OK")
                for item in account:
                    if 'NetLiquidation' in item.tag:
                        print(f"   Balance: ${item.value}")
                    elif 'BuyingPower' in item.tag:
                        print(f"   Buying Power: ${item.value}")
            else:
                print("❌ Pas d'info compte")
        except Exception as e:
            print(f"❌ Erreur Account: {e}")
        
        # 7. Résumé final
        print("\n" + "=" * 35)
        print("📊 RÉSUMÉ ULTRA RAPIDE")
        print("=" * 35)
        print("✅ Connexion: OK")
        print("✅ TWS: Connecté")
        print("✅ API: Fonctionnelle")
        
        if ticker.marketPrice() or ticker.bid or ticker.ask:
            print("✅ Données ES: RÉCUPÉRÉES")
        else:
            print("❌ Données ES: MANQUANTES")
            
        print(f"⏰ Fin: {datetime.now().strftime('%H:%M:%S')}")
        
        # Déconnexion
        ib.disconnect()
        print("✅ Déconnexion propre")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(test_ib_ultra_rapide())
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
