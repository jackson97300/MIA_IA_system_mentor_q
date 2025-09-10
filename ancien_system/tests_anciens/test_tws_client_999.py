#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 TEST TWS CLIENT ID 999 - MIA_IA_SYSTEM
Test connexion TWS avec Client ID 999 pour éviter tous les conflits
"""

import socket
import time
from datetime import datetime

def test_tws_client_999():
    """Test connexion TWS avec Client ID 999"""
    print("🔍 Test connexion TWS Client ID 999...")
    try:
        from ib_insync import IB
        ib = IB()
        
        print("   🔗 Tentative connexion...")
        ib.connect('127.0.0.1', 7496, clientId=999, timeout=20)
        
        if ib.isConnected():
            print("   ✅ Connexion réussie !")
            
            # Test rapide prix ES
            try:
                from ib_insync import Future
                contract = Future('ES', '20241220', 'CME')
                print(f"   📋 Contrat ES: {contract}")
                
                ib.reqMktData(contract)
                time.sleep(3)
                
                tickers = ib.tickers()
                for ticker in tickers:
                    if ticker.contract.symbol == 'ES':
                        prix = ticker.marketPrice()
                        print(f"   💰 Prix ES: {prix}")
                        
                        if prix and prix > 0:
                            print("   🎉 SUCCÈS ! Prix ES récupéré")
                            ib.disconnect()
                            return True
                        else:
                            print("   ⚠️ Prix ES non disponible")
                            break
                
                print("   ❌ Aucun ticker ES trouvé")
                
            except Exception as e:
                print(f"   ⚠️ Erreur prix ES: {e}")
            
            ib.disconnect()
            return True
        else:
            print("   ❌ Connexion échouée")
            ib.disconnect()
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur connexion: {e}")
        return False

def main():
    print("🚀 TEST TWS CLIENT ID 999 - MIA_IA_SYSTEM")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Port: 7496, Client ID: 999")
    print("=" * 50)
    
    # Test connexion
    success = test_tws_client_999()
    
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    
    if success:
        print("✅ Connexion TWS réussie avec Client ID 999")
        print("📋 Configuration finale pour MIA_IA_SYSTEM:")
        print("   - Host: 127.0.0.1")
        print("   - Port: 7496")
        print("   - Client ID: 999")
        print("   - Mode: RÉEL")
    else:
        print("❌ Connexion échouée même avec Client ID 999")
        print("🔧 Le problème n'est pas le Client ID")
        print("💡 Vérifiez que TWS a bien redémarré après la configuration")

if __name__ == "__main__":
    main()


