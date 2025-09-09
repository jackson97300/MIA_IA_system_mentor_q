#!/usr/bin/env python3
"""
🔧 IMPORTS MANAGER - MIA_IA_SYSTEM
Gestionnaire centralisé des imports pour éviter les imports circulaires,
nettoyer les legacy IBKR/Polygon/DTC, et fournir une interface unique.
"""

import importlib
import sys
import time
from typing import Optional, Any, Dict, Callable, Union
from functools import lru_cache
import threading
import logging

logger = logging.getLogger(__name__)

# Thread-safe cache for lazy imports
_import_cache: Dict[str, Any] = {}
_import_lock = threading.Lock()
_import_stats: Dict[str, Any] = {
    "loaded": [],
    "lazy": [],
    "missing": [],
    "start_time": time.time()
}

class ImportsManager:
    """Gestionnaire centralisé des imports avec nettoyage legacy et protection anti-circular"""
    
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
        self._circular_check = set()
        
        # Modules legacy à supprimer
        self._legacy_modules = {
            'ibkr_connector', 'ibkr_connector3', 'tws_connector', 'tws_*',
            'polygon_connector', 'polygon_*', 'sierra_connector', 'dtc_*'
        }
        
        logger.info("ImportsManager initialisé avec nettoyage legacy")
    
    def require(self, module_name: str, purpose: str) -> Any:
        """
        Import obligatoire d'un module avec message d'erreur explicite
        
        Args:
            module_name: Nom du module à importer
            purpose: Raison de l'import (pour le message d'erreur)
            
        Returns:
            Module importé
            
        Raises:
            ImportError: Si le module n'est pas disponible
        """
        try:
            module = importlib.import_module(module_name)
            _import_stats["loaded"].append(module_name)
            logger.debug(f"Module requis chargé: {module_name} pour {purpose}")
            return module
        except ImportError as e:
            error_msg = f"Module requis manquant: {module_name} pour {purpose}\n"
            error_msg += f"Erreur: {e}\n"
            error_msg += f"Solution: Vérifiez que le fichier {module_name.replace('.', '/')}.py existe"
            _import_stats["missing"].append(module_name)
            logger.error(error_msg)
            raise ImportError(error_msg)
    
    def optional(self, module_name: str) -> Optional[Any]:
        """
        Import optionnel d'un module
        
        Args:
            module_name: Nom du module à importer
            
        Returns:
            Module importé ou None si absent
        """
        try:
            module = importlib.import_module(module_name)
            _import_stats["loaded"].append(module_name)
            logger.debug(f"Module optionnel chargé: {module_name}")
            return module
        except ImportError:
            _import_stats["missing"].append(module_name)
            logger.info(f"Module optionnel manquant: {module_name}")
            return None
    
    def lazy_import(self, module_path: str, class_name: str = None) -> Callable:
        """
        Import paresseux d'un module ou d'une classe
        
        Args:
            module_path: Chemin du module (ex: 'features.confluence_analyzer')
            class_name: Nom de la classe (optionnel)
            
        Returns:
            Factory function qui importe et retourne l'objet
        """
        cache_key = f"{module_path}.{class_name}" if class_name else module_path
        _import_stats["lazy"].append(cache_key)
        
        def _import_factory():
            with self._lock:
                if cache_key in self._cache:
                    return self._cache[cache_key]
                
                try:
                    # Vérification anti-circular
                    if cache_key in self._circular_check:
                        logger.warning(f"Import circulaire détecté: {cache_key}")
                        return self._create_stub_class(class_name or module_path.split('.')[-1])
                    
                    self._circular_check.add(cache_key)
                    
                    module = importlib.import_module(module_path)
                    if class_name:
                        obj = getattr(module, class_name)
                    else:
                        obj = module
                    
                    self._cache[cache_key] = obj
                    _import_stats["loaded"].append(cache_key)
                    logger.debug(f"Import paresseux réussi: {cache_key}")
                    return obj
                    
                except ImportError as e:
                    logger.warning(f"Import paresseux échoué: {cache_key} - {e}")
                    return self._create_stub_class(class_name or module_path.split('.')[-1])
                finally:
                    self._circular_check.discard(cache_key)
        
        return _import_factory
    
    def get_module(self, name: str) -> Optional[Any]:
        """
        Récupère un module avec gestion d'erreur
        
        Args:
            name: Nom du module
            
        Returns:
            Module ou None si absent
        """
        try:
            return importlib.import_module(name)
        except ImportError as e:
            logger.warning(f"Module non disponible: {name} - {e}")
            return None
    
    def _create_stub_class(self, name: str):
        """Crée une classe stub inerte pour les imports échoués"""
        class StubClass:
            def __init__(self, *args, **kwargs):
                logger.warning(f"Utilisation d'un stub pour {name}")
                pass
            
            def __call__(self, *args, **kwargs):
                logger.warning(f"Appel sur un stub pour {name}")
                return None
            
            def __getattr__(self, name):
                logger.warning(f"Accès à l'attribut {name} sur un stub")
                return lambda *args, **kwargs: None
        
        StubClass.__name__ = f"Stub{name}"
        return StubClass
    
    def report(self) -> Dict[str, Any]:
        """
        Retourne un rapport sur l'état des imports
        
        Returns:
            Dict avec les statistiques d'import
        """
        elapsed = time.time() - _import_stats["start_time"]
        
        return {
            "loaded_count": len(_import_stats["loaded"]),
            "lazy_count": len(_import_stats["lazy"]),
            "missing_count": len(_import_stats["missing"]),
            "elapsed_seconds": round(elapsed, 2),
            "loaded_modules": _import_stats["loaded"],
            "lazy_modules": _import_stats["lazy"],
            "missing_modules": _import_stats["missing"]
        }

