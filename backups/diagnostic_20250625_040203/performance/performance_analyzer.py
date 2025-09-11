#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Performance Analyzer
📊 ANALYSE AUTO des trades pour identifier ce qui marche

Version: Phase 3B - Auto-Improvement Focus  
Responsabilité: Analyse intelligence des patterns & optimisation automatique

FONCTIONNALITÉS CRITIQUES :
1. 🎯 Analyse Strategy Performance - TREND vs RANGE optimisation
2. 🏆 Best Setups Detection - Patterns gagnants automatique  
3. 📈 Features Attribution - Quelles features sont predictives
4. ⏰ Time Analysis - Sessions/heures optimales
5. 🔍 Edge Metrics - Win rate, Profit Factor par contexte
6. 💡 Auto Suggestions - Optimisations basées données

WORKFLOW ANALYSE :
Trades Data → Segmentation → Pattern Analysis → Edge Calculation → Suggestions

ANALYSES FOURNIES :
- Performance par Strategy Mode (TREND/RANGE/BREAKOUT)
- Performance par Pattern Type (Battle Navale/Gamma Pin/Headfake)
- Performance par Features Combination
- Performance par Time of Day/Session
- Identification automatique best setups
- Métriques edge détaillées
"""

import os
import json
import time
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from datetime import datetime, timezone, date, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from enum import Enum
import statistics

# Local imports
from core.base_types import TradingSignal, TradeResult
from config.automation_config import get_automation_config

logger = logging.getLogger(__name__)

# === ANALYSIS ENUMS ===

class AnalysisType(Enum):
    """Types d'analyses performance"""
    STRATEGY_MODE = "strategy_mode"
    PATTERN_TYPE = "pattern_type"  
    FEATURES_COMBO = "features_combo"
    TIME_ANALYSIS = "time_analysis"
    SESSION_ANALYSIS = "session_analysis"
    EDGE_METRICS = "edge_metrics"

class PerformanceLevel(Enum):
    """Niveaux de performance"""
    EXCELLENT = "excellent"    # 70%+ win rate
    STRONG = "strong"         # 60-70% win rate  
    MODERATE = "moderate"     # 50-60% win rate
    WEAK = "weak"            # 40-50% win rate
    POOR = "poor"            # <40% win rate

class OptimizationType(Enum):
    """Types d'optimisations suggérées"""
    FEATURE_WEIGHTS = "feature_weights"
    STOP_DISTANCES = "stop_distances"
    CONFIDENCE_THRESHOLDS = "confidence_thresholds"
    PATTERN_SENSITIVITY = "pattern_sensitivity"
    TIME_FILTERS = "time_filters"

# === PERFORMANCE DATA STRUCTURES ===

@dataclass
class PerformanceMetrics:
    """Métriques de performance standardisées"""
    total_trades: int = 0
    profitable_trades: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    average_win: float = 0.0
    average_loss: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    edge_score: float = 0.0

@dataclass  
class SetupAnalysis:
    """Analyse d'un setup spécifique"""
    setup_name: str
    performance: PerformanceMetrics
    sample_size: int
    confidence_level: float
    best_conditions: List[str]
    worst_conditions: List[str]
    optimization_suggestions: List[str]

