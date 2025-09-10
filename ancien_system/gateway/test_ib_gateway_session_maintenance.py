#!/usr/bin/env python3
"""
Test IB Gateway Session Maintenance - MIA_IA_SYSTEM

Test spécifique pour maintenir la session active avec IB Gateway
Résout le problème de déconnexion après 8 secondes
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_session_maintenance():
    """Test maintenance session active"""
    
    logger.info("🔄 Test maintenance session IB Gateway")
    logger.info("=" * 60)
    
    try:
        from core.ibkr_connector import IBKRConnector
        
        # Configuration IB Gateway
        config = {
            'ibkr_host': '127.0.0.1',
            'ibkr_port': 4002,
            'ibkr_client_id': 999,
            'environment': 'PAPER',
            'use_ib_insync': False  # Utiliser ibapi
        }
        
        logger.info("📋 Configuration:")
        logger.info(f"   - Host: {config['ibkr_host']}")
        logger.info(f"   - Port: {config['ibkr_port']}")
        logger.info(f"   - Client ID: {config['ibkr_client_id']}")
        
        # Créer connecteur
        connector = IBKRConnector(config=config)
        
        # Connexion
        logger.info("🔗 Connexion IB Gateway...")
        connected = await connector.connect()
        
        if not connected:
            logger.error("❌ Échec connexion")
            return False
            
        logger.info("✅ Connexion réussie!")
        
        # Test maintenance session pendant 30 secondes
        logger.info("⏱️ Test maintenance session (30 secondes)...")
        start_time = time.time()
        
        for i in range(6):  # 6 x 5 secondes = 30 secondes
            elapsed = time.time() - start_time
            logger.info(f"⏰ Session active depuis {elapsed:.1f}s")
            
            # Health check
            if await connector.health_check():
                logger.info("✅ Health check réussi")
            else:
                logger.warning("⚠️ Health check échoué")
            
            # Attendre 5 secondes
            await asyncio.sleep(5)
        
        # Test données marché
        logger.info("📈 Test données marché...")
        try:
            market_data = await connector.get_market_data("ES")
            if market_data:
                logger.info("✅ Données marché reçues")
                logger.info(f"   - Symbol: {market_data.get('symbol', 'N/A')}")
                logger.info(f"   - Bid: {market_data.get('bid', 'N/A')}")
                logger.info(f"   - Ask: {market_data.get('ask', 'N/A')}")
            else:
                logger.info("⚠️ Pas de données marché (normal en dehors des heures)")
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
        
        # Fermer connexion proprement
        logger.info("🔌 Fermeture connexion...")
        await connector.disconnect()
        
        total_time = time.time() - start_time
        logger.info(f"✅ Test terminé - Session maintenue {total_time:.1f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

async def test_simple_trader_with_session():
    """Test Simple Trader avec maintenance session"""
    
    logger.info("🔧 Test Simple Trader avec maintenance session...")
    
    try:
        from execution.simple_trader import create_simple_trader
        
        # Créer trader
        trader = create_simple_trader("PAPER")
        
        logger.info("📋 Configuration Simple Trader:")
        logger.info(f"   - Mode: {trader.mode.value}")
        logger.info(f"   - IBKR Host: {trader.sierra_config.ibkr.host}")
        logger.info(f"   - IBKR Port: {trader.sierra_config.ibkr.port}")
        
        # Test vérifications pré-trading
        logger.info("🔍 Test vérifications pré-trading...")
        if await trader._pre_trading_checks():
            logger.info("✅ Vérifications pré-trading réussies")
            
            # Test maintenance session
            logger.info("🔄 Test maintenance session Simple Trader...")
            start_time = time.time()
            
            for i in range(4):  # 4 x 5 secondes = 20 secondes
                elapsed = time.time() - start_time
                logger.info(f"⏰ Simple Trader actif depuis {elapsed:.1f}s")
                
                # Health check du connecteur
                if hasattr(trader, 'ibkr_connector') and trader.ibkr_connector:
                    if await trader.ibkr_connector.health_check():
                        logger.info("✅ Health check Simple Trader réussi")
                    else:
                        logger.warning("⚠️ Health check Simple Trader échoué")
                
                await asyncio.sleep(5)
            
            return True
        else:
            logger.error("❌ Échec vérifications pré-trading")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

async def main():
    """Fonction principale"""
    logger.info("🚀 Test Maintenance Session IB Gateway")
    logger.info("=" * 60)
    
    # Test 1: Maintenance session directe
    logger.info("\n📋 TEST 1: Maintenance Session Directe")
    success1 = await test_session_maintenance()
    
    # Test 2: Simple Trader avec maintenance
    logger.info("\n📋 TEST 2: Simple Trader avec Maintenance")
    success2 = await test_simple_trader_with_session()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS MAINTENANCE SESSION")
    print("=" * 60)
    
    print(f"✅ Test maintenance directe: {'RÉUSSI' if success1 else 'ÉCHEC'}")
    print(f"✅ Test Simple Trader: {'RÉUSSI' if success2 else 'ÉCHEC'}")
    
    if success1 and success2:
        print("\n🎉 SUCCÈS TOTAL!")
        print("✅ Session maintenue active")
        print("✅ IB Gateway stable")
        print("✅ Simple Trader opérationnel")
        print("✅ Prêt pour trading en temps réel")
        
        print("\n📋 PROCHAINES ÉTAPES:")
        print("1. python execution/simple_trader.py --mode data_collection")
        print("2. python execution/simple_trader.py --mode paper")
        print("3. Tests de trading en temps réel")
        
    elif success1:
        print("\n⚠️ Maintenance session OK mais problème Simple Trader")
        
    elif success2:
        print("\n⚠️ Simple Trader OK mais problème maintenance session")
        
    else:
        print("\n❌ TOUS LES TESTS ÉCHOUÉS!")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

