#!/usr/bin/env python3
"""
🚀 TEST CONNEXION IBKR RÉEL - TWS LIVE
======================================

Test de connexion pour le mode réel TWS avec port 7495
"""

import sys
import asyncio
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.ibkr_connector import IBKRConnector

logger = get_logger(__name__)

async def test_ibkr_reel():
    """Test connexion IBKR mode réel"""
    logger.info("🚀 TEST CONNEXION IBKR RÉEL - TWS LIVE")
    logger.info("=" * 50)
    
    # Configuration mode réel
    host = "127.0.0.1"
    port = 7495  # Port TWS mode réel
    client_id = 1
    
    logger.info(f"🔗 Configuration mode RÉEL:")
    logger.info(f"   📡 Host: {host}")
    logger.info(f"   🔌 Port: {port} (TWS RÉEL)")
    logger.info(f"   🆔 Client ID: {client_id}")
    logger.info(f"   💰 Mode: LIVE TRADING")
    
    try:
        # Créer connecteur mode réel
        ibkr_connector = IBKRConnector(
            host=host,
            port=port,
            client_id=client_id,
            mode="LIVE"
        )
        
        logger.info("🔗 Tentative connexion TWS RÉEL...")
        
        # Connexion
        connection_result = await ibkr_connector.connect()
        
        if connection_result:
            logger.info("✅ Connexion TWS RÉEL réussie!")
            
            # Test contrats
            contracts = await ibkr_connector.get_contracts()
            if contracts:
                logger.info("✅ Contrats initialisés:")
                for symbol, contract in contracts.items():
                    logger.info(f"   📊 {symbol}: {contract.symbol} ({contract.localSymbol})")
                    logger.info(f"      Multiplier: {contract.multiplier}")
                    logger.info(f"      Exchange: {contract.exchange}")
            else:
                logger.warning("⚠️ Aucun contrat initialisé")
            
            # Test données ES
            logger.info("📈 Test données ES:")
            es_data = await ibkr_connector.get_orderflow_market_data('ES')
            if es_data:
                logger.info("✅ Données ES récupérées:")
                logger.info(f"   💱 Prix: {es_data.get('price', 'N/A')}")
                logger.info(f"   📊 Volume: {es_data.get('volume', 'N/A')}")
                logger.info(f"   📈 Delta: {es_data.get('delta', 'N/A')}")
            else:
                logger.warning("⚠️ Aucune donnée ES")
            
            # Test données NQ
            logger.info("📊 Test données NQ:")
            nq_data = await ibkr_connector.get_orderflow_market_data('NQ')
            if nq_data:
                logger.info("✅ Données NQ récupérées:")
                logger.info(f"   💱 Prix: {nq_data.get('price', 'N/A')}")
                logger.info(f"   📊 Volume: {nq_data.get('volume', 'N/A')}")
                logger.info(f"   📈 Delta: {nq_data.get('delta', 'N/A')}")
            else:
                logger.warning("⚠️ Aucune donnée NQ")
            
            # Déconnexion
            await ibkr_connector.disconnect()
            logger.info("✅ Déconnexion propre")
            
        else:
            logger.error("❌ Échec connexion TWS RÉEL")
            
    except Exception as e:
        logger.error(f"❌ Erreur connexion TWS RÉEL: {e}")
        logger.info("🔧 VÉRIFICATIONS:")
        logger.info("   1. TWS ouvert et connecté")
        logger.info("   2. API activée dans TWS")
        logger.info("   3. Port 7495 ouvert")
        logger.info("   4. Client ID unique")

if __name__ == "__main__":
    asyncio.run(test_ibkr_reel())

