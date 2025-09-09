#!/usr/bin/env python3
"""
Test SPX Options - MIA_IA_SYSTEM
=================================

Test SPX Options pour votre système.

USAGE:
python scripts/test_spx_options.py
"""

import sys
import os
import time
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_spx_options():
    """Test SPX Options"""
    
    print("🚀 TEST SPX OPTIONS")
    print("=" * 30)
    print(f"⏰ Début: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # Import direct ib_insync
        from ib_insync import IB, Option, Stock
        
        # 1. Connexion TWS Réel
        print("\n1️⃣ Connexion TWS Réel...")
        ib = IB()
        ib.connect('127.0.0.1', 7496, clientId=1, timeout=10)
        
        if ib.isConnected():
            print("✅ Connexion TWS Réel OK")
        else:
            print("❌ Échec connexion TWS Réel")
            return
        
        # 2. Test SPX Options
        print("\n2️⃣ Test SPX Options...")
        
        # Test SPX Call Option
        spx_call = Option('SPX', '202412', 4500, 'C', 'CBOE')
        ib.qualifyContracts(spx_call)
        print("✅ Contrat SPX Call qualifié")
        
        # Test SPX Put Option
        spx_put = Option('SPX', '202412', 4500, 'P', 'CBOE')
        ib.qualifyContracts(spx_put)
        print("✅ Contrat SPX Put qualifié")
        
        # 3. Demande données SPX Options
        print("\n3️⃣ Demande données SPX...")
        spx_call_ticker = ib.reqMktData(spx_call)
        spx_put_ticker = ib.reqMktData(spx_put)
        
        # Attendre max 10 secondes
        print("   ⏳ Attente données SPX...")
        for i in range(10):
            time.sleep(1)
            if (spx_call_ticker.marketPrice() or spx_call_ticker.bid or spx_call_ticker.ask or
                spx_put_ticker.marketPrice() or spx_put_ticker.bid or spx_put_ticker.ask):
                break
            print(f"   ⏳ {i+1}/10 secondes...")
        
        # 4. Affichage résultats SPX Call
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
        
        # 5. Affichage résultats SPX Put
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
        
        # 6. Test SPX Index
        print("\n6️⃣ Test SPX Index...")
        spx_index = Stock('SPX', 'CBOE', 'USD')
        ib.qualifyContracts(spx_index)
        spx_index_ticker = ib.reqMktData(spx_index)
        
        time.sleep(3)
        
        if spx_index_ticker.marketPrice():
            print(f"✅ Prix SPX Index: {spx_index_ticker.marketPrice()}")
        else:
            print("❌ Pas de prix SPX Index")
        
        # 7. Test Put/Call Ratio
        print("\n7️⃣ Test Put/Call Ratio...")
        try:
            # Calculer le ratio Put/Call basique
            put_volume = spx_put_ticker.volume if spx_put_ticker.volume else 0
            call_volume = spx_call_ticker.volume if spx_call_ticker.volume else 0
            
            if call_volume > 0:
                put_call_ratio = put_volume / call_volume
                print(f"✅ Put/Call Ratio: {put_call_ratio:.3f}")
            else:
                print("❌ Pas de données volume pour Put/Call Ratio")
        except Exception as e:
            print(f"❌ Erreur Put/Call Ratio: {e}")
        
        # 8. Résumé final
        print("\n" + "=" * 30)
        print("📊 RÉSUMÉ SPX OPTIONS")
        print("=" * 30)
        print("✅ Connexion: OK")
        print("✅ TWS: Connecté")
        print("✅ Mode: RÉEL")
        
        spx_data_available = (spx_call_ticker.marketPrice() or spx_call_ticker.bid or spx_call_ticker.ask or
                             spx_put_ticker.marketPrice() or spx_put_ticker.bid or spx_put_ticker.ask)
        
        if spx_data_available:
            print("✅ Données SPX: RÉCUPÉRÉES")
            print("🎉 SUCCÈS ! SPX Options fonctionne !")
        else:
            print("❌ Données SPX: MANQUANTES")
            
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
        test_spx_options()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


