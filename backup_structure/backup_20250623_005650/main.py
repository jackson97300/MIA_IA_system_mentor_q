"""
MIA_IA_SYSTEM - Main Entry Point
Point d'entrée principal système trading
Version: Production Ready
Performance: Optimisé pour trading live
"""

import sys
import time
import signal
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import argparse

# === SETUP DIRECTORIES FIRST ===

def ensure_directories():
    """Création répertoires AVANT logging setup"""
    directories = ['logs', 'data', 'models', 'config_files']
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(parents=True, exist_ok=True)

# Create directories BEFORE logging setup
ensure_directories()

# Setup logging AFTER directories exist - FIX UNICODE ENCODING
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/mia_system.log', mode='a', encoding='utf-8')  # FIX: encoding UTF-8
    ]
)

logger = logging.getLogger(__name__)

# Test imports Phase 1
try:
    from config import (
        get_trading_config, 
        set_trading_config,
        create_paper_trading_config,
        create_live_trading_config,
        TradingMode,
        RiskLevel
    )
    from core import (
        MarketData,
        TradingSignal,
        TradingFeatures,
        SignalType,
        MarketRegime,
        ES_TICK_SIZE,
        ES_TICK_VALUE,
        get_session_phase,
        validate_market_data
    )
    logger.info("Phase 1 imports successful")  # FIX: Remove emoji
    
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.info("ERREUR CRITIQUE: {e}")
    logger.info("Vérifiez que tous les fichiers Phase 1 sont présents")
    sys.exit(1)

# === SYSTEM STATE ===

class SystemState:
    """État global du système"""
    def __init__(self):
        self.is_running = False
        self.trading_active = False
        self.start_time = None
        self.config = None
        self.performance_stats = {
            'uptime_seconds': 0,
            'signals_generated': 0,
            'trades_executed': 0,
            'last_heartbeat': None
        }
    
    def start(self):
        """Démarrage système"""
        self.is_running = True
        self.start_time = datetime.now()
        self.performance_stats['last_heartbeat'] = datetime.now()
        logger.info("System started")
    
    def stop(self):
        """Arrêt système"""
        self.is_running = False
        self.trading_active = False
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
            self.performance_stats['uptime_seconds'] = uptime
        logger.info("System stopped")
    
    def heartbeat(self):
        """Heartbeat système"""
        self.performance_stats['last_heartbeat'] = datetime.now()
        if self.start_time:
            self.performance_stats['uptime_seconds'] = (
                datetime.now() - self.start_time
            ).total_seconds()

# Global system state
system_state = SystemState()

# === SIGNAL HANDLERS ===

def signal_handler(signum, frame):
    """Handler pour arrêt propre"""
    logger.info(f"Signal {signum} reçu - arrêt en cours...")
    system_state.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# === INITIALIZATION FUNCTIONS ===

def setup_directories():
    """Création répertoires nécessaires (redondant mais safe)"""
    directories = ['logs', 'data', 'models', 'config_files']
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Répertoire créé: {dir_name}")

def initialize_system(trading_mode: TradingMode = None) -> bool:
    """Initialisation système complet"""
    try:
        logger.info("Initialisation système...")
        
        # Setup directories (double check)
        setup_directories()
        
        # Load/create configuration
        if trading_mode == TradingMode.PAPER_TRADING:
            config = create_paper_trading_config()
        elif trading_mode == TradingMode.LIVE_TRADING:
            config = create_live_trading_config()
        else:
            config = get_trading_config()
        
        # Set global config
        set_trading_config(config)
        system_state.config = config
        
        logger.info(f"Configuration chargée: {config.trading_mode.value}")
        logger.info(f"Environment: {config.environment}")
        logger.info(f"Max position size: {config.risk_management.max_position_size}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur initialisation: {e}")
        return False

def validate_system() -> bool:
    """Validation système avant démarrage"""
    try:
        logger.info("Validation système...")
        
        # Test config
        config = get_trading_config()
        if not config.validate():
            logger.error("Configuration invalide")
            return False
        
        # Test types core
        import pandas as pd
        test_data = MarketData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            open=4500.0,
            high=4505.0,
            low=4495.0,
            close=4503.0,
            volume=1000
        )
        
        if not validate_market_data(test_data):
            logger.error("Validation market data failed")
            return False
        
        # Test features structure
        test_features = TradingFeatures(
            timestamp=pd.Timestamp.now(),
            battle_navale_signal=0.8,
            gamma_pin_strength=0.6,
            headfake_signal=0.3,
            microstructure_anomaly=0.7,
            market_regime_score=0.9,
            base_quality=0.75,
            confluence_score=0.85,
            session_context=0.6
        )
        
        feature_array = test_features.to_array()
        if len(feature_array) != 8:
            logger.error(f"Features array wrong size: {len(feature_array)}")
            return False
        
        logger.info("Validation système réussie")
        return True
        
    except Exception as e:
        logger.error(f"Erreur validation: {e}")
        return False

