#!/usr/bin/env python3
"""
Test IB Gateway avec ibapi - MIA_IA_SYSTEM

Test utilisant directement ibapi pour éviter les timeouts ib_insync
"""

import asyncio
import logging
import time

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_ib_gateway_ibapi():
    """Test IB Gateway avec ibapi direct"""
    
    logger.info("🔌 Test IB Gateway avec ibapi...")
    
    try:
        from core.ibkr_connector import IBKRConnector
        
        # Configuration pour IB Gateway
        config = {
            'ibkr_host': '127.0.0.1',
            'ibkr_port': 4002,
            'ibkr_client_id': 999,
            'environment': 'PAPER',
            'connection_timeout': 20,  # Plus court
            'use_ib_insync': False  # Forcer ibapi
        }
        
        logger.info("📋 Configuration ibapi:")
        logger.info(f"   - Host: {config['ibkr_host']}")
        logger.info(f"   - Port: {config['ibkr_port']}")
        logger.info(f"   - Client ID: {config['ibkr_client_id']}")
        logger.info(f"   - Use ib_insync: {config.get('use_ib_insync', True)}")
        
        # Créer connecteur
        connector = IBKRConnector(config=config)
        
        # Forcer ibapi
        connector.use_ib_insync = False
        
        # Tenter connexion
        logger.info("🔗 Tentative de connexion avec ibapi...")
        connected = await connector.connect()
        
        if connected:
            logger.info("✅ Connexion ibapi réussie!")
            
            # Test rapide données marché
            logger.info("📈 Test données marché...")
            try:
                market_data = await connector.get_market_data("ES")
                if market_data:
                    logger.info("✅ Données marché reçues")
                    logger.info(f"   - Symbol: {market_data.get('symbol', 'N/A')}")
                    logger.info(f"   - Bid: {market_data.get('bid', 'N/A')}")
                    logger.info(f"   - Ask: {market_data.get('ask', 'N/A')}")
                else:
                    logger.info("⚠️ Pas de données marché (normal en dehors des heures de trading)")
            except Exception as e:
                logger.info(f"⚠️ Erreur données marché: {e} (normal)")
            
            # Test infos compte
            logger.info("💰 Test infos compte...")
            try:
                account_info = await connector.get_account_info()
                if account_info:
                    logger.info("✅ Infos compte reçues")
                    logger.info(f"   - Compte: {account_info.get('account', 'N/A')}")
                    logger.info(f"   - Equity: ${account_info.get('equity', 0):,.2f}")
                else:
                    logger.info("⚠️ Pas d'infos compte")
            except Exception as e:
                logger.info(f"⚠️ Erreur infos compte: {e} (normal)")
            
            # Fermer connexion
            await connector.disconnect()
            logger.info("🔌 Connexion fermée")
            
            return True
            
        else:
            logger.error("❌ Échec connexion ibapi")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

async def test_simple_trader_ibapi():
    """Test Simple Trader avec ibapi"""
    
    logger.info("🔧 Test Simple Trader avec ibapi...")
    
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
        logger.error(f"❌ Erreur: {e}")
        return False

async def main():
    """Fonction principale"""
    logger.info("🚀 Test IB Gateway avec ibapi")
    logger.info("=" * 50)
    
    # Test 1: Connexion ibapi
    logger.info("\n📋 TEST 1: Connexion ibapi")
    success1 = await test_ib_gateway_ibapi()
    
    # Test 2: Simple Trader
    logger.info("\n📋 TEST 2: Simple Trader")
    success2 = await test_simple_trader_ibapi()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS IBAPI")
    print("=" * 50)
    
    print(f"✅ Test ibapi: {'RÉUSSI' if success1 else 'ÉCHEC'}")
    print(f"✅ Test Simple Trader: {'RÉUSSI' if success2 else 'ÉCHEC'}")
    
    if success1 and success2:
        print("\n🎉 SUCCÈS COMPLET!")
        print("✅ IB Gateway connecté avec ibapi")
        print("✅ Simple Trader configuré")
        print("✅ Prêt pour les tests de trading")
        
        print("\n📋 PROCHAINES ÉTAPES:")
        print("1. python execution/simple_trader.py --mode data_collection --target 10")
        print("2. python execution/simple_trader.py --mode paper")
        print("3. Tester les sessions de trading")
        
    elif success1:
        print("\n⚠️ Connexion ibapi OK mais problème Simple Trader")
        
    elif success2:
        print("\n⚠️ Simple Trader OK mais problème connexion ibapi")
        
    else:
        print("\n❌ TOUS LES TESTS ÉCHOUÉS!")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())

