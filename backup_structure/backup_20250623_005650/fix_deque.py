#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Fix Deque Error
Correction de l'erreur: name 'deque' is not defined
"""

import os
import shutil
from pathlib import Path

def check_strategy_selector_imports():
    """Vérifie les imports dans strategy_selector.py"""
    
    logger.debug("CHECKING strategy_selector.py imports")
    print("="*45)
    
    selector_path = Path("strategies/strategy_selector.py")
    
    if not selector_path.exists():
        logger.error("strategies/strategy_selector.py n'existe pas!")
        logger.info("💡 Créons un fichier strategy_selector.py minimal...")
        return create_minimal_strategy_selector()
    
    # Lire le contenu
    with open(selector_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier l'import deque
    if 'from collections import deque' in content:
        logger.info("Import deque trouvé dans strategy_selector.py")
        return True
    elif 'import deque' in content:
        logger.info("Import deque trouvé (style différent)")
        return True
    else:
        logger.error("Import deque MANQUANT dans strategy_selector.py")
        return fix_deque_import(selector_path, content)

def fix_deque_import(file_path, content):
    """Corrige l'import deque manquant"""
    
    logger.info("🔧 Correction import deque...")
    
    # Backup
    backup_path = Path(str(file_path) + ".backup")
    shutil.copy2(file_path, backup_path)
    
    # Chercher où ajouter l'import
    lines = content.split('\n')
    
    # Trouver la ligne d'import collections ou la zone d'imports
    import_line_idx = -1
    for i, line in enumerate(lines):
        if 'from collections import' in line and 'deque' not in line:
            # Ajouter deque à l'import existant
            lines[i] = line.replace('from collections import', 'from collections import deque,')
            import_line_idx = i
            break
        elif line.strip().startswith('import') and 'logging' in line:
            # Ajouter après les imports
            import_line_idx = i
    
    # Si pas trouvé, ajouter au début des imports
    if import_line_idx == -1:
        for i, line in enumerate(lines):
            if line.strip().startswith('import') or line.strip().startswith('from'):
                lines.insert(i, 'from collections import deque')
                import_line_idx = i
                break
    
    # Si toujours pas trouvé, ajouter après les commentaires
    if import_line_idx == -1:
        for i, line in enumerate(lines):
            if not line.strip().startswith('"""') and not line.strip().startswith('#') and line.strip():
                lines.insert(i, 'from collections import deque')
                break
    
    # Écrire le fichier corrigé
    corrected_content = '\n'.join(lines)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(corrected_content)
    
    logger.info("Import deque ajouté dans {file_path}")
    return True

