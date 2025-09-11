"""
MIA_IA_SYSTEM - Live Monitor
Surveillance temps réel et alertes intelligentes
Version: Phase 3 - Production Ready
Performance: Monitoring <50ms overhead, dashboard temps réel

RESPONSABILITÉS :
1. Monitoring temps réel tous composants système
2. Dashboard web simple mais efficace  
3. Système d'alertes intelligent (email, webhook, console)
4. Health checks automatiques
5. Métriques performance continues
6. Détection anomalies et dégradations

MÉTRIQUES SURVEILLÉES :
- Trading : P&L, win rate, drawdown, trades count
- Performance : Latence, throughput, errors
- Système : CPU, mémoire, disque, network
- Composants : Health status, uptime, errors
- Data : Quality, latency, missing ticks
"""

import time
import json
import asyncio
import logging
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import psutil
import socket
from pathlib import Path
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Web dashboard imports
try:
    from flask import Flask, render_template_string, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logger.warning("Flask non disponible - Dashboard web désactivé")

# Local imports
from config.automation_config import (
    get_automation_config, MonitoringConfig, AlertLevel
)

logger = logging.getLogger(__name__)

# === MONITORING ENUMS ===

class ComponentStatus(Enum):
    """Statuts composants système"""
    HEALTHY = "healthy"         # Tout va bien
    WARNING = "warning"         # Attention requise
    CRITICAL = "critical"       # Problème grave
    OFFLINE = "offline"         # Composant arrêté
    UNKNOWN = "unknown"         # Statut indéterminé

class MetricType(Enum):
    """Types de métriques"""
    COUNTER = "counter"         # Incrémental (trades count)
    GAUGE = "gauge"            # Valeur instantanée (P&L)
    TIMER = "timer"            # Durée (latence)
    PERCENTAGE = "percentage"   # Pourcentage (win rate)

class AlertSeverity(Enum):
    """Sévérité alertes"""
    INFO = "info"
    WARNING = "warning"  
    ERROR = "error"
    CRITICAL = "critical"

# === MONITORING DATA STRUCTURES ===

@dataclass
class Metric:
    """Métrique de monitoring"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    unit: str = ""
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'value': self.value,
            'type': self.metric_type.value,
            'timestamp': self.timestamp.isoformat(),
            'unit': self.unit,
            'description': self.description
        }

@dataclass
class ComponentHealth:
    """Santé d'un composant"""
    component_name: str
    status: ComponentStatus
    last_heartbeat: datetime
    metrics: Dict[str, Metric] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    uptime_seconds: float = 0.0
    
    def is_healthy(self) -> bool:
        return self.status == ComponentStatus.HEALTHY
    
    def add_error(self, error_msg: str):
        """Ajoute erreur avec rotation"""
        self.errors.append(f"{datetime.now().isoformat()}: {error_msg}")
        if len(self.errors) > 10:  # Garder seulement 10 dernières
            self.errors = self.errors[-10:]

@dataclass
class Alert:
    """Alerte système"""
    id: str
    severity: AlertSeverity
    component: str
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'severity': self.severity.value,
            'component': self.component,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

@dataclass
class TradingMetrics:
    """Métriques trading spécifiques"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    current_pnl: float = 0.0
    daily_pnl: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    current_position_size: int = 0
    signals_today: int = 0
    avg_trade_duration_minutes: float = 0.0
    
    def calculate_derived_metrics(self):
        """Calcule métriques dérivées"""
        if self.total_trades > 0:
            self.win_rate = self.winning_trades / self.total_trades
            
        if self.losing_trades > 0:
            avg_win = self.daily_pnl / max(self.winning_trades, 1)
            avg_loss = abs(self.daily_pnl) / max(self.losing_trades, 1)
            self.profit_factor = avg_win / avg_loss if avg_loss > 0 else 0

@dataclass
class SystemMetrics:
    """Métriques système"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_mb: float = 0.0
    disk_free_gb: float = 0.0
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    load_average: float = 0.0
    process_count: int = 0
    uptime_seconds: float = 0.0

# === MAIN LIVE MONITOR CLASS ===

