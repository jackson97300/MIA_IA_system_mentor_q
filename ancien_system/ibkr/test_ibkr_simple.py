#!/usr/bin/env python3
"""
test_ibkr_simple.py

Test simple et direct de la connexion IBKR TWS
"""

import asyncio
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_ibkr_direct():
    """Test direct de la connexion IBKR"""
    
    print("🔍 Test direct IBKR TWS (port 7496)")
    print("=" * 50)
    
    try:
        # Import direct du connecteur
        from features.ibkr_connector3 import IBKRConnector
        
        # Créer le connecteur avec port explicite
        connector = IBKRConnector(
            host="127.0.0.1",
            port=7496,
            client_id=1
        )
        
        print(f"🔗 Tentative de connexion à {connector.host}:{connector.port}")
        print("⏳ Connexion en cours...")
        
        # Test de connexion avec timeout court
        connected = await asyncio.wait_for(connector.connect(), timeout=15.0)
        
        if connected:
            print("✅ Connexion IBKR réussie !")
            
            # Test simple de données
            try:
                print("📊 Test récupération SPX...")
                spx_data = await connector.get_market_data("SPX")
                print(f"✅ SPX: {spx_data}")
            except Exception as e:
                print(f"❌ Erreur SPX: {e}")
            
            # Déconnexion propre
            await connector.disconnect()
            print("🔌 Déconnexion effectuée")
            
        else:
            print("❌ Échec de la connexion")
            
    except asyncio.TimeoutError:
        print("⏰ TIMEOUT: Connexion trop lente")
        print("💡 Vérifiez que TWS est bien connecté au marché")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("💡 Vérifiez la configuration TWS")
    
    print("=" * 50)

async def test_ibkr_connection_status():
    """Test du statut de connexion TWS"""
    
    print("🔍 Vérification statut TWS...")
    print("=" * 50)
    
    try:
        from features.ibkr_connector3 import IBKRConnector
        
        connector = IBKRConnector(host="127.0.0.1", port=7496, client_id=1)
        
        # Test de connexion basique
        print("🔗 Test connexion basique...")
        connected = await connector.connect()
        
        if connected:
            print("✅ TWS accessible")
            
            # Vérifier si connecté au marché
            try:
                # Test simple pour voir si on peut récupérer des données
                print("📊 Test accès marché...")
                await connector.get_market_data("SPX")
                print("✅ TWS connecté au marché")
            except Exception as e:
                print(f"⚠️ TWS accessible mais problème marché: {e}")
            
            await connector.disconnect()
        else:
            print("❌ TWS non accessible")
            
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
    
    print("=" * 50)

async def main():
    """Fonction principale"""
    print("🚀 Test IBKR TWS - Port 7496")
    print()
    
    # Test 1: Connexion directe
    await test_ibkr_direct()
    print()
    
    # Test 2: Statut connexion
    await test_ibkr_connection_status()
    print()
    
    print("📋 Checklist TWS:")
    print("1. ✅ TWS lancé sur port 7496")
    print("2. ✅ Mode 'Accept connections from localhost' activé")
    print("3. ✅ API activée dans TWS")
    print("4. ✅ Connecté au marché (pas en mode déconnecté)")
    print("5. ✅ Pas de popup de sécurité en attente")

if __name__ == "__main__":
    asyncio.run(main())
