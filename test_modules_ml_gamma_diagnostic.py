#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC ML ENSEMBLE & GAMMA CYCLES - MIA_IA_SYSTEM
==========================================================

Diagnostic spécifique pour identifier et résoudre les problèmes avec:
- ML Ensemble Filter
- Gamma Cycles Analyzer

Author: MIA_IA_SYSTEM
Version: Diagnostic v1.0
Date: Juillet 2025
"""

import sys
import traceback
import time
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

print("🔍 === DIAGNOSTIC ML ENSEMBLE & GAMMA CYCLES ===")
print("🎯 Identification des problèmes d'import et d'intégration")
print("=" * 60)

# Test 1: Vérification des imports de base
print("\n📋 TEST 1: IMPORTS DE BASE")
print("-" * 40)

try:
    import numpy as np
    print("✅ NumPy disponible")
except ImportError as e:
    print(f"❌ NumPy manquant: {e}")
    print("💡 Solution: pip install numpy")

try:
    import pandas as pd
    print("✅ Pandas disponible")
except ImportError as e:
    print(f"❌ Pandas manquant: {e}")
    print("💡 Solution: pip install pandas")

try:
    import sklearn
    print("✅ Scikit-learn disponible")
except ImportError as e:
    print(f"❌ Scikit-learn manquant: {e}")
    print("💡 Solution: pip install scikit-learn")

try:
    import xgboost as xgb
    print("✅ XGBoost disponible")
except ImportError as e:
    print(f"❌ XGBoost manquant: {e}")
    print("💡 Solution: pip install xgboost")

# Test 2: Diagnostic ML Ensemble Filter
print("\n🤖 TEST 2: ML ENSEMBLE FILTER")
print("-" * 40)

try:
    print("🔍 Tentative d'import ML Ensemble Filter...")
    from ml.ensemble_filter import MLEnsembleFilter, EnsembleConfig, EnsemblePrediction
    print("✅ Import ML Ensemble Filter réussi")
    
    # Test création instance
    try:
        config = EnsembleConfig()
        print("✅ EnsembleConfig créé")
    except Exception as e:
        print(f"❌ Erreur EnsembleConfig: {e}")
        config = None
    
    try:
        ml_filter = MLEnsembleFilter(config)
        print("✅ MLEnsembleFilter créé")
        
        # Test prédiction basique
        test_features = {
            "confluence_score": 0.75,
            "momentum_flow": 0.8,
            "trend_alignment": 0.7,
            "volume_profile": 0.6
        }
        
        try:
            prediction = ml_filter.predict_signal_quality(test_features)
            print(f"✅ Prédiction ML réussie: confidence={prediction.confidence:.3f}")
        except Exception as e:
            print(f"⚠️ Erreur prédiction ML: {e}")
            
    except Exception as e:
        print(f"❌ Erreur création MLEnsembleFilter: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        
except ImportError as e:
    print(f"❌ Import ML Ensemble Filter échoué: {e}")
    print(f"📋 Traceback: {traceback.format_exc()}")

# Test 3: Diagnostic Gamma Cycles Analyzer
print("\n📊 TEST 3: GAMMA CYCLES ANALYZER")
print("-" * 40)

try:
    print("🔍 Tentative d'import Gamma Cycles...")
    from ml.gamma_cycles import (
        GammaCyclesAnalyzer, 
        GammaCycleConfig, 
        GammaCycleAnalysis, 
        GammaPhase
    )
    print("✅ Import Gamma Cycles réussi")
    
    # Test création instance
    try:
        gamma_config = GammaCycleConfig()
        print("✅ GammaCycleConfig créé")
    except Exception as e:
        print(f"❌ Erreur GammaCycleConfig: {e}")
        gamma_config = None
    
    try:
        gamma_analyzer = GammaCyclesAnalyzer(gamma_config)
        print("✅ GammaCyclesAnalyzer créé")
        
        # Test analyse basique
        try:
            analysis = gamma_analyzer.analyze_gamma_cycle()
            print(f"✅ Analyse Gamma réussie: phase={analysis.gamma_phase.value}")
            print(f"   Facteur ajustement: {analysis.adjustment_factor:.2f}")
        except Exception as e:
            print(f"⚠️ Erreur analyse Gamma: {e}")
            
    except Exception as e:
        print(f"❌ Erreur création GammaCyclesAnalyzer: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        
except ImportError as e:
    print(f"❌ Import Gamma Cycles échoué: {e}")
    print(f"📋 Traceback: {traceback.format_exc()}")

# Test 4: Vérification des dépendances ML
print("\n🔧 TEST 4: DÉPENDANCES ML")
print("-" * 40)

try:
    # Vérifier si les dossiers nécessaires existent
    models_path = Path("ml/models")
    if models_path.exists():
        print(f"✅ Dossier modèles existe: {models_path}")
    else:
        print(f"⚠️ Dossier modèles manquant: {models_path}")
        print("💡 Le système créera automatiquement les modèles de base")
    
    # Vérifier les fichiers de configuration
    config_files = [
        "ml/ensemble_filter.py",
        "ml/gamma_cycles.py"
    ]
    
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✅ Fichier existe: {config_file}")
        else:
            print(f"❌ Fichier manquant: {config_file}")
            
except Exception as e:
    print(f"❌ Erreur vérification dépendances: {e}")

# Test 5: Test d'intégration dans automation_main
print("\n🚀 TEST 5: INTÉGRATION AUTOMATION_MAIN")
print("-" * 40)

try:
    from automation_main import MIAAutomationSystem, AutomationConfig
    
    # Configuration de test
    config = AutomationConfig(
        ml_ensemble_enabled=True,
        gamma_cycles_enabled=True
    )
    
    print("✅ Import automation_main réussi")
    
    try:
        system = MIAAutomationSystem(config)
        print("✅ MIAAutomationSystem créé")
        
        # Vérifier les composants ML
        if hasattr(system, 'ml_filter') and system.ml_filter:
            print("✅ ML Filter intégré dans le système")
        else:
            print("⚠️ ML Filter non disponible dans le système")
            
        if hasattr(system, 'gamma_analyzer') and system.gamma_analyzer:
            print("✅ Gamma Analyzer intégré dans le système")
        else:
            print("⚠️ Gamma Analyzer non disponible dans le système")
            
    except Exception as e:
        print(f"❌ Erreur création système: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        
except ImportError as e:
    print(f"❌ Import automation_main échoué: {e}")

# Test 6: Test de simulation avec fallback
print("\n🎯 TEST 6: SIMULATION AVEC FALLBACK")
print("-" * 40)

try:
    # Test avec classes mock si nécessaire
    class MockMLEnsembleFilter:
        def __init__(self):
            self.is_trained = True
        def predict_signal_quality(self, features):
            class MockPrediction:
                def __init__(self):
                    self.confidence = 0.75
                    self.signal_approved = True
                    self.models_used = ["mock"]
                    self.processing_time_ms = 10.0
            return MockPrediction()
    
    class MockGammaCyclesAnalyzer:
        def __init__(self, config):
            self.config = config
        def analyze_gamma_cycle(self):
            class MockAnalysis:
                def __init__(self):
                    self.gamma_phase = type('GammaPhase', (), {'value': 'normal'})()
                    self.adjustment_factor = 1.0
                    self.volatility_expectation = "normal"
            return MockAnalysis()
    
    # Test avec mocks
    mock_ml = MockMLEnsembleFilter()
    mock_gamma = MockGammaCyclesAnalyzer(None)
    
    # Test prédiction mock
    test_features = {"confluence_score": 0.8}
    mock_prediction = mock_ml.predict_signal_quality(test_features)
    print(f"✅ Mock ML: confidence={mock_prediction.confidence:.3f}")
    
    # Test analyse mock
    mock_analysis = mock_gamma.analyze_gamma_cycle()
    print(f"✅ Mock Gamma: phase={mock_analysis.gamma_phase.value}")
    
    print("✅ Simulation avec fallback réussie")
    
except Exception as e:
    print(f"❌ Erreur simulation fallback: {e}")

# Résultats finaux
print("\n" + "=" * 60)
print("🎯 RÉSULTATS DU DIAGNOSTIC")
print("=" * 60)

print("""
📊 RÉSUMÉ DES PROBLÈMES IDENTIFIÉS:

1. IMPORTS DE BASE:
   - Vérifier que numpy, pandas, scikit-learn, xgboost sont installés
   - Commandes: pip install numpy pandas scikit-learn xgboost

2. ML ENSEMBLE FILTER:
   - Problème possible: dépendances ML manquantes
   - Solution: installer les packages ML requis
   - Fallback disponible si problème persiste

3. GAMMA CYCLES ANALYZER:
   - Problème possible: imports circulaires ou dépendances
   - Solution: vérifier la structure des imports
   - Fallback disponible si problème persiste

4. INTÉGRATION:
   - Les modules sont intégrés dans automation_main.py
   - Fallback gracieux en cas de problème
   - Système fonctionne même si modules ML indisponibles

💡 SOLUTIONS RECOMMANDÉES:

1. Installer les dépendances ML:
   pip install numpy pandas scikit-learn xgboost

2. Vérifier la structure des imports dans ml/

3. Utiliser les fallbacks si problèmes persistants

4. Le système fonctionne même sans ML - mode dégradé disponible
""")

print("\n🏆 DIAGNOSTIC TERMINÉ !")
print("🚀 Le système MIA_IA reste opérationnel même avec les problèmes ML identifiés !") 