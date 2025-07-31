#!/usr/bin/env python3
"""
Script FINAL pour corriger les dernières erreurs
"""

import os
from pathlib import Path
import re

def final_fixes():
    """Applique les dernières corrections nécessaires"""
    
    project_root = Path("D:/MIA_IA_system")
    
    # Fix 1: alert_system.py - Corriger complètement le fichier
    print("📄 Réécriture complète: monitoring/alert_system.py")
    alert_system_path = project_root / "monitoring/alert_system.py"
    
    alert_content = '''"""
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
'''
    
    with open(alert_system_path, 'w', encoding='utf-8') as f:
        f.write(alert_content)
    print("  ✅ alert_system.py réécrit complètement")
    
    # Fix 2: Ajouter OrderStatus à base_types.py
    print("\n📄 Ajout OrderStatus: core/base_types.py")
    base_types_path = project_root / "core/base_types.py"
    
    with open(base_types_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ajouter OrderStatus si manquant
    if "class OrderStatus" not in content:
        order_status_def = '''
class OrderStatus(Enum):
    """Statuts des ordres"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
'''
        # Trouver où insérer (après OrderType de préférence)
        if "class OrderType(Enum):" in content:
            parts = content.split("class OrderType(Enum):")
            # Trouver la fin de OrderType
            lines = parts[1].split('\n')
            enum_end = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith(' ') and not line.startswith('\t') and i > 5:
                    enum_end = i
                    break
            
            before = parts[0] + "class OrderType(Enum):" + '\n'.join(lines[:enum_end])
            after = '\n'.join(lines[enum_end:])
            content = before + '\n' + order_status_def + '\n' + after
        else:
            # Sinon, ajouter après SignalType
            if "class SignalType(Enum):" in content:
                parts = content.split("class SignalType(Enum):")
                lines = parts[1].split('\n')
                enum_end = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith(' ') and not line.startswith('\t') and i > 5:
                        enum_end = i
                        break
                
                before = parts[0] + "class SignalType(Enum):" + '\n'.join(lines[:enum_end])
                after = '\n'.join(lines[enum_end:])
                content = before + '\n' + order_status_def + '\n' + after
    
    with open(base_types_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  ✅ OrderStatus ajouté")
    
    # Fix 3: Créer sierra_config.py s'il manque
    sierra_config_path = project_root / "config/sierra_config.py"
    if not sierra_config_path.exists():
        print("\n📄 Création: config/sierra_config.py")
        sierra_content = '''"""
Configuration Sierra Chart pour MIA_IA_SYSTEM
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class SierraConfig:
    """Configuration pour Sierra Chart DTC Protocol"""
    # Connection settings
    host: str = "127.0.0.1"
    port: int = 11099
    username: str = ""
    password: str = ""
    
    # Data settings
    historical_data_port: int = 11097
    update_frequency_ms: int = 100
    symbol_settings: dict = None
    
    # Features
    enable_historical_data: bool = True
    enable_real_time_data: bool = True
    enable_order_routing: bool = False
    
    # Timeouts
    connection_timeout: int = 30
    request_timeout: int = 10
    
    def __post_init__(self):
        if self.symbol_settings is None:
            self.symbol_settings = {
                "ES": {"exchange": "CME", "type": "FUTURE"},
                "NQ": {"exchange": "CME", "type": "FUTURE"},
                "MES": {"exchange": "CME", "type": "FUTURE"},
                "MNQ": {"exchange": "CME", "type": "FUTURE"}
            }

def get_sierra_config() -> SierraConfig:
    """Retourne la configuration Sierra Chart"""
    return SierraConfig()
'''
        with open(sierra_config_path, 'w', encoding='utf-8') as f:
            f.write(sierra_content)
        print("  ✅ sierra_config.py créé")
    
    # Fix 4: Mettre à jour config/__init__.py pour exporter sierra_config
    config_init_path = project_root / "config/__init__.py"
    with open(config_init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # S'assurer que sierra_config est bien exporté
    if "from .sierra_config import SierraIBKRConfig, get_sierra_config" not in content and "sierra_config" in content:
        content = content.replace(
            "logger.warning(\"Could not import sierra_config\")",
            """logger.warning("Could not import sierra_config")
    from .sierra_config import SierraIBKRConfig, get_sierra_config"""
        )
    
    with open(config_init_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Fix 5: S'assurer que OrderStatus est exporté dans base_types
    base_types_path = project_root / "core/base_types.py"
    with open(base_types_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ajouter OrderStatus à __all__ s'il n'y est pas
    if "'OrderStatus'" not in content and "OrderStatus" in content:
        if "__all__ = [" in content:
            content = content.replace(
                "'OrderType',",
                "'OrderType',\n    'OrderStatus',"
            )
        
    with open(base_types_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "=" * 60)
    print("✅ Toutes les corrections finales appliquées !")
    print("\nTestez maintenant :")
    print('python -c "import config; import core; import features; import strategies; import execution; import monitoring; import ml; import data; import performance; print(\'✅ SUCCÈS TOTAL !\')"')

if __name__ == "__main__":
    final_fixes()