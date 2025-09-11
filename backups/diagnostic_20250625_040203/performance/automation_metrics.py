#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Automation Metrics
📈 MÉTRIQUES SPÉCIFIQUES AUTOMATION & SYSTÈME

Version: Phase 3B - Automation Focus
Responsabilité: Métriques performance automatisation & efficacité système

FONCTIONNALITÉS CRITIQUES :
1. 🚀 Signal Generation Metrics - Timing, qualité, cohérence signaux
2. 🤖 Automation Efficiency - Uptime, latence, throughput système
3. 📊 System Performance - CPU, RAM, I/O, réseau temps réel
4. 🔄 Process Monitoring - États composants, santé pipeline
5. 📈 Trend Analysis - Évolution métriques dans le temps
6. 🚨 Alert Generation - Seuils automatiques & notifications

WORKFLOW TRACKING :
Data In → Processing → Signal Gen → Execution → Performance Out

MÉTRIQUES CLEFS :
- Signal generation time (<5ms target)
- System availability (>99% target)
- Memory usage optimization
- Network latency monitoring
- Component health tracking
- Automation success rate
"""

import os
import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field, asdict
from collections import deque, defaultdict, Counter
from enum import Enum
import logging
import statistics
import json

# Local imports
from core.base_types import TradingSignal, SignalType
from config.automation_config import get_automation_config

logger = logging.getLogger(__name__)

# === AUTOMATION METRICS ENUMS ===

class MetricType(Enum):
    """Types de métriques automation"""
    SIGNAL_GENERATION = "signal_generation"
    SYSTEM_PERFORMANCE = "system_performance"
    AUTOMATION_EFFICIENCY = "automation_efficiency"
    COMPONENT_HEALTH = "component_health"
    NETWORK_LATENCY = "network_latency"
    ERROR_TRACKING = "error_tracking"

class AlertSeverity(Enum):
    """Niveaux de sévérité alertes"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class ComponentStatus(Enum):
    """Status des composants système"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"

# === AUTOMATION METRICS DATA STRUCTURES ===

@dataclass
class SignalGenerationMetrics:
    """Métriques génération de signaux"""
    total_signals: int = 0
    avg_generation_time_ms: float = 0.0
    max_generation_time_ms: float = 0.0
    min_generation_time_ms: float = 999.0
    signals_per_minute: float = 0.0
    quality_distribution: Dict[str, int] = field(default_factory=dict)
    error_rate: float = 0.0
    last_signal_time: Optional[datetime] = None

@dataclass
class SystemPerformanceMetrics:
    """Métriques performance système"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_mb: float = 0.0
    disk_usage_percent: float = 0.0
    disk_free_gb: float = 0.0
    network_sent_mbps: float = 0.0
    network_recv_mbps: float = 0.0
    load_average: float = 0.0
    process_count: int = 0
    uptime_seconds: float = 0.0

@dataclass
class AutomationEfficiencyMetrics:
    """Métriques efficacité automation"""
    automation_uptime: float = 0.0      # Pourcentage temps actif
    successful_operations: int = 0       # Opérations réussies
    failed_operations: int = 0           # Opérations échouées
    success_rate: float = 0.0           # Taux de succès
    avg_response_time_ms: float = 0.0   # Temps réponse moyen
    throughput_per_hour: float = 0.0    # Débit opérations/heure
    efficiency_score: float = 0.0       # Score global efficacité

@dataclass
class ComponentHealth:
    """Santé d'un composant système"""
    component_name: str
    status: ComponentStatus
    last_heartbeat: datetime
    error_count: int = 0
    avg_response_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

