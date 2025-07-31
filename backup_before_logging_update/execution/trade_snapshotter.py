"""
MIA_IA_SYSTEM - Trade Snapshotter
Capture obsessive de données pour chaque moment de trading
Version: Phase 3 - Data Collection Intensive
Performance: Capture <5ms, stockage async

RESPONSABILITÉS :
1. Snapshot PRE-ANALYSE (état marché complet)
2. Snapshot DÉCISION (processus Battle Navale)
3. Snapshot EXÉCUTION (détails ordre/remplissage)
4. Snapshot RÉSULTAT (outcome complet + métriques)
5. Préparation données ML (features engineering)

PHILOSOPHIE :
- CAPTURE TOUT (on ne sait jamais ce qui sera utile)
- QUALITÉ DONNÉES OBSESSIVE (validation systématique)
- ORGANISATION TEMPORELLE (facile à analyser)
- ML-READY (features pré-calculées)
"""

import time
import json
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timezone
import hashlib
import gzip

# Ajout de l'énumération TradingMode
class TradingMode(Enum):
    LIVE = "live"
    PAPER = "paper"
    BACKTEST = "backtest"

# Local imports
from core.base_types import (
    MarketData, OrderFlowData, TradingSignal, TradeResult,
    MarketRegime, SignalType, ES_TICK_SIZE, ES_TICK_VALUE
)
from config.automation_config import (
    get_automation_config, DataGranularity, AutomationMode
)

logger = logging.getLogger(__name__)

# === SNAPSHOT ENUMS ===


class SnapshotType(Enum):
    """Types de snapshots"""
    PRE_ANALYSIS = "pre_analysis"         # Avant analyse Battle Navale
    DECISION = "decision"                 # Processus décision
    EXECUTION = "execution"               # Exécution ordre
    POSITION_UPDATE = "position_update"   # Update position
    EXIT_SIGNAL = "exit_signal"          # Signal de sortie
    FINAL_RESULT = "final_result"        # Résultat final trade


class DataQuality(Enum):
    """Qualité des données"""
    EXCELLENT = "excellent"    # Données complètes, validées
    GOOD = "good"             # Données complètes, warnings mineurs
    ACCEPTABLE = "acceptable"  # Données utilisables, quelques manques
    POOR = "poor"             # Données incomplètes
    INVALID = "invalid"       # Données corrompues

# === SNAPSHOT DATA STRUCTURES ===


@dataclass
class MarketSnapshot:
    """Snapshot état marché complet"""
    timestamp: datetime
    symbol: str

    # OHLC data
    open: float
    high: float
    low: float
    close: float
    volume: int

    # Session context
    session_phase: str                    # OPEN/MID/CLOSE
    session_high: float
    session_low: float
    session_volume: int
    time_since_open_minutes: int

    # Volatility context
    atr_14: float                        # Average True Range
    realized_volatility: float           # Volatilité réalisée
    volatility_regime: str               # LOW/NORMAL/HIGH

    # Market structure
    trend_direction: str                 # UP/DOWN/SIDEWAYS
    trend_strength: float                # 0-1
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None

    def validate(self) -> Tuple[bool, List[str]]:
        """Validation données marché"""
        issues = []

        if self.high < self.low:
            issues.append("High < Low invalide")
        if not (self.low <= self.close <= self.high):
            issues.append("Close hors range High/Low")
        if self.volume < 0:
            issues.append("Volume négatif")
        if self.atr_14 < 0:
            issues.append("ATR négatif")

        return len(issues) == 0, issues


@dataclass
class BattleNavaleSnapshot:
    """Snapshot analyse Battle Navale"""
    timestamp: datetime

    # Signal principal
    battle_navale_signal: float          # 0-1
    signal_confidence: float             # 0-1
    signal_direction: str                # LONG/SHORT/NEUTRAL

    # Composants Battle Navale
    boules_vertes_count: int
    boules_rouges_count: int
    base_quality_score: float           # 0-1
    rouge_sous_verte_status: bool       # Règle d'or

    # Confluence analysis
    confluence_score: float             # 0-1
    confluence_components: Dict[str, float]  # Détail confluence

    # Features snapshot (vos 8 features)
    vwap_trend_signal: float
    sierra_pattern_strength: float
    dow_trend_regime: float
    gamma_levels_proximity: float
    level_proximity: float
    es_nq_correlation: float
    volume_confirmation: float
    options_flow_bias: float

    # Decision logic
    decision_reasoning: str              # Explication décision
    filters_passed: List[str]           # Filtres passés
    filters_failed: List[str]           # Filtres échoués


