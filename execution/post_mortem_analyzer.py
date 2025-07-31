
#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Post-Mortem Analysis System
Analyse complète de tous les trades (gagnants et perdants)
Version: Production Ready
Intégration: execution/trade_snapshotter.py + monitoring/discord_notifier.py

NOUVELLE FONCTIONNALITÉ:
- Tracking post-trade automatique (5-20 minutes)
- Analyse performance complète tous trades
- Notifications Discord enrichies
- Base de données insights ML
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

# === CORE IMPORTS ===
from core.base_types import MarketData, ES_TICK_SIZE, ES_TICK_VALUE

logger = logging.getLogger(__name__)

# === ENUMS & TYPES ===

class TradeOutcome(Enum):
    """Types de résultats de trade"""
    WIN = "win"
    LOSS = "loss"
    BREAKEVEN = "breakeven"

class PostMortemInsight(Enum):
    """Types d'insights post-mortem"""
    STOP_TOO_TIGHT = "stop_too_tight"
    STOP_JUSTIFIED = "stop_justified"
    EXIT_TOO_EARLY = "exit_too_early"
    EXIT_OPTIMAL = "exit_optimal"
    TARGET_TOO_CONSERVATIVE = "target_too_conservative"
    MISSED_CONTINUATION = "missed_continuation"
    GOOD_RISK_MANAGEMENT = "good_risk_management"

@dataclass
class PostTradeTracking:
    """Données tracking post-trade"""
    trade_id: str
    trade_outcome: TradeOutcome
    tracking_start_time: datetime
    tracking_duration_minutes: int
    
    # Prix tracking
    price_at_exit: float
    max_favorable_price: float
    max_adverse_price: float
    final_price: float
    
    # Temps tracking
    time_to_max_favorable: int  # minutes
    time_to_max_adverse: int    # minutes
    
    # Volume analysis
    volume_spike_favorable: bool = False
    volume_spike_adverse: bool = False
    
    # Volatility context
    volatility_regime: str = "NORMAL"
    session_phase: str = "REGULAR"

@dataclass
class PostMortemAnalysis:
    """Analyse post-mortem complète"""
    trade_id: str
    analysis_timestamp: datetime
    
    # Trade original data
    original_entry_price: float
    original_exit_price: float
    original_pnl: float
    exit_reason: str
    trade_outcome: TradeOutcome
    
    # Post tracking data
    tracking_data: PostTradeTracking
    
    # Analysis results
    efficiency_score: float        # 0-100%
    decision_quality_score: float  # 0-100%
    insights: List[PostMortemInsight]
    
    # Monetary analysis
    money_left_on_table: float = 0.0
    money_saved_by_exit: float = 0.0
    optimal_exit_price: float = 0.0
    
    # Recommendations
    recommended_stop_adjustment: float = 0.0
    recommended_target_adjustment: float = 0.0
    confidence_score: float = 0.0

# === MAIN POST-MORTEM SYSTEM ===

