#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Mentor System Module
Système de mentorat automatique avec coaching personnalisé via Discord

Version: 1.0.0
Responsabilité: Coaching automatisé et conseils personnalisés

FONCTIONNALITÉS:
1. Analyse quotidienne des performances
2. Génération de conseils personnalisés
3. Envoi de messages Discord
4. Coaching basé sur les données réelles
5. Détection d'habitudes coûteuses
6. Suivi des améliorations
"""

import json
import sqlite3
import pandas as pd
import numpy as np
import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from decimal import Decimal
import os
from pathlib import Path

# === IMPORTS INTERNES ===
try:
    from core.lessons_learned_analyzer import LessonsLearnedAnalyzer
    from core.base_types import MarketData, OrderFlowData
    from core.logger import get_logger
except ImportError as e:
    logging.warning(f"Import interne non disponible: {e}")
    # Fallback logger
    def get_logger(name):
        return logging.getLogger(name)

# === TYPES ET ENUMS ===

class MentorMessageType(Enum):
    """Types de messages du mentor"""
    DAILY_REPORT = "daily_report"
    LESSON_LEARNED = "lesson_learned"
    PERFORMANCE_ALERT = "performance_alert"
    HABIT_WARNING = "habit_warning"
    IMPROVEMENT_SUGGESTION = "improvement_suggestion"
    CELEBRATION = "celebration"

class MentorAdviceLevel(Enum):
    """Niveaux de conseils du mentor"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SUCCESS = "success"

@dataclass
class MentorAdvice:
    """Conseil du mentor"""
    advice_id: str
    timestamp: datetime
    advice_type: MentorMessageType
    level: MentorAdviceLevel
    title: str
    message: str
    data: Dict[str, Any]
    actionable: bool = True
    priority: int = 1

@dataclass
class DailyPerformance:
    """Performance quotidienne"""
    date: datetime
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    avg_win: float
    avg_loss: float
    max_win: float
    max_loss: float
    profit_factor: float
    largest_drawdown: float
    best_pattern: str
    worst_pattern: str
    improvement_areas: List[str]
    strengths: List[str]

@dataclass
class MentorReport:
    """Rapport du mentor"""
    report_id: str
    date: datetime
    performance: DailyPerformance
    advice_list: List[MentorAdvice]
    overall_score: float
    mood: str  # "excellent", "good", "neutral", "concerned", "critical"
    next_day_focus: str

# === MENTOR SYSTEM ===