def create_minimal_strategy_selector():
    """Crée un strategy_selector.py minimal si il n'existe pas"""
    
    logger.info("🔧 CREATING minimal strategy_selector.py")
    
    selector_path = Path("strategies/strategy_selector.py")
    
    minimal_content = '''"""
MIA_IA_SYSTEM - Strategy Selector
Version minimale pour résoudre imports
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import deque  # ← IMPORT CRITIQUE

# Local imports
from core.base_types import (
    MarketData, OrderFlowData, TradingSignal, SignalType,
    ES_TICK_SIZE, ES_TICK_VALUE
)

logger = logging.getLogger(__name__)

# === ENUMS ===

class StrategyType(Enum):
    """Types de stratégies disponibles"""
    TREND_STRATEGY = "trend_strategy"
    RANGE_STRATEGY = "range_strategy"
    WAIT_STRATEGY = "wait_strategy"
    TRANSITION_STRATEGY = "transition_strategy"

class SignalDecision(Enum):
    """Décisions finales de signal"""
    EXECUTE_SIGNAL = "execute_signal"
    REJECT_SIGNAL = "reject_signal"
    WAIT_BETTER_SETUP = "wait_better_setup"
    REGIME_UNCLEAR = "regime_unclear"

class ExecutionMode(Enum):
    """Modes d'exécution"""
    PAPER_TRADING = "paper_trading"
    LIVE_TRADING = "live_trading"
    SIMULATION = "simulation"
    ANALYSIS_ONLY = "analysis_only"

# === DATACLASSES ===

@dataclass
class StrategySelectionResult:
    """Résultat sélection stratégie"""
    timestamp: pd.Timestamp
    selected_strategy: StrategyType
    selection_reason: str = "minimal_version"
    selection_confidence: float = 0.5
    market_regime: str = "unknown"
    regime_confidence: float = 0.5
    bias_strength: float = 0.5
    allowed_directions: List[str] = field(default_factory=list)
    signal_generated: bool = False
    signal_data: Optional[Any] = None
    final_decision: SignalDecision = SignalDecision.WAIT_BETTER_SETUP
    confluence_score: float = 0.0
    features_quality: float = 0.0
    total_processing_time_ms: float = 0.0

@dataclass
class TradingContext:
    """Contexte trading complet"""
    timestamp: pd.Timestamp
    market_data: MarketData
    es_nq_data: Optional[Dict[str, float]] = None
    structure_data: Optional[Dict[str, Any]] = None
    volume_data: Optional[Dict[str, float]] = None
    sierra_patterns: Optional[Dict[str, float]] = None
    session_phase: str = "unknown"
    execution_mode: ExecutionMode = ExecutionMode.PAPER_TRADING
    max_position_size: float = 1.0
    max_risk_per_trade: float = 15.0
    account_size: float = 100000.0

@dataclass
class SystemPerformance:
    """Performance système complète"""
    total_analyses: int = 0
    trend_signals: int = 0
    range_signals: int = 0
    rejected_signals: int = 0
    trend_strategy_usage: int = 0
    range_strategy_usage: int = 0
    wait_periods: int = 0
    avg_confluence_score: float = 0.0
    avg_processing_time: float = 0.0
    regime_detection_accuracy: float = 0.0
    successful_regime_transitions: int = 0
    failed_signal_validations: int = 0

# === MAIN STRATEGY SELECTOR ===

class StrategySelector:
    """Strategy Selector minimal pour résoudre imports"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation minimale"""
        self.config = config or {}
        self.regime_history: deque = deque(maxlen=100)  # ← UTILISE DEQUE
        self.signal_history: deque = deque(maxlen=200)
        self.performance = SystemPerformance()
        logger.info("StrategySelector initialisé (version minimale)")
    
    def analyze_and_select(self, trading_context: TradingContext) -> StrategySelectionResult:
        """Analyse minimale"""
        return StrategySelectionResult(
            timestamp=trading_context.timestamp,
            selected_strategy=StrategyType.WAIT_STRATEGY,
            selection_reason="Version minimale - en attente",
            market_regime="unknown"
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Status minimal"""
        return {
            'status': 'minimal_version',
            'total_analyses': self.performance.total_analyses
        }

# === FACTORY FUNCTIONS ===

def create_strategy_selector(config: Optional[Dict[str, Any]] = None) -> StrategySelector:
    """Factory function pour strategy selector"""
    return StrategySelector(config)

def execute_full_analysis(trading_context: TradingContext,
                         selector: Optional[StrategySelector] = None) -> StrategySelectionResult:
    """Helper function pour analyse complète"""
    if selector is None:
        selector = create_strategy_selector()
    return selector.analyze_and_select(trading_context)
'''
    
    with open(selector_path, 'w', encoding='utf-8') as f:
        f.write(minimal_content)
    
    logger.info("Fichier strategy_selector.py créé: {selector_path}")
    return True

def test_imports_after_fix():
    """Test final des imports"""
    
    logger.info("\n🔍 TEST FINAL DES IMPORTS")
    print("="*40)
    
    try:
        # Nettoyer cache
        import sys
        modules_to_clean = [k for k in sys.modules.keys() if k.startswith('strategies')]
        for mod in modules_to_clean:
            del sys.modules[mod]
        
        # Test imports critiques
        from strategies import create_trend_strategy, create_range_strategy
        logger.info("Factory functions importées")
        
        # Test instantiation (là où l'erreur deque se produit)
        trend_strategy = create_trend_strategy()
        logger.info("create_trend_strategy() fonctionne")
        
        range_strategy = create_range_strategy()
        logger.info("create_range_strategy() fonctionne")
        
        return True
        
    except Exception as e:
        logger.error("Erreur persistante: {e}")
        return False

def main():
    """Correction principale"""
    
    logger.info("🎯 FIX: name 'deque' is not defined")
    print("="*50)
    
    # 1. Vérifier strategy_selector.py
    success = check_strategy_selector_imports()
    
    if success:
        logger.info("\n🔧 Import deque corrigé")
        
        # 2. Test final
        if test_imports_after_fix():
            logger.info("\n🎉 PROBLÈME DEQUE RÉSOLU!")
            logger.info("Tous les imports fonctionnent maintenant")
            logger.info("Relancez: python test_phase2_integration.py")
        else:
            logger.info("\n⚠️ Problèmes persistants")
            logger.info("💡 Il peut y avoir d'autres imports manquants")
    else:
        logger.info("\n❌ Impossible de corriger automatiquement")
        logger.info("💡 Vérification manuelle nécessaire")

if __name__ == "__main__":
    main()