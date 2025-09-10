#!/usr/bin/env python3
"""
Test de connexion TWS simple - Port 7497
MIA_IA_SYSTEM - Test rapide de connectivité
"""

import socket
import time
from datetime import datetime

def test_port_7497():
    """Test simple du port 7497"""
    print("🔍 Test de connexion TWS Paper Trading - Port 7497")
    print("=" * 50)
    
    host = "127.0.0.1"
    port = 7497
    timeout = 10
    
    try:
        print(f"📡 Tentative connexion {host}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        start_time = time.time()
        result = sock.connect_ex((host, port))
        end_time = time.time()
        
        if result == 0:
            print(f"✅ Connexion réussie en {end_time - start_time:.2f}s")
            print("🎉 TWS Paper Trading est accessible !")
            sock.close()
            return True
        else:
            print(f"❌ Connexion échouée (code: {result})")
            print("💡 Vérifiez que TWS est démarré en mode Paper Trading")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_ib_api():
    """Test rapide de l'API IB"""
    print("\n🔧 Test API IB...")
    
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        
        class SimpleWrapper(EWrapper):
            def __init__(self):
                super().__init__()
                self.connected = False
                self.error_msg = ""
            
            def connectAck(self):
                print("✅ Connexion API établie")
                self.connected = True
            
            def error(self, reqId, errorCode, errorString):
                print(f"❌ Erreur API: {errorCode} - {errorString}")
                self.error_msg = f"{errorCode}: {errorString}"
            
            def nextValidId(self, orderId):
                print(f"✅ ID valide: {orderId}")
        
        wrapper = SimpleWrapper()
        client = EClient(wrapper)
        
        print("🔗 Connexion API...")
        client.connect("127.0.0.1", 7497, 1)
        
        # Test rapide
        start_time = time.time()
        while not wrapper.connected and not wrapper.error_msg:
            if time.time() - start_time > 5:
                print("⏰ Timeout API")
                break
            client.run()
            time.sleep(0.1)
        
        if wrapper.connected:
            print("🎉 API IB fonctionne !")
            client.disconnect()
            return True
        else:
            print(f"❌ API échouée: {wrapper.error_msg}")
            return False
            
    except ImportError:
        print("❌ IB API non installée")
        return False
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return False

def main():
    """Test principal"""
    print("🚀 TEST CONNEXION TWS PAPER TRADING")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test 1: Port
    port_ok = test_port_7497()
    
    # Test 2: API
    api_ok = False
    if port_ok:
        api_ok = test_ib_api()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    print(f"Port 7497: {'✅ OK' if port_ok else '❌ ÉCHEC'}")
    print(f"API IB: {'✅ OK' if api_ok else '❌ ÉCHEC'}")
    
    if port_ok and api_ok:
        print("\n🎉 TWS PAPER TRADING OPÉRATIONNEL !")
        print("🚀 MIA_IA_SYSTEM peut démarrer")
    elif port_ok:
        print("\n⚠️ Port ouvert mais API problème")
        print("💡 Vérifiez les paramètres TWS")
    else:
        print("\n❌ TWS non accessible")
        print("💡 Vérifiez que TWS est démarré")

if __name__ == "__main__":
    main()




