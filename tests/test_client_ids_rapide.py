#!/usr/bin/env python3
"""
TEST CLIENT IDs RAPIDE
MIA_IA_SYSTEM - Test rapide pour trouver un Client ID fonctionnel
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.ibkr_connector import IBKRConnector

async def test_client_id_rapide(client_id: int) -> bool:
    """Test rapide d'un Client ID (timeout 5s)"""
    
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 4002,
        'ibkr_client_id': client_id,
        'connection_timeout': 5,  # Timeout très court
        'simulation_mode': False,
        'require_real_data': True,
        'use_ib_insync': True
    }
    
    try:
        connector = IBKRConnector(config)
        success = await connector.connect()
        
        if success:
            await connector.disconnect()
            return True
        else:
            return False
            
    except Exception:
        return False

async def test_client_ids_rapide():
    """Test rapide de plusieurs Client IDs"""
    
    print("🔧 TEST CLIENT IDs RAPIDE - IB GATEWAY")
    print("=" * 40)
    
    # Client IDs prioritaires à tester
    client_ids = [
        1, 2, 3, 4, 5,  # Basiques
        10, 11, 12, 13, 14, 15,  # Intermédiaires
        100, 101, 102, 103, 104, 105,  # Élevés
        998, 999, 1000, 1001, 1002,  # Autour de 999
    ]
    
    print(f"📋 Test rapide de {len(client_ids)} Client IDs (timeout 5s chacun)...")
    print()
    
    for i, client_id in enumerate(client_ids, 1):
        print(f"[{i:2d}/{len(client_ids)}] Test Client ID {client_id:4d}...", end=" ")
        
        success = await test_client_id_rapide(client_id)
        
        if success:
            print("✅ SUCCÈS!")
            print(f"\n🎉 CLIENT ID TROUVÉ: {client_id}")
            print("=" * 40)
            
            # Créer configuration recommandée
            config_content = f"""# Configuration IBKR recommandée
config = {{
    'ibkr_host': '127.0.0.1',
    'ibkr_port': 4002,
    'ibkr_client_id': {client_id},
    'connection_timeout': 30,
    'simulation_mode': False,
    'require_real_data': True,
    'use_ib_insync': True
}}

# Utilisation:
# from core.ibkr_connector import IBKRConnector
# connector = IBKRConnector(config)
# await connector.connect()
"""
            
            with open('ibkr_config_reussi.py', 'w') as f:
                f.write(config_content)
            
            print(f"📄 Configuration sauvegardée: ibkr_config_reussi.py")
            print(f"✅ MIA_IA_SYSTEM peut maintenant utiliser Client ID {client_id}")
            return client_id
            
        else:
            print("❌ ÉCHEC")
        
        # Pause très courte
        await asyncio.sleep(0.5)
    
    print("\n❌ AUCUN CLIENT ID NE FONCTIONNE")
    print("🔧 Problème de configuration API IB Gateway")
    print("   - File → Global Configuration → API → Settings")
    print("   - Cocher 'Enable ActiveX and Socket Clients'")
    print("   - Redémarrer IB Gateway")
    return None

if __name__ == "__main__":
    print("🚀 Test rapide Client IDs...")
    result = asyncio.run(test_client_ids_rapide())
    
    if result:
        print(f"\n🎉 SUCCÈS: Client ID {result} fonctionne!")
        print("MIA_IA_SYSTEM peut maintenant se connecter à IB Gateway")
    else:
        print(f"\n🔧 PROBLÈME: Configuration API IB Gateway requise")
























