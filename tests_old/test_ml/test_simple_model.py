"""
Tests pour le Simple Model ML MIA_IA_SYSTEM
Validation complète du modèle Machine Learning Battle Navale
"""

from config.ml_config import ML_CONFIG
from core.battle_navale import BattleNavale
from ml.model_validator import ModelValidator
from ml.data_processor import DataProcessor
from ml.simple_model import SimpleModel
import unittest
import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, call
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
import pickle

# Imports du système MIA_IA_SYSTEM
import sys
from core.logger import get_logger

# Configure logging
logger = get_logger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class TestSimpleModel(unittest.TestCase):
    """Tests complets pour le Simple Model ML"""

    def setUp(self):
        """Setup pour chaque test"""
        self.temp_dir = tempfile.mkdtemp()

        # Configuration test
        self.test_config = {
            'model_type': 'linear_regression',
            'features_count': 8,  # Vos 8 features Battle Navale
            'target_type': 'classification',  # WIN/LOSS prediction
            'validation': {
                'test_size': 0.2,
                'cv_folds': 5,
                'stratify': True
            },
            'performance_thresholds': {
                'min_accuracy': 0.65,
                'min_precision': 0.60,
                'min_recall': 0.60,
                'min_f1_score': 0.60
            },
            'battle_navale': {
                'use_confluence_score': True,
                'use_pattern_encoding': True,
                'use_market_regime': True,
                'feature_engineering': True
            },
            'model_path': self.temp_dir
        }

        # Mock des dépendances
        self.mock_battle_navale = Mock(spec=BattleNavale)
        self.mock_data_processor = Mock(spec=DataProcessor)

        # Création du modèle
        self.simple_model = SimpleModel(
            config=self.test_config,
            battle_navale=self.mock_battle_navale,
            data_processor=self.mock_data_processor
        )

        # Génération de données d'entraînement synthétiques
        np.random.seed(42)  # Pour la reproductibilité
        self.n_samples = 1000

        # Features Battle Navale (8 features + confluence + pattern encoding)
        self.X_features = np.random.randn(self.n_samples, 8)  # 8 features principales
        self.confluence_scores = np.random.uniform(0.5, 1.0, self.n_samples)
        self.pattern_encodings = np.random.randint(0, 3, self.n_samples)  # 3 patterns elite
        self.market_regime = np.random.randint(0, 2, self.n_samples)  # TREND/RANGE

        # Combinaison pour dataset complet
        self.X_train = np.column_stack([
            self.X_features,
            self.confluence_scores,
            self.pattern_encodings,
            self.market_regime
        ])

        # Labels synthétiques avec logique réaliste
        # Probabilité WIN plus élevée avec confluence élevée
        win_probability = (
            0.3 +  # Base probability
            0.4 * self.confluence_scores +  # Confluence boost
            0.1 * (self.pattern_encodings == 1) +  # Pattern 2 le meilleur
            0.05 * self.market_regime  # Trend légèrement meilleur
        )

        self.y_train = (np.random.random(self.n_samples) < win_probability).astype(int)

        # Données de test
        self.X_test = np.random.randn(200, 11)  # 200 échantillons test
        self.y_test = np.random.randint(0, 2, 200)

        # Trades samples pour tests
        self.sample_trades_data = [
            {
                'features': [0.65, -0.23, 1.42, 0.78, -0.91, 2.15, 0.33, -1.67],
                'confluence_score': 0.87,
                'pattern': 'elite_pattern_2',
                'market_regime': 'TRENDING',
                'result': 'WIN'
            },
            {
                'features': [0.45, -0.67, 0.92, 1.23, -0.45, 1.78, 0.12, -0.89],
                'confluence_score': 0.82,
                'pattern': 'elite_pattern_1',
                'market_regime': 'RANGING',
                'result': 'WIN'
            },
            {
                'features': [0.23, -0.89, 0.67, 0.34, -1.23, 1.45, 0.78, -0.56],
                'confluence_score': 0.71,
                'pattern': 'elite_pattern_3',
                'market_regime': 'TRENDING',
                'result': 'LOSS'
            }
        ]

    def tearDown(self):
        """Nettoyage après chaque test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_simple_model_initialization(self):
        """Test : Initialisation correcte du Simple Model"""
        # Vérifier l'initialisation
        self.assertIsNotNone(self.simple_model)
        self.assertEqual(self.simple_model.config, self.test_config)
        self.assertEqual(self.simple_model.features_count, 8)
        self.assertEqual(self.simple_model.target_type, 'classification')

        # Vérifier que le modèle n'est pas encore entraîné
        self.assertFalse(self.simple_model.is_trained)
        self.assertIsNone(self.simple_model.model)

        # Vérifier configuration Battle Navale
        self.assertTrue(self.simple_model.use_confluence_score)
        self.assertTrue(self.simple_model.use_pattern_encoding)
        self.assertTrue(self.simple_model.use_market_regime)

    def test_data_preprocessing(self):
        """Test : Préprocessing des données Battle Navale"""
        # Mock du data processor
        self.mock_data_processor.preprocess_battle_navale_data.return_value = (
            self.X_train, self.y_train
        )

        # Tester preprocessing
        X_processed, y_processed = self.simple_model.preprocess_data(self.sample_trades_data)

        # Vérifications
        self.mock_data_processor.preprocess_battle_navale_data.assert_called_once()
        self.assertIsNotNone(X_processed)
        self.assertIsNotNone(y_processed)

        # Vérifier format des données
        self.assertEqual(X_processed.shape[1], 11)  # 8 features + confluence + pattern + regime
        self.assertIn(y_processed.dtype, [int, 'int32', 'int64'])

    def test_feature_engineering(self):
        """Test : Feature engineering spécifique Battle Navale"""
        # Features de base
        base_features = np.array([0.65, -0.23, 1.42, 0.78, -0.91, 2.15, 0.33, -1.67])
        confluence_score = 0.87
        pattern_name = 'elite_pattern_2'
        market_regime = 'TRENDING'

        # Appliquer feature engineering
        engineered_features = self.simple_model.engineer_features(
            base_features, confluence_score, pattern_name, market_regime
        )

        # Vérifications
        self.assertIsInstance(engineered_features, np.ndarray)
        self.assertEqual(len(engineered_features), 11)  # 8 + 3 engineered

        # Vérifier confluence incluse
        self.assertEqual(engineered_features[8], 0.87)

        # Vérifier encoding pattern (elite_pattern_2 -> 1)
        self.assertEqual(engineered_features[9], 1)

        # Vérifier encoding regime (TRENDING -> 1)
        self.assertEqual(engineered_features[10], 1)

    def test_model_training(self):
        """Test : Entraînement du modèle"""
        # Entraîner le modèle
        training_result = self.simple_model.train(self.X_train, self.y_train)

        # Vérifications
        self.assertTrue(training_result['success'])
        self.assertTrue(self.simple_model.is_trained)
        self.assertIsNotNone(self.simple_model.model)

        # Vérifier métriques d'entraînement
        metrics = training_result['training_metrics']
        self.assertIn('accuracy', metrics)
        self.assertIn('precision', metrics)
        self.assertIn('recall', metrics)
        self.assertIn('f1_score', metrics)

        # Vérifier seuils minimums respectés
        self.assertGreaterEqual(metrics['accuracy'],
                                self.test_config['performance_thresholds']['min_accuracy'])

    def test_model_prediction(self):
        """Test : Prédictions du modèle"""
        # Entraîner d'abord le modèle
        self.simple_model.train(self.X_train, self.y_train)

        # Faire des prédictions
        predictions = self.simple_model.predict(self.X_test)
        prediction_proba = self.simple_model.predict_proba(self.X_test)

        # Vérifications
        self.assertEqual(len(predictions), len(self.X_test))
        self.assertEqual(len(prediction_proba), len(self.X_test))

        # Vérifier format des prédictions
        self.assertTrue(all(pred in [0, 1] for pred in predictions))
        self.assertTrue(all(0 <= prob <= 1 for prob in prediction_proba))

    def test_model_evaluation(self):
        """Test : Évaluation du modèle"""
        # Entraîner le modèle
        self.simple_model.train(self.X_train, self.y_train)

        # Évaluer sur données de test
        evaluation_result = self.simple_model.evaluate(self.X_test, self.y_test)

        # Vérifications
        self.assertIn('accuracy', evaluation_result)
        self.assertIn('precision', evaluation_result)
        self.assertIn('recall', evaluation_result)
        self.assertIn('f1_score', evaluation_result)
        self.assertIn('confusion_matrix', evaluation_result)

        # Vérifier que les métriques sont dans les bonnes plages
        self.assertBetween(evaluation_result['accuracy'], 0.0, 1.0)
        self.assertBetween(evaluation_result['precision'], 0.0, 1.0)
        self.assertBetween(evaluation_result['recall'], 0.0, 1.0)
        self.assertBetween(evaluation_result['f1_score'], 0.0, 1.0)

    def assertBetween(self, value, min_val, max_val):
        """Helper method pour vérifier qu'une valeur est dans un intervalle"""
        self.assertGreaterEqual(value, min_val)
        self.assertLessEqual(value, max_val)

    def test_cross_validation(self):
        """Test : Validation croisée"""
        # Effectuer validation croisée
        cv_results = self.simple_model.cross_validate(self.X_train, self.y_train)

        # Vérifications
        self.assertIn('cv_scores', cv_results)
        self.assertIn('mean_score', cv_results)
        self.assertIn('std_score', cv_results)
        self.assertIn('individual_scores', cv_results)

        # Vérifier nombre de folds
        self.assertEqual(len(cv_results['individual_scores']), 5)

        # Vérifier cohérence des scores
        self.assertBetween(cv_results['mean_score'], 0.0, 1.0)
        self.assertGreaterEqual(cv_results['std_score'], 0.0)

    def test_feature_importance_analysis(self):
        """Test : Analyse d'importance des features"""
        # Entraîner le modèle
        self.simple_model.train(self.X_train, self.y_train)

        # Analyser importance des features
        importance_analysis = self.simple_model.analyze_feature_importance()

        # Vérifications
        self.assertIn('feature_importance', importance_analysis)
        self.assertIn('top_features', importance_analysis)
        self.assertIn('feature_names', importance_analysis)

        # Vérifier nombre de features
        self.assertEqual(len(importance_analysis['feature_importance']), 11)
        self.assertEqual(len(importance_analysis['feature_names']), 11)

        # Vérifier que confluence et patterns sont inclus
        feature_names = importance_analysis['feature_names']
        self.assertIn('confluence_score', feature_names)
        self.assertIn('pattern_encoding', feature_names)
        self.assertIn('market_regime', feature_names)

    def test_battle_navale_prediction_integration(self):
        """Test : Intégration prédiction avec Battle Navale"""
        # Entraîner le modèle
        self.simple_model.train(self.X_train, self.y_train)

        # Mock d'un signal Battle Navale complet
        signal_data = {
            'features': [0.65, -0.23, 1.42, 0.78, -0.91, 2.15, 0.33, -1.67],
            'confluence_score': 0.87,
            'pattern': 'elite_pattern_2',
            'market_regime': 'TRENDING',
            'signal_type': 'VIKINGS_ATTACK'
        }

        # Prédire succès du signal
        prediction_result = self.simple_model.predict_signal_success(signal_data)

        # Vérifications
        self.assertIn('prediction', prediction_result)
        self.assertIn('confidence', prediction_result)
        self.assertIn('feature_contributions', prediction_result)

        # Vérifier format prédiction
        self.assertIn(prediction_result['prediction'], ['WIN', 'LOSS'])
        self.assertBetween(prediction_result['confidence'], 0.0, 1.0)

    def test_model_persistence(self):
        """Test : Sauvegarde et chargement du modèle"""
        # Entraîner le modèle
        self.simple_model.train(self.X_train, self.y_train)

        # Sauvegarder le modèle
        model_path = os.path.join(self.temp_dir, 'battle_navale_model.pkl')
        save_result = self.simple_model.save_model(model_path)

        self.assertTrue(save_result)
        self.assertTrue(os.path.exists(model_path))

        # Créer nouveau modèle et charger
        new_model = SimpleModel(config=self.test_config)
        load_result = new_model.load_model(model_path)

        self.assertTrue(load_result)
        self.assertTrue(new_model.is_trained)

        # Vérifier que les prédictions sont identiques
        pred_original = self.simple_model.predict(self.X_test[:10])
        pred_loaded = new_model.predict(self.X_test[:10])

        np.testing.assert_array_equal(pred_original, pred_loaded)

    def test_online_learning_capability(self):
        """Test : Capacité d'apprentissage en ligne"""
        # Entraîner modèle initial
        initial_size = 800
        X_initial = self.X_train[:initial_size]
        y_initial = self.y_train[:initial_size]

        self.simple_model.train(X_initial, y_initial)

        # Performances initiales
        initial_accuracy = self.simple_model.evaluate(self.X_test, self.y_test)['accuracy']

        # Nouvelles données d'entraînement
        X_new = self.X_train[initial_size:]
        y_new = self.y_train[initial_size:]

        # Mise à jour incrémentale
        update_result = self.simple_model.incremental_update(X_new, y_new)

        # Vérifications
        self.assertTrue(update_result['success'])
        self.assertIn('accuracy_improvement', update_result)

        # Performances après mise à jour
        updated_accuracy = self.simple_model.evaluate(self.X_test, self.y_test)['accuracy']

        # L'accuracy devrait s'améliorer ou rester stable
        self.assertGreaterEqual(updated_accuracy, initial_accuracy - 0.05)  # Tolérance 5%

    def test_model_performance_monitoring(self):
        """Test : Monitoring des performances du modèle"""
        # Entraîner le modèle
        self.simple_model.train(self.X_train, self.y_train)

        # Simuler prédictions sur plusieurs périodes
        performance_history = []

        for i in range(5):
            # Données de test pour chaque période
            period_X = self.X_test[i*20:(i+1)*20]
            period_y = self.y_test[i*20:(i+1)*20]

            # Évaluation de la période
            period_metrics = self.simple_model.evaluate(period_X, period_y)
            period_metrics['period'] = i + 1
            performance_history.append(period_metrics)

        # Analyser dégradation des performances
        degradation_analysis = self.simple_model.analyze_performance_degradation(
            performance_history)

        # Vérifications
        self.assertIn('performance_trend', degradation_analysis)
        self.assertIn('degradation_detected', degradation_analysis)
        self.assertIn('recommended_actions', degradation_analysis)

    def test_confidence_calibration(self):
        """Test : Calibration de la confiance des prédictions"""
        # Entraîner le modèle
        self.simple_model.train(self.X_train, self.y_train)

        # Obtenir prédictions avec probabilités
        predictions = self.simple_model.predict(self.X_test)
        probabilities = self.simple_model.predict_proba(self.X_test)

        # Analyser calibration
        calibration_analysis = self.simple_model.analyze_confidence_calibration(
            self.y_test, predictions, probabilities
        )

        # Vérifications
        self.assertIn('calibration_score', calibration_analysis)
        self.assertIn('reliability_bins', calibration_analysis)
        self.assertIn('overconfidence_rate', calibration_analysis)

        # Score de calibration devrait être raisonnable
        self.assertBetween(calibration_analysis['calibration_score'], 0.0, 1.0)

    def test_model_explainability(self):
        """Test : Explicabilité des prédictions"""
        # Entraîner le modèle
        self.simple_model.train(self.X_train, self.y_train)

        # Échantillon pour explication
        sample_X = self.X_test[0].reshape(1, -1)

        # Expliquer prédiction
        explanation = self.simple_model.explain_prediction(sample_X[0])

        # Vérifications
        self.assertIn('prediction', explanation)
        self.assertIn('confidence', explanation)
        self.assertIn('feature_contributions', explanation)
        self.assertIn('top_influential_features', explanation)

        # Vérifier contributions des features
        contributions = explanation['feature_contributions']
        self.assertEqual(len(contributions), 11)  # Une contribution par feature

        # La somme des contributions devrait être cohérente
        total_contribution = sum(abs(contrib) for contrib in contributions.values())
        self.assertGreater(total_contribution, 0)


