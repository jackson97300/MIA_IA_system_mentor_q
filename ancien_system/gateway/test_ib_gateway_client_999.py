#!/usr/bin/env python3
"""
TEST IB GATEWAY CLIENT ID 999 - MIA_IA_SYSTEM
Version: 1.0.0 - Test avec client ID 999
"""

from ib_insync import *
import time

def test_ib_gateway_client_999():
    """Test connexion IB Gateway avec client ID 999"""
    
    print("🔌 Test connexion IB Gateway (Client ID 999)...")
    print("📡 Configuration: 127.0.0.1:4001 (Client ID 999)")
    
    ib = IB()
    
    try:
        print("🔄 Tentative connexion...")
        # Utiliser client ID 999 pour éviter conflits
        ib.connect('127.0.0.1', 4001, clientId=999, timeout=15)
        
        time.sleep(5)  # Attendre plus longtemps
        
        if ib.isConnected():
            print("✅ Connexion IB Gateway réussie!")
            
            # Test données compte
            try:
                account = ib.accountSummary()
                print(f"✅ Données compte: {len(account)} éléments")
                
                # Test données marché
                contract = Future('ES', '202412', 'CME')
                ib.qualifyContracts(contract)
                ib.reqMktData(contract)
                time.sleep(2)
                
                ticker = ib.ticker(contract)
                if ticker.marketPrice():
                    print(f"✅ Prix ES: {ticker.marketPrice()}")
                else:
                    print("⚠️ Pas de données marché")
                    
            except Exception as e:
                print(f"⚠️ Erreur données: {e}")
                
            ib.disconnect()
            return True
        else:
            print("❌ Connexion échouée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TEST IB GATEWAY CLIENT ID 999 - MIA_IA_SYSTEM")
    print("=" * 50)
    
    test_ib_gateway_client_999()
    
    print("\n" + "=" * 50)
    print("✅ Test terminé") 