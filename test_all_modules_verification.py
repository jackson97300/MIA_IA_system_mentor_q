#!/usr/bin/env python3
"""
🔍 VÉRIFICATION COMPLÈTE DE TOUS LES MODULES
Test systématique de tous les fichiers du projet MIA_IA_SYSTEM
"""

import sys
import importlib
from pathlib import Path
import traceback

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

def test_module_import(module_path, module_name):
    """Test import d'un module spécifique"""
    try:
        module = importlib.import_module(module_path)
        return True, f"✅ {module_name}: Import OK"
    except Exception as e:
        return False, f"❌ {module_name}: {str(e)}"

def verify_all_modules():
    """Vérification complète de tous les modules"""
    print("🔍 VÉRIFICATION COMPLÈTE DES MODULES MIA_IA_SYSTEM")
    print("="*70)
    
    results = {}
    
    # === CORE MODULES ===
    print("\n📦 MODULES CORE")
    print("-" * 30)
    core_modules = [
        ("core.logger", "Logger"),
        ("core.base_types", "BaseTypes"),
        ("core.trading_types", "TradingTypes"),
        ("core.structure_data", "StructureData"),
        ("core.ibkr_connector", "IBKRConnector"),
        ("core.sierra_connector", "SierraConnector"),
        ("core.battle_navale", "BattleNavale"),
        ("core.patterns_detector", "PatternsDetector"),
        ("core.signal_explainer", "SignalExplainer"),
        ("core.catastrophe_monitor", "CatastropheMonitor"),
        ("core.lessons_learned_analyzer", "LessonsLearnedAnalyzer"),
        ("core.session_analyzer", "SessionAnalyzer"),
        ("core.mentor_system", "MentorSystem")
    ]
    
    for module_path, module_name in core_modules:
        success, message = test_module_import(module_path, module_name)
        results[f"core_{module_name}"] = success
        print(message)
    
    # === FEATURES MODULES ===
    print("\n📊 MODULES FEATURES")
    print("-" * 30)
    features_modules = [
        ("features.feature_calculator", "FeatureCalculator"),
        ("features.smart_money_tracker", "SmartMoneyTracker"),
        ("features.order_book_imbalance", "OrderBookImbalance"),
        ("features.mtf_confluence_elite", "MTFConfluenceElite"),
        ("features.confluence_analyzer", "ConfluenceAnalyzer"),
        ("features.market_regime", "MarketRegime"),
        ("features.advanced.delta_divergence", "DeltaDivergence"),
        ("features.advanced.volatility_regime", "VolatilityRegime"),
        ("features.advanced.tick_momentum", "TickMomentum"),
        ("features.advanced.session_optimizer", "SessionOptimizer")
    ]
    
    for module_path, module_name in features_modules:
        success, message = test_module_import(module_path, module_name)
        results[f"features_{module_name}"] = success
        print(message)
    
    # === STRATEGIES MODULES ===
    print("\n🎯 MODULES STRATEGIES")
    print("-" * 30)
    strategies_modules = [
        ("strategies.signal_generator", "SignalGenerator"),
        ("strategies.trend_strategy", "TrendStrategy"),
        ("strategies.range_strategy", "RangeStrategy"),
        ("strategies.strategy_selector", "StrategySelector"),
        ("strategies.signal_core.signal_generator_core", "SignalGeneratorCore"),
        ("strategies.signal_core.confidence_calculator", "ConfidenceCalculator"),
        ("strategies.signal_core.quality_validator", "QualityValidator")
    ]
    
    for module_path, module_name in strategies_modules:
        success, message = test_module_import(module_path, module_name)
        results[f"strategies_{module_name}"] = success
        print(message)
    
    # === EXECUTION MODULES ===
    print("\n⚡ MODULES EXECUTION")
    print("-" * 30)
    execution_modules = [
        ("execution.order_manager", "OrderManager"),
        ("execution.risk_manager", "RiskManager"),
        ("execution.simple_trader", "SimpleTrader"),
        ("execution.trade_snapshotter", "TradeSnapshotter"),
        ("execution.post_mortem_analyzer", "PostMortemAnalyzer")
    ]
    
    for module_path, module_name in execution_modules:
        success, message = test_module_import(module_path, module_name)
        results[f"execution_{module_name}"] = success
        print(message)
    
    # === MONITORING MODULES ===
    print("\n📡 MODULES MONITORING")
    print("-" * 30)
    monitoring_modules = [
        ("monitoring.live_monitor", "LiveMonitor"),
        ("monitoring.health_checker", "HealthChecker"),
        ("monitoring.performance_tracker", "PerformanceTracker"),
        ("monitoring.alert_system", "AlertSystem"),
        ("monitoring.discord_notifier", "DiscordNotifier"),
        ("monitoring.session_replay", "SessionReplay")
    ]
    
    for module_path, module_name in monitoring_modules:
        success, message = test_module_import(module_path, module_name)
        results[f"monitoring_{module_name}"] = success
        print(message)
    
    # === AUTOMATION MODULES ===
    print("\n🤖 MODULES AUTOMATION")
    print("-" * 30)
    automation_modules = [
        ("automation_modules.config_manager", "ConfigManager"),
        ("automation_modules.trading_engine", "TradingEngine"),
        ("automation_modules.risk_manager", "AutoRiskManager"),
        ("automation_modules.performance_tracker", "AutoPerformanceTracker"),
        ("automation_modules.order_manager", "AutoOrderManager"),
        ("automation_modules.optimized_trading_system", "OptimizedTradingSystem"),
        ("automation_modules.sierra_connector", "AutoSierraConnector"),
        ("automation_modules.sierra_optimizer", "SierraOptimizer"),
        ("automation_modules.confluence_calculator", "ConfluenceCalculator")
    ]
    
    for module_path, module_name in automation_modules:
        success, message = test_module_import(module_path, module_name)
        results[f"automation_{module_name}"] = success
        print(message)
    
    # === CONFIG MODULES ===
    print("\n⚙️ MODULES CONFIG")
    print("-" * 30)
    config_modules = [
        ("config.automation_config", "AutomationConfig"),
        ("config.trading_config", "TradingConfig"),
        ("config.ml_config", "MLConfig"),
        ("config.logging_config", "LoggingConfig"),
        ("config.constants", "Constants"),
        ("config.sierra_config", "SierraConfig")
    ]
    
    for module_path, module_name in config_modules:
        success, message = test_module_import(module_path, module_name)
        results[f"config_{module_name}"] = success
        print(message)
    
    # === ML MODULES ===
    print("\n🧠 MODULES ML")
    print("-" * 30)
    ml_modules = [
        ("ml.simple_model", "SimpleModel"),
        ("ml.data_processor", "DataProcessor"),
        ("ml.model_trainer", "ModelTrainer"),
        ("ml.model_validator", "ModelValidator"),
        ("ml.ensemble_filter", "EnsembleFilter"),
        ("ml.gamma_cycles", "GammaCycles")
    ]
    
    for module_path, module_name in ml_modules:
        success, message = test_module_import(module_path, module_name)
        results[f"ml_{module_name}"] = success
        print(message)
    
    # === PERFORMANCE MODULES ===
    print("\n📈 MODULES PERFORMANCE")
    print("-" * 30)
    performance_modules = [
        ("performance.performance_analyzer", "PerformanceAnalyzer"),
        ("performance.trade_logger", "TradeLogger"),
        ("performance.automation_metrics", "AutomationMetrics"),
        ("performance.adaptive_optimizer", "AdaptiveOptimizer")
    ]
    
    for module_path, module_name in performance_modules:
        success, message = test_module_import(module_path, module_name)
        results[f"performance_{module_name}"] = success
        print(message)
    
    # === RÉSULTATS FINAUX ===
    print("\n" + "="*70)
    print("📊 RÉSULTATS VÉRIFICATION COMPLÈTE")
    print("="*70)
    
    total_modules = len(results)
    successful_modules = sum(results.values())
    failed_modules = total_modules - successful_modules
    
    print(f"📦 Total modules testés: {total_modules}")
    print(f"✅ Modules OK: {successful_modules}")
    print(f"❌ Modules ÉCHEC: {failed_modules}")
    print(f"📊 Taux de succès: {(successful_modules/total_modules)*100:.1f}%")
    
    if failed_modules > 0:
        print(f"\n⚠️ MODULES EN ÉCHEC:")
        for module_name, success in results.items():
            if not success:
                print(f"   ❌ {module_name}")
    
    if successful_modules == total_modules:
        print("\n🎉 TOUS LES MODULES SONT OPÉRATIONNELS!")
        print("✅ Système MIA_IA_SYSTEM prêt pour production")
    else:
        print(f"\n⚠️ {failed_modules} modules nécessitent des corrections")
        
    return results

def main():
    """Fonction principale"""
    try:
        results = verify_all_modules()
        return results
    except Exception as e:
        print(f"❌ Erreur durant la vérification: {e}")
        traceback.print_exc()
        return {}

if __name__ == "__main__":
    main()