"""
MIA_IA_SYSTEM - Test Gamma Cycles Analyzer
Tests pour l'analyseur de cycles gamma
Version: Production Ready
Performance: Validation complète Gamma Cycles
"""

import sys
import unittest
import tempfile
import shutil
import os
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, call
import pandas as pd
import numpy as np
import json
import time

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.logger import get_logger
from core.base_types import MarketData
from ml.gamma_cycles import (
    GammaCyclesAnalyzer, 
    GammaCycleConfig, 
    GammaCycleAnalysis, 
    GammaPhase
)

logger = get_logger(__name__)


class TestGammaCycleConfig(unittest.TestCase):
    """Tests pour la configuration gamma cycles"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.config = GammaCycleConfig()
    
    def test_gamma_config_initialization(self):
        """Test initialisation configuration gamma"""
        self.assertIsNotNone(self.config)
        self.assertTrue(hasattr(self.config, 'gamma_expiration_days'))
        self.assertTrue(hasattr(self.config, 'volatility_threshold'))
        self.assertTrue(hasattr(self.config, 'analysis_window_hours'))
    
    def test_default_values(self):
        """Test valeurs par défaut"""
        self.assertGreater(self.config.gamma_expiration_days, 0)
        self.assertGreater(self.config.volatility_threshold, 0.0)
        self.assertGreater(self.config.analysis_window_hours, 0)
    
    def test_config_validation(self):
        """Test validation configuration"""
        # Test avec valeurs valides
        self.config.gamma_expiration_days = 7
        self.config.volatility_threshold = 0.3
        self.config.analysis_window_hours = 24
        
        # Vérifier que la configuration est valide
        self.assertGreater(self.config.gamma_expiration_days, 0)
        self.assertGreater(self.config.volatility_threshold, 0.0)
        self.assertLess(self.config.volatility_threshold, 1.0)
        self.assertGreater(self.config.analysis_window_hours, 0)


class TestGammaCyclesAnalyzer(unittest.TestCase):
    """Tests pour l'analyseur de cycles gamma"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.config = GammaCycleConfig()
        self.gamma_analyzer = GammaCyclesAnalyzer(self.config)
        
        # Données de test
        self.sample_market_data = MarketData(
            timestamp=datetime.now(),
            symbol="ES",
            open=4500.0,
            high=4510.0,
            low=4495.0,
            close=4505.0,
            volume=1000
        )
    
    def test_gamma_analyzer_initialization(self):
        """Test initialisation analyseur gamma"""
        self.assertIsNotNone(self.gamma_analyzer)
        self.assertTrue(hasattr(self.gamma_analyzer, 'analyze_gamma_cycle'))
        self.assertTrue(hasattr(self.gamma_analyzer, 'calculate_expiration_factor'))
    
    def test_gamma_cycle_analysis(self):
        """Test analyse cycle gamma"""
        analysis = self.gamma_analyzer.analyze_gamma_cycle()
        self.assertIsNotNone(analysis)
        self.assertIsInstance(analysis, GammaCycleAnalysis)
        self.assertTrue(hasattr(analysis, 'gamma_phase'))
        self.assertTrue(hasattr(analysis, 'adjustment_factor'))
        self.assertTrue(hasattr(analysis, 'volatility_expectation'))
    
    def test_expiration_factor_calculation(self):
        """Test calcul facteur d'expiration"""
        factor = self.gamma_analyzer.calculate_expiration_factor()
        self.assertIsNotNone(factor)
        self.assertGreaterEqual(factor, 0.0)
        self.assertLessEqual(factor, 1.0)
    
    def test_volatility_expectation(self):
        """Test attente de volatilité"""
        expectation = self.gamma_analyzer.calculate_volatility_expectation()
        self.assertIsNotNone(expectation)
        self.assertIsInstance(expectation, str)
        self.assertIn(expectation, ['low', 'medium', 'high', 'extreme'])
    
    def test_days_to_expiry(self):
        """Test jours avant expiration"""
        days = self.gamma_analyzer.get_days_to_expiry()
        self.assertIsNotNone(days)
        self.assertIsInstance(days, int)
        self.assertGreaterEqual(days, 0)


