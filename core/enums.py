#!/usr/bin/env python3
"""
🔧 ENUMS CENTRALISÉS - MIA_IA_SYSTEM
====================================

Module centralisé pour tous les enums du système MIA_IA.
Élimine les doublons et assure la cohérence des définitions.

MIGRATION SÉCURISÉE :
- Toutes les définitions d'enums dupliquées sont centralisées ici
- Les anciens imports continuent de fonctionner via des alias
- Migration progressive sans casser le système existant

ENUMS CENTRALISÉS :
- AlertLevel : Niveaux d'alerte système
- AlertSeverity : Sévérité des alertes
- AlertCategory : Catégories d'alertes
- PerformanceMetric : Métriques de performance
- PerformancePeriod : Périodes d'analyse
- ComponentStatus : Status des composants
- MetricType : Types de métriques
"""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, timezone

# === ALERT ENUMS ===

class AlertLevel(Enum):
    """
    Niveaux d'alerte système - DÉFINITION CENTRALISÉE
    
    Remplace les doublons dans :
    - monitoring/alert_system.py
    - core/menthorq_staleness_monitor.py
    - monitoring/performance_tracker.py
    - scripts/analyze_performance.py
    """
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"
    
    @classmethod
    def from_string(cls, level_str: str) -> 'AlertLevel':
        """Conversion depuis string"""
        level_map = {
            'info': cls.INFO,
            'warning': cls.WARNING,
            'critical': cls.CRITICAL,
            'emergency': cls.EMERGENCY
        }
        return level_map.get(level_str.lower(), cls.INFO)
    
    @property
    def priority(self) -> int:
        """Priorité numérique pour tri"""
        priority_map = {
            self.INFO: 1,
            self.WARNING: 2,
            self.CRITICAL: 3,
            self.EMERGENCY: 4
        }
        return priority_map[self]


class AlertSeverity(Enum):
    """
    Sévérité des alertes - DÉFINITION CENTRALISÉE
    
    Remplace les doublons dans :
    - monitoring/alert_system.py
    - performance/automation_metrics.py
    - monitoring/live_monitor.py
    """
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"
    
    @classmethod
    def from_string(cls, severity_str: str) -> 'AlertSeverity':
        """Conversion depuis string"""
        severity_map = {
            'info': cls.INFO,
            'warning': cls.WARNING,
            'error': cls.ERROR,
            'critical': cls.CRITICAL,
            'emergency': cls.EMERGENCY
        }
        return severity_map.get(severity_str.lower(), cls.INFO)
    
    @property
    def priority(self) -> int:
        """Priorité numérique pour tri"""
        priority_map = {
            self.INFO: 1,
            self.WARNING: 2,
            self.ERROR: 3,
            self.CRITICAL: 4,
            self.EMERGENCY: 5
        }
        return priority_map[self]


class AlertCategory(Enum):
    """
    Catégories d'alertes - DÉFINITION CENTRALISÉE
    """
    SYSTEM = "system"
    TRADING = "trading"
    PERFORMANCE = "performance"
    RISK = "risk"
    DATA = "data"
    CONNECTION = "connection"
    MENTHORQ = "menthorq"
    EXECUTION = "execution"
    MONITORING = "monitoring"
    
    @classmethod
    def from_string(cls, category_str: str) -> 'AlertCategory':
        """Conversion depuis string"""
        category_map = {
            'system': cls.SYSTEM,
            'trading': cls.TRADING,
            'performance': cls.PERFORMANCE,
            'risk': cls.RISK,
            'data': cls.DATA,
            'connection': cls.CONNECTION,
            'menthorq': cls.MENTHORQ,
            'execution': cls.EXECUTION,
            'monitoring': cls.MONITORING
        }
        return category_map.get(category_str.lower(), cls.SYSTEM)


# === PERFORMANCE ENUMS ===

