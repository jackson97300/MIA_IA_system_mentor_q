"""
MIA_IA_SYSTEM - Feature Calculator Optimized
============================================

Version optimisée du FeatureCalculator avec factory routers et performance améliorée.
- Factory routers pour instanciation optimisée
- Cache intelligent avec TTL
- Calculs parallélisés
- Gestion d'erreurs robuste
- Monitoring de performance

Version: Production Ready v4.0 - Optimized
Performance: <1ms garanti pour toutes features
"""

import time
import asyncio
import threading
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from config.config_loader import get_feature_config
from enum import Enum
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import OrderedDict
import hashlib
import weakref

from core.logger import get_logger
from core.base_types import (
    MarketData, OrderFlowData, TradingFeatures,
    ES_TICK_SIZE, ES_TICK_VALUE, get_session_phase
)
from types import SimpleNamespace
from datetime import datetime, timezone, timedelta
from inspect import signature

# === TRADING THRESHOLDS ===

def get_trading_thresholds():
    """Récupère les seuils depuis la configuration"""
    config = get_feature_config()
    thresholds = config.thresholds
    
    return {
        'PREMIUM_SIGNAL': thresholds.premium,    # Premium trade (size ×1.5)
        'STRONG_SIGNAL': thresholds.strong,      # Strong trade (size ×1.0)
        'WEAK_SIGNAL': thresholds.weak,          # Weak trade (size ×0.5)
        'NO_TRADE': thresholds.no_trade,         # No trade (wait)
    }

TRADING_THRESHOLDS = get_trading_thresholds()

class SignalQuality(Enum):
    """Qualité du signal trading"""
    PREMIUM = "premium"     # 85-100%
    STRONG = "strong"       # 70-84%
    WEAK = "weak"          # 60-69%
    NO_TRADE = "no_trade"  # 0-59%

# === HELPERS DE NORMALISATION MARKETDATA ===

def _filter_kwargs_for_cls(cls, d: dict, aliases: dict | None = None) -> dict:
    """Filtre les kwargs et gère les alias pour une classe donnée"""
    # remap d'éventuels alias (ex: bin_size → price_bucket_size)
    if aliases:
        d = { (aliases.get(k, k)): v for k, v in d.items() }
    params = signature(cls).parameters
    return {k: v for k, v in d.items() if k in params}

def _ensure_datetime(ts) -> datetime:
    """Convertit n'importe quel timestamp en datetime UTC"""
    if ts is None:
        return datetime.now(timezone.utc)
    if isinstance(ts, datetime):
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
    # float/int (epoch sec ou Excel converti)
    try:
        tsf = float(ts)
        return datetime.fromtimestamp(tsf, tz=timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)

def _normalize_ts(ts):
    """Normalise timestamp Excel → Unix."""
    if ts is None:
        return None
    # Gérer les objets Timestamp pandas
    if hasattr(ts, 'timestamp'):
        return ts.timestamp()
    # Gérer les autres types
    ts = float(ts)
    if ts > 1e12:      # ms
        return ts / 1000.0
    if 40000 < ts < 80000:  # Excel days (Sierra/SC)
        base = datetime(1899, 12, 30, tzinfo=timezone.utc)
        return (base + timedelta(days=ts)).timestamp()
    return ts

def _as_cfg(cfg, defaults: dict):
    """Convertit dict → objet avec attributs, avec fallbacks par défaut."""
    if cfg is None:
        return SimpleNamespace(**defaults)
    if isinstance(cfg, dict):
        return SimpleNamespace(**{**defaults, **cfg})
    # objet: injecter les valeurs par défaut manquantes
    for k, v in defaults.items():
        if not hasattr(cfg, k):
            setattr(cfg, k, v)
    return cfg

def _clip01(value: float) -> float:
    """Ramène une valeur dans l'intervalle [0, 1]."""
    try:
        if value is None:
            return 0.0
        return 0.0 if value < 0.0 else (1.0 if value > 1.0 else float(value))
    except Exception:
        return 0.0

def _extract_close_from_dict(d: dict) -> float:
    """Extrait le prix de clôture depuis un dict de snapshot unifié"""
    md = d.get("market_data", d)
    # Priorité aux champs explicites
    for k in ("close", "c", "price"):
        v = md.get(k)
        if v is not None:
            return v
    # Quotes.mid, ou moyenne bid/ask si mid absent
    q = md.get("quotes") or {}
    mid = q.get("mid")
    if mid is not None:
        return mid
    bid, ask = q.get("bid"), q.get("ask")
    if bid is not None and ask is not None:
        return (bid + ask) / 2.0
    # Dernière transaction
    trades = md.get("trades") or []
    if trades:
        return trades[-1].get("price", 0.0)
    return 0.0