class AutomationMetrics:
    """
    AUTOMATION METRICS - Métriques spécifiques automation
    
    Responsabilités :
    1. Tracking performance génération signaux
    2. Monitoring santé système temps réel
    3. Analyse efficacité automation
    4. Détection anomalies & alertes
    5. Reporting métriques automation
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialisation Automation Metrics
        
        Args:
            config: Configuration optionnelle
        """
        self.config = config or get_automation_config()
        
        # Storage paths
        self.base_path = Path("data/performance/automation")
        self.metrics_path = self.base_path / "metrics"
        self.reports_path = self.base_path / "reports"
        
        # Création directories
        for path in [self.base_path, self.metrics_path, self.reports_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Métriques en temps réel
        self.signal_metrics = SignalGenerationMetrics()
        self.system_metrics = SystemPerformanceMetrics()
        self.efficiency_metrics = AutomationEfficiencyMetrics()
        
        # Component tracking
        self.component_health: Dict[str, ComponentHealth] = {}
        
        # Historical data
        self.signal_generation_times = deque(maxlen=1000)
        self.system_snapshots = deque(maxlen=500)
        self.operation_results = deque(maxlen=2000)
        
        # Threading pour monitoring continu
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # Performance tracking
        self.start_time = datetime.now(timezone.utc)
        self.last_snapshot_time = None
        
        # Seuils d'alerte
        self.alert_thresholds = {
            'signal_generation_time_ms': 10.0,
            'cpu_percent_max': 80.0,
            'memory_percent_max': 85.0,
            'disk_usage_max': 90.0,
            'error_rate_max': 0.05,  # 5%
            'response_time_ms_max': 100.0
        }
        
        self._start_system_monitoring()
        logger.info(f"AutomationMetrics initialisé: {self.base_path}")
    
    def track_signal_generation(self, generation_time_ms: float, 
                              signal_quality: str, success: bool = True) -> None:
        """
        TRACKING GÉNÉRATION SIGNAUX
        
        Args:
            generation_time_ms: Temps génération en ms
            signal_quality: Qualité du signal
            success: Succès de la génération
        """
        try:
            # Update basic metrics
            self.signal_metrics.total_signals += 1
            self.signal_metrics.last_signal_time = datetime.now(timezone.utc)
            
            if success:
                # Update timing metrics
                self.signal_generation_times.append(generation_time_ms)
                
                if generation_time_ms > self.signal_metrics.max_generation_time_ms:
                    self.signal_metrics.max_generation_time_ms = generation_time_ms
                
                if generation_time_ms < self.signal_metrics.min_generation_time_ms:
                    self.signal_metrics.min_generation_time_ms = generation_time_ms
                
                # Update quality distribution
                if signal_quality not in self.signal_metrics.quality_distribution:
                    self.signal_metrics.quality_distribution[signal_quality] = 0
                self.signal_metrics.quality_distribution[signal_quality] += 1
                
                # Recalcul moyennes
                self._update_signal_averages()
            else:
                # Track errors
                self._update_error_rates()
            
            # Check alerts
            self._check_signal_alerts(generation_time_ms, success)
            
        except Exception as e:
            logger.error(f"Erreur track_signal_generation: {e}")
    
    def track_system_operation(self, operation_type: str, 
                             duration_ms: float, success: bool) -> None:
        """
        TRACKING OPÉRATIONS SYSTÈME
        
        Args:
            operation_type: Type d'opération
            duration_ms: Durée en ms
            success: Succès de l'opération
        """
        try:
            # Record operation
            operation_record = {
                'timestamp': datetime.now(timezone.utc),
                'type': operation_type,
                'duration_ms': duration_ms,
                'success': success
            }
            self.operation_results.append(operation_record)
            
            # Update efficiency metrics
            if success:
                self.efficiency_metrics.successful_operations += 1
            else:
                self.efficiency_metrics.failed_operations += 1
            
            # Recalcul métriques dérivées
            self._update_efficiency_metrics()
            
        except Exception as e:
            logger.error(f"Erreur track_system_operation: {e}")
    
    def register_component(self, component_name: str) -> None:
        """
        ENREGISTREMENT COMPOSANT SYSTÈME
        
        Args:
            component_name: Nom du composant à tracker
        """
        try:
            self.component_health[component_name] = ComponentHealth(
                component_name=component_name,
                status=ComponentStatus.HEALTHY,
                last_heartbeat=datetime.now(timezone.utc)
            )
            
            logger.info(f"Composant enregistré: {component_name}")
            
        except Exception as e:
            logger.error(f"Erreur register_component: {e}")
    
    def update_component_health(self, component_name: str, 
                              status: ComponentStatus,
                              custom_metrics: Optional[Dict] = None) -> None:
        """
        MISE À JOUR SANTÉ COMPOSANT
        
        Args:
            component_name: Nom du composant
            status: Nouveau status
            custom_metrics: Métriques personnalisées
        """
        try:
            if component_name not in self.component_health:
                self.register_component(component_name)
            
            component = self.component_health[component_name]
            component.status = status
            component.last_heartbeat = datetime.now(timezone.utc)
            
            if custom_metrics:
                component.custom_metrics.update(custom_metrics)
            
            # Log status changes
            if status != ComponentStatus.HEALTHY:
                logger.warning(f"Component {component_name} status: {status.value}")
            
        except Exception as e:
            logger.error(f"Erreur update_component_health: {e}")
    
    def get_automation_summary(self) -> Dict[str, Any]:
        """
        RÉSUMÉ MÉTRIQUES AUTOMATION
        
        Returns:
            Dict: Résumé complet métriques
        """
        try:
            uptime_seconds = (datetime.now(timezone.utc) - self.start_time).total_seconds()
            
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'uptime_hours': uptime_seconds / 3600,
                
                # Signal generation
                'signal_generation': {
                    'total_signals': self.signal_metrics.total_signals,
                    'avg_time_ms': self.signal_metrics.avg_generation_time_ms,
                    'max_time_ms': self.signal_metrics.max_generation_time_ms,
                    'signals_per_minute': self.signal_metrics.signals_per_minute,
                    'quality_distribution': self.signal_metrics.quality_distribution,
                    'error_rate': self.signal_metrics.error_rate
                },
                
                # System performance
                'system_performance': asdict(self.system_metrics),
                
                # Automation efficiency
                'automation_efficiency': asdict(self.efficiency_metrics),
                
                # Component health
                'component_health': {
                    name: {
                        'status': comp.status.value,
                        'last_heartbeat': comp.last_heartbeat.isoformat(),
                        'error_count': comp.error_count
                    }
                    for name, comp in self.component_health.items()
                },
                
                # Alerts status
                'alerts_active': self._count_active_alerts()
            }
            
        except Exception as e:
            logger.error(f"Erreur get_automation_summary: {e}")
            return {'error': str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Status actuel des métriques"""
        return {
            'monitoring_active': self.is_monitoring,
            'components_tracked': len(self.component_health),
            'signals_tracked': self.signal_metrics.total_signals,
            'operations_tracked': len(self.operation_results),
            'uptime_hours': (datetime.now(timezone.utc) - self.start_time).total_seconds() / 3600
        }
    
    # === PRIVATE METHODS ===
    
    def _start_system_monitoring(self):
        """Démarrage monitoring système continu"""
        if not self.monitoring_thread or not self.monitoring_thread.is_alive():
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_worker,
                daemon=True
            )
            self.monitoring_thread.start()
    
    def _monitoring_worker(self):
        """Worker thread pour monitoring système"""
        while self.is_monitoring:
            try:
                # Update system metrics
                self._update_system_metrics()
                
                # Check component health
                self._check_component_timeouts()
                
                # Save snapshot
                self._save_metrics_snapshot()
                
                time.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Erreur monitoring worker: {e}")
                time.sleep(60)
    
    def _update_system_metrics(self):
        """Mise à jour métriques système"""
        try:
            # CPU usage
            self.system_metrics.cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_metrics.memory_percent = memory.percent
            self.system_metrics.memory_mb = memory.used / (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.system_metrics.disk_usage_percent = disk.percent
            self.system_metrics.disk_free_gb = disk.free / (1024 ** 3)
            
            # Network stats
            net_io = psutil.net_io_counters()
            if hasattr(self, '_last_net_io'):
                time_delta = 30  # 30 seconds interval
                sent_delta = net_io.bytes_sent - self._last_net_io.bytes_sent
                recv_delta = net_io.bytes_recv - self._last_net_io.bytes_recv
                
                self.system_metrics.network_sent_mbps = (sent_delta / time_delta) / (1024 * 1024)
                self.system_metrics.network_recv_mbps = (recv_delta / time_delta) / (1024 * 1024)
            
            self._last_net_io = net_io
            
            # Load average (Unix only)
            try:
                self.system_metrics.load_average = os.getloadavg()[0]
            except (OSError, AttributeError):
                self.system_metrics.load_average = 0.0
            
            # Process count
            self.system_metrics.process_count = len(psutil.pids())
            
            # Uptime
            uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()
            self.system_metrics.uptime_seconds = uptime
            
        except Exception as e:
            logger.error(f"Erreur update_system_metrics: {e}")
    
    def _update_signal_averages(self):
        """Mise à jour moyennes signaux"""
        if self.signal_generation_times:
            self.signal_metrics.avg_generation_time_ms = statistics.mean(
                self.signal_generation_times
            )
            
            # Calcul signals per minute
            recent_signals = [t for t in self.signal_generation_times if t > 0]
            if recent_signals:
                self.signal_metrics.signals_per_minute = min(60.0, 60.0 / len(recent_signals))
    
    def _update_efficiency_metrics(self):
        """Mise à jour métriques efficacité"""
        total_ops = self.efficiency_metrics.successful_operations + self.efficiency_metrics.failed_operations
        
        if total_ops > 0:
            self.efficiency_metrics.success_rate = (
                self.efficiency_metrics.successful_operations / total_ops
            )
        
        # Calcul uptime automation
        uptime_seconds = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        self.efficiency_metrics.automation_uptime = min(100.0, (uptime_seconds / 86400) * 100)
        
        # Efficiency score composite
        self.efficiency_metrics.efficiency_score = (
            self.efficiency_metrics.success_rate * 0.4 +
            (self.efficiency_metrics.automation_uptime / 100) * 0.3 +
            (1.0 - min(1.0, self.signal_metrics.avg_generation_time_ms / 10.0)) * 0.3
        )
    
    def _update_error_rates(self):
        """Mise à jour taux d'erreur"""
        total_signals = self.signal_metrics.total_signals
        errors = total_signals - len(self.signal_generation_times)
        
        if total_signals > 0:
            self.signal_metrics.error_rate = errors / total_signals
    
    def _check_signal_alerts(self, generation_time_ms: float, success: bool):
        """Vérification alertes signaux"""
        # Alert si temps génération trop élevé
        if generation_time_ms > self.alert_thresholds['signal_generation_time_ms']:
            logger.warning(f"Signal generation slow: {generation_time_ms:.1f}ms")
        
        # Alert si taux d'erreur élevé
        if self.signal_metrics.error_rate > self.alert_thresholds['error_rate_max']:
            logger.warning(f"High error rate: {self.signal_metrics.error_rate:.1%}")
    
    def _check_component_timeouts(self):
        """Vérification timeouts composants"""
        timeout_threshold = timedelta(minutes=5)
        current_time = datetime.now(timezone.utc)
        
        for name, component in self.component_health.items():
            if current_time - component.last_heartbeat > timeout_threshold:
                if component.status != ComponentStatus.OFFLINE:
                    component.status = ComponentStatus.OFFLINE
                    logger.error(f"Component timeout: {name}")
    
    def _save_metrics_snapshot(self):
        """Sauvegarde snapshot métriques"""
        snapshot = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'signal_metrics': asdict(self.signal_metrics),
            'system_metrics': asdict(self.system_metrics),
            'efficiency_metrics': asdict(self.efficiency_metrics)
        }
        
        self.system_snapshots.append(snapshot)
        self.last_snapshot_time = datetime.now(timezone.utc)
    
    def _count_active_alerts(self) -> int:
        """Comptage alertes actives"""
        # Stub pour comptage alertes
        return 0

# === FACTORY FUNCTION ===

def create_automation_metrics(config: Optional[Dict] = None) -> AutomationMetrics:
    """Factory function pour AutomationMetrics"""
    return AutomationMetrics(config)

# === END MODULE ===