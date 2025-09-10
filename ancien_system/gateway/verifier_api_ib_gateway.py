#!/usr/bin/env python3
"""
Vérification API IB Gateway
"""

import socket
import time

def verifier_api_ib_gateway():
    """Vérifier si l'API est activée"""
    print("🔍 VÉRIFICATION API IB GATEWAY")
    print("=" * 50)
    
    # Test 1: Port accessible
    print("1️⃣ Test port 4002...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("127.0.0.1", 4002))
        sock.close()
        
        if result == 0:
            print("✅ Port 4002 accessible")
        else:
            print(f"❌ Port 4002 non accessible (code: {result})")
            return False
    except Exception as e:
        print(f"❌ Erreur test port: {e}")
        return False
    
    # Test 2: API native
    print("\n2️⃣ Test API native...")
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        
        class TestWrapper(EWrapper):
            def __init__(self):
                super().__init__()
                self.connected = False
                self.error_msg = ""
            
            def connectAck(self):
                print("✅ API native - CONNEXION RÉUSSIE!")
                self.connected = True
            
            def error(self, reqId, errorCode, errorString):
                if errorCode == 2104 or errorCode == 2106 or errorCode == 2108:
                    print(f"✅ API native - OK ({errorCode})")
                else:
                    print(f"❌ API native - Erreur {errorCode}: {errorString}")
                    self.error_msg = f"{errorCode}: {errorString}"
            
            def nextValidId(self, orderId):
                print(f"✅ API native - ID valide: {orderId}")
        
        wrapper = TestWrapper()
        client = EClient(wrapper)
        
        client.connect("127.0.0.1", 4002, 1)
        
        start_time = time.time()
        while not wrapper.connected and not wrapper.error_msg:
            if time.time() - start_time > 5:
                print("⏰ API native - Timeout")
                break
            client.run()
            time.sleep(0.1)
        
        if wrapper.connected:
            print("🎉 API native fonctionne!")
            client.disconnect()
            return True
        else:
            print(f"❌ API native échoué: {wrapper.error_msg}")
            client.disconnect()
            
    except Exception as e:
        print(f"❌ Erreur API native: {e}")
    
    # Test 3: IB_insync
    print("\n3️⃣ Test IB_insync...")
    try:
        import asyncio
        from ib_insync import IB
        
        async def test_ib_insync():
            ib = IB()
            await ib.connectAsync(host='127.0.0.1', port=4002, clientId=1, timeout=5)
            
            if ib.isConnected():
                print("🎉 IB_insync fonctionne!")
                ib.disconnect()
                return True
            else:
                print("❌ IB_insync échoué")
                return False
        
        success = asyncio.run(test_ib_insync())
        if success:
            return True
            
    except Exception as e:
        print(f"❌ Erreur IB_insync: {e}")
    
    # Conclusion
    print("\n" + "=" * 50)
    print("❌ AUCUNE API FONCTIONNELLE")
    print("\n🔧 SOLUTION OBLIGATOIRE:")
    print("1. Ouvrir IB Gateway")
    print("2. File → Global Configuration")
    print("3. Onglet API → Settings")
    print("4. COCHER 'Enable ActiveX and Socket Clients'")
    print("5. Redémarrer IB Gateway")
    
    return False

if __name__ == "__main__":
    success = verifier_api_ib_gateway()
    
    if success:
        print("\n✅ API IB Gateway fonctionne!")
        print("🎉 Prêt pour MIA_IA_SYSTEM")
    else:
        print("\n❌ API non activée - Suivez les instructions ci-dessus")






