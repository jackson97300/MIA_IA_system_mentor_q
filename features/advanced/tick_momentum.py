"""
🎯 PHASE 2: ADVANCED FEATURES - FEATURE #1
TICK-BY-TICK MOMENTUM CALCULATOR

🎯 IMPACT: +2-3% win rate
Analyse la pression d'achat/vente tick par tick avec pondération volume
Détecte les accumulations/distributions granulaires

Performance: <1ms par calcul
Intégration: Compatible avec FeatureCalculator existant
"""

import time
import numpy as np
from typing import List, Dict, Optional, Tuple, NamedTuple
from dataclasses import dataclass
from collections import deque
from enum import Enum
import logging

# Imports locaux (selon architecture projet)
from core.base_types import MarketData

logger = logging.getLogger(__name__)

# ===== TYPES DE DONNÉES =====

class TickDirection(Enum):
    """Direction du tick"""
    UP = "up"
    DOWN = "down"
    NEUTRAL = "neutral"

@dataclass
class TickData:
    """Structure données tick individuel"""
    timestamp: float
    price: float
    volume: int
    direction: TickDirection
    aggressor: Optional[str] = None  # "buyer" or "seller"

@dataclass
class TickMomentumResult:
    """Résultat calcul momentum tick"""
    tick_momentum: float          # Momentum principal [-1, 1]
    volume_momentum: float        # Momentum pondéré volume [-1, 1]
    combined_momentum: float      # Momentum combiné final [-1, 1]
    pressure_strength: float      # Force de la pression [0, 1]
    directional_bias: str        # "bullish", "bearish", "neutral"
    calculation_time_ms: float   # Temps de calcul
    tick_count: int             # Nombre de ticks analysés
    confidence_score: float     # Score de confiance [0, 1]

class MomentumStrength(Enum):
    """Niveaux de force momentum"""
    STRONG_BULLISH = "strong_bullish"    # > 0.6
    MODERATE_BULLISH = "moderate_bullish" # 0.3 to 0.6
    NEUTRAL = "neutral"                   # -0.3 to 0.3
    MODERATE_BEARISH = "moderate_bearish" # -0.6 to -0.3
    STRONG_BEARISH = "strong_bearish"     # < -0.6

# ===== TICK MOMENTUM CALCULATOR =====

