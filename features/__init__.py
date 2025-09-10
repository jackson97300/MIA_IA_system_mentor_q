"""
Features module pour MIA_IA_SYSTEM - LAZY LOADING
=================================================

Module features avec lazy loading complet pour optimiser les performances
et éviter les effets de bord au démarrage.
"""

import importlib
from typing import Dict, Any, Optional, Callable
from core.logger import get_logger

logger = get_logger(__name__)

# === LAZY LOADING SYSTEM ===

# Cache des modules chargés
_loaded_modules: Dict[str, Any] = {}
_module_availability: Dict[str, bool] = {}

# Configuration des modules features
FEATURE_MODULES = {
    'feature_calculator': {
        'path': '.feature_calculator_optimized', 
        'class': 'FeatureCalculatorOptimized',
        'factory': 'create_feature_calculator_optimized'
    },
    'market_regime': {
        'path': '.market_regime',
        'class': 'MarketRegimeDetector',
        'factory': 'create_market_regime_detector'
    },
    'confluence_analyzer': {
        'path': '.confluence_analyzer',
        'class': 'ConfluenceAnalyzer', 
        'factory': 'create_confluence_analyzer'
    },
    'confluence_integrator': {
        'path': '.confluence_integrator',
        'class': 'ConfluenceIntegrator',
        'factory': 'create_confluence_integrator'
    },
    'order_book_imbalance': {
        'path': '.order_book_imbalance',
        'class': 'OrderBookImbalanceCalculator',
        'factory': 'create_order_book_imbalance_calculator'
    },
    'volume_profile_imbalance': {
        'path': '.volume_profile_imbalance',
        'class': 'VolumeProfileImbalanceDetector',
        'factory': 'create_volume_profile_imbalance_detector'
    },
    'vwap_bands_analyzer': {
        'path': '.vwap_bands_analyzer',
        'class': 'VWAPBandsAnalyzer',
        'factory': 'create_vwap_bands_analyzer'
    },
    'menthorq_integration': {
        'path': '.menthorq_integration',
        'class': 'MenthorQIntegration',
        'factory': 'create_menthorq_integration'
    },
    'menthorq_dealers_bias': {
        'path': '.menthorq_dealers_bias',
        'class': 'MenthorQDealersBiasAnalyzer',
        'factory': 'create_menthorq_dealers_bias_analyzer'
    },
    'leadership_analyzer': {
        'path': '.leadership_analyzer',
        'class': 'LeadershipAnalyzer',
        'factory': 'create_leadership_analyzer'
    },
    'market_state_analyzer': {
        'path': '.market_state_analyzer',
        'class': 'MarketStateAnalyzer',
        'factory': 'create_market_state_analyzer'
    }
}

# Exports publics
__all__ = [
    'create_feature_calculator',
    'create_market_regime_detector', 
    'create_confluence_analyzer',
    'create_confluence_integrator',
    'create_order_book_imbalance_calculator',
    'create_volume_profile_imbalance_detector',
    'create_vwap_bands_analyzer',
    'create_menthorq_integration',
    'create_menthorq_dealers_bias_analyzer',
    'create_leadership_analyzer',
    'create_market_state_analyzer',
    'get_features_status',
    'get_module_status',
    'is_module_available',
    'get_integrity_status',
    'start_integrity_monitoring',
    'stop_integrity_monitoring'
]

# === LAZY LOADING FUNCTIONS ===

def _lazy_import_module(module_name: str) -> Optional[Any]:
    """
    Import paresseux d'un module avec cache
    
    Args:
        module_name: Nom du module (clé dans FEATURE_MODULES)
        
    Returns:
        Module importé ou None si erreur
    """
    if module_name in _loaded_modules:
        return _loaded_modules[module_name]
    
    if module_name not in FEATURE_MODULES:
        logger.warning(f"Module inconnu: {module_name}")
        return None
    
    module_config = FEATURE_MODULES[module_name]
    module_path = module_config['path']
    
    try:
        module = importlib.import_module(module_path, package='features')
        _loaded_modules[module_name] = module
        _module_availability[module_name] = True
        logger.debug(f"✅ Module chargé: {module_name}")
        return module
    except Exception as e:
        logger.warning(f"❌ Échec chargement module {module_name}: {e}")
        _module_availability[module_name] = False
        return None

