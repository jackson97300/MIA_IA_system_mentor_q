#!/usr/bin/env python3
"""
TEST IB GATEWAY DEBUG DÉTAILLÉ - MIA_IA_SYSTEM
Version: 1.0.0 - Debug complet
"""

import socket
import time
import logging
from ib_insync import *

# Configuration logging détaillé
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_socket_connection():
    """Test connexion socket brute"""
    print("🔍 Test connexion socket brute...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        print("🔄 Tentative connexion socket...")
        sock.connect(('127.0.0.1', 4001))
        print("✅ Connexion socket réussie!")
        sock.close()
        return True
    except Exception as e:
        print(f"❌ Erreur socket: {e}")
        return False

def test_ib_connection_step_by_step():
    """Test connexion IB étape par étape"""
    print("🔍 Test connexion IB étape par étape...")
    
    ib = IB()
    
    try:
        print("1️⃣ Initialisation IB...")
        print(f"   - IB object créé: {ib}")
        
        print("2️⃣ Tentative connexion...")
        print("   - Host: 127.0.0.1")
        print("   - Port: 4001")
        print("   - Client ID: 1")
        print("   - Timeout: 20 secondes")
        
        # Connexion avec timeout plus long
        ib.connect('127.0.0.1', 4001, clientId=1, timeout=20)
        
        print("3️⃣ Attente connexion...")
        time.sleep(5)
        
        print("4️⃣ Vérification statut...")
        if ib.isConnected():
            print("✅ Connexion réussie!")
            
            print("5️⃣ Test données compte...")
            try:
                account = ib.accountSummary()
                print(f"✅ Données compte: {len(account)} éléments")
                return True
            except Exception as e:
                print(f"⚠️ Erreur données compte: {e}")
                return True  # Connexion OK même si pas de données
        else:
            print("❌ Connexion échouée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur détaillée: {e}")
        print(f"   Type d'erreur: {type(e).__name__}")
        return False
    finally:
        if ib.isConnected():
            print("🔌 Déconnexion...")
            ib.disconnect()

def test_ib_with_different_client_id():
    """Test avec différents client IDs"""
    print("🔍 Test avec différents client IDs...")
    
    for client_id in [1, 2, 3, 999]:
        print(f"   Test client ID: {client_id}")
        ib = IB()
        
        try:
            ib.connect('127.0.0.1', 4001, clientId=client_id, timeout=10)
            time.sleep(3)
            
            if ib.isConnected():
                print(f"✅ Connexion réussie avec client ID {client_id}!")
                ib.disconnect()
                return True
            else:
                print(f"❌ Échec avec client ID {client_id}")
                ib.disconnect()
                
        except Exception as e:
            print(f"❌ Erreur client ID {client_id}: {e}")
            ib.disconnect()
    
    return False

def main():
    """Test complet avec debug"""
    print("🚀 TEST IB GATEWAY DEBUG DÉTAILLÉ - MIA_IA_SYSTEM")
    print("=" * 60)
    
    # Test 1: Socket brut
    test1 = test_socket_connection()
    
    # Test 2: Connexion IB détaillée
    test2 = test_ib_connection_step_by_step()
    
    # Test 3: Différents client IDs
    if not test2:
        test3 = test_ib_with_different_client_id()
    else:
        test3 = True
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DEBUG:")
    print(f"   Socket brut: {'✅' if test1 else '❌'}")
    print(f"   Connexion IB détaillée: {'✅' if test2 else '❌'}")
    print(f"   Client ID alternatif: {'✅' if test3 else '❌'}")
    
    if test1 and (test2 or test3):
        print("\n🎉 CONNEXION RÉUSSIE!")
        print("✅ Votre IB Gateway est prêt pour MIA_IA_SYSTEM")
    else:
        print("\n🔧 PROBLÈMES IDENTIFIÉS:")
        if not test1:
            print("   - Problème réseau/port")
        if not test2 and not test3:
            print("   - Problème configuration API")
            print("   - Vérifiez les paramètres dans IB Gateway")

if __name__ == "__main__":
    main() 