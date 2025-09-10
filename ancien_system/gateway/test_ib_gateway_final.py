#!/usr/bin/env python3
"""
Test IB Gateway Final - MIA_IA_SYSTEM

Test final basé sur l'analyse des logs IB Gateway
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

async def test_ib_gateway_connection():
    """Test final de connexion IB Gateway"""
    
    logger.info("🔌 Test final IB Gateway...")
    
    try:
        from core.ibkr_connector import IBKRConnector
        
        # Configuration basée sur les logs réussis
        config = {
            'ibkr_host': '127.0.0.1',
            'ibkr_port': 4002,
            'ibkr_client_id': 999,
            'environment': 'PAPER',
            'connection_timeout': 45  # Plus long pour IB Gateway
        }
        
        logger.info("📋 Configuration finale:")
        logger.info(f"   - Host: {config['ibkr_host']}")
        logger.info(f"   - Port: {config['ibkr_port']}")
        logger.info(f"   - Client ID: {config['ibkr_client_id']}")
        logger.info(f"   - Timeout: {config['connection_timeout']}s")
        
        # Créer connecteur
        connector = IBKRConnector(config=config)
        
        # Tenter connexion
        logger.info("🔗 Tentative de connexion...")
        connected = await connector.connect()
        
        if connected:
            logger.info("✅ Connexion réussie!")
            
            # Test rapide données marché
            logger.info("📈 Test rapide données marché...")
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
            
            # Fermer connexion proprement
            await connector.disconnect()
            logger.info("🔌 Connexion fermée proprement")
            
            return True
            
        else:
            logger.error("❌ Échec connexion")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

async def test_simple_trader_config():
    """Test configuration Simple Trader avec IB Gateway"""
    
    logger.info("🔧 Test configuration Simple Trader...")
    
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
        logger.info(f"   - Environment: {trader.sierra_config.environment}")
        
        # Test vérifications pré-trading
        logger.info("🔍 Test vérifications pré-trading...")
        if await trader._pre_trading_checks():
            logger.info("✅ Vérifications pré-trading réussies")
            return True
        else:
            logger.error("❌ Échec vérifications pré-trading")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur configuration: {e}")
        return False

async def main():
    """Fonction principale"""
    logger.info("🚀 Test IB Gateway Final")
    logger.info("=" * 50)
    
    # Test 1: Connexion IB Gateway
    logger.info("\n📋 TEST 1: Connexion IB Gateway")
    success1 = await test_ib_gateway_connection()
    
    # Test 2: Configuration Simple Trader
    logger.info("\n📋 TEST 2: Configuration Simple Trader")
    success2 = await test_simple_trader_config()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS FINAUX")
    print("=" * 50)
    
    print(f"✅ Test Connexion: {'RÉUSSI' if success1 else 'ÉCHEC'}")
    print(f"✅ Test Configuration: {'RÉUSSI' if success2 else 'ÉCHEC'}")
    
    if success1 and success2:
        print("\n🎉 SUCCÈS COMPLET!")
        print("✅ IB Gateway connecté et fonctionnel")
        print("✅ Simple Trader configuré correctement")
        print("✅ Prêt pour les tests de trading")
        
        print("\n📋 PROCHAINES ÉTAPES:")
        print("1. Tester le mode DATA_COLLECTION")
        print("2. Tester le mode PAPER trading")
        print("3. Lancer des sessions de trading")
        
    elif success1:
        print("\n⚠️ Connexion OK mais problème de configuration")
        print("🔧 Vérifiez la configuration Simple Trader")
        
    elif success2:
        print("\n⚠️ Configuration OK mais problème de connexion")
        print("🔧 Vérifiez IB Gateway")
        
    else:
        print("\n❌ TOUS LES TESTS ÉCHOUÉS!")
        print("🔧 Vérifiez la configuration complète")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 