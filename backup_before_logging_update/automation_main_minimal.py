#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Automation Main MINIMAL
Version minimale pour tester sans erreurs d'import
"""

import sys
import os
import logging
import argparse
from datetime import datetime

# Configuration logging simple
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Tester les imports critiques
def test_imports():
    """Test des imports essentiels"""
    imports_status = {}
    
    # Core
    try:
        from core.base_types import MarketData, TradingSignal, ES_TICK_SIZE
        imports_status['core.base_types'] = "✅"
    except Exception as e:
        imports_status['core.base_types'] = f"❌ {str(e)}"
    
    # Strategies
    try:
        from strategies.signal_generator import SignalGenerator
        imports_status['strategies.signal_generator'] = "✅"
    except Exception as e:
        imports_status['strategies.signal_generator'] = f"❌ {str(e)}"
    
    # Config basique
    try:
        from config.trading_config import TradingConfig, get_trading_config
        imports_status['config.trading_config'] = "✅"
    except Exception as e:
        imports_status['config.trading_config'] = f"❌ {str(e)}"
    
    # Execution
    try:
        from execution.order_manager import OrderManager
        imports_status['execution.order_manager'] = "✅"
    except Exception as e:
        imports_status['execution.order_manager'] = f"❌ {str(e)}"
    
    return imports_status

def create_minimal_config():
    """Crée une configuration minimale sans dépendances complexes"""
    return {
        'trading_mode': 'paper',
        'max_position_size': 1,
        'daily_loss_limit': 500.0,
        'min_signal_confidence': 0.70,
        'enable_monitoring': True
    }

def run_minimal_test():
    """Test minimal du système"""
    logger.info("🚀 MIA Trading System - Test Minimal")
    logger.info("=" * 50)
    
    # Test imports
    logger.info("\n📦 Test des imports...")
    imports = test_imports()
    
    for module, status in imports.items():
        logger.info(f"  {module}: {status}")
    
    # Compter succès
    success_count = sum(1 for s in imports.values() if "✅" in s)
    total_count = len(imports)
    
    logger.info(f"\n📊 Résultat: {success_count}/{total_count} imports réussis")
    
    # Test configuration minimale
    if success_count == total_count:
        logger.info("\n⚙️ Test configuration minimale...")
        config = create_minimal_config()
        logger.info(f"  Mode: {config['trading_mode']}")
        logger.info(f"  Position max: {config['max_position_size']}")
        logger.info(f"  Loss limit: ${config['daily_loss_limit']}")
        
        # Test signal generator si disponible
        try:
            from strategies.signal_generator import create_signal_generator
            from core.base_types import MarketData
            import pandas as pd
            
            logger.info("\n🧠 Test Signal Generator...")
            generator = create_signal_generator()
            
            # Données test
            market_data = MarketData(
                timestamp=pd.Timestamp.now(),
                symbol="ES",
                open=4500.0,
                high=4505.0,
                low=4495.0,
                close=4502.0,
                volume=1000
            )
            
            signal = generator.generate_signal(market_data)
            logger.info(f"  Signal généré: {signal.decision}")
            logger.info(f"  Confidence: {signal.confidence:.2%}")
            
        except Exception as e:
            logger.error(f"❌ Erreur test signal: {e}")
    
    logger.info("\n✅ Test minimal terminé")
    return success_count == total_count

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='MIA Trading System - Minimal')
    parser.add_argument('--dry-run', action='store_true', help='Mode dry-run')
    parser.add_argument('--test', action='store_true', help='Test minimal')
    args = parser.parse_args()
    
    try:
        # Test par défaut
        success = run_minimal_test()
        
        if success and not args.test:
            logger.info("\n🎯 Système prêt pour automation")
            logger.info("Pour corriger les imports manquants:")
            logger.info("1. Vérifier sierra_config.py")
            logger.info("2. Vérifier automation_config.py") 
            logger.info("3. Lancer: python fix_encoding.py")
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())