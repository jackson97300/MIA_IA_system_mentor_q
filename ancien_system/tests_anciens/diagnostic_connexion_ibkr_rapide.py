#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Diagnostic Connexion IBKR Rapide
Diagnostique et corrige rapidement les problèmes de connexion IBKR
"""

import os
import sys
import socket
import subprocess
import time
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def diagnostic_connexion_ibkr_rapide():
    """Diagnostique rapide de la connexion IBKR"""

    print("MIA_IA_SYSTEM - DIAGNOSTIC CONNEXION IBKR RAPIDE")
    print("=" * 60)
    print("🔍 Diagnostic rapide connexion IBKR")
    print("🎯 Objectif: Résoudre timeout connexion")
    print("=" * 60)

    # 1. VÉRIFICATION PROCESSUS IBKR
    print("\n🔧 1. VÉRIFICATION PROCESSUS IBKR")
    print("=" * 40)

    try:
        # Vérifier si TWS ou Gateway sont en cours d'exécution
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq TWS.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'TWS.exe' in result.stdout:
            print("✅ TWS.exe en cours d'exécution")
        else:
            print("❌ TWS.exe non trouvé")
            
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq ibgateway.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'ibgateway.exe' in result.stdout:
            print("✅ ibgateway.exe en cours d'exécution")
        else:
            print("❌ ibgateway.exe non trouvé")

    except Exception as e:
        print(f"❌ Erreur vérification processus: {e}")

    # 2. TEST PORTS IBKR
    print("\n🔧 2. TEST PORTS IBKR")
    print("=" * 40)

    ports_to_test = [
        (7497, "TWS"),
        (4002, "Gateway"),
        (7496, "TWS Paper"),
        (4001, "Gateway Paper")
    ]

    active_ports = []
    
    for port, name in ports_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()

            if result == 0:
                print(f"✅ {name} connecté (port {port})")
                active_ports.append((port, name))
            else:
                print(f"❌ {name} non connecté (port {port})")

        except Exception as e:
            print(f"❌ Erreur test {name}: {e}")

    # 3. RECOMMANDATIONS RAPIDES
    print("\n🔧 3. RECOMMANDATIONS RAPIDES")
    print("=" * 40)

    if not active_ports:
        print("❌ AUCUN PORT IBKR ACTIF")
        print("\n💡 SOLUTIONS IMMÉDIATES:")
        print("   1. Démarrer TWS (Trader Workstation)")
        print("   2. Ou démarrer IB Gateway")
        print("   3. Vérifier que l'API est activée")
        print("   4. Vérifier les paramètres de connexion")
        
        print("\n🔧 DÉMARRAGE RAPIDE TWS:")
        print("   1. Ouvrir TWS")
        print("   2. Aller dans File > Global Configuration")
        print("   3. API > Settings")
        print("   4. Activer 'Enable ActiveX and Socket Clients'")
        print("   5. Port: 7497 (ou 4002 pour Gateway)")
        print("   6. Redémarrer TWS")
        
        return False
    else:
        print(f"✅ {len(active_ports)} port(s) IBKR actif(s)")
        for port, name in active_ports:
            print(f"   - {name} (port {port})")

    # 4. TEST CONNEXION RAPIDE
    print("\n🔧 4. TEST CONNEXION RAPIDE")
    print("=" * 40)

    if active_ports:
        # Utiliser le premier port actif
        test_port, test_name = active_ports[0]
        
        try:
            # Test simple avec socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect(('127.0.0.1', test_port))
            sock.close()
            print(f"✅ Connexion socket réussie sur {test_name} (port {test_port})")
            
            # Créer configuration rapide
            config_rapide = {
                "port_actif": test_port,
                "nom_application": test_name,
                "timestamp": datetime.now().isoformat(),
                "status": "connecte"
            }
            
            os.makedirs("config", exist_ok=True)
            with open("config/connexion_ibkr_rapide.json", "w") as f:
                import json
                json.dump(config_rapide, f, indent=2)
            
            print("✅ Configuration rapide sauvegardée")
            return True
            
        except Exception as e:
            print(f"❌ Échec connexion socket: {e}")
            return False

    return False

def corriger_connexion_rapide():
    """Corrige rapidement la connexion IBKR"""

    print("\n🔧 CORRECTION RAPIDE CONNEXION")
    print("=" * 40)

    # Vérifier si une configuration rapide existe
    config_file = "config/connexion_ibkr_rapide.json"
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                import json
                config = json.load(f)
            
            port = config.get('port_actif', 7497)
            nom = config.get('nom_application', 'TWS')
            
            print(f"✅ Configuration trouvée: {nom} (port {port})")
            
            # Créer script de lancement rapide
            script_rapide = f"""#!/usr/bin/env python3
import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def lance_rapide():
    try:
        from core.ibkr_connector import IBKRConnector
        
        # Configuration rapide
        ibkr = IBKRConnector()
        ibkr.host = "127.0.0.1"
        ibkr.port = {port}
        ibkr.client_id = 1
        ibkr.timeout = 15  # Timeout réduit
        
        print(f"🔗 Connexion rapide {nom} (port {port})...")
        await ibkr.connect()
        
        if await ibkr.is_connected():
            print("✅ Connexion réussie!")
            
            # Test données rapide
            data = await ibkr.get_market_data("ES")
            if data:
                print("✅ Données ES récupérées")
                print(f"   Prix: {{data.get('last', 'N/A')}}")
                print(f"   Volume: {{data.get('volume', 'N/A')}}")
            else:
                print("⚠️ Aucune donnée ES")
            
            await ibkr.disconnect()
            return True
        else:
            print("❌ Échec connexion")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {{e}}")
        return False

if __name__ == "__main__":
    asyncio.run(lance_rapide())
"""
            
            with open("test_connexion_rapide.py", "w") as f:
                f.write(script_rapide)
            
            print("✅ Script de test rapide créé")
            print("💡 Exécutez: python test_connexion_rapide.py")
            
        except Exception as e:
            print(f"❌ Erreur configuration: {e}")
    else:
        print("❌ Aucune configuration rapide trouvée")
        print("💡 Exécutez d'abord le diagnostic")

if __name__ == "__main__":
    success = diagnostic_connexion_ibkr_rapide()
    if success:
        corriger_connexion_rapide()
    
    print("\n💡 RÉSUMÉ DIAGNOSTIC")
    print("=" * 40)
    if success:
        print("✅ Diagnostic réussi - Connexion possible")
        print("🚀 Prêt pour lancement système")
    else:
        print("❌ Problèmes détectés - Correction nécessaire")
        print("💡 Vérifiez TWS/Gateway avant relance")






