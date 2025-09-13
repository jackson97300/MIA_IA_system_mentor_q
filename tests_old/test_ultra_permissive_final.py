#!/usr/bin/env python3
"""
🧪 TEST ULTRA-PERMISSIF FINAL - MIA_IA_SYSTEM
Test qui force directement les paramètres pour atteindre 25-30% de valid rate
- Bypass complet du config manager avec lock
- Paramètres ultra-permissifs
- 60 itérations
"""

import sys
import random
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from features.confluence_integrator import ConfluenceIntegrator
from config.leadership_config import LeadershipConfigManager, LeadershipCalibration

logger = get_logger(__name__)

# Seed pour reproductibilité
RNG_SEED = 1337
np.random.seed(RNG_SEED)
random.seed(RNG_SEED)

def create_realistic_test_data(seed: int, regime: str = 'normal'):
    """Crée des données de test réalistes"""
    rng = np.random.default_rng(seed)
    dates = pd.date_range('2025-08-22 15:00:00', periods=120, freq='1min')
    
    # ES: tendance haussière avec volatilité
    es_base = 6397
    es_trend = rng.normal(0.2, 0.5, 120).cumsum()
    es_noise = rng.normal(0, 0.1, 120)
    es_prices = es_base + es_trend + es_noise
    
    es_data = pd.DataFrame({
        'close': es_prices,
        'volume': 1000 + rng.normal(0, 100, 120),
        'buy_volume': 600 + rng.normal(0, 50, 120),
        'sell_volume': 400 + rng.normal(0, 50, 120)
    }, index=dates)
    
    # NQ: corrélation selon le régime
    nq_base = 23246
    
    if regime == 'tight':
        # Corrélation très serrée (>0.9)
        nq_prices = es_prices * 3.63 + rng.normal(0, 0.001, 120)
    elif regime == 'weak':
        # Corrélation faible (<0.7)
        nq_trend = rng.normal(0.1, 0.8, 120).cumsum()
        nq_noise = rng.normal(0, 0.2, 120)
        nq_prices = nq_base + nq_trend + nq_noise
        nq_prices = nq_prices[::-1]  # Décorréler
    else:
        # Corrélation normale (0.7-0.9)
        nq_trend = rng.normal(0.1, 0.8, 120).cumsum()
        nq_noise = rng.normal(0, 0.2, 120)
        nq_prices = nq_base + nq_trend + nq_noise
    
    nq_data = pd.DataFrame({
        'close': nq_prices,
        'volume': 800 + rng.normal(0, 80, 120),
        'buy_volume': 450 + rng.normal(0, 40, 120),
        'sell_volume': 350 + rng.normal(0, 40, 120)
    }, index=dates)
    
    return es_data, nq_data

