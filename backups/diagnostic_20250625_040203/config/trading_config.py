"""
MIA_IA_SYSTEM - Trading Configuration
Configuration centralisée trading + risk management
Version: Production Ready
Performance: Configuration optimisée pour trading live
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# === CONFIGURATION ENUMS ===

class TradingMode(Enum):
    """Modes de trading"""
    PAPER_TRADING = "paper_trading"
    LIVE_TRADING = "live_trading"
    BACKTESTING = "backtesting"
    SIMULATION = "simulation"

class DataSource(Enum):
    """Sources de données"""
    IBKR = "ibkr"
    SIERRA_CHART = "sierra_chart"
    SIMULATED = "simulated"

class ExecutionMode(Enum):
    """Modes d'exécution"""
    MANUAL_APPROVAL = "manual_approval"
    SEMI_AUTO = "semi_auto"
    FULL_AUTO = "full_auto"

class RiskLevel(Enum):
    """Niveaux de risque"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

# === CORE CONFIGURATION ===

@dataclass
class SymbolConfig:
    """Configuration par symbole"""
    symbol: str
    exchange: str
    tick_size: float
    tick_value: float
    min_quantity: float = 1.0
    max_quantity: float = 10.0
    trading_hours_start: int = 9
    trading_hours_end: int = 16
    commission_per_contract: float = 2.50
    
    def __post_init__(self):
        """Validation configuration symbole"""
        if self.tick_size <= 0:
            raise ValueError(f"Tick size must be > 0: {self.tick_size}")
        if self.max_quantity < self.min_quantity:
            raise ValueError(f"Max quantity < min quantity: {self.max_quantity} < {self.min_quantity}")

@dataclass
class RiskManagementConfig:
    """Configuration risk management"""
    # Position sizing
    max_position_size: int = 3
    position_size_method: str = "fixed"  # fixed, percentage, volatility
    base_position_size: float = 1.0
    
    # Daily limits
    max_daily_loss: float = 1000.0
    max_daily_trades: int = 10
    daily_profit_target: float = 500.0
    stop_trading_on_target: bool = False
    
    # Per trade limits
    max_risk_per_trade: float = 200.0
    min_risk_reward_ratio: float = 1.2
    max_holding_time_minutes: int = 240  # 4 hours
    
    # Stop loss settings
    use_adaptive_stops: bool = True
    base_stop_distance_ticks: int = 8
    max_stop_distance_ticks: int = 20
    trailing_stop_enabled: bool = True
    
    # Portfolio limits
    max_open_positions: int = 2
    max_correlation_exposure: float = 0.7
    
    def validate(self) -> bool:
        """Validation cohérence risk config"""
        try:
            if self.max_daily_loss <= 0:
                logger.error("Max daily loss doit être > 0")
                return False
            
            if self.max_risk_per_trade > self.max_daily_loss:
                logger.error("Risk per trade > daily loss limit")
                return False
            
            if self.min_risk_reward_ratio < 1.0:
                logger.warning("Risk/reward ratio < 1.0 peut être non profitable")
            
            return True
        except Exception as e:
            logger.error(f"Erreur validation risk config: {e}")
            return False

@dataclass
class FeatureConfig:
    """Configuration features et signaux"""
    # Feature calculation
    lookback_periods: int = 20
    feature_update_frequency_ms: int = 1000
    max_calculation_time_ms: float = 5.0
    
    # Signal generation
    min_signal_confidence: float = 0.65
    min_pattern_strength: float = 0.6
    signal_aggregation_method: str = "weighted_average"
    
    # Battle Navale settings
    battle_navale_enabled: bool = True
    min_base_quality: float = 0.6
    rouge_sous_verte_strict: bool = True
    base_size_threshold_ticks: int = 4
    
    # Pattern detection
    gamma_pin_enabled: bool = True
    headfake_detection_enabled: bool = True
    microstructure_ml_enabled: bool = True
    
    # Confluence settings
    confluence_required_levels: int = 2
    confluence_proximity_ticks: float = 2.0
    
    # Regime detection
    trend_range_threshold: float = 0.7
    regime_confirmation_periods: int = 5

@dataclass
class MLConfig:
    """Configuration ML models"""
    # Model settings
    model_type: str = "xgboost"  # xgboost, linear, ensemble
    retrain_frequency_trades: int = 100
    validation_split: float = 0.2
    
    # Performance thresholds
    min_model_accuracy: float = 0.65
    max_model_age_hours: int = 24
    model_validation_required: bool = True
    
    # Feature engineering
    feature_normalization: bool = True
    feature_selection_enabled: bool = False
    max_features: int = 8
    
    # Ensemble settings
    use_ensemble: bool = False
    ensemble_models: List[str] = field(default_factory=lambda: ["xgboost", "linear"])
    ensemble_weights: Dict[str, float] = field(default_factory=lambda: {"xgboost": 0.7, "linear": 0.3})

@dataclass
class DataConfig:
    """Configuration données"""
    # Data sources
    primary_data_source: DataSource = DataSource.IBKR
    backup_data_source: Optional[DataSource] = DataSource.SIERRA_CHART
    
    # Data quality
    max_data_latency_ms: int = 100
    data_validation_enabled: bool = True
    outlier_detection_enabled: bool = True
    
    # Historical data
    historical_data_days: int = 30
    tick_data_retention_hours: int = 24
    
    # Real-time data
    market_data_symbols: List[str] = field(default_factory=lambda: ["ES", "NQ"])
    options_data_enabled: bool = True
    level2_data_enabled: bool = True

@dataclass
class ExecutionConfig:
    """Configuration exécution"""
    # Execution mode
    execution_mode: ExecutionMode = ExecutionMode.SEMI_AUTO
    order_type_default: str = "MARKET"
    
    # Order management
    order_timeout_seconds: int = 30
    partial_fill_handling: str = "accept"  # accept, reject, cancel
    slippage_tolerance_ticks: float = 2.0
    
    # Broker settings
    broker_connection_timeout: int = 10
    max_reconnection_attempts: int = 3
    heartbeat_interval_seconds: int = 30
    
    # Position management
    auto_close_on_session_end: bool = True
    emergency_close_enabled: bool = True
    position_monitoring_interval_ms: int = 1000

@dataclass
class PerformanceConfig:
    """Configuration monitoring performance"""
    # Logging
    trade_logging_enabled: bool = True
    performance_logging_interval_trades: int = 10
    detailed_logging_enabled: bool = True
    
    # Analysis
    real_time_analysis_enabled: bool = True
    performance_analysis_window: int = 100  # trades
    adaptation_enabled: bool = True
    
    # Optimization
    auto_optimization_enabled: bool = True
    optimization_frequency_trades: int = 200
    a_b_testing_enabled: bool = True
    a_b_test_allocation: float = 0.3  # 30% new parameters
    
    # Alerts
    performance_alerts_enabled: bool = True
    alert_on_loss_streak: int = 3
    alert_on_low_win_rate: float = 0.5

# === MAIN CONFIGURATION CLASS ===

@dataclass
class TradingConfig:
    """Configuration principale système trading"""
    # Basic settings
    trading_mode: TradingMode = TradingMode.PAPER_TRADING
    config_version: str = "1.0.0"
    environment: str = "development"  # development, staging, production
    
    # Component configurations
    symbols: Dict[str, SymbolConfig] = field(default_factory=dict)
    risk_management: RiskManagementConfig = field(default_factory=RiskManagementConfig)
    features: FeatureConfig = field(default_factory=FeatureConfig)
    ml: MLConfig = field(default_factory=MLConfig)
    data: DataConfig = field(default_factory=DataConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # File paths
    data_directory: str = "data"
    logs_directory: str = "logs"
    models_directory: str = "models"
    config_file_path: Optional[str] = None
    
    def __post_init__(self):
        """Initialisation post-création"""
        if not self.symbols:
            self._setup_default_symbols()
        
        # Validation configuration
        if not self.validate():
            raise ValueError("Configuration invalide")
    
    def _setup_default_symbols(self):
        """Setup symboles par défaut"""
        # ES Futures
        self.symbols["ES"] = SymbolConfig(
            symbol="ES",
            exchange="CME",
            tick_size=0.25,
            tick_value=12.50,
            min_quantity=1.0,
            max_quantity=5.0,
            commission_per_contract=2.50
        )
        
        # MES Futures (micro)
        self.symbols["MES"] = SymbolConfig(
            symbol="MES",
            exchange="CME",
            tick_size=0.25,
            tick_value=1.25,
            min_quantity=1.0,
            max_quantity=10.0,
            commission_per_contract=0.85
        )
        
        # NQ Futures (pour corrélation)
        self.symbols["NQ"] = SymbolConfig(
            symbol="NQ",
            exchange="CME",
            tick_size=0.25,
            tick_value=5.00,
            min_quantity=1.0,
            max_quantity=3.0,
            commission_per_contract=2.50
        )
    
    def validate(self) -> bool:
        """Validation complète configuration"""
        try:
            # Validation risk management
            if not self.risk_management.validate():
                return False
            
            # Validation symboles
            for symbol, config in self.symbols.items():
                if config.tick_size <= 0 or config.tick_value <= 0:
                    logger.error(f"Configuration invalide pour {symbol}")
                    return False
            
            # Validation ML config
            if self.ml.max_features > 8:
                logger.error("Max features > 8 non supporté")
                return False
            
            # Validation data config
            if self.data.max_data_latency_ms > 1000:
                logger.warning("Latence data > 1s peut affecter performance")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur validation config: {e}")
            return False
    
    def save_to_file(self, file_path: str):
        """Sauvegarde configuration vers fichier"""
        try:
            config_dict = self.to_dict()
            
            with open(file_path, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)
            
            self.config_file_path = file_path
            logger.info(f"Configuration sauvée: {file_path}")
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde config: {e}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire"""
        return {
            'trading_mode': self.trading_mode.value,
            'config_version': self.config_version,
            'environment': self.environment,
            'symbols': {k: v.__dict__ for k, v in self.symbols.items()},
            'risk_management': self.risk_management.__dict__,
            'features': self.features.__dict__,
            'ml': self.ml.__dict__,
            'data': self.data.__dict__,
            'execution': self.execution.__dict__,
            'performance': self.performance.__dict__,
            'data_directory': self.data_directory,
            'logs_directory': self.logs_directory,
            'models_directory': self.models_directory
        }
    
    def update_risk_level(self, risk_level: RiskLevel):
        """Mise à jour niveau de risque"""
        if risk_level == RiskLevel.CONSERVATIVE:
            self.risk_management.max_position_size = 1
            self.risk_management.max_daily_loss = 500.0
            self.risk_management.max_risk_per_trade = 100.0
            self.features.min_signal_confidence = 0.75
            
        elif risk_level == RiskLevel.MODERATE:
            self.risk_management.max_position_size = 2
            self.risk_management.max_daily_loss = 1000.0
            self.risk_management.max_risk_per_trade = 200.0
            self.features.min_signal_confidence = 0.65
            
        elif risk_level == RiskLevel.AGGRESSIVE:
            self.risk_management.max_position_size = 3
            self.risk_management.max_daily_loss = 2000.0
            self.risk_management.max_risk_per_trade = 400.0
            self.features.min_signal_confidence = 0.60
        
        logger.info(f"Risk level mis à jour: {risk_level.value}")

