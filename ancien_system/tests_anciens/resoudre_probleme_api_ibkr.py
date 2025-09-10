#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Resoudre Probleme API IBKR
Resout les problemes de connexion API IBKR
"""

import os
import sys
import socket
import subprocess
import time
from datetime import datetime

# Ajouter le repertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def resoudre_probleme_api_ibkr():
    """Resout les problemes d'API IBKR"""

    print("MIA_IA_SYSTEM - RESOLUTION PROBLEME API IBKR")
    print("=" * 60)
    print("Diagnostic et resolution probleme API IBKR")
    print("Objectif: Connexion API fonctionnelle")
    print("=" * 60)

    # 1. DIAGNOSTIC DETAILLE
    print("\n1. DIAGNOSTIC DETAILLE")
    print("=" * 40)

    # Vérifier processus IBKR
    print("Verification processus IBKR...")
    
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq TWS.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'TWS.exe' in result.stdout:
            print("SUCCES: TWS.exe en cours d'execution")
            tws_running = True
        else:
            print("ECHEC: TWS.exe non trouve")
            tws_running = False
            
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq ibgateway.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'ibgateway.exe' in result.stdout:
            print("SUCCES: ibgateway.exe en cours d'execution")
            gateway_running = True
        else:
            print("ECHEC: ibgateway.exe non trouve")
            gateway_running = False

    except Exception as e:
        print(f"ERREUR verification processus: {e}")
        tws_running = False
        gateway_running = False

    # 2. SOLUTIONS IMMEDIATES
    print("\n2. SOLUTIONS IMMEDIATES")
    print("=" * 40)

    if not tws_running and not gateway_running:
        print("PROBLEME: Aucune application IBKR en cours d'execution")
        print("\nSOLUTIONS:")
        print("1. Demarrer TWS (Trader Workstation)")
        print("2. Ou demarrer IB Gateway")
        print("3. Attendre que l'application soit completement chargee")
        return False

    # 3. VERIFICATION CONFIGURATION API
    print("\n3. VERIFICATION CONFIGURATION API")
    print("=" * 40)

    print("PROBLEME DETECTE: API non configuree ou desactivee")
    print("\nCONFIGURATION REQUISE:")
    
    if tws_running:
        print("POUR TWS:")
        print("1. Ouvrir TWS")
        print("2. Aller dans File > Global Configuration")
        print("3. API > Settings")
        print("4. Activer 'Enable ActiveX and Socket Clients'")
        print("5. Port: 7497")
        print("6. Activer 'Allow connections from localhost'")
        print("7. Redemarrer TWS")
    
    if gateway_running:
        print("POUR GATEWAY:")
        print("1. Ouvrir IB Gateway")
        print("2. Aller dans File > Global Configuration")
        print("3. API > Settings")
        print("4. Activer 'Enable ActiveX and Socket Clients'")
        print("5. Port: 4002")
        print("6. Activer 'Allow connections from localhost'")
        print("7. Redemarrer Gateway")

    # 4. TEST CONNEXION ALTERNATIVE
    print("\n4. TEST CONNEXION ALTERNATIVE")
    print("=" * 40)

    # Tester avec un timeout plus court
    ports_to_test = [(7497, "TWS"), (4002, "Gateway")]
    
    for port, name in ports_to_test:
        print(f"Test connexion {name} (port {port})...")
        
        try:
            # Test socket simple
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()

            if result == 0:
                print(f"SUCCES: Port {port} ouvert")
                
                # Créer configuration alternative
                config_alt = {
                    "port": port,
                    "application": name,
                    "timeout": 10,
                    "client_id": 2,  # Essayer un autre Client ID
                    "timestamp": datetime.now().isoformat()
                }
                
                os.makedirs("config", exist_ok=True)
                with open(f"config/connexion_alt_{name.lower()}.json", "w") as f:
                    import json
                    json.dump(config_alt, f, indent=2)
                
                print(f"Configuration alternative sauvegardee pour {name}")
                
            else:
                print(f"ECHEC: Port {port} ferme")

        except Exception as e:
            print(f"ERREUR test {name}: {e}")

    # 5. SCRIPT DE TEST RAPIDE
    print("\n5. SCRIPT DE TEST RAPIDE")
    print("=" * 40)

    script_test = '''#!/usr/bin/env python3
import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_api_rapide():
    try:
        from core.ibkr_connector import IBKRConnector
        
        # Test avec timeout court et Client ID different
        ibkr = IBKRConnector()
        ibkr.host = "127.0.0.1"
        ibkr.port = 7497  # ou 4002 pour Gateway
        ibkr.client_id = 2  # Client ID different
        ibkr.timeout = 10  # Timeout court
        
        print("Test connexion API rapide...")
        await ibkr.connect()
        
        if await ibkr.is_connected():
            print("SUCCES: API connectee!")
            await ibkr.disconnect()
            return True
        else:
            print("ECHEC: API non connectee")
            return False
            
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_api_rapide())
'''
    
    with open("test_api_rapide.py", "w") as f:
        f.write(script_test)
    
    print("Script de test rapide cree: test_api_rapide.py")

    # 6. RECOMMANDATIONS FINALES
    print("\n6. RECOMMANDATIONS FINALES")
    print("=" * 40)

    print("ETAPES DE RESOLUTION:")
    print("1. Verifier que TWS/Gateway est completement charge")
    print("2. Activer l'API dans la configuration")
    print("3. Redemarrer l'application IBKR")
    print("4. Executer: python test_api_rapide.py")
    print("5. Si echec, essayer un autre Client ID")
    print("6. Si toujours echec, redemarrer l'ordinateur")

    print("\nCONFIGURATION API CRITIQUE:")
    print("- Enable ActiveX and Socket Clients: OUI")
    print("- Allow connections from localhost: OUI")
    print("- Port: 7497 (TWS) ou 4002 (Gateway)")
    print("- Client ID: 1 ou 2")
    print("- Timeout: 10-15 secondes")

    return True

if __name__ == "__main__":
    resoudre_probleme_api_ibkr()
    
    print("\nRESUME:")
    print("=" * 40)
    print("Le probleme est probablement la configuration API")
    print("Suivez les etapes de configuration indiquees")
    print("Puis testez avec: python test_api_rapide.py")






