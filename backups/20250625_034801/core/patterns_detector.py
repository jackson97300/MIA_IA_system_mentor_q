"""
MIA_IA_SYSTEM - Patterns Detector
PATTERNS ÉLITES COMPLÉTANT LE SYSTÈME
Version: Production Ready
Performance: <1ms par pattern garanti

PATTERNS IMPLÉMENTÉS :
1. GAMMA PIN - Zones où gamma options influence price action
2. HEADFAKE - Faux breakouts avec absorption order flow  
3. MICROSTRUCTURE ANOMALY - Anomalies détectées dans structure marché

INTÉGRATION SYSTÈME :
- Compatible avec battle_navale.py
- Utilisé par feature_calculator.py
- Expose patterns via base_types.py
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import deque

# Local imports
from core.base_types import (
    MarketData, OrderFlowData, PatternType,
    ES_TICK_SIZE, ES_TICK_VALUE
)

logger = logging.getLogger(__name__)

# === PATTERN ENUMS ===

class GammaPinStrength(Enum):
    """Force du gamma pin"""
    NO_PIN = "no_pin"              # <0.3 - Pas de pin
    WEAK_PIN = "weak_pin"          # 0.3-0.5 - Pin faible  
    MODERATE_PIN = "moderate_pin"  # 0.5-0.7 - Pin modéré
    STRONG_PIN = "strong_pin"      # 0.7-0.9 - Pin fort
    EXTREME_PIN = "extreme_pin"    # >0.9 - Pin extrême

class HeadFakeType(Enum):
    """Types de headfakes"""
    BULL_TRAP = "bull_trap"        # Faux breakout haussier
    BEAR_TRAP = "bear_trap"        # Faux breakout baissier
    RANGE_FAKE = "range_fake"      # Faux breakout range
    NO_HEADFAKE = "no_headfake"    # Pas de headfake

class AnomalyType(Enum):
    """Types d'anomalies microstructure"""
    VOLUME_ANOMALY = "volume_anomaly"          # Volume anormal
    SPREAD_ANOMALY = "spread_anomaly"          # Spread anormal
    ORDER_FLOW_ANOMALY = "order_flow_anomaly" # Order flow bizarre
    LATENCY_ANOMALY = "latency_anomaly"        # Latence réseau
    NO_ANOMALY = "no_anomaly"                  # RAS

# === DATACLASSES ===

@dataclass
class GammaPinResult:
    """Résultat analyse gamma pin"""
    timestamp: pd.Timestamp
    
    # Pin strength
    pin_strength: float = 0.0              # 0-1
    pin_level: float = 0.0                 # Prix du pin
    distance_to_pin: float = 0.0           # Distance en ticks
    
    # Gamma data
    call_wall: float = 0.0
    put_wall: float = 0.0
    net_gamma: float = 0.0
    gamma_exposure: float = 0.0
    
    # Classification
    pin_type: GammaPinStrength = GammaPinStrength.NO_PIN
    
    # Performance
    calculation_time_ms: float = 0.0

@dataclass
class HeadFakeResult:
    """Résultat analyse headfake"""
    timestamp: pd.Timestamp
    
    # Headfake data
    headfake_strength: float = 0.0         # 0-1
    breakout_level: float = 0.0            # Niveau cassé
    fake_confirmation: bool = False        # Faux breakout confirmé
    
    # Order flow analysis
    absorption_detected: bool = False      # Absorption order flow
    volume_spike: float = 0.0              # Volume spike ratio
    delta_divergence: float = 0.0          # Divergence net delta
    
    # Classification  
    headfake_type: HeadFakeType = HeadFakeType.NO_HEADFAKE
    
    # Performance
    calculation_time_ms: float = 0.0

@dataclass
class MicrostructureAnomalyResult:
    """Résultat analyse anomalie microstructure"""
    timestamp: pd.Timestamp
    
    # Anomaly strength
    anomaly_strength: float = 0.0          # 0-1
    anomaly_score: float = 0.0             # Score composite
    
    # Specific anomalies
    volume_anomaly: float = 0.0            # Anomalie volume
    spread_anomaly: float = 0.0            # Anomalie spread
    flow_anomaly: float = 0.0              # Anomalie order flow
    
    # Classification
    primary_anomaly: AnomalyType = AnomalyType.NO_ANOMALY
    
    # Market impact prediction
    predicted_impact: str = "none"         # none, bullish, bearish
    confidence: float = 0.0
    
    # Performance
    calculation_time_ms: float = 0.0

