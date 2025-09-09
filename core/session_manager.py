#!/usr/bin/env python3
"""
🕐 SESSION MANAGER - MIA_IA_SYSTEM
===================================

Gestionnaire de sessions de trading 24h/24 avec basculement automatique
entre données LIVE et sauvegardées selon les horaires de marché.

FONCTIONNALITÉS :
- ✅ Détection automatique des sessions (US, Londres, Asie, Overnight)
- ✅ Basculement automatique LIVE vs données sauvegardées
- ✅ Validation qualité données par session
- ✅ Adaptation des paramètres de trading par session
- ✅ Monitoring et alertes multi-sessions

Author: MIA_IA_SYSTEM
Version: 1.0.0
Date: Janvier 2025
"""

import asyncio
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from core.logger import get_logger

logger = get_logger(__name__)

class TradingSession(Enum):
    """Sessions de trading"""
    US_SESSION = "us_session"      # 9h30-16h EST
    LONDON_SESSION = "london_session"  # 2h-9h30 EST
    ASIA_SESSION = "asia_session"   # 18h-2h EST
    OVERNIGHT = "overnight"        # 16h-18h EST

class DataSource(Enum):
    """Sources de données"""
    LIVE_IBKR = "live_ibkr"       # Données temps réel IBKR
    SAVED_DATA = "saved_data"     # Données sauvegardées
    FALLBACK = "fallback"         # Données de secours

class SessionStatus(Enum):
    """Statuts de session"""
    ACTIVE = "active"             # Session active et trading
    INACTIVE = "inactive"         # Session inactive
    TRANSITION = "transition"     # Transition entre sessions
    ERROR = "error"               # Erreur session

@dataclass
class SessionConfig:
    """Configuration par session"""
    session_type: TradingSession
    data_source: DataSource
    trading_enabled: bool = True
    position_size_multiplier: float = 1.0
    risk_multiplier: float = 1.0
    min_confidence_threshold: float = 0.70
    max_data_age_hours: float = 18.0
    description: str = ""

@dataclass
class SessionState:
    """État d'une session"""
    session_type: TradingSession
    is_active: bool
    current_data_source: DataSource
    data_quality: str
    last_update: datetime
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

