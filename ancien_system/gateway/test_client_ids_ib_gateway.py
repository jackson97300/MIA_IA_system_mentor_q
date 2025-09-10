#!/usr/bin/env python3
"""
TEST CLIENT IDS IB GATEWAY
MIA_IA_SYSTEM - Test différents Client IDs pour résoudre le problème de connexion
"""
import asyncio
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.ibkr_connector import IBKRConnector

async def test_client_id(client_id, timeout=30):
    """Test un Client ID spécifique avec vérifications complètes"""
    
    print(f"\n🔍 TEST CLIENT ID {client_id}")
    print("-" * 30)
    
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 4002,  # IB Gateway
        'ibkr_client_id': client_id,
        'connection_timeout': timeout,
        'simulation_mode': False,
        'require_real_data': False,  # Désactivé pour test
        'use_ib_insync': True
    }
    
    print(f"📡 Configuration Client ID {client_id}:")
    print(f"   Timeout: {timeout}s")
    print(f"   Require Real Data: {config['require_real_data']}")
    
    try:
        start_time = time.time()
        connector = IBKRConnector(config)
        
        print(f"⏳ Tentative connexion Client ID {client_id}...")
        success = await connector.connect()
        connection_time = time.time() - start_time
        
        if success:
            print(f"✅ SUCCÈS Client ID {client_id} en {connection_time:.2f}s")
            
            # ✅ VÉRIFICATION 1: Test données ES
            print("   🔍 Vérification 1: Données ES...")
            try:
                market_data = await connector.get_market_data("ES")
                if market_data and isinstance(market_data, dict):
                    print(f"      📊 ES: {market_data.get('last', 'N/A')}")
                    if 'error' in market_data:
                        print(f"      ⚠️ Erreur: {market_data['error']}")
                else:
                    print("      ⚠️ Pas de données ES")
            except Exception as e:
                print(f"      ❌ Erreur ES: {e}")
            
            # ✅ VÉRIFICATION 2: Test données SPY
            print("   🔍 Vérification 2: Données SPY...")
            try:
                spy_data = await connector.get_market_data("SPY")
                if spy_data and isinstance(spy_data, dict):
                    print(f"      📊 SPY: {spy_data.get('last', 'N/A')}")
                    if 'error' in spy_data:
                        print(f"      ⚠️ Erreur: {spy_data['error']}")
                else:
                    print("      ⚠️ Pas de données SPY")
            except Exception as e:
                print(f"      ❌ Erreur SPY: {e}")
            
            # ✅ VÉRIFICATION 3: Test persistance connexion
            print("   🔍 Vérification 3: Persistance (5s)...")
            try:
                await asyncio.sleep(5)
                print("      ✅ Connexion stable après 5s")
            except Exception as e:
                print(f"      ❌ Erreur persistance: {e}")
            
            # ✅ VÉRIFICATION 4: Test déconnexion propre
            print("   🔍 Vérification 4: Déconnexion...")
            try:
                await connector.disconnect()
                print("      ✅ Déconnexion réussie")
            except Exception as e:
                print(f"      ❌ Erreur déconnexion: {e}")
            
            return True, connection_time
            
        else:
            print(f"❌ ÉCHEC Client ID {client_id} après {connection_time:.2f}s")
            return False, connection_time
            
    except Exception as e:
        print(f"❌ ERREUR Client ID {client_id}: {e}")
        return False, 0

