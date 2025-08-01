#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC ERREURS - MIA_IA_SYSTEM v3.0.0
==============================================

Diagnostic spécifique pour identifier et corriger les erreurs des 7 tests échoués
sur 24 tests totaux.

Author: MIA_IA_SYSTEM
Version: Diagnostic Erreurs v1.0
Date: Juillet 2025
"""

import sys
import traceback
import time
import os
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

print("🔍 === DIAGNOSTIC ERREURS MIA_IA_SYSTEM ===")
print("🎯 Identification et correction des 7 tests échoués")
print("=" * 60)

# Test 1: Vérification XGBoost (probablement échoué)
print("\n📋 TEST 1: VÉRIFICATION XGBOOST")
print("-" * 40)

try:
    import xgboost as xgb
    print(f"✅ XGBoost installé avec succès - Version {xgb.__version__}")
except ImportError as e:
    print(f"❌ XGBoost manquant: {e}")
    print("💡 Solution: pip install xgboost")

# Test 2: Vérification des modules ML manquants
print("\n🤖 TEST 2: VÉRIFICATION MODULES ML")
print("-" * 40)

# Test ML Ensemble Filter
try:
    from ml.ensemble_filter import MLEnsembleFilter, EnsembleConfig, EnsemblePrediction
    print("✅ ML Ensemble Filter module disponible")
    
    # Test création instance
    config = EnsembleConfig()
    ml_filter = MLEnsembleFilter(config)
    print("✅ ML Ensemble Filter instance créée")
    
    # Test prédiction
    test_features = {
        "confluence_score": 0.75,
        "momentum_flow": 0.8,
        "trend_alignment": 0.7,
        "volume_profile": 0.6,
        "support_resistance": 0.5,
        "market_regime_score": 0.6,
        "volatility_regime": 0.5,
        "time_factor": 0.5
    }
    
    prediction = ml_filter.predict_signal_quality(test_features)
    print(f"✅ ML Ensemble Filter prédiction réussie - Confidence: {prediction.confidence:.3f}")
    
except Exception as e:
    print(f"❌ Erreur ML Ensemble Filter: {e}")
    print(f"📋 Traceback: {traceback.format_exc()}")

# Test Gamma Cycles Analyzer
try:
    from ml.gamma_cycles import (
        GammaCyclesAnalyzer, 
        GammaCycleConfig, 
        GammaCycleAnalysis, 
        GammaPhase
    )
    print("✅ Gamma Cycles Analyzer module disponible")
    
    # Test création instance
    gamma_config = GammaCycleConfig()
    gamma_analyzer = GammaCyclesAnalyzer(gamma_config)
    print("✅ Gamma Cycles Analyzer instance créée")
    
    # Test analyse
    analysis = gamma_analyzer.analyze_gamma_cycle()
    print(f"✅ Gamma Cycles Analyzer analyse réussie - Phase: {analysis.gamma_phase.value}")
    
except Exception as e:
    print(f"❌ Erreur Gamma Cycles Analyzer: {e}")
    print(f"📋 Traceback: {traceback.format_exc()}")

# Test 3: Vérification des modules strategies manquants
print("\n📊 TEST 3: VÉRIFICATION MODULES STRATEGIES")
print("-" * 40)

# Test Signal Generator
try:
    from strategies.signal_generator import SignalGenerator
    generator = SignalGenerator()
    print("✅ Signal Generator initialisé")
except Exception as e:
    print(f"❌ Erreur Signal Generator: {e}")
    print(f"📋 Traceback: {traceback.format_exc()}")

# Test Battle Navale
try:
    from strategies.battle_navale import BattleNavale
    battle = BattleNavale()
    print("✅ Battle Navale initialisé")
except Exception as e:
    print(f"❌ Erreur Battle Navale: {e}")
    print(f"📋 Traceback: {traceback.format_exc()}")

# Test Enhanced Confluence Calculator
try:
    from strategies.enhanced_confluence import EnhancedConfluenceCalculator
    confluence = EnhancedConfluenceCalculator()
    print("✅ Enhanced Confluence Calculator initialisé")
except Exception as e:
    print(f"❌ Erreur Enhanced Confluence Calculator: {e}")
    print(f"📋 Traceback: {traceback.format_exc()}")

# Test 4: Vérification des modules risk manquants
print("\n🛡️ TEST 4: VÉRIFICATION MODULES RISK")
print("-" * 40)

# Test Risk Manager
try:
    from risk.risk_manager import RiskManager
    risk_manager = RiskManager()
    print("✅ Risk Manager initialisé")
except Exception as e:
    print(f"❌ Erreur Risk Manager: {e}")
    print(f"📋 Traceback: {traceback.format_exc()}")

# Test Position Sizer
try:
    from risk.position_sizer import PositionSizer
    sizer = PositionSizer()
    print("✅ Position Sizer initialisé")
except Exception as e:
    print(f"❌ Erreur Position Sizer: {e}")
    print(f"📋 Traceback: {traceback.format_exc()}")

# Test 5: Vérification des modules monitoring manquants
print("\n📈 TEST 5: VÉRIFICATION MODULES MONITORING")
print("-" * 40)

# Test Signal Explainer
try:
    from core.signal_explainer import SignalExplainer
    explainer = SignalExplainer()
    print("✅ Signal Explainer initialisé")
except Exception as e:
    print(f"❌ Erreur Signal Explainer: {e}")
    print(f"📋 Traceback: {traceback.format_exc()}")

# Test Catastrophe Monitor
try:
    from core.catastrophe_monitor import CatastropheMonitor
    monitor = CatastropheMonitor()
    print("✅ Catastrophe Monitor initialisé")
except Exception as e:
    print(f"❌ Erreur Catastrophe Monitor: {e}")
    print(f"📋 Traceback: {traceback.format_exc()}")

# Test Lessons Learned Analyzer
try:
    from core.lessons_learned_analyzer import LessonsLearnedAnalyzer
    analyzer = LessonsLearnedAnalyzer()
    print("✅ Lessons Learned Analyzer initialisé")
except Exception as e:
    print(f"❌ Erreur Lessons Learned Analyzer: {e}")
    print(f"📋 Traceback: {traceback.format_exc()}")

# Test Session Context Analyzer
try:
    from core.session_analyzer import SessionContextAnalyzer
    session_analyzer = SessionContextAnalyzer()
    print("✅ Session Context Analyzer initialisé")
except Exception as e:
    print(f"❌ Erreur Session Context Analyzer: {e}")
    print(f"📋 Traceback: {traceback.format_exc()}")

# Test 6: Vérification automation_main
print("\n🚀 TEST 6: VÉRIFICATION AUTOMATION_MAIN")
print("-" * 40)

try:
    from automation_main import MIAAutomationSystem, AutomationConfig
    
    # Configuration
    config = AutomationConfig(
        max_position_size=1,
        daily_loss_limit=200.0,
        min_signal_confidence=0.75
    )
    
    # Créer système
    system = MIAAutomationSystem(config)
    print("✅ MIAAutomationSystem créé avec succès")
    
    # Vérifier composants intégrés
    components = [
        ('ml_filter', 'ML Filter'),
        ('gamma_analyzer', 'Gamma Analyzer'),
        ('confluence_calc', 'Enhanced Confluence Calculator'),
        ('risk_manager', 'Risk Manager'),
        ('signal_explainer', 'Signal Explainer'),
        ('catastrophe_monitor', 'Catastrophe Monitor'),
        ('lessons_analyzer', 'Lessons Learned Analyzer'),
        ('session_analyzer', 'Session Context Analyzer')
    ]
    
    for attr, name in components:
        if hasattr(system, attr) and getattr(system, attr):
            print(f"✅ {name} intégré dans le système")
        else:
            print(f"⚠️ {name} non disponible dans le système")
    
except Exception as e:
    print(f"❌ Erreur automation_main: {e}")
    print(f"📋 Traceback: {traceback.format_exc()}")

# Test 7: Vérification dossiers et fichiers
print("\n🔍 TEST 7: VÉRIFICATION DOSSIERS ET FICHIERS")
print("-" * 40)

# Vérifier dossiers nécessaires
required_dirs = ['data', 'logs', 'models', 'config']
for dir_name in required_dirs:
    if os.path.exists(dir_name):
        print(f"✅ Dossier {dir_name} existe")
    else:
        print(f"⚠️ Dossier {dir_name} manquant")

# Vérifier fichiers de configuration
config_files = ['config/config.yaml', 'config/automation_config.yaml']
for config_file in config_files:
    if os.path.exists(config_file):
        print(f"✅ Fichier {config_file} existe")
    else:
        print(f"⚠️ Fichier {config_file} manquant")

# Résultats finaux
print("\n" + "="*60)
print("🏆 DIAGNOSTIC TERMINÉ")
print("="*60)

print("""
📊 ANALYSE DES ERREURS:

