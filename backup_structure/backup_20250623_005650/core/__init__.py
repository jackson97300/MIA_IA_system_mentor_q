"""
MIA_IA_SYSTEM - Core Package
Exports corrigés selon classes RÉELLEMENT définies
ROBUSTESSE COMPLÈTE PRÉSERVÉE - Méthode signature intacte
Version: Corrected Imports - No functionality loss
"""

# Import base types first (no local dependencies)
from .base_types import (
    # Core data structures
    MarketData,
    OrderFlowData,
    TradingFeatures,
    TradingSignal,
    TradeResult,
    
    # Enums
    MarketRegime,
    SignalType,
    PatternType,
    SignalStrength,
    SessionPhase,
    
    # Constants
    ES_TICK_SIZE,
    ES_TICK_VALUE,
    MES_TICK_VALUE,
    TRADING_HOURS,
    DEFAULT_RISK_PARAMS,
    PERFORMANCE_TARGETS,
    
    # Utility functions
    get_session_phase,
    validate_market_data,
    calculate_performance_metrics
)

# Battle Navale - CLASSES RÉELLEMENT DÉFINIES dans battle_navale.py
from .battle_navale import (
    # === CLASSE PRINCIPALE ===
    BattleNavaleAnalyzer,        # ← CLASSE RÉELLE (pas BattleNavaleDetector)
    
    # === RÉSULTATS ET STRUCTURES ===
    BattleNavaleResult,          # ← DATACLASS COMPLÈTE
    Base,                        # ← DATACLASS BASES (pas BaseData/BaseType)
    SierraPattern,               # ← PATTERNS SIERRA CHART
    
    # === ENUMS RÉELS ===
    BattleStatus,                # ← ENUM BATAILLE
    BaseQuality,                 # ← ENUM QUALITÉ BASE
    TrendContinuation,           # ← ENUM CONTINUATION (pas GoldenRuleStatus)
    
    # === FACTORY FUNCTIONS ===
    create_battle_navale_analyzer,      # ← FACTORY RÉELLE
    analyze_battle_navale_patterns,     # ← HELPER FUNCTION
    
    # === TEST FUNCTION ===
    test_battle_navale_analyzer         # ← TEST COMPLET
)

# Version info
__version__ = "2.0.0"
__author__ = "MIA Trading System"

# Export control - TOUTES LES CLASSES RÉELLES
__all__ = [
    # === BASE TYPES ===
    'MarketData',
    'OrderFlowData', 
    'TradingFeatures',
    'TradingSignal',
    'TradeResult',
    
    # === ENUMS BASE ===
    'MarketRegime',
    'SignalType',
    'PatternType', 
    'SignalStrength',
    'SessionPhase',
    
    # === CONSTANTS ===
    'ES_TICK_SIZE',
    'ES_TICK_VALUE',
    'MES_TICK_VALUE',
    'TRADING_HOURS',
    'DEFAULT_RISK_PARAMS',
    'PERFORMANCE_TARGETS',
    
    # === UTILITIES ===
    'get_session_phase',
    'validate_market_data',
    'calculate_performance_metrics',
    
    # === BATTLE NAVALE - MÉTHODE SIGNATURE COMPLÈTE ===
    'BattleNavaleAnalyzer',              # CLASSE PRINCIPALE
    'BattleNavaleResult',                # RÉSULTATS COMPLETS
    'Base',                              # STRUCTURE BASES
    'SierraPattern',                     # PATTERNS SIERRA
    'BattleStatus',                      # ÉTAT BATAILLE
    'BaseQuality',                       # QUALITÉ BASES
    'TrendContinuation',                 # CONTINUATION TREND
    'create_battle_navale_analyzer',     # FACTORY
    'analyze_battle_navale_patterns',    # HELPER
    'test_battle_navale_analyzer',       # TEST
    
    # === ALIAS COMPATIBILITÉ ===
    'BattleNavaleDetector',              # Alias vers Analyzer
    'GoldenRuleStatus',                  # Alias vers TrendContinuation
    'BaseType',                          # Alias vers Base
    'BaseData',                          # Alias vers Base
    'create_battle_navale_detector',     # Alias factory
]

# === ALIAS POUR COMPATIBILITÉ ANCIENS IMPORTS ===
# Ces alias permettent aux anciens imports de continuer à marcher
BattleNavaleDetector = BattleNavaleAnalyzer              # Main alias
GoldenRuleStatus = TrendContinuation                     # Enum alias
BaseType = Base                                          # Structure alias
BaseData = Base                                          # Structure alias
create_battle_navale_detector = create_battle_navale_analyzer  # Factory alias