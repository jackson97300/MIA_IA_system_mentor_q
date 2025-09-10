#!/usr/bin/env python3
"""
Test IB Gateway Robuste - MIA_IA_SYSTEM

Test robuste avec attente que IB Gateway soit complètement initialisé
"""

import asyncio
import logging
import time
from datetime import datetime

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def wait_for_ib_gateway_ready(max_wait_seconds: int = 60) -> bool:
    """Attend que IB Gateway soit prêt"""
    logger.info("⏳ Attente que IB Gateway soit prêt...")
    
    start_time = time.time()
    attempts = 0
    
    while time.time() - start_time < max_wait_seconds:
        try:
            from core.ibkr_connector import IBKRConnector
            
            # Configuration pour IB Gateway
            config = {
                'ibkr_host': '127.0.0.1',
                'ibkr_port': 4002,
                'ibkr_client_id': 999,
                'environment': 'PAPER',
                'connection_timeout': 10  # Timeout court pour test
            }
            
            connector = IBKRConnector(config=config)
            
            # Tentative connexion rapide
            connected = await connector.connect()
            
            if connected:
                logger.info("✅ IB Gateway prêt!")
                await connector.disconnect()
                return True
            else:
                attempts += 1
                logger.info(f"⏳ Tentative {attempts} - IB Gateway pas encore prêt...")
                await asyncio.sleep(5)
                
        except Exception as e:
            attempts += 1
            logger.info(f"⏳ Tentative {attempts} - Erreur: {e}")
            await asyncio.sleep(5)
    
    logger.error(f"❌ IB Gateway pas prêt après {max_wait_seconds} secondes")
    return False

async def test_ib_gateway_connection():
    """Test robuste de connexion IB Gateway"""
    
    logger.info("🔌 Test connexion IB Gateway (robuste)...")
    
    # Attendre que IB Gateway soit prêt
    if not await wait_for_ib_gateway_ready():
        return False
    
    try:
        # Import IBKR Connector
        from core.ibkr_connector import IBKRConnector
        
        # Configuration pour IB Gateway simulé
        host = "127.0.0.1"
        port = 4002
        client_id = 999
        
        logger.info(f"📋 Configuration:")
        logger.info(f"   - Host: {host}")
        logger.info(f"   - Port: {port}")
        logger.info(f"   - Client ID: {client_id}")
        
        # Créer connecteur
        config = {
            'ibkr_host': host,
            'ibkr_port': port,
            'ibkr_client_id': client_id,
            'environment': 'PAPER',
            'connection_timeout': 30
        }
        connector = IBKRConnector(config=config)
        
        # Tenter connexion
        logger.info("🔗 Tentative de connexion...")
        connected = await connector.connect()
        
        if connected:
            logger.info("✅ Connexion réussie!")
            
            # Vérifier statut
            status = await connector.get_connection_status()
            logger.info(f"📊 Statut: {status}")
            
            # Test simple données marché
            logger.info("📈 Test données marché...")
            try:
                market_data = await connector.get_market_data("ES")
                if market_data:
                    logger.info("✅ Données marché reçues")
                    logger.info(f"   - Symbol: {market_data.get('symbol', 'N/A')}")
                    logger.info(f"   - Bid: {market_data.get('bid', 'N/A')}")
                    logger.info(f"   - Ask: {market_data.get('ask', 'N/A')}")
                else:
                    logger.warning("⚠️ Aucune donnée marché")
            except Exception as e:
                logger.warning(f"⚠️ Erreur données marché: {e}")
            
            # Test infos compte
            logger.info("💰 Test infos compte...")
            try:
                account_info = await connector.get_account_info()
                if account_info:
                    logger.info("✅ Infos compte reçues")
                    logger.info(f"   - Compte: {account_info.get('account', 'N/A')}")
                    logger.info(f"   - Equity: ${account_info.get('equity', 0):,.2f}")
                else:
                    logger.warning("⚠️ Aucune info compte")
            except Exception as e:
                logger.warning(f"⚠️ Erreur infos compte: {e}")
            
            # Fermer connexion
            await connector.disconnect()
            logger.info("🔌 Connexion fermée")
            
            return True
            
        else:
            logger.error("❌ Échec connexion")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Module IBKR non trouvé: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

async def test_simple_trader_integration():
    """Test intégration avec simple trader"""
    
    logger.info("🔧 Test intégration Simple Trader...")
    
    try:
        from execution.simple_trader import create_simple_trader
        
        # Créer trader en mode PAPER
        trader = create_simple_trader("PAPER")
        
        # Afficher configuration
        logger.info("📋 Configuration Simple Trader:")
        logger.info(f"   - Mode: {trader.mode.value}")
        logger.info(f"   - IBKR Host: {trader.sierra_config.ibkr.host}")
        logger.info(f"   - IBKR Port: {trader.sierra_config.ibkr.port}")
        logger.info(f"   - Client ID: {trader.sierra_config.ibkr.client_id}")
        
        # Test vérifications pré-trading
        logger.info("🔍 Test vérifications pré-trading...")
        if await trader._pre_trading_checks():
            logger.info("✅ Vérifications pré-trading réussies")
            return True
        else:
            logger.error("❌ Échec vérifications pré-trading")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur intégration: {e}")
        return False

async def main():
    """Fonction principale"""
    logger.info("🚀 Test IB Gateway Robuste")
    logger.info("=" * 50)
    
    # Test 1: Attendre et tester connexion
    logger.info("\n📋 TEST 1: Connexion IB Gateway")
    success1 = await test_ib_gateway_connection()
    
    # Test 2: Intégration Simple Trader
    logger.info("\n📋 TEST 2: Intégration Simple Trader")
    success2 = await test_simple_trader_integration()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS DES TESTS")
    print("=" * 50)
    
    print(f"✅ Test Connexion: {'RÉUSSI' if success1 else 'ÉCHEC'}")
    print(f"✅ Test Intégration: {'RÉUSSI' if success2 else 'ÉCHEC'}")
    
    if success1 and success2:
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ IB Gateway prêt pour MIA_IA_SYSTEM")
        print("✅ Simple Trader configuré correctement")
    elif success1:
        print("\n⚠️ Connexion OK mais problème d'intégration")
    elif success2:
        print("\n⚠️ Intégration OK mais problème de connexion")
    else:
        print("\n❌ TOUS LES TESTS ÉCHOUÉS!")
        print("⚠️ Vérifiez la configuration IB Gateway")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())

