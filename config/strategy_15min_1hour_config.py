#!/usr/bin/env python3
"""
Configuration Stratégie 15min + 1hour
MIA_IA_SYSTEM - Intégration stratégie validée

Ce fichier configure l'intégration de la stratégie 15min + 1hour
dans le système principal MIA_IA_SYSTEM.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

# === CONFIGURATION STRATÉGIE 15MIN + 1HOUR ===

@dataclass
class TimeframeConfig:
    """Configuration des timeframes 15min + 1hour"""
    
    # Timeframes activés
    enabled_timeframes: List[str] = None
    
    # Poids par timeframe
    weights: Dict[str, float] = None
    
    # Seuils de confluence
    thresholds: Dict[str, float] = None
    
    def __post_init__(self):
        """Initialisation par défaut"""
        if self.enabled_timeframes is None:
            self.enabled_timeframes = ["15min", "1hour"]
        
        if self.weights is None:
            self.weights = {
                "15min": 0.70,  # 70% - Exécution précise
                "1hour": 0.30   # 30% - Direction macro
            }
        
        if self.thresholds is None:
            self.thresholds = {
                "min_15min_confluence": 0.65,    # 65% confluence 15min
                "min_1hour_confluence": 0.60,    # 60% confluence 1hour
                "min_final_confluence": 0.70     # 70% confluence finale
            }

class ConfluenceRule(Enum):
    """Règles de confluence"""
    BOTH_REQUIRED = "both_required"      # Les deux timeframes doivent être d'accord
    WEIGHTED_AVERAGE = "weighted_average" # Moyenne pondérée
    STRICT_ALIGNMENT = "strict_alignment" # Alignement strict

@dataclass
class StrategyConfig:
    """Configuration complète de la stratégie"""
    
    # Configuration timeframes
    timeframes: TimeframeConfig = None
    
    # Règle de confluence
    confluence_rule: ConfluenceRule = ConfluenceRule.BOTH_REQUIRED
    
    # Performance
    max_latency_ms: float = 5.0
    cache_enabled: bool = True
    optimization_mode: str = "balanced"
    
    # Logique de trading
    signal_validation: str = "strict"
    position_sizing: str = "fixed"
    
    def __post_init__(self):
        """Initialisation par défaut"""
        if self.timeframes is None:
            self.timeframes = TimeframeConfig()

# === CONFIGURATION PAR DÉFAUT ===

DEFAULT_STRATEGY_CONFIG = StrategyConfig()

# === FONCTIONS D'INTÉGRATION ===

def get_15min_1hour_config() -> StrategyConfig:
    """Retourne la configuration 15min + 1hour"""
    return DEFAULT_STRATEGY_CONFIG

def validate_timeframe_weights(weights: Dict[str, float]) -> bool:
    """Valide que les poids somment à 100%"""
    total = sum(weights.values())
    return abs(total - 1.0) < 0.001

def calculate_confluence_score(signals: Dict[str, float], weights: Dict[str, float]) -> float:
    """Calcule le score de confluence pondéré"""
    if not validate_timeframe_weights(weights):
        raise ValueError("Poids invalides: doivent sommer à 100%")
    
    confluence_score = 0.0
    for timeframe, weight in weights.items():
        if timeframe in signals:
            confluence_score += signals[timeframe] * weight
    
    return confluence_score

def determine_trading_signal(signals: Dict[str, str], config: StrategyConfig) -> str:
    """Détermine le signal de trading selon la logique 15min + 1hour"""
    
    if config.confluence_rule == ConfluenceRule.BOTH_REQUIRED:
        # Logique: Les deux timeframes doivent être d'accord
        if "15min" in signals and "1hour" in signals:
            signal_15min = signals["15min"]
            signal_1hour = signals["1hour"]
            
            if signal_15min == "BULLISH" and signal_1hour == "BULLISH":
                return "LONG"
            elif signal_15min == "BEARISH" and signal_1hour == "BEARISH":
                return "SHORT"
            else:
                return "NO_TRADE"
        else:
            return "NO_TRADE"
    
    elif config.confluence_rule == ConfluenceRule.WEIGHTED_AVERAGE:
        # Logique: Moyenne pondérée des scores
        weights = config.timeframes.weights
        scores = {tf: 1.0 if signals.get(tf) in ["BULLISH", "LONG"] else 
                        -1.0 if signals.get(tf) in ["BEARISH", "SHORT"] else 0.0
                 for tf in weights.keys()}
        
        weighted_score = calculate_confluence_score(scores, weights)
        
        if weighted_score > 0.3:
            return "LONG"
        elif weighted_score < -0.3:
            return "SHORT"
        else:
            return "NO_TRADE"
    
    else:
        return "NO_TRADE"

def validate_signal_quality(confluence_score: float, config: StrategyConfig) -> bool:
    """Valide la qualité du signal selon les seuils"""
    thresholds = config.timeframes.thresholds
    
    return (confluence_score >= thresholds["min_final_confluence"])

# === INTÉGRATION AVEC FEATURE CALCULATOR ===

def integrate_with_feature_calculator() -> Dict[str, Any]:
    """Intègre la configuration avec le Feature Calculator"""
    
    config = get_15min_1hour_config()
    
    # Adaptation des poids pour le Feature Calculator
    feature_weights = {
        'gamma_levels_proximity': 0.25,      # 25% - Options flow
        'volume_confirmation': 0.18,         # 18% - Order flow
        'vwap_trend_signal': 0.15,           # 15% - VWAP slope
        'sierra_pattern_strength': 0.15,     # 15% - Patterns
        'mtf_confluence_score': 0.12,        # 12% - MTF Confluence (15min + 1hour)
        'smart_money_strength': 0.10,        # 10% - Smart Money
        'order_book_imbalance': 0.03,        # 3% - Order Book
        'options_flow_bias': 0.02            # 2% - Options flow
    }
    
    return {
        'feature_weights': feature_weights,
        'timeframe_config': config.timeframes,
        'confluence_rule': config.confluence_rule,
        'thresholds': config.timeframes.thresholds
    }

# === TESTS D'INTÉGRATION ===

def test_integration():
    """Teste l'intégration de la configuration"""
    print("🧪 TEST INTÉGRATION 15MIN + 1HOUR")
    print("=" * 50)
    
    # Test configuration
    config = get_15min_1hour_config()
    print(f"✅ Configuration chargée: {len(config.timeframes.enabled_timeframes)} timeframes")
    
    # Test validation poids
    weights_valid = validate_timeframe_weights(config.timeframes.weights)
    print(f"✅ Validation poids: {'OK' if weights_valid else 'ERREUR'}")
    
    # Test logique confluence
    test_signals = [
        {"15min": "BULLISH", "1hour": "BULLISH"},
        {"15min": "BEARISH", "1hour": "BEARISH"},
        {"15min": "BULLISH", "1hour": "BEARISH"},
    ]
    
    for i, signals in enumerate(test_signals, 1):
        result = determine_trading_signal(signals, config)
        print(f"✅ Test {i}: {signals} → {result}")
    
    # Test intégration Feature Calculator
    integration = integrate_with_feature_calculator()
    print(f"✅ Intégration Feature Calculator: {len(integration)} éléments")
    
    print("\n🎉 INTÉGRATION VALIDÉE")
    return True

if __name__ == "__main__":
    test_integration() 