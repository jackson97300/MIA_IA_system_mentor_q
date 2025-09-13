"""
Collecteur de Métriques MIA_IA_SYSTEM
=====================================

Collecte et export des métriques système pour monitoring.
"""

import time
import json
import csv
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading
import asyncio

try:
    from prometheus_client import Counter, Histogram, Gauge, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MetricPoint:
    """Point de métrique"""
    timestamp: datetime
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """Collecteur de métriques système"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger
        
        # Stockage des métriques
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        
        # Configuration
        self.export_interval = self.config.get('export_interval_seconds', 60)
        self.prometheus_port = self.config.get('prometheus_port', 9090)
        self.csv_export_path = self.config.get('csv_export_path', 'metrics/')
        
        # Threading
        self._lock = threading.Lock()
        self._running = False
        self._export_task = None
        
        # Prometheus (si disponible)
        self.prometheus_metrics = {}
        if PROMETHEUS_AVAILABLE:
            self._init_prometheus_metrics()
        
        logger.info("📊 MetricsCollector initialisé")
    
    def _init_prometheus_metrics(self):
        """Initialise les métriques Prometheus"""
        if not PROMETHEUS_AVAILABLE:
            return
        
        # Compteurs
        self.prometheus_metrics['signals_generated'] = Counter(
            'mia_signals_generated_total',
            'Total signals generated',
            ['strategy', 'side']
        )
        
        self.prometheus_metrics['trades_executed'] = Counter(
            'mia_trades_executed_total',
            'Total trades executed',
            ['strategy', 'side', 'result']
        )
        
        self.prometheus_metrics['orders_rejected'] = Counter(
            'mia_orders_rejected_total',
            'Total orders rejected',
            ['reason']
        )
        
        self.prometheus_metrics['kill_switch_activations'] = Counter(
            'mia_kill_switch_activations_total',
            'Total kill switch activations',
            ['reason']
        )
        
        # Gauges
        self.prometheus_metrics['current_pnl'] = Gauge(
            'mia_current_pnl',
            'Current PnL',
            ['type']  # day, session
        )
        
        self.prometheus_metrics['current_drawdown'] = Gauge(
            'mia_current_drawdown',
            'Current drawdown percentage'
        )
        
        self.prometheus_metrics['data_latency'] = Gauge(
            'mia_data_latency_seconds',
            'Data latency in seconds',
            ['source']  # m1, m30, vix, menthorq
        )
        
        self.prometheus_metrics['system_health'] = Gauge(
            'mia_system_health',
            'System health status',
            ['component']  # collector, trading, safety
        )
        
        # Histogrammes
        self.prometheus_metrics['signal_processing_time'] = Histogram(
            'mia_signal_processing_seconds',
            'Signal processing time',
            ['strategy']
        )
        
        self.prometheus_metrics['order_execution_time'] = Histogram(
            'mia_order_execution_seconds',
            'Order execution time',
            ['side']
        )
        
        logger.info("📊 Métriques Prometheus initialisées")
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Incrémente un compteur"""
        with self._lock:
            self.counters[name] += value
            
            # Prometheus
            if PROMETHEUS_AVAILABLE and name in self.prometheus_metrics:
                if labels:
                    self.prometheus_metrics[name].labels(**labels).inc(value)
                else:
                    self.prometheus_metrics[name].inc(value)
            
            # Stockage
            self._store_metric(name, value, labels, 'counter')
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Définit une jauge"""
        with self._lock:
            self.gauges[name] = value
            
            # Prometheus
            if PROMETHEUS_AVAILABLE and name in self.prometheus_metrics:
                if labels:
                    self.prometheus_metrics[name].labels(**labels).set(value)
                else:
                    self.prometheus_metrics[name].set(value)
            
            # Stockage
            self._store_metric(name, value, labels, 'gauge')
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Observe une valeur dans un histogramme"""
        with self._lock:
            self.histograms[name].append(value)
            
            # Prometheus
            if PROMETHEUS_AVAILABLE and name in self.prometheus_metrics:
                if labels:
                    self.prometheus_metrics[name].labels(**labels).observe(value)
                else:
                    self.prometheus_metrics[name].observe(value)
            
            # Stockage
            self._store_metric(name, value, labels, 'histogram')
    
    def _store_metric(self, name: str, value: float, labels: Optional[Dict[str, str]], metric_type: str):
        """Stocke une métrique"""
        metric_point = MetricPoint(
            timestamp=datetime.now(timezone.utc),
            name=name,
            value=value,
            labels=labels or {},
            tags={'type': metric_type}
        )
        
        self.metrics[name].append(metric_point)
    
    # === MÉTRIQUES SPÉCIFIQUES ===
    
    def record_signal_generated(self, strategy: str, side: str, confidence: float):
        """Enregistre un signal généré"""
        self.increment_counter('signals_generated', labels={'strategy': strategy, 'side': side})
        self.observe_histogram('signal_confidence', confidence, labels={'strategy': strategy})
    
    def record_trade_executed(self, strategy: str, side: str, result: str, pnl: float):
        """Enregistre un trade exécuté"""
        self.increment_counter('trades_executed', labels={'strategy': strategy, 'side': side, 'result': result})
        self.observe_histogram('trade_pnl', pnl, labels={'strategy': strategy, 'side': side})
    
    def record_order_rejected(self, reason: str):
        """Enregistre un ordre rejeté"""
        self.increment_counter('orders_rejected', labels={'reason': reason})
    
    def record_kill_switch_activation(self, reason: str):
        """Enregistre une activation du kill switch"""
        self.increment_counter('kill_switch_activations', labels={'reason': reason})
    
    def update_pnl(self, pnl_day: float, pnl_session: float):
        """Met à jour le PnL"""
        self.set_gauge('pnl_day', pnl_day)
        self.set_gauge('pnl_session', pnl_session)
    
    def update_drawdown(self, drawdown: float):
        """Met à jour le drawdown"""
        self.set_gauge('current_drawdown', drawdown)
    
    def update_data_latency(self, source: str, latency: float):
        """Met à jour la latence des données"""
        self.set_gauge('data_latency', latency, labels={'source': source})
    
    def update_system_health(self, component: str, health: float):
        """Met à jour la santé du système (0-1)"""
        self.set_gauge('system_health', health, labels={'component': component})
    
    def record_processing_time(self, operation: str, duration: float, labels: Optional[Dict[str, str]] = None):
        """Enregistre le temps de traitement"""
        self.observe_histogram('processing_time', duration, labels={'operation': operation, **(labels or {})})
    
    # === EXPORT ===
    
    def start_prometheus_server(self, port: Optional[int] = None):
        """Démarre le serveur Prometheus"""
        if not PROMETHEUS_AVAILABLE:
            logger.warning("Prometheus non disponible - serveur non démarré")
            return False
        
        port = port or self.prometheus_port
        try:
            start_http_server(port)
            logger.info(f"📊 Serveur Prometheus démarré sur port {port}")
            return True
        except Exception as e:
            logger.error(f"Erreur démarrage serveur Prometheus: {e}")
            return False
    
    def export_csv(self, filename: Optional[str] = None) -> str:
        """Exporte les métriques en CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_export_{timestamp}.csv"
        
        filepath = f"{self.csv_export_path}/{filename}"
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # En-têtes
                writer.writerow(['timestamp', 'name', 'value', 'labels', 'tags', 'type'])
                
                # Données
                with self._lock:
                    for metric_name, metric_points in self.metrics.items():
                        for point in metric_points:
                            writer.writerow([
                                point.timestamp.isoformat(),
                                point.name,
                                point.value,
                                json.dumps(point.labels),
                                json.dumps(point.tags),
                                point.tags.get('type', 'unknown')
                            ])
            
            logger.info(f"📊 Métriques exportées vers {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Erreur export CSV: {e}")
            return ""
    
    def export_json(self, filename: Optional[str] = None) -> str:
        """Exporte les métriques en JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_export_{timestamp}.json"
        
        filepath = f"{self.csv_export_path}/{filename}"
        
        try:
            export_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {
                    name: {
                        'count': len(values),
                        'min': min(values) if values else 0,
                        'max': max(values) if values else 0,
                        'avg': sum(values) / len(values) if values else 0,
                        'values': values[-100:]  # Dernières 100 valeurs
                    }
                    for name, values in self.histograms.items()
                },
                'metrics': {
                    name: [
                        {
                            'timestamp': point.timestamp.isoformat(),
                            'value': point.value,
                            'labels': point.labels,
                            'tags': point.tags
                        }
                        for point in points
                    ]
                    for name, points in self.metrics.items()
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 Métriques exportées vers {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Erreur export JSON: {e}")
            return ""
    
    def get_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des métriques"""
        with self._lock:
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {
                    name: {
                        'count': len(values),
                        'min': min(values) if values else 0,
                        'max': max(values) if values else 0,
                        'avg': sum(values) / len(values) if values else 0
                    }
                    for name, values in self.histograms.items()
                },
                'total_metrics_points': sum(len(points) for points in self.metrics.values())
            }
    
    def start_auto_export(self):
        """Démarre l'export automatique"""
        if self._running:
            return
        
        self._running = True
        self._export_task = asyncio.create_task(self._auto_export_loop())
        logger.info("📊 Export automatique démarré")
    
    def stop_auto_export(self):
        """Arrête l'export automatique"""
        self._running = False
        if self._export_task:
            self._export_task.cancel()
        logger.info("📊 Export automatique arrêté")
    
    async def _auto_export_loop(self):
        """Boucle d'export automatique"""
        while self._running:
            try:
                await asyncio.sleep(self.export_interval)
                
                if self._running:
                    # Export CSV
                    self.export_csv()
                    
                    # Log du résumé
                    summary = self.get_summary()
                    logger.info(f"📊 Métriques: {summary['total_metrics_points']} points, "
                              f"{len(summary['counters'])} compteurs, "
                              f"{len(summary['gauges'])} jauges")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur export automatique: {e}")


# === INSTANCE GLOBALE ===

_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Retourne l'instance globale du collecteur de métriques"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def create_metrics_collector(config: Optional[Dict[str, Any]] = None) -> MetricsCollector:
    """Crée une instance du collecteur de métriques"""
    return MetricsCollector(config)


# === FONCTIONS UTILITAIRES ===

def record_signal_metric(strategy: str, side: str, confidence: float):
    """Enregistre une métrique de signal"""
    collector = get_metrics_collector()
    collector.record_signal_generated(strategy, side, confidence)

def record_trade_metric(strategy: str, side: str, result: str, pnl: float):
    """Enregistre une métrique de trade"""
    collector = get_metrics_collector()
    collector.record_trade_executed(strategy, side, result, pnl)

def record_kill_switch_metric(reason: str):
    """Enregistre une métrique de kill switch"""
    collector = get_metrics_collector()
    collector.record_kill_switch_activation(reason)

def update_pnl_metric(pnl_day: float, pnl_session: float):
    """Met à jour les métriques de PnL"""
    collector = get_metrics_collector()
    collector.update_pnl(pnl_day, pnl_session)

def update_latency_metric(source: str, latency: float):
    """Met à jour les métriques de latence"""
    collector = get_metrics_collector()
    collector.update_data_latency(source, latency)