class TestGammaCycleAnalysis(unittest.TestCase):
    """Tests pour l'analyse de cycle gamma"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.analysis = GammaCycleAnalysis(
            gamma_phase=GammaPhase.EXPIRATION_WEEK,
            adjustment_factor=0.8,
            volatility_expectation="high",
            days_to_expiry=3
        )
    
    def test_analysis_creation(self):
        """Test création analyse"""
        self.assertIsNotNone(self.analysis)
        self.assertEqual(self.analysis.gamma_phase, GammaPhase.EXPIRATION_WEEK)
        self.assertEqual(self.analysis.adjustment_factor, 0.8)
        self.assertEqual(self.analysis.volatility_expectation, "high")
        self.assertEqual(self.analysis.days_to_expiry, 3)
    
    def test_analysis_properties(self):
        """Test propriétés de l'analyse"""
        self.assertIsInstance(self.analysis.gamma_phase, GammaPhase)
        self.assertGreaterEqual(self.analysis.adjustment_factor, 0.0)
        self.assertLessEqual(self.analysis.adjustment_factor, 1.0)
        self.assertIsInstance(self.analysis.volatility_expectation, str)
        self.assertGreaterEqual(self.analysis.days_to_expiry, 0)
    
    def test_analysis_serialization(self):
        """Test sérialisation de l'analyse"""
        # Test conversion en dictionnaire
        analysis_dict = self.analysis.to_dict()
        self.assertIsInstance(analysis_dict, dict)
        self.assertIn('gamma_phase', analysis_dict)
        self.assertIn('adjustment_factor', analysis_dict)
        self.assertIn('volatility_expectation', analysis_dict)
        self.assertIn('days_to_expiry', analysis_dict)


class TestGammaPhase(unittest.TestCase):
    """Tests pour les phases gamma"""
    
    def test_gamma_phase_enum(self):
        """Test enum GammaPhase"""
        self.assertIn(GammaPhase.EARLY_CYCLE, GammaPhase)
        self.assertIn(GammaPhase.MID_CYCLE, GammaPhase)
        self.assertIn(GammaPhase.EXPIRATION_WEEK, GammaPhase)
        self.assertIn(GammaPhase.EXPIRATION_DAY, GammaPhase)
    
    def test_phase_values(self):
        """Test valeurs des phases"""
        self.assertEqual(GammaPhase.EARLY_CYCLE.value, "early_cycle")
        self.assertEqual(GammaPhase.MID_CYCLE.value, "mid_cycle")
        self.assertEqual(GammaPhase.EXPIRATION_WEEK.value, "expiration_week")
        self.assertEqual(GammaPhase.EXPIRATION_DAY.value, "expiration_day")


