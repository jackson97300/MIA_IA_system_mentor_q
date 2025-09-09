"""
strategies/signal_core/factory_functions.py

Factory functions et helpers pour Signal Generator
Extrait et nettoyé du fichier original signal_generator.py (dernières lignes)
"""

from typing import Dict, Optional, Any
import pandas as pd
from core.logger import get_logger
from core.base_types import MarketData, OrderFlowData

# Imports depuis les modules refactorisés
from .signal_generator_core import SignalGenerator
from .signal_components import FinalSignal

logger = get_logger(__name__)

# ===== FACTORY FUNCTIONS =====

def create_signal_generator(config: Optional[Dict[str, Any]] = None) -> SignalGenerator:
    """
    Factory pour créer SignalGenerator REFACTORISÉ
    
    NOUVEAU : Avec support cache optimisé, PRIORITÉ #2, PHASE 3 Elite MTF, 
             TECHNIQUE #2 Smart Money, TECHNIQUE #3 ML Ensemble et TECHNIQUE #4 Gamma Cycles
    
    Args:
        config: Configuration optionnelle pour le générateur
        
    Returns:
        SignalGenerator: Instance configurée et prête à l'emploi
        
    Example:
        >>> generator = create_signal_generator()
        >>> generator = create_signal_generator({'cache_ttl': 120, 'max_position_size': 5})
    """
    
    # Configuration par défaut optimisée
    default_config = {
        # Cache configuration
        'cache_config': {
            'cache_ttl': 60,
            'cache_size': 500
        },
        
        # Signal generation
        'min_signal_confidence': 0.70,
        'min_confluence_score': 0.60,
        'min_risk_reward': 1.5,
        'max_position_size': 3.0,
        
        # Battle Navale thresholds (PRIORITÉ #2)
        'battle_long_threshold': 0.25,
        'battle_short_threshold': -0.25,
        
        # MTF Elite (PHASE 3)
        'mtf_enabled': True,
        'mtf_elite_threshold': 0.75,
        'mtf_standard_threshold': 0.35,
        
        # Smart Money (TECHNIQUE #2)
        'smart_money_enabled': True,
        'smart_money_confidence_threshold': 0.6,
        'smart_money_institutional_threshold': 0.7,
        
        # ML Ensemble (TECHNIQUE #3)
        'ml_ensemble_enabled': True,
        'ml_confidence_threshold': 0.70,
        'ml_cache_enabled': True,
        
        # Gamma Cycles (TECHNIQUE #4)
        'gamma_cycles_enabled': True,
        'gamma_expiry_week_factor': 0.7,
        'gamma_peak_factor': 1.3,
        'gamma_moderate_factor': 1.1,
        'gamma_normal_factor': 1.0,
        'gamma_post_expiry_factor': 1.05,
        'gamma_cache_enabled': True,
        'gamma_cycles_position_impact': True,
        'gamma_cycles_confidence_impact': True
    }
    
    # Merge avec config utilisateur
    if config:
        # Merge récursif pour cache_config
        if 'cache_config' in config and 'cache_config' in default_config:
            default_config['cache_config'].update(config['cache_config'])
            config = {k: v for k, v in config.items() if k != 'cache_config'}
        
        default_config.update(config)
    
    logger.info("🏗️ Création SignalGenerator REFACTORISÉ avec configuration complète")
    logger.debug(f"Configuration utilisée: {len(default_config)} paramètres")
    
    return SignalGenerator(default_config)


