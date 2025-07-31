#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Performance Tracker
[UP] MÉTRIQUES PERFORMANCE DÉTAILLÉES & ANALYTICS AVANCÉES
Version: Phase 3B - Monitoring & Analytics Focused
Performance: Calculs temps réel, alertes automatiques, rapports professionnels

RESPONSABILITÉS CRITIQUES :
1. [STATS] TRACKING TRADING - P&L, Win Rate, Risk Metrics temps réel
2. [DOWN] ANALYTICS FINANCIÈRES - Sharpe, Sortino, Drawdown, VAR
3. [SEARCH] ANALYSE PÉRIODES - Détection patterns, cycles performance
4. 📋 REPORTING AVANCÉ - Rapports quotidiens/hebdomadaires professionnels
5. [ALERT] ALERTES PERFORMANCE - Seuils risque, dégradation détection
6. [UP] ATTRIBUTION ANALYSE - Performance par stratégie/symbole/période

MÉTRIQUES CALCULÉES :
- P&L (Gross/Net), Win Rate, Profit Factor
- Sharpe Ratio, Sortino Ratio, Calmar Ratio
- Maximum Drawdown, Recovery Time
- VAR (Value at Risk), Expected Shortfall
- Alpha, Beta vs benchmark
- Trade Distribution Analytics

WORKFLOW PRINCIPAL :
TradeResults → RealTimeTracking → Analytics → Reports → Alerts
"""

import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from datetime import datetime, date, timedelta, timezone
from core.logger import get_logger
from collections import defaultdict, deque
import statistics
import math
from scipy import stats
import sqlite3
import pickle
import threading
import time

# Local imports
from core.base_types import (
    MarketData, OrderFlowData, TradingSignal, TradeResult,
    ES_TICK_SIZE, ES_TICK_VALUE
)
from config.automation_config import get_automation_config

logger = get_logger(__name__)

# === PERFORMANCE TRACKING ENUMS ===


class PerformanceMetric(Enum):
    """Métriques de performance disponibles"""
    TOTAL_PNL = "total_pnl"
    WIN_RATE = "win_rate"
    PROFIT_FACTOR = "profit_factor"
    SHARPE_RATIO = "sharpe_ratio"
    SORTINO_RATIO = "sortino_ratio"
    CALMAR_RATIO = "calmar_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    AVERAGE_WIN = "average_win"
    AVERAGE_LOSS = "average_loss"
    LARGEST_WIN = "largest_win"
    LARGEST_LOSS = "largest_loss"
    CONSECUTIVE_WINS = "consecutive_wins"
    CONSECUTIVE_LOSSES = "consecutive_losses"
    VAR_95 = "var_95"
    EXPECTED_SHORTFALL = "expected_shortfall"


class AlertLevel(Enum):
    """Niveaux d'alerte performance"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class PerformancePeriod(Enum):
    """Périodes d'analyse performance"""
    INTRADAY = "intraday"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    INCEPTION = "inception"

# === PERFORMANCE DATA STRUCTURES ===


@dataclass
class TradeMetrics:
    """Métriques d'un trade individuel"""
    trade_id: str
    timestamp: datetime
    symbol: str
    side: str  # LONG/SHORT
    entry_price: float
    exit_price: float
    quantity: int
    gross_pnl: float
    net_pnl: float
    commission: float
    slippage: float
    holding_time_minutes: float
    return_percent: float
    trade_profitable: bool
    risk_reward_ratio: float
    battle_navale_signal: Optional[float] = None
    battle_strength: Optional[float] = None


@dataclass
class PerformanceSnapshot:
    """Snapshot performance à un moment donné"""
    timestamp: datetime
    period: PerformancePeriod

    # Basic metrics
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_gross_pnl: float
    total_net_pnl: float
    total_commission: float

    # Rate metrics
    win_rate: float
    loss_rate: float
    profit_factor: float

    # Risk metrics
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    current_drawdown: float

    # Trade analysis
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float

    # Advanced metrics
    var_95: float
    expected_shortfall: float
    recovery_factor: float

    # Streaks
    current_streak: int  # Positive if winning, negative if losing
    max_consecutive_wins: int
    max_consecutive_losses: int


@dataclass
class DrawdownPeriod:
    """Période de drawdown"""
    start_date: datetime
    end_date: Optional[datetime]
    peak_value: float
    trough_value: float
    max_drawdown_percent: float
    recovery_time_days: Optional[float]
    trades_during_drawdown: int
    is_active: bool


@dataclass
class PerformanceAlert:
    """Alerte performance"""
    timestamp: datetime
    alert_level: AlertLevel
    metric: str
    current_value: float
    threshold_value: float
    message: str
    period: PerformancePeriod
    recommendation: Optional[str] = None

# === MAIN PERFORMANCE TRACKER ===


