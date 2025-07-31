"""
Feature Calculator Optimisé avec Cache - Version Corrigée
Corrige le problème de tracking des stats et le non-déterminisme
"""

from functools import lru_cache, wraps
from typing import Dict, Optional, Tuple, Any
import hashlib
import json
import time
import logging
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd

from core.base_types import MarketData, OrderFlowData, ES_TICK_SIZE
from .feature_calculator import FeatureCalculator  # Import original

logger = logging.getLogger(__name__)

# === CACHE UTILITIES ===


def make_hashable(obj: Any) -> str:
    """Convertit un objet en hash pour cache"""
    if isinstance(obj, (MarketData, OrderFlowData)):
        # Convertir dataclass en dict puis JSON
        return json.dumps(asdict(obj), sort_keys=True, default=str)
    elif isinstance(obj, dict):
        return json.dumps(obj, sort_keys=True, default=str)
    elif isinstance(obj, pd.DataFrame):
        return hashlib.md5(pd.util.hash_pandas_object(obj).values).hexdigest()
    else:
        return str(obj)


def cache_key(*args, **kwargs) -> str:
    """Génère une clé de cache unique"""
    key_parts = []
    for arg in args:
        key_parts.append(make_hashable(arg))
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{make_hashable(v)}")
    return hashlib.md5("".join(key_parts).encode()).hexdigest()


