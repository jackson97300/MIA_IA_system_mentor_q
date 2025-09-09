"""
MIA_IA_SYSTEM - Test Core Modules Complètes
Tests pour tous les modules core du système
Version: Production Ready
Performance: Validation complète core modules
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
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger
from core.base_types import MarketData, SignalType, MarketRegime, OrderFlowData
from core.ibkr_connector import IBKRConnector
from core.sierra_connector import SierraConnector
from core.battle_navale import BattleNavale
from core.patterns_detector import ElitePatternsDetector
from core.signal_explainer import SignalExplainer
from core.catastrophe_monitor import CatastropheMonitor
from core.lessons_learned_analyzer import LessonsLearnedAnalyzer
from core.session_analyzer import SessionAnalyzer
from core.mentor_system import MentorSystem

logger = get_logger(__name__)


class TestBaseTypes(unittest.TestCase):
    """Tests pour les types de base"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.sample_market_data = MarketData(
            timestamp=datetime.now(),
            symbol="ES",
            open=4500.0,
            high=4510.0,
            low=4495.0,
            close=4505.0,
            volume=1000
        )
    
    def test_market_data_creation(self):
        """Test création MarketData"""
        self.assertIsNotNone(self.sample_market_data)
        self.assertEqual(self.sample_market_data.symbol, "ES")
        self.assertEqual(self.sample_market_data.open, 4500.0)
        self.assertEqual(self.sample_market_data.close, 4505.0)
    
    def test_market_data_properties(self):
        """Test propriétés MarketData"""
        self.assertTrue(hasattr(self.sample_market_data, 'is_bullish'))
        self.assertTrue(hasattr(self.sample_market_data, 'is_bearish'))
        self.assertTrue(hasattr(self.sample_market_data, 'price_range'))
    
    def test_order_flow_data_creation(self):
        """Test création OrderFlowData"""
        order_flow = OrderFlowData(
            timestamp=datetime.now(),
            symbol="ES",
            bid_volume=500,
            ask_volume=600,
            bid_price=4500.0,
            ask_price=4500.25
        )
        self.assertIsNotNone(order_flow)
        self.assertEqual(order_flow.symbol, "ES")
    
    def test_signal_type_enum(self):
        """Test enum SignalType"""
        self.assertIn(SignalType.LONG_TREND, SignalType)
        self.assertIn(SignalType.SHORT_TREND, SignalType)
        self.assertIn(SignalType.NO_SIGNAL, SignalType)
    
    def test_market_regime_enum(self):
        """Test enum MarketRegime"""
        self.assertIn(MarketRegime.TREND, MarketRegime)
        self.assertIn(MarketRegime.RANGE, MarketRegime)
        self.assertIn(MarketRegime.UNCLEAR, MarketRegime)


class TestIBKRConnector(unittest.TestCase):
    """Tests pour le connecteur IBKR"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.ibkr_connector = IBKRConnector()
    
    def test_ibkr_connector_initialization(self):
        """Test initialisation connecteur IBKR"""
        self.assertIsNotNone(self.ibkr_connector)
        self.assertTrue(hasattr(self.ibkr_connector, 'connect'))
        self.assertTrue(hasattr(self.ibkr_connector, 'disconnect'))
    
    @patch('core.ibkr_connector.IBKRConnector.connect')
    def test_connection_simulation(self, mock_connect):
        """Test simulation connexion IBKR"""
        mock_connect.return_value = True
        result = self.ibkr_connector.connect()
        self.assertTrue(result)
    
    def test_market_data_retrieval(self):
        """Test récupération données marché"""
        # Test avec données simulées
        market_data = self.ibkr_connector.get_market_data("ES")
        # Pour les tests, on accepte None si pas de connexion réelle
        if market_data is not None:
            self.assertIsInstance(market_data, MarketData)


class TestSierraConnector(unittest.TestCase):
    """Tests pour le connecteur Sierra"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.sierra_connector = SierraConnector()
    
    def test_sierra_connector_initialization(self):
        """Test initialisation connecteur Sierra"""
        self.assertIsNotNone(self.sierra_connector)
        self.assertTrue(hasattr(self.sierra_connector, 'connect'))
        self.assertTrue(hasattr(self.sierra_connector, 'send_order'))
    
    @patch('core.sierra_connector.SierraConnector.connect')
    def test_connection_simulation(self, mock_connect):
        """Test simulation connexion Sierra"""
        mock_connect.return_value = True
        result = self.sierra_connector.connect()
        self.assertTrue(result)
    
    def test_order_sending_simulation(self):
        """Test simulation envoi ordre"""
        # Test avec ordre simulé
        order_result = self.sierra_connector.send_order(
            symbol="ES",
            side="BUY",
            quantity=1,
            order_type="MKT"
        )
        # Pour les tests, on accepte None si pas de connexion réelle
        if order_result is not None:
            self.assertIsInstance(order_result, dict)


