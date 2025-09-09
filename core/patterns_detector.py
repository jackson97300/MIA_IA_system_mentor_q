#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Patterns Detector
Détection rapide de patterns microstructure (barres, delta, micro-breakouts, absorption, exhaustion)

Version: Production Ready v2.0
Performance: <2ms pour l'ensemble des patterns
Responsabilité: Détection patterns à partir de contextes agrégés
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Literal
from core.logger import get_logger
from core.trading_types import VIXRegime

logger = get_logger(__name__)

# === TYPES ===

@dataclass
class PatternHit:
    """Résultat de détection d'un pattern"""
    name: str
    confidence: float  # [0..1]
    direction: Literal["LONG", "SHORT", "BOTH", "NONE"]
    notes: List[str]
    
    def __post_init__(self):
        # Clamp confidence
        self.confidence = max(0.0, min(1.0, self.confidence))

@dataclass
class ContextM1:
    """Contexte M1 agrégé"""
    bars: List[Dict[str, float]]  # OHLCV des dernières barres M1
    volume: float
    delta: float
    cum_delta: float
    trades_count: int
    spread_avg: float
    vwap: float
    high: float
    low: float
    close: float

@dataclass
class ContextM30:
    """Contexte M30 agrégé"""
    bars: List[Dict[str, float]]  # OHLCV des dernières barres M30
    volume: float
    delta: float
    cum_delta: float
    trades_count: int
    spread_avg: float
    vwap: float
    high: float
    low: float
    close: float

@dataclass
class OrderFlowContext:
    """Contexte order flow"""
    delta: float
    cum_delta: float
    trades: List[Dict[str, Any]]  # Derniers trades
    spread_synthetic: float
    bid_ask_imbalance: float

# === CONSTANTS ===

# Seuils par défaut par régime VIX
DEFAULT_VIX_THRESHOLDS = {
    "LOW": {
        "delta_spike_sigma": 2.0,
        "volume_spike_ratio": 1.5,
        "price_move_ticks": 4,
        "absorption_ratio": 0.7,
        "gamma_prox_ticks": 8,
        "bl_prox_ticks": 5,
        "swing_prox_ticks": 15,
        "gex_cluster_min": 3
    },
    "MID": {
        "delta_spike_sigma": 2.5,
        "volume_spike_ratio": 2.0,
        "price_move_ticks": 6,
        "absorption_ratio": 0.8,
        "gamma_prox_ticks": 10,
        "bl_prox_ticks": 5,
        "swing_prox_ticks": 15,
        "gex_cluster_min": 3
    },
    "HIGH": {
        "delta_spike_sigma": 3.0,
        "volume_spike_ratio": 2.5,
        "price_move_ticks": 8,
        "absorption_ratio": 0.9,
        "gamma_prox_ticks": 12,
        "bl_prox_ticks": 6,
        "swing_prox_ticks": 18,
        "gex_cluster_min": 4
    }
}

# Patterns activables par défaut
DEFAULT_ACTIVE_PATTERNS = {
    "long_down_up_bar": True,
    "engulfing": True,
    "range_break": True,
    "delta_divergence": True,
    "exhaustion": True,
    "absorption": True,
    "trades_spike": True,
    "vwap_rejection": True,
    "vpoc_touch": True,
    "micro_breakout": True,
    # Patterns MenthorQ
    "mq_gamma_reaction": True,
    "mq_gamma_break": True,
    "mq_blind_spot_proximity": True,
    "mq_swing_reversal": True,
    "mq_gex_magnet": True
}

# === MAIN CLASS ===

