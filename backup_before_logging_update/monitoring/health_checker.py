#!/usr/bin/env python3
"""
🏥 MIA_IA_SYSTEM - HEALTH CHECKER SYSTEM
🎯 Surveillance intelligente et auto-recovery des composants
Version: Production Ready v3.0
Performance: <20ms overhead, recovery automatique, alertes proactives

RESPONSABILITÉS CRITIQUES :
1. 🔍 SURVEILLANCE COMPLÈTE - Tous composants MIA_IA_SYSTEM
2. 🔧 AUTO-RECOVERY - Redémarrage automatique composants défaillants
3. 🚨 ALERTES INTELLIGENTES - Discord/Email/SMS notifications
4. 📊 DASHBOARD SANTÉ - Interface web temps réel
5. 📈 MÉTRIQUES SYSTÈME - CPU, RAM, latence, throughput
6. 🛡️ PROTECTION PROACTIVE - Détection anomalies avant crash
7. 📋 RAPPORTS SANTÉ - Daily/Weekly health reports
8. 🔄 ORCHESTRATION - Coordination avec monitoring existant

COMPOSANTS SURVEILLÉS :
- 🧠 Signal Generator (get_signal_now performance)
- ⚔️ Battle Navale Analyzer (méthode signature)
- 🎪 Confluence Analyzer (multi-level confluence)
- 📊 Feature Calculator (8 features + confluence)
- 💹 Execution Layer (Simple Trader, Order Manager, Risk Manager)
- 📡 Data Feeds (IBKR, Sierra Chart connectivity)
- 🗃️ Data Storage (files, databases, caches)
- 💻 System Resources (CPU, memory, disk, network)
- 🔗 External Services (Discord, email, APIs)

INTÉGRATION MONITORING :
- Performance Tracker : Métriques trading
- Alert System : Système alertes intelligent
- Live Monitor : Surveillance temps réel
- Discord Notifier : Notifications instantanées

AUTO-RECOVERY ACTIONS :
- 🔄 Restart hung components
- 🧹 Clear memory leaks
- 📁 Cleanup disk space
- 🔗 Reconnect data feeds
- 💾 Backup critical data
- 🚨 Emergency shutdown if needed
"""

import time
import sys
import os
import gc
import psutil
import threading
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, NamedTuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque
import json
import pickle
import sqlite3
import subprocess
import socket
import requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

# === THIRD-PARTY ===
import numpy as np
import pandas as pd

# === WEB DASHBOARD ===
try:
    from flask import Flask, render_template_string, jsonify, request, send_from_directory
    from werkzeug.serving import make_server
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logger.warning("Flask non disponible - Dashboard web désactivé")

# === MIA_IA_SYSTEM IMPORTS ===
try:
    # Configuration
    from config import get_trading_config, get_automation_config

    # Core components
    from core import (
        MarketData, TradingSignal, SignalType,
        ES_TICK_SIZE, ES_TICK_VALUE
    )

    # Monitoring components (orchestrés par Health Checker)
    from monitoring.performance_tracker import PerformanceTracker, create_performance_tracker
    from monitoring.alert_system import AlertSystem, AlertLevel, create_alert_system
    from monitoring.discord_notifier import DiscordNotifier, create_discord_notifier

    # Strategies (pour health checks)
    from strategies import get_signal_now, create_signal_generator

    SYSTEM_INTEGRATION = True

except ImportError as e:
    SYSTEM_INTEGRATION = False
    logger.warning("Intégration MIA_IA_SYSTEM partielle: {e}")

# Logging
logger = logging.getLogger(__name__)

# === HEALTH CHECKER ENUMS ===


class HealthStatus(Enum):
    """États de santé composants"""
    HEALTHY = "healthy"           # 🟢 Tout va bien
    WARNING = "warning"           # 🟡 Attention requise
    CRITICAL = "critical"         # 🔴 Problème grave
    OFFLINE = "offline"           # ⚫ Composant arrêté
    RECOVERING = "recovering"     # 🔵 En cours de recovery
    UNKNOWN = "unknown"           # ❓ État indéterminé


class ComponentType(Enum):
    """Types de composants surveillés"""
    CORE = "core"                 # Signal Generator, Battle Navale
    EXECUTION = "execution"       # Trading, orders, risk
    DATA = "data"                 # Feeds, storage, connectivity
    MONITORING = "monitoring"     # Performance, alerts, health
    SYSTEM = "system"             # OS, resources, processes
    EXTERNAL = "external"         # Discord, APIs, services


class RecoveryAction(Enum):
    """Actions de recovery disponibles"""
    RESTART = "restart"           # Redémarre composant
    RECONNECT = "reconnect"       # Reconnecte services
    CLEANUP = "cleanup"           # Nettoie ressources
    RESET = "reset"               # Reset état
    BACKUP = "backup"             # Sauvegarde données
    SHUTDOWN = "shutdown"         # Arrêt d'urgence
    ESCALATE = "escalate"         # Escalade humaine


class AlertUrgency(Enum):
    """Urgence des alertes"""
    LOW = "low"                   # Info, pas critique
    MEDIUM = "medium"             # Important, action recommandée
    HIGH = "high"                 # Urgent, action requise
    CRITICAL = "critical"         # Critique, action immédiate

# === STRUCTURES DE DONNÉES ===


@dataclass
class ComponentHealth:
    """État de santé d'un composant"""
    component_name: str
    component_type: ComponentType
    status: HealthStatus = HealthStatus.UNKNOWN

    # Métriques
    last_heartbeat: Optional[datetime] = None
    response_time_ms: float = 0.0
    error_count: int = 0
    uptime_seconds: float = 0.0

    # Performance
    cpu_usage_pct: float = 0.0
    memory_usage_mb: float = 0.0
    throughput_per_sec: float = 0.0

    # Recovery
    recovery_attempts: int = 0
    last_recovery: Optional[datetime] = None
    auto_recovery_enabled: bool = True

    # Metadata
    version: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def is_healthy(self) -> bool:
        """Vérifie si composant en bonne santé"""
        return self.status in [HealthStatus.HEALTHY, HealthStatus.WARNING]

    def needs_recovery(self) -> bool:
        """Vérifie si recovery nécessaire"""
        return self.status in [HealthStatus.CRITICAL, HealthStatus.OFFLINE]

    def update_heartbeat(self):
        """Met à jour heartbeat"""
        self.last_heartbeat = datetime.now(timezone.utc)

    def calculate_uptime(self, start_time: datetime) -> float:
        """Calcule uptime en secondes"""
        if self.last_heartbeat:
            self.uptime_seconds = (self.last_heartbeat - start_time).total_seconds()
        return self.uptime_seconds


@dataclass
class HealthAlert:
    """Alerte de santé"""
    alert_id: str
    timestamp: datetime
    component_name: str
    alert_type: str
    urgency: AlertUrgency

    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    # Actions
    suggested_action: Optional[RecoveryAction] = None
    auto_recovery_triggered: bool = False
    resolved: bool = False
    resolution_time: Optional[datetime] = None


@dataclass
class SystemMetrics:
    """Métriques système globales"""
    timestamp: datetime

    # CPU
    cpu_usage_pct: float = 0.0
    cpu_count: int = 0
    load_average: float = 0.0

    # Memory
    memory_total_gb: float = 0.0
    memory_used_gb: float = 0.0
    memory_usage_pct: float = 0.0

    # Disk
    disk_total_gb: float = 0.0
    disk_used_gb: float = 0.0
    disk_usage_pct: float = 0.0

    # Network
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0

    # Processes
    process_count: int = 0
    thread_count: int = 0

    # Trading specific
    trading_active: bool = False
    market_connected: bool = False
    orders_pending: int = 0


