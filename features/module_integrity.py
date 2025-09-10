"""
MIA_IA_SYSTEM - Module Integrity Monitor
========================================

Système de monitoring de l'intégrité des modules features.
- Détection des modules défaillants
- Monitoring de performance
- Alertes en temps réel
- Statistiques de santé

Version: Production Ready v1.0
Performance: <1ms pour vérifications d'intégrité
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import weakref

from core.logger import get_logger

logger = get_logger(__name__)

# === INTEGRITY STATUS ===

class ModuleHealthStatus(Enum):
    """Statut de santé d'un module"""
    HEALTHY = "HEALTHY"           # Module fonctionnel
    DEGRADED = "DEGRADED"         # Module avec problèmes mineurs
    FAILING = "FAILING"           # Module avec erreurs fréquentes
    CRITICAL = "CRITICAL"         # Module complètement défaillant
    UNKNOWN = "UNKNOWN"           # Statut non déterminé

class IntegrityCheckType(Enum):
    """Types de vérifications d'intégrité"""
    IMPORT_CHECK = "IMPORT_CHECK"         # Vérification d'import
    INSTANTIATION_CHECK = "INSTANTIATION_CHECK"  # Vérification d'instanciation
    FUNCTIONALITY_CHECK = "FUNCTIONALITY_CHECK"  # Vérification fonctionnelle
    PERFORMANCE_CHECK = "PERFORMANCE_CHECK"      # Vérification de performance

# === INTEGRITY METRICS ===

@dataclass
class IntegrityMetrics:
    """Métriques d'intégrité d'un module"""
    module_name: str
    health_status: ModuleHealthStatus = ModuleHealthStatus.UNKNOWN
    
    # Compteurs
    total_checks: int = 0
    successful_checks: int = 0
    failed_checks: int = 0
    errors: int = 0
    
    # Performance
    average_response_time_ms: float = 0.0
    last_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    
    # Timestamps
    first_check: Optional[datetime] = None
    last_check: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    
    # Historique des erreurs
    recent_errors: deque = field(default_factory=lambda: deque(maxlen=10))
    
    @property
    def success_rate(self) -> float:
        """Taux de succès (0.0 à 1.0)"""
        if self.total_checks == 0:
            return 0.0
        return self.successful_checks / self.total_checks
    
    @property
    def error_rate(self) -> float:
        """Taux d'erreur (0.0 à 1.0)"""
        if self.total_checks == 0:
            return 0.0
        return self.failed_checks / self.total_checks
    
    @property
    def uptime_percentage(self) -> float:
        """Pourcentage de disponibilité"""
        if self.total_checks == 0:
            return 0.0
        return (self.successful_checks / self.total_checks) * 100
    
    def update_health_status(self):
        """Met à jour le statut de santé basé sur les métriques"""
        if self.total_checks == 0:
            self.health_status = ModuleHealthStatus.UNKNOWN
        elif self.success_rate >= 0.95:
            self.health_status = ModuleHealthStatus.HEALTHY
        elif self.success_rate >= 0.80:
            self.health_status = ModuleHealthStatus.DEGRADED
        elif self.success_rate >= 0.50:
            self.health_status = ModuleHealthStatus.FAILING
        else:
            self.health_status = ModuleHealthStatus.CRITICAL

# === INTEGRITY CHECK ===

@dataclass
class IntegrityCheck:
    """Configuration d'une vérification d'intégrité"""
    check_type: IntegrityCheckType
    check_function: Callable[[], bool]
    timeout_seconds: float = 5.0
    retry_count: int = 2
    critical: bool = False  # Si True, échec = module critique

# === MODULE INTEGRITY MONITOR ===