def generate_trading_signal(market_data: MarketData,
                            order_flow: Optional[OrderFlowData] = None,
                            options_data: Optional[Dict[str, Any]] = None,
                            structure_data: Optional[Dict[str, Any]] = None,
                            sierra_patterns: Optional[Dict[str, float]] = None,
                            generator: Optional[SignalGenerator] = None) -> FinalSignal:
    """
    Helper function pour génération rapide signal REFACTORISÉ

    Usage simple pour générer un signal avec toutes les techniques Elite.
    Si aucun générateur n'est fourni, en crée un automatiquement.

    Args:
        market_data: Données de marché actuelles
        order_flow: Données de flux d'ordres (optionnel)
        options_data: Données options (optionnel)
        structure_data: Données de structure de marché (optionnel)
        sierra_patterns: Patterns Sierra Chart (optionnel)
        generator: Générateur existant (optionnel, en crée un si None)

    Returns:
        FinalSignal: Signal complet avec toutes les analyses Elite

    Example:
        >>> signal = generate_trading_signal(market_data, order_flow, options_data)
        >>> if signal.decision == SignalDecision.EXECUTE_LONG:
        ...     execute_trade(signal)
        >>> 
        >>> # Avec générateur réutilisable
        >>> gen = create_signal_generator()
        >>> signal1 = generate_trading_signal(market_data1, generator=gen)
        >>> signal2 = generate_trading_signal(market_data2, generator=gen)
    """

    if generator is None:
        # Création générateur optimisé pour usage unique
        config = {
            'cache_config': {'cache_ttl': 30, 'cache_size': 100},  # Cache plus petit pour usage unique
            'max_position_size': 2.0  # Plus conservateur pour usage simple
        }
        generator = create_signal_generator(config)
        logger.debug("Générateur temporaire créé pour signal unique")

    return generator.generate_signal(
        market_data=market_data,
        order_flow=order_flow,
        options_data=options_data,
        structure_data=structure_data,
        sierra_patterns=sierra_patterns
    )


def create_signal_generator_for_backtesting(config: Optional[Dict[str, Any]] = None) -> SignalGenerator:
    """
    Factory spécialisée pour créer un SignalGenerator optimisé pour backtesting
    
    Configuration adaptée pour performance maximale en backtesting :
    - Cache désactivé (pas utile en backtesting)
    - Logging réduit
    - Validation risk simplifiée
    
    Args:
        config: Configuration additionnelle
        
    Returns:
        SignalGenerator: Instance optimisée pour backtesting
    """
    
    backtest_config = {
        # Performance backtesting
        'cache_config': {
            'cache_ttl': 0,  # Pas de cache en backtesting
            'cache_size': 10
        },
        
        # Validation simplifiée
        'min_risk_reward': 1.0,  # Moins strict
        'min_signal_confidence': 0.60,  # Moins strict
        
        # Toutes les techniques Elite activées
        'mtf_enabled': True,
        'smart_money_enabled': True,
        'ml_ensemble_enabled': True,
        'gamma_cycles_enabled': True,
        
        # Position sizing pour backtesting
        'max_position_size': 1.0,  # Plus conservateur
        
        # Logging réduit
        'log_level': 'WARNING'
    }
    
    if config:
        backtest_config.update(config)
    
    logger.info("🔬 Création SignalGenerator pour BACKTESTING")
    return SignalGenerator(backtest_config)


def create_signal_generator_for_paper_trading(config: Optional[Dict[str, Any]] = None) -> SignalGenerator:
    """
    Factory spécialisée pour créer un SignalGenerator optimisé pour paper trading
    
    Configuration équilibrée entre performance et validation complète.
    
    Args:
        config: Configuration additionnelle
        
    Returns:
        SignalGenerator: Instance optimisée pour paper trading
    """
    
    paper_config = {
        # Cache modéré
        'cache_config': {
            'cache_ttl': 60,
            'cache_size': 200
        },
        
        # Validation standard
        'min_risk_reward': 1.5,
        'min_signal_confidence': 0.70,
        
        # Toutes les techniques Elite
        'mtf_enabled': True,
        'smart_money_enabled': True,
        'ml_ensemble_enabled': True,
        'gamma_cycles_enabled': True,
        
        # Position sizing paper trading
        'max_position_size': 2.0,
        
        # Logging complet
        'log_level': 'INFO'
    }
    
    if config:
        paper_config.update(config)
    
    logger.info("📝 Création SignalGenerator pour PAPER TRADING")
    return SignalGenerator(paper_config)


