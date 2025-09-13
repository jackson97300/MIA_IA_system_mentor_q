#!/usr/bin/env python3
"""
📊 VIX REGIME TRACKER - MIA_IA_SYSTEM
======================================

Système de tracking du régime VIX dans les décisions de trading.
- Surveillance continue des niveaux VIX
- Détection des changements de régime
- Impact sur les décisions de trading
- Métriques de performance par régime
- Alertes sur les transitions critiques
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

# Imports des composants existants
try:
    from core.menthorq_staleness_manager import VIXRegime as ImportedVIXRegime
    from config.menthorq_rules_loader import get_menthorq_rules
    VIX_COMPONENTS_AVAILABLE = True
    VIXRegime = ImportedVIXRegime
except ImportError:
    VIX_COMPONENTS_AVAILABLE = False
    # Fallback enum
    class VIXRegime(Enum):
        LOW = "low"
        NORMAL = "normal"
        HIGH_VIX = "high_vix"
        EXTREME = "extreme"

logger = get_logger(__name__)

class VIXTransitionType(Enum):
    """Types de transitions VIX"""
    REGIME_CHANGE = "regime_change"
    SPIKE_DETECTED = "spike_detected"
    CRASH_DETECTED = "crash_detected"
    VOLATILITY_EXPLOSION = "volatility_explosion"
    CALM_PERIOD = "calm_period"

class TradingDecisionType(Enum):
    """Types de décisions de trading"""
    SIGNAL_GENERATED = "signal_generated"
    SIGNAL_BLOCKED = "signal_blocked"
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"
    RISK_ADJUSTED = "risk_adjusted"
    SIZING_MODIFIED = "sizing_modified"

@dataclass
class VIXSnapshot:
    """Snapshot VIX à un instant T"""
    timestamp: datetime
    vix_level: float
    regime: VIXRegime
    change_from_previous: float
    change_percent: float
    volatility_trend: str  # "increasing", "decreasing", "stable"
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VIXTransition:
    """Transition de régime VIX"""
    timestamp: datetime
    from_regime: VIXRegime
    to_regime: VIXRegime
    transition_type: VIXTransitionType
    vix_level: float
    duration_in_previous_regime: timedelta
    impact_score: float  # 0.0 à 1.0
    trading_implications: List[str] = field(default_factory=list)

@dataclass
class TradingDecision:
    """Décision de trading avec contexte VIX"""
    timestamp: datetime
    decision_type: TradingDecisionType
    vix_regime: VIXRegime
    vix_level: float
    decision_outcome: str  # "success", "failure", "neutral"
    vix_impact: float  # Impact du régime VIX sur la décision (0.0 à 1.0)
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VIXRegimeStats:
    """Statistiques par régime VIX"""
    regime: VIXRegime
    total_time_seconds: float = 0.0
    total_decisions: int = 0
    successful_decisions: int = 0
    failed_decisions: int = 0
    avg_vix_level: float = 0.0
    min_vix_level: float = float('inf')
    max_vix_level: float = 0.0
    success_rate: float = 0.0
    avg_decision_impact: float = 0.0
    last_activity: Optional[datetime] = None

@dataclass
class VIXAlert:
    """Alerte VIX"""
    timestamp: datetime
    alert_type: str
    severity: str  # "low", "medium", "high", "critical"
    message: str
    vix_level: float
    regime: VIXRegime
    context: Dict[str, Any] = field(default_factory=dict)

class VIXRegimeTracker:
    """Tracker du régime VIX dans les décisions de trading"""
    
    def __init__(self, max_history_size: int = 1000):
        """
        Initialisation du tracker VIX
        
        Args:
            max_history_size: Taille maximale de l'historique
        """
        self.max_history_size = max_history_size
        self.logger = get_logger(f"{__name__}.VIXRegimeTracker")
        
        # Historique des données
        self.vix_snapshots: deque = deque(maxlen=max_history_size)
        self.vix_transitions: deque = deque(maxlen=max_history_size)
        self.trading_decisions: deque = deque(maxlen=max_history_size)
        self.alerts: deque = deque(maxlen=500)
        
        # État actuel
        self.current_regime: Optional[VIXRegime] = None
        self.current_vix_level: float = 0.0
        self.last_snapshot: Optional[VIXSnapshot] = None
        
        # Statistiques par régime
        self.regime_stats: Dict[VIXRegime, VIXRegimeStats] = {}
        
        # Configuration des seuils VIX
        self.vix_thresholds = {
            VIXRegime.NORMAL: 25.0,
            VIXRegime.HIGH_VIX: 35.0,
            VIXRegime.EXTREME: 50.0
        }
        
        # Seuils d'alerte
        self.alert_thresholds = {
            'spike_threshold': 0.20,      # 20% d'augmentation
            'crash_threshold': -0.15,     # 15% de baisse
            'extreme_threshold': 50.0,    # Niveau VIX extrême
            'calm_threshold': 12.0,       # Niveau VIX très calme
            'regime_change_min_duration': 300  # 5 minutes minimum entre changements
        }
        
        # Thread de monitoring
        self.monitoring_thread: Optional[threading.Thread] = None
        self.is_monitoring = False
        self.stop_event = threading.Event()
        
        # Initialiser les statistiques par régime
        for regime in VIXRegime:
            self.regime_stats[regime] = VIXRegimeStats(regime=regime)
        
        self.logger.info(f"📊 VIXRegimeTracker initialisé (components_available: {VIX_COMPONENTS_AVAILABLE})")
    
    def update_vix_level(self, vix_level: float, context: Optional[Dict[str, Any]] = None) -> VIXSnapshot:
        """
        Met à jour le niveau VIX et détecte les changements de régime
        
        Args:
            vix_level: Niveau VIX actuel
            context: Contexte supplémentaire
            
        Returns:
            VIXSnapshot: Snapshot VIX créé
        """
        now = datetime.now(timezone.utc)
        
        # Calculer les changements
        change_from_previous = 0.0
        change_percent = 0.0
        volatility_trend = "stable"
        
        if self.last_snapshot:
            change_from_previous = vix_level - self.last_snapshot.vix_level
            if self.last_snapshot.vix_level > 0:
                change_percent = (change_from_previous / self.last_snapshot.vix_level) * 100
            
            if change_percent > 5:
                volatility_trend = "increasing"
            elif change_percent < -5:
                volatility_trend = "decreasing"
        
        # Déterminer le régime actuel
        current_regime = self._determine_vix_regime(vix_level)
        
        # Créer le snapshot
        snapshot = VIXSnapshot(
            timestamp=now,
            vix_level=vix_level,
            regime=current_regime,
            change_from_previous=change_from_previous,
            change_percent=change_percent,
            volatility_trend=volatility_trend,
            context=context or {}
        )
        
        # Détecter les transitions
        if self.current_regime and self.current_regime != current_regime:
            self._detect_regime_transition(snapshot)
        
        # Détecter les alertes
        self._check_vix_alerts(snapshot)
        
        # Mettre à jour l'état
        self.current_regime = current_regime
        self.current_vix_level = vix_level
        self.last_snapshot = snapshot
        
        # Ajouter à l'historique
        self.vix_snapshots.append(snapshot)
        
        # Mettre à jour les statistiques
        self._update_regime_stats(current_regime, vix_level)
        
        self.logger.debug(f"📊 VIX mis à jour: {vix_level:.2f} ({current_regime.value})")
        return snapshot
    
    def record_trading_decision(self, decision_type: TradingDecisionType, 
                              outcome: str, vix_impact: float = 0.0,
                              context: Optional[Dict[str, Any]] = None) -> TradingDecision:
        """
        Enregistre une décision de trading avec contexte VIX
        
        Args:
            decision_type: Type de décision
            outcome: Résultat de la décision
            vix_impact: Impact du régime VIX (0.0 à 1.0)
            context: Contexte supplémentaire
            
        Returns:
            TradingDecision: Décision enregistrée
        """
        now = datetime.now(timezone.utc)
        
        decision = TradingDecision(
            timestamp=now,
            decision_type=decision_type,
            vix_regime=self.current_regime or VIXRegime.NORMAL,
            vix_level=self.current_vix_level,
            decision_outcome=outcome,
            vix_impact=vix_impact,
            context=context or {}
        )
        
        # Ajouter à l'historique
        self.trading_decisions.append(decision)
        
        # Mettre à jour les statistiques de décision
        self._update_decision_stats(decision)
        
        self.logger.debug(f"📊 Décision enregistrée: {decision_type.value} ({outcome}) - VIX: {self.current_vix_level:.2f}")
        return decision
    
    def _determine_vix_regime(self, vix_level: float) -> VIXRegime:
        """Détermine le régime VIX basé sur le niveau"""
        if vix_level <= self.vix_thresholds[VIXRegime.NORMAL]:
            return VIXRegime.NORMAL
        elif vix_level <= self.vix_thresholds[VIXRegime.HIGH_VIX]:
            return VIXRegime.HIGH_VIX
        else:
            return VIXRegime.EXTREME
    
    def _detect_regime_transition(self, snapshot: VIXSnapshot) -> None:
        """Détecte et enregistre une transition de régime"""
        if not self.last_snapshot:
            return
        
        # Calculer la durée dans le régime précédent
        duration_in_previous = snapshot.timestamp - self.last_snapshot.timestamp
        
        # Vérifier la durée minimale
        if duration_in_previous.total_seconds() < self.alert_thresholds['regime_change_min_duration']:
            self.logger.debug(f"📊 Transition VIX ignorée (durée trop courte: {duration_in_previous.total_seconds():.1f}s)")
            return
        
        # Déterminer le type de transition
        transition_type = self._classify_transition(self.last_snapshot, snapshot)
        
        # Calculer l'impact
        impact_score = self._calculate_transition_impact(self.last_snapshot, snapshot)
        
        # Générer les implications trading
        trading_implications = self._generate_trading_implications(self.last_snapshot, snapshot)
        
        # Créer la transition
        transition = VIXTransition(
            timestamp=snapshot.timestamp,
            from_regime=self.last_snapshot.regime,
            to_regime=snapshot.regime,
            transition_type=transition_type,
            vix_level=snapshot.vix_level,
            duration_in_previous_regime=duration_in_previous,
            impact_score=impact_score,
            trading_implications=trading_implications
        )
        
        # Ajouter à l'historique
        self.vix_transitions.append(transition)
        
        self.logger.info(f"📊 Transition VIX détectée: {self.last_snapshot.regime.value} → {snapshot.regime.value} ({transition_type.value})")
    
    def _classify_transition(self, from_snapshot: VIXSnapshot, to_snapshot: VIXSnapshot) -> VIXTransitionType:
        """Classifie le type de transition VIX"""
        change_percent = to_snapshot.change_percent
        
        if change_percent > self.alert_thresholds['spike_threshold'] * 100:
            return VIXTransitionType.SPIKE_DETECTED
        elif change_percent < self.alert_thresholds['crash_threshold'] * 100:
            return VIXTransitionType.CRASH_DETECTED
        elif to_snapshot.vix_level > self.alert_thresholds['extreme_threshold']:
            return VIXTransitionType.VOLATILITY_EXPLOSION
        elif to_snapshot.vix_level < self.alert_thresholds['calm_threshold']:
            return VIXTransitionType.CALM_PERIOD
        else:
            return VIXTransitionType.REGIME_CHANGE
    
    def _calculate_transition_impact(self, from_snapshot: VIXSnapshot, to_snapshot: VIXSnapshot) -> float:
        """Calcule l'impact d'une transition VIX"""
        # Impact basé sur la magnitude du changement
        change_magnitude = abs(to_snapshot.change_percent) / 100
        
        # Impact basé sur le régime de destination
        regime_impact = {
            VIXRegime.NORMAL: 0.4,
            VIXRegime.HIGH_VIX: 0.7,
            VIXRegime.EXTREME: 1.0
        }
        
        base_impact = regime_impact.get(to_snapshot.regime, 0.4)
        return min(1.0, base_impact + change_magnitude * 0.3)
    
    def _generate_trading_implications(self, from_snapshot: VIXSnapshot, to_snapshot: VIXSnapshot) -> List[str]:
        """Génère les implications trading d'une transition VIX"""
        implications = []
        
        if to_snapshot.regime == VIXRegime.EXTREME:
            implications.extend([
                "Réduire la taille des positions",
                "Augmenter les stops loss",
                "Éviter les positions overnight",
                "Surveiller les gaps d'ouverture"
            ])
        elif to_snapshot.regime == VIXRegime.HIGH_VIX:
            implications.extend([
                "Position sizing conservateur",
                "Stops plus serrés",
                "Éviter les breakouts"
            ])
        elif to_snapshot.regime == VIXRegime.NORMAL:
            implications.extend([
                "Position sizing normal",
                "Rechercher les breakouts",
                "Stops plus larges"
            ])
        
        if to_snapshot.change_percent > 20:
            implications.append("Attendre la stabilisation avant de trader")
        elif to_snapshot.change_percent < -15:
            implications.append("Opportunité de reprise des positions")
        
        return implications
    
    def _check_vix_alerts(self, snapshot: VIXSnapshot) -> None:
        """Vérifie les alertes VIX"""
        # Alerte niveau extrême
        if snapshot.vix_level > self.alert_thresholds['extreme_threshold']:
            self._generate_alert(
                "extreme_vix",
                "critical",
                f"VIX niveau extrême: {snapshot.vix_level:.2f}",
                snapshot.vix_level,
                snapshot.regime
            )
        
        # Alerte spike
        if snapshot.change_percent > self.alert_thresholds['spike_threshold'] * 100:
            self._generate_alert(
                "vix_spike",
                "high",
                f"Spike VIX détecté: +{snapshot.change_percent:.1f}% ({snapshot.vix_level:.2f})",
                snapshot.vix_level,
                snapshot.regime
            )
        
        # Alerte crash
        if snapshot.change_percent < self.alert_thresholds['crash_threshold'] * 100:
            self._generate_alert(
                "vix_crash",
                "medium",
                f"Crash VIX détecté: {snapshot.change_percent:.1f}% ({snapshot.vix_level:.2f})",
                snapshot.vix_level,
                snapshot.regime
            )
        
        # Alerte période calme
        if snapshot.vix_level < self.alert_thresholds['calm_threshold']:
            self._generate_alert(
                "calm_period",
                "low",
                f"Période VIX très calme: {snapshot.vix_level:.2f}",
                snapshot.vix_level,
                snapshot.regime
            )
    
    def _generate_alert(self, alert_type: str, severity: str, message: str, 
                       vix_level: float, regime: VIXRegime) -> None:
        """Génère une alerte VIX"""
        alert = VIXAlert(
            timestamp=datetime.now(timezone.utc),
            alert_type=alert_type,
            severity=severity,
            message=message,
            vix_level=vix_level,
            regime=regime
        )
        
        self.alerts.append(alert)
        
        # Log selon la sévérité
        if severity == "critical":
            self.logger.critical(f"🚨 ALERTE CRITIQUE VIX: {message}")
        elif severity == "high":
            self.logger.error(f"⚠️ ALERTE HAUTE VIX: {message}")
        elif severity == "medium":
            self.logger.warning(f"⚠️ ALERTE MOYENNE VIX: {message}")
        else:
            self.logger.info(f"ℹ️ ALERTE INFO VIX: {message}")
    
    def _update_regime_stats(self, regime: VIXRegime, vix_level: float) -> None:
        """Met à jour les statistiques d'un régime"""
        stats = self.regime_stats[regime]
        
        # Mettre à jour les niveaux VIX
        stats.min_vix_level = min(stats.min_vix_level, vix_level)
        stats.max_vix_level = max(stats.max_vix_level, vix_level)
        
        # Moyenne mobile
        if stats.avg_vix_level == 0:
            stats.avg_vix_level = vix_level
        else:
            alpha = 0.1  # Facteur de lissage
            stats.avg_vix_level = alpha * vix_level + (1 - alpha) * stats.avg_vix_level
        
        stats.last_activity = datetime.now(timezone.utc)
    
    def _update_decision_stats(self, decision: TradingDecision) -> None:
        """Met à jour les statistiques de décision"""
        stats = self.regime_stats[decision.vix_regime]
        
        stats.total_decisions += 1
        
        if decision.decision_outcome == "success":
            stats.successful_decisions += 1
        elif decision.decision_outcome == "failure":
            stats.failed_decisions += 1
        
        # Calculer le taux de succès
        if stats.total_decisions > 0:
            stats.success_rate = stats.successful_decisions / stats.total_decisions
        
        # Moyenne mobile de l'impact
        if stats.avg_decision_impact == 0:
            stats.avg_decision_impact = decision.vix_impact
        else:
            alpha = 0.1
            stats.avg_decision_impact = alpha * decision.vix_impact + (1 - alpha) * stats.avg_decision_impact
    
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
                name="VIXRegimeTracker"
            )
            self.monitoring_thread.start()
            
            self.logger.info(f"🚀 Monitoring VIX démarré (intervalle: {check_interval_seconds}s)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage monitoring: {e}")
            self.is_monitoring = False
            return False
    
    def stop_monitoring(self) -> None:
        """Arrête le monitoring automatique"""
        if not self.is_monitoring:
            return
        
        self.logger.info("🛑 Arrêt du monitoring VIX...")
        self.is_monitoring = False
        self.stop_event.set()
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)
        
        self.logger.info("✅ Monitoring VIX arrêté")
    
    def _monitoring_loop(self, check_interval_seconds: int) -> None:
        """Boucle principale de monitoring"""
        self.logger.info("🔄 Boucle de monitoring VIX démarrée")
        
        while self.is_monitoring and not self.stop_event.is_set():
            try:
                # Analyser les tendances VIX
                self._analyze_vix_trends()
                
                # Attendre avant le prochain cycle
                self.stop_event.wait(check_interval_seconds)
                
            except Exception as e:
                self.logger.error(f"❌ Erreur dans la boucle de monitoring: {e}")
                time.sleep(5)
        
        self.logger.info("🔄 Boucle de monitoring VIX terminée")
    
    def _analyze_vix_trends(self) -> None:
        """Analyse les tendances VIX"""
        if len(self.vix_snapshots) < 10:
            return
        
        # Analyser les tendances récentes
        recent_snapshots = list(self.vix_snapshots)[-10:]
        vix_levels = [s.vix_level for s in recent_snapshots]
        
        if len(vix_levels) >= 5:
            avg_vix = statistics.mean(vix_levels)
            vix_std = statistics.stdev(vix_levels) if len(vix_levels) > 1 else 0
            
            # Détecter la volatilité de la volatilité
            if vix_std > 5.0:  # VIX très volatile
                self.logger.warning(f"⚠️ VIX très volatile détecté: std={vix_std:.2f}, avg={avg_vix:.2f}")
    
    def get_vix_summary(self) -> Dict[str, Any]:
        """Retourne un résumé VIX"""
        return {
            'current_vix_level': self.current_vix_level,
            'current_regime': self.current_regime.value if self.current_regime else None,
            'total_snapshots': len(self.vix_snapshots),
            'total_transitions': len(self.vix_transitions),
            'total_decisions': len(self.trading_decisions),
            'alerts_generated': len(self.alerts),
            'monitoring_active': self.is_monitoring,
            'last_update': self.last_snapshot.timestamp.isoformat() if self.last_snapshot else None
        }
    
    def get_regime_performance(self) -> Dict[str, Any]:
        """Retourne la performance par régime VIX"""
        return {
            regime.value: {
                'total_time_seconds': stats.total_time_seconds,
                'total_decisions': stats.total_decisions,
                'successful_decisions': stats.successful_decisions,
                'failed_decisions': stats.failed_decisions,
                'success_rate': round(stats.success_rate, 3),
                'avg_vix_level': round(stats.avg_vix_level, 2),
                'min_vix_level': round(stats.min_vix_level, 2) if stats.min_vix_level != float('inf') else 0,
                'max_vix_level': round(stats.max_vix_level, 2),
                'avg_decision_impact': round(stats.avg_decision_impact, 3),
                'last_activity': stats.last_activity.isoformat() if stats.last_activity else None
            }
            for regime, stats in self.regime_stats.items()
        }
    
    def get_recent_transitions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retourne les transitions récentes"""
        recent = list(self.vix_transitions)[-limit:]
        return [
            {
                'timestamp': transition.timestamp.isoformat(),
                'from_regime': transition.from_regime.value,
                'to_regime': transition.to_regime.value,
                'transition_type': transition.transition_type.value,
                'vix_level': transition.vix_level,
                'duration_seconds': transition.duration_in_previous_regime.total_seconds(),
                'impact_score': transition.impact_score,
                'trading_implications': transition.trading_implications
            }
            for transition in recent
        ]
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retourne les alertes récentes"""
        recent = list(self.alerts)[-limit:]
        return [
            {
                'timestamp': alert.timestamp.isoformat(),
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'message': alert.message,
                'vix_level': alert.vix_level,
                'regime': alert.regime.value
            }
            for alert in recent
        ]
    
    def export_vix_data(self, format: str = 'json') -> str:
        """Exporte les données VIX"""
        if format == 'json':
            data = {
                'summary': self.get_vix_summary(),
                'regime_performance': self.get_regime_performance(),
                'recent_transitions': self.get_recent_transitions(50),
                'recent_alerts': self.get_recent_alerts(50),
                'export_timestamp': datetime.now(timezone.utc).isoformat()
            }
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Format d'export non supporté: {format}")

# Instance globale
_global_vix_tracker: Optional[VIXRegimeTracker] = None

def get_vix_regime_tracker() -> VIXRegimeTracker:
    """Retourne l'instance globale du tracker VIX"""
    global _global_vix_tracker
    if _global_vix_tracker is None:
        _global_vix_tracker = VIXRegimeTracker()
    return _global_vix_tracker

def create_vix_regime_tracker(max_history_size: int = 1000) -> VIXRegimeTracker:
    """Crée une nouvelle instance du tracker VIX"""
    return VIXRegimeTracker(max_history_size)
