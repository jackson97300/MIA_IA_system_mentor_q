#!/usr/bin/env python3
"""
test_tws_config.py

Test simple de la configuration TWS
"""

import socket
import time

def test_port_connectivity():
    """Test de connectivité du port TWS"""
    
    print("🔍 Test de connectivité TWS")
    print("=" * 50)
    
    host = "127.0.0.1"
    port = 7496
    
    print(f"🔗 Test connexion TCP à {host}:{port}")
    
    try:
        # Test de connexion TCP basique
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        
        result = sock.connect_ex((host, port))
        
        if result == 0:
            print("✅ Port 7496 accessible - TWS écoute")
            sock.close()
            return True
        else:
            print(f"❌ Port 7496 fermé (code: {result})")
            print("💡 Vérifiez que TWS est lancé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False

def check_tws_status():
    """Vérification du statut TWS"""
    
    print("\n📋 Checklist TWS Configuration:")
    print("=" * 50)
    
    print("1. ✅ TWS lancé et connecté au marché")
    print("2. ⚠️  Edit → Global Configuration → API → Settings")
    print("3. ⚠️  'Enable ActiveX and Socket EClients' = ACTIVÉ")
    print("4. ⚠️  'Socket Port' = 7496")
    print("5. ⚠️  'Allow connections from localhost' = ACTIVÉ")
    print("6. ⚠️  'Read-Only API' = DÉSACTIVÉ")
    print("7. ⚠️  Pas de popup de sécurité en attente")
    print("8. ⚠️  TWS connecté au marché (pas en mode déconnecté)")
    
    print("\n🔧 Actions à faire dans TWS:")
    print("- Ouvrir TWS")
    print("- Aller dans Edit → Global Configuration")
    print("- Section API → Settings")
    print("- Cocher 'Enable ActiveX and Socket EClients'")
    print("- Vérifier port 7496")
    print("- Cocher 'Allow connections from localhost'")
    print("- Appliquer et redémarrer TWS si nécessaire")

def main():
    """Fonction principale"""
    print("🚀 Diagnostic TWS Configuration")
    print()
    
    # Test 1: Connectivité port
    port_ok = test_port_connectivity()
    
    # Test 2: Checklist configuration
    check_tws_status()
    
    print("\n" + "=" * 50)
    
    if port_ok:
        print("✅ Port accessible - Vérifiez la configuration API")
    else:
        print("❌ Port fermé - TWS non lancé ou configuration incorrecte")
    
    print("\n💡 Après configuration, relancez le test de connexion")

if __name__ == "__main__":
    main()
