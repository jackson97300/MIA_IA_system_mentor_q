#!/usr/bin/env python3
"""
🔧 TEST FEATURE CALCULATOR SIMPLIFIÉ
Test spécifique pour identifier le problème exact
"""

import sys
import pandas as pd
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.base_types import MarketData, OrderFlowData

logger = get_logger(__name__)

def test_feature_calculator_step_by_step():
    """Test étape par étape du FeatureCalculator"""
    
    print("🔧 TEST FEATURE CALCULATOR - ÉTAPE PAR ÉTAPE")
    print("="*60)
    
    # ÉTAPE 1: Import des modules
    try:
        print("📦 ÉTAPE 1: Import FeatureCalculator...")
        from features.feature_calculator import FeatureCalculator
        print("✅ FeatureCalculator importé")
    except Exception as e:
        print(f"❌ Erreur import FeatureCalculator: {e}")
        return False
    
    # ÉTAPE 2: Import des constantes
    try:
        print("📦 ÉTAPE 2: Import constantes...")
        from features.feature_calculator import CONFLUENCE_WEIGHTS, TRADING_THRESHOLDS
        print(f"✅ CONFLUENCE_WEIGHTS: {len(CONFLUENCE_WEIGHTS)} features")
        print(f"✅ TRADING_THRESHOLDS: {len(TRADING_THRESHOLDS)} seuils")
    except Exception as e:
        print(f"❌ Erreur import constantes: {e}")
        return False
    
    # ÉTAPE 3: Import FeatureCalculationResult
    try:
        print("📦 ÉTAPE 3: Import FeatureCalculationResult...")
        from features.feature_calculator import FeatureCalculationResult
        print("✅ FeatureCalculationResult importé")
    except Exception as e:
        print(f"❌ Erreur import FeatureCalculationResult: {e}")
        return False
    
    # ÉTAPE 4: Création calculateur
    try:
        print("🏗️ ÉTAPE 4: Création FeatureCalculator...")
        calculator = FeatureCalculator()
        print("✅ FeatureCalculator créé")
    except Exception as e:
        print(f"❌ Erreur création FeatureCalculator: {e}")
        return False
    
    # ÉTAPE 5: Test données
    try:
        print("📊 ÉTAPE 5: Création données test...")
        test_result = FeatureCalculationResult(
            timestamp=pd.Timestamp.now(),
            gamma_levels_proximity=0.8,
            volume_confirmation=0.7,
            vwap_trend_signal=0.6,
            sierra_pattern_strength=0.9,
            mtf_confluence_score=0.8,
            smart_money_strength=0.7,
            order_book_imbalance=0.5,
            options_flow_bias=0.6
        )
        print("✅ FeatureCalculationResult créé")
        print(f"   - timestamp: {test_result.timestamp}")
        print(f"   - gamma_levels_proximity: {test_result.gamma_levels_proximity}")
        print(f"   - smart_money_strength: {test_result.smart_money_strength}")
    except Exception as e:
        print(f"❌ Erreur création FeatureCalculationResult: {e}")
        return False
    
    # ÉTAPE 6: Test méthode _calculate_confluence_score
    try:
        print("🧮 ÉTAPE 6: Test _calculate_confluence_score...")
        
        # Vérifier que la méthode existe
        if not hasattr(calculator, '_calculate_confluence_score'):
            print("❌ Méthode _calculate_confluence_score introuvable")
            return False
        
        print("✅ Méthode _calculate_confluence_score trouvée")
        
        # Appeler la méthode
        confluence_score = calculator._calculate_confluence_score(test_result)
        print(f"✅ Score confluence calculé: {confluence_score:.3f}")
        
        # Vérifications
        if 0.0 <= confluence_score <= 1.0:
            print(f"✅ Score dans la plage valide [0, 1]: {confluence_score:.3f}")
        else:
            print(f"❌ Score hors plage: {confluence_score:.3f}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur calcul confluence_score: {e}")
        print(f"   Type erreur: {type(e).__name__}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False
    
    print("\n🎉 TOUS LES TESTS RÉUSSIS!")
    print(f"📊 Résumé:")
    print(f"   - FeatureCalculator: ✅ Opérationnel")
    print(f"   - Constantes: ✅ Importées")
    print(f"   - FeatureCalculationResult: ✅ Fonctionnel")
    print(f"   - Score confluence: ✅ {confluence_score:.3f}")
    
    return True

def main():
    """Fonction principale"""
    success = test_feature_calculator_step_by_step()
    
    if success:
        print("\n✅ DIAGNOSTIC: FeatureCalculator fonctionne correctement")
    else:
        print("\n❌ DIAGNOSTIC: Problème identifié avec FeatureCalculator")

if __name__ == "__main__":
    main()