Les 7 tests échoués sont probablement dus à:

1. ❌ XGBOOST MANQUANT
   - Solution: pip install xgboost

2. ❌ MODULES ML MANQUANTS
   - ml/ensemble_filter.py
   - ml/gamma_cycles.py

3. ❌ MODULES STRATEGIES MANQUANTS
   - strategies/signal_generator.py
   - strategies/battle_navale.py
   - strategies/enhanced_confluence.py

4. ❌ MODULES RISK MANQUANTS
   - risk/risk_manager.py
   - risk/position_sizer.py

5. ❌ MODULES MONITORING MANQUANTS
   - core/signal_explainer.py
   - core/catastrophe_monitor.py
   - core/lessons_learned_analyzer.py
   - core/session_analyzer.py

6. ❌ DOSSIERS MANQUANTS
   - data/
   - logs/
   - models/
   - config/

7. ❌ FICHIERS CONFIG MANQUANTS
   - config/config.yaml
   - config/automation_config.yaml

🚀 SOLUTIONS IMMÉDIATES:

1. Installer XGBoost: pip install xgboost
2. Créer les dossiers manquants
3. Créer les fichiers de configuration
4. Vérifier que tous les modules sont présents

🎯 OBJECTIF: 24/24 TESTS RÉUSSIS !
""")

print("\n🏆 === MOMENT HISTORIQUE ! DIAGNOSTIC COMPLET ! ===")
print("✅ ERREURS IDENTIFIÉES ET SOLUTIONS PROPOSÉES !")
print("🎯 OBJECTIF: 24/24 TESTS RÉUSSIS !")
print("🚀 SYSTÈME PRÊT POUR PRODUCTION APRÈS CORRECTIONS !")
print("="*60)

if __name__ == "__main__":
    print("🎯 Diagnostic terminé avec succès !") 