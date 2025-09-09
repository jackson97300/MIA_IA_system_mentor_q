#!/usr/bin/env python3
"""
🧮 TEST CORRÉLATION ES/NQ AVEC DONNÉES RÉELLES
Test avec ES=6397 et NQ=23246
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from calculate_es_nq_correlation import ESNQCorrelationCalculator
from core.logger import get_logger

logger = get_logger(__name__)

def test_correlation_reelle():
    """Test avec les données réelles ES=6397, NQ=23246"""
    logger.info("🧮 TEST CORRÉLATION ES/NQ AVEC DONNÉES RÉELLES")
    logger.info("=" * 60)
    
    calculator = ESNQCorrelationCalculator(window_size=20)
    
    # Données réelles actuelles
    es_actuel = 6397.0
    nq_actuel = 23246.0
    
    logger.info(f"📊 Données réelles actuelles:")
    logger.info(f"  📈 ES: {es_actuel:.2f}")
    logger.info(f"  📈 NQ: {nq_actuel:.2f}")
    logger.info(f"  🔗 Ratio NQ/ES: {nq_actuel/es_actuel:.3f}")
    logger.info("")
    
    # Simulation de mouvements réalistes autour des prix actuels
    mouvements_realistes = [
        (es_actuel, nq_actuel),           # Prix actuels
        (es_actuel + 5, nq_actuel + 20),  # ES +5, NQ +20
        (es_actuel + 3, nq_actuel + 12),  # ES +3, NQ +12
        (es_actuel - 2, nq_actuel - 8),   # ES -2, NQ -8
        (es_actuel + 7, nq_actuel + 28),  # ES +7, NQ +28
        (es_actuel - 4, nq_actuel - 16),  # ES -4, NQ -16
        (es_actuel + 1, nq_actuel + 4),   # ES +1, NQ +4
        (es_actuel + 6, nq_actuel + 24),  # ES +6, NQ +24
        (es_actuel - 3, nq_actuel - 12),  # ES -3, NQ -12
        (es_actuel + 8, nq_actuel + 32),  # ES +8, NQ +32
    ]
    
    logger.info("📊 Test avec mouvements corrélés (ES et NQ bougent ensemble):")
    for i, (es_price, nq_price) in enumerate(mouvements_realistes, 1):
        result = calculator.add_price_data(es_price, nq_price)
        logger.info(f"Point {i}: ES={es_price:.1f}, NQ={nq_price:.1f}")
        logger.info(f"  📈 Corrélation: {result['correlation']:.3f}")
        logger.info(f"  📊 Divergence: {result['divergence']:.3f}")
        logger.info(f"  🎯 Leader: {result['leader']}")
        logger.info(f"  💪 Force: {result['strength']:.3f}")
        logger.info(f"  🔗 Ratio NQ/ES: {result['ratio']:.3f}")
        logger.info(f"  🎯 Score: {result['score']:.3f}")
        logger.info("")
    
    # Test avec divergence (ES monte, NQ baisse)
    logger.info("📊 Test avec divergence (ES monte, NQ baisse):")
    divergence_data = [
        (es_actuel, nq_actuel),
        (es_actuel + 10, nq_actuel - 40),  # ES +10, NQ -40
        (es_actuel + 15, nq_actuel - 60),  # ES +15, NQ -60
        (es_actuel + 20, nq_actuel - 80),  # ES +20, NQ -80
        (es_actuel + 25, nq_actuel - 100), # ES +25, NQ -100
    ]
    
    for i, (es_price, nq_price) in enumerate(divergence_data, 1):
        result = calculator.add_price_data(es_price, nq_price)
        logger.info(f"Point {i}: ES={es_price:.1f}, NQ={nq_price:.1f}")
        logger.info(f"  📈 Corrélation: {result['correlation']:.3f}")
        logger.info(f"  📊 Divergence: {result['divergence']:.3f}")
        logger.info(f"  🔗 Ratio NQ/ES: {result['ratio']:.3f}")
        logger.info("")
    
    # Score final
    final_score = calculator.get_correlation_score()
    logger.info(f"🎯 Score corrélation final: {final_score:.3f}")
    
    # Résumé des métriques
    logger.info("\n📋 RÉSUMÉ DES MÉTRIQUES:")
    if calculator.correlation_history:
        avg_corr = sum(calculator.correlation_history) / len(calculator.correlation_history)
        logger.info(f"  📈 Corrélation moyenne: {avg_corr:.3f}")
    
    if calculator.correlation_ratios:
        avg_ratio = sum(calculator.correlation_ratios) / len(calculator.correlation_ratios)
        logger.info(f"  🔗 Ratio NQ/ES moyen: {avg_ratio:.3f}")
    
    logger.info(f"  🎯 Score final: {final_score:.3f}")
    
    # Recommandations pour le trading
    logger.info("\n💡 RECOMMANDATIONS POUR LE TRADING:")
    if final_score >= 0.8:
        logger.info("  ✅ Corrélation forte - Signaux ES/NQ fiables")
    elif final_score >= 0.6:
        logger.info("  ⚠️ Corrélation modérée - Vérifier divergence")
    else:
        logger.info("  ❌ Corrélation faible - Signaux ES/NQ peu fiables")
    
    if calculator.correlation_ratios:
        current_ratio = calculator.correlation_ratios[-1]
        if abs(current_ratio - 3.6) < 0.1:
            logger.info("  ✅ Ratio NQ/ES normal (3.6 ± 0.1)")
        else:
            logger.info(f"  ⚠️ Ratio NQ/ES anormal: {current_ratio:.3f}")

if __name__ == "__main__":
    test_correlation_reelle()