# === FACTORY FUNCTIONS ===

def create_default_config() -> TradingConfig:
    """Création configuration par défaut"""
    return TradingConfig()

def create_paper_trading_config() -> TradingConfig:
    """Configuration pour paper trading"""
    config = TradingConfig()
    config.trading_mode = TradingMode.PAPER_TRADING
    config.execution.execution_mode = ExecutionMode.FULL_AUTO
    config.risk_management.max_daily_loss = 10000.0  # Virtuel
    return config

def create_live_trading_config() -> TradingConfig:
    """Configuration pour trading live"""
    config = TradingConfig()
    config.trading_mode = TradingMode.LIVE_TRADING
    config.execution.execution_mode = ExecutionMode.SEMI_AUTO
    config.update_risk_level(RiskLevel.CONSERVATIVE)
    return config

def create_backtesting_config() -> TradingConfig:
    """Configuration pour backtesting"""
    config = TradingConfig()
    config.trading_mode = TradingMode.BACKTESTING
    config.data.historical_data_days = 365
    config.performance.real_time_analysis_enabled = False
    return config

def load_config_from_file(file_path: str) -> TradingConfig:
    """Chargement configuration depuis fichier"""
    try:
        with open(file_path, 'r') as f:
            config_dict = json.load(f)
        
        # Reconstruction objet (simplified)
        config = TradingConfig()
        config.trading_mode = TradingMode(config_dict['trading_mode'])
        config.config_version = config_dict['config_version']
        config.environment = config_dict['environment']
        
        # Update fields from dict
        if 'risk_management' in config_dict:
            rm_dict = config_dict['risk_management']
            for key, value in rm_dict.items():
                if hasattr(config.risk_management, key):
                    setattr(config.risk_management, key, value)
        
        config.config_file_path = file_path
        logger.info(f"Configuration chargée: {file_path}")
        
        return config
        
    except Exception as e:
        logger.error(f"Erreur chargement config: {e}")
        raise