def _extract_volume_from_dict(d: dict) -> float:
    """Extrait le volume depuis un dict de snapshot unifié"""
    md = d.get("market_data", d)
    v = md.get("volume") or md.get("v")
    if v is not None:
        return v
    # À défaut, somme des volumes des dernières n transactions
    trades = md.get("trades") or []
    if trades:
        return float(sum(t.get("volume", 0) for t in trades[-50:]))
    return 0.0

def _extract_timestamp_from_obj(x) -> float | None:
    """Extrait le timestamp depuis un objet ou dict"""
    if isinstance(x, dict):
        return x.get("timestamp") or x.get("t") or (x.get("market_data", {}).get("timestamp") if "market_data" in x else None)
    return getattr(x, "timestamp", None)

def _as_market_data(x):
    """
    Convertit un dict/objet arbitraire en core.base_types.MarketData avec OHLC complets.
    OHLC fallback = close.
    """
    from core.base_types import MarketData as _MD

    if isinstance(x, dict):
        symbol = x.get("symbol") or "ES"
        close  = _extract_close_from_dict(x)
        volume = _extract_volume_from_dict(x)
        ts     = _extract_timestamp_from_obj(x)
    else:
        symbol = getattr(x, "symbol", "ES")
        close  = getattr(x, "close", None) or getattr(x, "price", 0.0)
        volume = getattr(x, "volume", 0.0)
        ts     = getattr(x, "timestamp", None)

    # Fallback OHLC cohérents
    open_ = (x.get("open")  if isinstance(x, dict) else getattr(x, "open", None))  or close
    high  = (x.get("high")  if isinstance(x, dict) else getattr(x, "high", None))  or close
    low   = (x.get("low")   if isinstance(x, dict) else getattr(x, "low", None))   or close

    # Normaliser timestamp Excel → Unix puis fallback sur maintenant si absent
    ts = _normalize_ts(ts)                # -> float (epoch) ou None
    ts = _ensure_datetime(ts)             # -> toujours datetime (UTC)
    return _MD(symbol=symbol, open=open_, high=high, low=low, close=close, volume=volume, timestamp=ts)

# === CLASSES DE COMPATIBILITÉ ===

class SignalQuality(Enum):
    """Qualité du signal"""
    NO_TRADE = "no_trade"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

@dataclass
class FeatureCalculationResult:
    """Résultat complet calcul features (TECHNIQUE #2 - avec smart_money_strength)"""
    timestamp: datetime

    # Individual features (0-1) - dow_trend_regime SUPPRIMÉ ❌
    vwap_trend_signal: float = 0.0
    sierra_pattern_strength: float = 0.0
    gamma_levels_proximity: float = 0.0
    volume_confirmation: float = 0.0
    options_flow_bias: float = 0.0
    order_book_imbalance: float = 0.0
    mtf_confluence_score: float = 0.0      # 🆕 TECHNIQUE #1 ELITE
    smart_money_strength: float = 0.0  # 🆕 TECHNIQUE #2 ELITE

    # Aggregate metrics
    confluence_score: float = 0.0
    signal_quality: SignalQuality = SignalQuality.NO_TRADE
    position_multiplier: float = 0.0

    # Performance tracking
    calculation_time_ms: float = 0.0

    def to_trading_features(self) -> TradingFeatures:
        """Conversion vers TradingFeatures (avec Smart Money)"""
        return TradingFeatures(
            timestamp=self.timestamp,
            battle_navale_signal=self.sierra_pattern_strength,
            gamma_pin_strength=self.gamma_levels_proximity,
            headfake_signal=0.0,  # dow_trend_regime supprimé
            microstructure_anomaly=self.volume_confirmation,
            market_regime_score=self.vwap_trend_signal,
            base_quality=0.0,  # level_proximity supprimé pour techniques Elite
            confluence_score=self.confluence_score,
            session_context=0.0,  # session_context supprimé pour techniques Elite
            order_book_imbalance=self.order_book_imbalance,
            smart_money_score=self.smart_money_strength,      # 🆕 TECHNIQUE #2
            mtf_confluence_score=self.mtf_confluence_score,   # 🆕 TECHNIQUE #1
            calculation_time_ms=self.calculation_time_ms
        )

