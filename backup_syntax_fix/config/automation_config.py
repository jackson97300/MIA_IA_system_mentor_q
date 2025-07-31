"""
MIA_IA_SYSTEM - Automation Configuration
Configuration centralisée pour l'automation de trading
Version: Production Ready

Ce module gère toute la configuration de l'automation :
- Modes de trading (data collection, paper, live)
- Paramètres Battle Navale
- Seuils et limites
- Configuration ML progressive
- Monitoring et alertes
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import json
import logging
from datetime import time

logger = logging.getLogger(__name__)

# === ENUMS ===

class AutomationMode(Enum):
    """Modes d'automation disponibles"""
    DATA_COLLECTION = "data_collection"
    PAPER_TRADING = "paper_trading"
    LIVE_TRADING = "live_trading"
    BACKTESTING = "backtesting"
    SIMULATION = "simulation"

class TradingSession(Enum):
    """Sessions de trading"""
    ASIAN = "asian"
    LONDON = "london"
    NY_MORNING = "ny_morning"
    NY_AFTERNOON = "ny_afternoon"
    REGULAR = "regular"
    EXTENDED = "extended"

class SignalMode(Enum):
    """Mode de génération des signaux"""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"

# === CONFIGURATION CLASSES ===

@dataclass
class AutomationTradingConfig:
    """Configuration trading pour automation"""
    # Mode général
    automation_mode: AutomationMode = AutomationMode.PAPER_TRADING
    trading_session: TradingSession = TradingSession.REGULAR
    
    # Seuils Battle Navale
    battle_navale_min_confidence: float = 0.65
    battle_navale_max_confidence: float = 1.0
    enable_confluence_validation: bool = True
    min_confluence_score: float = 0.50
    
    # Position management
    max_positions_concurrent: int = 1
    position_size_base: float = 1.0
    position_size_max: float = 2.0
    
    # Timing
    analysis_frequency_ms: int = 1000  # Analyse toutes les secondes
    max_analysis_time_ms: float = 500.0  # Max 500ms par analyse
    order_timeout_seconds: int = 30
    
    # Filtres
    enable_regime_filtering: bool = True
    enable_session_filtering: bool = True
    enable_volatility_filtering: bool = True

@dataclass
class AutomationRiskConfig:
    """Configuration risk pour automation"""
    # Limites quotidiennes
    daily_loss_limit: float = 1000.0
    daily_profit_target: float = 500.0
    max_daily_trades: int = 20
    stop_on_daily_target: bool = False
    
    # Limites par trade
    stop_loss_ticks: int = 12
    take_profit_ticks: int = 24
    max_risk_per_trade: float = 200.0
    
    # Protection
    max_consecutive_losses: int = 3
    pause_after_consecutive_losses: bool = True
    pause_duration_minutes: int = 30
    
    # Kelly Criterion
    use_kelly_sizing: bool = True
    kelly_fraction: float = 0.25
    kelly_lookback_trades: int = 50

@dataclass
class AutomationMonitoringConfig:
    """Configuration monitoring pour automation"""
    # Monitoring général
    enable_monitoring: bool = True
    monitoring_interval_seconds: int = 5
    
    # Métriques
    track_execution_latency: bool = True
    track_signal_quality: bool = True
    track_performance_metrics: bool = True
    
    # Alertes
    enable_alerts: bool = True
    alert_on_error: bool = True
    alert_on_big_win: bool = True
    alert_on_big_loss: bool = True
    big_win_threshold: float = 200.0
    big_loss_threshold: float = 100.0
    
    # Logging
    log_all_signals: bool = True
    log_rejected_signals: bool = True
    log_execution_details: bool = True
    
    # Performance tracking
    performance_window_trades: int = 100
    performance_update_frequency: int = 10

@dataclass
class AutomationDataConfig:
    """Configuration data collection pour automation"""
    # Snapshots
    enable_snapshots: bool = True
    snapshot_all_signals: bool = True
    snapshot_rejected_trades: bool = False
    enhanced_ml_features: bool = True
    
    # Stockage
    data_retention_days: int = 90
    compress_old_data: bool = True
    auto_backup_enabled: bool = True
    backup_frequency_hours: int = 24
    
    # Export
    auto_export_daily: bool = True
    export_format: str = "parquet"
    export_path: str = "data/exports"

