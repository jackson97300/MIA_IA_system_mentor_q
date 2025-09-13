"""
scripts/analyze_performance.py

ANALYSE PERFORMANCE APPROFONDIE - OBJECTIF PRIORITÉ 10
Script d'analyse complète des performances de trading Battle Navale
Génération rapports, patterns, attribution, et visualisations

FONCTIONNALITÉS :
1. generate_daily_report() - Rapport quotidien automatique
2. analyze_trade_patterns() - Analyse patterns de trading
3. calculate_strategy_attribution() - Attribution performance par stratégie
4. export_performance_charts() - Export graphiques et visualisations
5. Métriques avancées de trading
6. Détection anomalies et signaux d'alerte
7. Comparaisons benchmarks et objectifs

ARCHITECTURE : Analytics robuste, visualisations riches, insights actionables
"""

# === STDLIB ===
import os
import sys
import time
from core.logger import get_logger
import argparse
import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime, timezone, timedelta
from enum import Enum
from collections import defaultdict, Counter
import statistics
import math

# === THIRD-PARTY ===
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo

# === LOCAL IMPORTS ===
from config import get_trading_config, get_automation_config
from core.base_types import (
    MarketData, TradingSignal, SignalType, SignalStrength,
    TradeResult, ES_TICK_SIZE, ES_TICK_VALUE, PERFORMANCE_TARGETS
)

# Logger
logger = get_logger(__name__)

# === PERFORMANCE ANALYSIS ENUMS ===


class ReportType(Enum):
    """Types de rapports"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"
    REAL_TIME = "real_time"


class PerformanceMetric(Enum):
    """Métriques de performance"""
    TOTAL_PNL = "total_pnl"
    WIN_RATE = "win_rate"
    PROFIT_FACTOR = "profit_factor"
    SHARPE_RATIO = "sharpe_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    AVERAGE_WIN = "average_win"
    AVERAGE_LOSS = "average_loss"
    EXPECTANCY = "expectancy"


class PatternType(Enum):
    """Types de patterns analysés"""
    TIME_OF_DAY = "time_of_day"
    DAY_OF_WEEK = "day_of_week"
    SESSION_PERFORMANCE = "session_performance"
    MARKET_CONDITIONS = "market_conditions"
    SIGNAL_STRENGTH = "signal_strength"
    CONFLUENCE_LEVELS = "confluence_levels"


class AlertLevel(Enum):
    """Niveaux d'alerte performance"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

# === PERFORMANCE DATA STRUCTURES ===


class TradingMetrics:
    """Métriques de trading consolidées"""

    def __init__(self, trades_data: pd.DataFrame):
        """
        Initialisation avec données de trades

        Args:
            trades_data: DataFrame avec historique trades
        """
        self.trades_data = trades_data
        self.total_trades = len(trades_data)
        self.winning_trades = len(trades_data[trades_data['pnl'] > 0])
        self.losing_trades = len(trades_data[trades_data['pnl'] < 0])

        # Calcul métriques de base
        self._calculate_basic_metrics()
        self._calculate_advanced_metrics()
        self._calculate_risk_metrics()

    def _calculate_basic_metrics(self):
        """Calcul métriques de base"""
        if self.total_trades == 0:
            self._set_zero_metrics()
            return

        # PnL et Win Rate
        self.total_pnl = self.trades_data['pnl'].sum()
        self.win_rate = (self.winning_trades / self.total_trades) * 100

        # Gains et pertes moyens
        winning_trades_data = self.trades_data[self.trades_data['pnl'] > 0]['pnl']
        losing_trades_data = self.trades_data[self.trades_data['pnl'] < 0]['pnl']

        self.average_win = winning_trades_data.mean() if len(winning_trades_data) > 0 else 0
        self.average_loss = losing_trades_data.mean() if len(losing_trades_data) > 0 else 0

        # Profit Factor
        gross_profit = winning_trades_data.sum() if len(winning_trades_data) > 0 else 0
        gross_loss = abs(losing_trades_data.sum()) if len(losing_trades_data) > 0 else 0
        self.profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

    def _calculate_advanced_metrics(self):
        """Calcul métriques avancées"""
        if self.total_trades == 0:
            return

        # Expectancy
        win_prob = self.win_rate / 100
        loss_prob = 1 - win_prob
        self.expectancy = (win_prob * self.average_win) + (loss_prob * self.average_loss)

        # Sharpe Ratio (approximation)
        daily_returns = self.trades_data.groupby(self.trades_data['timestamp'].dt.date)['pnl'].sum()
        if len(daily_returns) > 1:
            returns_std = daily_returns.std()
            returns_mean = daily_returns.mean()
            self.sharpe_ratio = (returns_mean / returns_std) * \
                np.sqrt(252) if returns_std > 0 else 0
        else:
            self.sharpe_ratio = 0

        # Consecutive wins/losses
        self.max_consecutive_wins = self._calculate_max_consecutive(self.trades_data['pnl'] > 0)
        self.max_consecutive_losses = self._calculate_max_consecutive(self.trades_data['pnl'] < 0)

    def _calculate_risk_metrics(self):
        """Calcul métriques de risque"""
        if self.total_trades == 0:
            return

        # Maximum Drawdown
        cumulative_pnl = self.trades_data['pnl'].cumsum()
        running_max = cumulative_pnl.expanding().max()
        drawdown = cumulative_pnl - running_max
        self.max_drawdown = abs(drawdown.min()) if len(drawdown) > 0 else 0

        # Value at Risk (VaR 95%)
        if len(self.trades_data) >= 20:
            self.var_95 = np.percentile(self.trades_data['pnl'], 5)
        else:
            self.var_95 = self.trades_data['pnl'].min()

        # Calmar Ratio
        annual_return = self.total_pnl * (252 / max(1, len(self.trades_data)))
        self.calmar_ratio = annual_return / self.max_drawdown if self.max_drawdown > 0 else 0

    def _calculate_max_consecutive(self, condition_series: pd.Series) -> int:
        """Calcul maximum trades consécutifs"""
        consecutive = 0
        max_consecutive = 0

        for condition in condition_series:
            if condition:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 0

        return max_consecutive

    def _set_zero_metrics(self):
        """Initialisation métriques à zéro"""
        self.total_pnl = 0
        self.win_rate = 0
        self.average_win = 0
        self.average_loss = 0
        self.profit_factor = 0
        self.expectancy = 0
        self.sharpe_ratio = 0
        self.max_consecutive_wins = 0
        self.max_consecutive_losses = 0
        self.max_drawdown = 0
        self.var_95 = 0
        self.calmar_ratio = 0


