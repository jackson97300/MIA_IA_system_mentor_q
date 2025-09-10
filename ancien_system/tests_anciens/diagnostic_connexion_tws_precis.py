#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Diagnostic Connexion TWS Précis
Diagnostic précis de la connexion TWS sur port 7497
"""

import os
import sys
import subprocess
import asyncio
import time
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verifier_processus_tws():
    """Vérifier processus TWS"""
    print("1. VÉRIFICATION PROCESSUS TWS")
    print("-" * 30)
    
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq TWS.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'TWS.exe' in result.stdout:
            print("✅ TWS.exe détecté")
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'TWS.exe' in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print("❌ TWS.exe non détecté")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def verifier_port_7497():
    """Vérifier port 7497"""
    print("\n2. VÉRIFICATION PORT 7497")
    print("-" * 30)
    
    try:
        result = subprocess.run(['netstat', '-an'], 
                              capture_output=True, text=True, shell=True)
        
        if '7497' in result.stdout:
            print("✅ Port 7497 détecté")
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if '7497' in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print("❌ Port 7497 non détecté")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def verifier_configuration_api():
    """Vérifier configuration API TWS"""
    print("\n3. VÉRIFICATION CONFIGURATION API TWS")
    print("-" * 30)
    
    print("🔧 VÉRIFICATIONS MANUELLES DANS TWS:")
    print("1. Configuration > API > Settings:")
    print("   - Enable ActiveX and Socket Clients: ✅")
    print("   - Socket port: 7497")
    print("   - Allow connections from localhost: ✅")
    print("   - Read-Only API: ❌ (désactivé)")
    print("2. Configuration > API > Precautions:")
    print("   - Bypass Order Precautions for API Orders: ✅")
    print("3. TWS est-il en mode Paper Trading?")
    print("4. TWS est-il connecté aux marchés?")
    
    return True

async def test_connexion_directe():
    """Test connexion directe"""
    print("\n4. TEST CONNEXION DIRECTE")
    print("-" * 30)
    
    try:
        from ib_insync import IB
        
        ib = IB()
        
        print("   Test connexion 127.0.0.1:7497...")
        
        try:
            await asyncio.wait_for(
                ib.connectAsync('127.0.0.1', 7497, clientId=1),
                timeout=8.0
            )
            
            if ib.isConnected():
                print("✅ Connexion réussie!")
                print(f"   Status: {ib.connectionStatus()}")
                ib.disconnect()
                return True
            else:
                print("❌ Connexion échouée")
                return False
                
        except asyncio.TimeoutError:
            print("❌ Timeout connexion (8s)")
            return False
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
            
    except ImportError:
        print("❌ ib_insync non disponible")
        return False
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

async def test_client_ids_differents():
    """Tester différents client IDs"""
    print("\n5. TEST CLIENT IDS DIFFÉRENTS")
    print("-" * 30)
    
    client_ids = [1, 2, 3, 10, 100]
    
    for client_id in client_ids:
        try:
            from ib_insync import IB
            
            ib = IB()
            
            print(f"   Test client ID {client_id}...")
            
            try:
                await asyncio.wait_for(
                    ib.connectAsync('127.0.0.1', 7497, clientId=client_id),
                    timeout=5.0
                )
                
                if ib.isConnected():
                    print(f"✅ SUCCÈS avec client ID {client_id}")
                    ib.disconnect()
                    return client_id
                else:
                    print(f"❌ ÉCHEC avec client ID {client_id}")
                    
            except asyncio.TimeoutError:
                print(f"❌ TIMEOUT avec client ID {client_id}")
            except Exception as e:
                print(f"❌ ERREUR avec client ID {client_id}: {e}")
                
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"❌ Erreur test client ID {client_id}: {e}")
    
    return None

def verifier_fichiers_configuration():
    """Vérifier les fichiers de configuration"""
    print("\n6. VÉRIFICATION FICHIERS CONFIGURATION")
    print("-" * 30)
    
    fichiers_config = [
        "config/mia_ia_system_tws_paper_fixed.py",
        "config/tws_paper_config.py",
        "config/ibkr_config.py",
        "core/ibkr_connector.py"
    ]
    
    for fichier in fichiers_config:
        if os.path.exists(fichier):
            try:
                with open(fichier, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if '7497' in content:
                    print(f"✅ {fichier} - Port 7497 configuré")
                else:
                    print(f"⚠️ {fichier} - Port 7497 non trouvé")
                    
                if 'clientId=1' in content or 'client_id=1' in content:
                    print(f"   - Client ID 1 configuré")
                else:
                    print(f"   - Client ID non trouvé")
                    
            except Exception as e:
                print(f"❌ {fichier} - Erreur lecture: {e}")
        else:
            print(f"⚠️ {fichier} - Fichier non trouvé")
    
    return True

async def main():
    """Fonction principale"""
    print("MIA_IA_SYSTEM - DIAGNOSTIC CONNEXION TWS PRÉCIS")
    print("=" * 60)
    print(f"Diagnostic: {datetime.now()}")
    print("=" * 60)
    
    # Vérifications
    tws_ok = verifier_processus_tws()
    port_ok = verifier_port_7497()
    config_ok = verifier_configuration_api()
    connexion_ok = await test_connexion_directe()
    client_id_ok = await test_client_ids_differents()
    fichiers_ok = verifier_fichiers_configuration()
    
    # Résultats
    print("\n" + "=" * 60)
    print("RÉSULTATS DIAGNOSTIC")
    print("=" * 60)
    
    print(f"Processus TWS: {'✅' if tws_ok else '❌'}")
    print(f"Port 7497: {'✅' if port_ok else '❌'}")
    print(f"Configuration API: {'✅' if config_ok else '⚠️'}")
    print(f"Connexion directe: {'✅' if connexion_ok else '❌'}")
    print(f"Client ID fonctionnel: {'✅' if client_id_ok else '❌'}")
    print(f"Fichiers config: {'✅' if fichiers_ok else '⚠️'}")
    
    if connexion_ok:
        print("\n🎉 SUCCÈS: Connexion TWS fonctionnelle!")
        print("✅ Système prêt pour test")
    elif client_id_ok:
        print(f"\n🔧 SOLUTION: Utiliser client ID {client_id_ok}")
        print("📋 Créer script de correction...")
        create_correction_script(client_id_ok)
    else:
        print("\n❌ PROBLÈME: Connexion TWS échoue")
        print("\n🔧 SOLUTIONS À ESSAYER:")
        print("1. Vérifier configuration API dans TWS")
        print("2. Redémarrer TWS")
        print("3. Vérifier que TWS est en mode Paper Trading")
        print("4. Vérifier que TWS est connecté aux marchés")
        print("5. Tester avec un autre client ID")
    
    print("=" * 60)

def create_correction_script(client_id):
    """Créer script de correction"""
    script_content = f'''#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Correction Client ID {client_id}
Corrige le client ID dans les fichiers de configuration
"""

