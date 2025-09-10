#!/usr/bin/env python3
"""
Test IB Gateway - Port 4001
MIA_IA_SYSTEM - Test de connexion IB Gateway
"""

import time
from datetime import datetime

def test_ib_gateway_4001():
    """Test IB Gateway port 4001"""
    print("🔧 Test IB Gateway port 4001...")
    
    try:
        from ib_insync import IB
        
        print("📋 Création client...")
        ib = IB()
        
        print("🔗 Connexion 127.0.0.1:4001...")
        start_time = time.time()
        
        # Test avec timeout court
        ib.connect('127.0.0.1', 4001, clientId=1, timeout=10)
        
        if ib.isConnected():
            print("🎉 Connexion IB Gateway réussie !")
            print(f"⏱️ Temps: {time.time() - start_time:.2f}s")
            
            # Test compte
            try:
                accounts = ib.managedAccounts()
                print(f"📊 Comptes: {accounts}")
            except:
                print("⚠️ Impossible de récupérer les comptes")
            
            # Test ES contract
            try:
                from ib_insync import Future
                contract = Future('ES', '20241220', 'CME')
                print(f"📋 Contrat ES: {contract}")
            except:
                print("⚠️ Impossible de créer le contrat ES")
            
            ib.disconnect()
            return True
        else:
            print("❌ Connexion IB Gateway échouée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_ibapi_gateway_4001():
    """Test IB API avec Gateway"""
    print("\n🔧 Test IB API avec Gateway...")
    
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        
        class GatewayWrapper(EWrapper):
            def __init__(self):
                super().__init__()
                self.connected = False
                self.error_msg = ""
            
            def connectAck(self):
                print("✅ connectAck() reçu")
                self.connected = True
            
            def error(self, reqId, errorCode, errorString):
                print(f"❌ Erreur {errorCode}: {errorString}")
                self.error_msg = f"{errorCode}: {errorString}"
            
            def nextValidId(self, orderId):
                print(f"✅ ID valide: {orderId}")
        
        print("📋 Création client...")
        wrapper = GatewayWrapper()
        client = EClient(wrapper)
        
        print("🔗 Connexion 127.0.0.1:4001...")
        start_time = time.time()
        client.connect("127.0.0.1", 4001, 1)
        
        # Test rapide
        timeout = 10
        while not wrapper.connected and not wrapper.error_msg:
            if time.time() - start_time > timeout:
                print("⏰ Timeout")
                break
            client.run()
            time.sleep(0.1)
        
        if wrapper.connected:
            print("🎉 Connexion API Gateway réussie !")
            print(f"⏱️ Temps: {time.time() - start_time:.2f}s")
            client.disconnect()
            return True
        else:
            print(f"❌ Échec: {wrapper.error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Test principal"""
    print("🚀 TEST IB GATEWAY - PORT 4001")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test 1: ib_insync
    insync_ok = test_ib_gateway_4001()
    
    # Test 2: ibapi
    api_ok = test_ibapi_gateway_4001()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    print(f"ib_insync: {'✅ OK' if insync_ok else '❌ ÉCHEC'}")
    print(f"ibapi: {'✅ OK' if api_ok else '❌ ÉCHEC'}")
    
    if insync_ok or api_ok:
        print("\n🎉 IB GATEWAY FONCTIONNE !")
        print("🚀 MIA_IA_SYSTEM peut utiliser IB Gateway")
        print("💡 Configuration recommandée:")
        print("   - Host: 127.0.0.1")
        print("   - Port: 4001")
        print("   - Client ID: 1")
    else:
        print("\n❌ PROBLÈME IB GATEWAY")
        print("💡 Vérifiez:")
        print("   - IB Gateway est démarré")
        print("   - Mode Paper Trading")
        print("   - Port 4001 ouvert")

if __name__ == "__main__":
    main()



