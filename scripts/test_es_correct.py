#!/usr/bin/env python3
"""
Test ES Correct - MIA_IA_SYSTEM
===============================
Test ES avec le bon contrat (Mars 2025).
"""

import time
from ib_insync import IB, Future

def test_es_correct():
    """Test ES avec contrat correct"""
    print("🚀 TEST ES FUTURES CORRECT")
    print("=" * 50)
    
    ib = IB()
    
    try:
        print("1️⃣ Connexion TWS Simulated...")
        ib.connect('127.0.0.1', 7497, clientId=9999)
        print("✅ Connexion OK")
        
        # 2. Test ES avec contrat correct
        print("\n2️⃣ Test ES Futures (Mars 2025)...")
        contract = Future('ES', '202503', 'CME')  # Mars 2025
        
        print("   Qualification contrat...")
        ib.qualifyContracts(contract)
        
        print("   Demande prix ES...")
        ticker = ib.reqMktData(contract)
        time.sleep(3)  # Attendre données
        
        if ticker.marketPrice() and ticker.marketPrice() > 0:
            print(f"✅ ES Prix: ${ticker.marketPrice():.2f}")
            print(f"   Bid: ${ticker.bid:.2f}")
            print(f"   Ask: ${ticker.ask:.2f}")
            print("🎉 SUCCÈS ES !")
        else:
            print("❌ Prix ES non disponible")
            print("   Vérifiez souscriptions CME API")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n3️⃣ Déconnexion...")
        ib.disconnect()
        print("✅ Déconnexion propre")

if __name__ == "__main__":
    try:
        test_es_correct()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