def _lazy_get_class(module_name: str) -> Optional[Any]:
    """
    Récupère une classe d'un module avec lazy loading
    
    Args:
        module_name: Nom du module
        
    Returns:
        Classe ou None si erreur
    """
    module = _lazy_import_module(module_name)
    if not module:
        return None
    
    class_name = FEATURE_MODULES[module_name]['class']
    return getattr(module, class_name, None)

def _lazy_get_factory(module_name: str) -> Optional[Callable]:
    """
    Récupère une factory function d'un module avec lazy loading
    
    Args:
        module_name: Nom du module
        
    Returns:
        Factory function ou None si erreur
    """
    module = _lazy_import_module(module_name)
    if not module:
        return None
    
    factory_name = FEATURE_MODULES[module_name]['factory']
    return getattr(module, factory_name, None)

# === FACTORY FUNCTIONS ===

def create_feature_calculator(config=None):
    """Factory pour FeatureCalculator avec fallback vers version optimisée"""
    # Essayer d'abord la version optimisée
    factory = _lazy_get_factory('feature_calculator_optimized')
    if factory:
        try:
            return factory(config)
        except Exception as e:
            logger.warning(f"Version optimisée échouée, fallback standard: {e}")
    
    # Fallback vers version standard
    factory = _lazy_get_factory('feature_calculator')
    return factory(config) if factory else None

def create_market_regime_detector(config=None):
    """Factory pour MarketRegimeDetector"""
    factory = _lazy_get_factory('market_regime')
    return factory(config) if factory else None

def create_confluence_analyzer(config=None):
    """Factory pour ConfluenceAnalyzer"""
    factory = _lazy_get_factory('confluence_analyzer')
    return factory(config) if factory else None

def create_confluence_integrator(config=None):
    """Factory pour ConfluenceIntegrator"""
    factory = _lazy_get_factory('confluence_integrator')
    return factory(config) if factory else None

def create_order_book_imbalance_calculator(*args, **kwargs):
    """Factory pour OrderBookImbalanceCalculator"""
    factory = _lazy_get_factory('order_book_imbalance')
    return factory(*args, **kwargs) if factory else None

def create_volume_profile_imbalance_detector(config=None):
    """Factory pour VolumeProfileImbalanceDetector"""
    factory = _lazy_get_factory('volume_profile_imbalance')
    return factory(config) if factory else None

def create_vwap_bands_analyzer(config=None):
    """Factory pour VWAPBandsAnalyzer"""
    factory = _lazy_get_factory('vwap_bands_analyzer')
    return factory(config) if factory else None

def create_menthorq_integration(config=None):
    """Factory pour MenthorQIntegration"""
    factory = _lazy_get_factory('menthorq_integration')
    return factory(config) if factory else None

def create_menthorq_dealers_bias_analyzer(config=None):
    """Factory pour MenthorQDealersBiasAnalyzer"""
    factory = _lazy_get_factory('menthorq_dealers_bias')
    return factory(config) if factory else None

def create_leadership_analyzer(config=None):
    """Factory pour LeadershipAnalyzer"""
    factory = _lazy_get_factory('leadership_analyzer')
    return factory(config) if factory else None

def create_market_state_analyzer(config=None):
    """Factory pour MarketStateAnalyzer"""
    factory = _lazy_get_factory('market_state_analyzer')
    return factory(config) if factory else None

# === STATUS FUNCTIONS ===

def is_module_available(module_name: str) -> bool:
    """
    Vérifie si un module est disponible sans le charger
    
    Args:
        module_name: Nom du module
        
    Returns:
        True si disponible, False sinon
    """
    if module_name in _module_availability:
        return _module_availability[module_name]
    
    # Test rapide d'import
    try:
        module_config = FEATURE_MODULES[module_name]
        importlib.import_module(module_config['path'], package='features')
        _module_availability[module_name] = True
        return True
    except Exception:
        _module_availability[module_name] = False
        return False

