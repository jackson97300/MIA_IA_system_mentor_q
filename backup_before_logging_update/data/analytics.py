#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Data Analytics Module
Analyse des données de trading et génération de rapports
Version: Production Ready

Ce module fournit :
- Analyse des performances de trading
- Statistiques des patterns Battle Navale
- Métriques ML et validation
- Génération de rapports détaillés
- Visualisations (optionnel)
"""

# === STDLIB ===
import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from datetime import datetime, timezone, timedelta
from enum import Enum
import statistics
from collections import defaultdict, Counter
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# === THIRD-PARTY ===
import numpy as np
import pandas as pd

# Visualisation optionnelle
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    plt = None
    sns = None

# === LOCAL IMPORTS ===
from config import get_trading_config, get_automation_config
from core.base_types import (
    MarketData, TradingSignal, SignalType, SignalStrength,
    TradeResult, ES_TICK_SIZE, ES_TICK_VALUE,
    SessionPhase, get_session_phase
)

# Logger
logger = logging.getLogger(__name__)

# === ANALYTICS ENUMS ===

class AnalysisType(Enum):
    """Types d'analyses disponibles"""
    PERFORMANCE = "performance"
    PATTERNS = "patterns"
    RISK = "risk"
    ML_METRICS = "ml_metrics"
    SESSION = "session"
    COMPREHENSIVE = "comprehensive"

class ReportFormat(Enum):
    """Formats de rapport"""
    JSON = "json"
    CSV = "csv"
    HTML = "html"
    PDF = "pdf"
    MARKDOWN = "markdown"

class TimeFrame(Enum):
    """Périodes d'analyse"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ALL_TIME = "all_time"

class PatternType(Enum):
    """Types de patterns détectables"""
    WINNING_STREAK = "winning_streak"
    LOSING_STREAK = "losing_streak"
    TIME_OF_DAY = "time_of_day"
    VOLATILITY_REGIME = "volatility_regime"
    SIGNAL_STRENGTH = "signal_strength"
    MARKET_CONDITION = "market_condition"

# === DATA STRUCTURES ===

@dataclass
class PerformanceMetrics:
    """Métriques de performance trading"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    
    # P&L
    total_pnl: float = 0.0
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    average_win: float = 0.0
    average_loss: float = 0.0
    avg_pnl: float = 0.0
    
    # Ratios
    win_rate: float = 0.0
    profit_factor: float = 0.0
    expectancy: float = 0.0
    
    # Risk metrics
    max_drawdown: float = 0.0
    max_drawdown_duration: int = 0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    
    # Statistiques
    largest_win: float = 0.0
    largest_loss: float = 0.0
    avg_trade_duration: float = 0.0
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    
    # Metrics avancées
    var_95: float = 0.0  # Value at Risk
    cvar_95: float = 0.0  # Conditional VaR
    trades_per_day: float = 0.0
    avg_holding_time_minutes: float = 0.0
    
    # Par session
    performance_by_session: Dict[str, Dict[str, float]] = field(default_factory=dict)

@dataclass
class PatternAnalysis:
    """Analyse des patterns Battle Navale"""
    pattern_frequency: Dict[str, int] = field(default_factory=dict)
    pattern_win_rate: Dict[str, float] = field(default_factory=dict)
    pattern_avg_pnl: Dict[str, float] = field(default_factory=dict)
    
    # Confluence
    confluence_distribution: Dict[float, int] = field(default_factory=dict)
    confluence_performance: Dict[str, float] = field(default_factory=dict)
    
    # Battle Navale spécifique
    battle_strength_distribution: List[float] = field(default_factory=list)
    base_quality_impact: Dict[str, float] = field(default_factory=dict)
    
    # Timing
    best_hours: List[int] = field(default_factory=list)
    worst_hours: List[int] = field(default_factory=list)
    
    # Patterns avancés
    time_patterns: Dict[str, Any] = field(default_factory=dict)
    volatility_patterns: Dict[str, Any] = field(default_factory=dict)
    signal_strength_patterns: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class RiskAnalysis:
    """Analyse des risques"""
    var_95: float = 0.0  # Value at Risk 95%
    cvar_95: float = 0.0  # Conditional VaR
    
    # Distribution des pertes
    loss_distribution: List[float] = field(default_factory=list)
    recovery_times: List[int] = field(default_factory=list)
    
    # Risk/Reward
    risk_reward_ratio: float = 0.0
    avg_risk_per_trade: float = 0.0
    
    # Kelly Criterion
    kelly_fraction: float = 0.0
    optimal_position_size: float = 0.0
    
    # Métriques avancées
    tail_ratio: float = 0.0
    omega_ratio: float = 0.0
    ulcer_index: float = 0.0
    recovery_factor: float = 0.0

@dataclass
class MLAnalysis:
    """Analyse des modèles ML"""
    model_accuracy: float = 0.0
    model_precision: float = 0.0
    model_recall: float = 0.0
    model_f1_score: float = 0.0
    
    # Feature importance
    feature_importance: Dict[str, float] = field(default_factory=dict)
    
    # Performance vs baseline
    ml_enhanced_win_rate: float = 0.0
    baseline_win_rate: float = 0.0
    improvement_percentage: float = 0.0
    
    # Prédictions
    prediction_distribution: Dict[str, int] = field(default_factory=dict)
    prediction_accuracy_by_confidence: Dict[float, float] = field(default_factory=dict)

@dataclass
class AnalyticsReport:
    """Rapport d'analyse complet"""
    report_id: str
    generated_at: datetime
    time_frame: TimeFrame
    analysis_type: AnalysisType
    
    # Données analysées
    start_date: datetime
    end_date: datetime
    total_records: int
    
    # Résultats
    performance: Optional[PerformanceMetrics] = None
    patterns: Optional[PatternAnalysis] = None
    risk: Optional[RiskAnalysis] = None
    ml_metrics: Optional[MLAnalysis] = None
    
    # Recommandations
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

# === MAIN ANALYTICS CLASS ===

