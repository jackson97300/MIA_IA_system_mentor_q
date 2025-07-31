#!/usr/bin/env python3
"""
Test import du FeatureCalculator optimisé
"""

import sys
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)

sys.path.append(str(Path(__file__).parent))

logger.info("🧪 TEST IMPORT FEATURE CALCULATOR OPTIMISÉ")
print("=" * 50)

try:
    # Test import de base
    from features.feature_calculator_optimized import (
        OptimizedFeatureCalculator,
        create_optimized_feature_calculator,
        timed_lru_cache,
        make_hashable,
        cache_key
    )
    logger.info("Import OptimizedFeatureCalculator réussi")
    
    # Test création instance
    calc = create_optimized_feature_calculator()
    logger.info("Instance créée: {type(calc).__name__}")
    
    # Vérifier méthodes
    methods = ['calculate_all_features', 'get_cache_stats', 'clear_cache']
    for method in methods:
        if hasattr(calc, method):
            logger.info("Méthode '{method}' disponible")
        else:
            logger.error("Méthode '{method}' manquante")
    
    logger.info("\n✅ IMPORT TEST RÉUSSI!")
    
except Exception as e:
    logger.info("\n❌ ERREUR IMPORT: {e}")
    import traceback
    traceback.print_exc()