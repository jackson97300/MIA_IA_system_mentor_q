#!/usr/bin/env python3
"""
⚡ EXECUTION LATENCY TRACKER - MIA_IA_SYSTEM
============================================

Système de tracking de latence d'exécution dans le pipeline de trading.
- Mesure des latences à chaque étape du pipeline
- Détection des goulots d'étranglement
- Alertes sur les dégradations de performance
- Métriques détaillées pour optimisation
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import threading
from collections import defaultdict, deque
import statistics
import json

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger

logger = get_logger(__name__)

class LatencyStage(Enum):
    """Étapes du pipeline de trading"""
    SIGNAL_GENERATION = "signal_generation"
    MENTHORQ_PROCESSING = "menthorq_processing"
    BATTLE_NAVALE_ANALYSIS = "battle_navale_analysis"
    VIX_REGIME_CHECK = "vix_regime_check"
    LEADERSHIP_FILTER = "leadership_filter"
    SCORE_CALCULATION = "score_calculation"
    TRADE_DECISION = "trade_decision"
    RISK_MANAGEMENT = "risk_management"
    ORDER_PREPARATION = "order_preparation"
    DTC_ROUTING = "dtc_routing"
    ORDER_EXECUTION = "order_execution"
    TRADE_CONFIRMATION = "trade_confirmation"
    LOGGING = "logging"

class LatencyAlertType(Enum):
    """Types d'alertes de latence"""
    HIGH_LATENCY = "high_latency"
    PIPELINE_BOTTLENECK = "pipeline_bottleneck"
    STAGE_TIMEOUT = "stage_timeout"
    PERFORMANCE_DEGRADATION = "performance_degradation"

@dataclass
class LatencyMeasurement:
    """Mesure de latence pour une étape"""
    stage: LatencyStage
    start_time: datetime
    end_time: datetime
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PipelineLatency:
    """Latence complète du pipeline"""
    pipeline_id: str
    start_time: datetime
    end_time: datetime
    total_duration_ms: float
    stages: List[LatencyMeasurement]
    success: bool
    signal_type: Optional[str] = None
    symbol: Optional[str] = None

@dataclass
class LatencyStats:
    """Statistiques de latence pour une étape"""
    stage: LatencyStage
    total_measurements: int = 0
    successful_measurements: int = 0
    avg_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0.0
    p50_duration_ms: float = 0.0
    p95_duration_ms: float = 0.0
    p99_duration_ms: float = 0.0
    error_rate: float = 0.0
    last_measurement: Optional[datetime] = None

@dataclass
class LatencyAlert:
    """Alerte de latence"""
    timestamp: datetime
    alert_type: LatencyAlertType
    severity: str  # "low", "medium", "high", "critical"
    message: str
    stage: Optional[LatencyStage] = None
    duration_ms: Optional[float] = None
    threshold_ms: Optional[float] = None
    context: Dict[str, Any] = field(default_factory=dict)

