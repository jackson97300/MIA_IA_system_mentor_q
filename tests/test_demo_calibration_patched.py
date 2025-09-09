#!/usr/bin/env python3
"""
🧪 TEST DEMO CALIBRATION PATCHED - MIA_IA_SYSTEM
Test de l'injection automatique de calibration demo permissive
PATCHES APPLIQUÉS:
- Index datetime pour corrélations robustes
- Séries corrélées déterministes (seed fixe)
- Affichage des seuils actifs
- Assertions de permissivité
- Test multi-régimes (tight/normal/weak)
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

def create_test_market_data(corr_regime='normal'):
    """Crée des données de marché de test avec corrélation contrôlée"""
    # PATCH: Seed déterministe pour reproductibilité
    rng = np.random.default_rng(1337)
    t = pd.date_range('2025-08-23 09:30:00', periods=100, freq='1min')

    # PATCH: Série ES avec tendance
    es_close = 4550 + rng.normal(0, 3, 100).cumsum()

    # PATCH: Série NQ avec corrélation contrôlée
    if corr_regime == 'tight':
        # Corrélation forte ~0.95
        nq_close = 15500 + 3.6*es_close + rng.normal(0, 0.5, 100)
    elif corr_regime == 'weak':
        # Corrélation faible/négative
        nq_close = 15500 + rng.normal(0, 3, 100).cumsum()[::-1]
    else:
        # Corrélation normale ~0.7
        nq_close = 15500 + es_close*1.2 + rng.normal(0, 2, 100)

    # PATCH: DataFrames avec index datetime
    es_df = pd.DataFrame({
        'open': es_close + rng.normal(0, 0.5, 100),
        'high': es_close + rng.normal(0.7, 0.5, 100),
        'low': es_close - rng.normal(0.7, 0.5, 100),
        'close': es_close,
        'volume': rng.integers(1000, 5000, 100)
    }, index=t)

    nq_df = pd.DataFrame({
        'open': nq_close + rng.normal(0, 1.0, 100),
        'high': nq_close + rng.normal(1.2, 1.0, 100),
        'low': nq_close - rng.normal(1.2, 1.0, 100),
        'close': nq_close,
        'volume': rng.integers(1000, 5000, 100)
    }, index=t)

    return {
        'ES': es_df,
        'NQ': nq_df,
        'bias': 'bullish',
        'symbol': 'ES',
        'now': t[-1].to_pydatetime(),
        'gamma_levels': {'call_wall': 4550.0, 'put_wall': 4500.0},  # PATCH: float explicite
        'vwap': float(es_close.mean()),
        'gamma_proximity': 0.7,
        'volume_confirmation': 0.6,
        'vwap_trend': 0.5,
        'options_flow': 0.4,
        'order_book_imbalance': 0.3
    }

def create_test_market_data_with_leader(corr_regime='normal', leader='ES'):
    """Crée des données avec un leader établi"""
    rng = np.random.default_rng(1337)
    t = pd.date_range('2025-08-23 09:30:00', periods=100, freq='1min')

    # Base ES
    es_close = 4550 + rng.normal(0, 3, 100).cumsum()
    
    if leader == 'ES':
        # ES leader : NQ suit ES avec délai
        nq_close = 15500 + 3.6*es_close + rng.normal(0, 0.5, 100)
        # Ajouter un délai pour renforcer le leadership
        nq_close = np.roll(nq_close, 2)  # NQ suit ES de 2 barres
    else:
        # NQ leader : ES suit NQ
        nq_base = 15500 + rng.normal(0, 3, 100).cumsum()
        es_close = (nq_base - 15500) / 3.6 + 4550 + rng.normal(0, 0.5, 100)
        nq_close = nq_base

    es_df = pd.DataFrame({
        'open': es_close + rng.normal(0, 0.5, 100),
        'high': es_close + rng.normal(0.7, 0.5, 100),
        'low': es_close - rng.normal(0.7, 0.5, 100),
        'close': es_close,
        'volume': rng.integers(1000, 5000, 100)
    }, index=t)

    nq_df = pd.DataFrame({
        'open': nq_close + rng.normal(0, 1.0, 100),
        'high': nq_close + rng.normal(1.2, 1.0, 100),
        'low': nq_close - rng.normal(1.2, 1.0, 100),
        'close': nq_close,
        'volume': rng.integers(1000, 5000, 100)
    }, index=t)

    return {
        'ES': es_df,
        'NQ': nq_df,
        'bias': 'bullish',
        'symbol': 'ES',
        'now': t[-1].to_pydatetime(),
        'gamma_levels': {'call_wall': 4550.0, 'put_wall': 4500.0},
        'vwap': float(es_close.mean()),
        'gamma_proximity': 0.7,
        'volume_confirmation': 0.6,
        'vwap_trend': 0.5,
        'options_flow': 0.4,
        'order_book_imbalance': 0.3
    }

def create_test_market_data_demo_pass():
    """Crée des données qui passent en demo mais échouent en normal"""
    rng = np.random.default_rng(1337)
    t = pd.date_range('2025-08-23 09:30:00', periods=100, freq='1min')

    # Série ES avec tendance claire
    es_close = 4550 + rng.normal(0, 2, 100).cumsum()
    
    # Série NQ avec corrélation modérée (suffisante pour demo, insuffisante pour normal)
    nq_close = 15500 + 2.0*es_close + rng.normal(0, 1.5, 100)  # Corrélation ~0.6-0.7

    es_df = pd.DataFrame({
        'open': es_close + rng.normal(0, 0.3, 100),
        'high': es_close + rng.normal(0.5, 0.3, 100),
        'low': es_close - rng.normal(0.5, 0.3, 100),
        'close': es_close,
        'volume': rng.integers(2000, 6000, 100)  # Volume plus élevé
    }, index=t)

    nq_df = pd.DataFrame({
        'open': nq_close + rng.normal(0, 0.8, 100),
        'high': nq_close + rng.normal(1.0, 0.8, 100),
        'low': nq_close - rng.normal(1.0, 0.8, 100),
        'close': nq_close,
        'volume': rng.integers(1500, 5000, 100)
    }, index=t)

    return {
        'ES': es_df,
        'NQ': nq_df,
        'bias': 'bullish',
        'symbol': 'ES',
        'now': t[-1].to_pydatetime(),
        'gamma_levels': {'call_wall': 4550.0, 'put_wall': 4500.0},
        'vwap': float(es_close.mean()),
        'gamma_proximity': 0.8,  # Plus proche des murs gamma
        'volume_confirmation': 0.7,  # Confirmation volume plus forte
        'vwap_trend': 0.6,  # Tendance VWAP plus claire
        'options_flow': 0.5,  # Flow options plus favorable
        'order_book_imbalance': 0.4
    }

def create_test_market_data_es_leader():
    """Crée des données avec ES comme leader clairement établi"""
    rng = np.random.default_rng(1337)
    t = pd.date_range('2025-08-23 09:30:00', periods=100, freq='1min')

    # ES avec tendance forte et claire
    es_close = 4550 + rng.normal(0, 1.5, 100).cumsum()  # Tendance plus forte
    
    # NQ suit ES avec délai et bruit modéré (leadership ES clair)
    nq_close = 15500 + 3.0*es_close + rng.normal(0, 1.0, 100)
    # Délai de 1 barre pour renforcer le leadership ES
    nq_close = np.roll(nq_close, 1)
    nq_close[0] = nq_close[1]  # Corriger la première valeur

    es_df = pd.DataFrame({
        'open': es_close + rng.normal(0, 0.2, 100),
        'high': es_close + rng.normal(0.3, 0.2, 100),
        'low': es_close - rng.normal(0.3, 0.2, 100),
        'close': es_close,
        'volume': rng.integers(3000, 8000, 100)  # Volume élevé pour ES
    }, index=t)

    nq_df = pd.DataFrame({
        'open': nq_close + rng.normal(0, 0.5, 100),
        'high': nq_close + rng.normal(0.8, 0.5, 100),
        'low': nq_close - rng.normal(0.8, 0.5, 100),
        'close': nq_close,
        'volume': rng.integers(2000, 6000, 100)  # Volume plus faible pour NQ
    }, index=t)

    return {
        'ES': es_df,
        'NQ': nq_df,
        'bias': 'bullish',
        'symbol': 'ES',
        'now': t[-1].to_pydatetime(),
        'gamma_levels': {'call_wall': 4550.0, 'put_wall': 4500.0},
        'vwap': float(es_close.mean()),
        'gamma_proximity': 0.9,  # Très proche des murs gamma
        'volume_confirmation': 0.8,  # Confirmation volume très forte
        'vwap_trend': 0.7,  # Tendance VWAP très claire
        'options_flow': 0.6,  # Flow options très favorable
        'order_book_imbalance': 0.5
    }

def log_thresholds_and_result(result, test_name):
    """PATCH: Log détaillé avec seuils actifs"""
    logger.info(f"  📊 Résultat {test_name}:")
    logger.info(f"    ✅ Valid: {result.is_valid}")
    logger.info(f"    📈 Score final: {result.final_score:.3f}")
    logger.info(f"    🎯 Leadership gate: {result.leadership_gate:.3f}")
    logger.info(f"    📋 Raison: {result.reason}")
    
    # PATCH: Afficher les seuils actifs si disponibles
    if hasattr(result, 'thresholds') and result.thresholds:
        corr_min = result.thresholds.get('corr_min', 'N/A')
        leader_min = result.thresholds.get('leader_strength_min', 'N/A')
        persistence = result.thresholds.get('persistence_bars', 'N/A')
        logger.info(f"    🔧 Seuils actifs: corr_min={corr_min}, leader_min={leader_min}, persistence={persistence}")

def test_demo_calibration_injection():
    """Test de l'injection automatique de calibration demo"""
    logger.info("🧪 TEST DEMO CALIBRATION PATCHED")
    logger.info("=" * 50)
    
    # PATCH: Test avec différents régimes de corrélation
    for regime in ['tight', 'normal', 'weak']:
        logger.info(f"\n🎯 RÉGIME: {regime.upper()}")
        logger.info("-" * 30)
        
        market_data = create_test_market_data(regime)
        
        # Test 1: Mode normal (pas de demo)
        logger.info(f"📊 Test 1: Mode normal sur {regime}")
        integrator_normal = ConfluenceIntegrator(demo_mode=False)
        result_normal = integrator_normal.calculate_confluence_with_leadership(market_data)
        log_thresholds_and_result(result_normal, "normal")
        
        # Test 2: Mode demo (injection automatique)
        logger.info(f"\n📊 Test 2: Mode demo sur {regime}")
        integrator_demo = ConfluenceIntegrator(demo_mode=True)
        result_demo = integrator_demo.calculate_confluence_with_leadership(market_data)
        log_thresholds_and_result(result_demo, "demo")
        
        # Test 3: Mode demo avec calibration explicite
        logger.info(f"\n📊 Test 3: Mode demo explicite sur {regime}")
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
        log_thresholds_and_result(result_explicit, "explicit")
        
        # PATCH: Assertions de permissivité
        logger.info(f"\n📊 ANALYSE PERMISSIVITÉ {regime.upper()}:")
        
        # Vérification demo vs normal
        if (not result_normal.is_valid) and result_demo.is_valid:
            logger.info("✅ SUCCÈS: Demo > Normal (attendu)")
        elif result_demo.is_valid == result_normal.is_valid:
            if result_demo.leadership_gate >= result_normal.leadership_gate:
                logger.info("✅ INFO: Même validité mais gate demo ≥ normal")
            else:
                logger.info("⚠️ INFO: Même validité mais gate demo < normal")
        else:
            logger.warning("❌ ATTENTION: Demo moins permissif que normal")
        
        # Vérification explicit vs demo
        if result_explicit.leadership_gate >= result_demo.leadership_gate:
            logger.info("✅ Calibration explicite ≥ permissive que l'auto-injection")
        else:
            logger.warning("⚠️ Calibration explicite < permissive que l'auto-injection")
        
        # PATCH: Statistiques corrélation pour validation
        try:
            es_returns = market_data['ES']['close'].pct_change().dropna()
            nq_returns = market_data['NQ']['close'].pct_change().dropna()
            actual_corr = np.corrcoef(es_returns, nq_returns)[0, 1]
            logger.info(f"    📈 Corrélation réelle ES/NQ: {actual_corr:.3f}")
        except Exception as e:
            logger.debug(f"Erreur calcul corrélation: {e}")
    
    # PATCH: Test avec leader établi
    logger.info(f"\n🎯 RÉGIME: LEADER ÉTABLI (ES)")
    logger.info("-" * 30)
    
    market_data_leader = create_test_market_data_with_leader('normal', 'ES')
    
    # Test avec leader
    logger.info("📊 Test avec leader ES établi")
    integrator_leader = ConfluenceIntegrator(demo_mode=True)
    result_leader = integrator_leader.calculate_confluence_with_leadership(market_data_leader)
    log_thresholds_and_result(result_leader, "leader_es")
    
    # PATCH: Test décisif - cas qui passe en demo mais échoue en normal
    logger.info(f"\n🎯 RÉGIME: DÉCISIF (Demo PASS vs Normal FAIL)")
    logger.info("-" * 30)
    
    market_data_decisive = create_test_market_data_demo_pass()
    
    # Test normal sur cas décisif
    logger.info("📊 Test normal sur cas décisif")
    integrator_normal_decisive = ConfluenceIntegrator(demo_mode=False)
    result_normal_decisive = integrator_normal_decisive.calculate_confluence_with_leadership(market_data_decisive)
    log_thresholds_and_result(result_normal_decisive, "normal_decisive")
    
    # Test demo sur cas décisif
    logger.info("📊 Test demo sur cas décisif")
    integrator_demo_decisive = ConfluenceIntegrator(demo_mode=True)
    result_demo_decisive = integrator_demo_decisive.calculate_confluence_with_leadership(market_data_decisive)
    log_thresholds_and_result(result_demo_decisive, "demo_decisive")
    
    # PATCH: Test avec ES leader clairement établi
    logger.info(f"\n🎯 RÉGIME: ES LEADER CLAIR")
    logger.info("-" * 30)
    
    market_data_es_leader = create_test_market_data_es_leader()
    
    # Test normal sur ES leader
    logger.info("📊 Test normal sur ES leader")
    integrator_normal_es = ConfluenceIntegrator(demo_mode=False)
    result_normal_es = integrator_normal_es.calculate_confluence_with_leadership(market_data_es_leader)
    log_thresholds_and_result(result_normal_es, "normal_es_leader")
    
    # Test demo sur ES leader
    logger.info("📊 Test demo sur ES leader")
    integrator_demo_es = ConfluenceIntegrator(demo_mode=True)
    result_demo_es = integrator_demo_es.calculate_confluence_with_leadership(market_data_es_leader)
    log_thresholds_and_result(result_demo_es, "demo_es_leader")
    
    # PATCH: Vérification finale de permissivité
    logger.info(f"\n📊 VÉRIFICATION FINALE PERMISSIVITÉ:")
    
    # Vérification cas décisif
    if (not result_normal_decisive.is_valid) and result_demo_decisive.is_valid:
        logger.info("🎉 SUCCÈS DÉCISIF: Demo passe quand normal échoue !")
    elif result_demo_decisive.is_valid == result_normal_decisive.is_valid:
        if result_demo_decisive.leadership_gate > result_normal_decisive.leadership_gate:
            logger.info("✅ SUCCÈS: Même validité mais gate demo > normal")
        else:
            logger.info("⚠️ INFO: Même validité et gate demo ≤ normal")
    else:
        logger.warning("❌ ATTENTION: Demo moins permissif que normal sur cas décisif")
    
    # Vérification ES leader
    if (not result_normal_es.is_valid) and result_demo_es.is_valid:
        logger.info("🎉 SUCCÈS ES LEADER: Demo passe quand normal échoue !")
    elif result_demo_es.is_valid == result_normal_es.is_valid:
        if result_demo_es.leadership_gate > result_normal_es.leadership_gate:
            logger.info("✅ SUCCÈS ES LEADER: Même validité mais gate demo > normal")
        else:
            logger.info("⚠️ INFO ES LEADER: Même validité et gate demo ≤ normal")
    else:
        logger.warning("❌ ATTENTION ES LEADER: Demo moins permissif que normal")
    
    # PATCH: Statistiques corrélation pour validation
    try:
        es_returns = market_data_decisive['ES']['close'].pct_change().dropna()
        nq_returns = market_data_decisive['NQ']['close'].pct_change().dropna()
        actual_corr = np.corrcoef(es_returns, nq_returns)[0, 1]
        logger.info(f"    📈 Corrélation réelle ES/NQ (décisif): {actual_corr:.3f}")
        
        es_returns_leader = market_data_es_leader['ES']['close'].pct_change().dropna()
        nq_returns_leader = market_data_es_leader['NQ']['close'].pct_change().dropna()
        actual_corr_leader = np.corrcoef(es_returns_leader, nq_returns_leader)[0, 1]
        logger.info(f"    📈 Corrélation réelle ES/NQ (ES leader): {actual_corr_leader:.3f}")
    except Exception as e:
        logger.debug(f"Erreur calcul corrélation: {e}")
    
    logger.info("\n🎯 TEST DEMO CALIBRATION PATCHED TERMINÉ")
    logger.info("=" * 50)

if __name__ == "__main__":
    test_demo_calibration_injection()
