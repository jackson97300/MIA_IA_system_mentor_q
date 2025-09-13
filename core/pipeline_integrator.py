#!/usr/bin/env python3
"""
🔗 PIPELINE INTEGRATOR - MIA_IA_SYSTEM
=======================================

Système d'intégration complet du pipeline de trading.
Connecte tous les composants créés dans un pipeline unifié :
- Configuration centralisée MenthorQ
- Monitoring de staleness automatique
- Dashboard de scores avec traces
- Tracking de latence d'exécution
- Tracking du régime VIX
- Filtre leadership amélioré
- Trade logger enrichi
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import threading
import time
from collections import defaultdict, deque
import json

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger

# Imports des composants créés
try:
    from config.menthorq_rules_loader import get_menthorq_rules
    from core.menthorq_staleness_manager import get_staleness_manager, VIXRegime
    from core.menthorq_staleness_monitor import get_menthorq_staleness_monitor
    from core.score_monitoring_dashboard import get_score_monitoring_dashboard
    from core.execution_latency_tracker import get_execution_latency_tracker, LatencyStage
    from core.vix_regime_tracker import get_vix_regime_tracker, TradingDecisionType
    from features.leadership_zmom import LeadershipZMom
    from performance.trade_logger import TradeLogger, TradeRecord
    from core.score_calculator import get_score_calculator, ScoreResult
    INTEGRATION_COMPONENTS_AVAILABLE = True
except ImportError as e:
    INTEGRATION_COMPONENTS_AVAILABLE = False
    logger = get_logger(__name__)
    logger.warning(f"⚠️ Composants d'intégration non disponibles: {e}")

logger = get_logger(__name__)

class PipelineStage(Enum):
    """Étapes du pipeline intégré"""
    DATA_INTAKE = "data_intake"
    MENTHORQ_PROCESSING = "menthorq_processing"
    VIX_ANALYSIS = "vix_analysis"
    LEADERSHIP_FILTERING = "leadership_filtering"
    SCORE_CALCULATION = "score_calculation"
    TRADE_DECISION = "trade_decision"
    EXECUTION = "execution"
    LOGGING = "logging"

class IntegrationStatus(Enum):
    """Statut d'intégration"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"

@dataclass
class PipelineMetrics:
    """Métriques du pipeline intégré"""
    total_signals_processed: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    blocked_signals: int = 0
    avg_processing_time_ms: float = 0.0
    last_signal_time: Optional[datetime] = None
    uptime_seconds: float = 0.0
    error_count: int = 0

@dataclass
class IntegratedSignal:
    """Signal intégré avec tous les composants"""
    timestamp: datetime
    symbol: str
    signal_type: str
    raw_score: float
    final_score: float
    vix_regime: str
    vix_level: float
    leadership_gate: float
    staleness_quality: str
    processing_latency_ms: float
    decision_reasons: List[str] = field(default_factory=list)
    component_traces: Dict[str, Any] = field(default_factory=dict)