class DataAnalytics:
    """
    Module d'analyse des données de trading
    
    Fournit des analyses détaillées sur :
    - Performance de trading
    - Patterns et leur efficacité
    - Métriques de risque
    - Performance ML
    - Insights et recommandations
    """
    
    def __init__(self):
        """Initialise le module analytics"""
        self.trading_config = get_trading_config()
        self.auto_config = get_automation_config()
        
        # Paths
        self.data_dir = Path("data")
        self.snapshots_dir = self.data_dir / "snapshots"
        self.reports_dir = self.data_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Cache
        self._data_cache: Dict[str, pd.DataFrame] = {}
        
        logger.info("DataAnalytics initialisé")
    
    def analyze_performance(self, 
                          trades: Union[List[Dict], pd.DataFrame],
                          time_frame: TimeFrame = TimeFrame.ALL_TIME) -> PerformanceMetrics:
        """
        Analyse les performances de trading
        
        Args:
            trades: Liste des trades ou DataFrame
            time_frame: Période d'analyse
            
        Returns:
            PerformanceMetrics avec toutes les statistiques
        """
        # Conversion en DataFrame si nécessaire
        if isinstance(trades, list):
            df = pd.DataFrame(trades)
        else:
            df = trades.copy()
        
        if df.empty:
            return PerformanceMetrics()
        
        # Filtrage par période
        df = self._filter_by_timeframe(df, time_frame)
        
        # Calculs de base
        metrics = PerformanceMetrics()
        metrics.total_trades = len(df)
        
        # Séparation wins/losses
        winners = df[df['pnl'] > 0]
        losers = df[df['pnl'] < 0]
        
        metrics.winning_trades = len(winners)
        metrics.losing_trades = len(losers)
        
        # P&L
        metrics.total_pnl = df['pnl'].sum()
        metrics.gross_profit = winners['pnl'].sum() if not winners.empty else 0
        metrics.gross_loss = abs(losers['pnl'].sum()) if not losers.empty else 0
        metrics.avg_pnl = df['pnl'].mean()
        
        # Moyennes
        metrics.average_win = winners['pnl'].mean() if not winners.empty else 0
        metrics.average_loss = abs(losers['pnl'].mean()) if not losers.empty else 0
        
        # Ratios
        metrics.win_rate = metrics.winning_trades / metrics.total_trades if metrics.total_trades > 0 else 0
        metrics.profit_factor = metrics.gross_profit / metrics.gross_loss if metrics.gross_loss > 0 else float('inf')
        
        # Expectancy
        if metrics.total_trades > 0:
            metrics.expectancy = (
                metrics.win_rate * metrics.average_win - 
                (1 - metrics.win_rate) * metrics.average_loss
            )
        
        # Risk metrics
        metrics.max_drawdown = self._calculate_max_drawdown(df)
        metrics.sharpe_ratio = self._calculate_sharpe_ratio(df)
        metrics.sortino_ratio = self._calculate_sortino_ratio(df)
        
        # Calmar ratio
        if metrics.max_drawdown > 0:
            metrics.calmar_ratio = (metrics.avg_pnl * 252) / metrics.max_drawdown
        
        # Records
        metrics.largest_win = winners['pnl'].max() if not winners.empty else 0
        metrics.largest_loss = abs(losers['pnl'].min()) if not losers.empty else 0
        
        # Durée moyenne (si disponible)
        if 'duration_minutes' in df.columns:
            metrics.avg_trade_duration = df['duration_minutes'].mean()
        
        if 'holding_time_minutes' in df.columns:
            metrics.avg_holding_time_minutes = df['holding_time_minutes'].mean()
        
        # Séquences
        streaks = self._calculate_streaks(df['pnl'])
        metrics.consecutive_wins = streaks['max_wins']
        metrics.consecutive_losses = streaks['max_losses']
        
        # VaR et CVaR
        metrics.var_95 = np.percentile(df['pnl'], 5)
        cvar_mask = df['pnl'] <= metrics.var_95
        metrics.cvar_95 = df.loc[cvar_mask, 'pnl'].mean() if cvar_mask.any() else metrics.var_95
        
        # Trades par jour
        if 'timestamp' in df.columns:
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
            unique_days = df['date'].nunique()
            metrics.trades_per_day = metrics.total_trades / unique_days if unique_days > 0 else 0
        
        # Performance par session
        if 'session' in df.columns:
            for session in df['session'].unique():
                session_df = df[df['session'] == session]
                metrics.performance_by_session[session] = {
                    'trades': len(session_df),
                    'win_rate': len(session_df[session_df['pnl'] > 0]) / len(session_df) if len(session_df) > 0 else 0,
                    'total_pnl': session_df['pnl'].sum()
                }
        
        return metrics
    
    def analyze_patterns(self,
                        snapshots: Union[List[Dict], pd.DataFrame]) -> PatternAnalysis:
        """
        Analyse les patterns Battle Navale
        
        Args:
            snapshots: Snapshots de trading
            
        Returns:
            PatternAnalysis avec statistiques des patterns
        """
        # Conversion en DataFrame
        if isinstance(snapshots, list):
            df = pd.DataFrame(snapshots)
        else:
            df = snapshots.copy()
        
        if df.empty:
            return PatternAnalysis()
        
        analysis = PatternAnalysis()
        
        # Fréquence des patterns
        if 'pattern_type' in df.columns:
            pattern_counts = df['pattern_type'].value_counts()
            analysis.pattern_frequency = pattern_counts.to_dict()
            
            # Performance par pattern
            for pattern in pattern_counts.index:
                pattern_df = df[df['pattern_type'] == pattern]
                if 'trade_result' in df.columns:
                    wins = len(pattern_df[pattern_df['trade_result'] == 'win'])
                    total = len(pattern_df)
                    analysis.pattern_win_rate[pattern] = wins / total if total > 0 else 0
                
                if 'pnl' in df.columns:
                    analysis.pattern_avg_pnl[pattern] = pattern_df['pnl'].mean()
        
        # Analyse confluence
        if 'confluence_score' in df.columns:
            # Distribution
            conf_bins = pd.cut(df['confluence_score'], bins=10)
            analysis.confluence_distribution = conf_bins.value_counts().to_dict()
            
            # Performance par niveau de confluence
            for level in ['low', 'medium', 'high']:
                if level == 'low':
                    level_df = df[df['confluence_score'] < 0.4]
                elif level == 'medium':
                    level_df = df[(df['confluence_score'] >= 0.4) & (df['confluence_score'] < 0.7)]
                else:
                    level_df = df[df['confluence_score'] >= 0.7]
                
                if not level_df.empty and 'pnl' in df.columns:
                    analysis.confluence_performance[level] = {
                        'win_rate': len(level_df[level_df['pnl'] > 0]) / len(level_df),
                        'avg_pnl': level_df['pnl'].mean()
                    }
        
        # Battle Navale spécifique
        if 'battle_strength' in df.columns:
            analysis.battle_strength_distribution = df['battle_strength'].tolist()
        
        if 'base_quality' in df.columns and 'pnl' in df.columns:
            for quality in ['low', 'medium', 'high']:
                if quality == 'low':
                    quality_df = df[df['base_quality'] < 0.4]
                elif quality == 'medium':
                    quality_df = df[(df['base_quality'] >= 0.4) & (df['base_quality'] < 0.7)]
                else:
                    quality_df = df[df['base_quality'] >= 0.7]
                
                if not quality_df.empty:
                    analysis.base_quality_impact[quality] = quality_df['pnl'].mean()
        
        # Analyse temporelle simple
        if 'timestamp' in df.columns:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            
            # Performance par heure
            hourly_perf = {}
            for hour in range(24):
                hour_df = df[df['hour'] == hour]
                if not hour_df.empty and 'pnl' in df.columns:
                    hourly_perf[hour] = hour_df['pnl'].mean()
            
            # Top 3 meilleures et pires heures
            sorted_hours = sorted(hourly_perf.items(), key=lambda x: x[1], reverse=True)
            analysis.best_hours = [h[0] for h in sorted_hours[:3]]
            analysis.worst_hours = [h[0] for h in sorted_hours[-3:]]
        
        # Analyses avancées
        analysis.time_patterns = self._analyze_time_of_day_pattern(df)
        analysis.volatility_patterns = self._analyze_volatility_pattern(df)
        analysis.signal_strength_patterns = self._analyze_signal_strength_pattern(df)
        
        # Analyse des streaks
        streak_patterns = self._analyze_streak_patterns(df)
        if streak_patterns:
            analysis.pattern_frequency['winning_streaks'] = len([p for p in streak_patterns if p['type'] == PatternType.WINNING_STREAK])
            analysis.pattern_frequency['losing_streaks'] = len([p for p in streak_patterns if p['type'] == PatternType.LOSING_STREAK])
        
        return analysis
    
    def analyze_risk(self,
                    trades: Union[List[Dict], pd.DataFrame]) -> RiskAnalysis:
        """
        Analyse des risques
        
        Args:
            trades: Historique des trades
            
        Returns:
            RiskAnalysis avec métriques de risque
        """
        # Conversion en DataFrame
        if isinstance(trades, list):
            df = pd.DataFrame(trades)
        else:
            df = trades.copy()
        
        if df.empty or 'pnl' not in df.columns:
            return RiskAnalysis()
        
        analysis = RiskAnalysis()
        
        # Distribution des pertes
        losses = df[df['pnl'] < 0]['pnl'].values
        analysis.loss_distribution = losses.tolist()
        
        # VaR et CVaR
        if len(losses) > 0:
            analysis.var_95 = np.percentile(losses, 5)
            analysis.cvar_95 = losses[losses <= analysis.var_95].mean()
        
        # Risk/Reward
        if 'stop_loss' in df.columns and 'take_profit' in df.columns and 'entry_price' in df.columns:
            df['risk'] = abs(df['entry_price'] - df['stop_loss']) * ES_TICK_VALUE
            df['reward'] = abs(df['take_profit'] - df['entry_price']) * ES_TICK_VALUE
            
            valid_rr = df['reward'] / df['risk']
            valid_rr = valid_rr[valid_rr.notna() & (valid_rr != np.inf)]
            
            if len(valid_rr) > 0:
                analysis.risk_reward_ratio = valid_rr.mean()
                analysis.avg_risk_per_trade = df['risk'].mean()
        
        # Kelly Criterion
        if len(df) > 0:
            win_rate = len(df[df['pnl'] > 0]) / len(df)
            avg_win = df[df['pnl'] > 0]['pnl'].mean() if len(df[df['pnl'] > 0]) > 0 else 0
            avg_loss = abs(df[df['pnl'] < 0]['pnl'].mean()) if len(df[df['pnl'] < 0]) > 0 else 0
            
            if avg_loss > 0 and avg_win > 0:
                analysis.kelly_fraction = self._calculate_kelly_criterion(win_rate, avg_win, avg_loss)
        
        # Métriques avancées
        analysis.tail_ratio = self._calculate_tail_ratio(df['pnl'])
        analysis.omega_ratio = self._calculate_omega_ratio(df['pnl'])
        
        # Ulcer Index
        if 'pnl' in df.columns:
            cumulative_pnl = df['pnl'].cumsum()
            analysis.ulcer_index = self._calculate_ulcer_index(cumulative_pnl)
            
            # Recovery Factor
            total_pnl = df['pnl'].sum()
            max_drawdown = self._calculate_max_drawdown(df)
            analysis.recovery_factor = self._calculate_recovery_factor(total_pnl, max_drawdown)
        
        return analysis
    
    def analyze_ml_performance(self,
                             predictions: pd.DataFrame,
                             actuals: pd.DataFrame) -> MLAnalysis:
        """
        Analyse la performance des modèles ML
        
        Args:
            predictions: Prédictions du modèle
            actuals: Résultats réels
            
        Returns:
            MLAnalysis avec métriques ML
        """
        analysis = MLAnalysis()
        
        if predictions.empty or actuals.empty:
            return analysis
        
        # Métriques de base
        try:
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        except ImportError:
            logger.warning("sklearn non disponible - métriques ML limitées")
            return analysis
        
        # Pour classification binaire (profitable/non profitable)
        if 'predicted_profitable' in predictions.columns and 'actual_profitable' in actuals.columns:
            y_pred = predictions['predicted_profitable']
            y_true = actuals['actual_profitable']
            
            analysis.model_accuracy = accuracy_score(y_true, y_pred)
            analysis.model_precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
            analysis.model_recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
            analysis.model_f1_score = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        # Feature importance (si disponible)
        if 'feature_importance' in predictions.columns:
            analysis.feature_importance = predictions['feature_importance'].iloc[0]
        
        # Performance vs baseline
        if 'ml_enhanced' in predictions.columns:
            ml_trades = predictions[predictions['ml_enhanced'] == True]
            baseline_trades = predictions[predictions['ml_enhanced'] == False]
            
            if not ml_trades.empty and 'profitable' in actuals.columns:
                ml_wins = len(ml_trades[actuals.loc[ml_trades.index, 'profitable'] == True])
                analysis.ml_enhanced_win_rate = ml_wins / len(ml_trades)
            
            if not baseline_trades.empty and 'profitable' in actuals.columns:
                baseline_wins = len(baseline_trades[actuals.loc[baseline_trades.index, 'profitable'] == True])
                analysis.baseline_win_rate = baseline_wins / len(baseline_trades)
            
            if analysis.baseline_win_rate > 0:
                analysis.improvement_percentage = (
                    (analysis.ml_enhanced_win_rate - analysis.baseline_win_rate) / 
                    analysis.baseline_win_rate * 100
                )
        
        # Distribution des prédictions
        if 'confidence_score' in predictions.columns:
            conf_bins = pd.cut(predictions['confidence_score'], bins=[0, 0.3, 0.5, 0.7, 0.9, 1.0])
            analysis.prediction_distribution = conf_bins.value_counts().to_dict()
            
            # Accuracy par niveau de confiance
            for conf_level in conf_bins.unique():
                if pd.notna(conf_level):
                    level_mask = conf_bins == conf_level
                    if level_mask.any() and 'actual_profitable' in actuals.columns:
                        level_acc = accuracy_score(
                            actuals.loc[level_mask, 'actual_profitable'],
                            predictions.loc[level_mask, 'predicted_profitable']
                        )
                        analysis.prediction_accuracy_by_confidence[str(conf_level)] = level_acc
        
        return analysis
    
    def generate_comprehensive_report(self,
                                    start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None,
                                    time_frame: TimeFrame = TimeFrame.ALL_TIME) -> AnalyticsReport:
        """
        Génère un rapport complet d'analyse
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            time_frame: Période d'analyse
            
        Returns:
            AnalyticsReport complet
        """
        # Chargement des données
        trades_df = self._load_trades_data(start_date, end_date)
        snapshots_df = self._load_snapshots_data(start_date, end_date)
        
        # Création du rapport
        report = AnalyticsReport(
            report_id=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            generated_at=datetime.now(timezone.utc),
            time_frame=time_frame,
            analysis_type=AnalysisType.COMPREHENSIVE,
            start_date=start_date or trades_df['timestamp'].min() if not trades_df.empty else datetime.now(),
            end_date=end_date or trades_df['timestamp'].max() if not trades_df.empty else datetime.now(),
            total_records=len(trades_df)
        )
        
        # Analyses
        if not trades_df.empty:
            report.performance = self.analyze_performance(trades_df, time_frame)
            report.risk = self.analyze_risk(trades_df)
        
        if not snapshots_df.empty:
            report.patterns = self.analyze_patterns(snapshots_df)
        
        # ML Analysis (si disponible)
        ml_data = self._load_ml_predictions()
        if ml_data is not None:
            predictions, actuals = ml_data
            report.ml_metrics = self.analyze_ml_performance(predictions, actuals)
        
        # Génération des insights
        report.insights = self._generate_insights(report)
        report.recommendations = self._generate_recommendations(report)
        report.warnings = self._generate_warnings(report)
        
        return report
    
    def save_report(self,
                   report: AnalyticsReport,
                   format: ReportFormat = ReportFormat.JSON) -> str:
        """
        Sauvegarde un rapport
        
        Args:
            report: Rapport à sauvegarder
            format: Format de sortie
            
        Returns:
            Chemin du fichier sauvegardé
        """
        filename = f"{report.report_id}.{format.value}"
        filepath = self.reports_dir / filename
        
        if format == ReportFormat.JSON:
            with open(filepath, 'w') as f:
                json.dump(asdict(report), f, indent=2, default=str)
                
        elif format == ReportFormat.CSV and report.performance:
            # Export des métriques principales en CSV
            metrics_dict = asdict(report.performance)
            df = pd.DataFrame([metrics_dict])
            df.to_csv(filepath, index=False)
            
        elif format == ReportFormat.MARKDOWN:
            markdown_content = self._generate_markdown_report(report)
            with open(filepath, 'w') as f:
                f.write(markdown_content)
        
        logger.info(f"Rapport sauvegardé: {filepath}")
        return str(filepath)
    
    def plot_performance(self,
                        trades: pd.DataFrame,
                        save_path: Optional[str] = None) -> Optional[plt.Figure]:
        """
        Génère des graphiques de performance
        
        Args:
            trades: DataFrame des trades
            save_path: Chemin pour sauvegarder
            
        Returns:
            Figure matplotlib ou None si plotting non disponible
        """
        if not PLOTTING_AVAILABLE:
            logger.warning("Matplotlib non disponible - pas de graphiques")
            return None
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Courbe de P&L cumulé
        ax1 = axes[0, 0]
        trades['cumulative_pnl'] = trades['pnl'].cumsum()
        ax1.plot(trades.index, trades['cumulative_pnl'])
        ax1.set_title('P&L Cumulé')
        ax1.set_xlabel('Trades')
        ax1.set_ylabel('P&L ($)')
        ax1.grid(True)
        
        # 2. Distribution des P&L
        ax2 = axes[0, 1]
        ax2.hist(trades['pnl'], bins=30, alpha=0.7, color='blue')
        ax2.axvline(trades['pnl'].mean(), color='red', linestyle='--', label='Moyenne')
        ax2.set_title('Distribution des P&L')
        ax2.set_xlabel('P&L ($)')
        ax2.set_ylabel('Fréquence')
        ax2.legend()
        
        # 3. Win Rate par session
        ax3 = axes[1, 0]
        if 'session' in trades.columns:
            session_stats = trades.groupby('session').agg({
                'pnl': lambda x: (x > 0).mean()
            }).sort_values('pnl', ascending=False)
            
            ax3.bar(session_stats.index, session_stats['pnl'])
            ax3.set_title('Win Rate par Session')
            ax3.set_xlabel('Session')
            ax3.set_ylabel('Win Rate')
            ax3.set_ylim(0, 1)
        
        # 4. Performance par heure
        ax4 = axes[1, 1]
        if 'timestamp' in trades.columns:
            trades['hour'] = pd.to_datetime(trades['timestamp']).dt.hour
            hourly_stats = trades.groupby('hour')['pnl'].mean()
            
            ax4.plot(hourly_stats.index, hourly_stats.values, marker='o')
            ax4.set_title('P&L Moyen par Heure')
            ax4.set_xlabel('Heure')
            ax4.set_ylabel('P&L Moyen ($)')
            ax4.set_xticks(range(0, 24, 2))
            ax4.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Graphiques sauvegardés: {save_path}")
        
        return fig
    
    # === MÉTHODES PRIVÉES ===
    
    def _filter_by_timeframe(self, df: pd.DataFrame, time_frame: TimeFrame) -> pd.DataFrame:
        """Filtre DataFrame par période"""
        if time_frame == TimeFrame.ALL_TIME or 'timestamp' not in df.columns:
            return df
        
        now = datetime.now(timezone.utc)
        
        if time_frame == TimeFrame.DAILY:
            cutoff = now - timedelta(days=1)
        elif time_frame == TimeFrame.WEEKLY:
            cutoff = now - timedelta(weeks=1)
        elif time_frame == TimeFrame.MONTHLY:
            cutoff = now - timedelta(days=30)
        elif time_frame == TimeFrame.QUARTERLY:
            cutoff = now - timedelta(days=90)
        elif time_frame == TimeFrame.YEARLY:
            cutoff = now - timedelta(days=365)
        else:
            return df
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df[df['timestamp'] >= cutoff]
    
    def _calculate_max_drawdown(self, df: pd.DataFrame) -> float:
        """Calcule le drawdown maximum"""
        if 'pnl' not in df.columns:
            return 0.0
        
        cumulative = df['pnl'].cumsum()
        running_max = cumulative.expanding().max()
        drawdown = cumulative - running_max
        
        return abs(drawdown.min()) if not drawdown.empty else 0.0
    
    def _calculate_sharpe_ratio(self, df: pd.DataFrame, risk_free_rate: float = 0.02) -> float:
        """Calcule le ratio de Sharpe"""
        if 'pnl' not in df.columns or len(df) < 2:
            return 0.0
        
        returns = df['pnl'].values
        if returns.std() == 0:
            return 0.0
        
        # Annualisé (252 jours de trading)
        sharpe = (returns.mean() - risk_free_rate/252) / returns.std() * np.sqrt(252)
        return sharpe
    
    def _calculate_sortino_ratio(self, df: pd.DataFrame, risk_free_rate: float = 0.02) -> float:
        """Calcule le ratio de Sortino"""
        if 'pnl' not in df.columns or len(df) < 2:
            return 0.0
        
        returns = df['pnl'].values
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        # Annualisé
        sortino = (returns.mean() - risk_free_rate/252) / downside_returns.std() * np.sqrt(252)
        return sortino
    
    def _max_consecutive_wins(self, df: pd.DataFrame) -> int:
        """Calcule le nombre maximum de gains consécutifs"""
        if 'pnl' not in df.columns:
            return 0
        
        wins = (df['pnl'] > 0).astype(int)
        groups = (wins != wins.shift()).cumsum()
        consecutive = wins.groupby(groups).sum()
        
        return consecutive.max() if not consecutive.empty else 0
    
    def _max_consecutive_losses(self, df: pd.DataFrame) -> int:
        """Calcule le nombre maximum de pertes consécutives"""
        if 'pnl' not in df.columns:
            return 0
        
        losses = (df['pnl'] < 0).astype(int)
        groups = (losses != losses.shift()).cumsum()
        consecutive = losses.groupby(groups).sum()
        
        return consecutive.max() if not consecutive.empty else 0
    
    # === NOUVELLES MÉTHODES AVANCÉES ===
    
    def _calculate_tail_ratio(self, returns: pd.Series, percentile: float = 95) -> float:
        """
        Calcule le Tail Ratio (mesure l'asymétrie des queues de distribution)
        
        Args:
            returns: Série des retours
            percentile: Percentile pour les queues (défaut 95%)
            
        Returns:
            Tail ratio (>1 = plus de gains extrêmes que de pertes extrêmes)
        """
        if len(returns) < 10:
            return 1.0
        
        # Percentiles pour les queues
        upper_tail = np.percentile(returns, percentile)
        lower_tail = np.percentile(returns, 100 - percentile)
        
        # Éviter division par zéro
        if abs(lower_tail) < 0.0001:
            return float('inf') if upper_tail > 0 else 1.0
        
        return abs(upper_tail / lower_tail)
    
    def _calculate_omega_ratio(self, returns: pd.Series, threshold: float = 0) -> float:
        """
        Calcule l'Omega Ratio (ratio gains/pertes par rapport à un seuil)
        
        Args:
            returns: Série des retours
            threshold: Seuil de rendement minimum acceptable
            
        Returns:
            Omega ratio (>1 = stratégie profitable)
        """
        if len(returns) == 0:
            return 1.0
        
        # Gains et pertes par rapport au seuil
        gains = returns[returns > threshold] - threshold
        losses = threshold - returns[returns <= threshold]
        
        # Sommes
        total_gains = gains.sum() if len(gains) > 0 else 0
        total_losses = losses.sum() if len(losses) > 0 else 0
        
        # Éviter division par zéro
        if total_losses == 0:
            return float('inf') if total_gains > 0 else 1.0
        
        return total_gains / total_losses
    
    def _calculate_ulcer_index(self, cumulative_returns: pd.Series) -> float:
        """
        Calcule l'Ulcer Index (mesure la profondeur et durée des drawdowns)
        
        Args:
            cumulative_returns: Série des retours cumulés
            
        Returns:
            Ulcer Index (plus bas = meilleur)
        """
        if len(cumulative_returns) < 2:
            return 0.0
        
        # Calcul du drawdown en pourcentage
        rolling_max = cumulative_returns.expanding().max()
        drawdown_pct = ((cumulative_returns - rolling_max) / rolling_max * 100)
        
        # Ulcer Index = racine carrée de la moyenne des drawdowns au carré
        ulcer_index = np.sqrt((drawdown_pct ** 2).mean())
        
        return ulcer_index
    
    def _calculate_recovery_factor(self, total_pnl: float, max_drawdown: float) -> float:
        """
        Calcule le Recovery Factor (capacité de récupération après drawdown)
        
        Args:
            total_pnl: P&L total
            max_drawdown: Drawdown maximum
            
        Returns:
            Recovery Factor
        """
        if max_drawdown == 0:
            return float('inf') if total_pnl > 0 else 0
        
        return abs(total_pnl / max_drawdown)
    
    def _analyze_time_of_day_pattern(self, snapshots_df: pd.DataFrame) -> Optional[Dict]:
        """
        Analyse détaillée des patterns par heure de la journée
        
        Args:
            snapshots_df: DataFrame des snapshots
            
        Returns:
            Dict avec analyse temporelle ou None
        """
        if snapshots_df.empty or 'timestamp' not in snapshots_df.columns:
            return None
        
        # Conversion timestamps
        snapshots_df['timestamp'] = pd.to_datetime(snapshots_df['timestamp'])
        snapshots_df['hour'] = snapshots_df['timestamp'].dt.hour
        snapshots_df['minute'] = snapshots_df['timestamp'].dt.minute
        snapshots_df['time_of_day'] = snapshots_df['hour'] + snapshots_df['minute'] / 60
        
        # Analyse par heure
        hourly_analysis = {}
        
        for hour in range(24):
            hour_data = snapshots_df[snapshots_df['hour'] == hour]
            
            if len(hour_data) > 0:
                hourly_analysis[hour] = {
                    'trade_count': len(hour_data),
                    'win_rate': len(hour_data[hour_data.get('pnl', 0) > 0]) / len(hour_data) if 'pnl' in hour_data else 0,
                    'avg_pnl': hour_data['pnl'].mean() if 'pnl' in hour_data else 0,
                    'volatility': hour_data['pnl'].std() if 'pnl' in hour_data else 0,
                    'signal_strength': hour_data['signal_strength'].mean() if 'signal_strength' in hour_data else 0
                }
        
        # Identification des meilleures périodes
        best_hours_by_pnl = sorted(hourly_analysis.items(), 
                                  key=lambda x: x[1]['avg_pnl'], 
                                  reverse=True)[:3]
        
        best_hours_by_winrate = sorted(hourly_analysis.items(), 
                                      key=lambda x: x[1]['win_rate'], 
                                      reverse=True)[:3]
        
        return {
            'hourly_stats': hourly_analysis,
            'best_hours_pnl': [h[0] for h in best_hours_by_pnl],
            'best_hours_winrate': [h[0] for h in best_hours_by_winrate],
            'most_active_hours': sorted(hourly_analysis.items(), 
                                      key=lambda x: x[1]['trade_count'], 
                                      reverse=True)[:3]
        }
    
    def _analyze_volatility_pattern(self, snapshots_df: pd.DataFrame) -> Optional[Dict]:
        """
        Analyse les patterns selon les régimes de volatilité
        
        Args:
            snapshots_df: DataFrame des snapshots
            
        Returns:
            Dict avec analyse volatilité ou None
        """
        if snapshots_df.empty or 'atr_14' not in snapshots_df.columns:
            return None
        
        # Classification des régimes de volatilité
        volatility_percentiles = snapshots_df['atr_14'].quantile([0.33, 0.67])
        
        def classify_volatility(atr):
            if atr <= volatility_percentiles[0.33]:
                return 'low'
            elif atr <= volatility_percentiles[0.67]:
                return 'medium'
            else:
                return 'high'
        
        snapshots_df['volatility_regime'] = snapshots_df['atr_14'].apply(classify_volatility)
        
        # Analyse par régime
        regime_analysis = {}
        
        for regime in ['low', 'medium', 'high']:
            regime_data = snapshots_df[snapshots_df['volatility_regime'] == regime]
            
            if len(regime_data) > 0:
                regime_analysis[regime] = {
                    'count': len(regime_data),
                    'avg_atr': regime_data['atr_14'].mean(),
                    'win_rate': len(regime_data[regime_data.get('pnl', 0) > 0]) / len(regime_data) if 'pnl' in regime_data else 0,
                    'avg_pnl': regime_data['pnl'].mean() if 'pnl' in regime_data else 0,
                    'avg_signal_strength': regime_data['signal_strength'].mean() if 'signal_strength' in regime_data else 0,
                    'best_patterns': self._get_best_patterns_for_regime(regime_data)
                }
        
        return {
            'regime_stats': regime_analysis,
            'optimal_regime': max(regime_analysis.items(), 
                                key=lambda x: x[1]['avg_pnl']) if regime_analysis else None
        }
    
    def _analyze_signal_strength_pattern(self, snapshots_df: pd.DataFrame) -> Optional[Dict]:
        """
        Analyse la performance selon la force des signaux
        
        Args:
            snapshots_df: DataFrame des snapshots
            
        Returns:
            Dict avec analyse signal strength ou None
        """
        if snapshots_df.empty or 'signal_strength' not in snapshots_df.columns:
            return None
        
        # Bins pour signal strength
        strength_bins = pd.cut(snapshots_df['signal_strength'], 
                             bins=[0, 0.3, 0.5, 0.7, 0.9, 1.0],
                             labels=['very_weak', 'weak', 'medium', 'strong', 'very_strong'])
        
        snapshots_df['strength_category'] = strength_bins
        
        # Analyse par catégorie
        strength_analysis = {}
        
        for category in ['very_weak', 'weak', 'medium', 'strong', 'very_strong']:
            cat_data = snapshots_df[snapshots_df['strength_category'] == category]
            
            if len(cat_data) > 0:
                strength_analysis[category] = {
                    'count': len(cat_data),
                    'avg_strength': cat_data['signal_strength'].mean(),
                    'win_rate': len(cat_data[cat_data.get('pnl', 0) > 0]) / len(cat_data) if 'pnl' in cat_data else 0,
                    'avg_pnl': cat_data['pnl'].mean() if 'pnl' in cat_data else 0,
                    'risk_reward': self._calculate_avg_risk_reward(cat_data)
                }
        
        # Corrélation signal strength vs performance
        if 'pnl' in snapshots_df.columns:
            correlation = snapshots_df['signal_strength'].corr(snapshots_df['pnl'])
        else:
            correlation = 0
        
        return {
            'strength_stats': strength_analysis,
            'correlation': correlation,
            'optimal_threshold': self._find_optimal_signal_threshold(snapshots_df)
        }
    
    def _analyze_streak_patterns(self, snapshots_df: pd.DataFrame) -> List[Dict]:
        """
        Analyse détaillée des séries de gains/pertes
        
        Args:
            snapshots_df: DataFrame des snapshots
            
        Returns:
            Liste des patterns de streaks
        """
        patterns = []
        
        if snapshots_df.empty or 'pnl' not in snapshots_df.columns:
            return patterns
        
        # Identification des streaks
        snapshots_df['is_win'] = snapshots_df['pnl'] > 0
        snapshots_df['streak_group'] = (snapshots_df['is_win'] != snapshots_df['is_win'].shift()).cumsum()
        
        # Analyse des streaks
        for group_id, group_data in snapshots_df.groupby('streak_group'):
            if len(group_data) >= 3:  # Streaks d'au moins 3 trades
                is_winning_streak = group_data['is_win'].iloc[0]
                
                pattern = {
                    'type': PatternType.WINNING_STREAK if is_winning_streak else PatternType.LOSING_STREAK,
                    'length': len(group_data),
                    'total_pnl': group_data['pnl'].sum(),
                    'avg_pnl': group_data['pnl'].mean(),
                    'start_time': group_data['timestamp'].iloc[0] if 'timestamp' in group_data else None,
                    'end_time': group_data['timestamp'].iloc[-1] if 'timestamp' in group_data else None,
                    'confidence': min(0.5 + (len(group_data) - 3) * 0.1, 0.9),
                    'performance_impact': group_data['pnl'].sum() / snapshots_df['pnl'].sum() if snapshots_df['pnl'].sum() != 0 else 0
                }
                
                patterns.append(pattern)
        
        return patterns
    
    # === MÉTHODES HELPER ===
    
    def _calculate_streaks(self, pnl_series: pd.Series) -> Dict[str, int]:
        """
        Calcule les séries de gains/pertes
        
        Args:
            pnl_series: Série des P&L
            
        Returns:
            Dict avec max wins et max losses consécutifs
        """
        if len(pnl_series) == 0:
            return {'max_wins': 0, 'max_losses': 0}
        
        # Identification wins/losses
        is_win = pnl_series > 0
        
        # Groupes de streaks
        streak_groups = (is_win != is_win.shift()).cumsum()
        
        # Calcul des longueurs
        max_wins = 0
        max_losses = 0
        
        for _, group in pnl_series.groupby(streak_groups):
            if len(group) > 0:
                if group.iloc[0] > 0:
                    max_wins = max(max_wins, len(group))
                else:
                    max_losses = max(max_losses, len(group))
        
        return {'max_wins': max_wins, 'max_losses': max_losses}
    
    def _calculate_kelly_criterion(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """
        Calcule le Kelly Criterion pour le sizing optimal
        
        Args:
            win_rate: Taux de victoire
            avg_win: Gain moyen
            avg_loss: Perte moyenne (valeur absolue)
            
        Returns:
            Fraction Kelly (cappée à 25%)
        """
        if avg_loss == 0 or avg_win == 0:
            return 0.0
        
        # Formule Kelly : f = (p*b - q) / b
        # où p = win_rate, q = 1-p, b = avg_win/avg_loss
        b = avg_win / avg_loss
        f = (win_rate * b - (1 - win_rate)) / b
        
        # Cap conservateur à 25%
        return max(0, min(0.25, f))
    
    def _get_best_patterns_for_regime(self, regime_data: pd.DataFrame) -> List[str]:
        """
        Trouve les meilleurs patterns pour un régime donné
        
        Args:
            regime_data: Données du régime
            
        Returns:
            Liste des meilleurs patterns
        """
        if 'pattern_type' not in regime_data.columns or 'pnl' not in regime_data.columns:
            return []
        
        pattern_perf = regime_data.groupby('pattern_type')['pnl'].agg(['mean', 'count'])
        pattern_perf = pattern_perf[pattern_perf['count'] >= 3]  # Au moins 3 occurrences
        
        if pattern_perf.empty:
            return []
        
        return pattern_perf.nlargest(3, 'mean').index.tolist()
    
    def _calculate_avg_risk_reward(self, data: pd.DataFrame) -> float:
        """
        Calcule le ratio risk/reward moyen
        
        Args:
            data: DataFrame avec stop_loss et take_profit
            
        Returns:
            Ratio risk/reward moyen
        """
        if 'stop_loss' not in data.columns or 'take_profit' not in data.columns:
            return 0.0
        
        if 'entry_price' in data.columns:
            risk = abs(data['entry_price'] - data['stop_loss'])
            reward = abs(data['take_profit'] - data['entry_price'])
            
            valid_ratios = reward / risk
            valid_ratios = valid_ratios[valid_ratios.notna() & (valid_ratios != np.inf)]
            
            return valid_ratios.mean() if len(valid_ratios) > 0 else 0.0
        
        return 0.0
    
    def _find_optimal_signal_threshold(self, snapshots_df: pd.DataFrame) -> float:
        """
        Trouve le seuil optimal de signal strength
        
        Args:
            snapshots_df: DataFrame des snapshots
            
        Returns:
            Seuil optimal
        """
        if 'signal_strength' not in snapshots_df.columns or 'pnl' not in snapshots_df.columns:
            return 0.5
        
        # Test différents seuils
        thresholds = np.arange(0.3, 0.9, 0.05)
        best_threshold = 0.5
        best_expectancy = 0
        
        for threshold in thresholds:
            filtered = snapshots_df[snapshots_df['signal_strength'] >= threshold]
            
            if len(filtered) >= 10:  # Au moins 10 trades
                win_rate = len(filtered[filtered['pnl'] > 0]) / len(filtered)
                avg_win = filtered[filtered['pnl'] > 0]['pnl'].mean() if any(filtered['pnl'] > 0) else 0
                avg_loss = abs(filtered[filtered['pnl'] < 0]['pnl'].mean()) if any(filtered['pnl'] < 0) else 0
                
                expectancy = win_rate * avg_win - (1 - win_rate) * avg_loss
                
                if expectancy > best_expectancy:
                    best_expectancy = expectancy
                    best_threshold = threshold
        
        return best_threshold
    
    def _load_trades_data(self, 
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Charge les données de trades"""
        # Implémentation dépend de votre stockage
        # Pour l'instant, retourne DataFrame vide
        return pd.DataFrame()
    
    def _load_snapshots_data(self,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Charge les snapshots"""
        # Implémentation dépend de votre stockage
        # Pour l'instant, retourne DataFrame vide
        return pd.DataFrame()
    
    def _load_ml_predictions(self) -> Optional[Tuple[pd.DataFrame, pd.DataFrame]]:
        """Charge les prédictions ML si disponibles"""
        # Implémentation dépend de votre stockage ML
        return None
    
    def _generate_insights(self, report: AnalyticsReport) -> List[str]:
        """Génère des insights basés sur l'analyse"""
        insights = []
        
        if report.performance:
            perf = report.performance
            
            if perf.win_rate > 0.6:
                insights.append(f"Excellent win rate de {perf.win_rate:.1%}")
            
            if perf.profit_factor > 2:
                insights.append(f"Profit factor robuste de {perf.profit_factor:.2f}")
            
            if perf.sharpe_ratio > 1.5:
                insights.append(f"Ratio de Sharpe élevé de {perf.sharpe_ratio:.2f}")
            
            # Sessions
            if perf.performance_by_session:
                best_session = max(perf.performance_by_session.items(), 
                                 key=lambda x: x[1].get('win_rate', 0))
                insights.append(f"Meilleure performance en session {best_session[0]}")
        
        if report.patterns:
            patterns = report.patterns
            
            if patterns.pattern_frequency:
                most_common = max(patterns.pattern_frequency.items(), key=lambda x: x[1])
                insights.append(f"Pattern le plus fréquent: {most_common[0]} ({most_common[1]} fois)")
            
            if patterns.best_hours:
                insights.append(f"Meilleures heures de trading: {patterns.best_hours}")
            
            # Insights patterns avancés
            if patterns.time_patterns and 'optimal_threshold' in patterns.signal_strength_patterns:
                threshold = patterns.signal_strength_patterns['optimal_threshold']
                insights.append(f"Seuil optimal de signal strength: {threshold:.2f}")
        
        if report.risk:
            risk = report.risk
            
            if risk.tail_ratio > 1.5:
                insights.append(f"Tail ratio favorable de {risk.tail_ratio:.2f}")
            
            if risk.omega_ratio > 1.5:
                insights.append(f"Omega ratio excellent de {risk.omega_ratio:.2f}")
        
        return insights
    
    def _generate_recommendations(self, report: AnalyticsReport) -> List[str]:
        """Génère des recommandations"""
        recommendations = []
        
        if report.performance:
            perf = report.performance
            
            if perf.win_rate < 0.5:
                recommendations.append("Améliorer les critères d'entrée - win rate < 50%")
            
            if perf.average_loss > perf.average_win * 1.5:
                recommendations.append("Revoir le risk management - pertes moyennes trop élevées")
            
            if perf.max_drawdown > 0.2 * abs(perf.total_pnl):
                recommendations.append("Drawdown élevé - considérer réduction taille positions")
        
        if report.risk:
            risk = report.risk
            
            if risk.kelly_fraction < 0.1:
                recommendations.append("Kelly fraction faible - stratégie peu profitable")
            
            if risk.risk_reward_ratio < 1.5:
                recommendations.append("Améliorer ratio risk/reward (cible minimum 1.5)")
            
            if risk.tail_ratio < 1:
                recommendations.append("Tail ratio défavorable - plus de pertes extrêmes que de gains")
        
        if report.patterns:
            patterns = report.patterns
            
            # Recommandations basées sur les patterns temporels
            if patterns.time_patterns and 'best_hours_pnl' in patterns.time_patterns:
                best_hours = patterns.time_patterns['best_hours_pnl']
                recommendations.append(f"Concentrer le trading sur les heures {best_hours}")
            
            # Recommandations volatilité
            if patterns.volatility_patterns and 'optimal_regime' in patterns.volatility_patterns:
                optimal = patterns.volatility_patterns['optimal_regime']
                if optimal:
                    recommendations.append(f"Privilégier le régime de volatilité '{optimal[0]}'")
        
        if report.ml_metrics:
            ml = report.ml_metrics
            
            if ml.improvement_percentage < 5:
                recommendations.append("Optimiser modèle ML - amélioration < 5%")
        
        return recommendations
    
    def _generate_warnings(self, report: AnalyticsReport) -> List[str]:
        """Génère des warnings"""
        warnings = []
        
        if report.performance:
            perf = report.performance
            
            if perf.consecutive_losses > 5:
                warnings.append(f"⚠️ {perf.consecutive_losses} pertes consécutives détectées")
            
            if perf.max_drawdown > 0.3 * abs(perf.total_pnl):
                warnings.append(f"⚠️ Drawdown critique: {perf.max_drawdown:.2f}")
        
        if report.risk:
            risk = report.risk
            
            if risk.ulcer_index > 10:
                warnings.append(f"⚠️ Ulcer Index élevé: {risk.ulcer_index:.1f}")
        
        if report.total_records < 30:
            warnings.append("⚠️ Échantillon limité - résultats peu fiables")
        
        return warnings
    
    def _generate_markdown_report(self, report: AnalyticsReport) -> str:
        """Génère un rapport au format Markdown"""
        md = f"""# Rapport d'Analyse Trading - {report.report_id}

**Généré le:** {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}  
**Période:** {report.start_date.strftime('%Y-%m-%d')} à {report.end_date.strftime('%Y-%m-%d')}  
**Nombre de trades:** {report.total_records}

## 📊 Performance

"""
        if report.performance:
            perf = report.performance
            md += f"""
- **Trades gagnants:** {perf.winning_trades} ({perf.win_rate:.1%})
- **Trades perdants:** {perf.losing_trades}
- **P&L Total:** ${perf.total_pnl:,.2f}
- **Profit Factor:** {perf.profit_factor:.2f}
- **Sharpe Ratio:** {perf.sharpe_ratio:.2f}
- **Max Drawdown:** ${perf.max_drawdown:,.2f}
"""

        if report.risk:
            risk = report.risk
            md += f"""
## 📉 Analyse de Risque

- **VaR 95%:** ${risk.var_95:,.2f}
- **CVaR 95%:** ${risk.cvar_95:,.2f}
- **Kelly Fraction:** {risk.kelly_fraction:.2%}
- **Tail Ratio:** {risk.tail_ratio:.2f}
- **Omega Ratio:** {risk.omega_ratio:.2f}
- **Risk/Reward Ratio:** {risk.risk_reward_ratio:.2f}
"""

        if report.insights:
            md += "\n## 💡 Insights\n\n"
            for insight in report.insights:
                md += f"- {insight}\n"
        
        if report.recommendations:
            md += "\n## 🎯 Recommandations\n\n"
            for rec in report.recommendations:
                md += f"- {rec}\n"
        
        if report.warnings:
            md += "\n## ⚠️ Avertissements\n\n"
            for warning in report.warnings:
                md += f"- {warning}\n"
        
        return md

# === FACTORY FUNCTIONS ===

def create_data_analytics() -> DataAnalytics:
    """Crée une instance DataAnalytics"""
    return DataAnalytics()

def generate_performance_report(trades: Union[List[Dict], pd.DataFrame],
                              format: ReportFormat = ReportFormat.JSON) -> str:
    """
    Génère rapidement un rapport de performance
    
    Args:
        trades: Données de trading
        format: Format du rapport
        
    Returns:
        Chemin du fichier généré
    """
    analytics = create_data_analytics()
    
    # Analyse
    if isinstance(trades, list):
        trades_df = pd.DataFrame(trades)
    else:
        trades_df = trades
    
    report = analytics.generate_comprehensive_report()
    
    # Sauvegarde
    filepath = analytics.save_report(report, format)
    
    return filepath

# === TESTS ===

def test_data_analytics():
    """Test du module analytics"""
    logger.info("=== TEST DATA ANALYTICS ===")
    
    # Création instance
    analytics = create_data_analytics()
    print("✅ DataAnalytics créé")
    
    # Données test
    test_trades = [
        {
            'timestamp': datetime.now() - timedelta(hours=i),
            'symbol': 'ES',
            'pnl': np.random.normal(50, 100),
            'session': 'NY_MORNING' if i % 2 == 0 else 'LONDON',
            'pattern_type': 'BATTLE_NAVALE' if i % 3 == 0 else 'CONFLUENCE',
            'confluence_score': np.random.uniform(0.3, 0.9),
            'battle_strength': np.random.uniform(0.4, 1.0),
            'signal_strength': np.random.uniform(0.3, 1.0),
            'atr_14': np.random.uniform(10, 30),
            'entry_price': 4500 + np.random.uniform(-50, 50),
            'stop_loss': 4500 + np.random.uniform(-100, -50),
            'take_profit': 4500 + np.random.uniform(50, 100)
        }
        for i in range(50)
    ]
    
    # Test analyse performance
    perf_metrics = analytics.analyze_performance(test_trades)
    print(f"✅ Performance analysée: {perf_metrics.total_trades} trades, "
          f"win rate {perf_metrics.win_rate:.1%}")
    
    # Test analyse patterns
    pattern_analysis = analytics.analyze_patterns(test_trades)
    print(f"✅ Patterns analysés: {len(pattern_analysis.pattern_frequency)} types")
    
    # Test analyse risk avec nouvelles métriques
    risk_analysis = analytics.analyze_risk(test_trades)
    print(f"✅ Risk analysé: Tail Ratio {risk_analysis.tail_ratio:.2f}, "
          f"Omega Ratio {risk_analysis.omega_ratio:.2f}")
    
    # Test patterns avancés
    if pattern_analysis.time_patterns:
        print(f"✅ Time patterns analysés: {len(pattern_analysis.time_patterns.get('hourly_stats', {}))} heures")
    
    if pattern_analysis.volatility_patterns:
        print(f"✅ Volatility patterns analysés: {len(pattern_analysis.volatility_patterns.get('regime_stats', {}))} régimes")
    
    # Test rapport complet
    report = analytics.generate_comprehensive_report()
    print(f"✅ Rapport généré: {report.report_id}")
    
    # Test sauvegarde
    filepath = analytics.save_report(report, ReportFormat.JSON)
    print(f"✅ Rapport sauvegardé: {filepath}")
    
    # Test rapport Markdown
    md_filepath = analytics.save_report(report, ReportFormat.MARKDOWN)
    print(f"✅ Rapport Markdown sauvegardé: {md_filepath}")
    
    logger.info("=== TEST TERMINÉ ===")

# === EXPORTS ===

__all__ = [
    # Classes principales
    'DataAnalytics',
    
    # Data structures
    'PerformanceMetrics',
    'PatternAnalysis',
    'RiskAnalysis',
    'MLAnalysis',
    'AnalyticsReport',
    
    # Enums
    'AnalysisType',
    'ReportFormat',
    'TimeFrame',
    'PatternType',
    
    # Factory functions
    'create_data_analytics',
    'generate_performance_report',
    
    # Test
    'test_data_analytics'
]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_data_analytics()