@dataclass
class ExecutionSnapshot:
    """Snapshot exécution ordre"""
    timestamp: datetime

    # Order details
    order_id: str
    order_type: str                     # MKT/LMT/STP
    side: str                          # BUY/SELL
    quantity: float
    price_requested: Optional[float]    # Prix demandé (si LMT)

    # Execution details
    price_filled: Optional[float]       # Prix rempli
    quantity_filled: float             # Quantité remplie
    execution_time_ms: float           # Temps exécution
    slippage_ticks: float              # Slippage en ticks

    # Market conditions at execution
    bid_price: float
    ask_price: float
    spread_ticks: float
    market_impact: float               # Impact sur le marché

    # Risk management
    stop_loss_price: Optional[float]
    take_profit_price: Optional[float]
    risk_reward_ratio: Optional[float]
    max_risk_dollars: float


@dataclass
class PositionSnapshot:
    """Snapshot position en cours"""
    timestamp: datetime

    # Position details
    symbol: str
    side: str                          # LONG/SHORT
    quantity: float
    entry_price: float
    current_price: float

    # P&L tracking
    unrealized_pnl: float
    unrealized_pnl_percent: float
    max_favorable_excursion: float     # MFE
    max_adverse_excursion: float       # MAE

    # Time tracking
    entry_time: datetime
    time_in_position_minutes: int

    # Risk monitoring
    distance_to_stop: float            # Ticks
    distance_to_target: float          # Ticks
    current_risk_reward: float


@dataclass
class TradeResultSnapshot:
    """Snapshot résultat final trade"""
    timestamp: datetime

    # Trade identification
    trade_id: str
    symbol: str

    # Basic trade data
    entry_price: float
    exit_price: float
    quantity: float
    side: str

    # Financial results
    gross_pnl: float
    net_pnl: float
    commission: float
    slippage_cost: float

    # Performance metrics
    return_percent: float
    risk_reward_achieved: float
    holding_time_minutes: int

    # Quality metrics
    execution_quality_score: float     # 0-1
    strategy_adherence_score: float    # 0-1

    # Market conditions
    entry_market_condition: str
    exit_market_condition: str
    volatility_during_trade: float

# === MAIN SNAPSHOTTER CLASS ===


