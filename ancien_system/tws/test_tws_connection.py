#!/usr/bin/env python3
"""
TEST TWS CONNECTION - MIA_IA_SYSTEM
Version: 1.0.0 - Test TWS au lieu d'IB Gateway
"""

from ib_insync import *
import time

def test_tws_connection():
    """Test connexion TWS"""
    
    print("🔌 Test connexion TWS...")
    print("📡 Configuration: 127.0.0.1:7497 (TWS)")
    
    ib = IB()
    
    try:
        print("🔄 Tentative connexion TWS...")
        # Port TWS standard : 7497
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=15)
        
        time.sleep(3)
        
        if ib.isConnected():
            print("✅ Connexion TWS réussie!")
            
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
            print("❌ Connexion TWS échouée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur TWS: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TEST CONNEXION TWS - MIA_IA_SYSTEM")
    print("=" * 50)
    
    test_tws_connection()
    
    print("\n" + "=" * 50)
    print("✅ Test terminé") 