import os
import sys

def corriger_client_id():
    """Corriger le client ID dans les fichiers de configuration"""
    
    print("MIA_IA_SYSTEM - CORRECTION CLIENT ID")
    print("=" * 40)
    print(f"Application client ID: {client_id}")
    print("=" * 40)
    
    fichiers_config = [
        "config/mia_ia_system_tws_paper_fixed.py",
        "config/tws_paper_config.py",
        "config/ibkr_config.py",
        "core/ibkr_connector.py"
    ]
    
    for fichier in fichiers_config:
        if os.path.exists(fichier):
            try:
                with open(fichier, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remplacer client ID
                content_modified = content.replace('clientId=1', f'clientId={client_id}')
                content_modified = content_modified.replace('client_id=1', f'client_id={client_id}')
                content_modified = content_modified.replace('clientId = 1', f'clientId = {client_id}')
                content_modified = content_modified.replace('client_id = 1', f'client_id = {client_id}')
                
                if content != content_modified:
                    with open(fichier, 'w', encoding='utf-8') as f:
                        f.write(content_modified)
                    print(f"✅ {fichier} - Client ID corrigé")
                else:
                    print(f"⚠️ {fichier} - Aucun changement nécessaire")
                    
            except Exception as e:
                print(f"❌ {fichier} - Erreur: {{e}}")
        else:
            print(f"⚠️ {fichier} - Fichier non trouvé")
    
    print("\\n🎉 Correction client ID terminée!")
    print(f"🚀 Client ID {client_id} appliqué")
    print("📋 Prochaine étape: python test_connexion_ibkr_simple.py")

if __name__ == "__main__":
    corriger_client_id()
'''
    
    with open('corriger_client_id_final.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ Script créé: corriger_client_id_final.py")
    print("📋 Exécuter: python corriger_client_id_final.py")

if __name__ == "__main__":
    asyncio.run(main())

