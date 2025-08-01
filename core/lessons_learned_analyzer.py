#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Lessons Learned Analyzer
Capture et analyse des leçons de chaque trade pour ML futur
Version: Production Ready v1.0 - Target 1000 trades
"""

import json
import sqlite3
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from core.logger import get_logger
import statistics
import asyncio

logger = get_logger(__name__)

@dataclass
class TradeLesson:
    """Leçon apprise d'un trade"""
    # Identifiants
    trade_id: str
    timestamp: datetime
    
    # Données marché au moment du trade
    symbol: str = "ES"
    entry_price: float = 0.0
    exit_price: float = 0.0
    position_size: int = 1
    direction: str = "LONG"  # LONG/SHORT
    
    # Performance du trade
    pnl_gross: float = 0.0
    pnl_ticks: float = 0.0
    duration_minutes: float = 0.0
    is_winner: bool = False
    
    # Context de marché
    session_phase: str = "unknown"  # NY_OPEN, LONDON, CLOSE, etc.
    volatility_regime: str = "normal"  # low, normal, high
    market_regime: str = "trending"  # trending, ranging, choppy
    volume_profile: str = "normal"  # low, normal, high
    
    # Signal et setup
    signal_type: str = "battle_navale"
    confluence_score: float = 0.0
    setup_quality: str = "good"  # poor, fair, good, excellent
    entry_timing: str = "good"  # early, good, late
    
    # Exécution
    slippage_ticks: float = 0.0
    fill_quality: str = "good"  # poor, fair, good, excellent
    execution_delay_ms: float = 0.0
    
    # Leçons qualitatives (CRITIQUE pour ML)
    what_worked: str = ""
    what_failed: str = ""
    market_context: str = ""
    improvement_suggestion: str = ""
    pattern_effectiveness: str = ""
    risk_management_notes: str = ""
    
    # Métriques calculées
    risk_reward_ratio: float = 0.0
    win_probability_estimated: float = 0.0
    confidence_level: str = "medium"  # low, medium, high