class PerformanceAlert:
    """Alerte de performance"""

    def __init__(self, level: AlertLevel, metric: str, current_value: float,
                 threshold: float, message: str):
        self.level = level
        self.metric = metric
        self.current_value = current_value
        self.threshold = threshold
        self.message = message
        self.timestamp = datetime.now(timezone.utc)

# === MAIN PERFORMANCE ANALYZER ===


class PerformanceAnalyzer:
    """
    ANALYSEUR DE PERFORMANCE COMPLET

    Analyse exhaustive des performances de trading :
    - Métriques de performance avancées
    - Analyse patterns temporels et conditions marché
    - Attribution performance par stratégie
    - Détection anomalies et alertes
    - Génération rapports et visualisations
    """

    def __init__(self):
        """Initialisation de l'analyseur"""

        # Configuration
        self.trading_config = get_trading_config()
        self.auto_config = get_automation_config()

        # Données de performance
        self.trades_data: Optional[pd.DataFrame] = None
        self.snapshots_data: Optional[pd.DataFrame] = None
        self.current_metrics: Optional[TradingMetrics] = None

        # Alertes et seuils
        self.performance_alerts: List[PerformanceAlert] = []
        self.alert_thresholds = self._get_alert_thresholds()

        # Paths pour outputs
        self.reports_dir = Path("reports/performance")
        self.charts_dir = Path("reports/charts")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.charts_dir.mkdir(parents=True, exist_ok=True)

        # Configuration visualisations
        self._setup_plotting_style()

        logger.info("PerformanceAnalyzer initialisé")

    def load_trading_data(self,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> bool:
        """
        Chargement des données de trading

        Args:
            start_date: Date début analyse (None = tout)
            end_date: Date fin analyse (None = maintenant)

        Returns:
            True si chargement réussi, False sinon
        """
        logger.info("Chargement données de trading...")

        try:
            # Simulation chargement données (à remplacer par vraie source)
            self.trades_data = self._load_trades_data(start_date, end_date)
            self.snapshots_data = self._load_snapshots_data(start_date, end_date)

            if self.trades_data is not None and not self.trades_data.empty:
                # Calcul métriques
                self.current_metrics = TradingMetrics(self.trades_data)
                logger.info(f"Données chargées: {len(self.trades_data)} trades")
                return True
            else:
                logger.warning("Aucune donnée de trading trouvée")
                return False

        except Exception as e:
            logger.error(f"Erreur chargement données: {e}")
            return False

    def generate_daily_report(self, target_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Génération rapport quotidien automatique

        Args:
            target_date: Date cible (None = aujourd'hui)

        Returns:
            Dictionnaire avec rapport complet
        """
        if target_date is None:
            target_date = datetime.now(timezone.utc).date()

        logger.info(f"Génération rapport quotidien pour {target_date}")

        try:
            # Chargement données du jour
            start_datetime = datetime.combine(
                target_date, datetime.min.time()).replace(
                tzinfo=timezone.utc)
            end_datetime = start_datetime + timedelta(days=1)

            if not self.load_trading_data(start_datetime, end_datetime):
                return {"error": "Aucune donnée disponible pour la date"}

            # Métriques du jour
            daily_metrics = self._calculate_daily_metrics()

            # Comparaison avec objectifs
            performance_vs_targets = self._compare_with_targets(daily_metrics)

            # Analyse trades du jour
            trades_analysis = self._analyze_daily_trades()

            # Patterns identifiés
            patterns_detected = self._detect_daily_patterns()

            # Alertes et recommandations
            alerts = self._generate_daily_alerts()
            recommendations = self._generate_daily_recommendations()

            # Attribution par stratégie
            strategy_attribution = self._calculate_daily_strategy_attribution()

            # Création rapport
            daily_report = {
                "date": target_date.isoformat(),
                "summary": {
                    "total_trades": self.current_metrics.total_trades,
                    "total_pnl": self.current_metrics.total_pnl,
                    "win_rate": self.current_metrics.win_rate,
                    "profit_factor": self.current_metrics.profit_factor
                },
                "detailed_metrics": daily_metrics,
                "performance_vs_targets": performance_vs_targets,
                "trades_analysis": trades_analysis,
                "patterns_detected": patterns_detected,
                "strategy_attribution": strategy_attribution,
                "alerts": [self._alert_to_dict(alert) for alert in alerts],
                "recommendations": recommendations,
                "generation_timestamp": datetime.now(timezone.utc).isoformat()
            }

            # Sauvegarde rapport
            self._save_daily_report(daily_report, target_date)

            logger.info("Rapport quotidien généré avec succès")
            return daily_report

        except Exception as e:
            logger.error(f"Erreur génération rapport quotidien: {e}")
            return {"error": str(e)}

    def analyze_trade_patterns(self,
                               pattern_types: List[PatternType] = None,
                               lookback_days: int = 30) -> Dict[str, Any]:
        """
        Analyse approfondie des patterns de trading

        Args:
            pattern_types: Types de patterns à analyser (None = tous)
            lookback_days: Nombre de jours d'historique

        Returns:
            Dictionnaire avec analyses de patterns
        """
        if pattern_types is None:
            pattern_types = list(PatternType)

        logger.info(f"Analyse patterns: {[p.value for p in pattern_types]}")

        try:
            # Chargement données historiques
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=lookback_days)

            if not self.load_trading_data(start_date, end_date):
                return {"error": "Données insuffisantes pour analyse patterns"}

            patterns_analysis = {}

            # Analyse par type de pattern
            for pattern_type in pattern_types:
                if pattern_type == PatternType.TIME_OF_DAY:
                    patterns_analysis["time_of_day"] = self._analyze_time_of_day_patterns()

                elif pattern_type == PatternType.DAY_OF_WEEK:
                    patterns_analysis["day_of_week"] = self._analyze_day_of_week_patterns()

                elif pattern_type == PatternType.SESSION_PERFORMANCE:
                    patterns_analysis["session_performance"] = self._analyze_session_patterns()

                elif pattern_type == PatternType.MARKET_CONDITIONS:
                    patterns_analysis["market_conditions"] = self._analyze_market_condition_patterns()

                elif pattern_type == PatternType.SIGNAL_STRENGTH:
                    patterns_analysis["signal_strength"] = self._analyze_signal_strength_patterns()

                elif pattern_type == PatternType.CONFLUENCE_LEVELS:
                    patterns_analysis["confluence_levels"] = self._analyze_confluence_patterns()

            # Insights et recommandations
            patterns_insights = self._generate_patterns_insights(patterns_analysis)

            final_analysis = {
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_trades": self.current_metrics.total_trades
                },
                "patterns_analysis": patterns_analysis,
                "insights": patterns_insights,
                "recommendations": self._generate_patterns_recommendations(patterns_analysis),
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            }

            logger.info("Analyse patterns terminée")
            return final_analysis

        except Exception as e:
            logger.error(f"Erreur analyse patterns: {e}")
            return {"error": str(e)}

    def calculate_strategy_attribution(self,
                                       attribution_period: int = 30) -> Dict[str, Any]:
        """
        Calcul attribution performance par stratégie

        Args:
            attribution_period: Période d'attribution en jours

        Returns:
            Dictionnaire avec attribution détaillée
        """
        logger.info(f"Calcul attribution stratégies sur {attribution_period} jours")

        try:
            # Chargement données période
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=attribution_period)

            if not self.load_trading_data(start_date, end_date):
                return {"error": "Données insuffisantes pour attribution"}

            # Attribution par stratégie
            strategy_performance = self._calculate_strategy_performance()

            # Attribution par type de signal
            signal_type_performance = self._calculate_signal_type_performance()

            # Attribution par conditions de marché
            market_condition_performance = self._calculate_market_condition_performance()

            # Attribution temporelle
            temporal_attribution = self._calculate_temporal_attribution()

            # Analyse contribution
            contribution_analysis = self._analyze_contribution_sources(
                strategy_performance, signal_type_performance,
                market_condition_performance, temporal_attribution
            )

            attribution_report = {
                "attribution_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_pnl": self.current_metrics.total_pnl
                },
                "strategy_performance": strategy_performance,
                "signal_type_performance": signal_type_performance,
                "market_condition_performance": market_condition_performance,
                "temporal_attribution": temporal_attribution,
                "contribution_analysis": contribution_analysis,
                "recommendations": self._generate_attribution_recommendations(contribution_analysis),
                "calculation_timestamp": datetime.now(timezone.utc).isoformat()
            }

            logger.info("Attribution stratégies calculée")
            return attribution_report

        except Exception as e:
            logger.error(f"Erreur calcul attribution: {e}")
            return {"error": str(e)}

    def export_performance_charts(self,
                                  chart_types: List[str] = None,
                                  output_format: str = "html") -> List[str]:
        """
        Export graphiques et visualisations performance

        Args:
            chart_types: Types de graphiques (None = tous)
            output_format: Format export ("html", "png", "pdf")

        Returns:
            Liste des fichiers générés
        """
        if chart_types is None:
            chart_types = [
                "equity_curve", "drawdown", "monthly_returns",
                "trade_distribution", "win_rate_evolution",
                "performance_heatmap", "correlation_matrix"
            ]

        logger.info(f"Export charts: {chart_types}")

        generated_files = []

        try:
            if self.current_metrics is None:
                if not self.load_trading_data():
                    logger.error("Impossible de charger données pour charts")
                    return []

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Génération des graphiques
            for chart_type in chart_types:
                try:
                    filename = f"{chart_type}_{timestamp}.{output_format}"
                    filepath = self.charts_dir / filename

                    if chart_type == "equity_curve":
                        self._create_equity_curve_chart(filepath, output_format)

                    elif chart_type == "drawdown":
                        self._create_drawdown_chart(filepath, output_format)

                    elif chart_type == "monthly_returns":
                        self._create_monthly_returns_chart(filepath, output_format)

                    elif chart_type == "trade_distribution":
                        self._create_trade_distribution_chart(filepath, output_format)

                    elif chart_type == "win_rate_evolution":
                        self._create_win_rate_evolution_chart(filepath, output_format)

                    elif chart_type == "performance_heatmap":
                        self._create_performance_heatmap(filepath, output_format)

                    elif chart_type == "correlation_matrix":
                        self._create_correlation_matrix_chart(filepath, output_format)

                    generated_files.append(str(filepath))
                    logger.info(f"Chart généré: {filename}")

                except Exception as e:
                    logger.error(f"Erreur génération chart {chart_type}: {e}")

            # Génération dashboard combiné
            if len(generated_files) > 0:
                dashboard_path = self._create_performance_dashboard(timestamp, output_format)
                if dashboard_path:
                    generated_files.append(dashboard_path)

            logger.info(f"Export charts terminé: {len(generated_files)} fichiers")
            return generated_files

        except Exception as e:
            logger.error(f"Erreur export charts: {e}")
            return []

    # === MÉTHODES PRIVÉES ===

    def _load_trades_data(
            self, start_date: Optional[datetime], end_date: Optional[datetime]) -> pd.DataFrame:
        """Chargement données trades (simulation)"""

        # Simulation de données de trading
        num_trades = np.random.randint(5, 50)

        if start_date is None:
            start_date = datetime.now(timezone.utc) - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now(timezone.utc)

        # Génération trades simulés
        trades = []
        for i in range(num_trades):
            trade_time = start_date + timedelta(
                seconds=np.random.randint(0, int((end_date - start_date).total_seconds()))
            )

            # PnL simulé avec bias légèrement positif
            pnl = np.random.normal(loc=10, scale=50)  # Bias positif de $10

            trade = {
                'trade_id': f'trade_{i}',
                'timestamp': trade_time,
                'symbol': 'ES',
                'signal_type': np.random.choice(['LONG', 'SHORT']),
                'entry_price': 4500 + np.random.normal(0, 20),
                'exit_price': 4500 + np.random.normal(0, 25),
                'pnl': pnl,
                'battle_score': np.random.uniform(0.3, 1.0),
                'confluence_score': np.random.uniform(0.2, 0.9),
                'signal_strength': np.random.choice(['WEAK', 'MEDIUM', 'STRONG']),
                'session': np.random.choice(['LONDON', 'NY', 'ASIA']),
                'market_condition': np.random.choice(['TREND', 'RANGE', 'TRANSITION'])
            }
            trades.append(trade)

        trades_df = pd.DataFrame(trades)
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
        trades_df = trades_df.sort_values('timestamp').reset_index(drop=True)

        return trades_df

    def _load_snapshots_data(
            self, start_date: Optional[datetime], end_date: Optional[datetime]) -> pd.DataFrame:
        """Chargement données snapshots (simulation)"""
        # Pour cette implémentation, on retourne un DataFrame vide
        # En production, charger depuis data/snapshots/
        return pd.DataFrame()

    def _get_alert_thresholds(self) -> Dict[str, float]:
        """Configuration seuils d'alerte"""
        return {
            "max_daily_loss": -200,  # $200 perte max par jour
            "min_win_rate": 55,      # 55% win rate minimum
            "max_drawdown": 300,     # $300 drawdown max
            "min_profit_factor": 1.2,  # Profit factor minimum 1.2
            "min_trades_per_day": 2,  # Minimum 2 trades par jour
            "max_consecutive_losses": 4  # Max 4 pertes consécutives
        }

    def _setup_plotting_style(self):
        """Configuration style des graphiques"""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

        # Configuration Plotly
        import plotly.io as pio
        pio.templates.default = "plotly_white"

    def _calculate_daily_metrics(self) -> Dict[str, Any]:
        """Calcul métriques quotidiennes détaillées"""
        if self.current_metrics is None:
            return {}

        return {
            "total_pnl": self.current_metrics.total_pnl,
            "total_trades": self.current_metrics.total_trades,
            "winning_trades": self.current_metrics.winning_trades,
            "losing_trades": self.current_metrics.losing_trades,
            "win_rate": self.current_metrics.win_rate,
            "profit_factor": self.current_metrics.profit_factor,
            "average_win": self.current_metrics.average_win,
            "average_loss": self.current_metrics.average_loss,
            "expectancy": self.current_metrics.expectancy,
            "max_drawdown": self.current_metrics.max_drawdown,
            "sharpe_ratio": self.current_metrics.sharpe_ratio,
            "max_consecutive_wins": self.current_metrics.max_consecutive_wins,
            "max_consecutive_losses": self.current_metrics.max_consecutive_losses
        }

    def _compare_with_targets(self, daily_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Comparaison avec objectifs de performance"""
        targets = PERFORMANCE_TARGETS

        comparison = {}

        for metric, target_value in targets.items():
            if metric in daily_metrics:
                current_value = daily_metrics[metric]
                comparison[metric] = {
                    "current": current_value,
                    "target": target_value,
                    "achievement_pct": (current_value / target_value * 100) if target_value != 0 else 0,
                    "status": "achieved" if current_value >= target_value else "below_target"
                }

        return comparison

    def _analyze_daily_trades(self) -> Dict[str, Any]:
        """Analyse détaillée des trades du jour"""
        if self.trades_data is None or self.trades_data.empty:
            return {}

        # Distribution par type de signal
        signal_distribution = self.trades_data['signal_type'].value_counts().to_dict()

        # Performance par signal
        signal_performance = self.trades_data.groupby(
            'signal_type')['pnl'].agg(['sum', 'mean', 'count']).to_dict()

        # Best et worst trades
        best_trade = self.trades_data.loc[self.trades_data['pnl'].idxmax()].to_dict()
        worst_trade = self.trades_data.loc[self.trades_data['pnl'].idxmin()].to_dict()

        return {
            "signal_distribution": signal_distribution,
            "signal_performance": signal_performance,
            "best_trade": best_trade,
            "worst_trade": worst_trade,
            "trade_frequency": len(self.trades_data)
        }

    def _detect_daily_patterns(self) -> List[Dict[str, Any]]:
        """Détection patterns du jour"""
        patterns = []

        if self.trades_data is None or self.trades_data.empty:
            return patterns

        # Pattern: concentration horaire
        hourly_distribution = self.trades_data['timestamp'].dt.hour.value_counts()
        if hourly_distribution.max() > len(self.trades_data) * 0.5:
            dominant_hour = hourly_distribution.idxmax()
            patterns.append({
                "type": "time_concentration",
                "description": f"Concentration trades à {dominant_hour}h",
                "confidence": "high"
            })

        # Pattern: streak de wins/losses
        if self.current_metrics.max_consecutive_wins >= 4:
            patterns.append({
                "type": "winning_streak",
                "description": f"Série de {self.current_metrics.max_consecutive_wins} gains consécutifs",
                "confidence": "medium"
            })

        if self.current_metrics.max_consecutive_losses >= 3:
            patterns.append({
                "type": "losing_streak",
                "description": f"Série de {self.current_metrics.max_consecutive_losses} pertes consécutives",
                "confidence": "high"
            })

        return patterns

    def _generate_daily_alerts(self) -> List[PerformanceAlert]:
        """Génération alertes quotidiennes"""
        alerts = []

        if self.current_metrics is None:
            return alerts

        # Alerte perte quotidienne
        if self.current_metrics.total_pnl < self.alert_thresholds["max_daily_loss"]:
            alerts.append(PerformanceAlert(
                level=AlertLevel.CRITICAL,
                metric="daily_pnl",
                current_value=self.current_metrics.total_pnl,
                threshold=self.alert_thresholds["max_daily_loss"],
                message=f"Perte quotidienne dépassée: ${self.current_metrics.total_pnl:.2f}"
            ))

        # Alerte win rate
        if self.current_metrics.win_rate < self.alert_thresholds["min_win_rate"]:
            alerts.append(PerformanceAlert(
                level=AlertLevel.WARNING,
                metric="win_rate",
                current_value=self.current_metrics.win_rate,
                threshold=self.alert_thresholds["min_win_rate"],
                message=f"Win rate faible: {self.current_metrics.win_rate:.1f}%"
            ))

        # Alerte pertes consécutives
        if self.current_metrics.max_consecutive_losses >= self.alert_thresholds["max_consecutive_losses"]:
            alerts.append(PerformanceAlert(
                level=AlertLevel.CRITICAL,
                metric="consecutive_losses",
                current_value=self.current_metrics.max_consecutive_losses,
                threshold=self.alert_thresholds["max_consecutive_losses"],
                message=f"Trop de pertes consécutives: {
                    self.current_metrics.max_consecutive_losses}"
            ))

        return alerts

    def _generate_daily_recommendations(self) -> List[str]:
        """Génération recommandations quotidiennes"""
        recommendations = []

        if self.current_metrics is None:
            return recommendations

        # Recommandations basées sur performance
        if self.current_metrics.win_rate < 60:
            recommendations.append("Réviser la sélection des signaux - Win rate sous-optimal")

        if self.current_metrics.profit_factor < 1.5:
            recommendations.append("Améliorer le ratio gain/perte - Profit factor faible")

        if self.current_metrics.total_trades < 3:
            recommendations.append("Augmenter la fréquence de trading si opportunités disponibles")

        if self.current_metrics.max_drawdown > 200:
            recommendations.append("Réduire la taille des positions - Drawdown élevé")

        return recommendations

    def _calculate_daily_strategy_attribution(self) -> Dict[str, Any]:
        """Attribution performance par stratégie (quotidien)"""
        if self.trades_data is None:
            return {}

        # Attribution simulée
        attribution = {
            "battle_navale_core": {
                "trades": int(len(self.trades_data) * 0.7),
                "pnl": float(self.current_metrics.total_pnl * 0.8),
                "win_rate": self.current_metrics.win_rate + 2
            },
            "confluence_enhanced": {
                "trades": int(len(self.trades_data) * 0.3),
                "pnl": float(self.current_metrics.total_pnl * 0.2),
                "win_rate": self.current_metrics.win_rate - 5
            }
        }

        return attribution

    def _analyze_time_of_day_patterns(self) -> Dict[str, Any]:
        """Analyse patterns par heure"""
        if self.trades_data is None:
            return {}

        hourly_stats = self.trades_data.groupby(self.trades_data['timestamp'].dt.hour).agg({
            'pnl': ['sum', 'mean', 'count'],
            'signal_type': lambda x: (x == 'LONG').sum() / len(x) * 100  # % LONG
        }).round(2)

        # Meilleure et pire heure
        hourly_pnl = hourly_stats['pnl']['sum']
        best_hour = hourly_pnl.idxmax()
        worst_hour = hourly_pnl.idxmin()

        return {
            "hourly_stats": hourly_stats.to_dict(),
            "best_hour": {"hour": best_hour, "pnl": hourly_pnl[best_hour]},
            "worst_hour": {"hour": worst_hour, "pnl": hourly_pnl[worst_hour]},
            "peak_trading_hours": hourly_stats['pnl']['count'].nlargest(3).to_dict()
        }

    def _analyze_day_of_week_patterns(self) -> Dict[str, Any]:
        """Analyse patterns par jour de semaine"""
        if self.trades_data is None:
            return {}

        daily_stats = self.trades_data.groupby(self.trades_data['timestamp'].dt.day_name()).agg({
            'pnl': ['sum', 'mean', 'count'],
        }).round(2)

        return {
            "daily_stats": daily_stats.to_dict(),
            "best_day": daily_stats['pnl']['sum'].idxmax(),
            "worst_day": daily_stats['pnl']['sum'].idxmin()
        }

    def _analyze_session_patterns(self) -> Dict[str, Any]:
        """Analyse patterns par session de trading"""
        if self.trades_data is None or 'session' not in self.trades_data.columns:
            return {}

        session_stats = self.trades_data.groupby('session').agg({
            'pnl': ['sum', 'mean', 'count'],
        }).round(2)

        return {
            "session_stats": session_stats.to_dict(),
            "best_session": session_stats['pnl']['sum'].idxmax(),
            "most_active_session": session_stats['pnl']['count'].idxmax()
        }

    def _analyze_market_condition_patterns(self) -> Dict[str, Any]:
        """Analyse patterns par conditions de marché"""
        if self.trades_data is None or 'market_condition' not in self.trades_data.columns:
            return {}

        condition_stats = self.trades_data.groupby('market_condition').agg({
            'pnl': ['sum', 'mean', 'count'],
        }).round(2)

        return {
            "condition_stats": condition_stats.to_dict(),
            "best_condition": condition_stats['pnl']['mean'].idxmax(),
            "preferred_condition": condition_stats['pnl']['count'].idxmax()
        }

    def _analyze_signal_strength_patterns(self) -> Dict[str, Any]:
        """Analyse patterns par force de signal"""
        if self.trades_data is None or 'signal_strength' not in self.trades_data.columns:
            return {}

        strength_stats = self.trades_data.groupby('signal_strength').agg({
            'pnl': ['sum', 'mean', 'count'],
        }).round(2)

        return {
            "strength_stats": strength_stats.to_dict(),
            "most_profitable_strength": strength_stats['pnl']['mean'].idxmax()
        }

    def _analyze_confluence_patterns(self) -> Dict[str, Any]:
        """Analyse patterns par niveaux de confluence"""
        if self.trades_data is None or 'confluence_score' not in self.trades_data.columns:
            return {}

        # Création bins de confluence
        self.trades_data['confluence_bin'] = pd.cut(
            self.trades_data['confluence_score'],
            bins=[0, 0.3, 0.6, 1.0],
            labels=['Low', 'Medium', 'High']
        )

        confluence_stats = self.trades_data.groupby('confluence_bin').agg({
            'pnl': ['sum', 'mean', 'count'],
        }).round(2)

        return {
            "confluence_stats": confluence_stats.to_dict(),
            "optimal_confluence_range": confluence_stats['pnl']['mean'].idxmax()
        }

    def _generate_patterns_insights(self, patterns_analysis: Dict[str, Any]) -> List[str]:
        """Génération insights depuis patterns"""
        insights = []

        # Insights temporels
        if "time_of_day" in patterns_analysis:
            time_data = patterns_analysis["time_of_day"]
            if "best_hour" in time_data:
                insights.append(f"Heure la plus profitable: {time_data['best_hour']['hour']}h")

        # Insights sessions
        if "session_performance" in patterns_analysis:
            session_data = patterns_analysis["session_performance"]
            if "best_session" in session_data:
                insights.append(f"Session la plus performante: {session_data['best_session']}")

        return insights

    def _generate_patterns_recommendations(self, patterns_analysis: Dict[str, Any]) -> List[str]:
        """Recommandations basées sur patterns"""
        recommendations = []

        # Recommandations temporelles
        if "time_of_day" in patterns_analysis:
            recommendations.append("Concentrer trading sur heures les plus performantes")

        # Recommandations conditions marché
        if "market_conditions" in patterns_analysis:
            recommendations.append("Adapter stratégie selon conditions de marché identifiées")

        return recommendations

    def _calculate_strategy_performance(self) -> Dict[str, Any]:
        """Calcul performance par stratégie"""
        # Attribution simulée pour cette implémentation
        total_pnl = self.current_metrics.total_pnl

        return {
            "battle_navale_pure": {
                "pnl": total_pnl * 0.6,
                "trades": int(self.current_metrics.total_trades * 0.6),
                "win_rate": self.current_metrics.win_rate + 3
            },
            "confluence_enhanced": {
                "pnl": total_pnl * 0.4,
                "trades": int(self.current_metrics.total_trades * 0.4),
                "win_rate": self.current_metrics.win_rate - 2
            }
        }

    def _calculate_signal_type_performance(self) -> Dict[str, Any]:
        """Performance par type de signal"""
        if self.trades_data is None:
            return {}

        signal_performance = self.trades_data.groupby('signal_type').agg({
            'pnl': ['sum', 'mean', 'count']
        }).round(2)

        return signal_performance.to_dict()

    def _calculate_market_condition_performance(self) -> Dict[str, Any]:
        """Performance par condition de marché"""
        if self.trades_data is None or 'market_condition' not in self.trades_data.columns:
            return {}

        condition_performance = self.trades_data.groupby('market_condition').agg({
            'pnl': ['sum', 'mean', 'count']
        }).round(2)

        return condition_performance.to_dict()

    def _calculate_temporal_attribution(self) -> Dict[str, Any]:
        """Attribution temporelle de performance"""
        if self.trades_data is None:
            return {}

        # Attribution par période de la journée
        self.trades_data['period'] = self.trades_data['timestamp'].dt.hour.apply(
            lambda x: 'Morning' if 6 <= x < 12 else
            'Afternoon' if 12 <= x < 18 else 'Evening'
        )

        temporal_performance = self.trades_data.groupby('period').agg({
            'pnl': ['sum', 'mean', 'count']
        }).round(2)

        return temporal_performance.to_dict()

    def _analyze_contribution_sources(self, *performance_dicts) -> Dict[str, Any]:
        """Analyse sources de contribution"""
        # Analyse simplifiée pour cette implémentation
        return {
            "primary_contributor": "battle_navale_pure",
            "contribution_percentage": 65.0,
            "risk_adjusted_contribution": "positive",
            "consistency_score": 0.8
        }

    def _generate_attribution_recommendations(
            self, contribution_analysis: Dict[str, Any]) -> List[str]:
        """Recommandations basées sur attribution"""
        recommendations = []

        primary_contributor = contribution_analysis.get("primary_contributor")
        if primary_contributor:
            recommendations.append(f"Optimiser davantage {primary_contributor}")

        consistency = contribution_analysis.get("consistency_score", 0)
        if consistency < 0.7:
            recommendations.append("Améliorer la consistance des stratégies")

        return recommendations

    def _create_equity_curve_chart(self, filepath: Path, output_format: str):
        """Création graphique courbe d'équité"""
        if self.trades_data is None:
            return

        # Calcul courbe d'équité
        equity_curve = self.trades_data['pnl'].cumsum()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=self.trades_data['timestamp'],
            y=equity_curve,
            mode='lines',
            name='Equity Curve',
            line=dict(color='blue', width=2)
        ))

        fig.update_layout(
            title='Courbe d\'Équité',
            xaxis_title='Date',
            yaxis_title='PnL Cumulé ($)',
            template='plotly_white'
        )

        if output_format == "html":
            fig.write_html(str(filepath))
        elif output_format == "png":
            fig.write_image(str(filepath))

    def _create_drawdown_chart(self, filepath: Path, output_format: str):
        """Création graphique drawdown"""
        if self.trades_data is None:
            return

        cumulative_pnl = self.trades_data['pnl'].cumsum()
        running_max = cumulative_pnl.expanding().max()
        drawdown = cumulative_pnl - running_max

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=self.trades_data['timestamp'],
            y=drawdown,
            mode='lines',
            name='Drawdown',
            fill='tozeroy',
            line=dict(color='red')
        ))

        fig.update_layout(
            title='Drawdown',
            xaxis_title='Date',
            yaxis_title='Drawdown ($)',
            template='plotly_white'
        )

        if output_format == "html":
            fig.write_html(str(filepath))
        elif output_format == "png":
            fig.write_image(str(filepath))

    def _create_monthly_returns_chart(self, filepath: Path, output_format: str):
        """Création graphique returns mensuels"""
        if self.trades_data is None:
            return

        monthly_returns = self.trades_data.groupby(
            self.trades_data['timestamp'].dt.to_period('M')
        )['pnl'].sum()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[str(period) for period in monthly_returns.index],
            y=monthly_returns.values,
            name='Returns Mensuels'
        ))

        fig.update_layout(
            title='Returns Mensuels',
            xaxis_title='Mois',
            yaxis_title='PnL ($)',
            template='plotly_white'
        )

        if output_format == "html":
            fig.write_html(str(filepath))
        elif output_format == "png":
            fig.write_image(str(filepath))

    def _create_trade_distribution_chart(self, filepath: Path, output_format: str):
        """Création graphique distribution trades"""
        if self.trades_data is None:
            return

        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=self.trades_data['pnl'],
            nbinsx=20,
            name='Distribution PnL'
        ))

        fig.update_layout(
            title='Distribution des Trades',
            xaxis_title='PnL ($)',
            yaxis_title='Fréquence',
            template='plotly_white'
        )

        if output_format == "html":
            fig.write_html(str(filepath))
        elif output_format == "png":
            fig.write_image(str(filepath))

    def _create_win_rate_evolution_chart(self, filepath: Path, output_format: str):
        """Création graphique évolution win rate"""
        if self.trades_data is None:
            return

        # Win rate mobile sur 10 trades
        win_rate_rolling = (self.trades_data['pnl'] > 0).rolling(window=10).mean() * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=self.trades_data['timestamp'],
            y=win_rate_rolling,
            mode='lines',
            name='Win Rate (10 trades mobile)'
        ))

        fig.update_layout(
            title='Évolution Win Rate',
            xaxis_title='Date',
            yaxis_title='Win Rate (%)',
            template='plotly_white'
        )

        if output_format == "html":
            fig.write_html(str(filepath))
        elif output_format == "png":
            fig.write_image(str(filepath))

    def _create_performance_heatmap(self, filepath: Path, output_format: str):
        """Création heatmap performance"""
        if self.trades_data is None:
            return

        # Heatmap heure vs jour de semaine
        self.trades_data['hour'] = self.trades_data['timestamp'].dt.hour
        self.trades_data['weekday'] = self.trades_data['timestamp'].dt.day_name()

        heatmap_data = self.trades_data.groupby(['weekday', 'hour'])[
            'pnl'].sum().unstack(fill_value=0)

        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='RdYlBu_r'
        ))

        fig.update_layout(
            title='Heatmap Performance (Jour vs Heure)',
            xaxis_title='Heure',
            yaxis_title='Jour de la semaine',
            template='plotly_white'
        )

        if output_format == "html":
            fig.write_html(str(filepath))
        elif output_format == "png":
            fig.write_image(str(filepath))

    def _create_correlation_matrix_chart(self, filepath: Path, output_format: str):
        """Création matrice de corrélation"""
        if self.trades_data is None:
            return

        # Sélection colonnes numériques pour corrélation
        numeric_cols = ['pnl', 'battle_score', 'confluence_score']
        correlation_data = self.trades_data[numeric_cols].corr()

        fig = go.Figure(data=go.Heatmap(
            z=correlation_data.values,
            x=correlation_data.columns,
            y=correlation_data.columns,
            colorscale='RdBu',
            zmid=0
        ))

        fig.update_layout(
            title='Matrice de Corrélation',
            template='plotly_white'
        )

        if output_format == "html":
            fig.write_html(str(filepath))
        elif output_format == "png":
            fig.write_image(str(filepath))

    def _create_performance_dashboard(self, timestamp: str, output_format: str) -> Optional[str]:
        """Création dashboard performance combiné"""
        if output_format != "html":
            return None

        dashboard_path = self.charts_dir / f"performance_dashboard_{timestamp}.html"

        try:
            # Dashboard HTML simple combinant tous les charts
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Performance Dashboard - {timestamp}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .chart-container {{ margin: 20px 0; }}
                    .metrics-summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <h1>Performance Dashboard - {datetime.now().strftime('%Y-%m-%d')}</h1>

                <div class="metrics-summary">
                    <h2>Résumé Métriques</h2>
                    <p>Total PnL: ${self.current_metrics.total_pnl:.2f}</p>
                    <p>Win Rate: {self.current_metrics.win_rate:.1f}%</p>
                    <p>Profit Factor: {self.current_metrics.profit_factor:.2f}</p>
                    <p>Total Trades: {self.current_metrics.total_trades}</p>
                </div>

                <div class="chart-container">
                    <p>Charts individuels générés dans le dossier charts/</p>
                </div>
            </body>
            </html>
            """

            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            return str(dashboard_path)

        except Exception as e:
            logger.error(f"Erreur création dashboard: {e}")
            return None

    def _save_daily_report(self, report: Dict[str, Any], target_date):
        """Sauvegarde rapport quotidien"""
        report_filename = f"daily_report_{target_date.strftime('%Y%m%d')}.json"
        report_path = self.reports_dir / report_filename

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"Rapport quotidien sauvegardé: {report_path}")

        except Exception as e:
            logger.error(f"Erreur sauvegarde rapport: {e}")

    def _alert_to_dict(self, alert: PerformanceAlert) -> Dict[str, Any]:
        """Conversion alerte en dictionnaire"""
        return {
            "level": alert.level.value,
            "metric": alert.metric,
            "current_value": alert.current_value,
            "threshold": alert.threshold,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat()
        }

# === GLOBAL ANALYZER INSTANCE ===


performance_analyzer = PerformanceAnalyzer()

# === FONCTIONS PRINCIPALES ===


def generate_daily_report(target_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Génération rapport quotidien automatique

    Args:
        target_date: Date cible (None = aujourd'hui)

    Returns:
        Dictionnaire avec rapport complet
    """
    return performance_analyzer.generate_daily_report(target_date)