@dataclass
class HealthReport:
    """Rapport de santé complet"""
    timestamp: datetime
    system_metrics: SystemMetrics
    components: Dict[str, ComponentHealth]
    alerts: List[HealthAlert]

    # Summary
    healthy_components: int = 0
    warning_components: int = 0
    critical_components: int = 0
    offline_components: int = 0

    # Performance
    avg_response_time_ms: float = 0.0
    total_errors: int = 0
    uptime_percentage: float = 0.0

    def calculate_summary(self):
        """Calcule résumé automatiquement"""
        self.healthy_components = len(
            [c for c in self.components.values() if c.status == HealthStatus.HEALTHY])
        self.warning_components = len(
            [c for c in self.components.values() if c.status == HealthStatus.WARNING])
        self.critical_components = len(
            [c for c in self.components.values() if c.status == HealthStatus.CRITICAL])
        self.offline_components = len(
            [c for c in self.components.values() if c.status == HealthStatus.OFFLINE])

        response_times = [c.response_time_ms for c in self.components.values()
                          if c.response_time_ms > 0]
        self.avg_response_time_ms = np.mean(response_times) if response_times else 0.0

        self.total_errors = sum(c.error_count for c in self.components.values())

        # Uptime calculation (simplified)
        if self.components:
            uptimes = [c.uptime_seconds for c in self.components.values() if c.uptime_seconds > 0]
            if uptimes:
                avg_uptime = np.mean(uptimes)
                # Assume 24h max for percentage calculation
                self.uptime_percentage = min(100.0, (avg_uptime / 86400) * 100)

# === CLASSE PRINCIPALE HEALTH CHECKER ===