class ExecutionLatencyTracker:
    """Tracker de latence d'exécution du pipeline de trading"""
    
    def __init__(self, max_history_size: int = 1000):
        """
        Initialisation du tracker de latence
        
        Args:
            max_history_size: Taille maximale de l'historique
        """
        self.max_history_size = max_history_size
        self.logger = get_logger(f"{__name__}.ExecutionLatencyTracker")
        
        # Historique des mesures
        self.measurements: deque = deque(maxlen=max_history_size)
        self.pipeline_measurements: deque = deque(maxlen=max_history_size)
        
        # Statistiques par étape
        self.stage_stats: Dict[LatencyStage, LatencyStats] = {}
        
        # Alertes
        self.alerts: deque = deque(maxlen=500)
        
        # Configuration des seuils
        self.latency_thresholds = {
            LatencyStage.SIGNAL_GENERATION: 50.0,      # 50ms
            LatencyStage.MENTHORQ_PROCESSING: 100.0,    # 100ms
            LatencyStage.BATTLE_NAVALE_ANALYSIS: 75.0,  # 75ms
            LatencyStage.VIX_REGIME_CHECK: 25.0,        # 25ms
            LatencyStage.LEADERSHIP_FILTER: 50.0,       # 50ms
            LatencyStage.SCORE_CALCULATION: 30.0,       # 30ms
            LatencyStage.RISK_MANAGEMENT: 100.0,        # 100ms
            LatencyStage.ORDER_PREPARATION: 50.0,       # 50ms
            LatencyStage.DTC_ROUTING: 200.0,            # 200ms
            LatencyStage.ORDER_EXECUTION: 500.0,        # 500ms
            LatencyStage.TRADE_CONFIRMATION: 100.0      # 100ms
        }
        
        # Seuils d'alerte
        self.alert_thresholds = {
            'high_latency_multiplier': 2.0,      # 2x le seuil normal
            'bottleneck_threshold': 0.8,         # 80% du temps total
            'timeout_threshold': 5.0,            # 5 secondes
            'degradation_threshold': 1.5         # 1.5x la moyenne récente
        }
        
        # Pipeline actuel
        self.current_pipeline: Optional[PipelineLatency] = None
        self.pipeline_counter = 0
        
        # Thread de monitoring
        self.monitoring_thread: Optional[threading.Thread] = None
        self.is_monitoring = False
        self.stop_event = threading.Event()
        
        self.logger.info("⚡ ExecutionLatencyTracker initialisé")
    
    def start_pipeline(self, signal_type: Optional[str] = None, symbol: Optional[str] = None) -> str:
        """
        Démarre le tracking d'un nouveau pipeline
        
        Args:
            signal_type: Type de signal (optionnel)
            symbol: Symbole tradé (optionnel)
            
        Returns:
            str: ID du pipeline
        """
        self.pipeline_counter += 1
        pipeline_id = f"pipeline_{self.pipeline_counter}_{int(time.time())}"
        
        self.current_pipeline = PipelineLatency(
            pipeline_id=pipeline_id,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),  # Sera mis à jour
            total_duration_ms=0.0,
            stages=[],
            success=False,
            signal_type=signal_type,
            symbol=symbol
        )
        
        self.logger.debug(f"🚀 Pipeline démarré: {pipeline_id}")
        return pipeline_id
    
    def start_stage(self, stage: LatencyStage, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Démarre le tracking d'une étape
        
        Args:
            stage: Étape du pipeline
            context: Contexte supplémentaire
        """
        if not self.current_pipeline:
            self.logger.warning(f"⚠️ Tentative de démarrage d'étape sans pipeline actif: {stage.value}")
            return
        
        measurement = LatencyMeasurement(
            stage=stage,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),  # Sera mis à jour
            duration_ms=0.0,
            success=False,
            context=context or {}
        )
        
        # Stocker temporairement la mesure
        if not hasattr(self, '_current_measurements'):
            self._current_measurements = {}
        self._current_measurements[stage] = measurement
        
        self.logger.debug(f"⏱️ Étape démarrée: {stage.value}")
    
    def end_stage(self, stage: LatencyStage, success: bool = True, error_message: Optional[str] = None) -> None:
        """
        Termine le tracking d'une étape
        
        Args:
            stage: Étape du pipeline
            success: Succès de l'étape
            error_message: Message d'erreur si échec
        """
        if not self.current_pipeline:
            self.logger.warning(f"⚠️ Tentative de fin d'étape sans pipeline actif: {stage.value}")
            return
        
        if not hasattr(self, '_current_measurements') or stage not in self._current_measurements:
            self.logger.warning(f"⚠️ Tentative de fin d'étape non démarrée: {stage.value}")
            return
        
        measurement = self._current_measurements[stage]
        measurement.end_time = datetime.now(timezone.utc)
        measurement.duration_ms = (measurement.end_time - measurement.start_time).total_seconds() * 1000
        measurement.success = success
        measurement.error_message = error_message
        
        # Ajouter au pipeline actuel
        self.current_pipeline.stages.append(measurement)
        
        # Ajouter à l'historique global
        self.measurements.append(measurement)
        
        # Mettre à jour les statistiques
        self._update_stage_stats(stage, measurement)
        
        # Vérifier les alertes
        self._check_latency_alerts(measurement)
        
        # Nettoyer
        del self._current_measurements[stage]
        
        self.logger.debug(f"✅ Étape terminée: {stage.value} ({measurement.duration_ms:.1f}ms)")
    
    def end_pipeline(self, success: bool = True) -> Optional[PipelineLatency]:
        """
        Termine le tracking du pipeline actuel
        
        Args:
            success: Succès du pipeline
            
        Returns:
            PipelineLatency: Pipeline terminé ou None
        """
        if not self.current_pipeline:
            self.logger.warning("⚠️ Tentative de fin de pipeline sans pipeline actif")
            return None
        
        self.current_pipeline.end_time = datetime.now(timezone.utc)
        self.current_pipeline.total_duration_ms = (
            self.current_pipeline.end_time - self.current_pipeline.start_time
        ).total_seconds() * 1000
        self.current_pipeline.success = success
        
        # Ajouter à l'historique
        self.pipeline_measurements.append(self.current_pipeline)
        
        # Analyser les goulots d'étranglement
        self._analyze_bottlenecks(self.current_pipeline)
        
        pipeline = self.current_pipeline
        self.current_pipeline = None
        
        self.logger.info(f"🏁 Pipeline terminé: {pipeline.pipeline_id} ({pipeline.total_duration_ms:.1f}ms)")
        return pipeline
    
    def _update_stage_stats(self, stage: LatencyStage, measurement: LatencyMeasurement) -> None:
        """Met à jour les statistiques d'une étape"""
        if stage not in self.stage_stats:
            self.stage_stats[stage] = LatencyStats(stage=stage)
        
        stats = self.stage_stats[stage]
        stats.total_measurements += 1
        stats.last_measurement = measurement.end_time
        
        if measurement.success:
            stats.successful_measurements += 1
        
        # Mettre à jour les statistiques de durée
        duration = measurement.duration_ms
        stats.min_duration_ms = min(stats.min_duration_ms, duration)
        stats.max_duration_ms = max(stats.max_duration_ms, duration)
        
        # Moyenne mobile
        if stats.avg_duration_ms == 0:
            stats.avg_duration_ms = duration
        else:
            alpha = 0.1  # Facteur de lissage
            stats.avg_duration_ms = alpha * duration + (1 - alpha) * stats.avg_duration_ms
        
        # Calculer les percentiles (simplifié)
        recent_measurements = [m for m in self.measurements if m.stage == stage and m.success][-100:]
        if len(recent_measurements) >= 5:
            durations = [m.duration_ms for m in recent_measurements]
            durations.sort()
            stats.p50_duration_ms = durations[len(durations) // 2]
            stats.p95_duration_ms = durations[int(len(durations) * 0.95)]
            stats.p99_duration_ms = durations[int(len(durations) * 0.99)]
        
        # Taux d'erreur
        stats.error_rate = (stats.total_measurements - stats.successful_measurements) / stats.total_measurements
    
    def _check_latency_alerts(self, measurement: LatencyMeasurement) -> None:
        """Vérifie les alertes de latence"""
        stage = measurement.stage
        duration = measurement.duration_ms
        threshold = self.latency_thresholds.get(stage, 100.0)
        
        # Alerte latence élevée
        if duration > threshold * self.alert_thresholds['high_latency_multiplier']:
            self._generate_alert(
                LatencyAlertType.HIGH_LATENCY,
                "high",
                f"Latence élevée détectée: {stage.value} = {duration:.1f}ms (seuil: {threshold:.1f}ms)",
                stage,
                duration,
                threshold
            )
        
        # Alerte timeout
        if duration > self.alert_thresholds['timeout_threshold'] * 1000:
            self._generate_alert(
                LatencyAlertType.STAGE_TIMEOUT,
                "critical",
                f"Timeout détecté: {stage.value} = {duration:.1f}ms",
                stage,
                duration,
                self.alert_thresholds['timeout_threshold'] * 1000
            )
        
        # Alerte dégradation de performance
        if stage in self.stage_stats:
            stats = self.stage_stats[stage]
            if stats.avg_duration_ms > 0:
                degradation_ratio = duration / stats.avg_duration_ms
                if degradation_ratio > self.alert_thresholds['degradation_threshold']:
                    self._generate_alert(
                        LatencyAlertType.PERFORMANCE_DEGRADATION,
                        "medium",
                        f"Dégradation de performance: {stage.value} = {duration:.1f}ms (moyenne: {stats.avg_duration_ms:.1f}ms)",
                        stage,
                        duration,
                        stats.avg_duration_ms * self.alert_thresholds['degradation_threshold']
                    )
    
    def _analyze_bottlenecks(self, pipeline: PipelineLatency) -> None:
        """Analyse les goulots d'étranglement du pipeline"""
        if not pipeline.stages:
            return
        
        total_duration = pipeline.total_duration_ms
        bottleneck_threshold = total_duration * self.alert_thresholds['bottleneck_threshold']
        
        # Trouver l'étape la plus lente
        slowest_stage = max(pipeline.stages, key=lambda m: m.duration_ms)
        
        if slowest_stage.duration_ms > bottleneck_threshold:
            self._generate_alert(
                LatencyAlertType.PIPELINE_BOTTLENECK,
                "medium",
                f"Goulot d'étranglement détecté: {slowest_stage.stage.value} = {slowest_stage.duration_ms:.1f}ms ({slowest_stage.duration_ms/total_duration*100:.1f}% du total)",
                slowest_stage.stage,
                slowest_stage.duration_ms,
                bottleneck_threshold
            )
    
    def _generate_alert(self, alert_type: LatencyAlertType, severity: str, message: str,
                       stage: Optional[LatencyStage], duration: Optional[float], threshold: Optional[float]) -> None:
        """Génère une alerte de latence"""
        alert = LatencyAlert(
            timestamp=datetime.now(timezone.utc),
            alert_type=alert_type,
            severity=severity,
            message=message,
            stage=stage,
            duration_ms=duration,
            threshold_ms=threshold
        )
        
        self.alerts.append(alert)
        
        # Log selon la sévérité
        if severity == "critical":
            self.logger.critical(f"🚨 ALERTE CRITIQUE: {message}")
        elif severity == "high":
            self.logger.error(f"⚠️ ALERTE HAUTE: {message}")
        elif severity == "medium":
            self.logger.warning(f"⚠️ ALERTE MOYENNE: {message}")
        else:
            self.logger.info(f"ℹ️ ALERTE INFO: {message}")
    
    def start_monitoring(self, check_interval_seconds: int = 60) -> bool:
        """
        Démarre le monitoring automatique
        
        Args:
            check_interval_seconds: Intervalle de vérification
            
        Returns:
            bool: True si démarré avec succès
        """
        if self.is_monitoring:
            self.logger.warning("⚠️ Monitoring déjà en cours")
            return False
        
        try:
            self.is_monitoring = True
            self.stop_event.clear()
            
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                args=(check_interval_seconds,),
                daemon=True,
                name="ExecutionLatencyTracker"
            )
            self.monitoring_thread.start()
            
            self.logger.info(f"🚀 Monitoring de latence démarré (intervalle: {check_interval_seconds}s)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage monitoring: {e}")
            self.is_monitoring = False
            return False
    
    def stop_monitoring(self) -> None:
        """Arrête le monitoring automatique"""
        if not self.is_monitoring:
            return
        
        self.logger.info("🛑 Arrêt du monitoring de latence...")
        self.is_monitoring = False
        self.stop_event.set()
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)
        
        self.logger.info("✅ Monitoring de latence arrêté")
    
    def _monitoring_loop(self, check_interval_seconds: int) -> None:
        """Boucle principale de monitoring"""
        self.logger.info("🔄 Boucle de monitoring de latence démarrée")
        
        while self.is_monitoring and not self.stop_event.is_set():
            try:
                # Analyser les tendances de performance
                self._analyze_performance_trends()
                
                # Attendre avant le prochain cycle
                self.stop_event.wait(check_interval_seconds)
                
            except Exception as e:
                self.logger.error(f"❌ Erreur dans la boucle de monitoring: {e}")
                time.sleep(5)
        
        self.logger.info("🔄 Boucle de monitoring de latence terminée")
    
    def _analyze_performance_trends(self) -> None:
        """Analyse les tendances de performance"""
        # Analyser les performances récentes
        recent_measurements = list(self.measurements)[-100:]  # 100 dernières mesures
        
        if len(recent_measurements) < 10:
            return
        
        # Grouper par étape
        stage_groups = defaultdict(list)
        for measurement in recent_measurements:
            stage_groups[measurement.stage].append(measurement)
        
        # Analyser chaque étape
        for stage, measurements in stage_groups.items():
            if len(measurements) < 5:
                continue
            
            durations = [m.duration_ms for m in measurements if m.success]
            if not durations:
                continue
            
            avg_duration = statistics.mean(durations)
            threshold = self.latency_thresholds.get(stage, 100.0)
            
            # Vérifier si la performance se dégrade
            if avg_duration > threshold * 1.2:  # 20% au-dessus du seuil
                self.logger.warning(f"⚠️ Performance dégradée détectée: {stage.value} = {avg_duration:.1f}ms (seuil: {threshold:.1f}ms)")
    
    def get_latency_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des latences"""
        return {
            'total_measurements': len(self.measurements),
            'total_pipelines': len(self.pipeline_measurements),
            'stages_monitored': len(self.stage_stats),
            'alerts_generated': len(self.alerts),
            'current_pipeline': self.current_pipeline.pipeline_id if self.current_pipeline else None,
            'monitoring_active': self.is_monitoring
        }
    
    def get_stage_performance(self) -> Dict[str, Any]:
        """Retourne la performance par étape"""
        return {
            stage.value: {
                'total_measurements': stats.total_measurements,
                'successful_measurements': stats.successful_measurements,
                'avg_duration_ms': round(stats.avg_duration_ms, 2),
                'min_duration_ms': round(stats.min_duration_ms, 2) if stats.min_duration_ms != float('inf') else 0,
                'max_duration_ms': round(stats.max_duration_ms, 2),
                'p50_duration_ms': round(stats.p50_duration_ms, 2),
                'p95_duration_ms': round(stats.p95_duration_ms, 2),
                'p99_duration_ms': round(stats.p99_duration_ms, 2),
                'error_rate': round(stats.error_rate, 3),
                'threshold_ms': self.latency_thresholds.get(stage, 100.0),
                'last_measurement': stats.last_measurement.isoformat() if stats.last_measurement else None
            }
            for stage, stats in self.stage_stats.items()
        }
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retourne les alertes récentes"""
        recent = list(self.alerts)[-limit:]
        return [
            {
                'timestamp': alert.timestamp.isoformat(),
                'alert_type': alert.alert_type.value,
                'severity': alert.severity,
                'message': alert.message,
                'stage': alert.stage.value if alert.stage else None,
                'duration_ms': alert.duration_ms,
                'threshold_ms': alert.threshold_ms
            }
            for alert in recent
        ]
    
    def export_metrics(self, format: str = 'json') -> str:
        """Exporte les métriques de latence"""
        if format == 'json':
            data = {
                'summary': self.get_latency_summary(),
                'stage_performance': self.get_stage_performance(),
                'recent_alerts': self.get_recent_alerts(50),
                'export_timestamp': datetime.now(timezone.utc).isoformat()
            }
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Format d'export non supporté: {format}")

# Instance globale
_global_latency_tracker: Optional[ExecutionLatencyTracker] = None

def get_execution_latency_tracker() -> ExecutionLatencyTracker:
    """Retourne l'instance globale du tracker de latence"""
    global _global_latency_tracker
    if _global_latency_tracker is None:
        _global_latency_tracker = ExecutionLatencyTracker()
    return _global_latency_tracker

def create_execution_latency_tracker(max_history_size: int = 1000) -> ExecutionLatencyTracker:
    """Crée une nouvelle instance du tracker de latence"""
    return ExecutionLatencyTracker(max_history_size)