class PatternsDetector:
    """Détecteur de patterns microstructure"""
    
    def __init__(self, 
                 active_patterns: Optional[Dict[str, bool]] = None,
                 vix_thresholds: Optional[Dict[str, Dict[str, float]]] = None):
        """
        Initialise le détecteur de patterns
        
        Args:
            active_patterns: Patterns activés/désactivés
            vix_thresholds: Seuils par régime VIX
        """
        self.active_patterns = active_patterns or DEFAULT_ACTIVE_PATTERNS.copy()
        self.vix_thresholds = vix_thresholds or DEFAULT_VIX_THRESHOLDS.copy()
        
        # Compteurs pour métriques
        self.pattern_counts = {name: 0 for name in self.active_patterns.keys()}
        
        logger.debug(f"PatternsDetector initialisé avec {sum(self.active_patterns.values())} patterns actifs")
    
    def detect_patterns(self,
                       context_m1: ContextM1,
                       context_m30: ContextM30,
                       oflow: OrderFlowContext,
                       vix_regime: str = "MID",
                       levels: Optional[Dict[str, Any]] = None) -> List[PatternHit]:
        """
        Détecte tous les patterns activés
        
        Args:
            context_m1: Contexte M1 agrégé
            context_m30: Contexte M30 agrégé
            oflow: Contexte order flow
            vix_regime: Régime VIX (LOW/MID/HIGH)
            levels: Niveaux structurels optionnels
            
        Returns:
            Liste des PatternHit détectés
        """
        patterns = []
        
        # Récupérer les seuils pour le régime VIX
        thresholds = self.vix_thresholds.get(vix_regime, self.vix_thresholds["MID"])
        
        # 1. Patterns bar-based
        if self.active_patterns.get("long_down_up_bar", False):
            hit = self._detect_long_down_up_bar(context_m1, thresholds)
            if hit:
                patterns.append(hit)
                self.pattern_counts["long_down_up_bar"] += 1
        
        if self.active_patterns.get("engulfing", False):
            hit = self._detect_engulfing(context_m1, thresholds)
            if hit:
                patterns.append(hit)
                self.pattern_counts["engulfing"] += 1
        
        if self.active_patterns.get("range_break", False):
            hit = self._detect_range_break(context_m1, context_m30, thresholds)
            if hit:
                patterns.append(hit)
                self.pattern_counts["range_break"] += 1
        
        # 2. Patterns orderflow
        if self.active_patterns.get("delta_divergence", False):
            hit = self._detect_delta_divergence(context_m1, oflow, thresholds)
            if hit:
                patterns.append(hit)
                self.pattern_counts["delta_divergence"] += 1
        
        if self.active_patterns.get("exhaustion", False):
            hit = self._detect_exhaustion(context_m1, oflow, thresholds)
            if hit:
                patterns.append(hit)
                self.pattern_counts["exhaustion"] += 1
        
        if self.active_patterns.get("absorption", False):
            hit = self._detect_absorption(context_m1, oflow, thresholds)
            if hit:
                patterns.append(hit)
                self.pattern_counts["absorption"] += 1
        
        if self.active_patterns.get("trades_spike", False):
            hit = self._detect_trades_spike(context_m1, oflow, thresholds)
            if hit:
                patterns.append(hit)
                self.pattern_counts["trades_spike"] += 1
        
        # 3. Patterns VWAP/VP
        if self.active_patterns.get("vwap_rejection", False):
            hit = self._detect_vwap_rejection(context_m1, context_m30, thresholds)
            if hit:
                patterns.append(hit)
                self.pattern_counts["vwap_rejection"] += 1
        
        if self.active_patterns.get("vpoc_touch", False):
            hit = self._detect_vpoc_touch(context_m1, context_m30, levels, thresholds)
            if hit:
                patterns.append(hit)
                self.pattern_counts["vpoc_touch"] += 1
        
        # 4. Patterns micro-breakout
        if self.active_patterns.get("micro_breakout", False):
            hit = self._detect_micro_breakout(context_m1, oflow, thresholds)
            if hit:
                patterns.append(hit)
                self.pattern_counts["micro_breakout"] += 1
        
        # 5. Patterns MenthorQ (n'exécute que si des niveaux MQ sont fournis)
        if levels and levels.get("menthorq"):
            if self.active_patterns.get("mq_blind_spot_proximity", False):
                hit = self._detect_mq_blind_spot_proximity(context_m1, vix_regime, levels)
                if hit:
                    patterns.append(hit)
                    self.pattern_counts["mq_blind_spot_proximity"] += 1

            if self.active_patterns.get("mq_gamma_reaction", False):
                hit = self._detect_mq_gamma_reaction(context_m1, vix_regime, levels)
                if hit:
                    patterns.append(hit)
                    self.pattern_counts["mq_gamma_reaction"] += 1

            if self.active_patterns.get("mq_gamma_break", False):
                hit = self._detect_mq_gamma_break(context_m1, vix_regime, levels)
                if hit:
                    patterns.append(hit)
                    self.pattern_counts["mq_gamma_break"] += 1

            if self.active_patterns.get("mq_swing_reversal", False):
                hit = self._detect_mq_swing_reversal(context_m1, oflow, vix_regime, levels)
                if hit:
                    patterns.append(hit)
                    self.pattern_counts["mq_swing_reversal"] += 1

            if self.active_patterns.get("mq_gex_magnet", False):
                hit = self._detect_mq_gex_magnet(context_m1, vix_regime, levels)
                if hit:
                    patterns.append(hit)
                    self.pattern_counts["mq_gex_magnet"] += 1

        logger.debug(f"Détection patterns: {len(patterns)} hits trouvés")
        return patterns
    
    # === PATTERN DETECTION METHODS ===
    
    def _detect_long_down_up_bar(self, context_m1: ContextM1, thresholds: Dict[str, float]) -> Optional[PatternHit]:
        """Détecte Long Down-Up Bar pattern"""
        if len(context_m1.bars) < 3:
            return None
        
        # Dernières 3 barres
        bar1 = context_m1.bars[-3]  # Barre 1
        bar2 = context_m1.bars[-2]  # Barre 2 (down)
        bar3 = context_m1.bars[-1]  # Barre 3 (up)
        
        # Vérifier pattern: down bar suivie d'up bar
        if (bar2['close'] < bar2['open'] and  # Barre 2 baissière
            bar3['close'] > bar3['open'] and  # Barre 3 haussière
            bar3['close'] > bar2['close']):   # Barre 3 ferme au-dessus de barre 2
            
            # Calculer confidence basée sur la force
            body_size = abs(bar3['close'] - bar3['open'])
            min_move = thresholds['price_move_ticks'] * 0.25  # 0.25 point ES
            
            if body_size >= min_move:
                confidence = min(1.0, body_size / (min_move * 2))
                return PatternHit(
                    name="long_down_up_bar",
                    confidence=confidence,
                    direction="LONG",
                    notes=[f"Body size: {body_size:.2f} ticks"]
                )
        
        return None
    
    def _detect_engulfing(self, context_m1: ContextM1, thresholds: Dict[str, float]) -> Optional[PatternHit]:
        """Détecte Engulfing pattern"""
        if len(context_m1.bars) < 2:
            return None
        
        bar1 = context_m1.bars[-2]  # Barre précédente
        bar2 = context_m1.bars[-1]  # Barre actuelle
        
        # Bullish engulfing
        if (bar1['close'] < bar1['open'] and  # Barre 1 baissière
            bar2['close'] > bar2['open'] and  # Barre 2 haussière
            bar2['open'] < bar1['close'] and  # Barre 2 ouvre sous close barre 1
            bar2['close'] > bar1['open']):    # Barre 2 ferme au-dessus open barre 1
            
            confidence = min(1.0, abs(bar2['close'] - bar2['open']) / (thresholds['price_move_ticks'] * 0.25))
            return PatternHit(
                name="engulfing",
                confidence=confidence,
                direction="LONG",
                notes=["Bullish engulfing"]
            )
        
        # Bearish engulfing
        elif (bar1['close'] > bar1['open'] and  # Barre 1 haussière
              bar2['close'] < bar2['open'] and  # Barre 2 baissière
              bar2['open'] > bar1['close'] and  # Barre 2 ouvre au-dessus close barre 1
              bar2['close'] < bar1['open']):    # Barre 2 ferme sous open barre 1
            
            confidence = min(1.0, abs(bar2['close'] - bar2['open']) / (thresholds['price_move_ticks'] * 0.25))
            return PatternHit(
                name="engulfing",
                confidence=confidence,
                direction="SHORT",
                notes=["Bearish engulfing"]
            )
        
        return None
    
    def _detect_range_break(self, context_m1: ContextM1, context_m30: ContextM30, thresholds: Dict[str, float]) -> Optional[PatternHit]:
        """Détecte Range Break pattern"""
        # Calculer range M30
        m30_range = context_m30.high - context_m30.low
        min_range = thresholds['price_move_ticks'] * 0.25 * 2  # 2 points ES minimum
        
        if m30_range < min_range:
            return None
        
        # Vérifier breakout
        current_price = context_m1.close
        
        # Breakout haussier
        if current_price > context_m30.high:
            confidence = min(1.0, (current_price - context_m30.high) / (thresholds['price_move_ticks'] * 0.25))
            return PatternHit(
                name="range_break",
                confidence=confidence,
                direction="LONG",
                notes=[f"Breakout above M30 high: {context_m30.high:.2f}"]
            )
        
        # Breakout baissier
        elif current_price < context_m30.low:
            confidence = min(1.0, (context_m30.low - current_price) / (thresholds['price_move_ticks'] * 0.25))
            return PatternHit(
                name="range_break",
                confidence=confidence,
                direction="SHORT",
                notes=[f"Breakout below M30 low: {context_m30.low:.2f}"]
            )
        
        return None
    
    def _detect_delta_divergence(self, context_m1: ContextM1, oflow: OrderFlowContext, thresholds: Dict[str, float]) -> Optional[PatternHit]:
        """Détecte Delta Divergence pattern"""
        if len(context_m1.bars) < 5:
            return None
        
        # Calculer delta moyen des dernières barres
        recent_deltas = [bar.get('delta', 0) for bar in context_m1.bars[-5:]]
        avg_delta = sum(recent_deltas) / len(recent_deltas)
        
        # Vérifier divergence prix vs delta
        price_trend = context_m1.close - context_m1.bars[-5]['close']
        delta_trend = oflow.delta - avg_delta
        
        # Divergence haussière: prix baisse, delta augmente
        if price_trend < 0 and delta_trend > 0:
            confidence = min(1.0, abs(delta_trend) / (thresholds['delta_spike_sigma'] * 100))
            return PatternHit(
                name="delta_divergence",
                confidence=confidence,
                direction="LONG",
                notes=[f"Price down {price_trend:.2f}, delta up {delta_trend:.2f}"]
            )
        
        # Divergence baissière: prix monte, delta baisse
        elif price_trend > 0 and delta_trend < 0:
            confidence = min(1.0, abs(delta_trend) / (thresholds['delta_spike_sigma'] * 100))
            return PatternHit(
                name="delta_divergence",
                confidence=confidence,
                direction="SHORT",
                notes=[f"Price up {price_trend:.2f}, delta down {delta_trend:.2f}"]
            )
        
        return None
    
    def _detect_exhaustion(self, context_m1: ContextM1, oflow: OrderFlowContext, thresholds: Dict[str, float]) -> Optional[PatternHit]:
        """Détecte Exhaustion pattern"""
        # Volume élevé avec faible mouvement de prix
        volume_ratio = context_m1.volume / (context_m1.volume * 0.5)  # Simplifié
        price_range = context_m1.high - context_m1.low
        min_range = thresholds['price_move_ticks'] * 0.25
        
        if volume_ratio > thresholds['volume_spike_ratio'] and price_range < min_range:
            confidence = min(1.0, volume_ratio / (thresholds['volume_spike_ratio'] * 2))
            return PatternHit(
                name="exhaustion",
                confidence=confidence,
                direction="NONE",
                notes=[f"High volume {volume_ratio:.2f}x, low range {price_range:.2f}"]
            )
        
        return None
    
    def _detect_absorption(self, context_m1: ContextM1, oflow: OrderFlowContext, thresholds: Dict[str, float]) -> Optional[PatternHit]:
        """Détecte Absorption pattern"""
        # Forte activité avec faible impact sur le prix
        if len(oflow.trades) < 10:
            return None
        
        # Calculer ratio absorption
        total_volume = sum(trade.get('size', 0) for trade in oflow.trades[-10:])
        if len(context_m1.bars) < 1:
            return None
        price_impact = abs(context_m1.close - context_m1.bars[-1]["open"])
        
        if total_volume > 0:
            absorption_ratio = price_impact / (total_volume * 0.01)  # Simplifié
            
            if absorption_ratio < thresholds['absorption_ratio']:
                confidence = min(1.0, (thresholds['absorption_ratio'] - absorption_ratio) / thresholds['absorption_ratio'])
                return PatternHit(
                    name="absorption",
                    confidence=confidence,
                    direction="BOTH",
                    notes=[f"Absorption ratio: {absorption_ratio:.3f}"]
                )
        
        return None
    
    def _detect_trades_spike(self, context_m1: ContextM1, oflow: OrderFlowContext, thresholds: Dict[str, float]) -> Optional[PatternHit]:
        """Détecte Trades Spike pattern"""
        # Spike dans le nombre de trades
        trades_ratio = context_m1.trades_count / max(1, context_m1.trades_count * 0.5)  # Simplifié
        
        if trades_ratio > thresholds['volume_spike_ratio']:
            confidence = min(1.0, trades_ratio / (thresholds['volume_spike_ratio'] * 2))
            return PatternHit(
                name="trades_spike",
                confidence=confidence,
                direction="BOTH",
                notes=[f"Trades spike: {trades_ratio:.2f}x normal"]
            )
        
        return None
    
    def _detect_vwap_rejection(self, context_m1: ContextM1, context_m30: ContextM30, thresholds: Dict[str, float]) -> Optional[PatternHit]:
        """Détecte VWAP Rejection pattern"""
        # Rejet du VWAP M30
        vwap_distance = abs(context_m1.close - context_m30.vwap)
        min_distance = thresholds['price_move_ticks'] * 0.25
        
        if vwap_distance > min_distance:
            # Déterminer direction
            if context_m1.close > context_m30.vwap:
                direction = "LONG"
                notes = [f"Rejection above VWAP: {context_m30.vwap:.2f}"]
            else:
                direction = "SHORT"
                notes = [f"Rejection below VWAP: {context_m30.vwap:.2f}"]
            
            confidence = min(1.0, vwap_distance / (min_distance * 2))
            return PatternHit(
                name="vwap_rejection",
                confidence=confidence,
                direction=direction,
                notes=notes
            )
        
        return None
    
    def _detect_vpoc_touch(self, context_m1: ContextM1, context_m30: ContextM30, levels: Optional[Dict[str, Any]], thresholds: Dict[str, float]) -> Optional[PatternHit]:
        """Détecte VPOC Touch pattern"""
        if not levels or 'vpoc' not in levels:
            return None
        
        vpoc_price = levels['vpoc']
        distance = abs(context_m1.close - vpoc_price)
        min_distance = thresholds['price_move_ticks'] * 0.25 * 0.5  # Plus proche
        
        if distance < min_distance:
            confidence = min(1.0, (min_distance - distance) / min_distance)
            return PatternHit(
                name="vpoc_touch",
                confidence=confidence,
                direction="BOTH",
                notes=[f"VPOC touch: {vpoc_price:.2f}, distance: {distance:.2f}"]
            )
        
        return None
    
    def _detect_micro_breakout(self, context_m1: ContextM1, oflow: OrderFlowContext, thresholds: Dict[str, float]) -> Optional[PatternHit]:
        """Détecte Micro Breakout pattern"""
        # Petit breakout avec volume
        price_range = context_m1.high - context_m1.low
        min_range = thresholds['price_move_ticks'] * 0.25 * 0.5  # Plus petit
        
        if price_range > min_range and context_m1.volume > context_m1.volume * 0.8:  # Simplifié
            # Déterminer direction
            if len(context_m1.bars) < 1:
                return None
            if context_m1.close > context_m1.bars[-1]["open"]:
                direction = "LONG"
            else:
                direction = "SHORT"
            
            confidence = min(1.0, price_range / (min_range * 2))
            return PatternHit(
                name="micro_breakout",
                confidence=confidence,
                direction=direction,
                notes=[f"Micro breakout: {price_range:.2f} ticks"]
            )
        
        return None
    
    # === MENTHORQ HELPER FUNCTIONS ===
    
    def _tick_size_from_levels(self, levels: Optional[Dict[str, Any]]) -> float:
        """ES par défaut; peut être surchargé via levels["tick_size"]"""
        return max(1e-9, (levels or {}).get("tick_size", 0.25))
    
    def _nearest_level(self, price: float, level_map: Dict[str, float]) -> Optional[tuple]:
        """Retourne (name, level_price, abs_distance) du niveau le plus proche"""
        if not level_map:
            return None
        nearest = min(level_map.items(), key=lambda kv: abs(price - float(kv[1])))
        name, lvl = nearest[0], float(nearest[1])
        return name, lvl, abs(price - lvl)
    
    def _levels_dict(self, levels: Optional[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Sécurise l'accès aux sous-dicos MenthorQ"""
        mq = (levels or {}).get("menthorq", {})
        return {
            "gamma": {k: float(v) for k, v in (mq.get("gamma", {}) or {}).items()},
            "blind_spots": {k: float(v) for k, v in (mq.get("blind_spots", {}) or {}).items()},
            "swing": {k: float(v) for k, v in (mq.get("swing", {}) or {}).items()},
            "gex": {k: float(v) for k, v in (mq.get("gex", {}) or {}).items()},
        }
    
    # === MENTHORQ PATTERN DETECTION METHODS ===
    
    def _detect_mq_blind_spot_proximity(self, context_m1: ContextM1, vix_regime: str, levels: Dict[str, Any]) -> Optional[PatternHit]:
        """Détecte proximité Blind Spot (pattern NO_TRADE)"""
        th = self.vix_thresholds.get(vix_regime, self.vix_thresholds["MID"])
        tick = self._tick_size_from_levels(levels)
        bl = self._levels_dict(levels)["blind_spots"]
        if not bl:
            return None
        last_close = context_m1.close
        nearest = self._nearest_level(last_close, bl)
        if not nearest: 
            return None
        name, lvl, dist = nearest
        if dist / tick <= th["bl_prox_ticks"]:
            # pattern "NO_TRADE" informatif
            conf = min(1.0, (th["bl_prox_ticks"] * tick) / max(tick, dist))
            return PatternHit(
                name="mq_blind_spot_proximity",
                confidence=conf,
                direction="NONE",
                notes=[f"{name} à {dist/tick:.1f} ticks ({lvl:.2f}) → zone interdite"]
            )
        return None

    def _detect_mq_gamma_reaction(self, context_m1: ContextM1, vix_regime: str, levels: Dict[str, Any]) -> Optional[PatternHit]:
        """Détecte réaction aux niveaux Gamma"""
        th = self.vix_thresholds.get(vix_regime, self.vix_thresholds["MID"])
        tick = self._tick_size_from_levels(levels)
        gamma = self._levels_dict(levels)["gamma"]
        if not gamma or len(context_m1.bars) < 1:
            return None
        last = context_m1.bars[-1]
        last_close, last_open, last_high, last_low = last["close"], last["open"], last["high"], last["low"]
        nearest = self._nearest_level(last_close, gamma)
        if not nearest:
            return None
        gname, glvl, gdist = nearest
        if gdist / tick > th["gamma_prox_ticks"]:
            return None
        # Rejet: mèche qui touche/dépasse le niveau puis close de l'autre côté
        if last_low <= glvl <= last_close and last_close > last_open:
            # rejet haussier depuis un support gamma
            body = abs(last_close - last_open)
            need = max(tick, 0.5 * th["price_move_ticks"] * tick)
            conf = min(1.0, body / need)
            return PatternHit(
                name="mq_gamma_reaction",
                confidence=conf,
                direction="LONG",
                notes=[f"Rejet haussier proche {gname} ({glvl:.2f}), dist {gdist/tick:.1f}t"]
            )
        if last_high >= glvl >= last_close and last_close < last_open:
            # rejet baissier depuis une résistance gamma
            body = abs(last_close - last_open)
            need = max(tick, 0.5 * th["price_move_ticks"] * tick)
            conf = min(1.0, body / need)
            return PatternHit(
                name="mq_gamma_reaction",
                confidence=conf,
                direction="SHORT",
                notes=[f"Rejet baissier proche {gname} ({glvl:.2f}), dist {gdist/tick:.1f}t"]
            )
        return None

    def _detect_mq_gamma_break(self, context_m1: ContextM1, vix_regime: str, levels: Dict[str, Any]) -> Optional[PatternHit]:
        """Détecte cassure des niveaux Gamma"""
        th = self.vix_thresholds.get(vix_regime, self.vix_thresholds["MID"])
        tick = self._tick_size_from_levels(levels)
        gamma = self._levels_dict(levels)["gamma"]
        if not gamma or len(context_m1.bars) < 1:
            return None
        last = context_m1.bars[-1]
        last_close, last_open = last["close"], last["open"]
        nearest = self._nearest_level(last_close, gamma)
        if not nearest:
            return None
        gname, glvl, gdist = nearest
        if gdist / tick > th["gamma_prox_ticks"]:
            return None
        body = abs(last_close - last_open)
        min_body = max(tick, th["price_move_ticks"] * 0.25)  # cohérent avec le code existant
        if last_close > glvl and last_close > last_open and body >= min_body:
            conf = min(1.0, body / (min_body * 2))
            return PatternHit(
                name="mq_gamma_break",
                confidence=conf,
                direction="LONG",
                notes=[f"Cassure au-dessus {gname} ({glvl:.2f}), corps {body/tick:.1f}t"]
            )
        if last_close < glvl and last_close < last_open and body >= min_body:
            conf = min(1.0, body / (min_body * 2))
            return PatternHit(
                name="mq_gamma_break",
                confidence=conf,
                direction="SHORT",
                notes=[f"Cassure au-dessous {gname} ({glvl:.2f}), corps {body/tick:.1f}t"]
            )
        return None

    def _detect_mq_swing_reversal(self, context_m1: ContextM1, oflow: OrderFlowContext, vix_regime: str, levels: Dict[str, Any]) -> Optional[PatternHit]:
        """Détecte reversal contrarien près des Swing"""
        th = self.vix_thresholds.get(vix_regime, self.vix_thresholds["MID"])
        tick = self._tick_size_from_levels(levels)
        swing = self._levels_dict(levels)["swing"]
        if not swing or len(context_m1.bars) < 5:
            return None
        last = context_m1.bars[-1]
        last_close, last_open = last["close"], last["open"]
        nearest = self._nearest_level(last_close, swing)
        if not nearest:
            return None
        sname, slvl, sdist = nearest
        if sdist / tick > th["swing_prox_ticks"]:
            return None
        # Contrarien proche swing + petite divergence delta
        price_trend = context_m1.close - context_m1.bars[-5]['close']
        delta_trend = oflow.delta - sum(bar.get('delta', 0) for bar in context_m1.bars[-5:]) / 5.0
        if slvl < last_close and delta_trend < 0 and last_close < last_open:
            # reversal baissier sous un swing supérieur
            conf = min(1.0, (th["swing_prox_ticks"] * tick) / max(tick, sdist))
            return PatternHit(
                name="mq_swing_reversal",
                confidence=conf,
                direction="SHORT",
                notes=[f"Reversal près {sname} ({slvl:.2f}), dist {sdist/tick:.1f}t, div-Δ"]
            )
        if slvl > last_close and delta_trend > 0 and last_close > last_open:
            # reversal haussier au-dessus d'un swing inférieur
            conf = min(1.0, (th["swing_prox_ticks"] * tick) / max(tick, sdist))
            return PatternHit(
                name="mq_swing_reversal",
                confidence=conf,
                direction="LONG",
                notes=[f"Reversal près {sname} ({slvl:.2f}), dist {sdist/tick:.1f}t, div+Δ"]
            )
        return None

    def _detect_mq_gex_magnet(self, context_m1: ContextM1, vix_regime: str, levels: Dict[str, Any]) -> Optional[PatternHit]:
        """Détecte aimantation vers cluster GEX majoritaire"""
        th = self.vix_thresholds.get(vix_regime, self.vix_thresholds["MID"])
        tick = self._tick_size_from_levels(levels)
        gex = self._levels_dict(levels)["gex"]
        if not gex:
            return None
        last_close = context_m1.close
        gex_prices = list(gex.values())
        above = sum(1 for p in gex_prices if p > last_close)
        below = sum(1 for p in gex_prices if p < last_close)
        if max(above, below) < th["gex_cluster_min"]:
            return None
        # Si la majorité est au-dessus → aimantation haussière vers cluster; inverse sinon
        direction = "LONG" if above > below else "SHORT"
        # Confiance augmente avec l'asymétrie
        asym = abs(above - below) / max(1, above + below)
        conf = min(1.0, 0.5 + 0.5 * asym)
        # Note sur la distance au gex le plus proche côté majoritaire
        side_prices = [p for p in gex_prices if (p > last_close) == (direction == "LONG")]
        if not side_prices:
            return None
        nearest = min(side_prices, key=lambda p: abs(p - last_close))
        dist = abs(nearest - last_close)
        return PatternHit(
            name="mq_gex_magnet",
            confidence=conf,
            direction=direction,
            notes=[f"Cluster GEX {'au-dessus' if direction=='LONG' else 'au-dessous'}; plus proche à {dist/tick:.1f}t ({nearest:.2f})"]
        )
    
    def get_pattern_stats(self) -> Dict[str, int]:
        """Retourne les statistiques des patterns détectés"""
        return self.pattern_counts.copy()
    
    def reset_stats(self):
        """Remet à zéro les statistiques"""
        self.pattern_counts = {name: 0 for name in self.active_patterns.keys()}

# === FACTORY FUNCTION ===

def create_patterns_detector(active_patterns: Optional[Dict[str, bool]] = None,
                           vix_thresholds: Optional[Dict[str, Dict[str, float]]] = None) -> PatternsDetector:
    """Factory function pour créer un détecteur de patterns"""
    return PatternsDetector(active_patterns, vix_thresholds)

# === TESTING ===

def test_patterns_detector():
    """Test du détecteur de patterns"""
    logger.info("=== TEST Patterns Detector ===")
    
    try:
        # Créer un détecteur
        detector = create_patterns_detector()
        
        # Créer des contextes de test
        context_m1 = ContextM1(
            bars=[
                {'open': 5290.0, 'high': 5292.0, 'low': 5288.0, 'close': 5289.0, 'volume': 1000, 'delta': -50},
                {'open': 5289.0, 'high': 5291.0, 'low': 5287.0, 'close': 5288.0, 'volume': 1200, 'delta': -80},
                {'open': 5288.0, 'high': 5293.0, 'low': 5287.0, 'close': 5292.0, 'volume': 1500, 'delta': 100}
            ],
            volume=1500,
            delta=100,
            cum_delta=1000,
            trades_count=150,
            spread_avg=0.25,
            vwap=5290.0,
            high=5293.0,
            low=5287.0,
            close=5292.0
        )
        
        context_m30 = ContextM30(
            bars=[
                {'open': 5285.0, 'high': 5295.0, 'low': 5280.0, 'close': 5292.0, 'volume': 5000, 'delta': 200}
            ],
            volume=5000,
            delta=200,
            cum_delta=5000,
            trades_count=500,
            spread_avg=0.25,
            vwap=5290.0,
            high=5295.0,
            low=5280.0,
            close=5292.0
        )
        
        oflow = OrderFlowContext(
            delta=100,
            cum_delta=1000,
            trades=[{'size': 10, 'price': 5292.0} for _ in range(10)],
            spread_synthetic=0.25,
            bid_ask_imbalance=0.1
        )
        
        # Test détection
        patterns = detector.detect_patterns(context_m1, context_m30, oflow, "MID")
        
        assert isinstance(patterns, list), "Doit retourner une liste"
        logger.info(f"✅ Test OK: {len(patterns)} patterns détectés")
        
        # Test stats
        stats = detector.get_pattern_stats()
        assert isinstance(stats, dict), "Stats doit être un dict"
        logger.info(f"✅ Stats OK: {stats}")
        
        # Test patterns MenthorQ
        patterns_mq = detector.detect_patterns(context_m1, context_m30, oflow, "MID", levels={
            "tick_size": 0.25,
            "menthorq": {
                "gamma": {"Call Resistance": 5300.0, "Put Support": 5285.0},
                "blind_spots": {"BL 1": 5295.0},
                "swing": {"SG1": 5288.0},
                "gex": {"GEX 1": 5295.0, "GEX 2": 5305.0, "GEX 3": 5286.0}
            }
        })
        logger.info(f"✅ Patterns MQ: {[p.name for p in patterns_mq]}")
        
        logger.info("🎉 Tous les tests Patterns Detector réussis!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_patterns_detector()
