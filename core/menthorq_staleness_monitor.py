#!/usr/bin/env python3
"""
🔍 MENTHORQ STALENESS MONITOR - MIA_IA_SYSTEM
==============================================

Système de monitoring automatique de la staleness des niveaux MenthorQ
- Monitoring en temps réel avec alertes automatiques
- Dashboard de surveillance avec métriques
- Intégration avec le système de trading
- Alertes Discord/Log selon la configuration
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import time
import asyncio
from collections import defaultdict, deque

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger

# Imports des composants existants
try:
    from core.menthorq_staleness_manager import get_staleness_manager, check_menthorq_staleness
    from config.menthorq_rules_loader import get_menthorq_rules
    STALENESS_MANAGER_AVAILABLE = True
except ImportError:
    STALENESS_MANAGER_AVAILABLE = False

# Import centralisé des enums (migration sécurisée)
try:
    from core.enums import AlertLevel
except ImportError:
    # Fallback pour compatibilité (sera supprimé après migration)
    class AlertLevel(Enum):
        """Niveaux d'alerte - FALLBACK"""
        INFO = "info"
        WARNING = "warning"
        CRITICAL = "critical"
        EMERGENCY = "emergency"

logger = get_logger(__name__)

class AlertChannel(Enum):
    """Canaux d'alerte"""
    LOG = "log"
    DISCORD = "discord"
    EMAIL = "email"
    WEBHOOK = "webhook"

@dataclass
class StalenessAlert:
    """Alerte de staleness"""
    timestamp: datetime
    source_id: str
    symbol: str
    data_type: str
    alert_level: AlertLevel
    message: str
    age_seconds: float
    max_age_seconds: int
    vix_regime: str
    severity: str
    channels: List[AlertChannel] = field(default_factory=list)

@dataclass
class MonitoringConfig:
    """Configuration du monitoring"""
    check_interval_seconds: int = 30
    alert_cooldown_seconds: int = 300  # 5 minutes entre alertes pour la même source
    max_alerts_per_hour: int = 10
    enable_discord_alerts: bool = False
    enable_email_alerts: bool = False
    enable_webhook_alerts: bool = False
    webhook_url: Optional[str] = None
    discord_webhook_url: Optional[str] = None
    email_recipients: List[str] = field(default_factory=list)
    vix_level: float = 20.0  # Niveau VIX par défaut pour les checks

@dataclass
class MonitoringStats:
    """Statistiques du monitoring"""
    total_checks: int = 0
    alerts_sent: int = 0
    sources_monitored: int = 0
    last_check_time: Optional[datetime] = None
    last_alert_time: Optional[datetime] = None
    alerts_by_level: Dict[str, int] = field(default_factory=dict)
    alerts_by_source: Dict[str, int] = field(default_factory=dict)
    uptime_seconds: float = 0.0

