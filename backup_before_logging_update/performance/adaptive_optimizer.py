#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Adaptive Optimizer
🔄 AUTO-AMÉLIORATION du système de trading

Version: Phase 3B - Smart Adaptation Focus
Responsabilité: Optimisation automatique basée sur performance réelle

FONCTIONNALITÉS CRITIQUES :
1. 🎯 Monitoring Performance - Détection dégradation automatique
2. 🔄 Adaptive Parameters - Ajustement paramètres en temps réel
3. 🧪 A/B Testing - Test nouvelles configurations automatique
4. 🛡️ Safety First - Backup & rollback automatique
5. 📊 Evidence-Based - Optimisation basée données réelles
6. 🚨 Alert System - Notifications changements critiques

WORKFLOW ADAPTATION :
Monitor → Detect Issue → Generate Solution → A/B Test → Validate → Apply

PARAMÈTRES OPTIMISÉS :
- Feature weights (8D model)
- Stop distances (par régime)
- Confidence thresholds (patterns)
- Pattern sensitivity (Battle Navale)
- Position sizing (risk-based)

PHILOSOPHIE : "NEVER BREAK WHAT WORKS"
- Sauvegarde avant tout changement
- Rollback instantané si dégradation
- A/B testing obligatoire
- Evidence-based optimization only
"""

import os
import json
import time
import copy
import logging
import hashlib
import threading
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
from enum import Enum
import numpy as np
import statistics

# Local imports
from core.base_types import TradingSignal, TradeResult
from config.automation_config import get_automation_config
from performance.trade_logger import TradeLogger
from performance.performance_analyzer import PerformanceAnalyzer

logger = logging.getLogger(__name__)

# === OPTIMIZATION ENUMS ===


class AdaptationTrigger(Enum):
    """Déclencheurs d'adaptation"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    WIN_RATE_DROP = "win_rate_drop"
    CONSECUTIVE_LOSSES = "consecutive_losses"
    PROFIT_FACTOR_LOW = "profit_factor_low"
    SCHEDULE_ROUTINE = "schedule_routine"
    MANUAL_REQUEST = "manual_request"


class OptimizationStatus(Enum):
    """Status des optimisations"""
    MONITORING = "monitoring"
    ADAPTATION_NEEDED = "adaptation_needed"
    TESTING_PARAMETERS = "testing_parameters"
    VALIDATING_RESULTS = "validating_results"
    APPLYING_CHANGES = "applying_changes"
    ROLLING_BACK = "rolling_back"


class ParameterType(Enum):
    """Types de paramètres optimisables"""
    FEATURE_WEIGHTS = "feature_weights"
    STOP_DISTANCES = "stop_distances"
    CONFIDENCE_THRESHOLDS = "confidence_thresholds"
    PATTERN_SENSITIVITY = "pattern_sensitivity"
    POSITION_SIZING = "position_sizing"

# === OPTIMIZATION DATA STRUCTURES ===


@dataclass
class ParameterSet:
    """Ensemble de paramètres de trading"""
    feature_weights: Dict[str, float]
    stop_distances: Dict[str, float]
    confidence_thresholds: Dict[str, float]
    pattern_sensitivity: Dict[str, float]
    position_sizing: Dict[str, float]

    # Metadata
    created_at: datetime
    performance_score: float = 0.0
    trades_tested: int = 0
    win_rate: float = 0.0
    profit_factor: float = 0.0

    def to_hash(self) -> str:
        """Génération hash unique pour ce set de paramètres"""
        content = json.dumps(asdict(self), sort_keys=True, default=str)
        return hashlib.md5(content.encode()).hexdigest()[:8]


@dataclass
class ABTestResult:
    """Résultat d'un test A/B"""
    test_id: str
    control_params: ParameterSet
    test_params: ParameterSet

    # Results
    control_performance: Dict[str, float]
    test_performance: Dict[str, float]

    # Statistical significance
    is_significant: bool
    confidence_level: float
    improvement_percentage: float

    # Test details
    trades_per_group: int
    test_duration_hours: float
    test_completed: bool


