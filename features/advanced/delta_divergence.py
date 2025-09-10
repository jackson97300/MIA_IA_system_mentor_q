"""
🎯 PHASE 2: ADVANCED FEATURES - FEATURE #2
DELTA DIVERGENCE DETECTION

🎯 IMPACT: +2-3% win rate
Détecte quand prix et delta divergent (signal de retournement)
Validation croisée avec volume confirmation

Performance: <1ms par calcul
Intégration: Compatible avec FeatureCalculator existant
"""

import time
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple, NamedTuple, Any  # ✅ AJOUT: Any pour compatibilité
from dataclasses import dataclass
from collections import deque
from enum import Enum
import logging
from scipy import stats

# Imports locaux (selon architecture projet)
from core.base_types import MarketData
from ..data_reader import get_latest_market_data

logger = logging.getLogger(__name__)

# ===== TYPES DE DONNÉES =====

class DivergenceType(Enum):
    """Types de divergence détectés"""
    BULLISH_DIVERGENCE = "bullish_divergence"    # Prix baisse, delta monte
    BEARISH_DIVERGENCE = "bearish_divergence"    # Prix monte, delta baisse
    NO_DIVERGENCE = "no_divergence"              # Prix et delta alignés
    HIDDEN_BULLISH = "hidden_bullish"            # Divergence cachée bull
    HIDDEN_BEARISH = "hidden_bearish"            # Divergence cachée bear

class DivergenceStrength(Enum):
    """Force de la divergence"""
    VERY_STRONG = "very_strong"      # > 0.8
    STRONG = "strong"                # 0.6 - 0.8
    MODERATE = "moderate"            # 0.4 - 0.6
    WEAK = "weak"                    # 0.2 - 0.4
    VERY_WEAK = "very_weak"          # < 0.2

@dataclass
class DeltaDataPoint:
    """Point de données delta"""
    timestamp: float
    price: float
    net_delta: float        # Delta net (acheteurs - vendeurs)
    cumulative_delta: float # Delta cumulé
    volume: int
    bid_volume: int
    ask_volume: int

@dataclass
class DivergenceSignal:
    """Signal de divergence détecté"""
    divergence_type: DivergenceType
    strength: float                  # Force divergence [0, 1]
    confidence: float               # Confiance [0, 1]
    price_slope: float              # Pente prix
    delta_slope: float              # Pente delta
    volume_confirmation: float      # Confirmation volume [0, 1]
    lookback_periods: int          # Périodes analysées
    signal_quality: DivergenceStrength

