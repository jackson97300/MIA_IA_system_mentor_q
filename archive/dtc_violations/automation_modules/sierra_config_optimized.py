#!/usr/bin/env python3
"""
⚙️ SIERRA CONFIG OPTIMIZED - DTC & LEVEL 2
Configuration optimisée pour Sierra Chart avec DTC Protocol et Level 2
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger

logger = get_logger(__name__)

class LatencyProfile(Enum):
    """Profils de latence optimisés"""
    ULTRA_LOW = "ultra_low"      # <5ms - Scalping HFT
    LOW = "low"                  # <20ms - Day trading
    STANDARD = "standard"        # <50ms - Swing trading
    RELAXED = "relaxed"          # <100ms - Position trading

class DataQuality(Enum):
    """Niveaux de qualité des données"""
    PRODUCTION = "production"    # Qualité maximale
    DEVELOPMENT = "development"  # Tests et développement  
    BUDGET = "budget"           # Coût minimal

@dataclass
class DTCProtocolConfig:
    """Configuration DTC Protocol optimisée"""
    
    # Connexion de base
    host: str = "127.0.0.1"
    port: int = 11099                    # ES par défaut
    username: str = ""
    password: str = ""
    client_name: str = "MIA_IA_DTC_V2"
    
    # Protocole
    protocol_version: int = 8
    heartbeat_interval: int = 20         # 20s optimal pour performance
    connection_timeout: float = 10.0     # 10s timeout
    reconnect_attempts: int = 5
    reconnect_delay: float = 2.0
    
    # Performance selon profil
    latency_profile: LatencyProfile = LatencyProfile.LOW
    
    # Buffers et optimisation
    send_buffer_size: int = 65536        # 64KB
    recv_buffer_size: int = 131072       # 128KB
    message_queue_size: int = 1000
    enable_compression: bool = False     # Désactivé pour latence
    
    # Logging et monitoring
    log_level: str = "INFO"
    enable_message_logging: bool = False  # Seulement si debug
    stats_interval: int = 60             # Stats toutes les 60s

@dataclass
class Level2Config:
    """Configuration Level 2 Order Book optimisée"""
    
    # Profondeur
    depth_levels: int = 10               # 10 niveaux standard
    max_depth_levels: int = 20           # Maximum supporté
    
    # Performance
    update_frequency_ms: int = 100       # 100ms entre updates
    batch_updates: bool = True           # Batcher les updates
    max_batch_size: int = 50
    
    # Filtrage et qualité
    min_order_size: int = 1              # Taille minimum ordre
    spread_filter_enabled: bool = True    # Filtrer spreads anormaux
    max_spread_ticks: float = 10.0       # Max 10 ticks de spread
    
    # Cache et historique
    cache_enabled: bool = True
    cache_size: int = 1000               # 1000 snapshots Level 2
    historical_depth: int = 100          # 100 updates gardés
    
    # Calculs avancés
    calculate_imbalance: bool = True      # Calcul ratio imbalance
    calculate_flow: bool = True           # Calcul order flow
    calculate_pressure: bool = True       # Calcul pression achat/vente

@dataclass
class OrderflowConfig:
    """Configuration Orderflow avancée"""
    
    # Paramètres de base
    lookback_periods: int = 50           # 50 ticks d'historique
    volume_threshold: int = 100          # Volume minimum pour analyse
    
    # Détection Smart Money
    block_trade_threshold: int = 300     # ✅ Validé par tests
    institutional_threshold: int = 800   # ✅ Validé par tests  
    iceberg_threshold: int = 150         # ✅ Validé par tests
    
    # Volume Profile
    price_bucket_size: float = 0.25      # Taille bucket (1 tick ES)
    min_volume_for_analysis: int = 50
    max_analysis_levels: int = 100
    
    # Cumulative Delta
    delta_calculation_method: str = "aggressive"  # "aggressive" ou "volume_weighted"
    delta_smoothing: bool = True
    delta_smoothing_periods: int = 10
    
    # Performance
    analysis_interval_ms: int = 500      # Analyse toutes les 500ms
    enable_real_time: bool = True
    max_history_size: int = 1000

@dataclass 
class SymbolConfig:
    """Configuration par symbole"""
    
    symbol: str
    exchange: str = "CME"
    tick_size: float = 0.25
    tick_value: float = 12.50
    margin_requirement: float = 5000.0
    commission: float = 2.50
    
    # Spécific au symbole
    level2_enabled: bool = True
    orderflow_enabled: bool = True
    smart_money_enabled: bool = True
    
    # Seuils spécifiques
    min_trade_size: int = 1
    max_trade_size: int = 1000
    volume_multiplier: float = 1.0

@dataclass
class SierraOptimizedConfigV2:
    """Configuration Sierra Chart complète optimisée"""
    
    # Configurations principales
    dtc_config: DTCProtocolConfig = field(default_factory=DTCProtocolConfig)
    level2_config: Level2Config = field(default_factory=Level2Config)
    orderflow_config: OrderflowConfig = field(default_factory=OrderflowConfig)
    
    # Configuration DTC Protocol manquante
    dtc_protocol: Dict[str, Any] = field(default_factory=lambda: {
        "encoding": "JSON_COMPACT",
        "heartbeat_sec": 5,
        "host": "127.0.0.1",
        "port": 11099
    })
    
    # Qualité et profil
    data_quality: DataQuality = DataQuality.PRODUCTION
    latency_profile: LatencyProfile = LatencyProfile.LOW
    
    # Symboles configurés
    symbols: Dict[str, SymbolConfig] = field(default_factory=lambda: {
        'ES': SymbolConfig(
            symbol='ES',
            exchange='CME',
            tick_size=0.25,
            tick_value=12.50,
            margin_requirement=5000.0,
            commission=2.50
        ),
        'NQ': SymbolConfig(
            symbol='NQ', 
            exchange='CME',
            tick_size=0.25,
            tick_value=5.00,
            margin_requirement=8000.0,
            commission=2.50
        )
    })
    
    # Ports et instances
    instance_ports: Dict[str, int] = field(default_factory=lambda: {
        'ES': 11099,
        'NQ': 11100
    })
    
    # Performance globale
    performance_targets: Dict[str, float] = field(default_factory=lambda: {
        'max_latency_ms': 20.0,           # Max 20ms
        'target_latency_ms': 5.0,         # Target 5ms
        'data_quality_min': 0.95,         # 95% qualité minimum
        'uptime_target': 0.999,           # 99.9% uptime
        'throughput_tps': 1000            # 1000 ticks/seconde
    })
    
    # Coûts réels optimisés
    monthly_costs: Dict[str, float] = field(default_factory=lambda: {
        'pack_12': 164.0,                 # ✅ Pack 12 Sierra Chart
        'denali_cme': 13.0,              # ✅ CME Market Depth (réel)
        'cboe_vix': 6.0,                 # ✅ VIX officiel (optionnel)
        'total_sierra': 183.0,           # ✅ Total réaliste
        'polygon_options': 0.0,          # ✅ Plan gratuit différé
        'total_system': 183.0            # ✅ Total système minimal
    })
    
    # Monitoring et alertes
    monitoring: Dict[str, Any] = field(default_factory=lambda: {
        'health_check_interval': 30,      # 30s
        'stats_collection': True,
        'performance_alerts': True,
        'latency_alerts_threshold': 50.0, # Alert si >50ms
        'quality_alerts_threshold': 0.90, # Alert si <90%
        'enable_dashboard': True
    })

def create_scalping_config() -> SierraOptimizedConfigV2:
    """Configuration optimisée pour scalping (ultra-low latency)"""
    config = SierraOptimizedConfigV2()
    
    # Ultra-low latency
    config.latency_profile = LatencyProfile.ULTRA_LOW
    config.dtc_config.latency_profile = LatencyProfile.ULTRA_LOW
    config.dtc_config.heartbeat_interval = 10  # Plus fréquent
    config.dtc_config.connection_timeout = 5.0
    
    # Level 2 ultra-rapide
    config.level2_config.update_frequency_ms = 50  # 50ms
    config.level2_config.batch_updates = False     # Pas de batch
    
    # Orderflow temps réel
    config.orderflow_config.analysis_interval_ms = 250  # 250ms
    config.orderflow_config.lookback_periods = 25       # Moins d'historique
    
    # Performance targets
    config.performance_targets['max_latency_ms'] = 5.0
    config.performance_targets['target_latency_ms'] = 2.0
    
    logger.info("🚀 Configuration Scalping Ultra-Low Latency créée")
    return config

def create_development_config() -> SierraOptimizedConfigV2:
    """Configuration pour développement et tests"""
    config = SierraOptimizedConfigV2()
    
    # Développement
    config.data_quality = DataQuality.DEVELOPMENT
    config.latency_profile = LatencyProfile.STANDARD
    
    # Logging étendu
    config.dtc_config.log_level = "DEBUG"
    config.dtc_config.enable_message_logging = True
    
    # Monitoring détaillé
    config.monitoring['stats_collection'] = True
    config.monitoring['health_check_interval'] = 10
    
    # Coûts réduits
    config.monthly_costs['cboe_vix'] = 0.0       # Pas de VIX en dev
    config.monthly_costs['total_sierra'] = 177.0
    config.monthly_costs['total_system'] = 177.0
    
    logger.info("🔧 Configuration Développement créée")
    return config

def create_budget_config() -> SierraOptimizedConfigV2:
    """Configuration budget minimal"""
    config = SierraOptimizedConfigV2()
    
    # Budget minimal
    config.data_quality = DataQuality.BUDGET
    config.latency_profile = LatencyProfile.RELAXED
    
    # Réductions performance
    config.level2_config.depth_levels = 5       # 5 niveaux seulement
    config.level2_config.update_frequency_ms = 500  # 500ms
    
    # Orderflow simplifié
    config.orderflow_config.smart_money_enabled = False  # Désactivé
    config.orderflow_config.analysis_interval_ms = 1000  # 1s
    
    # Coûts minimum
    config.monthly_costs['denali_cme'] = 13.0    # Minimum requis
    config.monthly_costs['cboe_vix'] = 0.0       # Pas de VIX
    config.monthly_costs['total_sierra'] = 177.0
    config.monthly_costs['total_system'] = 177.0
    
    logger.info("💰 Configuration Budget créée")
    return config

def get_config_for_profile(profile: str) -> SierraOptimizedConfigV2:
    """Factory pour récupérer config selon profil"""
    
    profiles = {
        'scalping': create_scalping_config,
        'development': create_development_config,
        'budget': create_budget_config,
        'production': SierraOptimizedConfigV2  # Défaut
    }
    
    config_factory = profiles.get(profile, SierraOptimizedConfigV2)
    
    if callable(config_factory):
        return config_factory()
    else:
        return config_factory()

def validate_config(config: SierraOptimizedConfigV2) -> List[str]:
    """Validation de configuration"""
    warnings = []
    
    # Validation latence
    if config.performance_targets['max_latency_ms'] < 1.0:
        warnings.append("⚠️ Latency target <1ms très ambitieux")
    
    # Validation Level 2
    if config.level2_config.depth_levels > 20:
        warnings.append("⚠️ Depth levels >20 peut impacter performance")
    
    # Validation coûts
    if config.monthly_costs['total_system'] > 300:
        warnings.append("⚠️ Coûts >$300/mois élevés")
    
    # Validation Smart Money
    if config.orderflow_config.block_trade_threshold < 100:
        warnings.append("⚠️ Block trade threshold <100 peut générer trop de faux positifs")
    
    return warnings

# Factory exports
__all__ = [
    'SierraOptimizedConfigV2',
    'DTCProtocolConfig', 
    'Level2Config',
    'OrderflowConfig',
    'SymbolConfig',
    'LatencyProfile',
    'DataQuality',
    'create_scalping_config',
    'create_development_config', 
    'create_budget_config',
    'get_config_for_profile',
    'validate_config'
]


