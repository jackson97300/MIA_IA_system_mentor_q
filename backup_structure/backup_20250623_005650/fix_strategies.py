#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Quick Fix Script CORRIGÉ
Correction immédiate de l'erreur import strategies
Version: Sans erreur de syntaxe
"""

import os
import shutil
from pathlib import Path

def quick_fix_strategies_init():
    """Correction rapide du fichier strategies/__init__.py"""
    
    logger.info("🚀 QUICK FIX: strategies/__init__.py")
    print("="*50)
    
    init_path = Path("strategies/__init__.py")
    
    if not init_path.exists():
        logger.error("Fichier strategies/__init__.py non trouvé!")
        return False
    
    # Backup
    backup_path = Path("strategies/__init__.py.backup")
    shutil.copy2(init_path, backup_path)
    logger.info("Backup créé: {backup_path}")
    
    # Nouveau contenu corrigé
    new_content = '''"""
MIA_IA_SYSTEM - Strategies Package
Orchestration complète des stratégies trading - IMPORTS FIXES
Version: Production Ready
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

# Local imports  
from core.base_types import (
    MarketData, OrderFlowData, TradingSignal, SignalType,
    ES_TICK_SIZE
)
from features.feature_calculator import (
    FeatureCalculationResult, FeatureCalculator, SignalQuality
)

# Strategy imports with factory functions - FIX PRINCIPAL
from .trend_strategy import (
    TrendStrategy, TrendSignalData, TrendSignalType, 
    create_trend_strategy, analyze_trend_opportunity
)
from .range_strategy import (
    RangeStrategy, RangeSignalData, RangeSignalType, 
    create_range_strategy, analyze_range_opportunity
)
from .strategy_selector import (
    StrategySelector, StrategySelectionResult, TradingContext, SystemPerformance,
    StrategyType, SignalDecision, ExecutionMode, 
    create_strategy_selector, execute_full_analysis
)

# Market regime
from features.market_regime import (
    MarketRegimeDetector, MarketRegimeData, MarketRegime as RegimeType,
    analyze_market_regime
)

logger = logging.getLogger(__name__)

# === FACTORY FUNCTIONS ===

def create_strategy_orchestrator(config: Optional[Dict[str, Any]] = None):
    """Factory function orchestrateur"""
    return create_strategy_selector(config)

def create_signal_aggregator(config: Optional[Dict[str, Any]] = None):
    """Factory function aggregator"""
    return create_strategy_selector(config)

def analyze_complete_trading_opportunity(
    market_data: MarketData,
    order_flow: Optional[OrderFlowData] = None,
    options_data: Optional[Dict[str, Any]] = None,
    structure_data: Optional[Dict[str, Any]] = None,
    es_nq_data: Optional[Dict[str, float]] = None,
    sierra_patterns: Optional[Dict[str, float]] = None,
    orchestrator = None
) -> Optional[Any]:
    """FONCTION PRINCIPALE - ANALYSE COMPLÈTE"""
    
    if orchestrator is None:
        orchestrator = create_strategy_selector()
    
    trading_context = TradingContext(
        timestamp=market_data.timestamp,
        market_data=market_data,
        es_nq_data=es_nq_data,
        structure_data=structure_data,
        sierra_patterns=sierra_patterns,
        execution_mode=ExecutionMode.PAPER_TRADING
    )
    
    return orchestrator.analyze_and_select(trading_context)

# Package exports - AVEC FACTORY FUNCTIONS CRITIQUES
__all__ = [
    # Core strategy classes
    'TrendStrategy',
    'RangeStrategy', 
    'StrategySelector',
    
    # Data classes
    'TrendSignalData',
    'RangeSignalData', 
    'StrategySelectionResult',
    'TradingContext',
    'SystemPerformance',
    
    # Enums
    'TrendSignalType',
    'RangeSignalType',
    'StrategyType',
    'SignalDecision',
    'ExecutionMode',
    
    # Factory functions - LES MANQUANTES ✅
    'create_trend_strategy',        # ✅ CRITICAL FIX
    'create_range_strategy',        # ✅ CRITICAL FIX  
    'create_strategy_selector',     # ✅ CRITICAL FIX
    'create_strategy_orchestrator',
    'create_signal_aggregator',
    
    # Analysis functions
    'analyze_trend_opportunity',
    'analyze_range_opportunity',
    'analyze_market_regime',
    'analyze_complete_trading_opportunity',
    'execute_full_analysis',
    
    # Market regime
    'MarketRegimeDetector',
    'MarketRegimeData',
]
'''
    
    # Écrire le nouveau contenu
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    logger.info("Fichier strategies/__init__.py mis à jour")
    return True

def test_imports():
    """Test simple des imports critiques"""
    logger.info("\n🔍 TEST DES IMPORTS CRITIQUES")
    print("-" * 40)
    
    try:
        # Test 1: Import du package
        import strategies
        logger.info("Package 'strategies' importé")
        
        # Test 2: Import des factory functions
        from strategies import create_trend_strategy
        logger.info("create_trend_strategy importée")
        
        from strategies import create_range_strategy  
        logger.info("create_range_strategy importée")
        
        from strategies import create_strategy_selector
        logger.info("create_strategy_selector importée")
        
        # Test 3: Test instantiation
        trend_strategy = create_trend_strategy()
        logger.info("create_trend_strategy() fonctionne")
        
        return True
        
    except ImportError as e:
        logger.error("Erreur import: {e}")
        return False
    except Exception as e:
        logger.error("Erreur: {e}")
        return False

if __name__ == "__main__":
    logger.info("🎯 QUICK FIX pour l'erreur: cannot import name 'create_trend_strategy'")
    print()
    
    # Appliquer la correction
    success = quick_fix_strategies_init()
    
    if success:
        logger.info("\n🎉 CORRECTION APPLIQUÉE!")
        
        # Nettoyer le cache des modules
        import sys
        modules_to_remove = [k for k in sys.modules.keys() if k.startswith('strategies')]
        for mod in modules_to_remove:
            del sys.modules[mod]
        logger.info("🧹 Cache modules nettoyé")
        
        # Tester les imports
        if test_imports():
            logger.info("\n🎉 SUCCÈS COMPLET!")
            logger.info("Relancez maintenant: python test_phase2_integration.py")
        else:
            logger.info("\n⚠️ Correction appliquée mais imports encore problématiques")
            logger.info("💡 Vérifiez manuellement strategies/__init__.py")
    else:
        logger.info("\n❌ ÉCHEC DE LA CORRECTION")
        logger.info("💡 Correction manuelle nécessaire")