class MenthorQStalenessMonitor:
    """Moniteur automatique de staleness MenthorQ"""
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        """
        Initialisation du moniteur de staleness
        
        Args:
            config: Configuration du monitoring
        """
        self.config = config or MonitoringConfig()
        self.logger = get_logger(f"{__name__}.MenthorQStalenessMonitor")
        
        # État du monitoring
        self.is_running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Statistiques
        self.stats = MonitoringStats()
        self.start_time = datetime.now(timezone.utc)
        
        # Historique des alertes
        self.alert_history: deque = deque(maxlen=1000)
        self.last_alert_times: Dict[str, datetime] = {}
        self.alerts_this_hour: Dict[str, int] = defaultdict(int)
        
        # Sources à surveiller
        self.monitored_sources: List[Dict[str, Any]] = []
        
        # Callbacks d'alerte
        self.alert_callbacks: List[Callable[[StalenessAlert], None]] = []
        
        self.logger.info(f"🔍 MenthorQStalenessMonitor initialisé (config_available: {STALENESS_MANAGER_AVAILABLE})")
    
    def add_monitored_source(self, symbol: str, data_type: str, 
                           expected_frequency_seconds: int = 60) -> None:
        """
        Ajoute une source à surveiller
        
        Args:
            symbol: Symbole (ES, NQ, etc.)
            data_type: Type de données (gamma_levels, blind_spots, swing_levels)
            expected_frequency_seconds: Fréquence attendue
        """
        source = {
            'symbol': symbol,
            'data_type': data_type,
            'expected_frequency_seconds': expected_frequency_seconds,
            'source_id': f"{symbol}_{data_type}"
        }
        
        self.monitored_sources.append(source)
        self.stats.sources_monitored = len(self.monitored_sources)
        
        self.logger.info(f"📊 Source ajoutée au monitoring: {source['source_id']}")
    
    def add_alert_callback(self, callback: Callable[[StalenessAlert], None]) -> None:
        """
        Ajoute un callback d'alerte
        
        Args:
            callback: Fonction appelée lors d'une alerte
        """
        self.alert_callbacks.append(callback)
        self.logger.debug(f"📞 Callback d'alerte ajouté: {callback.__name__}")
    
    def start_monitoring(self) -> bool:
        """
        Démarre le monitoring automatique
        
        Returns:
            bool: True si démarré avec succès
        """
        if self.is_running:
            self.logger.warning("⚠️ Monitoring déjà en cours")
            return False
        
        if not STALENESS_MANAGER_AVAILABLE:
            self.logger.error("❌ StalenessManager non disponible - monitoring impossible")
            return False
        
        if not self.monitored_sources:
            self.logger.warning("⚠️ Aucune source à surveiller - ajoutez des sources d'abord")
            return False
        
        try:
            self.is_running = True
            self.stop_event.clear()
            
            # Démarrer le thread de monitoring
            self.monitor_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True,
                name="MenthorQStalenessMonitor"
            )
            self.monitor_thread.start()
            
            self.logger.info(f"🚀 Monitoring démarré - {len(self.monitored_sources)} sources surveillées")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage monitoring: {e}")
            self.is_running = False
            return False
    
    def stop_monitoring(self) -> None:
        """Arrête le monitoring automatique"""
        if not self.is_running:
            return
        
        self.logger.info("🛑 Arrêt du monitoring...")
        self.is_running = False
        self.stop_event.set()
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        
        self.logger.info("✅ Monitoring arrêté")
    
    def _monitoring_loop(self) -> None:
        """Boucle principale de monitoring"""
        self.logger.info("🔄 Boucle de monitoring démarrée")
        
        while self.is_running and not self.stop_event.is_set():
            try:
                # Effectuer un cycle de monitoring
                self._monitoring_cycle()
                
                # Attendre avant le prochain cycle
                self.stop_event.wait(self.config.check_interval_seconds)
                
            except Exception as e:
                self.logger.error(f"❌ Erreur dans la boucle de monitoring: {e}")
                time.sleep(5)  # Pause avant de réessayer
        
        self.logger.info("🔄 Boucle de monitoring terminée")
    
    def _monitoring_cycle(self) -> None:
        """Effectue un cycle de monitoring"""
        self.stats.total_checks += 1
        self.stats.last_check_time = datetime.now(timezone.utc)
        
        # Vérifier chaque source surveillée
        for source in self.monitored_sources:
            try:
                self._check_source_staleness(source)
            except Exception as e:
                self.logger.error(f"❌ Erreur vérification source {source['source_id']}: {e}")
        
        # Nettoyer les compteurs horaires
        self._cleanup_hourly_counters()
    
    def _check_source_staleness(self, source: Dict[str, Any]) -> None:
        """Vérifie la staleness d'une source"""
        source_id = source['source_id']
        symbol = source['symbol']
        data_type = source['data_type']
        
        # Vérifier la staleness
        staleness_result = check_menthorq_staleness(symbol, data_type, self.config.vix_level)
        
        # Déterminer le niveau d'alerte
        alert_level = self._determine_alert_level(staleness_result)
        
        # Vérifier si on doit envoyer une alerte
        if alert_level != AlertLevel.INFO and self._should_send_alert(source_id, alert_level):
            self._send_alert(source, staleness_result, alert_level)
    
    def _determine_alert_level(self, staleness_result) -> AlertLevel:
        """Détermine le niveau d'alerte basé sur le résultat de staleness"""
        if not staleness_result.is_stale:
            return AlertLevel.INFO
        
        if staleness_result.severity == "CRITICAL":
            return AlertLevel.CRITICAL
        elif staleness_result.severity == "WARNING":
            return AlertLevel.WARNING
        else:
            return AlertLevel.INFO
    
    def _should_send_alert(self, source_id: str, alert_level: AlertLevel) -> bool:
        """Détermine si on doit envoyer une alerte"""
        now = datetime.now(timezone.utc)
        
        # Vérifier le cooldown
        if source_id in self.last_alert_times:
            time_since_last = (now - self.last_alert_times[source_id]).total_seconds()
            if time_since_last < self.config.alert_cooldown_seconds:
                return False
        
        # Vérifier la limite horaire
        hour_key = now.strftime("%Y-%m-%d-%H")
        if self.alerts_this_hour[hour_key] >= self.config.max_alerts_per_hour:
            return False
        
        return True
    
    def _send_alert(self, source: Dict[str, Any], staleness_result, alert_level: AlertLevel) -> None:
        """Envoie une alerte de staleness"""
        now = datetime.now(timezone.utc)
        
        # Créer l'alerte
        alert = StalenessAlert(
            timestamp=now,
            source_id=source['source_id'],
            symbol=source['symbol'],
            data_type=source['data_type'],
            alert_level=alert_level,
            message=self._create_alert_message(source, staleness_result),
            age_seconds=staleness_result.age_seconds,
            max_age_seconds=staleness_result.max_age_seconds,
            vix_regime=staleness_result.vix_regime,
            severity=staleness_result.severity,
            channels=self._get_alert_channels(alert_level)
        )
        
        # Envoyer l'alerte
        self._dispatch_alert(alert)
        
        # Mettre à jour les statistiques
        self.stats.alerts_sent += 1
        self.stats.last_alert_time = now
        self.stats.alerts_by_level[alert_level.value] = self.stats.alerts_by_level.get(alert_level.value, 0) + 1
        self.stats.alerts_by_source[source['source_id']] = self.stats.alerts_by_source.get(source['source_id'], 0) + 1
        
        # Enregistrer l'historique
        self.alert_history.append(alert)
        self.last_alert_times[source['source_id']] = now
        
        # Mettre à jour le compteur horaire
        hour_key = now.strftime("%Y-%m-%d-%H")
        self.alerts_this_hour[hour_key] += 1
        
        self.logger.warning(f"🚨 Alerte {alert_level.value.upper()}: {alert.message}")
    
    def _create_alert_message(self, source: Dict[str, Any], staleness_result) -> str:
        """Crée le message d'alerte"""
        age_minutes = staleness_result.age_seconds / 60
        max_age_minutes = staleness_result.max_age_seconds / 60
        
        return (f"Staleness {staleness_result.severity} détectée: "
                f"{source['source_id']} - "
                f"Âge: {age_minutes:.1f}min (max: {max_age_minutes:.1f}min) - "
                f"VIX: {staleness_result.vix_regime}")
    
    def _get_alert_channels(self, alert_level: AlertLevel) -> List[AlertChannel]:
        """Détermine les canaux d'alerte selon le niveau"""
        channels = [AlertChannel.LOG]  # Toujours log
        
        if alert_level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
            if self.config.enable_discord_alerts:
                channels.append(AlertChannel.DISCORD)
            if self.config.enable_webhook_alerts:
                channels.append(AlertChannel.WEBHOOK)
            if self.config.enable_email_alerts:
                channels.append(AlertChannel.EMAIL)
        
        return channels
    
    def _dispatch_alert(self, alert: StalenessAlert) -> None:
        """Dispatch l'alerte vers les canaux configurés"""
        # Appeler les callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"❌ Erreur callback alerte: {e}")
        
        # Envoyer vers les canaux configurés
        for channel in alert.channels:
            try:
                if channel == AlertChannel.LOG:
                    self._send_log_alert(alert)
                elif channel == AlertChannel.DISCORD:
                    self._send_discord_alert(alert)
                elif channel == AlertChannel.WEBHOOK:
                    self._send_webhook_alert(alert)
                elif channel == AlertChannel.EMAIL:
                    self._send_email_alert(alert)
            except Exception as e:
                self.logger.error(f"❌ Erreur envoi alerte {channel.value}: {e}")
    
    def _send_log_alert(self, alert: StalenessAlert) -> None:
        """Envoie l'alerte vers les logs"""
        level = alert.alert_level.value.upper()
        self.logger.warning(f"🚨 [{level}] {alert.message}")
    
    def _send_discord_alert(self, alert: StalenessAlert) -> None:
        """Envoie l'alerte vers Discord"""
        # TODO: Implémenter l'envoi Discord
        self.logger.info(f"📱 Discord alerte: {alert.message}")
    
    def _send_webhook_alert(self, alert: StalenessAlert) -> None:
        """Envoie l'alerte vers webhook"""
        # TODO: Implémenter l'envoi webhook
        self.logger.info(f"🔗 Webhook alerte: {alert.message}")
    
    def _send_email_alert(self, alert: StalenessAlert) -> None:
        """Envoie l'alerte par email"""
        # TODO: Implémenter l'envoi email
        self.logger.info(f"📧 Email alerte: {alert.message}")
    
    def _cleanup_hourly_counters(self) -> None:
        """Nettoie les compteurs horaires anciens"""
        now = datetime.now(timezone.utc)
        current_hour = now.strftime("%Y-%m-%d-%H")
        
        # Supprimer les compteurs des heures précédentes
        keys_to_remove = [key for key in self.alerts_this_hour.keys() if key != current_hour]
        for key in keys_to_remove:
            del self.alerts_this_hour[key]
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Retourne le statut du monitoring"""
        uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        
        return {
            'is_running': self.is_running,
            'sources_monitored': len(self.monitored_sources),
            'total_checks': self.stats.total_checks,
            'alerts_sent': self.stats.alerts_sent,
            'uptime_seconds': uptime,
            'last_check_time': self.stats.last_check_time.isoformat() if self.stats.last_check_time else None,
            'last_alert_time': self.stats.last_alert_time.isoformat() if self.stats.last_alert_time else None,
            'alerts_by_level': self.stats.alerts_by_level,
            'alerts_by_source': self.stats.alerts_by_source,
            'recent_alerts': len(self.alert_history)
        }
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retourne les alertes récentes"""
        recent = list(self.alert_history)[-limit:]
        return [
            {
                'timestamp': alert.timestamp.isoformat(),
                'source_id': alert.source_id,
                'alert_level': alert.alert_level.value,
                'message': alert.message,
                'severity': alert.severity
            }
            for alert in recent
        ]

# Instance globale
_global_monitor: Optional[MenthorQStalenessMonitor] = None

def get_menthorq_staleness_monitor() -> MenthorQStalenessMonitor:
    """Retourne l'instance globale du moniteur de staleness"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = MenthorQStalenessMonitor()
    return _global_monitor

def create_menthorq_staleness_monitor(config: Optional[MonitoringConfig] = None) -> MenthorQStalenessMonitor:
    """Crée une nouvelle instance du moniteur de staleness"""
    return MenthorQStalenessMonitor(config)

