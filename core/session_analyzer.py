#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Session Context Analyzer
Analyse automatique du contexte de session pour optimisation dynamique
Version: Production Ready v1.0 - Priorité HAUTE
"""

import time
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from core.logger import get_logger
import statistics
import pandas as pd
from collections import deque, defaultdict

logger = get_logger(__name__)

class SessionPhase(Enum):
    """Phases de session de trading"""
    PRE_MARKET = "pre_market"
    LONDON_OPEN = "london_open"
    NY_OPENING = "ny_opening"  
    NY_SESSION = "ny_session"
    NY_LUNCH = "ny_lunch"
    NY_CLOSE = "ny_close"
    AFTER_HOURS = "after_hours"
    ASIA_SESSION = "asia_session"

class MarketRegime(Enum):
    """Régimes de marché"""
    TRENDING_BULLISH = "trending_bullish"
    TRENDING_BEARISH = "trending_bearish"
    RANGING_TIGHT = "ranging_tight"
    RANGING_WIDE = "ranging_wide"
    VOLATILE_CHOPPY = "volatile_choppy"
    LOW_VOLUME = "low_volume"
    NEWS_DRIVEN = "news_driven"

class VolatilityRegime(Enum):
    """Régimes de volatilité"""
    VERY_LOW = "very_low"      # < 10 points ES
    LOW = "low"                # 10-20 points
    NORMAL = "normal"          # 20-40 points
    HIGH = "high"              # 40-60 points
    EXTREME = "extreme"        # > 60 points

@dataclass
class SessionContext:
    """Contexte complet d'une session"""
    # Timing
    session_phase: SessionPhase
    session_start: datetime
    minutes_elapsed: int
    time_until_close: int
    
    # Market conditions
    market_regime: MarketRegime
    volatility_regime: VolatilityRegime
    volume_profile: str  # "low", "normal", "high"
    spread_regime: str   # "tight", "normal", "wide"
    
    # Performance metrics
    session_range: float
    session_volume: int
    avg_trade_duration: float
    dominant_direction: str  # "bullish", "bearish", "neutral"
    
    # Dynamic parameters suggestions
    confluence_threshold: float
    position_size_multiplier: float
    time_filter_active: bool
    risk_multiplier: float
    
    # Session statistics
    total_signals: int
    signals_taken: int
    win_rate: float
    avg_pnl_per_trade: float
    
    # Context scoring
    session_quality_score: float  # 0-1
    signal_reliability: float     # 0-1
    execution_conditions: float   # 0-1

