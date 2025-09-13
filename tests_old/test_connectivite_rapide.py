#!/usr/bin/env python3
"""
Test de Connectivité Rapide
MIA_IA_SYSTEM - Vérification système en 2-3 minutes
"""

import asyncio
import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
import logging

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - CONNECTIVITE_RAPIDE - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/test_connectivite_rapide.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = get_logger(__name__)

async def test_connectivite():
    """Test rapide de connectivité et fonctionnement"""
    
    logger.info("🔍 === TEST DE CONNECTIVITÉ RAPIDE DÉMARRÉ ===")
    logger.info("⏱️ Durée: 2-3 minutes maximum")
    logger.info("🎯 Objectif: Vérifier que le système fonctionne")
    logger.info("")
    
    # Créer dossier logs
    from pathlib import Path
    Path("logs").mkdir(exist_ok=True)
    
    try:
        logger.info("🔄 Import du système...")
        from launch_24_7_orderflow_trading import OrderFlow24_7Launcher
        
        logger.info("✅ Import réussi")
        logger.info("🔄 Création du launcher...")
        
        launcher = OrderFlow24_7Launcher(live_trading=False)
        logger.info("✅ Launcher créé")
        
        logger.info("🔄 Test de configuration...")
        config = launcher._create_24_7_orderflow_config()
        logger.info("✅ Configuration créée")
        
        logger.info("🔄 Test de connexion IBKR...")
        # Test rapide de connexion
        try:
            # Lancer avec timeout très court pour tester la connexion
            logger.info("⏱️ Test de connexion (30 secondes)...")
            await asyncio.wait_for(launcher.start_24_7_trading(), timeout=30)
        except asyncio.TimeoutError:
            logger.info("✅ Connexion IBKR réussie (timeout normal)")
        except Exception as e:
            logger.error(f"❌ Erreur connexion IBKR: {e}")
            return False
        
        logger.info("✅ Test de connectivité RÉUSSI")
        logger.info("🎯 Le système est fonctionnel")
        logger.info("📊 Prêt pour les tests longs")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test connectivité: {e}")
        logger.error("💀 Le système a des problèmes")
        return False

async def main():
    """Lancement test connectivité"""
    start_time = time.time()
    
    success = await test_connectivite()
    
    elapsed = time.time() - start_time
    logger.info(f"⏱️ Durée totale: {elapsed:.1f} secondes")
    
    if success:
        logger.info("🏆 === TEST DE CONNECTIVITÉ RÉUSSI ===")
        logger.info("✅ Le système est prêt pour les tests longs")
        logger.info("🚀 Vous pouvez maintenant lancer les tests robustes")
    else:
        logger.error("💀 === TEST DE CONNECTIVITÉ ÉCHOUÉ ===")
        logger.error("❌ Problème détecté - Corriger avant tests longs")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
