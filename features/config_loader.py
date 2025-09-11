#!/usr/bin/env python3
"""
🎯 CONFIG LOADER - MIA_IA_SYSTEM
================================

Chargeur de configuration pour les features
- Chargement depuis config/feature_config.json
- Validation des paramètres
- Fallbacks par défaut
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ConfluenceConfig:
    """Configuration pour la confluence"""
    tolerance_ticks: float = 3.0
    quality_thresholds: Dict[str, float] = None
    leadership_gates: Dict[str, float] = None
    
    def __post_init__(self):
        if self.quality_thresholds is None:
            self.quality_thresholds = {
                "high": 0.8,
                "medium": 0.6,
                "low": 0.4
            }
        if self.leadership_gates is None:
            self.leadership_gates = {
                "correlation_min": 0.7,
                "volume_ratio_min": 0.3,
                "volatility_max": 0.02
            }

@dataclass
class MenthorQConfig:
    """Configuration pour MenthorQ"""
    gamma_proximity_ticks: float = 10.0
    blind_spot_proximity_ticks: float = 5.0
    swing_level_proximity_ticks: float = 15.0
    data_ttl_seconds: int = 300
    ema_alpha: float = 0.3
    min_levels_required: int = 3

@dataclass
class OrderBookConfig:
    """Configuration pour Order Book"""
    max_depth: int = 10
    decay_factor: float = 0.85
    min_depth_required: int = 3
    neutral_score: float = 0.5

@dataclass
class VolumeProfileConfig:
    """Configuration pour Volume Profile"""
    min_volume_threshold: int = 100
    proximity_ticks: float = 5.0
    imbalance_threshold: float = 0.1

@dataclass
class VWAPConfig:
    """Configuration pour VWAP"""
    bands_count: int = 4
    deviation_multipliers: list = None
    session_reset: bool = True
    
    def __post_init__(self):
        if self.deviation_multipliers is None:
            self.deviation_multipliers = [0.5, 1.0, 1.5, 2.0]

@dataclass
class VIXConfig:
    """Configuration pour VIX"""
    low_threshold: float = 15.0
    high_threshold: float = 30.0
    extreme_threshold: float = 40.0

@dataclass
class NBCVConfig:
    """Configuration pour NBCV"""
    delta_threshold: int = 1000
    volume_imbalance_threshold: float = 0.1
    trade_intensity_threshold: float = 0.5

@dataclass
class FeatureWeights:
    """Pondérations des features"""
    mtf_confluence_score: float = 0.25
    smart_money_strength: float = 0.20
    order_book_imbalance: float = 0.15
    volume_profile_imbalance: float = 0.15
    vwap_deviation: float = 0.10
    vix_regime: float = 0.10
    nbcv_orderflow: float = 0.05
    
    def validate(self) -> bool:
        """Valide que la somme des poids = 1.0"""
        total = sum([
            self.mtf_confluence_score,
            self.smart_money_strength,
            self.order_book_imbalance,
            self.volume_profile_imbalance,
            self.vwap_deviation,
            self.vix_regime,
            self.nbcv_orderflow
        ])
        return abs(total - 1.0) < 0.001

@dataclass
class Thresholds:
    """Seuils de décision"""
    premium: float = 0.8
    strong: float = 0.6
    weak: float = 0.4
    no_trade: float = 0.2

@dataclass
class DataSources:
    """Configuration des sources de données"""
    unified_file_path: str = "D:\\MIA_IA_system"
    max_lines_per_read: int = 1000
    cache_ttl_seconds: int = 60

@dataclass
class FeatureConfig:
    """Configuration complète des features"""
    confluence: ConfluenceConfig
    menthorq: MenthorQConfig
    order_book: OrderBookConfig
    volume_profile: VolumeProfileConfig
    vwap: VWAPConfig
    vix: VIXConfig
    nbcv: NBCVConfig
    feature_weights: FeatureWeights
    thresholds: Thresholds
    data_sources: DataSources

class ConfigLoader:
    """Chargeur de configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Chemin par défaut
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "feature_config.json"
        
        self.config_path = Path(config_path)
        self._config: Optional[FeatureConfig] = None
    
    def load_config(self) -> FeatureConfig:
        """Charge la configuration depuis le fichier JSON"""
        if self._config is not None:
            return self._config
        
        try:
            if not self.config_path.exists():
                logger.warning(f"⚠️ Fichier config non trouvé: {self.config_path}")
                logger.info("🔄 Utilisation de la configuration par défaut")
                self._config = self._create_default_config()
                return self._config
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            logger.info(f"✅ Configuration chargée depuis {self.config_path}")
            self._config = self._parse_config(config_data)
            
            # Valider la configuration
            if not self._config.feature_weights.validate():
                logger.warning("⚠️ Somme des poids features ≠ 1.0 - redistribution automatique")
                self._redistribute_weights()
            
            return self._config
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement config: {e}")
            logger.info("🔄 Utilisation de la configuration par défaut")
            self._config = self._create_default_config()
            return self._config
    
    def _parse_config(self, config_data: Dict[str, Any]) -> FeatureConfig:
        """Parse les données JSON en objets de configuration"""
        
        # Confluence
        confluence_data = config_data.get("confluence", {})
        confluence = ConfluenceConfig(
            tolerance_ticks=confluence_data.get("tolerance_ticks", 3.0),
            quality_thresholds=confluence_data.get("quality_thresholds", {}),
            leadership_gates=confluence_data.get("leadership_gates", {})
        )
        
        # MenthorQ
        menthorq_data = config_data.get("menthorq", {})
        menthorq = MenthorQConfig(
            gamma_proximity_ticks=menthorq_data.get("gamma_proximity_ticks", 10.0),
            blind_spot_proximity_ticks=menthorq_data.get("blind_spot_proximity_ticks", 5.0),
            swing_level_proximity_ticks=menthorq_data.get("swing_level_proximity_ticks", 15.0),
            data_ttl_seconds=menthorq_data.get("data_ttl_seconds", 300),
            ema_alpha=menthorq_data.get("ema_alpha", 0.3),
            min_levels_required=menthorq_data.get("min_levels_required", 3)
        )
        
        # Order Book
        order_book_data = config_data.get("order_book", {})
        order_book = OrderBookConfig(
            max_depth=order_book_data.get("max_depth", 10),
            decay_factor=order_book_data.get("decay_factor", 0.85),
            min_depth_required=order_book_data.get("min_depth_required", 3),
            neutral_score=order_book_data.get("neutral_score", 0.5)
        )
        
        # Volume Profile
        vp_data = config_data.get("volume_profile", {})
        volume_profile = VolumeProfileConfig(
            min_volume_threshold=vp_data.get("min_volume_threshold", 100),
            proximity_ticks=vp_data.get("proximity_ticks", 5.0),
            imbalance_threshold=vp_data.get("imbalance_threshold", 0.1)
        )
        
        # VWAP
        vwap_data = config_data.get("vwap", {})
        vwap = VWAPConfig(
            bands_count=vwap_data.get("bands_count", 4),
            deviation_multipliers=vwap_data.get("deviation_multipliers", [0.5, 1.0, 1.5, 2.0]),
            session_reset=vwap_data.get("session_reset", True)
        )
        
        # VIX
        vix_data = config_data.get("vix", {})
        vix = VIXConfig(
            low_threshold=vix_data.get("low_threshold", 15.0),
            high_threshold=vix_data.get("high_threshold", 30.0),
            extreme_threshold=vix_data.get("extreme_threshold", 40.0)
        )
        
        # NBCV
        nbcv_data = config_data.get("nbcv", {})
        nbcv = NBCVConfig(
            delta_threshold=nbcv_data.get("delta_threshold", 1000),
            volume_imbalance_threshold=nbcv_data.get("volume_imbalance_threshold", 0.1),
            trade_intensity_threshold=nbcv_data.get("trade_intensity_threshold", 0.5)
        )
        
        # Feature Weights
        weights_data = config_data.get("feature_weights", {})
        feature_weights = FeatureWeights(
            mtf_confluence_score=weights_data.get("mtf_confluence_score", 0.25),
            smart_money_strength=weights_data.get("smart_money_strength", 0.20),
            order_book_imbalance=weights_data.get("order_book_imbalance", 0.15),
            volume_profile_imbalance=weights_data.get("volume_profile_imbalance", 0.15),
            vwap_deviation=weights_data.get("vwap_deviation", 0.10),
            vix_regime=weights_data.get("vix_regime", 0.10),
            nbcv_orderflow=weights_data.get("nbcv_orderflow", 0.05)
        )
        
        # Thresholds
        thresholds_data = config_data.get("thresholds", {})
        thresholds = Thresholds(
            premium=thresholds_data.get("premium", 0.8),
            strong=thresholds_data.get("strong", 0.6),
            weak=thresholds_data.get("weak", 0.4),
            no_trade=thresholds_data.get("no_trade", 0.2)
        )
        
        # Data Sources
        data_sources_data = config_data.get("data_sources", {})
        data_sources = DataSources(
            unified_file_path=data_sources_data.get("unified_file_path", "D:\\MIA_IA_system"),
            max_lines_per_read=data_sources_data.get("max_lines_per_read", 1000),
            cache_ttl_seconds=data_sources_data.get("cache_ttl_seconds", 60)
        )
        
        return FeatureConfig(
            confluence=confluence,
            menthorq=menthorq,
            order_book=order_book,
            volume_profile=volume_profile,
            vwap=vwap,
            vix=vix,
            nbcv=nbcv,
            feature_weights=feature_weights,
            thresholds=thresholds,
            data_sources=data_sources
        )
    
    def _create_default_config(self) -> FeatureConfig:
        """Crée une configuration par défaut"""
        return FeatureConfig(
            confluence=ConfluenceConfig(),
            menthorq=MenthorQConfig(),
            order_book=OrderBookConfig(),
            volume_profile=VolumeProfileConfig(),
            vwap=VWAPConfig(),
            vix=VIXConfig(),
            nbcv=NBCVConfig(),
            feature_weights=FeatureWeights(),
            thresholds=Thresholds(),
            data_sources=DataSources()
        )
    
    def _redistribute_weights(self):
        """Redistribue les poids pour que la somme = 1.0"""
        weights = self._config.feature_weights
        total = sum([
            weights.mtf_confluence_score,
            weights.smart_money_strength,
            weights.order_book_imbalance,
            weights.volume_profile_imbalance,
            weights.vwap_deviation,
            weights.vix_regime,
            weights.nbcv_orderflow
        ])
        
        if total > 0:
            weights.mtf_confluence_score /= total
            weights.smart_money_strength /= total
            weights.order_book_imbalance /= total
            weights.volume_profile_imbalance /= total
            weights.vwap_deviation /= total
            weights.vix_regime /= total
            weights.nbcv_orderflow /= total
            
            logger.info("✅ Poids redistribués pour somme = 1.0")

# === INSTANCE GLOBALE ===
config_loader = ConfigLoader()

def get_feature_config() -> FeatureConfig:
    """Fonction utilitaire pour récupérer la configuration"""
    return config_loader.load_config()

if __name__ == "__main__":
    # Test du chargeur de configuration
    config = get_feature_config()
    
    print("🎯 Configuration des Features chargée:")
    print(f"   Confluence tolerance: {config.confluence.tolerance_ticks} ticks")
    print(f"   MenthorQ gamma proximity: {config.menthorq.gamma_proximity_ticks} ticks")
    print(f"   Order Book max depth: {config.order_book.max_depth}")
    print(f"   Feature weights valid: {config.feature_weights.validate()}")
    print(f"   Data path: {config.data_sources.unified_file_path}")