@dataclass
class AutomationMLConfig:
    """Configuration ML pour automation"""
    # ML général
    enable_ml_predictions: bool = False
    ml_confidence_threshold: float = 0.65
    
    # Training
    auto_retrain_enabled: bool = False
    retrain_frequency_trades: int = 500
    min_training_samples: int = 1000
    
    # Model
    model_type: str = "linear"  # linear, xgboost, ensemble
    feature_selection_enabled: bool = True
    max_features: int = 8
    
    # Validation
    validation_split: float = 0.2
    cross_validation_folds: int = 5
    min_model_accuracy: float = 0.60

@dataclass
class AutomationConfig:
    """Configuration complète automation"""
    # Sous-configurations
    trading: AutomationTradingConfig = field(default_factory=AutomationTradingConfig)
    risk: AutomationRiskConfig = field(default_factory=AutomationRiskConfig)
    monitoring: AutomationMonitoringConfig = field(default_factory=AutomationMonitoringConfig)
    data: AutomationDataConfig = field(default_factory=AutomationDataConfig)
    ml: AutomationMLConfig = field(default_factory=AutomationMLConfig)
    
    # Metadata
    config_name: str = "default"
    version: str = "1.0.0"
    created_at: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return asdict(self)
    
    def save_to_file(self, filepath: str):
        """Sauvegarde configuration dans fichier JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'AutomationConfig':
        """Charge configuration depuis fichier JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutomationConfig':
        """Crée instance depuis dictionnaire"""
        config = cls()
        
        # Trading config
        if 'trading' in data:
            for key, value in data['trading'].items():
                if hasattr(config.trading, key):
                    if key == 'automation_mode':
                        setattr(config.trading, key, AutomationMode(value))
                    elif key == 'trading_session':
                        setattr(config.trading, key, TradingSession(value))
                    else:
                        setattr(config.trading, key, value)
        
        # Risk config
        if 'risk' in data:
            for key, value in data['risk'].items():
                if hasattr(config.risk, key):
                    setattr(config.risk, key, value)
        
        # Monitoring config
        if 'monitoring' in data:
            for key, value in data['monitoring'].items():
                if hasattr(config.monitoring, key):
                    setattr(config.monitoring, key, value)
        
        # Data config
        if 'data' in data:
            for key, value in data['data'].items():
                if hasattr(config.data, key):
                    setattr(config.data, key, value)
        
        # ML config
        if 'ml' in data:
            for key, value in data['ml'].items():
                if hasattr(config.ml, key):
                    setattr(config.ml, key, value)
        
        # Metadata
        config.config_name = data.get('config_name', 'default')
        config.version = data.get('version', '1.0.0')
        config.created_at = data.get('created_at', '')
        
        return config

# === FACTORY FUNCTIONS ===

def create_data_collection_config() -> AutomationConfig:
    """Configuration optimisée pour collecte de données"""
    config = AutomationConfig()
    config.config_name = "data_collection"
    
    # Trading - Très permissif
    config.trading.automation_mode = AutomationMode.DATA_COLLECTION
    config.trading.battle_navale_min_confidence = 0.35  # Très bas
    config.trading.min_confluence_score = 0.35  # Très bas
    config.trading.max_positions_concurrent = 3
    
    # Risk - Limites hautes
    config.risk.daily_loss_limit = 5000.0
    config.risk.max_daily_trades = 100
    config.risk.stop_loss_ticks = 20  # Large
    config.risk.use_kelly_sizing = False
    
    # Data - Tout capturer
    config.data.snapshot_all_signals = True
    config.data.snapshot_rejected_trades = True
    config.data.enhanced_ml_features = True
    
    # Monitoring - Complet
    config.monitoring.log_all_signals = True
    config.monitoring.log_rejected_signals = True
    
    return config