class LessonsLearnedAnalyzer:
    """
    Analyseur de leçons apprises pour optimisation ML
    
    Objectif: Collecter 1000+ trades avec insights qualitatifs
    """
    
    def __init__(self, db_path: str = "data/lessons_learned.db"):
        self.logger = get_logger(__name__)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Stats de session
        self.session_stats = {
            'trades_analyzed': 0,
            'lessons_captured': 0,
            'discord_sent': 0,
            'analysis_errors': 0
        }
        
        # Seuils d'analyse
        self.analysis_thresholds = {
            'min_trades_for_pattern': 10,  # Minimum trades pour analyser un pattern
            'significant_sample': 50,      # Échantillon significatif
            'target_trades': 1000,         # Objectif final
            'discord_summary_every': 25    # Résumé Discord tous les 25 trades
        }
        
        # Initialize database
        self._init_database()
        
        self.logger.info(f"🧠 Lessons Learned Analyzer initialisé")
        self.logger.info(f"📊 Base de données: {self.db_path}")
        self.logger.info(f"🎯 Objectif: {self.analysis_thresholds['target_trades']} trades")
    
    def _init_database(self):
        """Initialise la base de données SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS trade_lessons (
                        trade_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        symbol TEXT,
                        entry_price REAL,
                        exit_price REAL,
                        position_size INTEGER,
                        direction TEXT,
                        pnl_gross REAL,
                        pnl_ticks REAL,
                        duration_minutes REAL,
                        is_winner BOOLEAN,
                        session_phase TEXT,
                        volatility_regime TEXT,
                        market_regime TEXT,
                        volume_profile TEXT,
                        signal_type TEXT,
                        confluence_score REAL,
                        setup_quality TEXT,
                        entry_timing TEXT,
                        slippage_ticks REAL,
                        fill_quality TEXT,
                        execution_delay_ms REAL,
                        what_worked TEXT,
                        what_failed TEXT,
                        market_context TEXT,
                        improvement_suggestion TEXT,
                        pattern_effectiveness TEXT,
                        risk_management_notes TEXT,
                        risk_reward_ratio REAL,
                        win_probability_estimated REAL,
                        confidence_level TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Index pour performances
                conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON trade_lessons(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_signal_type ON trade_lessons(signal_type)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_is_winner ON trade_lessons(is_winner)")
                
            self.logger.info("✅ Base de données initialisée")
            
        except Exception as e:
            self.logger.error(f"Erreur init database: {e}")
    
    def capture_trade_lesson(self, 
                           trade_data: Dict[str, Any],
                           market_context: Dict[str, Any] = None,
                           qualitative_notes: Dict[str, str] = None) -> TradeLesson:
        """
        Capture une leçon d'un trade
        
        Args:
            trade_data: Données du trade (prix, PnL, etc.)
            market_context: Contexte de marché
            qualitative_notes: Notes qualitatives (CRITIQUE)
            
        Returns:
            TradeLesson créée et stockée
        """
        try:
            # Générer ID unique
            trade_id = f"T{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(str(trade_data.get('entry_price', 0)).replace('.', ''))}"
            
            # Contexte par défaut
            context = market_context or {}
            notes = qualitative_notes or {}
            
            # Calculer métriques
            pnl_gross = trade_data.get('pnl_gross', 0.0)
            pnl_ticks = trade_data.get('pnl_ticks', pnl_gross / 12.5)  # ES: $12.5 per tick
            
            # Risk/Reward estimation
            risk_amount = abs(trade_data.get('stop_loss_distance', 1.0))
            reward_amount = abs(trade_data.get('take_profit_distance', 1.0))
            risk_reward = reward_amount / risk_amount if risk_amount > 0 else 0.0
            
            # Créer lesson
            lesson = TradeLesson(
                # IDs
                trade_id=trade_id,
                timestamp=datetime.now(timezone.utc),
                
                # Trade data
                symbol=trade_data.get('symbol', 'ES'),
                entry_price=trade_data.get('entry_price', 0.0),
                exit_price=trade_data.get('exit_price', 0.0),
                position_size=trade_data.get('position_size', 1),
                direction=trade_data.get('direction', 'LONG'),
                
                # Performance
                pnl_gross=pnl_gross,
                pnl_ticks=pnl_ticks,
                duration_minutes=trade_data.get('duration_minutes', 0.0),
                is_winner=pnl_gross > 0,
                
                # Market context
                session_phase=context.get('session_phase', self._detect_session_phase()),
                volatility_regime=context.get('volatility_regime', 'normal'),
                market_regime=context.get('market_regime', 'trending'),
                volume_profile=context.get('volume_profile', 'normal'),
                
                # Signal
                signal_type=trade_data.get('signal_type', 'battle_navale'),
                confluence_score=trade_data.get('confluence_score', 0.0),
                setup_quality=self._assess_setup_quality(trade_data),
                entry_timing=self._assess_entry_timing(trade_data),
                
                # Execution
                slippage_ticks=trade_data.get('slippage_ticks', 0.0),
                fill_quality=self._assess_fill_quality(trade_data),
                execution_delay_ms=trade_data.get('execution_delay_ms', 0.0),
                
                # Qualitative insights (CRITIQUE!)
                what_worked=notes.get('what_worked', self._auto_generate_what_worked(trade_data, pnl_gross > 0)),
                what_failed=notes.get('what_failed', self._auto_generate_what_failed(trade_data, pnl_gross <= 0)),
                market_context=notes.get('market_context', self._auto_generate_market_context(context)),
                improvement_suggestion=notes.get('improvement_suggestion', self._auto_generate_improvement(trade_data)),
                pattern_effectiveness=notes.get('pattern_effectiveness', self._assess_pattern_effectiveness(trade_data)),
                risk_management_notes=notes.get('risk_management_notes', self._auto_generate_risk_notes(trade_data)),
                
                # Calculated metrics
                risk_reward_ratio=risk_reward,
                win_probability_estimated=self._estimate_win_probability(trade_data),
                confidence_level=self._assess_confidence_level(trade_data)
            )
            
            # Stocker en base
            self._store_lesson(lesson)
            
            # Stats
            self.session_stats['trades_analyzed'] += 1
            self.session_stats['lessons_captured'] += 1
            
            self.logger.info(f"📚 Leçon capturée: {trade_id} ({lesson.direction} {lesson.pnl_ticks:+.1f} ticks)")
            
            return lesson
            
        except Exception as e:
            self.logger.error(f"Erreur capture lesson: {e}")
            self.session_stats['analysis_errors'] += 1
            raise
    
    def _store_lesson(self, lesson: TradeLesson):
        """Stocke la leçon en base de données"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Convertir en dict et préparer pour SQL
                data = asdict(lesson)
                data['timestamp'] = data['timestamp'].isoformat()
                
                # Colonnes et valeurs
                columns = list(data.keys())
                placeholders = ['?' for _ in columns]
                values = [data[col] for col in columns]
                
                sql = f"""
                    INSERT OR REPLACE INTO trade_lessons 
                    ({', '.join(columns)}) 
                    VALUES ({', '.join(placeholders)})
                """
                
                conn.execute(sql, values)
                
        except Exception as e:
            self.logger.error(f"Erreur stockage lesson: {e}")
            raise
    
    def analyze_patterns(self, min_trades: int = None) -> Dict[str, Any]:
        """
        Analyse les patterns de trading pour identifier ce qui marche
        
        Returns:
            Analyse complète des patterns
        """
        min_trades = min_trades or self.analysis_thresholds['min_trades_for_pattern']
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query("SELECT * FROM trade_lessons ORDER BY timestamp", conn)
            
            if len(df) < min_trades:
                return {
                    'status': 'insufficient_data',
                    'total_trades': len(df),
                    'min_required': min_trades,
                    'message': f'Besoin de {min_trades - len(df)} trades supplémentaires'
                }
            
            analysis = {
                'overview': self._analyze_overview(df),
                'patterns': self._analyze_signal_patterns(df),
                'timing': self._analyze_timing_patterns(df),
                'execution': self._analyze_execution_quality(df),
                'qualitative_insights': self._extract_qualitative_insights(df),
                'recommendations': self._generate_recommendations(df),
                'progress_to_target': {
                    'current_trades': len(df),
                    'target_trades': self.analysis_thresholds['target_trades'],
                    'completion_pct': (len(df) / self.analysis_thresholds['target_trades']) * 100
                }
            }
            
            self.logger.info(f"📊 Analyse pattern terminée: {len(df)} trades")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erreur analyse patterns: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _analyze_overview(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse générale des performances"""
        return {
            'total_trades': len(df),
            'win_rate': (df['is_winner'].sum() / len(df)) * 100,
            'avg_pnl_per_trade': df['pnl_gross'].mean(),
            'total_pnl': df['pnl_gross'].sum(),
            'avg_duration_minutes': df['duration_minutes'].mean(),
            'best_trade': df['pnl_gross'].max(),
            'worst_trade': df['pnl_gross'].min(),
            'avg_risk_reward': df['risk_reward_ratio'].mean(),
            'profitable_days': len(df[df['is_winner'] == True])
        }
    
    def _analyze_signal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse par type de signal"""
        patterns = {}
        
        for signal_type in df['signal_type'].unique():
            subset = df[df['signal_type'] == signal_type]
            if len(subset) >= 5:  # Minimum pour analyse
                patterns[signal_type] = {
                    'trades_count': len(subset),
                    'win_rate': (subset['is_winner'].sum() / len(subset)) * 100,
                    'avg_pnl': subset['pnl_gross'].mean(),
                    'avg_confluence': subset['confluence_score'].mean(),
                    'effectiveness': self._assess_signal_effectiveness(subset)
                }
        
        return patterns
    
    def _analyze_timing_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse des patterns temporels"""
        timing = {}
        
        # Par session
        for session in df['session_phase'].unique():
            subset = df[df['session_phase'] == session]
            if len(subset) >= 3:
                timing[f'session_{session}'] = {
                    'trades': len(subset),
                    'win_rate': (subset['is_winner'].sum() / len(subset)) * 100,
                    'avg_pnl': subset['pnl_gross'].mean()
                }
        
        return timing
    
    def _extract_qualitative_insights(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Extrait les insights qualitatifs les plus fréquents"""
        insights = {
            'top_what_worked': self._extract_top_phrases(df[df['is_winner'] == True]['what_worked']),
            'top_what_failed': self._extract_top_phrases(df[df['is_winner'] == False]['what_failed']),
            'top_improvements': self._extract_top_phrases(df['improvement_suggestion']),
            'pattern_effectiveness_notes': self._extract_top_phrases(df['pattern_effectiveness'])
        }
        return insights
    
    async def send_discord_summary(self, analysis: Dict[str, Any], discord_notifier=None) -> bool:
        """Envoie résumé sur Discord"""
        try:
            if not discord_notifier:
                return False
            
            overview = analysis.get('overview', {})
            progress = analysis.get('progress_to_target', {})
            
            title = f"📚 LESSONS LEARNED - Trade #{overview.get('total_trades', 0)}"
            
            description = f"""
**📊 PROGRESSION OBJECTIF 1000 TRADES:**
• **Trades analysés:** {progress.get('current_trades', 0)}/1000 ({progress.get('completion_pct', 0):.1f}%)
• **Win Rate:** {overview.get('win_rate', 0):.1f}%
• **P&L Total:** ${overview.get('total_pnl', 0):+.2f}
• **P&L Moyen/Trade:** ${overview.get('avg_pnl_per_trade', 0):+.2f}

**🎯 MEILLEURS PATTERNS:**
            """.strip()
            
            # Ajouter top patterns
            patterns = analysis.get('patterns', {})
            for pattern, stats in list(patterns.items())[:3]:
                win_rate = stats.get('win_rate', 0)
                avg_pnl = stats.get('avg_pnl', 0)
                description += f"\n• **{pattern}:** {win_rate:.1f}% WR (${avg_pnl:+.2f}/trade)"
            
            # Insights qualitatifs
            insights = analysis.get('qualitative_insights', {})
            top_worked = insights.get('top_what_worked', [])
            if top_worked:
                description += f"\n\n**💡 CE QUI MARCHE LE MIEUX:**\n• {top_worked[0] if top_worked else 'Analyse en cours...'}"
            
            await discord_notifier.send_custom_message(
                'backtest_results',  # Channel backtest pour analyses
                title,
                description,
                color=0x00FF00 if overview.get('win_rate', 0) > 60 else 0xFFA500
            )
            
            self.session_stats['discord_sent'] += 1
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur Discord summary: {e}")
            return False
    
    # === MÉTHODES UTILITAIRES ===
    
    def _detect_session_phase(self) -> str:
        """Détecte la phase de session actuelle"""
        hour = datetime.now().hour
        if 9 <= hour < 11:
            return "NY_OPEN"
        elif 11 <= hour < 14:
            return "NY_MID"
        elif 14 <= hour < 16:
            return "NY_CLOSE"
        else:
            return "AFTER_HOURS"
    
    def _assess_setup_quality(self, trade_data: Dict) -> str:
        """Évalue la qualité du setup"""
        confluence = trade_data.get('confluence_score', 0.0)
        if confluence >= 0.85:
            return "excellent"
        elif confluence >= 0.75:
            return "good"
        elif confluence >= 0.65:
            return "fair"
        else:
            return "poor"
    
    def _auto_generate_what_worked(self, trade_data: Dict, is_winner: bool) -> str:
        """Génère automatiquement ce qui a marché"""
        if not is_winner:
            return ""
        
        factors = []
        confluence = trade_data.get('confluence_score', 0)
        if confluence > 0.8:
            factors.append("Confluence élevée")
        if trade_data.get('slippage_ticks', 0) < 0.5:
            factors.append("Exécution propre")
        
        return " + ".join(factors) if factors else "Trade gagnant"
    
    def _auto_generate_what_failed(self, trade_data: Dict, is_loser: bool) -> str:
        """Génère automatiquement ce qui a échoué"""
        if not is_loser:
            return ""
        
        factors = []
        confluence = trade_data.get('confluence_score', 0)
        if confluence < 0.7:
            factors.append("Confluence insuffisante")
        if trade_data.get('slippage_ticks', 0) > 1.0:
            factors.append("Slippage excessif")
        
        return " + ".join(factors) if factors else "Trade perdant"
    
    def get_progress_to_target(self) -> Dict[str, Any]:
        """Retourne progression vers objectif 1000 trades"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                count = conn.execute("SELECT COUNT(*) FROM trade_lessons").fetchone()[0]
            
            target = self.analysis_thresholds['target_trades']
            return {
                'current_trades': count,
                'target_trades': target,
                'remaining_trades': target - count,
                'completion_pct': (count / target) * 100,
                'is_significant_sample': count >= self.analysis_thresholds['significant_sample']
            }
        except Exception as e:
            self.logger.error(f"Erreur progress check: {e}")
            return {'error': str(e)}
    
    # === MÉTHODES UTILITAIRES MANQUANTES ===
    
    def _assess_entry_timing(self, trade_data: Dict) -> str:
        """Évalue le timing d'entrée"""
        duration = trade_data.get('duration_minutes', 0)
        if duration < 2:
            return "early_exit"  # Sorti trop tôt
        elif duration > 30:
            return "late_exit"   # Gardé trop longtemps
        else:
            return "good"
    
    def _assess_fill_quality(self, trade_data: Dict) -> str:
        """Évalue la qualité du fill"""
        slippage = trade_data.get('slippage_ticks', 0)
        if slippage <= 0.25:
            return "excellent"
        elif slippage <= 0.5:
            return "good" 
        elif slippage <= 1.0:
            return "fair"
        else:
            return "poor"
    
    def _auto_generate_market_context(self, context: Dict) -> str:
        """Génère contexte marché automatiquement"""
        session = context.get('session_phase', 'unknown')
        regime = context.get('market_regime', 'unknown')
        volatility = context.get('volatility_regime', 'unknown')
        
        return f"Session: {session}, Regime: {regime}, Volatilité: {volatility}"
    
    def _auto_generate_improvement(self, trade_data: Dict) -> str:
        """Génère suggestion d'amélioration"""
        suggestions = []
        
        confluence = trade_data.get('confluence_score', 0)
        if confluence < 0.75:
            suggestions.append("Attendre confluence >0.75")
        
        slippage = trade_data.get('slippage_ticks', 0)
        if slippage > 0.5:
            suggestions.append("Améliorer timing d'exécution")
        
        return " + ".join(suggestions) if suggestions else "Continuer cette approche"
    
    def _assess_pattern_effectiveness(self, trade_data: Dict) -> str:
        """Évalue l'efficacité du pattern"""
        signal_type = trade_data.get('signal_type', '')
        confluence = trade_data.get('confluence_score', 0)
        
        if 'elite' in signal_type.lower():
            return "Pattern Elite détecté - très efficace"
        elif confluence > 0.8:
            return "Pattern standard avec forte confluence"
        else:
            return "Pattern standard avec confluence modérée"
    
    def _auto_generate_risk_notes(self, trade_data: Dict) -> str:
        """Génère notes de risk management"""
        notes = []
        
        position_size = trade_data.get('position_size', 1)
        if position_size > 1:
            notes.append(f"Position size: {position_size} contrats")
        
        if trade_data.get('stop_loss_distance'):
            notes.append(f"Stop: {trade_data['stop_loss_distance']} ticks")
        
        return " | ".join(notes) if notes else "Risk management standard"
    
    def _estimate_win_probability(self, trade_data: Dict) -> float:
        """Estime probabilité de gain basée sur setup"""
        confluence = trade_data.get('confluence_score', 0.5)
        
        # Modèle simple basé sur confluence
        if confluence >= 0.9:
            return 0.75
        elif confluence >= 0.8:
            return 0.65
        elif confluence >= 0.7:
            return 0.55
        else:
            return 0.45
    
    def _assess_confidence_level(self, trade_data: Dict) -> str:
        """Évalue niveau de confiance"""
        confluence = trade_data.get('confluence_score', 0)
        
        if confluence >= 0.85:
            return "high"
        elif confluence >= 0.7:
            return "medium"
        else:
            return "low"
    
    def _assess_signal_effectiveness(self, subset: pd.DataFrame) -> str:
        """Évalue efficacité d'un signal"""
        win_rate = (subset['is_winner'].sum() / len(subset)) * 100
        avg_pnl = subset['pnl_gross'].mean()
        
        if win_rate >= 70 and avg_pnl > 50:
            return "Très efficace"
        elif win_rate >= 60 and avg_pnl > 0:
            return "Efficace"
        elif win_rate >= 50:
            return "Modérément efficace"
        else:
            return "Peu efficace"
    
    def _analyze_execution_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse qualité d'exécution"""
        return {
            'avg_slippage_ticks': df['slippage_ticks'].mean(),
            'avg_execution_delay_ms': df['execution_delay_ms'].mean(),
            'excellent_fills_pct': (df['fill_quality'] == 'excellent').sum() / len(df) * 100,
            'poor_fills_pct': (df['fill_quality'] == 'poor').sum() / len(df) * 100
        }
    
    def _extract_top_phrases(self, series: pd.Series, top_n: int = 3) -> List[str]:
        """Extrait les phrases les plus fréquentes"""
        # Filtrer les valeurs vides
        clean_series = series.dropna()
        clean_series = clean_series[clean_series != ""]
        
        if len(clean_series) == 0:
            return []
        
        # Compter occurrences et retourner top N
        value_counts = clean_series.value_counts()
        return value_counts.head(top_n).index.tolist()
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Génère recommandations basées sur l'analyse"""
        recommendations = []
        
        # Analyse win rate
        win_rate = (df['is_winner'].sum() / len(df)) * 100
        if win_rate < 60:
            recommendations.append("Améliorer sélectivité - win rate sous 60%")
        
        # Analyse confluence
        avg_confluence = df['confluence_score'].mean()
        if avg_confluence < 0.75:
            recommendations.append("Augmenter seuil confluence minimum")
        
        # Analyse slippage
        avg_slippage = df['slippage_ticks'].mean()
        if avg_slippage > 0.5:
            recommendations.append("Optimiser timing d'exécution pour réduire slippage")
        
        return recommendations

# Factory function
def create_lessons_learned_analyzer(db_path: str = "data/lessons_learned.db") -> LessonsLearnedAnalyzer:
    """Factory pour créer le Lessons Learned Analyzer"""
    return LessonsLearnedAnalyzer(db_path)

# Exemple d'utilisation:
"""
# Après chaque trade dans automation_main.py:
lesson = self.lessons_analyzer.capture_trade_lesson(
    trade_data={
        'entry_price': 5247.50,
        'exit_price': 5249.00,
        'pnl_gross': 187.50,
        'direction': 'LONG',
        'confluence_score': 0.82,
        'signal_type': 'battle_navale'
    },
    qualitative_notes={
        'what_worked': 'Confluence multiple + volume confirmation',
        'market_context': 'NY session active, trending up',
        'improvement_suggestion': 'Entrée plus agressive possible'
    }
)

# Analyse tous les 25 trades:
if self.lessons_analyzer.get_progress_to_target()['current_trades'] % 25 == 0:
    analysis = self.lessons_analyzer.analyze_patterns()
    await self.lessons_analyzer.send_discord_summary(analysis, self.discord_notifier)
"""