"""
MIA_IA_SYSTEM - Test Rapide Imports
Test rapide sans problème de guillemets
"""

import sys
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)


def test_imports_quick():
    """Test imports rapide"""
    logger.debug("TEST IMPORTS RAPIDE")
    print("-" * 30)
    
    # Ajouter projet au path
    project_root = Path(".").absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        logger.info("Path ajouté: {project_root}")
    
    # Test 1: Config trading
    try:
        from config import get_trading_config
        config = get_trading_config()
        logger.info("Config import: OK")
        logger.info("Trading mode: {config.trading_mode.value}")
    except Exception as e:
        logger.error("Config import: {e}")
        return False
    
    # Test 2: Core types
    try:
        from core import MarketData, ES_TICK_SIZE
        logger.info("Core import: OK")
        logger.info("ES_TICK_SIZE: {ES_TICK_SIZE}")
    except Exception as e:
        logger.error("Core import: {e}")
        return False
    
    # Test 3: Configuration complète
    try:
        symbols = list(config.symbols.keys())
        risk_config = config.risk_management
        logger.info("Symboles: {symbols}")
        logger.info("Max position: {risk_config.max_position_size}")
        logger.info("Daily loss limit: {risk_config.max_daily_loss}")
    except Exception as e:
        logger.error("Config access: {e}")
        return False
    
    logger.info("\n🎉 TOUS IMPORTS OK!")
    return True

def test_structure():
    """Test structure projet"""
    logger.info("\n📁 TEST STRUCTURE")
    print("-" * 30)
    
    required_files = [
        "config/__init__.py",
        "config/trading_config.py", 
        "core/__init__.py",
        "core/base_types.py"
    ]
    
    missing = []
    for file_path in required_files:
        if Path(file_path).exists():
            logger.info("{file_path}")
        else:
            logger.error("MANQUANT: {file_path}")
            missing.append(file_path)
    
    if missing:
        logger.info("\n💀 FICHIERS MANQUANTS: {len(missing)}")
        logger.info("Action: Créer les fichiers manquants")
        return False
    else:
        logger.info("\n✅ Structure complète!")
        return True

def create_missing_files():
    """Créer fichiers manquants si nécessaire"""
    logger.info("\n🔧 CRÉATION FICHIERS MANQUANTS")
    print("-" * 30)
    
    # 1. config/__init__.py
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    config_init = config_dir / "__init__.py"
    if not config_init.exists():
        config_init_content = '''"""
MIA_IA_SYSTEM - Configuration Package
"""

from .trading_config import (
    TradingConfig,
    TradingMode,
    create_default_config,
    get_trading_config,
    get_risk_config
)

__all__ = [
    'TradingConfig',
    'TradingMode', 
    'create_default_config',
    'get_trading_config',
    'get_risk_config'
]
'''
        config_init.write_text(config_init_content, encoding='utf-8')
        logger.info("Créé: {config_init}")
    
    # 2. core/__init__.py  
    core_dir = Path("core")
    core_dir.mkdir(exist_ok=True)
    
    core_init = core_dir / "__init__.py"
    if not core_init.exists():
        core_init_content = '''"""
MIA_IA_SYSTEM - Core Package
"""

from .base_types import (
    MarketData,
    OrderFlowData,
    TradingSignal,
    SignalType,
    MarketRegime,
    ES_TICK_SIZE,
    ES_TICK_VALUE
)

__all__ = [
    'MarketData',
    'OrderFlowData',
    'TradingSignal', 
    'SignalType',
    'MarketRegime',
    'ES_TICK_SIZE',
    'ES_TICK_VALUE'
]
'''
        core_init.write_text(core_init_content, encoding='utf-8')
        logger.info("Créé: {core_init}")
    
    logger.info("Fichiers manquants créés!")

def main():
    """Test principal"""
    logger.info("🚀 MIA_IA_SYSTEM - TEST RAPIDE")
    print("=" * 40)
    
    # Test structure
    structure_ok = test_structure()
    
    if not structure_ok:
        logger.info("\n🔧 CRÉATION FICHIERS MANQUANTS...")
        create_missing_files()
        logger.info("\n🔄 RE-TEST STRUCTURE...")
        structure_ok = test_structure()
    
    if structure_ok:
        logger.info("\n🧪 TEST IMPORTS...")
        imports_ok = test_imports_quick()
        
        if imports_ok:
            logger.info("\n🎉 TESTS RÉUSSIS - SYSTÈME OPÉRATIONNEL!")
            return True
        else:
            logger.info("\n💀 PROBLÈME IMPORTS - DEBUG REQUIS")
            return False
    else:
        logger.info("\n💀 PROBLÈME STRUCTURE - FICHIERS MANQUANTS")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        logger.info("\n📋 PROCHAINES ÉTAPES:")
        logger.info("1. python technical_audit.py")
        logger.info("2. Si audit fail → python fix_imports.py")
        logger.info("3. Si performance issues → python performance_optimizer.py")
    else:
        logger.info("\n📋 ACTIONS REQUISES:")
        logger.info("1. Vérifier que trading_config.py existe")
        logger.info("2. Vérifier que base_types.py existe") 
        logger.info("3. Re-run: python test_quick.py")
    
    sys.exit(0 if success else 1)