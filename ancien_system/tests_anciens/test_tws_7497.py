#!/usr/bin/env python3
"""
Test TWS sur port 7497
"""

import time

def test_tws_7497():
    """Test TWS port 7497"""
    print("🚀 TEST TWS - PORT 7497")
    print("=" * 40)
    
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        
        class TWSWrapper(EWrapper):
            def __init__(self):
                super().__init__()
                self.connected = False
                self.error_msg = ""
            
            def connectAck(self):
                print("✅ TWS - CONNEXION RÉUSSIE!")
                self.connected = True
            
            def error(self, reqId, errorCode, errorString):
                if errorCode == 2104 or errorCode == 2106 or errorCode == 2108:
                    print(f"✅ TWS - OK ({errorCode})")
                else:
                    print(f"❌ TWS - Erreur {errorCode}: {errorString}")
                    self.error_msg = f"{errorCode}: {errorString}"
            
            def nextValidId(self, orderId):
                print(f"✅ TWS - ID valide: {orderId}")
        
        # Test TWS
        wrapper = TWSWrapper()
        client = EClient(wrapper)
        
        print("🔗 Connexion TWS 127.0.0.1:7497...")
        print("   Client ID: 1")
        
        client.connect("127.0.0.1", 7497, 1)
        
        # Attendre 8 secondes (TWS plus lent)
        start_time = time.time()
        while not wrapper.connected and not wrapper.error_msg:
            if time.time() - start_time > 8:
                print("⏰ TWS - Timeout")
                break
            client.run()
            time.sleep(0.1)
        
        if wrapper.connected:
            print("🎉 SUCCÈS - TWS fonctionne!")
            client.disconnect()
            
            # Configuration recommandée
            config = {
                "ibkr_host": "127.0.0.1",
                "ibkr_port": 7497,
                "ibkr_client_id": 1,
                "connection_timeout": 20
            }
            
            print(f"\n🔧 Configuration MIA_IA_SYSTEM (TWS):")
            print(f"   Host: {config['ibkr_host']}")
            print(f"   Port: {config['ibkr_port']}")
            print(f"   Client ID: {config['ibkr_client_id']}")
            
            return True
        else:
            print(f"❌ ÉCHEC - {wrapper.error_msg}")
            client.disconnect()
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = test_tws_7497()
    
    if success:
        print("\n✅ TWS prêt pour MIA_IA_SYSTEM")
        print("🎉 Utilisez TWS au lieu d'IB Gateway")
    else:
        print("\n❌ TWS ne fonctionne pas")
        print("💡 Vérifiez la configuration API dans TWS")






