"""
strategies/signal_core/confidence_calculator.py

Calculateur de confidence final avec toutes les techniques Elite
Extrait et nettoyé du fichier original signal_generator.py (lignes 1800-2200)
"""

from typing import Dict, Any, Optional
from core.logger import get_logger

# Imports depuis base_types
from .base_types import (
    QualityLevel,
    MIN_MTF_ELITE_SCORE, MIN_SMART_MONEY_CONFIDENCE, MIN_SMART_MONEY_INSTITUTIONAL_SCORE,
    MIN_ML_ENSEMBLE_CONFIDENCE, GammaPhase
)

# Imports depuis signal_components
from .signal_components import SignalComponents

logger = get_logger(__name__)

# ===== CONFIDENCE CALCULATOR =====

class ConfidenceCalculator:
    """
    Calculateur de confidence final intégrant toutes les techniques Elite
    
    Gère le calcul de confidence avec pondération dynamique selon les techniques
    disponibles et leurs performances.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation du calculateur de confidence"""
        self.config = config or {}
        
        # Poids par défaut pour chaque composant
        self.default_weights = {
            'strategy': 0.15,           # Réduit
            'battle_navale': 0.20,      # Maintenu
            'confluence': 0.15,         # Maintenu
            'regime': 0.10,             # Maintenu
            'mtf_confluence': 0.15,     # PHASE 3
            'smart_money': 0.10,        # TECHNIQUE #2
            'ml_ensemble': 0.10,        # TECHNIQUE #3
            'gamma_cycles': 0.05        # TECHNIQUE #4
        }
        
        # Permettre override des poids via config
        self.weights = {**self.default_weights, **self.config.get('confidence_weights', {})}
        
        # Validation des poids
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Poids confidence totaux = {total_weight:.3f}, normalisation appliquée")
            # Normalisation
            for key in self.weights:
                self.weights[key] /= total_weight
        
        logger.debug(f"ConfidenceCalculator initialisé avec poids: {self.weights}")

    def calculate_final_confidence_v4(self,
                                      components: SignalComponents,
                                      strategy_signal: Any) -> float:
        """
        🎯 TECHNIQUE #4: CALCUL CONFIDENCE AVEC GAMMA CYCLES
        
        Version finale incluant Gamma Cycles + ML Ensemble + Smart Money + MTF confluence
        """
        confidence = 0.0
        active_weights = {}
        
        # Strategy confidence
        if hasattr(strategy_signal, 'confidence'):
            strategy_conf = strategy_signal.confidence
            confidence += strategy_conf * self.weights['strategy']
            active_weights['strategy'] = self.weights['strategy']
            logger.debug(f"Strategy confidence: {strategy_conf:.3f}")

        # Battle navale
        if components.battle_navale:
            battle_signal = getattr(components.battle_navale, 'battle_navale_signal', 0.5)
            confidence += battle_signal * self.weights['battle_navale']
            active_weights['battle_navale'] = self.weights['battle_navale']
            logger.debug(f"Battle Navale signal: {battle_signal:.3f}")

        # Confluence traditionnelle
        if components.features:
            confluence_score = self._extract_confluence_score(components.features)
            confidence += confluence_score * self.weights['confluence']
            active_weights['confluence'] = self.weights['confluence']
            logger.debug(f"Confluence score: {confluence_score:.3f}")

        # Regime strength
        if components.market_regime:
            regime_confidence = getattr(components.market_regime, 'confidence', 0.5)
            confidence += regime_confidence * self.weights['regime']
            active_weights['regime'] = self.weights['regime']
            logger.debug(f"Regime confidence: {regime_confidence:.3f}")

        # 🆕 PHASE 3: MTF Confluence
        if components.mtf_confluence_score is not None:
            # Convertir MTF score (-1 à +1) vers confidence (0 à 1)
            mtf_confidence = (abs(components.mtf_confluence_score) + 1) / 2
            confidence += mtf_confidence * self.weights['mtf_confluence']
            active_weights['mtf_confluence'] = self.weights['mtf_confluence']
            logger.debug(f"MTF confluence: {components.mtf_confluence_score:.3f} -> {mtf_confidence:.3f}")
        else:
            # Si pas de MTF, redistribuer le poids
            confidence += 0.5 * self.weights['mtf_confluence']
            logger.debug("MTF confluence: Non disponible, poids redistribué")

        # 🎯 TECHNIQUE #2: Smart Money
        if components.smart_money_confidence is not None:
            confidence += components.smart_money_confidence * self.weights['smart_money']
            active_weights['smart_money'] = self.weights['smart_money']
            logger.debug(f"Smart Money confidence: {components.smart_money_confidence:.3f}")
        else:
            # Si pas de Smart Money, redistribuer le poids
            confidence += 0.5 * self.weights['smart_money']
            logger.debug("Smart Money: Non disponible, poids redistribué")

        # 🎯 TECHNIQUE #3: ML Ensemble
        if components.ml_ensemble_confidence is not None:
            confidence += components.ml_ensemble_confidence * self.weights['ml_ensemble']
            active_weights['ml_ensemble'] = self.weights['ml_ensemble']
            logger.debug(f"ML Ensemble confidence: {components.ml_ensemble_confidence:.3f}")
        else:
            # Si pas de ML, redistribuer le poids
            confidence += 0.5 * self.weights['ml_ensemble']
            logger.debug("ML Ensemble: Non disponible, poids redistribué")

        # 🎯 TECHNIQUE #4: Gamma Cycles
        if components.gamma_adjustment_factor is not None:
            # Convertir facteur gamma vers confidence (facteur > 1 = confidence plus haute)
            gamma_confidence = min(components.gamma_adjustment_factor / 1.5, 1.0)
            confidence += gamma_confidence * self.weights['gamma_cycles']
            active_weights['gamma_cycles'] = self.weights['gamma_cycles']
            logger.debug(f"Gamma Cycles factor: {components.gamma_adjustment_factor:.2f} -> {gamma_confidence:.3f}")
        else:
            # Si pas de Gamma, redistribuer le poids
            confidence += 0.5 * self.weights['gamma_cycles']
            logger.debug("Gamma Cycles: Non disponible, poids redistribué")

        # Validation finale
        final_confidence = min(1.0, max(0.0, confidence))
        
        logger.debug(f"Confidence finale: {final_confidence:.3f} (composants actifs: {len(active_weights)})")
        
        return final_confidence

    def _extract_confluence_score(self, features) -> float:
        """Extrait le score de confluence de manière robuste"""
        
        # Si features est un objet avec attributs (FeatureCalculationResult)
        if hasattr(features, 'confluence_score'):
            return features.confluence_score
        
        # Si features est un dictionnaire
        elif isinstance(features, dict):
            return features.get('confluence_score', 0.5)
        
        # Fallback
        else:
            logger.debug("Confluence score non trouvé dans features, utilisation valeur par défaut")
            return 0.5

    def determine_quality_level_v4(self, confidence: float, components: SignalComponents) -> QualityLevel:
        """
        🎯 TECHNIQUE #4: NIVEAU QUALITÉ AVEC ULTIMATE_ELITE
        
        Version finale incluant ULTIMATE_ELITE pour signaux 5/5 techniques Elite
        """
        
        # 🎯 TECHNIQUE #4: Check Ultimate Elite (5/5 techniques)
        if self._is_ultimate_elite_signal(confidence, components):
            return QualityLevel.ULTIMATE_ELITE

        # 🎯 TECHNIQUE #3: Check ML Validated (4/4 techniques sans Gamma)
        if self._is_ml_validated_signal(confidence, components):
            return QualityLevel.ML_VALIDATED

        # 🎯 TECHNIQUE #4: Check Gamma Optimized
        if self._is_gamma_optimized_signal(confidence, components):
            return QualityLevel.GAMMA_OPTIMIZED

        # 🎯 TECHNIQUE #2: Check Institutional Smart Money
        if self._is_institutional_signal(confidence, components):
            return QualityLevel.INSTITUTIONAL

        # 🆕 PHASE 3: Check Elite MTF
        if self._is_elite_mtf_signal(confidence, components):
            return QualityLevel.ELITE

        # Niveaux traditionnels basés sur confidence
        if confidence >= 0.85:
            return QualityLevel.PREMIUM
        elif confidence >= 0.75:
            return QualityLevel.STRONG
        elif confidence >= 0.65:
            return QualityLevel.MODERATE
        elif confidence >= 0.55:
            return QualityLevel.WEAK
        else:
            return QualityLevel.REJECTED

    def _is_ultimate_elite_signal(self, confidence: float, components: SignalComponents) -> bool:
        """Vérifie si c'est un signal Ultimate Elite (5/5 techniques)"""
        
        return (
            components.ml_ensemble_prediction and
            getattr(components.ml_ensemble_prediction, 'signal_approved', False) and
            getattr(components.ml_ensemble_prediction, 'confidence', 0) > 0.85 and
            confidence >= 0.80 and
            components.mtf_confluence_score is not None and
            abs(components.mtf_confluence_score) > MIN_MTF_ELITE_SCORE and
            components.smart_money_institutional_score and
            components.smart_money_institutional_score > MIN_SMART_MONEY_INSTITUTIONAL_SCORE and
            components.gamma_cycle_analysis and
            getattr(components.gamma_cycle_analysis, 'gamma_phase', None) in [
                GammaPhase.GAMMA_PEAK, GammaPhase.GAMMA_MODERATE
            ]
        )

    def _is_ml_validated_signal(self, confidence: float, components: SignalComponents) -> bool:
        """Vérifie si c'est un signal ML Validated (4/4 techniques sans Gamma)"""
        
        return (
            components.ml_ensemble_prediction and
            getattr(components.ml_ensemble_prediction, 'signal_approved', False) and
            getattr(components.ml_ensemble_prediction, 'confidence', 0) > 0.85 and
            confidence >= 0.75 and
            components.mtf_confluence_score is not None and
            abs(components.mtf_confluence_score) > MIN_MTF_ELITE_SCORE and
            components.smart_money_institutional_score and
            components.smart_money_institutional_score > MIN_SMART_MONEY_INSTITUTIONAL_SCORE
        )

    def _is_gamma_optimized_signal(self, confidence: float, components: SignalComponents) -> bool:
        """Vérifie si c'est un signal Gamma Optimized"""
        
        return (
            components.gamma_cycle_analysis and
            getattr(components.gamma_cycle_analysis, 'gamma_phase', None) == GammaPhase.GAMMA_PEAK and
            confidence >= 0.70
        )

    def _is_institutional_signal(self, confidence: float, components: SignalComponents) -> bool:
        """Vérifie si c'est un signal Institutional Smart Money"""
        
        return (
            components.smart_money_institutional_score and
            components.smart_money_institutional_score > MIN_SMART_MONEY_INSTITUTIONAL_SCORE and
            confidence >= 0.70
        )

    def _is_elite_mtf_signal(self, confidence: float, components: SignalComponents) -> bool:
        """Vérifie si c'est un signal Elite MTF"""
        
        return (
            components.mtf_confluence_score is not None and
            abs(components.mtf_confluence_score) > MIN_MTF_ELITE_SCORE and
            confidence >= 0.80
        )

    def calculate_position_size_v3(self,
                                   confidence: float,
                                   components: SignalComponents) -> float:
        """
        🎯 TECHNIQUE #4: CALCUL POSITION SIZE AVEC GAMMA CYCLES
        
        Version finale incluant bonus Gamma + ML + Smart Money + MTF
        """
        
        base_size = 1.0  # MES contracts
        max_position_size = self.config.get('max_position_size', 3.0)

        # Ajustement selon confidence
        if confidence >= 0.85:
            size_multiplier = 1.5
        elif confidence >= 0.75:
            size_multiplier = 1.0
        elif confidence >= 0.65:
            size_multiplier = 0.75
        else:
            size_multiplier = 0.5

        # 🆕 PHASE 3: Bonus Elite MTF
        if (components.mtf_confluence_score is not None and
            abs(components.mtf_confluence_score) > MIN_MTF_ELITE_SCORE):
            size_multiplier *= 1.25  # Bonus 25% pour Elite
            logger.debug("Bonus MTF Elite appliqué: +25%")

        # 🎯 TECHNIQUE #2: Bonus Smart Money Institutional
        if (components.smart_money_institutional_score and
            components.smart_money_institutional_score > MIN_SMART_MONEY_INSTITUTIONAL_SCORE):
            size_multiplier *= 1.20  # Bonus 20% pour flux institutionnels
            logger.debug("Bonus Smart Money Institutional appliqué: +20%")

        # 🎯 TECHNIQUE #2: Bonus alignment Smart Money + Battle Navale
        if self._has_smart_money_alignment(components):
            size_multiplier *= 1.10  # Bonus 10% pour alignment
            logger.debug("Bonus Smart Money Alignment appliqué: +10%")

        # 🎯 TECHNIQUE #3: Bonus ML Ensemble High Confidence
        if (components.ml_ensemble_prediction and
            getattr(components.ml_ensemble_prediction, 'confidence', 0) > 0.85):
            size_multiplier *= 1.15  # Bonus 15% pour ML haute confidence
            logger.debug("Bonus ML High Confidence appliqué: +15%")

        # 🎯 TECHNIQUE #4: Bonus/Malus Gamma Cycles
        if components.gamma_adjustment_factor is not None:
            gamma_factor = components.gamma_adjustment_factor

            # Appliquer directement le facteur gamma au size multiplier
            size_multiplier *= gamma_factor
            logger.debug(f"Facteur Gamma appliqué: {gamma_factor:.2f}")

            # Bonus supplémentaire si gamma peak
            if (components.gamma_cycle_analysis and
                getattr(components.gamma_cycle_analysis, 'gamma_phase', None) == GammaPhase.GAMMA_PEAK):
                size_multiplier *= 1.05  # Bonus 5% supplémentaire pour timing optimal
                logger.debug("Bonus Gamma Peak appliqué: +5%")

        # Ajustement selon volatilité
        if components.market_regime:
            if hasattr(components.market_regime, 'volatility'):
                if components.market_regime.volatility > 0.8:  # High vol
                    size_multiplier *= 0.75
                    logger.debug("Réduction volatilité élevée: -25%")

        final_size = base_size * size_multiplier

        # Limites
        final_size = min(max_position_size, max(0.5, final_size))
        
        logger.debug(f"Position size finale: {final_size:.2f} (multiplier: {size_multiplier:.2f})")
        
        return final_size

    def _has_smart_money_alignment(self, components: SignalComponents) -> bool:
        """Vérifie alignment Smart Money + Battle Navale"""
        
        if not components.smart_money_analysis or not components.battle_navale:
            return False

        battle_signal = getattr(components.battle_navale, 'battle_navale_signal', 0.0)
        smart_money_score = getattr(components.smart_money_analysis, 'smart_money_score', 0.0)

        # Alignment si même direction et force significative
        return ((battle_signal > 0 and smart_money_score > 0) or
                (battle_signal < 0 and smart_money_score < 0)) and \
               abs(smart_money_score) > 0.3

    def get_confidence_breakdown(self, components: SignalComponents, strategy_signal: Any) -> Dict[str, Any]:
        """Retourne un breakdown détaillé du calcul de confidence"""
        
        breakdown = {
            'total_confidence': 0.0,
            'components': {},
            'weights_used': {},
            'techniques_available': {}
        }

        # Calculer chaque composant individuellement
        if hasattr(strategy_signal, 'confidence'):
            breakdown['components']['strategy'] = strategy_signal.confidence
            breakdown['weights_used']['strategy'] = self.weights['strategy']

        if components.battle_navale:
            breakdown['components']['battle_navale'] = getattr(components.battle_navale, 'battle_navale_signal', 0.5)
            breakdown['weights_used']['battle_navale'] = self.weights['battle_navale']

        if components.features:
            breakdown['components']['confluence'] = self._extract_confluence_score(components.features)
            breakdown['weights_used']['confluence'] = self.weights['confluence']

        if components.market_regime:
            breakdown['components']['regime'] = getattr(components.market_regime, 'confidence', 0.5)
            breakdown['weights_used']['regime'] = self.weights['regime']

        # Techniques Elite
        breakdown['techniques_available']['mtf_confluence'] = components.mtf_confluence_score is not None
        breakdown['techniques_available']['smart_money'] = components.smart_money_confidence is not None
        breakdown['techniques_available']['ml_ensemble'] = components.ml_ensemble_confidence is not None
        breakdown['techniques_available']['gamma_cycles'] = components.gamma_adjustment_factor is not None

        if components.mtf_confluence_score is not None:
            breakdown['components']['mtf_confluence'] = (abs(components.mtf_confluence_score) + 1) / 2
            breakdown['weights_used']['mtf_confluence'] = self.weights['mtf_confluence']

        if components.smart_money_confidence is not None:
            breakdown['components']['smart_money'] = components.smart_money_confidence
            breakdown['weights_used']['smart_money'] = self.weights['smart_money']

        if components.ml_ensemble_confidence is not None:
            breakdown['components']['ml_ensemble'] = components.ml_ensemble_confidence
            breakdown['weights_used']['ml_ensemble'] = self.weights['ml_ensemble']

        if components.gamma_adjustment_factor is not None:
            breakdown['components']['gamma_cycles'] = min(components.gamma_adjustment_factor / 1.5, 1.0)
            breakdown['weights_used']['gamma_cycles'] = self.weights['gamma_cycles']

        # Calcul total
        breakdown['total_confidence'] = self.calculate_final_confidence_v4(components, strategy_signal)

        return breakdown

# ===== EXPORTS =====
__all__ = [
    'ConfidenceCalculator'
]