class MentorSystem:
    """
    🎓 MENTOR SYSTEM
    
    Système de mentorat automatique qui :
    - Analyse les performances quotidiennes
    - Génère des conseils personnalisés
    - Envoie des messages Discord
    - Fournit un coaching basé sur les données réelles
    """
    
    def __init__(self, discord_webhook_url: str, db_path: str = "data/lessons_learned.db"):
        self.discord_webhook_url = discord_webhook_url
        self.db_path = db_path
        self.logger = get_logger(f"{__name__}.MentorSystem")
        
        # Créer le dossier data s'il n'existe pas
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Configuration du mentor
        self.mentor_config = {
            'daily_report_time': '18:00',  # Heure du rapport quotidien
            'min_trades_for_analysis': 3,
            'performance_thresholds': {
                'excellent_win_rate': 0.7,
                'good_win_rate': 0.6,
                'concerning_win_rate': 0.4,
                'critical_win_rate': 0.3,
                'excellent_profit_factor': 2.0,
                'good_profit_factor': 1.5,
                'concerning_profit_factor': 1.0
            },
            'advice_cooldown_hours': 4,  # Éviter le spam
            'max_daily_messages': 3
        }
        
        # État du mentor
        self.last_advice_time: Dict[str, datetime] = {}
        self.daily_message_count = 0
        self.last_report_date = None
        
        # Initialiser l'analyseur de leçons
        try:
            self.lessons_analyzer = LessonsLearnedAnalyzer()
        except Exception as e:
            self.logger.warning(f"LessonsLearnedAnalyzer non disponible: {e}")
            self.lessons_analyzer = None
        
        # Initialiser la base de données
        self._init_database()
        
        self.logger.info("🎓 Mentor System initialisé")
    
    def _init_database(self):
        """Initialise la base de données SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS trades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,
                        symbol TEXT NOT NULL,
                        side TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        price REAL NOT NULL,
                        pnl REAL,
                        pattern TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                self.logger.info("✅ Base de données initialisée")
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation base de données: {e}")
    
    async def analyze_daily_performance(self, date: datetime = None) -> Optional[DailyPerformance]:
        """Analyse la performance quotidienne"""
        try:
            if date is None:
                date = datetime.now()
            
            # Charger les trades du jour
            trades_df = self._load_daily_trades(date)
            
            if trades_df.empty:
                self.logger.info(f"Aucun trade trouvé pour {date.strftime('%Y-%m-%d')}")
                return None
            
            # Calculer les métriques
            total_trades = len(trades_df)
            winning_trades = len(trades_df[trades_df['pnl'] > 0])
            losing_trades = len(trades_df[trades_df['pnl'] < 0])
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            total_pnl = trades_df['pnl'].sum()
            avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
            avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
            max_win = trades_df['pnl'].max() if not trades_df.empty else 0
            max_loss = trades_df['pnl'].min() if not trades_df.empty else 0
            
            profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
            largest_drawdown = self._calculate_drawdown(trades_df['pnl'])
            
            # Analyser les patterns
            best_pattern = self._identify_best_pattern(trades_df)
            worst_pattern = self._identify_worst_pattern(trades_df)
            
            # Identifier les domaines d'amélioration
            improvement_areas = self._identify_improvement_areas(trades_df)
            strengths = self._identify_strengths(trades_df)
            
            return DailyPerformance(
                date=date,
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=win_rate,
                total_pnl=total_pnl,
                avg_win=avg_win,
                avg_loss=avg_loss,
                max_win=max_win,
                max_loss=max_loss,
                profit_factor=profit_factor,
                largest_drawdown=largest_drawdown,
                best_pattern=best_pattern,
                worst_pattern=worst_pattern,
                improvement_areas=improvement_areas,
                strengths=strengths
            )
            
        except Exception as e:
            self.logger.error(f"Erreur analyse performance quotidienne: {e}")
            return None
    
    def generate_personalized_advice(self, performance: DailyPerformance) -> List[MentorAdvice]:
        """Génère des conseils personnalisés basés sur la performance"""
        try:
            advice_list = []
            
            # Conseils basés sur le win rate
            if performance.win_rate >= self.mentor_config['performance_thresholds']['excellent_win_rate']:
                advice_list.append(self._create_celebration_advice(performance))
            elif performance.win_rate <= self.mentor_config['performance_thresholds']['critical_win_rate']:
                advice_list.append(self._create_critical_advice(performance))
            
            # Conseils basés sur le profit factor
            if performance.profit_factor < self.mentor_config['performance_thresholds']['concerning_profit_factor']:
                advice_list.append(self._create_profit_factor_advice(performance))
            
            # Conseils basés sur les patterns
            if performance.worst_pattern:
                advice_list.append(self._create_pattern_advice(performance))
            
            # Conseils basés sur le drawdown
            if performance.largest_drawdown < -500:  # Seuil de drawdown
                advice_list.append(self._create_drawdown_advice(performance))
            
            # Conseils généraux d'amélioration
            if performance.improvement_areas:
                advice_list.append(self._create_improvement_advice(performance))
            
            # Conseils contextuels basés sur l'heure et le jour
            context_advice = self._create_contextual_advice(performance)
            if context_advice:
                advice_list.append(context_advice)
            
            # Conseils de motivation
            motivation_advice = self._create_motivation_advice(performance)
            if motivation_advice:
                advice_list.append(motivation_advice)
            
            return advice_list
            
        except Exception as e:
            self.logger.error(f"Erreur génération conseils: {e}")
            return []
    
    async def send_daily_mentor_message(self, performance: DailyPerformance, advice_list: List[MentorAdvice]) -> bool:
        """Envoie le message quotidien du mentor sur Discord"""
        try:
            if not self.discord_webhook_url:
                self.logger.warning("URL Discord webhook non configurée")
                return False
            
            # Créer l'embed Discord
            embed = self._create_discord_embed(performance, advice_list)
            
            # Envoyer via webhook
            async with aiohttp.ClientSession() as session:
                payload = {
                    "embeds": [embed],
                    "username": "🎓 MIA Mentor System",
                    "avatar_url": "https://cdn.discordapp.com/emojis/1234567890.png"
                }
                
                async with session.post(self.discord_webhook_url, json=payload) as response:
                    if response.status == 204:
                        self.logger.info("✅ Message mentor envoyé avec succès")
                        self.daily_message_count += 1
                        return True
                    else:
                        self.logger.error(f"❌ Erreur envoi message: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Erreur envoi message mentor: {e}")
            return False
    
    def _create_discord_embed(self, performance: DailyPerformance, advice_list: List[MentorAdvice]) -> Dict[str, Any]:
        """Crée l'embed Discord pour le message du mentor"""
        try:
            # Déterminer la couleur et l'humeur
            color, mood = self._determine_mood_and_color(performance)
            
            # Créer l'embed
            embed = {
                "title": f"🎓 RAPPORT MENTOR - {performance.date.strftime('%d/%m/%Y')}",
                "color": color,
                "description": self._generate_description(performance, mood),
                "fields": [],
                "footer": {
                    "text": "MIA IA System - Mentor Automatique"
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Ajouter les champs de performance
            embed["fields"].extend([
                {
                    "name": "📊 PERFORMANCE",
                    "value": f"**Trades:** {performance.total_trades}\n"
                            f"**Gagnants:** {performance.winning_trades}\n"
                            f"**Perdants:** {performance.losing_trades}\n"
                            f"**Win Rate:** {performance.win_rate:.1%}",
                    "inline": True
                },
                {
                    "name": "💰 RÉSULTATS",
                    "value": f"**PnL Total:** ${performance.total_pnl:,.2f}\n"
                            f"**Gain Moyen:** ${performance.avg_win:,.2f}\n"
                            f"**Perte Moyenne:** ${performance.avg_loss:,.2f}\n"
                            f"**Profit Factor:** {performance.profit_factor:.2f}",
                    "inline": True
                }
            ])
            
            # Ajouter les conseils
            if advice_list:
                advice_text = "\n".join([f"• {advice.message}" for advice in advice_list[:3]])
                embed["fields"].append({
                    "name": "💡 CONSEILS DU MENTOR",
                    "value": advice_text,
                    "inline": False
                })
            
            # Ajouter les domaines d'amélioration
            if performance.improvement_areas:
                improvement_text = "\n".join([f"• {area}" for area in performance.improvement_areas[:3]])
                embed["fields"].append({
                    "name": "🎯 DOMAINES D'AMÉLIORATION",
                    "value": improvement_text,
                    "inline": False
                })
            
            return embed
            
        except Exception as e:
            self.logger.error(f"Erreur création embed Discord: {e}")
            return {}
    
    def _determine_mood_and_color(self, performance: DailyPerformance) -> Tuple[int, str]:
        """Détermine l'humeur et la couleur basées sur la performance"""
        try:
            if performance.win_rate >= self.mentor_config['performance_thresholds']['excellent_win_rate']:
                return 0x00FF00, "excellent"  # Vert
            elif performance.win_rate >= self.mentor_config['performance_thresholds']['good_win_rate']:
                return 0x00AAFF, "good"  # Bleu
            elif performance.win_rate >= self.mentor_config['performance_thresholds']['concerning_win_rate']:
                return 0xFFFF00, "neutral"  # Jaune
            elif performance.win_rate >= self.mentor_config['performance_thresholds']['critical_win_rate']:
                return 0xFF8800, "concerned"  # Orange
            else:
                return 0xFF0000, "critical"  # Rouge
        except Exception:
            return 0x808080, "neutral"  # Gris par défaut
    
    def _generate_description(self, performance: DailyPerformance, mood: str) -> str:
        """Génère la description du message avec plus de personnalisation"""
        try:
            # Messages plus détaillés et motivants
            if mood == "excellent":
                messages = [
                    f"🌟 **EXCELLENTE PERFORMANCE !** Vous avez dominé le marché aujourd'hui avec un win rate de {performance.win_rate:.1%} !",
                    f"🏆 **MAÎTRISE TOTALE !** {performance.win_rate:.1%} de réussite - vous êtes en feu !",
                    f"💎 **PERFORMANCE DIAMANT !** {performance.total_trades} trades, {performance.win_rate:.1%} win rate - continuez cette domination !"
                ]
                return np.random.choice(messages)
                
            elif mood == "good":
                messages = [
                    f"👍 **BONNE PERFORMANCE** - Win rate de {performance.win_rate:.1%}, vous êtes sur la bonne voie !",
                    f"📈 **PROGRESSION SOLIDE** - {performance.win_rate:.1%} de réussite, quelques ajustements pour exceller !",
                    f"🎯 **OBJECTIF ATTEINT** - Win rate de {performance.win_rate:.1%}, vous respectez votre plan !"
                ]
                return np.random.choice(messages)
                
            elif mood == "neutral":
                messages = [
                    f"🤔 **PERFORMANCE MIXTE** - Win rate de {performance.win_rate:.1%}, analysez vos entrées et sorties.",
                    f"⚖️ **ÉQUILIBRE À TROUVER** - {performance.win_rate:.1%} de réussite, focus sur la qualité des trades.",
                    f"🔄 **AJUSTEMENTS NÉCESSAIRES** - Win rate de {performance.win_rate:.1%}, optimisez votre approche."
                ]
                return np.random.choice(messages)
                
            elif mood == "concerned":
                messages = [
                    f"⚠️ **PERFORMANCE PRÉOCCUPANTE** - Win rate de {performance.win_rate:.1%}, revoyez votre stratégie.",
                    f"🚨 **ALERTE QUALITÉ** - {performance.win_rate:.1%} de réussite, action immédiate requise.",
                    f"📉 **DÉGRADATION DÉTECTÉE** - Win rate de {performance.win_rate:.1%}, analysez vos erreurs."
                ]
                return np.random.choice(messages)
                
            else:
                messages = [
                    f"🚨 **PERFORMANCE CRITIQUE** - Win rate de {performance.win_rate:.1%}, STOP et analysez !",
                    f"💥 **URGENCE DÉTECTÉE** - {performance.win_rate:.1%} de réussite, action immédiate !",
                    f"🛑 **ARRÊT OBLIGATOIRE** - Win rate de {performance.win_rate:.1%}, revoyez tout !"
                ]
                return np.random.choice(messages)
                
        except Exception:
            return "📊 Analyse de performance quotidienne"
    
    def _create_celebration_advice(self, performance: DailyPerformance) -> MentorAdvice:
        """Crée un conseil de célébration personnalisé"""
        messages = [
            f"🌟 **CÉLÉBRATION !** Performance exceptionnelle ! Win rate de {performance.win_rate:.1%} et profit factor de {performance.profit_factor:.2f}. Vous maîtrisez parfaitement votre méthode !",
            f"🏆 **EXCELLENCE !** {performance.win_rate:.1%} de réussite avec un profit factor de {performance.profit_factor:.2f}. Vous êtes un trader d'élite !",
            f"💎 **MAÎTRISE TOTALE !** Win rate de {performance.win_rate:.1%} et profit factor de {performance.profit_factor:.2f}. Continuez sur cette lancée, vous êtes en feu !"
        ]
        
        return MentorAdvice(
            advice_id=f"CELEBRATION_{performance.date.strftime('%Y%m%d')}",
            timestamp=datetime.now(),
            advice_type=MentorMessageType.CELEBRATION,
            level=MentorAdviceLevel.SUCCESS,
            title="🌟 CÉLÉBRATION !",
            message=np.random.choice(messages),
            data={"win_rate": performance.win_rate, "profit_factor": performance.profit_factor}
        )
    
    def _create_critical_advice(self, performance: DailyPerformance) -> MentorAdvice:
        """Crée un conseil critique avec actions concrètes"""
        actions = [
            "1. Arrêtez le trading immédiatement",
            "2. Analysez vos 5 derniers trades perdants",
            "3. Vérifiez votre gestion du risque",
            "4. Revenez à votre plan de trading",
            "5. Considérez une pause de 24h"
        ]
        
        messages = [
            f"🚨 **ALERTE CRITIQUE** - Win rate de {performance.win_rate:.1%}. Actions immédiates : {' | '.join(actions[:3])}",
            f"💥 **URGENCE DÉTECTÉE** - {performance.win_rate:.1%} de réussite. Priorités : {' | '.join(actions[:2])}",
            f"🛑 **ARRÊT OBLIGATOIRE** - Win rate de {performance.win_rate:.1%}. Plan d'action : {' | '.join(actions[:3])}"
        ]
        
        return MentorAdvice(
            advice_id=f"CRITICAL_{performance.date.strftime('%Y%m%d')}",
            timestamp=datetime.now(),
            advice_type=MentorMessageType.PERFORMANCE_ALERT,
            level=MentorAdviceLevel.CRITICAL,
            title="🚨 ALERTE CRITIQUE",
            message=np.random.choice(messages),
            data={"win_rate": performance.win_rate, "actions": actions}
        )
    
    def _create_profit_factor_advice(self, performance: DailyPerformance) -> MentorAdvice:
        """Crée un conseil sur le profit factor avec solutions"""
        solutions = [
            "Augmentez votre ratio gain/perte (2:1 minimum)",
            "Réduisez la taille des positions perdantes",
            "Améliorez vos points de sortie",
            "Utilisez des trailing stops",
            "Focus sur les trades à fort potentiel"
        ]
        
        messages = [
            f"📉 **PROFIT FACTOR FAIBLE** ({performance.profit_factor:.2f}). Solutions : {' | '.join(solutions[:2])}",
            f"💰 **RATIO GAIN/PERTE** à améliorer ({performance.profit_factor:.2f}). Actions : {' | '.join(solutions[:3])}",
            f"⚖️ **ÉQUILIBRE À TROUVER** - Profit factor de {performance.profit_factor:.2f}. Focus : {' | '.join(solutions[:2])}"
        ]
        
        return MentorAdvice(
            advice_id=f"PROFIT_FACTOR_{performance.date.strftime('%Y%m%d')}",
            timestamp=datetime.now(),
            advice_type=MentorMessageType.IMPROVEMENT_SUGGESTION,
            level=MentorAdviceLevel.WARNING,
            title="📉 PROFIT FACTOR FAIBLE",
            message=np.random.choice(messages),
            data={"profit_factor": performance.profit_factor, "solutions": solutions}
        )
    
    def _create_pattern_advice(self, performance: DailyPerformance) -> MentorAdvice:
        """Crée un conseil sur les patterns avec solutions spécifiques"""
        pattern_solutions = {
            "Trades perdants répétitifs": [
                "Vérifiez votre timing d'entrée",
                "Analysez les conditions de marché",
                "Améliorez votre filtrage de signaux"
            ],
            "Pattern non identifié": [
                "Documentez vos trades",
                "Identifiez vos patterns récurrents",
                "Analysez vos meilleurs trades"
            ],
            "Aucun pattern perdant": [
                "Continuez votre approche actuelle",
                "Optimisez vos points de sortie",
                "Maintenez votre discipline"
            ]
        }
        
        solutions = pattern_solutions.get(performance.worst_pattern, [
            "Analysez vos patterns perdants",
            "Améliorez votre filtrage",
            "Optimisez votre approche"
        ])
        
        messages = [
            f"🔄 **PATTERN PROBLÉMATIQUE** : {performance.worst_pattern}. Solutions : {' | '.join(solutions[:2])}",
            f"🎯 **OPTIMISATION PATTERN** - {performance.worst_pattern}. Actions : {' | '.join(solutions[:3])}",
            f"📊 **ANALYSE PATTERN** - {performance.worst_pattern}. Focus : {' | '.join(solutions[:2])}"
        ]
        
        return MentorAdvice(
            advice_id=f"PATTERN_{performance.date.strftime('%Y%m%d')}",
            timestamp=datetime.now(),
            advice_type=MentorMessageType.HABIT_WARNING,
            level=MentorAdviceLevel.WARNING,
            title="🔄 PATTERN PROBLÉMATIQUE",
            message=np.random.choice(messages),
            data={"worst_pattern": performance.worst_pattern, "solutions": solutions}
        )
    
    def _create_drawdown_advice(self, performance: DailyPerformance) -> MentorAdvice:
        """Crée un conseil sur le drawdown avec actions concrètes"""
        drawdown_actions = [
            "Réduisez la taille des positions de 50%",
            "Augmentez vos stops loss",
            "Limitez le nombre de trades simultanés",
            "Utilisez des stops trailing",
            "Pause de trading de 2-4h"
        ]
        
        messages = [
            f"📉 **DRAWDOWN ÉLEVÉ** (${abs(performance.largest_drawdown):,.2f}). Actions : {' | '.join(drawdown_actions[:3])}",
            f"🚨 **GESTION RISQUE** - Drawdown de ${abs(performance.largest_drawdown):,.2f}. Priorités : {' | '.join(drawdown_actions[:2])}",
            f"⚠️ **ALERTE DRAWDOWN** - ${abs(performance.largest_drawdown):,.2f}. Plan : {' | '.join(drawdown_actions[:3])}"
        ]
        
        return MentorAdvice(
            advice_id=f"DRAWDOWN_{performance.date.strftime('%Y%m%d')}",
            timestamp=datetime.now(),
            advice_type=MentorMessageType.PERFORMANCE_ALERT,
            level=MentorAdviceLevel.WARNING,
            title="📉 DRAWDOWN ÉLEVÉ",
            message=np.random.choice(messages),
            data={"drawdown": performance.largest_drawdown, "actions": drawdown_actions}
        )
    
    def _create_improvement_advice(self, performance: DailyPerformance) -> MentorAdvice:
        """Crée un conseil d'amélioration avec plan d'action"""
        improvement_plans = {
            "Améliorer la qualité des entrées": [
                "Attendez des signaux plus clairs",
                "Vérifiez la confluence des indicateurs",
                "Analysez les conditions de marché"
            ],
            "Réduire la taille des positions": [
                "Divisez par 2 la taille des positions",
                "Utilisez des stops plus serrés",
                "Limitez le risque par trade à 1%"
            ],
            "Améliorer la consistance": [
                "Stickez à votre plan de trading",
                "Évitez les trades impulsifs",
                "Documentez chaque décision"
            ]
        }
        
        areas = performance.improvement_areas[:2]
        plans = []
        for area in areas:
            if area in improvement_plans:
                plans.extend(improvement_plans[area])
        
        if not plans:
            plans = [
                "Analysez vos trades perdants",
                "Optimisez votre approche",
                "Maintenez votre discipline"
            ]
        
        messages = [
            f"🎯 **DOMAINES D'AMÉLIORATION** : {', '.join(areas)}. Plan : {' | '.join(plans[:3])}",
            f"📈 **OPTIMISATION** - Focus sur : {', '.join(areas)}. Actions : {' | '.join(plans[:2])}",
            f"🔧 **AMÉLIORATION** - {', '.join(areas)}. Solutions : {' | '.join(plans[:3])}"
        ]
        
        return MentorAdvice(
            advice_id=f"IMPROVEMENT_{performance.date.strftime('%Y%m%d')}",
            timestamp=datetime.now(),
            advice_type=MentorMessageType.IMPROVEMENT_SUGGESTION,
            level=MentorAdviceLevel.INFO,
            title="🎯 DOMAINES D'AMÉLIORATION",
            message=np.random.choice(messages),
            data={"improvement_areas": performance.improvement_areas, "plans": plans}
        )
    
    def _load_daily_trades(self, date: datetime) -> pd.DataFrame:
        """Charge les trades d'une journée"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT * FROM trades 
                    WHERE DATE(timestamp) = DATE(?) 
                    ORDER BY timestamp
                """
                return pd.read_sql_query(query, conn, params=(date,))
        except Exception as e:
            self.logger.error(f"Erreur chargement trades: {e}")
            return pd.DataFrame()
    
    def _calculate_drawdown(self, pnl_series: pd.Series) -> float:
        """Calcule le drawdown maximum"""
        try:
            cumulative = pnl_series.cumsum()
            running_max = cumulative.expanding().max()
            drawdown = cumulative - running_max
            return drawdown.min()
        except Exception:
            return 0.0
    
    def _identify_best_pattern(self, trades_df: pd.DataFrame) -> str:
        """Identifie le meilleur pattern"""
        try:
            if trades_df.empty:
                return "Aucun pattern"
            
            # Logique simple d'identification de pattern
            winning_trades = trades_df[trades_df['pnl'] > 0]
            if len(winning_trades) > 0:
                return "Trades gagnants cohérents"
            else:
                return "Aucun pattern gagnant"
        except Exception:
            return "Pattern non identifié"
    
    def _identify_worst_pattern(self, trades_df: pd.DataFrame) -> str:
        """Identifie le pire pattern"""
        try:
            if trades_df.empty:
                return "Aucun pattern"
            
            # Logique simple d'identification de pattern
            losing_trades = trades_df[trades_df['pnl'] < 0]
            if len(losing_trades) > 0:
                return "Trades perdants répétitifs"
            else:
                return "Aucun pattern perdant"
        except Exception:
            return "Pattern non identifié"
    
    def _identify_improvement_areas(self, trades_df: pd.DataFrame) -> List[str]:
        """Identifie les domaines d'amélioration"""
        try:
            areas = []
            
            if len(trades_df) < 3:
                return ["Plus de données nécessaires"]
            
            # Analyser le win rate
            win_rate = len(trades_df[trades_df['pnl'] > 0]) / len(trades_df)
            if win_rate < 0.5:
                areas.append("Améliorer la qualité des entrées")
            
            # Analyser la gestion du risque
            avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean()
            if avg_loss < -200:
                areas.append("Réduire la taille des positions")
            
            # Analyser la consistance
            pnl_std = trades_df['pnl'].std()
            if pnl_std > 300:
                areas.append("Améliorer la consistance")
            
            return areas if areas else ["Performance stable"]
        except Exception:
            return ["Analyse non disponible"]
    
    def _identify_strengths(self, trades_df: pd.DataFrame) -> List[str]:
        """Identifie les forces"""
        try:
            strengths = []
            
            if len(trades_df) < 3:
                return ["Données insuffisantes"]
            
            # Analyser le win rate
            win_rate = len(trades_df[trades_df['pnl'] > 0]) / len(trades_df)
            if win_rate > 0.6:
                strengths.append("Excellent taux de réussite")
            
            # Analyser la gestion du risque
            avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean()
            if avg_loss > -150:
                strengths.append("Bonne gestion du risque")
            
            # Analyser la consistance
            pnl_std = trades_df['pnl'].std()
            if pnl_std < 200:
                strengths.append("Performance cohérente")
            
            return strengths if strengths else ["Forces à identifier"]
        except Exception:
            return ["Analyse non disponible"]
    
    async def should_send_daily_report(self) -> bool:
        """Détermine si un rapport quotidien doit être envoyé"""
        try:
            now = datetime.now()
            today = now.date()
            
            # Vérifier si on a déjà envoyé un rapport aujourd'hui
            if self.last_report_date == today:
                return False
            
            # Vérifier l'heure (après 18h00)
            if now.hour < 18:
                return False
            
            # Vérifier le nombre de messages quotidiens
            if self.daily_message_count >= self.mentor_config['max_daily_messages']:
                return False
            
            return True
        except Exception:
            return False
    
    async def run_daily_mentor_analysis(self) -> bool:
        """Exécute l'analyse quotidienne du mentor"""
        try:
            # Vérifier si on doit envoyer un rapport
            if not await self.should_send_daily_report():
                return False
            
            # Analyser la performance
            performance = await self.analyze_daily_performance()
            if not performance:
                self.logger.info("Aucune donnée pour l'analyse quotidienne")
                return False
            
            # Générer les conseils
            advice_list = self.generate_personalized_advice(performance)
            
            # Envoyer le message
            success = await self.send_daily_mentor_message(performance, advice_list)
            
            if success:
                self.last_report_date = datetime.now().date()
                self.logger.info("✅ Analyse quotidienne du mentor terminée")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erreur analyse quotidienne mentor: {e}")
            return False

# === FONCTIONS UTILITAIRES ===

def create_mentor_system(discord_webhook_url: str, db_path: str = "data/lessons_learned.db") -> MentorSystem:
    """Crée une instance du Mentor System"""
    return MentorSystem(discord_webhook_url, db_path)

async def send_mentor_message(webhook_url: str, performance: DailyPerformance, advice_list: List[MentorAdvice]) -> bool:
    """Fonction utilitaire pour envoyer un message mentor"""
    try:
        mentor = create_mentor_system(webhook_url)
        return await mentor.send_daily_mentor_message(performance, advice_list)
    except Exception as e:
        logging.error(f"Erreur envoi message mentor: {e}")
        return False

# === TEST ===

def test_mentor_system():
    """Test du module Mentor System"""
    try:
        # URL de test (remplacer par la vraie URL)
        test_webhook = "https://discordapp.com/api/webhooks/1389206555282640987/v0WvrD3ntDkwGJIyxRh0EEAFNoh1NpSY8Oloxy8tWMZjsFGRed_OYpG1zaSdP2dWH2j7"
        
        mentor = create_mentor_system(test_webhook)
        print("✅ Mentor System créé avec succès")
        
        # Test d'analyse de performance
        performance = asyncio.run(mentor.analyze_daily_performance())
        if performance:
            print(f"✅ Performance analysée: {performance.total_trades} trades")
            
            # Test de génération de conseils
            advice_list = mentor.generate_personalized_advice(performance)
            print(f"✅ {len(advice_list)} conseils générés")
        
        print("✅ Test Mentor System terminé")
        
    except Exception as e:
        print(f"❌ Erreur test Mentor System: {e}")

if __name__ == "__main__":
    test_mentor_system() 