#!/usr/bin/env python3
"""
Test Simple Trader avec IB Gateway - MIA_IA_SYSTEM

Test du trader simple avec IB Gateway en mode simulé
"""

import asyncio
import logging
import time
from datetime import datetime

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_simple_trader_with_ib_gateway():
    """Test du simple trader avec IB Gateway"""
    
    logger.info("🚀 Test Simple Trader avec IB Gateway")
    logger.info("=" * 60)
    
    try:
        # Import du trader
        from execution.simple_trader import create_simple_trader
        
        # Créer trader en mode PAPER
        logger.info("🔧 Création trader en mode PAPER...")
        trader = create_simple_trader("PAPER")
        
        # Afficher configuration
        logger.info("📋 Configuration trader:")
        logger.info(f"   - Mode: {trader.mode.value}")
        logger.info(f"   - IBKR Host: {trader.sierra_config.ibkr.host}")
        logger.info(f"   - IBKR Port: {trader.sierra_config.ibkr.port}")
        logger.info(f"   - Client ID: {trader.sierra_config.ibkr.client_id}")
        logger.info(f"   - Environment: {trader.sierra_config.environment}")
        
        # Afficher diagnostics
        logger.info("\n🔍 Diagnostics Risk Manager:")
        trader.log_risk_diagnostics()
        
        logger.info("\n🔍 Diagnostics Sierra/IBKR:")
        trader.log_sierra_ibkr_diagnostics()
        
        # Test connexion
        logger.info("\n🔌 Test connexion...")
        if await trader._pre_trading_checks():
            logger.info("✅ Vérifications pré-trading réussies")
        else:
            logger.error("❌ Échec vérifications pré-trading")
            return False
        
        # Démarrer session courte
        logger.info("\n📈 Démarrage session de trading (30 secondes)...")
        
        if await trader.start_trading_session():
            logger.info("✅ Session démarrée")
            
            # Lancer boucle de trading pour 30 secondes
            start_time = time.time()
            max_duration = 30  # secondes
            
            while time.time() - start_time < max_duration:
                try:
                    # Obtenir données marché
                    market_data = await trader._get_current_market_data()
                    if market_data:
                        logger.info(f"📊 Prix ES: {market_data.close}")
                        
                        # Générer signal
                        signal = trader.signal_generator.generate_signal(market_data)
                        if signal:
                            logger.info(f"🎯 Signal généré: {signal.decision.value} (confiance: {signal.total_confidence:.1%})")
                            
                            # Vérifier seuil
                            if signal.total_confidence >= trader.min_probability:
                                logger.info("✅ Signal au-dessus du seuil")
                            else:
                                logger.info("⚠️ Signal sous le seuil")
                        else:
                            logger.info("⏳ Aucun signal")
                    
                    # Attendre
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"❌ Erreur boucle: {e}")
                    break
            
            # Arrêter trading
            logger.info("\n⏹️ Arrêt du trading...")
            await trader.stop_trading()
            
            # Afficher statistiques
            logger.info("\n📊 Statistiques de la session:")
            stats = trader.get_statistics()
            logger.info(f"   - Trades: {stats['session_info']['trades_count']}")
            logger.info(f"   - Signaux: {stats['session_info']['signals_total']}")
            logger.info(f"   - P&L: ${stats['session_info']['pnl']:.2f}")
            
            return True
            
        else:
            logger.error("❌ Échec démarrage session")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Erreur import: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

async def test_data_collection_mode():
    """Test du mode collecte de données"""
    
    logger.info("\n🔬 Test mode collecte de données...")
    
    try:
        from execution.simple_trader import create_simple_trader
        
        # Créer trader en mode DATA_COLLECTION
        trader = create_simple_trader("DATA_COLLECTION")
        trader.target_trades = 5  # Petit objectif pour test
        
        logger.info(f"📋 Mode: {trader.mode.value}")
        logger.info(f"📋 Objectif: {trader.target_trades} trades")
        logger.info(f"📋 Seuil probabilité: {trader.min_probability:.1%}")
        
        # Démarrer session courte
        if await trader.start_trading_session():
            logger.info("✅ Session collecte démarrée")
            
            # Lancer pour 20 secondes
            start_time = time.time()
            max_duration = 20
            
            while time.time() - start_time < max_duration:
                try:
                    market_data = await trader._get_current_market_data()
                    if market_data:
                        signal = trader.signal_generator.generate_signal(market_data)
                        if signal and signal.total_confidence >= trader.min_probability:
                            logger.info(f"🎯 Signal collecte: {signal.decision.value} ({signal.total_confidence:.1%})")
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Erreur: {e}")
                    break
            
            await trader.stop_trading()
            
            # Statistiques
            stats = trader.get_statistics()
            logger.info(f"📊 Collecte: {stats['session_info']['trades_count']} trades")
            
            return True
        else:
            logger.error("❌ Échec démarrage collecte")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur collecte: {e}")
        return False

async def main():
    """Fonction principale"""
    logger.info("🚀 TESTS SIMPLE TRADER AVEC IB GATEWAY")
    logger.info("=" * 60)
    
    # Test 1: Mode PAPER
    logger.info("\n📋 TEST 1: Mode PAPER")
    success1 = await test_simple_trader_with_ib_gateway()
    
    # Test 2: Mode DATA_COLLECTION
    logger.info("\n📋 TEST 2: Mode DATA_COLLECTION")
    success2 = await test_data_collection_mode()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS DES TESTS")
    print("=" * 60)
    
    print(f"✅ Test PAPER: {'RÉUSSI' if success1 else 'ÉCHEC'}")
    print(f"✅ Test DATA_COLLECTION: {'RÉUSSI' if success2 else 'ÉCHEC'}")
    
    if success1 and success2:
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ Simple Trader prêt avec IB Gateway")
    elif success1 or success2:
        print("\n⚠️ Tests partiellement réussis")
    else:
        print("\n❌ TOUS LES TESTS ÉCHOUÉS!")
        print("⚠️ Vérifiez la configuration IB Gateway")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

