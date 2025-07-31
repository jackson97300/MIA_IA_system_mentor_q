"""
Alert System pour MIA_IA_SYSTEM
Gère les alertes et notifications du système
"""

import logging
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import threading
import queue

# Configure logger au début
logger = logging.getLogger(__name__)

# Import email avec gestion d'erreur
EMAIL_AVAILABLE = False
try:
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import smtplib
    EMAIL_AVAILABLE = True
    logger.info("Email functionality available")
except ImportError as e:
    logger.warning(f"Email functionality disabled: {e}")

class AlertLevel(Enum):
    """Niveaux d'alerte"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertType(Enum):
    """Types d'alertes"""
    SYSTEM = "system"
    TRADING = "trading"
    RISK = "risk"
    PERFORMANCE = "performance"
    DATA = "data"
    ML = "ml"

@dataclass
class Alert:
    """Structure d'une alerte"""
    level: AlertLevel
    type: AlertType
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    
class AlertSystem:
    """Système de gestion des alertes"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.alerts_queue = queue.Queue()
        self.alerts_history = []
        self.handlers = []
        self.is_running = False
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Configure les handlers d'alertes"""
        # Log handler (toujours actif)
        self.add_handler(self._log_handler)
        
        # Email handler si disponible
        if EMAIL_AVAILABLE and self.config.get('email_enabled'):
            self.add_handler(self._email_handler)
            
    def _log_handler(self, alert: Alert):
        """Handler qui log les alertes"""
        level_map = {
            AlertLevel.INFO: logger.info,
            AlertLevel.WARNING: logger.warning,
            AlertLevel.ERROR: logger.error,
            AlertLevel.CRITICAL: logger.critical
        }
        
        log_func = level_map.get(alert.level, logger.info)
        log_func(f"[{alert.type.value}] {alert.message}")
        
    def _email_handler(self, alert: Alert):
        """Handler pour envoyer des emails"""
        if not EMAIL_AVAILABLE:
            return
            
        if alert.level in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
            try:
                # Configuration email
                smtp_config = self.config.get('smtp', {})
                if not smtp_config:
                    return
                    
                # Créer le message
                msg = MIMEMultipart()
                msg['Subject'] = f"[MIA_IA] {alert.level.value.upper()}: {alert.type.value}"
                msg['From'] = smtp_config.get('from_email', '')
                msg['To'] = smtp_config.get('to_email', '')
                
                # Corps du message
                body = f"""
                Alert Level: {alert.level.value}
                Alert Type: {alert.type.value}
                Message: {alert.message}
                Timestamp: {alert.timestamp.isoformat()}
                Source: {alert.source}
                
                Details:
                {json.dumps(alert.details, indent=2)}
                """
                
                msg.attach(MIMEText(body, 'plain'))
                
                # Envoyer
                with smtplib.SMTP(smtp_config.get('host'), smtp_config.get('port', 587)) as server:
                    if smtp_config.get('use_tls', True):
                        server.starttls()
                    if smtp_config.get('username'):
                        server.login(smtp_config['username'], smtp_config['password'])
                    server.send_message(msg)
                    
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")
    
    def add_handler(self, handler):
        """Ajoute un handler d'alertes"""
        self.handlers.append(handler)
        
    def send_alert(self, level: AlertLevel, alert_type: AlertType, 
                  message: str, details: Optional[Dict] = None, source: str = "unknown"):
        """Envoie une alerte"""
        alert = Alert(
            level=level,
            type=alert_type,
            message=message,
            details=details or {},
            source=source
        )
        
        # Ajouter à l'historique
        self.alerts_history.append(alert)
        
        # Traiter avec les handlers
        for handler in self.handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Handler error: {e}")
                
        return alert

def create_alert_system(config: Optional[Dict] = None) -> AlertSystem:
    """Factory function pour créer un AlertSystem"""
    return AlertSystem(config)
