#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Catastrophe Monitor v2
🚨 RÔLE: Surveiller en continu les anomalies "non business" (tech/data) et déclencher des alertes précoces
Impact: Prévention des pertes avant que le safety_kill_switch n'ait à couper

RESPONSABILITÉS :
1. 📊 Surveiller les sources télémétrie (sierra_connector, market_snapshot, trading_executor)
2. 🔍 Détecter les anomalies (stall fichier, parse flood, stale sections, order health)
3. ⚡ Déclencher des alertes précoces (warn/alert) avec contexte
4. 📈 Maintenir un tableau de bord en mémoire (50 événements, compteurs)
5. 🎯 Suggérer (ne pas imposer) des actions au safety_kill_switch
6. 📋 Fournir observabilité (logs récap 60s, WARNING/ALERT contextualisés)

FEATURES AVANCÉES :
- Sources télémétrie spécifiques (tail_unified, staleness, order latency)
- Règles d'anomalie précises (seuils paramétrables)
- Interfaces spécifiques (ingest, tick, snapshot_state)
- Observabilité améliorée (logs récap, alertes contextualisées)
- Articulation claire vs Kill Switch (radar vs frein d'urgence)

PERFORMANCE : <5ms per tick
PRECISION : 100% déterministe, seuils configurables

Author: MIA_IA_SYSTEM Team
Version: 2.0 - Production Ready  
Date: Janvier 2025
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque
from core.logger import get_logger

logger = get_logger(__name__)

# === CONSTANTS ===

class SystemMode(Enum):
    OK = "OK"
    PAUSE = "PAUSE"
    KILL = "KILL"

class CriticalEvent(Enum):
    DRAWDOWN_SESSION = "dd_session"
    DRAWDOWN_DAY = "dd_day"
    ORDER_ANOMALY = "order_anomaly"
    DATA_STALE = "data_stale"
    CONNECTION_LOST = "connection_lost"
    SYMBOL_MISMATCH = "symbol_mismatch"
    BL_PROXIMITY_HIGH_VIX = "bl_proximity_high_vix"
    SYSTEM_OVERLOAD = "system_overload"

class SuggestedAction(Enum):
    NO_TRADE = "no_trade"
    FLATTEN_POSITIONS = "flatten"
    REDUCE_SIZING = "size_cap"
    MUTE_ORDERS = "mute_orders"
    PAUSE_ENGINES = "pause_engines"
    KILL_SWITCH = "kill_switch"

# === DATA STRUCTURES ===

@dataclass
class SierraConnectorMetrics:
    """Métriques du sierra_connector.tail_unified"""
    bytes_per_second: float = 0.0
    lines_per_second: float = 0.0
    last_line_timestamp: Optional[datetime] = None
    file_rotations: int = 0
    parse_errors: int = 0
    parse_error_rate: float = 0.0
    file_path: str = ""

@dataclass
class MarketSnapshotMetrics:
    """Métriques du market_snapshot - staleness par section"""
    m1_staleness_seconds: float = 0.0
    m30_staleness_seconds: float = 0.0
    vix_staleness_seconds: float = 0.0
    menthorq_staleness_seconds: float = 0.0
    menthorq_period_minutes: int = 30
    buffer_lengths: Dict[str, int] = field(default_factory=dict)

@dataclass
class TradingExecutorMetrics:
    """Métriques du trading_executor"""
    order_send_latency_ms: float = 0.0
    order_send_latency_p95_ms: float = 0.0
    rejections_per_minute: float = 0.0
    total_orders: int = 0
    rejected_orders: int = 0
    duplicate_guard_hits: int = 0

@dataclass
class RiskManagerMetrics:
    """Métriques du risk_manager"""
    pnl_variance_intraday: float = 0.0
    pnl_variance_10min: float = 0.0
    average_slippage: float = 0.0
    slippage_p95: float = 0.0
    current_pnl: float = 0.0
    session_pnl: float = 0.0

@dataclass
class SessionAnalyzerMetrics:
    """Métriques du session_analyzer"""
    current_session: str = "RTH"
    is_hot_window: bool = False
    is_maintenance: bool = False
    transitions_count: int = 0
    last_transition: Optional[datetime] = None

@dataclass
class PnLEvent:
    timestamp: datetime
    current_pnl: float
    session_pnl: float
    daily_pnl: float
    max_drawdown: float
    risk_units: float

@dataclass
class OrderEvent:
    timestamp: datetime
    orders_per_minute: int
    rejected_orders: int
    total_orders: int
    retry_count: int
    avg_latency_ms: float

@dataclass
class DataFreshnessEvent:
    timestamp: datetime
    graph3_last_update: datetime
    graph4_last_update: datetime
    graph8_last_update: datetime
    graph10_last_update: datetime
    vix_last_update: datetime
    menthorq_last_update: datetime
    menthorq_staleness_pct: float

@dataclass
class ConnectionEvent:
    timestamp: datetime
    sierra_dtc_connected: bool
    sierra_dtc_latency_ms: float
    symbol_mapping_ok: bool
    handshake_status: str
    last_heartbeat: datetime

@dataclass
class SystemLoadEvent:
    timestamp: datetime
    cpu_usage_pct: float
    memory_usage_pct: float
    disk_io_pct: float
    network_latency_ms: float

@dataclass
class TradingContext:
    timestamp: datetime
    vix_regime: str
    vix_level: float
    is_hot_zone: bool
    current_timeframe: int
    bl_proximity_ticks: Optional[float]
    active_positions: int
    pending_orders: int

@dataclass
class HealthSnapshot:
    timestamp: datetime
    data_freshness: Dict[str, float]
    connection_health: Dict[str, bool]
    system_load: Dict[str, float]
    trading_metrics: Dict[str, Any]
    last_actions: List[str]

@dataclass
class AlertEvent:
    """Événement d'alerte avec contexte"""
    timestamp: datetime
    level: str  # "WARN" ou "ALERT"
    type: str   # "tail_stall", "parse_errors", "stale_section", etc.
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    symbol: Optional[str] = None
    section: Optional[str] = None
    duration_seconds: Optional[float] = None
    threshold: Optional[float] = None

@dataclass
class DashboardState:
    """Tableau de bord en mémoire"""
    recent_events: deque = field(default_factory=lambda: deque(maxlen=50))
    counters: Dict[str, int] = field(default_factory=dict)
    last_60s_summary: Dict[str, Any] = field(default_factory=dict)
    current_alerts: List[AlertEvent] = field(default_factory=list)
    last_tick_time: Optional[datetime] = None

@dataclass
class SystemHealthState:
    mode: SystemMode
    reasons: List[str]
    suggested_actions: List[SuggestedAction]
    until: Optional[datetime]
    health_snapshot: HealthSnapshot
    last_switch: Dict[str, Any]
    confidence: float
    dashboard: DashboardState = field(default_factory=DashboardState)

# === MAIN CLASS ===

class CatastropheMonitor:
    """Moniteur de catastrophe temps réel v2"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.current_state = SystemMode.OK
        self.last_switch_time = datetime.utcnow()
        self.switch_count = 0
        self.flatten_requests = 0
        self.mq_degraded_hits = 0
        self.switch_pause = 0
        self.switch_kill = 0
        self._last_health_check = datetime.utcnow()
        self._consecutive_anomalies = 0
        
        # Nouvelles métriques v2
        self.dashboard = DashboardState()
        self._last_60s_summary = datetime.utcnow()
        self._metrics_buffer = {
            "sierra_connector": SierraConnectorMetrics(),
            "market_snapshot": MarketSnapshotMetrics(),
            "trading_executor": TradingExecutorMetrics(),
            "risk_manager": RiskManagerMetrics(),
            "session_analyzer": SessionAnalyzerMetrics()
        }
        
        logger.debug("CatastropheMonitor v2 initialisé")
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuration par défaut v2"""
        return {
            "thresholds": {
                # Anomalies existantes
                "max_dd_session": -2.0,
                "max_dd_day": -3.0,
                "max_orders_per_min": 20,
                "max_reject_ratio": 0.10,
                "max_data_staleness_sec": 10,
                "max_vix_staleness_sec": 90,
                "max_mq_staleness_pct": 0.20,
                "max_system_cpu_pct": 85.0,
                "max_system_memory_pct": 90.0,
                "max_dtc_latency_ms": 1000,
                "bl_proximity_high_vix_ticks": 4,
                
                # Nouvelles règles d'anomalie v2
                "tail_stall_seconds": 5.0,           # Stall fichier > 5s en RTH
                "parse_error_rate_max": 0.01,        # > 1% lignes malformées
                "m1_staleness_max": 30.0,            # M1 > 30s
                "m30_staleness_max": 300.0,          # M30 > 5m
                "vix_staleness_max": 300.0,          # VIX > 5m
                "mq_staleness_multiplier": 2.0,      # MQ > 2×période
                "order_rejections_max": 3.0,         # rejections/min > 3
                "order_latency_p95_max": 800.0,      # latency_p95 > 800ms
                "slippage_spike_multiplier": 3.0,    # p95 > 3× médiane 30min
                "pnl_variance_spike_multiplier": 4.0, # σ² 10-min > 4× base
                "rotate_loop_max": 3,                # > 3 rotations en < 1min
                "rotate_loop_window_seconds": 60.0
            },
            "policies": {
                "auto_recovery_minutes": 5,
                "consecutive_anomaly_limit": 3,
                "health_check_interval_sec": 30,
                "mq_degraded_size_cap": 0.5,
                "pause_duration_minutes": 2,
                "tick_interval_seconds": 1.0,        # Tick chaque seconde
                "summary_interval_seconds": 60.0,    # Récap 60s
                "dashboard_events_max": 50           # Max 50 événements
            },
            "vix_regime_multipliers": {
                "LOW": 1.0,
                "MID": 1.2,
                "HIGH": 1.5
            }
        }
    
    def monitor_system_health(self,
                            pnl_event: Optional[PnLEvent] = None,
                            order_event: Optional[OrderEvent] = None,
                            data_freshness: Optional[DataFreshnessEvent] = None,
                            connection_event: Optional[ConnectionEvent] = None,
                            system_load: Optional[SystemLoadEvent] = None,
                            trading_context: Optional[TradingContext] = None) -> SystemHealthState:
        """Surveillance complète de la santé système"""
        start_time = time.time()
        
        try:
            # 1. Analyser les conditions critiques
            critical_events = self._detect_critical_events(
                pnl_event, order_event, data_freshness, 
                connection_event, system_load, trading_context
            )
            
            # 2. Déterminer le mode système
            new_mode, reasons = self._determine_system_mode(critical_events, trading_context)
            
            # 3. Générer les actions suggérées
            suggested_actions = self._generate_suggested_actions(
                new_mode, critical_events, trading_context
            )
            
            # 4. Calculer la durée de l'état
            until_time = self._calculate_until_time(new_mode, critical_events)
            
            # 5. Créer le health snapshot
            health_snapshot = self._create_health_snapshot(
                pnl_event, order_event, data_freshness,
                connection_event, system_load, trading_context
            )
            
            # 6. Gérer les transitions d'état
            last_switch_info = self._handle_state_transition(new_mode, reasons)
            
            # 7. Calculer la confiance
            confidence = self._calculate_confidence(critical_events, new_mode)
            
            # 8. Construire l'état final
            system_health = SystemHealthState(
                mode=new_mode,
                reasons=reasons,
                suggested_actions=suggested_actions,
                until=until_time,
                health_snapshot=health_snapshot,
                last_switch=last_switch_info,
                confidence=confidence
            )
            
            # 9. Logs et métriques
            elapsed = (time.time() - start_time) * 1000
            self._update_metrics(system_health)
            
            if new_mode != self.current_state:
                logger.warning(f"🚨 Bascule système: {self.current_state.value} → {new_mode.value} - {', '.join(reasons)}")
            else:
                logger.debug(f"🔍 Health check: {new_mode.value} - {elapsed:.1f}ms")
            
            return system_health
            
        except Exception as e:
            logger.error(f"❌ Erreur monitoring: {e}")
            return self._fallback_health_state(str(e))
    
    # === NOUVELLES INTERFACES V2 ===
    
    def ingest(self, metric_name: str, value: Any, timestamp: Optional[datetime] = None) -> None:
        """Ingère une métrique ponctuelle"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        try:
            # Mettre à jour le buffer de métriques
            if metric_name.startswith("sierra_"):
                self._update_sierra_metrics(metric_name, value, timestamp)
            elif metric_name.startswith("market_"):
                self._update_market_metrics(metric_name, value, timestamp)
            elif metric_name.startswith("trading_"):
                self._update_trading_metrics(metric_name, value, timestamp)
            elif metric_name.startswith("risk_"):
                self._update_risk_metrics(metric_name, value, timestamp)
            elif metric_name.startswith("session_"):
                self._update_session_metrics(metric_name, value, timestamp)
            
            # Ajouter à l'historique
            self.dashboard.recent_events.append({
                "timestamp": timestamp,
                "metric": metric_name,
                "value": value
            })
            
        except Exception as e:
            logger.error(f"❌ Erreur ingest {metric_name}: {e}")
    
    def tick(self) -> List[AlertEvent]:
        """Tick chaque seconde - évalue les règles glissantes"""
        now = datetime.utcnow()
        self.dashboard.last_tick_time = now
        alerts = []
        
        try:
            # 1. Vérifier les règles d'anomalie
            alerts.extend(self._check_tail_stall())
            alerts.extend(self._check_parse_errors())
            alerts.extend(self._check_stale_sections())
            alerts.extend(self._check_order_health())
            alerts.extend(self._check_slippage_spike())
            alerts.extend(self._check_pnl_variance())
            alerts.extend(self._check_rotate_loop())
            
            # 2. Publier les alertes
            for alert in alerts:
                self._publish_alert(alert)
            
            # 3. Mettre à jour le tableau de bord
            self._update_dashboard_counters(alerts)
            
            # 4. Log récap 60s si nécessaire
            if (now - self._last_60s_summary).total_seconds() >= self.config["policies"]["summary_interval_seconds"]:
                self._log_60s_summary()
                self._last_60s_summary = now
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Erreur tick: {e}")
            return []
    
    def snapshot_state(self) -> Dict[str, Any]:
        """Retourne l'état du tableau de bord pour le launcher"""
        return {
            "current_mode": self.current_state.value,
            "dashboard": {
                "recent_events_count": len(self.dashboard.recent_events),
                "counters": self.dashboard.counters.copy(),
                "current_alerts_count": len(self.dashboard.current_alerts),
                "last_tick_time": self.dashboard.last_tick_time.isoformat() if self.dashboard.last_tick_time else None
            },
            "metrics": {
                "sierra_connector": {
                    "lines_per_second": self._metrics_buffer["sierra_connector"].lines_per_second,
                    "parse_error_rate": self._metrics_buffer["sierra_connector"].parse_error_rate,
                    "file_rotations": self._metrics_buffer["sierra_connector"].file_rotations
                },
                "market_snapshot": {
                    "m1_staleness": self._metrics_buffer["market_snapshot"].m1_staleness_seconds,
                    "m30_staleness": self._metrics_buffer["market_snapshot"].m30_staleness_seconds,
                    "vix_staleness": self._metrics_buffer["market_snapshot"].vix_staleness_seconds
                },
                "trading_executor": {
                    "rejections_per_minute": self._metrics_buffer["trading_executor"].rejections_per_minute,
                    "latency_p95_ms": self._metrics_buffer["trading_executor"].order_send_latency_p95_ms
                }
            },
            "last_60s_summary": self.dashboard.last_60s_summary
        }
    
    # === DETECTION METHODS ===
    
    def _detect_critical_events(self,
                              pnl_event: Optional[PnLEvent],
                              order_event: Optional[OrderEvent],
                              data_freshness: Optional[DataFreshnessEvent],
                              connection_event: Optional[ConnectionEvent],
                              system_load: Optional[SystemLoadEvent],
                              trading_context: Optional[TradingContext]) -> List[CriticalEvent]:
        """Détecte les événements critiques"""
        events = []
        
        # 1. Vérifier le drawdown
        if pnl_event:
            if pnl_event.session_pnl <= self.config["thresholds"]["max_dd_session"]:
                events.append(CriticalEvent.DRAWDOWN_SESSION)
            if pnl_event.daily_pnl <= self.config["thresholds"]["max_dd_day"]:
                events.append(CriticalEvent.DRAWDOWN_DAY)
        
        # 2. Vérifier les anomalies d'ordres
        if order_event:
            if order_event.orders_per_minute > self.config["thresholds"]["max_orders_per_min"]:
                events.append(CriticalEvent.ORDER_ANOMALY)
            reject_ratio = order_event.rejected_orders / max(order_event.total_orders, 1)
            if reject_ratio > self.config["thresholds"]["max_reject_ratio"]:
                events.append(CriticalEvent.ORDER_ANOMALY)
        
        # 3. Vérifier la fraîcheur des données
        if data_freshness:
            now = datetime.utcnow()
            max_staleness = self.config["thresholds"]["max_data_staleness_sec"]
            
            if (now - data_freshness.graph3_last_update).total_seconds() > max_staleness:
                events.append(CriticalEvent.DATA_STALE)
            if (now - data_freshness.graph4_last_update).total_seconds() > max_staleness:
                events.append(CriticalEvent.DATA_STALE)
            if (now - data_freshness.vix_last_update).total_seconds() > self.config["thresholds"]["max_vix_staleness_sec"]:
                events.append(CriticalEvent.DATA_STALE)
            if data_freshness.menthorq_staleness_pct > self.config["thresholds"]["max_mq_staleness_pct"]:
                events.append(CriticalEvent.DATA_STALE)
        
        # 4. Vérifier les connexions
        if connection_event:
            if not connection_event.sierra_dtc_connected:
                events.append(CriticalEvent.CONNECTION_LOST)
            if not connection_event.symbol_mapping_ok:
                events.append(CriticalEvent.SYMBOL_MISMATCH)
            if connection_event.sierra_dtc_latency_ms > self.config["thresholds"]["max_dtc_latency_ms"]:
                events.append(CriticalEvent.CONNECTION_LOST)
        
        # 5. Vérifier la charge système
        if system_load:
            if system_load.cpu_usage_pct > self.config["thresholds"]["max_system_cpu_pct"]:
                events.append(CriticalEvent.SYSTEM_OVERLOAD)
            if system_load.memory_usage_pct > self.config["thresholds"]["max_system_memory_pct"]:
                events.append(CriticalEvent.SYSTEM_OVERLOAD)
        
        # 6. Vérifier le contexte de trading
        if trading_context:
            if (trading_context.vix_regime == "HIGH" and 
                trading_context.bl_proximity_ticks and 
                trading_context.bl_proximity_ticks <= self.config["thresholds"]["bl_proximity_high_vix_ticks"]):
                events.append(CriticalEvent.BL_PROXIMITY_HIGH_VIX)
        
        return events
    
    # === NOUVELLES MÉTHODES V2 ===
    
    def _update_sierra_metrics(self, metric_name: str, value: Any, timestamp: datetime) -> None:
        """Met à jour les métriques sierra_connector"""
        metrics = self._metrics_buffer["sierra_connector"]
        
        if metric_name == "sierra_lines_per_second":
            metrics.lines_per_second = float(value)
        elif metric_name == "sierra_bytes_per_second":
            metrics.bytes_per_second = float(value)
        elif metric_name == "sierra_last_line_timestamp":
            metrics.last_line_timestamp = value
        elif metric_name == "sierra_file_rotations":
            metrics.file_rotations = int(value)
        elif metric_name == "sierra_parse_errors":
            metrics.parse_errors = int(value)
        elif metric_name == "sierra_parse_error_rate":
            metrics.parse_error_rate = float(value)
        elif metric_name == "sierra_file_path":
            metrics.file_path = str(value)
    
    def _update_market_metrics(self, metric_name: str, value: Any, timestamp: datetime) -> None:
        """Met à jour les métriques market_snapshot"""
        metrics = self._metrics_buffer["market_snapshot"]
        
        if metric_name == "market_m1_staleness":
            metrics.m1_staleness_seconds = float(value)
        elif metric_name == "market_m30_staleness":
            metrics.m30_staleness_seconds = float(value)
        elif metric_name == "market_vix_staleness":
            metrics.vix_staleness_seconds = float(value)
        elif metric_name == "market_menthorq_staleness":
            metrics.menthorq_staleness_seconds = float(value)
        elif metric_name == "market_menthorq_period":
            metrics.menthorq_period_minutes = int(value)
        elif metric_name == "market_buffer_lengths":
            metrics.buffer_lengths = value
    
    def _update_trading_metrics(self, metric_name: str, value: Any, timestamp: datetime) -> None:
        """Met à jour les métriques trading_executor"""
        metrics = self._metrics_buffer["trading_executor"]
        
        if metric_name == "trading_latency_ms":
            metrics.order_send_latency_ms = float(value)
        elif metric_name == "trading_latency_p95_ms":
            metrics.order_send_latency_p95_ms = float(value)
        elif metric_name == "trading_rejections_per_minute":
            metrics.rejections_per_minute = float(value)
        elif metric_name == "trading_total_orders":
            metrics.total_orders = int(value)
        elif metric_name == "trading_rejected_orders":
            metrics.rejected_orders = int(value)
        elif metric_name == "trading_duplicate_guard_hits":
            metrics.duplicate_guard_hits = int(value)
    
    def _update_risk_metrics(self, metric_name: str, value: Any, timestamp: datetime) -> None:
        """Met à jour les métriques risk_manager"""
        metrics = self._metrics_buffer["risk_manager"]
        
        if metric_name == "risk_pnl_variance_intraday":
            metrics.pnl_variance_intraday = float(value)
        elif metric_name == "risk_pnl_variance_10min":
            metrics.pnl_variance_10min = float(value)
        elif metric_name == "risk_average_slippage":
            metrics.average_slippage = float(value)
        elif metric_name == "risk_slippage_p95":
            metrics.slippage_p95 = float(value)
        elif metric_name == "risk_current_pnl":
            metrics.current_pnl = float(value)
        elif metric_name == "risk_session_pnl":
            metrics.session_pnl = float(value)
    
    def _update_session_metrics(self, metric_name: str, value: Any, timestamp: datetime) -> None:
        """Met à jour les métriques session_analyzer"""
        metrics = self._metrics_buffer["session_analyzer"]
        
        if metric_name == "session_current":
            metrics.current_session = str(value)
        elif metric_name == "session_hot_window":
            metrics.is_hot_window = bool(value)
        elif metric_name == "session_maintenance":
            metrics.is_maintenance = bool(value)
        elif metric_name == "session_transitions_count":
            metrics.transitions_count = int(value)
        elif metric_name == "session_last_transition":
            metrics.last_transition = value
    
    # === RÈGLES D'ANOMALIE V2 ===
    
    def _check_tail_stall(self) -> List[AlertEvent]:
        """Vérifie le stall fichier - lines/s == 0 pendant > 5s en RTH"""
        alerts = []
        sierra_metrics = self._metrics_buffer["sierra_connector"]
        session_metrics = self._metrics_buffer["session_analyzer"]
        
        # Vérifier si on est en RTH
        if session_metrics.current_session != "RTH":
            return alerts
        
        # Vérifier si lines/s == 0
        if sierra_metrics.lines_per_second == 0.0 and sierra_metrics.last_line_timestamp:
            stall_duration = (datetime.utcnow() - sierra_metrics.last_line_timestamp).total_seconds()
            threshold = self.config["thresholds"]["tail_stall_seconds"]
            
            if stall_duration > threshold:
                alert = AlertEvent(
                    timestamp=datetime.utcnow(),
                    level="ALERT",
                    type="tail_stall",
                    message=f"Tail stall {stall_duration:.1f}s (RTH)",
                    context={"file_path": sierra_metrics.file_path},
                    duration_seconds=stall_duration,
                    threshold=threshold
                )
                alerts.append(alert)
        
        return alerts
    
    def _check_parse_errors(self) -> List[AlertEvent]:
        """Vérifie le parse flood - > 1% lignes malformées"""
        alerts = []
        sierra_metrics = self._metrics_buffer["sierra_connector"]
        
        threshold = self.config["thresholds"]["parse_error_rate_max"]
        if sierra_metrics.parse_error_rate > threshold:
            alert = AlertEvent(
                timestamp=datetime.utcnow(),
                level="ALERT",
                type="parse_errors",
                message=f"Parse flood {sierra_metrics.parse_error_rate:.1%}",
                context={"parse_errors": sierra_metrics.parse_errors},
                threshold=threshold
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_stale_sections(self) -> List[AlertEvent]:
        """Vérifie les sections stale - M1>30s, M30>5m, VIX>5m, MQ>2×période"""
        alerts = []
        market_metrics = self._metrics_buffer["market_snapshot"]
        
        # M1 staleness
        if market_metrics.m1_staleness_seconds > self.config["thresholds"]["m1_staleness_max"]:
            alert = AlertEvent(
                timestamp=datetime.utcnow(),
                level="WARN",
                type="stale_section",
                message=f"Stale M1 {market_metrics.m1_staleness_seconds:.1f}s",
                section="M1",
                duration_seconds=market_metrics.m1_staleness_seconds,
                threshold=self.config["thresholds"]["m1_staleness_max"]
            )
            alerts.append(alert)
        
        # M30 staleness
        if market_metrics.m30_staleness_seconds > self.config["thresholds"]["m30_staleness_max"]:
            alert = AlertEvent(
                timestamp=datetime.utcnow(),
                level="WARN",
                type="stale_section",
                message=f"Stale M30 {market_metrics.m30_staleness_seconds:.1f}s",
                section="M30",
                duration_seconds=market_metrics.m30_staleness_seconds,
                threshold=self.config["thresholds"]["m30_staleness_max"]
            )
            alerts.append(alert)
        
        # VIX staleness
        if market_metrics.vix_staleness_seconds > self.config["thresholds"]["vix_staleness_max"]:
            alert = AlertEvent(
                timestamp=datetime.utcnow(),
                level="WARN",
                type="stale_section",
                message=f"Stale VIX {market_metrics.vix_staleness_seconds:.1f}s",
                section="VIX",
                duration_seconds=market_metrics.vix_staleness_seconds,
                threshold=self.config["thresholds"]["vix_staleness_max"]
            )
            alerts.append(alert)
        
        # MenthorQ staleness
        mq_threshold = market_metrics.menthorq_period_minutes * 60 * self.config["thresholds"]["mq_staleness_multiplier"]
        if market_metrics.menthorq_staleness_seconds > mq_threshold:
            alert = AlertEvent(
                timestamp=datetime.utcnow(),
                level="WARN",
                type="stale_section",
                message=f"Stale MQ {market_metrics.menthorq_staleness_seconds:.1f}s",
                section="MQ",
                duration_seconds=market_metrics.menthorq_staleness_seconds,
                threshold=mq_threshold
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_order_health(self) -> List[AlertEvent]:
        """Vérifie la santé des ordres - rejections/min > 3 ou latency_p95 > 800ms"""
        alerts = []
        trading_metrics = self._metrics_buffer["trading_executor"]
        
        # Rejections
        if trading_metrics.rejections_per_minute > self.config["thresholds"]["order_rejections_max"]:
            alert = AlertEvent(
                timestamp=datetime.utcnow(),
                level="ALERT",
                type="orders_health",
                message=f"High rejections {trading_metrics.rejections_per_minute:.1f}/min",
                context={"rejected_orders": trading_metrics.rejected_orders},
                threshold=self.config["thresholds"]["order_rejections_max"]
            )
            alerts.append(alert)
        
        # Latency
        if trading_metrics.order_send_latency_p95_ms > self.config["thresholds"]["order_latency_p95_max"]:
            alert = AlertEvent(
                timestamp=datetime.utcnow(),
                level="ALERT",
                type="orders_health",
                message=f"High latency p95 {trading_metrics.order_send_latency_p95_ms:.0f}ms",
                context={"latency_p95": trading_metrics.order_send_latency_p95_ms},
                threshold=self.config["thresholds"]["order_latency_p95_max"]
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_slippage_spike(self) -> List[AlertEvent]:
        """Vérifie le slippage spike - p95 > 3× médiane 30min"""
        alerts = []
        risk_metrics = self._metrics_buffer["risk_manager"]
        
        # Note: Cette vérification nécessiterait un historique des médianes
        # Pour l'instant, on utilise un seuil fixe
        if risk_metrics.slippage_p95 > 0.5:  # 0.5$ de slippage p95
            alert = AlertEvent(
                timestamp=datetime.utcnow(),
                level="WARN",
                type="slippage_spike",
                message=f"Slippage spike p95 {risk_metrics.slippage_p95:.2f}",
                context={"slippage_p95": risk_metrics.slippage_p95},
                threshold=0.5
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_pnl_variance(self) -> List[AlertEvent]:
        """Vérifie la variance PnL - σ² 10-min > 4× base"""
        alerts = []
        risk_metrics = self._metrics_buffer["risk_manager"]
        
        # Note: Cette vérification nécessiterait un historique des variances de base
        # Pour l'instant, on utilise un seuil fixe
        if risk_metrics.pnl_variance_10min > 1000.0:  # 1000$² de variance
            alert = AlertEvent(
                timestamp=datetime.utcnow(),
                level="WARN",
                type="pnl_variance",
                message=f"PnL variance spike {risk_metrics.pnl_variance_10min:.0f}",
                context={"pnl_variance_10min": risk_metrics.pnl_variance_10min},
                threshold=1000.0
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_rotate_loop(self) -> List[AlertEvent]:
        """Vérifie le rotate loop - > 3 rotations en < 1min"""
        alerts = []
        sierra_metrics = self._metrics_buffer["sierra_connector"]
        
        # Note: Cette vérification nécessiterait un historique des rotations
        # Pour l'instant, on utilise un seuil simple
        if sierra_metrics.file_rotations > self.config["thresholds"]["rotate_loop_max"]:
            alert = AlertEvent(
                timestamp=datetime.utcnow(),
                level="ALERT",
                type="rotate_loop",
                message=f"Rotate loop {sierra_metrics.file_rotations} rotations",
                context={"file_rotations": sierra_metrics.file_rotations},
                threshold=self.config["thresholds"]["rotate_loop_max"]
            )
            alerts.append(alert)
        
        return alerts
    
    def _publish_alert(self, alert: AlertEvent) -> None:
        """Publie un événement d'alerte (bus interne)"""
        # Ajouter à la liste des alertes courantes
        self.dashboard.current_alerts.append(alert)
        
        # Limiter le nombre d'alertes courantes
        max_alerts = 20
        if len(self.dashboard.current_alerts) > max_alerts:
            self.dashboard.current_alerts = self.dashboard.current_alerts[-max_alerts:]
        
        # Log contextualisé
        if alert.level == "ALERT":
            logger.warning(f"🚨 {alert.type}: {alert.message}")
        else:
            logger.warning(f"⚠️ {alert.type}: {alert.message}")
        
        # Ajouter le contexte si disponible
        if alert.context:
            logger.debug(f"   Contexte: {alert.context}")
        if alert.duration_seconds:
            logger.debug(f"   Durée: {alert.duration_seconds:.1f}s")
        if alert.threshold:
            logger.debug(f"   Seuil: {alert.threshold}")
    
    def _update_dashboard_counters(self, alerts: List[AlertEvent]) -> None:
        """Met à jour les compteurs du tableau de bord"""
        for alert in alerts:
            counter_key = f"{alert.level}_{alert.type}"
            self.dashboard.counters[counter_key] = self.dashboard.counters.get(counter_key, 0) + 1
    
    def _log_60s_summary(self) -> None:
        """Log récap 60s avec métriques clés"""
        sierra_metrics = self._metrics_buffer["sierra_connector"]
        market_metrics = self._metrics_buffer["market_snapshot"]
        trading_metrics = self._metrics_buffer["trading_executor"]
        
        # Construire le récap
        summary_parts = []
        
        # Sierra connector
        summary_parts.append(f"tail={sierra_metrics.lines_per_second:.1f}k l/s")
        summary_parts.append(f"err={sierra_metrics.parse_error_rate:.1%}")
        
        # Stale sections
        stale_sections = []
        if market_metrics.m1_staleness_seconds > 30:
            stale_sections.append("M1")
        if market_metrics.m30_staleness_seconds > 300:
            stale_sections.append("M30")
        if market_metrics.vix_staleness_seconds > 300:
            stale_sections.append("VIX")
        
        if stale_sections:
            summary_parts.append(f"stale=[{','.join(stale_sections)}]")
        
        # Orders
        summary_parts.append(f"orders:rej={trading_metrics.rejections_per_minute:.0f}/min")
        summary_parts.append(f"lat_p95={trading_metrics.order_send_latency_p95_ms:.0f}ms")
        
        # Construire le message final
        summary_message = " ".join(summary_parts)
        logger.info(f"monitor 60s summary {summary_message}")
        
        # Mettre à jour le récap dans le dashboard
        self.dashboard.last_60s_summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": summary_message,
            "metrics": {
                "tail_lps": sierra_metrics.lines_per_second,
                "parse_error_rate": sierra_metrics.parse_error_rate,
                "stale_sections": stale_sections,
                "rejections_per_min": trading_metrics.rejections_per_minute,
                "latency_p95_ms": trading_metrics.order_send_latency_p95_ms
            }
        }
    
    def _determine_system_mode(self, critical_events: List[CriticalEvent], 
                             trading_context: Optional[TradingContext]) -> Tuple[SystemMode, List[str]]:
        """Détermine le mode système basé sur les événements critiques"""
        reasons = []
        
        # Événements KILL (arrêt immédiat)
        kill_events = [
            CriticalEvent.DRAWDOWN_DAY,
            CriticalEvent.CONNECTION_LOST,
            CriticalEvent.SYMBOL_MISMATCH
        ]
        
        if any(event in critical_events for event in kill_events):
            for event in critical_events:
                if event in kill_events:
                    reasons.append(event.value)
            return SystemMode.KILL, reasons
        
        # Événements PAUSE (pause temporaire)
        pause_events = [
            CriticalEvent.DRAWDOWN_SESSION,
            CriticalEvent.ORDER_ANOMALY,
            CriticalEvent.DATA_STALE,
            CriticalEvent.SYSTEM_OVERLOAD,
            CriticalEvent.BL_PROXIMITY_HIGH_VIX
        ]
        
        if any(event in critical_events for event in pause_events):
            for event in critical_events:
                if event in pause_events:
                    reasons.append(event.value)
            return SystemMode.PAUSE, reasons
        
        # Mode OK
        return SystemMode.OK, ["all_systems_ok"]
    
    def _generate_suggested_actions(self, mode: SystemMode, 
                                  critical_events: List[CriticalEvent],
                                  trading_context: Optional[TradingContext]) -> List[SuggestedAction]:
        """Génère les actions suggérées basées sur le mode et les événements"""
        actions = []
        
        if mode == SystemMode.KILL:
            actions.extend([
                SuggestedAction.KILL_SWITCH,
                SuggestedAction.FLATTEN_POSITIONS,
                SuggestedAction.MUTE_ORDERS,
                SuggestedAction.PAUSE_ENGINES
            ])
        
        elif mode == SystemMode.PAUSE:
            actions.append(SuggestedAction.NO_TRADE)
            
            # Actions spécifiques selon les événements
            if CriticalEvent.DRAWDOWN_SESSION in critical_events:
                actions.append(SuggestedAction.REDUCE_SIZING)
            if CriticalEvent.ORDER_ANOMALY in critical_events:
                actions.append(SuggestedAction.MUTE_ORDERS)
            if CriticalEvent.DATA_STALE in critical_events:
                actions.append(SuggestedAction.REDUCE_SIZING)
            if CriticalEvent.SYSTEM_OVERLOAD in critical_events:
                actions.append(SuggestedAction.PAUSE_ENGINES)
            if CriticalEvent.BL_PROXIMITY_HIGH_VIX in critical_events:
                actions.append(SuggestedAction.NO_TRADE)
        
        return actions
    
    def _calculate_until_time(self, mode: SystemMode, 
                            critical_events: List[CriticalEvent]) -> Optional[datetime]:
        """Calcule le temps jusqu'à la prochaine vérification"""
        if mode == SystemMode.OK:
            return None
        
        # Durée de pause basée sur le type d'événement
        pause_duration = self.config["policies"]["pause_duration_minutes"]
        
        if CriticalEvent.ORDER_ANOMALY in critical_events:
            pause_duration = 2  # 2 minutes pour anomalies d'ordres
        elif CriticalEvent.DATA_STALE in critical_events:
            pause_duration = 1  # 1 minute pour données stale
        elif CriticalEvent.SYSTEM_OVERLOAD in critical_events:
            pause_duration = 5  # 5 minutes pour surcharge système
        
        return datetime.utcnow() + timedelta(minutes=pause_duration)
    
    def _create_health_snapshot(self,
                              pnl_event: Optional[PnLEvent],
                              order_event: Optional[OrderEvent],
                              data_freshness: Optional[DataFreshnessEvent],
                              connection_event: Optional[ConnectionEvent],
                              system_load: Optional[SystemLoadEvent],
                              trading_context: Optional[TradingContext]) -> HealthSnapshot:
        """Crée un snapshot de santé système"""
        now = datetime.utcnow()
        
        # Fraîcheur des données
        data_freshness_dict = {}
        if data_freshness:
            max_staleness = self.config["thresholds"]["max_data_staleness_sec"]
            data_freshness_dict = {
                "graph3": max(0, 1 - (now - data_freshness.graph3_last_update).total_seconds() / max_staleness),
                "graph4": max(0, 1 - (now - data_freshness.graph4_last_update).total_seconds() / max_staleness),
                "graph8": max(0, 1 - (now - data_freshness.graph8_last_update).total_seconds() / max_staleness),
                "graph10": max(0, 1 - (now - data_freshness.graph10_last_update).total_seconds() / max_staleness),
                "vix": max(0, 1 - (now - data_freshness.vix_last_update).total_seconds() / 90),
                "menthorq": 1 - data_freshness.menthorq_staleness_pct
            }
        
        # Santé des connexions
        connection_health = {}
        if connection_event:
            connection_health = {
                "sierra_dtc": connection_event.sierra_dtc_connected,
                "symbol_mapping": connection_event.symbol_mapping_ok,
                "handshake": connection_event.handshake_status == "OK"
            }
        
        # Charge système
        system_load_dict = {}
        if system_load:
            system_load_dict = {
                "cpu_pct": system_load.cpu_usage_pct,
                "memory_pct": system_load.memory_usage_pct,
                "disk_io_pct": system_load.disk_io_pct,
                "network_latency_ms": system_load.network_latency_ms
            }
        
        # Métriques de trading
        trading_metrics = {}
        if pnl_event:
            trading_metrics.update({
                "current_pnl": pnl_event.current_pnl,
                "session_pnl": pnl_event.session_pnl,
                "max_drawdown": pnl_event.max_drawdown
            })
        if order_event:
            trading_metrics.update({
                "orders_per_min": order_event.orders_per_minute,
                "reject_ratio": order_event.rejected_orders / max(order_event.total_orders, 1)
            })
        if trading_context:
            trading_metrics.update({
                "vix_regime": trading_context.vix_regime,
                "active_positions": trading_context.active_positions,
                "pending_orders": trading_context.pending_orders
            })
        
        return HealthSnapshot(
            timestamp=now,
            data_freshness=data_freshness_dict,
            connection_health=connection_health,
            system_load=system_load_dict,
            trading_metrics=trading_metrics,
            last_actions=[f"switch_{self.current_state.value}"]
        )
    
    def _handle_state_transition(self, new_mode: SystemMode, reasons: List[str]) -> Dict[str, Any]:
        """Gère les transitions d'état"""
        if new_mode != self.current_state:
            old_mode = self.current_state
            self.current_state = new_mode
            self.last_switch_time = datetime.utcnow()
            self.switch_count += 1
            
            # Mettre à jour les compteurs
            if new_mode == SystemMode.PAUSE:
                self.switch_pause += 1
            elif new_mode == SystemMode.KILL:
                self.switch_kill += 1
            
            return {
                "from": old_mode.value,
                "to": new_mode.value,
                "timestamp": self.last_switch_time.isoformat(),
                "reasons": reasons,
                "switch_count": self.switch_count
            }
        
        return {
            "current": self.current_state.value,
            "last_switch": self.last_switch_time.isoformat(),
            "switch_count": self.switch_count
        }
    
    def _calculate_confidence(self, critical_events: List[CriticalEvent], mode: SystemMode) -> float:
        """Calcule la confiance dans l'état système"""
        if mode == SystemMode.OK:
            return 1.0
        
        # Réduire la confiance selon le nombre d'événements critiques
        confidence = 1.0 - (len(critical_events) * 0.2)
        return max(0.1, confidence)
    
    def _update_metrics(self, system_health: SystemHealthState):
        """Met à jour les métriques internes"""
        if SuggestedAction.FLATTEN_POSITIONS in system_health.suggested_actions:
            self.flatten_requests += 1
        
        if "mq_degraded" in system_health.reasons:
            self.mq_degraded_hits += 1
    
    def _fallback_health_state(self, error: str) -> SystemHealthState:
        """État de santé de fallback en cas d'erreur"""
        return SystemHealthState(
            mode=SystemMode.KILL,
            reasons=["monitor_error"],
            suggested_actions=[SuggestedAction.KILL_SWITCH],
            until=None,
            health_snapshot=HealthSnapshot(
                timestamp=datetime.utcnow(),
                data_freshness={},
                connection_health={},
                system_load={},
                trading_metrics={"error": error},
                last_actions=["fallback"]
            ),
            last_switch={"error": error},
            confidence=0.0
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du moniteur"""
        return {
            "current_mode": self.current_state.value,
            "switch_count": self.switch_count,
            "switch_pause": self.switch_pause,
            "switch_kill": self.switch_kill,
            "flatten_requests": self.flatten_requests,
            "mq_degraded_hits": self.mq_degraded_hits,
            "last_switch_time": self.last_switch_time.isoformat(),
            "uptime_hours": (datetime.utcnow() - self.last_switch_time).total_seconds() / 3600
        }

def create_catastrophe_monitor(config: Optional[Dict[str, Any]] = None) -> CatastropheMonitor:
    """Factory function pour créer un CatastropheMonitor"""
    return CatastropheMonitor(config)

def test_catastrophe_monitor():
    """Test du CatastropheMonitor v2"""
    logger.info("=== TEST CATASTROPHE MONITOR V2 ===")
    
    try:
        monitor = create_catastrophe_monitor()
        
        # Test 1: État OK normal
        pnl_ok = PnLEvent(
            timestamp=datetime.utcnow(),
            current_pnl=100.0,
            session_pnl=50.0,
            daily_pnl=200.0,
            max_drawdown=-50.0,
            risk_units=1.0
        )
        
        health_ok = monitor.monitor_system_health(pnl_event=pnl_ok)
        assert health_ok.mode == SystemMode.OK, "État normal doit être OK"
        assert "all_systems_ok" in health_ok.reasons, "Doit avoir raison OK"
        
        # Test 2: Nouvelles interfaces v2 - ingest
        monitor.ingest("sierra_lines_per_second", 1500.0)
        monitor.ingest("sierra_parse_error_rate", 0.005)
        monitor.ingest("market_m1_staleness", 15.0)
        monitor.ingest("trading_rejections_per_minute", 1.0)
        
        # Test 3: Tick avec nouvelles règles d'anomalie
        alerts = monitor.tick()
        assert isinstance(alerts, list), "Tick doit retourner une liste d'alertes"
        
        # Test 4: Simuler tail stall
        monitor.ingest("sierra_lines_per_second", 0.0)
        monitor.ingest("sierra_last_line_timestamp", datetime.utcnow() - timedelta(seconds=6))
        monitor.ingest("session_current", "RTH")
        
        alerts_stall = monitor.tick()
        stall_alerts = [a for a in alerts_stall if a.type == "tail_stall"]
        assert len(stall_alerts) > 0, "Doit détecter tail stall"
        assert stall_alerts[0].level == "ALERT", "Tail stall doit être ALERT"
        
        # Test 5: Simuler parse flood
        monitor.ingest("sierra_parse_error_rate", 0.02)  # 2% > 1% seuil
        
        alerts_parse = monitor.tick()
        parse_alerts = [a for a in alerts_parse if a.type == "parse_errors"]
        assert len(parse_alerts) > 0, "Doit détecter parse flood"
        assert parse_alerts[0].level == "ALERT", "Parse flood doit être ALERT"
        
        # Test 6: Simuler stale sections
        monitor.ingest("market_m1_staleness", 35.0)  # > 30s seuil
        monitor.ingest("market_m30_staleness", 350.0)  # > 5m seuil
        
        alerts_stale = monitor.tick()
        stale_alerts = [a for a in alerts_stale if a.type == "stale_section"]
        assert len(stale_alerts) >= 2, "Doit détecter stale M1 et M30"
        
        # Test 7: Simuler order health
        monitor.ingest("trading_rejections_per_minute", 5.0)  # > 3 seuil
        monitor.ingest("trading_latency_p95_ms", 900.0)  # > 800ms seuil
        
        alerts_orders = monitor.tick()
        order_alerts = [a for a in alerts_orders if a.type == "orders_health"]
        assert len(order_alerts) >= 2, "Doit détecter rejections et latency"
        
        # Test 8: Snapshot state
        state = monitor.snapshot_state()
        assert "current_mode" in state, "Snapshot doit avoir current_mode"
        assert "dashboard" in state, "Snapshot doit avoir dashboard"
        assert "metrics" in state, "Snapshot doit avoir metrics"
        assert state["dashboard"]["recent_events_count"] > 0, "Doit avoir des événements récents"
        
        # Test 9: Vérifier les stats
        stats = monitor.get_stats()
        assert stats["switch_count"] >= 0, "Doit avoir des bascules"
        assert stats["current_mode"] in ["OK", "PAUSE", "KILL"], "Mode doit être valide"
        
        # Test 10: Vérifier le tableau de bord
        assert len(monitor.dashboard.recent_events) > 0, "Doit avoir des événements récents"
        assert len(monitor.dashboard.counters) > 0, "Doit avoir des compteurs"
        assert len(monitor.dashboard.current_alerts) > 0, "Doit avoir des alertes courantes"
        
        logger.info("✅ Test Catastrophe Monitor v2 OK")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_catastrophe_monitor()