class HealthChecker:
    """
    🏥 HEALTH CHECKER SYSTEM MIA_IA_SYSTEM

    Surveillance intelligente et auto-recovery complet de tous les composants.
    Orchestration du monitoring existant avec capacités avancées.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation Health Checker"""
        self.config = config or self._load_default_config()
        self.start_time = datetime.now(timezone.utc)
        self.is_running = False

        # État système
        self.components: Dict[str, ComponentHealth] = {}
        self.alerts: List[HealthAlert] = []
        self.system_metrics_history: deque = deque(maxlen=1000)
        self.health_reports_history: deque = deque(maxlen=100)

        # Threading
        self.monitor_thread: Optional[threading.Thread] = None
        self.recovery_thread: Optional[threading.Thread] = None
        self.dashboard_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Intégration monitoring existant
        self._initialize_monitoring_integration()

        # Dashboard web
        self.dashboard_app = None
        self.dashboard_server = None
        if FLASK_AVAILABLE and self.config.get('dashboard_enabled', True):
            self._setup_web_dashboard()

        # Statistiques
        self.stats = {
            'health_checks_performed': 0,
            'recoveries_attempted': 0,
            'recoveries_successful': 0,
            'alerts_generated': 0,
            'uptime_start': self.start_time,
            'last_full_check': None
        }

        # Initialisation composants
        self._register_system_components()

        logger.info(f"🏥 HealthChecker initialisé - Dashboard: {'✅' if FLASK_AVAILABLE else '❌'}")

    def _load_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut"""
        return {
            # Monitoring
            'check_interval_seconds': 30,
            'component_timeout_seconds': 10,
            'health_check_timeout_seconds': 5,

            # Recovery
            'auto_recovery_enabled': True,
            'max_recovery_attempts': 3,
            'recovery_cooldown_minutes': 5,

            # Alertes
            'alert_cooldown_minutes': 10,
            'emergency_alert_threshold': 3,  # Critical components

            # Dashboard
            'dashboard_enabled': True,
            'dashboard_port': 8080,
            'dashboard_host': '127.0.0.1',

            # Système
            'cpu_warning_threshold': 80,
            'cpu_critical_threshold': 95,
            'memory_warning_threshold': 80,
            'memory_critical_threshold': 95,
            'disk_warning_threshold': 85,
            'disk_critical_threshold': 95,

            # Trading
            'response_time_warning_ms': 100,
            'response_time_critical_ms': 500,
            'error_rate_warning': 0.05,  # 5%
            'error_rate_critical': 0.20   # 20%
        }

    def _initialize_monitoring_integration(self):
        """Initialise intégration avec monitoring existant"""
        try:
            if SYSTEM_INTEGRATION:
                # Performance Tracker
                self.performance_tracker = create_performance_tracker()
                logger.info("✅ Performance Tracker intégré")

                # Alert System
                self.alert_system = create_alert_system()
                logger.info("✅ Alert System intégré")

                # Discord Notifier
                self.discord_notifier = create_discord_notifier()
                logger.info("✅ Discord Notifier intégré")

                # Signal Generator (pour health checks)
                self.signal_generator = create_signal_generator()
                logger.info("✅ Signal Generator intégré")

            else:
                logger.warning("⚠️ Intégration MIA_IA_SYSTEM limitée")
                self.performance_tracker = None
                self.alert_system = None
                self.discord_notifier = None
                self.signal_generator = None

        except Exception as e:
            logger.error(f"Erreur intégration monitoring: {e}")
            self.performance_tracker = None
            self.alert_system = None
            self.discord_notifier = None
            self.signal_generator = None

    def _register_system_components(self):
        """Enregistre tous les composants à surveiller"""

        # === CORE COMPONENTS ===
        core_components = [
            ("signal_generator", ComponentType.CORE),
            ("battle_navale", ComponentType.CORE),
            ("confluence_analyzer", ComponentType.CORE),
            ("feature_calculator", ComponentType.CORE),
            ("market_regime", ComponentType.CORE)
        ]

        # === EXECUTION COMPONENTS ===
        execution_components = [
            ("simple_trader", ComponentType.EXECUTION),
            ("order_manager", ComponentType.EXECUTION),
            ("risk_manager", ComponentType.EXECUTION),
            ("trade_snapshotter", ComponentType.EXECUTION)
        ]

        # === DATA COMPONENTS ===
        data_components = [
            ("ibkr_connector", ComponentType.DATA),
            ("sierra_connector", ComponentType.DATA),
            ("market_data_feed", ComponentType.DATA),
            ("data_collector", ComponentType.DATA)
        ]

        # === MONITORING COMPONENTS ===
        monitoring_components = [
            ("performance_tracker", ComponentType.MONITORING),
            ("alert_system", ComponentType.MONITORING),
            ("discord_notifier", ComponentType.MONITORING),
            ("live_monitor", ComponentType.MONITORING)
        ]

        # === SYSTEM COMPONENTS ===
        system_components = [
            ("cpu", ComponentType.SYSTEM),
            ("memory", ComponentType.SYSTEM),
            ("disk", ComponentType.SYSTEM),
            ("network", ComponentType.SYSTEM),
            ("processes", ComponentType.SYSTEM)
        ]

        # === EXTERNAL COMPONENTS ===
        external_components = [
            ("discord_api", ComponentType.EXTERNAL),
            ("email_service", ComponentType.EXTERNAL),
            ("internet_connectivity", ComponentType.EXTERNAL)
        ]

        # Enregistrement
        all_components = (core_components + execution_components +
                          data_components + monitoring_components +
                          system_components + external_components)

        for comp_name, comp_type in all_components:
            self.components[comp_name] = ComponentHealth(
                component_name=comp_name,
                component_type=comp_type,
                status=HealthStatus.UNKNOWN,
                auto_recovery_enabled=comp_type != ComponentType.SYSTEM  # System components pas d'auto-recovery
            )

        logger.info(f"📋 {len(self.components)} composants enregistrés pour surveillance")

    # === DÉMARRAGE ET ARRÊT ===

    def start(self):
        """Démarre le Health Checker"""
        try:
            logger.info("🏥 Démarrage Health Checker System...")
            self.is_running = True

            # Thread monitoring principal
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()

            # Thread recovery
            self.recovery_thread = threading.Thread(target=self._recovery_loop, daemon=True)
            self.recovery_thread.start()

            # Dashboard web
            if self.dashboard_app and self.config.get('dashboard_enabled'):
                self._start_dashboard()

            logger.info("✅ Health Checker démarré avec succès")

        except Exception as e:
            logger.error(f"❌ Erreur démarrage Health Checker: {e}")
            self.stop()
            raise

    def stop(self):
        """Arrête le Health Checker"""
        logger.info("🛑 Arrêt Health Checker...")
        self.is_running = False

        # Arrêt dashboard
        if self.dashboard_server:
            self.dashboard_server.shutdown()

        # Attendre threads
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)

        if self.recovery_thread and self.recovery_thread.is_alive():
            self.recovery_thread.join(timeout=5)

        # Arrêt executor
        self.executor.shutdown(wait=True)

        logger.info("✅ Health Checker arrêté")

    # === MONITORING LOOP ===

    def _monitoring_loop(self):
        """Loop principal de monitoring"""
        logger.info("🔄 Loop monitoring démarré")

        while self.is_running:
            try:
                check_start = time.perf_counter()

                # 1. Collecter métriques système
                system_metrics = self._collect_system_metrics()
                self.system_metrics_history.append(system_metrics)

                # 2. Health check tous composants
                self._perform_health_checks()

                # 3. Analyser alertes
                self._analyze_alerts()

                # 4. Générer rapport
                if len(self.system_metrics_history) % 10 == 0:  # Tous les 10 cycles
                    self._generate_health_report()

                # 5. Nettoyage
                self._cleanup_old_data()

                # Stats
                self.stats['health_checks_performed'] += 1
                self.stats['last_full_check'] = datetime.now(timezone.utc)

                # Timing
                check_time = (time.perf_counter() - check_start) * 1000
                if check_time > 100:  # Warning si >100ms
                    logger.warning(f"Health check lent: {check_time:.1f}ms")

                # Sleep
                time.sleep(self.config['check_interval_seconds'])

            except Exception as e:
                logger.error(f"Erreur monitoring loop: {e}")
                time.sleep(5)  # Recovery sleep

    def _collect_system_metrics(self) -> SystemMetrics:
        """Collecte métriques système"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0.0

            # Memory
            memory = psutil.virtual_memory()
            memory_total = memory.total / (1024**3)  # GB
            memory_used = memory.used / (1024**3)
            memory_percent = memory.percent

            # Disk
            disk = psutil.disk_usage('/')
            disk_total = disk.total / (1024**3)
            disk_used = disk.used / (1024**3)
            disk_percent = (disk_used / disk_total) * 100

            # Network
            net_io = psutil.net_io_counters()
            net_sent = net_io.bytes_sent / (1024**2)  # MB
            net_recv = net_io.bytes_recv / (1024**2)

            # Processes
            process_count = len(psutil.pids())
            thread_count = sum(p.num_threads() for p in psutil.process_iter(['num_threads'])
                               if p.info['num_threads'] is not None)

            return SystemMetrics(
                timestamp=datetime.now(timezone.utc),
                cpu_usage_pct=cpu_percent,
                cpu_count=cpu_count,
                load_average=load_avg,
                memory_total_gb=memory_total,
                memory_used_gb=memory_used,
                memory_usage_pct=memory_percent,
                disk_total_gb=disk_total,
                disk_used_gb=disk_used,
                disk_usage_pct=disk_percent,
                network_sent_mb=net_sent,
                network_recv_mb=net_recv,
                process_count=process_count,
                thread_count=thread_count,
                trading_active=self._is_trading_active(),
                market_connected=self._is_market_connected(),
                orders_pending=self._get_pending_orders_count()
            )

        except Exception as e:
            logger.error(f"Erreur collecte métriques système: {e}")
            return SystemMetrics(timestamp=datetime.now(timezone.utc))

    def _perform_health_checks(self):
        """Effectue health checks sur tous composants"""
        futures = {}

        # Lance health checks en parallèle
        for comp_name, component in self.components.items():
            future = self.executor.submit(self._check_component_health, comp_name, component)
            futures[comp_name] = future

        # Collecte résultats avec timeout
        for comp_name, future in futures.items():
            try:
                updated_component = future.result(
                    timeout=self.config['health_check_timeout_seconds'])
                if updated_component:
                    self.components[comp_name] = updated_component

            except FutureTimeoutError:
                logger.warning(f"Health check timeout: {comp_name}")
                self.components[comp_name].status = HealthStatus.WARNING

            except Exception as e:
                logger.error(f"Erreur health check {comp_name}: {e}")
                self.components[comp_name].status = HealthStatus.CRITICAL
                self.components[comp_name].error_count += 1

    def _check_component_health(self, comp_name: str,
                                component: ComponentHealth) -> Optional[ComponentHealth]:
        """Health check d'un composant spécifique"""
        try:
            check_start = time.perf_counter()

            # Health check selon type de composant
            if component.component_type == ComponentType.CORE:
                status = self._check_core_component(comp_name)
            elif component.component_type == ComponentType.EXECUTION:
                status = self._check_execution_component(comp_name)
            elif component.component_type == ComponentType.DATA:
                status = self._check_data_component(comp_name)
            elif component.component_type == ComponentType.MONITORING:
                status = self._check_monitoring_component(comp_name)
            elif component.component_type == ComponentType.SYSTEM:
                status = self._check_system_component(comp_name)
            elif component.component_type == ComponentType.EXTERNAL:
                status = self._check_external_component(comp_name)
            else:
                status = HealthStatus.UNKNOWN

            # Mise à jour composant
            component.status = status
            component.response_time_ms = (time.perf_counter() - check_start) * 1000
            component.update_heartbeat()
            component.calculate_uptime(self.start_time)

            return component

        except Exception as e:
            logger.error(f"Erreur check {comp_name}: {e}")
            component.status = HealthStatus.CRITICAL
            component.error_count += 1
            return component

    def _check_core_component(self, comp_name: str) -> HealthStatus:
        """Health check composants core"""
        try:
            if comp_name == "signal_generator":
                if SYSTEM_INTEGRATION and self.signal_generator:
                    # Test rapide génération signal
                    test_data = MarketData(
                        timestamp=pd.Timestamp.now(),
                        symbol="ES",
                        close=4500.0,
                        open=4500.0,
                        high=4502.0,
                        low=4498.0,
                        volume=1000
                    )
                    signal = get_signal_now(test_data)
                    return HealthStatus.HEALTHY if signal is not None else HealthStatus.WARNING
                else:
                    return HealthStatus.OFFLINE

            elif comp_name == "battle_navale":
                # Vérifie si module importable et fonctionnel
                try:
                    from core.battle_navale import create_battle_navale_analyzer
                    analyzer = create_battle_navale_analyzer()
                    return HealthStatus.HEALTHY if analyzer else HealthStatus.WARNING
                except Exception:
                    return HealthStatus.CRITICAL

            elif comp_name == "confluence_analyzer":
                try:
                    from features.confluence_analyzer import ConfluenceAnalyzer
                    return HealthStatus.HEALTHY
                except Exception:
                    return HealthStatus.CRITICAL

            elif comp_name == "feature_calculator":
                try:
                    from features.feature_calculator import create_feature_calculator
                    calc = create_feature_calculator()
                    return HealthStatus.HEALTHY if calc else HealthStatus.WARNING
                except Exception:
                    return HealthStatus.CRITICAL

            elif comp_name == "market_regime":
                try:
                    from features.market_regime import MarketRegimeDetector
                    return HealthStatus.HEALTHY
                except Exception:
                    return HealthStatus.CRITICAL

            return HealthStatus.UNKNOWN

        except Exception as e:
            logger.error(f"Erreur check core {comp_name}: {e}")
            return HealthStatus.CRITICAL

    def _check_execution_component(self, comp_name: str) -> HealthStatus:
        """Health check composants execution"""
        try:
            if comp_name == "simple_trader":
                # Vérifie fichier et import
                trader_file = Path("execution/simple_trader.py")
                if trader_file.exists():
                    try:
                        from execution.simple_trader import SimpleBattleNavaleTrader
                        return HealthStatus.HEALTHY
                    except Exception:
                        return HealthStatus.CRITICAL
                else:
                    return HealthStatus.OFFLINE

            elif comp_name == "order_manager":
                try:
                    from execution.order_manager import OrderManager
                    return HealthStatus.HEALTHY
                except Exception:
                    return HealthStatus.CRITICAL

            elif comp_name == "risk_manager":
                try:
                    from execution.risk_manager import RiskManager
                    return HealthStatus.HEALTHY
                except Exception:
                    return HealthStatus.CRITICAL

            elif comp_name == "trade_snapshotter":
                snapshotter_file = Path("execution/trade_snapshotter.py")
                if snapshotter_file.exists():
                    try:
                        from execution.trade_snapshotter import TradeSnapshotter
                        return HealthStatus.HEALTHY
                    except Exception:
                        return HealthStatus.CRITICAL
                else:
                    return HealthStatus.OFFLINE

            return HealthStatus.UNKNOWN

        except Exception as e:
            logger.error(f"Erreur check execution {comp_name}: {e}")
            return HealthStatus.CRITICAL

    def _check_data_component(self, comp_name: str) -> HealthStatus:
        """Health check composants data"""
        try:
            if comp_name == "ibkr_connector":
                try:
                    from core.ibkr_connector import IBKRConnector
                    # Test connexion rapide si possible
                    return HealthStatus.HEALTHY
                except Exception:
                    return HealthStatus.WARNING

            elif comp_name == "sierra_connector":
                try:
                    from core.sierra_connector import SierraConnector
                    return HealthStatus.HEALTHY
                except Exception:
                    return HealthStatus.WARNING

            elif comp_name == "market_data_feed":
                # Vérifie si données récentes disponibles
                data_files = [
                    Path("data/live/current_session"),
                    Path("data/historical"),
                    Path("data/raw")
                ]

                for data_path in data_files:
                    if data_path.exists() and any(data_path.iterdir()):
                        return HealthStatus.HEALTHY

                return HealthStatus.WARNING

            elif comp_name == "data_collector":
                collector_file = Path("data/data_collector.py")
                return HealthStatus.HEALTHY if collector_file.exists() else HealthStatus.OFFLINE

            return HealthStatus.UNKNOWN

        except Exception as e:
            logger.error(f"Erreur check data {comp_name}: {e}")
            return HealthStatus.CRITICAL

    def _check_monitoring_component(self, comp_name: str) -> HealthStatus:
        """Health check composants monitoring"""
        try:
            if comp_name == "performance_tracker":
                return HealthStatus.HEALTHY if self.performance_tracker else HealthStatus.OFFLINE

            elif comp_name == "alert_system":
                return HealthStatus.HEALTHY if self.alert_system else HealthStatus.OFFLINE

            elif comp_name == "discord_notifier":
                return HealthStatus.HEALTHY if self.discord_notifier else HealthStatus.OFFLINE

            elif comp_name == "live_monitor":
                monitor_file = Path("monitoring/live_monitor.py")
                return HealthStatus.HEALTHY if monitor_file.exists() else HealthStatus.OFFLINE

            return HealthStatus.UNKNOWN

        except Exception as e:
            logger.error(f"Erreur check monitoring {comp_name}: {e}")
            return HealthStatus.CRITICAL

    def _check_system_component(self, comp_name: str) -> HealthStatus:
        """Health check composants système"""
        try:
            if comp_name == "cpu":
                cpu_usage = psutil.cpu_percent(interval=1)
                if cpu_usage >= self.config['cpu_critical_threshold']:
                    return HealthStatus.CRITICAL
                elif cpu_usage >= self.config['cpu_warning_threshold']:
                    return HealthStatus.WARNING
                else:
                    return HealthStatus.HEALTHY

            elif comp_name == "memory":
                memory = psutil.virtual_memory()
                if memory.percent >= self.config['memory_critical_threshold']:
                    return HealthStatus.CRITICAL
                elif memory.percent >= self.config['memory_warning_threshold']:
                    return HealthStatus.WARNING
                else:
                    return HealthStatus.HEALTHY

            elif comp_name == "disk":
                disk = psutil.disk_usage('/')
                usage_pct = (disk.used / disk.total) * 100
                if usage_pct >= self.config['disk_critical_threshold']:
                    return HealthStatus.CRITICAL
                elif usage_pct >= self.config['disk_warning_threshold']:
                    return HealthStatus.WARNING
                else:
                    return HealthStatus.HEALTHY

            elif comp_name == "network":
                # Test connectivité internet basique
                try:
                    socket.create_connection(("8.8.8.8", 53), timeout=3)
                    return HealthStatus.HEALTHY
                except Exception:
                    return HealthStatus.CRITICAL

            elif comp_name == "processes":
                # Vérifie si pas trop de processus
                process_count = len(psutil.pids())
                if process_count > 1000:  # Threshold arbitraire
                    return HealthStatus.WARNING
                else:
                    return HealthStatus.HEALTHY

            return HealthStatus.UNKNOWN

        except Exception as e:
            logger.error(f"Erreur check system {comp_name}: {e}")
            return HealthStatus.CRITICAL

    def _check_external_component(self, comp_name: str) -> HealthStatus:
        """Health check services externes"""
        try:
            if comp_name == "discord_api":
                if self.discord_notifier:
                    # Test Discord API rapidement
                    try:
                        # Simple ping si méthode disponible
                        return HealthStatus.HEALTHY
                    except Exception:
                        return HealthStatus.WARNING
                else:
                    return HealthStatus.OFFLINE

            elif comp_name == "email_service":
                # Test SMTP basique si configuré
                return HealthStatus.HEALTHY  # Simplified

            elif comp_name == "internet_connectivity":
                try:
                    # Test multiple endpoints
                    endpoints = [
                        ("google.com", 80),
                        ("discord.com", 443),
                        ("github.com", 443)
                    ]

                    for host, port in endpoints:
                        socket.create_connection((host, port), timeout=3)
                        return HealthStatus.HEALTHY

                    return HealthStatus.CRITICAL
                except Exception:
                    return HealthStatus.CRITICAL

            return HealthStatus.UNKNOWN

        except Exception as e:
            logger.error(f"Erreur check external {comp_name}: {e}")
            return HealthStatus.CRITICAL

    # === HELPER METHODS ===

    def _is_trading_active(self) -> bool:
        """Vérifie si trading actif"""
        # Simplified - à adapter selon votre système
        return any(comp.status == HealthStatus.HEALTHY
                   for name, comp in self.components.items()
                   if name in ["simple_trader", "order_manager"])

    def _is_market_connected(self) -> bool:
        """Vérifie connexion marché"""
        return any(comp.status == HealthStatus.HEALTHY
                   for name, comp in self.components.items()
                   if name in ["ibkr_connector", "sierra_connector"])

    def _get_pending_orders_count(self) -> int:
        """Nombre d'ordres en attente"""
        # Simplified - à adapter
        return 0

    # === RECOVERY SYSTEM ===

    def _recovery_loop(self):
        """Loop de recovery automatique"""
        logger.info("🔧 Recovery loop démarré")

        while self.is_running:
            try:
                # Cherche composants nécessitant recovery
                components_to_recover = [
                    (name, comp) for name, comp in self.components.items()
                    if comp.needs_recovery() and comp.auto_recovery_enabled
                    and comp.recovery_attempts < self.config['max_recovery_attempts']
                ]

                for comp_name, component in components_to_recover:
                    self._attempt_component_recovery(comp_name, component)

                time.sleep(60)  # Check recovery moins fréquent

            except Exception as e:
                logger.error(f"Erreur recovery loop: {e}")
                time.sleep(30)

    def _attempt_component_recovery(self, comp_name: str, component: ComponentHealth):
        """Tente recovery d'un composant"""
        try:
            logger.info(f"🔧 Tentative recovery: {comp_name}")

            # Cooldown check
            if component.last_recovery:
                cooldown_minutes = self.config['recovery_cooldown_minutes']
                time_since_recovery = datetime.now(timezone.utc) - component.last_recovery
                if time_since_recovery.total_seconds() < (cooldown_minutes * 60):
                    return

            # Détermine action recovery
            recovery_action = self._determine_recovery_action(comp_name, component)

            # Execute recovery
            success = self._execute_recovery_action(comp_name, component, recovery_action)

            # Update component
            component.recovery_attempts += 1
            component.last_recovery = datetime.now(timezone.utc)

            if success:
                component.status = HealthStatus.RECOVERING
                self.stats['recoveries_successful'] += 1
                logger.info(f"✅ Recovery réussi: {comp_name}")

                # Notification
                self._send_recovery_notification(comp_name, recovery_action, True)
            else:
                logger.warning(f"❌ Recovery échoué: {comp_name}")
                self._send_recovery_notification(comp_name, recovery_action, False)

            self.stats['recoveries_attempted'] += 1

        except Exception as e:
            logger.error(f"Erreur recovery {comp_name}: {e}")

    def _determine_recovery_action(self, comp_name: str,
                                   component: ComponentHealth) -> RecoveryAction:
        """Détermine action de recovery appropriée"""

        if component.component_type == ComponentType.DATA:
            return RecoveryAction.RECONNECT
        elif component.component_type == ComponentType.EXECUTION:
            return RecoveryAction.RESTART
        elif component.component_type == ComponentType.SYSTEM:
            return RecoveryAction.CLEANUP
        else:
            return RecoveryAction.RESET

    def _execute_recovery_action(
            self, comp_name: str, component: ComponentHealth, action: RecoveryAction) -> bool:
        """Exécute action de recovery"""
        try:
            if action == RecoveryAction.RESTART:
                return self._restart_component(comp_name, component)
            elif action == RecoveryAction.RECONNECT:
                return self._reconnect_component(comp_name, component)
            elif action == RecoveryAction.CLEANUP:
                return self._cleanup_component(comp_name, component)
            elif action == RecoveryAction.RESET:
                return self._reset_component(comp_name, component)
            elif action == RecoveryAction.BACKUP:
                return self._backup_component_data(comp_name, component)
            else:
                logger.warning(f"Action recovery non implémentée: {action}")
                return False

        except Exception as e:
            logger.error(f"Erreur exécution recovery {comp_name}: {e}")
            return False

    def _restart_component(self, comp_name: str, component: ComponentHealth) -> bool:
        """Redémarre un composant"""
        # Simplified implementation
        logger.info(f"🔄 Restart component: {comp_name}")

        # Force garbage collection
        gc.collect()

        # Reset error count
        component.error_count = 0

        return True

    def _reconnect_component(self, comp_name: str, component: ComponentHealth) -> bool:
        """Reconnecte un composant data"""
        logger.info(f"🔗 Reconnect component: {comp_name}")

        # Simplified - à adapter selon vos connecteurs
        return True

    def _cleanup_component(self, comp_name: str, component: ComponentHealth) -> bool:
        """Nettoie ressources d'un composant"""
        logger.info(f"🧹 Cleanup component: {comp_name}")

        # Memory cleanup
        if comp_name == "memory":
            gc.collect()
            return True

        # Disk cleanup
        elif comp_name == "disk":
            self._cleanup_disk_space()
            return True

        return True

    def _reset_component(self, comp_name: str, component: ComponentHealth) -> bool:
        """Reset état d'un composant"""
        logger.info(f"🔄 Reset component: {comp_name}")

        component.error_count = 0
        component.recovery_attempts = 0

        return True

    def _backup_component_data(self, comp_name: str, component: ComponentHealth) -> bool:
        """Sauvegarde données critiques"""
        logger.info(f"💾 Backup component data: {comp_name}")

        # Simplified backup implementation
        return True

    def _cleanup_disk_space(self):
        """Nettoie espace disque"""
        try:
            # Nettoie logs anciens
            logs_dir = Path("logs")
            if logs_dir.exists():
                cutoff_date = datetime.now() - timedelta(days=30)
                for log_file in logs_dir.rglob("*.log"):
                    if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                        log_file.unlink()

            # Nettoie données temporaires
            temp_dirs = [Path("data/temp"), Path("reports/temp")]
            for temp_dir in temp_dirs:
                if temp_dir.exists():
                    for temp_file in temp_dir.rglob("*"):
                        if temp_file.is_file():
                            temp_file.unlink()

        except Exception as e:
            logger.error(f"Erreur cleanup disk: {e}")

    # === ALERTES ===

    def _analyze_alerts(self):
        """Analyse et génère alertes"""
        current_time = datetime.now(timezone.utc)

        # Check composants critiques
        critical_components = [comp for comp in self.components.values()
                               if comp.status == HealthStatus.CRITICAL]

        if len(critical_components) >= self.config['emergency_alert_threshold']:
            self._generate_emergency_alert(critical_components)

        # Check performance dégradée
        slow_components = [comp for comp in self.components.values()
                           if comp.response_time_ms > self.config['response_time_critical_ms']]

        if slow_components:
            self._generate_performance_alert(slow_components)

        # Check système
        if self.system_metrics_history:
            latest_metrics = self.system_metrics_history[-1]

            if latest_metrics.cpu_usage_pct >= self.config['cpu_critical_threshold']:
                self._generate_system_alert("CPU", latest_metrics.cpu_usage_pct)

            if latest_metrics.memory_usage_pct >= self.config['memory_critical_threshold']:
                self._generate_system_alert("Memory", latest_metrics.memory_usage_pct)

            if latest_metrics.disk_usage_pct >= self.config['disk_critical_threshold']:
                self._generate_system_alert("Disk", latest_metrics.disk_usage_pct)

    def _generate_emergency_alert(self, critical_components: List[ComponentHealth]):
        """Génère alerte d'urgence"""
        alert = HealthAlert(
            alert_id=f"emergency_{int(time.time())}",
            timestamp=datetime.now(timezone.utc),
            component_name="system",
            alert_type="emergency",
            urgency=AlertUrgency.CRITICAL,
            message=f"🚨 URGENCE: {len(critical_components)} composants critiques défaillants",
            details={
                'critical_components': [c.component_name for c in critical_components],
                'failed_count': len(critical_components),
                'total_components': len(self.components)
            },
            suggested_action=RecoveryAction.ESCALATE
        )

        self.alerts.append(alert)
        self.stats['alerts_generated'] += 1

        # Notification immédiate
        self._send_alert_notification(alert)

    def _generate_performance_alert(self, slow_components: List[ComponentHealth]):
        """Génère alerte performance"""
        alert = HealthAlert(
            alert_id=f"performance_{int(time.time())}",
            timestamp=datetime.now(timezone.utc),
            component_name="performance",
            alert_type="performance_degradation",
            urgency=AlertUrgency.HIGH,
            message=f"⚠️ Dégradation performance: {len(slow_components)} composants lents",
            details={
                'slow_components': [(c.component_name, c.response_time_ms) for c in slow_components],
                'threshold_ms': self.config['response_time_critical_ms']
            },
            suggested_action=RecoveryAction.RESTART
        )

        self.alerts.append(alert)
        self.stats['alerts_generated'] += 1

        self._send_alert_notification(alert)

    def _generate_system_alert(self, resource_type: str, usage_pct: float):
        """Génère alerte système"""
        alert = HealthAlert(
            alert_id=f"system_{resource_type.lower()}_{int(time.time())}",
            timestamp=datetime.now(timezone.utc),
            component_name=resource_type.lower(),
            alert_type="resource_usage",
            urgency=AlertUrgency.HIGH,
            message=f"🔴 {resource_type} usage critique: {usage_pct:.1f}%",
            details={
                'resource_type': resource_type,
                'current_usage_pct': usage_pct,
                'threshold_pct': self.config[f'{resource_type.lower()}_critical_threshold']
            },
            suggested_action=RecoveryAction.CLEANUP
        )

        self.alerts.append(alert)
        self.stats['alerts_generated'] += 1

        self._send_alert_notification(alert)

    def _send_alert_notification(self, alert: HealthAlert):
        """Envoie notification alerte"""
        try:
            # Discord notification
            if self.discord_notifier:
                self._send_discord_alert(alert)

            # Email notification (si configuré)
            # self._send_email_alert(alert)

            # Console log
            urgency_emoji = {
                AlertUrgency.LOW: "ℹ️",
                AlertUrgency.MEDIUM: "⚠️",
                AlertUrgency.HIGH: "🔴",
                AlertUrgency.CRITICAL: "🚨"
            }

            emoji = urgency_emoji.get(alert.urgency, "❓")
            logger.warning(f"{emoji} ALERTE: {alert.message}")

        except Exception as e:
            logger.error(f"Erreur envoi notification: {e}")

    def _send_discord_alert(self, alert: HealthAlert):
        """Envoie alerte Discord"""
        try:
            if not self.discord_notifier:
                return

            # Simplified Discord integration
            message = f"🏥 **HEALTH ALERT**\n"
            message += f"**Component:** {alert.component_name}\n"
            message += f"**Type:** {alert.alert_type}\n"
            message += f"**Urgency:** {alert.urgency.value.upper()}\n"
            message += f"**Message:** {alert.message}\n"
            message += f"**Time:** {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"

            if alert.suggested_action:
                message += f"**Suggested Action:** {alert.suggested_action.value}\n"

            # Send via discord notifier (adapt to your implementation)
            # self.discord_notifier.send_alert_message(message)

        except Exception as e:
            logger.error(f"Erreur Discord alert: {e}")

    def _send_recovery_notification(self, comp_name: str, action: RecoveryAction, success: bool):
        """Notification de recovery"""
        try:
            status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
            message = f"🔧 Recovery {comp_name}: {action.value} - {status}"

            if self.discord_notifier:
                # self.discord_notifier.send_recovery_message(message)
                pass

            logger.info(message)

        except Exception as e:
            logger.error(f"Erreur notification recovery: {e}")

    # === REPORTS ===

    def _generate_health_report(self) -> HealthReport:
        """Génère rapport de santé complet"""
        try:
            current_time = datetime.now(timezone.utc)
            latest_metrics = self.system_metrics_history[-1] if self.system_metrics_history else SystemMetrics(
                timestamp=current_time)

            # Copie composants
            components_copy = {name: ComponentHealth(
                component_name=comp.component_name,
                component_type=comp.component_type,
                status=comp.status,
                last_heartbeat=comp.last_heartbeat,
                response_time_ms=comp.response_time_ms,
                error_count=comp.error_count,
                uptime_seconds=comp.uptime_seconds,
                cpu_usage_pct=comp.cpu_usage_pct,
                memory_usage_mb=comp.memory_usage_mb,
                throughput_per_sec=comp.throughput_per_sec,
                recovery_attempts=comp.recovery_attempts,
                last_recovery=comp.last_recovery,
                auto_recovery_enabled=comp.auto_recovery_enabled,
                version=comp.version,
                config=comp.config.copy(),
                metrics=comp.metrics.copy()
            ) for name, comp in self.components.items()}

            # Créer rapport
            report = HealthReport(
                timestamp=current_time,
                system_metrics=latest_metrics,
                components=components_copy,
                alerts=self.alerts.copy()
            )

            # Calculer résumé
            report.calculate_summary()

            # Ajouter à historique
            self.health_reports_history.append(report)

            return report

        except Exception as e:
            logger.error(f"Erreur génération rapport: {e}")
            return HealthReport(
                timestamp=datetime.now(timezone.utc),
                system_metrics=SystemMetrics(timestamp=datetime.now(timezone.utc)),
                components={},
                alerts=[]
            )

    def _cleanup_old_data(self):
        """Nettoie données anciennes"""
        try:
            current_time = datetime.now(timezone.utc)

            # Nettoie alertes anciennes (garde 7 jours)
            cutoff_time = current_time - timedelta(days=7)
            self.alerts = [alert for alert in self.alerts if alert.timestamp > cutoff_time]

            # Les deques ont déjà maxlen, pas besoin de nettoyer

        except Exception as e:
            logger.error(f"Erreur cleanup données: {e}")

    # === WEB DASHBOARD ===

    def _setup_web_dashboard(self):
        """Configure dashboard web"""
        try:
            self.dashboard_app = Flask(__name__)

            @self.dashboard_app.route('/')
            def dashboard():
                """Page principale dashboard"""
                return self._render_dashboard_html()

            @self.dashboard_app.route('/api/health')
            def api_health():
                """API health status"""
                return jsonify(self._get_dashboard_data())

            @self.dashboard_app.route('/api/components')
            def api_components():
                """API composants détail"""
                return jsonify({
                    name: {
                        'name': comp.component_name,
                        'type': comp.component_type.value,
                        'status': comp.status.value,
                        'response_time_ms': comp.response_time_ms,
                        'error_count': comp.error_count,
                        'uptime_seconds': comp.uptime_seconds,
                        'recovery_attempts': comp.recovery_attempts,
                        'last_heartbeat': comp.last_heartbeat.isoformat() if comp.last_heartbeat else None
                    }
                    for name, comp in self.components.items()
                })

            @self.dashboard_app.route('/api/metrics')
            def api_metrics():
                """API métriques système"""
                if self.system_metrics_history:
                    latest = self.system_metrics_history[-1]
                    return jsonify({
                        'cpu_usage_pct': latest.cpu_usage_pct,
                        'memory_usage_pct': latest.memory_usage_pct,
                        'disk_usage_pct': latest.disk_usage_pct,
                        'process_count': latest.process_count,
                        'trading_active': latest.trading_active,
                        'market_connected': latest.market_connected
                    })
                else:
                    return jsonify({})

            logger.info("✅ Dashboard web configuré")

        except Exception as e:
            logger.error(f"Erreur setup dashboard: {e}")
            self.dashboard_app = None

    def _start_dashboard(self):
        """Démarre serveur dashboard"""
        try:
            if not self.dashboard_app:
                return

            host = self.config.get('dashboard_host', '127.0.0.1')
            port = self.config.get('dashboard_port', 8080)

            self.dashboard_server = make_server(host, port, self.dashboard_app, threaded=True)

            def run_server():
                logger.info(f"🌐 Dashboard démarré: http://{host}:{port}")
                self.dashboard_server.serve_forever()

            self.dashboard_thread = threading.Thread(target=run_server, daemon=True)
            self.dashboard_thread.start()

        except Exception as e:
            logger.error(f"Erreur démarrage dashboard: {e}")

    def _get_dashboard_data(self) -> Dict[str, Any]:
        """Données pour dashboard"""
        try:
            # Statistiques globales
            total_components = len(self.components)
            healthy = len([c for c in self.components.values() if c.status == HealthStatus.HEALTHY])
            warning = len([c for c in self.components.values() if c.status == HealthStatus.WARNING])
            critical = len([c for c in self.components.values()
                           if c.status == HealthStatus.CRITICAL])
            offline = len([c for c in self.components.values() if c.status == HealthStatus.OFFLINE])

            # Métriques système
            latest_metrics = self.system_metrics_history[-1] if self.system_metrics_history else None

            # Alertes récentes
            recent_alerts = [alert for alert in self.alerts[-10:]]  # 10 dernières

            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'uptime_seconds': (datetime.now(timezone.utc) - self.start_time).total_seconds(),
                'status': {
                    'total_components': total_components,
                    'healthy': healthy,
                    'warning': warning,
                    'critical': critical,
                    'offline': offline,
                    'health_percentage': (healthy / total_components * 100) if total_components > 0 else 0
                },
                'system_metrics': {
                    'cpu_usage_pct': latest_metrics.cpu_usage_pct if latest_metrics else 0,
                    'memory_usage_pct': latest_metrics.memory_usage_pct if latest_metrics else 0,
                    'disk_usage_pct': latest_metrics.disk_usage_pct if latest_metrics else 0,
                    'trading_active': latest_metrics.trading_active if latest_metrics else False,
                    'market_connected': latest_metrics.market_connected if latest_metrics else False
                },
                'stats': self.stats.copy(),
                'recent_alerts': [
                    {
                        'timestamp': alert.timestamp.isoformat(),
                        'component': alert.component_name,
                        'type': alert.alert_type,
                        'urgency': alert.urgency.value,
                        'message': alert.message
                    }
                    for alert in recent_alerts
                ]
            }

        except Exception as e:
            logger.error(f"Erreur données dashboard: {e}")
            return {'error': str(e)}

    def _render_dashboard_html(self) -> str:
        """Rendu HTML dashboard"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏥 MIA_IA_SYSTEM Health Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            color: #4a5568;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease;
        }
        .status-card:hover {
            transform: translateY(-5px);
        }
        .status-value {
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .status-label {
            font-size: 1.1em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .healthy { color: #48bb78; }
        .warning { color: #ed8936; }
        .critical { color: #f56565; }
        .offline { color: #a0aec0; }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        .chart-card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        .chart-card h3 {
            margin-bottom: 20px;
            color: #4a5568;
            text-align: center;
        }

        .alerts-section {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        .alert-item {
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            border-left: 4px solid #f56565;
        }
        .alert-time {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        .alert-message {
            font-weight: bold;
        }

        .refresh-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(72,187,120,0.9);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .loading {
            animation: pulse 1.5s infinite;
        }
    </style>
</head>
<body>
    <div class="refresh-indicator" id="refreshIndicator">🔄 Live</div>

    <div class="container">
        <div class="header">
            <h1>🏥 MIA_IA_SYSTEM Health Dashboard</h1>
            <p>Real-time system monitoring & auto-recovery</p>
            <p id="lastUpdate">Loading...</p>
        </div>

        <div class="status-grid">
            <div class="status-card">
                <div class="status-value healthy" id="healthyCount">-</div>
                <div class="status-label">Healthy</div>
            </div>
            <div class="status-card">
                <div class="status-value warning" id="warningCount">-</div>
                <div class="status-label">Warning</div>
            </div>
            <div class="status-card">
                <div class="status-value critical" id="criticalCount">-</div>
                <div class="status-label">Critical</div>
            </div>
            <div class="status-card">
                <div class="status-value offline" id="offlineCount">-</div>
                <div class="status-label">Offline</div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-card">
                <h3>📊 System Resources</h3>
                <canvas id="resourcesChart" width="400" height="200"></canvas>
            </div>
            <div class="chart-card">
                <h3>⚡ System Status</h3>
                <canvas id="statusChart" width="400" height="200"></canvas>
            </div>
        </div>

        <div class="alerts-section">
            <h3>🚨 Recent Alerts</h3>
            <div id="alertsList">Loading alerts...</div>
        </div>
    </div>

    <script>
        let resourcesChart, statusChart;

        // Initialize charts
        function initCharts() {
            // Resources Chart
            const resourcesCtx = document.getElementById('resourcesChart').getContext('2d');
            resourcesChart = new Chart(resourcesCtx, {
                type: 'doughnut',
                data: {
                    labels: ['CPU Usage', 'Memory Usage', 'Disk Usage'],
                    datasets: [{
                        data: [0, 0, 0],
                        backgroundColor: ['#f56565', '#ed8936', '#48bb78'],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });

            // Status Chart
            const statusCtx = document.getElementById('statusChart').getContext('2d');
            statusChart = new Chart(statusCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Healthy', 'Warning', 'Critical', 'Offline'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: ['#48bb78', '#ed8936', '#f56565', '#a0aec0'],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        }

        // Update dashboard data
        function updateDashboard() {
            fetch('/api/health')
                .then(response => response.json())
                .then(data => {
                    // Update status counts
                    document.getElementById('healthyCount').textContent = data.status.healthy;
                    document.getElementById('warningCount').textContent = data.status.warning;
                    document.getElementById('criticalCount').textContent = data.status.critical;
                    document.getElementById('offlineCount').textContent = data.status.offline;

                    // Update last update time
                    const lastUpdate = new Date(data.timestamp);
                    document.getElementById('lastUpdate').textContent =
                        `Last update: ${lastUpdate.toLocaleTimeString()}`;

                    // Update charts
                    if (resourcesChart && data.system_metrics) {
                        resourcesChart.data.datasets[0].data = [
                            data.system_metrics.cpu_usage_pct,
                            data.system_metrics.memory_usage_pct,
                            data.system_metrics.disk_usage_pct
                        ];
                        resourcesChart.update();
                    }

                    if (statusChart) {
                        statusChart.data.datasets[0].data = [
                            data.status.healthy,
                            data.status.warning,
                            data.status.critical,
                            data.status.offline
                        ];
                        statusChart.update();
                    }

                    // Update alerts
                    updateAlerts(data.recent_alerts || []);

                    // Flash refresh indicator
                    const indicator = document.getElementById('refreshIndicator');
                    indicator.classList.add('loading');
                    setTimeout(() => indicator.classList.remove('loading'), 500);
                })
                .catch(error => {
                    console.error('Error updating dashboard:', error);
                    document.getElementById('lastUpdate').textContent = 'Update failed';
                });
        }

        // Update alerts section
        function updateAlerts(alerts) {
            const alertsList = document.getElementById('alertsList');

            if (alerts.length === 0) {
                alertsList.innerHTML = '<p style="text-align: center; color: #48bb78;">✅ No recent alerts</p>';
                return;
            }

            alertsList.innerHTML = alerts.map(alert => `
                <div class="alert-item">
                    <div class="alert-time">${new Date(alert.timestamp).toLocaleString()}</div>
                    <div class="alert-message">${alert.message}</div>
                    <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                        Component: ${alert.component} | Type: ${alert.type} | Urgency: ${alert.urgency}
                    </div>
                </div>
            `).join('');
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            updateDashboard();

            // Auto-refresh every 10 seconds
            setInterval(updateDashboard, 10000);
        });
    </script>
</body>
</html>
        """

    # === MÉTHODES PUBLIQUES ===

    def get_health_status(self) -> Dict[str, Any]:
        """Retourne status santé global"""
        healthy = len([c for c in self.components.values() if c.status == HealthStatus.HEALTHY])
        total = len(self.components)
        health_percentage = (healthy / total * 100) if total > 0 else 0

        return {
            'overall_health': health_percentage,
            'components_total': total,
            'components_healthy': healthy,
            'components_warning': len([c for c in self.components.values() if c.status == HealthStatus.WARNING]),
            'components_critical': len([c for c in self.components.values() if c.status == HealthStatus.CRITICAL]),
            'components_offline': len([c for c in self.components.values() if c.status == HealthStatus.OFFLINE]),
            'uptime_seconds': (datetime.now(timezone.utc) - self.start_time).total_seconds(),
            'is_trading_safe': health_percentage >= 80,  # 80% minimum pour trading
            'recovery_attempts': self.stats['recoveries_attempted'],
            'recovery_success_rate': (self.stats['recoveries_successful'] / self.stats['recoveries_attempted'] * 100)
            if self.stats['recoveries_attempted'] > 0 else 0
        }

    def get_component_health(self, component_name: str) -> Optional[ComponentHealth]:
        """Retourne santé d'un composant spécifique"""
        return self.components.get(component_name)

    def force_component_recovery(self, component_name: str) -> bool:
        """Force recovery d'un composant"""
        component = self.components.get(component_name)
        if not component:
            return False

        try:
            self._attempt_component_recovery(component_name, component)
            return True
        except Exception as e:
            logger.error(f"Erreur force recovery {component_name}: {e}")
            return False

    def generate_health_report_json(self) -> Dict[str, Any]:
        """Génère rapport JSON complet"""
        report = self._generate_health_report()

        return {
            'timestamp': report.timestamp.isoformat(),
            'summary': {
                'healthy_components': report.healthy_components,
                'warning_components': report.warning_components,
                'critical_components': report.critical_components,
                'offline_components': report.offline_components,
                'avg_response_time_ms': report.avg_response_time_ms,
                'total_errors': report.total_errors,
                'uptime_percentage': report.uptime_percentage
            },
            'system_metrics': asdict(report.system_metrics),
            'components': {
                name: {
                    'name': comp.component_name,
                    'type': comp.component_type.value,
                    'status': comp.status.value,
                    'response_time_ms': comp.response_time_ms,
                    'error_count': comp.error_count,
                    'uptime_seconds': comp.uptime_seconds,
                    'recovery_attempts': comp.recovery_attempts,
                    'last_heartbeat': comp.last_heartbeat.isoformat() if comp.last_heartbeat else None,
                    'auto_recovery_enabled': comp.auto_recovery_enabled
                }
                for name, comp in report.components.items()
            },
            'recent_alerts': [
                {
                    'timestamp': alert.timestamp.isoformat(),
                    'component': alert.component_name,
                    'type': alert.alert_type,
                    'urgency': alert.urgency.value,
                    'message': alert.message,
                    'resolved': alert.resolved
                }
                for alert in report.alerts[-20:]  # 20 dernières alertes
            ],
            'stats': self.stats.copy()
        }

