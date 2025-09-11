#!/usr/bin/env python3
"""
🚀 EXECUTION IMPORTS OPTIMIZER - MIA_IA_SYSTEM
==============================================

Optimiseur d'imports pour le dossier execution/ afin d'améliorer les performances
et réduire les temps de chargement des modules.

Fonctionnalités:
- Imports paresseux (lazy imports)
- Cache des modules importés
- Gestion d'erreurs robuste
- Monitoring des performances d'import

Auteur: MIA_IA_SYSTEM
Version: 1.0.0
Date: Janvier 2025
"""

import sys
import time
import importlib
import threading
import logging
from typing import Dict, Any, Optional, Callable, Type
from functools import lru_cache
from dataclasses import dataclass
from pathlib import Path

# Configuration du logger
logger = logging.getLogger(__name__)

@dataclass
class ImportMetrics:
    """Métriques d'import pour monitoring"""
    module_name: str
    import_time_ms: float
    success: bool
    error: Optional[str] = None
    cache_hit: bool = False

class ExecutionImportsOptimizer:
    """Optimiseur d'imports pour les modules execution/"""
    
    def __init__(self):
        self._import_cache: Dict[str, Any] = {}
        self._import_metrics: Dict[str, ImportMetrics] = {}
        self._lock = threading.Lock()
        
        # Modules critiques avec priorités
        self._critical_modules = {
            'sierra_connector': 1,
            'risk_manager': 2,
            'simple_trader': 3,
            'trading_executor': 4,
            'sierra_dtc_connector': 5,
            'sierra_order_router': 6,
            'order_manager': 7,
            'post_mortem_analyzer': 8,
            'sierra_battle_navale_integrator': 9,
            'sierra_optimizer': 10,
            'trade_snapshotter': 11
        }
        
        logger.info("🚀 ExecutionImportsOptimizer initialisé")
    
    @lru_cache(maxsize=128)
    def get_module(self, module_name: str) -> Any:
        """
        Import paresseux avec cache LRU
        
        Args:
            module_name: Nom du module à importer
            
        Returns:
            Module importé ou None si erreur
        """
        start_time = time.perf_counter()
        
        try:
            with self._lock:
                # Vérifier le cache
                if module_name in self._import_cache:
                    import_time = (time.perf_counter() - start_time) * 1000
                    self._import_metrics[module_name] = ImportMetrics(
                        module_name=module_name,
                        import_time_ms=import_time,
                        success=True,
                        cache_hit=True
                    )
                    return self._import_cache[module_name]
                
                # Import du module
                full_module_name = f"execution.{module_name}"
                module = importlib.import_module(full_module_name)
                
                # Mise en cache
                self._import_cache[module_name] = module
                
                import_time = (time.perf_counter() - start_time) * 1000
                self._import_metrics[module_name] = ImportMetrics(
                    module_name=module_name,
                    import_time_ms=import_time,
                    success=True,
                    cache_hit=False
                )
                
                logger.debug(f"✅ Module {module_name} importé en {import_time:.2f}ms")
                return module
                
        except Exception as e:
            import_time = (time.perf_counter() - start_time) * 1000
            self._import_metrics[module_name] = ImportMetrics(
                module_name=module_name,
                import_time_ms=import_time,
                success=False,
                error=str(e)
            )
            logger.error(f"❌ Erreur import {module_name}: {e}")
            return None
    
    def get_class(self, module_name: str, class_name: str) -> Optional[Type]:
        """
        Récupère une classe spécifique d'un module
        
        Args:
            module_name: Nom du module
            class_name: Nom de la classe
            
        Returns:
            Classe ou None si erreur
        """
        try:
            module = self.get_module(module_name)
            if module and hasattr(module, class_name):
                return getattr(module, class_name)
            return None
        except Exception as e:
            logger.error(f"❌ Erreur récupération classe {class_name} de {module_name}: {e}")
            return None
    
    def create_instance(self, module_name: str, class_name: str, *args, **kwargs) -> Optional[Any]:
        """
        Crée une instance d'une classe avec import paresseux
        
        Args:
            module_name: Nom du module
            class_name: Nom de la classe
            *args: Arguments positionnels
            **kwargs: Arguments nommés
            
        Returns:
            Instance créée ou None si erreur
        """
        try:
            cls = self.get_class(module_name, class_name)
            if cls:
                return cls(*args, **kwargs)
            return None
        except Exception as e:
            logger.error(f"❌ Erreur création instance {class_name}: {e}")
            return None
    
    def preload_critical_modules(self) -> Dict[str, bool]:
        """
        Précharge les modules critiques par ordre de priorité
        
        Returns:
            Dict avec le statut de préchargement de chaque module
        """
        results = {}
        
        # Trier par priorité
        sorted_modules = sorted(
            self._critical_modules.items(),
            key=lambda x: x[1]
        )
        
        logger.info("🔄 Préchargement des modules critiques...")
        
        for module_name, priority in sorted_modules:
            try:
                start_time = time.perf_counter()
                module = self.get_module(module_name)
                load_time = (time.perf_counter() - start_time) * 1000
                
                if module:
                    results[module_name] = True
                    logger.info(f"✅ {module_name} préchargé en {load_time:.2f}ms (priorité {priority})")
                else:
                    results[module_name] = False
                    logger.warning(f"⚠️ Échec préchargement {module_name}")
                    
            except Exception as e:
                results[module_name] = False
                logger.error(f"❌ Erreur préchargement {module_name}: {e}")
        
        success_count = sum(results.values())
        total_count = len(results)
        logger.info(f"📊 Préchargement terminé: {success_count}/{total_count} modules")
        
        return results
    
    def get_import_metrics(self) -> Dict[str, Any]:
        """
        Retourne les métriques d'import
        
        Returns:
            Dict avec les métriques détaillées
        """
        if not self._import_metrics:
            return {"message": "Aucune métrique disponible"}
        
        # Calculs statistiques
        successful_imports = [m for m in self._import_metrics.values() if m.success]
        failed_imports = [m for m in self._import_metrics.values() if not m.success]
        
        if successful_imports:
            avg_import_time = sum(m.import_time_ms for m in successful_imports) / len(successful_imports)
            max_import_time = max(m.import_time_ms for m in successful_imports)
            min_import_time = min(m.import_time_ms for m in successful_imports)
        else:
            avg_import_time = max_import_time = min_import_time = 0.0
        
        cache_hits = sum(1 for m in self._import_metrics.values() if m.cache_hit)
        total_imports = len(self._import_metrics)
        cache_hit_rate = (cache_hits / total_imports * 100) if total_imports > 0 else 0
        
        return {
            "total_modules": total_imports,
            "successful_imports": len(successful_imports),
            "failed_imports": len(failed_imports),
            "success_rate": (len(successful_imports) / total_imports * 100) if total_imports > 0 else 0,
            "cache_hit_rate": cache_hit_rate,
            "performance": {
                "avg_import_time_ms": round(avg_import_time, 2),
                "max_import_time_ms": round(max_import_time, 2),
                "min_import_time_ms": round(min_import_time, 2)
            },
            "failed_modules": [m.module_name for m in failed_imports],
            "detailed_metrics": {
                name: {
                    "import_time_ms": round(metrics.import_time_ms, 2),
                    "success": metrics.success,
                    "cache_hit": metrics.cache_hit,
                    "error": metrics.error
                }
                for name, metrics in self._import_metrics.items()
            }
        }
    
    def clear_cache(self) -> None:
        """Vide le cache d'imports"""
        with self._lock:
            self._import_cache.clear()
            self.get_module.cache_clear()
            logger.info("🧹 Cache d'imports vidé")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Vérification de santé de l'optimiseur
        
        Returns:
            Dict avec le statut de santé
        """
        try:
            # Test d'import d'un module critique
            test_module = self.get_module('sierra_connector')
            
            # Vérification cache
            cache_size = len(self._import_cache)
            
            # Vérification métriques
            metrics = self.get_import_metrics()
            
            health_status = {
                "status": "healthy" if test_module else "degraded",
                "cache_size": cache_size,
                "total_imports": metrics.get("total_modules", 0),
                "success_rate": metrics.get("success_rate", 0),
                "avg_import_time_ms": metrics.get("performance", {}).get("avg_import_time_ms", 0),
                "last_check": time.time()
            }
            
            return health_status
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_check": time.time()
            }

# Instance globale de l'optimiseur
_import_optimizer = None

def get_import_optimizer() -> ExecutionImportsOptimizer:
    """Retourne l'instance globale de l'optimiseur"""
    global _import_optimizer
    if _import_optimizer is None:
        _import_optimizer = ExecutionImportsOptimizer()
    return _import_optimizer

# Fonctions de convenance pour les imports optimisés
def get_sierra_connector(*args, **kwargs):
    """Import optimisé de SierraConnector"""
    optimizer = get_import_optimizer()
    return optimizer.create_instance('sierra_connector', 'SierraConnector', *args, **kwargs)

def get_risk_manager(*args, **kwargs):
    """Import optimisé de RiskManager"""
    optimizer = get_import_optimizer()
    return optimizer.create_instance('risk_manager', 'RiskManager', *args, **kwargs)

def get_simple_trader(*args, **kwargs):
    """Import optimisé de MIAAutomationSystem"""
    optimizer = get_import_optimizer()
    return optimizer.create_instance('simple_trader', 'MIAAutomationSystem', *args, **kwargs)

def get_trading_executor(*args, **kwargs):
    """Import optimisé de TradingExecutor"""
    optimizer = get_import_optimizer()
    return optimizer.create_instance('trading_executor', 'TradingExecutor', *args, **kwargs)

def get_sierra_dtc_connector(*args, **kwargs):
    """Import optimisé de SierraDTCConnector"""
    optimizer = get_import_optimizer()
    return optimizer.create_instance('sierra_dtc_connector', 'SierraDTCConnector', *args, **kwargs)

def get_sierra_order_router(*args, **kwargs):
    """Import optimisé de SierraOrderRouter"""
    optimizer = get_import_optimizer()
    return optimizer.create_instance('sierra_order_router', 'SierraOrderRouter', *args, **kwargs)

def get_order_manager(*args, **kwargs):
    """Import optimisé de OrderManager"""
    optimizer = get_import_optimizer()
    return optimizer.create_instance('order_manager', 'OrderManager', *args, **kwargs)

# Fonction de préchargement pour les lanceurs
def preload_execution_modules() -> Dict[str, bool]:
    """Précharge tous les modules execution/ critiques"""
    optimizer = get_import_optimizer()
    return optimizer.preload_critical_modules()

# Fonction de monitoring pour les lanceurs
def get_execution_import_metrics() -> Dict[str, Any]:
    """Retourne les métriques d'import pour monitoring"""
    optimizer = get_import_optimizer()
    return optimizer.get_import_metrics()

if __name__ == "__main__":
    # Test de l'optimiseur
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print("🧪 Test ExecutionImportsOptimizer")
    
    optimizer = get_import_optimizer()
    
    # Test préchargement
    results = optimizer.preload_critical_modules()
    print(f"📊 Résultats préchargement: {results}")
    
    # Test métriques
    metrics = optimizer.get_import_metrics()
    print(f"📈 Métriques: {metrics}")
    
    # Test health check
    health = optimizer.health_check()
    print(f"🏥 Health Check: {health}")
    
    print("✅ Test terminé")
