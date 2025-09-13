#!/usr/bin/env python3
"""
Test ROBUSTE CONSERVATEUR
MIA_IA_SYSTEM - Version améliorée avec gestion d'erreurs
"""

import asyncio
import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
import logging

# Configuration de test CONSERVATEUR
config_data = {
    "name": "CONSERVATEUR_ROBUSTE",
    "description": "Win Rate 40-50% - Paramètres prudents (Version robuste)",
    "expected_win_rate": "40-50%",
    "risk_level": "FAIBLE"
}

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - CONSERVATEUR_ROBUSTE - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/test_robuste_conservateur.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = get_logger(__name__)

async def main():
    """Lancement test CONSERVATEUR ROBUSTE"""
    
    logger.info("🚀 === TEST CONSERVATEUR ROBUSTE DÉMARRÉ ===")
    logger.info(f"📊 Configuration: {config_data['description']}")
    logger.info(f"🎯 Win Rate attendu: {config_data['expected_win_rate']}")
    logger.info(f"⚠️ Niveau de risque: {config_data['risk_level']}")
    logger.info("🛡️ Mode robuste activé - Gestion d'erreurs améliorée")
    
    # Créer dossier logs
    from pathlib import Path
    Path("logs").mkdir(exist_ok=True)
    
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logger.info(f"🔄 Tentative {retry_count + 1}/{max_retries}")
            
            # Importer et lancer le système
            from launch_24_7_orderflow_trading import OrderFlow24_7Launcher
            
            launcher = OrderFlow24_7Launcher(live_trading=False)
            
            # Override configuration
            config = launcher._create_24_7_orderflow_config()
            
            # Appliquer paramètres de test CONSERVATEUR
            config.min_confidence_threshold = 0.15
            config.footprint_threshold = 0.05
            config.volume_threshold = 10
            config.delta_threshold = 0.06
            
            logger.info("✅ Configuration appliquée")
            logger.info(f"   📊 min_confidence_threshold: {config.min_confidence_threshold}")
            logger.info(f"   🎯 footprint_threshold: {config.footprint_threshold}")
            logger.info(f"   📈 volume_threshold: {config.volume_threshold}")
            logger.info(f"   💰 delta_threshold: {config.delta_threshold}")
            
            # Lancer le système avec timeout
            logger.info("⏱️ Lancement avec timeout de 30 minutes...")
            await asyncio.wait_for(launcher.start_24_7_trading(), timeout=1800)  # 30 minutes
            
            logger.info("✅ Test terminé avec succès")
            break
            
        except asyncio.TimeoutError:
            logger.info("⏰ Timeout atteint (30 minutes) - Test terminé normalement")
            break
            
        except KeyboardInterrupt:
            logger.info("⏹️ Test CONSERVATEUR ROBUSTE arrêté par l'utilisateur")
            break
            
        except Exception as e:
            retry_count += 1
            logger.error(f"❌ Erreur test CONSERVATEUR ROBUSTE (tentative {retry_count}): {e}")
            
            if retry_count < max_retries:
                wait_time = retry_count * 30  # Attendre 30s, 60s, 90s...
                logger.info(f"⏳ Nouvelle tentative dans {wait_time} secondes...")
                await asyncio.sleep(wait_time)
            else:
                logger.error("💀 Nombre maximum de tentatives atteint - Arrêt du test")
                break
    
    logger.info("🏁 === TEST CONSERVATEUR ROBUSTE TERMINÉ ===")

if __name__ == "__main__":
    asyncio.run(main())
























