#!/usr/bin/env python3
"""
Test ES Current - MIA_IA_SYSTEM
================================
Test ES avec le contrat actuel (Décembre 2024).
"""

import time
from ib_insync import IB, Future

def test_es_current():
    """Test ES avec contrat actuel"""
    print("🚀 TEST ES FUTURES ACTUEL")
    print("=" * 50)
    
    ib = IB()
    
    try:
        print("1️⃣ Connexion TWS Simulated...")
        ib.connect('127.0.0.1', 7497, clientId=9999)
        print("✅ Connexion OK")
        
        # 2. Test ES avec contrat actuel
        print("\n2️⃣ Test ES Futures (Décembre 2024)...")
        contract = Future('ES', '202412', 'CME')  # Décembre 2024
        
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
        test_es_current()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