class PerformanceAnalyzer:
    """
    PERFORMANCE ANALYZER - Analyse automatique des trades
    
    Responsabilités :
    1. Analyse performance par strategy mode, patterns, features
    2. Identification automatique des meilleurs setups
    3. Calcul edge metrics par contexte  
    4. Génération suggestions d'optimisation
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialisation Performance Analyzer
        
        Args:
            config: Configuration optionnelle
        """
        self.config = config or get_automation_config()
        
        # Storage paths
        self.base_path = Path("data/performance/analysis")
        self.trades_path = Path("data/performance/logs")
        self.reports_path = self.base_path / "reports"
        
        # Création directories
        for path in [self.base_path, self.reports_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Data storage
        self.trades_data: Optional[pd.DataFrame] = None
        self.analysis_cache: Dict[str, Any] = {}
        self.performance_history: List[Dict] = []
        
        # Analysis config
        self.min_sample_size = 10
        self.confidence_threshold = 0.95
        self.edge_threshold = 0.6  # Win rate minimum pour "edge"
        
        # Performance tracking
        self.last_analysis_time = None
        self.analysis_results: Dict[str, Any] = {}
        
        logger.info(f"PerformanceAnalyzer initialisé: {self.base_path}")
    
    def analyze_strategy_performance(self, lookback_days: int = 30) -> Dict[str, Any]:
        """
        ANALYSE PERFORMANCE PAR STRATEGY MODE
        
        Analyse performance par :
        - Strategy mode (TREND vs RANGE vs BREAKOUT)
        - Pattern type (Battle navale vs Gamma pin vs Headfake)  
        - Features combination effectiveness
        - Time of day / session optimal
        
        Args:
            lookback_days: Période d'analyse en jours
            
        Returns:
            Dict: Analyse complète performance
        """
        try:
            start_time = time.perf_counter()
            
            # Chargement données
            if not self._load_trades_data(lookback_days):
                return {'error': 'Pas de données disponibles'}
            
            analysis_results = {
                'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                'lookback_days': lookback_days,
                'total_trades_analyzed': len(self.trades_data)
            }
            
            # 1. Analyse par Strategy Mode
            strategy_analysis = self._analyze_by_strategy_mode()
            analysis_results['strategy_performance'] = strategy_analysis
            
            # 2. Analyse par Pattern Type
            pattern_analysis = self._analyze_by_pattern_type()
            analysis_results['pattern_performance'] = pattern_analysis
            
            # 3. Analyse Features Combinations
            features_analysis = self._analyze_features_combinations()
            analysis_results['features_effectiveness'] = features_analysis
            
            # 4. Analyse temporelle
            time_analysis = self._analyze_time_patterns()
            analysis_results['time_analysis'] = time_analysis
            
            # 5. Calcul Edge Metrics
            edge_metrics = self._calculate_edge_metrics()
            analysis_results['edge_metrics'] = edge_metrics
            
            # Performance timing
            analysis_time = (time.perf_counter() - start_time) * 1000
            analysis_results['analysis_time_ms'] = analysis_time
            
            # Cache results
            self.analysis_results = analysis_results
            self.last_analysis_time = datetime.now(timezone.utc)
            
            logger.info(f"Analyse strategy performance terminée ({analysis_time:.1f}ms)")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Erreur analyze_strategy_performance: {e}")
            return {'error': str(e)}
    
    def identify_best_setups(self, min_edge: float = 0.65) -> Dict[str, SetupAnalysis]:
        """
        IDENTIFICATION AUTOMATIQUE MEILLEURS SETUPS
        
        Trouve automatiquement :
        - Quels patterns gagnent le plus
        - Quelles features sont predictives  
        - Quels régimes/contextes optimaux
        
        Args:
            min_edge: Edge minimum requis (win rate)
            
        Returns:
            Dict: Meilleurs setups identifiés
        """
        try:
            if self.trades_data is None:
                self._load_trades_data()
            
            best_setups = {}
            
            # 1. Setups par Strategy Mode
            strategy_setups = self._find_best_strategy_setups(min_edge)
            best_setups.update(strategy_setups)
            
            # 2. Setups par Pattern
            pattern_setups = self._find_best_pattern_setups(min_edge)  
            best_setups.update(pattern_setups)
            
            # 3. Setups par Features Combination
            feature_setups = self._find_best_feature_setups(min_edge)
            best_setups.update(feature_setups)
            
            # 4. Setups par Time Window
            time_setups = self._find_best_time_setups(min_edge)
            best_setups.update(time_setups)
            
            # Tri par performance
            sorted_setups = dict(sorted(
                best_setups.items(),
                key=lambda x: x[1].performance.edge_score,
                reverse=True
            ))
            
            logger.info(f"Identifié {len(sorted_setups)} setups avec edge ≥ {min_edge}")
            return sorted_setups
            
        except Exception as e:
            logger.error(f"Erreur identify_best_setups: {e}")
            return {}
    
    def generate_optimization_suggestions(self) -> Dict[str, List[str]]:
        """
        GÉNÉRATION SUGGESTIONS D'OPTIMISATION
        
        Suggère automatiquement :
        - Ajuster seuils features
        - Changer pondération patterns
        - Modifier stop distances
        - Optimiser timing entries
        
        Returns:
            Dict: Suggestions par catégorie
        """
        try:
            if not self.analysis_results:
                self.analyze_strategy_performance()
            
            suggestions = {
                'feature_optimization': [],
                'pattern_optimization': [], 
                'timing_optimization': [],
                'risk_optimization': [],
                'priority_actions': []
            }
            
            # 1. Suggestions Features
            features_suggestions = self._generate_features_suggestions()
            suggestions['feature_optimization'].extend(features_suggestions)
            
            # 2. Suggestions Patterns
            pattern_suggestions = self._generate_pattern_suggestions()
            suggestions['pattern_optimization'].extend(pattern_suggestions)
            
            # 3. Suggestions Timing
            timing_suggestions = self._generate_timing_suggestions()
            suggestions['timing_optimization'].extend(timing_suggestions)
            
            # 4. Suggestions Risk Management
            risk_suggestions = self._generate_risk_suggestions()
            suggestions['risk_optimization'].extend(risk_suggestions)
            
            # 5. Actions prioritaires
            priority_suggestions = self._generate_priority_actions()
            suggestions['priority_actions'].extend(priority_suggestions)
            
            logger.info(f"Généré {sum(len(v) for v in suggestions.values())} suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"Erreur generate_optimization_suggestions: {e}")
            return {}
    
    def calculate_edge_metrics(self) -> Dict[str, Any]:
        """
        CALCUL EDGE METRICS DÉTAILLÉES
        
        Calcule edge réel :
        - Win rate par setup
        - Profit factor par pattern
        - Sharpe ratio par régime
        - Risk-adjusted returns
        
        Returns:
            Dict: Edge metrics complètes
        """
        try:
            if self.trades_data is None:
                self._load_trades_data()
            
            edge_metrics = {
                'overall_edge': self._calculate_overall_edge(),
                'edge_by_strategy': self._calculate_edge_by_strategy(),
                'edge_by_pattern': self._calculate_edge_by_pattern(),
                'edge_by_time': self._calculate_edge_by_time(),
                'risk_adjusted_metrics': self._calculate_risk_adjusted_metrics()
            }
            
            return edge_metrics
            
        except Exception as e:
            logger.error(f"Erreur calculate_edge_metrics: {e}")
            return {}
    
    def get_status(self) -> Dict[str, Any]:
        """Status actuel de l'analyzer"""
        return {
            'trades_loaded': len(self.trades_data) if self.trades_data is not None else 0,
            'last_analysis': self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            'analysis_available': bool(self.analysis_results),
            'cache_size': len(self.analysis_cache)
        }
    
    # === PRIVATE METHODS ===
    
    def _load_trades_data(self, lookback_days: int = 30) -> bool:
        """Chargement données de trades"""
        try:
            # Collecte des fichiers de trades
            end_date = date.today()
            start_date = end_date - timedelta(days=lookback_days)
            
            all_trades = []
            
            for single_date in pd.date_range(start_date, end_date):
                daily_file = self.trades_path / "daily" / f"trades_{single_date.strftime('%Y-%m-%d')}.jsonl"
                
                if daily_file.exists():
                    daily_trades = self._load_daily_trades(daily_file)
                    all_trades.extend(daily_trades)
            
            if not all_trades:
                logger.warning("Aucune donnée trade trouvée")
                return False
            
            # Conversion en DataFrame
            self.trades_data = pd.DataFrame(all_trades)
            
            # Nettoyage et validation
            self.trades_data = self._clean_trades_data(self.trades_data)
            
            logger.info(f"Chargé {len(self.trades_data)} trades sur {lookback_days} jours")
            return True
            
        except Exception as e:
            logger.error(f"Erreur chargement trades: {e}")
            return False
    
    def _analyze_by_strategy_mode(self) -> Dict[str, Any]:
        """Analyse performance par mode stratégique"""
        if 'strategy_mode' not in self.trades_data.columns:
            return {}
        
        strategy_results = {}
        
        for strategy in self.trades_data['strategy_mode'].unique():
            strategy_trades = self.trades_data[self.trades_data['strategy_mode'] == strategy]
            
            if len(strategy_trades) >= self.min_sample_size:
                metrics = self._calculate_performance_metrics(strategy_trades)
                strategy_results[strategy] = {
                    'performance': asdict(metrics),
                    'trade_count': len(strategy_trades),
                    'performance_level': self._classify_performance_level(metrics.win_rate)
                }
        
        return strategy_results
    
    def _analyze_by_pattern_type(self) -> Dict[str, Any]:
        """Analyse performance par type de pattern"""
        if 'pattern_detected' not in self.trades_data.columns:
            return {}
        
        # Expansion des patterns (liste vers rows individuelles)
        pattern_rows = []
        for idx, row in self.trades_data.iterrows():
            patterns = row.get('pattern_detected', [])
            if isinstance(patterns, list):
                for pattern in patterns:
                    pattern_row = row.copy()
                    pattern_row['single_pattern'] = pattern
                    pattern_rows.append(pattern_row)
        
        if not pattern_rows:
            return {}
        
        pattern_df = pd.DataFrame(pattern_rows)
        pattern_results = {}
        
        for pattern in pattern_df['single_pattern'].unique():
            pattern_trades = pattern_df[pattern_df['single_pattern'] == pattern]
            
            if len(pattern_trades) >= self.min_sample_size:
                metrics = self._calculate_performance_metrics(pattern_trades)
                pattern_results[pattern] = {
                    'performance': asdict(metrics),
                    'trade_count': len(pattern_trades),
                    'performance_level': self._classify_performance_level(metrics.win_rate)
                }
        
        return pattern_results
    
    def _calculate_performance_metrics(self, trades_df: pd.DataFrame) -> PerformanceMetrics:
        """Calcul métriques de performance pour un subset de trades"""
        if trades_df.empty:
            return PerformanceMetrics()
        
        # Extraction des outcomes
        profitable_trades = 0
        total_pnl = 0.0
        wins = []
        losses = []
        
        for _, trade in trades_df.iterrows():
            outcome = trade.get('outcome')
            if outcome and isinstance(outcome, dict):
                pnl = outcome.get('pnl_net', 0.0)
                total_pnl += pnl
                
                if pnl > 0:
                    profitable_trades += 1
                    wins.append(pnl)
                elif pnl < 0:
                    losses.append(abs(pnl))
        
        total_trades = len(trades_df)
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0.0
        
        avg_win = statistics.mean(wins) if wins else 0.0
        avg_loss = statistics.mean(losses) if losses else 0.0
        
        profit_factor = (avg_win * len(wins)) / (avg_loss * len(losses)) if losses else float('inf')
        
        # Edge score simple
        edge_score = win_rate if profit_factor >= 1.0 else win_rate * 0.5
        
        return PerformanceMetrics(
            total_trades=total_trades,
            profitable_trades=profitable_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            average_win=avg_win,
            average_loss=avg_loss,
            profit_factor=profit_factor,
            edge_score=edge_score
        )
    
    def _classify_performance_level(self, win_rate: float) -> str:
        """Classification niveau de performance"""
        if win_rate >= 0.70:
            return PerformanceLevel.EXCELLENT.value
        elif win_rate >= 0.60:
            return PerformanceLevel.STRONG.value
        elif win_rate >= 0.50:
            return PerformanceLevel.MODERATE.value
        elif win_rate >= 0.40:
            return PerformanceLevel.WEAK.value
        else:
            return PerformanceLevel.POOR.value
    
    def _generate_features_suggestions(self) -> List[str]:
        """Génération suggestions optimisation features"""
        suggestions = []
        
        # Analyse performance features si disponibles
        if 'features_effectiveness' in self.analysis_results:
            features_analysis = self.analysis_results['features_effectiveness']
            
            # Suggestion basée sur features les moins performantes
            if 'underperforming_features' in features_analysis:
                suggestions.append("Réduire pondération des features sous-performantes")
            
            # Suggestion basée sur features top
            if 'top_features' in features_analysis:
                suggestions.append("Augmenter pondération des features les plus predictives")
        
        suggestions.append("Tester nouvelles combinaisons features basées sur corrélations")
        
        return suggestions
    
    def _load_daily_trades(self, file_path: Path) -> List[Dict]:
        """Chargement trades d'un fichier quotidien"""
        trades = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        trade_data = json.loads(line)
                        if trade_data.get('operation') == 'trade_entry':
                            trades.append(trade_data['data'])
        except Exception as e:
            logger.error(f"Erreur lecture {file_path}: {e}")
        
        return trades
    
    def _clean_trades_data(self, trades_df: pd.DataFrame) -> pd.DataFrame:
        """Nettoyage et validation données trades"""
        # Suppression trades sans outcome
        trades_df = trades_df.dropna(subset=['outcome'])
        
        # Suppression outcomes invalides  
        valid_outcomes = []
        for _, row in trades_df.iterrows():
            outcome = row.get('outcome')
            if isinstance(outcome, dict) and 'pnl_net' in outcome:
                valid_outcomes.append(True)
            else:
                valid_outcomes.append(False)
        
        trades_df = trades_df[valid_outcomes]
        
        # Reset index
        trades_df.reset_index(drop=True, inplace=True)
        
        return trades_df
    
    # Méthodes stub pour fonctionnalités avancées
    def _analyze_features_combinations(self) -> Dict[str, Any]:
        """Stub - Analyse combinations features"""
        return {'status': 'not_implemented'}
    
    def _analyze_time_patterns(self) -> Dict[str, Any]:
        """Stub - Analyse patterns temporels"""
        return {'status': 'not_implemented'}
    
    def _calculate_edge_metrics(self) -> Dict[str, Any]:
        """Stub - Calcul edge metrics"""
        return {'status': 'not_implemented'}

# === FACTORY FUNCTIONS ===

def create_performance_analyzer(config: Optional[Dict] = None) -> PerformanceAnalyzer:
    """Factory function pour PerformanceAnalyzer"""
    return PerformanceAnalyzer(config)

# === END MODULE ===