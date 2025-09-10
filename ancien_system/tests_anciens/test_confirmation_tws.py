#!/usr/bin/env python3
"""
TEST CONFIRMATION TWS
MIA_IA_SYSTEM - Confirmation connexion TWS
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.ibkr_connector import IBKRConnector

async def test_confirmation_tws():
    """Test de confirmation TWS"""
    
    print("🎯 CONFIRMATION TWS - MIA_IA_SYSTEM")
    print("=" * 40)
    
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 7497,  # TWS
        'ibkr_client_id': 1,  # Client ID qui fonctionne
        'connection_timeout': 20,
        'simulation_mode': False,
        'require_real_data': True,
        'use_ib_insync': True
    }
    
    print(f"📍 Connexion: {config['ibkr_host']}:{config['ibkr_port']}")
    print(f"🆔 Client ID: {config['ibkr_client_id']}")
    print(f"⏱️ Timeout: {config['connection_timeout']}s")
    
    try:
        connector = IBKRConnector(config)
        
        print("\n🔗 Test connexion...")
        success = await connector.connect()
        
        if success:
            print("✅ CONNEXION TWS RÉUSSIE!")
            
            # Test données marché
            print("\n📊 Test données ES...")
            market_data = await connector.get_market_data("ES")
            
            if market_data:
                print("✅ Données ES reçues:")
                print(f"   Prix: {market_data.get('price', 'N/A')}")
                print(f"   Volume: {market_data.get('volume', 'N/A')}")
                print(f"   Bid: {market_data.get('bid', 'N/A')}")
                print(f"   Ask: {market_data.get('ask', 'N/A')}")
            else:
                print("⚠️ Pas de données ES")
            
            # Déconnexion
            await connector.disconnect()
            print("\n🎉 CONFIRMATION RÉUSSIE!")
            return True
            
        else:
            print("❌ ÉCHEC CONNEXION")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Test confirmation TWS...")
    success = asyncio.run(test_confirmation_tws())
    
    if success:
        print("\n🎉 TWS OPÉRATIONNEL!")
        print("\n📋 CONFIGURATION FINALE:")
        print("   - TWS (port 7497)")
        print("   - Client ID: 1")
        print("   - API activée")
        print("\n✅ MIA_IA_SYSTEM peut utiliser TWS!")
    else:
        print("\n🔧 Problème persistant")
        print("Vérifier la configuration TWS")
























