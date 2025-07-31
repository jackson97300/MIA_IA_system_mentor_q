"""
strategies/signal_core/stats_tracker.py

Tracker de statistiques et performance avec toutes les techniques Elite
Extrait et nettoyé du fichier original signal_generator.py (lignes 2200-2788)
"""

import time
from typing import Dict, List, Any, Optional
from collections import defaultdict
from core.logger import get_logger

# Imports depuis base_types
from .base_types import SignalSource, QualityLevel

# Imports depuis signal_components
from .signal_components import SignalComponents, FinalSignal

logger = get_logger(__name__)

# ===== STATS TRACKER =====

class StatsTracker:
    """
    Tracker de statistiques et performance avec toutes les techniques Elite
    
    Suit les performances de chaque technique, les fréquences de signaux,
    les taux de cache, et les métriques de performance globales.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation du tracker de statistiques"""
        self.config = config or {}
        
        # === STATISTIQUES PRINCIPALES ===
        self.stats = {
            'signals_generated': 0,
            'signals_executed': 0,
            'avg_generation_time_ms': 0.0,
            'cache_hit_rate': 0.0,
            'quality_distribution': defaultdict(int),
            'regime_distribution': defaultdict(int),
            'success_by_source': defaultdict(list),
            
            # === PRIORITÉ #2: STATS BATTLE NAVALE ===
            'battle_navale_signals': 0,
            'threshold_boost_stats': defaultdict(int),
            
            # 🆕 PHASE 3: STATS MTF ===
            'mtf_elite_signals': 0,
            'mtf_standard_signals': 0,
            'mtf_processing_time_ms': 0.0,
            
            # 🎯 TECHNIQUE #2: STATS SMART MONEY ===
            'smart_money_signals': 0,
            'institutional_signals': 0,
            'smart_money_processing_time_ms': 0.0,
            'smart_money_alignment_count': 0,
            
            # 🎯 TECHNIQUE #3: STATS ML ENSEMBLE ===
            'ml_ensemble_signals': 0,
            'ml_high_confidence_signals': 0,
            'ml_ensemble_processing_time_ms': 0.0,
            'ml_ensemble_approval_rate': 0.0,
            
            # 🎯 TECHNIQUE #4: STATS GAMMA CYCLES ===
            'gamma_optimized_signals': 0,
            'gamma_peak_signals': 0,
            'gamma_cycles_processing_time_ms': 0.0,
            'gamma_cycles_impact_positive': 0,
            'gamma_cycles_impact_negative': 0
        }

        # === TRACKING FRÉQUENCE SIGNAUX ===
        self.signal_frequency_tracking = {
            'old_threshold_signals': 0,  # Signaux avec anciens seuils (0.35/-0.35)
            'new_threshold_signals': 0,  # Signaux avec nouveaux seuils (0.25/-0.25)
            'frequency_boost_pct': 0.0,  # Pourcentage d'augmentation
            
            # 🆕 PHASE 3: Tracking MTF
            'mtf_elite_signals': 0,
            'mtf_standard_signals': 0,
            'mtf_boost_pct': 0.0,
            
            # 🎯 TECHNIQUE #2: Tracking Smart Money
            'smart_money_signals': 0,
            'institutional_signals': 0,
            'smart_money_boost_pct': 0.0,
            
            # 🎯 TECHNIQUE #3: Tracking ML Ensemble
            'ml_ensemble_signals': 0,
            'ml_high_confidence_signals': 0,
            'ml_ensemble_boost_pct': 0.0,
            
            # 🎯 TECHNIQUE #4: Tracking Gamma Cycles
            'gamma_optimized_signals': 0,
            'gamma_peak_signals': 0,
            'gamma_cycles_boost_pct': 0.0
        }

        # Cache stats tracking
        self._last_cache_stats_update = time.time()
        
        logger.debug("StatsTracker initialisé avec toutes les métriques Elite")

    def update_stats(self, signal: FinalSignal, execution_time: float):
        """Mise à jour statistiques avec cache + MTF + Smart Money + ML + Gamma"""
        
        self.stats['signals_generated'] += 1

        # Rolling average temps génération
        count = self.stats['signals_generated']
        prev_avg = self.stats['avg_generation_time_ms']
        self.stats['avg_generation_time_ms'] = ((prev_avg * (count - 1)) + execution_time) / count

        # Distribution qualité
        self.stats['quality_distribution'][signal.quality_level.value] += 1

        # Distribution régime
        self.stats['regime_distribution'][signal.regime.value] += 1

        # === PRIORITÉ #2: STATS BATTLE NAVALE ===
        if signal.source == SignalSource.BATTLE_NAVALE:
            self.stats['battle_navale_signals'] += 1

        # 🆕 PHASE 3: STATS MTF ELITE
        if signal.source == SignalSource.MTF_ELITE_CONFLUENCE:
            self.stats['mtf_elite_signals'] += 1
        elif signal.meets_mtf_elite_threshold():
            self.stats['mtf_standard_signals'] += 1

        # 🎯 TECHNIQUE #2: STATS SMART MONEY
        if signal.source == SignalSource.SMART_MONEY_INSTITUTIONAL:
            self.stats['smart_money_signals'] += 1

        if signal.is_institutional_signal():
            self.stats['institutional_signals'] += 1

        # 🎯 TECHNIQUE #3: STATS ML ENSEMBLE
        if signal.meets_ml_ensemble_threshold():
            self.stats['ml_ensemble_signals'] += 1

        # Calcul approval rate ML
        total_ml_predictions = self.stats['ml_ensemble_signals']
        if total_ml_predictions > 0:
            self.stats['ml_ensemble_approval_rate'] = total_ml_predictions / count

        # 🎯 TECHNIQUE #4: STATS GAMMA CYCLES
        if signal.meets_gamma_optimization_criteria():
            self.stats['gamma_optimized_signals'] += 1

        if signal.is_gamma_peak_signal():
            self.stats['gamma_peak_signals'] += 1

        # Impact positif/négatif gamma
        if signal.components.gamma_adjustment_factor:
            if signal.components.gamma_adjustment_factor > 1.0:
                self.stats['gamma_cycles_impact_positive'] += 1
            elif signal.components.gamma_adjustment_factor < 1.0:
                self.stats['gamma_cycles_impact_negative'] += 1

        # Tracking par source
        from .base_types import SignalDecision
        if signal.decision in [SignalDecision.EXECUTE_LONG, SignalDecision.EXECUTE_SHORT]:
            self.stats['signals_executed'] += 1
            self._track_signal_details(signal)

        logger.debug(f"Stats mis à jour: {count} signaux générés, {self.stats['signals_executed']} exécutés")

    def _track_signal_details(self, signal: FinalSignal):
        """Track détails du signal pour analyse"""
        
        signal_details = {
            'timestamp': signal.timestamp,
            'confidence': signal.confidence,
            'cache_hits': signal.cache_hits,
            'battle_navale_strength': signal.get_battle_navale_strength(),
            'mtf_confluence_strength': signal.get_mtf_confluence_strength(),
            'smart_money_strength': signal.get_smart_money_strength(),
            'institutional_score': signal.get_smart_money_institutional_score(),
            'ml_ensemble_confidence': signal.get_ml_ensemble_confidence(),
            'gamma_adjustment_factor': signal.get_gamma_adjustment_factor(),
            'gamma_phase': signal.get_gamma_phase(),
            'is_elite': signal.is_elite_signal(),
            'is_institutional': signal.is_institutional_signal(),
            'is_ml_validated': signal.is_ml_validated_signal(),
            'is_gamma_optimized': signal.meets_gamma_optimization_criteria(),
            'is_ultimate_elite': signal.is_ultimate_elite_signal(),
            'has_smart_money_alignment': signal.has_smart_money_alignment(),
            'has_ml_high_confidence': signal.has_ml_high_confidence(),
            'is_gamma_peak': signal.is_gamma_peak_signal()
        }
        
        self.stats['success_by_source'][signal.source.value].append(signal_details)

    def track_signal_frequency_v5(self, components: SignalComponents):
        """
        🎯 TECHNIQUE #4: TRACKING FRÉQUENCE AVEC GAMMA CYCLES
        
        Version finale incluant tracking Gamma Cycles + ML + Smart Money + MTF Elite
        """
        
        # PRIORITÉ #2: Tracking original
        self._track_signal_frequency_priority2(components)

        # 🆕 PHASE 3: Tracking MTF
        self._track_mtf_frequency(components)

        # 🎯 TECHNIQUE #2: Tracking Smart Money
        self._track_smart_money_frequency(components)

        # 🎯 TECHNIQUE #3: Tracking ML Ensemble
        self._track_ml_ensemble_frequency(components)

        # 🎯 TECHNIQUE #4: Tracking Gamma Cycles
        self._track_gamma_cycles_frequency(components)

    def _track_signal_frequency_priority2(self, components: SignalComponents):
        """PRIORITÉ #2: Tracking fréquence signaux Battle Navale"""
        
        if not components.battle_navale:
            return

        battle_signal = getattr(components.battle_navale, 'battle_navale_signal', 0.5)

        # Test anciens seuils (0.35/-0.35)
        old_threshold_signal = (battle_signal > 0.35) or (battle_signal < -0.35)

        # Test nouveaux seuils (0.25/-0.25)
        from .base_types import MIN_BATTLE_NAVALE_SIGNAL_LONG, MIN_BATTLE_NAVALE_SIGNAL_SHORT
        new_threshold_signal = (battle_signal > MIN_BATTLE_NAVALE_SIGNAL_LONG) or \
                              (battle_signal < MIN_BATTLE_NAVALE_SIGNAL_SHORT)

        if old_threshold_signal:
            self.signal_frequency_tracking['old_threshold_signals'] += 1

        if new_threshold_signal:
            self.signal_frequency_tracking['new_threshold_signals'] += 1

        # Calcul boost fréquence
        old_count = self.signal_frequency_tracking['old_threshold_signals']
        new_count = self.signal_frequency_tracking['new_threshold_signals']

        if old_count > 0:
            boost_pct = ((new_count - old_count) / old_count) * 100
            self.signal_frequency_tracking['frequency_boost_pct'] = boost_pct

    def _track_mtf_frequency(self, components: SignalComponents):
        """🆕 PHASE 3: Tracking MTF"""
        
        if components.mtf_confluence_score is None:
            return
            
        from .base_types import MIN_MTF_ELITE_SCORE, MIN_MTF_STANDARD_SCORE
        mtf_score = abs(components.mtf_confluence_score)

        if mtf_score > MIN_MTF_ELITE_SCORE:
            self.signal_frequency_tracking['mtf_elite_signals'] += 1
        elif mtf_score > MIN_MTF_STANDARD_SCORE:
            self.signal_frequency_tracking['mtf_standard_signals'] += 1

        # Calcul boost MTF
        total_mtf = (self.signal_frequency_tracking['mtf_elite_signals'] +
                    self.signal_frequency_tracking['mtf_standard_signals'])
        total_signals = self.stats['signals_generated']

        if total_signals > 0:
            mtf_boost = (total_mtf / total_signals) * 100
            self.signal_frequency_tracking['mtf_boost_pct'] = mtf_boost

    def _track_smart_money_frequency(self, components: SignalComponents):
        """🎯 TECHNIQUE #2: Tracking Smart Money"""
        
        if components.smart_money_confidence is None:
            return
            
        from .base_types import MIN_SMART_MONEY_CONFIDENCE, MIN_SMART_MONEY_INSTITUTIONAL_SCORE
        smart_money_conf = components.smart_money_confidence

        if smart_money_conf > MIN_SMART_MONEY_CONFIDENCE:
            self.signal_frequency_tracking['smart_money_signals'] += 1

            # Check flux institutionnel
            if (components.smart_money_institutional_score and
                components.smart_money_institutional_score > MIN_SMART_MONEY_INSTITUTIONAL_SCORE):
                self.signal_frequency_tracking['institutional_signals'] += 1

        # Calcul boost Smart Money
        total_smart_money = self.signal_frequency_tracking['smart_money_signals']
        total_signals = self.stats['signals_generated']

        if total_signals > 0:
            smart_money_boost = (total_smart_money / total_signals) * 100
            self.signal_frequency_tracking['smart_money_boost_pct'] = smart_money_boost

    def _track_ml_ensemble_frequency(self, components: SignalComponents):
        """🎯 TECHNIQUE #3: Tracking ML Ensemble"""
        
        if components.ml_ensemble_prediction is None:
            return
            
        ml_prediction = components.ml_ensemble_prediction

        if getattr(ml_prediction, 'signal_approved', False):
            self.signal_frequency_tracking['ml_ensemble_signals'] += 1

            # Check haute confidence
            if getattr(ml_prediction, 'confidence', 0) > 0.85:
                self.signal_frequency_tracking['ml_high_confidence_signals'] += 1

        # Calcul boost ML Ensemble
        total_ml_signals = self.signal_frequency_tracking['ml_ensemble_signals']
        total_signals = self.stats['signals_generated']

        if total_signals > 0:
            ml_boost = (total_ml_signals / total_signals) * 100
            self.signal_frequency_tracking['ml_ensemble_boost_pct'] = ml_boost

    def _track_gamma_cycles_frequency(self, components: SignalComponents):
        """🎯 TECHNIQUE #4: Tracking Gamma Cycles"""
        
        if components.gamma_cycle_analysis is None:
            return
            
        from .base_types import GammaPhase
        gamma_analysis = components.gamma_cycle_analysis
        gamma_phase = getattr(gamma_analysis, 'gamma_phase', None)

        # Signaux optimisés gamma (phases favorables)
        if gamma_phase in [GammaPhase.GAMMA_PEAK, GammaPhase.GAMMA_MODERATE, GammaPhase.POST_EXPIRY]:
            self.signal_frequency_tracking['gamma_optimized_signals'] += 1

        # Signaux pendant gamma peak spécifiquement
        if gamma_phase == GammaPhase.GAMMA_PEAK:
            self.signal_frequency_tracking['gamma_peak_signals'] += 1

        # Calcul boost Gamma Cycles
        total_gamma_signals = self.signal_frequency_tracking['gamma_optimized_signals']
        total_signals = self.stats['signals_generated']

        if total_signals > 0:
            gamma_boost = (total_gamma_signals / total_signals) * 100
            self.signal_frequency_tracking['gamma_cycles_boost_pct'] = gamma_boost

    def update_cache_stats_periodically(self, feature_calculator):
        """Met à jour stats cache toutes les 5 minutes"""
        
        now = time.time()
        if now - self._last_cache_stats_update > 300:  # 5 minutes
            if hasattr(feature_calculator, 'get_cache_stats'):
                cache_stats = feature_calculator.get_cache_stats()
                self.stats['cache_hit_rate'] = cache_stats.get('hit_rate', 0)

                logger.info(f"[STATS] Cache Stats Update: "
                            f"Hit rate={cache_stats.get('hit_rate', 0):.1%}, "
                            f"Avg time={cache_stats.get('avg_calculation_time_ms', 0):.2f}ms, "
                            f"Total calcs={cache_stats.get('total_calculations', 0)}")

            self._last_cache_stats_update = now

    def get_performance_stats(self, feature_calculator=None) -> Dict[str, Any]:
        """Statistiques performance avec cache, PRIORITÉ #2, PHASE 3, TOUTES TECHNIQUES"""
        
        executed_rate = self.stats['signals_executed'] / max(1, self.stats['signals_generated'])

        # Cache stats si disponibles
        cache_stats = {}
        if feature_calculator and hasattr(feature_calculator, 'get_cache_stats'):
            cache_stats = feature_calculator.get_cache_stats()

        return {
            'signals_generated': self.stats['signals_generated'],
            'signals_executed': self.stats['signals_executed'],
            'execution_rate': executed_rate,
            'avg_generation_time_ms': self.stats['avg_generation_time_ms'],
            'quality_distribution': dict(self.stats['quality_distribution']),
            'regime_distribution': dict(self.stats['regime_distribution']),
            
            'cache_performance': {
                'hit_rate': cache_stats.get('hit_rate', 0),
                'avg_calc_time_ms': cache_stats.get('avg_calculation_time_ms', 0),
                'total_calculations': cache_stats.get('total_calculations', 0),
                'min_calc_time_ms': cache_stats.get('min_calculation_time_ms', 0),
                'max_calc_time_ms': cache_stats.get('max_calculation_time_ms', 0)
            },
            
            # === PRIORITÉ #2: STATS ===
            'priority_2_stats': {
                'battle_navale_signals': self.stats['battle_navale_signals'],
                'signal_frequency_tracking': self.signal_frequency_tracking,
                'thresholds_used': {
                    'long_threshold': 0.25,
                    'short_threshold': -0.25
                }
            },
            
            # 🆕 PHASE 3: STATS MTF
            'phase_3_stats': {
                'mtf_elite_signals': self.stats['mtf_elite_signals'],
                'mtf_standard_signals': self.stats['mtf_standard_signals'],
                'mtf_processing_time_ms': self.stats.get('mtf_processing_time_ms', 0.0)
            },
            
            # 🎯 TECHNIQUE #2: STATS SMART MONEY
            'technique_2_stats': {
                'smart_money_signals': self.stats['smart_money_signals'],
                'institutional_signals': self.stats['institutional_signals'],
                'smart_money_processing_time_ms': self.stats.get('smart_money_processing_time_ms', 0.0),
                'smart_money_alignment_count': self.stats['smart_money_alignment_count']
            },
            
            # 🎯 TECHNIQUE #3: STATS ML ENSEMBLE
            'technique_3_stats': {
                'ml_ensemble_signals': self.stats['ml_ensemble_signals'],
                'ml_high_confidence_signals': self.stats['ml_high_confidence_signals'],
                'ml_ensemble_processing_time_ms': self.stats.get('ml_ensemble_processing_time_ms', 0.0),
                'ml_ensemble_approval_rate': self.stats.get('ml_ensemble_approval_rate', 0.0)
            },
            
            # 🎯 TECHNIQUE #4: STATS GAMMA CYCLES
            'technique_4_stats': {
                'gamma_optimized_signals': self.stats['gamma_optimized_signals'],
                'gamma_peak_signals': self.stats['gamma_peak_signals'],
                'gamma_cycles_processing_time_ms': self.stats.get('gamma_cycles_processing_time_ms', 0.0),
                'gamma_cycles_impact_positive': self.stats['gamma_cycles_impact_positive'],
                'gamma_cycles_impact_negative': self.stats['gamma_cycles_impact_negative']
            }
        }

    def get_priority_2_summary(self) -> Dict[str, Any]:
        """PRIORITÉ #2: Résumé impact nouveaux seuils"""
        
        tracking = self.signal_frequency_tracking

        return {
            'thresholds': {
                'old': {'long': 0.35, 'short': -0.35},
                'new': {'long': 0.25, 'short': -0.25}
            },
            'signal_counts': {
                'old_threshold_signals': tracking['old_threshold_signals'],
                'new_threshold_signals': tracking['new_threshold_signals']
            },
            'frequency_boost': {
                'percentage': tracking['frequency_boost_pct'],
                'target': 150.0,
                'status': '✅ Atteint' if tracking['frequency_boost_pct'] >= 140 else '🔄 En cours'
            },
            'total_signals_generated': self.stats['signals_generated'],
            'battle_navale_signals': self.stats['battle_navale_signals']
        }

    def get_techniques_summary(self) -> Dict[str, Any]:
        """Résumé performance de toutes les techniques Elite"""
        
        return {
            'phase_3_mtf': self._get_mtf_summary(),
            'technique_2_smart_money': self._get_smart_money_summary(),
            'technique_3_ml_ensemble': self._get_ml_ensemble_summary(),
            'technique_4_gamma_cycles': self._get_gamma_cycles_summary()
        }

    def _get_mtf_summary(self) -> Dict[str, Any]:
        """🆕 PHASE 3: Résumé MTF"""
        tracking = self.signal_frequency_tracking
        
        return {
            'mtf_signal_counts': {
                'elite_signals': tracking['mtf_elite_signals'],
                'standard_signals': tracking['mtf_standard_signals'],
                'total_mtf_signals': tracking['mtf_elite_signals'] + tracking['mtf_standard_signals']
            },
            'boost_percentage': tracking['mtf_boost_pct'],
            'processing_time_ms': self.stats.get('mtf_processing_time_ms', 0.0)
        }

    def _get_smart_money_summary(self) -> Dict[str, Any]:
        """🎯 TECHNIQUE #2: Résumé Smart Money"""
        tracking = self.signal_frequency_tracking
        
        return {
            'smart_money_signal_counts': {
                'smart_money_signals': tracking['smart_money_signals'],
                'institutional_signals': tracking['institutional_signals'],
                'alignment_count': self.stats['smart_money_alignment_count']
            },
            'boost_percentage': tracking['smart_money_boost_pct'],
            'processing_time_ms': self.stats.get('smart_money_processing_time_ms', 0.0)
        }

    def _get_ml_ensemble_summary(self) -> Dict[str, Any]:
        """🎯 TECHNIQUE #3: Résumé ML Ensemble"""
        tracking = self.signal_frequency_tracking
        
        return {
            'ml_ensemble_signal_counts': {
                'ml_ensemble_signals': tracking['ml_ensemble_signals'],
                'ml_high_confidence_signals': tracking['ml_high_confidence_signals']
            },
            'boost_percentage': tracking['ml_ensemble_boost_pct'],
            'approval_rate': self.stats.get('ml_ensemble_approval_rate', 0.0),
            'processing_time_ms': self.stats.get('ml_ensemble_processing_time_ms', 0.0)
        }

    def _get_gamma_cycles_summary(self) -> Dict[str, Any]:
        """🎯 TECHNIQUE #4: Résumé Gamma Cycles"""
        tracking = self.signal_frequency_tracking
        
        return {
            'gamma_signal_counts': {
                'gamma_optimized_signals': tracking['gamma_optimized_signals'],
                'gamma_peak_signals': tracking['gamma_peak_signals']
            },
            'boost_percentage': tracking['gamma_cycles_boost_pct'],
            'impact_positive': self.stats['gamma_cycles_impact_positive'],
            'impact_negative': self.stats['gamma_cycles_impact_negative'],
            'processing_time_ms': self.stats.get('gamma_cycles_processing_time_ms', 0.0)
        }

    def reset_stats(self):
        """Reset toutes les statistiques"""
        
        # Reset stats principales
        for key in self.stats:
            if isinstance(self.stats[key], (int, float)):
                self.stats[key] = 0 if isinstance(self.stats[key], int) else 0.0
            elif isinstance(self.stats[key], defaultdict):
                self.stats[key].clear()

        # Reset tracking fréquence
        for key in self.signal_frequency_tracking:
            if isinstance(self.signal_frequency_tracking[key], (int, float)):
                self.signal_frequency_tracking[key] = 0 if isinstance(self.signal_frequency_tracking[key], int) else 0.0

        logger.info("✅ Toutes les statistiques ont été reset")

# ===== EXPORTS =====
__all__ = [
    'StatsTracker'
]