#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test Connexion Client ID Différent
Test connexion IBKR avec différents client IDs
"""

import os
import sys
import asyncio
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_client_id(client_id):
    """Test connexion avec un client ID spécifique"""
    try:
        from ib_insync import IB
        
        ib = IB()
        
        print(f"   Test client ID {client_id}...")
        
        try:
            await asyncio.wait_for(
                ib.connectAsync('127.0.0.1', 7497, clientId=client_id),
                timeout=8.0
            )
            
            if ib.isConnected():
                print(f"✅ SUCCÈS avec client ID {client_id}")
                print(f"   Status: {ib.connectionStatus()}")
                ib.disconnect()
                return True
            else:
                print(f"❌ ÉCHEC avec client ID {client_id}")
                return False
                
        except asyncio.TimeoutError:
            print(f"❌ TIMEOUT avec client ID {client_id}")
            return False
        except Exception as e:
            print(f"❌ ERREUR avec client ID {client_id}: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test client ID {client_id}: {e}")
        return False

async def main():
    """Fonction principale"""
    print("MIA_IA_SYSTEM - TEST CLIENT ID DIFFÉRENT")
    print("=" * 50)
    print(f"Test: {datetime.now()}")
    print("=" * 50)
    
    # Liste des client IDs à tester
    client_ids = [1, 2, 3, 10, 100, 999]
    
    print(f"\nTest de {len(client_ids)} client IDs différents...")
    print("(TWS peut bloquer les connexions multiples avec le même ID)")
    
    success_count = 0
    successful_ids = []
    
    for client_id in client_ids:
        success = await test_client_id(client_id)
        if success:
            success_count += 1
            successful_ids.append(client_id)
        await asyncio.sleep(1)  # Pause entre tests
    
    # Résultats
    print("\n" + "=" * 50)
    print("RÉSULTATS TEST CLIENT ID")
    print("=" * 50)
    
    print(f"Tests réussis: {success_count}/{len(client_ids)}")
    
    if successful_ids:
        print(f"✅ Client IDs fonctionnels: {successful_ids}")
        print(f"🚀 Recommandé: utiliser client ID {successful_ids[0]}")
        
        # Créer script de correction
        print("\n📝 Création script de correction...")
        create_correction_script(successful_ids[0])
        
    else:
        print("❌ Aucun client ID fonctionnel")
        print("\n🔧 PROBLÈMES POSSIBLES:")
        print("1. TWS n'est pas complètement démarré")
        print("2. Configuration API incorrecte")
        print("3. TWS en mode Read-Only")
        print("4. Problème réseau/firewall")
    
    print("=" * 50)

def create_correction_script(client_id):
    """Créer un script pour corriger le client ID"""
    script_content = f'''#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Correction Client ID
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
    print("📋 Prochaine étape: python lance_mia_ia_tws.py")

if __name__ == "__main__":
    corriger_client_id()
'''
    
    with open('corriger_client_id.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ Script créé: corriger_client_id.py")
    print("📋 Exécuter: python corriger_client_id.py")

if __name__ == "__main__":
    asyncio.run(main())

