#!/usr/bin/env python3
"""
Lanceur Test MODÉRÉ
MIA_IA_SYSTEM - Configuration Win Rate 45-55% - Paramètres équilibrés
"""

import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
import logging

# Configuration de test MODÉRÉ
config_data = {
    "name": "MODÉRÉ",
    "description": "Win Rate 45-55% - Paramètres équilibrés",
    "expected_win_rate": "45-55%",
    "risk_level": "MOYEN"
}

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - MODERE - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/test_modéré.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = get_logger(__name__)

class TestConfig:
    """Configuration de test MODÉRÉ"""
    
    def get_orderflow_config(self):
        return {
            "min_confidence_threshold": 0.18,
            "footprint_threshold": 0.06,
            "volume_threshold": 12,
            "delta_threshold": 0.08,
            "lookback_periods": 10
        }
    
    def get_level2_config(self):
        return {
            "depth": 10,
            "update_frequency": 0.1
        }

async def main():
    """Lancement test MODÉRÉ"""
    
    logger.info("🚀 === TEST MODÉRÉ DÉMARRÉ ===")
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
    config.min_confidence_threshold = 0.18
    config.footprint_threshold = 0.06
    config.volume_threshold = 12
    config.delta_threshold = 0.08
    
    logger.info("✅ Configuration appliquée")
    logger.info(f"   📊 min_confidence_threshold: {config.min_confidence_threshold}")
    logger.info(f"   🎯 footprint_threshold: {config.footprint_threshold}")
    logger.info(f"   📈 volume_threshold: {config.volume_threshold}")
    logger.info(f"   💰 delta_threshold: {config.delta_threshold}")
    
    # Lancer le système
    try:
        await launcher.start_24_7_trading()
    except KeyboardInterrupt:
        logger.info("⏹️ Test MODÉRÉ arrêté par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur test MODÉRÉ: {e}")

if __name__ == "__main__":
    asyncio.run(main())