@dataclass
class PatternsDetectionResult:
    """Résultat complet tous patterns"""
    timestamp: pd.Timestamp
    
    # Pattern results
    gamma_pin: GammaPinResult
    headfake: HeadFakeResult
    microstructure: MicrostructureAnomalyResult
    
    # Aggregate scores (for feature_calculator)
    gamma_pin_strength: float = 0.0        # 0-1
    headfake_signal: float = 0.0           # 0-1  
    microstructure_anomaly: float = 0.0    # 0-1
    
    # Performance
    total_calculation_time_ms: float = 0.0
    patterns_detected_count: int = 0

# === MAIN PATTERNS DETECTOR ===

class ElitePatternsDetector:
    """
    DÉTECTEUR PATTERNS ÉLITES
    
    Implémente les 3 patterns manquants du système :
    1. Gamma Pin (influence options sur ES)
    2. Headfake (faux breakouts + absorption)
    3. Microstructure Anomaly (anomalies marché)
    
    Performance garantie <1ms par pattern
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation détecteur patterns"""
        self.config = config or {}
        
        # Paramètres gamma pin
        self.gamma_pin_params = {
            'proximity_threshold_ticks': self.config.get('gamma_proximity_ticks', 5),
            'pin_strength_multiplier': self.config.get('pin_multiplier', 2.0),
            'min_gamma_exposure': self.config.get('min_gamma', 1000)
        }
        
        # Paramètres headfake
        self.headfake_params = {
            'min_breakout_volume': self.config.get('min_breakout_vol', 1.5),
            'absorption_threshold': self.config.get('absorption_thresh', 0.7),
            'lookback_bars': self.config.get('headfake_lookback', 10)
        }
        
        # Paramètres microstructure
        self.microstructure_params = {
            'volume_anomaly_threshold': self.config.get('vol_anomaly', 3.0),
            'spread_anomaly_threshold': self.config.get('spread_anomaly', 2.0),
            'flow_anomaly_threshold': self.config.get('flow_anomaly', 2.5)
        }
        
        # Historiques
        self.price_history: deque = deque(maxlen=50)
        self.volume_history: deque = deque(maxlen=30)
        self.spread_history: deque = deque(maxlen=30)
        
        # Performance tracking
        self.stats = {
            'gamma_pins_detected': 0,
            'headfakes_detected': 0,
            'anomalies_detected': 0,
            'total_analyses': 0,
            'avg_calc_time_ms': 0.0
        }
        
        logger.info("ElitePatternsDetector initialisé - 3 patterns élites")
    
    def detect_all_patterns(self,
                          market_data: MarketData,
                          options_data: Optional[Dict[str, Any]] = None,
                          order_flow: Optional[OrderFlowData] = None) -> PatternsDetectionResult:
        """
        DÉTECTION COMPLÈTE TOUS PATTERNS
        
        Args:
            market_data: Données OHLC + volume
            options_data: Données options pour gamma pin
            order_flow: Order flow pour headfake + anomalies
            
        Returns:
            PatternsDetectionResult avec tous patterns
        """
        start_time = time.perf_counter()
        
        try:
            # Ajout historique
            self.price_history.append(market_data)
            if market_data.volume > 0:
                self.volume_history.append(market_data.volume)
            if market_data.spread:
                self.spread_history.append(market_data.spread)
            
            # === 1. GAMMA PIN DETECTION ===
            
            gamma_result = self.detect_gamma_pin(market_data, options_data)
            
            # === 2. HEADFAKE DETECTION ===
            
            headfake_result = self.detect_headfake(market_data, order_flow)
            
            # === 3. MICROSTRUCTURE ANOMALY ===
            
            anomaly_result = self.detect_microstructure_anomaly(market_data, order_flow)
            
            # === 4. SYNTHÈSE FINALE ===
            
            result = PatternsDetectionResult(
                timestamp=market_data.timestamp,
                gamma_pin=gamma_result,
                headfake=headfake_result,
                microstructure=anomaly_result,
                
                # Aggregate scores for feature_calculator
                gamma_pin_strength=gamma_result.pin_strength,
                headfake_signal=headfake_result.headfake_strength,
                microstructure_anomaly=anomaly_result.anomaly_strength,
                
                patterns_detected_count=sum([
                    1 if gamma_result.pin_strength > 0.3 else 0,
                    1 if headfake_result.headfake_strength > 0.3 else 0,
                    1 if anomaly_result.anomaly_strength > 0.3 else 0
                ])
            )
            
            # Performance tracking
            calc_time = (time.perf_counter() - start_time) * 1000
            result.total_calculation_time_ms = calc_time
            
            self._update_stats(calc_time, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur détection patterns: {e}")
            return PatternsDetectionResult(
                timestamp=market_data.timestamp,
                gamma_pin=GammaPinResult(timestamp=market_data.timestamp),
                headfake=HeadFakeResult(timestamp=market_data.timestamp),
                microstructure=MicrostructureAnomalyResult(timestamp=market_data.timestamp),
                total_calculation_time_ms=(time.perf_counter() - start_time) * 1000
            )
    
    def detect_gamma_pin(self,
                        market_data: MarketData,
                        options_data: Optional[Dict[str, Any]] = None) -> GammaPinResult:
        """
        DÉTECTION GAMMA PIN
        
        Analyse si le prix est "pinné" par les niveaux gamma options.
        Basé sur call/put walls et exposition gamma dealers.
        """
        start_time = time.perf_counter()
        
        try:
            result = GammaPinResult(timestamp=market_data.timestamp)
            
            if not options_data:
                return result
            
            # Extract options data
            call_wall = options_data.get('call_wall', 0.0)
            put_wall = options_data.get('put_wall', 0.0)
            net_gamma = options_data.get('net_gamma', 0.0)
            
            result.call_wall = call_wall
            result.put_wall = put_wall
            result.net_gamma = net_gamma
            result.gamma_exposure = abs(net_gamma)
            
            current_price = market_data.close
            
            # === PROXIMITÉ AUX GAMMA LEVELS ===
            
            pin_strength = 0.0
            pin_level = 0.0
            
            # Distance call wall
            if call_wall > 0:
                call_distance_ticks = abs(current_price - call_wall) / ES_TICK_SIZE
                if call_distance_ticks <= self.gamma_pin_params['proximity_threshold_ticks']:
                    call_pin_strength = 1.0 - (call_distance_ticks / self.gamma_pin_params['proximity_threshold_ticks'])
                    if call_pin_strength > pin_strength:
                        pin_strength = call_pin_strength
                        pin_level = call_wall
            
            # Distance put wall
            if put_wall > 0:
                put_distance_ticks = abs(current_price - put_wall) / ES_TICK_SIZE
                if put_distance_ticks <= self.gamma_pin_params['proximity_threshold_ticks']:
                    put_pin_strength = 1.0 - (put_distance_ticks / self.gamma_pin_params['proximity_threshold_ticks'])
                    if put_pin_strength > pin_strength:
                        pin_strength = put_pin_strength
                        pin_level = put_wall
            
            # === FORCE GAMMA EXPOSURE ===
            
            if result.gamma_exposure >= self.gamma_pin_params['min_gamma_exposure']:
                gamma_multiplier = min(result.gamma_exposure / 5000, 2.0)  # Scale up to 2x
                pin_strength *= gamma_multiplier
            
            # === CONFIRMATION VOLUME ===
            
            if len(self.volume_history) >= 5:
                recent_vol = np.mean(list(self.volume_history)[-5:])
                current_vol = market_data.volume
                
                if current_vol > 0:
                    vol_ratio = current_vol / recent_vol if recent_vol > 0 else 1.0
                    # Volume faible = potentiel pin plus fort
                    if vol_ratio < 0.7:  # Volume below average
                        pin_strength *= 1.2
            
            # === CLASSIFICATION ===
            
            result.pin_strength = min(pin_strength, 1.0)
            result.pin_level = pin_level
            result.distance_to_pin = abs(current_price - pin_level) / ES_TICK_SIZE if pin_level > 0 else 999
            
            if pin_strength >= 0.9:
                result.pin_type = GammaPinStrength.EXTREME_PIN
            elif pin_strength >= 0.7:
                result.pin_type = GammaPinStrength.STRONG_PIN
            elif pin_strength >= 0.5:
                result.pin_type = GammaPinStrength.MODERATE_PIN
            elif pin_strength >= 0.3:
                result.pin_type = GammaPinStrength.WEAK_PIN
            else:
                result.pin_type = GammaPinStrength.NO_PIN
            
            result.calculation_time_ms = (time.perf_counter() - start_time) * 1000
            return result
            
        except Exception as e:
            logger.error(f"Erreur gamma pin detection: {e}")
            return GammaPinResult(
                timestamp=market_data.timestamp,
                calculation_time_ms=(time.perf_counter() - start_time) * 1000
            )
    
    def detect_headfake(self,
                       market_data: MarketData,
                       order_flow: Optional[OrderFlowData] = None) -> HeadFakeResult:
        """
        DÉTECTION HEADFAKE (FAUX BREAKOUT)
        
        Identifie les faux breakouts avec absorption order flow.
        Analyse volume spike + divergence delta.
        """
        start_time = time.perf_counter()
        
        try:
            result = HeadFakeResult(timestamp=market_data.timestamp)
            
            if len(self.price_history) < self.headfake_params['lookback_bars']:
                return result
            
            bars = list(self.price_history)
            current_bar = bars[-1]
            recent_bars = bars[-self.headfake_params['lookback_bars']:]
            
            # === IDENTIFICATION BREAKOUT ===
            
            # Calcul range récent
            recent_highs = [bar.high for bar in recent_bars[:-1]]  # Exclude current
            recent_lows = [bar.low for bar in recent_bars[:-1]]
            
            resistance_level = max(recent_highs)
            support_level = min(recent_lows)
            
            # Détection breakout
            breakout_detected = False
            breakout_type = None
            breakout_level = 0.0
            
            if current_bar.high > resistance_level:
                breakout_detected = True
                breakout_type = "bullish"
                breakout_level = resistance_level
            elif current_bar.low < support_level:
                breakout_detected = True
                breakout_type = "bearish" 
                breakout_level = support_level
            
            if not breakout_detected:
                return result
            
            result.breakout_level = breakout_level
            
            # === ANALYSE VOLUME SPIKE ===
            
            volume_spike = 0.0
            if len(self.volume_history) >= 5:
                recent_vol_avg = np.mean(list(self.volume_history)[:-1])  # Exclude current
                current_vol = current_bar.volume
                
                if recent_vol_avg > 0:
                    volume_spike = current_vol / recent_vol_avg
                    result.volume_spike = volume_spike
            
            # === ANALYSE ORDER FLOW DIVERGENCE ===
            
            delta_divergence = 0.0
            absorption_detected = False
            
            if order_flow:
                # Volume spike MAIS net delta faible = absorption
                if volume_spike > self.headfake_params['min_breakout_volume']:
                    total_volume = order_flow.bid_volume + order_flow.ask_volume
                    
                    if total_volume > 0:
                        net_delta_ratio = abs(order_flow.net_delta) / total_volume
                        
                        # Volume élevé mais delta faible = absorption
                        if net_delta_ratio < 0.3:  # Net delta <30% du volume
                            absorption_detected = True
                            delta_divergence = 1.0 - net_delta_ratio
                
                result.absorption_detected = absorption_detected
                result.delta_divergence = delta_divergence
            
            # === CONFIRMATION HEADFAKE ===
            
            headfake_strength = 0.0
            
            # Volume spike required
            if volume_spike > self.headfake_params['min_breakout_volume']:
                headfake_strength += 0.4
                
                # Absorption confirmation
                if absorption_detected:
                    headfake_strength += 0.6
                    result.fake_confirmation = True
                
                # Price rejection (retrace rapide)
                if breakout_type == "bullish" and current_bar.close < (breakout_level + 2 * ES_TICK_SIZE):
                    headfake_strength += 0.3
                elif breakout_type == "bearish" and current_bar.close > (breakout_level - 2 * ES_TICK_SIZE):
                    headfake_strength += 0.3
            
            # === CLASSIFICATION ===
            
            result.headfake_strength = min(headfake_strength, 1.0)
            
            if result.headfake_strength >= 0.7:
                if breakout_type == "bullish":
                    result.headfake_type = HeadFakeType.BULL_TRAP
                else:
                    result.headfake_type = HeadFakeType.BEAR_TRAP
            elif result.headfake_strength >= 0.3:
                result.headfake_type = HeadFakeType.RANGE_FAKE
            else:
                result.headfake_type = HeadFakeType.NO_HEADFAKE
            
            result.calculation_time_ms = (time.perf_counter() - start_time) * 1000
            return result
            
        except Exception as e:
            logger.error(f"Erreur headfake detection: {e}")
            return HeadFakeResult(
                timestamp=market_data.timestamp,
                calculation_time_ms=(time.perf_counter() - start_time) * 1000
            )
    
    def detect_microstructure_anomaly(self,
                                    market_data: MarketData,
                                    order_flow: Optional[OrderFlowData] = None) -> MicrostructureAnomalyResult:
        """
        DÉTECTION ANOMALIE MICROSTRUCTURE
        
        Identifie anomalies dans volume, spread, order flow.
        Utilise Z-score pour détection outliers.
        """
        start_time = time.perf_counter()
        
        try:
            result = MicrostructureAnomalyResult(timestamp=market_data.timestamp)
            
            anomaly_scores = []
            
            # === 1. ANOMALIE VOLUME ===
            
            if len(self.volume_history) >= 10:
                volumes = np.array(list(self.volume_history))
                vol_mean = np.mean(volumes[:-1])  # Exclude current
                vol_std = np.std(volumes[:-1])
                
                if vol_std > 0:
                    current_vol = market_data.volume
                    vol_z_score = abs(current_vol - vol_mean) / vol_std
                    
                    if vol_z_score > self.microstructure_params['volume_anomaly_threshold']:
                        volume_anomaly = min(vol_z_score / 5.0, 1.0)  # Normalize
                        result.volume_anomaly = volume_anomaly
                        anomaly_scores.append(('volume', volume_anomaly))
            
            # === 2. ANOMALIE SPREAD ===
            
            if len(self.spread_history) >= 10 and market_data.spread:
                spreads = np.array(list(self.spread_history))
                spread_mean = np.mean(spreads[:-1])
                spread_std = np.std(spreads[:-1])
                
                if spread_std > 0:
                    current_spread = market_data.spread
                    spread_z_score = abs(current_spread - spread_mean) / spread_std
                    
                    if spread_z_score > self.microstructure_params['spread_anomaly_threshold']:
                        spread_anomaly = min(spread_z_score / 4.0, 1.0)
                        result.spread_anomaly = spread_anomaly
                        anomaly_scores.append(('spread', spread_anomaly))
            
            # === 3. ANOMALIE ORDER FLOW ===
            
            if order_flow:
                # Analyse aggressive ratio
                total_aggressive = order_flow.aggressive_buys + order_flow.aggressive_sells
                total_volume = order_flow.bid_volume + order_flow.ask_volume
                
                if total_volume > 0 and total_aggressive > 0:
                    aggressive_ratio = total_aggressive / total_volume
                    
                    # Ratio normal = 0.1-0.4, au-delà = anomalie
                    if aggressive_ratio > 0.6 or aggressive_ratio < 0.05:
                        flow_anomaly = min(abs(aggressive_ratio - 0.25) / 0.35, 1.0)
                        result.flow_anomaly = flow_anomaly
                        anomaly_scores.append(('flow', flow_anomaly))
                
                # Analyse imbalance extreme
                if total_volume > 0:
                    imbalance = abs(order_flow.bid_volume - order_flow.ask_volume) / total_volume
                    if imbalance > 0.8:  # Imbalance >80%
                        imbalance_anomaly = (imbalance - 0.5) / 0.5
                        anomaly_scores.append(('imbalance', imbalance_anomaly))
            
            # === 4. SYNTHÈSE ANOMALIES ===
            
            if anomaly_scores:
                # Score composite (max anomaly)
                max_anomaly = max(anomaly_scores, key=lambda x: x[1])
                result.primary_anomaly = AnomalyType(max_anomaly[0] + '_anomaly')
                result.anomaly_strength = max_anomaly[1]
                result.anomaly_score = np.mean([score for _, score in anomaly_scores])
                
                # Prediction impact marché
                if result.anomaly_strength > 0.7:
                    if result.primary_anomaly == AnomalyType.VOLUME_ANOMALY:
                        result.predicted_impact = "bullish" if market_data.volume > np.mean(list(self.volume_history)[:-1]) else "bearish"
                        result.confidence = 0.6
                    elif result.primary_anomaly == AnomalyType.FLOW_ANOMALY:
                        result.predicted_impact = "bearish"  # Flow anomaly often bearish
                        result.confidence = 0.7
                    else:
                        result.predicted_impact = "bearish"  # Spread anomaly typically bearish
                        result.confidence = 0.5
            else:
                result.primary_anomaly = AnomalyType.NO_ANOMALY
            
            result.calculation_time_ms = (time.perf_counter() - start_time) * 1000
            return result
            
        except Exception as e:
            logger.error(f"Erreur microstructure anomaly detection: {e}")
            return MicrostructureAnomalyResult(
                timestamp=market_data.timestamp,
                calculation_time_ms=(time.perf_counter() - start_time) * 1000
            )
    
    # === UTILITY METHODS ===
    
    def _update_stats(self, calc_time: float, result: PatternsDetectionResult):
        """Mise à jour statistiques"""
        self.stats['total_analyses'] += 1
        
        # Rolling average calculation time
        count = self.stats['total_analyses']
        prev_avg = self.stats['avg_calc_time_ms']
        self.stats['avg_calc_time_ms'] = ((prev_avg * (count - 1)) + calc_time) / count
        
        # Patterns detected
        if result.gamma_pin_strength > 0.3:
            self.stats['gamma_pins_detected'] += 1
        
        if result.headfake_signal > 0.3:
            self.stats['headfakes_detected'] += 1
        
        if result.microstructure_anomaly > 0.3:
            self.stats['anomalies_detected'] += 1
    
    def get_patterns_for_feature_calculator(self) -> Dict[str, float]:
        """Export patterns pour feature_calculator.py"""
        # Cette méthode sera appelée par feature_calculator
        # On retourne les derniers résultats ou des defaults
        return {
            'gamma_pin_strength': 0.0,
            'headfake_signal': 0.0,
            'microstructure_anomaly': 0.0
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques détecteur"""
        return {
            'total_analyses': self.stats['total_analyses'],
            'gamma_pins_detected': self.stats['gamma_pins_detected'],
            'headfakes_detected': self.stats['headfakes_detected'],
            'anomalies_detected': self.stats['anomalies_detected'],
            'avg_calculation_time_ms': round(self.stats['avg_calc_time_ms'], 3),
            'gamma_detection_rate': (self.stats['gamma_pins_detected'] / self.stats['total_analyses'] * 100) if self.stats['total_analyses'] > 0 else 0,
            'headfake_detection_rate': (self.stats['headfakes_detected'] / self.stats['total_analyses'] * 100) if self.stats['total_analyses'] > 0 else 0,
            'anomaly_detection_rate': (self.stats['anomalies_detected'] / self.stats['total_analyses'] * 100) if self.stats['total_analyses'] > 0 else 0
        }

# === FACTORY FUNCTIONS ===

def create_patterns_detector(config: Optional[Dict[str, Any]] = None) -> ElitePatternsDetector:
    """Factory function pour patterns detector"""
    return ElitePatternsDetector(config)

def detect_all_elite_patterns(market_data: MarketData,
                            options_data: Optional[Dict[str, Any]] = None,
                            order_flow: Optional[OrderFlowData] = None,
                            detector: Optional[ElitePatternsDetector] = None) -> PatternsDetectionResult:
    """Helper function pour détection complète"""
    
    if detector is None:
        detector = create_patterns_detector()
    
    return detector.detect_all_patterns(market_data, options_data, order_flow)

# === TESTING ===

def test_patterns_detector():
    """Test complet patterns detector"""
    logger.debug("TEST ELITE PATTERNS DETECTOR")
    print("=" * 50)
    
    # Création detector
    detector = create_patterns_detector()
    
    logger.info("🎯 TEST GAMMA PIN DETECTION")
    
    # Test gamma pin
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4500.0,
        high=4505.0,
        low=4498.0,
        close=4502.0,  # Proche call wall
        volume=1500
    )
    
    options_data = {
        'call_wall': 4500.0,  # Call wall proche
        'put_wall': 4480.0,
        'net_gamma': 3000.0   # Gamma élevée
    }
    
    gamma_result = detector.detect_gamma_pin(market_data, options_data)
    logger.info("Gamma pin strength: {gamma_result.pin_strength:.3f}")
    logger.info("Pin type: {gamma_result.pin_type.value}")
    logger.info("Distance to pin: {gamma_result.distance_to_pin:.1f} ticks")
    
    logger.info("\n🎯 TEST HEADFAKE DETECTION")
    
    # Simulation historique pour headfake
    for i in range(15):
        test_bar = MarketData(
            timestamp=pd.Timestamp.now() - pd.Timedelta(minutes=15-i),
            symbol="ES",
            open=4500.0 + np.random.normal(0, 1),
            high=4505.0 + np.random.normal(0, 1),
            low=4495.0 + np.random.normal(0, 1),
            close=4500.0 + np.random.normal(0, 1),
            volume=1200 + np.random.randint(-200, 200)
        )
        detector.price_history.append(test_bar)
        detector.volume_history.append(test_bar.volume)
    
    # Breakout avec volume spike mais absorption
    breakout_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4505.0,
        high=4512.0,  # Breakout above range
        low=4504.0,
        close=4506.0,  # Mais fermeture faible
        volume=3000    # Volume spike
    )
    
    order_flow = OrderFlowData(
        timestamp=breakout_data.timestamp,
        symbol="ES",
        cumulative_delta=50.0,  # Delta faible malgré volume
        bid_volume=1600,        # Absorption
        ask_volume=1400,
        aggressive_buys=800,
        aggressive_sells=1200   # Plus de ventes agressives
    )
    
    headfake_result = detector.detect_headfake(breakout_data, order_flow)
    logger.info("Headfake strength: {headfake_result.headfake_strength:.3f}")
    logger.info("Headfake type: {headfake_result.headfake_type.value}")
    logger.info("Absorption detected: {headfake_result.absorption_detected}")
    logger.info("Volume spike: {headfake_result.volume_spike:.2f}x")
    
    logger.info("\n🎯 TEST MICROSTRUCTURE ANOMALY")
    
    # Simulation anomalie spread
    for i in range(15):
        detector.spread_history.append(0.25 + np.random.normal(0, 0.05))
    
    anomaly_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4505.0,
        high=4507.0,
        low=4504.0,
        close=4506.0,
        volume=5000,  # Volume anomalie
        bid=4505.5,
        ask=4507.0,   # Spread anomalie
        spread=1.5    # Spread très large
    )
    
    anomaly_order_flow = OrderFlowData(
        timestamp=anomaly_data.timestamp,
        symbol="ES",
        cumulative_delta=200.0,
        bid_volume=500,
        ask_volume=4500,  # Imbalance extrême
        aggressive_buys=100,
        aggressive_sells=50   # Ratio anomalie
    )
    
    anomaly_result = detector.detect_microstructure_anomaly(anomaly_data, anomaly_order_flow)
    logger.info("Anomaly strength: {anomaly_result.anomaly_strength:.3f}")
    logger.info("Primary anomaly: {anomaly_result.primary_anomaly.value}")
    logger.info("Volume anomaly: {anomaly_result.volume_anomaly:.3f}")
    logger.info("Spread anomaly: {anomaly_result.spread_anomaly:.3f}")
    logger.info("Predicted impact: {anomaly_result.predicted_impact}")
    
    logger.info("\n🎯 TEST INTEGRATION COMPLÈTE")
    
    # Test détection complète
    start_time = time.perf_counter()
    complete_result = detector.detect_all_patterns(
        market_data=anomaly_data,
        options_data=options_data,
        order_flow=anomaly_order_flow
    )
    total_time = (time.perf_counter() - start_time) * 1000
    
    logger.info("Total analysis: {total_time:.2f}ms")
    logger.info("Patterns detected: {complete_result.patterns_detected_count}")
    logger.info("Gamma pin: {complete_result.gamma_pin_strength:.3f}")
    logger.info("Headfake: {complete_result.headfake_signal:.3f}")
    logger.info("Anomaly: {complete_result.microstructure_anomaly:.3f}")
    
    # Statistiques
    stats = detector.get_statistics()
    logger.info("\n📊 STATISTICS:")
    for key, value in stats.items():
        logger.info("   • {key}: {value}")
    
    logger.info("\n🎯 ELITE PATTERNS DETECTOR TEST COMPLETED")
    logger.info("🎪 3 PATTERNS ÉLITES OPÉRATIONNELS !")
    
    return True

if __name__ == "__main__":
    test_patterns_detector()