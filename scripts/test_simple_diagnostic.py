#!/usr/bin/env python3
"""
Test Simple Diagnostic - MIA_IA_SYSTEM
======================================
Test de diagnostic simple.
"""

import time
from ib_insync import IB

def test_simple_diagnostic():
    """Test diagnostic simple"""
    print("🚀 TEST DIAGNOSTIC SIMPLE")
    print("=" * 50)
    
    # Connexion TWS
    ib = IB()
    
    try:
        print("1️⃣ Tentative connexion TWS Simulated...")
        print("   Port: 7497")
        print("   Client ID: 9999")
        
        ib.connect('127.0.0.1', 7497, clientId=9999)
        print("✅ Connexion TWS Simulated OK")
        
        # 2. Test simple
        print("\n2️⃣ Test simple...")
        print("   Vérification connexion...")
        time.sleep(2)
        
        if ib.isConnected():
            print("✅ Connexion active")
            print("🎉 SUCCÈS ! API fonctionne !")
        else:
            print("❌ Connexion inactive")
        
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
        test_simple_diagnostic()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


