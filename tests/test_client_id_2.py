#!/usr/bin/env python3
"""
Test rapide Client ID 2 - IB Gateway
"""

import socket
import time

def test_client_id_2():
    """Test rapide Client ID 2"""
    print("🚀 TEST RAPIDE - CLIENT ID 2")
    print("=" * 40)
    
    host = "127.0.0.1"
    port = 4002
    client_id = 2
    timeout = 5
    
    print(f"🔍 Test Client ID {client_id} sur {host}:{port}")
    print(f"⏱️ Timeout: {timeout} secondes")
    print()
    
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
                print(f"❌ Erreur {errorCode}: {errorString}")
                self.error_msg = f"{errorCode}: {errorString}"
            
            def nextValidId(self, orderId):
                print(f"✅ ID valide: {orderId}")
        
        # Test rapide
        wrapper = QuickWrapper()
        client = EClient(wrapper)
        
        print(f"🔗 Connexion Client ID {client_id}...")
        client.connect(host, port, client_id)
        
        # Attendre 5 secondes max
        start_time = time.time()
        while not wrapper.connected and not wrapper.error_msg:
            if time.time() - start_time > timeout:
                print("⏰ Timeout")
                break
            client.run()
            time.sleep(0.1)
        
        if wrapper.connected:
            print("🎉 SUCCÈS - Client ID 2 fonctionne!")
            client.disconnect()
            
            # Configuration recommandée
            config = {
                "ibkr_host": host,
                "ibkr_port": port,
                "ibkr_client_id": client_id,
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
            
    except ImportError:
        print("❌ IB API non installée")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = test_client_id_2()
    
    if success:
        print("\n✅ Client ID 2 prêt pour MIA_IA_SYSTEM")
    else:
        print("\n❌ Client ID 2 ne fonctionne pas")
        print("💡 Essayez un autre Client ID (1, 3, 4, 5...)")






