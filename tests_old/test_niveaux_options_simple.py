#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test Simple Niveaux Options Réels
Test direct sans imports complexes
"""

import os
import sys
import asyncio
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_connexion_ibkr_simple():
    """Test simple connexion IBKR"""
    
    print("MIA_IA_SYSTEM - TEST SIMPLE CONNEXION IBKR")
    print("=" * 50)
    
    try:
        # Test import IBKR connector seulement
        from core.ibkr_connector import IBKRConnector
        print("✅ IBKRConnector importé avec succès")
        
        # Configuration
        config = {
            'ibkr_host': '127.0.0.1',
            'ibkr_port': 7497,
            'ibkr_client_id': 1,
            'simulation_mode': False,
            'require_real_data': True,
            'fallback_to_saved_data': False
        }
        
        # Création connector
        connector = IBKRConnector(config)
        print("✅ IBKRConnector créé")
        print(f"   Host: {connector.host}")
        print(f"   Port: {connector.port}")
        print(f"   Simulation mode: {connector.simulation_mode}")
        
        # Test connexion
        print("\nTentative connexion IBKR...")
        connected = await connector.connect()
        
        if connected:
            print("✅ IBKR connecté avec succès")
            print(f"   Status: {connector.connection_status}")
            print(f"   Is connected: {connector.is_connected_flag}")
            
            # Test récupération données SPX basique
            print("\nTest récupération données SPX...")
            try:
                # Test direct via IBKR connector
                if hasattr(connector, 'get_spx_options_data'):
                    spx_data = await connector.get_spx_options_data()
                    print("✅ Données SPX récupérées via connector")
                    print(f"   Source: {spx_data.get('data_source', 'N/A')}")
                    return spx_data.get('data_source') == 'ibkr_real'
                else:
                    print("⚠️ Méthode get_spx_options_data non disponible")
                    return False
                    
            except Exception as e:
                print(f"❌ Erreur récupération SPX: {e}")
                return False
        else:
            print("❌ Échec connexion IBKR")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

def main():
    """Fonction principale"""
    try:
        print(f"Début test: {datetime.now()}")
        
        # Exécuter test async
        success = asyncio.run(test_connexion_ibkr_simple())
        
        print("\n" + "=" * 50)
        print("RÉSULTATS TEST SIMPLE")
        print("=" * 50)
        
        if success:
            print("✅ SUCCÈS: Connexion IBKR et données SPX OK")
            print("✅ Système prêt pour test 2h")
        else:
            print("❌ ÉCHEC: Problème connexion ou données")
            print("🔧 Vérifier TWS et souscription SPX")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erreur exécution: {e}")

if __name__ == "__main__":
    main()


