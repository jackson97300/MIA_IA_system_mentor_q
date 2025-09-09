#!/usr/bin/env python3
"""
Test Connection Only - MIA_IA_SYSTEM
====================================
Test connexion API seulement.
"""

import time
from ib_insync import IB

def test_connection_only():
    """Test connexion seulement"""
    print("🚀 TEST CONNEXION SEULEMENT")
    print("=" * 50)
    
    # Connexion TWS
    ib = IB()
    
    try:
        print("1️⃣ Connexion TWS...")
        ib.connect('127.0.0.1', 7496, clientId=9999)
        print("✅ Connexion TWS OK")
        
        # 2. Test account info (pas de données de marché)
        print("\n2️⃣ Test Account Info...")
        account_info = ib.accountSummary()
        
        if account_info:
            print("✅ Account Info récupéré")
            print("🎉 SUCCÈS ! API fonctionne !")
        else:
            print("❌ Pas d'account info")
        
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
        test_connection_only()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