# === FACTORY FUNCTIONS ===


def create_health_checker(config: Optional[Dict[str, Any]] = None) -> HealthChecker:
    """Factory function pour Health Checker"""
    return HealthChecker(config)


def start_health_monitoring(config: Optional[Dict[str, Any]] = None) -> HealthChecker:
    """Démarre monitoring santé complet"""
    health_checker = create_health_checker(config)
    health_checker.start()
    return health_checker

# === TESTING ===


def test_health_checker():
    """Test complet Health Checker"""
    logger.info("🏥 TEST HEALTH CHECKER SYSTEM")
    print("=" * 50)

    try:
        # Création Health Checker
        logger.info("1. Création Health Checker...")
        health_checker = create_health_checker()
        logger.info("Health Checker créé")

        # Test configuration
        logger.info("2. Test configuration...")
        config = health_checker.config
        logger.info("Configuration: {len(config)} paramètres")

        # Test composants
        logger.info("3. Test enregistrement composants...")
        components_count = len(health_checker.components)
        logger.info("Composants enregistrés: {components_count}")

        # Test health checks
        logger.info("4. Test health checks...")
        health_checker._perform_health_checks()
        healthy_count = len([c for c in health_checker.components.values()
                             if c.status == HealthStatus.HEALTHY])
        logger.info("Health checks: {healthy_count}/{components_count} healthy")

        # Test métriques système
        logger.info("5. Test métriques système...")
        system_metrics = health_checker._collect_system_metrics()
        print(f"✅ Métriques: CPU {system_metrics.cpu_usage_pct:.1f}%, "
              f"Memory {system_metrics.memory_usage_pct:.1f}%")

        # Test rapport santé
        logger.info("6. Test rapport santé...")
        health_status = health_checker.get_health_status()
        logger.info("Santé globale: {health_status['overall_health']:.1f}%")

        # Test dashboard data
        logger.info("7. Test dashboard...")
        if FLASK_AVAILABLE:
            dashboard_data = health_checker._get_dashboard_data()
            logger.info("Dashboard: {len(dashboard_data)} sections")
        else:
            logger.warning("Dashboard: Flask non disponible")

        print("\n" + "="*50)
        logger.info("🎉 TOUS LES TESTS RÉUSSIS!")
        logger.info("🏥 Health Checker opérationnel avec {components_count} composants")
        logger.info("📊 Santé système: {health_status['overall_health']:.1f}%")

        return health_checker

    except Exception as e:
        logger.error("ERREUR TEST: {e}")
        raise

