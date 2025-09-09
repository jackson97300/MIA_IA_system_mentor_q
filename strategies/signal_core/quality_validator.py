"""
strategies/signal_core/quality_validator.py

Validateur de qualité des signaux avec toutes les techniques Elite
Extrait et nettoyé du fichier original signal_generator.py (lignes 1400-1700)
"""

from typing import Dict, Any, Optional
from core.logger import get_logger

# Imports depuis base_types
from .base_types import (
    MIN_BATTLE_NAVALE_SIGNAL_LONG, MIN_BATTLE_NAVALE_SIGNAL_SHORT,
    MIN_CONFLUENCE_SCORE, MIN_MTF_ELITE_SCORE, MIN_MTF_STANDARD_SCORE,
    MIN_SMART_MONEY_CONFIDENCE, MIN_SMART_MONEY_INSTITUTIONAL_SCORE,
    MIN_ML_ENSEMBLE_CONFIDENCE, GammaPhase
)

# Imports depuis signal_components
from .signal_components import SignalComponents, FinalSignal

logger = get_logger(__name__)

# ===== QUALITY VALIDATOR =====

class QualityValidator:
    """
    Validateur de qualité des signaux avec toutes les techniques Elite
    
    Gère la validation à plusieurs niveaux :
    - Validation minimale (seuils Battle Navale)
    - Validation Elite (MTF + Smart Money + ML + Gamma)
    - Validation confluence (multi-niveaux)
    - Validation risk management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation du validateur de qualité"""
        self.config = config or {}
        
        # Configuration validation
        self.min_confluence = self.config.get('min_confluence_score', MIN_CONFLUENCE_SCORE)
        self.min_risk_reward = self.config.get('min_risk_reward', 1.5)
        self.max_position_size = self.config.get('max_position_size', 3.0)
        
        # Seuils Battle Navale
        self.battle_navale_long_threshold = self.config.get('battle_long_threshold', MIN_BATTLE_NAVALE_SIGNAL_LONG)
        self.battle_navale_short_threshold = self.config.get('battle_short_threshold', MIN_BATTLE_NAVALE_SIGNAL_SHORT)
        
        # Configuration techniques Elite
        self.mtf_enabled = self.config.get('mtf_enabled', True)
        self.mtf_elite_threshold = self.config.get('mtf_elite_threshold', MIN_MTF_ELITE_SCORE)
        self.mtf_standard_threshold = self.config.get('mtf_standard_threshold', MIN_MTF_STANDARD_SCORE)
        
        self.smart_money_enabled = self.config.get('smart_money_enabled', True)
        self.smart_money_confidence_threshold = self.config.get('smart_money_confidence_threshold', MIN_SMART_MONEY_CONFIDENCE)
        self.smart_money_institutional_threshold = self.config.get('smart_money_institutional_threshold', MIN_SMART_MONEY_INSTITUTIONAL_SCORE)
        
        self.ml_ensemble_enabled = self.config.get('ml_ensemble_enabled', True)
        self.ml_ensemble_confidence_threshold = self.config.get('ml_ensemble_confidence_threshold', MIN_ML_ENSEMBLE_CONFIDENCE)
        
        self.gamma_cycles_enabled = self.config.get('gamma_cycles_enabled', True)
        
        logger.debug("QualityValidator initialisé avec tous les seuils Elite")

    def validate_signal_quality_v6(self, components: SignalComponents) -> bool:
        """
        🎯 TECHNIQUE #4: VALIDATION QUALITÉ AVEC GAMMA CYCLES
        
        Version finale incluant validation Gamma Cycles + ML + Smart Money + MTF
        """
        
        if not components.features:
            logger.debug("Validation échouée: Pas de features calculées")
            return False

        # 1. Confluence score minimum (maintenu)
        confluence_score = self._extract_confluence_score(components.features)
        if confluence_score < self.min_confluence:
            logger.debug(f"Validation échouée: Confluence insuffisante: {confluence_score:.3f} < {self.min_confluence}")
            return False

        # 2. === PRIORITÉ #2: VALIDATION NOUVEAUX SEUILS BATTLE NAVALE ===
        if not self._validate_battle_navale_thresholds(components):
            return False

        # 3. 🆕 PHASE 3: VALIDATION MTF CONFLUENCE (OPTIONNELLE)
        self._validate_mtf_confluence(components)

        # 4. 🎯 TECHNIQUE #2: VALIDATION SMART MONEY (OPTIONNELLE MAIS BONUS)
        self._validate_smart_money(components)

        # 5. 🎯 TECHNIQUE #3: VALIDATION ML ENSEMBLE (FILTRE CRITIQUE)
        if not self._validate_ml_ensemble(components):
            return False  # ❌ REJET CRITIQUE par ML Ensemble

        # 6. 🎯 TECHNIQUE #4: VALIDATION GAMMA CYCLES (OPTIONNELLE MAIS INFORMATIVE)
        self._validate_gamma_cycles(components)

        logger.debug("✅ Signal validé par tous les critères de qualité")
        return True

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

    def _validate_battle_navale_thresholds(self, components: SignalComponents) -> bool:
        """Validation nouveaux seuils Battle Navale"""
        
        if not components.battle_navale:
            logger.debug("Validation échouée: Pas d'analyse Battle Navale disponible")
            return False

        battle_signal = getattr(components.battle_navale, 'battle_navale_signal', 0.5)

        # Vérification seuils directionnels
        valid_long = battle_signal > self.battle_navale_long_threshold
        valid_short = battle_signal < self.battle_navale_short_threshold

        if not (valid_long or valid_short):
            logger.debug(f"Validation échouée: Battle navale sous nouveaux seuils: {battle_signal:.3f} "
                       f"(LONG>{self.battle_navale_long_threshold}, SHORT<{self.battle_navale_short_threshold})")
            return False

        logger.debug(f"✅ Battle Navale validé: {battle_signal:.3f} (seuils: {self.battle_navale_long_threshold}/{self.battle_navale_short_threshold})")
        return True

    def _validate_mtf_confluence(self, components: SignalComponents):
        """🆕 PHASE 3: Validation MTF Confluence (optionnelle)"""
        
        if not self.mtf_enabled or components.mtf_confluence_score is None:
            return
            
        mtf_score = abs(components.mtf_confluence_score)

        # MTF confluence comme boost, pas requirement strict
        if mtf_score > self.mtf_elite_threshold:
            logger.debug(f"🏆 MTF Elite détecté: {mtf_score:.3f} > {self.mtf_elite_threshold}")
        elif mtf_score > self.mtf_standard_threshold:
            logger.debug(f"✅ MTF Standard détecté: {mtf_score:.3f} > {self.mtf_standard_threshold}")
        else:
            logger.debug(f"🔶 MTF Faible: {mtf_score:.3f} (pas de rejet)")

    def _validate_smart_money(self, components: SignalComponents):
        """🎯 TECHNIQUE #2: Validation Smart Money (optionnelle mais bonus)"""
        
        if not self.smart_money_enabled or components.smart_money_confidence is None:
            return
            
        smart_money_conf = components.smart_money_confidence

        if smart_money_conf > self.smart_money_confidence_threshold:
            logger.debug(f"🎯 Smart Money détecté: {smart_money_conf:.3f} > {self.smart_money_confidence_threshold}")

            # Check flux institutionnel
            if (components.smart_money_institutional_score and
                components.smart_money_institutional_score > self.smart_money_institutional_threshold):
                logger.debug(f"🏛️ Flux institutionnel détecté: {components.smart_money_institutional_score:.3f}")
        else:
            logger.debug(f"🔶 Smart Money faible: {smart_money_conf:.3f} (pas de rejet)")

    def _validate_ml_ensemble(self, components: SignalComponents) -> bool:
        """🎯 TECHNIQUE #3: Validation ML Ensemble (filtre critique)"""
        
        if not self.ml_ensemble_enabled or components.ml_ensemble_prediction is None:
            return True  # Pas de ML, pas de rejet
            
        ml_approved = getattr(components.ml_ensemble_prediction, 'signal_approved', False)
        ml_confidence = getattr(components.ml_ensemble_prediction, 'confidence', 0.0)

        if not ml_approved:
            logger.debug(f"❌ Signal rejeté par ML Ensemble: {ml_confidence:.3f} < {self.ml_ensemble_confidence_threshold}")
            return False  # ❌ REJET CRITIQUE par ML Ensemble
        else:
            logger.debug(f"🎯 Signal validé par ML Ensemble: {ml_confidence:.3f}")
            return True

    def _validate_gamma_cycles(self, components: SignalComponents):
        """🎯 TECHNIQUE #4: Validation Gamma Cycles (optionnelle mais informative)"""
        
        if not self.gamma_cycles_enabled or components.gamma_cycle_analysis is None:
            return
            
        gamma_analysis = components.gamma_cycle_analysis
        gamma_factor = getattr(gamma_analysis, 'adjustment_factor', 1.0)
        gamma_phase = getattr(gamma_analysis, 'gamma_phase', None)

        # Log phase gamma pour information
        if gamma_phase:
            logger.debug(f"🎯 Gamma Phase: {gamma_phase.value}, "
                        f"Factor: {gamma_factor:.2f}")

            # Avertissement si semaine expiration (haute volatilité)
            if gamma_phase == GammaPhase.EXPIRY_WEEK:
                logger.debug("⚠️ Semaine expiration options - Attention volatilité élevée")

            # Info si gamma peak (conditions optimales)
            elif gamma_phase == GammaPhase.GAMMA_PEAK:
                logger.debug("🏆 Gamma Peak détecté - Conditions optimales trading")

    def validate_confluence_v3(self,
                               components: SignalComponents,
                               strategy_signal: Any) -> bool:
        """
        🎯 TECHNIQUE #4: VALIDATION CONFLUENCE INCLUANT GAMMA CYCLES
        
        Version améliorée avec prise en compte Gamma + Smart Money + MTF Elite
        """
        
        # Validation confluence traditionnelle
        traditional_valid = self._validate_confluence_traditional(components, strategy_signal)

        # 🆕 PHASE 3: Boost si MTF Elite
        mtf_boost = self._check_mtf_elite_override(components)

        # 🎯 TECHNIQUE #2: Boost si Smart Money + Battle Navale alignés
        smart_money_boost = self._check_smart_money_alignment_override(components)

        # 🎯 TECHNIQUE #4: Boost si Gamma Peak timing optimal
        gamma_boost = self._check_gamma_peak_override(components)

        # Toute technique Elite peut override confluence faible
        final_valid = traditional_valid or mtf_boost or smart_money_boost or gamma_boost
        
        if final_valid and not traditional_valid:
            logger.debug("✅ Confluence validation boostée par techniques Elite")
            
        return final_valid

    def _validate_confluence_traditional(self, components: SignalComponents, strategy_signal: Any) -> bool:
        """Validation confluence traditionnelle (version originale)"""
        
        # Si pas d'analyse confluence, on accepte
        if not components.confluence_analysis:
            return True

        # Vérifier alignement avec zones de confluence
        if hasattr(components.confluence_analysis, 'nearest_support_zone'):
            support_zone = components.confluence_analysis.nearest_support_zone
            resistance_zone = components.confluence_analysis.nearest_resistance_zone

            if hasattr(strategy_signal, 'entry_price'):
                entry_price = strategy_signal.entry_price

                # Vérifier proximité zones importantes
                min_distance = float('inf')

                if support_zone:
                    distance = abs(entry_price - support_zone.center_price)
                    min_distance = min(min_distance, distance)

                if resistance_zone:
                    distance = abs(entry_price - resistance_zone.center_price)
                    min_distance = min(min_distance, distance)

                # Signal trop loin des zones importantes
                if min_distance > 3.0:  # Plus de 3 points de distance
                    logger.debug("Confluence traditionnelle: Signal trop loin des zones importantes")
                    return False

        return True

    def _check_mtf_elite_override(self, components: SignalComponents) -> bool:
        """Vérifie si MTF Elite peut override confluence faible"""
        
        if (self.mtf_enabled and
            components.mtf_confluence_score is not None and
            abs(components.mtf_confluence_score) > self.mtf_elite_threshold):
            logger.debug("🚀 MTF Elite override: Confluence validation boostée")
            return True
        return False

    def _check_smart_money_alignment_override(self, components: SignalComponents) -> bool:
        """Vérifie si Smart Money + Battle Navale alignés peuvent override"""
        
        if (self.smart_money_enabled and
            components.smart_money_analysis and
            components.battle_navale):

            battle_signal = getattr(components.battle_navale, 'battle_navale_signal', 0.0)
            smart_money_score = getattr(components.smart_money_analysis, 'smart_money_score', 0.0)

            # Alignment si même direction et force significative
            if ((battle_signal > 0 and smart_money_score > 0) or
                (battle_signal < 0 and smart_money_score < 0)) and \
               abs(smart_money_score) > 0.3:
                logger.debug("🎯 Smart Money alignment override: Confluence validation boostée")
                return True
        return False

    def _check_gamma_peak_override(self, components: SignalComponents) -> bool:
        """Vérifie si Gamma Peak peut override confluence faible"""
        
        if (self.gamma_cycles_enabled and
            components.gamma_cycle_analysis and
            getattr(components.gamma_cycle_analysis, 'gamma_phase', None) == GammaPhase.GAMMA_PEAK):
            logger.debug("🎯 Gamma Peak override: Confluence validation boostée")
            return True
        return False

    def validate_risk_parameters(self, signal: FinalSignal) -> bool:
        """Validation finale paramètres de risque"""
        
        # Risk/Reward minimum
        if signal.risk_reward_ratio < self.min_risk_reward:
            logger.debug(f"Risk management échoué: R:R insuffisant: {signal.risk_reward_ratio:.2f} < {self.min_risk_reward}")
            return False

        # Stop loss raisonnable
        from core.base_types import ES_TICK_SIZE
        risk_ticks = abs(signal.entry_price - signal.stop_loss) / ES_TICK_SIZE
        if risk_ticks > 20:  # Max 5 points ES
            logger.debug(f"Risk management échoué: Stop loss trop large: {risk_ticks} ticks")
            return False

        # Position size valide
        if signal.position_size <= 0 or signal.position_size > self.max_position_size:
            logger.debug(f"Risk management échoué: Position size invalide: {signal.position_size}")
            return False

        logger.debug("✅ Risk management validé")
        return True

    def get_validation_summary(self, components: SignalComponents) -> Dict[str, Any]:
        """Retourne un résumé complet de la validation"""
        
        summary = {
            'overall_valid': False,
            'validations': {},
            'techniques_status': {},
            'scores': {},
            'overrides': {}
        }

        # Test validation globale
        summary['overall_valid'] = self.validate_signal_quality_v6(components)

        # Validations individuelles
        summary['validations']['confluence'] = self._extract_confluence_score(components.features) >= self.min_confluence
        summary['validations']['battle_navale'] = self._validate_battle_navale_thresholds(components)
        summary['validations']['ml_ensemble'] = self._validate_ml_ensemble(components)

        # Status techniques
        summary['techniques_status']['mtf_enabled'] = self.mtf_enabled
        summary['techniques_status']['smart_money_enabled'] = self.smart_money_enabled
        summary['techniques_status']['ml_ensemble_enabled'] = self.ml_ensemble_enabled
        summary['techniques_status']['gamma_cycles_enabled'] = self.gamma_cycles_enabled

        # Scores
        summary['scores']['confluence'] = self._extract_confluence_score(components.features)
        if components.battle_navale:
            summary['scores']['battle_navale'] = getattr(components.battle_navale, 'battle_navale_signal', 0)
        if components.mtf_confluence_score is not None:
            summary['scores']['mtf_confluence'] = components.mtf_confluence_score
        if components.smart_money_confidence is not None:
            summary['scores']['smart_money'] = components.smart_money_confidence
        if components.ml_ensemble_confidence is not None:
            summary['scores']['ml_ensemble'] = components.ml_ensemble_confidence

        # Overrides possibles
        summary['overrides']['mtf_elite'] = self._check_mtf_elite_override(components)
        summary['overrides']['smart_money_alignment'] = self._check_smart_money_alignment_override(components)
        summary['overrides']['gamma_peak'] = self._check_gamma_peak_override(components)

        return summary

    def get_rejection_reason(self, components: SignalComponents) -> str:
        """Retourne la raison précise du rejet"""
        
        # Test confluence
        confluence_score = self._extract_confluence_score(components.features)
        if confluence_score < self.min_confluence:
            return f"Confluence insuffisante: {confluence_score:.3f} < {self.min_confluence}"

        # Test Battle Navale
        if not self._validate_battle_navale_thresholds(components):
            if components.battle_navale:
                battle_signal = getattr(components.battle_navale, 'battle_navale_signal', 0)
                return f"Battle Navale sous seuils: {battle_signal:.3f} (seuils: {self.battle_navale_long_threshold}/{self.battle_navale_short_threshold})"
            else:
                return "Pas d'analyse Battle Navale disponible"

        # Test ML Ensemble
        if not self._validate_ml_ensemble(components):
            if components.ml_ensemble_prediction:
                ml_confidence = getattr(components.ml_ensemble_prediction, 'confidence', 0)
                return f"Rejeté par ML Ensemble: {ml_confidence:.3f} < {self.ml_ensemble_confidence_threshold}"
            else:
                return "ML Ensemble non disponible mais requis"

        return "Validation réussie"

# ===== EXPORTS =====
__all__ = [
    'QualityValidator'
]