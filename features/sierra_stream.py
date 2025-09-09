#!/usr/bin/env python3
"""
🌊 SIERRA STREAM - MIA_IA_SYSTEM
================================

Lecteur non-bloquant des fichiers JSONL Sierra Chart
- Lecture en parallèle des charts 3, 4, 8, 10
- Détection automatique de rotation quotidienne
- Enrichissement des événements avec graph et ingest_ts
"""

import json
import time
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, AsyncIterator, Any
from dataclasses import dataclass
from collections import defaultdict

from core.logger import get_logger
from config.sierra_paths import DEFAULT_CHARTS, per_chart_daily_path, get_today_date_str

logger = get_logger(__name__)

@dataclass
class SierraEvent:
    """Événement Sierra enrichi"""
    raw_data: Dict[str, Any]
    graph: int
    ingest_ts: datetime
    file_path: Path
    
    @property
    def symbol(self) -> Optional[str]:
        """Symbole de l'événement"""
        return self.raw_data.get('sym')
    
    @property
    def event_type(self) -> Optional[str]:
        """Type d'événement"""
        return self.raw_data.get('type')
    
    @property
    def timestamp(self) -> Optional[str]:
        """Timestamp original"""
        return self.raw_data.get('t')

class SierraTail:
    """Lecteur non-bloquant des fichiers JSONL Sierra"""
    
    def __init__(self, 
                 charts: List[int] = None,
                 output_dir: Path = None,
                 poll_interval: float = 0.1,
                 max_events_per_poll: int = 100):
        
        self.charts = charts or DEFAULT_CHARTS.copy()
        self.output_dir = output_dir or Path(r"D:\MIA_IA_system")
        self.poll_interval = poll_interval
        self.max_events_per_poll = max_events_per_poll
        
        # État interne
        self.file_handles: Dict[int, Any] = {}
        self.file_positions: Dict[int, int] = {}
        self.current_date = get_today_date_str()
        self.is_running = False
        
        logger.info(f"SierraTail initialisé pour charts {self.charts}")
    
    async def start(self) -> None:
        """Démarre la lecture des fichiers"""
        self.is_running = True
        await self._open_files()
        logger.info("SierraTail démarré")
    
    async def stop(self) -> None:
        """Arrête la lecture des fichiers"""
        self.is_running = False
        await self._close_files()
        logger.info("SierraTail arrêté")
    
    async def _open_files(self) -> None:
        """Ouvre les fichiers pour la lecture"""
        for chart in self.charts:
            file_path = per_chart_daily_path(chart, self.current_date)
            try:
                if file_path.exists():
                    handle = open(file_path, 'r', encoding='utf-8')
                    # Positionner à la fin du fichier pour la lecture en continu
                    handle.seek(0, 2)  # SEEK_END
                    self.file_handles[chart] = handle
                    self.file_positions[chart] = handle.tell()
                    logger.debug(f"Fichier ouvert: {file_path}")
                else:
                    logger.warning(f"Fichier non trouvé: {file_path}")
            except Exception as e:
                logger.error(f"Erreur ouverture fichier {file_path}: {e}")
    
    async def _close_files(self) -> None:
        """Ferme les fichiers"""
        for handle in self.file_handles.values():
            try:
                handle.close()
            except Exception as e:
                logger.error(f"Erreur fermeture fichier: {e}")
        
        self.file_handles.clear()
        self.file_positions.clear()
    
    async def _check_date_rotation(self) -> bool:
        """Vérifie si une rotation de date est nécessaire"""
        new_date = get_today_date_str()
        if new_date != self.current_date:
            logger.info(f"Rotation de date détectée: {self.current_date} -> {new_date}")
            await self._close_files()
            self.current_date = new_date
            await self._open_files()
            return True
        return False
    
    async def _read_new_lines(self, chart: int) -> List[SierraEvent]:
        """Lit les nouvelles lignes d'un fichier chart"""
        events = []
        
        if chart not in self.file_handles:
            return events
        
        handle = self.file_handles[chart]
        current_pos = self.file_positions[chart]
        
        try:
            # Lire depuis la dernière position
            handle.seek(current_pos)
            new_lines = handle.readlines()
            
            # Traiter les nouvelles lignes
            for line in new_lines:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    event = SierraEvent(
                        raw_data=data,
                        graph=chart,
                        ingest_ts=datetime.now(timezone.utc),
                        file_path=per_chart_daily_path(chart, self.current_date)
                    )
                    events.append(event)
                except json.JSONDecodeError as e:
                    logger.warning(f"Ligne JSON invalide dans chart {chart}: {line[:100]}...")
                except Exception as e:
                    logger.error(f"Erreur traitement ligne chart {chart}: {e}")
            
            # Mettre à jour la position
            self.file_positions[chart] = handle.tell()
            
        except Exception as e:
            logger.error(f"Erreur lecture chart {chart}: {e}")
        
        return events
    
    async def events(self) -> AsyncIterator[SierraEvent]:
        """Générateur d'événements en continu"""
        logger.info("Démarrage du générateur d'événements")
        
        while self.is_running:
            try:
                # Vérifier la rotation de date
                await self._check_date_rotation()
                
                # Lire les nouveaux événements de tous les charts
                all_events = []
                for chart in self.charts:
                    events = await self._read_new_lines(chart)
                    all_events.extend(events)
                
                # Limiter le nombre d'événements par poll
                if len(all_events) > self.max_events_per_poll:
                    all_events = all_events[:self.max_events_per_poll]
                    logger.debug(f"Limitation à {self.max_events_per_poll} événements")
                
                # Yielder les événements
                for event in all_events:
                    yield event
                
                # Attendre avant le prochain poll
                if not all_events:
                    await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Erreur dans le générateur d'événements: {e}")
                await asyncio.sleep(self.poll_interval)
    
    async def read_events_once(self, max_events: int = 100) -> List[SierraEvent]:
        """Lit les événements une seule fois (pour tests)"""
        events = []
        
        for chart in self.charts:
            chart_events = await self._read_new_lines(chart)
            events.extend(chart_events)
        
        return events[:max_events]
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du lecteur"""
        return {
            'is_running': self.is_running,
            'charts': self.charts,
            'current_date': self.current_date,
            'open_files': len(self.file_handles),
            'file_positions': self.file_positions.copy(),
            'poll_interval': self.poll_interval,
            'max_events_per_poll': self.max_events_per_poll
        }

# === FONCTIONS UTILITAIRES ===

async def create_sierra_tail(charts: List[int] = None, **kwargs) -> SierraTail:
    """Factory pour créer un SierraTail"""
    tail = SierraTail(charts=charts, **kwargs)
    await tail.start()
    return tail

def parse_charts_string(charts_str: str) -> List[int]:
    """Parse une chaîne de charts (ex: "3,4,8,10")"""
    try:
        return [int(x.strip()) for x in charts_str.split(',') if x.strip()]
    except ValueError:
        logger.error(f"Format de charts invalide: {charts_str}")
        return DEFAULT_CHARTS

# === EXPORTS ===
__all__ = [
    'SierraEvent',
    'SierraTail',
    'create_sierra_tail',
    'parse_charts_string'
]
