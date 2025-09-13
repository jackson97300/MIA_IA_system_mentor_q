"""
MIA_IA_SYSTEM - Import Testing Suite
Test automatique de tous les imports pour éviter erreurs
Version: Production Ready
Performance: Validation rapide imports
"""

import sys
import importlib
import traceback
from pathlib import Path
from typing import List, Tuple, Dict, Any
import time
from core.logger import get_logger

# Configure logging
logger = get_logger(__name__)


# === PHASE 1 MODULES TO TEST ===

PHASE_1_MODULES = [
    # Core types (leaf - no local imports)
    'core.base_types',

    # Config (leaf - no local imports)
    'config.trading_config',

    # Package exports
    'config',
    'core',
]

# === VALIDATION FUNCTIONS ===


def test_single_import(module_name: str) -> Tuple[bool, str, float]:
    """Test import d'un module unique"""
    start_time = time.perf_counter()

    try:
        # Clear module cache to ensure fresh import
        if module_name in sys.modules:
            del sys.modules[module_name]

        # Import module
        imported_module = importlib.import_module(module_name)

        # Verify module has expected attributes
        if not hasattr(imported_module, '__file__'):
            return False, "Module sans __file__ attribute", 0

        import_time = (time.perf_counter() - start_time) * 1000
        return True, "OK", import_time

    except ImportError as e:
        import_time = (time.perf_counter() - start_time) * 1000
        return False, f"ImportError: {str(e)}", import_time

    except SyntaxError as e:
        import_time = (time.perf_counter() - start_time) * 1000
        return False, f"SyntaxError: {str(e)} at line {e.lineno}", import_time

    except Exception as e:
        import_time = (time.perf_counter() - start_time) * 1000
        return False, f"Unexpected error: {str(e)}", import_time


def test_module_functionality(module_name: str) -> Tuple[bool, str]:
    """Test fonctionnalité basique du module"""
    try:
        module = importlib.import_module(module_name)

        # Test spécifique par module
        if module_name == 'core.base_types':
            # Test création MarketData
            from core.base_types import MarketData, SignalType
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

            if not test_data.is_bullish:
                return False, "MarketData logic error"

        elif module_name == 'config.trading_config':
            # Test création config
            from config.trading_config import create_default_config

            config = create_default_config()
            if not config.validate():
                return False, "Config validation failed"

        elif module_name == 'config':
            # Test exports package
            from config import get_trading_config, TradingMode

            config = get_trading_config()
            if config.trading_mode not in TradingMode:
                return False, "Config package export error"

        elif module_name == 'core':
            # Test exports package
            from core import MarketData, ES_TICK_SIZE

            if ES_TICK_SIZE != 0.25:
                return False, "Core package export error"

        return True, "Functionality OK"

    except Exception as e:
        return False, f"Functionality test failed: {str(e)}"


def test_circular_imports() -> Tuple[bool, str]:
    """Test détection imports circulaires"""
    try:
        # Clear all project modules from cache
        modules_to_clear = [m for m in sys.modules.keys()
                            if m.startswith(('core', 'config'))]

        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]

        # Import all modules in sequence
        for module_name in PHASE_1_MODULES:
            importlib.import_module(module_name)

        return True, "No circular imports detected"

    except Exception as e:
        return False, f"Circular import detected: {str(e)}"


def test_syntax_all_files() -> List[Tuple[str, bool, str]]:
    """Test syntaxe de tous les fichiers Python"""
    project_root = Path(__file__).parent.parent
    python_files = []

    # Scan files in specific directories only (phase 1)
    for directory in ['core', 'config', 'tests']:
        dir_path = project_root / directory
        if dir_path.exists():
            python_files.extend(dir_path.rglob("*.py"))

    results = []

    for py_file in python_files:
        if "__pycache__" in str(py_file):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                source = f.read()

            # Compile syntax
            compile(source, str(py_file), 'exec')
            results.append((str(py_file), True, "Syntax OK"))

        except SyntaxError as e:
            results.append((str(py_file), False, f"Syntax error line {e.lineno}: {e.msg}"))
        except Exception as e:
            results.append((str(py_file), False, f"Error: {str(e)}"))

    return results

# === MAIN TEST FUNCTIONS ===


