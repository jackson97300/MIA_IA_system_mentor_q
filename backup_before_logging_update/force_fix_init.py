#!/usr/bin/env python3
"""
Script pour remplacer complètement les fichiers __init__.py problématiques
"""

import os
from pathlib import Path
import shutil

def replace_init_files():
    """Remplace tous les fichiers __init__.py par des versions propres"""
    
    project_root = Path("D:/MIA_IA_system")
    
    # Contenu propre pour chaque __init__.py
    init_contents = {
        "config/__init__.py": '''"""
Configuration module pour MIA_IA_SYSTEM
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Import configuration classes
try:
    from .trading_config import TradingConfig, get_trading_config
except ImportError:
    logger.warning("Could not import trading_config")
    TradingConfig = None
    get_trading_config = None

try:
    from .automation_config import AutomationConfig, get_automation_config
except ImportError:
    logger.warning("Could not import automation_config")
    AutomationConfig = None
    get_automation_config = None

try:
    from .ml_config import MLConfig, get_ml_config
except ImportError:
    logger.warning("Could not import ml_config")
    MLConfig = None
    get_ml_config = None

try:
    from .sierra_config import SierraIBKRConfig, get_sierra_config
except ImportError:
    logger.warning("Could not import sierra_config")
    SierraIBKRConfig = None
    get_sierra_config = None

# Export only what was successfully imported
__all__ = []

if TradingConfig:
    __all__.extend(['TradingConfig', 'get_trading_config'])
if AutomationConfig:
    __all__.extend(['AutomationConfig', 'get_automation_config'])
if MLConfig:
    __all__.extend(['MLConfig', 'get_ml_config'])
if SierraConfig:
    __all__.extend(['SierraConfig', 'get_sierra_config'])
''',

        "core/__init__.py": '''"""
Core module pour MIA_IA_SYSTEM
"""

import logging

logger = logging.getLogger(__name__)

# Import base types
try:
    from .base_types import (
        MarketData, TradingSignal, SignalType, MarketRegime,
        ES_TICK_SIZE, ES_TICK_VALUE, OrderFlowData,
        get_session_phase, validate_market_data
    )
    base_imports = True
except ImportError as e:
    logger.warning(f"Could not import base_types: {e}")
    base_imports = False

# Import detectors
try:
    from .battle_navale import BattleNavaleDetector, create_battle_navale_detector
    battle_imports = True
except ImportError as e:
    logger.warning(f"Could not import battle_navale: {e}")
    battle_imports = False

try:
    from .patterns_detector import PatternsDetector, create_patterns_detector
    patterns_imports = True
except ImportError as e:
    logger.warning(f"Could not import patterns_detector: {e}")
    patterns_imports = False

# Import connectors
try:
    from .ibkr_connector import IBKRConnector
    ibkr_imports = True
except ImportError as e:
    logger.warning(f"Could not import ibkr_connector: {e}")
    ibkr_imports = False

try:
    from .sierra_connector import SierraConnector
    sierra_imports = True
except ImportError as e:
    logger.warning(f"Could not import sierra_connector: {e}")
    sierra_imports = False

try:
    from .structure_data import StructureData, create_structure_data
    structure_imports = True
except ImportError as e:
    logger.warning(f"Could not import structure_data: {e}")
    structure_imports = False

# Build __all__ based on successful imports
__all__ = []

if base_imports:
    __all__.extend([
        'MarketData', 'TradingSignal', 'SignalType', 'MarketRegime',
        'ES_TICK_SIZE', 'ES_TICK_VALUE', 'OrderFlowData',
        'get_session_phase', 'validate_market_data'
    ])

if battle_imports:
    __all__.extend(['BattleNavaleDetector', 'create_battle_navale_detector'])

if patterns_imports:
    __all__.extend(['PatternsDetector', 'create_patterns_detector'])

if ibkr_imports:
    __all__.append('IBKRConnector')

if sierra_imports:
    __all__.append('SierraConnector')

if structure_imports:
    __all__.extend(['StructureData', 'create_structure_data'])
''',

        "features/__init__.py": '''"""
Features module pour MIA_IA_SYSTEM
"""

import logging

logger = logging.getLogger(__name__)

# Safe imports with error handling
__all__ = []

try:
    from .feature_calculator import FeatureCalculator, create_feature_calculator
    __all__.extend(['FeatureCalculator', 'create_feature_calculator'])
except ImportError as e:
    logger.warning(f"Could not import feature_calculator: {e}")

try:
    from .market_regime import MarketRegimeDetector, create_market_regime_detector
    __all__.extend(['MarketRegimeDetector', 'create_market_regime_detector'])
except ImportError as e:
    logger.warning(f"Could not import market_regime: {e}")

try:
    from .confluence_analyzer import ConfluenceAnalyzer, create_confluence_analyzer
    __all__.extend(['ConfluenceAnalyzer', 'create_confluence_analyzer'])
except ImportError as e:
    logger.warning(f"Could not import confluence_analyzer: {e}")
''',

        "strategies/__init__.py": '''"""
Strategies module pour MIA_IA_SYSTEM
"""

import logging

logger = logging.getLogger(__name__)

# Safe imports
__all__ = []

try:
    from .signal_generator import SignalGenerator, create_signal_generator
    __all__.extend(['SignalGenerator', 'create_signal_generator'])
except ImportError as e:
    logger.warning(f"Could not import signal_generator: {e}")

try:
    from .trend_strategy import TrendStrategy, create_trend_strategy
    __all__.extend(['TrendStrategy', 'create_trend_strategy'])
except ImportError as e:
    logger.warning(f"Could not import trend_strategy: {e}")

try:
    from .range_strategy import RangeStrategy, create_range_strategy
    __all__.extend(['RangeStrategy', 'create_range_strategy'])
except ImportError as e:
    logger.warning(f"Could not import range_strategy: {e}")

try:
    from .strategy_selector import StrategySelector, create_strategy_selector
    __all__.extend(['StrategySelector', 'create_strategy_selector'])
except ImportError as e:
    logger.warning(f"Could not import strategy_selector: {e}")
''',

        "execution/__init__.py": '''"""
Execution module pour MIA_IA_SYSTEM
"""

import logging

logger = logging.getLogger(__name__)

# Safe imports
__all__ = []

try:
    from .order_manager import OrderManager, create_order_manager
    __all__.extend(['OrderManager', 'create_order_manager'])
except ImportError as e:
    logger.warning(f"Could not import order_manager: {e}")

try:
    from .risk_manager import RiskManager, create_risk_manager
    __all__.extend(['RiskManager', 'create_risk_manager'])
except ImportError as e:
    logger.warning(f"Could not import risk_manager: {e}")

try:
    from .simple_trader import SimpleBattleNavaleTrader, create_simple_trader
    __all__.extend(['SimpleBattleNavaleTrader', 'create_simple_trader'])
except ImportError as e:
    logger.warning(f"Could not import simple_trader: {e}")

try:
    from .trade_snapshotter import TradeSnapshotter, create_trade_snapshotter
    __all__.extend(['TradeSnapshotter', 'create_trade_snapshotter'])
except ImportError as e:
    logger.warning(f"Could not import trade_snapshotter: {e}")
''',

        "monitoring/__init__.py": '''"""
Monitoring module pour MIA_IA_SYSTEM
"""

import logging

logger = logging.getLogger(__name__)

# Safe imports
__all__ = []

try:
    from .live_monitor import LiveMonitor, create_live_monitor
    __all__.extend(['LiveMonitor', 'create_live_monitor'])
except ImportError as e:
    logger.warning(f"Could not import live_monitor: {e}")

try:
    from .performance_tracker import PerformanceTracker, create_performance_tracker
    __all__.extend(['PerformanceTracker', 'create_performance_tracker'])
except ImportError as e:
    logger.warning(f"Could not import performance_tracker: {e}")

try:
    from .alert_system import AlertSystem, create_alert_system
    __all__.extend(['AlertSystem', 'create_alert_system'])
except ImportError as e:
    logger.warning(f"Could not import alert_system: {e}")

try:
    from .health_checker import HealthChecker, create_health_checker
    __all__.extend(['HealthChecker', 'create_health_checker'])
except ImportError as e:
    logger.warning(f"Could not import health_checker: {e}")
''',

        "data/__init__.py": '''"""
Data module pour MIA_IA_SYSTEM
"""

import logging

logger = logging.getLogger(__name__)

# Safe imports
__all__ = []

try:
    from .data_collector import DataCollector, create_data_collector
    __all__.extend(['DataCollector', 'create_data_collector'])
except ImportError as e:
    logger.warning(f"Could not import data_collector: {e}")

try:
    from .market_data_feed import MarketDataFeed, create_market_data_feed
    __all__.extend(['MarketDataFeed', 'create_market_data_feed'])
except ImportError as e:
    logger.warning(f"Could not import market_data_feed: {e}")
''',

        "ml/__init__.py": '''"""
ML module pour MIA_IA_SYSTEM
"""

import logging

logger = logging.getLogger(__name__)

# Safe imports
__all__ = []

try:
    from .simple_model import SimpleLinearPredictor, ModelType, create_battle_navale_model
    __all__.extend(['SimpleLinearPredictor', 'ModelType', 'create_battle_navale_model'])
except ImportError as e:
    logger.warning(f"Could not import simple_model: {e}")

try:
    from .data_processor import MLDataProcessor, create_data_processor
    __all__.extend(['MLDataProcessor', 'create_data_processor'])
except ImportError as e:
    logger.warning(f"Could not import data_processor: {e}")

try:
    from .model_validator import ModelValidator, create_model_validator
    __all__.extend(['ModelValidator', 'create_model_validator'])
except ImportError as e:
    logger.warning(f"Could not import model_validator: {e}")

try:
    from .model_trainer import ModelTrainer, create_model_trainer
    __all__.extend(['ModelTrainer', 'create_model_trainer'])
except ImportError as e:
    logger.warning(f"Could not import model_trainer: {e}")
''',

        "performance/__init__.py": '''"""
Performance module pour MIA_IA_SYSTEM
"""

import logging

logger = logging.getLogger(__name__)

# Safe imports
__all__ = []

try:
    from .trade_logger import TradeLogger, create_trade_logger
    __all__.extend(['TradeLogger', 'create_trade_logger'])
except ImportError as e:
    logger.warning(f"Could not import trade_logger: {e}")

try:
    from .performance_analyzer import PerformanceAnalyzer, create_performance_analyzer
    __all__.extend(['PerformanceAnalyzer', 'create_performance_analyzer'])
except ImportError as e:
    logger.warning(f"Could not import performance_analyzer: {e}")

try:
    from .adaptive_optimizer import AdaptiveOptimizer, create_adaptive_optimizer
    __all__.extend(['AdaptiveOptimizer', 'create_adaptive_optimizer'])
except ImportError as e:
    logger.warning(f"Could not import adaptive_optimizer: {e}")

try:
    from .automation_metrics import AutomationMetrics, create_automation_metrics
    __all__.extend(['AutomationMetrics', 'create_automation_metrics'])
except ImportError as e:
    logger.warning(f"Could not import automation_metrics: {e}")
'''
    }
    
    print("🔧 Remplacement forcé des fichiers __init__.py")
    print("=" * 60)
    
    for file_path, content in init_contents.items():
        full_path = project_root / file_path
        
        print(f"\n📄 Remplacement: {file_path}")
        
        try:
            # Backup
            if full_path.exists():
                backup_path = full_path.with_suffix('.py.backup_force')
                shutil.copy2(full_path, backup_path)
                print(f"  ✓ Backup créé: {backup_path.name}")
            
            # Créer le répertoire si nécessaire
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Écrire le nouveau contenu
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ Fichier remplacé avec succès")
            
            # Vérifier la syntaxe
            import ast
            try:
                ast.parse(content)
                print(f"  ✅ Syntaxe validée")
            except SyntaxError as e:
                print(f"  ❌ Erreur de syntaxe: {e}")
                
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ Remplacement terminé !")
    print("\nTestez maintenant les imports :")
    print('python -c "import config; import core; import features; print(\'OK\')"')

if __name__ == "__main__":
    replace_init_files()