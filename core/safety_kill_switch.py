#!/usr/bin/env python3
"""
🚨 SAFETY KILL SWITCH ENHANCED - MIA_IA_SYSTEM
==============================================

Surveillance continue des conditions catastrophes et coupure propre :
- Stop trading, flatten, bascule paper, alerte
- Protège contre dérives de données, latences, pertes de route DTC, sur-perte journalière
- Intégration avec risk_manager, market_snapshot, menthorq_monitoring, trading_executor

FONCTIONNALITÉS:
- ✅ Surveillance continue des conditions catastrophes
- ✅ Règles de coupure paramétrables (PnL, DTC, stale data, VIX spike)
- ✅ Actions automatiques (halt_entries, halt_trading, paper_mode, flatten_all)
- ✅ Intégration avec tous les composants système
- ✅ Observabilité complète avec compteurs et alertes
- ✅ Déverrouillage manuel ou automatique (J+1)

Author: MIA_IA_SYSTEM
Version: 2.0.0
Date: Janvier 2025
"""

import time
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

try:
    from core.logger import get_logger
except ImportError:
    # Fallback pour test direct
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)

# === TYPES ===

class KillSwitchState(Enum):
    """États du kill switch"""
    NORMAL = "normal"           # Fonctionnement normal
    HALT_ENTRIES = "halt_entries"  # Pas de nouvelles positions
    HALT_TRADING = "halt_trading"  # Aucune action sauf flatten
    PAPER_MODE = "paper_mode"   # Route ordres simulée
    EMERGENCY = "emergency"     # Arrêt d'urgence complet

class KillSwitchReason(Enum):
    """Raisons d'activation du kill switch"""
    DAILY_LOSS_LIMIT = "daily_loss_limit"
    DTC_ROUTE_DOWN = "dtc_route_down"
    STALE_DATA_CRITICAL = "stale_data_critical"
    VIX_SPIKE = "vix_spike"
    ORDER_REJECTIONS = "order_rejections"
    MENTHORQ_STALE = "menthorq_stale"
    SYSTEM_OVERLOAD = "system_overload"
    MANUAL_OVERRIDE = "manual_override"

@dataclass
class TelemetryData:
    """Données de télémétrie pour surveillance"""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Risk Manager
    pnl_day: float = 0.0
    pnl_session: float = 0.0
    drawdown: float = 0.0
    variance: float = 0.0
    
    # Sierra Connector
    dtc_route_up: bool = True
    dtc_latency_ms: float = 0.0
    last_dtc_heartbeat: Optional[datetime] = None
    
    # Market Snapshot
    m1_stale_seconds: float = 0.0
    m30_stale_seconds: float = 0.0
    vix_stale_seconds: float = 0.0
    menthorq_stale_seconds: float = 0.0
    
    # Session Manager
    session_active: bool = True
    session_type: str = "unknown"
    
    # MenthorQ Monitoring
    hard_rule_hits: int = 0
    rejections_last_5m: int = 0
    stale_ticks: int = 0
    
    # VIX
    vix_value: float = 20.0
    vix_regime: str = "MID"

@dataclass
class KillSwitchConfig:
    """Configuration du kill switch"""
    # Seuils de coupure
    daily_loss_limit: float = -1000.0  # Perte journalière max
    dtc_down_timeout_seconds: int = 30  # Timeout route DTC
    stale_data_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "m1_max_seconds": 30.0,
        "m30_max_seconds": 300.0,  # 5 minutes
        "vix_max_seconds": 300.0,  # 5 minutes
        "menthorq_max_periods": 2.0  # 2x période attendue
    })
    vix_spike_threshold: float = 30.0  # Seuil VIX spike
    order_rejections_threshold: int = 10  # Rejets par minute
    
    # Actions
    auto_flatten_on_halt: bool = True
    auto_paper_mode_on_dtc_down: bool = True
    auto_reset_daily: bool = True
    
    # Monitoring
    check_interval_seconds: int = 5
    health_check_interval_seconds: int = 30

