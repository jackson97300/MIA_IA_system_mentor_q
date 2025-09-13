#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC CONTRAT NQ - MIA_IA_SYSTEM
Script de diagnostic pour identifier les problèmes de contrat NQ
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.ibkr_connector import IBKRConnector

logger = get_logger(__name__)

async def test_nq_contract():
    """Test spécifique du contrat NQ"""
    logger.info("🔍 DIAGNOSTIC CONTRAT NQ")
    logger.info("=" * 50)
    
    # Initialiser le connecteur
    connector = IBKRConnector()
    logger.info("✅ IBKR Connector initialisé")
    
    # Test 1: Initialisation des contrats
    logger.info("\n🧪 TEST 1: Initialisation contrats")
    try:
        await connector._initialize_contracts_async()
        logger.info(f"✅ Contrats initialisés: {list(connector.contracts.keys())}")
        
        if "NQ" in connector.contracts:
            logger.info(f"✅ Contrat NQ trouvé: {connector.contracts['NQ']}")
        else:
            logger.error("❌ Contrat NQ manquant!")
            return
            
    except Exception as e:
        logger.error(f"❌ Erreur initialisation contrats: {e}")
        return
    
    # Test 2: Connexion IBKR
    logger.info("\n🧪 TEST 2: Connexion IBKR")
    try:
        connected = await connector.is_connected()
        if connected:
            logger.info("✅ Connexion IBKR active")
        else:
            logger.warning("⚠️ Connexion IBKR inactive - Tentative de connexion...")
            await connector.connect()
            connected = await connector.is_connected()
            if connected:
                logger.info("✅ Connexion IBKR établie")
            else:
                logger.error("❌ Impossible de se connecter à IBKR")
                return
    except Exception as e:
        logger.error(f"❌ Erreur connexion IBKR: {e}")
        return
    
    # Test 3: Récupération données NQ
    logger.info("\n🧪 TEST 3: Récupération données NQ")
    try:
        nq_data = await connector.get_orderflow_market_data("NQ")
        logger.info("✅ Données NQ récupérées:")
        logger.info(f"  📊 Symbol: {nq_data.get('symbol', 'N/A')}")
        logger.info(f"  💰 Price: {nq_data.get('price', 'N/A')}")
        logger.info(f"  📈 Volume: {nq_data.get('volume', 'N/A')}")
        logger.info(f"  📊 Delta: {nq_data.get('delta', 'N/A')}")
        logger.info(f"  💰 Bid Volume: {nq_data.get('bid_volume', 'N/A')}")
        logger.info(f"  💰 Ask Volume: {nq_data.get('ask_volume', 'N/A')}")
        logger.info(f"  🎯 Mode: {nq_data.get('mode', 'N/A')}")
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération données NQ: {e}")
        import traceback
        logger.error(f"📊 Traceback: {traceback.format_exc()}")
    
    # Test 4: Comparaison ES vs NQ
    logger.info("\n🧪 TEST 4: Comparaison ES vs NQ")
    try:
        es_data = await connector.get_orderflow_market_data("ES")
        logger.info("✅ Données ES récupérées:")
        logger.info(f"  📊 Volume ES: {es_data.get('volume', 'N/A')}")
        logger.info(f"  📊 Volume NQ: {nq_data.get('volume', 'N/A')}")
        
        if es_data.get('volume', 0) > 0 and nq_data.get('volume', 0) == 0:
            logger.warning("⚠️ Volume ES > 0 mais Volume NQ = 0")
            logger.warning("💡 Problème spécifique au contrat NQ détecté")
        elif es_data.get('volume', 0) == 0 and nq_data.get('volume', 0) == 0:
            logger.warning("⚠️ Volumes ES et NQ = 0")
            logger.warning("💡 Problème général de données de marché")
        else:
            logger.info("✅ Volumes ES et NQ corrects")
            
    except Exception as e:
        logger.error(f"❌ Erreur comparaison ES/NQ: {e}")
    
    logger.info("\n🔍 DIAGNOSTIC TERMINÉ")

if __name__ == "__main__":
    asyncio.run(test_nq_contract())

