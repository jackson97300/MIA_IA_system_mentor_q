#!/usr/bin/env python3
"""
🎯 SIERRA PATTERNS COMPLETE INTEGRATOR
Intégration COMPLÈTE de TOUS les patterns existants :
1. GAMMA PIN - Zones où gamma options influence price action
2. HEADFAKE - Faux breakouts avec absorption order flow  
3. MICROSTRUCTURE ANOMALY - Anomalies détectées dans structure marché
4. BATTLE NAVALE - Patterns existants optimisés
5. SIERRA CHART - Patterns tick reversal optimisés
"""

import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from collections import deque

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger
from core.base_types import MarketData, OrderFlowData
from core.battle_navale import BattleNavaleDetector, create_battle_navale_detector
from execution.sierra_battle_navale_integrator import (
    SierraBattleNavaleIntegrator,
    IntegratedSignal,
    IntegrationConfig,
    SignalQuality
)

# Imports patterns spécialisés
try:
    from features.volume_profile_imbalance import VolumeProfileImbalanceDetector
    from features.dealers_bias_analyzer import DealersBiasAnalyzer
    from features.create_options_snapshot import _compute_gamma_pins
    VPI_AVAILABLE = True
except ImportError:
    VPI_AVAILABLE = False

logger = get_logger(__name__)

class PatternCategory(Enum):
    """Catégories de patterns"""
    GAMMA_PATTERNS = "gamma_patterns"               # Patterns Gamma/Options
    MICROSTRUCTURE = "microstructure"               # Anomalies microstructure  
    ORDERFLOW_PATTERNS = "orderflow_patterns"       # Patterns OrderFlow
    BATTLE_NAVALE = "battle_navale"                 # Battle Navale core
    SIERRA_CHART = "sierra_chart"                   # Sierra Chart patterns
    HEADFAKE_DETECTION = "headfake_detection"       # Détection HeadFake

@dataclass
class GammaPinSignal:
    """Signal Gamma Pin détecté"""
    timestamp: pd.Timestamp
    strike_level: float
    gamma_exposure: float
    distance_from_current: float
    strength: float
    pin_type: str                    # "Strong", "Medium", "Weak"
    attraction_score: float          # 0.0-1.0 force d'attraction

@dataclass
class HeadFakeSignal:
    """Signal HeadFake détecté"""
    timestamp: pd.Timestamp
    breakout_level: float
    fake_direction: str              # "LONG_FAKE", "SHORT_FAKE"
    absorption_volume: int
    reversal_strength: float         # 0.0-1.0
    confidence: float                # 0.0-1.0

@dataclass
class MicrostructureAnomalySignal:
    """Signal anomalie microstructure"""
    timestamp: pd.Timestamp
    anomaly_type: str                # "VOLUME_SPIKE", "SPREAD_ANOMALY", "TICK_IMBALANCE"
    severity: float                  # 0.0-1.0
    expected_impact: str             # "BULLISH", "BEARISH", "NEUTRAL"
    confidence: float                # 0.0-1.0

@dataclass
class CompletePatternSignal:
    """Signal complet intégrant TOUS les patterns"""
    
    # Informations de base
    timestamp: pd.Timestamp
    symbol: str
    price_level: float
    
    # Signaux composants
    battle_navale_score: float       # Score Battle Navale
    sierra_patterns_score: float     # Score Sierra patterns
    gamma_pin_score: float          # Score Gamma pins
    headfake_score: float           # Score HeadFake detection
    microstructure_score: float     # Score anomalies microstructure
    
    # Score final et direction
    integrated_score: float          # Score intégré final 0.0-1.0
    signal_direction: str            # "LONG", "SHORT", "NEUTRAL"
    signal_quality: SignalQuality
    confidence: float                # 0.0-1.0
    
    # Signaux détaillés
    gamma_pins: List[GammaPinSignal] = field(default_factory=list)
    headfake_signals: List[HeadFakeSignal] = field(default_factory=list)
    microstructure_anomalies: List[MicrostructureAnomalySignal] = field(default_factory=list)
    
    # Métadonnées
    pattern_categories_active: List[PatternCategory] = field(default_factory=list)
    confluence_strength: float = 0.0
    reasoning: str = ""

