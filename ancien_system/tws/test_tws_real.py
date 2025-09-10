#!/usr/bin/env python3
"""
Test TWS Real - MIA_IA_SYSTEM
==============================

Test TWS en mode réel sur le port 7496.

USAGE:
python scripts/test_tws_real.py
"""

import sys
import os
import time
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_tws_real():
    """Test TWS en mode réel"""
    
    print("🚀 TEST TWS RÉEL")
    print("=" * 35)
    print(f"⏰ Début: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # Import direct ib_insync
        from ib_insync import IB, Future, Stock
        
        # 1. Connexion TWS Réel
        print("\n1️⃣ Connexion TWS Réel (Port 7496)...")
        ib = IB()
        ib.connect('127.0.0.1', 7496, clientId=1, timeout=10)
        
        if ib.isConnected():
            print("✅ Connexion TWS Réel OK")
        else:
            print("❌ Échec connexion TWS Réel")
            return
        
        # 2. Test ES Futures
        print("\n2️⃣ Test ES Futures...")
        contract = Future('ES', '202412', 'CME')
        ib.qualifyContracts(contract)
        print("✅ Contrat ES qualifié")
        
        # 3. Demande données temps réel
        print("\n3️⃣ Demande données ES...")
        ticker = ib.reqMktData(contract)
        
        # Attendre max 10 secondes
        print("   ⏳ Attente données...")
        for i in range(10):
            time.sleep(1)
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
        
        time.sleep(3)
        
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
        
        # 7. Test Level 2 (si disponible)
        print("\n7️⃣ Test Level 2...")
        try:
            depth = ib.reqMktDepth(contract, numRows=5)
            time.sleep(2)
            
            if depth:
                print("✅ Level 2 disponible")
                print(f"   Bids: {len(depth.bids)} niveaux")
                print(f"   Asks: {len(depth.asks)} niveaux")
            else:
                print("❌ Level 2 non disponible")
        except Exception as e:
            print(f"❌ Erreur Level 2: {e}")
        
        # 8. Résumé final
        print("\n" + "=" * 35)
        print("📊 RÉSUMÉ TWS RÉEL")
        print("=" * 35)
        print("✅ Connexion: OK")
        print("✅ TWS: Connecté")
        print("✅ Mode: RÉEL")
        
        if ticker.marketPrice() or ticker.bid or ticker.ask:
            print("✅ Données ES: RÉCUPÉRÉES")
            print("🎉 SUCCÈS ! TWS Réel fonctionne !")
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
        test_tws_real()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


