#!/usr/bin/env python3
"""
Test ultra-rapide Client ID 2
"""

import time

def test_ultra_rapide():
    print("⚡ TEST ULTRA-RAPIDE - CLIENT ID 2")
    print("=" * 40)
    
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        
        class UltraWrapper(EWrapper):
            def __init__(self):
                super().__init__()
                self.connected = False
                self.error_msg = ""
            
            def connectAck(self):
                print("✅ CONNEXION RÉUSSIE!")
                self.connected = True
            
            def error(self, reqId, errorCode, errorString):
                if errorCode == 2104 or errorCode == 2106 or errorCode == 2108:
                    print(f"✅ Client ID 2 - OK ({errorCode})")
                else:
                    print(f"❌ Erreur {errorCode}: {errorString}")
                    self.error_msg = f"{errorCode}: {errorString}"
            
            def nextValidId(self, orderId):
                print(f"✅ ID valide: {orderId}")
        
        # Test ultra-rapide
        wrapper = UltraWrapper()
        client = EClient(wrapper)
        
        print("🔗 Connexion Client ID 2...")
        client.connect("127.0.0.1", 4002, 2)
        
        # Timeout très court : 3 secondes
        start_time = time.time()
        while not wrapper.connected and not wrapper.error_msg:
            if time.time() - start_time > 3:
                print("⏰ Timeout (3s)")
                break
            client.run()
            time.sleep(0.05)  # Plus rapide
        
        if wrapper.connected:
            print("🎉 SUCCÈS - Client ID 2 fonctionne!")
            client.disconnect()
            return True
        else:
            print(f"❌ ÉCHEC - {wrapper.error_msg}")
            client.disconnect()
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = test_ultra_rapide()
    
    if success:
        print("\n✅ Client ID 2 prêt pour MIA_IA_SYSTEM")
        print("🔧 Config: Host=127.0.0.1, Port=4002, Client ID=2")
    else:
        print("\n❌ Client ID 2 ne fonctionne pas")
        print("💡 Essayez Client ID 1 ou 3")