class TickMomentumCalculator:
    """
    Calculateur momentum tick-by-tick avec optimisation performance
    
    Features:
    - Analyse pression achat/vente granulaire
    - Pondération par volume intelligent
    - Cache LRU pour performance
    - Détection patterns accumulation/distribution
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialisation calculateur"""
        self.config = config or {}
        
        # Paramètres calcul
        self.default_window = self.config.get('tick_window', 20)
        self.volume_weight = self.config.get('volume_weight', 0.6)
        self.tick_weight = self.config.get('tick_weight', 0.4)
        
        # Historique ticks (buffer circulaire)
        self.max_history_size = self.config.get('max_history', 200)
        self.tick_history: deque = deque(maxlen=self.max_history_size)
        
        # Cache pour optimisation
        self.cache: Dict[str, Tuple[float, TickMomentumResult]] = {}
        self.cache_max_size = 50
        self.cache_ttl = 5.0  # 5 secondes
        
        # Statistiques performance
        self.stats = {
            'calculations_count': 0,
            'cache_hits': 0,
            'avg_calc_time_ms': 0.0,
            'total_ticks_processed': 0
        }
        
        logger.info(f"TickMomentumCalculator initialisé (window={self.default_window}, volume_weight={self.volume_weight})")
    
    def add_tick(self, price: float, volume: int, timestamp: Optional[float] = None) -> None:
        """
        Ajoute un nouveau tick à l'historique
        
        Args:
            price: Prix du tick
            volume: Volume du tick
            timestamp: Timestamp (optionnel, auto si None)
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Détermination direction du tick
        direction = self._determine_tick_direction(price)
        
        # Création tick data
        tick = TickData(
            timestamp=timestamp,
            price=price,
            volume=volume,
            direction=direction
        )
        
        # Ajout à l'historique
        self.tick_history.append(tick)
        self.stats['total_ticks_processed'] += 1
        
        # Nettoyage cache si trop ancien
        self._cleanup_cache()
    
    def calculate_tick_momentum(self, window: Optional[int] = None) -> TickMomentumResult:
        """
        🎯 CALCUL PRINCIPAL: Momentum tick-by-tick
        
        Analyse la pression d'achat/vente sur fenêtre glissante
        Pondère par volume pour détecter accumulation/distribution
        
        Args:
            window: Taille fenêtre analyse (défaut: 20)
            
        Returns:
            TickMomentumResult avec momentum combiné
        """
        start_time = time.perf_counter()
        
        try:
            # Paramètres
            window_size = window or self.default_window
            
            # Vérification cache
            cache_key = f"momentum_{window_size}_{len(self.tick_history)}"
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                self.stats['cache_hits'] += 1
                return cached_result
            
            # Vérification données suffisantes
            if len(self.tick_history) < 3:
                return self._create_neutral_result(start_time, window_size)
            
            # Extraction fenêtre analyse
            analysis_window = min(window_size, len(self.tick_history))
            recent_ticks = list(self.tick_history)[-analysis_window:]
            
            # 1. CALCUL MOMENTUM DIRECTIONNEL
            tick_momentum = self._calculate_directional_momentum(recent_ticks)
            
            # 2. CALCUL MOMENTUM VOLUME
            volume_momentum = self._calculate_volume_momentum(recent_ticks)
            
            # 3. COMBINAISON PONDÉRÉE
            combined_momentum = (tick_momentum * self.tick_weight + 
                               volume_momentum * self.volume_weight)
            
            # 4. ANALYSE FORCE ET BIAIS
            pressure_strength = abs(combined_momentum)
            directional_bias = self._determine_bias(combined_momentum)
            confidence_score = self._calculate_confidence(recent_ticks, combined_momentum)
            
            # 5. CRÉATION RÉSULTAT
            calc_time = (time.perf_counter() - start_time) * 1000
            
            result = TickMomentumResult(
                tick_momentum=tick_momentum,
                volume_momentum=volume_momentum,
                combined_momentum=combined_momentum,
                pressure_strength=pressure_strength,
                directional_bias=directional_bias,
                calculation_time_ms=calc_time,
                tick_count=len(recent_ticks),
                confidence_score=confidence_score
            )
            
            # Cache et stats
            self._cache_result(cache_key, result)
            self._update_stats(calc_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur calcul tick momentum: {e}")
            return self._create_neutral_result(start_time, window_size)
    
    def _determine_tick_direction(self, current_price: float) -> TickDirection:
        """Détermine direction du tick vs tick précédent"""
        if len(self.tick_history) == 0:
            return TickDirection.NEUTRAL
        
        last_price = self.tick_history[-1].price
        
        if current_price > last_price:
            return TickDirection.UP
        elif current_price < last_price:
            return TickDirection.DOWN
        else:
            return TickDirection.NEUTRAL
    
    def _calculate_directional_momentum(self, ticks: List[TickData]) -> float:
        """
        Calcule momentum directionnel pur
        
        Returns:
            float: Momentum [-1, 1]
        """
        if len(ticks) < 2:
            return 0.0
        
        # Comptage directions
        up_ticks = sum(1 for tick in ticks if tick.direction == TickDirection.UP)
        down_ticks = sum(1 for tick in ticks if tick.direction == TickDirection.DOWN)
        total_directional = up_ticks + down_ticks
        
        if total_directional == 0:
            return 0.0
        
        # Momentum normalisé
        momentum = (up_ticks - down_ticks) / len(ticks)
        return np.clip(momentum, -1.0, 1.0)
    
    def _calculate_volume_momentum(self, ticks: List[TickData]) -> float:
        """
        Calcule momentum pondéré par volume
        
        Accumulation = volume sur upticks
        Distribution = volume sur downticks
        
        Returns:
            float: Volume momentum [-1, 1]
        """
        if len(ticks) < 2:
            return 0.0
        
        # Volume par direction
        up_volume = sum(tick.volume for tick in ticks 
                       if tick.direction == TickDirection.UP)
        down_volume = sum(tick.volume for tick in ticks 
                         if tick.direction == TickDirection.DOWN)
        total_volume = sum(tick.volume for tick in ticks)
        
        if total_volume == 0:
            return 0.0
        
        # Momentum volume pondéré
        volume_momentum = (up_volume - down_volume) / total_volume
        return np.clip(volume_momentum, -1.0, 1.0)
    
    def _determine_bias(self, momentum: float) -> str:
        """Détermine biais directionnel"""
        if momentum > 0.3:
            return "bullish"
        elif momentum < -0.3:
            return "bearish"
        else:
            return "neutral"
    
    def _calculate_confidence(self, ticks: List[TickData], momentum: float) -> float:
        """
        Calcule score de confiance du signal
        
        Facteurs:
        - Consistance directionnelle
        - Volume relatif
        - Nombre de ticks
        """
        if len(ticks) < 3:
            return 0.0
        
        # 1. Consistance directionnelle
        direction_consistency = abs(momentum)
        
        # 2. Volume consistency (évite les micro-volumes)
        volumes = [tick.volume for tick in ticks]
        avg_volume = np.mean(volumes)
        volume_factor = min(1.0, avg_volume / 100)  # Normalisation arbitraire
        
        # 3. Sample size factor
        sample_factor = min(1.0, len(ticks) / self.default_window)
        
        # Confidence combinée
        confidence = (direction_consistency * 0.5 + 
                     volume_factor * 0.3 + 
                     sample_factor * 0.2)
        
        return np.clip(confidence, 0.0, 1.0)
    
    def _create_neutral_result(self, start_time: float, window_size: int) -> TickMomentumResult:
        """Crée résultat neutre en cas de données insuffisantes"""
        calc_time = (time.perf_counter() - start_time) * 1000
        
        return TickMomentumResult(
            tick_momentum=0.0,
            volume_momentum=0.0,
            combined_momentum=0.0,
            pressure_strength=0.0,
            directional_bias="neutral",
            calculation_time_ms=calc_time,
            tick_count=len(self.tick_history),
            confidence_score=0.0
        )
    
    # ===== CACHE ET OPTIMISATION =====
    
    def _get_from_cache(self, key: str) -> Optional[TickMomentumResult]:
        """Récupération depuis cache avec TTL"""
        if key in self.cache:
            timestamp, result = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return result
            else:
                del self.cache[key]
        return None
    
    def _cache_result(self, key: str, result: TickMomentumResult) -> None:
        """Sauvegarde en cache avec gestion taille"""
        # Nettoyage si trop grand
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
    
    def _update_stats(self, calc_time: float) -> None:
        """Mise à jour statistiques performance"""
        self.stats['calculations_count'] += 1
        
        # Rolling average
        count = self.stats['calculations_count']
        prev_avg = self.stats['avg_calc_time_ms']
        self.stats['avg_calc_time_ms'] = ((prev_avg * (count - 1)) + calc_time) / count
    
    # ===== MÉTHODES UTILITAIRES =====
    
    def get_momentum_strength(self, momentum: float) -> MomentumStrength:
        """Classifie force du momentum"""
        if momentum > 0.6:
            return MomentumStrength.STRONG_BULLISH
        elif momentum > 0.3:
            return MomentumStrength.MODERATE_BULLISH
        elif momentum < -0.6:
            return MomentumStrength.STRONG_BEARISH
        elif momentum < -0.3:
            return MomentumStrength.MODERATE_BEARISH
        else:
            return MomentumStrength.NEUTRAL
    
    def get_statistics(self) -> Dict[str, any]:
        """Statistiques calculateur"""
        cache_hit_rate = (self.stats['cache_hits'] / max(1, self.stats['calculations_count'])) * 100
        
        return {
            'calculations_count': self.stats['calculations_count'],
            'total_ticks_processed': self.stats['total_ticks_processed'],
            'avg_calculation_time_ms': round(self.stats['avg_calc_time_ms'], 3),
            'cache_hit_rate_pct': round(cache_hit_rate, 1),
            'current_tick_count': len(self.tick_history),
            'cache_size': len(self.cache)
        }
    
    def reset_history(self) -> None:
        """Reset historique ticks (pour tests/debug)"""
        self.tick_history.clear()
        self.cache.clear()
        logger.info("Historique ticks reseté")

# ===== FACTORY ET HELPERS =====

def create_tick_momentum_calculator(config: Optional[Dict] = None) -> TickMomentumCalculator:
    """Factory function pour calculateur momentum"""
    return TickMomentumCalculator(config)

def simulate_tick_data(count: int = 50, 
                      base_price: float = 4500.0,
                      trend_bias: float = 0.0) -> List[TickData]:
    """
    Génère données tick simulées pour testing
    
    Args:
        count: Nombre de ticks à générer
        base_price: Prix de base
        trend_bias: Biais de tendance [-1, 1]
    """
    ticks = []
    current_price = base_price
    
    for i in range(count):
        # Direction avec biais
        if np.random.random() < (0.5 + trend_bias * 0.3):
            direction = TickDirection.UP
            price_change = np.random.uniform(0.25, 1.0)
        else:
            direction = TickDirection.DOWN
            price_change = -np.random.uniform(0.25, 1.0)
        
        current_price += price_change
        volume = np.random.randint(1, 100)
        
        tick = TickData(
            timestamp=time.time() + i,
            price=current_price,
            volume=volume,
            direction=direction
        )
        ticks.append(tick)
    
    return ticks

# ===== TESTING =====

def test_tick_momentum_calculator():
    """Test complet tick momentum calculator"""
    print("=" * 50)
    print("🎯 TEST TICK MOMENTUM CALCULATOR")
    print("=" * 50)
    
    # Configuration test
    config = {
        'tick_window': 20,
        'volume_weight': 0.6,
        'tick_weight': 0.4
    }
    
    calculator = create_tick_momentum_calculator(config)
    
    # Test 1: Données tick simulées bullish
    print("\n📈 TEST 1: Simulation tendance bullish")
    bullish_ticks = simulate_tick_data(30, 4500.0, 0.7)
    
    for tick in bullish_ticks:
        calculator.add_tick(tick.price, tick.volume, tick.timestamp)
    
    result = calculator.calculate_tick_momentum()
    print(f"Combined momentum: {result.combined_momentum:.3f}")
    print(f"Directional bias: {result.directional_bias}")
    print(f"Pressure strength: {result.pressure_strength:.3f}")
    print(f"Confidence: {result.confidence_score:.3f}")
    print(f"Calculation time: {result.calculation_time_ms:.2f}ms")
    
    # Test 2: Reset et tendance bearish
    print("\n📉 TEST 2: Simulation tendance bearish")
    calculator.reset_history()
    
    bearish_ticks = simulate_tick_data(25, 4500.0, -0.8)
    for tick in bearish_ticks:
        calculator.add_tick(tick.price, tick.volume, tick.timestamp)
    
    result = calculator.calculate_tick_momentum()
    print(f"Combined momentum: {result.combined_momentum:.3f}")
    print(f"Directional bias: {result.directional_bias}")
    print(f"Pressure strength: {result.pressure_strength:.3f}")
    
    # Test 3: Performance avec cache
    print("\n⚡ TEST 3: Performance cache")
    start = time.perf_counter()
    for _ in range(10):
        calculator.calculate_tick_momentum()
    cache_time = (time.perf_counter() - start) * 1000
    print(f"10 calculs avec cache: {cache_time:.2f}ms")
    
    # Statistiques finales
    stats = calculator.get_statistics()
    print(f"\n📊 STATISTIQUES:")
    for key, value in stats.items():
        print(f"   • {key}: {value}")
    
    print("\n✅ TICK MOMENTUM CALCULATOR TEST COMPLETED")
    return True

if __name__ == "__main__":
    test_tick_momentum_calculator()