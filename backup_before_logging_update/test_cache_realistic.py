#!/usr/bin/env python3
"""
Test du cache avec des calculs plus réalistes
Simule des calculs plus coûteux pour mieux voir les bénéfices du cache
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List
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

def create_complex_market_data(seed: int = 42) -> List[MarketData]:
    """Crée une série de données de marché plus complexes"""
    np.random.seed(seed)
    
    base_price = 4500.0
    data_list = []
    
    # Créer 100 points de données
    for i in range(100):
        # Simuler mouvement de prix réaliste
        change = np.random.normal(0, 10)
        base_price += change
        
        high = base_price + abs(np.random.normal(0, 5))
        low = base_price - abs(np.random.normal(0, 5))
        
        data = MarketData(
            timestamp=pd.Timestamp.now() + pd.Timedelta(minutes=i),
            symbol="ES",
            open=base_price - np.random.uniform(-2, 2),
            high=high,
            low=low,
            close=base_price,
            volume=np.random.randint(1000, 5000),
            # Paramètres optionnels de base
            bid=base_price - 0.25,
            ask=base_price + 0.25
        )
        data_list.append(data)
    
    return data_list

def simulate_heavy_calculation(calculator, market_data: MarketData) -> Dict:
    """Simule un calcul plus lourd en appelant plusieurs fois les features"""
    # Appeler plusieurs fois pour simuler un calcul complexe
    features = calculator.calculate_all_features(market_data)
    
    # Simuler des calculs supplémentaires
    time.sleep(0.001)  # 1ms de calcul simulé
    
    return features

def main():
    logger.info("🧪 TEST CACHE AVEC CALCULS RÉALISTES")
    print("=" * 50)
    
    # Créer calculator avec cache
    calculator = create_feature_calculator(
        optimized=True,
        cache_config={
            'cache_ttl': 300,  # 5 minutes
            'cache_size': 1000  # 1000 entrées
        }
    )
    
    # Créer données de test
    logger.info("📊 Création de 100 points de données...")
    data_list = create_complex_market_data()
    
    # Test 1: Premier passage (tout en cache miss)
    logger.info("\n🔄 Test 1: Premier passage (cache miss)")
    start = time.time()
    results_first = []
    
    for i, data in enumerate(data_list[:20]):  # Tester avec 20 points
        result = simulate_heavy_calculation(calculator, data)
        results_first.append(result)
        
        if i % 5 == 0:
            logger.info("  Traité {i+1}/20 points...")
    
    time_first = time.time() - start
    logger.info("⏱️ Temps total: {time_first*1000:.2f}ms")
    logger.info("⏱️ Temps moyen par point: {(time_first/20)*1000:.2f}ms")
    
    # Afficher stats cache
    if hasattr(calculator, 'get_cache_stats'):
        stats = calculator.get_cache_stats()
        logger.info("\n📊 STATS CACHE APRÈS PREMIER PASSAGE:")
        logger.info("  Hit rate: {stats.get('hit_rate', 0):.1%}")
        logger.info("  Hits: {stats.get('cache_hits', 0)}")
        logger.info("  Misses: {stats.get('cache_misses', 0)}")
    
    # Test 2: Deuxième passage avec mêmes données (cache hits)
    logger.info("\n🚀 Test 2: Deuxième passage (cache hits)")
    start = time.time()
    results_second = []
    
    for i, data in enumerate(data_list[:20]):  # Mêmes 20 points
        result = simulate_heavy_calculation(calculator, data)
        results_second.append(result)
    
    time_second = time.time() - start
    logger.info("⏱️ Temps total: {time_second*1000:.2f}ms")
    logger.info("⏱️ Temps moyen par point: {(time_second/20)*1000:.2f}ms")
    logger.info("🚀 SPEEDUP: {time_first/time_second:.1f}x plus rapide!")
    
    # Vérifier que les résultats sont identiques
    all_identical = all(
        str(r1) == str(r2) 
        for r1, r2 in zip(results_first, results_second)
    )
    logger.info("Résultats identiques: {all_identical}")
    
    # Stats finales
    if hasattr(calculator, 'get_cache_stats'):
        stats = calculator.get_cache_stats()
        logger.info("\n📊 STATS CACHE FINALES:")
        logger.info("  Hit rate: {stats.get('hit_rate', 0):.1%}")
        logger.info("  Hits: {stats.get('cache_hits', 0)}")
        logger.info("  Misses: {stats.get('cache_misses', 0)}")
        logger.info("  Avg calc time: {stats.get('avg_calculation_time_ms', 0):.2f}ms")
    
    # Test 3: Pattern réaliste (mélange de hits et misses)
    logger.info("\n🎯 Test 3: Pattern réaliste (80% répétitions)")
    start = time.time()
    
    # Créer un pattern avec 80% de répétitions
    pattern_indices = []
    for i in range(50):
        if np.random.random() < 0.8:  # 80% de chance de répétition
            pattern_indices.append(np.random.randint(0, 10))
        else:
            pattern_indices.append(np.random.randint(10, 20))
    
    for idx in pattern_indices:
        _ = simulate_heavy_calculation(calculator, data_list[idx])
    
    time_pattern = time.time() - start
    logger.info("⏱️ Temps pour 50 calculs: {time_pattern*1000:.2f}ms")
    
    # Stats finales après pattern
    if hasattr(calculator, 'get_cache_stats'):
        stats = calculator.get_cache_stats()
        logger.info("\n📊 STATS APRÈS PATTERN RÉALISTE:")
        logger.info("  Hit rate: {stats.get('hit_rate', 0):.1%}")
        logger.info("  Total calculations: {stats.get('total_calculations', 0)}")
        
        # Calculer économie de temps estimée
        if stats.get('hit_rate', 0) > 0:
            time_saved = stats.get('cache_hits', 0) * stats.get('avg_calculation_time_ms', 0)
            logger.info("  ⏰ Temps économisé: ~{time_saved:.0f}ms")
    
    logger.info("\n✅ TEST RÉALISTE TERMINÉ!")
    
    # Test 4: Vider le cache
    logger.info("\n🧹 Test 4: Clear cache")
    if hasattr(calculator, 'clear_cache'):
        calculator.clear_cache()
        logger.info("Cache vidé")
        
        # Vérifier que le cache est vide
        if hasattr(calculator, 'get_cache_stats'):
            stats = calculator.get_cache_stats()
            logger.info("  Hits après clear: {stats.get('cache_hits', 0)}")
            logger.info("  Misses après clear: {stats.get('cache_misses', 0)}")

if __name__ == "__main__":
    main()