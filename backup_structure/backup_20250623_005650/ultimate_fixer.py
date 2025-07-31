"""
MIA_IA_SYSTEM - Ultimate Fixer
Correction finale imports + nettoyage fichiers parasites
Version: Sans emojis, sans fichiers problematiques
"""

import sys
import os
import importlib
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)


def clean_problematic_files():
    """Supprime fichiers problematiques avec emojis"""
    logger.info("NETTOYAGE FICHIERS PROBLEMATIQUES")
    print("-" * 40)
    
    problematic_files = [
        "performance_patch.py",
        "performance_patch_corrected.py", 
        "fix_base_types_final.py",
        "base_types_optional.py",
        "complete_fix_plan.py"
    ]
    
    cleaned = []
    for file_path in problematic_files:
        if Path(file_path).exists():
            try:
                os.remove(file_path)
                cleaned.append(file_path)
                logger.info("[REMOVED] {file_path}")
            except Exception as e:
                logger.info("[ERROR] Cannot remove {file_path}: {e}")
    
    logger.info("[OK] {len(cleaned)} fichiers problematiques supprimes")
    return cleaned

def ensure_init_files():
    """Assure presence fichiers __init__.py"""
    logger.info("\nCREATION __init__.py MANQUANTS")
    print("-" * 40)
    
    directories = ["config", "core", "features", "strategies", "tests"]
    created = []
    
    for directory in directories:
        dir_path = Path(directory)
        if dir_path.exists():
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                # Contenu minimal sans emojis
                if directory == "config":
                    content = '''"""Configuration package"""
from .trading_config import (
    TradingConfig, get_trading_config, get_risk_config
)
__all__ = ['TradingConfig', 'get_trading_config', 'get_risk_config']
'''
                elif directory == "core":
                    content = '''"""Core package"""
from .base_types import (
    MarketData, SignalType, ES_TICK_SIZE
)
__all__ = ['MarketData', 'SignalType', 'ES_TICK_SIZE']
'''
                else:
                    content = f'"""Package {directory}"""\n'
                
                init_file.write_text(content, encoding='utf-8')
                created.append(str(init_file))
                logger.info("[CREATED] {init_file}")
    
    logger.info("[OK] {len(created)} fichiers __init__.py crees")
    return created

def test_critical_imports():
    """Test imports critiques seulement"""
    logger.info("\nTEST IMPORTS CRITIQUES")
    print("-" * 40)
    
    # Ajouter au path
    project_root = Path(".").absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    critical_modules = [
        "config.trading_config",
        "core.base_types",
        "config", 
        "core"
    ]
    
    success_count = 0
    
    for module_name in critical_modules:
        try:
            # Clear cache
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            importlib.import_module(module_name)
            logger.info("[OK] {module_name}")
            success_count += 1
            
        except Exception as e:
            logger.info("[ERROR] {module_name}: {e}")
    
    logger.info("\n[RESULT] {success_count}/{len(critical_modules)} imports OK")
    return success_count == len(critical_modules)

def test_functionality():
    """Test fonctionnalite de base"""
    logger.info("\nTEST FONCTIONNALITE")
    print("-" * 40)
    
    try:
        # Test config
        from config import get_trading_config
        config = get_trading_config()
        logger.info("[OK] Config: {config.trading_mode.value}")
        
        # Test core types
        from core import MarketData, ES_TICK_SIZE
        logger.info("[OK] ES_TICK_SIZE: {ES_TICK_SIZE}")
        
        # Test creation MarketData avec tous parametres
        import pandas as pd
        test_data = MarketData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            open=4500.0,
            high=4510.0, 
            low=4495.0,
            close=4505.0,
            volume=1000
        )
        logger.info("[OK] MarketData creation: {test_data.close}")
        
        return True
        
    except Exception as e:
        logger.info("[ERROR] Functionality test: {e}")
        return False

def main():
    """Correction finale complete"""
    print("=" * 50)
    logger.info("MIA_IA_SYSTEM - ULTIMATE FIXER")
    print("=" * 50)
    
    # 1. Nettoyage
    cleaned_files = clean_problematic_files()
    
    # 2. Creation __init__.py
    created_inits = ensure_init_files()
    
    # 3. Test imports
    imports_ok = test_critical_imports()
    
    # 4. Test fonctionnalite
    functionality_ok = test_functionality()
    
    # Resume
    print("\n" + "=" * 50)
    logger.info("RESUME CORRECTION")
    print("=" * 50)
    
    logger.info("[INFO] Fichiers nettoyes: {len(cleaned_files)}")
    logger.info("[INFO] __init__.py crees: {len(created_inits)}")
    logger.info("[INFO] Imports: {'OK' if imports_ok else 'FAILED'}")
    logger.info("[INFO] Fonctionnalite: {'OK' if functionality_ok else 'FAILED'}")
    
    if imports_ok and functionality_ok:
        logger.info("\n[SUCCESS] CORRECTION REUSSIE!")
        logger.info("[NEXT] Lancer maintenant: python technical_audit.py")
        logger.info("[EXPECT] Score audit: 85-90%+")
        return True
    else:
        logger.info("\n[FAILED] CORRECTION INCOMPLETE")
        if not imports_ok:
            logger.info("[ACTION] Verifier structure fichiers manuellement")
        if not functionality_ok:
            logger.info("[ACTION] Verifier contenu trading_config.py et base_types.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)