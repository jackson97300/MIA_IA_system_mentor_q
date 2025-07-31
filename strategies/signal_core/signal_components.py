"""
strategies/signal_core/signal_components.py

Classes SignalComponents et FinalSignal
Extrait et nettoyé du fichier original signal_generator.py (lignes 300-900)
"""

import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

# Imports depuis base_types
from .base_types import (
    SignalDecision, SignalSource, QualityLevel,
    MIN_BATTLE_NAVALE_SIGNAL_LONG, MIN_BATTLE_NAVALE_SIGNAL_SHORT,
    MIN_SMART_MONEY_CONFIDENCE, MIN_SMART_MONEY_INSTITUTIONAL_SCORE,
    MIN_MTF_ELITE_SCORE, GammaPhase, GammaCycleAnalysis
)

# Imports core
from core.base_types import MarketRegime, ES_TICK_SIZE, ES_TICK_VALUE

# ===== DATA STRUCTURES =====

@dataclass
class SignalComponents:
    """Composants analysés pour génération signal"""
    timestamp: pd.Timestamp
    features: Optional[Any] = None  # FeatureCalculationResult ou Dict
    battle_navale: Optional[Any] = None
    market_regime: Optional[Any] = None  # MarketRegimeData
    trend_signal: Optional[Any] = None
    range_signal: Optional[Any] = None
    confluence_analysis: Optional[Any] = None
    risk_assessment: Optional[Dict[str, float]] = None
    
    # 🆕 PHASE 3: MTF Elite Analysis
    mtf_confluence_score: Optional[float] = None
    mtf_analysis: Optional[Dict[str, Any]] = None
    
    # 🎯 TECHNIQUE #2: Smart Money Analysis
    smart_money_analysis: Optional[Any] = None
    smart_money_confidence: Optional[float] = None
    smart_money_institutional_score: Optional[float] = None
    
    # 🎯 TECHNIQUE #3: ML Ensemble Analysis
    ml_ensemble_prediction: Optional[Any] = None
    ml_ensemble_confidence: Optional[float] = None
    ml_ensemble_approved: Optional[bool] = None
    
    # 🎯 TECHNIQUE #4: Gamma Cycles Analysis
    gamma_cycle_analysis: Optional[GammaCycleAnalysis] = None
    gamma_adjustment_factor: Optional[float] = None
    gamma_phase: Optional[GammaPhase] = None