class TradeSnapshotter:
    """Capture obsessive données trading"""

    def __init__(self):
        self.config = get_automation_config()
        self.snapshots: Dict[str, List[Dict]] = {
            'pre_analysis': [],
            'decisions': [],
            'executions': [],
            'positions': [],
            'results': []
        }

        # Stockage
        self.base_path = Path(self.config.snapshots_directory)
        self.ensure_directories()

        # Tracking
        self.current_trade_id: Optional[str] = None
        self.active_snapshots: Dict[str, Dict] = {}

        # Performance
        self.capture_stats = {
            'total_snapshots': 0,
            'avg_capture_time_ms': 0.0,
            'data_quality_scores': []
        }

        logger.info("TradeSnapshotter initialisé avec stockage obsessif")

    def ensure_directories(self):
        """Création structure dossiers"""
        directories = [
            self.base_path,
            self.base_path / "daily",
            self.base_path / "weekly",
            self.base_path / "archive",
            self.base_path / "ml_ready",
            self.base_path / "backups"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def generate_trade_id(self) -> str:
        """Génération ID trade unique"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"TRADE_{timestamp}_{unique_id}"

    def capture_pre_analysis_snapshot(self,
                                      market_data: MarketData,
                                      order_flow: Optional[OrderFlowData] = None) -> str:
        """
        SNAPSHOT PRE-ANALYSE
        Capture état complet avant analyse Battle Navale
        """
        start_time = time.perf_counter()

        try:
            # Generate new trade ID
            trade_id = self.generate_trade_id()
            self.current_trade_id = trade_id

            # Market snapshot
            market_snapshot = MarketSnapshot(
                timestamp=market_data.timestamp,
                symbol=market_data.symbol,
                open=market_data.open,
                high=market_data.high,
                low=market_data.low,
                close=market_data.close,
                volume=market_data.volume,
                session_phase=self._determine_session_phase(market_data.timestamp),
                session_high=market_data.high,  # Simplifiée
                session_low=market_data.low,    # Simplifiée
                session_volume=market_data.volume,
                time_since_open_minutes=self._calculate_time_since_open(market_data.timestamp),
                atr_14=self._calculate_atr(market_data),
                realized_volatility=self._calculate_realized_vol(market_data),
                volatility_regime=self._determine_vol_regime(market_data),
                trend_direction=self._determine_trend_direction(market_data),
                trend_strength=self._calculate_trend_strength(market_data)
            )

            # Validation
            is_valid, issues = market_snapshot.validate()

            # Complete snapshot
            complete_snapshot = {
                'snapshot_id': f"{trade_id}_PRE",
                'trade_id': trade_id,
                'snapshot_type': SnapshotType.PRE_ANALYSIS.value,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'capture_time_ms': 0.0,  # Calculé à la fin

                # Data
                'market_data': asdict(market_snapshot),
                'order_flow_data': asdict(order_flow) if order_flow else None,

                # Quality
                'data_quality': DataQuality.EXCELLENT.value if is_valid else DataQuality.POOR.value,
                'data_quality': DataQuality.EXCELLENT.value if is_valid else DataQuality.POOR.value,
                'quality_issues': issues,

                # Context
                'automation_mode': self.config.trading.automation_mode.value,
                'environment': self.config.environment
            }

            # Calcul temps capture
            capture_time = (time.perf_counter() - start_time) * 1000
            complete_snapshot['capture_time_ms'] = capture_time

            # Stockage
            self.snapshots['pre_analysis'].append(complete_snapshot)
            self.active_snapshots[trade_id] = complete_snapshot

            # Stats
            self._update_capture_stats(capture_time)

            logger.debug(f"Pre-analysis snapshot capturé: {trade_id} ({capture_time:.2f}ms)")

            return trade_id

        except Exception as e:
            logger.error(f"Erreur capture pre-analysis snapshot: {e}")
            return ""

    def capture_decision_snapshot(self,
                                  trade_id: str,
                                  battle_navale_result: Dict[str, Any],
                                  features: Dict[str, float],
                                  signal: Optional[TradingSignal] = None) -> bool:
        """
        SNAPSHOT DÉCISION
        Capture processus décision Battle Navale complet
        """
        start_time = time.perf_counter()

        try:
            if trade_id not in self.active_snapshots:
                logger.error(f"Trade ID {trade_id} non trouvé pour decision snapshot")
                return False

            # Battle Navale snapshot
            bn_snapshot = BattleNavaleSnapshot(
                timestamp=datetime.now(timezone.utc),
                battle_navale_signal=battle_navale_result.get('signal_strength', 0.0),
                signal_confidence=battle_navale_result.get('confidence', 0.0),
                signal_direction=battle_navale_result.get('direction', 'NEUTRAL'),
                boules_vertes_count=battle_navale_result.get('boules_vertes', 0),
                boules_rouges_count=battle_navale_result.get('boules_rouges', 0),
                base_quality_score=battle_navale_result.get('base_quality', 0.0),
                rouge_sous_verte_status=battle_navale_result.get('rouge_sous_verte', False),
                confluence_score=battle_navale_result.get('confluence_score', 0.0),
                confluence_components=battle_navale_result.get('confluence_details', {}),

                # Features (vos 8 features)
                vwap_trend_signal=features.get('vwap_trend_signal', 0.5),
                sierra_pattern_strength=features.get('sierra_pattern_strength', 0.5),
                dow_trend_regime=features.get('dow_trend_regime', 0.5),
                gamma_levels_proximity=features.get('gamma_levels_proximity', 0.5),
                level_proximity=features.get('level_proximity', 0.5),
                es_nq_correlation=features.get('es_nq_correlation', 0.5),
                volume_confirmation=features.get('volume_confirmation', 0.5),
                options_flow_bias=features.get('options_flow_bias', 0.5),

                decision_reasoning=battle_navale_result.get('reasoning', ''),
                filters_passed=battle_navale_result.get('filters_passed', []),
                filters_failed=battle_navale_result.get('filters_failed', [])
            )

            # Complete snapshot
            decision_snapshot = {
                'snapshot_id': f"{trade_id}_DECISION",
                'trade_id': trade_id,
                'snapshot_type': SnapshotType.DECISION.value,
                'timestamp': datetime.now(timezone.utc).isoformat(),

                # Battle Navale analysis
                'battle_navale_analysis': asdict(bn_snapshot),

                # Signal generated
                'signal_generated': asdict(signal) if signal else None,

                # Decision outcome
                'decision_outcome': {
                    'should_trade': signal is not None,
                    'trade_direction': signal.signal_type.value if signal else None,
                    'confidence_final': signal.confidence if signal else 0.0
                }
            }

            # Calcul temps
            capture_time = (time.perf_counter() - start_time) * 1000
            decision_snapshot['capture_time_ms'] = capture_time

            # Stockage
            self.snapshots['decisions'].append(decision_snapshot)
            self.active_snapshots[trade_id].update({'decision': decision_snapshot})

            logger.debug(f"Decision snapshot capturé: {trade_id} ({capture_time:.2f}ms)")

            return True

        except Exception as e:
            logger.error(f"Erreur capture decision snapshot: {e}")
            return False

    def capture_execution_snapshot(self,
                                   trade_id: str,
                                   order_details: Dict[str, Any],
                                   execution_result: Dict[str, Any]) -> bool:
        """
        SNAPSHOT EXÉCUTION
        Capture détails exécution ordre complets
        """
        start_time = time.perf_counter()

        try:
            # Execution snapshot
            exec_snapshot = ExecutionSnapshot(
                timestamp=datetime.now(timezone.utc),
                order_id=order_details.get('order_id', ''),
                order_type=order_details.get('order_type', 'MKT'),
                side=order_details.get('side', ''),
                quantity=order_details.get('quantity', 0.0),
                price_requested=order_details.get('price_requested'),
                price_filled=execution_result.get('fill_price'),
                quantity_filled=execution_result.get('fill_quantity', 0.0),
                execution_time_ms=execution_result.get('execution_time_ms', 0.0),
                slippage_ticks=execution_result.get('slippage_ticks', 0.0),
                bid_price=execution_result.get('bid_price', 0.0),
                ask_price=execution_result.get('ask_price', 0.0),
                spread_ticks=execution_result.get('spread_ticks', 0.0),
                market_impact=execution_result.get('market_impact', 0.0),
                stop_loss_price=order_details.get('stop_loss'),
                take_profit_price=order_details.get('take_profit'),
                risk_reward_ratio=order_details.get('risk_reward_ratio'),
                max_risk_dollars=order_details.get('max_risk_dollars', 0.0)
            )

            # Complete snapshot
            execution_snapshot = {
                'snapshot_id': f"{trade_id}_EXECUTION",
                'trade_id': trade_id,
                'snapshot_type': SnapshotType.EXECUTION.value,
                'timestamp': datetime.now(timezone.utc).isoformat(),

                'execution_details': asdict(exec_snapshot),
                'execution_quality': self._calculate_execution_quality(exec_snapshot),
                'market_conditions': execution_result.get('market_conditions', {})
            }

            # Calcul temps
            capture_time = (time.perf_counter() - start_time) * 1000
            execution_snapshot['capture_time_ms'] = capture_time

            # Stockage
            self.snapshots['executions'].append(execution_snapshot)

            logger.debug(f"Execution snapshot capturé: {trade_id} ({capture_time:.2f}ms)")

            return True

        except Exception as e:
            logger.error(f"Erreur capture execution snapshot: {e}")
            return False

    def finalize_trade_snapshot(self,
                                trade_id: str,
                                trade_result: TradeResult) -> bool:
        """
        SNAPSHOT FINAL
        Finalise snapshot avec résultat complet trade
        """
        start_time = time.perf_counter()

        try:
            # Trade result snapshot
            result_snapshot = TradeResultSnapshot(
                timestamp=datetime.now(timezone.utc),
                trade_id=trade_id,
                symbol=trade_result.symbol,
                entry_price=trade_result.entry_price,
                exit_price=trade_result.exit_price,
                quantity=trade_result.quantity,
                side=trade_result.side,
                gross_pnl=trade_result.gross_pnl,
                net_pnl=trade_result.net_pnl,
                commission=trade_result.commission,
                slippage_cost=trade_result.slippage_cost,
                return_percent=trade_result.return_percent,
                risk_reward_achieved=trade_result.risk_reward_achieved,
                holding_time_minutes=trade_result.holding_time_minutes,
                execution_quality_score=self._calculate_overall_execution_quality(trade_result),
                strategy_adherence_score=self._calculate_strategy_adherence(trade_result),
                entry_market_condition="NORMAL",  # À améliorer
                exit_market_condition="NORMAL",   # À améliorer
                volatility_during_trade=0.0       # À calculer
            )

            # Complete final snapshot
            final_snapshot = {
                'snapshot_id': f"{trade_id}_FINAL",
                'trade_id': trade_id,
                'snapshot_type': SnapshotType.FINAL_RESULT.value,
                'timestamp': datetime.now(timezone.utc).isoformat(),

                'trade_result': asdict(result_snapshot),
                'ml_features_prepared': self._prepare_ml_features(trade_id),
                'performance_metrics': self._calculate_performance_metrics(result_snapshot)
            }

            # Calcul temps
            capture_time = (time.perf_counter() - start_time) * 1000
            final_snapshot['capture_time_ms'] = capture_time

            # Stockage
            self.snapshots['results'].append(final_snapshot)

            # Sauvegarde complète trade
            self._save_complete_trade_snapshot(trade_id, final_snapshot)

            # Cleanup
            if trade_id in self.active_snapshots:
                del self.active_snapshots[trade_id]

            logger.info(f"Trade snapshot finalisé: {trade_id} (P&L: ${trade_result.net_pnl:.2f})")

            return True

        except Exception as e:
            logger.error(f"Erreur finalisation trade snapshot: {e}")
            return False

    def get_ml_training_data(self, min_trades: int = 50) -> Optional[Dict[str, Any]]:
        """Extraction données pour training ML"""
        try:
            completed_trades = [s for s in self.snapshots['results'] if s.get('trade_result')]

            if len(completed_trades) < min_trades:
                logger.warning(
                    f"Pas assez de trades pour ML training: {
                        len(completed_trades)}/{min_trades}")
                return None

            # Préparation features et labels
            features_list = []
            labels_list = []
            metadata_list = []

            for trade_snapshot in completed_trades:
                ml_features = trade_snapshot.get('ml_features_prepared', {})
                trade_result = trade_snapshot.get('trade_result', {})

                if ml_features and trade_result:
                    features_list.append(ml_features)
                    labels_list.append(trade_result['net_pnl'] > 0)  # Profitable or not
                    metadata_list.append({
                        'trade_id': trade_snapshot['trade_id'],
                        'timestamp': trade_snapshot['timestamp'],
                        'pnl': trade_result['net_pnl']
                    })

            return {
                'features': features_list,
                'labels': labels_list,
                'metadata': metadata_list,
                'total_trades': len(features_list),
                'profitable_trades': sum(labels_list),
                'win_rate': sum(labels_list) / len(labels_list) if labels_list else 0.0
            }

        except Exception as e:
            logger.error(f"Erreur extraction ML data: {e}")
            return None

    # === HELPER METHODS ===

    def _determine_session_phase(self, timestamp: datetime) -> str:
        """Détermine phase session marché"""
        hour = timestamp.hour
        if 4 <= hour < 9:
            return "PRE_MARKET"
        elif 9 <= hour < 16:
            return "REGULAR"
        elif 16 <= hour < 20:
            return "AFTER_HOURS"
        else:
            return "OVERNIGHT"

    def _calculate_time_since_open(self, timestamp: datetime) -> int:
        """Calcule minutes depuis ouverture"""
        # Simplifiée - à améliorer
        return timestamp.minute

    def _calculate_atr(self, market_data: MarketData) -> float:
        """Calcule ATR simplifié"""
        return abs(market_data.high - market_data.low) / ES_TICK_SIZE

    def _calculate_realized_vol(self, market_data: MarketData) -> float:
        """Calcule volatilité réalisée simplifiée"""
        return abs(market_data.close - market_data.open) / market_data.open

    def _determine_vol_regime(self, market_data: MarketData) -> str:
        """Détermine régime volatilité"""
        vol = self._calculate_realized_vol(market_data)
        if vol < 0.005:
            return "LOW"
        elif vol > 0.015:
            return "HIGH"
        else:
            return "NORMAL"

    def _determine_trend_direction(self, market_data: MarketData) -> str:
        """Détermine direction tendance"""
        if market_data.close > market_data.open:
            return "UP"
        elif market_data.close < market_data.open:
            return "DOWN"
        else:
            return "SIDEWAYS"

    def _calculate_trend_strength(self, market_data: MarketData) -> float:
        """Calcule force tendance"""
        body_size = abs(market_data.close - market_data.open)
        range_size = market_data.high - market_data.low
        return body_size / range_size if range_size > 0 else 0.0

    def _calculate_execution_quality(self, exec_snapshot: ExecutionSnapshot) -> float:
        """Calcule qualité exécution"""
        # Score basé sur slippage et timing
        slippage_score = max(0, 1 - abs(exec_snapshot.slippage_ticks) / 5.0)
        timing_score = max(0, 1 - exec_snapshot.execution_time_ms / 1000.0)
        return (slippage_score + timing_score) / 2.0

    def _calculate_overall_execution_quality(self, trade_result: TradeResult) -> float:
        """Qualité exécution globale"""
        return 0.8  # Placeholder

    def _calculate_strategy_adherence(self, trade_result: TradeResult) -> float:
        """Adhérence à la stratégie"""
        return 0.9  # Placeholder

    def _prepare_ml_features(self, trade_id: str) -> Dict[str, float]:
        """Préparation features ML du trade"""
        # Extraction features depuis snapshots du trade
        if trade_id not in self.active_snapshots:
            return {}

        # Placeholder - à implémenter complètement
        return {
            'battle_navale_signal': 0.8,
            'confluence_score': 0.7,
            'volatility': 0.5,
            'trend_strength': 0.6,
            'session_phase_numeric': 1.0  # Encoded
        }

    def _calculate_performance_metrics(
            self, result_snapshot: TradeResultSnapshot) -> Dict[str, float]:
        """Calcule métriques performance"""
        return {
            'return_on_risk': result_snapshot.return_percent,
            'efficiency_score': result_snapshot.execution_quality_score,
            'time_efficiency': 1.0 / max(result_snapshot.holding_time_minutes, 1),
            'overall_score': (result_snapshot.execution_quality_score +
                              result_snapshot.strategy_adherence_score) / 2.0
        }

    def _save_complete_trade_snapshot(self, trade_id: str, final_snapshot: Dict[str, Any]):
        """Sauvegarde snapshot complet trade"""
        try:
            # Fichier par trade
            filename = f"{trade_id}_complete.json"
            filepath = self.base_path / "daily" / filename

            # Collecte tous les snapshots du trade
            complete_data = {
                'trade_id': trade_id,
                'snapshots': {
                    'pre_analysis': self.active_snapshots.get(trade_id, {}),
                    'final_result': final_snapshot
                },
                'created_at': datetime.now(timezone.utc).isoformat()
            }

            # Sauvegarde
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(complete_data, f, indent=2, default=str)

            logger.debug(f"Trade snapshot sauvé: {filepath}")

        except Exception as e:
            logger.error(f"Erreur sauvegarde snapshot: {e}")

    def _update_capture_stats(self, capture_time_ms: float):
        """Mise à jour statistiques capture"""
        self.capture_stats['total_snapshots'] += 1
        current_avg = self.capture_stats['avg_capture_time_ms']
        count = self.capture_stats['total_snapshots']

        # Moyenne mobile
        self.capture_stats['avg_capture_time_ms'] = (
            (current_avg * (count - 1) + capture_time_ms) / count
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques snapshotter"""
        return {
            'total_snapshots': self.capture_stats['total_snapshots'],
            'avg_capture_time_ms': round(self.capture_stats['avg_capture_time_ms'], 3),
            'pre_analysis_count': len(self.snapshots['pre_analysis']),
            'decisions_count': len(self.snapshots['decisions']),
            'executions_count': len(self.snapshots['executions']),
            'completed_trades': len(self.snapshots['results']),
            'active_trades': len(self.active_snapshots)
        }

# === FACTORY FUNCTION ===


def create_trade_snapshotter() -> TradeSnapshotter:
    """Factory function pour trade snapshotter"""
    return TradeSnapshotter()

# === TESTING ===


def test_trade_snapshotter():
    """Test trade snapshotter"""
    logger.debug("Test trade snapshotter...")

    snapshotter = create_trade_snapshotter()

    # Test market data
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4500.0,
        high=4510.0,
        low=4495.0,
        close=4505.0,
        volume=1500
    )

    # Test pre-analysis snapshot
    trade_id = snapshotter.capture_pre_analysis_snapshot(market_data)
    logger.info("Pre-analysis snapshot: {trade_id}")

    # Test decision snapshot
    battle_result = {
        'signal_strength': 0.8,
        'confidence': 0.75,
        'direction': 'LONG'
    }
    features = {'vwap_trend_signal': 0.7}

    success = snapshotter.capture_decision_snapshot(trade_id, battle_result, features)
    logger.info("Decision snapshot: {success}")

    # Test statistics
    stats = snapshotter.get_statistics()
    logger.info("Stats: {stats}")

    logger.info("🎯 Trade snapshotter test COMPLETED")
    return True


if __name__ == "__main__":
    test_trade_snapshotter()

# Exportation explicite
__all__ = [
    "TradeSnapshotter",
    "create_trade_snapshotter",
    "TradingMode",
]