class ModuleIntegrityMonitor:
    """
    Moniteur d'intégrité des modules features
    
    Fonctionnalités:
    - Vérifications périodiques d'intégrité
    - Détection automatique des problèmes
    - Alertes en temps réel
    - Statistiques de santé
    """
    
    def __init__(self, check_interval_seconds: int = 60):
        """
        Initialise le moniteur d'intégrité
        
        Args:
            check_interval_seconds: Intervalle entre les vérifications (défaut: 60s)
        """
        self.check_interval = check_interval_seconds
        self.metrics: Dict[str, IntegrityMetrics] = {}
        self.checks: Dict[str, List[IntegrityCheck]] = defaultdict(list)
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.RLock()
        
        # Configuration des seuils d'alerte
        self.alert_thresholds = {
            'error_rate': 0.1,      # 10% d'erreurs
            'response_time_ms': 1000,  # 1 seconde
            'success_rate': 0.8     # 80% de succès
        }
        
        logger.info("🔍 ModuleIntegrityMonitor initialisé")
    
    def register_module(self, module_name: str, checks: List[IntegrityCheck]):
        """
        Enregistre un module pour le monitoring
        
        Args:
            module_name: Nom du module
            checks: Liste des vérifications à effectuer
        """
        with self.lock:
            self.checks[module_name] = checks
            if module_name not in self.metrics:
                self.metrics[module_name] = IntegrityMetrics(module_name)
            
            logger.info(f"📋 Module enregistré: {module_name} ({len(checks)} vérifications)")
    
    def start_monitoring(self):
        """Démarre le monitoring en arrière-plan"""
        if self.running:
            logger.warning("⚠️ Monitoring déjà en cours")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info(f"🚀 Monitoring démarré (intervalle: {self.check_interval}s)")
    
    def stop_monitoring(self):
        """Arrête le monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        
        logger.info("🛑 Monitoring arrêté")
    
    def _monitor_loop(self):
        """Boucle principale de monitoring"""
        while self.running:
            try:
                self._run_all_checks()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Erreur dans la boucle de monitoring: {e}")
                time.sleep(5)  # Attendre avant de réessayer
    
    def _run_all_checks(self):
        """Exécute toutes les vérifications d'intégrité"""
        with self.lock:
            for module_name, checks in self.checks.items():
                self._run_module_checks(module_name, checks)
    
    def _run_module_checks(self, module_name: str, checks: List[IntegrityCheck]):
        """Exécute les vérifications pour un module"""
        metrics = self.metrics[module_name]
        
        for check in checks:
            try:
                start_time = time.time()
                success = self._execute_check(check)
                response_time = (time.time() - start_time) * 1000
                
                # Mettre à jour les métriques
                metrics.total_checks += 1
                metrics.last_check = datetime.now()
                metrics.last_response_time_ms = response_time
                metrics.max_response_time_ms = max(metrics.max_response_time_ms, response_time)
                
                if metrics.first_check is None:
                    metrics.first_check = datetime.now()
                
                if success:
                    metrics.successful_checks += 1
                    metrics.last_success = datetime.now()
                else:
                    metrics.failed_checks += 1
                    metrics.last_failure = datetime.now()
                    metrics.errors += 1
                    
                    # Ajouter à l'historique des erreurs
                    error_info = {
                        'timestamp': datetime.now(),
                        'check_type': check.check_type.value,
                        'response_time_ms': response_time,
                        'critical': check.critical
                    }
                    metrics.recent_errors.append(error_info)
                
                # Mettre à jour le temps de réponse moyen
                total_time = metrics.average_response_time_ms * (metrics.total_checks - 1)
                metrics.average_response_time_ms = (total_time + response_time) / metrics.total_checks
                
                # Mettre à jour le statut de santé
                metrics.update_health_status()
                
                # Vérifier les seuils d'alerte
                self._check_alert_thresholds(module_name, metrics)
                
            except Exception as e:
                logger.error(f"❌ Erreur vérification {module_name}: {e}")
                metrics.errors += 1
                metrics.failed_checks += 1
    
    def _execute_check(self, check: IntegrityCheck) -> bool:
        """Exécute une vérification d'intégrité"""
        try:
            # Exécuter avec timeout (compatible Windows)
            import threading
            import time
            
            result = [None]
            exception = [None]
            
            def run_check():
                try:
                    result[0] = check.check_function()
                except Exception as e:
                    exception[0] = e
            
            # Lancer la vérification dans un thread
            thread = threading.Thread(target=run_check, daemon=True)
            thread.start()
            thread.join(timeout=check.timeout_seconds)
            
            # Vérifier si le thread est encore actif (timeout)
            if thread.is_alive():
                logger.warning(f"⏰ Timeout vérification: {check.check_type.value}")
                return False
            
            # Vérifier s'il y a eu une exception
            if exception[0]:
                raise exception[0]
            
            return bool(result[0])
            
        except TimeoutError:
            logger.warning(f"⏰ Timeout vérification: {check.check_type.value}")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur vérification {check.check_type.value}: {e}")
            return False
    
    def _check_alert_thresholds(self, module_name: str, metrics: IntegrityMetrics):
        """Vérifie les seuils d'alerte et génère des alertes"""
        alerts = []
        
        # Vérifier le taux d'erreur
        if metrics.error_rate > self.alert_thresholds['error_rate']:
            alerts.append(f"Taux d'erreur élevé: {metrics.error_rate:.1%}")
        
        # Vérifier le temps de réponse
        if metrics.last_response_time_ms > self.alert_thresholds['response_time_ms']:
            alerts.append(f"Temps de réponse lent: {metrics.last_response_time_ms:.1f}ms")
        
        # Vérifier le taux de succès
        if metrics.success_rate < self.alert_thresholds['success_rate']:
            alerts.append(f"Taux de succès faible: {metrics.success_rate:.1%}")
        
        # Générer les alertes
        if alerts:
            alert_message = f"🚨 ALERTE {module_name}: {', '.join(alerts)}"
            logger.warning(alert_message)
    
    def get_module_health(self, module_name: str) -> Optional[IntegrityMetrics]:
        """Retourne les métriques de santé d'un module"""
        with self.lock:
            return self.metrics.get(module_name)
    
    def get_all_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Retourne le statut de santé de tous les modules"""
        with self.lock:
            status = {}
            for module_name, metrics in self.metrics.items():
                status[module_name] = {
                    'health_status': metrics.health_status.value,
                    'success_rate': metrics.success_rate,
                    'error_rate': metrics.error_rate,
                    'uptime_percentage': metrics.uptime_percentage,
                    'average_response_time_ms': metrics.average_response_time_ms,
                    'total_checks': metrics.total_checks,
                    'errors': metrics.errors,
                    'last_check': metrics.last_check.isoformat() if metrics.last_check else None,
                    'last_success': metrics.last_success.isoformat() if metrics.last_success else None,
                    'last_failure': metrics.last_failure.isoformat() if metrics.last_failure else None
                }
            return status
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de la santé globale"""
        with self.lock:
            total_modules = len(self.metrics)
            healthy_modules = sum(1 for m in self.metrics.values() 
                                if m.health_status == ModuleHealthStatus.HEALTHY)
            degraded_modules = sum(1 for m in self.metrics.values() 
                                 if m.health_status == ModuleHealthStatus.DEGRADED)
            failing_modules = sum(1 for m in self.metrics.values() 
                                if m.health_status == ModuleHealthStatus.FAILING)
            critical_modules = sum(1 for m in self.metrics.values() 
                                 if m.health_status == ModuleHealthStatus.CRITICAL)
            
            return {
                'total_modules': total_modules,
                'healthy_modules': healthy_modules,
                'degraded_modules': degraded_modules,
                'failing_modules': failing_modules,
                'critical_modules': critical_modules,
                'overall_health_percentage': (healthy_modules / max(1, total_modules)) * 100,
                'monitoring_active': self.running,
                'check_interval_seconds': self.check_interval
            }
    
    def force_check(self, module_name: Optional[str] = None):
        """Force une vérification immédiate"""
        with self.lock:
            if module_name:
                if module_name in self.checks:
                    self._run_module_checks(module_name, self.checks[module_name])
                    logger.info(f"🔍 Vérification forcée: {module_name}")
                else:
                    logger.warning(f"⚠️ Module non trouvé: {module_name}")
            else:
                self._run_all_checks()
                logger.info("🔍 Vérification forcée: tous les modules")

