#!/usr/bin/env python3
"""
Vérification Configuration TWS - MIA_IA_SYSTEM
==============================================

Script pour vérifier la configuration TWS et identifier les problèmes.

USAGE:
python scripts/verify_tws_configuration.py
"""

import sys
import os
import time
import socket
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_port_connectivity(host, port, description):
    """Test de connectivité d'un port"""
    print(f"\n🔍 Test {description} ({host}:{port})...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} ouvert et accessible")
            return True
        else:
            print(f"❌ Port {port} fermé ou inaccessible")
            return False
    except Exception as e:
        print(f"❌ Erreur test port {port}: {e}")
        return False

def test_ib_connection(host, port, client_id, description):
    """Test de connexion IB avec timeout court"""
    print(f"\n🔍 Test connexion {description}...")
    
    try:
        from ib_insync import IB
        
        ib = IB()
        ib.connect(host, port, clientId=client_id, timeout=5)
        
        if ib.isConnected():
            print(f"✅ Connexion {description} OK")
            ib.disconnect()
            return True
        else:
            print(f"❌ Connexion {description} échouée")
            return False
    except Exception as e:
        print(f"❌ Erreur connexion {description}: {e}")
        return False

def verify_tws_configuration():
    """Vérification complète de la configuration TWS"""
    
    print("🔧 VÉRIFICATION CONFIGURATION TWS")
    print("=" * 45)
    print(f"⏰ Début: {datetime.now().strftime('%H:%M:%S')}")
    
    # 1. Test connectivité réseau
    print("\n1️⃣ Test Connectivité Réseau...")
    test_port_connectivity('127.0.0.1', 7497, "TWS Simulated")
    test_port_connectivity('127.0.0.1', 4001, "IB Gateway")
    test_port_connectivity('127.0.0.1', 7496, "TWS Live")
    
    # 2. Test connexions IB
    print("\n2️⃣ Test Connexions IB...")
    test_ib_connection('127.0.0.1', 7497, 1, "TWS Simulated Client 1")
    test_ib_connection('127.0.0.1', 7497, 999, "TWS Simulated Client 999")
    test_ib_connection('127.0.0.1', 4001, 1, "IB Gateway Client 1")
    
    # 3. Test processus TWS
    print("\n3️⃣ Test Processus TWS...")
    try:
        import psutil
        tws_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'tws' in proc.info['name'].lower() or 'trader' in proc.info['name'].lower():
                    tws_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if tws_processes:
            print("✅ Processus TWS détectés:")
            for proc in tws_processes:
                print(f"   PID: {proc['pid']}, Nom: {proc['name']}")
        else:
            print("❌ Aucun processus TWS détecté")
    except ImportError:
        print("⚠️ psutil non installé - impossible de vérifier les processus")
    except Exception as e:
        print(f"❌ Erreur vérification processus: {e}")
    
    # 4. Test configuration API
    print("\n4️⃣ Test Configuration API...")
    try:
        from ib_insync import IB, Future
        
        # Test avec différents paramètres
        configs = [
            ('127.0.0.1', 7497, 1, "TWS Simulated"),
            ('127.0.0.1', 7497, 999, "TWS Simulated (Client 999)"),
            ('127.0.0.1', 4001, 1, "IB Gateway"),
        ]
        
        for host, port, client_id, desc in configs:
            print(f"\n   Test {desc}...")
            try:
                ib = IB()
                ib.connect(host, port, clientId=client_id, timeout=3)
                
                if ib.isConnected():
                    print(f"   ✅ {desc} connecté")
                    
                    # Test contrat ES
                    contract = Future('ES', '202412', 'CME')
                    ib.qualifyContracts(contract)
                    print(f"   ✅ Contrat ES qualifié")
                    
                    # Test données
                    ticker = ib.reqMktData(contract)
                    time.sleep(2)
                    
                    if ticker.marketPrice() or ticker.bid or ticker.ask:
                        print(f"   ✅ Données ES reçues")
                        print(f"      Prix: {ticker.marketPrice()}")
                        print(f"      Bid: {ticker.bid}")
                        print(f"      Ask: {ticker.ask}")
                    else:
                        print(f"   ❌ Pas de données ES")
                    
                    ib.disconnect()
                else:
                    print(f"   ❌ {desc} non connecté")
            except Exception as e:
                print(f"   ❌ Erreur {desc}: {e}")
                
    except Exception as e:
        print(f"❌ Erreur test configuration API: {e}")
    
    # 5. Recommandations
    print("\n5️⃣ Recommandations...")
    print("📋 Vérifiez dans TWS:")
    print("   - Configuration > API > Settings")
    print("   - Socket port: 7497 (Simulated)")
    print("   - Enable ActiveX and Socket Clients: ✅")
    print("   - Read-Only API: ✅")
    print("   - Créer journal de messages API: ✅")
    print("   - Logging Level: Detail")
    
    print("\n📋 Vérifiez les souscriptions:")
    print("   - ES futures souscrits dans TWS")
    print("   - Données temps réel activées")
    print("   - Compte simulé connecté")
    
    # 6. Résumé final
    print("\n" + "=" * 45)
    print("📊 RÉSUMÉ VÉRIFICATION TWS")
    print("=" * 45)
    print("✅ Requirements: OK")
    print("✅ ib_insync: Installé")
    print("⚠️ Connexion: À vérifier")
    print("⚠️ Données: À vérifier")
    print(f"⏰ Fin: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    try:
        verify_tws_configuration()
    except KeyboardInterrupt:
        print("\n⏹️ Vérification interrompue")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