def test_phase_1_imports() -> bool:
    """Test complet imports Phase 1"""
    logger.debug("TEST IMPORTS PHASE 1")
    print("=" * 50)

    all_passed = True
    total_time = 0.0

    # Test individual module imports
    logger.info("\n📦 TEST MODULES INDIVIDUELS:")
    for module_name in PHASE_1_MODULES:
        success, message, import_time = test_single_import(module_name)
        total_time += import_time

        status = "[OK]" if success else "[ERROR]"
        logger.info("{status} {module_name:25} ({import_time:5.1f}ms) - {message}")

        if not success:
            all_passed = False

    # Test functionality
    logger.info("\n🧪 TEST FONCTIONNALITÉ:")
    for module_name in PHASE_1_MODULES:
        success, message = test_module_functionality(module_name)

        status = "[OK]" if success else "[ERROR]"
        logger.info("{status} {module_name:25} - {message}")

        if not success:
            all_passed = False

    # Test circular imports
    logger.info("\n[SYNC] TEST IMPORTS CIRCULAIRES:")
    success, message = test_circular_imports()
    status = "[OK]" if success else "[ERROR]"
    logger.info("{status} Circular imports check - {message}")

    if not success:
        all_passed = False

    # Test syntax all files
    logger.info("\n[LOG] TEST SYNTAXE FICHIERS:")
    syntax_results = test_syntax_all_files()
    syntax_passed = 0

    for file_path, success, message in syntax_results:
        file_name = Path(file_path).name
        status = "[OK]" if success else "[ERROR]"
        logger.info("{status} {file_name:25} - {message}")

        if success:
            syntax_passed += 1
        else:
            all_passed = False

    # Summary
    print("\n" + "=" * 50)
    logger.info("[STATS] RÉSULTATS PHASE 1:")
    logger.info("   • Modules testés: {len(PHASE_1_MODULES)}")
    logger.info("   • Temps total import: {total_time:.1f}ms")
    logger.info("   • Fichiers syntax OK: {syntax_passed}/{len(syntax_results)}")

    if all_passed:
        logger.info("[TARGET] TOUS LES TESTS PASSÉS - PHASE 1 READY!")
        return True
    else:
        logger.info("💀 ERREURS DÉTECTÉES - FIX AVANT PHASE 2!")
        return False


def quick_import_test() -> bool:
    """Test rapide pour développement"""
    logger.info("[FAST] QUICK IMPORT TEST...")

    failed_modules = []

    for module_name in PHASE_1_MODULES:
        success, message, _ = test_single_import(module_name)
        if not success:
            failed_modules.append((module_name, message))
            logger.error("{module_name}: {message}")
        else:
            logger.info("{module_name}")

    if failed_modules:
        logger.info("\n💀 {len(failed_modules)} MODULES ÉCHOUÉS")
        return False
    else:
        logger.info("\n[TARGET] ALL {len(PHASE_1_MODULES)} MODULES OK")
        return True


def test_project_structure() -> bool:
    """Validation structure projet Phase 1"""
    logger.info("[FOLDER] TEST STRUCTURE PROJET...")

    project_root = Path(__file__).parent.parent
    required_structure = {
        'core': ['__init__.py', 'base_types.py'],
        'config': ['__init__.py', 'trading_config.py'],
        'tests': ['test_imports.py']
    }

    missing_items = []

    for directory, files in required_structure.items():
        dir_path = project_root / directory

        if not dir_path.exists():
            missing_items.append(f"Directory: {directory}")
            continue

        for file_name in files:
            file_path = dir_path / file_name
            if not file_path.exists():
                missing_items.append(f"File: {directory}/{file_name}")

    if missing_items:
        logger.error("STRUCTURE INCOMPLÈTE:")
        for item in missing_items:
            logger.info("   • Missing: {item}")
        return False
    else:
        logger.info("STRUCTURE PROJET OK")
        return True

# === MAIN EXECUTION ===


def main():
    """Fonction principale de test"""
    logger.info("[LAUNCH] MIA_IA_SYSTEM - IMPORT TESTING SUITE")
    logger.info("Python version: {sys.version}")
    logger.info("Working directory: {Path.cwd()}")

    # Test structure projet
    if not test_project_structure():
        sys.exit(1)

    # Test imports complet
    if not test_phase_1_imports():
        sys.exit(1)

    logger.info("\n[PARTY] PHASE 1 VALIDATION COMPLETE - READY FOR PHASE 2!")


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--quick':
            success = quick_import_test()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == '--structure':
            success = test_project_structure()
            sys.exit(0 if success else 1)

    # Full test suite
    main()