class PipelineIntegrator:
    """Intégrateur du pipeline de trading complet"""
    
    def __init__(self):
        """Initialisation de l'intégrateur de pipeline"""
        self.logger = get_logger(f"{__name__}.PipelineIntegrator")
        
        # État du pipeline
        self.status = IntegrationStatus.INITIALIZING
        self.start_time = datetime.now(timezone.utc)
        self.metrics = PipelineMetrics()
        
        # Composants intégrés
        self.components = {}
        self.component_status = {}
        
        # Pipeline de traitement
        self.processing_queue = deque(maxlen=1000)
        self.processed_signals = deque(maxlen=1000)
        
        # Threads de traitement
        self.processing_thread: Optional[threading.Thread] = None
        self.monitoring_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.stop_event = threading.Event()
        
        # Configuration
        self.config = None
        self.processing_interval_seconds = 1.0
        self.monitoring_interval_seconds = 30.0
        
        self.logger.info(f"🔗 PipelineIntegrator initialisé (components_available: {INTEGRATION_COMPONENTS_AVAILABLE})")
    
    def initialize_components(self) -> bool:
        """
        Initialise tous les composants du pipeline
        
        Returns:
            bool: True si tous les composants sont initialisés avec succès
        """
        try:
            self.logger.info("🔧 Initialisation des composants du pipeline...")
            
            # 1. Configuration MenthorQ
            self.components['menthorq_rules'] = get_menthorq_rules()
            self.component_status['menthorq_rules'] = self.components['menthorq_rules'] is not None
            self.logger.info(f"✅ Configuration MenthorQ: {self.component_status['menthorq_rules']}")
            
            # 2. Gestionnaire de staleness
            self.components['staleness_manager'] = get_staleness_manager()
            self.component_status['staleness_manager'] = True
            self.logger.info("✅ Gestionnaire de staleness initialisé")
            
            # 3. Moniteur de staleness
            self.components['staleness_monitor'] = get_menthorq_staleness_monitor()
            self.component_status['staleness_monitor'] = True
            self.logger.info("✅ Moniteur de staleness initialisé")
            
            # 4. Dashboard de monitoring des scores
            self.components['score_dashboard'] = get_score_monitoring_dashboard()
            self.component_status['score_dashboard'] = True
            self.logger.info("✅ Dashboard de scores initialisé")
            
            # 5. Tracker de latence d'exécution
            self.components['latency_tracker'] = get_execution_latency_tracker()
            self.component_status['latency_tracker'] = True
            self.logger.info("✅ Tracker de latence initialisé")
            
            # 6. Tracker du régime VIX
            self.components['vix_tracker'] = get_vix_regime_tracker()
            self.component_status['vix_tracker'] = True
            self.logger.info("✅ Tracker VIX initialisé")
            
            # 7. Filtre de leadership amélioré
            self.components['leadership_filter'] = LeadershipZMom()
            self.component_status['leadership_filter'] = True
            self.logger.info("✅ Filtre de leadership initialisé")
            
            # 8. Trade logger enrichi
            self.components['trade_logger'] = TradeLogger()
            self.component_status['trade_logger'] = True
            self.logger.info("✅ Trade logger initialisé")
            
            # 9. Calculateur de scores
            self.components['score_calculator'] = get_score_calculator()
            self.component_status['score_calculator'] = True
            self.logger.info("✅ Calculateur de scores initialisé")
            
            # Vérifier que tous les composants sont initialisés
            all_initialized = all(self.component_status.values())
            
            if all_initialized:
                self.status = IntegrationStatus.RUNNING
                self.logger.info("🎉 Tous les composants initialisés avec succès!")
            else:
                self.status = IntegrationStatus.ERROR
                failed_components = [name for name, status in self.component_status.items() if not status]
                self.logger.error(f"❌ Composants non initialisés: {failed_components}")
            
            return all_initialized
            
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation composants: {e}")
            self.status = IntegrationStatus.ERROR
            return False
    
    def start_pipeline(self) -> bool:
        """
        Démarre le pipeline intégré
        
        Returns:
            bool: True si démarré avec succès
        """
        if not self.initialize_components():
            self.logger.error("❌ Impossible de démarrer le pipeline - composants non initialisés")
            return False
        
        try:
            self.is_running = True
            self.stop_event.clear()
            
            # Démarrer le thread de traitement
            self.processing_thread = threading.Thread(
                target=self._processing_loop,
                daemon=True,
                name="PipelineProcessing"
            )
            self.processing_thread.start()
            
            # Démarrer le thread de monitoring
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True,
                name="PipelineMonitoring"
            )
            self.monitoring_thread.start()
            
            # Démarrer les moniteurs des composants
            self._start_component_monitors()
            
            self.logger.info("🚀 Pipeline intégré démarré avec succès!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage pipeline: {e}")
            self.is_running = False
            return False
    
    def stop_pipeline(self) -> None:
        """Arrête le pipeline intégré"""
        self.logger.info("🛑 Arrêt du pipeline intégré...")
        
        self.is_running = False
        self.stop_event.set()
        
        # Arrêter les threads
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5.0)
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)
        
        # Arrêter les moniteurs des composants
        self._stop_component_monitors()
        
        self.status = IntegrationStatus.STOPPED
        self.logger.info("✅ Pipeline intégré arrêté")
    
    def _start_component_monitors(self) -> None:
        """Démarre les moniteurs des composants"""
        try:
            # Démarrer le moniteur de staleness
            if 'staleness_monitor' in self.components:
                self.components['staleness_monitor'].start_monitoring()
            
            # Démarrer le tracker de latence
            if 'latency_tracker' in self.components:
                self.components['latency_tracker'].start_monitoring(check_interval_seconds=60)
            
            # Démarrer le tracker VIX
            if 'vix_tracker' in self.components:
                self.components['vix_tracker'].start_monitoring(check_interval_seconds=60)
            
            self.logger.info("✅ Moniteurs des composants démarrés")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage moniteurs: {e}")
    
    def _stop_component_monitors(self) -> None:
        """Arrête les moniteurs des composants"""
        try:
            # Arrêter le moniteur de staleness
            if 'staleness_monitor' in self.components:
                self.components['staleness_monitor'].stop_monitoring()
            
            # Arrêter le tracker de latence
            if 'latency_tracker' in self.components:
                self.components['latency_tracker'].stop_monitoring()
            
            # Arrêter le tracker VIX
            if 'vix_tracker' in self.components:
                self.components['vix_tracker'].stop_monitoring()
            
            self.logger.info("✅ Moniteurs des composants arrêtés")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur arrêt moniteurs: {e}")
    
    def _processing_loop(self) -> None:
        """Boucle principale de traitement du pipeline"""
        self.logger.info("🔄 Boucle de traitement du pipeline démarrée")
        
        while self.is_running and not self.stop_event.is_set():
            try:
                # Traiter les signaux en attente
                self._process_pending_signals()
                
                # Attendre avant le prochain cycle
                self.stop_event.wait(self.processing_interval_seconds)
                
            except Exception as e:
                self.logger.error(f"❌ Erreur dans la boucle de traitement: {e}")
                self.metrics.error_count += 1
                time.sleep(5)
        
        self.logger.info("🔄 Boucle de traitement du pipeline terminée")
    
    def _monitoring_loop(self) -> None:
        """Boucle de monitoring du pipeline"""
        self.logger.info("🔄 Boucle de monitoring du pipeline démarrée")
        
        while self.is_running and not self.stop_event.is_set():
            try:
                # Mettre à jour les métriques
                self._update_pipeline_metrics()
                
                # Vérifier la santé des composants
                self._check_component_health()
                
                # Attendre avant le prochain cycle
                self.stop_event.wait(self.monitoring_interval_seconds)
                
            except Exception as e:
                self.logger.error(f"❌ Erreur dans la boucle de monitoring: {e}")
                time.sleep(5)
        
        self.logger.info("🔄 Boucle de monitoring du pipeline terminée")
    
    def _process_pending_signals(self) -> None:
        """Traite les signaux en attente"""
        if not self.processing_queue:
            return
        
        # Traiter un signal à la fois
        signal_data = self.processing_queue.popleft()
        
        try:
            # Démarrer le tracking de latence
            pipeline_id = self.components['latency_tracker'].start_pipeline(
                signal_type=signal_data.get('signal_type'),
                symbol=signal_data.get('symbol')
            )
            
            # Traiter le signal à travers le pipeline
            integrated_signal = self._process_signal_through_pipeline(signal_data, pipeline_id)
            
            # Ajouter au pipeline des signaux traités
            self.processed_signals.append(integrated_signal)
            
            # Mettre à jour les métriques
            self.metrics.total_signals_processed += 1
            self.metrics.last_signal_time = datetime.now(timezone.utc)
            
            self.logger.debug(f"✅ Signal traité: {integrated_signal.symbol} - Score: {integrated_signal.final_score:.3f}")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur traitement signal: {e}")
            self.metrics.error_count += 1
    
    def _process_signal_through_pipeline(self, signal_data: Dict[str, Any], pipeline_id: str) -> IntegratedSignal:
        """Traite un signal à travers le pipeline complet"""
        start_time = datetime.now(timezone.utc)
        
        # 1. MenthorQ Processing
        self.components['latency_tracker'].start_stage(LatencyStage.MENTHORQ_PROCESSING)
        menthorq_data = self._process_menthorq_data(signal_data)
        self.components['latency_tracker'].end_stage(LatencyStage.MENTHORQ_PROCESSING)
        
        # 2. VIX Analysis
        self.components['latency_tracker'].start_stage(LatencyStage.VIX_REGIME_CHECK)
        vix_data = self._analyze_vix_regime(signal_data)
        self.components['latency_tracker'].end_stage(LatencyStage.VIX_REGIME_CHECK)
        
        # 3. Leadership Filtering
        self.components['latency_tracker'].start_stage(LatencyStage.LEADERSHIP_FILTER)
        leadership_result = self._apply_leadership_filter(signal_data, vix_data)
        self.components['latency_tracker'].end_stage(LatencyStage.LEADERSHIP_FILTER)
        
        # 4. Score Calculation
        self.components['latency_tracker'].start_stage(LatencyStage.SCORE_CALCULATION)
        score_result = self._calculate_integrated_score(menthorq_data, vix_data, signal_data)
        self.components['latency_tracker'].end_stage(LatencyStage.SCORE_CALCULATION)
        
        # 5. Trade Decision
        self.components['latency_tracker'].start_stage(LatencyStage.TRADE_DECISION)
        decision_result = self._make_trade_decision(score_result, leadership_result, vix_data)
        self.components['latency_tracker'].end_stage(LatencyStage.TRADE_DECISION)
        
        # 6. Logging
        self.components['latency_tracker'].start_stage(LatencyStage.LOGGING)
        self._log_integrated_trade(decision_result, score_result, vix_data)
        self.components['latency_tracker'].end_stage(LatencyStage.LOGGING)
        
        # Terminer le pipeline de latence
        pipeline_result = self.components['latency_tracker'].end_pipeline(success=True)
        
        # Créer le signal intégré
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        integrated_signal = IntegratedSignal(
            timestamp=start_time,
            symbol=signal_data.get('symbol', 'UNKNOWN'),
            signal_type=signal_data.get('signal_type', 'UNKNOWN'),
            raw_score=signal_data.get('raw_score', 0.0),
            final_score=score_result.final_score if score_result else 0.0,
            vix_regime=vix_data.get('regime', 'normal'),
            vix_level=vix_data.get('level', 20.0),
            leadership_gate=leadership_result.get('gate', 0.0),
            staleness_quality=menthorq_data.get('staleness_quality', 'unknown'),
            processing_latency_ms=processing_time,
            decision_reasons=decision_result.get('reasons', []),
            component_traces={
                'menthorq': menthorq_data,
                'vix': vix_data,
                'leadership': leadership_result,
                'score': score_result.__dict__ if score_result else {},
                'decision': decision_result
            }
        )
        
        return integrated_signal
    
    def _process_menthorq_data(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Traite les données MenthorQ"""
        # Simuler le traitement MenthorQ
        return {
            'gamma_levels': signal_data.get('gamma_levels', {}),
            'blind_spots': signal_data.get('blind_spots', {}),
            'swing_levels': signal_data.get('swing_levels', {}),
            'staleness_quality': 'good',
            'dealers_bias': signal_data.get('dealers_bias', 0.0)
        }
    
    def _analyze_vix_regime(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse le régime VIX"""
        vix_level = signal_data.get('vix_level', 20.0)
        
        # Mettre à jour le tracker VIX
        vix_snapshot = self.components['vix_tracker'].update_vix_level(vix_level)
        
        return {
            'level': vix_level,
            'regime': vix_snapshot.regime.value,
            'trend': vix_snapshot.volatility_trend,
            'change_percent': vix_snapshot.change_percent
        }
    
    def _apply_leadership_filter(self, signal_data: Dict[str, Any], vix_data: Dict[str, Any]) -> Dict[str, Any]:
        """Applique le filtre de leadership"""
        signal_score = signal_data.get('raw_score', 0.0)
        leadership_gate = signal_data.get('leadership_gate', 0.5)
        leader = signal_data.get('leader', 'ES')
        leader_trend = signal_data.get('leader_trend', 0.0)
        
        # Appliquer le filtre de leadership amélioré
        filter_result = self.components['leadership_filter'].filter_signal(
            signal_score=signal_score,
            leadership_gate=leadership_gate,
            leader=leader,
            leader_trend=leader_trend,
            vix_level=vix_data['level'],
            vix_regime=vix_data['regime']
        )
        
        return {
            'is_blocked': filter_result.is_blocked,
            'gate': leadership_gate,
            'reason': filter_result.block_reason.value if filter_result.block_reason else None,
            'message': filter_result.block_message
        }
    
    def _calculate_integrated_score(self, menthorq_data: Dict[str, Any], vix_data: Dict[str, Any], signal_data: Dict[str, Any]) -> Optional[ScoreResult]:
        """Calcule le score intégré"""
        try:
            # Préparer les données pour le calculateur de scores
            battle_navale_data = {
                'confluence': signal_data.get('confluence', 0.5),
                'volume_profile': signal_data.get('volume_profile', {}),
                'vwap_position': signal_data.get('vwap_position', 0.5)
            }
            
            # Calculer le score
            score_result = self.components['score_calculator'].calculate_trading_score(
                menthorq_data=menthorq_data,
                battle_navale_data=battle_navale_data,
                vix_data=vix_data
            )
            
            # Ajouter au dashboard de monitoring
            self.components['score_dashboard'].add_score_result(score_result)
            
            return score_result
            
        except Exception as e:
            self.logger.error(f"❌ Erreur calcul score: {e}")
            return None
    
    def _make_trade_decision(self, score_result: Optional[ScoreResult], leadership_result: Dict[str, Any], vix_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prend une décision de trading"""
        reasons = []
        
        if not score_result:
            reasons.append("Score calculation failed")
            return {'action': 'REJECT', 'reasons': reasons}
        
        if leadership_result.get('is_blocked', False):
            reasons.append(f"Leadership filter: {leadership_result.get('reason', 'unknown')}")
            return {'action': 'REJECT', 'reasons': reasons}
        
        if score_result.final_score < 0.6:
            reasons.append(f"Score too low: {score_result.final_score:.3f}")
            return {'action': 'REJECT', 'reasons': reasons}
        
        if vix_data['regime'] == 'extreme':
            reasons.append("VIX regime too extreme")
            return {'action': 'REJECT', 'reasons': reasons}
        
        reasons.append(f"Score acceptable: {score_result.final_score:.3f}")
        reasons.append(f"VIX regime: {vix_data['regime']}")
        
        return {'action': 'ACCEPT', 'reasons': reasons}
    
    def _log_integrated_trade(self, decision_result: Dict[str, Any], score_result: Optional[ScoreResult], vix_data: Dict[str, Any]) -> None:
        """Enregistre le trade intégré"""
        try:
            # Enregistrer la décision de trading
            decision_type = TradingDecisionType.SIGNAL_GENERATED if decision_result['action'] == 'ACCEPT' else TradingDecisionType.SIGNAL_BLOCKED
            outcome = 'success' if decision_result['action'] == 'ACCEPT' else 'failure'
            
            self.components['vix_tracker'].record_trading_decision(
                decision_type=decision_type,
                outcome=outcome,
                vix_impact=0.5,  # Impact moyen
                context={'reasons': decision_result['reasons']}
            )
            
            # Enregistrer le trade enrichi
            if decision_result['action'] == 'ACCEPT' and score_result:
                trade_data = {
                    'symbol': 'ESZ5',
                    'action': 'ENTRY',
                    'side': 'LONG',
                    'price': 4500.0,
                    'quantity': 1,
                    'final_score': score_result.final_score,
                    'score_components': [comp.__dict__ for comp in score_result.components],
                    'vix_level': vix_data['level'],
                    'vix_regime': vix_data['regime'],
                    'decision_reasons': decision_result['reasons'],
                    'calculation_latency_ms': 50.0
                }
                
                self.components['trade_logger'].log_trade(trade_data)
            
        except Exception as e:
            self.logger.error(f"❌ Erreur logging trade: {e}")
    
    def _update_pipeline_metrics(self) -> None:
        """Met à jour les métriques du pipeline"""
        self.metrics.uptime_seconds = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        
        # Calculer le temps de traitement moyen
        if self.processed_signals:
            recent_signals = list(self.processed_signals)[-10:]
            avg_latency = sum(s.processing_latency_ms for s in recent_signals) / len(recent_signals)
            self.metrics.avg_processing_time_ms = avg_latency
    
    def _check_component_health(self) -> None:
        """Vérifie la santé des composants"""
        for component_name, component in self.components.items():
            try:
                # Vérifications basiques selon le composant
                if hasattr(component, 'is_monitoring'):
                    if not component.is_monitoring:
                        self.logger.warning(f"⚠️ Composant {component_name} n'est pas en monitoring")
                
                if hasattr(component, 'get_status'):
                    status = component.get_status()
                    if not status.get('healthy', True):
                        self.logger.warning(f"⚠️ Composant {component_name} en mauvaise santé")
                        
            except Exception as e:
                self.logger.error(f"❌ Erreur vérification santé {component_name}: {e}")
    
    def add_signal(self, signal_data: Dict[str, Any]) -> bool:
        """
        Ajoute un signal au pipeline de traitement
        
        Args:
            signal_data: Données du signal
            
        Returns:
            bool: True si ajouté avec succès
        """
        try:
            self.processing_queue.append(signal_data)
            self.logger.debug(f"📊 Signal ajouté au pipeline: {signal_data.get('symbol', 'UNKNOWN')}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erreur ajout signal: {e}")
            return False
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Retourne le statut du pipeline"""
        return {
            'status': self.status.value,
            'is_running': self.is_running,
            'uptime_seconds': self.metrics.uptime_seconds,
            'total_signals_processed': self.metrics.total_signals_processed,
            'successful_trades': self.metrics.successful_trades,
            'failed_trades': self.metrics.failed_trades,
            'blocked_signals': self.metrics.blocked_signals,
            'avg_processing_time_ms': self.metrics.avg_processing_time_ms,
            'error_count': self.metrics.error_count,
            'queue_size': len(self.processing_queue),
            'processed_signals_count': len(self.processed_signals),
            'component_status': self.component_status,
            'last_signal_time': self.metrics.last_signal_time.isoformat() if self.metrics.last_signal_time else None
        }
    
    def get_component_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques des composants"""
        metrics = {}
        
        try:
            # Métriques du dashboard de scores
            if 'score_dashboard' in self.components:
                metrics['score_dashboard'] = self.components['score_dashboard'].get_dashboard_summary()
            
            # Métriques du tracker de latence
            if 'latency_tracker' in self.components:
                metrics['latency_tracker'] = self.components['latency_tracker'].get_latency_summary()
            
            # Métriques du tracker VIX
            if 'vix_tracker' in self.components:
                metrics['vix_tracker'] = self.components['vix_tracker'].get_vix_summary()
            
            # Métriques du moniteur de staleness
            if 'staleness_monitor' in self.components:
                metrics['staleness_monitor'] = self.components['staleness_monitor'].get_monitoring_status()
            
        except Exception as e:
            self.logger.error(f"❌ Erreur récupération métriques composants: {e}")
        
        return metrics
    
    def export_pipeline_data(self, format: str = 'json') -> str:
        """Exporte les données du pipeline"""
        if format == 'json':
            data = {
                'pipeline_status': self.get_pipeline_status(),
                'component_metrics': self.get_component_metrics(),
                'recent_signals': [
                    {
                        'timestamp': signal.timestamp.isoformat(),
                        'symbol': signal.symbol,
                        'signal_type': signal.signal_type,
                        'final_score': signal.final_score,
                        'vix_regime': signal.vix_regime,
                        'processing_latency_ms': signal.processing_latency_ms,
                        'decision_reasons': signal.decision_reasons
                    }
                    for signal in list(self.processed_signals)[-10:]
                ],
                'export_timestamp': datetime.now(timezone.utc).isoformat()
            }
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Format d'export non supporté: {format}")

# Instance globale
_global_pipeline_integrator: Optional[PipelineIntegrator] = None

def get_pipeline_integrator() -> PipelineIntegrator:
    """Retourne l'instance globale de l'intégrateur de pipeline"""
    global _global_pipeline_integrator
    if _global_pipeline_integrator is None:
        _global_pipeline_integrator = PipelineIntegrator()
    return _global_pipeline_integrator

def create_pipeline_integrator() -> PipelineIntegrator:
    """Crée une nouvelle instance de l'intégrateur de pipeline"""
    return PipelineIntegrator()