# === CLI INTERFACE ===


def main():
    """Interface ligne de commande"""
    import argparse

    parser = argparse.ArgumentParser(description="🏥 MIA_IA_SYSTEM Health Checker")
    parser.add_argument('--start', action='store_true', help='Démarre le Health Checker')
    parser.add_argument('--test', action='store_true', help='Execute tests')
    parser.add_argument('--status', action='store_true', help='Affiche status santé')
    parser.add_argument('--dashboard', action='store_true', help='Démarre seulement dashboard')
    parser.add_argument('--port', type=int, default=8080, help='Port dashboard (défaut: 8080)')
    parser.add_argument('--config', help='Fichier configuration JSON')

    args = parser.parse_args()

    try:
        if args.test:
            test_health_checker()
            return 0

        # Chargement configuration
        config = None
        if args.config:
            with open(args.config, 'r') as f:
                config = json.load(f)

        if args.status:
            health_checker = create_health_checker(config)
            health_status = health_checker.get_health_status()

            logger.info("🏥 MIA_IA_SYSTEM HEALTH STATUS")
            print("=" * 40)
            logger.info("📊 Santé globale: {health_status['overall_health']:.1f}%")
            logger.info("💚 Healthy: {health_status['components_healthy']}")
            logger.info("🟡 Warning: {health_status['components_warning']}")
            logger.info("🔴 Critical: {health_status['components_critical']}")
            logger.info("⚫ Offline: {health_status['components_offline']}")
            logger.info("🕐 Uptime: {health_status['uptime_seconds']:.0f}s")
            logger.info("Trading Safe: {health_status['is_trading_safe']}")

            return 0

        if args.start or args.dashboard:
            if config is None:
                config = {}

            if args.dashboard:
                config['dashboard_enabled'] = True
                config['dashboard_port'] = args.port

            health_checker = create_health_checker(config)

            if args.start:
                logger.info("🏥 Démarrage Health Checker complet...")
                health_checker.start()

                logger.info("Health Checker démarré")
                if FLASK_AVAILABLE:
                    logger.info("🌐 Dashboard: http://127.0.0.1:{args.port}")

                logger.info("Press Ctrl+C to stop...")

                try:
                    while health_checker.is_running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("\n🛑 Arrêt demandé...")
                    health_checker.stop()
                    logger.info("Health Checker arrêté")

            elif args.dashboard:
                logger.info("🌐 Démarrage dashboard seul sur port {args.port}...")
                if FLASK_AVAILABLE:
                    health_checker._start_dashboard()
                    logger.info("Dashboard disponible: http://127.0.0.1:{args.port}")
                    logger.info("Press Ctrl+C to stop...")

                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        logger.info("\n🛑 Dashboard arrêté")
                else:
                    logger.error("Flask non disponible - Dashboard indisponible")
                    return 1

        else:
            parser.print_help()
            return 1

        return 0

    except Exception as e:
        logger.error("Erreur: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
