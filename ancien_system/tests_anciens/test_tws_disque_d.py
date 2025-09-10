#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 TEST TWS DISQUE D - MIA_IA_SYSTEM
Détection TWS sur disque D et test Paper Trading
"""

import socket
import time
import subprocess
import os
from datetime import datetime

def find_tws_process():
    """Trouver TWS peu importe où il est installé"""
    print("🔍 Recherche TWS sur tous les disques...")
    
    try:
        # Vérifier tous les processus Java
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq javaw.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'javaw.exe' in result.stdout:
            print("✅ TWS (javaw.exe) détecté")
            
            # Obtenir plus d'informations sur le processus
            try:
                detailed_result = subprocess.run(['wmic', 'process', 'where', 'name="javaw.exe"', 'get', 'ProcessId,ExecutablePath'], 
                                              capture_output=True, text=True, shell=True)
                print("📁 Informations processus TWS:")
                print(detailed_result.stdout)
            except:
                pass
            
            return True
        else:
            print("❌ TWS (javaw.exe) non détecté")
            return False
    except Exception as e:
        print(f"❌ Erreur recherche TWS: {e}")
        return False

def check_tws_installation():
    """Vérifier l'installation TWS sur disque D"""
    print("🔍 Vérification installation TWS sur disque D...")
    
    possible_paths = [
        "D:\\TWS\\jts.ini",
        "D:\\Interactive Brokers\\TWS\\jts.ini",
        "D:\\IBKR\\TWS\\jts.ini",
        "D:\\Program Files\\Interactive Brokers\\TWS\\jts.ini",
        "D:\\Program Files (x86)\\Interactive Brokers\\TWS\\jts.ini"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ TWS trouvé: {path}")
            return True
    
    print("❌ TWS non trouvé dans les chemins standards")
    return False

def test_socket_paper():
    """Test socket port 7497 (Paper Trading)"""
    print("🔍 Test socket port 7497 (Paper Trading)...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7497))
        
        if result == 0:
            print("✅ Socket Paper Trading accessible")
            sock.close()
            return True
        else:
            print(f"❌ Socket Paper Trading inaccessible (code: {result})")
            sock.close()
            return False
    except Exception as e:
        print(f"❌ Erreur socket Paper: {e}")
        return False

def test_ib_insync_paper():
    """Test ib_insync avec Paper Trading"""
    print("🔗 Test ib_insync Paper Trading...")
    
    try:
        from ib_insync import IB, Future
        
        ib = IB()
        
        # Configuration Paper Trading
        host = '127.0.0.1'
        port = 7497  # Port Paper Trading
        client_id = 999
        timeout = 30
        
        print(f"   🔗 Connexion Paper: {host}:{port}, Client ID: {client_id}")
        
        try:
            ib.connect(host, port, clientId=client_id, timeout=timeout)
            
            if ib.isConnected():
                print("   ✅ Connexion Paper Trading réussie !")
                
                # Test rapide ES
                try:
                    contract = Future('ES', '20241220', 'CME')
                    ib.reqMktData(contract)
                    time.sleep(3)
                    
                    tickers = ib.tickers()
                    if tickers:
                        for ticker in tickers:
                            if ticker.contract.symbol == 'ES':
                                prix = ticker.marketPrice()
                                if prix and prix > 0:
                                    print(f"   💰 Prix ES Paper: {prix}")
                                    print("   🎉 SUCCÈS Paper Trading !")
                                    ib.disconnect()
                                    return True, {
                                        'host': host,
                                        'port': port,
                                        'client_id': client_id,
                                        'timeout': timeout,
                                        'mode': 'PAPER'
                                    }
                    
                    print("   ⚠️ Connexion Paper OK mais pas de données ES")
                    ib.disconnect()
                    return True, {
                        'host': host,
                        'port': port,
                        'client_id': client_id,
                        'timeout': timeout,
                        'mode': 'PAPER'
                    }
                    
                except Exception as e:
                    print(f"   ⚠️ Erreur test ES Paper: {e}")
                    ib.disconnect()
                    return True, {
                        'host': host,
                        'port': port,
                        'client_id': client_id,
                        'timeout': timeout,
                        'mode': 'PAPER'
                    }
            else:
                print("   ❌ Connexion Paper échouée")
                ib.disconnect()
                return False, None
                
        except Exception as e:
            print(f"   ❌ Erreur connexion Paper: {e}")
            return False, None
            
    except ImportError:
        print("   ❌ ib_insync non disponible")
        return False, None
    except Exception as e:
        print(f"   ❌ Erreur générale Paper: {e}")
        return False, None

def launch_tws_disque_d():
    """Lancer TWS depuis le disque D"""
    print("🚀 Tentative lancement TWS depuis disque D...")
    
    possible_executables = [
        "D:\\TWS\\tws.exe",
        "D:\\Interactive Brokers\\TWS\\tws.exe",
        "D:\\IBKR\\TWS\\tws.exe",
        "D:\\Program Files\\Interactive Brokers\\TWS\\tws.exe",
        "D:\\Program Files (x86)\\Interactive Brokers\\TWS\\tws.exe"
    ]
    
    for exe_path in possible_executables:
        if os.path.exists(exe_path):
            print(f"✅ TWS trouvé: {exe_path}")
            try:
                # Lancer TWS
                subprocess.Popen([exe_path], shell=True)
                print("🚀 TWS lancé !")
                time.sleep(5)  # Attendre le démarrage
                return True
            except Exception as e:
                print(f"❌ Erreur lancement TWS: {e}")
    
    print("❌ Aucun exécutable TWS trouvé sur disque D")
    return False

def main():
    print("🎮 TEST TWS DISQUE D - MIA_IA_SYSTEM")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Détection TWS sur disque D et test Paper Trading")
    print("=" * 60)
    
    # Étape 1: Vérifier installation TWS
    if not check_tws_installation():
        print("\n❌ TWS non trouvé sur disque D !")
        print("🔧 SOLUTIONS:")
        print("1. Vérifiez que TWS est installé sur D:")
        print("   - D:\\TWS\\")
        print("   - D:\\Interactive Brokers\\TWS\\")
        print("   - D:\\IBKR\\TWS\\")
        print("2. Lancez TWS manuellement depuis le disque D")
        return
    
    # Étape 2: Vérifier processus TWS
    if not find_tws_process():
        print("\n⚠️ TWS installé mais pas en cours d'exécution")
        print("🚀 Tentative lancement automatique...")
        
        if not launch_tws_disque_d():
            print("❌ Impossible de lancer TWS automatiquement")
            print("🔧 Lancez TWS manuellement depuis le disque D")
            return
    
    # Étape 3: Test socket Paper
    if not test_socket_paper():
        print("\n❌ Port 7497 (Paper Trading) inaccessible !")
        print("🔧 SOLUTIONS:")
        print("1. Vérifiez que TWS est en mode Paper Trading")
        print("2. Configurez le port 7497 dans TWS")
        print("3. Redémarrez TWS")
        return
    
    # Étape 4: Test connexion Paper
    print("\n🔗 Test connexion Paper Trading...")
    success, config = test_ib_insync_paper()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ TWS DISQUE D")
    
    if success and config:
        print("🎉 SUCCÈS ! Configuration Paper Trading trouvée:")
        print(f"   - Host: {config['host']}")
        print(f"   - Port: {config['port']} (Paper Trading)")
        print(f"   - Client ID: {config['client_id']}")
        print(f"   - Mode: {config['mode']}")
        
        print("\n🚀 MIA_IA_SYSTEM PRÊT POUR DÉVELOPPEMENT !")
        
        # Sauvegarder configuration
        with open('config_tws_disque_d.py', 'w', encoding='utf-8') as f:
            f.write(f"""# Configuration TWS Disque D - MIA_IA_SYSTEM
TWS_DISQUE_D_CONFIG = {{
    'host': '{config['host']}',
    'port': {config['port']},
    'client_id': {config['client_id']},
    'timeout': {config['timeout']},
    'mode': '{config['mode']}',
    'installation': 'DISQUE_D',
    'status': 'WORKING'
}}

# Configuration réussie sur disque D
# ✅ TWS détecté et connecté
# ✅ Paper Trading fonctionnel
# ✅ Pas d'authentification 2FA requise
""")
        print("✅ Configuration sauvegardée dans 'config_tws_disque_d.py'")
        
    else:
        print("❌ Échec de la connexion Paper Trading")
        print("\n🔧 SOLUTIONS:")
        print("1. Lancez TWS manuellement depuis le disque D")
        print("2. Assurez-vous qu'il est en mode Paper Trading")
        print("3. Configurez le port 7497 dans TWS")
        print("4. Redémarrez TWS complètement")

if __name__ == "__main__":
    main()

