#!/usr/bin/env python3
"""
Test de debug pour comprendre pourquoi le cache ne fonctionne pas
"""

import time
import pandas as pd
import numpy as np
import sys
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)


# Ajouter le dossier parent au path
sys.path.append(str(Path(__file__).parent))

# Import des composants
from core.base_types import MarketData
from features import create_feature_calculator

def test_basic_cache():
    """Test le plus basique possible du cache"""
    logger.debug("TEST DEBUG DU CACHE")
    print("=" * 50)
    
    # Créer calculator
    calculator = create_feature_calculator(
        optimized=True,
        cache_config={
            'cache_ttl': 300,
            'cache_size': 100
        }
    )
    
    # Vérifier le type de calculator
    logger.info("📊 Type de calculator: {type(calculator).__name__}")
    logger.info("📊 A la méthode get_cache_stats: {hasattr(calculator, 'get_cache_stats')}")
    
    # Créer données identiques
    timestamp = pd.Timestamp.now()
    data1 = MarketData(
        timestamp=timestamp,
        symbol="ES",
        open=4500.0,
        high=4510.0,
        low=4495.0,
        close=4505.0,
        volume=1000
    )
    
    # Copie exacte
    data2 = MarketData(
        timestamp=timestamp,
        symbol="ES",
        open=4500.0,
        high=4510.0,
        low=4495.0,
        close=4505.0,
        volume=1000
    )
    
    logger.info("\n🧪 Test 1: Premier calcul")
    start = time.time()
    features1 = calculator.calculate_all_features(data1)
    time1 = (time.time() - start) * 1000
    logger.info("⏱️ Temps: {time1:.2f}ms")
    logger.info("📈 Nombre de features: {len(features1)}")
    
    # Afficher stats si disponibles
    if hasattr(calculator, 'get_cache_stats'):
        stats = calculator.get_cache_stats()
        logger.info("📊 Stats après calcul 1: {stats}")
    
    logger.info("\n🧪 Test 2: Même données (devrait être un cache hit)")
    start = time.time()
    features2 = calculator.calculate_all_features(data2)
    time2 = (time.time() - start) * 1000
    logger.info("⏱️ Temps: {time2:.2f}ms")
    
    # Comparer les résultats
    logger.info("\n🔍 Comparaison:")
    logger.info("  - Même timestamp: {data1.timestamp == data2.timestamp}")
    logger.info("  - Même hash data1: {hash((data1.timestamp, data1.open, data1.high, data1.low, data1.close, data1.volume))}")
    logger.info("  - Même hash data2: {hash((data2.timestamp, data2.open, data2.high, data2.low, data2.close, data2.volume))}")
    
    # Comparer features
    same_keys = set(features1.keys()) == set(features2.keys())
    logger.info("  - Mêmes clés: {same_keys}")
    
    if same_keys:
        differences = []
        for key in features1:
            if features1[key] != features2[key]:
                differences.append(f"{key}: {features1[key]} vs {features2[key]}")
        
        if differences:
            logger.info("  - Différences trouvées ({len(differences)}):")
            for diff in differences[:5]:  # Montrer max 5 différences
                logger.info("    {diff}")
        else:
            logger.info("  - ✅ Toutes les valeurs sont identiques")
    
    # Stats finales
    if hasattr(calculator, 'get_cache_stats'):
        stats = calculator.get_cache_stats()
        logger.info("\n📊 STATS FINALES:")
        logger.info("  Hit rate: {stats.get('hit_rate', 0):.1%}")
        logger.info("  Hits: {stats.get('cache_hits', 0)}")
        logger.info("  Misses: {stats.get('cache_misses', 0)}")
    
    # Test 3: Vérifier si c'est un problème de hash
    logger.info("\n🔍 Test 3: Vérification du mécanisme de cache")
    
    # Essayer d'appeler directement une méthode cachée si elle existe
    if hasattr(calculator, '_calculate_momentum_features_cached'):
        logger.info("Méthode cachée trouvée: _calculate_momentum_features_cached")
        
        # Vérifier le cache info
        if hasattr(calculator._calculate_momentum_features_cached, 'cache_info'):
            info = calculator._calculate_momentum_features_cached.cache_info()
            logger.info("📊 Cache info momentum: {info}")
    
    if hasattr(calculator, '_calculate_vwap_features_cached'):
        logger.info("Méthode cachée trouvée: _calculate_vwap_features_cached")
        
        # Vérifier le cache info
        if hasattr(calculator._calculate_vwap_features_cached, 'cache_info'):
            info = calculator._calculate_vwap_features_cached.cache_info()
            logger.info("📊 Cache info VWAP: {info}")
    
    # Test 4: Appel multiple fois la même méthode
    logger.info("\n🔄 Test 4: Appels multiples")
    for i in range(5):
        start = time.time()
        _ = calculator.calculate_all_features(data1)
        elapsed = (time.time() - start) * 1000
        logger.info("  Appel {i+1}: {elapsed:.2f}ms")
    
    if hasattr(calculator, 'get_cache_stats'):
        stats = calculator.get_cache_stats()
        logger.info("\n📊 Stats après appels multiples:")
        logger.info("  Total calculations: {stats.get('total_calculations', 0)}")
        logger.info("  Hit rate: {stats.get('hit_rate', 0):.1%}")

if __name__ == "__main__":
    test_basic_cache()