class PostMortemAnalyzer:
    """
    SYSTÈME POST-MORTEM COMPLET
    
    Analyse automatique de tous les trades pour amélioration continue.
    Intégration avec TradeSnapshotter et Discord pour feedback temps réel.
    """
    
    def __init__(self, discord_notifier=None):
        self.discord = discord_notifier
        self.active_trackings: Dict[str, asyncio.Task] = {}
        self.completed_analyses: List[PostMortemAnalysis] = []
        
        # Configuration dynamique
        self.tracking_configs = {
            TradeOutcome.WIN: {
                'duration_minutes': 20,
                'focus': ['profit_extension', 'exit_timing'],
                'priority': 'HIGH'
            },
            TradeOutcome.LOSS: {
                'duration_minutes': 15,
                'focus': ['stop_justification', 'reversal_patterns'],
                'priority': 'CRITICAL'
            },
            TradeOutcome.BREAKEVEN: {
                'duration_minutes': 12,
                'focus': ['missed_opportunities', 'timing_issues'],
                'priority': 'MEDIUM'
            }
        }
        
        # Pattern detection
        self.pattern_tracker = PatternTracker()
        
        logger.info("✅ PostMortemAnalyzer initialisé")
    
    def start_post_mortem_tracking(self, 
                                  trade_id: str,
                                  trade_result: Dict[str, Any],
                                  current_market_data: MarketData):
        """
        POINT D'ENTRÉE PRINCIPAL
        Lance le tracking post-mortem pour un trade
        
        À appeler depuis simple_trader.py dans _close_position()
        """
        try:
            # Déterminer outcome
            pnl = trade_result.get('pnl', 0.0)
            outcome = self._determine_trade_outcome(pnl)
            
            # Configuration tracking
            config = self.tracking_configs[outcome]
            
            # Créer task async
            tracking_task = asyncio.create_task(
                self._execute_post_mortem_tracking(
                    trade_id, trade_result, current_market_data, config
                )
            )
            
            self.active_trackings[trade_id] = tracking_task
            
            logger.info(f"🔍 Post-mortem tracking started: {trade_id} ({outcome.value})")
            
        except Exception as e:
            logger.error(f"❌ Erreur start post-mortem: {e}")
    
    async def _execute_post_mortem_tracking(self,
                                          trade_id: str,
                                          trade_result: Dict[str, Any],
                                          initial_market_data: MarketData,
                                          config: Dict[str, Any]):
        """Exécute le tracking post-mortem complet"""
        
        tracking_start = datetime.now(timezone.utc)
        duration_minutes = config['duration_minutes']
        
        # Initialiser tracking data
        tracking_data = PostTradeTracking(
            trade_id=trade_id,
            trade_outcome=self._determine_trade_outcome(trade_result.get('pnl', 0.0)),
            tracking_start_time=tracking_start,
            tracking_duration_minutes=duration_minutes,
            price_at_exit=trade_result.get('exit_price', 0.0),
            max_favorable_price=trade_result.get('exit_price', 0.0),
            max_adverse_price=trade_result.get('exit_price', 0.0),
            final_price=0.0
        )
        
        # Notification immédiate
        await self._send_immediate_notification(trade_id, trade_result, tracking_data)
        
        # Loop de tracking
        end_time = tracking_start + timedelta(minutes=duration_minutes)
        
        while datetime.now(timezone.utc) < end_time:
            try:
                # Obtenir données marché actuelles
                current_data = await self._get_current_market_data()
                
                if current_data:
                    # Mettre à jour tracking
                    self._update_tracking_data(tracking_data, current_data, trade_result)
                
                # Attendre 30 secondes
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Erreur pendant tracking {trade_id}: {e}")
        
        # Finaliser tracking
        tracking_data.final_price = current_data.close if current_data else tracking_data.price_at_exit
        
        # Analyser résultats
        analysis = self._perform_complete_analysis(trade_result, tracking_data)
        
        # Sauvegarder
        self.completed_analyses.append(analysis)
        
        # Notification finale
        await self._send_final_analysis_notification(analysis)
        
        # Pattern detection
        self.pattern_tracker.add_analysis(analysis)
        
        # Nettoyer
        if trade_id in self.active_trackings:
            del self.active_trackings[trade_id]
        
        logger.info(f"✅ Post-mortem completed: {trade_id}")
    
    def _determine_trade_outcome(self, pnl: float) -> TradeOutcome:
        """Détermine le type de résultat"""
        if pnl > 5.0:  # Plus de $5
            return TradeOutcome.WIN
        elif pnl < -5.0:  # Moins de -$5
            return TradeOutcome.LOSS
        else:
            return TradeOutcome.BREAKEVEN
    
    def _update_tracking_data(self, 
                            tracking_data: PostTradeTracking,
                            current_data: MarketData,
                            trade_result: Dict[str, Any]):
        """Met à jour les données de tracking"""
        
        current_price = current_data.close
        trade_direction = trade_result.get('side', 'LONG')
        
        # Déterminer favorable vs adverse selon direction
        if trade_direction == 'LONG':
            if current_price > tracking_data.max_favorable_price:
                tracking_data.max_favorable_price = current_price
                tracking_data.time_to_max_favorable = (
                    datetime.now(timezone.utc) - tracking_data.tracking_start_time
                ).total_seconds() / 60
            
            if current_price < tracking_data.max_adverse_price:
                tracking_data.max_adverse_price = current_price
                tracking_data.time_to_max_adverse = (
                    datetime.now(timezone.utc) - tracking_data.tracking_start_time
                ).total_seconds() / 60
        else:  # SHORT
            if current_price < tracking_data.max_favorable_price:
                tracking_data.max_favorable_price = current_price
                tracking_data.time_to_max_favorable = (
                    datetime.now(timezone.utc) - tracking_data.tracking_start_time
                ).total_seconds() / 60
            
            if current_price > tracking_data.max_adverse_price:
                tracking_data.max_adverse_price = current_price
                tracking_data.time_to_max_adverse = (
                    datetime.now(timezone.utc) - tracking_data.tracking_start_time
                ).total_seconds() / 60
    
    def _perform_complete_analysis(self, 
                                 trade_result: Dict[str, Any],
                                 tracking_data: PostTradeTracking) -> PostMortemAnalysis:
        """Analyse complète post-mortem"""
        
        analysis = PostMortemAnalysis(
            trade_id=tracking_data.trade_id,
            analysis_timestamp=datetime.now(timezone.utc),
            original_entry_price=trade_result.get('entry_price', 0.0),
            original_exit_price=trade_result.get('exit_price', 0.0),
            original_pnl=trade_result.get('pnl', 0.0),
            exit_reason=trade_result.get('exit_reason', 'UNKNOWN'),
            trade_outcome=tracking_data.trade_outcome,
            tracking_data=tracking_data,
            efficiency_score=0.0,
            decision_quality_score=0.0,
            insights=[]
        )
        
        # Analyse selon type de trade
        if tracking_data.trade_outcome == TradeOutcome.WIN:
            self._analyze_winning_trade(analysis)
        elif tracking_data.trade_outcome == TradeOutcome.LOSS:
            self._analyze_losing_trade(analysis)
        else:
            self._analyze_breakeven_trade(analysis)
        
        return analysis
    
    def _analyze_winning_trade(self, analysis: PostMortemAnalysis):
        """Analyse spécifique trades gagnants"""
        
        # Calculer efficacité profit
        entry_price = analysis.original_entry_price
        exit_price = analysis.original_exit_price
        max_favorable = analysis.tracking_data.max_favorable_price
        
        trade_direction = "LONG" if exit_price > entry_price else "SHORT"
        
        if trade_direction == "LONG":
            actual_gain = exit_price - entry_price
            potential_gain = max_favorable - entry_price
        else:
            actual_gain = entry_price - exit_price
            potential_gain = entry_price - max_favorable
        
        if potential_gain > 0:
            analysis.efficiency_score = (actual_gain / potential_gain) * 100
            analysis.money_left_on_table = (potential_gain - actual_gain) * ES_TICK_VALUE / ES_TICK_SIZE
        else:
            analysis.efficiency_score = 100.0
        
        analysis.optimal_exit_price = max_favorable
        
        # Insights
        if analysis.efficiency_score < 60:
            analysis.insights.append(PostMortemInsight.EXIT_TOO_EARLY)
        elif analysis.efficiency_score > 85:
            analysis.insights.append(PostMortemInsight.EXIT_OPTIMAL)
        
        if analysis.money_left_on_table > 100:  # Plus de $100 laissé
            analysis.insights.append(PostMortemInsight.MISSED_CONTINUATION)
    
    def _analyze_losing_trade(self, analysis: PostMortemAnalysis):
        """Analyse spécifique trades perdants"""
        
        entry_price = analysis.original_entry_price
        exit_price = analysis.original_exit_price
        max_favorable = analysis.tracking_data.max_favorable_price
        max_adverse = analysis.tracking_data.max_adverse_price
        
        trade_direction = "LONG" if analysis.original_pnl < 0 and exit_price < entry_price else "SHORT"
        
        # Score justification stop
        score = 0
        
        # Critère 1: Direction post-stop (40 points)
        if trade_direction == "LONG":
            favorable_move = max_favorable - exit_price
            adverse_move = exit_price - max_adverse
            stop_distance = entry_price - exit_price
        else:
            favorable_move = exit_price - max_favorable
            adverse_move = max_adverse - exit_price
            stop_distance = exit_price - entry_price
        
        favorable_ticks = favorable_move / ES_TICK_SIZE
        adverse_ticks = adverse_move / ES_TICK_SIZE
        stop_ticks = stop_distance / ES_TICK_SIZE
        
        if favorable_ticks >= stop_ticks * 2:  # Aurait fait 2x le stop
            score -= 40
            analysis.insights.append(PostMortemInsight.STOP_TOO_TIGHT)
        elif adverse_ticks >= stop_ticks * 2:  # Marché a continué contre
            score += 40
            analysis.insights.append(PostMortemInsight.STOP_JUSTIFIED)
        
        # Critère 2: Timing reversal (20 points)
        if analysis.tracking_data.time_to_max_favorable <= 2:  # 2 minutes
            score -= 20
        elif analysis.tracking_data.time_to_max_favorable >= 8:  # 8 minutes
            score += 10
        
        analysis.decision_quality_score = max(0, min(100, score + 50))  # Normaliser 0-100
        
        # Calculs monétaires
        if favorable_ticks > 0:
            analysis.money_left_on_table = favorable_ticks * ES_TICK_VALUE
        if adverse_ticks > 0:
            analysis.money_saved_by_exit = adverse_ticks * ES_TICK_VALUE
    
    def _analyze_breakeven_trade(self, analysis: PostMortemAnalysis):
        """Analyse spécifique trades breakeven"""
        
        max_favorable = analysis.tracking_data.max_favorable_price
        max_adverse = analysis.tracking_data.max_adverse_price
        exit_price = analysis.original_exit_price
        
        # Opportunité ratée vs risque évité
        favorable_move = abs(max_favorable - exit_price)
        adverse_move = abs(max_adverse - exit_price)
        
        analysis.money_left_on_table = (favorable_move / ES_TICK_SIZE) * ES_TICK_VALUE
        analysis.money_saved_by_exit = (adverse_move / ES_TICK_SIZE) * ES_TICK_VALUE
        
        # Score décision
        if analysis.money_saved_by_exit > analysis.money_left_on_table:
            analysis.decision_quality_score = 80.0
            analysis.insights.append(PostMortemInsight.GOOD_RISK_MANAGEMENT)
        else:
            analysis.decision_quality_score = 40.0
    
    async def _send_immediate_notification(self, 
                                         trade_id: str,
                                         trade_result: Dict[str, Any],
                                         tracking_data: PostTradeTracking):
        """Notification immédiate début tracking"""
        
        if not self.discord:
            return
        
        try:
            outcome_emoji = {
                TradeOutcome.WIN: "✅",
                TradeOutcome.LOSS: "❌", 
                TradeOutcome.BREAKEVEN: "⚖️"
            }
            
            message = f"{outcome_emoji[tracking_data.trade_outcome]} TRADE FERMÉ: {trade_result.get('exit_reason', 'UNKNOWN')}\n"
            message += f"📊 Analyse post-trade en cours...\n"
            message += f"⏱️ Suivi: {tracking_data.tracking_duration_minutes} minutes\n"
            message += f"💰 P&L: ${trade_result.get('pnl', 0.0):.2f}"
            
            await self.discord.send_notification(
                message,
                notification_type=self.discord.NotificationType.INFO,
                channel='trades'
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur notification immédiate: {e}")
    
    async def _send_final_analysis_notification(self, analysis: PostMortemAnalysis):
        """Notification finale avec analyse complète"""
        
        if not self.discord:
            return
        
        try:
            # Construire message selon outcome
            if analysis.trade_outcome == TradeOutcome.WIN:
                message = self._format_winning_trade_message(analysis)
            elif analysis.trade_outcome == TradeOutcome.LOSS:
                message = self._format_losing_trade_message(analysis)
            else:
                message = self._format_breakeven_trade_message(analysis)
            
            await self.discord.send_notification(
                message,
                notification_type=self.discord.NotificationType.INFO,
                channel='trades',
                urgent=True
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur notification finale: {e}")
    
    def _format_winning_trade_message(self, analysis: PostMortemAnalysis) -> str:
        """Format message pour trade gagnant"""
        
        message = f"✅ POST-MORTEM Trade #{analysis.trade_id} - WIN +${analysis.original_pnl:.2f}\n\n"
        message += f"📊 ANALYSE PERFORMANCE:\n"
        message += f"💰 Profit capturé: ${analysis.original_pnl:.2f}\n"
        message += f"🎯 Profit max possible: ${analysis.original_pnl + analysis.money_left_on_table:.2f}\n"
        message += f"📈 Efficacité: {analysis.efficiency_score:.0f}%\n"
        
        if analysis.money_left_on_table > 50:
            message += f"💸 Laissé sur table: ${analysis.money_left_on_table:.2f}\n"
        
        message += f"\n📈 CONTINUATION ANALYSIS:\n"
        message += f"⏱️ Prix max atteint: {analysis.tracking_data.max_favorable_price:.2f}\n"
        message += f"⏰ Temps au max: {analysis.tracking_data.time_to_max_favorable:.0f} minutes\n"
        
        # Insights
        if PostMortemInsight.EXIT_TOO_EARLY in analysis.insights:
            message += f"\n💡 INSIGHT: Sortie trop précoce détectée\n"
            message += f"⚙️ Suggestion: Tenir +3-5 minutes\n"
        
        return message
    
    def _format_losing_trade_message(self, analysis: PostMortemAnalysis) -> str:
        """Format message pour trade perdant"""
        
        message = f"❌ POST-MORTEM Trade #{analysis.trade_id} - LOSS ${analysis.original_pnl:.2f}\n\n"
        message += f"📊 ANALYSE JUSTIFICATION:\n"
        message += f"🛑 Stop Loss: {analysis.original_exit_price:.2f}\n"
        message += f"📈 Prix max favorable: {analysis.tracking_data.max_favorable_price:.2f}\n"
        message += f"📉 Prix max adverse: {analysis.tracking_data.max_adverse_price:.2f}\n"
        
        favorable_ticks = abs(analysis.tracking_data.max_favorable_price - analysis.original_exit_price) / ES_TICK_SIZE
        message += f"📊 Move favorable: +{favorable_ticks:.1f} ticks\n"
        
        message += f"\n🎯 CONCLUSION: "
        if PostMortemInsight.STOP_TOO_TIGHT in analysis.insights:
            message += f"STOP TROP SERRÉ (Score: {analysis.decision_quality_score:.0f}%)\n"
            message += f"💡 Marché aurait fait +{favorable_ticks:.0f} ticks\n"
            message += f"⚙️ Suggestion: Stop +2-3 ticks\n"
        elif PostMortemInsight.STOP_JUSTIFIED in analysis.insights:
            message += f"STOP JUSTIFIÉ (Score: {analysis.decision_quality_score:.0f}%)\n"
            message += f"✅ Bonne gestion du risque\n"
        
        return message
    
    def _format_breakeven_trade_message(self, analysis: PostMortemAnalysis) -> str:
        """Format message pour trade breakeven"""
        
        message = f"⚖️ POST-MORTEM Trade #{analysis.trade_id} - BREAKEVEN\n\n"
        message += f"📊 ANALYSE DÉCISION:\n"
        message += f"💰 P&L: ${analysis.original_pnl:.2f}\n"
        message += f"📈 Profit max possible: +${analysis.money_left_on_table:.2f}\n"
        message += f"📉 Loss max évité: -${analysis.money_saved_by_exit:.2f}\n"
        
        message += f"\n🎯 ÉVALUATION SORTIE:\n"
        message += f"📊 Score décision: {analysis.decision_quality_score:.0f}%\n"
        
        if PostMortemInsight.GOOD_RISK_MANAGEMENT in analysis.insights:
            message += f"✅ Excellente gestion du risque\n"
        
        return message
    
    async def _get_current_market_data(self) -> Optional[MarketData]:
        """Obtient données marché actuelles"""
        # À implémenter selon votre source de données
        # Placeholder pour maintenant
        return None


class PatternTracker:
    """Détection patterns récurrents dans analyses post-mortem"""
    
    def __init__(self):
        self.analyses_history: List[PostMortemAnalysis] = []
        self.pattern_counts: Dict[str, int] = {}
    
    def add_analysis(self, analysis: PostMortemAnalysis):
        """Ajoute analyse et détecte patterns"""
        self.analyses_history.append(analysis)
        
        # Limiter historique
        if len(self.analyses_history) > 100:
            self.analyses_history = self.analyses_history[-50:]
        
        # Détecter patterns
        self._detect_recurring_patterns()
    
    def _detect_recurring_patterns(self):
        """Détecte patterns récurrents"""
        
        recent_analyses = self.analyses_history[-10:]  # 10 derniers trades
        
        # Compter insights récurrents
        insight_counts = {}
        for analysis in recent_analyses:
            for insight in analysis.insights:
                insight_counts[insight.value] = insight_counts.get(insight.value, 0) + 1
        
        # Alerter si pattern récurrent
        for insight, count in insight_counts.items():
            if count >= 3:  # 3 occurrences sur 10 trades
                logger.warning(f"🔄 Pattern récurrent détecté: {insight} ({count}/10 trades)")


# === INTÉGRATION AVEC TRADE SNAPSHOTTER ===

def integrate_post_mortem_with_snapshotter(trade_snapshotter, post_mortem_analyzer):
    """Intègre post-mortem avec TradeSnapshotter existant"""
    
    # Étendre TradeSnapshotter avec post-mortem
    original_finalize = trade_snapshotter.finalize_trade_snapshot
    
    def enhanced_finalize_trade_snapshot(trade_id: str, trade_result, market_data=None):
        """Version enrichie avec post-mortem automatique"""
        
        # Appeler méthode originale
        success = original_finalize(trade_id, trade_result)
        
        if success and market_data:
            # Lancer post-mortem automatiquement
            post_mortem_analyzer.start_post_mortem_tracking(
                trade_id, trade_result.__dict__, market_data
            )
        
        return success
    
    # Remplacer méthode
    trade_snapshotter.finalize_trade_snapshot = enhanced_finalize_trade_snapshot
    
    return trade_snapshotter


# === FACTORY FUNCTIONS ===

def create_post_mortem_analyzer(discord_notifier=None):
    """Factory function pour post-mortem analyzer"""
    return PostMortemAnalyzer(discord_notifier)

def setup_complete_post_mortem_system(trade_snapshotter, discord_notifier=None):
    """Setup système post-mortem complet"""
    
    # Créer analyzer
    post_mortem = create_post_mortem_analyzer(discord_notifier)
    
    # Intégrer avec snapshotter
    enhanced_snapshotter = integrate_post_mortem_with_snapshotter(
        trade_snapshotter, post_mortem
    )
    
    return enhanced_snapshotter, post_mortem


# === TESTING ===

if __name__ == "__main__":
    print("🔍 Test Post-Mortem System...")
    
    # Test analyzer
    analyzer = create_post_mortem_analyzer()
    print("✅ PostMortemAnalyzer créé")
    
    print("🎯 Post-Mortem System ready for integration!")