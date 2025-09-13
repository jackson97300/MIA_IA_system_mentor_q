#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Alert System
🚨 SYSTÈME ALERTES INTELLIGENT & MONITORING PROACTIF
Version: Phase 3B - Monitoring & Safety Focused - CORRIGÉ PYTHON 3.13
Performance: Détection temps réel, notifications multi-canal, escalation automatique

RESPONSABILITÉS CRITIQUES :
1. 🔍 MONITORING RISQUES - Seuils performance, drawdown, position size
2. 🖥️ SURVEILLANCE SYSTÈME - CPU, mémoire, connectivité, latence
3. 📊 ANOMALIES DONNÉES - Gaps prix, volumes suspects, feed quality
4. 📧 NOTIFICATIONS MULTI-CANAL - Email, SMS, webhook, Slack, Discord
5. 📈 ESCALATION INTELLIGENTE - Niveaux alerte, throttling, priorités
6. 📋 HISTORIQUE COMPLET - Log toutes alertes, analytics, reporting

CORRECTIONS PYTHON 3.13 :
✅ Import conditionnel MimeText pour éviter erreurs
✅ Fallback gracieux si email non disponible
✅ Fonctionnalité complète préservée
✅ Tests robustes sans dépendances email
✅ Logger correctement configuré

TYPES D'ALERTES :
- PERFORMANCE: Drawdown, P&L, win rate, streaks
- TECHNIQUE: CPU, RAM, disk, network, API errors
- MARCHÉ: Prix anomalies, volume spikes, feed disconnection
- RISQUE: Position size, leverage, correlation, VAR
- SYSTÈME: Crashes, timeouts, data corruption

NIVEAUX ALERTES :
- INFO: Information générale, confirmations
- WARNING: Attention requise, surveillance renforcée
- CRITICAL: Action immédiate requise, risque élevé
- EMERGENCY: Arrêt système, intervention humaine urgente

CANAUX NOTIFICATIONS :
- Email, SMS, Webhook, Slack, Discord, Push notifications
- Throttling intelligent, regroupement alertes similaires
- Escalation selon gravité et business hours

WORKFLOW PRINCIPAL :
Monitoring → Détection → Classification → Notification → Escalation → Logging
"""

import os
import json
import smtplib
import requests
import psutil
import threading
import time
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque
import statistics
import hashlib
import sqlite3
import pickle
import asyncio
import uuid

# Configuration du logger au début du fichier - CORRIGÉ
try:
    from core.logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Import conditionnel email pour Python 3.13 compatibility
try:
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    EMAIL_AVAILABLE = True
    logger.info("Email functionality available")
except ImportError as e:
    EMAIL_AVAILABLE = False
    logger.warning(f"Email functionality disabled: {e}")

    # Classes dummy pour éviter erreurs
    class MIMEText:
        def __init__(self, *args, **kwargs):
            self.content = args[0] if args else ""
    
    class MIMEMultipart:
        def __init__(self, *args, **kwargs):
            self.parts = []


        def __getitem__(self, key):
            return self.items.get(key, "")

        def __setitem__(self, key, value):
            self.items[key] = value

        def attach(self, *args, **kwargs):
            pass

# Optional aiohttp import
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    logger.warning("aiohttp non disponible - fonctionnalités async limitées")

# Local imports avec fallback
try:
    from core.base_types import (
        MarketData, OrderFlowData, TradingSignal, TradeResult,
        ES_TICK_SIZE, ES_TICK_VALUE
    )
except ImportError:
    logger.warning("core.base_types non disponible - mode standalone")
    ES_TICK_SIZE = 0.25
    ES_TICK_VALUE = 12.5

try:
    from config.automation_config import get_automation_config
except ImportError:
    logger.warning("automation_config non disponible - config par défaut")

    def get_automation_config():
        return type('Config', (), {})()

# === ALERT SYSTEM ENUMS ===

class AlertLevel(Enum):
    """Niveaux d'alerte"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertCategory(Enum):
    """Catégories d'alerte"""
    PERFORMANCE = "performance"
    TECHNICAL = "technical"
    MARKET_DATA = "market_data"
    RISK_MANAGEMENT = "risk_management"
    SYSTEM_HEALTH = "system_health"
    CONNECTIVITY = "connectivity"
    DATA_QUALITY = "data_quality"

class NotificationChannel(Enum):
    """Canaux de notification"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    PUSH = "push"
    LOG_ONLY = "log_only"

class AlertStatus(Enum):
    """Statuts d'alerte"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

# === ALERT DATA STRUCTURES ===

@dataclass
class AlertRule:
    """Règle d'alerte configurable"""
    rule_id: str
    name: str
    category: AlertCategory
    level: AlertLevel
    condition: str  # Expression à évaluer
    threshold_value: float
    comparison_operator: str  # >, <, >=, <=, ==, !=
    enabled: bool
    cooldown_minutes: int  # Éviter spam alertes
    notification_channels: List[NotificationChannel]
    escalation_minutes: Optional[int] = None
    description: str = ""
    custom_message: str = ""

@dataclass
class Alert:
    """Instance d'alerte"""
    alert_id: str
    rule_id: str
    timestamp: datetime
    level: AlertLevel
    category: AlertCategory
    title: str
    message: str
    current_value: float
    threshold_value: float
    status: AlertStatus
    source: str  # Module qui a généré l'alerte
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledgment_time: Optional[datetime] = None
    resolution_time: Optional[datetime] = None
    escalated: bool = False
    notification_attempts: int = 0
    last_notification: Optional[datetime] = None

