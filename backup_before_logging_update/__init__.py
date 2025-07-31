"""
MIA_IA_SYSTEM - Système de Trading Automatisé
🧠 Bot de trading avec méthode Bataille Navale + Intelligence artificielle
Version: 3.0.0 avec SignalGenerator
    else:
        # Fallback pour Python < 3.7
        try:
        except:
            # Si erreur, ne rien faire (éviter le crash)
            pass

POINT D'ENTRÉE PRINCIPAL :
from strategies import get_signal_now, analyze_trading_opportunity

USAGE RAPIDE :
```python
from strategies import get_signal_now
from core.base_types import MarketData

# Générer signal en 1 ligne
signal = get_signal_now(market_data)
if signal.decision == SignalDecision.EXECUTE_LONG:
    execute_trade(signal)
```

ARCHITECTURE COMPLÈTE :
- core/ : Types de base + Bataille Navale
- features/ : Calcul features + Confluence
- strategies/ : Orchestration signaux (SignalGenerator)
- execution/ : Exécution trades
- monitoring/ : Surveillance système
"""

# 🧠 CERVEAU CENTRAL - Import direct du système principal
from strategies import (
import logging

# Configure logging
logger = logging.getLogger(__name__)

    SignalGenerator, FinalSignal, SignalDecision,
    create_signal_generator, generate_trading_signal,
    get_signal_now, analyze_trading_opportunity
)

# Core components
from core import (
    MarketData, TradingSignal, SignalType, MarketRegime,
    ES_TICK_SIZE, ES_TICK_VALUE
)

# Features
from features import (
    FeatureCalculator, ConfluenceAnalyzer, MarketRegimeDetector
)

# Version globale
__version__ = "3.0.0"
__author__ = "MIA Trading System"

# Exports globaux - Point d'entrée système
__all__ = [
    # 🎯 POINT D'ENTRÉE PRINCIPAL (usage simplifié)
    'get_signal_now',
    'analyze_trading_opportunity',
    
    # 🧠 Système complet (usage avancé)
    'SignalGenerator',
    'FinalSignal',
    'SignalDecision', 
    'create_signal_generator',
    'generate_trading_signal',
    
    # Core essentials
    'MarketData',
    'TradingSignal',
    'SignalType',
    'MarketRegime',
    
    # Constants
    'ES_TICK_SIZE',
    'ES_TICK_VALUE',
    
    # Version
    '__version__'
]

def quick_start_example():
    """
    🚀 EXEMPLE QUICK START
    
    Montre comment utiliser le système en quelques lignes
    """
    logger.info("🎯 MIA_IA_SYSTEM - Quick Start Example")
    print("=" * 40)
    print()
    logger.info("# 1. Import principal")
    logger.info("from strategies import get_signal_now")
    logger.info("from core.base_types import MarketData")
    print()
    logger.info("# 2. Créer données marché") 
    logger.info("market_data = MarketData(")
    logger.info("    timestamp=pd.Timestamp.now(),")
    logger.info("    symbol='ES', open=4500, high=4505,")
    logger.info("    low=4495, close=4502, volume=1000")
    logger.info(")")
    print()
    logger.info("# 3. Générer signal (1 ligne !)")
    logger.info("signal = get_signal_now(market_data)")
    print()
    logger.info("# 4. Décision trading")
    logger.info("if signal.decision == SignalDecision.EXECUTE_LONG:")
    print("    logger.info("🚀 LONG signal: {signal.confidence:.3f}")")
    logger.info("    # execute_trade(signal)")
    print()
    logger.info("Votre bot est prêt !")

if __name__ == "__main__":
    quick_start_example()