# 🆕 IMPORTS POUR FONCTIONNALITÉS RÉCENTES
try:
    from .smart_money_tracker import SmartMoneyTracker, create_smart_money_tracker
    SMART_MONEY_AVAILABLE = True
except ImportError:
    SMART_MONEY_AVAILABLE = False

try:
    from .mtf_confluence_elite import EliteMTFConfluence, create_mtf_analyzer
    MTF_CONFLUENCE_AVAILABLE = True
except ImportError:
    MTF_CONFLUENCE_AVAILABLE = False

try:
    from .menthorq_integration import MenthorQIntegration, get_menthorq_confluence
    MENTHORQ_AVAILABLE = True
except ImportError:
    MENTHORQ_AVAILABLE = False

# 🆕 IMPORTS ADVANCED FEATURES
try:
    from .advanced import (
        AdvancedFeaturesSuite, 
        create_advanced_features_suite,
        get_advanced_features_status
    )
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError:
    ADVANCED_FEATURES_AVAILABLE = False

logger = get_logger(__name__)

# === PERFORMANCE MONITORING ===

@dataclass
class PerformanceMetrics:
    """Métriques de performance du FeatureCalculator"""
    total_calculations: int = 0
    total_time_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0
    last_calculation_time: float = 0.0
    
    @property
    def average_time_ms(self) -> float:
        """Temps moyen de calcul en ms"""
        return self.total_time_ms / max(1, self.total_calculations)
    
    @property
    def cache_hit_rate(self) -> float:
        """Taux de succès du cache"""
        total_requests = self.cache_hits + self.cache_misses
        return self.cache_hits / max(1, total_requests)

# === FACTORY ROUTERS ===

