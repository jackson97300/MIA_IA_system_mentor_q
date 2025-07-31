"""
Test imports pour audit technique
Contourne probleme chemins Windows
"""

import sys
import importlib
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)


def test_imports_for_audit():
    """Test imports compatibles audit"""
    
    # Add to path
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Test modules critiques
    modules_to_test = {
        'config.trading_config': 'config/trading_config.py',
        'core.base_types': 'core/base_types.py',
        'config': 'config/__init__.py',
        'core': 'core/__init__.py'
    }
    
    results = {}
    
    for module_name, file_path in modules_to_test.items():
        try:
            # Verifier fichier existe
            if not Path(file_path).exists():
                results[module_name] = f"File missing: {file_path}"
                continue
            
            # Test import
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            importlib.import_module(module_name)
            results[module_name] = "OK"
            
        except Exception as e:
            results[module_name] = f"Error: {str(e)}"
    
    return results

if __name__ == "__main__":
    results = test_imports_for_audit()
    
    logger.info("IMPORT TEST RESULTS:")
    print("=" * 30)
    
    success_count = 0
    for module, result in results.items():
        status = "[OK]" if result == "OK" else "[ERROR]"
        logger.info("{status} {module}: {result}")
        if result == "OK":
            success_count += 1
    
    logger.info("\nSUCCESS RATE: {success_count}/{len(results)}")
    
    if success_count == len(results):
        logger.info("ALL IMPORTS OK - Audit should pass")
    else:
        logger.info("IMPORTS FAILED - Fix required")
