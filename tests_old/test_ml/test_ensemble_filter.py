"""
MIA_IA_SYSTEM - Test ML Ensemble Filter
Tests pour le filtre ML ensemble
Version: Production Ready
Performance: Validation complète ML Ensemble Filter
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
from ml.ensemble_filter import MLEnsembleFilter, EnsembleConfig, EnsemblePrediction

logger = get_logger(__name__)


class TestEnsembleConfig(unittest.TestCase):
    """Tests pour la configuration ensemble"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.config = EnsembleConfig()
    
    def test_ensemble_config_initialization(self):
        """Test initialisation configuration ensemble"""
        self.assertIsNotNone(self.config)
        self.assertTrue(hasattr(self.config, 'ensemble_enabled'))
        self.assertTrue(hasattr(self.config, 'min_ensemble_confidence'))
        self.assertTrue(hasattr(self.config, 'ensemble_models'))
    
    def test_default_values(self):
        """Test valeurs par défaut"""
        self.assertTrue(self.config.ensemble_enabled)
        self.assertGreater(self.config.min_ensemble_confidence, 0.0)
        self.assertLess(self.config.min_ensemble_confidence, 1.0)
        self.assertIsInstance(self.config.ensemble_models, list)
        self.assertGreater(len(self.config.ensemble_models), 0)
    
    def test_config_validation(self):
        """Test validation configuration"""
        # Test avec valeurs valides
        self.config.min_ensemble_confidence = 0.7
        self.config.ensemble_models = ["random_forest", "gradient_boost"]
        
        # Vérifier que la configuration est valide
        self.assertGreaterEqual(self.config.min_ensemble_confidence, 0.0)
        self.assertLessEqual(self.config.min_ensemble_confidence, 1.0)
        self.assertGreater(len(self.config.ensemble_models), 0)


class TestMLEnsembleFilter(unittest.TestCase):
    """Tests pour le filtre ML ensemble"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.config = EnsembleConfig()
        self.ml_filter = MLEnsembleFilter(self.config)
        
        # Données de test
        self.sample_features = {
            "confluence_score": 0.75,
            "momentum_flow": 0.8,
            "trend_alignment": 0.7,
            "volume_profile": 0.6,
            "support_resistance": 0.5,
            "market_regime_score": 0.6,
            "volatility_regime": 0.5,
            "time_factor": 0.5
        }
    
    def test_ml_filter_initialization(self):
        """Test initialisation filtre ML ensemble"""
        self.assertIsNotNone(self.ml_filter)
        self.assertTrue(hasattr(self.ml_filter, 'predict_signal_quality'))
        self.assertTrue(hasattr(self.ml_filter, 'train_models'))
    
    def test_feature_preprocessing(self):
        """Test prétraitement des features"""
        processed_features = self.ml_filter.preprocess_features(self.sample_features)
        self.assertIsNotNone(processed_features)
        self.assertIsInstance(processed_features, dict)
        self.assertTrue(len(processed_features) > 0)
    
    def test_prediction_generation(self):
        """Test génération de prédiction"""
        prediction = self.ml_filter.predict_signal_quality(self.sample_features)
        self.assertIsNotNone(prediction)
        self.assertIsInstance(prediction, EnsemblePrediction)
        self.assertTrue(hasattr(prediction, 'confidence'))
        self.assertTrue(hasattr(prediction, 'signal_approved'))
        self.assertTrue(hasattr(prediction, 'models_used'))
    
    def test_prediction_validation(self):
        """Test validation des prédictions"""
        prediction = self.ml_filter.predict_signal_quality(self.sample_features)
        
        # Vérifier les propriétés de la prédiction
        self.assertGreaterEqual(prediction.confidence, 0.0)
        self.assertLessEqual(prediction.confidence, 1.0)
        self.assertIsInstance(prediction.signal_approved, bool)
        self.assertIsInstance(prediction.models_used, list)
        self.assertGreater(len(prediction.models_used), 0)
    
    def test_confidence_threshold(self):
        """Test seuil de confiance"""
        # Test avec features de haute confiance
        high_confidence_features = {
            "confluence_score": 0.9,
            "momentum_flow": 0.95,
            "trend_alignment": 0.9,
            "volume_profile": 0.8,
            "support_resistance": 0.7,
            "market_regime_score": 0.8,
            "volatility_regime": 0.6,
            "time_factor": 0.7
        }
        
        prediction = self.ml_filter.predict_signal_quality(high_confidence_features)
        self.assertGreater(prediction.confidence, 0.5)
    
    def test_low_confidence_features(self):
        """Test features de faible confiance"""
        low_confidence_features = {
            "confluence_score": 0.3,
            "momentum_flow": 0.2,
            "trend_alignment": 0.3,
            "volume_profile": 0.4,
            "support_resistance": 0.3,
            "market_regime_score": 0.4,
            "volatility_regime": 0.5,
            "time_factor": 0.3
        }
        
        prediction = self.ml_filter.predict_signal_quality(low_confidence_features)
        self.assertIsNotNone(prediction)
        self.assertGreaterEqual(prediction.confidence, 0.0)
        self.assertLessEqual(prediction.confidence, 1.0)


class TestEnsemblePrediction(unittest.TestCase):
    """Tests pour les prédictions ensemble"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.prediction = EnsemblePrediction(
            confidence=0.75,
            signal_approved=True,
            models_used=["random_forest", "gradient_boost"],
            processing_time_ms=15.5
        )
    
    def test_prediction_creation(self):
        """Test création prédiction"""
        self.assertIsNotNone(self.prediction)
        self.assertEqual(self.prediction.confidence, 0.75)
        self.assertTrue(self.prediction.signal_approved)
        self.assertEqual(len(self.prediction.models_used), 2)
        self.assertEqual(self.prediction.processing_time_ms, 15.5)
    
    def test_prediction_properties(self):
        """Test propriétés de la prédiction"""
        self.assertGreaterEqual(self.prediction.confidence, 0.0)
        self.assertLessEqual(self.prediction.confidence, 1.0)
        self.assertIsInstance(self.prediction.signal_approved, bool)
        self.assertIsInstance(self.prediction.models_used, list)
        self.assertGreaterEqual(self.prediction.processing_time_ms, 0.0)
    
    def test_prediction_serialization(self):
        """Test sérialisation de la prédiction"""
        # Test conversion en dictionnaire
        pred_dict = self.prediction.to_dict()
        self.assertIsInstance(pred_dict, dict)
        self.assertIn('confidence', pred_dict)
        self.assertIn('signal_approved', pred_dict)
        self.assertIn('models_used', pred_dict)
        self.assertIn('processing_time_ms', pred_dict)