class PerformanceMetric(Enum):
    """
    Métriques de performance - DÉFINITION CENTRALISÉE
    
    Remplace les doublons dans :
    - monitoring/performance_tracker.py
    - monitoring/live_monitor.py
    """
    # Métriques de base
    GROSS_PNL = "gross_pnl"
    NET_PNL = "net_pnl"
    WIN_RATE = "win_rate"
    PROFIT_FACTOR = "profit_factor"
    
    # Métriques de risque
    MAX_DRAWDOWN = "max_drawdown"
    SHARPE_RATIO = "sharpe_ratio"
    SORTINO_RATIO = "sortino_ratio"
    CALMAR_RATIO = "calmar_ratio"
    
    # Métriques avancées
    VAR = "var"
    EXPECTED_SHORTFALL = "expected_shortfall"
    ALPHA = "alpha"
    BETA = "beta"
    
    # Métriques de trading
    TOTAL_TRADES = "total_trades"
    WINNING_TRADES = "winning_trades"
    LOSING_TRADES = "losing_trades"
    AVERAGE_WIN = "average_win"
    AVERAGE_LOSS = "average_loss"
    
    # Métriques de temps
    HOLDING_TIME = "holding_time"
    RECOVERY_TIME = "recovery_time"
    
    @classmethod
    def from_string(cls, metric_str: str) -> 'PerformanceMetric':
        """Conversion depuis string"""
        metric_map = {metric.value: metric for metric in cls}
        return metric_map.get(metric_str.lower(), cls.GROSS_PNL)


class PerformancePeriod(Enum):
    """
    Périodes d'analyse performance - DÉFINITION CENTRALISÉE
    """
    INTRADAY = "intraday"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    INCEPTION = "inception"
    
    @classmethod
    def from_string(cls, period_str: str) -> 'PerformancePeriod':
        """Conversion depuis string"""
        period_map = {period.value: period for period in cls}
        return period_map.get(period_str.lower(), cls.DAILY)


# === COMPONENT ENUMS ===

class ComponentStatus(Enum):
    """
    Status des composants système - DÉFINITION CENTRALISÉE
    """
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_string(cls, status_str: str) -> 'ComponentStatus':
        """Conversion depuis string"""
        status_map = {status.value: status for status in cls}
        return status_map.get(status_str.lower(), cls.UNKNOWN)


class MetricType(Enum):
    """
    Types de métriques - DÉFINITION CENTRALISÉE
    """
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    DURATION = "duration"
    PERCENTAGE = "percentage"
    ERROR_TRACKING = "error_tracking"
    
    @classmethod
    def from_string(cls, type_str: str) -> 'MetricType':
        """Conversion depuis string"""
        type_map = {type_val.value: type_val for type_val in cls}
        return type_map.get(type_str.lower(), cls.GAUGE)


# === ALIAS DE COMPATIBILITÉ ===

# Pour assurer la compatibilité avec les anciens imports
# Ces alias permettent aux anciens codes de continuer à fonctionner

# Alias pour AlertLevel (compatibilité)
AlertLevel = AlertLevel  # Redéfinition pour compatibilité

# Alias pour AlertSeverity (compatibilité)
AlertSeverity = AlertSeverity  # Redéfinition pour compatibilité

# Alias pour les autres enums
AlertCategory = AlertCategory
PerformanceMetric = PerformanceMetric
PerformancePeriod = PerformancePeriod
ComponentStatus = ComponentStatus
MetricType = MetricType


# === UTILITAIRES ===

def get_enum_by_name(enum_name: str) -> Optional[Enum]:
    """
    Récupère un enum par son nom (utile pour la sérialisation)
    """
    enum_map = {
        'AlertLevel': AlertLevel,
        'AlertSeverity': AlertSeverity,
        'AlertCategory': AlertCategory,
        'PerformanceMetric': PerformanceMetric,
        'PerformancePeriod': PerformancePeriod,
        'ComponentStatus': ComponentStatus,
        'MetricType': MetricType
    }
    return enum_map.get(enum_name)


def serialize_enum(enum_value: Enum) -> Dict[str, Any]:
    """
    Sérialise un enum pour stockage/transmission
    """
    return {
        'enum_type': enum_value.__class__.__name__,
        'value': enum_value.value,
        'name': enum_value.name
    }


def deserialize_enum(enum_data: Dict[str, Any]) -> Optional[Enum]:
    """
    Désérialise un enum depuis stockage/transmission
    """
    enum_class = get_enum_by_name(enum_data.get('enum_type'))
    if enum_class:
        return enum_class(enum_data.get('value'))
    return None


# === EXPORTS ===

__all__ = [
    'AlertLevel',
    'AlertSeverity', 
    'AlertCategory',
    'PerformanceMetric',
    'PerformancePeriod',
    'ComponentStatus',
    'MetricType',
    'get_enum_by_name',
    'serialize_enum',
    'deserialize_enum'
]

