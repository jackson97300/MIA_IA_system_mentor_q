#!/usr/bin/env python3
"""
Debug API IB - Test détaillé des problèmes de connexion
MIA_IA_SYSTEM - Diagnostic complet API IB
"""

import socket
import time
import sys
from datetime import datetime

def test_ib_api_installation():
    """Test de l'installation de l'API IB"""
    print("🔍 Test installation API IB...")
    
    try:
        import ibapi
        print(f"✅ ibapi installé - Version: {ibapi.__version__}")
        
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        from ibapi.contract import Contract
        print("✅ Modules IB API importés avec succès")
        return True
        
    except ImportError as e:
        print(f"❌ Erreur import IB API: {e}")
        print("💡 Installez avec: pip install ibapi")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def test_ib_insync_installation():
    """Test de l'installation d'ib_insync"""
    print("\n🔍 Test installation ib_insync...")
    
    try:
        import ib_insync
        print(f"✅ ib_insync installé - Version: {ib_insync.__version__}")
        
        from ib_insync import IB
        print("✅ Modules ib_insync importés avec succès")
        return True
        
    except ImportError as e:
        print(f"❌ Erreur import ib_insync: {e}")
        print("💡 Installez avec: pip install ib_insync")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def test_api_connection_detailed():
    """Test détaillé de connexion API"""
    print("\n🔧 Test connexion API détaillé...")
    
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        
        class DebugWrapper(EWrapper):
            def __init__(self):
                super().__init__()
                self.connected = False
                self.error_received = False
                self.error_msg = ""
                self.next_valid_id = None
                self.connection_time = None
            
            def connectAck(self):
                self.connected = True
                self.connection_time = time.time()
                print(f"✅ connectAck() appelé à {self.connection_time}")
            
            def error(self, reqId, errorCode, errorString):
                self.error_received = True
                self.error_msg = f"{errorCode}: {errorString}"
                print(f"❌ Erreur API - reqId: {reqId}, Code: {errorCode}, Message: {errorString}")
            
            def nextValidId(self, orderId):
                self.next_valid_id = orderId
                print(f"✅ nextValidId() reçu: {orderId}")
            
            def connectionClosed(self):
                print("⚠️ Connexion fermée par le serveur")
        
        print("📋 Création wrapper et client...")
        wrapper = DebugWrapper()
        client = EClient(wrapper)
        
        print("🔗 Tentative connexion...")
        start_time = time.time()
        client.connect("127.0.0.1", 7497, 1)
        
        print("⏳ Attente connexion...")
        timeout = 10
        while not wrapper.connected and not wrapper.error_received:
            if time.time() - start_time > timeout:
                print(f"⏰ Timeout après {timeout}s")
                break
            
            try:
                client.run()
                time.sleep(0.1)
            except Exception as e:
                print(f"❌ Erreur dans client.run(): {e}")
                break
        
        if wrapper.connected:
            print("🎉 Connexion API réussie !")
            print(f"⏱️ Temps de connexion: {wrapper.connection_time - start_time:.2f}s")
            
            if wrapper.next_valid_id:
                print(f"🆔 ID valide: {wrapper.next_valid_id}")
            
            client.disconnect()
            return True
        else:
            print(f"❌ Connexion échouée: {wrapper.error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ib_insync_connection():
    """Test avec ib_insync"""
    print("\n🔧 Test ib_insync...")
    
    try:
        from ib_insync import IB
        
        print("📋 Création client ib_insync...")
        ib = IB()
        
        print("🔗 Connexion ib_insync...")
        start_time = time.time()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if ib.isConnected():
            print("🎉 Connexion ib_insync réussie !")
            print(f"⏱️ Temps de connexion: {time.time() - start_time:.2f}s")
            
            # Test compte
            accounts = ib.managedAccounts()
            print(f"📊 Comptes: {accounts}")
            
            ib.disconnect()
            return True
        else:
            print("❌ Connexion ib_insync échouée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur ib_insync: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_tws_settings():
    """Vérification des paramètres TWS"""
    print("\n🔍 Vérification paramètres TWS...")
    print("📋 Vérifiez dans TWS:")
    print("   1. Edit > Global Configuration")
    print("   2. API > Settings")
    print("   3. Enable ActiveX and Socket Clients: ✅")
    print("   4. Socket port: 7497")
    print("   5. Allow connections from localhost: ✅")
    print("   6. Read-Only API: ✅ (recommandé)")
    print("   7. Download open orders on connection: ✅")

def main():
    """Test principal de debug"""
    print("🚀 DEBUG API IB - DIAGNOSTIC COMPLET")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test 1: Installation
    ib_api_ok = test_ib_api_installation()
    insync_ok = test_ib_insync_installation()
    
    # Test 2: Connexion API standard
    api_connection_ok = False
    if ib_api_ok:
        api_connection_ok = test_api_connection_detailed()
    
    # Test 3: Connexion ib_insync
    insync_connection_ok = False
    if insync_ok:
        insync_connection_ok = test_ib_insync_connection()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DEBUG")
    print(f"IB API installé: {'✅' if ib_api_ok else '❌'}")
    print(f"ib_insync installé: {'✅' if insync_ok else '❌'}")
    print(f"Connexion API standard: {'✅' if api_connection_ok else '❌'}")
    print(f"Connexion ib_insync: {'✅' if insync_connection_ok else '❌'}")
    
    if api_connection_ok or insync_connection_ok:
        print("\n🎉 API IB FONCTIONNELLE !")
        print("🚀 MIA_IA_SYSTEM peut utiliser l'API")
    else:
        print("\n❌ PROBLÈME API IB")
        print("💡 Solutions possibles:")
        print("   1. Vérifiez que TWS est démarré")
        print("   2. Vérifiez les paramètres API dans TWS")
        print("   3. Redémarrez TWS")
        print("   4. Vérifiez le firewall")
        
        check_tws_settings()

if __name__ == "__main__":
    main()