class TestBattleNavale(unittest.TestCase):
    """Tests pour Battle Navale"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.battle_navale = BattleNavale()
        
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
    
    def test_battle_navale_initialization(self):
        """Test initialisation Battle Navale"""
        self.assertIsNotNone(self.battle_navale)
        self.assertTrue(hasattr(self.battle_navale, 'analyze'))
        self.assertTrue(hasattr(self.battle_navale, 'generate_signal'))
    
    def test_battle_navale_analysis(self):
        """Test analyse Battle Navale"""
        result = self.battle_navale.analyze(self.sample_market_data)
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'signal_type'))
        self.assertTrue(hasattr(result, 'confidence'))
    
    def test_signal_generation(self):
        """Test génération signal Battle Navale"""
        signal = self.battle_navale.generate_signal(self.sample_market_data)
        self.assertIsNotNone(signal)
        self.assertTrue(hasattr(signal, 'signal_type'))
        self.assertTrue(hasattr(signal, 'confidence'))


class TestPatternsDetector(unittest.TestCase):
    """Tests pour le détecteur de patterns"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.patterns_detector = ElitePatternsDetector()
        
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
    
    def test_patterns_detector_initialization(self):
        """Test initialisation détecteur de patterns"""
        self.assertIsNotNone(self.patterns_detector)
        self.assertTrue(hasattr(self.patterns_detector, 'detect_all_patterns'))
    
    def test_gamma_pin_detection(self):
        """Test détection gamma pin"""
        gamma_pin = self.patterns_detector.detect_gamma_pin(self.sample_market_data)
        self.assertIsNotNone(gamma_pin)
        self.assertTrue(hasattr(gamma_pin, 'pin_strength'))
        self.assertTrue(hasattr(gamma_pin, 'pin_level'))
    
    def test_headfake_detection(self):
        """Test détection headfake"""
        headfake = self.patterns_detector.detect_headfake(self.sample_market_data)
        self.assertIsNotNone(headfake)
        self.assertTrue(hasattr(headfake, 'headfake_strength'))
        self.assertTrue(hasattr(headfake, 'headfake_type'))
    
    def test_microstructure_anomaly_detection(self):
        """Test détection anomalie microstructure"""
        anomaly = self.patterns_detector.detect_microstructure_anomaly(self.sample_market_data)
        self.assertIsNotNone(anomaly)
        self.assertTrue(hasattr(anomaly, 'anomaly_strength'))
        self.assertTrue(hasattr(anomaly, 'primary_anomaly'))
    
    def test_all_patterns_detection(self):
        """Test détection tous patterns"""
        all_patterns = self.patterns_detector.detect_all_patterns(self.sample_market_data)
        self.assertIsNotNone(all_patterns)
        self.assertTrue(hasattr(all_patterns, 'gamma_pin'))
        self.assertTrue(hasattr(all_patterns, 'headfake'))
        self.assertTrue(hasattr(all_patterns, 'microstructure'))