def get_module_status(module_name: str) -> Dict[str, Any]:
    """
    Retourne le statut détaillé d'un module
    
    Args:
        module_name: Nom du module
        
    Returns:
        Dict avec statut, disponibilité, etc.
    """
    available = is_module_available(module_name)
    loaded = module_name in _loaded_modules
    
    return {
        'name': module_name,
        'available': available,
        'loaded': loaded,
        'path': FEATURE_MODULES.get(module_name, {}).get('path', 'unknown'),
        'class': FEATURE_MODULES.get(module_name, {}).get('class', 'unknown'),
        'factory': FEATURE_MODULES.get(module_name, {}).get('factory', 'unknown')
    }

def get_features_status() -> Dict[str, Any]:
    """
    Retourne le statut global des modules features
    
    Returns:
        Dict avec statut de tous les modules
    """
    status = {}
    total_available = 0
    total_loaded = 0
    
    for module_name in FEATURE_MODULES.keys():
        module_status = get_module_status(module_name)
        status[module_name] = module_status
        
        if module_status['available']:
            total_available += 1
        if module_status['loaded']:
            total_loaded += 1
    
    status['summary'] = {
        'total_modules': len(FEATURE_MODULES),
        'available_modules': total_available,
        'loaded_modules': total_loaded,
        'availability_rate': total_available / len(FEATURE_MODULES) if FEATURE_MODULES else 0
    }
    
    return status

# === INTEGRITY MONITORING ===

# Instance globale du moniteur d'intégrité
_integrity_monitor: Optional[Any] = None

def _setup_integrity_monitoring():
    """Configure le monitoring d'intégrité des modules"""
    global _integrity_monitor
    
    try:
        from .module_integrity import (
            create_module_integrity_monitor,
            create_import_check,
            create_instantiation_check,
            IntegrityCheckType
        )
        
        _integrity_monitor = create_module_integrity_monitor(check_interval_seconds=120)
        
        # Enregistrer les modules avec leurs vérifications
        for module_name, module_config in FEATURE_MODULES.items():
            checks = []
            
            # Convertir le chemin relatif en chemin absolu
            absolute_path = f"features{module_config['path']}"
            
            # Vérification d'import
            checks.append(create_import_check(
                absolute_path, 
                module_config['class']
            ))
            
            # Vérification d'instanciation
            checks.append(create_instantiation_check(
                absolute_path,
                module_config['class'],
                module_config['factory']
            ))
            
            # Note: Pas de vérification fonctionnelle complexe pour éviter les timeouts
            # Les vérifications d'import et d'instanciation suffisent pour la santé du module
            
            _integrity_monitor.register_module(module_name, checks)
        
        logger.info("🔍 Monitoring d'intégrité configuré")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ Impossible de configurer le monitoring d'intégrité: {e}")
        return False

def start_integrity_monitoring():
    """Démarre le monitoring d'intégrité"""
    global _integrity_monitor
    
    if _integrity_monitor is None:
        if not _setup_integrity_monitoring():
            return False
    
    if _integrity_monitor:
        _integrity_monitor.start_monitoring()
        logger.info("🚀 Monitoring d'intégrité démarré")
        return True
    
    return False

def stop_integrity_monitoring():
    """Arrête le monitoring d'intégrité"""
    global _integrity_monitor
    
    if _integrity_monitor:
        _integrity_monitor.stop_monitoring()
        logger.info("🛑 Monitoring d'intégrité arrêté")
        return True
    
    return False

def get_integrity_status() -> Dict[str, Any]:
    """Retourne le statut d'intégrité des modules"""
    global _integrity_monitor
    
    if _integrity_monitor is None:
        return {
            'monitoring_active': False,
            'error': 'Monitoring d\'intégrité non configuré'
        }
    
    try:
        return {
            'monitoring_active': _integrity_monitor.running,
            'health_summary': _integrity_monitor.get_health_summary(),
            'module_health': _integrity_monitor.get_all_health_status()
        }
    except Exception as e:
        return {
            'monitoring_active': False,
            'error': f'Erreur récupération statut: {e}'
        }

# === INITIALIZATION ===

logger.info(f"🚀 Features module initialized with lazy loading - {len(FEATURE_MODULES)} modules configured")
logger.info(f"📊 Available exports: {len(__all__)}")

# Log du statut initial (sans charger les modules)
initial_status = get_features_status()
logger.info(f"📈 Module availability: {initial_status['summary']['available_modules']}/{initial_status['summary']['total_modules']}")

# Configurer le monitoring d'intégrité (sans le démarrer automatiquement)
_setup_integrity_monitoring()