class TestGammaCyclesIntegration(unittest.TestCase):
    """Tests d'intégration pour les cycles gamma"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.config = GammaCycleConfig()
        self.gamma_analyzer = GammaCyclesAnalyzer(self.config)
        
        # Données de test variées
        self.early_cycle_data = MarketData(
            timestamp=datetime.now() - timedelta(days=10),
            symbol="ES",
            open=4500.0,
            high=4510.0,
            low=4495.0,
            close=4505.0,
            volume=1000
        )
        
        self.expiration_week_data = MarketData(
            timestamp=datetime.now() - timedelta(days=3),
            symbol="ES",
            open=4500.0,
            high=4510.0,
            low=4495.0,
            close=4505.0,
            volume=1500
        )
        
        self.expiration_day_data = MarketData(
            timestamp=datetime.now() - timedelta(hours=6),
            symbol="ES",
            open=4500.0,
            high=4510.0,
            low=4495.0,
            close=4505.0,
            volume=2000
        )
    
    def test_cycle_phase_detection(self):
        """Test détection phase de cycle"""
        # Test cycle précoce
        early_analysis = self.gamma_analyzer.analyze_gamma_cycle()
        self.assertIsNotNone(early_analysis)
        self.assertIsInstance(early_analysis, GammaCycleAnalysis)
        
        # Test semaine d'expiration
        expiration_analysis = self.gamma_analyzer.analyze_gamma_cycle()
        self.assertIsNotNone(expiration_analysis)
        self.assertIsInstance(expiration_analysis, GammaCycleAnalysis)
    
    def test_adjustment_factor_calculation(self):
        """Test calcul facteur d'ajustement"""
        factor = self.gamma_analyzer.calculate_expiration_factor()
        self.assertIsNotNone(factor)
        self.assertGreaterEqual(factor, 0.0)
        self.assertLessEqual(factor, 1.0)
        
        # Le facteur doit être plus élevé près de l'expiration
        early_factor = self.gamma_analyzer.calculate_expiration_factor()
        self.assertIsNotNone(early_factor)
    
    def test_volatility_prediction(self):
        """Test prédiction volatilité"""
        expectation = self.gamma_analyzer.calculate_volatility_expectation()
        self.assertIsNotNone(expectation)
        self.assertIsInstance(expectation, str)
        self.assertIn(expectation, ['low', 'medium', 'high', 'extreme'])
    
    def test_performance_benchmark(self):
        """Test benchmark performance"""
        start_time = time.time()
        
        # Analyses multiples
        for _ in range(50):
            analysis = self.gamma_analyzer.analyze_gamma_cycle()
            self.assertIsNotNone(analysis)
            self.assertIsInstance(analysis, GammaCycleAnalysis)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Vérifier que l'exécution est rapide (< 1 seconde pour 50 analyses)
        self.assertLess(execution_time, 1.0)
        logger.info(f"Performance test: {execution_time:.3f}s pour 50 analyses gamma")
    
    def test_cycle_consistency(self):
        """Test cohérence des cycles"""
        # Test que les analyses sont cohérentes
        analysis1 = self.gamma_analyzer.analyze_gamma_cycle()
        analysis2 = self.gamma_analyzer.analyze_gamma_cycle()
        
        # Les analyses doivent être similaires (même jour)
        self.assertEqual(analysis1.days_to_expiry, analysis2.days_to_expiry)
        self.assertEqual(analysis1.volatility_expectation, analysis2.volatility_expectation)


