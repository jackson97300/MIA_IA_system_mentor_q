#!/usr/bin/env python3
"""
Correction rapide SimpleTrader import
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_simple_trader_import():
    """Corrige l'import SimpleTrader"""
    logger.info("🔧 CORRECTION IMPORT SIMPLETRADER")
    
    simple_trader_file = Path(__file__).parent / 'execution' / 'simple_trader.py'
    
    try:
        with open(simple_trader_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ajouter l'alias SimpleTrader
        additional_exports = '''

# Alias pour compatibilité
SimpleTrader = SimpleBattleNavaleTrader

# Exports principaux
__all__ = [
    'SimpleBattleNavaleTrader',
    'SimpleTrader',
    'create_simple_trader',
    'run_data_collection_session',
    'TradingSession',
    'Position',
    'TradingMode',
    'AutomationStatus'
]
'''
        
        # Ajouter à la fin du fichier
        if 'SimpleTrader = SimpleBattleNavaleTrader' not in content:
            with open(simple_trader_file, 'a', encoding='utf-8') as f:
                f.write(additional_exports)
            
            logger.info("✅ Alias SimpleTrader ajouté")
        else:
            logger.info("✅ Alias SimpleTrader déjà présent")
            
    except Exception as e:
        logger.error(f"❌ Erreur correction simple_trader: {e}")

def test_fix():
    """Teste la correction"""
    logger.info("🧪 TEST CORRECTION SIMPLETRADER")
    
    try:
        from execution.simple_trader import SimpleTrader
        logger.info("✅ SimpleTrader - IMPORT RÉUSSI")
        
        # Test création instance
        trader = SimpleTrader("PAPER")
        logger.info("✅ SimpleTrader - INSTANCIATION RÉUSSIE")
        
    except Exception as e:
        logger.error(f"❌ Test SimpleTrader échoué: {e}")

def main():
    """Correction principale"""
    logger.info("🚀 === CORRECTION RAPIDE SIMPLETRADER ===")
    
    fix_simple_trader_import()
    test_fix()
    
    logger.info("🎉 CORRECTION TERMINÉE")

if __name__ == "__main__":
    main()
