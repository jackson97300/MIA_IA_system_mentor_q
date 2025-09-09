#!/usr/bin/env python3
"""
Diagnostic spécifique des erreurs OrderFlow
"""

import asyncio
import logging
from datetime import datetime

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def diagnostic_orderflow():
    """Diagnostic précis des erreurs OrderFlow"""
    
    logger.info("🔍 DIAGNOSTIC ORDERFLOW - DÉMARRAGE")
    
    try:
        # 1. Test import des modules
        logger.info("📦 Test 1: Import des modules...")
        from core.ibkr_connector import IBKRConnector
        from automation_modules.orderflow_analyzer import OrderFlowAnalyzer
        from config.automation_config import AutomationConfig
        logger.info("✅ Import des modules réussi")
        
        # 2. Test configuration
        logger.info("⚙️ Test 2: Configuration...")
        config = AutomationConfig()
        config.ibkr.port = 7496
        config.ibkr.host = "127.0.0.1"
        config.ibkr.client_id = 1
        logger.info(f"✅ Configuration: {config.ibkr.host}:{config.ibkr.port}")
        
        # 3. Test connexion IBKR
        logger.info("🔗 Test 3: Connexion IBKR...")
        ibkr = IBKRConnector(
            host=config.ibkr.host,
            port=config.ibkr.port,
            client_id=config.ibkr.client_id,
            mode="LIVE"
        )
        
        connected = await ibkr.connect()
        logger.info(f"✅ Connexion IBKR: {'SUCCÈS' if connected else 'ÉCHEC'}")
        
        if not connected:
            logger.error("❌ Impossible de se connecter à IBKR")
            return
        
        # 4. Test récupération données ES
        logger.info("📊 Test 4: Récupération données ES...")
        try:
            es_data = await ibkr.get_orderflow_market_data("ES")
            logger.info(f"✅ Données ES récupérées")
            logger.info(f"  📊 Volume: {es_data.get('volume', 'N/A')}")
            logger.info(f"  📈 Delta: {es_data.get('delta', 'N/A')}")
            logger.info(f"  💰 Bid Volume: {es_data.get('bid_volume', 'N/A')}")
            logger.info(f"  💰 Ask Volume: {es_data.get('ask_volume', 'N/A')}")
            logger.info(f"  🎯 Mode: {es_data.get('mode', 'N/A')}")
            
            # Vérification volume
            volume = es_data.get('volume', 0)
            if volume == 0:
                logger.error("❌ ERREUR CRITIQUE: Volume = 0")
                logger.error("💡 Solutions:")
                logger.error("  • Vérifier que TWS/IB Gateway est démarré")
                logger.error("  • Vérifier les permissions de données")
                logger.error("  • Vérifier que le marché ES est ouvert")
            else:
                logger.info(f"✅ Volume valide: {volume}")
                
        except Exception as e:
            logger.error(f"❌ Erreur récupération données ES: {e}")
            return
        
        # 5. Test OrderFlow Analyzer
        logger.info("🧠 Test 5: OrderFlow Analyzer...")
        try:
            analyzer = OrderFlowAnalyzer(config)
            logger.info("✅ OrderFlow Analyzer initialisé")
            
            # Test analyse
            signal = await analyzer.analyze_orderflow_data(es_data)
            if signal:
                logger.info("✅ Signal OrderFlow généré")
                logger.info(f"  📊 Type: {signal.signal_type}")
                logger.info(f"  🎯 Confiance: {signal.confidence}")
            else:
                logger.warning("⚠️ Aucun signal généré (normal si volume insuffisant)")
                
        except Exception as e:
            logger.error(f"❌ Erreur OrderFlow Analyzer: {e}")
            return
        
        # 6. Test déconnexion
        logger.info("🔌 Test 6: Déconnexion...")
        await ibkr.disconnect()
        logger.info("✅ Déconnexion réussie")
        
        logger.info("🎉 DIAGNOSTIC ORDERFLOW TERMINÉ - TOUT OK")
        
    except Exception as e:
        logger.error(f"❌ ERREUR GÉNÉRALE: {e}")
        import traceback
        logger.error(f"📋 Stack trace: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(diagnostic_orderflow())


