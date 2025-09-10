#!/usr/bin/env python3
"""
TEST CONNEXION TWS - CLIENT ID DIFFÉRENT
MIA_IA_SYSTEM - Test connexion via TWS avec Client ID alternatif
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.ibkr_connector import IBKRConnector

async def test_tws_different_client_id():
    """Test connexion via TWS avec Client ID différent"""
    
    print("🔧 TEST TWS - CLIENT ID ALTERNATIF")
    print("=" * 40)
    
    # Test plusieurs Client IDs
    client_ids = [1, 2, 3, 100, 200, 500, 1000, 2000]
    
    for client_id in client_ids:
        print(f"\n🆔 Test Client ID: {client_id}")
        print("-" * 30)
        
        config = {
            'ibkr_host': '127.0.0.1',
            'ibkr_port': 7497,  # Port TWS
            'ibkr_client_id': client_id,
            'connection_timeout': 15,  # Timeout court
            'simulation_mode': False,
            'require_real_data': True,
            'use_ib_insync': True
        }
        
        try:
            # Créer connecteur
            connector = IBKRConnector(config)
            
            # Test connexion rapide
            print(f"🔗 Tentative connexion...")
            success = await connector.connect()
            
            if success:
                print(f"✅ SUCCÈS avec Client ID {client_id}!")
                
                # Test données marché rapide
                market_data = await connector.get_market_data("ES")
                if market_data:
                    print(f"📊 Données ES: {market_data.get('price', 'N/A')}")
                
                # Déconnexion
                await connector.disconnect()
                print(f"🎉 Client ID {client_id} FONCTIONNE!")
                return client_id
                
            else:
                print(f"❌ Échec Client ID {client_id}")
                
        except Exception as e:
            print(f"❌ Erreur Client ID {client_id}: {e}")
            continue
    
    print("\n❌ AUCUN CLIENT ID FONCTIONNE")
    return None

if __name__ == "__main__":
    print("🚀 Test Client IDs TWS...")
    working_client_id = asyncio.run(test_tws_different_client_id())
    
    if working_client_id:
        print(f"\n🎉 SOLUTION TROUVÉE!")
        print(f"Client ID fonctionnel: {working_client_id}")
        print(f"\n📋 Configuration recommandée:")
        print(f"   - TWS (port 7497)")
        print(f"   - Client ID: {working_client_id}")
        print(f"   - Remplacer 999 par {working_client_id}")
    else:
        print("\n🔧 PROBLÈME PERSISTANT")
        print("Vérifier:")
        print("  - TWS redémarré après config API")
        print("  - Firewall Windows")
        print("  - Antivirus")
