class AdaptiveOptimizer:
    """
    ADAPTIVE OPTIMIZER - Auto-amélioration système

    Responsabilités :
    1. Monitoring performance continue
    2. Détection automatique besoin d'adaptation
    3. Génération paramètres optimisés
    4. A/B testing sécurisé
    5. Application changements si prouvés
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialisation Adaptive Optimizer

        Args:
            config: Configuration optionnelle
        """
        self.config = config or get_automation_config()

        # Storage paths
        self.base_path = Path("data/performance/optimization")
        self.backup_path = self.base_path / "backups"
        self.results_path = self.base_path / "results"

        # Création directories
        for path in [self.base_path, self.backup_path, self.results_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Performance thresholds
        self.performance_threshold = 0.65      # Win rate minimum
        self.adaptation_frequency = 100        # Trades avant check
        self.min_improvement_threshold = 0.02  # 2% amélioration minimum
        self.max_parameter_change = 0.1        # 10% changement max par fois

        # A/B Testing config
        self.ab_test_allocation = 0.3          # 30% nouvelles paramètres
        self.ab_test_min_trades = 50           # Trades minimum par groupe
        self.ab_test_max_duration = 24         # Heures maximum test

        # Current state
        self.current_params: Optional[ParameterSet] = None
        self.backup_params: Optional[ParameterSet] = None
        self.status = OptimizationStatus.MONITORING

        # Active A/B test
        self.active_ab_test: Optional[ABTestResult] = None
        self.ab_test_trades_control = deque(maxlen=200)
        self.ab_test_trades_test = deque(maxlen=200)

        # Performance tracking
        self.recent_trades = deque(maxlen=self.adaptation_frequency)
        self.performance_history = deque(maxlen=1000)
        self.consecutive_losses = 0
        self.last_adaptation_time = None

        # Threading
        self.monitoring_thread = None
        self.is_monitoring = False

        # Components integration
        self.trade_logger: Optional[TradeLogger] = None
        self.performance_analyzer: Optional[PerformanceAnalyzer] = None

        self._initialize_default_parameters()
        self._start_monitoring()

        logger.info(f"AdaptiveOptimizer initialisé: {self.base_path}")

    def should_adapt(self) -> Tuple[bool, AdaptationTrigger]:
        """
        DÉTERMINE SI ADAPTATION NÉCESSAIRE

        Vérifie :
        - Performance récente vs seuil
        - Tendance dégradation
        - Nombre trades depuis dernière adaptation

        Returns:
            Tuple: (besoin_adaptation, raison)
        """
        try:
            if len(self.recent_trades) < self.adaptation_frequency:
                return False, None

            # Calcul performance récente
            recent_performance = self._calculate_recent_performance()

            # Check 1: Win rate en dessous du seuil
            if recent_performance['win_rate'] < self.performance_threshold:
                logger.warning(f"Win rate faible: {recent_performance['win_rate']:.1%}")
                return True, AdaptationTrigger.WIN_RATE_DROP

            # Check 2: Profit factor insuffisant
            if recent_performance['profit_factor'] < 1.2:
                logger.warning(f"Profit factor faible: {recent_performance['profit_factor']:.2f}")
                return True, AdaptationTrigger.PROFIT_FACTOR_LOW

            # Check 3: Série de pertes consécutives
            if self.consecutive_losses >= 5:
                logger.warning(f"Série de pertes: {self.consecutive_losses}")
                return True, AdaptationTrigger.CONSECUTIVE_LOSSES

            # Check 4: Dégradation tendance
            if self._detect_performance_degradation():
                logger.warning("Tendance de dégradation détectée")
                return True, AdaptationTrigger.PERFORMANCE_DEGRADATION

            # Check 5: Adaptation routinière
            if self._should_routine_adaptation():
                logger.info("Adaptation routinière programmée")
                return True, AdaptationTrigger.SCHEDULE_ROUTINE

            return False, None

        except Exception as e:
            logger.error(f"Erreur should_adapt: {e}")
            return False, None

    def optimize_parameters(self) -> ParameterSet:
        """
        OPTIMISATION AUTOMATIQUE PARAMÈTRES

        Optimise automatiquement :
        - Feature weights (8D model)
        - Stop distances (par régime)
        - Confidence thresholds (patterns)
        - Pattern sensitivity (Battle Navale)

        Returns:
            ParameterSet: Nouveaux paramètres optimisés
        """
        try:
            logger.info("Génération paramètres optimisés...")

            # Backup paramètres actuels
            self.backup_working_config()

            # Analyse performance pour optimisation
            performance_analysis = self._analyze_performance_for_optimization()

            # Génération nouveaux paramètres
            new_params = copy.deepcopy(self.current_params)

            # 1. Optimisation Feature Weights
            if 'feature_effectiveness' in performance_analysis:
                new_params.feature_weights = self._optimize_feature_weights(
                    performance_analysis['feature_effectiveness']
                )

            # 2. Optimisation Stop Distances
            if 'risk_analysis' in performance_analysis:
                new_params.stop_distances = self._optimize_stop_distances(
                    performance_analysis['risk_analysis']
                )

            # 3. Optimisation Confidence Thresholds
            if 'pattern_performance' in performance_analysis:
                new_params.confidence_thresholds = self._optimize_confidence_thresholds(
                    performance_analysis['pattern_performance']
                )

            # 4. Optimisation Pattern Sensitivity
            new_params.pattern_sensitivity = self._optimize_pattern_sensitivity(
                performance_analysis
            )

            # Update metadata
            new_params.created_at = datetime.now(timezone.utc)

            logger.info(f"Paramètres optimisés générés: {new_params.to_hash()}")
            return new_params

        except Exception as e:
            logger.error(f"Erreur optimize_parameters: {e}")
            return self.current_params

    def a_b_test_modifications(self, new_params: ParameterSet) -> str:
        """
        TEST A/B AUTOMATIQUE

        Test A/B automatique :
        - 70% trades avec paramètres actuels (contrôle)
        - 30% trades avec paramètres optimisés (test)
        - Switch si amélioration statistiquement significative

        Args:
            new_params: Nouveaux paramètres à tester

        Returns:
            str: ID du test A/B
        """
        try:
            if self.active_ab_test and not self.active_ab_test.test_completed:
                logger.warning("Test A/B déjà en cours")
                return self.active_ab_test.test_id

            # Génération ID test
            test_id = f"ab_test_{int(time.time())}"

            # Initialisation test A/B
            self.active_ab_test = ABTestResult(
                test_id=test_id,
                control_params=copy.deepcopy(self.current_params),
                test_params=new_params,
                control_performance={},
                test_performance={},
                is_significant=False,
                confidence_level=0.0,
                improvement_percentage=0.0,
                trades_per_group=0,
                test_duration_hours=0.0,
                test_completed=False
            )

            # Clear previous test data
            self.ab_test_trades_control.clear()
            self.ab_test_trades_test.clear()

            # Update status
            self.status = OptimizationStatus.TESTING_PARAMETERS

            logger.info(f"Test A/B démarré: {test_id}")
            logger.info(f"Contrôle: {self.current_params.to_hash()}")
            logger.info(f"Test: {new_params.to_hash()}")

            return test_id

        except Exception as e:
            logger.error(f"Erreur a_b_test_modifications: {e}")
            return None

    def backup_working_config(self) -> bool:
        """
        SAUVEGARDE CONFIG QUI MARCHE

        Sauvegarde configuration actuelle avant modification
        Permet rollback instantané si problème

        Returns:
            bool: Succès de la sauvegarde
        """
        try:
            if not self.current_params:
                logger.warning("Pas de paramètres actuels à sauvegarder")
                return False

            # Création backup
            self.backup_params = copy.deepcopy(self.current_params)

            # Sauvegarde sur disque
            backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = self.backup_path / backup_filename

            backup_data = {
                'params': asdict(self.backup_params),
                'backup_time': datetime.now(timezone.utc).isoformat(),
                'reason': 'pre_optimization_backup'
            }

            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, default=str)

            logger.info(f"Configuration sauvegardée: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Erreur backup_working_config: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Status actuel de l'optimizer"""
        status_data = {
            'status': self.status.value,
            'current_params_hash': self.current_params.to_hash() if self.current_params else None,
            'recent_trades_count': len(self.recent_trades),
            'consecutive_losses': self.consecutive_losses,
            'last_adaptation': self.last_adaptation_time.isoformat() if self.last_adaptation_time else None,
            'active_ab_test': None
        }

        if self.active_ab_test:
            status_data['active_ab_test'] = {
                'test_id': self.active_ab_test.test_id,
                'control_trades': len(self.ab_test_trades_control),
                'test_trades': len(self.ab_test_trades_test),
                'completed': self.active_ab_test.test_completed
            }

        return status_data

    # === PRIVATE METHODS ===

    def _initialize_default_parameters(self):
        """Initialisation paramètres par défaut"""
        self.current_params = ParameterSet(
            feature_weights={
                'vwap_trend_signal': 0.15,
                'sierra_pattern_strength': 0.15,
                'dow_trend_regime': 0.125,
                'gamma_levels_proximity': 0.125,
                'volume_profile_signal': 0.125,
                'level2_strength': 0.125,
                'momentum_shift': 0.1,
                'confluence_score': 0.125
            },
            stop_distances={
                'TREND': 6.0,
                'RANGE': 4.0,
                'BREAKOUT': 8.0
            },
            confidence_thresholds={
                'battle_navale': 0.65,
                'gamma_pin': 0.70,
                'confluence': 0.60
            },
            pattern_sensitivity={
                'base_quality_threshold': 0.6,
                'rouge_sous_verte_weight': 1.2,
                'confluence_boost': 1.15
            },
            position_sizing={
                'base_size': 1.0,
                'max_size': 3.0,
                'confidence_multiplier': 1.5
            },
            created_at=datetime.now(timezone.utc)
        )

    def _calculate_recent_performance(self) -> Dict[str, float]:
        """Calcul performance récente"""
        if not self.recent_trades:
            return {'win_rate': 0.0, 'profit_factor': 0.0, 'total_pnl': 0.0}

        profitable_trades = sum(1 for trade in self.recent_trades if trade.get('pnl', 0) > 0)
        total_pnl = sum(trade.get('pnl', 0) for trade in self.recent_trades)

        wins = [trade['pnl'] for trade in self.recent_trades if trade.get('pnl', 0) > 0]
        losses = [abs(trade['pnl']) for trade in self.recent_trades if trade.get('pnl', 0) < 0]

        win_rate = profitable_trades / len(self.recent_trades)

        if wins and losses:
            profit_factor = sum(wins) / sum(losses)
        else:
            profit_factor = float('inf') if wins else 0.0

        return {
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_pnl': total_pnl
        }

    def _start_monitoring(self):
        """Démarrage monitoring en arrière-plan"""
        if not self.monitoring_thread or not self.monitoring_thread.is_alive():
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_worker,
                daemon=True
            )
            self.monitoring_thread.start()

    def _monitoring_worker(self):
        """Worker thread pour monitoring performance"""
        while self.is_monitoring:
            try:
                # Check adaptation nécessaire
                need_adaptation, trigger = self.should_adapt()

                if need_adaptation and self.status == OptimizationStatus.MONITORING:
                    logger.info(f"Adaptation déclenchée: {trigger.value}")

                    # Génération paramètres optimisés
                    new_params = self.optimize_parameters()

                    # Démarrage A/B test
                    test_id = self.a_b_test_modifications(new_params)

                # Check A/B test en cours
                if self.active_ab_test and not self.active_ab_test.test_completed:
                    self._check_ab_test_completion()

                time.sleep(60)  # Check chaque minute

            except Exception as e:
                logger.error(f"Erreur monitoring worker: {e}")
                time.sleep(300)  # Pause plus longue en cas d'erreur

    # Stubs pour méthodes complexes
    def _detect_performance_degradation(self) -> bool:
        """Stub - Détection dégradation tendance"""
        return False

    def _should_routine_adaptation(self) -> bool:
        """Stub - Adaptation routinière"""
        return False

    def _analyze_performance_for_optimization(self) -> Dict[str, Any]:
        """Stub - Analyse performance pour optimisation"""
        return {}

    def _optimize_feature_weights(self, effectiveness_data: Dict) -> Dict[str, float]:
        """Stub - Optimisation poids features"""
        return self.current_params.feature_weights if self.current_params else {}

# === FACTORY FUNCTION ===


def create_adaptive_optimizer(config: Optional[Dict] = None) -> AdaptiveOptimizer:
    """Factory function pour AdaptiveOptimizer"""
    return AdaptiveOptimizer(config)

# === END MODULE ===
