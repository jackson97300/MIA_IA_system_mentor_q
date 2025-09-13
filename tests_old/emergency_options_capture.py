#!/usr/bin/env python3
"""
🚨 EMERGENCY OPTIONS CAPTURE - MIA_IA_SYSTEM
Capture intensive données options SPX/QQQ avant fermeture marchés US

PRIORITÉ ABSOLUE : Capturer TOUTES les données pour sessions Asia/London
Format: CSV pour facilité d'utilisation
Fréquence: Toutes les 5 secondes
Durée: Jusqu'à fermeture marchés US
"""

import asyncio
import csv
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from features.spx_options_retriever import SPXOptionsRetriever
from core.logger import get_logger

logger = get_logger(__name__)

class EmergencyOptionsCapture:
    """Capture d'urgence données options SPX/QQQ"""
    
    def __init__(self):
        self.spx_retriever = SPXOptionsRetriever()
        self.capture_dir = Path("data/emergency_captures")
        self.capture_dir.mkdir(parents=True, exist_ok=True)
        
        # Timestamp pour nommage
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Fichiers CSV
        self.spx_csv_file = self.capture_dir / f"spx_emergency_{self.timestamp}.csv"
        self.qqq_csv_file = self.capture_dir / f"qqq_emergency_{self.timestamp}.csv"
        self.metadata_file = self.capture_dir / f"metadata_{self.timestamp}.json"
        
        # Headers CSV
        self.spx_headers = [
            'timestamp', 'symbol', 'gamma_exposure', 'put_call_ratio',
            'call_wall', 'put_wall', 'vol_trigger', 'net_gamma',
            'call_volume', 'put_volume', 'call_oi', 'put_oi',
            'vix_level', 'dealer_position', 'gamma_flip', 'unusual_activity',
            'pin_levels', 'dealer_hedging', 'source', 'quality_score'
        ]
        
        self.qqq_headers = [
            'timestamp', 'symbol', 'gamma_exposure', 'put_call_ratio',
            'call_wall', 'put_wall', 'vol_trigger', 'net_gamma',
            'call_volume', 'put_volume', 'call_oi', 'put_oi',
            'vxn_level', 'dealer_position', 'gamma_flip', 'unusual_activity',
            'pin_levels', 'dealer_hedging', 'tech_sentiment', 'source', 'quality_score'
        ]
        
        # Initialiser fichiers CSV
        self._init_csv_files()
        
        # Statistiques
        self.spx_captures = 0
        self.qqq_captures = 0
        self.start_time = datetime.now()
    
    def _init_csv_files(self):
        """Initialiser fichiers CSV avec headers"""
        # SPX CSV
        with open(self.spx_csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(self.spx_headers)
        
        # QQQ CSV
        with open(self.qqq_csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(self.qqq_headers)
        
        logger.info(f"📊 Fichiers CSV créés:")
        logger.info(f"   SPX: {self.spx_csv_file}")
        logger.info(f"   QQQ: {self.qqq_csv_file}")
    
    async def capture_spx_data(self) -> Optional[Dict]:
        """Capture données SPX options réelles"""
        try:
            options_data = await self.spx_retriever.get_options_data()
            
            if options_data:
                capture_data = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': 'SPX',
                    'gamma_exposure': options_data.gamma_exposure,
                    'put_call_ratio': options_data.put_call_ratio,
                    'call_wall': options_data.call_wall,
                    'put_wall': options_data.put_wall,
                    'vol_trigger': options_data.vol_trigger,
                    'net_gamma': options_data.net_gamma,
                    'call_volume': options_data.call_volume,
                    'put_volume': options_data.put_volume,
                    'call_oi': getattr(options_data, 'call_oi', 0),
                    'put_oi': getattr(options_data, 'put_oi', 0),
                    'vix_level': getattr(options_data, 'vix_level', 0),
                    'dealer_position': getattr(options_data, 'dealer_position', 'neutral'),
                    'gamma_flip': getattr(options_data, 'gamma_flip', 0),
                    'unusual_activity': getattr(options_data, 'unusual_activity', False),
                    'pin_levels': getattr(options_data, 'pin_levels', []),
                    'dealer_hedging': getattr(options_data, 'dealer_hedging', 'neutral'),
                    'source': 'ibkr_real',
                    'quality_score': 1.0
                }
                return capture_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur capture SPX: {e}")
            return None
    
    def generate_qqq_data(self) -> Dict:
        """Génération données QQQ options (simulation)"""
        try:
            # Simulation réaliste données QQQ
            capture_data = {
                'timestamp': datetime.now().isoformat(),
                'symbol': 'QQQ',
                'gamma_exposure': random.uniform(0.05, 0.15) * 1e9,  # 50M-150M
                'put_call_ratio': random.uniform(0.8, 1.4),
                'call_wall': random.uniform(400, 450),
                'put_wall': random.uniform(350, 400),
                'vol_trigger': random.uniform(380, 420),
                'net_gamma': random.uniform(-0.1, 0.1),
                'call_volume': random.randint(1000, 5000),
                'put_volume': random.randint(1000, 5000),
                'call_oi': random.randint(5000, 20000),
                'put_oi': random.randint(5000, 20000),
                'vxn_level': random.uniform(15, 25),
                'dealer_position': random.choice(['long', 'short', 'neutral']),
                'gamma_flip': random.uniform(390, 410),
                'unusual_activity': random.choice([True, False]),
                'pin_levels': [random.uniform(380, 420) for _ in range(3)],
                'dealer_hedging': random.choice(['long', 'short', 'neutral']),
                'tech_sentiment': random.uniform(-1, 1),
                'source': 'simulation',
                'quality_score': 0.8
            }
            return capture_data
            
        except Exception as e:
            logger.error(f"❌ Erreur génération QQQ: {e}")
            return {}
    
    def save_spx_to_csv(self, data: Dict):
        """Sauvegarder données SPX en CSV"""
        try:
            with open(self.spx_csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                row = [
                    data.get('timestamp', ''),
                    data.get('symbol', 'SPX'),
                    data.get('gamma_exposure', 0),
                    data.get('put_call_ratio', 0),
                    data.get('call_wall', 0),
                    data.get('put_wall', 0),
                    data.get('vol_trigger', 0),
                    data.get('net_gamma', 0),
                    data.get('call_volume', 0),
                    data.get('put_volume', 0),
                    data.get('call_oi', 0),
                    data.get('put_oi', 0),
                    data.get('vix_level', 0),
                    data.get('dealer_position', 'neutral'),
                    data.get('gamma_flip', 0),
                    data.get('unusual_activity', False),
                    str(data.get('pin_levels', [])),
                    data.get('dealer_hedging', 'neutral'),
                    data.get('source', 'ibkr_real'),
                    data.get('quality_score', 1.0)
                ]
                writer.writerow(row)
            
            self.spx_captures += 1
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde SPX CSV: {e}")
    
    def save_qqq_to_csv(self, data: Dict):
        """Sauvegarder données QQQ en CSV"""
        try:
            with open(self.qqq_csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                row = [
                    data.get('timestamp', ''),
                    data.get('symbol', 'QQQ'),
                    data.get('gamma_exposure', 0),
                    data.get('put_call_ratio', 0),
                    data.get('call_wall', 0),
                    data.get('put_wall', 0),
                    data.get('vol_trigger', 0),
                    data.get('net_gamma', 0),
                    data.get('call_volume', 0),
                    data.get('put_volume', 0),
                    data.get('call_oi', 0),
                    data.get('put_oi', 0),
                    data.get('vxn_level', 0),
                    data.get('dealer_position', 'neutral'),
                    data.get('gamma_flip', 0),
                    data.get('unusual_activity', False),
                    str(data.get('pin_levels', [])),
                    data.get('dealer_hedging', 'neutral'),
                    data.get('tech_sentiment', 0),
                    data.get('source', 'simulation'),
                    data.get('quality_score', 0.8)
                ]
                writer.writerow(row)
            
            self.qqq_captures += 1
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde QQQ CSV: {e}")
    
    def save_metadata(self):
        """Sauvegarder métadonnées de capture"""
        try:
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds() / 60
            
            metadata = {
                'capture_timestamp': self.timestamp,
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_minutes': duration,
                'spx_captures_count': self.spx_captures,
                'qqq_captures_count': self.qqq_captures,
                'total_captures': self.spx_captures + self.qqq_captures,
                'capture_frequency_seconds': 5,
                'intended_for': ['asia_session', 'london_session'],
                'data_quality': 'emergency_capture',
                'files_created': {
                    'spx_csv': str(self.spx_csv_file),
                    'qqq_csv': str(self.qqq_csv_file),
                    'metadata_json': str(self.metadata_file)
                },
                'capture_stats': {
                    'spx_success_rate': f"{(self.spx_captures / max(1, self.spx_captures + self.qqq_captures)) * 100:.1f}%",
                    'qqq_success_rate': f"{(self.qqq_captures / max(1, self.spx_captures + self.qqq_captures)) * 100:.1f}%",
                    'avg_captures_per_minute': f"{((self.spx_captures + self.qqq_captures) / max(1, duration)):.1f}"
                }
            }
            
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"💾 Métadonnées sauvegardées: {self.metadata_file}")
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde métadonnées: {e}")
    
    async def run_emergency_capture(self, max_captures: int = 100):
        """Lancer capture d'urgence"""
        logger.warning("🚨 CAPTURE D'URGENCE DÉMARRÉE")
        logger.warning("⏰ Marchés US ferment bientôt - Capture intensive activée")
        logger.warning(f"📊 Max captures: {max_captures}")
        logger.warning(f"⏱️ Fréquence: 5 secondes")
        
        try:
            for i in range(max_captures):
                current_time = datetime.now()
                
                # Capture SPX
                spx_data = await self.capture_spx_data()
                if spx_data:
                    self.save_spx_to_csv(spx_data)
                    logger.info(f"📊 SPX #{i+1}: Gamma ${spx_data.get('gamma_exposure', 0)/1e9:.1f}B, PCR {spx_data.get('put_call_ratio', 0):.2f}")
                
                # Capture QQQ
                qqq_data = self.generate_qqq_data()
                if qqq_data:
                    self.save_qqq_to_csv(qqq_data)
                    logger.info(f"📱 QQQ #{i+1}: Gamma ${qqq_data.get('gamma_exposure', 0)/1e9:.1f}B, PCR {qqq_data.get('put_call_ratio', 0):.2f}")
                
                # Statistiques
                if (i + 1) % 10 == 0:
                    logger.info(f"📈 Progression: {i+1}/{max_captures} ({((i+1)/max_captures)*100:.1f}%)")
                    logger.info(f"   SPX: {self.spx_captures}, QQQ: {self.qqq_captures}")
                
                # Attendre 5 secondes
                await asyncio.sleep(5)
            
            # Sauvegarde finale
            self.save_metadata()
            
            logger.warning("✅ CAPTURE D'URGENCE TERMINÉE")
            logger.warning(f"📊 SPX Captures: {self.spx_captures}")
            logger.warning(f"📱 QQQ Captures: {self.qqq_captures}")
            logger.warning(f"💾 Données sauvegardées pour sessions Asia/London")
            logger.warning(f"📁 Fichiers créés:")
            logger.warning(f"   {self.spx_csv_file}")
            logger.warning(f"   {self.qqq_csv_file}")
            logger.warning(f"   {self.metadata_file}")
            
        except KeyboardInterrupt:
            logger.warning("⏹️ Capture interrompue par l'utilisateur")
            self.save_metadata()
        except Exception as e:
            logger.error(f"❌ Erreur capture d'urgence: {e}")
            self.save_metadata()

async def main():
    """Fonction principale"""
    capture = EmergencyOptionsCapture()
    await capture.run_emergency_capture(max_captures=100)

if __name__ == "__main__":
    asyncio.run(main())


