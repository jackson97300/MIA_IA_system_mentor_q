#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 DIAGNOSTIC TWS API - MIA_IA_SYSTEM
Diagnostic détaillé de la configuration API TWS
"""

import socket
import time
from datetime import datetime

def test_socket_detailed():
    """Test socket détaillé"""
    print("🔍 Test socket détaillé port 7496...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7496))
        
        if result == 0:
            print("✅ Socket accessible")
            # Test d'envoi de données
            try:
                sock.send(b"test")
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

def test_api_connection_detailed():
    """Test connexion API détaillé"""
    print("🔍 Test connexion API détaillé...")
    
    # Test avec différents timeouts
    timeouts = [5, 10, 15]
    
    for timeout in timeouts:
        print(f"   ⏱️ Test avec timeout {timeout}s...")
        try:
            from ib_insync import IB
            ib = IB()
            ib.connect('127.0.0.1', 7496, clientId=1, timeout=timeout)
            
            if ib.isConnected():
                print(f"   ✅ Connexion réussie avec timeout {timeout}s")
                ib.disconnect()
                return True
            else:
                print(f"   ❌ Connexion échouée avec timeout {timeout}s")
                ib.disconnect()
                
        except Exception as e:
            print(f"   ❌ Erreur avec timeout {timeout}s: {e}")
    
    return False

def test_client_ids():
    """Test différents Client IDs"""
    print("🔍 Test différents Client IDs...")
    
    client_ids = [1, 2, 3, 10, 100]
    
    for client_id in client_ids:
        print(f"   🔗 Test Client ID {client_id}...")
        try:
            from ib_insync import IB
            ib = IB()
            ib.connect('127.0.0.1', 7496, clientId=client_id, timeout=5)
            
            if ib.isConnected():
                print(f"   ✅ Client ID {client_id} fonctionne")
                ib.disconnect()
                return client_id
            else:
                print(f"   ❌ Client ID {client_id} échoue")
                ib.disconnect()
                
        except Exception as e:
            print(f"   ❌ Erreur Client ID {client_id}: {e}")
    
    return None

def main():
    print("🔧 DIAGNOSTIC TWS API - MIA_IA_SYSTEM")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Port: 7496 (TWS Réel)")
    print("=" * 50)
    
    # Test 1: Socket détaillé
    socket_ok = test_socket_detailed()
    
    if not socket_ok:
        print("\n❌ Problème de socket")
        print("Vérifiez que TWS est ouvert")
        return
    
    # Test 2: API détaillé
    api_ok = test_api_connection_detailed()
    
    if not api_ok:
        # Test 3: Client IDs
        working_client_id = test_client_ids()
        
        print("\n" + "=" * 50)
        print("📊 RÉSUMÉ DIAGNOSTIC")
        print(f"Socket: {'✅' if socket_ok else '❌'}")
        print(f"API: {'✅' if api_ok else '❌'}")
        
        if working_client_id:
            print(f"Client ID fonctionnel: {working_client_id}")
        else:
            print("❌ Aucun Client ID ne fonctionne")
        
        print("\n🔧 PROBLÈME IDENTIFIÉ: Configuration API TWS")
        print("\n📋 SOLUTION REQUISE:")
        print("1. Dans TWS: Edit > Global Configuration")
        print("2. API > Settings")
        print("   ✅ Enable ActiveX and Socket Clients")
        print("   ✅ Socket port: 7496")
        print("   ✅ Allow connections from localhost")
        print("   ✅ Download open orders on connection")
        print("3. API > Precautions")
        print("   ✅ Bypass Order Precautions for API Orders")
        print("4. Cliquez 'OK' et redémarrez TWS")
        print("5. Relancez ce test")
    else:
        print("\n✅ Connexion API réussie !")
        print("Le problème était le timeout")

if __name__ == "__main__":
    main()


