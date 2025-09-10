#!/usr/bin/env python3
"""
Vérification statut TWS en temps réel
"""
import socket
import time

def check_tws_status():
    """Vérification complète du statut TWS"""
    print("🔍 VÉRIFICATION STATUT TWS EN TEMPS RÉEL")
    print("=" * 50)
    
    # Test 1: Port 7496
    print("\n📡 Test 1: Port 7496 (TWS Live)")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', 7496))
        sock.close()
        
        if result == 0:
            print("✅ Port 7496: OUVERT (TWS démarré)")
        else:
            print("❌ Port 7496: FERMÉ (TWS pas démarré)")
            return False
    except Exception as e:
        print(f"❌ Erreur test port 7496: {e}")
        return False
    
    # Test 2: Port 7497
    print("\n📡 Test 2: Port 7497 (TWS Paper)")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', 7497))
        sock.close()
        
        if result == 0:
            print("✅ Port 7497: OUVERT (TWS Paper disponible)")
        else:
            print("⚠️ Port 7497: FERMÉ (Normal si TWS configuré pour Live uniquement)")
    except Exception as e:
        print(f"⚠️ Erreur test port 7497: {e}")
    
    # Test 3: Port 4001 (IB Gateway)
    print("\n📡 Test 3: Port 4001 (IB Gateway)")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', 4001))
        sock.close()
        
        if result == 0:
            print("✅ Port 4001: OUVERT (IB Gateway démarré)")
        else:
            print("⚠️ Port 4001: FERMÉ (IB Gateway pas démarré)")
    except Exception as e:
        print(f"⚠️ Erreur test port 4001: {e}")
    
    # Recommandations
    print("\n" + "=" * 50)
    print("🎯 RECOMMANDATIONS")
    print("=" * 50)
    print("1. Vérifiez que TWS affiche 'Connected' en bas")
    print("2. Vérifiez que vous êtes connecté au compte RÉEL")
    print("3. Essayez de redémarrer TWS si nécessaire")
    print("4. Testez avec Client ID 999: python test_tws_client_id_999.py")
    
    return True

if __name__ == "__main__":
    check_tws_status() 