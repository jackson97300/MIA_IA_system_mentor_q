#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Diagnostic Connexion IBKR
Diagnostic spécifique du problème de connexion IBKR
"""

import os
import sys
import asyncio
import socket
import subprocess
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verifier_tws_demarre():
    """Vérifier si TWS est démarré"""
    print("1. VÉRIFICATION TWS DÉMARRÉ")
    print("-" * 40)
    
    try:
        # Vérifier processus TWS
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq TWS.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'TWS.exe' in result.stdout:
            print("✅ TWS.exe détecté dans les processus")
            return True
        else:
            print("❌ TWS.exe non détecté")
            print("   TWS n'est pas démarré")
            return False
            
    except Exception as e:
        print(f"❌ Erreur vérification TWS: {e}")
        return False

def verifier_port_7497():
    """Vérifier si le port 7497 est ouvert"""
    print("\n2. VÉRIFICATION PORT 7497")
    print("-" * 40)
    
    try:
        # Test connexion socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7497))
        sock.close()
        
        if result == 0:
            print("✅ Port 7497 ouvert et accessible")
            return True
        else:
            print("❌ Port 7497 fermé ou inaccessible")
            print(f"   Code erreur: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test port: {e}")
        return False

def verifier_netstat():
    """Vérifier les connexions réseau"""
    print("\n3. VÉRIFICATION CONNEXIONS RÉSEAU")
    print("-" * 40)
    
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, shell=True)
        
        if '127.0.0.1:7497' in result.stdout:
            print("✅ Port 7497 détecté dans netstat")
            return True
        else:
            print("❌ Port 7497 non détecté dans netstat")
            return False
            
    except Exception as e:
        print(f"❌ Erreur netstat: {e}")
        return False

async def test_connexion_ibkr_direct():
    """Test connexion IBKR directe"""
    print("\n4. TEST CONNEXION IBKR DIRECTE")
    print("-" * 40)
    
    try:
        # Test import ib_insync
        try:
            from ib_insync import IB
            print("✅ ib_insync disponible")
        except ImportError:
            print("❌ ib_insync non installé")
            return False
        
        # Test connexion
        ib = IB()
        print("   Tentative connexion...")
        
        try:
            await asyncio.wait_for(
                ib.connectAsync('127.0.0.1', 7497, clientId=1),
                timeout=10.0
            )
            
            if ib.isConnected():
                print("✅ Connexion IBKR réussie")
                print(f"   Status: {ib.connectionStatus()}")
                
                # Test récupération données
                print("\n   Test récupération données...")
                try:
                    # Test contrat ES
                    from ib_insync import Future
                    es_contract = Future('ES', '202503', 'CME')
                    
                    # Demander données
                    ib.reqMktData(es_contract)
                    await asyncio.sleep(2)
                    
                    if es_contract.marketPrice():
                        print(f"✅ Données ES récupérées: {es_contract.marketPrice()}")
                        ib.disconnect()
                        return True
                    else:
                        print("❌ Aucune donnée ES récupérée")
                        ib.disconnect()
                        return False
                        
                except Exception as e:
                    print(f"❌ Erreur récupération données: {e}")
                    ib.disconnect()
                    return False
            else:
                print("❌ Connexion IBKR échouée")
                return False
                
        except asyncio.TimeoutError:
            print("❌ Timeout connexion IBKR (10s)")
            return False
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test IBKR: {e}")
        return False

def analyser_configuration_tws():
    """Analyser configuration TWS"""
    print("\n5. ANALYSE CONFIGURATION TWS")
    print("-" * 40)
    
    # Vérifier fichiers de configuration TWS
    tws_config_paths = [
        os.path.expanduser("~/Jts"),
        "C:/Jts",
        "D:/Jts"
    ]
    
    for path in tws_config_paths:
        if os.path.exists(path):
            print(f"✅ Répertoire TWS trouvé: {path}")
            
            # Vérifier jts.ini
            jts_ini = os.path.join(path, "jts.ini")
            if os.path.exists(jts_ini):
                print(f"   ✅ jts.ini trouvé")
                try:
                    with open(jts_ini, 'r') as f:
                        content = f.read()
                        if 'SocketPort=7497' in content:
                            print("   ✅ Port 7497 configuré dans jts.ini")
                        else:
                            print("   ⚠️ Port 7497 non trouvé dans jts.ini")
                except Exception as e:
                    print(f"   ❌ Erreur lecture jts.ini: {e}")
            else:
                print(f"   ❌ jts.ini non trouvé")
            
            return True
    
    print("❌ Aucun répertoire TWS trouvé")
    return False

def corriger_connexion_ibkr():
    """Correction connexion IBKR"""
    print("\n6. CORRECTION CONNEXION IBKR")
    print("-" * 40)
    
    corrections = []
    
    # 1. Vérifier TWS démarré
    if not verifier_tws_demarre():
        corrections.append("1. Démarrer TWS")
    
    # 2. Vérifier port
    if not verifier_port_7497():
        corrections.append("2. Vérifier configuration TWS port 7497")
    
    # 3. Vérifier configuration
    if not analyser_configuration_tws():
        corrections.append("3. Vérifier installation TWS")
    
    if corrections:
        print("🔧 CORRECTIONS NÉCESSAIRES:")
        for correction in corrections:
            print(f"   - {correction}")
    else:
        print("✅ Aucune correction nécessaire")
    
    return len(corrections) == 0

async def main():
    """Fonction principale"""
    try:
        print("MIA_IA_SYSTEM - DIAGNOSTIC CONNEXION IBKR")
        print("=" * 60)
        print(f"Diagnostic: {datetime.now()}")
        print("=" * 60)
        
        # Diagnostic complet
        tws_ok = verifier_tws_demarre()
        port_ok = verifier_port_7497()
        netstat_ok = verifier_netstat()
        config_ok = analyser_configuration_tws()
        
        # Test connexion si conditions remplies
        connexion_ok = False
        if tws_ok and port_ok:
            connexion_ok = await test_connexion_ibkr_direct()
        
        # Résultats
        print("\n" + "=" * 60)
        print("RÉSULTATS DIAGNOSTIC CONNEXION IBKR")
        print("=" * 60)
        
        print(f"TWS démarré: {'✅' if tws_ok else '❌'}")
        print(f"Port 7497 ouvert: {'✅' if port_ok else '❌'}")
        print(f"Netstat OK: {'✅' if netstat_ok else '❌'}")
        print(f"Configuration TWS: {'✅' if config_ok else '❌'}")
        print(f"Connexion IBKR: {'✅' if connexion_ok else '❌'}")
        
        if connexion_ok:
            print("\n✅ SUCCÈS: Connexion IBKR fonctionnelle")
            print("✅ Système prêt pour test 2h")
            print("🚀 Lancement recommandé: python lance_mia_ia_tws.py")
        else:
            print("\n❌ ÉCHEC: Connexion IBKR non fonctionnelle")
            print("\n🔧 ACTIONS CORRECTIVES:")
            
            if not tws_ok:
                print("1. Démarrer TWS (Trader Workstation)")
                print("   - Vérifier TWS installé")
                print("   - Lancer TWS depuis le menu Démarrer")
            
            if not port_ok:
                print("2. Configurer TWS pour API")
                print("   - Dans TWS: Edit > Global Configuration")
                print("   - API > Settings > Enable ActiveX and Socket Clients")
                print("   - Socket port: 7497")
                print("   - Redémarrer TWS")
            
            if not config_ok:
                print("3. Vérifier installation TWS")
                print("   - Réinstaller TWS si nécessaire")
                print("   - Vérifier permissions")
            
            print("\n4. Après corrections:")
            print("   - Redémarrer TWS")
            print("   - Relancer ce diagnostic")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erreur diagnostic: {e}")

if __name__ == "__main__":
    asyncio.run(main())


