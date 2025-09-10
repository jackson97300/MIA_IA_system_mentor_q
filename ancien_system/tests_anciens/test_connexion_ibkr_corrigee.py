#!/usr/bin/env python3
"""
🔧 TEST CONNEXION IBKR CORRIGÉE
MIA_IA_SYSTEM - Vérification connexion avec port 7497 (TWS Paper Trading)
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

async def test_connexion_ibkr_corrigee():
    """Test connexion IBKR avec port 7497 corrigé"""
    
    print("🔧 === TEST CONNEXION IBKR CORRIGÉE ===")
    print("🎯 Port: 7497 (TWS Paper Trading)")
    print("🔗 Host: 127.0.0.1")
    print("🆔 Client ID: 999")
    print()
    
    # Configuration IBKR corrigée
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 7497,  # ✅ PORT CORRIGÉ
        'ibkr_client_id': 999,
        'connection_timeout': 30,
        'simulation_mode': False
    }
    
    # Créer connecteur
    print("🔗 Création connecteur IBKR...")
    connector = IBKRConnector(config)
    
    # Test connexion
    print("\n1️⃣ Test connexion IBKR...")
    start_time = time.time()
    
    try:
        success = await connector.connect()
        connection_time = time.time() - start_time
        
        if success:
            print(f"✅ Connexion IBKR RÉUSSIE en {connection_time:.2f}s")
            print("📊 Source: IBKR (données réelles)")
            
            # Test données marché
            print("\n2️⃣ Test données marché ES...")
            market_data = await connector.get_market_data("ES")
            
            if market_data:
                print("✅ Données marché ES récupérées")
                print(f"   📈 Prix: {market_data.get('price', 'N/A')}")
                print(f"   📊 Volume: {market_data.get('volume', 'N/A')}")
                print(f"   💰 Bid: {market_data.get('bid', 'N/A')}")
                print(f"   💰 Ask: {market_data.get('ask', 'N/A')}")
            else:
                print("❌ Erreur récupération données marché")
            
            # Test info compte
            print("\n3️⃣ Test info compte...")
            account_info = await connector.get_account_info()
            
            if account_info:
                print("✅ Info compte récupérée")
                print(f"   🆔 Account ID: {account_info.get('account_id', 'N/A')}")
                print(f"   💰 Available Funds: {account_info.get('available_funds', 'N/A')}")
                print(f"   📊 Mode: {account_info.get('mode', 'N/A')}")
            else:
                print("❌ Erreur récupération info compte")
            
            # Déconnexion
            await connector.disconnect()
            print("\n🔌 Déconnexion IBKR")
            
        else:
            print("❌ Échec connexion IBKR")
            print("🔍 Vérifications à faire:")
            print("   1. TWS est-il démarré ?")
            print("   2. Port 7497 est-il ouvert ?")
            print("   3. API est-elle activée dans TWS ?")
            print("   4. Client ID 999 est-il disponible ?")
            
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        print("🔍 Détails de l'erreur:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {str(e)}")
    
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ TEST CONNEXION IBKR")
    print("=" * 50)
    
    if success:
        print("✅ CONNEXION IBKR CORRIGÉE - SUCCÈS !")
        print("🎯 Port 7497 fonctionne correctement")
        print("🚀 Système prêt pour trading")
    else:
        print("❌ CONNEXION IBKR - ÉCHEC")
        print("🔧 Actions recommandées:")
        print("   1. Démarrer TWS")
        print("   2. Activer API (Edit → Global Configuration → API)")
        print("   3. Vérifier port 7497")
        print("   4. Redémarrer TWS")

if __name__ == "__main__":
    print("⚠️ TEST CONNEXION IBKR AVEC PORT CORRIGÉ")
    print("🎯 Objectif: Vérifier que le port 7497 fonctionne")
    print()
    
    asyncio.run(test_connexion_ibkr_corrigee())
























