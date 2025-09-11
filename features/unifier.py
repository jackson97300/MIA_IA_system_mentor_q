#!/usr/bin/env python3
"""
🔗 UNIFIER - MIA_IA_SYSTEM
==========================

Écrivain du fichier unifié Sierra JSONL
- Écriture append-only vers mia_unified_{YYYYMMDD}.jsonl
- Filtrage optionnel via config/menthorq_runtime
- Support de tous les types d'événements
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

from core.logger import get_logger
from config.sierra_paths import unified_daily_path, get_today_date_str
from features.sierra_stream import SierraEvent

logger = get_logger(__name__)

@dataclass
class UnifyConfig:
    """Configuration pour l'unification"""
    enable_filtering: bool = False
    filter_menthorq: bool = True
    filter_trades: bool = False
    filter_quotes: bool = False
    filter_basedata: bool = False
    max_file_size_mb: Optional[int] = None
    compression_enabled: bool = False

class UnifiedWriter:
    """Écrivain du fichier unifié Sierra JSONL"""
    
    def __init__(self, 
                 output_dir: Path = None,
                 config: UnifyConfig = None,
                 date_str: str = None):
        
        self.output_dir = output_dir or Path(r"D:\MIA_IA_system")
        self.config = config or UnifyConfig()
        self.date_str = date_str or get_today_date_str()
        
        # État interne
        self.file_path = unified_daily_path(self.date_str)
        self.file_handle = None
        self.bytes_written = 0
        self.events_written = 0
        self.is_open = False
        
        # Filtres
        self.menthorq_filter = None
        if self.config.filter_menthorq:
            self._setup_menthorq_filter()
        
        logger.info(f"UnifiedWriter initialisé: {self.file_path}")
    
    def _setup_menthorq_filter(self) -> None:
        """Configure le filtre MenthorQ"""
        try:
            from config.menthorq_runtime import should_emit_level
            self.menthorq_filter = should_emit_level
            logger.debug("Filtre MenthorQ configuré")
        except ImportError:
            logger.warning("Filtre MenthorQ non disponible - écriture sans filtrage")
    
    async def open(self) -> None:
        """Ouvre le fichier pour l'écriture"""
        try:
            # S'assurer que le répertoire existe
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Ouvrir le fichier en mode append
            self.file_handle = open(self.file_path, 'a', encoding='utf-8')
            self.is_open = True
            
            # Obtenir la taille actuelle
            self.file_handle.seek(0, 2)  # SEEK_END
            self.bytes_written = self.file_handle.tell()
            
            logger.info(f"Fichier unifié ouvert: {self.file_path} ({self.bytes_written} bytes)")
            
        except Exception as e:
            logger.error(f"Erreur ouverture fichier unifié: {e}")
            raise
    
    async def close(self) -> None:
        """Ferme le fichier"""
        if self.file_handle:
            try:
                self.file_handle.close()
                self.is_open = False
                logger.info(f"Fichier unifié fermé: {self.events_written} événements, {self.bytes_written} bytes")
            except Exception as e:
                logger.error(f"Erreur fermeture fichier unifié: {e}")
    
    def _should_write_event(self, event: SierraEvent) -> tuple[bool, str]:
        """
        Détermine si un événement doit être écrit
        
        Returns:
            (should_write, reason)
        """
        if not self.config.enable_filtering:
            return True, "no_filtering"
        
        event_type = event.event_type
        
        # Filtrage par type
        if event_type == "menthorq_gamma_levels" or event_type == "menthorq_blind_spots" or event_type == "menthorq_swing_levels":
            # Forcer MenthorQ uniquement sur le graph 10
            if getattr(event, 'graph', None) != 10:
                return False, "menthorq_wrong_chart"
            if self.config.filter_menthorq and self.menthorq_filter:
                # Appliquer le filtre MenthorQ
                try:
                    symbol = event.symbol or "ES"
                    kind = event_type.replace("menthorq_", "").replace("_levels", "")
                    
                    # Extraire les données pour le filtre
                    price = event.raw_data.get('price')
                    if price is None:
                        return False, "menthorq_no_price"
                    
                    # Note: Le filtre complet nécessiterait last_value et last_emit_ts
                    # Pour l'instant, on écrit tout (peut être amélioré plus tard)
                    return True, "menthorq_emit"
                    
                except Exception as e:
                    logger.warning(f"Erreur filtre MenthorQ: {e}")
                    return True, "menthorq_error_fallback"
            return True, "menthorq_no_filter"
        
        elif event_type in ["trade", "quote"]:
            if self.config.filter_trades and event_type == "trade":
                return False, "trade_filtered"
            if self.config.filter_quotes and event_type == "quote":
                return False, "quote_filtered"
            return True, "trade_quote_ok"
        
        elif event_type == "basedata":
            if self.config.filter_basedata:
                return False, "basedata_filtered"
            return True, "basedata_ok"
        
        # Autres types (vwap, vva, pvwap, vix, depth, vap)
        return True, "other_type_ok"
    
    def _check_file_size(self) -> bool:
        """Vérifie si la taille du fichier dépasse la limite"""
        if self.config.max_file_size_mb is None:
            return True
        
        max_bytes = self.config.max_file_size_mb * 1024 * 1024
        return self.bytes_written < max_bytes
    
    async def route(self, event: SierraEvent) -> bool:
        """
        Route un événement vers le fichier unifié
        
        Args:
            event: Événement Sierra à écrire
            
        Returns:
            True si l'événement a été écrit, False sinon
        """
        if not self.is_open:
            logger.warning("UnifiedWriter non ouvert - événement ignoré")
            return False
        
        # Vérifier la taille du fichier
        if not self._check_file_size():
            logger.warning(f"Taille limite atteinte ({self.config.max_file_size_mb}MB) - événement ignoré")
            return False
        
        # Appliquer les filtres
        should_write, reason = self._should_write_event(event)
        if not should_write:
            logger.debug(f"Événement filtré ({reason}): {event.event_type}")
            return False
        
        try:
            # Préparer l'événement pour l'écriture
            unified_event = {
                't': event.timestamp,
                'sym': event.symbol,
                'graph': event.graph,
                'type': event.event_type,
                'ingest_ts': event.ingest_ts.isoformat(),
                'data': event.raw_data
            }
            
            # Écrire la ligne JSONL
            line = json.dumps(unified_event, ensure_ascii=False) + '\n'
            self.file_handle.write(line)
            self.file_handle.flush()
            
            # Mettre à jour les compteurs
            self.bytes_written += len(line.encode('utf-8'))
            self.events_written += 1
            
            logger.debug(f"Événement écrit ({reason}): {event.event_type} graph {event.graph}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur écriture événement: {e}")
            return False
    
    async def route_batch(self, events: List[SierraEvent]) -> int:
        """
        Route plusieurs événements en lot
        
        Args:
            events: Liste d'événements à écrire
            
        Returns:
            Nombre d'événements écrits
        """
        written = 0
        for event in events:
            if await self.route(event):
                written += 1
        return written
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'écriture"""
        return {
            'file_path': str(self.file_path),
            'is_open': self.is_open,
            'events_written': self.events_written,
            'bytes_written': self.bytes_written,
            'date': self.date_str,
            'config': {
                'enable_filtering': self.config.enable_filtering,
                'filter_menthorq': self.config.filter_menthorq,
                'filter_trades': self.config.filter_trades,
                'filter_quotes': self.config.filter_quotes,
                'filter_basedata': self.config.filter_basedata,
                'max_file_size_mb': self.config.max_file_size_mb
            }
        }

# === FONCTIONS UTILITAIRES ===

async def create_unified_writer(output_dir: Path = None, 
                               config: UnifyConfig = None,
                               date_str: str = None) -> UnifiedWriter:
    """Factory pour créer un UnifiedWriter"""
    writer = UnifiedWriter(output_dir=output_dir, config=config, date_str=date_str)
    await writer.open()
    return writer

def create_unify_config(enable_filtering: bool = False,
                       filter_menthorq: bool = True,
                       filter_trades: bool = False,
                       filter_quotes: bool = False,
                       filter_basedata: bool = False,
                       max_file_size_mb: Optional[int] = None) -> UnifyConfig:
    """Factory pour créer une configuration UnifyConfig"""
    return UnifyConfig(
        enable_filtering=enable_filtering,
        filter_menthorq=filter_menthorq,
        filter_trades=filter_trades,
        filter_quotes=filter_quotes,
        filter_basedata=filter_basedata,
        max_file_size_mb=max_file_size_mb
    )

# === EXPORTS ===
__all__ = [
    'UnifyConfig',
    'UnifiedWriter',
    'create_unified_writer',
    'create_unify_config'
]