class SessionContextAnalyzer:
    """
    🕐 SESSION CONTEXT ANALYZER
    
    Analyse le contexte de session en temps réel pour optimiser :
    - Seuils de confluence selon la session
    - Taille de position selon volatilité
    - Filtres temporels selon l'heure
    - Gestion du risque selon conditions
    """
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.SessionContextAnalyzer")
        
        # Configuration par défaut
        self.session_rules = {
            SessionPhase.LONDON_OPEN: {
                'confluence_threshold': 0.85,
                'position_size_multiplier': 0.8,
                'risk_multiplier': 1.2,
                'time_filter_active': True
            },
            SessionPhase.NY_OPENING: {
                'confluence_threshold': 0.75,
                'position_size_multiplier': 1.0,
                'risk_multiplier': 1.0,
                'time_filter_active': False
            },
            SessionPhase.NY_SESSION: {
                'confluence_threshold': 0.70,
                'position_size_multiplier': 1.0,
                'risk_multiplier': 0.9,
                'time_filter_active': False
            },
            SessionPhase.NY_LUNCH: {
                'confluence_threshold': 0.80,
                'position_size_multiplier': 0.6,
                'risk_multiplier': 1.3,
                'time_filter_active': True
            },
            SessionPhase.NY_CLOSE: {
                'confluence_threshold': 0.85,
                'position_size_multiplier': 0.7,
                'risk_multiplier': 1.1,
                'time_filter_active': True
            }
        }
        
        # Historique et métriques
        self.session_history = deque(maxlen=100)
        self.current_session_data = {
            'start_time': None,
            'trades': [],
            'signals': [],
            'price_high': None,
            'price_low': None,
            'volume_data': deque(maxlen=500)
        }
        
        # Cache pour optimisation
        self.context_cache = {}
        self.cache_timestamp = 0
        self.cache_duration = 60  # secondes
        
        self.logger.info("📅 Session Context Analyzer initialisé")
    
    def get_current_session_phase(self) -> SessionPhase:
        """Détermine la phase de session actuelle basée sur l'heure UTC"""
        now = datetime.now(timezone.utc)
        hour = now.hour
        minute = now.minute
        
        # Londres : 8h-17h UTC (ajustement DST automatique)
        if 8 <= hour < 9:
            return SessionPhase.LONDON_OPEN
        # New York : 14h30-21h UTC 
        elif hour == 14 and minute >= 30:
            return SessionPhase.NY_OPENING
        elif 15 <= hour < 17:
            return SessionPhase.NY_SESSION
        elif 17 <= hour < 19:
            return SessionPhase.NY_LUNCH
        elif 19 <= hour < 21:
            return SessionPhase.NY_CLOSE
        elif 21 <= hour <= 23:
            return SessionPhase.AFTER_HOURS
        # Asie : 1h-8h UTC
        elif 1 <= hour < 8:
            return SessionPhase.ASIA_SESSION
        else:
            return SessionPhase.PRE_MARKET
    
    def analyze_market_regime(self, market_data: 'MarketData', lookback_periods: int = 50) -> MarketRegime:
        """Analyse le régime de marché basé sur les données récentes"""
        try:
            # Simulation avec données disponibles
            current_price = getattr(market_data, 'close', getattr(market_data, 'price', 4500.0))
            high = getattr(market_data, 'high', current_price + 5)
            low = getattr(market_data, 'low', current_price - 5)
            volume = getattr(market_data, 'volume', 1000)
            
            # Calcul de la range de session
            session_range = high - low
            
            # Détermination du régime basé sur la volatilité et range
            if session_range < 10:
                return MarketRegime.RANGING_TIGHT
            elif session_range > 40:
                if volume > 5000:
                    return MarketRegime.VOLATILE_CHOPPY
                else:
                    return MarketRegime.RANGING_WIDE
            else:
                # Tendance basée sur la position dans la range
                mid_point = (high + low) / 2
                if current_price > mid_point + (session_range * 0.2):
                    return MarketRegime.TRENDING_BULLISH
                elif current_price < mid_point - (session_range * 0.2):
                    return MarketRegime.TRENDING_BEARISH
                else:
                    return MarketRegime.RANGING_TIGHT
                    
        except Exception as e:
            self.logger.warning(f"Erreur analyse régime marché: {e}")
            return MarketRegime.RANGING_TIGHT
    
    def analyze_volatility_regime(self, market_data: 'MarketData') -> VolatilityRegime:
        """Analyse le régime de volatilité"""
        try:
            current_price = getattr(market_data, 'close', getattr(market_data, 'price', 4500.0))
            high = getattr(market_data, 'high', current_price + 5)
            low = getattr(market_data, 'low', current_price - 5)
            
            session_range = high - low
            
            if session_range < 10:
                return VolatilityRegime.VERY_LOW
            elif session_range < 20:
                return VolatilityRegime.LOW
            elif session_range < 40:
                return VolatilityRegime.NORMAL
            elif session_range < 60:
                return VolatilityRegime.HIGH
            else:
                return VolatilityRegime.EXTREME
                
        except Exception as e:
            self.logger.warning(f"Erreur analyse volatilité: {e}")
            return VolatilityRegime.NORMAL
    
    def get_dynamic_parameters(self, session_phase: SessionPhase, market_regime: MarketRegime, 
                              volatility_regime: VolatilityRegime) -> Dict[str, Any]:
        """Calcule les paramètres dynamiques optimaux"""
        
        # Base parameters from session rules
        base_params = self.session_rules.get(session_phase, {
            'confluence_threshold': 0.75,
            'position_size_multiplier': 1.0,
            'risk_multiplier': 1.0,
            'time_filter_active': False
        })
        
        # Adjustments based on market regime
        confluence_adj = 0.0
        position_adj = 0.0
        risk_adj = 0.0
        
        if market_regime == MarketRegime.TRENDING_BULLISH:
            confluence_adj = -0.05  # Plus permissif en tendance
            position_adj = 0.2
        elif market_regime == MarketRegime.TRENDING_BEARISH:
            confluence_adj = -0.05
            position_adj = 0.2
        elif market_regime == MarketRegime.RANGING_TIGHT:
            confluence_adj = 0.10  # Plus strict en range
            position_adj = -0.3
            risk_adj = 0.2
        elif market_regime == MarketRegime.VOLATILE_CHOPPY:
            confluence_adj = 0.15
            position_adj = -0.5
            risk_adj = 0.5
        
        # Adjustments based on volatility regime
        if volatility_regime == VolatilityRegime.VERY_LOW:
            position_adj += -0.2
            risk_adj += 0.3
        elif volatility_regime == VolatilityRegime.EXTREME:
            confluence_adj += 0.10
            position_adj += -0.4
            risk_adj += 0.6
        
        # Apply adjustments
        dynamic_params = {
            'confluence_threshold': max(0.60, min(0.95, base_params['confluence_threshold'] + confluence_adj)),
            'position_size_multiplier': max(0.3, min(2.0, base_params['position_size_multiplier'] + position_adj)),
            'risk_multiplier': max(0.5, min(3.0, base_params['risk_multiplier'] + risk_adj)),
            'time_filter_active': base_params['time_filter_active']
        }
        
        return dynamic_params
    
    def calculate_session_quality_score(self, context: SessionContext) -> float:
        """Calcule un score de qualité de session (0-1)"""
        score = 0.0
        
        # Volume score (30%)
        if context.volume_profile == "high":
            score += 0.30
        elif context.volume_profile == "normal":
            score += 0.20
        else:
            score += 0.10
        
        # Spread score (20%)
        if context.spread_regime == "tight":
            score += 0.20
        elif context.spread_regime == "normal":
            score += 0.15
        else:
            score += 0.05
        
        # Volatility score (25%)
        if context.volatility_regime in [VolatilityRegime.NORMAL, VolatilityRegime.HIGH]:
            score += 0.25
        elif context.volatility_regime == VolatilityRegime.LOW:
            score += 0.15
        else:
            score += 0.05
        
        # Session phase score (25%)
        favorable_phases = [SessionPhase.NY_OPENING, SessionPhase.NY_SESSION, SessionPhase.LONDON_OPEN]
        if context.session_phase in favorable_phases:
            score += 0.25
        else:
            score += 0.10
        
        return min(1.0, score)
    
    def analyze_session_context(self, market_data: 'MarketData', 
                               session_stats: Optional[Dict] = None) -> SessionContext:
        """
        Analyse complète du contexte de session
        
        Args:
            market_data: Données de marché actuelles
            session_stats: Statistiques de session optionnelles
            
        Returns:
            SessionContext complet avec paramètres optimisés
        """
        
        # Cache check
        current_time = time.time()
        if (current_time - self.cache_timestamp) < self.cache_duration and self.context_cache:
            cached_context = self.context_cache.copy()
            # Update only time-sensitive fields
            cached_context['minutes_elapsed'] = self._get_minutes_elapsed()
            cached_context['time_until_close'] = self._get_time_until_close()
            return SessionContext(**cached_context)
        
        try:
            # Basic session information
            session_phase = self.get_current_session_phase()
            market_regime = self.analyze_market_regime(market_data)
            volatility_regime = self.analyze_volatility_regime(market_data)
            
            # Market metrics
            current_price = getattr(market_data, 'close', getattr(market_data, 'price', 4500.0))
            volume = getattr(market_data, 'volume', 1000)
            session_range = getattr(market_data, 'high', current_price + 5) - getattr(market_data, 'low', current_price - 5)
            
            # Volume and spread analysis
            volume_profile = self._analyze_volume_profile(volume)
            spread_regime = self._analyze_spread_regime(market_data)
            
            # Dynamic parameters
            dynamic_params = self.get_dynamic_parameters(session_phase, market_regime, volatility_regime)
            
            # Session statistics
            stats = session_stats or {}
            total_signals = stats.get('total_signals', 0)
            signals_taken = stats.get('signals_taken', 0)
            win_rate = stats.get('win_rate', 0.0)
            avg_pnl = stats.get('avg_pnl_per_trade', 0.0)
            
            # Create context
            context = SessionContext(
                # Timing
                session_phase=session_phase,
                session_start=self._get_session_start(),
                minutes_elapsed=self._get_minutes_elapsed(),
                time_until_close=self._get_time_until_close(),
                
                # Market conditions
                market_regime=market_regime,
                volatility_regime=volatility_regime,
                volume_profile=volume_profile,
                spread_regime=spread_regime,
                
                # Performance metrics
                session_range=session_range,
                session_volume=volume,
                avg_trade_duration=stats.get('avg_trade_duration', 0.0),
                dominant_direction=self._get_dominant_direction(market_data),
                
                # Dynamic parameters
                confluence_threshold=dynamic_params['confluence_threshold'],
                position_size_multiplier=dynamic_params['position_size_multiplier'],
                time_filter_active=dynamic_params['time_filter_active'],
                risk_multiplier=dynamic_params['risk_multiplier'],
                
                # Session statistics
                total_signals=total_signals,
                signals_taken=signals_taken,
                win_rate=win_rate,
                avg_pnl_per_trade=avg_pnl,
                
                # Context scoring (will be calculated)
                session_quality_score=0.0,
                signal_reliability=0.0,
                execution_conditions=0.0
            )
            
            # Calculate scores
            context.session_quality_score = self.calculate_session_quality_score(context)
            context.signal_reliability = self._calculate_signal_reliability(context)
            context.execution_conditions = self._calculate_execution_conditions(context)
            
            # Cache result
            self.context_cache = asdict(context)
            self.cache_timestamp = current_time
            
            self.logger.debug(f"Session context analysé: {session_phase.value}, "
                            f"Score qualité: {context.session_quality_score:.2f}")
            
            return context
            
        except Exception as e:
            self.logger.error(f"Erreur analyse contexte session: {e}")
            # Return default context
            return self._get_default_context()
    
    def get_session_recommendations(self, context: SessionContext) -> Dict[str, Any]:
        """Génère des recommandations basées sur le contexte"""
        recommendations = {
            'trading_active': True,
            'suggested_confluence': context.confluence_threshold,
            'suggested_position_size': context.position_size_multiplier,
            'risk_adjustment': context.risk_multiplier,
            'time_filters': context.time_filter_active,
            'priority_level': 'normal'
        }
        
        # Quality-based adjustments
        if context.session_quality_score < 0.3:
            recommendations['trading_active'] = False
            recommendations['priority_level'] = 'low'
        elif context.session_quality_score > 0.8:
            recommendations['priority_level'] = 'high'
        
        # Volatility-based adjustments
        if context.volatility_regime == VolatilityRegime.EXTREME:
            recommendations['trading_active'] = False
            recommendations['priority_level'] = 'paused'
        
        return recommendations
    
    # Helper methods
    def _analyze_volume_profile(self, volume: int) -> str:
        """Analyse le profil de volume"""
        if volume > 10000:
            return "high"
        elif volume > 2000:
            return "normal"
        else:
            return "low"
    
    def _analyze_spread_regime(self, market_data: 'MarketData') -> str:
        """Analyse le régime de spread"""
        try:
            bid = getattr(market_data, 'bid', None)
            ask = getattr(market_data, 'ask', None)
            
            if bid and ask:
                spread = ask - bid
                if spread <= 0.25:
                    return "tight"
                elif spread <= 0.50:
                    return "normal"
                else:
                    return "wide"
            else:
                return "normal"  # Default when no bid/ask available
        except:
            return "normal"
    
    def _get_session_start(self) -> datetime:
        """Retourne l'heure de début de session"""
        if not self.current_session_data['start_time']:
            self.current_session_data['start_time'] = datetime.now(timezone.utc)
        return self.current_session_data['start_time']
    
    def _get_minutes_elapsed(self) -> int:
        """Minutes écoulées depuis le début de session"""
        session_start = self._get_session_start()
        return int((datetime.now(timezone.utc) - session_start).total_seconds() / 60)
    
    def _get_time_until_close(self) -> int:
        """Minutes jusqu'à la fermeture de session"""
        now = datetime.now(timezone.utc)
        
        # Calcul approximatif jusqu'à 21h UTC (fin NY)
        close_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
        if now.hour >= 21:
            close_time += timedelta(days=1)
        
        return int((close_time - now).total_seconds() / 60)
    
    def _get_dominant_direction(self, market_data: 'MarketData') -> str:
        """Détermine la direction dominante"""
        try:
            current_price = getattr(market_data, 'close', getattr(market_data, 'price', 4500.0))
            high = getattr(market_data, 'high', current_price + 5)
            low = getattr(market_data, 'low', current_price - 5)
            
            mid_point = (high + low) / 2
            
            if current_price > mid_point + 2:
                return "bullish"
            elif current_price < mid_point - 2:
                return "bearish"
            else:
                return "neutral"
        except:
            return "neutral"
    
    def _calculate_signal_reliability(self, context: SessionContext) -> float:
        """Calcule la fiabilité des signaux basée sur le contexte"""
        base_reliability = 0.5
        
        # Adjustments based on session quality
        if context.session_quality_score > 0.8:
            base_reliability += 0.3
        elif context.session_quality_score > 0.6:
            base_reliability += 0.2
        elif context.session_quality_score < 0.3:
            base_reliability -= 0.2
        
        # Adjustments based on volatility
        if context.volatility_regime == VolatilityRegime.NORMAL:
            base_reliability += 0.1
        elif context.volatility_regime == VolatilityRegime.EXTREME:
            base_reliability -= 0.3
        
        return max(0.0, min(1.0, base_reliability))
    
    def _calculate_execution_conditions(self, context: SessionContext) -> float:
        """Calcule la qualité des conditions d'exécution"""
        score = 0.5
        
        # Spread impact
        if context.spread_regime == "tight":
            score += 0.2
        elif context.spread_regime == "wide":
            score -= 0.2
        
        # Volume impact
        if context.volume_profile == "high":
            score += 0.2
        elif context.volume_profile == "low":
            score -= 0.2
        
        # Session phase impact
        favorable_phases = [SessionPhase.NY_OPENING, SessionPhase.NY_SESSION]
        if context.session_phase in favorable_phases:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _get_default_context(self) -> SessionContext:
        """Contexte par défaut en cas d'erreur"""
        return SessionContext(
            session_phase=SessionPhase.NY_SESSION,
            session_start=datetime.now(timezone.utc),
            minutes_elapsed=0,
            time_until_close=300,
            market_regime=MarketRegime.RANGING_TIGHT,
            volatility_regime=VolatilityRegime.NORMAL,
            volume_profile="normal",
            spread_regime="normal",
            session_range=20.0,
            session_volume=5000,
            avg_trade_duration=10.0,
            dominant_direction="neutral",
            confluence_threshold=0.75,
            position_size_multiplier=1.0,
            time_filter_active=False,
            risk_multiplier=1.0,
            total_signals=0,
            signals_taken=0,
            win_rate=0.0,
            avg_pnl_per_trade=0.0,
            session_quality_score=0.5,
            signal_reliability=0.5,
            execution_conditions=0.5
        )

# Factory function
def create_session_analyzer() -> SessionContextAnalyzer:
    """Factory pour créer le Session Context Analyzer"""
    return SessionContextAnalyzer()

# Exemple d'utilisation:
"""
# Dans automation_main.py:
session_analyzer = create_session_analyzer()

# Avant chaque décision de trading:
context = session_analyzer.analyze_session_context(market_data, session_stats)
recommendations = session_analyzer.get_session_recommendations(context)

# Utiliser les paramètres dynamiques:
confluence_threshold = context.confluence_threshold
position_size = base_position_size * context.position_size_multiplier
risk_multiplier = context.risk_multiplier
"""