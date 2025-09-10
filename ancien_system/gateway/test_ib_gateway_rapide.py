#!/usr/bin/env python3
"""
TEST RAPIDE IB GATEWAY
MIA_IA_SYSTEM - Test connexion immédiat
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.ibkr_connector import IBKRConnector

async def test_ib_gateway_rapide():
    """Test rapide de connexion IB Gateway"""
    
    print("🔧 TEST RAPIDE IB GATEWAY")
    print("=" * 40)
    
    # Configuration basée sur la documentation
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 4002,  # Port IB Gateway
        'ibkr_client_id': 999,  # Client ID fixe documenté
        'connection_timeout': 30,  # Timeout réduit
        'simulation_mode': False,
        'require_real_data': True,
        'use_ib_insync': True  # Utiliser ib_insync comme documenté
    }
    
    print(f"📍 Connexion à {config['ibkr_host']}:{config['ibkr_port']}")
    print(f"🆔 Client ID: {config['ibkr_client_id']}")
    print(f"⏱️ Timeout: {config['connection_timeout']}s")
    
    try:
        # Créer connecteur
        connector = IBKRConnector(config)
        
        # Test connexion
        print("\n🔗 Tentative connexion...")
        success = await connector.connect()
        
        if success:
            print("✅ CONNEXION RÉUSSIE!")
            
            # Test données marché
            print("\n📊 Test données marché...")
            market_data = await connector.get_market_data("ES")
            
            if market_data:
                print("✅ Données marché reçues:")
                print(f"   Prix: {market_data.get('price', 'N/A')}")
                print(f"   Volume: {market_data.get('volume', 'N/A')}")
                print(f"   Bid: {market_data.get('bid', 'N/A')}")
                print(f"   Ask: {market_data.get('ask', 'N/A')}")
            else:
                print("⚠️ Pas de données marché")
            
            # Déconnexion propre
            await connector.disconnect()
            print("\n✅ Test terminé avec succès")
            return True
            
        else:
            print("❌ ÉCHEC CONNEXION")
            print("Vérifier:")
            print("  - IB Gateway démarré sur port 4002")
            print("  - Client ID 999 disponible")
            print("  - Configuration API activée")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ib_gateway_rapide())
    
    if success:
        print("\n🎉 IB GATEWAY OPÉRATIONNEL!")
        print("Le système MIA_IA_SYSTEM peut maintenant se connecter")
    else:
        print("\n🔧 PROBLÈME DÉTECTÉ")
        print("Vérifier la configuration IB Gateway")
