# === MAIN TRADING LOOP (PHASE 1 - MINIMAL) ===

def trading_loop_phase1():
    """Boucle trading Phase 1 - simulation basique"""
    logger.info("Démarrage boucle trading Phase 1")
    
    config = get_trading_config()
    loop_count = 0
    
    try:
        while system_state.is_running:
            loop_start = time.perf_counter()
            
            # Simulation données marché
            import pandas as pd
            import numpy as np
            
            current_time = pd.Timestamp.now()
            base_price = 4500.0 + np.random.normal(0, 5)  # ES price simulation
            
            simulated_data = MarketData(
                timestamp=current_time,
                symbol="ES",
                open=base_price,
                high=base_price + abs(np.random.normal(0, 2)),
                low=base_price - abs(np.random.normal(0, 2)),
                close=base_price + np.random.normal(0, 1),
                volume=int(1000 + np.random.normal(0, 200))
            )
            
            # Simulation features
            simulated_features = TradingFeatures(
                timestamp=current_time,
                battle_navale_signal=np.random.uniform(0.3, 0.9),
                gamma_pin_strength=np.random.uniform(0.2, 0.8),
                headfake_signal=np.random.uniform(0.1, 0.6),
                microstructure_anomaly=np.random.uniform(0.4, 0.8),
                market_regime_score=np.random.uniform(0.5, 1.0),
                base_quality=np.random.uniform(0.4, 0.9),
                confluence_score=np.random.uniform(0.3, 0.8),
                session_context=np.random.uniform(0.4, 0.8)
            )
            
            # Simulation signal generation
            confidence = np.mean(simulated_features.to_array())
            
            if confidence > config.features.min_signal_confidence:
                signal = TradingSignal(
                    timestamp=current_time,
                    signal_type=SignalType.LONG_TREND,
                    confidence=confidence,
                    strength=4,  # SignalStrength.STRONG
                    price=simulated_data.close,
                    market_regime=MarketRegime.TREND_BULLISH,
                    patterns_detected=[],
                    features=simulated_features
                )
                
                system_state.performance_stats['signals_generated'] += 1
                
                if loop_count % 10 == 0:  # Log every 10 signals
                    logger.info(f"Signal généré: {signal.signal_type.value} "
                              f"@ {signal.price:.2f} (conf: {signal.confidence:.2f})")
            
            # Performance monitoring
            loop_count += 1
            system_state.heartbeat()
            
            # Logs périodiques
            if loop_count % 100 == 0:
                uptime = system_state.performance_stats['uptime_seconds']
                signals = system_state.performance_stats['signals_generated']
                logger.info(f"Uptime: {uptime:.0f}s, Signals: {signals}, Loops: {loop_count}")
            
            # Performance control
            loop_time = (time.perf_counter() - loop_start) * 1000
            if loop_time > 100:  # Warn if > 100ms
                logger.warning(f"Slow loop: {loop_time:.1f}ms")
            
            # Sleep to control frequency
            time.sleep(0.1)  # 10Hz loop
            
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par utilisateur")
    except Exception as e:
        logger.error(f"Erreur boucle trading: {e}")
    finally:
        logger.info("Boucle trading terminée")

# === TEST FUNCTIONS ===