class SessionManager:
    """
    Gestionnaire de sessions de trading 24h/24
    """
    
    def __init__(self):
        # Configuration des sessions
        self.session_configs = self._initialize_session_configs()
        
        # État actuel
        self.current_session = None
        self.current_data_source = None
        self.session_start_time = None
        
        # Monitoring
        self.session_history = []
        self.last_session_check = None
        
        # Callbacks
        self.on_session_change = None
        self.on_data_source_change = None
        
        logger.info("🕐 SessionManager initialisé")
    
    def _initialize_session_configs(self) -> Dict[TradingSession, SessionConfig]:
        """Initialise les configurations par session"""
        return {
            TradingSession.US_SESSION: SessionConfig(
                session_type=TradingSession.US_SESSION,
                data_source=DataSource.LIVE_IBKR,
                trading_enabled=True,
                position_size_multiplier=1.0,
                risk_multiplier=1.0,
                min_confidence_threshold=0.70,
                max_data_age_hours=1.0,  # 1h max pour session US
                description="Session US - Données LIVE IBKR"
            ),
            TradingSession.LONDON_SESSION: SessionConfig(
                session_type=TradingSession.LONDON_SESSION,
                data_source=DataSource.SAVED_DATA,
                trading_enabled=True,
                position_size_multiplier=0.8,  # Réduire positions
                risk_multiplier=1.2,  # Plus prudent
                min_confidence_threshold=0.75,
                max_data_age_hours=18.0,
                description="Session Londres - Données sauvegardées"
            ),
            TradingSession.ASIA_SESSION: SessionConfig(
                session_type=TradingSession.ASIA_SESSION,
                data_source=DataSource.SAVED_DATA,
                trading_enabled=True,
                position_size_multiplier=0.6,  # Positions réduites
                risk_multiplier=1.5,  # Très prudent
                min_confidence_threshold=0.80,
                max_data_age_hours=18.0,
                description="Session Asie - Données sauvegardées"
            ),
            TradingSession.OVERNIGHT: SessionConfig(
                session_type=TradingSession.OVERNIGHT,
                data_source=DataSource.SAVED_DATA,
                trading_enabled=False,  # Pas de trading overnight
                position_size_multiplier=0.0,
                risk_multiplier=2.0,
                min_confidence_threshold=1.0,
                max_data_age_hours=18.0,
                description="Overnight - Pas de trading"
            )
        }
    
    def get_current_session(self) -> TradingSession:
        """Détermine la session actuelle basée sur l'heure EST"""
        now = datetime.now(timezone(timedelta(hours=-5)))  # EST timezone
        current_hour = now.hour
        current_minute = now.minute
        
        # Session US : 9h30-16h EST
        if (current_hour == 9 and current_minute >= 30) or (10 <= current_hour < 16):
            return TradingSession.US_SESSION
        
        # Session Londres : 2h-9h30 EST
        elif 2 <= current_hour < 9 or (current_hour == 9 and current_minute < 30):
            return TradingSession.LONDON_SESSION
        
        # Session Asie : 18h-2h EST
        elif current_hour >= 18 or current_hour < 2:
            return TradingSession.ASIA_SESSION
        
        # Overnight : 16h-18h EST
        else:
            return TradingSession.OVERNIGHT
    
    def get_session_config(self, session_type: Optional[TradingSession] = None) -> SessionConfig:
        """Récupère la configuration d'une session"""
        if session_type is None:
            session_type = self.get_current_session()
        
        return self.session_configs.get(session_type, self.session_configs[TradingSession.OVERNIGHT])
    
    def should_use_live_data(self, session_type: Optional[TradingSession] = None) -> bool:
        """Détermine si on doit utiliser les données LIVE"""
        if session_type is None:
            session_type = self.get_current_session()
        
        config = self.get_session_config(session_type)
        return config.data_source == DataSource.LIVE_IBKR
    
    def should_use_saved_data(self, session_type: Optional[TradingSession] = None) -> bool:
        """Détermine si on doit utiliser les données sauvegardées"""
        if session_type is None:
            session_type = self.get_current_session()
        
        config = self.get_session_config(session_type)
        return config.data_source == DataSource.SAVED_DATA
    
    def is_trading_enabled(self, session_type: Optional[TradingSession] = None) -> bool:
        """Vérifie si le trading est activé pour la session"""
        if session_type is None:
            session_type = self.get_current_session()
        
        config = self.get_session_config(session_type)
        return config.trading_enabled
    
    def get_position_size_multiplier(self, session_type: Optional[TradingSession] = None) -> float:
        """Récupère le multiplicateur de taille de position"""
        if session_type is None:
            session_type = self.get_current_session()
        
        config = self.get_session_config(session_type)
        return config.position_size_multiplier
    
    def get_risk_multiplier(self, session_type: Optional[TradingSession] = None) -> float:
        """Récupère le multiplicateur de risque"""
        if session_type is None:
            session_type = self.get_current_session()
        
        config = self.get_session_config(session_type)
        return config.risk_multiplier
    
    def get_min_confidence_threshold(self, session_type: Optional[TradingSession] = None) -> float:
        """Récupère le seuil de confiance minimum"""
        if session_type is None:
            session_type = self.get_current_session()
        
        config = self.get_session_config(session_type)
        return config.min_confidence_threshold
    
    def get_max_data_age_hours(self, session_type: Optional[TradingSession] = None) -> float:
        """Récupère l'âge maximum des données accepté"""
        if session_type is None:
            session_type = self.get_current_session()
        
        config = self.get_session_config(session_type)
        return config.max_data_age_hours
    
    async def check_session_change(self) -> bool:
        """
        Vérifie s'il y a eu un changement de session
        Retourne True si changement détecté
        """
        current_session = self.get_current_session()
        
        if self.current_session != current_session:
            old_session = self.current_session
            self.current_session = current_session
            
            # Mettre à jour la source de données
            config = self.get_session_config(current_session)
            self.current_data_source = config.data_source
            
            # Enregistrer le changement
            self.session_start_time = datetime.now(timezone.utc)
            self.session_history.append({
                'timestamp': self.session_start_time,
                'old_session': old_session.value if old_session else None,
                'new_session': current_session.value,
                'data_source': self.current_data_source.value
            })
            
            # Notifier le changement
            await self._notify_session_change(old_session, current_session)
            
            logger.info(f"🔄 Changement de session: {old_session.value if old_session else 'None'} → {current_session.value}")
            logger.info(f"📊 Source de données: {self.current_data_source.value}")
            logger.info(f"🎯 Trading activé: {config.trading_enabled}")
            
            return True
        
        return False
    
    async def _notify_session_change(self, old_session: Optional[TradingSession], new_session: TradingSession):
        """Notifie le changement de session"""
        if self.on_session_change:
            try:
                await self.on_session_change(old_session, new_session)
            except Exception as e:
                logger.error(f"❌ Erreur notification changement session: {e}")
    
    def get_session_state(self) -> SessionState:
        """Récupère l'état actuel de la session"""
        current_session = self.get_current_session()
        config = self.get_session_config(current_session)
        
        # Déterminer la qualité des données
        data_quality = "good"
        warnings = []
        errors = []
        
        if not config.trading_enabled:
            data_quality = "disabled"
            warnings.append("Trading désactivé pour cette session")
        
        if config.data_source == DataSource.SAVED_DATA:
            warnings.append("Utilisation de données sauvegardées")
        
        return SessionState(
            session_type=current_session,
            is_active=config.trading_enabled,
            current_data_source=self.current_data_source or config.data_source,
            data_quality=data_quality,
            last_update=datetime.now(timezone.utc),
            warnings=warnings,
            errors=errors
        )
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Récupère un résumé de la session actuelle"""
        current_session = self.get_current_session()
        config = self.get_session_config(current_session)
        state = self.get_session_state()
        
        return {
            'current_session': current_session.value,
            'session_description': config.description,
            'trading_enabled': config.trading_enabled,
            'data_source': self.current_data_source.value if self.current_data_source else config.data_source.value,
            'position_size_multiplier': config.position_size_multiplier,
            'risk_multiplier': config.risk_multiplier,
            'min_confidence_threshold': config.min_confidence_threshold,
            'max_data_age_hours': config.max_data_age_hours,
            'session_start_time': self.session_start_time.isoformat() if self.session_start_time else None,
            'data_quality': state.data_quality,
            'warnings': state.warnings,
            'errors': state.errors
        }
    
    def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère l'historique des sessions"""
        return self.session_history[-limit:] if self.session_history else []
    
    async def start_session_monitoring(self, check_interval_seconds: int = 60):
        """
        Démarre le monitoring automatique des sessions
        """
        logger.info(f"🕐 Démarrage monitoring sessions (intervalle: {check_interval_seconds}s)")
        
        while True:
            try:
                # Vérifier changement de session
                changed = await self.check_session_change()
                
                if changed:
                    # Attendre un peu après un changement
                    await asyncio.sleep(5)
                else:
                    # Attendre l'intervalle normal
                    await asyncio.sleep(check_interval_seconds)
                    
            except Exception as e:
                logger.error(f"❌ Erreur monitoring sessions: {e}")
                await asyncio.sleep(check_interval_seconds)
    
    def validate_data_for_session(self, data_age_hours: float, session_type: Optional[TradingSession] = None) -> Tuple[bool, List[str]]:
        """
        Valide si les données sont acceptables pour la session actuelle
        """
        if session_type is None:
            session_type = self.get_current_session()
        
        config = self.get_session_config(session_type)
        max_age = config.max_data_age_hours
        
        warnings = []
        is_valid = True
        
        if data_age_hours > max_age:
            is_valid = False
            warnings.append(f"Données trop anciennes ({data_age_hours:.1f}h > {max_age}h)")
        
        if data_age_hours > max_age * 0.8:  # 80% du seuil
            warnings.append(f"Données approchant du seuil d'âge ({data_age_hours:.1f}h)")
        
        return is_valid, warnings