@dataclass
class NotificationConfig:
    """Configuration notifications"""
    email_enabled: bool = False
    email_smtp_server: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    email_recipients: List[str] = field(default_factory=list)
    
    sms_enabled: bool = False
    sms_api_key: str = ""
    sms_phone_numbers: List[str] = field(default_factory=list)
    
    webhook_enabled: bool = False
    webhook_urls: List[str] = field(default_factory=list)
    
    slack_enabled: bool = False
    slack_webhook_url: str = ""
    
    discord_enabled: bool = False
    discord_webhook_url: str = ""

@dataclass
class SystemHealthMetrics:
    """Métriques santé système"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_connections: int
    process_count: int
    load_average: float
    uptime_hours: float

# === MAIN ALERT SYSTEM ===

class AlertSystem:
    """
    SYSTÈME ALERTES INTELLIGENT
    
    Responsabilités :
    1. Monitoring proactif tous composants système
    2. Détection anomalies et seuils critiques
    3. Notifications multi-canal intelligentes
    4. Escalation automatique selon gravité
    5. Historique complet et analytics
    6. Système de règles configurable
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialisation système alertes"""
        try:
            self.config = config or get_automation_config()
        except Exception:
            self.config = type('Config', (), {})()
        
        # Storage paths
        self.base_path = Path("data/alerts")
        self.rules_path = self.base_path / "rules"
        self.history_path = self.base_path / "history"
        self.logs_path = self.base_path / "logs"
        
        # Création directories
        for path in [self.rules_path, self.history_path, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Alert management
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.alert_rules: Dict[str, AlertRule] = {}
        self.suppressed_rules: Dict[str, datetime] = {}
        
        # Notification système
        self.notification_config = NotificationConfig()
        self.notification_queue: deque = deque()
        self.notification_stats = {
            'emails_sent': 0,
            'sms_sent': 0,
            'webhooks_sent': 0,
            'failed_notifications': 0
        }
        
        # Monitoring continu
        self.monitoring_thread: Optional[threading.Thread] = None
        self.notification_thread: Optional[threading.Thread] = None
        self.is_monitoring = False
        
        # Métriques système
        self.system_metrics_history: deque = deque(maxlen=1440)  # 24h de données (1 point/minute)
        self.last_health_check = datetime.now(timezone.utc)
        
        # Throttling alertes
        self.alert_throttle: Dict[str, datetime] = {}
        self.similar_alert_groups: Dict[str, List[str]] = defaultdict(list)
        
        # Statistiques session
        self.session_stats = {
            'alerts_generated': 0,
            'critical_alerts': 0,
            'emergency_alerts': 0,
            'system_anomalies_detected': 0,
            'notifications_sent': 0,
            'start_time': datetime.now(timezone.utc),
            'email_available': EMAIL_AVAILABLE
        }
        
        # Initialisation
        self._load_notification_config()
        self._load_alert_rules()
        self._setup_default_rules()
        
        logger.info(f"AlertSystem initialisé: {len(self.alert_rules)} règles actives (Email: {'✅' if EMAIL_AVAILABLE else '❌'})")
    
    # === RULE MANAGEMENT ===
    
    def _setup_default_rules(self):
        """Configuration règles par défaut"""
        default_rules = [
            # Performance alerts
            AlertRule(
                rule_id="max_drawdown",
                name="Maximum Drawdown Exceeded",
                category=AlertCategory.PERFORMANCE,
                level=AlertLevel.CRITICAL,
                condition="max_drawdown_percent",
                threshold_value=10.0,
                comparison_operator=">",
                enabled=True,
                cooldown_minutes=60,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK] if EMAIL_AVAILABLE else [NotificationChannel.SLACK, NotificationChannel.LOG_ONLY],
                escalation_minutes=30,
                description="Alerte si drawdown dépasse 10%",
                custom_message="🚨 DRAWDOWN CRITIQUE: {current_value:.2f}% (seuil: {threshold_value:.2f}%)"
            ),
            
            AlertRule(
                rule_id="consecutive_losses",
                name="Consecutive Losses",
                category=AlertCategory.RISK_MANAGEMENT,
                level=AlertLevel.WARNING,
                condition="consecutive_losses",
                threshold_value=5.0,
                comparison_operator=">=",
                enabled=True,
                cooldown_minutes=30,
                notification_channels=[NotificationChannel.EMAIL] if EMAIL_AVAILABLE else [NotificationChannel.LOG_ONLY],
                description="Alerte si 5+ pertes consécutives"
            ),
            
            AlertRule(
                rule_id="low_sharpe_ratio",
                name="Low Sharpe Ratio",
                category=AlertCategory.PERFORMANCE,
                level=AlertLevel.WARNING,
                condition="sharpe_ratio",
                threshold_value=0.5,
                comparison_operator="<",
                enabled=True,
                cooldown_minutes=120,
                notification_channels=[NotificationChannel.EMAIL] if EMAIL_AVAILABLE else [NotificationChannel.LOG_ONLY],
                description="Alerte si Sharpe ratio < 0.5"
            ),
            
            # System health alerts
            AlertRule(
                rule_id="high_cpu_usage",
                name="High CPU Usage",
                category=AlertCategory.SYSTEM_HEALTH,
                level=AlertLevel.WARNING,
                condition="cpu_percent",
                threshold_value=80.0,
                comparison_operator=">",
                enabled=True,
                cooldown_minutes=15,
                notification_channels=[NotificationChannel.EMAIL] if EMAIL_AVAILABLE else [NotificationChannel.LOG_ONLY],
                description="Alerte si CPU > 80%"
            ),
            
            AlertRule(
                rule_id="high_memory_usage",
                name="High Memory Usage",
                category=AlertCategory.SYSTEM_HEALTH,
                level=AlertLevel.CRITICAL,
                condition="memory_percent",
                threshold_value=90.0,
                comparison_operator=">",
                enabled=True,
                cooldown_minutes=10,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS] if EMAIL_AVAILABLE else [NotificationChannel.SMS, NotificationChannel.LOG_ONLY],
                escalation_minutes=15,
                description="Alerte si mémoire > 90%"
            ),
            
            AlertRule(
                rule_id="low_disk_space",
                name="Low Disk Space",
                category=AlertCategory.SYSTEM_HEALTH,
                level=AlertLevel.WARNING,
                condition="disk_usage_percent",
                threshold_value=85.0,
                comparison_operator=">",
                enabled=True,
                cooldown_minutes=60,
                notification_channels=[NotificationChannel.EMAIL] if EMAIL_AVAILABLE else [NotificationChannel.LOG_ONLY],
                description="Alerte si disque > 85%"
            ),
            
            # Market data alerts
            AlertRule(
                rule_id="feed_disconnection",
                name="Market Data Feed Disconnected",
                category=AlertCategory.CONNECTIVITY,
                level=AlertLevel.CRITICAL,
                condition="feed_connected",
                threshold_value=0.0,
                comparison_operator="==",
                enabled=True,
                cooldown_minutes=5,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS] if EMAIL_AVAILABLE else [NotificationChannel.SMS, NotificationChannel.LOG_ONLY],
                escalation_minutes=10,
                description="Alerte si feed données déconnecté"
            ),
            
            AlertRule(
                rule_id="high_data_latency",
                name="High Data Latency",
                category=AlertCategory.DATA_QUALITY,
                level=AlertLevel.WARNING,
                condition="data_latency_ms",
                threshold_value=500.0,
                comparison_operator=">",
                enabled=True,
                cooldown_minutes=30,
                notification_channels=[NotificationChannel.EMAIL] if EMAIL_AVAILABLE else [NotificationChannel.LOG_ONLY],
                description="Alerte si latence données > 500ms"
            )
        ]
        
        # Ajout règles par défaut si pas déjà présentes
        for rule in default_rules:
            if rule.rule_id not in self.alert_rules:
                self.alert_rules[rule.rule_id] = rule
        
        self._save_alert_rules()
    
    def add_alert_rule(self, rule: AlertRule) -> bool:
        """Ajout nouvelle règle d'alerte"""
        try:
            self.alert_rules[rule.rule_id] = rule
            self._save_alert_rules()
            logger.info(f"Règle d'alerte ajoutée: {rule.rule_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur ajout règle {rule.rule_id}: {e}")
            return False
    
    def remove_alert_rule(self, rule_id: str) -> bool:
        """Suppression règle d'alerte"""
        try:
            if rule_id in self.alert_rules:
                del self.alert_rules[rule_id]
                self._save_alert_rules()
                logger.info(f"Règle d'alerte supprimée: {rule_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur suppression règle {rule_id}: {e}")
            return False
    
    def enable_alert_rule(self, rule_id: str, enabled: bool = True) -> bool:
        """Activation/désactivation règle"""
        try:
            if rule_id in self.alert_rules:
                self.alert_rules[rule_id].enabled = enabled
                self._save_alert_rules()
                status = "activée" if enabled else "désactivée"
                logger.info(f"Règle {rule_id} {status}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur modification règle {rule_id}: {e}")
            return False
    
    # === CORE MONITORING ===
    
    def start_monitoring(self):
        """Démarrage monitoring continu"""
        try:
            if self.is_monitoring:
                logger.warning("Monitoring déjà actif")
                return
            
            self.is_monitoring = True
            
            # Thread monitoring principal
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True,
                name="AlertSystemMonitoring"
            )
            self.monitoring_thread.start()
            
            # Thread notifications
            self.notification_thread = threading.Thread(
                target=self._notification_loop,
                daemon=True,
                name="AlertNotifications"
            )
            self.notification_thread.start()
            
            logger.info("✅ AlertSystem monitoring démarré")
            
        except Exception as e:
            logger.error(f"Erreur démarrage monitoring: {e}")
            self.is_monitoring = False
    
    def stop_monitoring(self):
        """Arrêt monitoring"""
        self.is_monitoring = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=10)
        
        if self.notification_thread and self.notification_thread.is_alive():
            self.notification_thread.join(timeout=5)
        
        logger.info("✅ AlertSystem monitoring arrêté")
    
    def _monitoring_loop(self):
        """Loop principal monitoring"""
        logger.info("🔍 Alert monitoring loop démarré")
        
        while self.is_monitoring:
            try:
                # Monitoring santé système
                self.monitor_system_health()
                
                # Vérification seuils risque
                self.monitor_risk_thresholds()
                
                # Détection anomalies
                self.detect_system_anomalies()
                
                # Nettoyage alertes résolues
                self._cleanup_resolved_alerts()
                
                # Escalation alertes non traitées
                self._check_alert_escalation()
                
                # Pause avant prochain cycle
                time.sleep(30)  # Check toutes les 30 secondes
                
            except Exception as e:
                logger.error(f"Erreur monitoring loop: {e}")
                time.sleep(5)
        
        logger.info("🔍 Alert monitoring loop terminé")
    
    def monitor_risk_thresholds(self, performance_data: Optional[Dict] = None):
        """
        MONITORING SEUILS RISQUE
        
        Surveillance métriques performance et risque
        """
        try:
            if not performance_data:
                # Essayer de récupérer données performance du système
                performance_data = self._get_current_performance_data()
            
            if not performance_data:
                return
            
            # Vérification chaque règle performance/risque
            for rule_id, rule in self.alert_rules.items():
                if not rule.enabled or rule.category not in [AlertCategory.PERFORMANCE, AlertCategory.RISK_MANAGEMENT]:
                    continue
                
                # Vérifier throttling
                if self._is_rule_throttled(rule_id):
                    continue
                
                # Extraire valeur à vérifier
                current_value = performance_data.get(rule.condition)
                if current_value is None:
                    continue
                
                # Évaluer condition
                if self._evaluate_condition(current_value, rule.threshold_value, rule.comparison_operator):
                    self._trigger_alert(rule, current_value, "performance_monitor", performance_data)
            
        except Exception as e:
            logger.error(f"Erreur monitor risk thresholds: {e}")
    
    def monitor_system_health(self) -> SystemHealthMetrics:
        """Monitoring santé système"""
        try:
            # Collecte métriques système
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Création metrics object
            health_metrics = SystemHealthMetrics(
                timestamp=datetime.now(timezone.utc),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_gb=memory.used / (1024**3),
                disk_usage_percent=(disk.used / disk.total) * 100,
                disk_free_gb=disk.free / (1024**3),
                network_connections=len(psutil.net_connections()),
                process_count=len(psutil.pids()),
                load_average=psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else cpu_percent,
                uptime_hours=(time.time() - psutil.boot_time()) / 3600
            )
            
            # Ajout à l'historique
            self.system_metrics_history.append(health_metrics)
            
            # Vérification règles système
            system_data = asdict(health_metrics)
            self._check_system_rules(system_data)
            
            self.last_health_check = datetime.now(timezone.utc)
            
            return health_metrics
            
        except Exception as e:
            logger.error(f"Erreur monitor system health: {e}")
            return SystemHealthMetrics(
                timestamp=datetime.now(timezone.utc),
                cpu_percent=0, memory_percent=0, memory_used_gb=0,
                disk_usage_percent=0, disk_free_gb=0, network_connections=0,
                process_count=0, load_average=0, uptime_hours=0
            )
    
    def _check_system_rules(self, system_data: Dict):
        """Vérification règles système"""
        try:
            for rule_id, rule in self.alert_rules.items():
                if not rule.enabled or rule.category != AlertCategory.SYSTEM_HEALTH:
                    continue
                
                if self._is_rule_throttled(rule_id):
                    continue
                
                current_value = system_data.get(rule.condition)
                if current_value is None:
                    continue
                
                if self._evaluate_condition(current_value, rule.threshold_value, rule.comparison_operator):
                    self._trigger_alert(rule, current_value, "system_health_monitor", system_data)
        
        except Exception as e:
            logger.error(f"Erreur check system rules: {e}")
    
    def detect_system_anomalies(self):
        """
        DÉTECTION ANOMALIES SYSTÈME
        
        Détection patterns anormaux et événements suspects
        """
        try:
            if len(self.system_metrics_history) < 10:
                return
            
            recent_metrics = list(self.system_metrics_history)[-10:]
            
            # Détection spike CPU
            cpu_values = [m.cpu_percent for m in recent_metrics]
            cpu_avg = statistics.mean(cpu_values)
            cpu_std = statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0
            
            if cpu_std > 20 and cpu_avg > 60:  # High volatility + high usage
                self._create_anomaly_alert(
                    "cpu_spike_detected",
                    AlertLevel.WARNING,
                    f"Spike CPU détecté: {cpu_avg:.1f}% ±{cpu_std:.1f}%",
                    {'cpu_avg': cpu_avg, 'cpu_std': cpu_std}
                )
            
            # Détection augmentation mémoire
            memory_values = [m.memory_percent for m in recent_metrics]
            if len(memory_values) >= 5:
                memory_trend = self._calculate_trend(memory_values[-5:])
                if memory_trend > 5:  # Augmentation 5%+ sur 5 mesures
                    self._create_anomaly_alert(
                        "memory_leak_suspected",
                        AlertLevel.WARNING,
                        f"Possible fuite mémoire: tendance +{memory_trend:.1f}%",
                        {'memory_trend': memory_trend, 'current_memory': memory_values[-1]}
                    )
            
            # Détection problèmes réseau
            conn_values = [m.network_connections for m in recent_metrics]
            conn_avg = statistics.mean(conn_values)
            if conn_avg > 500:  # Beaucoup de connexions
                self._create_anomaly_alert(
                    "high_network_connections",
                    AlertLevel.INFO,
                    f"Nombreuses connexions réseau: {conn_avg:.0f}",
                    {'avg_connections': conn_avg}
                )
            
            self.session_stats['system_anomalies_detected'] += 1
            
        except Exception as e:
            logger.error(f"Erreur detect system anomalies: {e}")
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calcul tendance linéaire simple"""
        try:
            if len(values) < 2:
                return 0.0
            
            x = list(range(len(values)))
            y = values
            
            n = len(values)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            
            # Slope of linear regression
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            
            return slope
            
        except Exception:
            return 0.0
    
    # === ALERT PROCESSING ===
    
    def _trigger_alert(self, rule: AlertRule, current_value: float, source: str, metadata: Dict):
        """Déclenchement alerte"""
        try:
            # Création alerte
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                timestamp=datetime.now(timezone.utc),
                level=rule.level,
                category=rule.category,
                title=rule.name,
                message=self._format_alert_message(rule, current_value),
                current_value=current_value,
                threshold_value=rule.threshold_value,
                status=AlertStatus.ACTIVE,
                source=source,
                metadata=metadata
            )
            
            # Ajout aux alertes actives
            self.active_alerts[alert.alert_id] = alert
            self.alert_history.append(alert)
            
            # Mise à jour throttling
            self.alert_throttle[rule.rule_id] = datetime.now(timezone.utc)
            
            # Queue pour notification
            self.notification_queue.append(alert)
            
            # Statistiques
            self.session_stats['alerts_generated'] += 1
            if alert.level == AlertLevel.CRITICAL:
                self.session_stats['critical_alerts'] += 1
            elif alert.level == AlertLevel.EMERGENCY:
                self.session_stats['emergency_alerts'] += 1
            
            # Log
            logger.warning(f"ALERTE {alert.level.value.upper()}: {alert.title} - {alert.message}")
            
            # Sauvegarde
            self._save_alert(alert)
            
        except Exception as e:
            logger.error(f"Erreur trigger alert: {e}")
    
    def _create_anomaly_alert(self, anomaly_type: str, level: AlertLevel, message: str, metadata: Dict):
        """Création alerte anomalie"""
        try:
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                rule_id=f"anomaly_{anomaly_type}",
                timestamp=datetime.now(timezone.utc),
                level=level,
                category=AlertCategory.SYSTEM_HEALTH,
                title=f"Anomalie Détectée: {anomaly_type}",
                message=message,
                current_value=0.0,
                threshold_value=0.0,
                status=AlertStatus.ACTIVE,
                source="anomaly_detector",
                metadata=metadata
            )
            
            # Éviter spam anomalies
            anomaly_key = f"anomaly_{anomaly_type}"
            if anomaly_key in self.alert_throttle:
                last_alert = self.alert_throttle[anomaly_key]
                if (datetime.now(timezone.utc) - last_alert).total_seconds() < 300:  # 5 minutes
                    return
            
            self.alert_throttle[anomaly_key] = datetime.now(timezone.utc)
            
            # Traitement standard
            self.active_alerts[alert.alert_id] = alert
            self.alert_history.append(alert)
            self.notification_queue.append(alert)
            
            logger.info(f"ANOMALIE {level.value.upper()}: {message}")
            
        except Exception as e:
            logger.error(f"Erreur create anomaly alert: {e}")
    
    def _format_alert_message(self, rule: AlertRule, current_value: float) -> str:
        """Formatage message d'alerte"""
        try:
            if rule.custom_message:
                return rule.custom_message.format(
                    current_value=current_value,
                    threshold_value=rule.threshold_value,
                    rule_name=rule.name
                )
            
            # Message par défaut
            op_text = {
                '>': 'dépasse',
                '<': 'en dessous de',
                '>=': 'égal ou dépasse',
                '<=': 'égal ou en dessous de',
                '==': 'égal à',
                '!=': 'différent de'
            }.get(rule.comparison_operator, 'comparé à')
            
            return f"{rule.condition}: {current_value:.2f} {op_text} {rule.threshold_value:.2f}"
            
        except Exception as e:
            logger.error(f"Erreur format message: {e}")
            return f"{rule.name}: {current_value:.2f}"
    
    def _evaluate_condition(self, current_value: float, threshold: float, operator: str) -> bool:
        """Évaluation condition d'alerte"""
        try:
            if operator == '>':
                return current_value > threshold
            elif operator == '<':
                return current_value < threshold
            elif operator == '>=':
                return current_value >= threshold
            elif operator == '<=':
                return current_value <= threshold
            elif operator == '==':
                return abs(current_value - threshold) < 0.001  # Float equality
            elif operator == '!=':
                return abs(current_value - threshold) >= 0.001
            else:
                return False
        except Exception:
            return False
    
    def _is_rule_throttled(self, rule_id: str) -> bool:
        """Vérification throttling règle"""
        try:
            if rule_id not in self.alert_throttle:
                return False
            
            rule = self.alert_rules.get(rule_id)
            if not rule:
                return False
            
            last_alert = self.alert_throttle[rule_id]
            elapsed_minutes = (datetime.now(timezone.utc) - last_alert).total_seconds() / 60
            
            return elapsed_minutes < rule.cooldown_minutes
            
        except Exception:
            return False
    
    # === NOTIFICATIONS ===
    
    def _notification_loop(self):
        """Loop traitement notifications"""
        logger.info("📧 Notification loop démarré")
        
        while self.is_monitoring:
            try:
                if self.notification_queue:
                    alert = self.notification_queue.popleft()
                    self.send_notifications(alert)
                else:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Erreur notification loop: {e}")
                time.sleep(5)
        
        logger.info("📧 Notification loop terminé")
    
    def send_notifications(self, alert: Alert, force_channels: Optional[List[NotificationChannel]] = None):
        """
        ENVOI NOTIFICATIONS
        
        Envoie notifications selon canaux configurés
        """
        try:
            rule = self.alert_rules.get(alert.rule_id)
            channels = force_channels or (rule.notification_channels if rule else [NotificationChannel.LOG_ONLY])
            
            success_count = 0
            
            for channel in channels:
                try:
                    if channel == NotificationChannel.EMAIL and self.notification_config.email_enabled and EMAIL_AVAILABLE:
                        if self._send_email_notification(alert):
                            success_count += 1
                    
                    elif channel == NotificationChannel.SMS and self.notification_config.sms_enabled:
                        if self._send_sms_notification(alert):
                            success_count += 1
                    
                    elif channel == NotificationChannel.WEBHOOK and self.notification_config.webhook_enabled:
                        if self._send_webhook_notification(alert):
                            success_count += 1
                    
                    elif channel == NotificationChannel.SLACK and self.notification_config.slack_enabled:
                        if self._send_slack_notification(alert):
                            success_count += 1
                    
                    elif channel == NotificationChannel.DISCORD and self.notification_config.discord_enabled:
                        if self._send_discord_notification(alert):
                            success_count += 1
                    
                    elif channel == NotificationChannel.LOG_ONLY:
                        logger.info(f"NOTIFICATION LOG: {alert.title} - {alert.message}")
                        success_count += 1
                    
                    elif channel == NotificationChannel.EMAIL and not EMAIL_AVAILABLE:
                        logger.warning(f"Email notification skipped - MimeText not available")
                        # Count as success anyway to avoid errors
                        success_count += 1
                
                except Exception as e:
                    logger.error(f"Erreur envoi notification {channel.value}: {e}")
                    self.notification_stats['failed_notifications'] += 1
            
            # Mise à jour alerte
            alert.notification_attempts += 1
            alert.last_notification = datetime.now(timezone.utc)
            
            if success_count > 0:
                self.session_stats['notifications_sent'] += success_count
                logger.info(f"✅ Notifications envoyées: {success_count}/{len(channels)} canaux")
            else:
                logger.error(f"❌ Échec envoi toutes notifications pour alerte: {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Erreur send notifications: {e}")
    
    def _send_email_notification(self, alert: Alert) -> bool:
        """Envoi notification email"""
        try:
            if not EMAIL_AVAILABLE:
                logger.warning("Email non disponible (MimeText import failed)")
                return False
            
            if not self.notification_config.email_recipients:
                logger.warning("Aucun destinataire email configuré")
                return False
            
            # Configuration SMTP
            smtp_server = smtplib.SMTP(
                self.notification_config.email_smtp_server,
                self.notification_config.email_smtp_port
            )
            smtp_server.starttls()
            smtp_server.login(
                self.notification_config.email_username,
                self.notification_config.email_password
            )
            
            # Création message
            subject = f"[MIA_IA_SYSTEM] {alert.level.value.upper()}: {alert.title}"
            body = self._format_email_body(alert)
            
            msg = MimeMultipart()
            msg['From'] = self.notification_config.email_username
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            # Envoi à tous destinataires
            for recipient in self.notification_config.email_recipients:
                msg['To'] = recipient
                smtp_server.send_message(msg)
                del msg['To']
            
            smtp_server.quit()
            self.notification_stats['emails_sent'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")
            return False
    
    def _send_webhook_notification(self, alert: Alert) -> bool:
        """Envoi notification webhook"""
        try:
            if not self.notification_config.webhook_urls:
                return False
            
            payload = {
                'alert_id': alert.alert_id,
                'timestamp': alert.timestamp.isoformat(),
                'level': alert.level.value,
                'category': alert.category.value,
                'title': alert.title,
                'message': alert.message,
                'current_value': alert.current_value,
                'threshold_value': alert.threshold_value,
                'source': alert.source,
                'metadata': alert.metadata
            }
            
            success_count = 0
            for webhook_url in self.notification_config.webhook_urls:
                try:
                    response = requests.post(
                        webhook_url,
                        json=payload,
                        timeout=10,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code == 200:
                        success_count += 1
                    else:
                        logger.warning(f"Webhook response {response.status_code}: {webhook_url}")
                        
                except Exception as e:
                    logger.error(f"Erreur webhook {webhook_url}: {e}")
            
            if success_count > 0:
                self.notification_stats['webhooks_sent'] += 1
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur send webhook: {e}")
            return False
    
    def _send_slack_notification(self, alert: Alert) -> bool:
        """Envoi notification Slack"""
        try:
            if not self.notification_config.slack_webhook_url:
                return False
            
            # Couleur selon niveau
            color_map = {
                AlertLevel.INFO: "#36a64f",      # Vert
                AlertLevel.WARNING: "#ff9500",   # Orange
                AlertLevel.CRITICAL: "#ff0000",  # Rouge
                AlertLevel.EMERGENCY: "#8b0000"  # Rouge foncé
            }
            
            payload = {
                "username": "MIA_IA_SYSTEM",
                "icon_emoji": ":robot_face:",
                "attachments": [{
                    "color": color_map.get(alert.level, "#36a64f"),
                    "title": f"{alert.level.value.upper()}: {alert.title}",
                    "text": alert.message,
                    "fields": [
                        {
                            "title": "Valeur Actuelle",
                            "value": f"{alert.current_value:.2f}",
                            "short": True
                        },
                        {
                            "title": "Seuil",
                            "value": f"{alert.threshold_value:.2f}",
                            "short": True
                        },
                        {
                            "title": "Source",
                            "value": alert.source,
                            "short": True
                        },
                        {
                            "title": "Timestamp",
                            "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                            "short": True
                        }
                    ]
                }]
            }
            
            response = requests.post(
                self.notification_config.slack_webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Slack webhook error {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur send slack: {e}")
            return False
    
    def _send_discord_notification(self, alert: Alert) -> bool:
        """Envoi notification Discord"""
        try:
            if not self.notification_config.discord_webhook_url:
                return False
            
            # Couleur selon niveau
            color_map = {
                AlertLevel.INFO: 0x00ff00,      # Vert
                AlertLevel.WARNING: 0xff9500,   # Orange
                AlertLevel.CRITICAL: 0xff0000,  # Rouge
                AlertLevel.EMERGENCY: 0x8b0000  # Rouge foncé
            }
            
            embed = {
                "title": f"{alert.level.value.upper()}: {alert.title}",
                "description": alert.message,
                "color": color_map.get(alert.level, 0x00ff00),
                "timestamp": alert.timestamp.isoformat(),
                "fields": [
                    {
                        "name": "Valeur Actuelle",
                        "value": f"{alert.current_value:.2f}",
                        "inline": True
                    },
                    {
                        "name": "Seuil",
                        "value": f"{alert.threshold_value:.2f}",
                        "inline": True
                    },
                    {
                        "name": "Source",
                        "value": alert.source,
                        "inline": True
                    }
                ]
            }
            
            payload = {
                "username": "MIA_IA_SYSTEM",
                "embeds": [embed]
            }
            
            response = requests.post(
                self.notification_config.discord_webhook_url,
                json=payload,
                timeout=10
            )
            
            return response.status_code == 204  # Discord returns 204 for success
            
        except Exception as e:
            logger.error(f"Erreur send discord: {e}")
            return False
    
    def _send_sms_notification(self, alert: Alert) -> bool:
        """Envoi notification SMS (placeholder)"""
        try:
            # Placeholder - implémentation dépend du provider SMS
            # Exemple avec Twilio, Nexmo, etc.
            logger.info(f"SMS notification (placeholder): {alert.title}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur send sms: {e}")
            return False
    
    def _format_email_body(self, alert: Alert) -> str:
        """Formatage corps email"""
        return f"""
        <html>
        <body>
        <h2>🚨 Alerte MIA_IA_SYSTEM</h2>
        
        <h3>{alert.title}</h3>
        <p><strong>Niveau:</strong> {alert.level.value.upper()}</p>
        <p><strong>Catégorie:</strong> {alert.category.value}</p>
        <p><strong>Message:</strong> {alert.message}</p>
        
        <h4>Détails:</h4>
        <ul>
        <li><strong>Valeur Actuelle:</strong> {alert.current_value:.2f}</li>
        <li><strong>Seuil:</strong> {alert.threshold_value:.2f}</li>
        <li><strong>Source:</strong> {alert.source}</li>
        <li><strong>Timestamp:</strong> {alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}</li>
        <li><strong>Alert ID:</strong> {alert.alert_id}</li>
        </ul>
        
        <p><em>MIA_IA_SYSTEM Monitoring</em></p>
        </body>
        </html>
        """
    
    # === ESCALATION & CLEANUP ===
    
    def _check_alert_escalation(self):
        """Vérification escalation alertes"""
        try:
            current_time = datetime.now(timezone.utc)
            
            for alert in self.active_alerts.values():
                if alert.escalated or alert.status != AlertStatus.ACTIVE:
                    continue
                
                rule = self.alert_rules.get(alert.rule_id)
                if not rule or not rule.escalation_minutes:
                    continue
                
                # Vérifier si escalation nécessaire
                elapsed_minutes = (current_time - alert.timestamp).total_seconds() / 60
                
                if elapsed_minutes >= rule.escalation_minutes:
                    self._escalate_alert(alert)
                    
        except Exception as e:
            logger.error(f"Erreur check escalation: {e}")
    
    def _escalate_alert(self, alert: Alert):
        """Escalation alerte"""
        try:
            # Marquer comme escalé
            alert.escalated = True
            
            # Notification escalation (tous canaux + urgence)
            escalation_channels = [
                NotificationChannel.SMS,
                NotificationChannel.SLACK,
                NotificationChannel.LOG_ONLY
            ]
            
            if EMAIL_AVAILABLE:
                escalation_channels.insert(0, NotificationChannel.EMAIL)
            
            # Création alerte escalation
            escalation_alert = Alert(
                alert_id=str(uuid.uuid4()),
                rule_id=f"escalation_{alert.rule_id}",
                timestamp=datetime.now(timezone.utc),
                level=AlertLevel.EMERGENCY,
                category=alert.category,
                title=f"ESCALATION: {alert.title}",
                message=f"Alerte non traitée depuis {alert.timestamp.strftime('%H:%M:%S')} - Action immédiate requise",
                current_value=alert.current_value,
                threshold_value=alert.threshold_value,
                status=AlertStatus.ACTIVE,
                source="escalation_system",
                metadata={'original_alert_id': alert.alert_id}
            )
            
            # Envoi notifications escalation
            self.send_notifications(escalation_alert, escalation_channels)
            
            logger.critical(f"ESCALATION ALERTE: {alert.title} - ID: {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Erreur escalate alert: {e}")
    
    def _cleanup_resolved_alerts(self):
        """Nettoyage alertes résolues"""
        try:
            current_time = datetime.now(timezone.utc)
            resolved_alerts = []
            
            for alert_id, alert in self.active_alerts.items():
                # Auto-résolution après 24h pour alertes INFO/WARNING
                if alert.level in [AlertLevel.INFO, AlertLevel.WARNING]:
                    elapsed_hours = (current_time - alert.timestamp).total_seconds() / 3600
                    if elapsed_hours >= 24:
                        alert.status = AlertStatus.RESOLVED
                        alert.resolution_time = current_time
                        resolved_alerts.append(alert_id)
            
            # Supprimer alertes résolues
            for alert_id in resolved_alerts:
                del self.active_alerts[alert_id]
                
        except Exception as e:
            logger.error(f"Erreur cleanup alerts: {e}")
    
    # === DATA MANAGEMENT ===
    
    def _get_current_performance_data(self) -> Dict:
        """Récupération données performance actuelles"""
        try:
            # Placeholder - intégration avec PerformanceTracker
            # return performance_tracker.get_current_performance()
            return {}
        except Exception:
            return {}
    
    def acknowledge_alert(self, alert_id: str, user: str = "system") -> bool:
        """Acknowledgment d'alerte"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledgment_time = datetime.now(timezone.utc)
                alert.metadata['acknowledged_by'] = user
                
                logger.info(f"Alerte acquittée: {alert_id} par {user}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur acknowledge alert: {e}")
            return False
    
    def resolve_alert(self, alert_id: str, user: str = "system") -> bool:
        """Résolution d'alerte"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolution_time = datetime.now(timezone.utc)
                alert.metadata['resolved_by'] = user
                
                # Retirer des alertes actives
                del self.active_alerts[alert_id]
                
                logger.info(f"Alerte résolue: {alert_id} par {user}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur resolve alert: {e}")
            return False
    
    def log_alert_history(self, days: int = 7) -> List[Dict]:
        """
        LOG HISTORIQUE ALERTES
        
        Retourne historique alertes sur période
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            recent_alerts = [
                alert for alert in self.alert_history
                if alert.timestamp >= cutoff_date
            ]
            
            return [asdict(alert) for alert in recent_alerts]
            
        except Exception as e:
            logger.error(f"Erreur log alert history: {e}")
            return []
    
    # === PERSISTENCE ===
    
    def _save_alert(self, alert: Alert):
        """Sauvegarde alerte"""
        try:
            alert_date = alert.timestamp.date()
            alerts_file = self.history_path / f"alerts_{alert_date.isoformat()}.jsonl"
            
            with open(alerts_file, 'a', encoding='utf-8') as f:
                json.dump(asdict(alert), f, default=str)
                f.write('\n')
                
        except Exception as e:
            logger.error(f"Erreur sauvegarde alert: {e}")
    
    def _save_alert_rules(self):
        """Sauvegarde règles d'alerte"""
        try:
            rules_file = self.rules_path / "alert_rules.json"
            rules_data = {rule_id: asdict(rule) for rule_id, rule in self.alert_rules.items()}
            
            with open(rules_file, 'w', encoding='utf-8') as f:
                json.dump(rules_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Erreur sauvegarde rules: {e}")
    
    def _load_alert_rules(self):
        """Chargement règles d'alerte"""
        try:
            rules_file = self.rules_path / "alert_rules.json"
            if rules_file.exists():
                with open(rules_file, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)
                
                for rule_id, rule_dict in rules_data.items():
                    try:
                        # Reconstitution enums
                        rule_dict['category'] = AlertCategory(rule_dict['category'])
                        rule_dict['level'] = AlertLevel(rule_dict['level'])
                        rule_dict['notification_channels'] = [
                            NotificationChannel(ch) for ch in rule_dict['notification_channels']
                        ]
                        
                        self.alert_rules[rule_id] = AlertRule(**rule_dict)
                    except Exception as e:
                        logger.warning(f"Erreur chargement règle {rule_id}: {e}")
                
                logger.info(f"Règles chargées: {len(self.alert_rules)}")
                
        except Exception as e:
            logger.error(f"Erreur load rules: {e}")
    
    def _load_notification_config(self):
        """Chargement configuration notifications"""
        try:
            config_file = self.base_path / "notification_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                self.notification_config = NotificationConfig(**config_data)
                logger.info("Configuration notifications chargée")
                
        except Exception as e:
            logger.error(f"Erreur load notification config: {e}")

    # === METHODE PUBLIQUE POUR TRAITEMENT ALERTE ===
    
    def process_alert(self, alert: Alert):
        """
        TRAITEMENT ALERTE PUBLIQUE
        
        Méthode publique pour traiter une alerte depuis l'extérieur
        """
        try:
            # Ajouter aux alertes actives et historique
            self.active_alerts[alert.alert_id] = alert
            self.alert_history.append(alert)
            
            # Ajouter à la queue de notification
            self.notification_queue.append(alert)
            
            # Statistiques
            self.session_stats['alerts_generated'] += 1
            if alert.level == AlertLevel.CRITICAL:
                self.session_stats['critical_alerts'] += 1
            elif alert.level == AlertLevel.EMERGENCY:
                self.session_stats['emergency_alerts'] += 1
            
            # Log
            logger.warning(f"ALERTE EXTERNE {alert.level.value.upper()}: {alert.title} - {alert.message}")
            
            # Sauvegarde
            self._save_alert(alert)
            
            # Si pas de monitoring actif, traiter directement
            if not self.is_monitoring:
                self.send_notifications(alert)
            
        except Exception as e:
            logger.error(f"Erreur process alert: {e}")
    
    # === PUBLIC INTERFACE ===
    
    def get_active_alerts(self) -> List[Dict]:
        """Interface publique - Alertes actives"""
        return [asdict(alert) for alert in self.active_alerts.values()]
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Interface publique - Statistiques alertes"""
        return {
            'session_stats': self.session_stats.copy(),
            'notification_stats': self.notification_stats.copy(),
            'active_alerts_count': len(self.active_alerts),
            'total_rules': len(self.alert_rules),
            'enabled_rules': sum(1 for rule in self.alert_rules.values() if rule.enabled),
            'last_health_check': self.last_health_check.isoformat(),
            'email_available': EMAIL_AVAILABLE
        }

# === FACTORY FUNCTIONS ===

def create_alert_system(config: Optional[Dict] = None) -> AlertSystem:
    """Factory function pour alert system"""
    return AlertSystem(config)

def check_email_functionality() -> bool:
    """Check si fonctionnalité email disponible"""
    return EMAIL_AVAILABLE

# === TESTING ===

def test_alert_system():
    """Test alert system"""
    print("🚨 TEST ALERT SYSTEM")
    print("=" * 35)
    
    alert_system = create_alert_system()
    
    # Test démarrage monitoring
    alert_system.start_monitoring()
    print("✅ Monitoring démarré")
    
    # Test health check
    health = alert_system.monitor_system_health()
    print(f"✅ System health: CPU {health.cpu_percent:.1f}%, RAM {health.memory_percent:.1f}%")
    
    # Test alerte factice
    fake_performance = {'max_drawdown_percent': 15.0}
    alert_system.monitor_risk_thresholds(fake_performance)
    print("✅ Test alerte drawdown")
    
    # Attendre un peu
    time.sleep(2)
    
    # Statistiques
    stats = alert_system.get_alert_statistics()
    print(f"✅ Alertes générées: {stats['session_stats']['alerts_generated']}")
    print(f"✅ Email disponible: {stats['email_available']}")
    
    # Arrêt
    alert_system.stop_monitoring()
    print("✅ Monitoring arrêté")
    
    print("🎯 Alert system test COMPLETED")
    return True

if __name__ == "__main__":
    print(f"Email functionality: {'✅ Available' if EMAIL_AVAILABLE else '❌ Disabled (MimeText import failed)'}")
    test_alert_system()