# === CONFIGURATION PRESETS ===

def get_prop_firm_config() -> TradingConfig:
    """Configuration optimisée prop firm"""
    config = create_live_trading_config()
    
    # Risk management strict
    config.risk_management.max_daily_loss = 800.0  # 80% of typical $1000 limit
    config.risk_management.daily_profit_target = 400.0
    config.risk_management.max_position_size = 2
    config.risk_management.stop_trading_on_target = True
    
    # Signals conservateurs
    config.features.min_signal_confidence = 0.75
    config.features.min_pattern_strength = 0.7
    
    # Monitoring renforcé
    config.performance.performance_alerts_enabled = True
    config.performance.alert_on_loss_streak = 2
    
    return config

def get_development_config() -> TradingConfig:
    """Configuration pour développement"""
    config = create_paper_trading_config()
    config.environment = "development"
    config.performance.detailed_logging_enabled = True
    config.ml.model_validation_required = False  # Plus rapide en dev
    return config

# === GLOBAL CONFIG INSTANCE ===

_global_config: Optional[TradingConfig] = None

def get_trading_config() -> TradingConfig:
    """Récupération configuration globale"""
    global _global_config
    if _global_config is None:
        _global_config = create_default_config()
    return _global_config

def set_trading_config(config: TradingConfig):
    """Définition configuration globale"""
    global _global_config
    _global_config = config
    logger.info("Configuration globale mise à jour")

