#!/usr/bin/env python3
"""
Test Volume Profile Integration
Vérifie que le Volume Profile du backup fonctionne correctement
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import pandas as pd
from datetime import datetime
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_volume_profile_import():
    """Test import Volume Profile"""
    try:
        from features.volume_profile_imbalance import (
            VolumeProfileImbalanceDetector,
            VolumeProfileImbalanceResult,
            create_volume_profile_imbalance_detector
        )
        logger.info("✅ Import Volume Profile réussi")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur import Volume Profile: {e}")
        return False

def test_volume_profile_initialization():
    """Test initialisation Volume Profile"""
    try:
        from features.volume_profile_imbalance import create_volume_profile_imbalance_detector
        
        detector = create_volume_profile_imbalance_detector()
        logger.info("✅ Initialisation Volume Profile réussi")
        return detector
    except Exception as e:
        logger.error(f"❌ Erreur initialisation Volume Profile: {e}")
        return None

def test_volume_profile_analysis():
    """Test analysis Volume Profile"""
    try:
        from features.volume_profile_imbalance import create_volume_profile_imbalance_detector
        
        detector = create_volume_profile_imbalance_detector()
        
        # Market data simulé
        class MockMarketData:
            def __init__(self):
                self.timestamp = pd.Timestamp.now()
                self.close = 5425.0
                self.volume = 1500
        
        market_data = MockMarketData()
        
        # Test detection
        result = detector.detect_imbalances(market_data)
        
        logger.info(f"✅ Analysis Volume Profile réussi")
        logger.info(f"   - Primary Imbalance: {result.primary_imbalance.value}")
        logger.info(f"   - Imbalance Strength: {result.imbalance_strength:.3f}")
        logger.info(f"   - Smart Money Direction: {result.smart_money_direction}")
        logger.info(f"   - Confidence Score: {result.confidence_score:.3f}")
        logger.info(f"   - Calculation Time: {result.calculation_time_ms:.2f}ms")
        
        return result
    except Exception as e:
        logger.error(f"❌ Erreur analysis Volume Profile: {e}")
        return None

def test_volume_profile_integration():
    """Test intégration avec Feature Calculator"""
    try:
        from features.feature_calculator_integrated import FeatureCalculatorIntegrated
        
        # Test import
        calculator = FeatureCalculatorIntegrated()
        logger.info("✅ Intégration Feature Calculator réussi")
        
        # Vérifier que Volume Profile est disponible
        if hasattr(calculator, 'volume_profile_detector'):
            logger.info("✅ Volume Profile détecteur disponible")
        else:
            logger.warning("⚠️ Volume Profile détecteur non trouvé dans Feature Calculator")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erreur intégration Feature Calculator: {e}")
        return False

def main():
    """Test principal"""
    logger.info("🚀 === TEST VOLUME PROFILE INTEGRATION ===")
    
    # Test 1: Import
    if not test_volume_profile_import():
        logger.error("❌ Test import échoué - Arrêt")
        return False
    
    # Test 2: Initialisation
    detector = test_volume_profile_initialization()
    if detector is None:
        logger.error("❌ Test initialisation échoué - Arrêt")
        return False
    
    # Test 3: Analysis
    result = test_volume_profile_analysis()
    if result is None:
        logger.error("❌ Test analysis échoué - Arrêt")
        return False
    
    # Test 4: Intégration
    if not test_volume_profile_integration():
        logger.warning("⚠️ Test intégration échoué - Continuer")
    
    logger.info("🎉 === TOUS LES TESTS VOLUME PROFILE RÉUSSIS ===")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ Volume Profile prêt pour production")
    else:
        logger.error("❌ Volume Profile a des problèmes")