@dataclass
class FinalSignal:
    """Signal final généré par le système"""
    timestamp: pd.Timestamp
    decision: SignalDecision
    signal_type: Any  # SignalType
    confidence: float
    quality_level: QualityLevel

    # Détails exécution
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float

    # Contexte et reasoning
    source: SignalSource
    regime: MarketRegime
    components: SignalComponents
    reasoning: str

    # Risk metrics
    risk_reward_ratio: float
    max_risk_dollars: float

    # Metadata
    generation_time_ms: float
    cache_hits: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ===== MÉTHODES DE VALIDATION BATTLE NAVALE =====
    
    def meets_battle_navale_threshold(self) -> bool:
        """Vérifie si signal dépasse nouveaux seuils Battle Navale"""
        if not self.components.battle_navale:
            return False

        battle_signal = getattr(self.components.battle_navale, 'battle_navale_signal', 0.5)

        if self.decision == SignalDecision.EXECUTE_LONG:
            return battle_signal > MIN_BATTLE_NAVALE_SIGNAL_LONG
        elif self.decision == SignalDecision.EXECUTE_SHORT:
            return battle_signal < MIN_BATTLE_NAVALE_SIGNAL_SHORT

        return False

    def get_battle_navale_strength(self) -> float:
        """Retourne force du signal Battle Navale selon nouveaux seuils"""
        if not self.components.battle_navale:
            return 0.0

        battle_signal = getattr(self.components.battle_navale, 'battle_navale_signal', 0.5)

        if battle_signal > MIN_BATTLE_NAVALE_SIGNAL_LONG:
            # Force LONG basée sur dépassement seuil
            return min((battle_signal - MIN_BATTLE_NAVALE_SIGNAL_LONG) * 4.0, 1.0)
        elif battle_signal < MIN_BATTLE_NAVALE_SIGNAL_SHORT:
            # Force SHORT basée sur dépassement seuil (valeur absolue)
            return min((MIN_BATTLE_NAVALE_SIGNAL_SHORT - battle_signal) * 4.0, 1.0)

        return 0.0

    # ===== MÉTHODES MTF ELITE =====
    
    def meets_mtf_elite_threshold(self) -> bool:
        """Vérifie si signal dépasse seuils MTF Elite"""
        if not self.components.mtf_confluence_score:
            return False

        return abs(self.components.mtf_confluence_score) > MIN_MTF_ELITE_SCORE

    def get_mtf_confluence_strength(self) -> float:
        """Retourne force confluence MTF Elite"""
        if not self.components.mtf_confluence_score:
            return 0.0

        return abs(self.components.mtf_confluence_score)

    # ===== MÉTHODES SMART MONEY =====
    
    def meets_smart_money_threshold(self) -> bool:
        """Vérifie si signal dépasse seuils Smart Money"""
        if not self.components.smart_money_confidence:
            return False

        return self.components.smart_money_confidence > MIN_SMART_MONEY_CONFIDENCE

    def get_smart_money_strength(self) -> float:
        """Retourne force signal Smart Money"""
        if not self.components.smart_money_confidence:
            return 0.0

        return self.components.smart_money_confidence

    def get_smart_money_institutional_score(self) -> float:
        """Retourne score flux institutionnel Smart Money"""
        if not self.components.smart_money_institutional_score:
            return 0.0

        return self.components.smart_money_institutional_score

    def has_smart_money_alignment(self) -> bool:
        """Vérifie alignment Smart Money avec Battle Navale"""
        if not self.components.smart_money_analysis or not self.components.battle_navale:
            return False

        battle_signal = getattr(self.components.battle_navale, 'battle_navale_signal', 0.0)
        smart_money_score = getattr(self.components.smart_money_analysis, 'smart_money_score', 0.0)

        # Alignment si même direction et force significative
        return ((battle_signal > 0 and smart_money_score > 0) or
                (battle_signal < 0 and smart_money_score < 0)) and \
               abs(smart_money_score) > 0.3

    # ===== MÉTHODES ML ENSEMBLE =====
    
    def meets_ml_ensemble_threshold(self) -> bool:
        """🎯 Vérifie si signal validé par ML Ensemble"""
        if not self.components.ml_ensemble_prediction:
            return False

        return getattr(self.components.ml_ensemble_prediction, 'signal_approved', False)

    def get_ml_ensemble_confidence(self) -> float:
        """🎯 Retourne confidence ML Ensemble"""
        if not self.components.ml_ensemble_confidence:
            return 0.0

        return self.components.ml_ensemble_confidence

    def is_ml_validated_signal(self) -> bool:
        """🎯 Vérifie si c'est un signal ML validé (toutes techniques Elite)"""
        return (self.meets_battle_navale_threshold() and
                self.meets_mtf_elite_threshold() and
                self.meets_smart_money_threshold() and
                self.meets_ml_ensemble_threshold())

    def has_ml_high_confidence(self) -> bool:
        """🎯 Vérifie si ML a très haute confidence (>85%)"""
        if not self.components.ml_ensemble_prediction:
            return False

        return getattr(self.components.ml_ensemble_prediction, 'confidence', 0.0) > 0.85

    # ===== MÉTHODES GAMMA CYCLES =====
    
    def meets_gamma_optimization_criteria(self) -> bool:
        """🎯 Vérifie si signal bénéficie d'optimisation gamma"""
        if not self.components.gamma_cycle_analysis:
            return False

        # Optimisation si phase gamma favorable
        favorable_phases = [GammaPhase.GAMMA_PEAK, GammaPhase.GAMMA_MODERATE, GammaPhase.POST_EXPIRY]
        return self.components.gamma_cycle_analysis.gamma_phase in favorable_phases

    def get_gamma_adjustment_factor(self) -> float:
        """🎯 Retourne facteur ajustement gamma"""
        if not self.components.gamma_adjustment_factor:
            return 1.0

        return self.components.gamma_adjustment_factor

    def get_gamma_phase(self) -> str:
        """🎯 Retourne phase gamma actuelle"""
        if not self.components.gamma_phase:
            return "UNKNOWN"

        return self.components.gamma_phase.value

    def is_gamma_peak_signal(self) -> bool:
        """🎯 Vérifie si signal pendant gamma peak optimal"""
        if not self.components.gamma_cycle_analysis:
            return False

        return self.components.gamma_cycle_analysis.gamma_phase == GammaPhase.GAMMA_PEAK

    # ===== MÉTHODES ELITE COMPOSÉES =====
    
    def is_ultimate_elite_signal(self) -> bool:
        """🎯 Vérifie si c'est un signal ULTIMATE ELITE (5/5 techniques)"""
        return (self.meets_battle_navale_threshold() and
                self.meets_mtf_elite_threshold() and
                self.meets_smart_money_threshold() and
                self.meets_ml_ensemble_threshold() and
                self.meets_gamma_optimization_criteria())

    def is_elite_signal(self) -> bool:
        """Vérifie si c'est un signal Elite (Battle Navale + MTF confluence + Smart Money)"""
        return (self.meets_battle_navale_threshold() and
                self.meets_mtf_elite_threshold() and
                self.meets_smart_money_threshold() and
                self.quality_level in [QualityLevel.ELITE, QualityLevel.INSTITUTIONAL, QualityLevel.PREMIUM])

    def is_institutional_signal(self) -> bool:
        """🎯 Vérifie si c'est un signal institutionnel Smart Money"""
        return (self.meets_smart_money_threshold() and
                self.components.smart_money_institutional_score and
                self.components.smart_money_institutional_score > MIN_SMART_MONEY_INSTITUTIONAL_SCORE)

    # ===== MÉTHODES UTILITAIRES =====
    
    def get_techniques_validated(self) -> List[str]:
        """Retourne la liste des techniques Elite validées"""
        techniques = []
        
        if self.meets_battle_navale_threshold():
            techniques.append("Battle_Navale")
        if self.meets_mtf_elite_threshold():
            techniques.append("MTF_Elite")
        if self.meets_smart_money_threshold():
            techniques.append("Smart_Money")
        if self.meets_ml_ensemble_threshold():
            techniques.append("ML_Ensemble")
        if self.meets_gamma_optimization_criteria():
            techniques.append("Gamma_Cycles")
            
        return techniques

    def get_signal_summary(self) -> Dict[str, Any]:
        """Retourne un résumé complet du signal"""
        return {
            'decision': self.decision.value,
            'confidence': round(self.confidence, 3),
            'quality_level': self.quality_level.value,
            'source': self.source.value,
            'techniques_validated': self.get_techniques_validated(),
            'battle_navale_strength': round(self.get_battle_navale_strength(), 3),
            'mtf_confluence_strength': round(self.get_mtf_confluence_strength(), 3),
            'smart_money_strength': round(self.get_smart_money_strength(), 3),
            'ml_ensemble_confidence': round(self.get_ml_ensemble_confidence(), 3),
            'gamma_adjustment_factor': round(self.get_gamma_adjustment_factor(), 2),
            'gamma_phase': self.get_gamma_phase(),
            'is_elite': self.is_elite_signal(),
            'is_institutional': self.is_institutional_signal(),
            'is_ml_validated': self.is_ml_validated_signal(),
            'is_ultimate_elite': self.is_ultimate_elite_signal(),
            'risk_reward_ratio': round(self.risk_reward_ratio, 2),
            'position_size': self.position_size,
            'generation_time_ms': round(self.generation_time_ms, 2),
            'cache_hits': self.cache_hits
        }

    def to_dict(self) -> Dict[str, Any]:
        """Conversion complète en dictionnaire"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'decision': self.decision.value,
            'signal_type': str(self.signal_type),
            'confidence': self.confidence,
            'quality_level': self.quality_level.value,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'position_size': self.position_size,
            'source': self.source.value,
            'regime': self.regime.value,
            'reasoning': self.reasoning,
            'risk_reward_ratio': self.risk_reward_ratio,
            'max_risk_dollars': self.max_risk_dollars,
            'generation_time_ms': self.generation_time_ms,
            'cache_hits': self.cache_hits,
            'metadata': self.metadata,
            'signal_summary': self.get_signal_summary()
        }

# ===== HELPER FUNCTIONS =====

def create_no_trade_signal(timestamp: pd.Timestamp, reason: str) -> FinalSignal:
    """Helper pour créer un signal NO_TRADE"""
    return FinalSignal(
        timestamp=timestamp,
        decision=SignalDecision.WAIT_BETTER_SETUP,
        signal_type=None,  # Sera remplacé par le bon type
        confidence=0.0,
        quality_level=QualityLevel.REJECTED,
        entry_price=0.0,
        stop_loss=0.0,
        take_profit=0.0,
        position_size=0.0,
        source=SignalSource.BATTLE_NAVALE,
        regime=MarketRegime.UNKNOWN,
        components=SignalComponents(timestamp=timestamp),
        reasoning=reason,
        risk_reward_ratio=0.0,
        max_risk_dollars=0.0,
        generation_time_ms=0.0,
        metadata={'rejection_reason': reason}
    )

def create_empty_components(timestamp: pd.Timestamp) -> SignalComponents:
    """Helper pour créer des composants vides"""
    return SignalComponents(timestamp=timestamp)

# ===== EXPORTS =====
__all__ = [
    'SignalComponents',
    'FinalSignal',
    'create_no_trade_signal',
    'create_empty_components'
]