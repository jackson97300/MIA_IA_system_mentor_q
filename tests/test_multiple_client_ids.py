#!/usr/bin/env python3
"""
Test multiple Client IDs avec IB Gateway
Trouver le Client ID qui fonctionne
"""

import socket
import time
import threading

def test_client_id(host, port, client_id, timeout=5):
    """Tester un Client ID spécifique"""
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        
        class TestWrapper(EWrapper):
            def __init__(self, client_id):
                super().__init__()
                self.client_id = client_id
                self.connected = False
                self.error_msg = ""
                self.error_code = None
            
            def connectAck(self):
                print(f"✅ Client ID {self.client_id} - CONNEXION RÉUSSIE!")
                self.connected = True
            
            def error(self, reqId, errorCode, errorString):
                self.error_code = errorCode
                self.error_msg = errorString
                if errorCode == 2104:  # Market data farm connection is OK
                    print(f"✅ Client ID {self.client_id} - Market data OK")
                elif errorCode == 2106:  # HMDS data farm connection is OK
                    print(f"✅ Client ID {self.client_id} - HMDS OK")
                elif errorCode == 2108:  # Financial data farm connection is OK
                    print(f"✅ Client ID {self.client_id} - Financial data OK")
                elif errorCode == 2158:  # Sec-def data farm connection is OK
                    print(f"✅ Client ID {self.client_id} - Sec-def OK")
                else:
                    print(f"❌ Client ID {self.client_id} - Erreur {errorCode}: {errorString}")
            
            def nextValidId(self, orderId):
                print(f"✅ Client ID {self.client_id} - ID valide: {orderId}")
        
        # Créer client
        wrapper = TestWrapper(client_id)
        client = EClient(wrapper)
        
        # Connexion
        client.connect(host, port, client_id)
        
        # Attendre connexion
        start_time = time.time()
        while not wrapper.connected and not wrapper.error_msg:
            if time.time() - start_time > timeout:
                break
            client.run()
            time.sleep(0.1)
        
        # Résultat
        if wrapper.connected:
            client.disconnect()
            return True, f"Client ID {client_id} - SUCCÈS"
        else:
            client.disconnect()
            return False, f"Client ID {client_id} - ÉCHEC: {wrapper.error_msg}"
            
    except Exception as e:
        return False, f"Client ID {client_id} - ERREUR: {e}"

def test_all_client_ids():
    """Tester tous les Client IDs"""
    print("🚀 TEST MULTIPLE CLIENT IDs - IB GATEWAY")
    print("=" * 60)
    
    host = "127.0.0.1"
    port = 4002  # IB Gateway
    timeout = 8  # Timeout plus long
    
    # Client IDs à tester (par ordre de priorité)
    client_ids = [
        1,      # Client ID 1 (solution documentée)
        999,    # Client ID 999 (standard)
        100,    # Client ID 100
        101,    # Client ID 101
        102,    # Client ID 102
        103,    # Client ID 103
        104,    # Client ID 104
        105,    # Client ID 105
        200,    # Client ID 200
        300,    # Client ID 300
        400,    # Client ID 400
        500,    # Client ID 500
        600,    # Client ID 600
        700,    # Client ID 700
        800,    # Client ID 800
        900,    # Client ID 900
    ]
    
    print(f"🔍 Test de {len(client_ids)} Client IDs sur {host}:{port}")
    print(f"⏱️ Timeout par test: {timeout} secondes")
    print()
    
    # Vérifier d'abord si le port est accessible
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result != 0:
            print(f"❌ Port {port} non accessible (code: {result})")
            print("Vérifiez que IB Gateway est démarré")
            return
        else:
            print(f"✅ Port {port} accessible")
    except Exception as e:
        print(f"❌ Erreur test port: {e}")
        return
    
    print()
    
    # Tester chaque Client ID
    working_clients = []
    failed_clients = []
    
    for i, client_id in enumerate(client_ids, 1):
        print(f"🔧 Test {i}/{len(client_ids)}: Client ID {client_id}")
        
        success, message = test_client_id(host, port, client_id, timeout)
        
        if success:
            working_clients.append(client_id)
            print(f"🎉 {message}")
        else:
            failed_clients.append(client_id)
            print(f"❌ {message}")
        
        print("-" * 40)
        time.sleep(1)  # Pause entre tests
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 60)
    
    if working_clients:
        print(f"🎉 {len(working_clients)} Client ID(s) fonctionnel(s):")
        for client_id in working_clients:
            print(f"   ✅ Client ID {client_id}")
        
        # Recommandation
        recommended_client = working_clients[0]
        print(f"\n💡 CLIENT ID RECOMMANDÉ: {recommended_client}")
        
        # Configuration pour MIA_IA_SYSTEM
        config = {
            "ibkr_host": host,
            "ibkr_port": port,
            "ibkr_client_id": recommended_client,
            "connection_timeout": 20
        }
        
        print(f"\n🔧 Configuration MIA_IA_SYSTEM:")
        print(f"   Host: {config['ibkr_host']}")
        print(f"   Port: {config['ibkr_port']}")
        print(f"   Client ID: {config['ibkr_client_id']}")
        
        # Sauvegarder la configuration
        import json
        with open("ibkr_working_config.json", "w") as f:
            json.dump(config, f, indent=2)
        print(f"\n💾 Configuration sauvegardée: ibkr_working_config.json")
        
    else:
        print("❌ AUCUN CLIENT ID FONCTIONNEL")
        print("Vérifiez la configuration API dans IB Gateway:")
        print("  - File → Global Configuration → API → Settings")
        print("  - Cocher 'Enable ActiveX and Socket Clients'")
        print("  - Redémarrer IB Gateway")
    
    if failed_clients:
        print(f"\n❌ {len(failed_clients)} Client ID(s) échoué(s):")
        for client_id in failed_clients[:5]:  # Afficher seulement les 5 premiers
            print(f"   ❌ Client ID {client_id}")
        if len(failed_clients) > 5:
            print(f"   ... et {len(failed_clients) - 5} autres")

if __name__ == "__main__":
    test_all_client_ids()
