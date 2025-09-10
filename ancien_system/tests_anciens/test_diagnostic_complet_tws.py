#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 DIAGNOSTIC COMPLET TWS - MIA_IA_SYSTEM
Diagnostic basé sur l'analyse du code et de la documentation
"""

import socket
import time
import asyncio
from datetime import datetime

def test_socket_detailed():
    """Test socket détaillé avec analyse"""
    print("🔍 Test socket détaillé port 7496...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7496))
        
        if result == 0:
            print("✅ Socket accessible")
            # Test d'envoi de données IBKR
            try:
                # Envoi d'un message de test IBKR
                test_message = b"test"
                sock.send(test_message)
                print("✅ Socket accepte les données")
            except Exception as e:
                print(f"❌ Erreur envoi socket: {e}")
            sock.close()
            return True
        else:
            print(f"❌ Socket inaccessible (code: {result})")
            sock.close()
            return False
    except Exception as e:
        print(f"❌ Erreur socket: {e}")
        return False

def test_ib_insync_detailed():
    """Test ib_insync détaillé avec analyse"""
    print("🔍 Test ib_insync détaillé...")
    
    try:
        from ib_insync import IB
        print("   ✅ ib_insync importé")
        
        ib = IB()
        print("   ✅ IB() créé")
        
        # Test avec différents paramètres
        test_configs = [
            {'client_id': 999, 'timeout': 10},
            {'client_id': 1, 'timeout': 20},
            {'client_id': 100, 'timeout': 15}
        ]
        
        for i, config in enumerate(test_configs):
            print(f"   🔗 Test {i+1}: Client ID {config['client_id']}, Timeout {config['timeout']}s")
            try:
                # Test connexion sync d'abord
                ib.connect('127.0.0.1', 7496, clientId=config['client_id'], timeout=config['timeout'])
                
                if ib.isConnected():
                    print(f"   ✅ Connexion réussie avec config {i+1}")
                    
                    # Test rapide
                    try:
                        from ib_insync import Future
                        contract = Future('ES', '20241220', 'CME')
                        ib.reqMktData(contract)
                        time.sleep(2)
                        
                        tickers = ib.tickers()
                        if tickers:
                            print(f"   📊 {len(tickers)} tickers reçus")
                            for ticker in tickers:
                                if ticker.contract.symbol == 'ES':
                                    prix = ticker.marketPrice()
                                    print(f"   💰 Prix ES: {prix}")
                                    if prix and prix > 0:
                                        print(f"   🎉 SUCCÈS COMPLET avec config {i+1} !")
                                        ib.disconnect()
                                        return True, config
                    except Exception as e:
                        print(f"   ⚠️ Erreur test prix: {e}")
                    
                    ib.disconnect()
                    return True, config
                else:
                    print(f"   ❌ Connexion échouée avec config {i+1}")
                    ib.disconnect()
                    
            except Exception as e:
                print(f"   ❌ Erreur config {i+1}: {e}")
                try:
                    ib.disconnect()
                except:
                    pass
        
        return False, None
        
    except ImportError as e:
        print(f"   ❌ ib_insync non disponible: {e}")
        return False, None
    except Exception as e:
        print(f"   ❌ Erreur ib_insync: {e}")
        return False, None

def test_ibapi_detailed():
    """Test ibapi détaillé"""
    print("🔍 Test ibapi détaillé...")
    
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        print("   ✅ ibapi importé")
        
        class TestWrapper(EWrapper):
            def __init__(self):
                self.connected = False
                self.error_received = False
                self.error_message = ""
            
            def connectAck(self):
                self.connected = True
                print("   ✅ ibapi connectAck reçu")
            
            def error(self, reqId, errorCode, errorString):
                self.error_received = True
                self.error_message = f"Code {errorCode}: {errorString}"
                print(f"   ❌ ibapi erreur: {self.error_message}")
        
        class TestClient(EClient):
            def __init__(self, wrapper):
                EClient.__init__(self, wrapper)
        
        wrapper = TestWrapper()
        client = TestClient(wrapper)
        
        print("   🔗 Tentative connexion ibapi...")
        client.connect('127.0.0.1', 7496, 999)
        
        # Attendre un peu
        time.sleep(3)
        
        if wrapper.connected:
            print("   ✅ ibapi connecté")
            client.disconnect()
            return True
        elif wrapper.error_received:
            print(f"   ❌ ibapi erreur: {wrapper.error_message}")
            client.disconnect()
            return False
        else:
            print("   ❌ ibapi timeout")
            client.disconnect()
            return False
            
    except ImportError as e:
        print(f"   ❌ ibapi non disponible: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Erreur ibapi: {e}")
        return False

def analyze_configuration():
    """Analyse de la configuration basée sur la documentation"""
    print("🔍 Analyse configuration basée sur la documentation...")
    
    print("   📋 Configuration TWS requise (d'après docs):")
    print("      ✅ Enable ActiveX and Socket Clients")
    print("      ✅ Socket port: 7496 (TWS Réel)")
    print("      ✅ Allow connections from localhost")
    print("      ✅ Download open orders on connection")
    print("      ✅ Bypass Order Precautions for API Orders")
    
    print("   📋 Configuration MIA_IA_SYSTEM (d'après code):")
    print("      - Host: 127.0.0.1")
    print("      - Port: 7496 (TWS Réel)")
    print("      - Client ID: Variable (1, 999, 100)")
    print("      - Timeout: 20-30s")
    
    print("   🔍 Problèmes potentiels identifiés:")
    print("      1. TWS n'a pas redémarré après configuration")
    print("      2. Conflit de Client ID avec autre application")
    print("      3. Firewall/antivirus bloque la connexion")
    print("      4. TWS en mode lecture seule")
    print("      5. Problème de permissions Windows")

def main():
    print("🔧 DIAGNOSTIC COMPLET TWS - MIA_IA_SYSTEM")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Analyse basée sur le code et la documentation")
    print("=" * 60)
    
    # Test 1: Socket
    socket_ok = test_socket_detailed()
    
    # Test 2: ib_insync
    ib_insync_ok, working_config = test_ib_insync_detailed()
    
    # Test 3: ibapi
    ibapi_ok = test_ibapi_detailed()
    
    # Analyse configuration
    analyze_configuration()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DIAGNOSTIC COMPLET")
    print(f"Socket: {'✅' if socket_ok else '❌'}")
    print(f"ib_insync: {'✅' if ib_insync_ok else '❌'}")
    print(f"ibapi: {'✅' if ibapi_ok else '❌'}")
    
    if working_config:
        print(f"✅ Configuration fonctionnelle trouvée: {working_config}")
        print("\n🎉 SUCCÈS ! Configuration optimale:")
        print(f"   - Host: 127.0.0.1")
        print(f"   - Port: 7496")
        print(f"   - Client ID: {working_config['client_id']}")
        print(f"   - Timeout: {working_config['timeout']}s")
    else:
        print("\n❌ Aucune configuration fonctionnelle")
        print("\n🔧 SOLUTIONS RECOMMANDÉES:")
        print("1. Redémarrez TWS complètement")
        print("2. Vérifiez qu'aucune autre application n'utilise le port 7496")
        print("3. Désactivez temporairement firewall/antivirus")
        print("4. Vérifiez les permissions Windows")
        print("5. Testez avec TWS en mode Paper Trading (port 7497)")

if __name__ == "__main__":
    main()