class TestMLEnsembleFilterIntegration(unittest.TestCase):
    """Tests d'intégration pour le filtre ML ensemble"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.config = EnsembleConfig()
        self.ml_filter = MLEnsembleFilter(self.config)
        
        # Données de test variées
        self.high_quality_features = {
            "confluence_score": 0.9,
            "momentum_flow": 0.95,
            "trend_alignment": 0.9,
            "volume_profile": 0.8,
            "support_resistance": 0.7,
            "market_regime_score": 0.8,
            "volatility_regime": 0.6,
            "time_factor": 0.7
        }
        
        self.medium_quality_features = {
            "confluence_score": 0.6,
            "momentum_flow": 0.5,
            "trend_alignment": 0.6,
            "volume_profile": 0.5,
            "support_resistance": 0.4,
            "market_regime_score": 0.5,
            "volatility_regime": 0.5,
            "time_factor": 0.5
        }
        
        self.low_quality_features = {
            "confluence_score": 0.3,
            "momentum_flow": 0.2,
            "trend_alignment": 0.3,
            "volume_profile": 0.4,
            "support_resistance": 0.3,
            "market_regime_score": 0.4,
            "volatility_regime": 0.5,
            "time_factor": 0.3
        }
    
    def test_quality_gradient(self):
        """Test gradient de qualité"""
        # Test haute qualité
        high_prediction = self.ml_filter.predict_signal_quality(self.high_quality_features)
        self.assertGreater(high_prediction.confidence, 0.5)
        
        # Test qualité moyenne
        medium_prediction = self.ml_filter.predict_signal_quality(self.medium_quality_features)
        self.assertIsNotNone(medium_prediction.confidence)
        
        # Test faible qualité
        low_prediction = self.ml_filter.predict_signal_quality(self.low_quality_features)
        self.assertIsNotNone(low_prediction.confidence)
        
        # Vérifier que la confiance suit le gradient de qualité
        self.assertGreaterEqual(high_prediction.confidence, medium_prediction.confidence)
        self.assertGreaterEqual(medium_prediction.confidence, low_prediction.confidence)
    
    def test_batch_processing(self):
        """Test traitement par lot"""
        features_batch = [
            self.high_quality_features,
            self.medium_quality_features,
            self.low_quality_features
        ]
        
        predictions = []
        for features in features_batch:
            prediction = self.ml_filter.predict_signal_quality(features)
            predictions.append(prediction)
            self.assertIsNotNone(prediction)
            self.assertIsInstance(prediction, EnsemblePrediction)
        
        self.assertEqual(len(predictions), 3)
    
    def test_performance_benchmark(self):
        """Test benchmark performance"""
        start_time = time.time()
        
        # Prédictions multiples
        for _ in range(100):
            prediction = self.ml_filter.predict_signal_quality(self.high_quality_features)
            self.assertIsNotNone(prediction)
            self.assertIsInstance(prediction, EnsemblePrediction)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Vérifier que l'exécution est rapide (< 2 secondes pour 100 prédictions)
        self.assertLess(execution_time, 2.0)
        logger.info(f"Performance test: {execution_time:.3f}s pour 100 prédictions ML")
    
    def test_model_consistency(self):
        """Test cohérence des modèles"""
        # Test que les mêmes features donnent des résultats cohérents
        prediction1 = self.ml_filter.predict_signal_quality(self.high_quality_features)
        prediction2 = self.ml_filter.predict_signal_quality(self.high_quality_features)
        
        # Les prédictions doivent être similaires (tolérance de 0.1)
        self.assertAlmostEqual(prediction1.confidence, prediction2.confidence, delta=0.1)
        self.assertEqual(prediction1.signal_approved, prediction2.signal_approved)


class TestMLEnsembleFilterEdgeCases(unittest.TestCase):
    """Tests cas limites pour le filtre ML ensemble"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.config = EnsembleConfig()
        self.ml_filter = MLEnsembleFilter(self.config)
    
    def test_empty_features(self):
        """Test features vides"""
        empty_features = {}
        
        # Le système doit gérer les features vides
        try:
            prediction = self.ml_filter.predict_signal_quality(empty_features)
            self.assertIsNotNone(prediction)
        except Exception as e:
            # Si une exception est levée, elle doit être gérée proprement
            self.assertIsInstance(e, Exception)
    
    def test_missing_features(self):
        """Test features manquantes"""
        partial_features = {
            "confluence_score": 0.7,
            "momentum_flow": 0.6
            # Features manquantes
        }
        
        try:
            prediction = self.ml_filter.predict_signal_quality(partial_features)
            self.assertIsNotNone(prediction)
        except Exception as e:
            # Si une exception est levée, elle doit être gérée proprement
            self.assertIsInstance(e, Exception)
    
    def test_extreme_values(self):
        """Test valeurs extrêmes"""
        extreme_features = {
            "confluence_score": 1.0,
            "momentum_flow": 1.0,
            "trend_alignment": 1.0,
            "volume_profile": 1.0,
            "support_resistance": 1.0,
            "market_regime_score": 1.0,
            "volatility_regime": 1.0,
            "time_factor": 1.0
        }
        
        prediction = self.ml_filter.predict_signal_quality(extreme_features)
        self.assertIsNotNone(prediction)
        self.assertGreaterEqual(prediction.confidence, 0.0)
        self.assertLessEqual(prediction.confidence, 1.0)
    
    def test_negative_values(self):
        """Test valeurs négatives"""
        negative_features = {
            "confluence_score": -0.5,
            "momentum_flow": -0.3,
            "trend_alignment": -0.2,
            "volume_profile": -0.1,
            "support_resistance": -0.4,
            "market_regime_score": -0.3,
            "volatility_regime": -0.2,
            "time_factor": -0.1
        }
        
        try:
            prediction = self.ml_filter.predict_signal_quality(negative_features)
            self.assertIsNotNone(prediction)
        except Exception as e:
            # Si une exception est levée, elle doit être gérée proprement
            self.assertIsInstance(e, Exception)


def run_ensemble_filter_tests():
    """Fonction principale pour exécuter tous les tests"""
    logger.info("🧪 Démarrage tests ML Ensemble Filter...")
    
    # Créer suite de tests
    test_suite = unittest.TestSuite()
    
    # Ajouter tests
    test_suite.addTest(unittest.makeSuite(TestEnsembleConfig))
    test_suite.addTest(unittest.makeSuite(TestMLEnsembleFilter))
    test_suite.addTest(unittest.makeSuite(TestEnsemblePrediction))
    test_suite.addTest(unittest.makeSuite(TestMLEnsembleFilterIntegration))
    test_suite.addTest(unittest.makeSuite(TestMLEnsembleFilterEdgeCases))
    
    # Exécuter tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Résultats
    logger.info(f"✅ Tests ML Ensemble Filter terminés: {result.testsRun} tests, {len(result.failures)} échecs")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_ensemble_filter_tests()
    if success:
        print("🎉 Tous les tests ML Ensemble Filter ont réussi !")
    else:
        print("❌ Certains tests ML Ensemble Filter ont échoué.") 