def create_signal_generator_for_production(config: Optional[Dict[str, Any]] = None) -> SignalGenerator:
    """
    Factory spécialisée pour créer un SignalGenerator optimisé pour production
    
    Configuration maximale sécurité et performance.
    
    Args:
        config: Configuration additionnelle
        
    Returns:
        SignalGenerator: Instance optimisée pour production
    """
    
    prod_config = {
        # Cache optimisé production
        'cache_config': {
            'cache_ttl': 120,  # Plus long pour performance
            'cache_size': 1000  # Plus grand pour performance
        },
        
        # Validation stricte
        'min_risk_reward': 2.0,  # Plus strict
        'min_signal_confidence': 0.75,  # Plus strict
        'min_confluence_score': 0.65,  # Plus strict
        
        # Toutes les techniques Elite avec validation max
        'mtf_enabled': True,
        'smart_money_enabled': True,
        'ml_ensemble_enabled': True,
        'gamma_cycles_enabled': True,
        
        # Position sizing conservateur
        'max_position_size': 3.0,
        
        # Logging optimal
        'log_level': 'INFO'
    }
    
    if config:
        prod_config.update(config)
    
    logger.info("🚀 Création SignalGenerator pour PRODUCTION")
    return SignalGenerator(prod_config)


# ===== HELPER FUNCTIONS =====

def validate_market_data(market_data: MarketData) -> bool:
    """
    Valide les données de marché avant génération de signal
    
    Args:
        market_data: Données à valider
        
    Returns:
        bool: True si valides, False sinon
    """
    
    if not market_data:
        logger.warning("MarketData manquant")
        return False
    
    # Validation prix
    if market_data.close <= 0:
        logger.warning(f"Prix invalide: {market_data.close}")
        return False
    
    # Validation cohérence OHLC
    if not (market_data.low <= market_data.close <= market_data.high):
        logger.warning("Cohérence OHLC invalide")
        return False
    
    # Validation timestamp
    if not market_data.timestamp:
        logger.warning("Timestamp manquant")
        return False
    
    # Validation volume
    if market_data.volume < 0:
        logger.warning(f"Volume invalide: {market_data.volume}")
        return False
    
    return True


def get_signal_generator_version() -> str:
    """
    Retourne la version du SignalGenerator refactorisé
    
    Returns:
        str: Version string
    """
    return "v3.6_refactored_modular"


def get_available_techniques() -> Dict[str, bool]:
    """
    Retourne la disponibilité des techniques Elite
    
    Returns:
        Dict: Status de chaque technique
    """
    
    from .base_types import get_availability_status
    
    availability = get_availability_status()
    
    return {
        'battle_navale': True,  # Toujours disponible
        'mtf_elite_confluence': True,  # Toujours disponible
        'smart_money_tracker': True,  # Assumé disponible
        'ml_ensemble_filter': availability.get('ml_ensemble', False),
        'gamma_cycles_analyzer': availability.get('gamma_cycles', False),
        'all_techniques_available': all(availability.values())
    }


def create_test_market_data() -> MarketData:
    """
    Crée des données de marché factices pour tests
    
    Returns:
        MarketData: Données test valides
    """
    
    return MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4500.0,
        high=4505.0,
        low=4495.0,
        close=4502.0,
        volume=1000
    )


# ===== MIGRATION HELPERS =====

def migrate_from_original_signal_generator(original_generator) -> SignalGenerator:
    """
    Aide à la migration depuis l'ancien SignalGenerator
    
    Args:
        original_generator: Instance de l'ancien générateur
        
    Returns:
        SignalGenerator: Nouvelle instance avec configuration migrée
    """
    
    # Extraction configuration de l'ancien générateur
    config = {}
    
    if hasattr(original_generator, 'config'):
        config = original_generator.config.copy()
    
    # Migration paramètres spécifiques
    if hasattr(original_generator, 'min_confidence'):
        config['min_signal_confidence'] = original_generator.min_confidence
    
    if hasattr(original_generator, 'max_position_size'):
        config['max_position_size'] = original_generator.max_position_size
    
    logger.info("🔄 Migration depuis ancien SignalGenerator")
    return create_signal_generator(config)


# ===== EXPORTS =====
__all__ = [
    # Factory functions principales
    'create_signal_generator',
    'generate_trading_signal',
    
    # Factory functions spécialisées
    'create_signal_generator_for_backtesting',
    'create_signal_generator_for_paper_trading',
    'create_signal_generator_for_production',
    
    # Helper functions
    'validate_market_data',
    'get_signal_generator_version',
    'get_available_techniques',
    'create_test_market_data',
    
    # Migration helpers
    'migrate_from_original_signal_generator'
]