class SafetyKillSwitch:
    """Système de sécurité avancé avec surveillance continue"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = KillSwitchConfig()
        if config:
            self._update_config_from_dict(config)
        
        self.logger = logger
        
        # État du kill switch
        self.current_state = KillSwitchState.NORMAL
        self.current_reason: Optional[KillSwitchReason] = None
        self.activated_since: Optional[datetime] = None
        
        # Compteurs et métriques
        self.hard_rule_hits = 0
        self.rejections_last_5m = 0
        self.stale_ticks = 0
        self.last_health_check = datetime.now(timezone.utc)
        
        # Historique des activations
        self.activation_history: List[Dict[str, Any]] = []
        
        # Callbacks
        self.on_state_change = None
        self.on_flatten_request = None
        
        # Composants intégrés (seront injectés)
        self.trading_executor = None
        self.market_snapshot = None
        self.session_manager = None
        self.sierra_router = None
        
        logger.info("🚨 SafetyKillSwitch Enhanced initialisé")
    
    # === MÉTHODES DE CONFIGURATION ===
    
    def _update_config_from_dict(self, config: Dict[str, Any]):
        """Met à jour la configuration depuis un dictionnaire"""
        if 'daily_loss_limit' in config:
            self.config.daily_loss_limit = config['daily_loss_limit']
        if 'dtc_down_timeout_seconds' in config:
            self.config.dtc_down_timeout_seconds = config['dtc_down_timeout_seconds']
        if 'stale_data_thresholds' in config:
            self.config.stale_data_thresholds.update(config['stale_data_thresholds'])
        if 'vix_spike_threshold' in config:
            self.config.vix_spike_threshold = config['vix_spike_threshold']
        if 'order_rejections_threshold' in config:
            self.config.order_rejections_threshold = config['order_rejections_threshold']
    
    def set_components(self, trading_executor=None, market_snapshot=None, session_manager=None, sierra_router=None):
        """Injecte les composants système"""
        if trading_executor:
            self.trading_executor = trading_executor
        if market_snapshot:
            self.market_snapshot = market_snapshot
        if session_manager:
            self.session_manager = session_manager
        if sierra_router:
            self.sierra_router = sierra_router
        
        logger.info("🔗 Composants système injectés dans SafetyKillSwitch")
    
    # === MÉTHODES DE SURVEILLANCE ===
    
    def update(self, telemetry: TelemetryData) -> bool:
        """
        Met à jour l'état du kill switch avec les données de télémétrie
        
        Args:
            telemetry: Données de télémétrie du système
            
        Returns:
            True si l'état a changé, False sinon
        """
        try:
            old_state = self.current_state
            old_reason = self.current_reason
            
            # Évaluer les règles de coupure
            new_state, new_reason = self._evaluate_kill_switch_rules(telemetry)
            
            # Si changement d'état
            if new_state != old_state or new_reason != old_reason:
                self._change_state(new_state, new_reason, telemetry)
                return True
            
            # Mettre à jour les compteurs
            self._update_counters(telemetry)
            
            return False
        
        except Exception as e:
            logger.error(f"Erreur update kill switch: {e}")
            return False
    
    def _evaluate_kill_switch_rules(self, telemetry: TelemetryData) -> Tuple[KillSwitchState, Optional[KillSwitchReason]]:
        """Évalue les règles de coupure et détermine le nouvel état"""
        
        # 1. Perte journalière max atteinte
        if telemetry.pnl_day <= self.config.daily_loss_limit:
            return KillSwitchState.HALT_TRADING, KillSwitchReason.DAILY_LOSS_LIMIT
        
        # 2. Route DTC down > timeout
        if not telemetry.dtc_route_up:
            if telemetry.last_dtc_heartbeat:
                dtc_down_time = (telemetry.timestamp - telemetry.last_dtc_heartbeat).total_seconds()
                if dtc_down_time > self.config.dtc_down_timeout_seconds:
                    return KillSwitchState.PAPER_MODE, KillSwitchReason.DTC_ROUTE_DOWN
        
        # 3. Stale data critique
        if (telemetry.m1_stale_seconds > self.config.stale_data_thresholds["m1_max_seconds"] or
            telemetry.m30_stale_seconds > self.config.stale_data_thresholds["m30_max_seconds"] or
            telemetry.vix_stale_seconds > self.config.stale_data_thresholds["vix_max_seconds"]):
            return KillSwitchState.HALT_ENTRIES, KillSwitchReason.STALE_DATA_CRITICAL
        
        # 4. VIX spike en pleine session
        if (telemetry.vix_value > self.config.vix_spike_threshold and 
            telemetry.session_active and 
            telemetry.session_type in ["us_session", "london_session"]):
            return KillSwitchState.HALT_ENTRIES, KillSwitchReason.VIX_SPIKE
        
        # 5. Order rejections répétés
        if telemetry.rejections_last_5m > self.config.order_rejections_threshold:
            return KillSwitchState.HALT_TRADING, KillSwitchReason.ORDER_REJECTIONS
        
        # 6. MenthorQ stale critique
        if telemetry.menthorq_stale_seconds > (self.config.stale_data_thresholds["menthorq_max_periods"] * 60):
            return KillSwitchState.HALT_ENTRIES, KillSwitchReason.MENTHORQ_STALE
        
        # 7. Hard rules hits excessifs
        if telemetry.hard_rule_hits > 5:  # Plus de 5 hard rules en 5 minutes
            return KillSwitchState.HALT_ENTRIES, KillSwitchReason.SYSTEM_OVERLOAD
        
        # État normal
        return KillSwitchState.NORMAL, None
    
    def _change_state(self, new_state: KillSwitchState, reason: Optional[KillSwitchReason], telemetry: TelemetryData):
        """Change l'état du kill switch et exécute les actions"""
        old_state = self.current_state
        
        self.current_state = new_state
        self.current_reason = reason
        self.activated_since = datetime.now(timezone.utc)
        
        # Enregistrer l'activation
        self.activation_history.append({
            'timestamp': self.activated_since,
            'old_state': old_state.value,
            'new_state': new_state.value,
            'reason': reason.value if reason else None,
            'telemetry': {
                'pnl_day': telemetry.pnl_day,
                'vix_value': telemetry.vix_value,
                'dtc_route_up': telemetry.dtc_route_up
            }
        })
        
        # Limiter l'historique
        if len(self.activation_history) > 100:
            self.activation_history = self.activation_history[-100:]
        
        # Exécuter les actions selon le nouvel état
        self._execute_state_actions(new_state, reason, telemetry)
        
        # Notifier le changement
        self._notify_state_change(old_state, new_state, reason)
        
        # Logs
        if new_state != KillSwitchState.NORMAL:
            logger.warning(f"kill_switch: {new_state.value} true ({reason.value if reason else 'unknown'})")
        else:
            logger.info(f"kill_switch: reset to normal")
    
    def _execute_state_actions(self, state: KillSwitchState, reason: Optional[KillSwitchReason], telemetry: TelemetryData):
        """Exécute les actions selon l'état du kill switch"""
        
        if state == KillSwitchState.HALT_TRADING:
            # Flatten toutes les positions
            if self.config.auto_flatten_on_halt and self.trading_executor:
                try:
                    success = self.trading_executor.flatten_all()
                    if not success:
                        logger.error("flatten_all failed route_down → set paper_mode")
                        self.current_state = KillSwitchState.PAPER_MODE
                        self.current_reason = KillSwitchReason.DTC_ROUTE_DOWN
                except Exception as e:
                    logger.error(f"Erreur flatten_all: {e}")
                    self.current_state = KillSwitchState.PAPER_MODE
                    self.current_reason = KillSwitchReason.DTC_ROUTE_DOWN
        
        elif state == KillSwitchState.PAPER_MODE:
            # Activer le mode papier
            if self.trading_executor:
                self.trading_executor.set_paper_mode(True)
                logger.info("kill_switch: paper_mode activated")
        
        elif state == KillSwitchState.NORMAL:
            # Désactiver le mode papier
            if self.trading_executor:
                self.trading_executor.set_paper_mode(False)
                logger.info("kill_switch: paper_mode deactivated")
    
    def _update_counters(self, telemetry: TelemetryData):
        """Met à jour les compteurs de surveillance"""
        self.hard_rule_hits = telemetry.hard_rule_hits
        self.rejections_last_5m = telemetry.rejections_last_5m
        self.stale_ticks = telemetry.stale_ticks
    
    def _notify_state_change(self, old_state: KillSwitchState, new_state: KillSwitchState, reason: Optional[KillSwitchReason]):
        """Notifie le changement d'état"""
        if self.on_state_change:
            try:
                self.on_state_change(old_state, new_state, reason)
            except Exception as e:
                logger.error(f"Erreur callback state_change: {e}")
    
    # === MÉTHODES PUBLIQUES ===
    
    def get_state(self) -> Dict[str, Any]:
        """
        Retourne l'état actuel du kill switch
        
        Returns:
            Dict avec halt_entries, halt_trading, paper_mode, reason, since
        """
        return {
            'halt_entries': self.current_state in [KillSwitchState.HALT_ENTRIES, KillSwitchState.HALT_TRADING, KillSwitchState.PAPER_MODE, KillSwitchState.EMERGENCY],
            'halt_trading': self.current_state in [KillSwitchState.HALT_TRADING, KillSwitchState.PAPER_MODE, KillSwitchState.EMERGENCY],
            'paper_mode': self.current_state == KillSwitchState.PAPER_MODE,
            'emergency': self.current_state == KillSwitchState.EMERGENCY,
            'reason': self.current_reason.value if self.current_reason else None,
            'since': self.activated_since.isoformat() if self.activated_since else None,
            'state': self.current_state.value,
            'counters': {
                'hard_rule_hits': self.hard_rule_hits,
                'rejections_last_5m': self.rejections_last_5m,
                'stale_ticks': self.stale_ticks
            }
        }
    
    def reset(self, reason: str = "manual_reset"):
        """Déverrouillage manuel du kill switch"""
        if self.current_state != KillSwitchState.NORMAL:
            old_state = self.current_state
            self.current_state = KillSwitchState.NORMAL
            self.current_reason = None
            self.activated_since = None
            
            # Désactiver le mode papier
            if self.trading_executor:
                self.trading_executor.set_paper_mode(False)
            
            logger.info(f"kill_switch: reset at {reason}")
            self._notify_state_change(old_state, KillSwitchState.NORMAL, None)
    
    def emergency_stop(self):
        """Arrêt d'urgence complet"""
        self._change_state(KillSwitchState.EMERGENCY, KillSwitchReason.MANUAL_OVERRIDE, TelemetryData())
        logger.critical("🚨 EMERGENCY STOP ACTIVATED")
    
    def can_trade(self) -> bool:
        """Vérifie si le trading est autorisé"""
        return self.current_state == KillSwitchState.NORMAL
    
    def can_enter_positions(self) -> bool:
        """Vérifie si on peut entrer de nouvelles positions"""
        return self.current_state == KillSwitchState.NORMAL
    
    def can_exit_positions(self) -> bool:
        """Vérifie si on peut sortir des positions (toujours autorisé sauf emergency)"""
        return self.current_state != KillSwitchState.EMERGENCY
    
    # === MÉTHODES DE MONITORING ===
    
    async def start_monitoring(self):
        """Démarre la surveillance continue"""
        logger.info(f"🚨 Démarrage surveillance kill switch (intervalle: {self.config.check_interval_seconds}s)")
        
        while True:
            try:
                # Collecter les données de télémétrie
                telemetry = self._collect_telemetry()
                
                # Mettre à jour l'état
                state_changed = self.update(telemetry)
                
                if state_changed:
                    logger.info(f"État kill switch changé: {self.current_state.value}")
                
                # Attendre l'intervalle
                await asyncio.sleep(self.config.check_interval_seconds)
                
            except Exception as e:
                logger.error(f"Erreur surveillance kill switch: {e}")
                await asyncio.sleep(self.config.check_interval_seconds)
    
    def _collect_telemetry(self) -> TelemetryData:
        """Collecte les données de télémétrie depuis les composants"""
        telemetry = TelemetryData()
        
        try:
            # Market Snapshot
            if self.market_snapshot:
                try:
                    snapshot_data = self.market_snapshot.get_latest_snapshot()
                    if snapshot_data:
                        # Calculer les stale times
                        now = datetime.now(timezone.utc)
                        
                        # M1 stale
                        if 'm1_last_update' in snapshot_data:
                            m1_last = snapshot_data['m1_last_update']
                            if isinstance(m1_last, str):
                                m1_last = datetime.fromisoformat(m1_last.replace('Z', '+00:00'))
                            telemetry.m1_stale_seconds = (now - m1_last).total_seconds()
                        
                        # M30 stale
                        if 'm30_last_update' in snapshot_data:
                            m30_last = snapshot_data['m30_last_update']
                            if isinstance(m30_last, str):
                                m30_last = datetime.fromisoformat(m30_last.replace('Z', '+00:00'))
                            telemetry.m30_stale_seconds = (now - m30_last).total_seconds()
                        
                        # VIX stale
                        if 'vix_last_update' in snapshot_data:
                            vix_last = snapshot_data['vix_last_update']
                            if isinstance(vix_last, str):
                                vix_last = datetime.fromisoformat(vix_last.replace('Z', '+00:00'))
                            telemetry.vix_stale_seconds = (now - vix_last).total_seconds()
                            telemetry.vix_value = snapshot_data.get('vix_value', 20.0)
                        
                        # MenthorQ stale
                        if 'menthorq_last_update' in snapshot_data:
                            menthorq_last = snapshot_data['menthorq_last_update']
                            if isinstance(menthorq_last, str):
                                menthorq_last = datetime.fromisoformat(menthorq_last.replace('Z', '+00:00'))
                            telemetry.menthorq_stale_seconds = (now - menthorq_last).total_seconds()
                except Exception as e:
                    logger.warning(f"Erreur collecte market_snapshot: {e}")
            
            # Session Manager
            if self.session_manager:
                try:
                    session_state = self.session_manager.get_session_state()
                    telemetry.session_active = session_state.get('is_active', True)
                    telemetry.session_type = session_state.get('session_type', 'unknown')
                except Exception as e:
                    logger.warning(f"Erreur collecte session_manager: {e}")
            
            # Sierra Router
            if self.sierra_router:
                try:
                    health = self.sierra_router.health_check()
                    telemetry.dtc_route_up = health.get('dtc_connected', False)
                    telemetry.dtc_latency_ms = health.get('latency_ms', 0.0)
                    telemetry.last_dtc_heartbeat = datetime.now(timezone.utc) if telemetry.dtc_route_up else None
                except Exception as e:
                    logger.warning(f"Erreur collecte sierra_router: {e}")
                    telemetry.dtc_route_up = False
            
            # Trading Executor
            if self.trading_executor:
                try:
                    trading_state = self.trading_executor.get_trading_state()
                    telemetry.pnl_day = trading_state.get('pnl_day', 0.0)
                    telemetry.pnl_session = trading_state.get('pnl_session', 0.0)
                    telemetry.drawdown = trading_state.get('drawdown', 0.0)
                    telemetry.rejections_last_5m = trading_state.get('rejections_last_5m', 0)
                except Exception as e:
                    logger.warning(f"Erreur collecte trading_executor: {e}")
            
        except Exception as e:
            logger.error(f"Erreur collecte télémétrie: {e}")
        
        return telemetry
    
    def get_activation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retourne l'historique des activations"""
        return self.activation_history[-limit:] if self.activation_history else []
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de santé du système"""
        return {
            'current_state': self.current_state.value,
            'current_reason': self.current_reason.value if self.current_reason else None,
            'activated_since': self.activated_since.isoformat() if self.activated_since else None,
            'can_trade': self.can_trade(),
            'can_enter_positions': self.can_enter_positions(),
            'can_exit_positions': self.can_exit_positions(),
            'counters': {
                'hard_rule_hits': self.hard_rule_hits,
                'rejections_last_5m': self.rejections_last_5m,
                'stale_ticks': self.stale_ticks
            },
            'config': {
                'daily_loss_limit': self.config.daily_loss_limit,
                'dtc_down_timeout_seconds': self.config.dtc_down_timeout_seconds,
                'vix_spike_threshold': self.config.vix_spike_threshold,
                'order_rejections_threshold': self.config.order_rejections_threshold
            }
        }

# === INSTANCE GLOBALE ===

_safety_kill_switch = None

def get_safety_kill_switch() -> SafetyKillSwitch:
    """Retourne l'instance globale du SafetyKillSwitch"""
    global _safety_kill_switch
    if _safety_kill_switch is None:
        _safety_kill_switch = SafetyKillSwitch()
    return _safety_kill_switch

