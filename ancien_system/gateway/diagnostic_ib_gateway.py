#!/usr/bin/env python3
"""
DIAGNOSTIC IB GATEWAY - MIA_IA_SYSTEM
Version: 1.0.0 - Diagnostic complet
"""

import socket
import time
from ib_insync import *

def test_port_connection():
    """Test si le port 4001 est accessible"""
    print("🔍 Test de connectivité port 4001...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 4001))
        sock.close()
        
        if result == 0:
            print("✅ Port 4001 accessible")
            return True
        else:
            print("❌ Port 4001 fermé ou inaccessible")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test port: {e}")
        return False

def test_ib_import():
    """Test import ib-insync"""
    print("🔍 Test import ib-insync...")
    
    try:
        from ib_insync import IB
        print("✅ ib-insync importé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur import ib-insync: {e}")
        return False

def test_ib_connection_basic():
    """Test connexion IB basique"""
    print("🔍 Test connexion IB basique...")
    
    ib = IB()
    
    try:
        print("🔄 Tentative connexion...")
        ib.connect('127.0.0.1', 4001, clientId=1, timeout=10)
        
        if ib.isConnected():
            print("✅ Connexion réussie!")
            ib.disconnect()
            return True
        else:
            print("❌ Connexion échouée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False

def test_ib_connection_detailed():
    """Test connexion IB détaillé avec logs"""
    print("🔍 Test connexion IB détaillé...")
    
    # Activer logs détaillés
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    ib = IB()
    
    try:
        print("🔄 Tentative connexion avec logs...")
        ib.connect('127.0.0.1', 4001, clientId=1, timeout=15)
        
        time.sleep(5)  # Attendre plus longtemps
        
        if ib.isConnected():
            print("✅ Connexion réussie!")
            
            # Test simple
            try:
                account = ib.accountSummary()
                print(f"✅ Données compte: {len(account)} éléments")
            except Exception as e:
                print(f"⚠️ Erreur données compte: {e}")
                
            ib.disconnect()
            return True
        else:
            print("❌ Connexion échouée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur connexion détaillée: {e}")
        return False

def main():
    """Diagnostic complet"""
    print("🚀 DIAGNOSTIC IB GATEWAY - MIA_IA_SYSTEM")
    print("=" * 50)
    
    # Test 1: Import
    test1 = test_ib_import()
    
    # Test 2: Port
    test2 = test_port_connection()
    
    # Test 3: Connexion basique
    test3 = test_ib_connection_basic()
    
    # Test 4: Connexion détaillée (si les autres réussissent)
    if test1 and test2 and test3:
        test4 = test_ib_connection_detailed()
    else:
        print("⚠️ Tests précédents échoués, skip test détaillé")
        test4 = False
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DIAGNOSTIC:")
    print(f"   Import ib-insync: {'✅' if test1 else '❌'}")
    print(f"   Port 4001 accessible: {'✅' if test2 else '❌'}")
    print(f"   Connexion basique: {'✅' if test3 else '❌'}")
    print(f"   Connexion détaillée: {'✅' if test4 else '❌'}")
    
    if test1 and test2 and test3 and test4:
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ Votre IB Gateway est prêt pour MIA_IA_SYSTEM")
    else:
        print("\n🔧 PROBLÈMES DÉTECTÉS:")
        if not test1:
            print("   - Réinstaller ib-insync: pip install ib-insync==0.9.86")
        if not test2:
            print("   - Vérifier que IB Gateway est ouvert et configuré")
        if not test3:
            print("   - Vérifier la configuration API dans IB Gateway")
        if not test4:
            print("   - Vérifier les permissions de données marché")

if __name__ == "__main__":
    main() 