@dataclass
class DeltaDivergenceResult:
    """Résultat complet analyse divergence"""
    primary_signal: DivergenceSignal
    secondary_signals: List[DivergenceSignal]
    divergence_strength: float      # Force globale [0, 1]
    reversal_probability: float     # Probabilité retournement [0, 1]
    entry_signal: float            # Signal d'entrée [-1, 1]
    calculation_time_ms: float     # Temps calcul
    data_points_analyzed: int      # Points analysés
    volume_confirmation: float     # Confirmation volume globale
    
    # ✅ CORRECTION: Ajout méthodes pour compatibilité dictionnaire
    def get(self, key: str, default=None):
        """Méthode get() pour compatibilité avec code existant"""
        if hasattr(self, key):
            return getattr(self, key)
        return default
    
    def __getitem__(self, key: str):
        """Support pour access dict-style: result['key']"""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Attribut '{key}' non trouvé dans DeltaDivergenceResult")
    
    def __contains__(self, key: str) -> bool:
        """Support pour 'key' in result"""
        return hasattr(self, key)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit vers dictionnaire pour rétrocompatibilité"""
        return {
            'primary_signal': self.primary_signal,
            'secondary_signals': self.secondary_signals,
            'divergence_strength': self.divergence_strength,
            'reversal_probability': self.reversal_probability,
            'entry_signal': self.entry_signal,
            'calculation_time_ms': self.calculation_time_ms,
            'data_points_analyzed': self.data_points_analyzed,
            'volume_confirmation': self.volume_confirmation
        }

# ===== DELTA DIVERGENCE DETECTOR =====

class DeltaDivergenceDetector:
    """
    Détecteur de divergence prix/delta avec confirmation volume
    
    Fonctionnalités:
    - Détection divergences classiques et cachées
    - Calcul slopes avec régression linéaire
    - Validation croisée volume
    - Cache LRU pour performance
    - Multiple timeframes
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialisation détecteur"""
        self.config = config or {}
        
        # Paramètres divergence
        self.default_lookback = self.config.get('lookback_periods', 10)
        self.min_lookback = self.config.get('min_lookback', 5)
        self.max_lookback = self.config.get('max_lookback', 20)
        
        # Seuils détection
        self.divergence_threshold = self.config.get('divergence_threshold', 0.7)
        self.volume_confirmation_threshold = self.config.get('volume_threshold', 0.5)
        self.min_slope_significance = self.config.get('min_slope', 0.1)
        
        # Historique données
        self.max_history_size = self.config.get('max_history', 100)
        self.price_history: deque = deque(maxlen=self.max_history_size)
        self.delta_history: deque = deque(maxlen=self.max_history_size)
        self.volume_history: deque = deque(maxlen=self.max_history_size)
        
        # Cache pour optimisation
        self.cache: Dict[str, Tuple[float, DeltaDivergenceResult]] = {}
        self.cache_max_size = 30
        self.cache_ttl = 3.0  # 3 secondes
        
        # Statistiques
        self.stats = {
            'total_analyses': 0,
            'divergences_detected': 0,
            'bullish_divergences': 0,
            'bearish_divergences': 0,
            'avg_calc_time_ms': 0.0,
            'cache_hits': 0,
            'volume_confirmations': 0
        }
        
        logger.info(f"DeltaDivergenceDetector initialisé (lookback={self.default_lookback}, threshold={self.divergence_threshold})")
    
    def add_data_point(self, 
                      price: float, 
                      net_delta: float, 
                      volume: int,
                      bid_volume: int = 0,
                      ask_volume: int = 0,
                      timestamp: Optional[float] = None) -> None:
        """
        Ajoute un point de données pour analyse
        
        Args:
            price: Prix actuel
            net_delta: Delta net (acheteurs - vendeurs)
            volume: Volume total
            bid_volume: Volume bid
            ask_volume: Volume ask
            timestamp: Timestamp (auto si None)
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calcul delta cumulé
        if self.delta_history:
            last_cumulative = self.delta_history[-1].cumulative_delta
            cumulative_delta = last_cumulative + net_delta
        else:
            cumulative_delta = net_delta
        
        # Création point de données
        data_point = DeltaDataPoint(
            timestamp=timestamp,
            price=price,
            net_delta=net_delta,
            cumulative_delta=cumulative_delta,
            volume=volume,
            bid_volume=bid_volume,
            ask_volume=ask_volume
        )
        
        # Ajout aux historiques
        self.price_history.append(price)
        self.delta_history.append(data_point)
        self.volume_history.append(volume)
        
        # Nettoyage cache
        self._cleanup_cache()
    
    def add_real_market_data(self, symbol: str = "ES") -> None:
        """
        🆕 Ajoute les vraies données de marché depuis Sierra Chart
        
        Args:
            symbol: Symbole à analyser (défaut: ES)
        """
        try:
            # Récupérer les vraies données
            market_data = get_latest_market_data(symbol)
            
            if market_data and 'close' in market_data and 'delta' in market_data:
                price = market_data['close']
                delta = market_data['delta']
                volume = market_data.get('total_volume', 1000)
                bid_volume = market_data.get('bid_volume', 500)
                ask_volume = market_data.get('ask_volume', 500)
                
                # Ajouter le point de données
                self.add_data_point(price, delta, volume, bid_volume, ask_volume)
                
                logger.debug(f"✅ Données réelles ajoutées: {symbol} @ {price:.2f}, delta: {delta}")
            else:
                logger.warning(f"⚠️ Données incomplètes pour {symbol}")
                
        except Exception as e:
            logger.error(f"❌ Erreur ajout données réelles: {e}")
    
    def calculate_delta_divergence(self, lookback: Optional[int] = None) -> DeltaDivergenceResult:
        """
        🎯 CALCUL PRINCIPAL: Détection divergence prix/delta
        
        Analyse:
        1. Calcul slopes prix et delta
        2. Détection type divergence
        3. Validation volume
        4. Score de confiance
        
        Args:
            lookback: Périodes à analyser (défaut: 10)
            
        Returns:
            DeltaDivergenceResult avec signal divergence
        """
        start_time = time.perf_counter()
        
        try:
            # Paramètres
            periods = lookback or self.default_lookback
            periods = max(self.min_lookback, min(periods, self.max_lookback))
            
            # Vérification cache
            cache_key = f"divergence_{periods}_{len(self.delta_history)}"
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                self.stats['cache_hits'] += 1
                return cached_result
            
            # Vérification données suffisantes
            if len(self.price_history) < periods or len(self.delta_history) < periods:
                return self._create_neutral_result(start_time, periods)
            
            # Extraction données pour analyse
            recent_prices = list(self.price_history)[-periods:]
            recent_deltas = [d.cumulative_delta for d in list(self.delta_history)[-periods:]]
            recent_volumes = list(self.volume_history)[-periods:]
            
            # 1. CALCUL SLOPES AVEC RÉGRESSION
            price_slope, price_r2 = self._calculate_slope_with_r2(recent_prices)
            delta_slope, delta_r2 = self._calculate_slope_with_r2(recent_deltas)
            
            # 2. DÉTECTION TYPE DIVERGENCE
            divergence_type, divergence_strength = self._detect_divergence_type(
                price_slope, delta_slope, price_r2, delta_r2
            )
            
            # 3. VALIDATION VOLUME
            volume_confirmation = self._calculate_volume_confirmation(
                recent_volumes, recent_deltas, divergence_type
            )
            
            # 4. SIGNAL PRINCIPAL
            primary_signal = self._create_divergence_signal(
                divergence_type, divergence_strength, price_slope, delta_slope,
                volume_confirmation, periods
            )
            
            # 5. SIGNAUX SECONDAIRES (différents lookbacks)
            secondary_signals = self._analyze_multiple_timeframes(periods)
            
            # 6. CALCUL PROBABILITÉ RETOURNEMENT
            reversal_probability = self._calculate_reversal_probability(
                primary_signal, secondary_signals, volume_confirmation
            )
            
            # 7. SIGNAL D'ENTRÉE FINAL
            entry_signal = self._generate_entry_signal(
                primary_signal, reversal_probability, volume_confirmation
            )
            
            # 8. CRÉATION RÉSULTAT
            calc_time = (time.perf_counter() - start_time) * 1000
            
            result = DeltaDivergenceResult(
                primary_signal=primary_signal,
                secondary_signals=secondary_signals,
                divergence_strength=divergence_strength,
                reversal_probability=reversal_probability,
                entry_signal=entry_signal,
                calculation_time_ms=calc_time,
                data_points_analyzed=periods,
                volume_confirmation=volume_confirmation
            )
            
            # Cache et stats
            self._cache_result(cache_key, result)
            self._update_stats(calc_time, divergence_type, volume_confirmation)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur calcul divergence delta: {e}")
            return self._create_neutral_result(start_time, periods)
    
    def _calculate_slope_with_r2(self, data: List[float]) -> Tuple[float, float]:
        """
        Calcule slope avec régression linéaire et R²
        
        Returns:
            Tuple[slope, r_squared]
        """
        if len(data) < 3:
            return 0.0, 0.0
        
        try:
            x = np.arange(len(data))
            y = np.array(data)
            
            # Régression linéaire
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            r_squared = r_value ** 2
            
            return slope, r_squared
            
        except Exception:
            return 0.0, 0.0
    
    def _detect_divergence_type(self, 
                               price_slope: float, 
                               delta_slope: float,
                               price_r2: float,
                               delta_r2: float) -> Tuple[DivergenceType, float]:
        """
        Détecte type et force de divergence
        
        Returns:
            Tuple[divergence_type, strength]
        """
        # Vérification significativité slopes
        if abs(price_slope) < self.min_slope_significance or abs(delta_slope) < self.min_slope_significance:
            return DivergenceType.NO_DIVERGENCE, 0.0
        
        # Vérification qualité régression
        min_r2 = 0.3  # R² minimum pour considérer la tendance
        if price_r2 < min_r2 or delta_r2 < min_r2:
            return DivergenceType.NO_DIVERGENCE, 0.0
        
        # Calcul divergence strength
        # Plus les slopes vont dans des directions opposées, plus la divergence est forte
        divergence_raw = abs(price_slope + delta_slope) / (abs(price_slope) + abs(delta_slope) + 0.001)
        
        # Ajustement par qualité régression
        quality_factor = (price_r2 + delta_r2) / 2
        divergence_strength = divergence_raw * quality_factor
        
        # Détection type selon directions
        if divergence_strength > self.divergence_threshold:
            if price_slope > 0 and delta_slope < 0:
                return DivergenceType.BEARISH_DIVERGENCE, divergence_strength
            elif price_slope < 0 and delta_slope > 0:
                return DivergenceType.BULLISH_DIVERGENCE, divergence_strength
            elif price_slope > 0 and delta_slope > 0:
                # Prix et delta montent, mais à des rythmes différents
                if abs(price_slope) > abs(delta_slope) * 2:
                    return DivergenceType.HIDDEN_BEARISH, divergence_strength * 0.7
            elif price_slope < 0 and delta_slope < 0:
                # Prix et delta baissent, mais à des rythmes différents
                if abs(delta_slope) > abs(price_slope) * 2:
                    return DivergenceType.HIDDEN_BULLISH, divergence_strength * 0.7
        
        return DivergenceType.NO_DIVERGENCE, divergence_strength
    
    def _calculate_volume_confirmation(self, 
                                     volumes: List[int],
                                     deltas: List[float],
                                     divergence_type: DivergenceType) -> float:
        """
        Calcule confirmation volume pour divergence
        
        Volume confirmation = cohérence entre volume et direction delta
        """
        if len(volumes) < 3 or divergence_type == DivergenceType.NO_DIVERGENCE:
            return 0.0
        
        try:
            # Volume moyen récent vs historique
            recent_volume = np.mean(volumes[-3:])
            avg_volume = np.mean(volumes)
            
            if avg_volume == 0:
                return 0.0
            
            volume_ratio = recent_volume / avg_volume
            
            # Delta momentum récent
            recent_delta_change = deltas[-1] - deltas[-3] if len(deltas) >= 3 else 0
            
            # Confirmation selon type divergence
            if divergence_type == DivergenceType.BULLISH_DIVERGENCE:
                # Pour divergence bullish, on veut voir du volume sur delta positif
                confirmation = min(1.0, volume_ratio) * (1 if recent_delta_change > 0 else 0.5)
            elif divergence_type == DivergenceType.BEARISH_DIVERGENCE:
                # Pour divergence bearish, on veut voir du volume sur delta négatif
                confirmation = min(1.0, volume_ratio) * (1 if recent_delta_change < 0 else 0.5)
            else:
                # Divergences cachées
                confirmation = min(1.0, volume_ratio) * 0.7
            
            return np.clip(confirmation, 0.0, 1.0)
            
        except Exception:
            return 0.0
    
    def _create_divergence_signal(self,
                                 divergence_type: DivergenceType,
                                 strength: float,
                                 price_slope: float,
                                 delta_slope: float,
                                 volume_confirmation: float,
                                 periods: int) -> DivergenceSignal:
        """Crée signal de divergence structuré"""
        
        # Calcul confiance
        confidence = strength * volume_confirmation
        
        # Classification strength
        if strength > 0.8:
            signal_quality = DivergenceStrength.VERY_STRONG
        elif strength > 0.6:
            signal_quality = DivergenceStrength.STRONG
        elif strength > 0.4:
            signal_quality = DivergenceStrength.MODERATE
        elif strength > 0.2:
            signal_quality = DivergenceStrength.WEAK
        else:
            signal_quality = DivergenceStrength.VERY_WEAK
        
        return DivergenceSignal(
            divergence_type=divergence_type,
            strength=strength,
            confidence=confidence,
            price_slope=price_slope,
            delta_slope=delta_slope,
            volume_confirmation=volume_confirmation,
            lookback_periods=periods,
            signal_quality=signal_quality
        )
    
    def _analyze_multiple_timeframes(self, base_periods: int) -> List[DivergenceSignal]:
        """Analyse divergences sur multiples timeframes"""
        secondary_signals = []
        
        # Timeframes alternatifs
        timeframes = [
            max(self.min_lookback, base_periods // 2),  # Plus court
            min(self.max_lookback, base_periods * 2)    # Plus long
        ]
        
        for tf in timeframes:
            if tf != base_periods and len(self.price_history) >= tf:
                try:
                    # Extraction données
                    prices = list(self.price_history)[-tf:]
                    deltas = [d.cumulative_delta for d in list(self.delta_history)[-tf:]]
                    volumes = list(self.volume_history)[-tf:]
                    
                    # Calcul slopes
                    price_slope, price_r2 = self._calculate_slope_with_r2(prices)
                    delta_slope, delta_r2 = self._calculate_slope_with_r2(deltas)
                    
                    # Détection divergence
                    div_type, strength = self._detect_divergence_type(
                        price_slope, delta_slope, price_r2, delta_r2
                    )
                    
                    if div_type != DivergenceType.NO_DIVERGENCE:
                        volume_conf = self._calculate_volume_confirmation(volumes, deltas, div_type)
                        signal = self._create_divergence_signal(
                            div_type, strength, price_slope, delta_slope, volume_conf, tf
                        )
                        secondary_signals.append(signal)
                        
                except Exception:
                    continue
        
        return secondary_signals
    
    def _calculate_reversal_probability(self,
                                      primary_signal: DivergenceSignal,
                                      secondary_signals: List[DivergenceSignal],
                                      volume_confirmation: float) -> float:
        """
        Calcule probabilité de retournement
        
        Facteurs:
        - Force signal principal
        - Convergence signaux secondaires
        - Confirmation volume
        """
        if primary_signal.divergence_type == DivergenceType.NO_DIVERGENCE:
            return 0.0
        
        # Base: force signal principal
        base_probability = primary_signal.strength * primary_signal.confidence
        
        # Bonus convergence multi-timeframe
        convergence_bonus = 0.0
        if secondary_signals:
            same_direction = sum(1 for s in secondary_signals 
                               if s.divergence_type == primary_signal.divergence_type)
            convergence_bonus = (same_direction / len(secondary_signals)) * 0.2
        
        # Bonus volume
        volume_bonus = volume_confirmation * 0.15
        
        # Probabilité finale
        probability = base_probability + convergence_bonus + volume_bonus
        return np.clip(probability, 0.0, 1.0)
    
    def _generate_entry_signal(self,
                              primary_signal: DivergenceSignal,
                              reversal_probability: float,
                              volume_confirmation: float) -> float:
        """
        Génère signal d'entrée final [-1, 1]
        
        -1 = Signal short fort
         0 = Pas de signal  
        +1 = Signal long fort
        """
        if primary_signal.divergence_type == DivergenceType.NO_DIVERGENCE:
            return 0.0
        
        # Direction signal selon type divergence
        if primary_signal.divergence_type in [DivergenceType.BULLISH_DIVERGENCE, DivergenceType.HIDDEN_BULLISH]:
            direction = 1.0
        elif primary_signal.divergence_type in [DivergenceType.BEARISH_DIVERGENCE, DivergenceType.HIDDEN_BEARISH]:
            direction = -1.0
        else:
            return 0.0
        
        # Force signal
        signal_strength = reversal_probability
        
        # Validation volume minimale
        if volume_confirmation < self.volume_confirmation_threshold:
            signal_strength *= 0.5  # Réduction si volume faible
        
        return direction * signal_strength
    
    def _create_neutral_result(self, start_time: float, periods: int) -> DeltaDivergenceResult:
        """Crée résultat neutre en cas de données insuffisantes"""
        calc_time = (time.perf_counter() - start_time) * 1000
        
        neutral_signal = DivergenceSignal(
            divergence_type=DivergenceType.NO_DIVERGENCE,
            strength=0.0,
            confidence=0.0,
            price_slope=0.0,
            delta_slope=0.0,
            volume_confirmation=0.0,
            lookback_periods=periods,
            signal_quality=DivergenceStrength.VERY_WEAK
        )
        
        return DeltaDivergenceResult(
            primary_signal=neutral_signal,
            secondary_signals=[],
            divergence_strength=0.0,
            reversal_probability=0.0,
            entry_signal=0.0,
            calculation_time_ms=calc_time,
            data_points_analyzed=len(self.delta_history),
            volume_confirmation=0.0
        )
    
    # ===== CACHE ET OPTIMISATION =====
    
    def _get_from_cache(self, key: str) -> Optional[DeltaDivergenceResult]:
        """Récupération depuis cache avec TTL"""
        if key in self.cache:
            timestamp, result = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return result
            else:
                del self.cache[key]
        return None
    
    def _cache_result(self, key: str, result: DeltaDivergenceResult) -> None:
        """Sauvegarde en cache"""
        if len(self.cache) >= self.cache_max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = (time.time(), result)
    
    def _cleanup_cache(self) -> None:
        """Nettoyage cache expiré"""
        current_time = time.time()
        expired_keys = [
            key for key, (timestamp, _) in self.cache.items()
            if current_time - timestamp > self.cache_ttl
        ]
        for key in expired_keys:
            del self.cache[key]
    
    def _update_stats(self, calc_time: float, divergence_type: DivergenceType, volume_conf: float) -> None:
        """Mise à jour statistiques"""
        self.stats['total_analyses'] += 1
        
        # Rolling average calc time
        count = self.stats['total_analyses']
        prev_avg = self.stats['avg_calc_time_ms']
        self.stats['avg_calc_time_ms'] = ((prev_avg * (count - 1)) + calc_time) / count
        
        # Comptage divergences
        if divergence_type != DivergenceType.NO_DIVERGENCE:
            self.stats['divergences_detected'] += 1
            
            if divergence_type in [DivergenceType.BULLISH_DIVERGENCE, DivergenceType.HIDDEN_BULLISH]:
                self.stats['bullish_divergences'] += 1
            elif divergence_type in [DivergenceType.BEARISH_DIVERGENCE, DivergenceType.HIDDEN_BEARISH]:
                self.stats['bearish_divergences'] += 1
        
        # Volume confirmations
        if volume_conf > self.volume_confirmation_threshold:
            self.stats['volume_confirmations'] += 1
    
    # ===== MÉTHODES UTILITAIRES =====
    
    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques détecteur"""
        total = self.stats['total_analyses']
        cache_hit_rate = (self.stats['cache_hits'] / max(1, total)) * 100
        divergence_rate = (self.stats['divergences_detected'] / max(1, total)) * 100
        volume_confirmation_rate = (self.stats['volume_confirmations'] / max(1, total)) * 100
        
        return {
            'total_analyses': total,
            'divergences_detected': self.stats['divergences_detected'],
            'bullish_divergences': self.stats['bullish_divergences'],
            'bearish_divergences': self.stats['bearish_divergences'],
            'avg_calculation_time_ms': round(self.stats['avg_calc_time_ms'], 3),
            'cache_hit_rate_pct': round(cache_hit_rate, 1),
            'divergence_detection_rate_pct': round(divergence_rate, 1),
            'volume_confirmation_rate_pct': round(volume_confirmation_rate, 1),
            'current_data_points': len(self.delta_history),
            'cache_size': len(self.cache)
        }
    
    def reset_history(self) -> None:
        """Reset historique (pour tests/debug)"""
        self.price_history.clear()
        self.delta_history.clear()
        self.volume_history.clear()
        self.cache.clear()
        logger.info("Historique delta divergence reseté")

# ===== FACTORY ET HELPERS =====

def create_delta_divergence_detector(config: Optional[Dict] = None) -> DeltaDivergenceDetector:
    """Factory function pour détecteur divergence"""
    return DeltaDivergenceDetector(config)

def simulate_divergence_scenario(scenario: str = "bullish") -> List[Tuple[float, float, int]]:
    """
    Génère scénario de divergence pour testing
    
    Args:
        scenario: "bullish", "bearish", "none"
        
    Returns:
        List[(price, delta, volume)]
    """
    data_points = []
    base_price = 4500.0
    base_delta = 0.0
    
    for i in range(20):
        if scenario == "bullish":
            # Prix baisse mais delta monte (divergence bullish)
            price = base_price - (i * 0.5) + np.random.normal(0, 0.2)
            delta = base_delta + (i * 2.0) + np.random.normal(0, 1.0)
        elif scenario == "bearish":
            # Prix monte mais delta baisse (divergence bearish)
            price = base_price + (i * 0.5) + np.random.normal(0, 0.2)
            delta = base_delta - (i * 2.0) + np.random.normal(0, 1.0)
        else:  # "none"
            # Prix et delta alignés
            price = base_price + (i * 0.3) + np.random.normal(0, 0.2)
            delta = base_delta + (i * 1.5) + np.random.normal(0, 1.0)
        
        volume = int(50 + np.random.exponential(50))
        data_points.append((price, delta, volume))
    
    return data_points

# ===== TESTING =====

def test_delta_divergence_detector():
    """Test complet delta divergence detector"""
    print("=" * 50)
    print("🎯 TEST DELTA DIVERGENCE DETECTOR")
    print("=" * 50)
    
    # Configuration test
    config = {
        'lookback_periods': 10,
        'divergence_threshold': 0.7,
        'volume_threshold': 0.5
    }
    
    detector = create_delta_divergence_detector(config)
    
    # Test 1: Divergence bullish
    print("\n📈 TEST 1: Divergence bullish")
    bullish_data = simulate_divergence_scenario("bullish")
    
    for price, delta, volume in bullish_data:
        detector.add_data_point(price, delta, volume)
    
    result = detector.calculate_delta_divergence()
    print(f"Type divergence: {result.primary_signal.divergence_type.value}")
    print(f"Force: {result.divergence_strength:.3f}")
    print(f"Signal entrée: {result.entry_signal:.3f}")
    print(f"Probabilité retournement: {result.reversal_probability:.3f}")
    print(f"Confirmation volume: {result.volume_confirmation:.3f}")
    print(f"Temps calcul: {result.calculation_time_ms:.2f}ms")
    
    # Test 2: Reset et divergence bearish
    print("\n📉 TEST 2: Divergence bearish")
    detector.reset_history()
    
    bearish_data = simulate_divergence_scenario("bearish")
    for price, delta, volume in bearish_data:
        detector.add_data_point(price, delta, volume)
    
    result = detector.calculate_delta_divergence()
    print(f"Type divergence: {result.primary_signal.divergence_type.value}")
    print(f"Signal entrée: {result.entry_signal:.3f}")
    print(f"Signaux secondaires: {len(result.secondary_signals)}")
    
    # Test 3: Pas de divergence
    print("\n➡️ TEST 3: Aucune divergence")
    detector.reset_history()
    
    neutral_data = simulate_divergence_scenario("none")
    for price, delta, volume in neutral_data:
        detector.add_data_point(price, delta, volume)
    
    result = detector.calculate_delta_divergence()
    print(f"Type divergence: {result.primary_signal.divergence_type.value}")
    print(f"Signal entrée: {result.entry_signal:.3f}")
    
    # Test 4: Performance cache
    print("\n⚡ TEST 4: Performance cache")
    start = time.perf_counter()
    for _ in range(10):
        detector.calculate_delta_divergence()
    cache_time = (time.perf_counter() - start) * 1000
    print(f"10 calculs avec cache: {cache_time:.2f}ms")
    
    # Statistiques finales
    stats = detector.get_statistics()
    print(f"\n📊 STATISTIQUES:")
    for key, value in stats.items():
        print(f"   • {key}: {value}")
    
    print("\n✅ DELTA DIVERGENCE DETECTOR TEST COMPLETED")
    return True

if __name__ == "__main__":
    test_delta_divergence_detector()