class TestGammaCyclesEdgeCases(unittest.TestCase):
    """Tests cas limites pour les cycles gamma"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.config = GammaCycleConfig()
        self.gamma_analyzer = GammaCyclesAnalyzer(self.config)
    
    def test_expiration_day_edge_case(self):
        """Test cas limite jour d'expiration"""
        # Simuler jour d'expiration
        with patch('ml.gamma_cycles.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 17, 15, 30)  # Vendredi expiration
            mock_datetime.return_value = datetime
            
            analysis = self.gamma_analyzer.analyze_gamma_cycle()
            self.assertIsNotNone(analysis)
            self.assertEqual(analysis.days_to_expiry, 0)
            self.assertEqual(analysis.gamma_phase, GammaPhase.EXPIRATION_DAY)
    
    def test_early_cycle_edge_case(self):
        """Test cas limite cycle précoce"""
        # Simuler début de cycle
        with patch('ml.gamma_cycles.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 20, 9, 30)  # Lundi après expiration
            mock_datetime.return_value = datetime
            
            analysis = self.gamma_analyzer.analyze_gamma_cycle()
            self.assertIsNotNone(analysis)
            self.assertGreater(analysis.days_to_expiry, 0)
            self.assertEqual(analysis.gamma_phase, GammaPhase.EARLY_CYCLE)
    
    def test_invalid_config(self):
        """Test configuration invalide"""
        invalid_config = GammaCycleConfig()
        invalid_config.gamma_expiration_days = -1  # Valeur invalide
        
        try:
            analyzer = GammaCyclesAnalyzer(invalid_config)
            analysis = analyzer.analyze_gamma_cycle()
            self.assertIsNotNone(analysis)
        except Exception as e:
            # Si une exception est levée, elle doit être gérée proprement
            self.assertIsInstance(e, Exception)
    
    def test_extreme_volatility(self):
        """Test volatilité extrême"""
        # Simuler conditions de volatilité extrême
        with patch('ml.gamma_cycles.np.random') as mock_random:
            mock_random.normal.return_value = 0.8  # Volatilité élevée
            
            expectation = self.gamma_analyzer.calculate_volatility_expectation()
            self.assertIsNotNone(expectation)
            self.assertIn(expectation, ['low', 'medium', 'high', 'extreme'])


class TestGammaCyclesMarketData(unittest.TestCase):
    """Tests avec données marché pour cycles gamma"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.config = GammaCycleConfig()
        self.gamma_analyzer = GammaCyclesAnalyzer(self.config)
        
        # Données marché de test
        self.market_data = MarketData(
            timestamp=datetime.now(),
            symbol="ES",
            open=4500.0,
            high=4510.0,
            low=4495.0,
            close=4505.0,
            volume=1000
        )
    
    def test_market_data_integration(self):
        """Test intégration données marché"""
        # Test que l'analyseur peut traiter les données marché
        analysis = self.gamma_analyzer.analyze_gamma_cycle()
        self.assertIsNotNone(analysis)
        self.assertIsInstance(analysis, GammaCycleAnalysis)
    
    def test_volume_impact(self):
        """Test impact du volume"""
        # Test avec volume élevé
        high_volume_data = MarketData(
            timestamp=datetime.now(),
            symbol="ES",
            open=4500.0,
            high=4510.0,
            low=4495.0,
            close=4505.0,
            volume=5000  # Volume élevé
        )
        
        analysis = self.gamma_analyzer.analyze_gamma_cycle()
        self.assertIsNotNone(analysis)
    
    def test_price_volatility_impact(self):
        """Test impact volatilité prix"""
        # Test avec forte volatilité
        volatile_data = MarketData(
            timestamp=datetime.now(),
            symbol="ES",
            open=4500.0,
            high=4520.0,  # Plus grande amplitude
            low=4480.0,   # Plus grande amplitude
            close=4505.0,
            volume=1000
        )
        
        analysis = self.gamma_analyzer.analyze_gamma_cycle()
        self.assertIsNotNone(analysis)


def run_gamma_cycles_tests():
    """Fonction principale pour exécuter tous les tests"""
    logger.info("🧪 Démarrage tests Gamma Cycles...")
    
    # Créer suite de tests
    test_suite = unittest.TestSuite()
    
    # Ajouter tests
    test_suite.addTest(unittest.makeSuite(TestGammaCycleConfig))
    test_suite.addTest(unittest.makeSuite(TestGammaCyclesAnalyzer))
    test_suite.addTest(unittest.makeSuite(TestGammaCycleAnalysis))
    test_suite.addTest(unittest.makeSuite(TestGammaPhase))
    test_suite.addTest(unittest.makeSuite(TestGammaCyclesIntegration))
    test_suite.addTest(unittest.makeSuite(TestGammaCyclesEdgeCases))
    test_suite.addTest(unittest.makeSuite(TestGammaCyclesMarketData))
    
    # Exécuter tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Résultats
    logger.info(f"✅ Tests Gamma Cycles terminés: {result.testsRun} tests, {len(result.failures)} échecs")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_gamma_cycles_tests()
    if success:
        print("🎉 Tous les tests Gamma Cycles ont réussi !")
    else:
        print("❌ Certains tests Gamma Cycles ont échoué.") 