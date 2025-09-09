#!/usr/bin/env python3
"""
🔍 VÉRIFICATION PRIX ACTUELS - ES/NQ
====================================

Script pour vérifier les prix actuels des indices ES et NQ
et comparer avec les données du diagnostic.
"""

import sys
import asyncio
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.ibkr_connector import IBKRConnector

logger = get_logger(__name__)

async def check_current_prices():
    """Vérifie les prix actuels ES/NQ"""
    logger.info("🔍 VÉRIFICATION PRIX ACTUELS ES/NQ")
    logger.info("=" * 50)
    
    try:
        # Connexion IBKR
        ibkr_connector = IBKRConnector()
        await ibkr_connector.connect()
        
        if not ibkr_connector.is_connected():
            logger.error("❌ Impossible de se connecter à IBKR")
            return
        
        logger.info("✅ Connexion IBKR établie")
        
        # Vérification ES
        logger.info("📈 Vérification ES (S&P 500):")
        es_data = await ibkr_connector.get_orderflow_market_data('ES')
        if es_data:
            es_price = es_data.get('price', 0)
            es_volume = es_data.get('volume', 0)
            es_delta = es_data.get('delta', 0)
            
            logger.info(f"   💱 Prix actuel: {es_price}")
            logger.info(f"   📊 Volume: {es_volume}")
            logger.info(f"   📈 Delta: {es_delta}")
            
            # Comparaison avec diagnostic
            diagnostic_price = 6479.5
            price_diff = abs(es_price - diagnostic_price)
            price_diff_pct = (price_diff / diagnostic_price) * 100
            
            logger.info(f"   🔍 Comparaison diagnostic:")
            logger.info(f"      Diagnostic: {diagnostic_price}")
            logger.info(f"      Actuel: {es_price}")
            logger.info(f"      Différence: {price_diff:.2f} ({price_diff_pct:.2f}%)")
            
            if price_diff_pct > 5:
                logger.warning(f"   ⚠️ Différence importante détectée!")
            else:
                logger.info(f"   ✅ Prix cohérent")
        else:
            logger.error("❌ Impossible de récupérer les données ES")
        
        # Vérification NQ
        logger.info("📊 Vérification NQ (NASDAQ):")
        nq_data = await ibkr_connector.get_orderflow_market_data('NQ')
        if nq_data:
            nq_price = nq_data.get('price', 0)
            nq_volume = nq_data.get('volume', 0)
            nq_delta = nq_data.get('delta', 0)
            
            logger.info(f"   💱 Prix actuel: {nq_price}")
            logger.info(f"   📊 Volume: {nq_volume}")
            logger.info(f"   📈 Delta: {nq_delta}")
            
            # Comparaison avec diagnostic
            diagnostic_price = 23549.0
            price_diff = abs(nq_price - diagnostic_price)
            price_diff_pct = (price_diff / diagnostic_price) * 100
            
            logger.info(f"   🔍 Comparaison diagnostic:")
            logger.info(f"      Diagnostic: {diagnostic_price}")
            logger.info(f"      Actuel: {nq_price}")
            logger.info(f"      Différence: {price_diff:.2f} ({price_diff_pct:.2f}%)")
            
            if price_diff_pct > 5:
                logger.warning(f"   ⚠️ Différence importante détectée!")
            else:
                logger.info(f"   ✅ Prix cohérent")
        else:
            logger.error("❌ Impossible de récupérer les données NQ")
        
        # Vérification avec vos données
        logger.info("🎯 VÉRIFICATION AVEC VOS DONNÉES:")
        logger.info(f"   📈 ES attendu: 6425")
        logger.info(f"   📊 NQ attendu: 23333")
        
        if es_data and nq_data:
            es_current = es_data.get('price', 0)
            nq_current = nq_data.get('price', 0)
            
            es_diff = abs(es_current - 6425)
            nq_diff = abs(nq_current - 23333)
            
            logger.info(f"   📈 ES actuel: {es_current} (diff: {es_diff:.2f})")
            logger.info(f"   📊 NQ actuel: {nq_current} (diff: {nq_diff:.2f})")
            
            if es_diff > 50 or nq_diff > 100:
                logger.warning("   ⚠️ Différences importantes avec vos données!")
            else:
                logger.info("   ✅ Prix cohérents avec vos données")
        
        # Déconnexion
        await ibkr_connector.disconnect()
        logger.info("✅ Déconnexion IBKR")
        
    except Exception as e:
        logger.error(f"❌ Erreur vérification prix: {e}")

if __name__ == "__main__":
    asyncio.run(check_current_prices())