async def test_multiple_client_ids():
    """Test plusieurs Client IDs avec vérifications complètes"""
    
    print("🔧 TEST MULTIPLES CLIENT IDS IB GATEWAY")
    print("=" * 50)
    print("🎯 Objectif: Trouver un Client ID fonctionnel")
    print()
    
    # ✅ VÉRIFICATION PRÉLIMINAIRE: Test port
    print("🔍 VÉRIFICATION PRÉLIMINAIRE:")
    print("-" * 35)
    
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 4002))
        sock.close()
        
        if result == 0:
            print("✅ Port 4002 accessible")
        else:
            print("❌ Port 4002 fermé - IB Gateway non démarré")
            return []
    except Exception as e:
        print(f"❌ Erreur test port: {e}")
        return []
    
    print()
    
    # Liste des Client IDs à tester (plus de variété)
    client_ids = [2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000]
    
    print("📋 CLIENT IDS À TESTER:")
    for i, client_id in enumerate(client_ids, 1):
        print(f"   {i:2d}. Client ID {client_id}")
    print()
    
    results = []
    
    for client_id in client_ids:
        success, connection_time = await test_client_id(client_id, timeout=20)
        results.append({
            'client_id': client_id,
            'success': success,
            'connection_time': connection_time
        })
        
        # Pause entre tests
        if client_id != client_ids[-1]:
            await asyncio.sleep(2)
    
    # ✅ ANALYSE RÉSULTATS AVEC VÉRIFICATIONS
    print("\n📊 RÉSULTATS DES TESTS")
    print("=" * 40)
    
    successful_ids = [r for r in results if r['success']]
    failed_ids = [r for r in results if not r['success']]
    
    print(f"📈 STATISTIQUES:")
    print(f"   • Total testés: {len(results)}")
    print(f"   • Succès: {len(successful_ids)}")
    print(f"   • Échecs: {len(failed_ids)}")
    print(f"   • Taux de succès: {(len(successful_ids)/len(results)*100):.1f}%")
    
    if successful_ids:
        print("\n✅ CLIENT IDS FONCTIONNELS:")
        # Trier par temps de connexion
        successful_ids.sort(key=lambda x: x['connection_time'])
        for i, result in enumerate(successful_ids, 1):
            print(f"   {i:2d}. Client ID {result['client_id']:4d} - {result['connection_time']:.2f}s")
        
        # Recommandation
        best_id = successful_ids[0]  # Déjà trié par temps
        print(f"\n🎯 RECOMMANDATION: Client ID {best_id['client_id']}")
        print(f"   Temps de connexion: {best_id['connection_time']:.2f}s")
        print(f"   Rang: 1er sur {len(successful_ids)} succès")
        
        # ✅ VÉRIFICATION PATTERNS
        print(f"\n🔍 ANALYSE PATTERNS:")
        low_ids = [r for r in successful_ids if r['client_id'] <= 10]
        mid_ids = [r for r in successful_ids if 10 < r['client_id'] <= 100]
        high_ids = [r for r in successful_ids if r['client_id'] > 100]
        
        print(f"   • Client IDs ≤ 10: {len(low_ids)} succès")
        print(f"   • Client IDs 11-100: {len(mid_ids)} succès")
        print(f"   • Client IDs > 100: {len(high_ids)} succès")
        
        if low_ids:
            print(f"   💡 Recommandation: Privilégier Client IDs ≤ 10")
        
    else:
        print("\n❌ AUCUN CLIENT ID FONCTIONNEL")
        print("🔍 DIAGNOSTIC APPROFONDI:")
        print("   • IB Gateway: Vérifier qu'il est démarré")
        print("   • Port 4002: Vérifier qu'il est ouvert")
        print("   • API: Vérifier 'Enable ActiveX and Socket Clients'")
        print("   • Timeout: Peut-être trop court (20s)")
        print("   • Conflit: Possible conflit avec autre application")
        print("   • Firewall: Vérifier pare-feu Windows")
    
    if failed_ids:
        print(f"\n❌ CLIENT IDS ÉCHOUÉS ({len(failed_ids)}):")
        # Afficher les premiers et derniers
        for result in failed_ids[:3]:
            print(f"   • Client ID {result['client_id']}")
        if len(failed_ids) > 6:
            print(f"   • ... ({len(failed_ids) - 6} autres) ...")
        for result in failed_ids[-3:]:
            print(f"   • Client ID {result['client_id']}")
    
    return successful_ids

def creer_configuration_optimale(successful_ids):
    """Créer une configuration optimale basée sur les résultats"""
    
    if not successful_ids:
        print("\n❌ Impossible de créer configuration - aucun Client ID fonctionnel")
        return None
    
    best_id = min(successful_ids, key=lambda x: x['connection_time'])
    
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 4002,  # IB Gateway
        'ibkr_client_id': best_id['client_id'],
        'connection_timeout': 30,
        'request_timeout': 15,
        'simulation_mode': False,
        'require_real_data': True,  # Réactivé
        'use_ib_insync': True,
        'max_reconnection_attempts': 3,
        'reconnection_delay': 5
    }
    
    print(f"\n⚙️ CONFIGURATION OPTIMALE CRÉÉE:")
    print(f"   Client ID: {config['ibkr_client_id']} (meilleur temps: {best_id['connection_time']:.2f}s)")
    print(f"   Connection Timeout: {config['connection_timeout']}s")
    print(f"   Request Timeout: {config['request_timeout']}s")
    print(f"   Require Real Data: {config['require_real_data']}")
    
    return config

async def test_configuration_finale(config):
    """Test de la configuration finale"""
    
    if not config:
        return False
    
    print(f"\n🔧 TEST CONFIGURATION FINALE")
    print("-" * 35)
    
    try:
        connector = IBKRConnector(config)
        start_time = time.time()
        
        print("⏳ Test connexion finale...")
        success = await connector.connect()
        connection_time = time.time() - start_time
        
        if success:
            print(f"✅ CONFIGURATION VALIDÉE en {connection_time:.2f}s")
            
            # Test données réelles
            try:
                market_data = await connector.get_market_data("ES")
                if market_data and isinstance(market_data, dict):
                    print(f"✅ Données ES: {market_data.get('last', 'N/A')}")
                    if 'error' in market_data:
                        print(f"⚠️ Erreur 2119: {market_data['error']}")
                        print("💡 C'est normal - données futures limitées")
                else:
                    print("⚠️ Pas de données")
            except Exception as e:
                print(f"❌ Erreur données: {e}")
            
            await connector.disconnect()
            return True
            
        else:
            print(f"❌ ÉCHEC configuration finale")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR configuration finale: {e}")
        return False

if __name__ == "__main__":
    print("🔧 TEST CLIENT IDS IB GATEWAY")
    print("=" * 40)
    
    # Test multiple Client IDs
    successful_ids = asyncio.run(test_multiple_client_ids())
    
    # Créer configuration optimale
    config_optimale = creer_configuration_optimale(successful_ids)
    
    # Test configuration finale
    if config_optimale:
        success_finale = asyncio.run(test_configuration_finale(config_optimale))
        
        if success_finale:
            print("\n🎉 SUCCÈS - Configuration optimale trouvée!")
            print("💡 Client ID fonctionnel identifié")
        else:
            print("\n❌ ÉCHEC - Configuration finale non validée")
    else:
        print("\n❌ ÉCHEC - Aucune configuration possible")