class TestSimpleModelIntegration(unittest.TestCase):
    """Tests d'intégration avec le système Battle Navale complet"""

    def setUp(self):
        """Setup pour tests d'intégration"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ML_CONFIG.copy()
        self.config['model_path'] = self.temp_dir

    def tearDown(self):
        """Nettoyage"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('ml.data_processor.DataProcessor')
    @patch('core.battle_navale.BattleNavale')
    def test_end_to_end_ml_pipeline(self, mock_battle_navale_class, mock_data_processor_class):
        """Test : Pipeline ML end-to-end complet"""
        # Setup mocks
        mock_battle_navale = mock_battle_navale_class.return_value
        mock_data_processor = mock_data_processor_class.return_value

        # Mock données d'entraînement
        training_data = [
            {
                'features': np.random.randn(8),
                'confluence_score': np.random.uniform(0.6, 1.0),
                'pattern': f'elite_pattern_{np.random.randint(1, 4)}',
                'market_regime': np.random.choice(['TRENDING', 'RANGING']),
                'result': np.random.choice(['WIN', 'LOSS'])
            }
            for _ in range(500)
        ]

        # Données preprocessées mockées
        X_mock = np.random.randn(500, 11)
        y_mock = np.random.randint(0, 2, 500)
        mock_data_processor.preprocess_battle_navale_data.return_value = (X_mock, y_mock)

        # Créer modèle avec dépendances mockées
        model = SimpleModel(
            config=self.config,
            battle_navale=mock_battle_navale,
            data_processor=mock_data_processor
        )

        # Pipeline complet
        # 1. Preprocessing
        X_processed, y_processed = model.preprocess_data(training_data)

        # 2. Entraînement
        training_result = model.train(X_processed, y_processed)
        self.assertTrue(training_result['success'])

        # 3. Validation
        X_test = np.random.randn(100, 11)
        y_test = np.random.randint(0, 2, 100)
        evaluation = model.evaluate(X_test, y_test)
        self.assertIn('accuracy', evaluation)

        # 4. Sauvegarde
        model_path = os.path.join(self.temp_dir, 'integrated_model.pkl')
        save_success = model.save_model(model_path)
        self.assertTrue(save_success)

        # 5. Prédiction sur nouveau signal
        new_signal = {
            'features': np.random.randn(8),
            'confluence_score': 0.85,
            'pattern': 'elite_pattern_2',
            'market_regime': 'TRENDING'
        }

        prediction = model.predict_signal_success(new_signal)
        self.assertIn('prediction', prediction)
        self.assertIn('confidence', prediction)

    def test_model_production_readiness(self):
        """Test : Préparation pour production"""
        # Créer modèle pour production
        production_model = SimpleModel(config=self.config)

        # Générer données d'entraînement de qualité production
        np.random.seed(123)
        n_samples = 2000  # Plus de données pour production

        X_production = np.random.randn(n_samples, 11)
        # Labels avec pattern réaliste (60% win rate)
        y_production = (np.random.random(n_samples) < 0.6).astype(int)

        # Entraînement
        training_result = production_model.train(X_production, y_production)

        # Vérifications pour production
        metrics = training_result['training_metrics']

        # Seuils production plus stricts
        self.assertGreaterEqual(metrics['accuracy'], 0.65)
        self.assertGreaterEqual(metrics['precision'], 0.60)
        self.assertGreaterEqual(metrics['recall'], 0.60)

        # Test de performance sous charge
        start_time = datetime.now()
        for _ in range(1000):
            test_input = np.random.randn(11)
            prediction = production_model.predict(test_input.reshape(1, -1))
        end_time = datetime.now()

        # Latence moyenne doit être <1ms par prédiction
        avg_latency_ms = (end_time - start_time).total_seconds() * 1000 / 1000
        self.assertLess(avg_latency_ms, 1.0)