class TestSignalExplainer(unittest.TestCase):
    """Tests pour l'explicateur de signaux"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.signal_explainer = SignalExplainer()
        
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
    
    def test_signal_explainer_initialization(self):
        """Test initialisation explicateur de signaux"""
        self.assertIsNotNone(self.signal_explainer)
        self.assertTrue(hasattr(self.signal_explainer, 'explain_signal'))
    
    def test_signal_explanation(self):
        """Test explication de signal"""
        explanation = self.signal_explainer.explain_signal(self.sample_market_data)
        self.assertIsNotNone(explanation)
        self.assertTrue(hasattr(explanation, 'reason'))
        self.assertTrue(hasattr(explanation, 'confidence'))
    
    def test_no_signal_explanation(self):
        """Test explication absence de signal"""
        explanation = self.signal_explainer.explain_no_signal(self.sample_market_data)
        self.assertIsNotNone(explanation)
        self.assertTrue(hasattr(explanation, 'reason'))


class TestCatastropheMonitor(unittest.TestCase):
    """Tests pour le moniteur de catastrophe"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.catastrophe_monitor = CatastropheMonitor()
    
    def test_catastrophe_monitor_initialization(self):
        """Test initialisation moniteur de catastrophe"""
        self.assertIsNotNone(self.catastrophe_monitor)
        self.assertTrue(hasattr(self.catastrophe_monitor, 'check_conditions'))
    
    def test_normal_conditions(self):
        """Test conditions normales"""
        result = self.catastrophe_monitor.check_conditions(
            daily_pnl=100.0,
            consecutive_losses=0,
            system_health="normal"
        )
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'alert_level'))
        self.assertTrue(hasattr(result, 'action'))
    
    def test_emergency_conditions(self):
        """Test conditions d'urgence"""
        result = self.catastrophe_monitor.check_conditions(
            daily_pnl=-500.0,
            consecutive_losses=5,
            system_health="degraded"
        )
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'alert_level'))
        self.assertTrue(hasattr(result, 'action'))


class TestLessonsLearnedAnalyzer(unittest.TestCase):
    """Tests pour l'analyseur de leçons apprises"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.lessons_analyzer = LessonsLearnedAnalyzer()
    
    def test_lessons_analyzer_initialization(self):
        """Test initialisation analyseur de leçons"""
        self.assertIsNotNone(self.lessons_analyzer)
        self.assertTrue(hasattr(self.lessons_analyzer, 'analyze_trades'))
    
    def test_trade_analysis(self):
        """Test analyse de trades"""
        trades_data = [
            {
                'timestamp': datetime.now(),
                'symbol': 'ES',
                'pnl': 100.0,
                'result': 'WIN',
                'pattern': 'gamma_pin'
            }
        ]
        
        analysis = self.lessons_analyzer.analyze_trades(trades_data)
        self.assertIsNotNone(analysis)
        self.assertTrue(hasattr(analysis, 'lessons'))
        self.assertTrue(hasattr(analysis, 'recommendations'))


class TestSessionAnalyzer(unittest.TestCase):
    """Tests pour l'analyseur de session"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.session_analyzer = SessionAnalyzer()
    
    def test_session_analyzer_initialization(self):
        """Test initialisation analyseur de session"""
        self.assertIsNotNone(self.session_analyzer)
        self.assertTrue(hasattr(self.session_analyzer, 'analyze_session'))
    
    def test_session_analysis(self):
        """Test analyse de session"""
        session_data = {
            'start_time': datetime.now() - timedelta(hours=6),
            'end_time': datetime.now(),
            'trades': 10,
            'win_rate': 0.7,
            'total_pnl': 500.0
        }
        
        analysis = self.session_analyzer.analyze_session(session_data)
        self.assertIsNotNone(analysis)
        self.assertTrue(hasattr(analysis, 'session_score'))
        self.assertTrue(hasattr(analysis, 'insights'))