def test_foundation():
    """Test foundation système Phase 1"""
    logger.info("TEST FOUNDATION PHASE 1")
    print("=" * 40)
    
    try:
        # Test imports
        logger.info("Test imports...")
        config = get_trading_config()
        logger.info("[OK] Config: {config.trading_mode.value}")
        
        # Test types
        logger.info("Test types...")
        import pandas as pd
        
        market_data = MarketData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            open=4500.0,
            high=4505.0,
            low=4495.0,
            close=4503.0,
            volume=1000
        )
        logger.info("[OK] MarketData: {market_data.symbol} @ {market_data.close}")
        
        # Test features
        logger.info("Test features...")
        features = TradingFeatures(
            timestamp=pd.Timestamp.now(),
            battle_navale_signal=0.8,
            gamma_pin_strength=0.6,
            headfake_signal=0.3,
            microstructure_anomaly=0.7,
            market_regime_score=0.9,
            base_quality=0.75,
            confluence_score=0.85,
            session_context=0.6
        )
        
        feature_array = features.to_array()
        logger.info("[OK] Features: {len(feature_array)} dimensions")
        logger.info("[OK] Feature values: {feature_array}")
        
        # Test constants
        logger.info("Test constants...")
        logger.info("[OK] ES tick size: {ES_TICK_SIZE}")
        logger.info("[OK] ES tick value: ${ES_TICK_VALUE}")
        
        # Test utilities
        logger.info("Test utilities...")
        session = get_session_phase(pd.Timestamp.now())
        logger.info("[OK] Current session: {session.value}")
        
        logger.info("\nFOUNDATION TEST COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        logger.info("\nFOUNDATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def performance_test():
    """Test performance système"""
    logger.info("PERFORMANCE TEST")
    print("=" * 30)
    
    import pandas as pd
    import numpy as np
    
    # Test creation speed
    start_time = time.perf_counter()
    
    for i in range(1000):
        market_data = MarketData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            open=4500.0 + i,
            high=4505.0 + i,
            low=4495.0 + i,
            close=4503.0 + i,
            volume=1000 + i
        )
        
        features = TradingFeatures(
            timestamp=pd.Timestamp.now(),
            battle_navale_signal=0.8,
            gamma_pin_strength=0.6,
            headfake_signal=0.3,
            microstructure_anomaly=0.7,
            market_regime_score=0.9,
            base_quality=0.75,
            confluence_score=0.85,
            session_context=0.6
        )
        
        feature_array = features.to_array()
    
    total_time = (time.perf_counter() - start_time) * 1000
    avg_time = total_time / 1000
    
    logger.info("[OK] 1000 iterations: {total_time:.1f}ms")
    logger.info("[OK] Average per iteration: {avg_time:.3f}ms")
    
    if avg_time < 1.0:
        logger.info("PERFORMANCE OK - Ready for production")
        return True
    else:
        logger.info("PERFORMANCE WARNING - Optimize needed")
        return False

# === MAIN FUNCTION ===

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='MIA Trading System')
    parser.add_argument('--mode', choices=['paper', 'live', 'test'], 
                       default='paper', help='Trading mode')
    parser.add_argument('--test-foundation', action='store_true',
                       help='Run foundation tests')
    parser.add_argument('--test-performance', action='store_true',
                       help='Run performance tests')
    parser.add_argument('--validate-only', action='store_true',
                       help='Validate system and exit')
    parser.add_argument('--risk-level', choices=['conservative', 'moderate', 'aggressive'],
                       default='conservative', help='Risk level')
    
    args = parser.parse_args()
    
    logger.info("MIA_IA_SYSTEM - TRADING SYSTEM")
    print("=" * 50)
    logger.info("Version: Phase 1 Foundation")
    logger.info("Python: {sys.version}")
    logger.info("Working Directory: {Path.cwd()}")
    print("=" * 50)
    
    # Test mode
    if args.test_foundation:
        success = test_foundation()
        sys.exit(0 if success else 1)
    
    if args.test_performance:
        success = performance_test()
        sys.exit(0 if success else 1)
    
    # Initialize system
    trading_mode = {
        'paper': TradingMode.PAPER_TRADING,
        'live': TradingMode.LIVE_TRADING,
        'test': TradingMode.SIMULATION
    }[args.mode]
    
    if not initialize_system(trading_mode):
        logger.error("Échec initialisation système")
        sys.exit(1)
    
    # Validate system
    if not validate_system():
        logger.error("Échec validation système")
        sys.exit(1)
    
    if args.validate_only:
        logger.info("Validation réussie - exit")
        sys.exit(0)
    
    # Update risk level
    config = get_trading_config()
    risk_level = {
        'conservative': RiskLevel.CONSERVATIVE,
        'moderate': RiskLevel.MODERATE,
        'aggressive': RiskLevel.AGGRESSIVE
    }[args.risk_level]
    config.update_risk_level(risk_level)
    
    logger.info(f"Démarrage mode: {trading_mode.value}")
    logger.info(f"Risk level: {risk_level.value}")
    
    # Start system
    system_state.start()
    
    try:
        # Phase 1: Basic trading loop
        trading_loop_phase1()
        
    except Exception as e:
        logger.error(f"Erreur critique: {e}")
        sys.exit(1)
    finally:
        system_state.stop()
        
        # Final stats
        stats = system_state.performance_stats
        logger.info("STATISTIQUES FINALES:")
        logger.info(f"   • Uptime: {stats['uptime_seconds']:.0f}s")
        logger.info(f"   • Signals générés: {stats['signals_generated']}")
        logger.info(f"   • Trades exécutés: {stats['trades_executed']}")

if __name__ == "__main__":
    main()