def analyze_trade_patterns(
        pattern_types: List[PatternType] = None, lookback_days: int = 30) -> Dict[str, Any]:
    """
    Analyse patterns de trading

    Args:
        pattern_types: Types de patterns (None = tous)
        lookback_days: Historique en jours

    Returns:
        Analyses de patterns
    """
    return performance_analyzer.analyze_trade_patterns(pattern_types, lookback_days)


def calculate_strategy_attribution(attribution_period: int = 30) -> Dict[str, Any]:
    """
    Calcul attribution performance par stratégie

    Args:
        attribution_period: Période en jours

    Returns:
        Attribution détaillée
    """
    return performance_analyzer.calculate_strategy_attribution(attribution_period)


def export_performance_charts(
        chart_types: List[str] = None, output_format: str = "html") -> List[str]:
    """
    Export graphiques performance

    Args:
        chart_types: Types de graphiques (None = tous)
        output_format: Format export

    Returns:
        Liste fichiers générés
    """
    return performance_analyzer.export_performance_charts(chart_types, output_format)

# === CLI INTERFACE ===


def main():
    """Interface en ligne de commande"""

    parser = argparse.ArgumentParser(description="MIA Trading Performance Analyzer")
    parser.add_argument("command", choices=["daily", "patterns", "attribution", "charts", "full"],
                        help="Type d'analyse")

    # Arguments optionnels
    parser.add_argument("--date", type=str, help="Date au format YYYY-MM-DD")
    parser.add_argument("--lookback", type=int, default=30, help="Jours d'historique")
    parser.add_argument(
        "--format",
        choices=[
            "html",
            "png",
            "pdf"],
        default="html",
        help="Format export")
    parser.add_argument("--verbose", "-v", action="store_true", help="Logging verbose")

    args = parser.parse_args()

    # Configuration logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(
                f"logs/performance/analysis_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler()
        ]
    )

    logger.info("=== MIA TRADING PERFORMANCE ANALYZER ===")

    try:
        # Exécution selon commande
        if args.command == "daily":
            target_date = None
            if args.date:
                target_date = datetime.strptime(args.date, "%Y-%m-%d")

            report = generate_daily_report(target_date)
            logger.info("[STATS] RAPPORT QUOTIDIEN GÉNÉRÉ")
            print(json.dumps(report.get("summary", {}), indent=2))

        elif args.command == "patterns":
            analysis = analyze_trade_patterns(lookback_days=args.lookback)
            logger.info("[UP] ANALYSE PATTERNS TERMINÉE")
            logger.info("Patterns analysés sur {args.lookback} jours")

            insights = analysis.get("insights", [])
            if insights:
                logger.info("Insights principaux:")
                for insight in insights[:3]:
                    logger.info("  • {insight}")

        elif args.command == "attribution":
            attribution = calculate_strategy_attribution(args.lookback)
            logger.info("📋 ATTRIBUTION STRATÉGIES CALCULÉE")

            contrib = attribution.get("contribution_analysis", {})
            primary = contrib.get("primary_contributor")
            if primary:
                logger.info("Contributeur principal: {primary}")

        elif args.command == "charts":
            files = export_performance_charts(output_format=args.format)
            logger.info("[STATS] CHARTS EXPORTÉS: {len(files)} fichiers")
            for file in files[:5]:  # Afficher les 5 premiers
                logger.info("  • {Path(file).name}")

        elif args.command == "full":
            logger.info("[SYNC] ANALYSE COMPLÈTE EN COURS...")

            # Rapport quotidien
            daily_report = generate_daily_report()
            logger.info("Rapport quotidien généré")

            # Patterns
            patterns = analyze_trade_patterns(lookback_days=args.lookback)
            logger.info("Patterns analysés")

            # Attribution
            attribution = calculate_strategy_attribution(args.lookback)
            logger.info("Attribution calculée")

            # Charts
            charts = export_performance_charts(output_format=args.format)
            logger.info("{len(charts)} charts exportés")

            logger.info("[PARTY] ANALYSE COMPLÈTE TERMINÉE")

    except Exception as e:
        logger.error(f"Erreur analyse: {e}")
        logger.error("Erreur: {e}")
        sys.exit(1)