# Instance globale
import_manager = ImportsManager()

# === STUBS POUR MODULES LEGACY SUPPRIMÉS ===

class NotAvailable:
    """Classe stub pour les modules legacy supprimés"""
    def __init__(self, *args, **kwargs):
        logger.warning("Tentative d'utilisation d'un module legacy supprimé (IBKR/Polygon/DTC)")
        raise ImportError("Module legacy supprimé - utilisez les nouveaux connecteurs")
    
    def __call__(self, *args, **kwargs):
        raise ImportError("Module legacy supprimé - utilisez les nouveaux connecteurs")
    
    def __getattr__(self, name):
        raise ImportError("Module legacy supprimé - utilisez les nouveaux connecteurs")

# Stubs pour les modules legacy
IBKRConnector = NotAvailable
PolygonConnector = NotAvailable
SierraConnector = NotAvailable
TWSConnector = NotAvailable

# === NOUVELLES FONCTIONS D'IMPORT ===

def require(module_name: str, purpose: str) -> Any:
    """Import obligatoire d'un module"""
    return import_manager.require(module_name, purpose)

def optional(module_name: str) -> Optional[Any]:
    """Import optionnel d'un module"""
    return import_manager.optional(module_name)

def lazy_import(module_path: str, class_name: str = None) -> Callable:
    """Import paresseux d'un module ou d'une classe"""
    return import_manager.lazy_import(module_path, class_name)

def get_module(name: str) -> Optional[Any]:
    """Récupère un module avec gestion d'erreur"""
    return import_manager.get_module(name)

# === LAZY IMPORTS POUR LES MODULES PRINCIPAUX (NETTOYÉS) ===

def get_confluence_analyzer():
    """Import paresseux du ConfluenceAnalyzer"""
    factory = import_manager.lazy_import('features.confluence_analyzer', 'ConfluenceAnalyzer')
    return factory()

def get_feature_calculator():
    """Import paresseux du FeatureCalculator"""
    factory = import_manager.lazy_import('features.feature_calculator', 'FeatureCalculator')
    return factory()

def get_battle_navale_detector():
    """Import paresseux du BattleNavaleDetector"""
    factory = import_manager.lazy_import('core.battle_navale', 'BattleNavaleDetector')
    return factory()

def get_risk_manager():
    """Import paresseux du RiskManager"""
    factory = import_manager.lazy_import('automation_modules.risk_manager', 'RiskManager')
    return factory()

def get_trading_engine():
    """Import paresseux du TradingEngine"""
    factory = import_manager.lazy_import('automation_modules.trading_engine', 'MIAAutomationSystem')
    return factory()

def get_performance_tracker():
    """Import paresseux du PerformanceTracker"""
    factory = import_manager.lazy_import('monitoring.performance_tracker', 'PerformanceTracker')
    return factory()

def get_market_regime_detector():
    """Import paresseux du MarketRegimeDetector"""
    factory = import_manager.lazy_import('features.market_regime', 'MarketRegimeDetector')
    return factory()

def get_signal_generator():
    """Import paresseux du SignalGenerator"""
    factory = import_manager.lazy_import('strategies.signal_generator', 'SignalGenerator')
    return factory()

def get_elite_snapshots_system():
    """Import paresseux du Elite Snapshots System"""
    factory = import_manager.lazy_import('features.elite_snapshots_system', 'EliteSnapshotsSystem')
    return factory()

def get_create_real_snapshot():
    """Import paresseux du create_real_snapshot"""
    factory = import_manager.lazy_import('features.create_real_snapshot', 'create_real_snapshot')
    return factory()

# === NOUVEAUX CONNECTEURS (remplacent les legacy) ===

def get_sierra_connector():
    """Import paresseux du SierraConnector (remplace IBKR)"""
    factory = import_manager.lazy_import('features.sierra_connector', 'SierraConnector')
    return factory()

def get_menthorq_integration():
    """Import paresseux du MenthorqIntegration"""
    factory = import_manager.lazy_import('features.menthorq_integration', 'MenthorqIntegration')
    return factory()

# === FONCTION DE RAPPORT PRINCIPALE ===

def report() -> Dict[str, Any]:
    """
    Retourne un rapport complet sur l'état des imports
    
    Returns:
        Dict avec les statistiques d'import pour le launcher
    """
    return import_manager.report()

