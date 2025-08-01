#!/usr/bin/env python3
"""
🎯 CONFLUENCE CALCULATOR - MIA_IA_SYSTEM
Calcul de confluence optimisé et modulaire
"""

import sys
from pathlib import Path
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger

logger = get_logger(__name__)

class EnhancedConfluenceCalculator:
    """Calculateur de confluence optimisé"""
    
    def __init__(self):
        self.session_start = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
        self.last_calculation = None
        self.calculation_cache = {}
        
    def calculate_enhanced_confluence(self, market_data) -> float:
        """Calcul de confluence principal optimisé"""
        try:
            # Cache pour éviter recalculs
            cache_key = f"{market_data.price:.2f}_{market_data.volume}"
            if cache_key in self.calculation_cache:
                return self.calculation_cache[cache_key]
            
            # Composants de confluence
            gamma_levels = self._calculate_gamma_levels(market_data)
            vwap_trend = self._calculate_vwap_trend_signal(market_data)
            correlation = self._calculate_es_nq_correlation(market_data)
            level_proximity = self._calculate_level_proximity(market_data)
            session_context = self._calculate_session_context(market_data)
            pullback_quality = self._calculate_pullback_quality(market_data)
            sierra_patterns = self._calculate_sierra_pattern_strength(market_data)
            volume_confirmation = self._calculate_volume_confirmation(market_data)
            options_flow = self._calculate_options_flow(market_data)
            order_book = self._calculate_order_book_imbalance(market_data)
            tick_momentum = self._calculate_tick_momentum(market_data)
            delta_divergence = self._calculate_delta_divergence(market_data)
            smart_money = self._calculate_smart_money_index(market_data)
            mtf_confluence = self._calculate_mtf_confluence(market_data)
            
            # Pondération des composants
            confluence = (
                gamma_levels * 0.15 +
                vwap_trend * 0.12 +
                correlation * 0.10 +
                level_proximity * 0.10 +
                session_context * 0.08 +
                pullback_quality * 0.08 +
                sierra_patterns * 0.10 +
                volume_confirmation * 0.05 +
                options_flow * 0.05 +
                order_book * 0.03 +
                tick_momentum * 0.03 +
                delta_divergence * 0.03 +
                smart_money * 0.03 +
                mtf_confluence * 0.03
            )
            
            # Normalisation
            confluence = max(0.0, min(1.0, confluence))
            
            # Cache du résultat
            self.calculation_cache[cache_key] = confluence
            self.last_calculation = datetime.now()
            
            logger.debug(f"🎯 Confluence calculée: {confluence:.3f}")
            return confluence
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul confluence: {e}")
            return 0.5  # Valeur neutre en cas d'erreur
    
    def _calculate_gamma_levels(self, market_data) -> float:
        """Calcul des niveaux gamma"""
        try:
            # Simulation des niveaux gamma
            base_gamma = 0.025
            volatility_factor = random.uniform(0.8, 1.2)
            time_factor = self._get_gamma_expiration_factor()
            
            gamma_level = base_gamma * volatility_factor * time_factor
            return min(1.0, gamma_level * 10)  # Normalisation
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur gamma levels: {e}")
            return 0.5
    
    def _calculate_vwap_trend_signal(self, market_data) -> float:
        """Calcul signal tendance VWAP"""
        try:
            # Simulation VWAP
            vwap_price = market_data.price + random.uniform(-2.0, 2.0)
            price_vs_vwap = (market_data.price - vwap_price) / vwap_price
            
            return max(0.0, min(1.0, abs(price_vs_vwap) * 5))
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur VWAP trend: {e}")
            return 0.5
    
    def _calculate_es_nq_correlation(self, market_data) -> float:
        """Calcul corrélation ES/NQ"""
        try:
            # Simulation corrélation
            correlation = 0.85 + random.uniform(-0.1, 0.1)
            return max(0.0, min(1.0, correlation))
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur ES/NQ correlation: {e}")
            return 0.8
    
    def _calculate_level_proximity(self, market_data) -> float:
        """Calcul proximité niveaux"""
        try:
            # Simulation niveaux
            key_levels = [4500, 4490, 4510, 4480, 4520]
            min_distance = min(abs(market_data.price - level) for level in key_levels)
            
            proximity = max(0.0, 1.0 - (min_distance / 10))
            return proximity
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur level proximity: {e}")
            return 0.5
    
    def _calculate_session_context(self, market_data) -> float:
        """Calcul contexte session"""
        try:
            now = datetime.now()
            session_hours = (now - self.session_start).total_seconds() / 3600
            
            if session_hours < 1:  # Première heure
                return 0.8
            elif session_hours < 3:  # Session matinale
                return 0.9
            elif session_hours < 6:  # Session principale
                return 1.0
            else:  # Session tardive
                return 0.7
                
        except Exception as e:
            logger.warning(f"⚠️ Erreur session context: {e}")
            return 0.8
    
    def _calculate_pullback_quality(self, market_data) -> float:
        """Calcul qualité pullback"""
        try:
            # Simulation pullback
            pullback_strength = random.uniform(0.3, 0.9)
            return pullback_strength
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur pullback quality: {e}")
            return 0.6
    
    def _calculate_sierra_pattern_strength(self, market_data) -> float:
        """Calcul force patterns Sierra"""
        try:
            # Simulation patterns
            patterns = ['double_top', 'double_bottom', 'triangle', 'flag']
            pattern_strength = random.uniform(0.4, 0.9)
            
            return pattern_strength
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur Sierra patterns: {e}")
            return 0.6
    
    def _calculate_volume_confirmation(self, market_data) -> float:
        """Calcul confirmation volume"""
        try:
            # Simulation volume
            avg_volume = 1000
            current_volume = market_data.volume
            volume_ratio = current_volume / avg_volume
            
            return min(1.0, volume_ratio / 2)
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur volume confirmation: {e}")
            return 0.7
    
    def _calculate_options_flow(self, market_data) -> float:
        """Calcul options flow"""
        try:
            # Simulation options data
            put_call_ratio = 1.05 + random.uniform(-0.1, 0.1)
            implied_vol = 0.22 + random.uniform(-0.05, 0.05)
            
            # Calcul bias options
            options_bias = self._calculate_options_bias(put_call_ratio, implied_vol, {})
            return options_bias
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur options flow: {e}")
            return 0.5
    
    def _calculate_order_book_imbalance(self, market_data) -> float:
        """Calcul déséquilibre order book"""
        try:
            # Simulation order book
            bid_volume = random.randint(800, 1200)
            ask_volume = random.randint(800, 1200)
            
            imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
            return max(0.0, min(1.0, abs(imbalance) * 2))
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur order book: {e}")
            return 0.5
    
    def _calculate_tick_momentum(self, market_data) -> float:
        """Calcul momentum tick"""
        try:
            # Simulation tick momentum
            momentum = random.uniform(-0.5, 0.5)
            return max(0.0, min(1.0, (momentum + 0.5)))
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur tick momentum: {e}")
            return 0.5
    
    def _calculate_delta_divergence(self, market_data) -> float:
        """Calcul divergence delta"""
        try:
            # Simulation delta divergence
            divergence = random.uniform(0.2, 0.8)
            return divergence
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur delta divergence: {e}")
            return 0.5
    
    def _calculate_smart_money_index(self, market_data) -> float:
        """Calcul index smart money"""
        try:
            # Simulation smart money
            smart_money_flow = random.uniform(0.3, 0.9)
            return smart_money_flow
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur smart money: {e}")
            return 0.6
    
    def _calculate_mtf_confluence(self, market_data) -> float:
        """Calcul confluence multi-timeframe"""
        try:
            # Simulation MTF confluence
            mtf_score = random.uniform(0.4, 0.9)
            return mtf_score
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur MTF confluence: {e}")
            return 0.6
    
    def _calculate_options_bias(self, put_call_ratio: float, implied_vol: float, greeks: Dict[str, float]) -> float:
        """Calcul bias options"""
        try:
            # 1. Put/Call Ratio Analysis (40% du poids)
            pcr_bias = 0.0
            if put_call_ratio > 1.2:  # Bearish sentiment
                pcr_bias = -0.4
            elif put_call_ratio < 0.8:  # Bullish sentiment
                pcr_bias = 0.4
            else:  # Neutral
                pcr_bias = (put_call_ratio - 1.0) * 2.0
            
            # 2. Implied Volatility Analysis (30% du poids)
            vol_bias = 0.0
            if implied_vol > 0.25:  # High volatility
                vol_bias = -0.2
            elif implied_vol < 0.15:  # Low volatility
                vol_bias = 0.2
            else:  # Normal volatility
                vol_bias = (implied_vol - 0.20) * 4.0
            
            # 3. Greeks Analysis (30% du poids)
            greeks_bias = 0.0
            delta = greeks.get('delta', 0.0)
            gamma = greeks.get('gamma', 0.0)
            
            if abs(delta) > 0.5:
                greeks_bias = delta * 0.3
            else:
                greeks_bias = delta * 0.6
            
            if gamma > 0.03:
                greeks_bias += 0.1
            elif gamma < 0.01:
                greeks_bias -= 0.1
            
            # Combine all biases
            total_bias = (pcr_bias * 0.4) + (vol_bias * 0.3) + (greeks_bias * 0.3)
            normalized_bias = (total_bias + 1.0) / 2.0
            
            return max(0.0, min(1.0, normalized_bias))
            
        except Exception as e:
            logger.error(f"Erreur calcul options bias: {e}")
            return 0.5
    
    def _get_gamma_expiration_factor(self) -> float:
        """Facteur d'expiration gamma"""
        try:
            now = datetime.now()
            days_to_expiry = 5  # Simulation
            return max(0.5, 1.0 - (days_to_expiry / 30))
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur gamma expiration: {e}")
            return 0.8
    
    def clear_cache(self) -> None:
        """Nettoie le cache"""
        self.calculation_cache.clear()
        logger.info("🧹 Cache confluence nettoyé") 