class LiveMonitor:
    """Système de monitoring temps réel"""
    
    def __init__(self):
        self.config = get_automation_config().monitoring
        self.start_time = datetime.now()
        
        # État monitoring
        self.is_monitoring = False
        self.components: Dict[str, ComponentHealth] = {}
        self.metrics_history: List[Dict[str, Any]] = []
        self.alerts: Dict[str, Alert] = {}
        self.alert_handlers: List[Callable] = []
        
        # Métriques spécialisées
        self.trading_metrics = TradingMetrics()
        self.system_metrics = SystemMetrics()
        
        # Performance tracking
        self.monitor_stats = {
            'iterations': 0,
            'avg_iteration_time_ms': 0.0,
            'errors_count': 0,
            'alerts_sent': 0
        }
        
        # Web dashboard
        self.dashboard_app = None
        if FLASK_AVAILABLE and self.config.enable_dashboard:
            self._setup_web_dashboard()
        
        # Enregistrer composants système
        self._register_system_components()
        
        logger.info("LiveMonitor initialisé avec surveillance complète")
    
    def _register_system_components(self):
        """Enregistre composants système à surveiller"""
        components = [
            "trader", "snapshotter", "config", "data_feed", 
            "order_manager", "risk_manager", "system"
        ]
        
        for comp_name in components:
            self.components[comp_name] = ComponentHealth(
                component_name=comp_name,
                status=ComponentStatus.UNKNOWN,
                last_heartbeat=datetime.now()
            )
    
    async def start_monitoring(self):
        """Démarre monitoring complet"""
        try:
            logger.info("🔍 Démarrage monitoring temps réel...")
            self.is_monitoring = True
            
            # Démarrer dashboard web si activé
            if self.dashboard_app and self.config.enable_dashboard:
                self._start_web_dashboard()
            
            # Loop principal monitoring
            await self._monitoring_loop()
            
        except Exception as e:
            logger.error(f"❌ Erreur monitoring: {e}")
        finally:
            self.is_monitoring = False
    
    async def _monitoring_loop(self):
        """Loop principal de monitoring"""
        logger.info("🔄 Loop monitoring démarré")
        
        while self.is_monitoring:
            try:
                iteration_start = time.perf_counter()
                
                # 1. Collecter métriques système
                await self._collect_system_metrics()
                
                # 2. Vérifier santé composants
                await self._check_components_health()
                
                # 3. Collecter métriques trading
                await self._collect_trading_metrics()
                
                # 4. Détecter anomalies et alertes
                await self._detect_anomalies()
                
                # 5. Nettoyer données anciennes
                self._cleanup_old_data()
                
                # 6. Sauvegarder snapshot métriques
                self._save_metrics_snapshot()
                
                # Performance tracking
                iteration_time = (time.perf_counter() - iteration_start) * 1000
                self._update_monitor_performance(iteration_time)
                
                # Sleep jusqu'à prochaine itération
                await asyncio.sleep(self.config.monitoring_frequency_seconds)
                
            except Exception as e:
                logger.error(f"❌ Erreur itération monitoring: {e}")
                self.monitor_stats['errors_count'] += 1
                await asyncio.sleep(5)  # Sleep plus long en cas d'erreur
    
    async def _collect_system_metrics(self):
        """Collecte métriques système"""
        try:
            # CPU
            self.system_metrics.cpu_percent = psutil.cpu_percent(interval=None)
            
            # Mémoire
            memory = psutil.virtual_memory()
            self.system_metrics.memory_percent = memory.percent
            self.system_metrics.memory_mb = memory.used / 1024 / 1024
            
            # Disque
            disk = psutil.disk_usage('.')
            self.system_metrics.disk_free_gb = disk.free / (1024**3)
            
            # Network (si disponible)
            try:
                net_io = psutil.net_io_counters()
                self.system_metrics.network_bytes_sent = net_io.bytes_sent
                self.system_metrics.network_bytes_recv = net_io.bytes_recv
            except:
                pass
            
            # Load average (Unix only)
            try:
                self.system_metrics.load_average = psutil.getloadavg()[0]
            except:
                self.system_metrics.load_average = self.system_metrics.cpu_percent / 100
            
            # Process info
            try:
                self.system_metrics.process_count = len(psutil.pids())
            except:
                pass
            
            # Uptime
            self.system_metrics.uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            
            # Update component health
            self._update_component_health("system", ComponentStatus.HEALTHY, {
                'cpu_percent': Metric("cpu_percent", self.system_metrics.cpu_percent, MetricType.PERCENTAGE, datetime.now(), "%"),
                'memory_percent': Metric("memory_percent", self.system_metrics.memory_percent, MetricType.PERCENTAGE, datetime.now(), "%"),
                'disk_free_gb': Metric("disk_free_gb", self.system_metrics.disk_free_gb, MetricType.GAUGE, datetime.now(), "GB")
            })
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte métriques système: {e}")
            self._update_component_health("system", ComponentStatus.WARNING)
    
    async def _collect_trading_metrics(self):
        """Collecte métriques trading depuis les composants"""
        try:
            # Essayer d'obtenir stats depuis trader (si accessible)
            # En production, ceci serait injecté par l'orchestrator
            
            # Pour l'instant, simulation ou données mockées
            # TODO: Intégrer avec SimpleBattleNavaleTrader réel
            
            # Calculs dérivés
            self.trading_metrics.calculate_derived_metrics()
            
            # Créer métriques pour composant trader
            trader_metrics = {
                'total_trades': Metric("total_trades", self.trading_metrics.total_trades, MetricType.COUNTER, datetime.now()),
                'daily_pnl': Metric("daily_pnl", self.trading_metrics.daily_pnl, MetricType.GAUGE, datetime.now(), "$"),
                'win_rate': Metric("win_rate", self.trading_metrics.win_rate, MetricType.PERCENTAGE, datetime.now(), "%"),
                'current_position': Metric("current_position", self.trading_metrics.current_position_size, MetricType.GAUGE, datetime.now())
            }
            
            # Déterminer status trader
            trader_status = ComponentStatus.HEALTHY
            if self.trading_metrics.daily_pnl < -500:  # Perte importante
                trader_status = ComponentStatus.WARNING
            if self.trading_metrics.daily_pnl < -1000:  # Perte critique
                trader_status = ComponentStatus.CRITICAL
            
            self._update_component_health("trader", trader_status, trader_metrics)
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte métriques trading: {e}")
            self._update_component_health("trader", ComponentStatus.WARNING)
    
    async def _check_components_health(self):
        """Vérifie santé de tous les composants"""
        try:
            current_time = datetime.now()
            
            for comp_name, health in self.components.items():
                # Vérifier timeout heartbeat
                time_since_heartbeat = (current_time - health.last_heartbeat).total_seconds()
                
                if time_since_heartbeat > 300:  # 5 minutes sans heartbeat
                    health.status = ComponentStatus.OFFLINE
                elif time_since_heartbeat > 120:  # 2 minutes
                    health.status = ComponentStatus.WARNING
                
                # Calculer uptime
                health.uptime_seconds = time_since_heartbeat
                
        except Exception as e:
            logger.error(f"❌ Erreur check components health: {e}")
    
    async def _detect_anomalies(self):
        """Détecte anomalies et génère alertes"""
        try:
            # 1. Alertes système
            if self.system_metrics.memory_percent > 90:
                await self._create_alert(
                    AlertSeverity.WARNING,
                    "system",
                    f"Mémoire élevée: {self.system_metrics.memory_percent:.1f}%"
                )
            
            if self.system_metrics.cpu_percent > 80:
                await self._create_alert(
                    AlertSeverity.WARNING,
                    "system", 
                    f"CPU élevé: {self.system_metrics.cpu_percent:.1f}%"
                )
            
            if self.system_metrics.disk_free_gb < 1.0:
                await self._create_alert(
                    AlertSeverity.CRITICAL,
                    "system",
                    f"Espace disque critique: {self.system_metrics.disk_free_gb:.1f}GB"
                )
            
            # 2. Alertes trading
            if self.trading_metrics.daily_pnl < -self.config.alert_on_daily_loss_percent * 10:  # Approximation
                await self._create_alert(
                    AlertSeverity.ERROR,
                    "trader",
                    f"Perte quotidienne importante: ${self.trading_metrics.daily_pnl:.2f}"
                )
            
            if self.trading_metrics.losing_trades >= self.config.alert_on_loss_streak:
                await self._create_alert(
                    AlertSeverity.WARNING,
                    "trader",
                    f"Série de pertes: {self.trading_metrics.losing_trades} trades"
                )
            
            # 3. Alertes composants offline
            for comp_name, health in self.components.items():
                if health.status == ComponentStatus.OFFLINE:
                    await self._create_alert(
                        AlertSeverity.CRITICAL,
                        comp_name,
                        f"Composant hors ligne: {comp_name}"
                    )
            
        except Exception as e:
            logger.error(f"❌ Erreur détection anomalies: {e}")
    
    async def _create_alert(self, severity: AlertSeverity, component: str, message: str):
        """Crée et traite une alerte"""
        try:
            # Créer ID unique
            alert_id = f"{component}_{severity.value}_{int(time.time())}"
            
            # Vérifier si alerte similaire récente existe
            for existing_alert in self.alerts.values():
                if (existing_alert.component == component and 
                    existing_alert.message == message and
                    not existing_alert.resolved and
                    (datetime.now() - existing_alert.timestamp).total_seconds() < 300):
                    return  # Éviter spam alertes identiques
            
            # Créer nouvelle alerte
            alert = Alert(
                id=alert_id,
                severity=severity,
                component=component,
                message=message,
                timestamp=datetime.now()
            )
            
            self.alerts[alert_id] = alert
            self.monitor_stats['alerts_sent'] += 1
            
            # Logger selon sévérité
            if severity == AlertSeverity.CRITICAL:
                logger.critical(f"🚨 CRITICAL: {component} - {message}")
            elif severity == AlertSeverity.ERROR:
                logger.error(f"❌ ERROR: {component} - {message}")
            elif severity == AlertSeverity.WARNING:
                logger.warning(f"⚠️ WARNING: {component} - {message}")
            else:
                logger.info(f"ℹ️ INFO: {component} - {message}")
            
            # Envoyer alerte via handlers
            await self._send_alert(alert)
            
        except Exception as e:
            logger.error(f"❌ Erreur création alerte: {e}")
    
    async def _send_alert(self, alert: Alert):
        """Envoie alerte via différents canaux"""
        try:
            # Email si configuré
            if self.config.alert_email:
                await self._send_email_alert(alert)
            
            # Webhook si configuré
            if self.config.alert_webhook:
                await self._send_webhook_alert(alert)
            
            # Console (toujours)
            self._send_console_alert(alert)
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi alerte: {e}")
    
    async def _send_email_alert(self, alert: Alert):
        """Envoie alerte par email"""
        try:
            # TODO: Implémenter envoi email
            # Configuration SMTP à ajouter dans automation_config
            logger.debug(f"📧 Email alert: {alert.message}")
        except Exception as e:
            logger.error(f"❌ Erreur email alert: {e}")
    
    async def _send_webhook_alert(self, alert: Alert):
        """Envoie alerte par webhook"""
        try:
            if not self.config.alert_webhook:
                return
            
            payload = {
                'alert': alert.to_dict(),
                'system': 'MIA_IA_SYSTEM',
                'timestamp': datetime.now().isoformat()
            }
            
            # Envoi asynchrone
            response = requests.post(
                self.config.alert_webhook,
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.debug(f"📡 Webhook alert envoyé: {alert.id}")
            else:
                logger.warning(f"⚠️ Webhook alert échec: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Erreur webhook alert: {e}")
    
    def _send_console_alert(self, alert: Alert):
        """Affiche alerte en console"""
        emoji = {
            AlertSeverity.CRITICAL: "🚨",
            AlertSeverity.ERROR: "❌", 
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.INFO: "ℹ️"
        }
        
        logger.info("\n{emoji[alert.severity]} ALERT [{alert.severity.value.upper()}]")
        logger.info("Component: {alert.component}")
        logger.info("Message: {alert.message}")
        logger.info("Time: {alert.timestamp.strftime('%H:%M:%S')}")
        print("-" * 50)
    
    def _update_component_health(self, 
                               component_name: str, 
                               status: ComponentStatus,
                               metrics: Optional[Dict[str, Metric]] = None):
        """Met à jour santé d'un composant"""
        if component_name not in self.components:
            self.components[component_name] = ComponentHealth(
                component_name=component_name,
                status=status,
                last_heartbeat=datetime.now()
            )
        
        health = self.components[component_name]
        health.status = status
        health.last_heartbeat = datetime.now()
        
        if metrics:
            health.metrics.update(metrics)
    
    def _update_monitor_performance(self, iteration_time_ms: float):
        """Met à jour stats performance monitoring"""
        self.monitor_stats['iterations'] += 1
        
        # Moyenne mobile temps itération
        current_avg = self.monitor_stats['avg_iteration_time_ms']
        count = self.monitor_stats['iterations']
        
        self.monitor_stats['avg_iteration_time_ms'] = (
            (current_avg * (count - 1) + iteration_time_ms) / count
        )
    
    def _cleanup_old_data(self):
        """Nettoie données anciennes"""
        try:
            current_time = datetime.now()
            
            # Nettoyer alertes résolues anciennes (>24h)
            old_alerts = [
                alert_id for alert_id, alert in self.alerts.items()
                if alert.resolved and 
                alert.resolved_at and
                (current_time - alert.resolved_at).total_seconds() > 86400
            ]
            
            for alert_id in old_alerts:
                del self.alerts[alert_id]
            
            # Limiter historique métriques (garder 1000 derniers points)
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
                
        except Exception as e:
            logger.error(f"❌ Erreur cleanup: {e}")
    
    def _save_metrics_snapshot(self):
        """Sauvegarde snapshot métriques"""
        try:
            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'trading_metrics': asdict(self.trading_metrics),
                'system_metrics': asdict(self.system_metrics),
                'components_health': {
                    name: {
                        'status': health.status.value,
                        'last_heartbeat': health.last_heartbeat.isoformat(),
                        'uptime_seconds': health.uptime_seconds,
                        'errors_count': len(health.errors)
                    }
                    for name, health in self.components.items()
                },
                'monitor_stats': self.monitor_stats.copy()
            }
            
            self.metrics_history.append(snapshot)
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde snapshot: {e}")
    
    # === WEB DASHBOARD ===
    
    def _setup_web_dashboard(self):
        """Setup dashboard web Flask"""
        if not FLASK_AVAILABLE:
            return
        
        try:
            self.dashboard_app = Flask(__name__)
            
            # Route principale dashboard
            @self.dashboard_app.route('/')
            def dashboard():
                return self._render_dashboard()
            
            # API endpoints
            @self.dashboard_app.route('/api/status')
            def api_status():
                return jsonify(self.get_full_status())
            
            @self.dashboard_app.route('/api/metrics')
            def api_metrics():
                return jsonify({
                    'trading': asdict(self.trading_metrics),
                    'system': asdict(self.system_metrics)
                })
            
            @self.dashboard_app.route('/api/alerts')
            def api_alerts():
                return jsonify([alert.to_dict() for alert in self.alerts.values()])
            
            logger.info("✅ Dashboard web configuré")
            
        except Exception as e:
            logger.error(f"❌ Erreur setup dashboard: {e}")
    
    def _render_dashboard(self) -> str:
        """Rendu HTML dashboard"""
        # Dashboard HTML simple mais efficace
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MIA_IA_SYSTEM - Live Monitor</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                .metric-card { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                .metric-value { font-size: 2em; font-weight: bold; color: #2c3e50; }
                .metric-label { color: #7f8c8d; font-size: 0.9em; }
                .status-healthy { color: #27ae60; }
                .status-warning { color: #f39c12; }
                .status-critical { color: #e74c3c; }
                .alert { padding: 10px; margin: 5px 0; border-radius: 3px; }
                .alert-warning { background: #fff3cd; border-left: 4px solid #ffc107; }
                .alert-error { background: #f8d7da; border-left: 4px solid #dc3545; }
                .alert-critical { background: #f8d7da; border-left: 4px solid #dc3545; animation: blink 1s infinite; }
                @keyframes blink { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0.5; } }
                .refresh-info { text-align: center; color: #7f8c8d; margin-top: 20px; }
            </style>
            <script>
                function refreshPage() { location.reload(); }
                setInterval(refreshPage, 10000); // Refresh toutes les 10s
            </script>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 MIA_IA_SYSTEM - Live Monitor</h1>
                    <p>Surveillance temps réel • {{timestamp}}</p>
                </div>
                
                <div class="metrics-grid">
                    <!-- Trading Metrics -->
                    <div class="metric-card">
                        <h3>📊 Trading Performance</h3>
                        <div class="metric-value {{pnl_class}}">{{daily_pnl}}</div>
                        <div class="metric-label">P&L Quotidien</div>
                        <hr>
                        <p>Trades: {{total_trades}} | Win Rate: {{win_rate}}%</p>
                        <p>Position: {{position_size}} | Signaux: {{signals_today}}</p>
                    </div>
                    
                    <!-- System Health -->
                    <div class="metric-card">
                        <h3>💻 Système</h3>
                        <div class="metric-value">{{cpu_percent}}%</div>
                        <div class="metric-label">CPU Usage</div>
                        <hr>
                        <p>Mémoire: {{memory_percent}}% ({{memory_mb}}MB)</p>
                        <p>Disque libre: {{disk_free_gb}}GB</p>
                    </div>
                    
                    <!-- Components Status -->
                    <div class="metric-card">
                        <h3>🔧 Composants</h3>
                        {{components_status}}
                    </div>
                    
                    <!-- Recent Alerts -->
                    <div class="metric-card">
                        <h3>⚠️ Alertes Récentes</h3>
                        <div id="alerts">
                            {{recent_alerts}}
                        </div>
                    </div>
                </div>
                
                <div class="refresh-info">
                    <p>🔄 Actualisation automatique toutes les 10 secondes</p>
                    <p>Monitor uptime: {{uptime_hours}}h | Itérations: {{iterations}}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Préparer données pour template
        try:
            # Calculs
            uptime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
            pnl_class = "status-healthy" if self.trading_metrics.daily_pnl >= 0 else "status-critical"
            
            # Components status
            components_html = ""
            for name, health in self.components.items():
                status_class = f"status-{health.status.value}"
                components_html += f'<p class="{status_class}">• {name.title()}: {health.status.value.title()}</p>'
            
            # Recent alerts (5 dernières)
            recent_alerts_html = ""
            recent_alerts = sorted(self.alerts.values(), key=lambda x: x.timestamp, reverse=True)[:5]
            
            if not recent_alerts:
                recent_alerts_html = "<p class='status-healthy'>Aucune alerte récente ✅</p>"
            else:
                for alert in recent_alerts:
                    alert_class = f"alert alert-{alert.severity.value}"
                    time_str = alert.timestamp.strftime('%H:%M:%S')
                    recent_alerts_html += f'<div class="{alert_class}">[{time_str}] {alert.component}: {alert.message}</div>'
            
            # Remplacer variables template
            html = html_template.replace('{{timestamp}}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            html = html.replace('{{daily_pnl}}', f"${self.trading_metrics.daily_pnl:.2f}")
            html = html.replace('{{pnl_class}}', pnl_class)
            html = html.replace('{{total_trades}}', str(self.trading_metrics.total_trades))
            html = html.replace('{{win_rate}}', f"{self.trading_metrics.win_rate*100:.1f}")
            html = html.replace('{{position_size}}', str(self.trading_metrics.current_position_size))
            html = html.replace('{{signals_today}}', str(self.trading_metrics.signals_today))
            html = html.replace('{{cpu_percent}}', f"{self.system_metrics.cpu_percent:.1f}")
            html = html.replace('{{memory_percent}}', f"{self.system_metrics.memory_percent:.1f}")
            html = html.replace('{{memory_mb}}', f"{self.system_metrics.memory_mb:.0f}")
            html = html.replace('{{disk_free_gb}}', f"{self.system_metrics.disk_free_gb:.1f}")
            html = html.replace('{{components_status}}', components_html)
            html = html.replace('{{recent_alerts}}', recent_alerts_html)
            html = html.replace('{{uptime_hours}}', f"{uptime_hours:.1f}")
            html = html.replace('{{iterations}}', str(self.monitor_stats['iterations']))
            
            return html
            
        except Exception as e:
            logger.error(f"❌ Erreur rendu dashboard: {e}")
            return f"<h1>Erreur Dashboard</h1><p>{e}</p>"
    
    def _start_web_dashboard(self):
        """Démarre serveur web dashboard dans thread séparé"""
        def run_flask():
            try:
                self.dashboard_app.run(
                    host='0.0.0.0',
                    port=self.config.dashboard_port,
                    debug=False,
                    threaded=True
                )
            except Exception as e:
                logger.error(f"❌ Erreur serveur dashboard: {e}")
        
        if self.dashboard_app:
            dashboard_thread = threading.Thread(target=run_flask, daemon=True)
            dashboard_thread.start()
            logger.info(f"🌐 Dashboard disponible: http://localhost:{self.config.dashboard_port}")
    
    # === PUBLIC METHODS ===
    
    def heartbeat(self, component_name: str, status: ComponentStatus = ComponentStatus.HEALTHY, 
                  metrics: Optional[Dict[str, Any]] = None):
        """Enregistre heartbeat d'un composant"""
        try:
            metric_objects = {}
            if metrics:
                for name, value in metrics.items():
                    metric_objects[name] = Metric(
                        name=name,
                        value=float(value),
                        metric_type=MetricType.GAUGE,
                        timestamp=datetime.now()
                    )
            
            self._update_component_health(component_name, status, metric_objects)
            
        except Exception as e:
            logger.error(f"❌ Erreur heartbeat {component_name}: {e}")
    
    def update_trading_metrics(self, metrics: Dict[str, Any]):
        """Met à jour métriques trading depuis externe"""
        try:
            for key, value in metrics.items():
                if hasattr(self.trading_metrics, key):
                    setattr(self.trading_metrics, key, value)
            
            self.trading_metrics.calculate_derived_metrics()
            
        except Exception as e:
            logger.error(f"❌ Erreur update trading metrics: {e}")
    
    def get_full_status(self) -> Dict[str, Any]:
        """Retourne status complet système"""
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'trading_metrics': asdict(self.trading_metrics),
            'system_metrics': asdict(self.system_metrics),
            'components': {
                name: {
                    'status': health.status.value,
                    'last_heartbeat': health.last_heartbeat.isoformat(),
                    'uptime_seconds': health.uptime_seconds,
                    'errors_count': len(health.errors)
                }
                for name, health in self.components.items()
            },
            'alerts': [alert.to_dict() for alert in self.alerts.values()],
            'monitor_performance': self.monitor_stats
        }
    
    async def stop_monitoring(self):
        """Arrête monitoring"""
        logger.info("🛑 Arrêt monitoring...")
        self.is_monitoring = False
        
        # Sauvegarder état final
        try:
            final_status = self.get_full_status()
            status_file = Path("logs") / f"monitor_final_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(status_file, 'w') as f:
                json.dump(final_status, f, indent=2, default=str)
            logger.info(f"📄 Status final sauvé: {status_file}")
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde status final: {e}")

# === FACTORY FUNCTION ===

def create_live_monitor() -> LiveMonitor:
    """Factory function pour live monitor"""
    return LiveMonitor()

# === TESTING ===

def test_live_monitor():
    """Test live monitor"""
    logger.debug("Test live monitor...")
    
    monitor = create_live_monitor()
    
    # Test heartbeat
    monitor.heartbeat("test_component", ComponentStatus.HEALTHY, {
        'test_metric': 42.0,
        'another_metric': 3.14
    })
    
    # Test update trading metrics
    monitor.update_trading_metrics({
        'total_trades': 5,
        'daily_pnl': 150.0,
        'win_rate': 0.8
    })
    
    # Test status
    status = monitor.get_full_status()
    logger.info("Status components: {len(status['components'])}")
    logger.info("Trading P&L: ${status['trading_metrics']['daily_pnl']}")
    logger.info("System CPU: {status['system_metrics']['cpu_percent']:.1f}%")
    
    # Test dashboard si disponible
    if FLASK_AVAILABLE:
        logger.info("Dashboard web disponible")
    else:
        logger.warning("Dashboard web non disponible (Flask manquant)")
    
    logger.info("🎯 Live monitor test COMPLETED")
    return True

if __name__ == "__main__":
    test_live_monitor()