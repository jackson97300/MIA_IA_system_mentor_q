#!/usr/bin/env python3
"""
📊 SCORE MONITORING DASHBOARD - MIA_IA_SYSTEM
=============================================

Dashboard de monitoring des scores avec traces détaillées par composant.
- Visualisation en temps réel des scores de trading
- Traces détaillées par composant (MenthorQ, Battle Navale, VIX)
- Métriques de performance et qualité des données
- Alertes sur les anomalies de scoring
- Export des données pour analyse
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import threading
import time
from collections import defaultdict, deque
import statistics

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger

# Imports des composants existants
try:
    from core.score_calculator import ScoreCalculator, ScoreResult, ComponentTrace, ScoreComponent
    from core.advanced_metrics import AdvancedMetrics
    from performance.trade_logger import TradeRecord
    from config.menthorq_rules_loader import get_menthorq_rules
    SCORE_COMPONENTS_AVAILABLE = True
except ImportError:
    SCORE_COMPONENTS_AVAILABLE = False

logger = get_logger(__name__)

class DashboardMetric(Enum):
    """Métriques du dashboard"""
    SCORE_TREND = "score_trend"
    COMPONENT_PERFORMANCE = "component_performance"
    DATA_QUALITY = "data_quality"
    ANOMALY_DETECTION = "anomaly_detection"
    PERFORMANCE_STATS = "performance_stats"

class AlertType(Enum):
    """Types d'alertes du dashboard"""
    SCORE_ANOMALY = "score_anomaly"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    COMPONENT_FAILURE = "component_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"

@dataclass
class DashboardAlert:
    """Alerte du dashboard"""
    timestamp: datetime
    alert_type: AlertType
    severity: str  # "low", "medium", "high", "critical"
    message: str
    component: Optional[str] = None
    score_value: Optional[float] = None
    threshold: Optional[float] = None
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComponentPerformance:
    """Performance d'un composant de score"""
    component_name: str
    avg_score: float
    score_std: float
    min_score: float
    max_score: float
    data_quality: str
    last_update: datetime
    trend: str  # "improving", "stable", "degrading"
    anomaly_count: int = 0

@dataclass
class DashboardStats:
    """Statistiques du dashboard"""
    total_calculations: int = 0
    avg_calculation_time_ms: float = 0.0
    alerts_generated: int = 0
    data_quality_issues: int = 0
    component_failures: int = 0
    last_update: Optional[datetime] = None
    uptime_seconds: float = 0.0

