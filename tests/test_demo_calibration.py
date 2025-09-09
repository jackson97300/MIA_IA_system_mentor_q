#!/usr/bin/env python3
"""
🧪 TEST DEMO CALIBRATION - MIA_IA_SYSTEM
Test de l'injection automatique de calibration demo permissive
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from features.confluence_integrator import ConfluenceIntegrator
from config.leadership_config import LeadershipCalibration

logger = get_logger(__name__)

def create_test_market_data():
    """Crée des données de marché de test"""
    # Données ES simulées
    es_data = {
        'timestamp': pd.date_range(start='2025-08-23 09:30:00', periods=100, freq='1min'),
        'open': np.random.uniform(4500, 4600, 100),
        'high': np.random.uniform(4500, 4600, 100),
        'low': np.random.uniform(4500, 4600, 100),
        'close': np.random.uniform(4500, 4600, 100),
        'volume': np.random.randint(1000, 5000, 100)
    }
    es_df = pd.DataFrame(es_data)
    
    # Données NQ simulées
    nq_data = {
        'timestamp': pd.date_range(start='2025-08-23 09:30:00', periods=100, freq='1min'),
        'open': np.random.uniform(15000, 16000, 100),
        'high': np.random.uniform(15000, 16000, 100),
        'low': np.random.uniform(15000, 16000, 100),
        'close': np.random.uniform(15000, 16000, 100),
        'volume': np.random.randint(1000, 5000, 100)
    }
    nq_df = pd.DataFrame(nq_data)
    
    return {
        'ES': es_df,
        'NQ': nq_df,
        'bias': 'bullish',
        'symbol': 'ES',
        'now': datetime.now(),
        'gamma_levels': {'call_wall': 4550, 'put_wall': 4500},
        'vwap': 4525.0,
        'gamma_proximity': 0.7,
        'volume_confirmation': 0.6,
        'vwap_trend': 0.5,
        'options_flow': 0.4,
        'order_book_imbalance': 0.3
    }

def test_demo_calibration_injection():
    """Test de l'injection automatique de calibration demo"""
    logger.info("🧪 TEST DEMO CALIBRATION INJECTION")
    logger.info("=" * 50)
    
    # Test 1: Mode normal (pas de demo)
    logger.info("📊 Test 1: Mode normal (demo_mode=False)")
    integrator_normal = ConfluenceIntegrator(demo_mode=False)
    market_data = create_test_market_data()
    
    result_normal = integrator_normal.calculate_confluence_with_leadership(market_data)
    
    logger.info(f"  📊 Résultat normal:")
    logger.info(f"    ✅ Valid: {result_normal.is_valid}")
    logger.info(f"    📈 Score final: {result_normal.final_score:.3f}")
    logger.info(f"    🎯 Leadership gate: {result_normal.leadership_gate:.3f}")
    logger.info(f"    📋 Raison: {result_normal.reason}")
    
    # Test 2: Mode demo (injection automatique)
    logger.info("\n📊 Test 2: Mode demo (demo_mode=True)")
    integrator_demo = ConfluenceIntegrator(demo_mode=True)
    
    result_demo = integrator_demo.calculate_confluence_with_leadership(market_data)
    
    logger.info(f"  📊 Résultat demo:")
    logger.info(f"    ✅ Valid: {result_demo.is_valid}")
    logger.info(f"    📈 Score final: {result_demo.final_score:.3f}")
    logger.info(f"    🎯 Leadership gate: {result_demo.leadership_gate:.3f}")
    logger.info(f"    📋 Raison: {result_demo.reason}")
    
    # Test 3: Mode demo avec calibration explicite
    logger.info("\n📊 Test 3: Mode demo avec calibration explicite")
    explicit_calibration = LeadershipCalibration(
        corr_min=0.05,
        leader_strength_min=0.05,
        persistence_bars=1,
        allow_half_size_if_neutral=True,
        risk_multiplier_tight_corr=0.9,
        risk_multiplier_weak_corr=0.95
    )
    
    integrator_explicit = ConfluenceIntegrator(
        demo_mode=True, 
        calibration=explicit_calibration
    )
    
    result_explicit = integrator_explicit.calculate_confluence_with_leadership(market_data)
    
    logger.info(f"  📊 Résultat explicit:")
    logger.info(f"    ✅ Valid: {result_explicit.is_valid}")
    logger.info(f"    📈 Score final: {result_explicit.final_score:.3f}")
    logger.info(f"    🎯 Leadership gate: {result_explicit.leadership_gate:.3f}")
    logger.info(f"    📋 Raison: {result_explicit.reason}")
    
    # Analyse comparative
    logger.info("\n📊 ANALYSE COMPARATIVE:")
    logger.info(f"  🎯 Normal mode valid rate: {result_normal.is_valid}")
    logger.info(f"  🎯 Demo mode valid rate: {result_demo.is_valid}")
    logger.info(f"  🎯 Explicit demo valid rate: {result_explicit.is_valid}")
    
    # Vérification que demo mode est plus permissif
    if result_demo.is_valid and not result_normal.is_valid:
        logger.info("✅ SUCCÈS: Demo mode plus permissif que normal mode")
    elif result_demo.is_valid == result_normal.is_valid:
        logger.info("⚠️ INFO: Même validité - données de test peut-être trop favorables")
    else:
        logger.warning("❌ ATTENTION: Demo mode moins permissif que normal mode")
    
    logger.info("\n🎯 TEST DEMO CALIBRATION TERMINÉ")

if __name__ == "__main__":
    test_demo_calibration_injection()
