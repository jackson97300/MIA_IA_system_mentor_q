#!/usr/bin/env python3
"""
Test rapide Client ID 999 - IB Gateway
"""

import time

def test_client_999():
    print("🚀 TEST RAPIDE - CLIENT ID 999")
    print("=" * 40)
    
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        
        class QuickWrapper(EWrapper):
            def __init__(self):
                super().__init__()
                self.connected = False
                self.error_msg = ""
            
            def connectAck(self):
                print("✅ CONNEXION RÉUSSIE!")
                self.connected = True
            
            def error(self, reqId, errorCode, errorString):
                if errorCode == 2104 or errorCode == 2106 or errorCode == 2108:
                    print(f"✅ Client ID 999 - OK ({errorCode})")
                else:
                    print(f"❌ Erreur {errorCode}: {errorString}")
                    self.error_msg = f"{errorCode}: {errorString}"
            
            def nextValidId(self, orderId):
                print(f"✅ ID valide: {orderId}")
        
        # Test rapide
        wrapper = QuickWrapper()
        client = EClient(wrapper)
        
        print("🔗 Connexion Client ID 999...")
        client.connect("127.0.0.1", 4002, 999)
        
        # Timeout court : 4 secondes
        start_time = time.time()
        while not wrapper.connected and not wrapper.error_msg:
            if time.time() - start_time > 4:
                print("⏰ Timeout (4s)")
                break
            client.run()
            time.sleep(0.1)
        
        if wrapper.connected:
            print("🎉 SUCCÈS - Client ID 999 fonctionne!")
            client.disconnect()
            
            # Configuration recommandée
            config = {
                "ibkr_host": "127.0.0.1",
                "ibkr_port": 4002,
                "ibkr_client_id": 999,
                "connection_timeout": 20
            }
            
            print(f"\n🔧 Configuration MIA_IA_SYSTEM:")
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
    success = test_client_999()
    
    if success:
        print("\n✅ Client ID 999 prêt pour MIA_IA_SYSTEM")
    else:
        print("\n❌ Client ID 999 ne fonctionne pas")
        print("💡 Essayez Client ID 1 ou 100")