def create_paper_trading_config() -> AutomationConfig:
    """Configuration pour paper trading"""
    config = AutomationConfig()
    config.config_name = "paper_trading"
    
    # Trading - Standard
    config.trading.automation_mode = AutomationMode.PAPER_TRADING
    config.trading.battle_navale_min_confidence = 0.65
    config.trading.min_confluence_score = 0.50
    config.trading.max_positions_concurrent = 2
    
    # Risk - Modéré
    config.risk.daily_loss_limit = 1000.0
    config.risk.max_daily_trades = 20
    config.risk.use_kelly_sizing = True
    config.risk.kelly_fraction = 0.25
    
    return config

def create_live_trading_config() -> AutomationConfig:
    """Configuration pour live trading"""
    config = AutomationConfig()
    config.config_name = "live_trading"
    
    # Trading - Strict
    config.trading.automation_mode = AutomationMode.LIVE_TRADING
    config.trading.battle_navale_min_confidence = 0.75
    config.trading.min_confluence_score = 0.65
    config.trading.max_positions_concurrent = 1
    
    # Risk - Conservateur
    config.risk.daily_loss_limit = 500.0
    config.risk.max_daily_trades = 10
    config.risk.stop_loss_ticks = 8
    config.risk.use_kelly_sizing = True
    config.risk.kelly_fraction = 0.15
    
    # Monitoring - Maximum
    config.monitoring.enable_alerts = True
    config.monitoring.alert_on_error = True
    
    return config

def create_conservative_config() -> AutomationConfig:
    """Configuration ultra-conservative pour débuter"""
    config = create_live_trading_config()
    config.config_name = "conservative"
    
    # Encore plus strict
    config.trading.battle_navale_min_confidence = 0.80
    config.trading.min_confluence_score = 0.70
    config.risk.daily_loss_limit = 300.0
    config.risk.max_daily_trades = 5
    
    return config

# === HELPERS ===

def get_automation_config(mode: str = "paper") -> AutomationConfig:
    """Récupère config selon le mode"""
    mode = mode.lower()
    
    if mode in ["data", "data_collection"]:
        return create_data_collection_config()
    elif mode == "paper":
        return create_paper_trading_config()
    elif mode == "live":
        return create_live_trading_config()
    elif mode == "conservative":
        return create_conservative_config()
    else:
        logger.warning(f"Mode inconnu: {mode}, utilisation paper trading")
        return create_paper_trading_config()

def validate_config(config: AutomationConfig) -> bool:
    """Valide la cohérence de la configuration"""
    try:
        # Vérifications de base
        assert 0 < config.trading.battle_navale_min_confidence <= 1
        assert 0 < config.trading.min_confluence_score <= 1
        assert config.risk.daily_loss_limit > 0
        assert config.risk.stop_loss_ticks > 0
        assert config.risk.take_profit_ticks > config.risk.stop_loss_ticks
        
        # Cohérence mode/paramètres
        if config.trading.automation_mode == AutomationMode.LIVE_TRADING:
            assert config.risk.daily_loss_limit <= 1000  # Safety
            assert config.trading.max_positions_concurrent <= 2
        
        return True
        
    except AssertionError as e:
        logger.error(f"Configuration invalide: {e}")
        return False

# === EXPORTS ===

__all__ = [
    # Classes
    'AutomationConfig',
    'AutomationTradingConfig',
    'AutomationRiskConfig',
    'AutomationMonitoringConfig',
    'AutomationDataConfig',
    'AutomationMLConfig',
    
    # Enums
    'AutomationMode',
    'TradingSession',
    'SignalMode',
    
    # Factory functions
    'create_data_collection_config',
    'create_paper_trading_config',
    'create_live_trading_config',
    'create_conservative_config',
    'get_automation_config',
    
    # Helpers
    'validate_config'
]


@dataclass
class DataCollectionConfig:
    """Configuration collecte données"""
    enabled: bool = True
    symbols: List[str] = field(default_factory=lambda: ["ES", "NQ"])
    save_snapshots: bool = True
    snapshot_interval: int = 60
    max_snapshots_per_day: int = 1000
    compress_old_data: bool = True
    retention_days: int = 30