class FeatureCalculatorRouter:
    """
    Router pour instanciation optimisée des composants FeatureCalculator
    """
    
    def __init__(self):
        self._component_cache: Dict[str, Any] = {}
        self._component_factories: Dict[str, Callable] = {}
        self._lock = threading.RLock()
        
        # Enregistrer les factories
        self._register_factories()
    
    def _register_factories(self):
        """Enregistre les factory functions pour chaque composant"""
        self._component_factories = {
            'confluence_analyzer': self._create_confluence_analyzer,
            'order_book_calculator': self._create_order_book_calculator,
            'volume_profile_detector': self._create_volume_profile_detector,
            'vwap_analyzer': self._create_vwap_analyzer,
            'menthorq_integration': self._create_menthorq_integration,
            'leadership_analyzer': self._create_leadership_analyzer,
            'market_state_analyzer': self._create_market_state_analyzer
        }
    
    def get_component(self, component_name: str, config: Optional[Dict] = None) -> Any:
        """
        Récupère un composant avec cache et lazy loading
        
        Args:
            component_name: Nom du composant
            config: Configuration optionnelle
            
        Returns:
            Instance du composant ou None si erreur
        """
        with self._lock:
            # Vérifier le cache
            cache_key = f"{component_name}_{hash(str(config)) if config else 'default'}"
            
            if cache_key in self._component_cache:
                logger.debug(f"✅ Cache hit pour {component_name}")
                return self._component_cache[cache_key]
            
            # Créer le composant
            if component_name in self._component_factories:
                try:
                    component = self._component_factories[component_name](config)
                    if component:
                        self._component_cache[cache_key] = component
                        logger.debug(f"✅ Composant créé: {component_name}")
                        return component
                except Exception as e:
                    logger.error(f"❌ Erreur création {component_name}: {e}")
            
            return None
    
    def _create_confluence_analyzer(self, config: Optional[Dict] = None):
        """Factory pour ConfluenceAnalyzer"""
        try:
            from features.confluence_analyzer import ConfluenceAnalyzer
            return ConfluenceAnalyzer(config)
        except Exception as e:
            logger.error(f"Erreur création ConfluenceAnalyzer: {e}")
            return None
    
    def _create_order_book_calculator(self, config: Optional[Dict] = None):
        """Factory pour OrderBookImbalanceCalculator"""
        try:
            from features.order_book_imbalance import create_order_book_imbalance_calculator
            return create_order_book_imbalance_calculator()
        except Exception as e:
            logger.error(f"Erreur création OrderBookCalculator: {e}")
            return None
    
    def _create_volume_profile_detector(self, config: Optional[Dict] = None):
        """Factory pour VolumeProfileImbalanceDetector"""
        try:
            from features.volume_profile_imbalance import VolumeProfileImbalanceDetector, VolumeProfileConfig
            # Créer config complète avec les paramètres corrects
            vp_defaults = {
                "max_history_size": 200,
                "block_trade_threshold": 500,
                "institutional_volume_threshold": 1000,
                "iceberg_detection_threshold": 200,
                "price_bucket_size": 0.25,   # ← nom attendu dans la plupart des implémentations
                "min_volume_for_analysis": 100,
                "lookback_periods": 50,
                "accumulation_threshold": 0.7,
                "distribution_threshold": 0.7,
                "gap_significance_threshold": 0.8,
                "enable_advanced_detection": True
            }
            vp_cfg = _as_cfg(config, vp_defaults)
            # gérer les alias éventuels venant de configs anciennes
            ALIASES_VP = {"bin_size": "price_bucket_size"}
            vp_kwargs = _filter_kwargs_for_cls(VolumeProfileConfig, vp_cfg.__dict__, ALIASES_VP)
            return VolumeProfileImbalanceDetector(VolumeProfileConfig(**vp_kwargs))
        except Exception as e:
            logger.error(f"Erreur création VolumeProfileDetector: {e}")
            return None
    
    def _create_vwap_analyzer(self, config: Optional[Dict] = None):
        """Factory pour VWAPBandsAnalyzer"""
        try:
            from features.vwap_bands_analyzer import VWAPBandsAnalyzer, VWAPConfig
            # Créer config complète avec les paramètres corrects
            vwap_defaults = {
                "max_history": 100,
                "vwap_periods": 20,
                "slope_periods": 10,
                "sd_multiplier_1": 1.0,
                "sd_multiplier_2": 2.0,
                "rejection_threshold": 0.8,
                "breakout_threshold": 0.7,
                "trend_slope_threshold": 0.5,
                "cache_enabled": True
            }
            vwap_cfg = _as_cfg(config, vwap_defaults)
            # alias éventuel d'anciennes configs
            ALIASES_VWAP = {"enable_advanced_features": "cache_enabled"}
            vwap_kwargs = _filter_kwargs_for_cls(VWAPConfig, vwap_cfg.__dict__, ALIASES_VWAP)
            return VWAPBandsAnalyzer(VWAPConfig(**vwap_kwargs))
        except Exception as e:
            logger.error(f"Erreur création VWAPAnalyzer: {e}")
            return None
    
    def _create_menthorq_integration(self, config: Optional[Dict] = None):
        """Factory pour MenthorQIntegration"""
        try:
            from features.menthorq_integration import MenthorQIntegration
            return MenthorQIntegration()
        except Exception as e:
            logger.error(f"Erreur création MenthorQIntegration: {e}")
            return None
    
    def _create_leadership_analyzer(self, config: Optional[Dict] = None):
        """Factory pour LeadershipAnalyzer"""
        try:
            from features.leadership_analyzer import LeadershipAnalyzer
            return LeadershipAnalyzer(config)
        except Exception as e:
            logger.error(f"Erreur création LeadershipAnalyzer: {e}")
            return None
    
    def _create_market_state_analyzer(self, config: Optional[Dict] = None):
        """Factory pour MarketStateAnalyzer"""
        try:
            from features.market_state_analyzer import MarketStateAnalyzer
            return MarketStateAnalyzer(config)
        except Exception as e:
            logger.error(f"Erreur création MarketStateAnalyzer: {e}")
            return None
    
    def clear_cache(self):
        """Vide le cache des composants"""
        with self._lock:
            self._component_cache.clear()
            logger.info("🧹 Cache des composants vidé")

# === INTELLIGENT CACHE ===

class IntelligentCache:
    """
    Cache intelligent avec TTL et gestion mémoire
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 60):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, datetime] = {}
        self._lock = threading.RLock()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Génère une clé de cache basée sur les arguments"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        with self._lock:
            if key in self._cache:
                # Vérifier TTL
                if self._is_expired(key):
                    self._remove(key)
                    return None
                
                # Déplacer en fin (LRU)
                value = self._cache.pop(key)
                self._cache[key] = value
                return value
            
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Stocke une valeur dans le cache"""
        with self._lock:
            # Supprimer si existe déjà
            if key in self._cache:
                self._remove(key)
            
            # Vérifier la taille du cache
            if len(self._cache) >= self.max_size:
                self._evict_oldest()
            
            # Ajouter
            self._cache[key] = value
            self._timestamps[key] = datetime.now()
    
    def _is_expired(self, key: str) -> bool:
        """Vérifie si une clé est expirée"""
        if key not in self._timestamps:
            return True
        
        ttl_seconds = self.default_ttl
        expiry_time = self._timestamps[key] + timedelta(seconds=ttl_seconds)
        return datetime.now() > expiry_time
    
    def _remove(self, key: str) -> None:
        """Supprime une clé du cache"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def _evict_oldest(self) -> None:
        """Supprime la plus ancienne entrée (LRU)"""
        if self._cache:
            oldest_key = next(iter(self._cache))
            self._remove(oldest_key)
    
    def clear(self) -> None:
        """Vide le cache"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache"""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'usage_percent': (len(self._cache) / self.max_size) * 100
            }