# === FACTORY FUNCTIONS ===

def create_integrity_check(check_type: IntegrityCheckType, 
                          check_function: Callable[[], bool],
                          timeout_seconds: float = 5.0,
                          critical: bool = False) -> IntegrityCheck:
    """Factory pour créer une vérification d'intégrité"""
    return IntegrityCheck(
        check_type=check_type,
        check_function=check_function,
        timeout_seconds=timeout_seconds,
        critical=critical
    )

def create_module_integrity_monitor(check_interval_seconds: int = 60) -> ModuleIntegrityMonitor:
    """Factory pour créer un moniteur d'intégrité"""
    return ModuleIntegrityMonitor(check_interval_seconds)

# === INTEGRITY CHECK FUNCTIONS ===

def create_import_check(module_path: str, class_name: str) -> IntegrityCheck:
    """Crée une vérification d'import"""
    def check_import():
        try:
            import importlib
            module = importlib.import_module(module_path)
            return hasattr(module, class_name)
        except Exception:
            return False
    
    return create_integrity_check(
        IntegrityCheckType.IMPORT_CHECK,
        check_import,
        timeout_seconds=2.0
    )

def create_instantiation_check(module_path: str, class_name: str, 
                              factory_function: Optional[str] = None) -> IntegrityCheck:
    """Crée une vérification d'instanciation"""
    def check_instantiation():
        try:
            import importlib
            module = importlib.import_module(module_path)
            
            if factory_function and hasattr(module, factory_function):
                factory = getattr(module, factory_function)
                instance = factory()
                return instance is not None
            elif hasattr(module, class_name):
                cls = getattr(module, class_name)
                instance = cls()
                return instance is not None
            else:
                return False
        except Exception:
            return False
    
    return create_integrity_check(
        IntegrityCheckType.INSTANTIATION_CHECK,
        check_instantiation,
        timeout_seconds=5.0
    )

