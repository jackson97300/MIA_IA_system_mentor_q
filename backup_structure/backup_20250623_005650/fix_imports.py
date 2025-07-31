"""
MIA_IA_SYSTEM - Import Fixer
Correction automatique des imports cassés
"""

import os
import sys
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)


def fix_imports_project():
    """Correction complète des imports du projet"""
    logger.info("🔧 FIXING IMPORTS AUTOMATIQUE...")
    
    project_root = Path(".")
    
    # 1. Créer __init__.py manquants
    create_missing_init_files(project_root)
    
    # 2. Fixer PYTHONPATH
    fix_python_path()
    
    # 3. Créer config/__init__.py correct
    create_config_init()
    
    # 4. Vérifier structure
    verify_structure()
    
    logger.info("IMPORTS FIXES COMPLETE!")

def create_missing_init_files(project_root: Path):
    """Créer tous les __init__.py manquants"""
    logger.info("\n📁 Création __init__.py...")
    
    directories = ['config', 'core', 'features', 'strategies', 'tests']
    
    for directory in directories:
        dir_path = project_root / directory
        if dir_path.exists():
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_file.touch()
                logger.info("Créé: {init_file}")

def fix_python_path():
    """Ajouter projet au PYTHONPATH"""
    logger.info("\n🐍 Fix PYTHONPATH...")
    
    # Créer setup.py minimal pour développement
    setup_content = '''"""Setup pour développement local"""
import sys
from pathlib import Path

# Ajouter projet root au path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

logger.info("Projet ajouté au PYTHONPATH: {project_root}")
'''
    
    with open("setup_dev.py", "w", encoding="utf-8") as f:
        f.write(setup_content)
    
    logger.info("setup_dev.py créé")

def create_config_init():
    """Créer config/__init__.py correct"""
    logger.info("\n⚙️ Création config/__init__.py...")
    
    config_init = '''"""
MIA_IA_SYSTEM - Configuration Package
Exports propres pour éviter les imports cassés
"""

from .trading_config import (
    TradingConfig,
    SymbolConfig,
    RiskManagementConfig,
    FeatureConfig,
    TradingMode,
    DataSource,
    ExecutionMode,
    RiskLevel,
    create_default_config,
    create_paper_trading_config,
    create_live_trading_config,
    get_trading_config,
    set_trading_config,
    get_risk_config,
    get_feature_config
)

__all__ = [
    'TradingConfig',
    'SymbolConfig', 
    'RiskManagementConfig',
    'FeatureConfig',
    'TradingMode',
    'DataSource',
    'ExecutionMode',
    'RiskLevel',
    'create_default_config',
    'create_paper_trading_config',
    'create_live_trading_config',
    'get_trading_config',
    'set_trading_config',
    'get_risk_config',
    'get_feature_config'
]
'''
    
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    with open(config_dir / "__init__.py", "w", encoding="utf-8") as f:
        f.write(config_init)
    
    logger.info("config/__init__.py créé")

def verify_structure():
    """Vérifier structure finale"""
    logger.info("\n🔍 Vérification structure...")
    
    required_files = [
        "config/__init__.py",
        "config/trading_config.py",
        "core/__init__.py", 
        "core/base_types.py",
        "core/patterns_detector.py",
        "core/battle_navale.py"
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        logger.error("Fichiers manquants:")
        for file in missing:
            logger.info("   • {file}")
    else:
        logger.info("Structure complète!")

def test_imports_quick():
    """Test rapide des imports critiques"""
    logger.info("\n🧪 Test imports rapide...")
    
    # Ajouter au path pour test
    import sys
    sys.path.insert(0, ".")
    
    test_modules = [
        "config.trading_config",
        "core.base_types", 
        "config",
        "core"
    ]
    
    failed = []
    for module in test_modules:
        try:
            __import__(module)
            logger.info("{module}")
        except Exception as e:
            failed.append((module, str(e)))
            logger.error("{module}: {e}")
    
    return len(failed) == 0

if __name__ == "__main__":
    # Exécution
    fix_imports_project()
    
    # Test
    success = test_imports_quick()
    
    if success:
        logger.info("\n🎉 IMPORTS FIXES RÉUSSIS!")
        logger.info("\nPROCHAINES ÉTAPES:")
        logger.info("1. Exécuter: python -c 'import setup_dev'")
        logger.info("2. Tester: python technical_audit.py")
        print("3. Vérifier: python -c 'from config import get_trading_config; print(\"OK\")'")
    else:
        logger.info("\n💀 IMPORTS ENCORE CASSÉS - Debug nécessaire")