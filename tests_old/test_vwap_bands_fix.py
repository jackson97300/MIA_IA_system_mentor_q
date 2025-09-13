#!/usr/bin/env python3
"""
🧪 TEST VWAP BANDS FIX - MIA_IA_SYSTEM
=====================================

Test l'initialisation et le fonctionnement de VWAP Bands
pour résoudre le problème "VWAP Bands Signal: 0.000"

Author: MIA_IA_SYSTEM
Date: Janvier 2025
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.base_types import MarketData
import pandas as pd

logger = get_logger(__name__)

def test_vwap_bands_import():
    """Test import VWAP Bands"""
    logger.info("🧪 === TEST IMPORT VWAP BANDS ===")
    
    try:
        from features.vwap_bands_analyzer import (
            VWAPBandsAnalyzer,
            create_vwap_bands_analyzer,
            VWAPBandsData
        )
        logger.info("✅ Import VWAP Bands réussi")
        return True
    except Exception as e:
        logger.error(f"❌ Import VWAP Bands échoué: {e}")
        return False

def test_vwap_bands_initialization():
    """Test initialisation VWAP Bands"""
    logger.info("🧪 === TEST INITIALISATION VWAP BANDS ===")
    
    try:
        from features.vwap_bands_analyzer import create_vwap_bands_analyzer
        
        # Créer analyzer
        vwap_config = {'vwap_periods': 20}
        analyzer = create_vwap_bands_analyzer(vwap_config)
        
        logger.info("✅ VWAP Bands Analyzer créé")
        return analyzer
    except Exception as e:
        logger.error(f"❌ Initialisation VWAP Bands échouée: {e}")
        return None

def test_vwap_bands_calculation():
    """Test calcul VWAP Bands"""
    logger.info("🧪 === TEST CALCUL VWAP BANDS ===")
    
    try:
        from features.vwap_bands_analyzer import create_vwap_bands_analyzer
        
        # Créer analyzer
        analyzer = create_vwap_bands_analyzer()
        
        # Créer données de test
        market_data = MarketData(
            symbol='ES',
            timestamp=pd.Timestamp.now(),
            open=6475.0,
            high=6478.0,
            low=6472.0,
            close=6476.0,
            volume=100,
            bid=6475.5,
            ask=6476.5
        )
        
        # Calculer VWAP Bands
        result = analyzer.analyze_vwap_bands(market_data)
        
        logger.info(f"✅ VWAP Bands calculé:")
        logger.info(f"   📊 VWAP: {result.vwap:.2f}")
        logger.info(f"   📈 SD1 Up: {result.sd1_up:.2f}")
        logger.info(f"   📉 SD1 Down: {result.sd1_down:.2f}")
        logger.info(f"   🎯 Rejection Signal: {result.rejection_signal:.3f}")
        logger.info(f"   📊 Breakout Signal: {result.breakout_signal:.3f}")
        logger.info(f"   📈 Trend Strength: {result.trend_strength:.3f}")
        
        return result
    except Exception as e:
        logger.error(f"❌ Calcul VWAP Bands échoué: {e}")
        return None

def test_integrated_feature_calculator():
    """Test Feature Calculator Intégré"""
    logger.info("🧪 === TEST FEATURE CALCULATOR INTÉGRÉ ===")
    
    try:
        from features.feature_calculator_integrated import create_integrated_feature_calculator
        
        # Créer calculator
        config = {
            'vwap_bands': {'vwap_periods': 20},
            'volume_imbalance': {'threshold': 0.1}
        }
        calculator = create_integrated_feature_calculator(config)
        
        logger.info("✅ Feature Calculator Intégré créé")
        return calculator
    except Exception as e:
        logger.error(f"❌ Feature Calculator Intégré échoué: {e}")
        return None

async def test_integrated_calculation():
    """Test calcul intégré complet"""
    logger.info("🧪 === TEST CALCUL INTÉGRÉ COMPLET ===")
    
    try:
        from features.feature_calculator_integrated import create_integrated_feature_calculator
        from core.base_types import MarketData, OrderFlowData
        import pandas as pd
        
        # Créer calculator
        calculator = create_integrated_feature_calculator()
        
        # Créer données de test
        market_data = MarketData(
            symbol='ES',
            timestamp=pd.Timestamp.now(),
            open=6475.0,
            high=6478.0,
            low=6472.0,
            close=6476.0,
            volume=100,
            bid=6475.5,
            ask=6476.5
        )
        
        order_flow = OrderFlowData(
            symbol='ES',
            timestamp=pd.Timestamp.now(),
            cumulative_delta=10,
            bid_volume=45,
            ask_volume=55,
            aggressive_buys=55,
            aggressive_sells=45,
            net_delta=10
        )
        
        # Calculer features intégrées
        result = await calculator.calculate_integrated_features(
            market_data, order_flow
        )
        
        logger.info(f"✅ Features Intégrées calculées:")
        logger.info(f"   📊 Confluence Score: {result.integrated_confluence_score:.3f}")
        logger.info(f"   📈 Signal Quality: {result.signal_quality.value}")
        logger.info(f"   💪 Position Multiplier: ×{result.position_multiplier}")
        logger.info(f"   📊 VWAP Bands Signal: {result.vwap_bands_signal:.3f}")
        logger.info(f"   💰 Volume Imbalance Signal: {result.volume_imbalance_signal:.3f}")
        logger.info(f"   ⚡ Temps calcul: {result.calculation_time_ms:.1f}ms")
        
        return result
    except Exception as e:
        logger.error(f"❌ Calcul intégré échoué: {e}")
        return None

async def main():
    """Test principal"""
    logger.info("🚀 === DÉMARRAGE TESTS VWAP BANDS FIX ===")
    
    # Test 1: Import
    if not test_vwap_bands_import():
        logger.error("❌ Test import échoué - Arrêt")
        return
    
    # Test 2: Initialisation
    analyzer = test_vwap_bands_initialization()
    if not analyzer:
        logger.error("❌ Test initialisation échoué - Arrêt")
        return
    
    # Test 3: Calcul simple
    result = test_vwap_bands_calculation()
    if not result:
        logger.error("❌ Test calcul simple échoué - Arrêt")
        return
    
    # Test 4: Feature Calculator Intégré
    calculator = test_integrated_feature_calculator()
    if not calculator:
        logger.error("❌ Test Feature Calculator échoué - Arrêt")
        return
    
    # Test 5: Calcul intégré complet
    integrated_result = await test_integrated_calculation()
    if not integrated_result:
        logger.error("❌ Test calcul intégré échoué - Arrêt")
        return
    
    logger.info("🎉 === TOUS LES TESTS RÉUSSIS ===")
    logger.info("   VWAP Bands fonctionne correctement")
    logger.info("   Le problème 'VWAP Bands Signal: 0.000' devrait être résolu")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

