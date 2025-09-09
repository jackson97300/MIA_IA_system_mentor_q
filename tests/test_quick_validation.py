"""
MIA_IA_SYSTEM - Test Validation Rapide
Test rapide des imports et structure de base
Version: Production Ready
Performance: Validation rapide système
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def test_basic_imports():
    """Test imports de base"""
    print("🧪 Test imports de base...")
    
    try:
        # Test core modules
        from core.logger import get_logger
        print("✅ Core logger importé")
        
        from core.base_types import MarketData, SignalType, MarketRegime
        print("✅ Core base_types importé")
        
        # Test config
        from config.automation_config import AutomationConfig
        print("✅ Config automation importé")
        
        # Test features
        from features.feature_calculator import FeatureCalculator
        print("✅ Features calculator importé")
        
        # Test strategies
        from strategies.signal_generator import SignalGenerator
        print("✅ Strategies signal_generator importé")
        
        # Test ML modules
        from ml.ensemble_filter import MLEnsembleFilter
        print("✅ ML ensemble_filter importé")
        
        from ml.gamma_cycles import GammaCyclesAnalyzer
        print("✅ ML gamma_cycles importé")
        
        # Test monitoring
        from monitoring.performance_tracker import PerformanceTracker
        print("✅ Monitoring performance_tracker importé")
        
        # Test execution
        from execution.simple_trader import SimpleBattleNavaleTrader
        print("✅ Execution simple_trader importé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur import: {e}")
        return False


def test_basic_functionality():
    """Test fonctionnalité de base"""
    print("\n🧪 Test fonctionnalité de base...")
    
    try:
        # Test création MarketData
        from core.base_types import MarketData
        from datetime import datetime
        
        market_data = MarketData(
            timestamp=datetime.now(),
            symbol="ES",
            open=4500.0,
            high=4510.0,
            low=4495.0,
            close=4505.0,
            volume=1000
        )
        print("✅ MarketData créé avec succès")
        
        # Test création config
        from config.automation_config import AutomationConfig
        config = AutomationConfig()
        print("✅ AutomationConfig créé avec succès")
        
        # Test création logger
        from core.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Test logger fonctionnel")
        print("✅ Logger fonctionnel")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur fonctionnalité: {e}")
        return False


def test_ml_modules():
    """Test modules ML"""
    print("\n🧪 Test modules ML...")
    
    try:
        # Test ML Ensemble Filter
        from ml.ensemble_filter import MLEnsembleFilter, EnsembleConfig
        
        config = EnsembleConfig()
        ml_filter = MLEnsembleFilter(config)
        print("✅ ML Ensemble Filter créé")
        
        # Test Gamma Cycles
        from ml.gamma_cycles import GammaCyclesAnalyzer, GammaCycleConfig
        
        gamma_config = GammaCycleConfig()
        gamma_analyzer = GammaCyclesAnalyzer(gamma_config)
        print("✅ Gamma Cycles Analyzer créé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur modules ML: {e}")
        return False


def test_strategies():
    """Test stratégies"""
    print("\n🧪 Test stratégies...")
    
    try:
        # Test Signal Generator
        from strategies.signal_generator import SignalGenerator
        
        signal_gen = SignalGenerator()
        print("✅ Signal Generator créé")
        
        # Test Strategy Selector
        from strategies.strategy_selector import StrategySelector
        
        selector = StrategySelector()
        print("✅ Strategy Selector créé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur stratégies: {e}")
        return False


def test_monitoring():
    """Test monitoring"""
    print("\n🧪 Test monitoring...")
    
    try:
        # Test Performance Tracker
        from monitoring.performance_tracker import PerformanceTracker
        
        tracker = PerformanceTracker()
        print("✅ Performance Tracker créé")
        
        # Test Live Monitor
        from monitoring.live_monitor import LiveMonitor
        
        monitor = LiveMonitor()
        print("✅ Live Monitor créé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur monitoring: {e}")
        return False


def test_execution():
    """Test execution"""
    print("\n🧪 Test execution...")
    
    try:
        # Test Simple Trader
        from execution.simple_trader import SimpleBattleNavaleTrader
        
        trader = SimpleBattleNavaleTrader()
        print("✅ Simple Trader créé")
        
        # Test Trade Snapshotter
        from execution.trade_snapshotter import TradeSnapshotter
        
        snapshotter = TradeSnapshotter()
        print("✅ Trade Snapshotter créé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur execution: {e}")
        return False


def run_quick_validation():
    """Exécuter validation rapide complète"""
    print("🚀 MIA_IA_SYSTEM - Validation Rapide")
    print("=" * 50)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    # Tests par catégorie
    tests = [
        ("Imports de base", test_basic_imports),
        ("Fonctionnalité de base", test_basic_functionality),
        ("Modules ML", test_ml_modules),
        ("Stratégies", test_strategies),
        ("Monitoring", test_monitoring),
        ("Execution", test_execution)
    ]
    
    results = {}
    
    for test_name, test_function in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            success = test_function()
            results[test_name] = success
            
            if success:
                print(f"✅ {test_name}: SUCCÈS")
            else:
                print(f"❌ {test_name}: ÉCHEC")
                
        except Exception as e:
            print(f"❌ {test_name}: ERREUR - {e}")
            results[test_name] = False
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Résultats finaux
    print("\n" + "=" * 50)
    print("🏆 RÉSULTATS VALIDATION RAPIDE")
    print("=" * 50)
    
    passed = sum(1 for success in results.values() if success)
    failed = len(results) - passed
    
    print(f"⏱️  Temps total: {total_time:.2f} secondes")
    print(f"📊 Tests réussis: {passed}/{len(results)}")
    print(f"📊 Tests échoués: {failed}/{len(results)}")
    
    print("\n📋 DÉTAIL PAR CATÉGORIE:")
    for test_name, success in results.items():
        status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
        print(f"  {test_name}: {status}")
    
    if all(results.values()):
        print("\n🎉 VALIDATION RAPIDE RÉUSSIE !")
        print("🚀 SYSTÈME PRÊT POUR TESTS COMPLETS !")
        return True
    else:
        print("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus")
        return False


if __name__ == "__main__":
    success = run_quick_validation()
    if success:
        print("\n🎉 Validation rapide réussie !")
        sys.exit(0)
    else:
        print("\n❌ Validation rapide échouée")
        sys.exit(1) 