class PerformanceTracker:
    """
    TRACKER PERFORMANCE MASTER

    Responsabilités :
    1. Tracking métriques trading temps réel
    2. Calculs analytics financières avancées
    3. Détection patterns et anomalies
    4. Génération rapports détaillés
    5. Système alertes automatiques
    6. Attribution analyse performance
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialisation performance tracker"""
        self.config = config or get_automation_config()

        # Storage paths
        self.base_path = Path("data/performance")
        self.daily_path = self.base_path / "daily"
        self.reports_path = self.base_path / "reports"
        self.alerts_path = self.base_path / "alerts"

        # Création directories
        for path in [self.daily_path, self.reports_path, self.alerts_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Trade data storage
        self.trade_history: List[TradeMetrics] = []
        self.daily_snapshots: Dict[date, PerformanceSnapshot] = {}
        self.drawdown_periods: List[DrawdownPeriod] = []
        self.performance_alerts: List[PerformanceAlert] = []

        # Real-time tracking
        self.current_snapshot: Optional[PerformanceSnapshot] = None
        self.equity_curve: deque = deque(maxlen=10000)  # Last 10k equity points
        self.returns_series: deque = deque(maxlen=1000)  # Daily returns

        # Performance thresholds
        self.alert_thresholds = {
            'max_drawdown_percent': 10.0,      # Alert si drawdown > 10%
            'min_sharpe_ratio': 1.0,           # Alert si Sharpe < 1.0
            'max_consecutive_losses': 5,       # Alert si 5+ pertes consécutives
            'min_win_rate_percent': 40.0,      # Alert si win rate < 40%
            'max_daily_loss_percent': 5.0,     # Alert si perte journalière > 5%
            'min_profit_factor': 1.2           # Alert si profit factor < 1.2
        }

        # Threading pour monitoring
        self.monitoring_thread: Optional[threading.Thread] = None
        self.is_monitoring = False

        # Session tracking
        self.session_start_time = datetime.now(timezone.utc)
        self.session_metrics = {
            'trades_processed': 0,
            'alerts_generated': 0,
            'reports_created': 0,
            'last_update': datetime.now(timezone.utc)
        }

        logger.info(f"PerformanceTracker initialisé: {self.base_path}")

    # === TRADE PROCESSING ===

    def track_trading_metrics(self, trade_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        TRACKING MÉTRIQUES TRADING

        Traite résultat trade et met à jour métriques
        """
        try:
            # Conversion en TradeMetrics
            trade_metrics = self._convert_to_trade_metrics(trade_result)

            if not trade_metrics:
                logger.error("Impossible de convertir trade result")
                return {'success': False, 'error': 'conversion_failed'}

            # Ajout à l'historique
            self.trade_history.append(trade_metrics)

            # Mise à jour equity curve
            self._update_equity_curve(trade_metrics)

            # Calcul métriques temps réel
            current_metrics = self._calculate_current_metrics()

            # Mise à jour snapshot courant
            self.current_snapshot = self._create_performance_snapshot(
                PerformancePeriod.INTRADAY,
                current_metrics
            )

            # Détection alertes
            alerts = self._check_performance_alerts(self.current_snapshot)
            self.performance_alerts.extend(alerts)

            # Update session stats
            self.session_metrics['trades_processed'] += 1
            self.session_metrics['last_update'] = datetime.now(timezone.utc)

            # Sauvegarde périodique
            self._save_trade_metrics(trade_metrics)

            return {
                'success': True,
                'trade_metrics': asdict(trade_metrics),
                'current_performance': asdict(self.current_snapshot),
                'alerts_generated': len(alerts)
            }

        except Exception as e:
            logger.error(f"Erreur tracking metrics: {e}")
            return {'success': False, 'error': str(e)}

    def _convert_to_trade_metrics(self, trade_result: Dict) -> Optional[TradeMetrics]:
        """Conversion trade result vers TradeMetrics"""
        try:
            # Extraction données principales
            trade_id = trade_result.get('trade_id', f"trade_{int(time.time())}")
            timestamp_str = trade_result.get('timestamp', datetime.now(timezone.utc).isoformat())

            # Parse timestamp
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = timestamp_str

            # Données trade
            symbol = trade_result.get('symbol', 'ES')
            side = trade_result.get('side', 'LONG')
            entry_price = trade_result.get('entry_price', 0.0)
            exit_price = trade_result.get('exit_price', 0.0)
            quantity = trade_result.get('quantity', 1)

            # P&L calculation
            if side.upper() == 'LONG':
                gross_pnl = (exit_price - entry_price) * quantity * ES_TICK_VALUE
            else:
                gross_pnl = (entry_price - exit_price) * quantity * ES_TICK_VALUE

            commission = trade_result.get('commission', 2.5)  # $2.50 per contract default
            slippage = trade_result.get('slippage', 0.0)
            net_pnl = gross_pnl - commission - slippage

            # Métriques calculées
            if entry_price > 0:
                return_percent = ((exit_price - entry_price) / entry_price) * 100
                if side.upper() == 'SHORT':
                    return_percent = -return_percent
            else:
                return_percent = 0.0

            holding_time_minutes = trade_result.get('holding_time_minutes', 0.0)
            trade_profitable = net_pnl > 0

            # Risk reward ratio
            risk_amount = abs(trade_result.get('stop_loss', entry_price) -
                              entry_price) * quantity * ES_TICK_VALUE
            if risk_amount > 0:
                risk_reward_ratio = max(0, gross_pnl) / risk_amount
            else:
                risk_reward_ratio = 0.0

            return TradeMetrics(
                trade_id=trade_id,
                timestamp=timestamp,
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                exit_price=exit_price,
                quantity=quantity,
                gross_pnl=gross_pnl,
                net_pnl=net_pnl,
                commission=commission,
                slippage=slippage,
                holding_time_minutes=holding_time_minutes,
                return_percent=return_percent,
                trade_profitable=trade_profitable,
                risk_reward_ratio=risk_reward_ratio,
                battle_navale_signal=trade_result.get('battle_navale_signal'),
                battle_strength=trade_result.get('battle_strength')
            )

        except Exception as e:
            logger.error(f"Erreur conversion trade metrics: {e}")
            return None

    def _update_equity_curve(self, trade_metrics: TradeMetrics):
        """Mise à jour courbe equity - VERSION CORRIGÉE"""
        try:
            # ✅ CORRECTION DU BUG - Extraction correcte de la valeur equity
            if self.equity_curve:
                # self.equity_curve[-1] est un dictionnaire, pas un float !
                last_equity_value = self.equity_curve[-1]['equity']
                current_equity = last_equity_value + trade_metrics.net_pnl
            else:
                current_equity = trade_metrics.net_pnl

            # Ajout point equity
            equity_point = {
                'timestamp': trade_metrics.timestamp,
                'equity': current_equity,
                'trade_pnl': trade_metrics.net_pnl,
                'cumulative_trades': len(self.trade_history)
            }

            self.equity_curve.append(equity_point)

            # Calcul return quotidien si nouveau jour
            self._update_daily_returns(equity_point)

        except Exception as e:
            logger.error(f"Erreur update equity curve: {e}")

    def _update_daily_returns(self, equity_point: Dict):
        """Mise à jour returns quotidiens"""
        try:
            current_date = equity_point['timestamp'].date()

            # Si nouveau jour, calculer return de la journée précédente
            if self.returns_series and len(self.equity_curve) > 1:
                previous_equity = self.equity_curve[-2]['equity']
                current_equity = equity_point['equity']

                if previous_equity != 0:
                    daily_return = (current_equity - previous_equity) / abs(previous_equity)
                    self.returns_series.append(daily_return)

        except Exception as e:
            logger.error(f"Erreur update daily returns: {e}")

    # === ANALYTICS CALCULATIONS ===

    def calculate_sharpe_ratio(self, period: PerformancePeriod = PerformancePeriod.DAILY) -> float:
        """
        CALCUL SHARPE RATIO

        Sharpe = (Return - Risk Free Rate) / Standard Deviation
        """
        try:
            if len(self.returns_series) < 2:
                return 0.0

            returns = list(self.returns_series)
            risk_free_rate = 0.02 / 252  # 2% annual risk-free rate, daily

            excess_returns = [r - risk_free_rate for r in returns]

            if len(excess_returns) < 2:
                return 0.0

            mean_excess_return = np.mean(excess_returns)
            std_excess_return = np.std(excess_returns, ddof=1)

            if std_excess_return == 0:
                return 0.0

            sharpe_ratio = mean_excess_return / std_excess_return

            # Annualisation
            if period == PerformancePeriod.DAILY:
                sharpe_ratio *= np.sqrt(252)  # Trading days per year

            return sharpe_ratio

        except Exception as e:
            logger.error(f"Erreur calcul Sharpe ratio: {e}")
            return 0.0

    def calculate_sortino_ratio(self) -> float:
        """Calcul Sortino Ratio (comme Sharpe mais avec downside deviation)"""
        try:
            if len(self.returns_series) < 2:
                return 0.0

            returns = list(self.returns_series)
            risk_free_rate = 0.02 / 252

            excess_returns = [r - risk_free_rate for r in returns]
            negative_returns = [r for r in excess_returns if r < 0]

            if len(negative_returns) < 2:
                return float('inf') if np.mean(excess_returns) > 0 else 0.0

            mean_excess_return = np.mean(excess_returns)
            downside_deviation = np.std(negative_returns, ddof=1)

            if downside_deviation == 0:
                return float('inf') if mean_excess_return > 0 else 0.0

            sortino_ratio = mean_excess_return / downside_deviation * np.sqrt(252)
            return sortino_ratio

        except Exception as e:
            logger.error(f"Erreur calcul Sortino ratio: {e}")
            return 0.0

    def calculate_max_drawdown(self) -> Tuple[float, Optional[DrawdownPeriod]]:
        """Calcul maximum drawdown et période associée"""
        try:
            if len(self.equity_curve) < 2:
                return 0.0, None

            equity_values = [point['equity'] for point in self.equity_curve]
            timestamps = [point['timestamp'] for point in self.equity_curve]

            # Calcul running maximum
            running_max = np.maximum.accumulate(equity_values)
            drawdowns = (equity_values - running_max) / \
                np.maximum(running_max, 1)  # Éviter division par 0

            max_dd_idx = np.argmin(drawdowns)
            max_drawdown_percent = abs(drawdowns[max_dd_idx]) * 100

            # Trouver début drawdown (dernier peak avant max DD)
            peak_idx = max_dd_idx
            for i in range(max_dd_idx, -1, -1):
                if drawdowns[i] == 0:  # Nouveau high
                    peak_idx = i
                    break

            # Trouver fin drawdown (premier recovery après max DD)
            recovery_idx = None
            peak_value = equity_values[peak_idx]
            for i in range(max_dd_idx + 1, len(equity_values)):
                if equity_values[i] >= peak_value:
                    recovery_idx = i
                    break

            # Création DrawdownPeriod
            drawdown_period = DrawdownPeriod(
                start_date=timestamps[peak_idx],
                end_date=timestamps[recovery_idx] if recovery_idx else None,
                peak_value=equity_values[peak_idx],
                trough_value=equity_values[max_dd_idx],
                max_drawdown_percent=max_drawdown_percent,
                recovery_time_days=(timestamps[recovery_idx] -
                                    timestamps[peak_idx]).days if recovery_idx else None,
                trades_during_drawdown=recovery_idx -
                peak_idx if recovery_idx else len(equity_values) - peak_idx,
                is_active=recovery_idx is None
            )

            return max_drawdown_percent, drawdown_period

        except Exception as e:
            logger.error(f"Erreur calcul max drawdown: {e}")
            return 0.0, None

    def calculate_var_and_es(self, confidence_level: float = 0.95) -> Tuple[float, float]:
        """Calcul Value at Risk et Expected Shortfall"""
        try:
            if len(self.returns_series) < 10:
                return 0.0, 0.0

            returns = sorted(list(self.returns_series))

            # VaR
            var_index = int((1 - confidence_level) * len(returns))
            var_95 = abs(returns[var_index]) if var_index < len(returns) else 0.0

            # Expected Shortfall (moyenne des returns pires que VaR)
            tail_returns = returns[:var_index] if var_index > 0 else [returns[0]]
            expected_shortfall = abs(np.mean(tail_returns)) if tail_returns else 0.0

            return var_95, expected_shortfall

        except Exception as e:
            logger.error(f"Erreur calcul VaR/ES: {e}")
            return 0.0, 0.0

    def analyze_drawdown_periods(self) -> List[DrawdownPeriod]:
        """
        ANALYSE PÉRIODES DRAWDOWN

        Identifie et analyse toutes les périodes de drawdown
        """
        try:
            if len(self.equity_curve) < 2:
                return []

            equity_values = [point['equity'] for point in self.equity_curve]
            timestamps = [point['timestamp'] for point in self.equity_curve]

            drawdown_periods = []
            running_max = equity_values[0]
            in_drawdown = False
            drawdown_start_idx = 0
            drawdown_peak_value = 0

            for i, equity in enumerate(equity_values):
                if equity > running_max:
                    # Nouveau high - fin drawdown si en cours
                    if in_drawdown:
                        # Finaliser drawdown précédent
                        drawdown_end = i
                        min_equity_idx = drawdown_start_idx + \
                            np.argmin(equity_values[drawdown_start_idx:i])

                        dd_percent = abs(
                            (equity_values[min_equity_idx] - drawdown_peak_value) / drawdown_peak_value) * 100

                        drawdown_period = DrawdownPeriod(
                            start_date=timestamps[drawdown_start_idx],
                            end_date=timestamps[i],
                            peak_value=drawdown_peak_value,
                            trough_value=equity_values[min_equity_idx],
                            max_drawdown_percent=dd_percent,
                            recovery_time_days=(
                                timestamps[i] - timestamps[drawdown_start_idx]).days,
                            trades_during_drawdown=i - drawdown_start_idx,
                            is_active=False
                        )

                        drawdown_periods.append(drawdown_period)
                        in_drawdown = False

                    running_max = equity

                elif equity < running_max and not in_drawdown:
                    # Début nouveau drawdown
                    in_drawdown = True
                    drawdown_start_idx = i - 1  # Peak précédent
                    drawdown_peak_value = running_max

            # Drawdown actif si terminé en drawdown
            if in_drawdown:
                min_equity_idx = drawdown_start_idx + np.argmin(equity_values[drawdown_start_idx:])
                dd_percent = abs(
                    (equity_values[min_equity_idx] - drawdown_peak_value) / drawdown_peak_value) * 100

                active_drawdown = DrawdownPeriod(
                    start_date=timestamps[drawdown_start_idx],
                    end_date=None,
                    peak_value=drawdown_peak_value,
                    trough_value=equity_values[min_equity_idx],
                    max_drawdown_percent=dd_percent,
                    recovery_time_days=None,
                    trades_during_drawdown=len(equity_values) - drawdown_start_idx,
                    is_active=True
                )

                drawdown_periods.append(active_drawdown)

            # Mise à jour liste drawdowns
            self.drawdown_periods = drawdown_periods

            return drawdown_periods

        except Exception as e:
            logger.error(f"Erreur analyse drawdown periods: {e}")
            return []

    def _calculate_current_metrics(self) -> Dict[str, float]:
        """Calcul métriques courantes"""
        try:
            if not self.trade_history:
                return {}

            # Séparation trades gagnants/perdants
            winning_trades = [t for t in self.trade_history if t.trade_profitable]
            losing_trades = [t for t in self.trade_history if not t.trade_profitable]

            # Métriques de base
            total_trades = len(self.trade_history)
            winning_count = len(winning_trades)
            losing_count = len(losing_trades)

            total_gross_pnl = sum(t.gross_pnl for t in self.trade_history)
            total_net_pnl = sum(t.net_pnl for t in self.trade_history)
            total_commission = sum(t.commission for t in self.trade_history)

            # Rates
            win_rate = (winning_count / total_trades) * 100 if total_trades > 0 else 0
            loss_rate = (losing_count / total_trades) * 100 if total_trades > 0 else 0

            # Profit factor
            gross_profits = sum(t.gross_pnl for t in winning_trades) if winning_trades else 0
            gross_losses = abs(sum(t.gross_pnl for t in losing_trades)) if losing_trades else 1
            profit_factor = gross_profits / gross_losses if gross_losses > 0 else 0

            # Moyennes
            average_win = np.mean([t.net_pnl for t in winning_trades]) if winning_trades else 0
            average_loss = np.mean([t.net_pnl for t in losing_trades]) if losing_trades else 0

            # Extremes
            largest_win = max([t.net_pnl for t in winning_trades]) if winning_trades else 0
            largest_loss = min([t.net_pnl for t in losing_trades]) if losing_trades else 0

            # Risk metrics
            sharpe_ratio = self.calculate_sharpe_ratio()
            sortino_ratio = self.calculate_sortino_ratio()
            max_drawdown_percent, _ = self.calculate_max_drawdown()
            var_95, expected_shortfall = self.calculate_var_and_es()

            # Streaks
            current_streak, max_wins, max_losses = self._calculate_streaks()

            return {
                'total_trades': total_trades,
                'winning_trades': winning_count,
                'losing_trades': losing_count,
                'total_gross_pnl': total_gross_pnl,
                'total_net_pnl': total_net_pnl,
                'total_commission': total_commission,
                'win_rate': win_rate,
                'loss_rate': loss_rate,
                'profit_factor': profit_factor,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'max_drawdown': max_drawdown_percent,
                'average_win': average_win,
                'average_loss': average_loss,
                'largest_win': largest_win,
                'largest_loss': largest_loss,
                'current_streak': current_streak,
                'max_consecutive_wins': max_wins,
                'max_consecutive_losses': max_losses,
                'var_95': var_95,
                'expected_shortfall': expected_shortfall
            }

        except Exception as e:
            logger.error(f"Erreur calcul current metrics: {e}")
            return {}

    def _calculate_streaks(self) -> Tuple[int, int, int]:
        """Calcul streaks gagnantes/perdantes"""
        try:
            if not self.trade_history:
                return 0, 0, 0

            current_streak = 0
            max_wins = 0
            max_losses = 0
            temp_wins = 0
            temp_losses = 0

            for trade in self.trade_history:
                if trade.trade_profitable:
                    temp_wins += 1
                    temp_losses = 0
                    current_streak = temp_wins
                    max_wins = max(max_wins, temp_wins)
                else:
                    temp_losses += 1
                    temp_wins = 0
                    current_streak = -temp_losses
                    max_losses = max(max_losses, temp_losses)

            return current_streak, max_wins, max_losses

        except Exception as e:
            logger.error(f"Erreur calcul streaks: {e}")
            return 0, 0, 0

    def _create_performance_snapshot(self, period: PerformancePeriod,
                                     metrics: Dict) -> PerformanceSnapshot:
        """Création snapshot performance"""
        try:
            # Calcul drawdown courant
            if self.equity_curve:
                equity_values = [p['equity'] for p in self.equity_curve]
                peak = max(equity_values)
                current = equity_values[-1]
                current_drawdown = abs((current - peak) / peak) * 100 if peak > 0 else 0
            else:
                current_drawdown = 0

            # Recovery factor
            recovery_factor = 0
            if metrics.get('max_drawdown', 0) > 0:
                recovery_factor = metrics.get('total_net_pnl', 0) / metrics.get('max_drawdown', 1)

            return PerformanceSnapshot(
                timestamp=datetime.now(timezone.utc),
                period=period,
                total_trades=int(metrics.get('total_trades', 0)),
                winning_trades=int(metrics.get('winning_trades', 0)),
                losing_trades=int(metrics.get('losing_trades', 0)),
                total_gross_pnl=metrics.get('total_gross_pnl', 0.0),
                total_net_pnl=metrics.get('total_net_pnl', 0.0),
                total_commission=metrics.get('total_commission', 0.0),
                win_rate=metrics.get('win_rate', 0.0),
                loss_rate=metrics.get('loss_rate', 0.0),
                profit_factor=metrics.get('profit_factor', 0.0),
                sharpe_ratio=metrics.get('sharpe_ratio', 0.0),
                sortino_ratio=metrics.get('sortino_ratio', 0.0),
                calmar_ratio=0.0,  # TODO: Implement
                max_drawdown=metrics.get('max_drawdown', 0.0),
                current_drawdown=current_drawdown,
                average_win=metrics.get('average_win', 0.0),
                average_loss=metrics.get('average_loss', 0.0),
                largest_win=metrics.get('largest_win', 0.0),
                largest_loss=metrics.get('largest_loss', 0.0),
                var_95=metrics.get('var_95', 0.0),
                expected_shortfall=metrics.get('expected_shortfall', 0.0),
                recovery_factor=recovery_factor,
                current_streak=int(metrics.get('current_streak', 0)),
                max_consecutive_wins=int(metrics.get('max_consecutive_wins', 0)),
                max_consecutive_losses=int(metrics.get('max_consecutive_losses', 0))
            )

        except Exception as e:
            logger.error(f"Erreur création snapshot: {e}")
            return PerformanceSnapshot(
                timestamp=datetime.now(timezone.utc),
                period=period,
                total_trades=0, winning_trades=0, losing_trades=0,
                total_gross_pnl=0.0, total_net_pnl=0.0, total_commission=0.0,
                win_rate=0.0, loss_rate=0.0, profit_factor=0.0,
                sharpe_ratio=0.0, sortino_ratio=0.0, calmar_ratio=0.0,
                max_drawdown=0.0, current_drawdown=0.0,
                average_win=0.0, average_loss=0.0,
                largest_win=0.0, largest_loss=0.0,
                var_95=0.0, expected_shortfall=0.0, recovery_factor=0.0,
                current_streak=0, max_consecutive_wins=0, max_consecutive_losses=0
            )

    # === ALERTS & MONITORING ===

    def _check_performance_alerts(self, snapshot: PerformanceSnapshot) -> List[PerformanceAlert]:
        """Vérification seuils d'alerte"""
        alerts = []

        try:
            # ✅ AJOUT: Skip alertes si aucun trade
            if snapshot.total_trades == 0:
                return alerts  # Pas d'alertes sur système vide
            
            # Drawdown alert - SEULEMENT si trades > 0
            if snapshot.max_drawdown > self.alert_thresholds['max_drawdown_percent']:
                alerts.append(PerformanceAlert(
                    timestamp=datetime.now(timezone.utc),
                    alert_level=AlertLevel.CRITICAL,
                    metric='max_drawdown',
                    current_value=snapshot.max_drawdown,
                    threshold_value=self.alert_thresholds['max_drawdown_percent'],
                    message=f"Maximum drawdown dépassé: {snapshot.max_drawdown:.2f}%",
                    period=PerformancePeriod.INTRADAY,
                    recommendation="Considérer réduction taille position ou pause trading"
                ))

            # Sharpe ratio alert
            if snapshot.total_trades >= 10 and snapshot.sharpe_ratio < self.alert_thresholds[
                    'min_sharpe_ratio']:
                alerts.append(PerformanceAlert(
                    timestamp=datetime.now(timezone.utc),
                    alert_level=AlertLevel.WARNING,
                    metric='sharpe_ratio',
                    current_value=snapshot.sharpe_ratio,
                    threshold_value=self.alert_thresholds['min_sharpe_ratio'],
                    message=f"Sharpe ratio faible: {snapshot.sharpe_ratio:.2f}",
                    period=PerformancePeriod.INTRADAY,
                    recommendation="Analyser stratégie et paramètres risque"
                ))

            # Consecutive losses alert
            if abs(
                    snapshot.current_streak) >= self.alert_thresholds['max_consecutive_losses'] and snapshot.current_streak < 0:
                alerts.append(PerformanceAlert(
                    timestamp=datetime.now(timezone.utc),
                    alert_level=AlertLevel.WARNING,
                    metric='consecutive_losses',
                    current_value=abs(snapshot.current_streak),
                    threshold_value=self.alert_thresholds['max_consecutive_losses'],
                    message=f"Série de pertes: {abs(snapshot.current_streak)} trades",
                    period=PerformancePeriod.INTRADAY,
                    recommendation="Pause trading recommandée pour analyse"
                ))

            # Win rate alert
            if snapshot.total_trades >= 20 and snapshot.win_rate < self.alert_thresholds[
                    'min_win_rate_percent']:
                alerts.append(PerformanceAlert(
                    timestamp=datetime.now(timezone.utc),
                    alert_level=AlertLevel.WARNING,
                    metric='win_rate',
                    current_value=snapshot.win_rate,
                    threshold_value=self.alert_thresholds['min_win_rate_percent'],
                    message=f"Win rate faible: {snapshot.win_rate:.1f}%",
                    period=PerformancePeriod.INTRADAY,
                    recommendation="Réviser signaux et paramètres entrée"
                ))

            # Profit factor alert
            if snapshot.total_trades >= 10 and snapshot.profit_factor < self.alert_thresholds[
                    'min_profit_factor']:
                alerts.append(PerformanceAlert(
                    timestamp=datetime.now(timezone.utc),
                    alert_level=AlertLevel.WARNING,
                    metric='profit_factor',
                    current_value=snapshot.profit_factor,
                    threshold_value=self.alert_thresholds['min_profit_factor'],
                    message=f"Profit factor faible: {snapshot.profit_factor:.2f}",
                    period=PerformancePeriod.INTRADAY,
                    recommendation="Optimiser ratio risk/reward"
                ))

            # Log alerts
            for alert in alerts:
                logger.warning(f"ALERT {alert.alert_level.value.upper()}: {alert.message}")
                self.session_metrics['alerts_generated'] += 1

            return alerts

        except Exception as e:
            logger.error(f"Erreur check alerts: {e}")
            return []

    # === REPORTING ===

    def generate_performance_report(
            self, period: PerformancePeriod = PerformancePeriod.DAILY) -> str:
        """
        GÉNÉRATION RAPPORT PERFORMANCE

        Crée rapport détaillé selon période
        """
        try:
            if not self.current_snapshot:
                return "Aucune donnée de performance disponible"

            snapshot = self.current_snapshot
            report_lines = []

            # Header
            report_lines.append("=" * 60)
            report_lines.append(f"RAPPORT PERFORMANCE MIA_IA_SYSTEM")
            report_lines.append(f"Période: {period.value.upper()}")
            report_lines.append(f"Généré: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("=" * 60)

            # Section Trading Summary
            report_lines.append("\n[STATS] RÉSUMÉ TRADING")
            report_lines.append("-" * 30)
            report_lines.append(f"Total Trades:        {snapshot.total_trades}")
            report_lines.append(f"Trades Gagnants:     {snapshot.winning_trades}")
            report_lines.append(f"Trades Perdants:     {snapshot.losing_trades}")
            report_lines.append(f"Win Rate:            {snapshot.win_rate:.2f}%")
            report_lines.append(f"Profit Factor:       {snapshot.profit_factor:.2f}")

            # Section P&L
            report_lines.append("\n[MONEY] PROFIT & LOSS")
            report_lines.append("-" * 30)
            report_lines.append(f"P&L Brut:           ${snapshot.total_gross_pnl:,.2f}")
            report_lines.append(f"P&L Net:            ${snapshot.total_net_pnl:,.2f}")
            report_lines.append(f"Commissions:        ${snapshot.total_commission:,.2f}")
            report_lines.append(f"Gain Moyen:         ${snapshot.average_win:,.2f}")
            report_lines.append(f"Perte Moyenne:      ${snapshot.average_loss:,.2f}")
            report_lines.append(f"Plus Gros Gain:     ${snapshot.largest_win:,.2f}")
            report_lines.append(f"Plus Grosse Perte:  ${snapshot.largest_loss:,.2f}")

            # Section Risk Metrics
            report_lines.append("\n[WARN] MÉTRIQUES RISQUE")
            report_lines.append("-" * 30)
            report_lines.append(f"Sharpe Ratio:        {snapshot.sharpe_ratio:.3f}")
            report_lines.append(f"Sortino Ratio:       {snapshot.sortino_ratio:.3f}")
            report_lines.append(f"Max Drawdown:        {snapshot.max_drawdown:.2f}%")
            report_lines.append(f"Drawdown Actuel:     {snapshot.current_drawdown:.2f}%")
            report_lines.append(f"VaR 95%:            ${snapshot.var_95:,.2f}")
            report_lines.append(f"Expected Shortfall: ${snapshot.expected_shortfall:,.2f}")

            # Section Streaks
            report_lines.append("\n[HOT] SÉRIES")
            report_lines.append("-" * 30)
            streak_type = "Gains" if snapshot.current_streak > 0 else "Pertes"
            report_lines.append(
                f"Série Actuelle:      {abs(snapshot.current_streak)} {streak_type}")
            report_lines.append(f"Max Gains Consécutifs: {snapshot.max_consecutive_wins}")
            report_lines.append(f"Max Pertes Consécutives: {snapshot.max_consecutive_losses}")

            # Section Alerts
            active_alerts = [a for a in self.performance_alerts if
                             (datetime.now(timezone.utc) - a.timestamp).hours < 24]

            if active_alerts:
                report_lines.append("\n[ALERT] ALERTES ACTIVES")
                report_lines.append("-" * 30)
                for alert in active_alerts[-5:]:  # Dernières 5 alertes
                    report_lines.append(f"{alert.alert_level.value.upper()}: {alert.message}")

            # Section Recommandations
            recommendations = self._generate_recommendations(snapshot)
            if recommendations:
                report_lines.append("\n[IDEA] RECOMMANDATIONS")
                report_lines.append("-" * 30)
                for rec in recommendations:
                    report_lines.append(f"• {rec}")

            report = "\n".join(report_lines)

            # Sauvegarde rapport
            self._save_performance_report(report, period)

            return report

        except Exception as e:
            logger.error(f"Erreur génération rapport: {e}")
            return f"Erreur génération rapport: {e}"

    def _generate_recommendations(self, snapshot: PerformanceSnapshot) -> List[str]:
        """Génération recommandations basées sur performance"""
        recommendations = []

        try:
            # Recommandations drawdown
            if snapshot.max_drawdown > 15:
                recommendations.append("Drawdown élevé - Réduire taille positions de 50%")
            elif snapshot.max_drawdown > 10:
                recommendations.append("Drawdown significatif - Surveillance renforcée")

            # Recommandations win rate
            if snapshot.win_rate < 40 and snapshot.total_trades >= 20:
                recommendations.append("Win rate faible - Réviser critères entrée")
            elif snapshot.win_rate > 70 and snapshot.total_trades >= 20:
                recommendations.append("Excellent win rate - Considérer augmentation taille")

            # Recommandations Sharpe
            if snapshot.sharpe_ratio < 0.5 and snapshot.total_trades >= 10:
                recommendations.append("Sharpe faible - Optimiser ratio risk/reward")
            elif snapshot.sharpe_ratio > 2.0:
                recommendations.append("Excellent Sharpe - Performance exceptionnelle")

            # Recommandations streak
            if abs(snapshot.current_streak) >= 5 and snapshot.current_streak < 0:
                recommendations.append("Série de pertes - Pause trading 24h recommandée")
            elif snapshot.current_streak >= 10:
                recommendations.append("Excellente série - Attention à l'overconfidence")

            return recommendations

        except Exception as e:
            logger.error(f"Erreur génération recommandations: {e}")
            return ["Erreur génération recommandations"]

    # === PERSISTENCE ===

    def _save_trade_metrics(self, trade_metrics: TradeMetrics):
        """Sauvegarde métriques trade"""
        try:
            trade_date = trade_metrics.timestamp.date()
            trades_file = self.daily_path / f"trades_{trade_date.isoformat()}.jsonl"

            with open(trades_file, 'a', encoding='utf-8') as f:
                json.dump(asdict(trade_metrics), f, default=str)
                f.write('\n')

        except Exception as e:
            logger.error(f"Erreur sauvegarde trade metrics: {e}")

    def _save_performance_report(self, report: str, period: PerformancePeriod):
        """Sauvegarde rapport performance"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_path / f"performance_report_{period.value}_{timestamp}.txt"

            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)

            self.session_metrics['reports_created'] += 1
            logger.info(f"Rapport sauvegardé: {report_file}")

        except Exception as e:
            logger.error(f"Erreur sauvegarde rapport: {e}")

    # === PUBLIC INTERFACE ===

    def get_current_performance(self) -> Dict[str, Any]:
        """Interface publique - Performance actuelle"""
        if self.current_snapshot:
            return asdict(self.current_snapshot)
        return {}

    def get_session_metrics(self) -> Dict[str, Any]:
        """Interface publique - Métriques session"""
        return self.session_metrics.copy()

# === FACTORY FUNCTIONS ===


def create_performance_tracker(config: Optional[Dict] = None) -> PerformanceTracker:
    """Factory function pour performance tracker"""
    return PerformanceTracker(config)

# === TESTING ===


def test_performance_tracker():
    """Test performance tracker"""
    logger.info("[UP] TEST PERFORMANCE TRACKER")
    print("=" * 40)

    tracker = create_performance_tracker()

    # Test trade result
    test_trade = {
        'trade_id': 'TEST_001',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'symbol': 'ES',
        'side': 'LONG',
        'entry_price': 4500.0,
        'exit_price': 4510.0,
        'quantity': 1,
        'commission': 2.5,
        'holding_time_minutes': 45.0
    }

    result = tracker.track_trading_metrics(test_trade)
    logger.info("Track metrics: {result['success']}")

    # Test calculs
    sharpe = tracker.calculate_sharpe_ratio()
    logger.info("Sharpe ratio: {sharpe:.3f}")

    # Test rapport
    report = tracker.generate_performance_report()
    logger.info("Rapport généré: {len(report)} caractères")

    logger.info("[TARGET] Performance tracker test COMPLETED")
    return True


if __name__ == "__main__":
    test_performance_tracker()