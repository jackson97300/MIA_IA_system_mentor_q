#!/usr/bin/env python3
"""
🔧 TEST DIFFÉRENTS CLIENT IDs
MIA_IA_SYSTEM - Trouver le bon Client ID pour IBKR
"""
import asyncio
import sys
import time
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.ibkr_connector import IBKRConnector

logger = get_logger(__name__)

async def test_client_id(client_id: int, timeout: int = 10) -> bool:
    """Test un Client ID spécifique"""
    
    print(f"🔍 Test Client ID: {client_id}")
    
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 4002,
        'ibkr_client_id': client_id,
        'connection_timeout': timeout
    }
    
    try:
        connector = IBKRConnector(config)
        start_time = time.time()
        
        success = await connector.connect()
        connection_time = time.time() - start_time
        
        if success:
            print(f"✅ Client ID {client_id}: RÉUSSI en {connection_time:.2f}s")
            
            # Test données marché
            market_data = await connector.get_market_data("ES")
            if market_data:
                print(f"   📊 Données ES: Prix={market_data.get('price', 'N/A')}")
            
            await connector.disconnect()
            return True
        else:
            print(f"❌ Client ID {client_id}: ÉCHOUÉ après {connection_time:.2f}s")
            return False
            
    except Exception as e:
        print(f"❌ Client ID {client_id}: ERREUR - {e}")
        return False

async def test_multiple_client_ids():
    """Test plusieurs Client IDs"""
    
    print("🔧 === TEST DIFFÉRENTS CLIENT IDs ===")
    print("🎯 Objectif: Trouver le bon Client ID pour IBKR")
    print()
    
    # Liste des Client IDs à tester (par ordre de probabilité de succès)
    client_ids = [
        999,   # Généralement fonctionne
        1,     # Standard
        2,     # Standard
        3,     # Standard
        100,   # Alternative
        200,   # Alternative
        500,   # Alternative
        1000,  # Alternative
        1234,  # Alternative
    ]
    
    successful_ids = []
    
    for client_id in client_ids:
        print(f"\n{'='*50}")
        success = await test_client_id(client_id)
        
        if success:
            successful_ids.append(client_id)
            print(f"🎉 Client ID {client_id} FONCTIONNE !")
            break  # Arrêter au premier succès
        else:
            print(f"❌ Client ID {client_id} échoué")
        
        # Pause entre les tests
        await asyncio.sleep(2)
    
    print(f"\n{'='*50}")
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    if successful_ids:
        best_client_id = successful_ids[0]
        print(f"✅ Client ID fonctionnel trouvé: {best_client_id}")
        print(f"🚀 Utilisez ce Client ID dans la configuration")
        
        # Mettre à jour la configuration
        print(f"\n🔧 Configuration recommandée:")
        print(f"config.ibkr_client_id = {best_client_id}")
        
        return best_client_id
    else:
        print("❌ Aucun Client ID fonctionnel trouvé")
        print("🔧 Actions recommandées:")
        print("   1. Vérifier que IB Gateway est démarré")
        print("   2. Vérifier la configuration API")
        print("   3. Redémarrer IB Gateway")
        print("   4. Tester avec d'autres Client IDs")
        
        return None

async def test_specific_client_id(client_id: int):
    """Test un Client ID spécifique avec plus de détails"""
    
    print(f"🔍 === TEST DÉTAILLÉ CLIENT ID {client_id} ===")
    
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 4002,
        'ibkr_client_id': client_id,
        'connection_timeout': 15
    }
    
    try:
        connector = IBKRConnector(config)
        
        print(f"🔗 Tentative connexion avec Client ID {client_id}...")
        success = await connector.connect()
        
        if success:
            print(f"✅ Connexion RÉUSSIE avec Client ID {client_id}")
            
            # Test données marché
            print("📊 Test données marché ES...")
            market_data = await connector.get_market_data("ES")
            
            if market_data:
                print("✅ Données marché récupérées")
                print(f"   📈 Prix: {market_data.get('price', 'N/A')}")
                print(f"   📊 Volume: {market_data.get('volume', 'N/A')}")
                print(f"   💰 Bid: {market_data.get('bid', 'N/A')}")
                print(f"   💰 Ask: {market_data.get('ask', 'N/A')}")
            else:
                print("❌ Erreur récupération données marché")
            
            # Test info compte
            print("\n📋 Test info compte...")
            account_info = await connector.get_account_info()
            
            if account_info:
                print("✅ Info compte récupérée")
                print(f"   🆔 Account ID: {account_info.get('account_id', 'N/A')}")
                print(f"   💰 Available Funds: {account_info.get('available_funds', 'N/A')}")
            else:
                print("❌ Erreur récupération info compte")
            
            await connector.disconnect()
            print(f"\n🔌 Déconnexion réussie")
            
            return True
        else:
            print(f"❌ Échec connexion avec Client ID {client_id}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        return False

if __name__ == "__main__":
    print("⚠️ TEST DIFFÉRENTS CLIENT IDs")
    print("🎯 Objectif: Trouver le bon Client ID pour IBKR")
    print()
    
    # Demander le mode de test
    print("🔍 Mode de test:")
    print("1. Test automatique (tous les Client IDs)")
    print("2. Test spécifique (Client ID 999)")
    print("3. Test spécifique (Client ID personnalisé)")
    
    choice = input("Choix (1/2/3): ").strip()
    
    if choice == "1":
        # Test automatique
        best_id = asyncio.run(test_multiple_client_ids())
        if best_id:
            print(f"\n🎉 Client ID {best_id} sélectionné !")
    elif choice == "2":
        # Test Client ID 999
        success = asyncio.run(test_specific_client_id(999))
        if success:
            print(f"\n🎉 Client ID 999 fonctionne !")
        else:
            print(f"\n❌ Client ID 999 échoué")
    elif choice == "3":
        # Test Client ID personnalisé
        try:
            custom_id = int(input("Client ID à tester: "))
            success = asyncio.run(test_specific_client_id(custom_id))
            if success:
                print(f"\n🎉 Client ID {custom_id} fonctionne !")
            else:
                print(f"\n❌ Client ID {custom_id} échoué")
        except ValueError:
            print("❌ Client ID invalide")
    else:
        print("❌ Choix invalide")
























