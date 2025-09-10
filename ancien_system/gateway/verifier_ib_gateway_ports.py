#!/usr/bin/env python3
"""
Vérification des ports IB Gateway après redémarrage
"""

import socket
import time
import subprocess

def check_port(host, port, timeout=2):
    """Vérifier si un port est ouvert"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def find_ib_gateway_ports():
    """Trouver les ports IB Gateway actifs"""
    print("🔍 Recherche des ports IB Gateway...")
    print("=" * 50)
    
    # Ports possibles IB Gateway
    possible_ports = [
        4001,  # IB Gateway Paper
        4002,  # IB Gateway Live
        7496,  # TWS Paper
        7497,  # TWS Live
        7495,  # TWS Paper (ancien)
        7494,  # TWS Live (ancien)
    ]
    
    active_ports = []
    
    for port in possible_ports:
        if check_port("127.0.0.1", port):
            print(f"✅ Port {port} - ACTIF")
            active_ports.append(port)
        else:
            print(f"❌ Port {port} - INACTIF")
    
    return active_ports

def test_connection_on_port(port):
    """Tester la connexion sur un port spécifique"""
    print(f"\n🔧 Test connexion port {port}")
    
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        
        class TestWrapper(EWrapper):
            def __init__(self):
                super().__init__()
                self.connected = False
                self.error_msg = ""
            
            def connectAck(self):
                print(f"✅ Connexion établie sur port {port}")
                self.connected = True
            
            def error(self, reqId, errorCode, errorString):
                print(f"❌ Erreur {errorCode}: {errorString}")
                self.error_msg = f"{errorCode}: {errorString}"
            
            def nextValidId(self, orderId):
                print(f"✅ ID valide reçu: {orderId}")
        
        # Test avec Client ID 1
        wrapper = TestWrapper()
        client = EClient(wrapper)
        
        print(f"🔗 Tentative connexion 127.0.0.1:{port} (Client ID 1)")
        client.connect("127.0.0.1", port, 1)
        
        # Attendre 5 secondes
        start_time = time.time()
        while not wrapper.connected and not wrapper.error_msg:
            if time.time() - start_time > 5:
                print("⏰ Timeout")
                break
            client.run()
            time.sleep(0.1)
        
        if wrapper.connected:
            print(f"🎉 SUCCÈS - Port {port} fonctionne avec Client ID 1")
            client.disconnect()
            return True
        else:
            print(f"❌ ÉCHEC - Port {port}: {wrapper.error_msg}")
            return False
            
    except ImportError:
        print("❌ IB API non installée")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 VÉRIFICATION IB GATEWAY APRÈS REDÉMARRAGE")
    print("=" * 60)
    
    # Attendre un peu que IB Gateway démarre
    print("⏳ Attente du démarrage IB Gateway...")
    time.sleep(3)
    
    # Trouver les ports actifs
    active_ports = find_ib_gateway_ports()
    
    if not active_ports:
        print("\n❌ AUCUN PORT IB GATEWAY TROUVÉ")
        print("Vérifiez que IB Gateway est bien démarré")
        return
    
    print(f"\n✅ {len(active_ports)} port(s) actif(s) trouvé(s)")
    
    # Tester chaque port actif
    working_ports = []
    for port in active_ports:
        if test_connection_on_port(port):
            working_ports.append(port)
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ FINAL")
    
    if working_ports:
        print(f"🎉 {len(working_ports)} port(s) fonctionnel(s): {working_ports}")
        print(f"💡 Utilisez le port {working_ports[0]} pour MIA_IA_SYSTEM")
        
        # Créer config recommandée
        config = {
            "ibkr_host": "127.0.0.1",
            "ibkr_port": working_ports[0],
            "ibkr_client_id": 1,
            "connection_timeout": 20
        }
        
        print(f"\n🔧 Configuration recommandée:")
        print(f"   Host: {config['ibkr_host']}")
        print(f"   Port: {config['ibkr_port']}")
        print(f"   Client ID: {config['ibkr_client_id']}")
        
    else:
        print("❌ AUCUN PORT FONCTIONNEL")
        print("Vérifiez la configuration IB Gateway")

if __name__ == "__main__":
    main()






