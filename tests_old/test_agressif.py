#!/usr/bin/env python3
"""
Lanceur Test AGRESSIF
MIA_IA_SYSTEM - Configuration Win Rate 50-60% - Paramètres optimistes
"""

import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
import logging

# Configuration de test AGRESSIF
config_data = {
    "name": "AGRESSIF",
    "description": "Win Rate 50-60% - Paramètres optimistes",
    "expected_win_rate": "50-60%",
    "risk_level": "ÉLEVÉ"
}

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - AGRESSIF - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/test_agressif.log'),
        logging.StreamHandler()
    ]
)
logger = get_logger(__name__)

class TestConfig:
    """Configuration de test AGRESSIF"""
    
    def get_orderflow_config(self):
        return {
            "min_confidence_threshold": 0.22,
            "footprint_threshold": 0.08,
            "volume_threshold": 15,
            "delta_threshold": 0.12,
            "lookback_periods": 10
        }
    
    def get_level2_config(self):
        return {
            "depth": 10,
            "update_frequency": 0.1
        }

async def main():
    """Lancement test AGRESSIF"""
    
    logger.info("🚀 === TEST AGRESSIF DÉMARRÉ ===")
    logger.info(f"📊 Configuration: {config_data['description']}")
    logger.info(f"🎯 Win Rate attendu: {config_data['expected_win_rate']}")
    logger.info(f"⚠️ Niveau de risque: {config_data['risk_level']}")
    
    # Créer dossier logs
    from pathlib import Path
    Path("logs").mkdir(exist_ok=True)
    
    # Importer et lancer le système
    from launch_24_7_orderflow_trading import OrderFlow24_7Launcher
    
    launcher = OrderFlow24_7Launcher(live_trading=False)
    
    # Override configuration
    config = launcher._create_24_7_orderflow_config()
    
    # Appliquer paramètres de test
    config.min_confidence_threshold = 0.22
    config.footprint_threshold = 0.08
    config.volume_threshold = 15
    config.delta_threshold = 0.12
    
    logger.info("✅ Configuration appliquée")
    logger.info(f"   📊 min_confidence_threshold: {config.min_confidence_threshold}")
    logger.info(f"   🎯 footprint_threshold: {config.footprint_threshold}")
    logger.info(f"   📈 volume_threshold: {config.volume_threshold}")
    logger.info(f"   💰 delta_threshold: {config.delta_threshold}")
    
    # Lancer le système
    try:
        await launcher.start_24_7_trading()
    except KeyboardInterrupt:
        logger.info("⏹️ Test AGRESSIF arrêté par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur test AGRESSIF: {e}")

if __name__ == "__main__":
    asyncio.run(main())
