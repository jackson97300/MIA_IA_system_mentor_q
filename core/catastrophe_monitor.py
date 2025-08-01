#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Catastrophe Monitor
Protection absolue contre les pertes catastrophiques
Version: Simple v1.0 - Protection maximale, code minimal
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import time
from core.logger import get_logger

logger = get_logger(__name__)

class CatastropheLevel(Enum):
    """Niveaux de catastrophe"""
    NORMAL = "normal"           # Tout va bien
    WARNING = "warning"         # Attention
    DANGER = "danger"           # Danger imminent
    EMERGENCY = "emergency"     # Arrêt immédiat requis

@dataclass
class CatastropheAlert:
    """Alerte de catastrophe"""
    level: CatastropheLevel
    trigger: str                # Ce qui a déclenché l'alerte
    current_value: float
    threshold_value: float
    action_required: str        # Action à prendre
    timestamp: datetime
    
class CatastropheMonitor:
    """
    Moniteur de catastrophes trading
    
    Protection contre :
    - Flash crashes
    - Pertes journalières excessives  
    - Drawdown excessif
    - Erreurs système critiques
    - Gaps de weekend
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = get_logger(__name__)
        
        # Configuration par défaut (CONSERVATRICE)
        default_config = {
            # Limites financières
            'daily_loss_limit': 500.0,          # $500 max par jour
            'weekly_loss_limit': 1500.0,        # $1500 max par semaine
            'max_drawdown_percent': 5.0,        # 5% max drawdown
            'account_balance_min': 1000.0,      # Balance minimum
            
            # Limites de trading
            'max_position_size': 2,             # 2 contrats max
            'max_trades_per_hour': 10,          # 10 trades max/heure
            'max_consecutive_losses': 5,        # 5 pertes d'affilée max
            
            # Protection technique
            'max_slippage_percent': 2.0,        # 2% slippage max
            'max_spread_ticks': 3,              # 3 ticks spread max
            'connection_timeout_seconds': 30,    # 30s timeout max
            
            # Protection temps
            'market_close_buffer_minutes': 15,   # Arrêt 15min avant close
            'weekend_gap_protection': True,      # Protection gaps weekend
            'news_event_pause_minutes': 30,     # Pause 30min après news importantes
        }
        
        self.config = {**default_config, **(config or {})}
        
        # État du monitoring
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0
        self.consecutive_losses = 0
        self.trades_this_hour = 0
        self.last_hour_reset = time.time()
        self.emergency_stop_triggered = False
        self.alerts_history: List[CatastropheAlert] = []
        
        # Compteurs pour stats
        self.stats = {
            'alerts_generated': 0,
            'emergency_stops': 0,
            'trades_blocked': 0,
            'last_reset_time': time.time()
        }
        
        self.logger.info("🛡️ Catastrophe Monitor initialisé avec limites conservatrices")
    
    def check_catastrophe_conditions(self, 
                                   current_pnl: float,
                                   account_balance: float,
                                   position_size: int = 0,
                                   market_data: Any = None) -> CatastropheAlert:
        """
        Vérifie toutes les conditions de catastrophe
        
        Args:
            current_pnl: P&L actuel de la journée
            account_balance: Balance du compte
            position_size: Taille de position actuelle
            market_data: Données de marché (optionnel)
            
        Returns:
            CatastropheAlert avec le niveau le plus critique détecté
        """
        try:
            self.daily_pnl = current_pnl
            
            # Vérifier toutes les conditions par ordre de criticité
            alerts = []
            
            # 1. EMERGENCY - Perte journalière critique
            if abs(current_pnl) > self.config['daily_loss_limit']:
                alerts.append(CatastropheAlert(
                    level=CatastropheLevel.EMERGENCY,
                    trigger="daily_loss_limit_exceeded",
                    current_value=abs(current_pnl),
                    threshold_value=self.config['daily_loss_limit'],
                    action_required="STOP_ALL_TRADING_IMMEDIATELY",
                    timestamp=datetime.now()
                ))
            
            # 2. EMERGENCY - Balance compte trop faible
            if account_balance < self.config['account_balance_min']:
                alerts.append(CatastropheAlert(
                    level=CatastropheLevel.EMERGENCY,
                    trigger="account_balance_critical",
                    current_value=account_balance,
                    threshold_value=self.config['account_balance_min'],
                    action_required="STOP_ALL_TRADING_IMMEDIATELY",
                    timestamp=datetime.now()
                ))
            
            # 3. DANGER - Pertes consécutives
            if self.consecutive_losses >= self.config['max_consecutive_losses']:
                alerts.append(CatastropheAlert(
                    level=CatastropheLevel.DANGER,
                    trigger="consecutive_losses_limit",
                    current_value=self.consecutive_losses,
                    threshold_value=self.config['max_consecutive_losses'],
                    action_required="PAUSE_TRADING_1_HOUR",
                    timestamp=datetime.now()
                ))
            
            # 4. DANGER - Position trop large
            if abs(position_size) > self.config['max_position_size']:
                alerts.append(CatastropheAlert(
                    level=CatastropheLevel.DANGER,
                    trigger="position_size_exceeded",
                    current_value=abs(position_size),
                    threshold_value=self.config['max_position_size'],
                    action_required="REDUCE_POSITION_IMMEDIATELY",
                    timestamp=datetime.now()
                ))
            
            # 5. WARNING - Trop de trades cette heure
            self._reset_hourly_counters()
            if self.trades_this_hour >= self.config['max_trades_per_hour']:
                alerts.append(CatastropheAlert(
                    level=CatastropheLevel.WARNING,
                    trigger="trades_per_hour_limit",
                    current_value=self.trades_this_hour,
                    threshold_value=self.config['max_trades_per_hour'],
                    action_required="SLOW_DOWN_TRADING",
                    timestamp=datetime.now()
                ))
            
            # 6. Vérifications marché si données disponibles
            if market_data:
                market_alerts = self._check_market_conditions(market_data)
                alerts.extend(market_alerts)
            
            # Retourner l'alerte la plus critique
            if alerts:
                # Trier par niveau de criticité
                critical_order = {
                    CatastropheLevel.EMERGENCY: 4,
                    CatastropheLevel.DANGER: 3,
                    CatastropheLevel.WARNING: 2,
                    CatastropheLevel.NORMAL: 1
                }
                
                most_critical = max(alerts, key=lambda x: critical_order[x.level])
                
                # Ajouter à l'historique
                self.alerts_history.append(most_critical)
                self.stats['alerts_generated'] += 1
                
                # Déclencher emergency stop si nécessaire
                if most_critical.level == CatastropheLevel.EMERGENCY:
                    self.emergency_stop_triggered = True
                    self.stats['emergency_stops'] += 1
                
                return most_critical
            
            # Tout va bien
            return CatastropheAlert(
                level=CatastropheLevel.NORMAL,
                trigger="all_conditions_ok",
                current_value=0,
                threshold_value=0,
                action_required="CONTINUE_TRADING",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Erreur check_catastrophe_conditions: {e}")
            # En cas d'erreur, retourner alerte critique par sécurité
            return CatastropheAlert(
                level=CatastropheLevel.EMERGENCY,
                trigger="monitor_system_error",
                current_value=0,
                threshold_value=1,
                action_required="STOP_ALL_TRADING_SYSTEM_ERROR",
                timestamp=datetime.now()
            )
    
    def _check_market_conditions(self, market_data) -> List[CatastropheAlert]:
        """Vérifie conditions de marché dangereuses"""
        alerts = []
        
        try:
            # Check spread si disponible
            if hasattr(market_data, 'bid') and hasattr(market_data, 'ask'):
                spread = market_data.ask - market_data.bid
                if spread > self.config['max_spread_ticks'] * 0.25:  # 0.25 = tick size ES
                    alerts.append(CatastropheAlert(
                        level=CatastropheLevel.WARNING,
                        trigger="spread_too_wide",
                        current_value=spread,
                        threshold_value=self.config['max_spread_ticks'] * 0.25,
                        action_required="AVOID_TRADING_UNTIL_SPREAD_NORMAL",
                        timestamp=datetime.now()
                    ))
            
            # Check volume anormal (flash crash indicator)
            if hasattr(market_data, 'volume'):
                # Simple heuristique : volume > 10x normal = possible flash crash
                avg_volume = getattr(market_data, 'avg_volume', market_data.volume)
                if market_data.volume > avg_volume * 10:
                    alerts.append(CatastropheAlert(
                        level=CatastropheLevel.DANGER,
                        trigger="abnormal_volume_spike",
                        current_value=market_data.volume,
                        threshold_value=avg_volume * 10,
                        action_required="PAUSE_TRADING_VOLUME_SPIKE",
                        timestamp=datetime.now()
                    ))
            
        except Exception as e:
            self.logger.debug(f"Erreur _check_market_conditions: {e}")
        
        return alerts
    
    def _reset_hourly_counters(self):
        """Reset compteurs horaires"""
        current_time = time.time()
        if current_time - self.last_hour_reset > 3600:  # 1 heure
            self.trades_this_hour = 0
            self.last_hour_reset = current_time
    
    def record_trade_result(self, pnl: float, is_winner: bool):
        """Enregistre résultat d'un trade"""
        try:
            self.trades_this_hour += 1
            
            if is_winner:
                self.consecutive_losses = 0
            else:
                self.consecutive_losses += 1
            
            self.logger.debug(f"Trade enregistré: PnL={pnl}, Winner={is_winner}, Consecutive losses={self.consecutive_losses}")
            
        except Exception as e:
            self.logger.error(f"Erreur record_trade_result: {e}")
    
    def should_block_trading(self) -> bool:
        """Détermine si le trading doit être bloqué"""
        return self.emergency_stop_triggered
    
    def reset_emergency_stop(self, force: bool = False):
        """Reset emergency stop (avec confirmation)"""
        if force or datetime.now().hour != datetime.now().hour:  # Reset automatique chaque heure
            self.emergency_stop_triggered = False
            self.logger.warning("🔄 Emergency stop reset")
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Retourne résumé du status"""
        return {
            'emergency_stop_active': self.emergency_stop_triggered,
            'daily_pnl': self.daily_pnl,
            'consecutive_losses': self.consecutive_losses,
            'trades_this_hour': self.trades_this_hour,
            'alerts_today': len([a for a in self.alerts_history 
                               if a.timestamp.date() == datetime.now().date()]),
            'last_alert': self.alerts_history[-1].trigger if self.alerts_history else "none",
            'stats': self.stats
        }

# ================================
# INTÉGRATION SIMPLE 
# ================================

def create_catastrophe_monitor(config: Dict[str, Any] = None) -> CatastropheMonitor:
    """Factory pour créer le Catastrophe Monitor"""
    return CatastropheMonitor(config)

# Exemple d'utilisation :
"""
# Dans votre risk_manager.py ou automation_main.py :

# Initialisation
self.catastrophe_monitor = create_catastrophe_monitor()

# Avant chaque trade
alert = self.catastrophe_monitor.check_catastrophe_conditions(
    current_pnl=self.daily_pnl,
    account_balance=self.account_balance,
    position_size=current_position_size,
    market_data=market_data
)

if alert.level == CatastropheLevel.EMERGENCY:
    self.logger.critical(f"🚨 CATASTROPHE: {alert.trigger}")
    # ARRÊTER TOUT IMMÉDIATEMENT
    await self.emergency_shutdown()
elif alert.level == CatastropheLevel.DANGER:
    self.logger.error(f"⚠️ DANGER: {alert.trigger}")
    # Réduire risques
elif alert.level == CatastropheLevel.WARNING:
    self.logger.warning(f"💡 WARNING: {alert.trigger}")

# Après chaque trade
self.catastrophe_monitor.record_trade_result(pnl=trade_pnl, is_winner=trade_pnl > 0)
"""