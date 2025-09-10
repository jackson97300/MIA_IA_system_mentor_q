#!/usr/bin/env python3
"""
📊 MARKET STATE ANALYZER - MIA_IA_SYSTEM (patched)
Analyse l'état du marché et adapte automatiquement les seuils de leadership
- Corrélation 15m alignée + fallback neutre 0.0
- Volatilité réalisée bornée (0.1%..10%)
- Volume Z-score sans NaN (EWM fallback)
- Gamma avec hystérésis (near/expansion)
- Adaptation des seuils bornés + logging
- Session Europe/Paris TZ-safe
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from copy import deepcopy
from zoneinfo import ZoneInfo

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger

logger = get_logger(__name__)

# Constantes pour hystérésis gamma
_GAMMA_NEAR_IN  = 0.003   # 0.3%
_GAMMA_NEAR_OUT = 0.0045  # 0.45%
_GAMMA_EXP_IN   = 0.010   # 1.0%
_GAMMA_EXP_OUT  = 0.008   # 0.8%

@dataclass
class MarketState:
    """État du marché avec tous les régimes"""
    vol_regime: str          # 'low' | 'normal' | 'high'
    corr_15m: float          # corrélation rolling 15 min
    corr_regime: str         # 'weak' | 'normal' | 'tight'
    liq_regime: str          # 'thin' | 'normal' | 'thick'
    gamma_regime: str        # 'near_wall' | 'neutral' | 'expansion'
    session: str             # 'open' | 'mid' | 'power' | 'after'
    realized_vol: float      # Volatilité réalisée
    volume_zscore: float     # Z-score du volume
    gamma_distance: float    # Distance au mur gamma le plus proche

@dataclass
class LeadershipConfig:
    """Configuration adaptative du leadership"""
    corr_min: float = 0.75
    leader_strength_min: float = 0.35
    persistence_bars: int = 3
    risk_multiplier_tight_corr: float = 0.5
    risk_multiplier_weak_corr: float = 0.7     # PATCH: Ajouté
    allow_half_size_if_neutral: bool = False
    max_latency_ms: int = 50
    bars_timeframe_minutes: int = 1            # PATCH: Ajouté

class MarketStateAnalyzer:
    """Analyseur d'état de marché avec adaptation automatique des seuils"""
    
    def __init__(self, calibration: LeadershipConfig | None = None):
        self.cal = calibration  # PATCH: peut être None -> fallback valeurs actuelles
        self.last_analysis = None
        self.analysis_count = 0
        self.regime_history = []
        
        logger.info("📊 MarketStateAnalyzer initialisé")
    
    def compute_market_state(self, es_df: pd.DataFrame, nq_df: pd.DataFrame,
                           vwap: Optional[float] = None, 
                           gamma_levels: Optional[List[float]] = None,
                           clock: Optional[datetime] = None) -> MarketState:
        """
        Calcule l'état complet du marché
        
        Args:
            es_df: DataFrame ES avec données de marché
            nq_df: DataFrame NQ avec données de marché
            vwap: VWAP actuel (optionnel)
            gamma_levels: Niveaux gamma (optionnel)
            clock: Horloge actuelle (optionnel)
            
        Returns:
            MarketState avec tous les régimes
        """
        try:
            if clock is None:
                clock = datetime.now()
            
            # 1. Régime de volatilité (volatilité réalisée)
            realized_vol = self._compute_realized_volatility(es_df)
            vol_regime = self._classify_volatility_regime(realized_vol)
            
            # 2. Corrélations multi-fenêtres (PATCH: pondération 15m:60%, 5m:30%, 1m:10%)
            corr_15m = self._compute_correlation_15m(es_df, nq_df)
            corr_5m = self._compute_correlation_5m(es_df, nq_df)
            corr_1m = self._compute_correlation_1m(es_df, nq_df)
            corr_effective = self._calculate_weighted_correlation(corr_15m, corr_5m, corr_1m)
            corr_regime = self._classify_correlation_regime(corr_effective)
            
            # 3. Régime de liquidité (PATCH: sans NaN, EWM fallback)
            volume_zscore = self._compute_volume_zscore(es_df)
            liq_regime = self._classify_liquidity_regime(volume_zscore)
            
            # 4. Régime gamma (PATCH: avec hystérésis)
            gamma_distance = self._compute_gamma_distance(es_df, gamma_levels)
            gamma_regime = self._classify_gamma_regime(gamma_distance)
            
            # 5. Session (PATCH: timezone-safe)
            session = self._classify_session(clock)
            
            # Créer l'état de marché
            market_state = MarketState(
                vol_regime=vol_regime,
                corr_15m=corr_effective,  # PATCH: utiliser corrélation pondérée
                corr_regime=corr_regime,
                liq_regime=liq_regime,
                gamma_regime=gamma_regime,
                session=session,
                realized_vol=realized_vol,
                volume_zscore=volume_zscore,
                gamma_distance=gamma_distance
            )
            
            # Mise à jour des statistiques
            self.analysis_count += 1
            self.last_analysis = clock
            self.regime_history.append({
                'ts': clock.isoformat(),
                'vol_regime': vol_regime,
                'corr_regime': corr_regime,
                'liq_regime': liq_regime,
                'gamma_regime': gamma_regime,
                'session': session
            })
            
            return market_state
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse état marché: {e}")
            # Retourner un état par défaut (PATCH: corr neutre)
            return MarketState(
                vol_regime='normal',
                corr_15m=0.0,  # PATCH: neutre au lieu de 0.85
                corr_regime='normal',
                liq_regime='normal',
                gamma_regime='neutral',
                session='mid',
                realized_vol=0.01,
                volume_zscore=0.0,
                gamma_distance=1.0
            )
    
    def _compute_realized_volatility(self, df: pd.DataFrame) -> float:
        """Calcule la volatilité réalisée (PATCH: bornée)"""
        try:
            if len(df) < 100:
                return 0.01  # Valeur par défaut
            
            # Returns 1 minute sur 100 périodes
            returns = df['close'].pct_change().tail(100).dropna()
            if returns.empty:
                return 0.01
            
            # Volatilité annualisée (√390 pour 1 minute)
            realized_vol = float(returns.std() * np.sqrt(390))
            
            # PATCH: Bornes de sécurité (0.1%..10%)
            return float(np.clip(realized_vol, 0.001, 0.10))
            
        except Exception as e:
            logger.error(f"❌ Erreur volatilité réalisée: {e}")
            return 0.01
    
    def _classify_volatility_regime(self, realized_vol: float) -> str:
        """Classifie le régime de volatilité"""
        # PATCH: Utiliser les seuils de calibration si disponibles
        low = getattr(self.cal, "vol_low_threshold", 0.008) if self.cal else 0.008
        high = getattr(self.cal, "vol_high_threshold", 0.015) if self.cal else 0.015
        if realized_vol < low:
            return 'low'
        elif realized_vol > high:
            return 'high'
        else:
            return 'normal'
    
    def _compute_correlation_15m(self, es_df: pd.DataFrame, nq_df: pd.DataFrame) -> float:
        """Calcule la corrélation rolling sur 15 minutes (PATCH: robuste + min_bars)"""
        try:
            # On travaille sur des returns homogènes, avec min_periods pour éviter DoF<=0
            es_ret = es_df['close'].pct_change()
            nq_ret = nq_df['close'].pct_change()

            # fenêtre 15 "barres" (ton TF est à la minute), mais avec min_periods
            win = 15
            min_bars = max(2, int(win * 0.6))  # PATCH: minimum 2 barres
            
            es_tail = es_ret.tail(win).dropna()
            nq_tail = nq_ret.tail(win).dropna()

            if len(es_tail) < min_bars or len(nq_tail) < min_bars:
                # PATCH: fallback si échantillon trop court
                logger.debug(f"Corr 15m: échantillon insuffisant (ES:{len(es_tail)}, NQ:{len(nq_tail)}, min:{min_bars})")
                return 0.0

            # PATCH: Vérification supplémentaire pour éviter warnings NumPy
            if len(es_tail) <= 1 or len(nq_tail) <= 1:
                return 0.0

            with np.errstate(all='ignore'):
                corr = float(np.corrcoef(es_tail, nq_tail)[0,1])

            if not np.isfinite(corr):
                corr = 0.0

            # clamp
            corr = max(min(corr, 1.0), -1.0)
            return corr

        except Exception as e:
            logger.debug(f"Erreur corr 15m: {e}")
            return 0.0
    
    def _compute_correlation_5m(self, es_df: pd.DataFrame, nq_df: pd.DataFrame) -> float:
        """Calcule la corrélation ES/NQ sur 5 minutes (PATCH: robuste + min_bars)"""
        try:
            es_ret = es_df['close'].pct_change()
            nq_ret = nq_df['close'].pct_change()
            
            win = 5
            min_bars = max(2, int(win * 0.6))  # PATCH: minimum 2 barres
            
            es_tail = es_ret.tail(win).dropna()
            nq_tail = nq_ret.tail(win).dropna()
            
            if len(es_tail) < min_bars or len(nq_tail) < min_bars:
                logger.debug(f"Corr 5m: échantillon insuffisant (ES:{len(es_tail)}, NQ:{len(nq_tail)}, min:{min_bars})")
                return 0.0
            
            # PATCH: Vérification supplémentaire pour éviter warnings NumPy
            if len(es_tail) <= 1 or len(nq_tail) <= 1:
                return 0.0
            
            with np.errstate(all='ignore'):
                corr = float(np.corrcoef(es_tail, nq_tail)[0,1])
            
            if not np.isfinite(corr):
                corr = 0.0
                
            return max(min(corr, 1.0), -1.0)
            
        except Exception as e:
            logger.debug(f"Erreur corr 5m: {e}")
            return 0.0
    
    def _compute_correlation_1m(self, es_df: pd.DataFrame, nq_df: pd.DataFrame) -> float:
        """Calcule la corrélation ES/NQ sur 1 minute (PATCH: robuste + min_bars)"""
        try:
            if len(es_df) < 3 or len(nq_df) < 3:
                return 0.0
                
            es_ret = es_df['close'].pct_change()
            nq_ret = nq_df['close'].pct_change()
            
            win = 3
            min_bars = max(2, int(win * 0.6))  # PATCH: minimum 2 barres
            
            es_tail = es_ret.tail(win).dropna()
            nq_tail = nq_ret.tail(win).dropna()
            
            if len(es_tail) < min_bars or len(nq_tail) < min_bars:
                logger.debug(f"Corr 1m: échantillon insuffisant (ES:{len(es_tail)}, NQ:{len(nq_tail)}, min:{min_bars})")
                return 0.0
            
            # PATCH: Vérification supplémentaire pour éviter warnings NumPy
            if len(es_tail) <= 1 or len(nq_tail) <= 1:
                return 0.0
            
            with np.errstate(all='ignore'):
                corr = float(np.corrcoef(es_tail, nq_tail)[0,1])
            
            if not np.isfinite(corr):
                corr = 0.0
                
            return max(min(corr, 1.0), -1.0)
            
        except Exception as e:
            logger.debug(f"Erreur corr 1m: {e}")
            return 0.0
    
    def _calculate_weighted_correlation(self, corr_15m: float, corr_5m: float, corr_1m: float) -> float:
        """Calcule la corrélation pondérée (15m:60%, 5m:30%, 1m:10%)"""
        try:
            # Pondération des corrélations valides
            weights = []
            values = []
            
            if np.isfinite(corr_15m):
                weights.append(0.6)
                values.append(corr_15m)
            
            if np.isfinite(corr_5m):
                weights.append(0.3)
                values.append(corr_5m)
                
            if np.isfinite(corr_1m):
                weights.append(0.1)
                values.append(corr_1m)
            
            if not weights:
                return 0.0
                
            # Normaliser les poids
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            
            # Calculer la moyenne pondérée
            corr_effective = sum(w * v for w, v in zip(normalized_weights, values))
            
            return float(corr_effective)
            
        except Exception as e:
            logger.debug(f"❌ Erreur corrélation pondérée: {e}")
            return 0.0
    
    def _classify_correlation_regime(self, corr_15m: float) -> str:
        """Classifie le régime de corrélation"""
        # Seuils configurables ou par défaut
        weak = getattr(self.cal, "corr_weak_threshold", 0.70) if self.cal else 0.70
        tight = getattr(self.cal, "corr_tight_threshold", 0.90) if self.cal else 0.90
        
        if abs(corr_15m) < weak:
            return 'weak'
        elif abs(corr_15m) > tight:
            return 'tight'
        else:
            return 'normal'
    
    def _compute_volume_zscore(self, df: pd.DataFrame) -> float:
        """Calcule le Z-score du volume (PATCH: sans NaN, EWM fallback)"""
        try:
            if len(df) < 10 or 'volume' not in df.columns:
                return 0.0
            
            vol5 = df['volume'].rolling(5, min_periods=5).sum()
            current = float(vol5.iloc[-1])
            
            if len(vol5) >= 390*20:
                base = vol5.rolling(390*20, min_periods=50)
                mu = float(base.mean().iloc[-1])
                sigma = float(base.std().iloc[-1])
            else:
                # PATCH: EWM fallback pour lisser
                mu = float(vol5.ewm(span=150, adjust=False).mean().iloc[-1])
                sigma = float(vol5.ewm(span=150, adjust=False).std().iloc[-1])
            
            if not np.isfinite(mu) or not np.isfinite(sigma) or sigma == 0:
                return 0.0
            
            return float((current - mu) / sigma)
            
        except Exception as e:
            logger.error(f"❌ Erreur Z-score volume: {e}")
            return 0.0
    
    def _classify_liquidity_regime(self, volume_zscore: float) -> str:
        """Classifie le régime de liquidité"""
        if volume_zscore < -0.5:
            return 'thin'
        elif volume_zscore > 0.5:
            return 'thick'
        else:
            return 'normal'
    
    def _compute_gamma_distance(self, df: pd.DataFrame, gamma_levels: Optional[List[float]]) -> float:
        """Calcule la distance au mur gamma le plus proche (PATCH: robuste dtype)"""
        try:
            if gamma_levels is None or not gamma_levels:
                return 1.0  # Pas de mur gamma
            
            current_price = float(df['close'].iloc[-1])
            
            # PATCH: Conversion robuste des gamma_levels en float
            try:
                levels = np.asarray(gamma_levels, dtype=float)
                price = float(current_price)
                distances = np.abs(levels - price)
                min_distance = float(np.min(distances))
            except (ValueError, TypeError, AttributeError):
                # Fallback si conversion échoue
                logger.debug(f"Fallback gamma distance: levels={gamma_levels}, price={current_price}")
                return 1.0
            
            # Distance normalisée par le prix
            normalized_distance = min_distance / current_price
            
            return float(normalized_distance)
            
        except Exception as e:
            logger.error(f"❌ Erreur distance gamma: {e}")
            return 1.0
    
    def _classify_gamma_regime(self, gamma_distance: float) -> str:
        """Classifie le régime gamma (PATCH: avec hystérésis)"""
        # PATCH: Utiliser les seuils de calibration si disponibles
        near_in = getattr(self.cal, "gamma_near_wall_threshold", _GAMMA_NEAR_IN) if self.cal else _GAMMA_NEAR_IN
        near_out = getattr(self.cal, "gamma_near_wall_threshold", _GAMMA_NEAR_OUT) if self.cal else _GAMMA_NEAR_OUT
        exp_in = getattr(self.cal, "gamma_expansion_threshold", _GAMMA_EXP_IN) if self.cal else _GAMMA_EXP_IN
        exp_out = getattr(self.cal, "gamma_expansion_threshold", _GAMMA_EXP_OUT) if self.cal else _GAMMA_EXP_OUT
        
        prev = self.regime_history[-1]['gamma_regime'] if self.regime_history else None
        
        # Hystérésis: sortie
        if prev == 'near_wall':
            if gamma_distance <= near_out:
                return 'near_wall'
        if prev == 'expansion':
            if gamma_distance >= exp_out:
                return 'expansion'
        
        # Entrées
        if gamma_distance < near_in:
            return 'near_wall'
        if gamma_distance > exp_in:
            return 'expansion'
        
        return 'neutral'
    
    def _classify_session(self, clock: datetime) -> str:
        """Classifie la session de trading (PATCH: timezone-safe)"""
        # PATCH: Force Europe/Paris
        if clock.tzinfo is None:
            clock = clock.replace(tzinfo=ZoneInfo("Europe/Paris"))
        else:
            clock = clock.astimezone(ZoneInfo("Europe/Paris"))
        
        hour = clock.hour + clock.minute / 60.0
        
        if 15.5 <= hour <= 17.0:  # 15:30 - 17:00
            return 'open'
        elif 20.0 <= hour <= 22.0:  # 20:00 - 22:00
            return 'power'
        elif 17.0 < hour < 20.0:  # 17:00 - 20:00
            return 'mid'
        else:
            return 'after'
    
    def adapt_thresholds(self, base_config: LeadershipConfig, market_state: MarketState) -> LeadershipConfig:
        """
        Adapte dynamiquement les seuils selon l'état du marché
        """
        cfg = deepcopy(base_config)
        # --- Risk corr continu (0..1) en fonction de |corr| ---
        # Entre seuil "weak" et "tight", on interpole linéairement
        weak = getattr(cfg, "corr_weak_threshold", 0.70)
        tight = getattr(cfg, "corr_tight_threshold", 0.90)
        c = float(max(-1.0, min(1.0, market_state.corr_15m)))
        ac = abs(c)
        if ac <= weak:
            risk_corr = getattr(cfg, "risk_multiplier_weak_corr", 0.7)
        elif ac >= tight:
            risk_corr = 1.0
        else:
            span = (tight - weak) or 1e-6
            t = (ac - weak) / span
            lo = getattr(cfg, "risk_multiplier_weak_corr", 0.7)
            hi = 1.0
            risk_corr = lo + t * (hi - lo)
        # expose pour l'intégrateur
        cfg.risk_corr = float(max(0.0, min(1.0, risk_corr)))

        # --- exemples existants d'adaptation (vol, gamma…) ---
        if market_state.vol_regime == 'high':
            cfg.leader_strength_min = max(0.0, min(1.0, cfg.leader_strength_min + 0.05))
            cfg.persistence_bars = max(1, cfg.persistence_bars + 1)

        # Configuration standard (sans mode démo)
        cfg.corr_min_effective = cfg.corr_min

        return cfg
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'analyseur"""
        return {
            'analysis_count': self.analysis_count,
            'last_analysis': self.last_analysis.isoformat() if self.last_analysis else None,
            'regime_history_count': len(self.regime_history)
        }
    
    def get_risk_context(self, market_state: Optional[MarketState] = None) -> Dict[str, Any]:
        """🎯 Retourne le contexte de risque basé sur l'état du marché"""
        try:
            # Si pas d'état fourni, utiliser le dernier analysé
            if market_state is None:
                if self.last_analysis is None:
                    return self._get_default_risk_context()
                market_state = self.last_analysis
            
            # Calcul du niveau de risque global
            risk_level = self._calculate_risk_level(market_state)
            
            # Facteurs de risque individuels
            risk_factors = {
                'volatility_risk': self._assess_volatility_risk(market_state),
                'correlation_risk': self._assess_correlation_risk(market_state),
                'liquidity_risk': self._assess_liquidity_risk(market_state),
                'gamma_risk': self._assess_gamma_risk(market_state),
                'session_risk': self._assess_session_risk(market_state)
            }
            
            # Recommandations de trading
            trading_recommendations = self._generate_trading_recommendations(market_state, risk_level)
            
            return {
                'risk_level': risk_level,
                'risk_score': self._calculate_risk_score(risk_factors),
                'risk_factors': risk_factors,
                'trading_recommendations': trading_recommendations,
                'market_state': {
                    'vol_regime': market_state.vol_regime,
                    'corr_regime': market_state.corr_regime,
                    'liq_regime': market_state.liq_regime,
                    'gamma_regime': market_state.gamma_regime,
                    'session': market_state.session
                },
                'timestamp': datetime.now().isoformat(),
                'analysis_quality': 'real' if market_state else 'fallback'
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul contexte risque: {e}")
            return self._get_default_risk_context()
    
    def _calculate_risk_level(self, market_state: MarketState) -> str:
        """Calcule le niveau de risque global"""
        risk_score = 0
        
        # Volatilité
        if market_state.vol_regime == 'high':
            risk_score += 3
        elif market_state.vol_regime == 'normal':
            risk_score += 1
        
        # Corrélation
        if market_state.corr_regime == 'weak':
            risk_score += 2
        elif market_state.corr_regime == 'tight':
            risk_score += 1
        
        # Liquidité
        if market_state.liq_regime == 'thin':
            risk_score += 2
        
        # Gamma
        if market_state.gamma_regime == 'near_wall':
            risk_score += 3
        elif market_state.gamma_regime == 'expansion':
            risk_score += 1
        
        # Session
        if market_state.session in ['power', 'after']:
            risk_score += 1
        
        # Classification
        if risk_score >= 7:
            return 'very_high'
        elif risk_score >= 5:
            return 'high'
        elif risk_score >= 3:
            return 'moderate'
        elif risk_score >= 1:
            return 'low'
        else:
            return 'very_low'
    
    def _assess_volatility_risk(self, market_state: MarketState) -> Dict[str, Any]:
        """Évalue le risque de volatilité"""
        risk_level = 'low'
        if market_state.vol_regime == 'high':
            risk_level = 'high'
        elif market_state.vol_regime == 'normal':
            risk_level = 'moderate'
        
        return {
            'level': risk_level,
            'realized_vol': market_state.realized_vol,
            'regime': market_state.vol_regime,
            'recommendation': 'Réduire la taille des positions' if risk_level == 'high' else 'Taille normale'
        }
    
    def _assess_correlation_risk(self, market_state: MarketState) -> Dict[str, Any]:
        """Évalue le risque de corrélation"""
        risk_level = 'low'
        if market_state.corr_regime == 'weak':
            risk_level = 'high'
        elif market_state.corr_regime == 'tight':
            risk_level = 'moderate'
        
        return {
            'level': risk_level,
            'correlation_15m': market_state.corr_15m,
            'regime': market_state.corr_regime,
            'recommendation': 'Vérifier la cohérence ES/NQ' if risk_level == 'high' else 'Corrélation stable'
        }
    
    def _assess_liquidity_risk(self, market_state: MarketState) -> Dict[str, Any]:
        """Évalue le risque de liquidité"""
        risk_level = 'low'
        if market_state.liq_regime == 'thin':
            risk_level = 'high'
        elif market_state.liq_regime == 'normal':
            risk_level = 'moderate'
        
        return {
            'level': risk_level,
            'volume_zscore': market_state.volume_zscore,
            'regime': market_state.liq_regime,
            'recommendation': 'Éviter les gros ordres' if risk_level == 'high' else 'Liquidité normale'
        }
    
    def _assess_gamma_risk(self, market_state: MarketState) -> Dict[str, Any]:
        """Évalue le risque gamma"""
        risk_level = 'low'
        if market_state.gamma_regime == 'near_wall':
            risk_level = 'high'
        elif market_state.gamma_regime == 'expansion':
            risk_level = 'moderate'
        
        return {
            'level': risk_level,
            'gamma_distance': market_state.gamma_distance,
            'regime': market_state.gamma_regime,
            'recommendation': 'Attention aux murs gamma' if risk_level == 'high' else 'Gamma neutre'
        }
    
    def _assess_session_risk(self, market_state: MarketState) -> Dict[str, Any]:
        """Évalue le risque de session"""
        risk_level = 'low'
        if market_state.session in ['power', 'after']:
            risk_level = 'moderate'
        
        return {
            'level': risk_level,
            'session': market_state.session,
            'recommendation': 'Session volatile' if risk_level == 'moderate' else 'Session stable'
        }
    
    def _calculate_risk_score(self, risk_factors: Dict[str, Dict[str, Any]]) -> float:
        """Calcule un score de risque global (0-1)"""
        risk_weights = {
            'volatility_risk': 0.3,
            'correlation_risk': 0.25,
            'liquidity_risk': 0.2,
            'gamma_risk': 0.15,
            'session_risk': 0.1
        }
        
        risk_levels = {'low': 0.2, 'moderate': 0.5, 'high': 0.8, 'very_high': 1.0}
        
        total_score = 0
        for factor, weight in risk_weights.items():
            if factor in risk_factors:
                level = risk_factors[factor]['level']
                total_score += risk_levels.get(level, 0.5) * weight
        
        return min(1.0, total_score)
    
    def _generate_trading_recommendations(self, market_state: MarketState, risk_level: str) -> Dict[str, Any]:
        """Génère des recommandations de trading basées sur le risque"""
        recommendations = {
            'position_sizing': 'normal',
            'stop_loss_tightness': 'normal',
            'take_profit_aggressiveness': 'normal',
            'entry_timing': 'normal',
            'overall_advice': 'Trading normal'
        }
        
        if risk_level in ['high', 'very_high']:
            recommendations.update({
                'position_sizing': 'reduce',
                'stop_loss_tightness': 'tight',
                'take_profit_aggressiveness': 'conservative',
                'entry_timing': 'wait',
                'overall_advice': 'Conditions risquées - Réduire l\'exposition'
            })
        elif risk_level == 'moderate':
            recommendations.update({
                'position_sizing': 'slightly_reduce',
                'stop_loss_tightness': 'slightly_tight',
                'overall_advice': 'Conditions modérées - Prudence recommandée'
            })
        elif risk_level == 'very_low':
            recommendations.update({
                'position_sizing': 'slightly_increase',
                'take_profit_aggressiveness': 'slightly_aggressive',
                'overall_advice': 'Conditions favorables - Opportunités possibles'
            })
        
        return recommendations
    
    def _get_default_risk_context(self) -> Dict[str, Any]:
        """Retourne un contexte de risque par défaut en cas d'erreur"""
        return {
            'risk_level': 'moderate',
            'risk_score': 0.5,
            'risk_factors': {
                'volatility_risk': {'level': 'moderate', 'recommendation': 'Données indisponibles'},
                'correlation_risk': {'level': 'moderate', 'recommendation': 'Données indisponibles'},
                'liquidity_risk': {'level': 'moderate', 'recommendation': 'Données indisponibles'},
                'gamma_risk': {'level': 'moderate', 'recommendation': 'Données indisponibles'},
                'session_risk': {'level': 'moderate', 'recommendation': 'Données indisponibles'}
            },
            'trading_recommendations': {
                'position_sizing': 'normal',
                'stop_loss_tightness': 'normal',
                'take_profit_aggressiveness': 'normal',
                'entry_timing': 'normal',
                'overall_advice': 'Données de marché indisponibles - Prudence recommandée'
            },
            'market_state': {
                'vol_regime': 'unknown',
                'corr_regime': 'unknown',
                'liq_regime': 'unknown',
                'gamma_regime': 'unknown',
                'session': 'unknown'
            },
            'timestamp': datetime.now().isoformat(),
            'analysis_quality': 'fallback'
        }
    
    def get_recent_regimes(self, count: int = 10) -> List[Dict]:
        """Retourne les régimes récents"""
        return self.regime_history[-count:]

def test_market_state_analyzer():
    """Test de l'analyseur d'état de marché"""
    logger.info("🧮 TEST MARKET STATE ANALYZER (patched)")
    logger.info("=" * 50)
    
    # Créer des données de test
    dates = pd.date_range('2025-08-22 15:00:00', periods=100, freq='1min')
    
    # ES: données avec volatilité normale
    es_data = pd.DataFrame({
        'close': [6397 + i*0.5 + np.random.normal(0, 0.1) for i in range(100)],
        'volume': [1000 + np.random.normal(0, 100) for _ in range(100)]
    }, index=dates)
    
    # NQ: données corrélées
    nq_data = pd.DataFrame({
        'close': [23246 + i*0.2 + np.random.normal(0, 0.2) for i in range(100)],
        'volume': [800 + np.random.normal(0, 80) for _ in range(100)]
    }, index=dates)
    
    # Initialiser l'analyseur
    analyzer = MarketStateAnalyzer()
    
    # Test d'analyse d'état
    market_state = analyzer.compute_market_state(
        es_data, nq_data,
        gamma_levels=[6400, 6450, 6500],
        clock=datetime.now()
    )
    
    logger.info("📊 ÉTAT DU MARCHÉ:")
    logger.info(f"  📈 Volatilité: {market_state.realized_vol:.4f} ({market_state.vol_regime})")
    logger.info(f"  🔗 Corrélation: {market_state.corr_15m:.3f} ({market_state.corr_regime})")
    logger.info(f"  💰 Liquidité: Z-score {market_state.volume_zscore:.2f} ({market_state.liq_regime})")
    logger.info(f"  🎯 Gamma: Distance {market_state.gamma_distance:.4f} ({market_state.gamma_regime})")
    logger.info(f"  🕐 Session: {market_state.session}")
    
    # Test d'adaptation des seuils
    base_config = LeadershipConfig()
    adapted_config = analyzer.adapt_thresholds(base_config, market_state)
    
    logger.info("\n🔧 CONFIGURATION ADAPTÉE:")
    logger.info(f"  📊 Corr min: {adapted_config.corr_min:.2f}")
    logger.info(f"  💪 Leader strength min: {adapted_config.leader_strength_min:.2f}")
    logger.info(f"  ⏱️ Persistence bars: {adapted_config.persistence_bars}")
    logger.info(f"  🎯 Risk multiplier tight corr: {adapted_config.risk_multiplier_tight_corr:.1f}")
    
    # Statut
    status = analyzer.get_status()
    logger.info(f"\n📋 Statut: {status['analysis_count']} analyses effectuées")

if __name__ == "__main__":
    test_market_state_analyzer()