def create_functionality_check(test_function: Callable[[], bool]) -> IntegrityCheck:
    """Crée une vérification fonctionnelle"""
    return create_integrity_check(
        IntegrityCheckType.FUNCTIONALITY_CHECK,
        test_function,
        timeout_seconds=10.0,
        critical=True
    )

# === TESTING ===

def test_module_integrity_monitor():
    """Test du moniteur d'intégrité"""
    logger.info("🧪 Test ModuleIntegrityMonitor...")
    
    # Créer le moniteur
    monitor = create_module_integrity_monitor(check_interval_seconds=5)
    
    # Enregistrer quelques modules de test
    test_checks = [
        create_import_check('features.confluence_analyzer', 'ConfluenceAnalyzer'),
        create_instantiation_check('features.confluence_analyzer', 'ConfluenceAnalyzer'),
        create_functionality_check(lambda: True)  # Test simple
    ]
    
    monitor.register_module('test_module', test_checks)
    
    # Démarrer le monitoring
    monitor.start_monitoring()
    
    # Attendre quelques vérifications
    time.sleep(8)
    
    # Vérifier les résultats
    health = monitor.get_module_health('test_module')
    if health:
        logger.info(f"✅ Santé module: {health.health_status.value}")
        logger.info(f"   Taux de succès: {health.success_rate:.1%}")
        logger.info(f"   Temps de réponse moyen: {health.average_response_time_ms:.1f}ms")
    
    # Afficher le résumé
    summary = monitor.get_health_summary()
    logger.info(f"📊 Résumé santé: {summary}")
    
    # Arrêter le monitoring
    monitor.stop_monitoring()
    
    logger.info("✅ Test ModuleIntegrityMonitor terminé")
    return True

if __name__ == "__main__":
    test_module_integrity_monitor()