class ScoreMonitoringDashboard:
    """Dashboard de monitoring des scores avec traces détaillées"""
    
    def __init__(self, max_history_size: int = 1000):
        """
        Initialisation du dashboard de monitoring
        
        Args:
            max_history_size: Taille maximale de l'historique
        """
        self.max_history_size = max_history_size
        self.logger = get_logger(f"{__name__}.ScoreMonitoringDashboard")
        
        # Historique des scores
        self.score_history: deque = deque(maxlen=max_history_size)
        self.component_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history_size))
        
        # Alertes
        self.alerts: deque = deque(maxlen=500)
        
        # Statistiques
        self.stats = DashboardStats()
        self.start_time = datetime.now(timezone.utc)
        
        # Performance des composants
        self.component_performance: Dict[str, ComponentPerformance] = {}
        
        # Configuration des seuils d'alerte
        self.alert_thresholds = {
            'score_anomaly_threshold': 0.3,  # Écart type pour détecter anomalies
            'data_quality_warning_threshold': 0.8,  # Score de qualité minimum
            'component_failure_threshold': 0.1,  # Score minimum pour un composant
            'performance_degradation_threshold': 100.0  # Temps de calcul max en ms
        }
        
        # Thread de monitoring
        self.monitoring_thread: Optional[threading.Thread] = None
        self.is_monitoring = False
        self.stop_event = threading.Event()
        
        self.logger.info(f"📊 ScoreMonitoringDashboard initialisé (components_available: {SCORE_COMPONENTS_AVAILABLE})")
    
    def start_monitoring(self, check_interval_seconds: int = 30) -> bool:
        """
        Démarre le monitoring automatique
        
        Args:
            check_interval_seconds: Intervalle de vérification en secondes
            
        Returns:
            bool: True si démarré avec succès
        """
        if self.is_monitoring:
            self.logger.warning("⚠️ Monitoring déjà en cours")
            return False
        
        try:
            self.is_monitoring = True
            self.stop_event.clear()
            
            # Démarrer le thread de monitoring
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                args=(check_interval_seconds,),
                daemon=True,
                name="ScoreMonitoringDashboard"
            )
            self.monitoring_thread.start()
            
            self.logger.info(f"🚀 Monitoring des scores démarré (intervalle: {check_interval_seconds}s)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage monitoring: {e}")
            self.is_monitoring = False
            return False
    
    def stop_monitoring(self) -> None:
        """Arrête le monitoring automatique"""
        if not self.is_monitoring:
            return
        
        self.logger.info("🛑 Arrêt du monitoring des scores...")
        self.is_monitoring = False
        self.stop_event.set()
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)
        
        self.logger.info("✅ Monitoring des scores arrêté")
    
    def _monitoring_loop(self, check_interval_seconds: int) -> None:
        """Boucle principale de monitoring"""
        self.logger.info("🔄 Boucle de monitoring des scores démarrée")
        
        while self.is_monitoring and not self.stop_event.is_set():
            try:
                # Effectuer un cycle de monitoring
                self._monitoring_cycle()
                
                # Attendre avant le prochain cycle
                self.stop_event.wait(check_interval_seconds)
                
            except Exception as e:
                self.logger.error(f"❌ Erreur dans la boucle de monitoring: {e}")
                time.sleep(5)  # Pause avant de réessayer
        
        self.logger.info("🔄 Boucle de monitoring des scores terminée")
    
    def _monitoring_cycle(self) -> None:
        """Effectue un cycle de monitoring"""
        try:
            # Analyser les tendances des scores
            self._analyze_score_trends()
            
            # Vérifier la qualité des données
            self._check_data_quality()
            
            # Détecter les anomalies
            self._detect_anomalies()
            
            # Mettre à jour les statistiques
            self._update_stats()
            
        except Exception as e:
            self.logger.error(f"❌ Erreur cycle de monitoring: {e}")
    
    def add_score_result(self, score_result: ScoreResult) -> None:
        """
        Ajoute un résultat de score au dashboard
        
        Args:
            score_result: Résultat de calcul de score
        """
        try:
            # Ajouter à l'historique principal
            self.score_history.append(score_result)
            
            # Ajouter les composants à leur historique respectif
            for component in score_result.components:
                self.component_history[component.component.value].append(component)
            
            # Mettre à jour les statistiques
            self.stats.total_calculations += 1
            self.stats.last_update = datetime.now(timezone.utc)
            
            # Calculer le temps de calcul
            if hasattr(score_result, 'calculation_time_ms'):
                self._update_avg_calculation_time(score_result.calculation_time_ms)
            
            # Vérifier les alertes
            self._check_score_alerts(score_result)
            
            self.logger.debug(f"📊 Score ajouté au dashboard: {score_result.final_score:.3f}")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur ajout score au dashboard: {e}")
    
    def _analyze_score_trends(self) -> None:
        """Analyse les tendances des scores"""
        if len(self.score_history) < 10:
            return
        
        try:
            # Analyser la tendance globale
            recent_scores = [s.final_score for s in list(self.score_history)[-10:]]
            trend = self._calculate_trend(recent_scores)
            
            # Analyser les tendances par composant
            for component_name, history in self.component_history.items():
                if len(history) >= 5:
                    recent_component_scores = [c.score for c in list(history)[-5:]]
                    component_trend = self._calculate_trend(recent_component_scores)
                    
                    # Mettre à jour la performance du composant
                    self._update_component_performance(component_name, recent_component_scores, component_trend)
            
        except Exception as e:
            self.logger.error(f"❌ Erreur analyse tendances: {e}")
    
    def _check_data_quality(self) -> None:
        """Vérifie la qualité des données"""
        if len(self.score_history) < 5:
            return
        
        try:
            recent_results = list(self.score_history)[-5:]
            
            for result in recent_results:
                # Vérifier la qualité des données pour chaque composant
                for component in result.components:
                    if component.data_quality == "POOR":
                        self._generate_alert(
                            AlertType.DATA_QUALITY_ISSUE,
                            "medium",
                            f"Qualité des données faible pour {component.component.value}",
                            component.component.value,
                            component.raw_score,
                            self.alert_thresholds['data_quality_warning_threshold']
                        )
                        self.stats.data_quality_issues += 1
            
        except Exception as e:
            self.logger.error(f"❌ Erreur vérification qualité données: {e}")
    
    def _detect_anomalies(self) -> None:
        """Détecte les anomalies dans les scores"""
        if len(self.score_history) < 20:
            return
        
        try:
            recent_scores = [s.final_score for s in list(self.score_history)[-20:]]
            
            if len(recent_scores) >= 10:
                # Calculer la moyenne et l'écart type
                mean_score = statistics.mean(recent_scores)
                std_score = statistics.stdev(recent_scores) if len(recent_scores) > 1 else 0
                
                # Détecter les scores anormaux
                threshold = self.alert_thresholds['score_anomaly_threshold']
                for i, score in enumerate(recent_scores[-5:]):  # Vérifier les 5 derniers
                    if abs(score - mean_score) > threshold * std_score:
                        self._generate_alert(
                            AlertType.SCORE_ANOMALY,
                            "high",
                            f"Score anormal détecté: {score:.3f} (moyenne: {mean_score:.3f})",
                            None,
                            score,
                            mean_score + threshold * std_score
                        )
            
        except Exception as e:
            self.logger.error(f"❌ Erreur détection anomalies: {e}")
    
    def _check_score_alerts(self, score_result: ScoreResult) -> None:
        """Vérifie les alertes pour un résultat de score"""
        try:
            # Vérifier les scores de composants trop faibles
            for component in score_result.components:
                if component.raw_score < self.alert_thresholds['component_failure_threshold']:
                    self._generate_alert(
                        AlertType.COMPONENT_FAILURE,
                        "high",
                        f"Score de composant critique: {component.component.value} = {component.raw_score:.3f}",
                        component.component.value,
                        component.raw_score,
                        self.alert_thresholds['component_failure_threshold']
                    )
                    self.stats.component_failures += 1
            
            # Vérifier le temps de calcul
            if hasattr(score_result, 'calculation_time_ms'):
                if score_result.calculation_time_ms > self.alert_thresholds['performance_degradation_threshold']:
                    self._generate_alert(
                        AlertType.PERFORMANCE_DEGRADATION,
                        "medium",
                        f"Performance dégradée: {score_result.calculation_time_ms:.1f}ms",
                        None,
                        score_result.calculation_time_ms,
                        self.alert_thresholds['performance_degradation_threshold']
                    )
            
        except Exception as e:
            self.logger.error(f"❌ Erreur vérification alertes score: {e}")
    
    def _generate_alert(self, alert_type: AlertType, severity: str, message: str,
                       component: Optional[str], value: Optional[float], threshold: Optional[float]) -> None:
        """Génère une alerte"""
        alert = DashboardAlert(
            timestamp=datetime.now(timezone.utc),
            alert_type=alert_type,
            severity=severity,
            message=message,
            component=component,
            score_value=value,
            threshold=threshold
        )
        
        self.alerts.append(alert)
        self.stats.alerts_generated += 1
        
        # Log selon la sévérité
        if severity == "critical":
            self.logger.critical(f"🚨 ALERTE CRITIQUE: {message}")
        elif severity == "high":
            self.logger.error(f"⚠️ ALERTE HAUTE: {message}")
        elif severity == "medium":
            self.logger.warning(f"⚠️ ALERTE MOYENNE: {message}")
        else:
            self.logger.info(f"ℹ️ ALERTE INFO: {message}")
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calcule la tendance d'une série de valeurs"""
        if len(values) < 2:
            return "stable"
        
        # Calculer la pente de régression linéaire simple
        n = len(values)
        x = list(range(n))
        y = values
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "degrading"
        else:
            return "stable"
    
    def _update_component_performance(self, component_name: str, scores: List[float], trend: str) -> None:
        """Met à jour la performance d'un composant"""
        try:
            avg_score = statistics.mean(scores)
            score_std = statistics.stdev(scores) if len(scores) > 1 else 0
            min_score = min(scores)
            max_score = max(scores)
            
            # Déterminer la qualité des données
            data_quality = "GOOD"
            if score_std > 0.3:
                data_quality = "POOR"
            elif score_std > 0.15:
                data_quality = "FAIR"
            
            self.component_performance[component_name] = ComponentPerformance(
                component_name=component_name,
                avg_score=avg_score,
                score_std=score_std,
                min_score=min_score,
                max_score=max_score,
                data_quality=data_quality,
                last_update=datetime.now(timezone.utc),
                trend=trend
            )
            
        except Exception as e:
            self.logger.error(f"❌ Erreur mise à jour performance composant {component_name}: {e}")
    
    def _update_avg_calculation_time(self, calculation_time_ms: float) -> None:
        """Met à jour le temps de calcul moyen"""
        if self.stats.avg_calculation_time_ms == 0:
            self.stats.avg_calculation_time_ms = calculation_time_ms
        else:
            # Moyenne mobile
            alpha = 0.1  # Facteur de lissage
            self.stats.avg_calculation_time_ms = (
                alpha * calculation_time_ms + 
                (1 - alpha) * self.stats.avg_calculation_time_ms
            )
    
    def _update_stats(self) -> None:
        """Met à jour les statistiques générales"""
        self.stats.uptime_seconds = (datetime.now(timezone.utc) - self.start_time).total_seconds()
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Retourne un résumé du dashboard"""
        return {
            'status': 'active' if self.is_monitoring else 'inactive',
            'total_calculations': self.stats.total_calculations,
            'avg_calculation_time_ms': round(self.stats.avg_calculation_time_ms, 2),
            'alerts_generated': self.stats.alerts_generated,
            'data_quality_issues': self.stats.data_quality_issues,
            'component_failures': self.stats.component_failures,
            'uptime_seconds': round(self.stats.uptime_seconds, 1),
            'last_update': self.stats.last_update.isoformat() if self.stats.last_update else None,
            'components_monitored': len(self.component_performance),
            'recent_scores_count': len(self.score_history)
        }
    
    def get_component_performance(self) -> Dict[str, Any]:
        """Retourne la performance des composants"""
        return {
            component_name: {
                'avg_score': round(perf.avg_score, 3),
                'score_std': round(perf.score_std, 3),
                'min_score': round(perf.min_score, 3),
                'max_score': round(perf.max_score, 3),
                'data_quality': perf.data_quality,
                'trend': perf.trend,
                'last_update': perf.last_update.isoformat(),
                'anomaly_count': perf.anomaly_count
            }
            for component_name, perf in self.component_performance.items()
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
                'component': alert.component,
                'score_value': alert.score_value,
                'threshold': alert.threshold
            }
            for alert in recent
        ]
    
    def get_score_trends(self, hours: int = 1) -> Dict[str, Any]:
        """Retourne les tendances des scores sur une période"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Filtrer les scores récents
        recent_scores = [
            s for s in self.score_history 
            if s.timestamp >= cutoff_time
        ]
        
        if not recent_scores:
            return {'error': 'Pas de données récentes'}
        
        scores = [s.final_score for s in recent_scores]
        
        return {
            'period_hours': hours,
            'score_count': len(scores),
            'avg_score': round(statistics.mean(scores), 3),
            'min_score': round(min(scores), 3),
            'max_score': round(max(scores), 3),
            'score_std': round(statistics.stdev(scores) if len(scores) > 1 else 0, 3),
            'trend': self._calculate_trend(scores),
            'sentiment_distribution': self._calculate_sentiment_distribution(recent_scores)
        }
    
    def _calculate_sentiment_distribution(self, score_results: List[ScoreResult]) -> Dict[str, int]:
        """Calcule la distribution des sentiments"""
        distribution = {'BULLISH': 0, 'BEARISH': 0, 'NEUTRAL': 0}
        
        for result in score_results:
            sentiment = getattr(result, 'sentiment', 'NEUTRAL')
            if sentiment in distribution:
                distribution[sentiment] += 1
        
        return distribution
    
    def export_data(self, format: str = 'json') -> str:
        """Exporte les données du dashboard"""
        if format == 'json':
            data = {
                'dashboard_summary': self.get_dashboard_summary(),
                'component_performance': self.get_component_performance(),
                'recent_alerts': self.get_recent_alerts(50),
                'score_trends': self.get_score_trends(24),
                'export_timestamp': datetime.now(timezone.utc).isoformat()
            }
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Format d'export non supporté: {format}")

# Instance globale
_global_dashboard: Optional[ScoreMonitoringDashboard] = None

def get_score_monitoring_dashboard() -> ScoreMonitoringDashboard:
    """Retourne l'instance globale du dashboard de monitoring des scores"""
    global _global_dashboard
    if _global_dashboard is None:
        _global_dashboard = ScoreMonitoringDashboard()
    return _global_dashboard

def create_score_monitoring_dashboard(max_history_size: int = 1000) -> ScoreMonitoringDashboard:
    """Crée une nouvelle instance du dashboard de monitoring des scores"""
    return ScoreMonitoringDashboard(max_history_size)
