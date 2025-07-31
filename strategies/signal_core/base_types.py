"""
strategies/signal_core/base_types.py

Types de base, enums et constantes pour Signal Generator
Extrait et nettoyé du fichier original signal_generator.py (lignes 1-300)
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd

# ===== IMPORTS CORE =====
from core.base_types import (
    MarketData, OrderFlowData, TradingSignal,
    SignalType, MarketRegime, ES_TICK_SIZE, ES_TICK_VALUE
)

# ===== CONSTANTES GLOBAUX =====

# PRIORITÉ #2: CONSTANTES SEUILS BATTLE NAVALE
MIN_BATTLE_NAVALE_SIGNAL_LONG = 0.25    # Nouveau seuil LONG
MIN_BATTLE_NAVALE_SIGNAL_SHORT = -0.25  # Nouveau seuil SHORT

# Seuils confluence ajustés pour cohérence
MIN_CONFLUENCE_SCORE = 0.60          # Maintenu
MIN_CONFLUENCE_PREMIUM = 0.80        # Pour signaux premium
MIN_CONFLUENCE_STRONG = 0.70         # Pour signaux strong

# 🆕 PHASE 3: SEUILS MTF ELITE
MIN_MTF_ELITE_SCORE = 0.75           # Score MTF pour signaux Elite
MIN_MTF_STANDARD_SCORE = 0.35        # Score MTF pour signaux Standard

# 🎯 TECHNIQUE #2: SEUILS SMART MONEY
MIN_SMART_MONEY_CONFIDENCE = 0.6     # Confidence minimum Smart Money
MIN_SMART_MONEY_INSTITUTIONAL_SCORE = 0.7  # Score minimum flux institutionnel
SMART_MONEY_ALIGNMENT_BONUS = 1.15   # Bonus confluence si Smart Money align

# 🎯 TECHNIQUE #3: SEUILS ML ENSEMBLE
MIN_ML_ENSEMBLE_CONFIDENCE = 0.70       # Confidence minimum ML pour validation signal
ML_ENSEMBLE_BOOST_FACTOR = 1.08         # Boost confidence si ML très confiant (>85%)
ML_ENSEMBLE_POSITION_BONUS = 1.15       # Bonus position size si ML valide

# 🎯 TECHNIQUE #4: SEUILS GAMMA CYCLES
GAMMA_EXPIRY_WEEK_FACTOR = 0.7       # Réduction semaine expiration
GAMMA_PEAK_FACTOR = 1.3              # Boost gamma peak (3-5j avant)
GAMMA_MODERATE_FACTOR = 1.1          # Boost modéré (6-10j avant)
GAMMA_NORMAL_FACTOR = 1.0            # Phase normale
GAMMA_POST_EXPIRY_FACTOR = 1.05      # Léger boost post-expiration

# ===== ENUMS =====

class SignalDecision(Enum):
    """Décisions finales possibles"""
    EXECUTE_LONG = "execute_long"
    EXECUTE_SHORT = "execute_short"
    EXIT_POSITION = "exit_position"
    WAIT_BETTER_SETUP = "wait_better_setup"
    NO_TRADE = "no_trade"


class SignalSource(Enum):
    """Source du signal"""
    BATTLE_NAVALE = "battle_navale"
    TREND_STRATEGY = "trend_strategy"
    RANGE_STRATEGY = "range_strategy"
    ML_PREDICTION = "ml_prediction"
    MANUAL_OVERRIDE = "manual_override"
    # 🆕 PHASE 3: Nouvelle source
    MTF_ELITE_CONFLUENCE = "mtf_elite_confluence"
    # 🎯 TECHNIQUE #2: Nouvelle source
    SMART_MONEY_INSTITUTIONAL = "smart_money_institutional"
    # 🎯 TECHNIQUE #3: Nouvelle source
    ML_ENSEMBLE_VALIDATED = "ml_ensemble_validated"
    # 🎯 TECHNIQUE #4: Nouvelle source
    GAMMA_CYCLE_OPTIMIZED = "gamma_cycle_optimized"


class QualityLevel(Enum):
    """Niveau de qualité du signal"""
    PREMIUM = "premium"      # >85% confluence
    STRONG = "strong"        # 75-85%
    MODERATE = "moderate"    # 65-75%
    WEAK = "weak"           # 55-65%
    REJECTED = "rejected"    # <55%
    # 🆕 PHASE 3: Nouveau niveau
    ELITE = "elite"         # >90% MTF confluence
    # 🎯 TECHNIQUE #2: Nouveau niveau
    INSTITUTIONAL = "institutional"  # Smart Money détecté
    # 🎯 TECHNIQUE #3: Nouveau niveau
    ML_VALIDATED = "ml_validated"        # Signal validé par ML Ensemble
    # 🎯 TECHNIQUE #4: Nouveau niveau
    GAMMA_OPTIMIZED = "gamma_optimized"    # Signal optimisé gamma cycles
    ULTIMATE_ELITE = "ultimate_elite"      # Signal 5/5 techniques Elite

# ===== IMPORTS OPTIONNELS TECHNIQUES AVANCÉES =====

# 🎯 TECHNIQUE #3: Import ML Ensemble Filter
try:
    from ml.ensemble_filter import (
        ml_ensemble_filter,
        MLEnsembleFilter,
        EnsembleConfig,
        EnsemblePrediction
    )
    ML_ENSEMBLE_AVAILABLE = True
except ImportError:
    ML_ENSEMBLE_AVAILABLE = False
    # Création de classes mock pour éviter les erreurs
    class EnsembleConfig:
        def __init__(self, confidence_threshold=0.7, cache_enabled=True):
            self.confidence_threshold = confidence_threshold
            self.cache_enabled = cache_enabled
    
    class EnsemblePrediction:
        def __init__(self):
            self.confidence = 0.0
            self.signal_approved = False
            self.models_used = []
            self.processing_time_ms = 0.0
    
    class MLEnsembleFilter:
        def __init__(self, config=None):
            pass
        def is_ready(self):
            return False
        def predict_signal_quality(self, features):
            return EnsemblePrediction()

# 🎯 TECHNIQUE #4: Import Gamma Cycles
try:
    from ml.gamma_cycles import (
        gamma_expiration_factor,
        GammaCyclesAnalyzer,
        GammaCycleConfig,
        GammaCycleAnalysis,
        GammaPhase
    )
    GAMMA_CYCLES_AVAILABLE = True
except ImportError:
    GAMMA_CYCLES_AVAILABLE = False
    # Création de classes mock
    from enum import Enum as BaseEnum
    
    class GammaPhase(BaseEnum):
        GAMMA_PEAK = "gamma_peak"
        GAMMA_MODERATE = "gamma_moderate"
        EXPIRY_WEEK = "expiry_week"
        NORMAL = "normal"
        POST_EXPIRY = "post_expiry"
    
    class GammaCycleAnalysis:
        def __init__(self):
            self.gamma_phase = GammaPhase.NORMAL
            self.adjustment_factor = 1.0
            self.confidence_adjustment = 1.0
            self.position_size_adjustment = 1.0
            self.days_to_expiry = 15
            self.volatility_expectation = "normal"
            self.reasoning = "Mock analysis"
    
    class GammaCycleConfig:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class GammaCyclesAnalyzer:
        def __init__(self, config):
            self.config = config
        def analyze_gamma_cycle(self, timestamp=None):
            return GammaCycleAnalysis()
        def get_statistics(self):
            return {"cache_hit_rate": 0.0}

# ===== HELPER FUNCTIONS =====

def get_availability_status() -> Dict[str, bool]:
    """Retourne le statut de disponibilité des techniques avancées"""
    return {
        "ml_ensemble": ML_ENSEMBLE_AVAILABLE,
        "gamma_cycles": GAMMA_CYCLES_AVAILABLE
    }

def get_all_constants() -> Dict[str, float]:
    """Retourne toutes les constantes du système"""
    return {
        "MIN_BATTLE_NAVALE_SIGNAL_LONG": MIN_BATTLE_NAVALE_SIGNAL_LONG,
        "MIN_BATTLE_NAVALE_SIGNAL_SHORT": MIN_BATTLE_NAVALE_SIGNAL_SHORT,
        "MIN_CONFLUENCE_SCORE": MIN_CONFLUENCE_SCORE,
        "MIN_MTF_ELITE_SCORE": MIN_MTF_ELITE_SCORE,
        "MIN_SMART_MONEY_CONFIDENCE": MIN_SMART_MONEY_CONFIDENCE,
        "MIN_ML_ENSEMBLE_CONFIDENCE": MIN_ML_ENSEMBLE_CONFIDENCE,
        "GAMMA_PEAK_FACTOR": GAMMA_PEAK_FACTOR
    }

# ===== EXPORTS =====
__all__ = [
    # Enums
    'SignalDecision',
    'SignalSource', 
    'QualityLevel',
    
    # Constantes Battle Navale
    'MIN_BATTLE_NAVALE_SIGNAL_LONG',
    'MIN_BATTLE_NAVALE_SIGNAL_SHORT',
    
    # Constantes Confluence
    'MIN_CONFLUENCE_SCORE',
    'MIN_CONFLUENCE_PREMIUM', 
    'MIN_CONFLUENCE_STRONG',
    
    # Constantes MTF Elite
    'MIN_MTF_ELITE_SCORE',
    'MIN_MTF_STANDARD_SCORE',
    
    # Constantes Smart Money
    'MIN_SMART_MONEY_CONFIDENCE',
    'MIN_SMART_MONEY_INSTITUTIONAL_SCORE',
    'SMART_MONEY_ALIGNMENT_BONUS',
    
    # Constantes ML Ensemble
    'MIN_ML_ENSEMBLE_CONFIDENCE',
    'ML_ENSEMBLE_BOOST_FACTOR',
    'ML_ENSEMBLE_POSITION_BONUS',
    
    # Constantes Gamma Cycles
    'GAMMA_EXPIRY_WEEK_FACTOR',
    'GAMMA_PEAK_FACTOR',
    'GAMMA_MODERATE_FACTOR',
    'GAMMA_NORMAL_FACTOR',
    'GAMMA_POST_EXPIRY_FACTOR',
    
    # Classes techniques avancées (mock si non disponibles)
    'MLEnsembleFilter',
    'EnsembleConfig',
    'EnsemblePrediction',
    'GammaCyclesAnalyzer',
    'GammaCycleConfig',
    'GammaCycleAnalysis',
    'GammaPhase',
    
    # Flags disponibilité
    'ML_ENSEMBLE_AVAILABLE',
    'GAMMA_CYCLES_AVAILABLE',
    
    # Helper functions
    'get_availability_status',
    'get_all_constants'
]