#!/usr/bin/env python3
"""
Test TWS rapide - Diagnostic simple
MIA_IA_SYSTEM - Test de connexion direct
"""

import time
from datetime import datetime

def test_ib_insync_rapide():
    """Test rapide avec ib_insync"""
    print("🔧 Test ib_insync rapide...")
    
    try:
        from ib_insync import IB
        
        print("📋 Création client...")
        ib = IB()
        
        print("🔗 Connexion 127.0.0.1:7497...")
        start_time = time.time()
        
        # Test avec timeout court
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=5)
        
        if ib.isConnected():
            print("🎉 Connexion réussie !")
            print(f"⏱️ Temps: {time.time() - start_time:.2f}s")
            
            # Test compte
            try:
                accounts = ib.managedAccounts()
                print(f"📊 Comptes: {accounts}")
            except:
                print("⚠️ Impossible de récupérer les comptes")
            
            ib.disconnect()
            return True
        else:
            print("❌ Connexion échouée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_ibapi_rapide():
    """Test rapide avec ibapi standard"""
    print("\n🔧 Test ibapi rapide...")
    
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        
        class SimpleWrapper(EWrapper):
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
        wrapper = SimpleWrapper()
        client = EClient(wrapper)
        
        print("🔗 Connexion 127.0.0.1:7497...")
        start_time = time.time()
        client.connect("127.0.0.1", 7497, 1)
        
        # Test rapide
        timeout = 5
        while not wrapper.connected and not wrapper.error_msg:
            if time.time() - start_time > timeout:
                print("⏰ Timeout")
                break
            client.run()
            time.sleep(0.1)
        
        if wrapper.connected:
            print("🎉 Connexion réussie !")
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
    print("🚀 TEST TWS RAPIDE")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 40)
    
    # Test 1: ib_insync
    insync_ok = test_ib_insync_rapide()
    
    # Test 2: ibapi
    api_ok = test_ibapi_rapide()
    
    # Résumé
    print("\n" + "=" * 40)
    print("📊 RÉSUMÉ")
    print(f"ib_insync: {'✅ OK' if insync_ok else '❌ ÉCHEC'}")
    print(f"ibapi: {'✅ OK' if api_ok else '❌ ÉCHEC'}")
    
    if insync_ok or api_ok:
        print("\n🎉 TWS FONCTIONNE !")
        print("🚀 MIA_IA_SYSTEM peut démarrer")
    else:
        print("\n❌ PROBLÈME TWS")
        print("💡 Vérifiez:")
        print("   - TWS est démarré")
        print("   - Mode Paper Trading")
        print("   - Port 7497 ouvert")
        print("   - API activée dans TWS")

if __name__ == "__main__":
    main()




