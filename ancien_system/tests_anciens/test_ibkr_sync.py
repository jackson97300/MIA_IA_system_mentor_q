#!/usr/bin/env python3
"""
🚀 TEST CONNEXION IBKR SYNCHRONE - SANS ASYNCIO
===============================================

Test de connexion IBKR en mode synchrone pour éviter les conflits d'event loop
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger

logger = get_logger(__name__)

def test_ibkr_sync():
    """Test connexion IBKR synchrone"""
    logger.info("🚀 TEST CONNEXION IBKR SYNCHRONE")
    logger.info("=" * 50)
    
    # Configuration
    host = "127.0.0.1"
    port = 7496  # Port TWS mode paper
    client_id = 1
    
    logger.info(f"🔗 Configuration:")
    logger.info(f"   📡 Host: {host}")
    logger.info(f"   🔌 Port: {port} (TWS PAPER)")
    logger.info(f"   🆔 Client ID: {client_id}")
    logger.info(f"   💰 Mode: PAPER TRADING")
    
    try:
        from ib_insync import IB, Contract
        
        logger.info("📦 Import ib_insync réussi")
        
        # Créer instance IB
        ib = IB()
        
        logger.info("🔗 Tentative connexion TWS...")
        
        # Connexion synchrone
        ib.connect(host, port, clientId=client_id, timeout=30)
        
        if ib.isConnected():
            logger.info("✅ Connexion TWS réussie!")
            
            # Test contrats
            logger.info("📊 Test contrats:")
            
            # Contrat ES
            es_contract = Contract(
                symbol='ES',
                secType='FUT',
                exchange='CME',
                currency='USD',
                lastTradingDay='20241220'
            )
            logger.info("✅ Contrat ES créé")
            
            # Contrat NQ
            nq_contract = Contract(
                symbol='NQ',
                secType='FUT',
                exchange='CME',
                currency='USD',
                lastTradingDay='20241220'
            )
            logger.info("✅ Contrat NQ créé")
            
            # Test données ES
            logger.info("📈 Test données ES:")
            try:
                ib.reqMktData(es_contract)
                ib.sleep(2)  # Attendre données
                
                if es_contract.marketPrice():
                    logger.info(f"✅ Prix ES: {es_contract.marketPrice()}")
                else:
                    logger.warning("⚠️ Pas de prix ES")
                    
            except Exception as e:
                logger.warning(f"⚠️ Erreur données ES: {e}")
            
            # Test données NQ
            logger.info("📊 Test données NQ:")
            try:
                ib.reqMktData(nq_contract)
                ib.sleep(2)  # Attendre données
                
                if nq_contract.marketPrice():
                    logger.info(f"✅ Prix NQ: {nq_contract.marketPrice()}")
                else:
                    logger.warning("⚠️ Pas de prix NQ")
                    
            except Exception as e:
                logger.warning(f"⚠️ Erreur données NQ: {e}")
            
            # Déconnexion
            ib.disconnect()
            logger.info("✅ Déconnexion propre")
            
        else:
            logger.error("❌ Échec connexion TWS")
            
    except Exception as e:
        logger.error(f"❌ Erreur connexion TWS: {e}")
        logger.info("🔧 VÉRIFICATIONS:")
        logger.info("   1. TWS ouvert et connecté")
        logger.info("   2. API activée dans TWS")
        logger.info("   3. Mode PAPER sélectionné")
        logger.info("   4. Permissions API accordées")

if __name__ == "__main__":
    test_ibkr_sync()