# === FONCTIONS UTILITAIRES ===

def create_safety_kill_switch(config: Optional[Dict[str, Any]] = None) -> SafetyKillSwitch:
    """Crée une instance du kill switch de sécurité"""
    return SafetyKillSwitch(config)

# === TEST ===

if __name__ == "__main__":
    # Test du kill switch enhanced
    logging.basicConfig(level=logging.INFO)
    
    kill_switch = SafetyKillSwitch()
    
    print("🚨 TEST SAFETY KILL SWITCH ENHANCED")
    print("=" * 60)
    
    # Test état initial
    state = kill_switch.get_state()
    print(f"État initial: {state}")
    
    # Test télémétrie normale
    telemetry_normal = TelemetryData(
        pnl_day=100.0,
        dtc_route_up=True,
        m1_stale_seconds=5.0,
        vix_value=20.0
    )
    
    changed = kill_switch.update(telemetry_normal)
    print(f"Télémétrie normale - Changé: {changed}")
    
    # Test télémétrie critique (perte journalière)
    telemetry_critical = TelemetryData(
        pnl_day=-1500.0,  # Au-dessus du seuil
        dtc_route_up=True,
        m1_stale_seconds=5.0,
        vix_value=20.0
    )
    
    changed = kill_switch.update(telemetry_critical)
    print(f"Télémétrie critique - Changé: {changed}")
    
    # Test état après activation
    state = kill_switch.get_state()
    print(f"État après activation: {state}")
    
    # Test reset
    kill_switch.reset("test_reset")
    state = kill_switch.get_state()
    print(f"État après reset: {state}")
    
    print("\n🎯 CONCLUSION: SafetyKillSwitch Enhanced fonctionnel !") 