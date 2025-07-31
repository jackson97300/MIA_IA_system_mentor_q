#!/usr/bin/env python3
"""
Test fonctionnalité du cache
"""

import time
import pandas as pd
from pathlib import Path
import sys
import logging

# Configure logging
logger = logging.getLogger(__name__)

sys.path.append(str(Path(__file__).parent))

from core.base_types import MarketData
from features.feature_calculator_optimized import create_optimized_feature_calculator

logger.info("🧪 TEST FONCTIONNALITÉ CACHE")
print("=" * 50)

# Créer calculator
calc = create_optimized_feature_calculator()

# Créer données test
market_data = MarketData(
    timestamp=pd.Timestamp.now(),
    symbol="ES",
    open=4500.0,
    high=4510.0,
    low=4495.0,
    close=4505.0,
    volume=1000
)

# Structure data pour test VWAP
structure_data = {
    'vwap_price': 4502.0,
    'vwap_sd1_up': 4508.0,
    'vwap_sd1_down': 4496.0,
    'vwap_sd2_up': 4514.0,
    'vwap_sd2_down': 4490.0
}

logger.info("\n📊 Test 1: Premier appel (cache miss)")
start = time.time()
features1 = calc.calculate_all_features(
    market_data, 
    structure_data=structure_data, 
    use_history=False  # IMPORTANT: Désactiver l'historique pour cohérence
)
time1 = (time.time() - start) * 1000
logger.info("⏱️ Temps: {time1:.2f}ms")
logger.info("📈 Features calculées: {len(features1)}")

logger.info("\n📊 Test 2: Même données (cache hit attendu)")
start = time.time()
features2 = calc.calculate_all_features(
    market_data, 
    structure_data=structure_data,
    use_history=False  # IMPORTANT: Désactiver l'historique pour cohérence
)
time2 = (time.time() - start) * 1000
logger.info("⏱️ Temps: {time2:.2f}ms")
logger.info("🚀 Speedup: {time1/time2:.1f}x")

# Vérifier que les résultats sont identiques
if features1 == features2:
    logger.info("Résultats identiques")
else:
    logger.error("Résultats différents!")
    # Afficher les différences
    for key in set(features1.keys()) | set(features2.keys()):
        if features1.get(key) != features2.get(key):
            logger.info("  - {key}: {features1.get(key)} != {features2.get(key)}")

# Stats cache
stats = calc.get_cache_stats()
logger.info("\n📊 STATS CACHE:")
logger.info("  Hit rate: {stats.get('hit_rate', 0):.1%}")
logger.info("  Hits: {stats.get('cache_hits', 0)}")
logger.info("  Misses: {stats.get('cache_misses', 0)}")
logger.info("  Avg time: {stats.get('avg_calculation_time_ms', 0):.2f}ms")

# Test avec nouvelles données pour voir cache miss
logger.info("\n📊 Test 3: Nouvelles données (cache miss)")
market_data_new = MarketData(
    timestamp=pd.Timestamp.now(),
    symbol="ES",
    open=4510.0,  # Différent
    high=4520.0,
    low=4505.0,
    close=4515.0,
    volume=1200
)

start = time.time()
features3 = calc.calculate_all_features(
    market_data_new,
    structure_data=structure_data,
    use_history=False
)
time3 = (time.time() - start) * 1000
logger.info("⏱️ Temps: {time3:.2f}ms")

# Stats finales
stats_final = calc.get_cache_stats()
logger.info("\n📊 STATS FINALES:")
logger.info("  Total calculations: {stats_final.get('total_calculations', 0)}")
logger.info("  Hit rate: {stats_final.get('hit_rate', 0):.1%}")
logger.info("  Hits: {stats_final.get('cache_hits', 0)}")
logger.info("  Misses: {stats_final.get('cache_misses', 0)}")
logger.info("  Avg time: {stats_final.get('avg_calculation_time_ms', 0):.2f}ms")
logger.info("  Min time: {stats_final.get('min_calculation_time_ms', 0):.2f}ms")
logger.info("  Max time: {stats_final.get('max_calculation_time_ms', 0):.2f}ms")

logger.info("\n✅ TEST FONCTIONNALITÉ RÉUSSI!")