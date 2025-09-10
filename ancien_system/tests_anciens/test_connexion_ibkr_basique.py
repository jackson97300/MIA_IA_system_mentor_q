#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test Connexion IBKR Basique
Test minimal de connexion IBKR
"""

import os
import sys
import asyncio
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_connexion_basique():
    """Test basique connexion IBKR"""
    
    print("MIA_IA_SYSTEM - TEST CONNEXION IBKR BASIQUE")
    print("=" * 50)
    print(f"Début: {datetime.now()}")
    
    try:
        # Test import simple
        print("\n1. Test import IBKRConnector...")
        from core.ibkr_connector import IBKRConnector
        print("✅ Import réussi")
        
        # Configuration minimale
        print("\n2. Configuration...")
        config = {
            'ibkr_host': '127.0.0.1',
            'ibkr_port': 7497,
            'ibkr_client_id': 1,
            'simulation_mode': False,
            'require_real_data': True,
            'fallback_to_saved_data': False
        }
        print(f"   Config: {config}")
        
        # Création connector
        print("\n3. Création connector...")
        connector = IBKRConnector(config)
        print("✅ Connector créé")
        print(f"   Host: {connector.host}")
        print(f"   Port: {connector.port}")
        print(f"   Simulation: {connector.simulation_mode}")
        
        # Test connexion
        print("\n4. Test connexion...")
        print("   Tentative connexion...")
        
        # Timeout de 10 secondes
        try:
            connected = await asyncio.wait_for(connector.connect(), timeout=10.0)
            print(f"   Résultat: {connected}")
            
            if connected:
                print("✅ Connexion réussie")
                print(f"   Status: {connector.connection_status}")
                print(f"   Connected: {connector.is_connected_flag}")
                return True
            else:
                print("❌ Connexion échouée")
                return False
                
        except asyncio.TimeoutError:
            print("❌ Timeout connexion (10s)")
            return False
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    try:
        print("Démarrage test connexion basique...")
        
        # Exécuter test
        success = asyncio.run(test_connexion_basique())
        
        print("\n" + "=" * 50)
        print("RÉSULTATS TEST BASIQUE")
        print("=" * 50)
        
        if success:
            print("✅ SUCCÈS: Connexion IBKR OK")
            print("✅ TWS accessible sur port 7497")
            print("✅ Système prêt pour test 2h")
        else:
            print("❌ ÉCHEC: Problème connexion")
            print("🔧 Vérifications nécessaires:")
            print("   - TWS démarré et connecté")
            print("   - Port 7497 ouvert")
            print("   - Souscription données activée")
            print("   - Configuration IBKR correcte")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erreur exécution: {e}")

if __name__ == "__main__":
    main()