# === TEST FUNCTION ===


def test_performance_analyzer():
    """Test complet de l'analyseur de performance"""
    logger.info("=== TEST PERFORMANCE ANALYZER ===")

    logger.info("Test 1: Chargement données")
    success = performance_analyzer.load_trading_data()
    logger.info("Chargement données: {'[OK]' if success else '[ERROR]'}")

    if success:
        logger.info("Test 2: Rapport quotidien")
        daily_report = generate_daily_report()
        logger.info("Rapport quotidien: {'[OK]' if 'summary' in daily_report else '[ERROR]'}")

        logger.info("Test 3: Analyse patterns")
        patterns = analyze_trade_patterns(lookback_days=7)
        logger.info("Analyse patterns: {'[OK]' if 'patterns_analysis' in patterns else '[ERROR]'}")

        logger.info("Test 4: Attribution")
        attribution = calculate_strategy_attribution(7)
        logger.info("Attribution: {'[OK]' if 'strategy_performance' in attribution else '[ERROR]'}")

        logger.info("Test 5: Export charts")
        charts = export_performance_charts(["equity_curve", "drawdown"])
        logger.info("Export charts: {'[OK]' if len(charts) > 0 else '[ERROR]'}")

    logger.info("=== TEST TERMINÉ ===")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        logger.info("Usage: python analyze_performance.py {daily|patterns|attribution|charts|full}")
        logger.info("Ou lancez test_performance_analyzer() pour tests")