def test_ultra_permissive_final():
    """Test ultra-permissif final pour atteindre 25-30%"""
    logger.info("🎯 TEST ULTRA-PERMISSIF FINAL - Objectif 25-30%")
    logger.info("=" * 60)
    
    # 1. Configuration ULTRA-permissive
    ultra_calibration = LeadershipCalibration(
        corr_min=0.05,  # Seuil ultra-permissif
        leader_strength_min=0.05,  # Ultra-permissif
        persistence_bars=1,  # Très rapide
        risk_multiplier_tight_corr=0.8,
        risk_multiplier_weak_corr=0.9,
        allow_half_size_if_neutral=True
    )
    
    # 2. PATCH: Forcer la calibration demo dans le config manager AVANT d'initialiser
    config_manager = LeadershipConfigManager(auto_load=False)
    config_manager.set_calibration(ultra_calibration, lock=True)
    
    # 3. Initialiser l'intégrateur en mode demo
    integrator = ConfluenceIntegrator(
        max_latency_ms=50,
        calibration=ultra_calibration,
        demo_mode=True
    )
    
    logger.info("⚙️ Configuration ULTRA-PERMISSIVE:")
    logger.info(f"  📈 Corr min: {ultra_calibration.corr_min}")
    logger.info(f"  💪 Leader strength min: {ultra_calibration.leader_strength_min}")
    logger.info(f"  ⏱️ Persistence bars: {ultra_calibration.persistence_bars}")
    logger.info(f"  🎯 Demo mode: {integrator.demo_mode}")
    
    # 4. Test sur 60 itérations
    total_tests = 60
    valid_count = 0
    results = []
    
    logger.info(f"\n🧪 Test sur {total_tests} itérations...")
    
    for i in range(total_tests):
        # Alterner les régimes pour variété
        regime = ['normal', 'tight', 'weak'][i % 3]
        bias = ['bullish', 'bearish', 'neutral'][i % 3]
        instrument = ['ES', 'NQ'][i % 2]
        
        # Créer données
        es_data, nq_data = create_realistic_test_data(RNG_SEED + i, regime)
        
        # Données de marché
        market_data = {
            'ES': es_data,
            'NQ': nq_data,
            'bias': bias,
            'symbol': instrument,
            'now': datetime.now(),
            'gamma_levels': [6400, 6450, 6500],
            'gamma_proximity': 0.6 + 0.3 * np.random.random(),
            'volume_confirmation': 0.5 + 0.4 * np.random.random(),
            'vwap_trend': 0.4 + 0.5 * np.random.random(),
            'options_flow': 0.3 + 0.6 * np.random.random(),
            'order_book_imbalance': 0.2 + 0.7 * np.random.random(),
            'demo_mode': True
        }
        
        # Test d'intégration
        result = integrator.calculate_confluence_with_leadership(market_data)
        
        # Collecter résultats
        if result.is_valid:
            valid_count += 1
        
        results.append({
            'iteration': i + 1,
            'regime': regime,
            'bias': bias,
            'instrument': instrument,
            'is_valid': result.is_valid,
            'final_score': result.final_score,
            'leadership_gate': result.leadership_gate,
            'reason': result.reason,
            'corr_15m': result.market_state.corr_15m,
            'leader': result.leadership_result.leader
        })
        
        # Log progress
        if (i + 1) % 10 == 0:
            current_rate = (valid_count / (i + 1)) * 100
            logger.info(f"  📊 Itération {i+1}/{total_tests}: {valid_count} validés ({current_rate:.1f}%)")
    
    # 5. Analyse des résultats
    valid_rate = (valid_count / total_tests) * 100
    
    logger.info(f"\n📋 RÉSULTATS FINAUX:")
    logger.info(f"  🎯 Valid rate: {valid_rate:.1f}% ({valid_count}/{total_tests})")
    logger.info(f"  📈 Objectif atteint: {'✅ OUI' if 25 <= valid_rate <= 30 else '❌ NON'}")
    
    # 6. Statistiques détaillées
    stats = integrator.get_statistics()
    logger.info(f"\n📊 STATISTIQUES DÉTAILLÉES:")
    logger.info(f"  📊 Intégrations: {stats['integration_count']}")
    logger.info(f"  ⏱️ Latence dépassée: {stats['latency_exceeded_rate']:.1%}")
    logger.info(f"  ✅ Pass rate: {stats['leadership_stats']['pass_rate']:.1%}")
    logger.info(f"  ❌ Reject rate: {stats['leadership_stats']['reject_rate']:.1%}")
    logger.info(f"  ⚠️ Downgrade rate: {stats['leadership_stats']['downgrade_rate']:.1%}")
    
    # 7. Monitoring par régime
    if 'regime_monitoring' in stats:
        logger.info(f"\n📈 MONITORING PAR RÉGIME:")
        for regime in stats['regime_monitoring']:
            logger.info(f"  {regime['session']} | {regime['corr_regime']} | {regime['gamma_regime']}: "
                       f"{regime['count']} tests, {regime['pass_pct']:.1%} pass, "
                       f"avg_risk={regime['avg_risk']:.3f}")
    
    # 8. Analyse des raisons de rejet
    reject_reasons = {}
    for r in results:
        if not r['is_valid']:
            reason = r['reason']
            reject_reasons[reason] = reject_reasons.get(reason, 0) + 1
    
    logger.info(f"\n🚫 RAISONS DE REJET:")
    for reason, count in sorted(reject_reasons.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_tests) * 100
        logger.info(f"  📝 {reason}: {count} fois ({percentage:.1f}%)")
    
    # 9. Recommandations
    logger.info(f"\n💡 RECOMMANDATIONS:")
    if valid_rate < 25:
        logger.info("  🔧 Augmenter la permissivité:")
        logger.info("    - Réduire corr_min (actuel: 0.05)")
        logger.info("    - Réduire leader_strength_min (actuel: 0.05)")
        logger.info("    - Réduire persistence_bars (actuel: 1)")
    elif valid_rate > 30:
        logger.info("  🔧 Réduire la permissivité:")
        logger.info("    - Augmenter corr_min")
        logger.info("    - Augmenter leader_strength_min")
        logger.info("    - Augmenter persistence_bars")
    else:
        logger.info("  ✅ Configuration optimale atteinte!")
    
    return valid_rate, results

if __name__ == "__main__":
    test_ultra_permissive_final()

