#!/usr/bin/env python3
"""
Test de connexion IB Gateway
MIA_IA_SYSTEM - Diagnostic IB Connection
"""

import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from ib_insync import IB, util
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_ib_connection():
    """Test de connexion IB Gateway"""
    
    logger.info("🔍 Test de connexion IB Gateway...")
    
    try:
        # Créer client IB
        ib = IB()
        
        # Configuration
        host = "127.0.0.1"
        port = 7497  # Paper trading
        client_id = 1
        
        logger.info(f"📡 Connexion à {host}:{port} (client_id: {client_id})")
        
        # Connexion
        await ib.connectAsync(
            host=host,
            port=port,
            clientId=client_id,
            timeout=10
        )
        
        if ib.isConnected():
            logger.info("✅ Connexion IB Gateway réussie!")
            
            # Test données de base
            try:
                # Récupérer info compte
                account = ib.accountSummary()
                logger.info(f"📊 Compte: {len(account)} éléments")
                
                # Récupérer contrats ES
                contracts = ib.reqContractDetails(util.Contract(symbol='ES', secType='FUT', exchange='CME'))
                logger.info(f"📈 Contrats ES: {len(contracts)} trouvés")
                
                if contracts:
                    es_contract = contracts[0].contract
                    logger.info(f"   - ES Contract: {es_contract.localSymbol}")
                    
                    # Test données marché
                    tickers = ib.reqMktData(es_contract)
                    await asyncio.sleep(2)
                    
                    if tickers:
                        ticker = tickers[0]
                        logger.info(f"   - ES Price: {ticker.marketPrice()}")
                        logger.info(f"   - ES Bid: {ticker.bid}")
                        logger.info(f"   - ES Ask: {ticker.ask}")
                        logger.info(f"   - ES Volume: {ticker.volume}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Erreur données: {e}")
            
            # Déconnexion
            ib.disconnect()
            logger.info("✅ Test terminé avec succès")
            
        else:
            logger.error("❌ Connexion échouée")
            
    except Exception as e:
        logger.error(f"❌ Erreur connexion: {e}")

if __name__ == "__main__":
    asyncio.run(test_ib_connection())