@dataclass
class CompleteIntegrationConfig:
    """Configuration intégration complète"""
    
    # Pondérations patterns (doivent sommer à 1.0)
    battle_navale_weight: float = 0.30      # 30% - Battle Navale core
    sierra_patterns_weight: float = 0.25    # 25% - Sierra patterns
    gamma_pins_weight: float = 0.20         # 20% - Gamma pins
    headfake_weight: float = 0.15           # 15% - HeadFake detection
    microstructure_weight: float = 0.10     # 10% - Microstructure anomalies
    
    # Seuils patterns
    gamma_pin_min_strength: float = 1.5     # Force minimum gamma pin
    headfake_min_confidence: float = 0.65   # Confidence minimum HeadFake
    microstructure_min_severity: float = 0.7 # Sévérité minimum anomalie
    
    # Confluence  
    min_active_categories: int = 3          # Minimum 3 catégories actives
    confluence_bonus: float = 0.20          # +20% bonus confluence
    
    # Performance
    analysis_interval_ms: int = 500         # 500ms entre analyses
    gamma_analysis_enabled: bool = True     # Analyse gamma pins
    headfake_detection_enabled: bool = True # Détection HeadFake
    microstructure_enabled: bool = True     # Analyse microstructure

class SierraPatternsCompleteIntegrator:
    """
    Intégrateur COMPLET de tous les patterns :
    - Battle Navale (existant)
    - Sierra Chart patterns (existant)  
    - Gamma Pins (options influence)
    - HeadFake detection (faux breakouts)
    - Microstructure anomalies (structure marché)
    """
    
    def __init__(self, config: Optional[CompleteIntegrationConfig] = None):
        self.config = config or CompleteIntegrationConfig()
        
        # Intégrateur de base (Battle Navale + Sierra)
        base_integration_config = IntegrationConfig()
        base_integration_config.analysis_interval_ms = self.config.analysis_interval_ms
        self.base_integrator = SierraBattleNavaleIntegrator(base_integration_config)
        
        # Analyseurs spécialisés
        if VPI_AVAILABLE:
            self.volume_profile_detector = VolumeProfileImbalanceDetector()
        else:
            self.volume_profile_detector = None
            logger.warning("⚠️ VolumeProfileImbalanceDetector non disponible")
        
        # Historique et cache
        self.market_data_history: deque = deque(maxlen=100)
        self.options_data_history: deque = deque(maxlen=50)
        self.complete_signals_history: deque = deque(maxlen=50)
        
        # Statistiques
        self.stats = {
            'total_complete_signals': 0,
            'gamma_pins_detected': 0,
            'headfakes_detected': 0,
            'microstructure_anomalies': 0,
            'confluence_signals': 0,
            'avg_analysis_time_ms': 0.0
        }
        
        logger.info("🎯 Sierra Patterns Complete Integrator initialisé")
    
    async def analyze_complete_patterns(self,
                                      market_data: MarketData,
                                      orderflow_data: Optional[OrderFlowData] = None,
                                      options_data: Optional[Dict] = None,
                                      volume_profile: Optional[Dict] = None) -> Optional[CompletePatternSignal]:
        """Analyse complète de TOUS les patterns"""
        
        start_time = time.perf_counter()
        
        # Ajouter données à l'historique
        self.market_data_history.append(market_data)
        if options_data:
            self.options_data_history.append(options_data)
        
        if len(self.market_data_history) < 5:
            return None
        
        try:
            # 1. Analyse de base (Battle Navale + Sierra)
            base_signal = await self.base_integrator.analyze_integrated_signals(
                market_data, orderflow_data, volume_profile
            )
            
            # 2. Analyse Gamma Pins
            gamma_score, gamma_pins = await self._analyze_gamma_pins(market_data, options_data)
            
            # 3. Analyse HeadFake
            headfake_score, headfake_signals = await self._analyze_headfake_patterns(market_data, orderflow_data)
            
            # 4. Analyse Microstructure
            microstructure_score, microstructure_anomalies = await self._analyze_microstructure_anomalies(
                market_data, orderflow_data
            )
            
            # 5. Intégration complète
            complete_signal = self._integrate_complete_patterns(
                market_data,
                base_signal,
                gamma_score, gamma_pins,
                headfake_score, headfake_signals,
                microstructure_score, microstructure_anomalies
            )
            
            if complete_signal:
                # Ajouter à l'historique
                self.complete_signals_history.append(complete_signal)
                
                # Mise à jour statistiques
                analysis_time = (time.perf_counter() - start_time) * 1000
                self._update_stats(complete_signal, analysis_time)
                
                logger.info(f"🎯 Signal complet: {complete_signal.signal_quality.value} - Score {complete_signal.integrated_score:.3f}")
                
                return complete_signal
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse complète: {e}")
            return None
    
    async def _analyze_gamma_pins(self, 
                                market_data: MarketData,
                                options_data: Optional[Dict] = None) -> Tuple[float, List[GammaPinSignal]]:
        """Analyse Gamma Pins - Zones où gamma options influence price action"""
        
        if not self.config.gamma_analysis_enabled or not options_data:
            return 0.0, []
        
        try:
            current_price = market_data.close
            
            # Récupérer options data
            options_list = options_data.get('options', [])
            if not options_list:
                return 0.0, []
            
            # Calculer gamma pins
            gamma_pins_raw = _compute_gamma_pins(options_list, current_price, 100, top_n=5)
            
            gamma_pins = []
            total_attraction = 0.0
            
            for pin_data in gamma_pins_raw:
                strength = pin_data.get('strength', 0.0)
                
                if strength >= self.config.gamma_pin_min_strength:
                    # Calculer attraction score
                    distance = abs(pin_data.get('distance_from_current', 0.0))
                    attraction = strength / max(1.0, distance / 10.0)  # Décroît avec distance
                    
                    gamma_pin = GammaPinSignal(
                        timestamp=market_data.timestamp,
                        strike_level=pin_data.get('strike', 0.0),
                        gamma_exposure=pin_data.get('gamma_exposure', 0.0),
                        distance_from_current=pin_data.get('distance_from_current', 0.0),
                        strength=strength,
                        pin_type=pin_data.get('strength_category', 'Medium'),
                        attraction_score=min(1.0, attraction)
                    )
                    
                    gamma_pins.append(gamma_pin)
                    total_attraction += attraction
            
            # Score basé sur attraction totale
            gamma_score = min(1.0, total_attraction / 3.0)  # Normaliser
            
            return gamma_score, gamma_pins
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse gamma pins: {e}")
            return 0.0, []
    
    async def _analyze_headfake_patterns(self,
                                       market_data: MarketData,
                                       orderflow_data: Optional[OrderFlowData] = None) -> Tuple[float, List[HeadFakeSignal]]:
        """Analyse HeadFake - Faux breakouts avec absorption order flow"""
        
        if not self.config.headfake_detection_enabled or len(self.market_data_history) < 10:
            return 0.0, []
        
        try:
            headfake_signals = []
            
            # Récupérer données récentes
            recent_data = list(self.market_data_history)[-10:]
            current_price = market_data.close
            
            # Détecter niveaux clés (support/résistance)
            highs = [d.high for d in recent_data]
            lows = [d.low for d in recent_data]
            
            resistance_level = max(highs)
            support_level = min(lows)
            
            # Détecter tentative breakout
            fake_breakout_detected = False
            fake_direction = ""
            absorption_volume = 0
            
            # Breakout au-dessus de résistance puis retour
            if (current_price < resistance_level and 
                market_data.high > resistance_level and
                len(recent_data) >= 3):
                
                # Vérifier si volume d'absorption (vente importante)
                if orderflow_data and orderflow_data.aggressive_sells > orderflow_data.aggressive_buys * 1.5:
                    fake_breakout_detected = True
                    fake_direction = "LONG_FAKE"
                    absorption_volume = orderflow_data.aggressive_sells
            
            # Breakout en-dessous de support puis retour
            elif (current_price > support_level and 
                  market_data.low < support_level and
                  len(recent_data) >= 3):
                
                # Vérifier si volume d'absorption (achat important)
                if orderflow_data and orderflow_data.aggressive_buys > orderflow_data.aggressive_sells * 1.5:
                    fake_breakout_detected = True
                    fake_direction = "SHORT_FAKE"
                    absorption_volume = orderflow_data.aggressive_buys
            
            if fake_breakout_detected:
                # Calculer force reversal
                price_rejection = 0.0
                if fake_direction == "LONG_FAKE":
                    price_rejection = (resistance_level - current_price) / resistance_level
                else:
                    price_rejection = (current_price - support_level) / support_level
                
                reversal_strength = min(1.0, abs(price_rejection) * 10)  # Amplifier signal
                
                # Confidence basée sur volume et rejection
                volume_ratio = absorption_volume / max(market_data.volume, 1)
                confidence = min(1.0, (reversal_strength + volume_ratio) / 2.0)
                
                if confidence >= self.config.headfake_min_confidence:
                    headfake_signal = HeadFakeSignal(
                        timestamp=market_data.timestamp,
                        breakout_level=resistance_level if fake_direction == "LONG_FAKE" else support_level,
                        fake_direction=fake_direction,
                        absorption_volume=absorption_volume,
                        reversal_strength=reversal_strength,
                        confidence=confidence
                    )
                    
                    headfake_signals.append(headfake_signal)
            
            # Score HeadFake
            headfake_score = 0.0
            if headfake_signals:
                avg_confidence = np.mean([h.confidence for h in headfake_signals])
                headfake_score = avg_confidence
            
            return headfake_score, headfake_signals
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse HeadFake: {e}")
            return 0.0, []
    
    async def _analyze_microstructure_anomalies(self,
                                              market_data: MarketData,
                                              orderflow_data: Optional[OrderFlowData] = None) -> Tuple[float, List[MicrostructureAnomalySignal]]:
        """Analyse Microstructure Anomalies - Anomalies dans structure marché"""
        
        if not self.config.microstructure_enabled or len(self.market_data_history) < 5:
            return 0.0, []
        
        try:
            anomalies = []
            
            # Récupérer données récentes pour comparaison
            recent_data = list(self.market_data_history)[-5:]
            avg_volume = np.mean([d.volume for d in recent_data])
            avg_range = np.mean([d.high - d.low for d in recent_data])
            
            # 1. Détection Volume Spike
            current_volume = market_data.volume
            volume_ratio = current_volume / max(avg_volume, 1)
            
            if volume_ratio > 2.0:  # Volume 2x supérieur à la moyenne
                severity = min(1.0, volume_ratio / 5.0)  # Normaliser
                
                # Déterminer impact probable
                if orderflow_data:
                    if orderflow_data.aggressive_buys > orderflow_data.aggressive_sells * 1.2:
                        expected_impact = "BULLISH"
                    elif orderflow_data.aggressive_sells > orderflow_data.aggressive_buys * 1.2:
                        expected_impact = "BEARISH"
                    else:
                        expected_impact = "NEUTRAL"
                else:
                    expected_impact = "NEUTRAL"
                
                anomaly = MicrostructureAnomalySignal(
                    timestamp=market_data.timestamp,
                    anomaly_type="VOLUME_SPIKE",
                    severity=severity,
                    expected_impact=expected_impact,
                    confidence=min(1.0, severity)
                )
                
                if severity >= self.config.microstructure_min_severity:
                    anomalies.append(anomaly)
            
            # 2. Détection Spread Anomaly
            current_range = market_data.high - market_data.low
            range_ratio = current_range / max(avg_range, 0.01)
            
            if range_ratio > 3.0 or range_ratio < 0.3:  # Range anormalement large ou étroit
                severity = min(1.0, abs(np.log(range_ratio)))
                
                expected_impact = "NEUTRAL"  # Spread anomaly = incertitude
                if range_ratio > 3.0:
                    expected_impact = "VOLATILE"
                
                anomaly = MicrostructureAnomalySignal(
                    timestamp=market_data.timestamp,
                    anomaly_type="SPREAD_ANOMALY",
                    severity=severity,
                    expected_impact=expected_impact,
                    confidence=min(1.0, severity * 0.8)  # Moins confiant que volume
                )
                
                if severity >= self.config.microstructure_min_severity:
                    anomalies.append(anomaly)
            
            # 3. Détection Tick Imbalance
            if orderflow_data:
                total_aggressive = orderflow_data.aggressive_buys + orderflow_data.aggressive_sells
                if total_aggressive > 0:
                    imbalance_ratio = abs(orderflow_data.aggressive_buys - orderflow_data.aggressive_sells) / total_aggressive
                    
                    if imbalance_ratio > 0.7:  # 70% imbalance
                        severity = imbalance_ratio
                        expected_impact = "BULLISH" if orderflow_data.aggressive_buys > orderflow_data.aggressive_sells else "BEARISH"
                        
                        anomaly = MicrostructureAnomalySignal(
                            timestamp=market_data.timestamp,
                            anomaly_type="TICK_IMBALANCE",
                            severity=severity,
                            expected_impact=expected_impact,
                            confidence=severity
                        )
                        
                        if severity >= self.config.microstructure_min_severity:
                            anomalies.append(anomaly)
            
            # Score microstructure
            microstructure_score = 0.0
            if anomalies:
                avg_severity = np.mean([a.severity for a in anomalies])
                microstructure_score = avg_severity
            
            return microstructure_score, anomalies
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse microstructure: {e}")
            return 0.0, []
    
    def _integrate_complete_patterns(self,
                                   market_data: MarketData,
                                   base_signal: Optional[IntegratedSignal],
                                   gamma_score: float, gamma_pins: List[GammaPinSignal],
                                   headfake_score: float, headfake_signals: List[HeadFakeSignal],
                                   microstructure_score: float, microstructure_anomalies: List[MicrostructureAnomalySignal]) -> Optional[CompletePatternSignal]:
        """Intègre tous les patterns en signal final"""
        
        # Scores de base
        battle_navale_score = base_signal.battle_navale_score if base_signal else 0.0
        sierra_patterns_score = base_signal.sierra_patterns_score if base_signal else 0.0
        
        # Calcul score pondéré
        weighted_score = (
            battle_navale_score * self.config.battle_navale_weight +
            sierra_patterns_score * self.config.sierra_patterns_weight +
            gamma_score * self.config.gamma_pins_weight +
            headfake_score * self.config.headfake_weight +
            microstructure_score * self.config.microstructure_weight
        )
        
        # Compter catégories actives
        active_categories = []
        if battle_navale_score > 0.5:
            active_categories.append(PatternCategory.BATTLE_NAVALE)
        if sierra_patterns_score > 0.5:
            active_categories.append(PatternCategory.SIERRA_CHART)
        if gamma_score > 0.3:
            active_categories.append(PatternCategory.GAMMA_PATTERNS)
        if headfake_score > 0.5:
            active_categories.append(PatternCategory.HEADFAKE_DETECTION)
        if microstructure_score > 0.5:
            active_categories.append(PatternCategory.MICROSTRUCTURE)
        
        # Vérifier confluence minimum
        if len(active_categories) < self.config.min_active_categories:
            return None
        
        # Bonus confluence
        if len(active_categories) >= 4:
            weighted_score += self.config.confluence_bonus
        
        # Normaliser score final
        final_score = max(0.0, min(1.0, weighted_score))
        
        # Déterminer direction signal
        signal_direction = self._determine_complete_signal_direction(
            base_signal, gamma_pins, headfake_signals, microstructure_anomalies
        )
        
        # Qualité signal
        if final_score >= 0.95:
            signal_quality = SignalQuality.ELITE
        elif final_score >= 0.85:
            signal_quality = SignalQuality.PREMIUM
        elif final_score >= 0.75:
            signal_quality = SignalQuality.STRONG
        elif final_score >= 0.65:
            signal_quality = SignalQuality.GOOD
        else:
            signal_quality = SignalQuality.WEAK
        
        # Confluence strength
        confluence_strength = len(active_categories) / 5.0  # Normaliser
        
        # Reasoning
        reasoning = self._generate_complete_reasoning(
            battle_navale_score, sierra_patterns_score, gamma_score,
            headfake_score, microstructure_score, active_categories
        )
        
        return CompletePatternSignal(
            timestamp=market_data.timestamp,
            symbol=market_data.symbol,
            price_level=market_data.close,
            battle_navale_score=battle_navale_score,
            sierra_patterns_score=sierra_patterns_score,
            gamma_pin_score=gamma_score,
            headfake_score=headfake_score,
            microstructure_score=microstructure_score,
            gamma_pins=gamma_pins,
            headfake_signals=headfake_signals,
            microstructure_anomalies=microstructure_anomalies,
            integrated_score=final_score,
            signal_direction=signal_direction,
            signal_quality=signal_quality,
            confidence=final_score,
            pattern_categories_active=active_categories,
            confluence_strength=confluence_strength,
            reasoning=reasoning
        )
    
    def _determine_complete_signal_direction(self,
                                           base_signal: Optional[IntegratedSignal],
                                           gamma_pins: List[GammaPinSignal],
                                           headfake_signals: List[HeadFakeSignal],
                                           microstructure_anomalies: List[MicrostructureAnomalySignal]) -> str:
        """Détermine direction signal final"""
        
        bullish_indicators = 0
        bearish_indicators = 0
        
        # Signal de base
        if base_signal:
            if base_signal.signal_direction == "LONG":
                bullish_indicators += 2  # Poids double
            elif base_signal.signal_direction == "SHORT":
                bearish_indicators += 2
        
        # HeadFake signals (inversés)
        for headfake in headfake_signals:
            if headfake.fake_direction == "LONG_FAKE":
                bearish_indicators += 1  # Fake long = bearish
            elif headfake.fake_direction == "SHORT_FAKE":
                bullish_indicators += 1  # Fake short = bullish
        
        # Microstructure anomalies
        for anomaly in microstructure_anomalies:
            if anomaly.expected_impact == "BULLISH":
                bullish_indicators += 1
            elif anomaly.expected_impact == "BEARISH":
                bearish_indicators += 1
        
        # Déterminer direction
        if bullish_indicators > bearish_indicators:
            return "LONG"
        elif bearish_indicators > bullish_indicators:
            return "SHORT"
        else:
            return "NEUTRAL"
    
    def _generate_complete_reasoning(self,
                                   battle_score: float,
                                   sierra_score: float,
                                   gamma_score: float,
                                   headfake_score: float,
                                   microstructure_score: float,
                                   active_categories: List[PatternCategory]) -> str:
        """Génère explication complète du signal"""
        
        reasoning_parts = []
        
        # Confluence
        reasoning_parts.append(f"🎯 Confluence: {len(active_categories)} patterns actifs")
        
        # Patterns actifs
        if battle_score > 0.5:
            reasoning_parts.append(f"⚔️ Battle Navale ({battle_score:.2f})")
        
        if sierra_score > 0.5:
            reasoning_parts.append(f"📊 Sierra Chart ({sierra_score:.2f})")
        
        if gamma_score > 0.3:
            reasoning_parts.append(f"🎯 Gamma Pins ({gamma_score:.2f})")
        
        if headfake_score > 0.5:
            reasoning_parts.append(f"🎭 HeadFake ({headfake_score:.2f})")
        
        if microstructure_score > 0.5:
            reasoning_parts.append(f"🔬 Microstructure ({microstructure_score:.2f})")
        
        return " | ".join(reasoning_parts)
    
    def _update_stats(self, signal: CompletePatternSignal, analysis_time_ms: float):
        """Met à jour statistiques"""
        
        self.stats['total_complete_signals'] += 1
        
        if signal.gamma_pins:
            self.stats['gamma_pins_detected'] += len(signal.gamma_pins)
        
        if signal.headfake_signals:
            self.stats['headfakes_detected'] += len(signal.headfake_signals)
        
        if signal.microstructure_anomalies:
            self.stats['microstructure_anomalies'] += len(signal.microstructure_anomalies)
        
        if len(signal.pattern_categories_active) >= 4:
            self.stats['confluence_signals'] += 1
        
        # Moyenne mobile temps analyse
        current_avg = self.stats['avg_analysis_time_ms']
        self.stats['avg_analysis_time_ms'] = (current_avg * 0.9 + analysis_time_ms * 0.1)
    
    def get_complete_summary(self) -> Dict[str, Any]:
        """Résumé complet de l'intégration"""
        
        return {
            'total_signals': self.stats['total_complete_signals'],
            'gamma_pins_detected': self.stats['gamma_pins_detected'],
            'headfakes_detected': self.stats['headfakes_detected'],
            'microstructure_anomalies': self.stats['microstructure_anomalies'],
            'confluence_signals': self.stats['confluence_signals'],
            'avg_analysis_time_ms': self.stats['avg_analysis_time_ms'],
            'patterns_available': {
                'battle_navale': True,
                'sierra_chart': True,
                'gamma_pins': self.config.gamma_analysis_enabled,
                'headfake_detection': self.config.headfake_detection_enabled,
                'microstructure': self.config.microstructure_enabled,
                'volume_profile_imbalance': VPI_AVAILABLE
            }
        }
    
    def export_for_feature_calculator(self, signal: CompletePatternSignal) -> Dict[str, float]:
        """Export signal complet pour feature_calculator.py"""
        
        # Format compatible avec tous les patterns
        result = {
            # Patterns existants
            'battle_navale_signal': signal.battle_navale_score,
            'sierra_pattern_strength': signal.sierra_patterns_score,
            
            # Nouveaux patterns intégrés
            'gamma_pin_strength': signal.gamma_pin_score,
            'headfake_signal': signal.headfake_score,
            'microstructure_anomaly': signal.microstructure_score,
            
            # Scores intégrés
            'complete_pattern_score': signal.integrated_score,
            'confluence_strength': signal.confluence_strength,
            'pattern_categories_count': len(signal.pattern_categories_active),
            
            # Qualité et confidence
            'signal_quality_numeric': self._quality_to_numeric(signal.signal_quality),
            'pattern_confidence': signal.confidence
        }
        
        return result
    
    def _quality_to_numeric(self, quality: SignalQuality) -> float:
        """Convertit qualité en valeur numérique"""
        
        quality_map = {
            SignalQuality.ELITE: 1.0,
            SignalQuality.PREMIUM: 0.9,
            SignalQuality.STRONG: 0.8,
            SignalQuality.GOOD: 0.7,
            SignalQuality.WEAK: 0.6,
            SignalQuality.NO_SIGNAL: 0.0
        }
        
        return quality_map.get(quality, 0.0)

# Factory functions
def create_complete_integrator_production() -> SierraPatternsCompleteIntegrator:
    """Intégrateur complet pour production"""
    config = CompleteIntegrationConfig()
    config.min_active_categories = 3
    config.confluence_bonus = 0.15
    
    return SierraPatternsCompleteIntegrator(config)

def create_complete_integrator_development() -> SierraPatternsCompleteIntegrator:
    """Intégrateur complet pour développement"""
    config = CompleteIntegrationConfig()
    config.min_active_categories = 2         # Moins strict
    config.gamma_pin_min_strength = 1.2     # Seuils plus bas
    config.headfake_min_confidence = 0.55
    config.microstructure_min_severity = 0.6
    
    return SierraPatternsCompleteIntegrator(config)

# Export principal
__all__ = [
    'SierraPatternsCompleteIntegrator',
    'CompletePatternSignal',
    'CompleteIntegrationConfig',
    'GammaPinSignal',
    'HeadFakeSignal', 
    'MicrostructureAnomalySignal',
    'PatternCategory',
    'create_complete_integrator_production',
    'create_complete_integrator_development'
]