def create_session_manager() -> SessionManager:
    """Factory function pour créer un SessionManager"""
    return SessionManager()

# === INSTANCE GLOBALE ===

_session_manager = None

def get_session_manager() -> SessionManager:
    """Retourne l'instance globale du SessionManager"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager

# Test du module
async def test_session_manager():
    """Test du SessionManager"""
    logger.info("🧪 Test SessionManager...")
    
    manager = create_session_manager()
    
    # Test détection session actuelle
    current_session = manager.get_current_session()
    logger.info(f"Session actuelle: {current_session.value}")
    
    # Test configuration session
    config = manager.get_session_config(current_session)
    logger.info(f"Configuration: {config.description}")
    logger.info(f"Trading activé: {config.trading_enabled}")
    logger.info(f"Source données: {config.data_source.value}")
    
    # Test validation données
    is_valid, warnings = manager.validate_data_for_session(5.0)
    logger.info(f"Validation données 5h: Valide={is_valid}, Warnings={warnings}")
    
    # Test état session
    state = manager.get_session_state()
    logger.info(f"État session: {state.data_quality}")
    
    # Test résumé
    summary = manager.get_session_summary()
    logger.info(f"Résumé: {summary['session_description']}")

if __name__ == "__main__":
    asyncio.run(test_session_manager())

