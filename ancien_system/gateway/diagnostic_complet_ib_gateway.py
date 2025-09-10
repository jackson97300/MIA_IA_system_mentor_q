#!/usr/bin/env python3
"""
DIAGNOSTIC COMPLET IB GATEWAY
MIA_IA_SYSTEM - Analyse complète des problèmes de connexion
"""
import asyncio
import sys
import time
import socket
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.ibkr_connector import IBKRConnector

async def diagnostic_complet():
    """Diagnostic complet IB Gateway"""
    
    print("🔍 DIAGNOSTIC COMPLET IB GATEWAY")
    print("=" * 50)
    
    # 1. Test connectivité port
    print("\n1️⃣ TEST CONNECTIVITÉ PORT 4002")
    print("-" * 30)
    test_port_connectivite()
    
    # 2. Test connexion simple
    print("\n2️⃣ TEST CONNEXION SIMPLE")
    print("-" * 25)
    await test_connexion_simple()
    
    # 3. Test persistance connexion
    print("\n3️⃣ TEST PERSISTANCE CONNEXION")
    print("-" * 30)
    await test_persistance_connexion()
    
    # 4. Test récupération données
    print("\n4️⃣ TEST RÉCUPÉRATION DONNÉES")
    print("-" * 30)
    await test_recuperation_donnees()
    
    # 5. Analyse erreurs
    print("\n5️⃣ ANALYSE ERREURS")
    print("-" * 20)
    analyser_erreurs()

def test_port_connectivite():
    """Test connectivité port 4002"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 4002))
        sock.close()
        
        if result == 0:
            print("✅ Port 4002 accessible")
        else:
            print("❌ Port 4002 fermé")
            print("🔍 Vérifier IB Gateway démarré")
    except Exception as e:
        print(f"❌ Erreur test port: {e}")

async def test_connexion_simple():
    """Test connexion simple sans données"""
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 4002,
        'ibkr_client_id': 1,
        'connection_timeout': 10,
        'simulation_mode': False,
        'require_real_data': False,  # Pas de données réelles
        'use_ib_insync': True
    }
    
    try:
        connector = IBKRConnector(config)
        success = await connector.connect()
        
        if success:
            print("✅ Connexion simple réussie")
            await connector.disconnect()
            return True
        else:
            print("❌ Échec connexion simple")
            return False
            
    except Exception as e:
        print(f"❌ Erreur connexion simple: {e}")
        return False

async def test_persistance_connexion():
    """Test persistance de la connexion"""
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 4002,
        'ibkr_client_id': 1,
        'connection_timeout': 30,
        'simulation_mode': False,
        'require_real_data': False,
        'use_ib_insync': True
    }
    
    try:
        connector = IBKRConnector(config)
        success = await connector.connect()
        
        if success:
            print("✅ Connexion établie")
            
            # Test persistance 30 secondes
            for i in range(6):
                if connector.is_connected_flag:
                    print(f"   ✅ Connexion maintenue ({i*5}s)")
                    await asyncio.sleep(5)
                else:
                    print(f"   ❌ Connexion perdue à {i*5}s")
                    break
            
            await connector.disconnect()
            return True
        else:
            print("❌ Échec connexion")
            return False
            
    except Exception as e:
        print(f"❌ Erreur persistance: {e}")
        return False

async def test_recuperation_donnees():
    """Test récupération données avec gestion d'erreur"""
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 4002,
        'ibkr_client_id': 1,
        'connection_timeout': 30,
        'simulation_mode': False,
        'require_real_data': True,
        'use_ib_insync': True
    }
    
    try:
        connector = IBKRConnector(config)
        success = await connector.connect()
        
        if success:
            print("✅ Connexion établie")
            
            # Test récupération données avec try/catch
            try:
                print("📊 Tentative récupération données...")
                market_data = await connector.get_market_data("ES")
                
                if market_data:
                    print("✅ Données récupérées avec succès")
                    print(f"   Symbol: {getattr(market_data, 'symbol', 'N/A')}")
                    print(f"   Prix: {getattr(market_data, 'close', 'N/A')}")
                else:
                    print("⚠️ Pas de données récupérées")
                    
            except AttributeError as e:
                print(f"❌ Erreur attribut: {e}")
                print("🔍 Problème dans la structure des données")
            except Exception as e:
                print(f"❌ Erreur récupération: {e}")
            
            await connector.disconnect()
            return True
        else:
            print("❌ Échec connexion")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test données: {e}")
        return False

def analyser_erreurs():
    """Analyse des erreurs identifiées"""
    print("🔍 ANALYSE ERREURS IDENTIFIÉES:")
    print("-" * 35)
    
    print("1️⃣ IBKR Error 2119:")
    print("   - Problème: Connexion aux données de marché")
    print("   - Cause: Abonnement CME Real-Time manquant")
    print("   - Solution: Vérifier abonnement IBKR")
    
    print("\n2️⃣ Erreur 'dict' object:")
    print("   - Problème: Structure de données incorrecte")
    print("   - Cause: get_market_data retourne dict au lieu d'objet")
    print("   - Solution: Corriger le code de récupération")
    
    print("\n3️⃣ Déconnexion automatique:")
    print("   - Problème: API se déconnecte après quelques secondes")
    print("   - Cause: Timeout ou problème de maintenance")
    print("   - Solution: Augmenter timeout et vérifier heartbeat")
    
    print("\n📋 RECOMMANDATIONS:")
    print("-" * 20)
    print("1. Vérifier abonnement CME Real-Time dans IBKR")
    print("2. Corriger le code get_market_data")
    print("3. Augmenter les timeouts")
    print("4. Vérifier les paramètres IB Gateway")

if __name__ == "__main__":
    print("🔍 DIAGNOSTIC COMPLET IB GATEWAY")
    print("=" * 50)
    
    asyncio.run(diagnostic_complet())
    
    print("\n📋 DIAGNOSTIC TERMINÉ")
    print("🔍 Vérifier les recommandations ci-dessus")