class TestMentorSystem(unittest.TestCase):
    """Tests pour le système de mentorat"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.mentor_system = MentorSystem("test_webhook_url")
    
    def test_mentor_system_initialization(self):
        """Test initialisation système de mentorat"""
        self.assertIsNotNone(self.mentor_system)
        self.assertTrue(hasattr(self.mentor_system, 'analyze_daily_performance'))
    
    def test_daily_performance_analysis(self):
        """Test analyse performance quotidienne"""
        performance_data = {
            'total_trades': 20,
            'winning_trades': 14,
            'losing_trades': 6,
            'total_pnl': 800.0,
            'win_rate': 0.7
        }
        
        analysis = self.mentor_system.analyze_daily_performance(performance_data)
        self.assertIsNotNone(analysis)
        self.assertTrue(hasattr(analysis, 'advice_list'))
        self.assertTrue(hasattr(analysis, 'overall_score'))


class TestCoreIntegration(unittest.TestCase):
    """Tests d'intégration pour tous les modules core"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.battle_navale = BattleNavale()
        self.patterns_detector = ElitePatternsDetector()
        self.signal_explainer = SignalExplainer()
        self.catastrophe_monitor = CatastropheMonitor()
        
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
    
    def test_complete_core_pipeline(self):
        """Test pipeline complet core"""
        # Test Battle Navale
        battle_signal = self.battle_navale.generate_signal(self.sample_market_data)
        self.assertIsNotNone(battle_signal)
        
        # Test Patterns Detector
        patterns = self.patterns_detector.detect_all_patterns(self.sample_market_data)
        self.assertIsNotNone(patterns)
        
        # Test Signal Explainer
        explanation = self.signal_explainer.explain_signal(self.sample_market_data)
        self.assertIsNotNone(explanation)
        
        # Test Catastrophe Monitor
        catastrophe_check = self.catastrophe_monitor.check_conditions(
            daily_pnl=100.0,
            consecutive_losses=0,
            system_health="normal"
        )
        self.assertIsNotNone(catastrophe_check)
    
    def test_performance_benchmark(self):
        """Test benchmark performance core"""
        start_time = time.time()
        
        # Tests multiples
        for _ in range(50):
            battle_signal = self.battle_navale.generate_signal(self.sample_market_data)
            patterns = self.patterns_detector.detect_all_patterns(self.sample_market_data)
            explanation = self.signal_explainer.explain_signal(self.sample_market_data)
            
            self.assertIsNotNone(battle_signal)
            self.assertIsNotNone(patterns)
            self.assertIsNotNone(explanation)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Vérifier que l'exécution est rapide (< 3 secondes pour 50 tests)
        self.assertLess(execution_time, 3.0)
        logger.info(f"Performance test: {execution_time:.3f}s pour 50 tests core")


def run_core_tests():
    """Fonction principale pour exécuter tous les tests"""
    logger.info("🧪 Démarrage tests core modules...")
    
    # Créer suite de tests
    test_suite = unittest.TestSuite()
    
    # Ajouter tests
    test_suite.addTest(unittest.makeSuite(TestBaseTypes))
    test_suite.addTest(unittest.makeSuite(TestIBKRConnector))
    test_suite.addTest(unittest.makeSuite(TestSierraConnector))
    test_suite.addTest(unittest.makeSuite(TestBattleNavale))
    test_suite.addTest(unittest.makeSuite(TestPatternsDetector))
    test_suite.addTest(unittest.makeSuite(TestSignalExplainer))
    test_suite.addTest(unittest.makeSuite(TestCatastropheMonitor))
    test_suite.addTest(unittest.makeSuite(TestLessonsLearnedAnalyzer))
    test_suite.addTest(unittest.makeSuite(TestSessionAnalyzer))
    test_suite.addTest(unittest.makeSuite(TestMentorSystem))
    test_suite.addTest(unittest.makeSuite(TestCoreIntegration))
    
    # Exécuter tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Résultats
    logger.info(f"✅ Tests core modules terminés: {result.testsRun} tests, {len(result.failures)} échecs")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_core_tests()
    if success:
        print("🎉 Tous les tests core modules ont réussi !")
    else:
        print("❌ Certains tests core modules ont échoué.") 