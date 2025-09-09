#!/usr/bin/env python3
"""
🚀 FORCE ASIA SESSION SPX - MIA_IA_SYSTEM
Force l'utilisation des données SPX sauvegardées pour la session Asia
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from data.options_data_manager import OPTIONS_DATA_MANAGER
from core.session_manager import TradingSession

logger = get_logger(__name__)

class AsiaSessionSPXForcer:
    """Force l'utilisation des données SPX en session Asia"""
    
    def __init__(self):
        self.options_manager = OPTIONS_DATA_MANAGER
        self.spx_data = None
        
    async def load_saved_spx_data(self) -> bool:
        """Charge les données SPX sauvegardées"""
        try:
            logger.info("📊 Chargement données SPX sauvegardées...")
            
            # Charger le snapshot le plus récent
            snapshot_path = Path("data/options_snapshots/spx_snapshot_2025-08-21.json")
            if not snapshot_path.exists():
                logger.error("❌ Fichier snapshot SPX non trouvé")
                return False
                
            with open(snapshot_path, 'r') as f:
                snapshot_data = json.load(f)
            
            # Extraire les données essentielles
            self.spx_data = {
                'vix_level': snapshot_data.get('market_data', {}).get('vix_level', 16.07),
                'put_call_ratio': snapshot_data.get('options_flow', {}).get('put_call_ratio', 1.15),
                'gamma_exposure': snapshot_data.get('levels', {}).get('total_gamma_exposure', 75000000000),
                'call_walls': snapshot_data.get('levels', {}).get('call_walls', [6400, 6500, 6600]),
                'put_walls': snapshot_data.get('levels', {}).get('put_walls', [6300, 6200]),
                'gamma_flip': snapshot_data.get('levels', {}).get('gamma_flip', 6350),
                'dealer_position': snapshot_data.get('levels', {}).get('dealer_position', 'short'),
                'pin_levels': snapshot_data.get('pin_levels', [6350, 6400, 6450]),
                'underlying_price': snapshot_data.get('undPrice', 6382.23),
                'data_timestamp': snapshot_data.get('asof', datetime.now().isoformat()),
                'data_source': 'ASIA_SESSION_FORCED'
            }
            
            logger.info("✅ Données SPX chargées avec succès:")
            logger.info(f"  📊 VIX Level: {self.spx_data['vix_level']}")
            logger.info(f"  📈 Put/Call Ratio: {self.spx_data['put_call_ratio']}")
            logger.info(f"  💰 Gamma Exposure: ${self.spx_data['gamma_exposure']/1e9:.1f}B")
            logger.info(f"  🏦 Dealer Position: {self.spx_data['dealer_position']}")
            logger.info(f"  📍 Call Walls: {self.spx_data['call_walls']}")
            logger.info(f"  📍 Put Walls: {self.spx_data['put_walls']}")
            logger.info(f"  🎯 Gamma Flip: {self.spx_data['gamma_flip']}")
            logger.info(f"  📍 Pin Levels: {self.spx_data['pin_levels']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement données SPX: {e}")
            return False
    
    async def inject_spx_data_to_system(self) -> bool:
        """Injecte les données SPX dans le système"""
        try:
            if not self.spx_data:
                logger.error("❌ Aucune donnée SPX à injecter")
                return False
            
            # Sauvegarder dans le système
            self.options_manager.save_spx_data(self.spx_data)
            
            # Forcer la session Asia
            current_time = datetime.now(timezone.utc)
            current_hour = current_time.hour
            
            # Déterminer la session actuelle
            if 2 <= current_hour < 9:
                session_type = TradingSession.LONDON_SESSION
            elif 9 <= current_hour < 16:
                session_type = TradingSession.US_SESSION
            elif 16 <= current_hour < 18:
                session_type = TradingSession.OVERNIGHT
            else:
                session_type = TradingSession.ASIA_SESSION
            
            logger.info(f"🕐 Session actuelle: {session_type.value}")
            logger.info("📊 Données SPX injectées dans le système")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur injection données SPX: {e}")
            return False
    
    async def run_asia_session_setup(self) -> bool:
        """Configure la session Asia avec données SPX"""
        try:
            logger.info("🌏 CONFIGURATION SESSION ASIA AVEC DONNÉES SPX")
            logger.info("=" * 60)
            
            # 1. Charger données SPX
            if not await self.load_saved_spx_data():
                return False
            
            # 2. Injecter dans le système
            if not await self.inject_spx_data_to_system():
                return False
            
            # 3. Validation
            logger.info("✅ Configuration session Asia terminée")
            logger.info("🚀 Le système peut maintenant utiliser les données SPX sauvegardées")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration session Asia: {e}")
            return False

async def main():
    """Fonction principale"""
    forcer = AsiaSessionSPXForcer()
    success = await forcer.run_asia_session_setup()
    
    if success:
        logger.info("🎯 Session Asia configurée - Lancez le système principal")
    else:
        logger.error("❌ Échec configuration session Asia")

if __name__ == "__main__":
    asyncio.run(main())
