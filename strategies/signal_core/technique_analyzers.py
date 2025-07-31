"""
strategies/signal_core/technique_analyzers.py

Analyseurs des 4 techniques Elite : MTF, Smart Money, ML Ensemble, Gamma Cycles
Extrait et nettoyé du fichier original signal_generator.py (lignes 1100-1800)
"""

import time
from typing import Dict, Optional, Any
from core.logger import get_logger
from core.base_types import MarketData, OrderFlowData

# Imports depuis base_types
from .base_types import (
    MIN_MTF_ELITE_SCORE, MIN_MTF_STANDARD_SCORE,
    MIN_SMART_MONEY_CONFIDENCE, MIN_SMART_MONEY_INSTITUTIONAL_SCORE,
    MIN_ML_ENSEMBLE_CONFIDENCE,
    MLEnsembleFilter, ml_ensemble_filter,
    GammaCyclesAnalyzer, GammaPhase,
    ML_ENSEMBLE_AVAILABLE, GAMMA_CYCLES_AVAILABLE
)

# Imports depuis signal_components
from .signal_components import SignalComponents

logger = get_logger(__name__)

# ===== TECHNIQUE ANALYZERS =====

class TechniqueAnalyzers:
    """
    Gestionnaire centralisé des 4 techniques Elite
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation des analyseurs de techniques"""
        self.config = config or {}
        
        # État des techniques
        self.mtf_enabled = self.config.get('mtf_enabled', True)
        self.smart_money_enabled = self._check_smart_money_availability()
        self.ml_ensemble_enabled = self._check_ml_ensemble_availability()
        self.gamma_cycles_enabled = self._check_gamma_cycles_availability()
        
        # Analyseurs
        self.ml_ensemble = None
        self.gamma_analyzer = None
        
        self._initialize_analyzers()
        
        logger.info(f"TechniqueAnalyzers initialisé - MTF:{self.mtf_enabled}, "
                   f"Smart Money:{self.smart_money_enabled}, "
                   f"ML:{self.ml_ensemble_enabled}, Gamma:{self.gamma_cycles_enabled}")

    def _initialize_analyzers(self):
        """Initialise les analyseurs disponibles"""
        
        # 🎯 TECHNIQUE #3: ML Ensemble Filter - VERSION CORRIGÉE
        if self.ml_ensemble_enabled:
            try:
                # ✅ CORRECTION: Utilisation directe sans paramètre cache_enabled
                self.ml_ensemble = MLEnsembleFilter()
                logger.info("🎯 ML Ensemble Filter initialisé - TECHNIQUE #3 prête")
            except Exception as e:
                logger.warning(f"Erreur initialisation ML Ensemble: {e}")
                self.ml_ensemble_enabled = False

        # 🎯 TECHNIQUE #4: Gamma Cycles Analyzer - VERSION CORRIGÉE
        if self.gamma_cycles_enabled:
            try:
                # ✅ CORRECTION: Utilisation directe sans paramètre cache_enabled
                self.gamma_analyzer = GammaCyclesAnalyzer()
                logger.info("🎯 Gamma Cycles Analyzer initialisé - TECHNIQUE #4 prête")
            except Exception as e:
                logger.warning(f"Erreur initialisation Gamma Cycles: {e}")
                self.gamma_cycles_enabled = False

    def _check_smart_money_availability(self) -> bool:
        """🎯 Vérifie disponibilité Smart Money Tracker"""
        try:
            # Vérification alternative dans features
            return True  # Assume disponible, sera validé par feature_calculator
        except Exception as e:
            logger.warning(f"Erreur vérification Smart Money: {e}")
            return False

    def _check_ml_ensemble_availability(self) -> bool:
        """🎯 Vérifie disponibilité ML Ensemble Filter"""
        if not ML_ENSEMBLE_AVAILABLE:
            return False

        try:
            from pathlib import Path
            models_path = Path("ml/trained_models")
            if not models_path.exists():
                logger.warning("Dossier ml/trained_models non trouvé")
                return False

            # Vérifier au moins un modèle disponible
            model_files = ['rf_signal_filter.pkl', 'xgb_signal_filter.pkl', 'lr_signal_filter.pkl']
            available_models = sum(1 for f in model_files if (models_path / f).exists())

            if available_models == 0:
                logger.warning("Aucun modèle ML trouvé dans ml/trained_models")
                return False

            logger.info(f"🎯 ML Ensemble: {available_models}/3 modèles disponibles")
            return True

        except Exception as e:
            logger.warning(f"Erreur vérification ML Ensemble: {e}")
            return False

    def _check_gamma_cycles_availability(self) -> bool:
        """🎯 Vérifie disponibilité Gamma Cycles Analyzer"""
        if not GAMMA_CYCLES_AVAILABLE:
            return False

        try:
            # ✅ CORRECTION: Test simple sans configuration complexe
            test_analyzer = GammaCyclesAnalyzer()

            # Test fonctionnel basique
            if hasattr(test_analyzer, 'analyze_gamma_cycle'):
                logger.info("🎯 Gamma Cycles: Test réussi, analyzer disponible")
                return True
            else:
                logger.warning("Gamma Cycles: Méthode analyze_gamma_cycle non disponible")
                return False

        except Exception as e:
            logger.warning(f"Erreur vérification Gamma Cycles: {e}")
            return False

    # ===== ANALYSE MTF ELITE CONFLUENCE =====
    
    def analyze_mtf_elite_confluence(self, market_data: MarketData, components: SignalComponents):
        """
        🆕 PHASE 3: ANALYSE ELITE MTF CONFLUENCE
        
        Calcule confluence multi-timeframes et l'intègre aux composants
        """
        try:
            if not self.mtf_enabled:
                components.mtf_confluence_score = 0.0
                components.mtf_analysis = {}
                return

            # Préparation données pour MTF
            market_data_dict = {
                "symbol": market_data.symbol,
                "current_price": market_data.close,
                "volume": market_data.volume,
                "timestamp": market_data.timestamp,
                "volatility": self._estimate_volatility(market_data),
                "session": self._detect_session_phase(market_data)
            }

            # Calcul Elite MTF Confluence (simulation si pas d'analyseur réel)
            mtf_score, mtf_analysis = self._calculate_mtf_confluence(market_data_dict)

            # Ajout aux composants
            components.mtf_confluence_score = mtf_score
            components.mtf_analysis = mtf_analysis

            # Logging détaillé
            logger.debug(f"🚀 MTF Analysis: Score={mtf_score:.3f}, "
                        f"Base={mtf_analysis.get('base_score', 0):.3f}, "
                        f"Alignment={mtf_analysis.get('alignment_bonus', 0):.3f}")

        except Exception as e:
            logger.warning(f"Erreur MTF Elite Confluence: {e}")
            components.mtf_confluence_score = 0.0
            components.mtf_analysis = {}

    def _calculate_mtf_confluence(self, market_data_dict: Dict[str, Any]) -> tuple:
        """Calcul MTF confluence (simulation simplifiée)"""
        
        # Score de base basé sur volatilité et volume
        base_score = 0.5
        
        volatility = market_data_dict.get('volatility', 0.5)
        if volatility > 1.5:  # Haute volatilité
            base_score += 0.2
        elif volatility < 0.5:  # Basse volatilité
            base_score -= 0.1
            
        # Bonus session
        session = market_data_dict.get('session', 'OVERNIGHT')
        session_bonus = 0.0
        if session == 'US_OPEN':
            session_bonus = 0.15
        elif session == 'US_SESSION':
            session_bonus = 0.1
        elif session == 'US_CLOSE':
            session_bonus = 0.05
        
        # Score final
        final_score = base_score + session_bonus
        final_score = max(-1.0, min(1.0, final_score))  # Clamp [-1, 1]
        
        # Analyse détaillée
        analysis = {
            'base_score': base_score,
            'session_bonus': session_bonus,
            'alignment_bonus': 0.0,
            'quality_bonus': 0.0,
            'volatility': volatility,
            'session': session,
            'timestamp': market_data_dict.get('timestamp')
        }
        
        return final_score, analysis

    # ===== ANALYSE SMART MONEY FLOWS =====
    
    def analyze_smart_money_flows(self, 
                                  market_data: MarketData,
                                  order_flow: Optional[OrderFlowData],
                                  components: SignalComponents):
        """
        🎯 TECHNIQUE #2: ANALYSE SMART MONEY FLOWS
        
        Analyse flux institutionnels et intègre aux composants
        """
        try:
            if not self.smart_money_enabled:
                components.smart_money_confidence = 0.0
                components.smart_money_institutional_score = 0.0
                components.smart_money_analysis = None
                return

            # ✅ FIX: Vérifier que features est disponible et accessible
            smart_money_feature = self._extract_smart_money_feature(components)

            if smart_money_feature is not None:
                # Conversion de [0,1] vers confidence et score institutionnel
                components.smart_money_confidence = smart_money_feature

                # Score institutionnel basé sur seuil élevé
                if smart_money_feature > 0.7:
                    components.smart_money_institutional_score = smart_money_feature
                else:
                    components.smart_money_institutional_score = 0.0

                # Création analysis pour compatibilité
                components.smart_money_analysis = self._create_smart_money_analysis(smart_money_feature)

                logger.debug(f"🎯 Smart Money: Feature={smart_money_feature:.3f}, "
                           f"Confidence={components.smart_money_confidence:.3f}, "
                           f"Institutional={components.smart_money_institutional_score:.3f}")
            else:
                # Pas de Smart Money disponible
                components.smart_money_confidence = 0.0
                components.smart_money_institutional_score = 0.0
                components.smart_money_analysis = None
                logger.debug("🎯 Smart Money: Pas de données disponibles")

        except Exception as e:
            logger.warning(f"Erreur Smart Money analysis: {e}")
            components.smart_money_confidence = 0.0
            components.smart_money_institutional_score = 0.0
            components.smart_money_analysis = None

    def _extract_smart_money_feature(self, components: SignalComponents) -> Optional[float]:
        """Extrait la feature smart_money_strength de manière robuste"""
        
        if not hasattr(components, 'features') or not components.features:
            return None
            
        # Si features est un objet avec attributs (FeatureCalculationResult)
        if hasattr(components.features, 'smart_money_strength'):
            return components.features.smart_money_strength
            
        # Si features est un dictionnaire
        if isinstance(components.features, dict) and 'smart_money_strength' in components.features:
            return components.features['smart_money_strength']
            
        # Fallback: chercher des attributs similaires
        for attr_name in ['volume_confirmation', 'order_book_imbalance', 'sierra_pattern_strength']:
            if hasattr(components.features, attr_name):
                base_value = getattr(components.features, attr_name, 0.5)
                # Simulation smart money basée sur autres features
                return min(base_value * 0.8, 0.9)
            elif isinstance(components.features, dict) and attr_name in components.features:
                base_value = components.features[attr_name]
                return min(base_value * 0.8, 0.9)
        
        return None

    def _create_smart_money_analysis(self, smart_money_feature: float):
        """Crée un objet d'analyse Smart Money compatible"""
        
        class SmartMoneyAnalysis:
            def __init__(self, feature_value):
                self.smart_money_score = (feature_value - 0.5) * 2  # Conversion vers [-1,1]
                self.signal_type = 'INSTITUTIONAL_BUYING' if feature_value > 0.6 else 'NEUTRAL'
                self.confidence = feature_value
                self.large_trades_count = 3 if feature_value > 0.6 else 0
        
        return SmartMoneyAnalysis(smart_money_feature)

    # ===== ANALYSE ML ENSEMBLE FILTER =====
    
    def analyze_ml_ensemble_filter(self,
                                   market_data: MarketData,
                                   components: SignalComponents):
        """
        🎯 TECHNIQUE #3: ANALYSE ML ENSEMBLE FILTER
        
        Filtre ML pour éliminer faux signaux avec ensemble de modèles
        """
        try:
            if not self.ml_ensemble_enabled or not self.ml_ensemble:
                components.ml_ensemble_prediction = None
                components.ml_ensemble_confidence = 0.0
                components.ml_ensemble_approved = False
                return

            if not components.features:
                components.ml_ensemble_prediction = None
                components.ml_ensemble_confidence = 0.0
                components.ml_ensemble_approved = False
                return

            # ✅ FIX: Préparation features pour ML avec gestion objet/dict
            ml_features = self._prepare_ml_features(components)

            # 🎯 PRÉDICTION ML ENSEMBLE
            prediction = self.ml_ensemble.predict_signal_quality(ml_features)

            # Stockage résultats
            components.ml_ensemble_prediction = prediction
            components.ml_ensemble_confidence = getattr(prediction, 'confidence', 0.0)
            components.ml_ensemble_approved = getattr(prediction, 'signal_approved', False)

            logger.debug(f"🎯 ML Ensemble: Confidence={components.ml_ensemble_confidence:.3f}, "
                        f"Approved={components.ml_ensemble_approved}")

        except Exception as e:
            logger.warning(f"Erreur ML Ensemble analysis: {e}")
            components.ml_ensemble_prediction = None
            components.ml_ensemble_confidence = 0.0
            components.ml_ensemble_approved = False

    def _prepare_ml_features(self, components: SignalComponents) -> Dict[str, float]:
        """Prépare les features pour ML de manière robuste"""
        
        ml_features = {}
        
        # Mapping des features disponibles vers features ML
        feature_mappings = {
            'momentum_flow': 'vwap_trend_signal',
            'volume_profile': 'volume_confirmation',
            'trend_alignment': 'sierra_pattern_strength',
            'support_resistance': 'level_proximity',
            'volatility_regime': 'session_context',
            'time_factor': 'session_context'
        }
        
        for ml_key, feature_attr in feature_mappings.items():
            if hasattr(components.features, feature_attr):
                ml_features[ml_key] = getattr(components.features, feature_attr, 0.5)
            elif isinstance(components.features, dict):
                ml_features[ml_key] = components.features.get(feature_attr, 0.5)
            else:
                ml_features[ml_key] = 0.5
        
        # Ajout des scores calculés
        ml_features['confluence_score'] = components.mtf_confluence_score or 0.5
        ml_features['market_regime_score'] = components.smart_money_confidence or 0.5
        
        return ml_features

    # ===== ANALYSE GAMMA CYCLES =====
    
    def analyze_gamma_cycles(self,
                             market_data: MarketData,
                             components: SignalComponents):
        """
        🎯 TECHNIQUE #4: ANALYSE GAMMA EXPIRATION CYCLES
        
        Analyse cycles gamma pour optimisation temporelle trading
        """
        try:
            if not self.gamma_cycles_enabled or not self.gamma_analyzer:
                components.gamma_cycle_analysis = None
                components.gamma_adjustment_factor = 1.0
                components.gamma_phase = None
                return

            # ✅ CORRECTION: Analyse cycle gamma avec gestion d'erreur robuste
            try:
                gamma_analysis = self.gamma_analyzer.analyze_gamma_cycle(market_data.timestamp)
            except Exception as gamma_error:
                logger.debug(f"Erreur analyse gamma spécifique: {gamma_error}")
                # Fallback avec analyse basique
                gamma_analysis = self._create_fallback_gamma_analysis()

            # Stockage résultats
            components.gamma_cycle_analysis = gamma_analysis
            components.gamma_adjustment_factor = getattr(gamma_analysis, 'adjustment_factor', 1.0)
            components.gamma_phase = getattr(gamma_analysis, 'gamma_phase', None)

            logger.debug(f"🎯 Gamma Cycles: Phase={getattr(gamma_analysis, 'gamma_phase', 'unknown')}, "
                        f"Factor={components.gamma_adjustment_factor:.2f}")

        except Exception as e:
            logger.warning(f"Erreur Gamma Cycles analysis: {e}")
            components.gamma_cycle_analysis = None
            components.gamma_adjustment_factor = 1.0
            components.gamma_phase = None

    def _create_fallback_gamma_analysis(self):
        """Crée une analyse gamma de fallback"""
        
        class FallbackGammaAnalysis:
            def __init__(self):
                self.adjustment_factor = 1.0
                self.gamma_phase = "normal"
                self.expiry_distance = 7  # jours
                
        return FallbackGammaAnalysis()

    # ===== HELPER METHODS =====
    
    def _estimate_volatility(self, market_data: MarketData) -> float:
        """Estimation rapide volatilité pour MTF"""
        # Utilise range de la barre comme proxy volatilité
        bar_range = market_data.high - market_data.low
        avg_range = 15.0  # Range moyen ES en points
        return min(bar_range / avg_range, 2.0)

    def _detect_session_phase(self, market_data: MarketData) -> str:
        """Détection phase de session pour MTF"""
        hour = market_data.timestamp.hour

        if 9 <= hour <= 10:
            return "US_OPEN"
        elif 10 <= hour <= 15:
            return "US_SESSION"
        elif 15 <= hour <= 16:
            return "US_CLOSE"
        else:
            return "OVERNIGHT"

    # ===== ANALYSE COMPLÈTE =====
    
    def analyze_all_techniques(self,
                               market_data: MarketData,
                               order_flow: Optional[OrderFlowData],
                               components: SignalComponents):
        """
        Analyse toutes les techniques disponibles en séquence
        """
        start_time = time.time()
        
        # 🆕 PHASE 3: MTF Elite Confluence
        if self.mtf_enabled:
            self.analyze_mtf_elite_confluence(market_data, components)
        
        # 🎯 TECHNIQUE #2: Smart Money Flow
        if self.smart_money_enabled:
            self.analyze_smart_money_flows(market_data, order_flow, components)
        
        # 🎯 TECHNIQUE #3: ML Ensemble Filter
        if self.ml_ensemble_enabled:
            self.analyze_ml_ensemble_filter(market_data, components)
        
        # 🎯 TECHNIQUE #4: Gamma Cycles
        if self.gamma_cycles_enabled:
            self.analyze_gamma_cycles(market_data, components)
        
        total_time = (time.time() - start_time) * 1000
        logger.debug(f"🎯 Toutes techniques analysées en {total_time:.2f}ms")

    def get_techniques_status(self) -> Dict[str, bool]:
        """Retourne le statut de toutes les techniques"""
        return {
            'mtf_enabled': self.mtf_enabled,
            'smart_money_enabled': self.smart_money_enabled,
            'ml_ensemble_enabled': self.ml_ensemble_enabled,
            'gamma_cycles_enabled': self.gamma_cycles_enabled
        }

# ===== EXPORTS =====
__all__ = [
    'TechniqueAnalyzers'
]