def get_risk_config() -> RiskManagementConfig:
    """Raccourci vers risk management config"""
    return get_trading_config().risk_management

def get_feature_config() -> FeatureConfig:
    """Raccourci vers feature config"""
    return get_trading_config().features

# === TESTING ===

def test_trading_config():
    """Test configuration trading"""
    logger.debug("Test trading config...")
    
    # Test config par défaut
    config = create_default_config()
    logger.info("Config par défaut: {config.trading_mode.value}")
    logger.info("Symboles: {list(config.symbols.keys())}")
    logger.info("Max position: {config.risk_management.max_position_size}")
    logger.info("Min confidence: {config.features.min_signal_confidence}")
    
    # Test validation
    is_valid = config.validate()
    logger.info("Validation: {is_valid}")
    
    # Test risk levels
    config.update_risk_level(RiskLevel.CONSERVATIVE)
    logger.info("Conservative risk: max pos = {config.risk_management.max_position_size}")
    
    # Test prop firm config
    prop_config = get_prop_firm_config()
    logger.info("Prop firm: daily loss = {prop_config.risk_management.max_daily_loss}")
    
    # Test serialization
    config_dict = config.to_dict()
    logger.info("Serialization: {len(config_dict)} keys")
    
    logger.info("🎯 Trading config test COMPLETED")
    return True

if __name__ == "__main__":
    test_trading_config()