def timed_lru_cache(seconds: int = 300, maxsize: int = 128):
    """LRU cache avec expiration temporelle"""
    def decorator(func):
        # Cache avec timestamps
        cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Générer clé unique
            key = cache_key(*args[1:], **kwargs)  # Skip self
            now = time.time()

            # Vérifier si en cache et non expiré
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < seconds:
                    # Cache hit
                    if hasattr(args[0], '_cache_stats'):
                        args[0]._cache_stats['hits'] += 1
                    return result

            # Cache miss
            if hasattr(args[0], '_cache_stats'):
                args[0]._cache_stats['misses'] += 1

            # Calculer avec timing
            start_time = time.time()
            result = func(*args, **kwargs)
            calc_time = (time.time() - start_time) * 1000  # en ms

            # Mettre à jour stats de temps
            if hasattr(args[0], '_cache_stats'):
                args[0]._cache_stats['calculation_times'].append(calc_time)

            # Stocker dans cache
            cache[key] = (result, now)

            # Nettoyer cache expiré périodiquement
            if len(cache) > maxsize * 1.5:
                expired_keys = [k for k, (_, ts) in cache.items()
                                if now - ts >= seconds]
                for k in expired_keys[:len(expired_keys)//2]:  # Nettoyer la moitié
                    del cache[k]

            return result

        # Ajouter méthodes utiles
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_info = lambda: {"size": len(cache), "maxsize": maxsize}

        return wrapper
    return decorator

# === OPTIMIZED FEATURE CALCULATOR ===


class OptimizedFeatureCalculator(FeatureCalculator):
    """
    Feature Calculator avec cache intelligent
    Hérite de FeatureCalculator et ajoute optimisations
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'calculation_times': []
        }
        # Configuration cache
        cache_config = config.get('cache_config', {}) if config else {}
        self._cache_ttl = cache_config.get('cache_ttl', 60)
        self._cache_size = cache_config.get('cache_size', 500)

    def calculate_all_features(self,
                               market_data: MarketData,
                               order_flow: Optional[OrderFlowData] = None,
                               options_data: Optional[Dict[str, Any]] = None,
                               structure_data: Optional[Dict[str, Any]] = None,
                               sierra_patterns: Optional[Dict[str, float]] = None,
                               use_history: bool = True) -> Dict[str, float]:
        """Calcule toutes les features avec cache intelligent"""
        start_time = time.time()

        # Initialiser features
        features = {}

        # Features de base (rapides, pas besoin de cache)
        features.update(self._calculate_base_features(market_data))

        # Momentum (peut être caché si complexe)
        features.update(self._calculate_momentum_features(market_data))

        # Structure avec cache pour VWAP
        if structure_data and 'vwap_price' in structure_data:
            vwap_bands = tuple(structure_data.get('vwap_bands', []))  # Tuple pour hashable
            vwap_features = self._calculate_vwap_features_cached(
                market_data.close,
                structure_data['vwap_price'],
                vwap_bands
            )
            features.update(vwap_features)

        # Patterns Sierra - Utiliser les patterns fournis ou calculer
        if sierra_patterns:
            features.update(sierra_patterns)
        else:
            # Calculer avec cache si pas fourni
            prev_close = structure_data.get(
                'prev_close', market_data.close) if structure_data else market_data.close
            pattern_features = self._detect_sierra_pattern_cached(
                market_data.open,
                market_data.high,
                market_data.low,
                market_data.close,
                prev_close
            )
            features.update(pattern_features)

        # Gamma avec cache
        if options_data and 'gamma_levels' in options_data:
            gamma_str = json.dumps(options_data['gamma_levels'], sort_keys=True)
            gamma_features = self._calculate_gamma_features_cached(
                market_data.close,
                gamma_str
            )
            features.update(gamma_features)

        # Order flow (rapide, pas de cache)
        if order_flow:
            features.update(self._calculate_order_flow_features(order_flow))

        # Context (rapide, pas de cache)
        features.update(self._calculate_market_context_features(market_data))

        # Mesurer temps total
        total_time = (time.time() - start_time) * 1000
        self._cache_stats['calculation_times'].append(total_time)

        return features

    # === MÉTHODES HELPER ===

    def _calculate_band_position(self, price: float, upper_band: float, lower_band: float) -> float:
        """Calcule position relative dans une bande"""
        if upper_band == lower_band:
            return 0.5

        position = (price - lower_band) / (upper_band - lower_band)
        return max(0.0, min(1.0, position))

    def _calculate_band_proximity(self, price: float, upper_band: float,
                                  lower_band: float) -> float:
        """Calcule proximité aux bandes"""
        dist_upper = abs(price - upper_band)
        dist_lower = abs(price - lower_band)

        min_dist = min(dist_upper, dist_lower)
        normalized_dist = min_dist / abs(upper_band - lower_band) if upper_band != lower_band else 0

        return max(0.0, 1.0 - normalized_dist)

    # === MÉTHODES CACHÉES ===

    @timed_lru_cache(seconds=60, maxsize=500)
    def _calculate_vwap_features_cached(self,
                                        price: float,
                                        vwap: float,
                                        vwap_bands: Tuple[float, ...]) -> Dict[str, float]:
        """Version cachée du calcul VWAP"""
        features = {}

        # Distance VWAP
        features['vwap_distance'] = (price - vwap) / vwap * 100 if vwap > 0 else 0

        # Position par rapport à VWAP
        features['vwap_position'] = 1.0 if price > vwap else 0.0

        # Position dans les bandes SD1
        if len(vwap_bands) >= 2:
            features['sd1_position'] = self._calculate_band_position(
                price, vwap_bands[0], vwap_bands[1]
            )

        # Proximité aux bandes SD2
        if len(vwap_bands) >= 4:
            features['sd2_proximity'] = self._calculate_band_proximity(
                price, vwap_bands[2], vwap_bands[3]
            )

        return features

    @timed_lru_cache(seconds=60, maxsize=1000)
    def _detect_sierra_pattern_cached(self,
                                      open_: float,
                                      high: float,
                                      low: float,
                                      close: float,
                                      prev_close: float) -> Dict[str, float]:
        """Détection patterns Sierra avec cache"""
        range_size = high - low
        range_ticks = range_size / ES_TICK_SIZE

        patterns = {
            'long_down_up_bar': 0.0,
            'long_up_down_bar': 0.0,
            'color_down_setting': 0.0
        }

        # Long Down Up Bar
        if range_ticks >= 8 and open_ < prev_close * 0.999:  # Gap down
            if close > (low + range_size * 0.6):
                patterns['long_down_up_bar'] = min(1.0, range_ticks / 12)

        # Long Up Down Bar
        if range_ticks >= 8 and open_ > prev_close * 1.001:  # Gap up
            if close < (high - range_size * 0.6):
                patterns['long_up_down_bar'] = min(1.0, range_ticks / 16)

        # Color Down Setting
        if range_ticks >= 12 and close < open_:
            patterns['color_down_setting'] = min(1.0, range_ticks / 16)

        return patterns

    @timed_lru_cache(seconds=300, maxsize=200)
    def _calculate_gamma_features_cached(self,
                                         price: float,
                                         gamma_levels: str) -> Dict[str, float]:
        """Calcul features gamma avec cache"""
        # Reconvertir string en dict
        gamma_dict = json.loads(gamma_levels)
        features = {}

        # Distance aux niveaux gamma importants
        if 'call_wall' in gamma_dict:
            call_wall_dist = abs(price - gamma_dict['call_wall']) / price * 100
            features['gamma_call_wall_proximity'] = max(0, 1 - call_wall_dist / 2)

        if 'put_wall' in gamma_dict:
            put_wall_dist = abs(price - gamma_dict['put_wall']) / price * 100
            features['gamma_put_wall_proximity'] = max(0, 1 - put_wall_dist / 2)

        if 'flip_level' in gamma_dict:
            flip_dist = abs(price - gamma_dict['flip_level']) / price * 100
            features['gamma_flip_proximity'] = max(0, 1 - flip_dist / 1)

        return features

    # === MÉTHODES NON CACHÉES (RAPIDES) ===

    def _calculate_base_features(self, market_data: MarketData) -> Dict[str, float]:
        """Calcul features de base"""
        features = {}

        # Prix et range
        range_size = market_data.high - market_data.low
        features['range_size'] = range_size
        features['range_ticks'] = range_size / ES_TICK_SIZE

        # Direction
        features['bull_bar'] = 1.0 if market_data.close > market_data.open else 0.0
        features['bear_bar'] = 1.0 if market_data.close < market_data.open else 0.0

        # Position dans range
        if range_size > 0:
            features['close_position'] = (market_data.close - market_data.low) / range_size
        else:
            features['close_position'] = 0.5

        return features

    def _calculate_momentum_features(self, market_data: MarketData) -> Dict[str, float]:
        """Calcul features momentum"""
        features = {}

        # Momentum simple
        features['price_momentum'] = 0.0  # Nécessite historique
        features['volume_momentum'] = 0.0  # Nécessite historique

        # Pour l'instant, retourner des valeurs par défaut
        # Dans une implémentation complète, utiliser l'historique des prix

        return features

    def _calculate_order_flow_features(self, order_flow: OrderFlowData) -> Dict[str, float]:
        """Calcul features order flow (non caché car très rapide)"""
        features = {}

        # Delta features
        if hasattr(order_flow, 'cumulative_delta'):
            features['cumulative_delta_normalized'] = order_flow.cumulative_delta / 1000

        # Volume imbalance
        if hasattr(order_flow, 'volume_imbalance'):
            features['volume_imbalance'] = order_flow.volume_imbalance

        # POC distance
        if hasattr(order_flow, 'poc_price'):
            poc_distance = abs(order_flow.current_price - order_flow.poc_price)
            features['poc_distance_ticks'] = poc_distance / ES_TICK_SIZE

        # CVD momentum
        if hasattr(order_flow, 'cvd_momentum'):
            features['cvd_momentum'] = order_flow.cvd_momentum

        return features

    def _calculate_market_context_features(self, market_data: MarketData) -> Dict[str, float]:
        """Calcul features contexte marché"""
        features = {}

        # Range
        range_size = market_data.high - market_data.low
        features['range_ticks'] = range_size / ES_TICK_SIZE

        # Position dans la bougie
        if range_size > 0:
            features['candle_position'] = (market_data.close - market_data.low) / range_size
        else:
            features['candle_position'] = 0.5

        return features

    # === STATS ET GESTION CACHE ===

    def get_cache_stats(self) -> Dict[str, Any]:
        """Retourne statistiques du cache"""
        calc_times = self._cache_stats['calculation_times']
        total_calls = self._cache_stats['hits'] + self._cache_stats['misses']

        return {
            'cache_hits': self._cache_stats['hits'],
            'cache_misses': self._cache_stats['misses'],
            'hit_rate': self._cache_stats['hits'] / max(1, total_calls),
            'avg_calculation_time_ms': np.mean(calc_times) if calc_times else 0,
            'max_calculation_time_ms': max(calc_times) if calc_times else 0,
            'min_calculation_time_ms': min(calc_times) if calc_times else 0,
            'total_calculations': len(calc_times)
        }

    def clear_cache(self):
        """Vide tous les caches"""
        # Clear caches des méthodes
        if hasattr(self, '_calculate_vwap_features_cached'):
            self._calculate_vwap_features_cached.cache_clear()
        if hasattr(self, '_detect_sierra_pattern_cached'):
            self._detect_sierra_pattern_cached.cache_clear()
        if hasattr(self, '_calculate_gamma_features_cached'):
            self._calculate_gamma_features_cached.cache_clear()

        # Reset stats
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'calculation_times': []
        }

        logger.info("Feature calculator cache cleared")

# === FACTORY FUNCTION ===


def create_optimized_feature_calculator(
        config: Optional[Dict[str, Any]] = None) -> OptimizedFeatureCalculator:
    """Factory pour créer calculator optimisé"""
    return OptimizedFeatureCalculator(config)
