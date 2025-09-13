"""
MIA_IA_SYSTEM - Monitoring et Observabilité
==========================================

Modules de monitoring, métriques et observabilité.
"""

from .metrics_collector import (
    MetricsCollector,
    get_metrics_collector,
    create_metrics_collector,
    record_signal_metric,
    record_trade_metric,
    record_kill_switch_metric,
    update_pnl_metric,
    update_latency_metric,
)

from .structured_logger import (
    StructuredLogger,
    get_structured_logger,
    setup_structured_logging,
    log_context,
)

from .metrics_exporter import (
    MetricsExporter,
    export_metrics,
    auto_export_metrics,
)

__all__ = [
    # Metrics Collector
    "MetricsCollector",
    "get_metrics_collector",
    "create_metrics_collector",
    "record_signal_metric",
    "record_trade_metric",
    "record_kill_switch_metric",
    "update_pnl_metric",
    "update_latency_metric",
    
    # Structured Logger
    "StructuredLogger",
    "get_structured_logger",
    "setup_structured_logging",
    "log_context",
    
    # Metrics Exporter
    "MetricsExporter",
    "export_metrics",
    "auto_export_metrics",
]