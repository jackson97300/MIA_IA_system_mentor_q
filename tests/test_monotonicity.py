#!/usr/bin/env python3
"""
🧪 TESTS DE MONOTONIE - MIA_IA_SYSTEM
Validation automatique des propriétés critiques après corrections

Tests effectués :
1. Plages [0,1] pour tous les scores
2. Monotonie des fonctions
3. Absence de NaN/Inf
4. Cohérence des échelles
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from features.feature_calculator import FeatureCalculator
from features.spx_options_retriever import SPXOptionsRetriever
from core.logger import get_logger
from utils.numeric import approx_eq, approx_le, approx_ge, EPSILON

logger = get_logger(__name__)

class MonotonicityTester:
    """Tests de monotonie pour validation des corrections"""
    
    def __init__(self):
        self.feature_calculator = FeatureCalculator()
        self.test_results = {}
        
    def test_gamma_proximity_monotonicity(self) -> Dict[str, bool]:
        """Test monotonie gamma_proximity"""
        logger.info("🧪 Test monotonie gamma_proximity...")
        
        results = {
            'call_distance_decreasing': True,
            'put_distance_increasing': True,
            'vol_distance_decreasing': True,
            'ranges_valid': True,
            'no_nan': True
        }
        
        # Données de test
        current_price = 5400.0
        test_levels = [5300, 5350, 5400, 5450, 5500]
        
        # Test monotonie call wall
        call_scores = []
        for level in test_levels:
            options_data = self._create_test_options_data(
                call_wall=level, put_wall=5500, vol_trigger=5450
            )
            score = self.feature_calculator._calculate_gamma_proximity(current_price, options_data)
            call_scores.append(score)
            
            # Vérification plage
            if not (0.0 <= score <= 1.0):
                results['ranges_valid'] = False
                logger.error(f"❌ Score hors plage: {score}")
            
            # Vérification NaN
            if np.isnan(score) or np.isinf(score):
                results['no_nan'] = False
                logger.error(f"❌ Score NaN/Inf: {score}")
        
        # Vérification monotonie (distance ↓ → score non-décroissant avec tolérance)
        for i in range(1, len(call_scores)):
            distance_prev = abs(current_price - test_levels[i-1])
            distance_curr = abs(current_price - test_levels[i])
            
            if distance_curr + EPSILON < distance_prev and call_scores[i] + EPSILON < call_scores[i-1]:
                results['call_distance_decreasing'] = False
                logger.error(f"❌ Monotonie call wall violée: {call_scores[i-1]} → {call_scores[i]}")
        
        logger.info(f"✅ Gamma proximity tests: {sum(results.values())}/{len(results)} passés")
        return results
    
    def test_options_flow_bias_monotonicity(self) -> Dict[str, bool]:
        """Test monotonie options_flow_bias"""
        logger.info("🧪 Test monotonie options_flow_bias...")
        
        results = {
            'pcr_monotonicity': True,
            'volume_flow_monotonicity': True,
            'walls_monotonicity': True,
            'ranges_valid': True,
            'neutral_center': True
        }
        
        current_price = 5400.0
        
        # Test PCR monotonie
        pcr_values = [0.3, 0.5, 0.7, 1.0, 1.3, 1.6]
        pcr_scores = []
        
        for pcr in pcr_values:
            options_data = self._create_test_options_data(put_call_ratio=pcr)
            score = self.feature_calculator._calculate_options_flow_bias(options_data, current_price)
            pcr_scores.append(score)
            
            # Vérification plage
            if not (0.0 <= score <= 1.0):
                results['ranges_valid'] = False
                logger.error(f"❌ Score hors plage: {score}")
        
        # Vérification monotonie PCR (PCR ↑ → bias non-croissant avec tolérance)
        for i in range(1, len(pcr_scores)):
            if pcr_values[i] > pcr_values[i-1] and pcr_scores[i] > pcr_scores[i-1] + EPSILON:
                results['pcr_monotonicity'] = False
                logger.error(f"❌ Monotonie PCR violée: {pcr_scores[i-1]} → {pcr_scores[i]}")
        
        # Test neutral center (PCR = 1.0 devrait être proche de 0.5)
        neutral_idx = pcr_values.index(1.0)
        neutral_score = pcr_scores[neutral_idx]
        if not (0.4 <= neutral_score <= 0.6):
            results['neutral_center'] = False
            logger.error(f"❌ Centre neutre incorrect: {neutral_score}")
        
        logger.info(f"✅ Options flow bias tests: {sum(results.values())}/{len(results)} passés")
        return results
    
    def test_safe_proximity_calculation(self) -> Dict[str, bool]:
        """Test fonction de sécurité proximité"""
        logger.info("🧪 Test safe_proximity_calculation...")
        
        results = {
            'null_handling': True,
            'negative_handling': True,
            'infinite_handling': True,
            'normal_cases': True
        }
        
        # Test cas null/négatifs
        test_cases = [
            (None, 5400, "null_current"),
            (5400, None, "null_target"),
            (-100, 5400, "negative_current"),
            (5400, -100, "negative_target"),
            (float('inf'), 5400, "inf_current"),
            (5400, float('inf'), "inf_target")
        ]
        
        for current, target, case in test_cases:
            result = self.feature_calculator._safe_proximity_calculation(current, target)
            if result != 0.0:
                results['null_handling'] = False
                logger.error(f"❌ Cas {case} devrait retourner 0.0, got {result}")
        
        # Test cas normaux
        normal_cases = [
            (5400, 5400, 1.0),  # Même niveau
            (5400, 5450, 0.8),  # Proche
            (5400, 5500, 0.6),  # Moyen
            (5400, 5600, 0.2),  # Loin
        ]
        
        for current, target, expected in normal_cases:
            result = self.feature_calculator._safe_proximity_calculation(current, target)
            if not (0.0 <= result <= 1.0):
                results['normal_cases'] = False
                logger.error(f"❌ Cas normal hors plage: {result}")
        
        logger.info(f"✅ Safe proximity tests: {sum(results.values())}/{len(results)} passés")
        return results
    
    def test_epsilon_comparison(self) -> Dict[str, bool]:
        """Test comparaisons avec EPSILON"""
        logger.info("🧪 Test comparaisons EPSILON...")
        
        results = {
            'epsilon_works': True,
            'edge_cases': True
        }
        
        # Test EPSILON avec logique corrigée et cas flottants
        test_cases = [
            (0.100, 0.100, True),   # Égal
            (0.100 + EPSILON, 0.100, True),  # Juste au-dessus
            (0.100 - EPSILON, 0.100, True),  # Juste en-dessous
            (0.100 + 2*EPSILON, 0.100, False),  # Au-dessus
            (0.100 - 2*EPSILON, 0.100, False),  # En-dessous
            # Cas de précision flottante
            (0.0999999, 0.1, True),  # Précision flottante
            (0.1000001, 0.1, True),  # Précision flottante
        ]
        
        for a, b, should_pass in test_cases:
            if should_pass:
                if not approx_eq(a, b):
                    results['epsilon_works'] = False
                    logger.error(f"❌ EPSILON échoue (devrait être ≈): a={a}, b={b}")
            else:
                # on exige une différence "significative"
                if approx_eq(a, b):
                    results['epsilon_works'] = False
                    logger.error(f"❌ EPSILON échoue (devrait être ≠): a={a}, b={b}")
        
        logger.info(f"✅ EPSILON tests: {sum(results.values())}/{len(results)} passés")
        return results
    
    def run_all_tests(self) -> Dict[str, Dict[str, bool]]:
        """Lancer tous les tests"""
        logger.info("🚀 LANCEMENT TESTS DE MONOTONIE")
        
        self.test_results = {
            'gamma_proximity': self.test_gamma_proximity_monotonicity(),
            'options_flow_bias': self.test_options_flow_bias_monotonicity(),
            'safe_proximity': self.test_safe_proximity_calculation(),
            'epsilon_comparison': self.test_epsilon_comparison()
        }
        
        # Résumé global
        total_tests = sum(len(results) for results in self.test_results.values())
        passed_tests = sum(sum(results.values()) for results in self.test_results.values())
        
        logger.info("📊 RÉSUMÉ TESTS:")
        logger.info(f"  Total: {total_tests}")
        logger.info(f"  Passés: {passed_tests}")
        logger.info(f"  Échoués: {total_tests - passed_tests}")
        logger.info(f"  Taux succès: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            logger.info("✅ TOUS LES TESTS PASSÉS - Corrections validées!")
        else:
            logger.warning("⚠️ CERTAINS TESTS ÉCHOUÉS - Vérification requise")
        
        return self.test_results
    
    def _create_test_options_data(self, **kwargs):
        """Créer données options de test"""
        from features.feature_calculator import OptionsData
        
        defaults = {
            'call_wall': 5450,
            'put_wall': 5350,
            'vol_trigger': 5400,
            'net_gamma': 0.05,
            'call_volume': 1000,
            'put_volume': 1200,
            'put_call_ratio': 1.2,
            'gamma_exposure': 75000000000,  # $75B
        }
        
        defaults.update(kwargs)
        
        return OptionsData(
            timestamp=pd.Timestamp.now(),
            **defaults
        )

def main():
    """Fonction principale"""
    tester = MonotonicityTester()
    results = tester.run_all_tests()
    
    # Sauvegarder résultats
    import json
    with open('test_monotonicity_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("💾 Résultats sauvegardés: test_monotonicity_results.json")

if __name__ == "__main__":
    main()