def log_import_status():
    """Log le statut des imports au démarrage du système"""
    report_data = report()
    
    logger.info(f"imports: loaded={report_data['loaded_count']} "
               f"lazy={report_data['lazy_count']} "
               f"missing={report_data['missing_count']} "
               f"({', '.join(report_data['missing_modules'][:3])} "
               f"{'...' if len(report_data['missing_modules']) > 3 else ''})")

# === UTILITAIRES D'IMPORT (NETTOYÉS) ===

@lru_cache(maxsize=128)
def safe_import(module_path: str, class_name: str = None, default=None):
    """
    Import sécurisé avec cache (compatibilité)
    
    Args:
        module_path: Chemin du module
        class_name: Nom de la classe (optionnel)
        default: Valeur par défaut si l'import échoue
        
    Returns:
        Module ou classe importé, ou default si échec
    """
    try:
        module = importlib.import_module(module_path)
        if class_name:
            return getattr(module, class_name)
        return module
    except (ImportError, AttributeError):
        return default

def check_import_available(module_path: str, class_name: str = None) -> bool:
    """
    Vérifie si un import est disponible sans l'importer
    
    Args:
        module_path: Chemin du module
        class_name: Nom de la classe (optionnel)
        
    Returns:
        True si l'import est disponible
    """
    try:
        module = importlib.import_module(module_path)
        if class_name:
            return hasattr(module, class_name)
        return True
    except ImportError:
        return False

# === FACTORY FUNCTIONS CENTRALISÉES (NETTOYÉES) ===

def create_components_lazy():
    """
    Crée les composants principaux avec imports paresseux
    
    Returns:
        Dict avec les factory functions des composants
    """
    return {
        'confluence_analyzer': get_confluence_analyzer,
        'feature_calculator': get_feature_calculator,
        'battle_navale_detector': get_battle_navale_detector,
        'risk_manager': get_risk_manager,
        'trading_engine': get_trading_engine,
        'performance_tracker': get_performance_tracker,
        'market_regime_detector': get_market_regime_detector,
        'signal_generator': get_signal_generator,
        'sierra_connector': get_sierra_connector,
        'menthorq_integration': get_menthorq_integration,
    }

def create_component_safe(component_name: str, *args, **kwargs):
    """
    Crée un composant de manière sécurisée
    
    Args:
        component_name: Nom du composant
        *args, **kwargs: Arguments pour le constructeur
        
    Returns:
        Instance du composant ou None si échec
    """
    factories = create_components_lazy()
    
    if component_name not in factories:
        raise ValueError(f"Unknown component: {component_name}")
    
    try:
        component_class = factories[component_name]()
        return component_class(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Could not create {component_name}: {e}")
        return None

# === VALIDATION D'IMPORTS (NETTOYÉE) ===

def validate_all_imports() -> Dict[str, str]:
    """
    Valide tous les imports principaux (sans legacy)
    
    Returns:
        Dictionnaire avec le statut de chaque import
    """
    results = {}
    
    # Test des imports principaux (sans legacy)
    test_imports = [
        ('core.logger', 'get_logger'),
        ('core.base_types', 'MarketData'),
        ('core.battle_navale', 'BattleNavaleDetector'),
        ('features.feature_calculator', 'FeatureCalculator'),
        ('automation_modules.trading_engine', 'MIAAutomationSystem'),
        ('strategies.signal_generator', 'SignalGenerator'),
        ('features.sierra_connector', 'SierraConnector'),
        ('features.menthorq_integration', 'MenthorqIntegration'),
    ]
    
    for module_path, class_name in test_imports:
        try:
            safe_import(module_path, class_name)
            results[f"{module_path}.{class_name}"] = "✅ OK"
        except Exception as e:
            results[f"{module_path}.{class_name}"] = f"❌ {str(e)}"
    
    return results

# === INITIALISATION DU SYSTÈME ===

def initialize_imports():
    """Initialise le système d'imports et log le statut"""
    log_import_status()
    
    # Vérifier les imports critiques
    critical_modules = [
        'core.market_hours_manager',
        'core.patterns_detector', 
        'core.mentor_system'
    ]
    
    for module_name in critical_modules:
        try:
            import_manager.require(module_name, 'système critique')
        except ImportError as e:
            logger.error(f"Module critique manquant: {e}")

if __name__ == "__main__":
    # Test du gestionnaire d'imports
    print("🔧 Test du gestionnaire d'imports...")
    
    # Initialiser le système
    initialize_imports()
    
    # Valider tous les imports
    validation_results = validate_all_imports()
    
    print("\n📊 Résultats de validation:")
    for import_path, status in validation_results.items():
        print(f"  {import_path}: {status}")
    
    # Afficher le rapport
    print("\n📋 Rapport d'imports:")
    report_data = report()
    print(f"  Chargés: {report_data['loaded_count']}")
    print(f"  Lazy: {report_data['lazy_count']}")
    print(f"  Manquants: {report_data['missing_count']}")
    print(f"  Temps: {report_data['elapsed_seconds']}s")