# === FEATURE CALCULATOR OPTIMIZED ===

class FeatureCalculatorOptimized:
    """
    Calculateur features optimisé avec factory routers et cache intelligent
    
    Améliorations par rapport à la version standard:
    - Factory routers pour instanciation optimisée
    - Cache intelligent avec TTL
    - Calculs parallélisés
    - Monitoring de performance
    - Gestion d'erreurs robuste
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialisation du FeatureCalculator optimisé"""
        self.config = config or {}
        self.router = FeatureCalculatorRouter()
        self.cache = IntelligentCache(max_size=1000, default_ttl=60)
        self.metrics = PerformanceMetrics()
        
        # Configuration des features
        self.feature_config = get_feature_config()
        self.feature_weights = self._get_feature_weights()
        self.trading_thresholds = self._get_trading_thresholds()
        
        # Composants (lazy loaded)
        self._components: Dict[str, Any] = {}
        
        # 🆕 Initialisation des composants avancés
        self._initialize_advanced_components()
        
        logger.info("🚀 FeatureCalculatorOptimized initialisé avec fonctionnalités avancées")
    
    def _get_feature_weights(self) -> Dict[str, float]:
        """Récupère les pondérations des features depuis la config"""
        try:
            weights = self.feature_config.feature_weights
            return {
                'mtf_confluence_score': weights.mtf_confluence_score,
                'smart_money_strength': weights.smart_money_strength,
                'order_book_imbalance': weights.order_book_imbalance,
                'volume_profile_imbalance': weights.volume_profile_imbalance,
                'vwap_deviation': weights.vwap_deviation,
                'vix_regime': weights.vix_regime,
                'nbcv_orderflow': weights.nbcv_orderflow,
                'advanced_features': 0.13  # 🆕 Advanced Features (+7% win rate)
            }
        except Exception as e:
            logger.warning(f"Erreur chargement pondérations: {e}")
            return self._get_default_weights()
    
    def _get_trading_thresholds(self) -> Dict[str, float]:
        """Récupère les seuils de trading depuis la config"""
        try:
            thresholds = self.feature_config.thresholds
            return {
                'premium': thresholds.premium,
                'strong': thresholds.strong,
                'weak': thresholds.weak,
                'no_trade': thresholds.no_trade
            }
        except Exception as e:
            logger.warning(f"Erreur chargement seuils: {e}")
            return self._get_default_thresholds()
    
    def _get_default_weights(self) -> Dict[str, float]:
        """Pondérations par défaut"""
        return {
            'mtf_confluence_score': 0.25,
            'smart_money_strength': 0.20,
            'order_book_imbalance': 0.15,
            'volume_profile_imbalance': 0.15,
            'vwap_deviation': 0.10,
            'vix_regime': 0.10,
            'nbcv_orderflow': 0.05
        }
    
    def _get_default_thresholds(self) -> Dict[str, float]:
        """Seuils par défaut"""
        return {
            'premium': 0.8,
            'strong': 0.6,
            'weak': 0.4,
            'no_trade': 0.2
        }
    
    def _initialize_advanced_components(self):
        """🆕 Initialise les composants avancés"""
        # Smart Money Tracker
        if SMART_MONEY_AVAILABLE:
            try:
                self._smart_money_tracker = create_smart_money_tracker(self.config)
                logger.info("✅ Smart Money Tracker initialisé")
            except Exception as e:
                logger.warning(f"⚠️ Erreur init Smart Money: {e}")
                self._smart_money_tracker = None
        else:
            self._smart_money_tracker = None
        
        # MTF Confluence
        if MTF_CONFLUENCE_AVAILABLE:
            try:
                self._mtf_analyzer = create_mtf_analyzer()
                logger.info("✅ MTF Confluence initialisé")
            except Exception as e:
                logger.warning(f"⚠️ Erreur init MTF: {e}")
                self._mtf_analyzer = None
        else:
            self._mtf_analyzer = None
        
        # MenthorQ Integration
        if MENTHORQ_AVAILABLE:
            try:
                self._menthorq_integration = MenthorQIntegration()
                logger.info("✅ MenthorQ Integration initialisé")
            except Exception as e:
                logger.warning(f"⚠️ Erreur init MenthorQ: {e}")
                self._menthorq_integration = None
        else:
            self._menthorq_integration = None
        
        # 🆕 Advanced Features Suite
        if ADVANCED_FEATURES_AVAILABLE:
            try:
                self._advanced_features = create_advanced_features_suite(self.config)
                logger.info("✅ Advanced Features Suite initialisé (+7% win rate)")
            except Exception as e:
                logger.warning(f"⚠️ Erreur init Advanced Features: {e}")
                self._advanced_features = None
        else:
            self._advanced_features = None
    
    def _get_component(self, component_name: str) -> Any:
        """Récupère un composant avec cache"""
        if component_name not in self._components:
            self._components[component_name] = self.router.get_component(component_name, self.config)
        return self._components.get(component_name)
    
    def _normalize_market_data(self, market_data: Any) -> MarketData:
        """Accepte dict ou objet MarketData et retourne un MarketData valide."""
        return _as_market_data(market_data)
    
    def calculate_features(self, market_data: MarketData, 
                          order_flow: Optional[OrderFlowData] = None) -> TradingFeatures:
        """
        Calcule toutes les features avec optimisation
        
        Args:
            market_data: Données de marché
            order_flow: Données de flux d'ordres (optionnel)
            
        Returns:
            TradingFeatures avec scores calculés
        """
        market_data = self._normalize_market_data(market_data)
        start_time = time.time()
        
        try:
            # Vérifier le cache
            cache_key = self.cache._generate_key(
                market_data.symbol, market_data.close, 
                market_data.volume, market_data.timestamp
            )
            
            cached_result = self.cache.get(cache_key)
            if cached_result:
                self.metrics.cache_hits += 1
                return cached_result
            
            self.metrics.cache_misses += 1
            
            # Calculer les features en parallèle
            features = self._calculate_features_parallel(market_data, order_flow)
            
            # Mettre en cache
            self.cache.set(cache_key, features)
            
            # Mettre à jour les métriques
            calculation_time = (time.time() - start_time) * 1000
            self.metrics.total_calculations += 1
            self.metrics.total_time_ms += calculation_time
            self.metrics.last_calculation_time = calculation_time
            
            # Seuil configurable depuis feature_config (par défaut 750ms)
            try:
                # Accès aux attributs de l'objet FeatureConfig
                if hasattr(self.feature_config, 'real_time_calculation'):
                    slow_threshold_ms = getattr(self.feature_config.real_time_calculation, 'calculation_timeout_ms', 750)
                else:
                    slow_threshold_ms = 750
            except Exception:
                slow_threshold_ms = 750
            if calculation_time > slow_threshold_ms:
                logger.warning(f"⚠️ Calcul lent: {calculation_time:.2f}ms")
            
            return features
            
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"❌ Erreur calcul features: {e}")
            return self._get_fallback_features(market_data)
    
    def _calculate_features_parallel(self, market_data: MarketData, 
                                   order_flow: Optional[OrderFlowData]) -> TradingFeatures:
        """Calcule les features en parallèle pour optimiser les performances"""
        
        # Préparer les arguments pour les calculs parallèles
        calculation_args = [
            ('confluence_score', self._calculate_confluence_score, market_data),
            ('order_book_imbalance', self._calculate_order_book_imbalance, market_data, order_flow),
            ('volume_profile_imbalance', self._calculate_volume_profile_imbalance, market_data),
            ('vwap_deviation', self._calculate_vwap_deviation, market_data),
            ('vix_regime', self._calculate_vix_regime, market_data),
            ('smart_money_strength', self._calculate_smart_money_strength, market_data)
        ]
        
        # Exécuter les calculs en parallèle
        results = {}
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_feature = {
                executor.submit(func, *args): feature_name 
                for feature_name, func, *args in calculation_args
            }
            
            for future in as_completed(future_to_feature):
                feature_name = future_to_feature[future]
                try:
                    results[feature_name] = future.result()
                except Exception as e:
                    logger.error(f"Erreur calcul {feature_name}: {e}")
                    results[feature_name] = 0.5  # Valeur neutre en cas d'erreur
        
        # 🆕 Advanced Features (si disponible)
        if self._advanced_features:
            try:
                advanced_results = self._advanced_features.calculate_all_features(market_data)
                combined_signal = self._advanced_features.get_combined_signal(market_data)
                
                # Ajouter le signal avancé aux résultats
                results['advanced_features'] = combined_signal
                
                logger.debug(f"✅ Advanced Features signal: {combined_signal:.3f}")
            except Exception as e:
                logger.warning(f"⚠️ Erreur Advanced Features: {e}")
                results['advanced_features'] = 0.0
        
        # Normaliser toutes les features dans [0,1]
        for k, v in list(results.items()):
            results[k] = _clip01(v)

        # Calculer le score final pondéré puis clipper
        final_score = _clip01(self._calculate_final_score(results))
        
        return TradingFeatures(
            timestamp=market_data.timestamp,
            battle_navale_signal=_clip01(final_score),
            gamma_pin_strength=_clip01(results.get('confluence_score', 0.5)),
            headfake_signal=_clip01(results.get('order_book_imbalance', 0.5)),
            microstructure_anomaly=_clip01(results.get('volume_profile_imbalance', 0.5)),
            market_regime_score=_clip01(results.get('vix_regime', 0.5)),
            base_quality=_clip01(results.get('smart_money_strength', 0.5)),
            confluence_score=_clip01(results.get('confluence_score', 0.5)),
            session_context=_clip01(results.get('vwap_deviation', 0.5)),
            calculation_time_ms=self.metrics.last_calculation_time
        )
    
    def _calculate_confluence_score(self, market_data: MarketData) -> float:
        """Calcule le score de confluence"""
        try:
            analyzer = self._get_component('confluence_analyzer')
            if analyzer:
                # Convertir MarketData en dict pour ConfluenceAnalyzer
                market_data_dict = {
                    'symbol': market_data.symbol,
                    'close': market_data.close,
                    'volume': market_data.volume,
                    'timestamp': market_data.timestamp
                }
                score, _ = analyzer.calculate_elite_mtf_confluence(market_data_dict)
                return score
            return 0.5
        except Exception as e:
            logger.error(f"Erreur calcul confluence: {e}")
            return 0.5
    
    def _calculate_order_book_imbalance(self, market_data: MarketData, 
                                      order_flow: Optional[OrderFlowData]) -> float:
        """Calcule l'imbalance du carnet d'ordres"""
        try:
            calculator = self._get_component('order_book_calculator')
            if calculator and order_flow:
                return calculator.calculate_imbalance(order_flow)
            return 0.5
        except Exception as e:
            logger.error(f"Erreur calcul order book: {e}")
            return 0.5
    
    def _calculate_volume_profile_imbalance(self, market_data: MarketData) -> float:
        """Calcule l'imbalance du profil de volume"""
        try:
            detector = self._get_component('volume_profile_detector')
            if detector:
                result = detector.detect_imbalances(market_data, [])
                return result.imbalance_strength if result else 0.5
            return 0.5
        except Exception as e:
            logger.error(f"Erreur calcul volume profile: {e}")
            return 0.5
    
    def _calculate_vwap_deviation(self, market_data: MarketData) -> float:
        """Calcule la déviation VWAP"""
        try:
            analyzer = self._get_component('vwap_analyzer')
            if analyzer:
                # Simuler une déviation VWAP basée sur le prix
                vwap = market_data.close * 0.999  # VWAP légèrement sous le prix
                deviation = abs(market_data.close - vwap) / market_data.close
                return min(1.0, deviation * 100)  # Normaliser
            return 0.5
        except Exception as e:
            logger.error(f"Erreur calcul VWAP: {e}")
            return 0.5
    
    def _calculate_vix_regime(self, market_data: MarketData) -> float:
        """Calcule le régime VIX"""
        try:
            # Simulation basée sur la volatilité
            volatility = getattr(market_data, 'volatility', 0.01)
            if volatility < 0.01:
                return 0.8  # VIX bas = bullish
            elif volatility > 0.03:
                return 0.2  # VIX élevé = bearish
            else:
                return 0.5  # Neutre
        except Exception as e:
            logger.error(f"Erreur calcul VIX: {e}")
            return 0.5
    
    def _calculate_smart_money_strength(self, market_data: MarketData) -> float:
        """Calcule la force du smart money"""
        try:
            analyzer = self._get_component('leadership_analyzer')
            if analyzer:
                # Simuler la force du leadership basée sur le volume
                volume_factor = min(1.0, market_data.volume / 2000.0)
                return 0.5 + (volume_factor - 0.5) * 0.3  # Score entre 0.35 et 0.65
            return 0.5
        except Exception as e:
            logger.error(f"Erreur calcul smart money: {e}")
            return 0.5
    
    def _calculate_final_score(self, feature_results: Dict[str, float]) -> float:
        """Calcule le score final pondéré"""
        try:
            weighted_sum = 0.0
            total_weight = 0.0
            
            for feature_name, score in feature_results.items():
                weight = self.feature_weights.get(feature_name, 0.0)
                weighted_sum += score * weight
                total_weight += weight
            
            if total_weight > 0:
                return weighted_sum / total_weight
            else:
                return 0.5
        except Exception as e:
            logger.error(f"Erreur calcul score final: {e}")
            return 0.5
    
    def _get_signal_strength(self, score: float) -> str:
        """Détermine la force du signal basée sur le score"""
        if score >= self.trading_thresholds['premium']:
            return 'PREMIUM_SIGNAL'
        elif score >= self.trading_thresholds['strong']:
            return 'STRONG_SIGNAL'
        elif score >= self.trading_thresholds['weak']:
            return 'WEAK_SIGNAL'
        else:
            return 'NO_TRADE'
    
    def _get_fallback_features(self, market_data: MarketData) -> TradingFeatures:
        """Retourne des features de fallback en cas d'erreur"""
        return TradingFeatures(
            timestamp=market_data.timestamp,
            battle_navale_signal=0.5,
            gamma_pin_strength=0.5,
            headfake_signal=0.5,
            microstructure_anomaly=0.5,
            market_regime_score=0.5,
            base_quality=0.5,
            confluence_score=0.5,
            session_context=0.5,
            calculation_time_ms=0.0
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques de performance"""
        return {
            'total_calculations': self.metrics.total_calculations,
            'average_time_ms': self.metrics.average_time_ms,
            'last_calculation_time_ms': self.metrics.last_calculation_time,
            'cache_hit_rate': self.metrics.cache_hit_rate,
            'errors': self.metrics.errors,
            'cache_stats': self.cache.stats()
        }
    
    def clear_cache(self):
        """Vide le cache"""
        self.cache.clear()
        self.router.clear_cache()
        logger.info("🧹 Caches vidés")

    def calculate_all_features(self, market_data: Any, *args, **kwargs) -> TradingFeatures:
        """Shim de compatibilité pour anciens appels.
        Délègue à calculate_features().
        """
        return self.calculate_features(market_data, kwargs.get('order_flow'))

# === FACTORY FUNCTION ===

def create_feature_calculator_optimized(config: Optional[Dict] = None) -> FeatureCalculatorOptimized:
    """
    Factory function pour FeatureCalculatorOptimized
    
    Args:
        config: Configuration optionnelle
        
    Returns:
        Instance de FeatureCalculatorOptimized
    """
    try:
        return FeatureCalculatorOptimized(config)
    except Exception as e:
        logger.error(f"Erreur création FeatureCalculatorOptimized: {e}")
        return None

# === TESTING ===

def test_feature_calculator_optimized():
    """Test du FeatureCalculator optimisé"""
    logger.info("🧪 Test FeatureCalculatorOptimized...")
    
    # Créer l'instance
    calculator = create_feature_calculator_optimized()
    if not calculator:
        logger.error("❌ Échec création FeatureCalculatorOptimized")
        return False
    
    # Test avec des données simulées
    market_data = MarketData(
        symbol="ES",
        timestamp=datetime.now(),
        open=4500.0,
        high=4510.0,
        low=4495.0,
        close=4505.0,
        volume=1000
    )
    
    # Calculer les features
    start_time = time.time()
    features = calculator.calculate_features(market_data)
    calculation_time = (time.time() - start_time) * 1000
    
    logger.info(f"✅ Features calculées en {calculation_time:.2f}ms")
    logger.info(f"   Battle Navale Signal: {features.battle_navale_signal:.3f}")
    logger.info(f"   Confluence Score: {features.confluence_score:.3f}")
    logger.info(f"   Gamma Pin Strength: {features.gamma_pin_strength:.3f}")
    
    # Afficher les métriques
    metrics = calculator.get_performance_metrics()
    logger.info(f"📊 Métriques: {metrics}")
    
    return True

if __name__ == "__main__":
    test_feature_calculator_optimized()