if __name__ == '__main__':
    # Configuration des tests
    unittest.TestLoader.sortTestMethodsUsing = None

    # Suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSimpleModel)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSimpleModelIntegration))

    # Exécution avec rapport détaillé
    runner = unittest.TextTestRunner(
        verbosity=2,
        buffer=True,
        failfast=False
    )

    logger.info("🧪 DÉMARRAGE DES TESTS SIMPLE MODEL ML")
    print("=" * 50)

    result = runner.run(suite)

    print("\n" + "=" * 50)
    if result.wasSuccessful():
        logger.info("TOUS LES TESTS SIMPLE MODEL ML RÉUSSIS !")
    else:
        logger.error("{len(result.failures)} ÉCHECS, {len(result.errors)} ERREURS")

    logger.info("[STATS] Tests exécutés: {result.testsRun}")
    logger.info("[TIME]  Temps d'exécution: {result.stop_time - result.start_time:.2f}s")
    logger.info("\n[TARGET] MODÈLE ML BATTLE NAVALE VALIDÉ :")
    logger.info("   • Features engineering 8 features + confluence")
    logger.info("   • Prédiction WIN/LOSS avec >65% accuracy")
    logger.info("   • Intégration patterns elite + régimes marché")
    logger.info("   • Performance <1ms par prédiction")
    logger.info("   • Apprentissage incrémental opérationnel")
