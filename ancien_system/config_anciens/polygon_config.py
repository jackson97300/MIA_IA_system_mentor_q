#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - POLYGON.IO CONFIGURATION
Configuration centralisée pour l'intégration Polygon.io

Author: MIA_IA_SYSTEM
Version: 1.0.0
Date: Août 2025
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class PolygonConfig:
    """Configuration Polygon.io pour MIA_IA_SYSTEM"""
    
    # API Configuration
    api_key: str = "wInzDiC4jEA4tgf4zfH98uRDRVbvPbcy"
    api_base_url: str = "https://api.polygon.io"
    
    # Rate Limiting
    rate_limit_delay: float = 0.2  # 200ms entre requêtes (5 calls/min)
    max_requests_per_minute: int = 5  # Plan Starter
    
    # Cache Configuration
    cache_ttl_seconds: int = 300  # 5 minutes (pour différé 15min)
    max_cache_size: int = 1000
    
    # WebSocket Configuration
    use_websocket: bool = False  # Pas disponible en Starter
    websocket_subscriptions: List[str] = None
    
    # Options Configuration
    default_expiry_offset_days: int = 30
    strike_window_percent: float = 0.10  # ±10% autour du prix
    strike_increment_spx: int = 5
    strike_increment_ndx: int = 25
    
    # Simulation/Fallback Configuration
    enable_simulation_fallback: bool = True
    simulation_iv_spx: float = 0.15
    simulation_iv_ndx: float = 0.18
    
    # Timeout Configuration
    connection_timeout_seconds: int = 30
    request_timeout_seconds: int = 10
    max_retries: int = 3
    
    # Plan Starter Limitations
    plan_limitations: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialisation post-création"""
        if not self.api_key:
            self.api_key = os.getenv("POLYGON_API_KEY", "")
        
        if self.websocket_subscriptions is None:
            self.websocket_subscriptions = []
        
        # Limitations du plan Starter
        self.plan_limitations = {
            'plan_type': 'Starter',
            'monthly_cost': 29.0,
            'calls_per_minute': 5,
            'data_delay_minutes': 15,
            'historical_data_days': 2,
            'options_data': True,
            'real_time_data': False,
            'websocket_access': False
        }
    
    @classmethod
    def from_env(cls) -> 'PolygonConfig':
        """Crée une configuration depuis les variables d'environnement"""
        return cls(
            api_key=os.getenv("POLYGON_API_KEY", "wInzDiC4jEA4tgf4zfH98uRDRVbvPbcy")
        )
    
    def get_rate_limit_delay(self) -> float:
        """Retourne le délai entre requêtes selon le plan"""
        return self.rate_limit_delay
    
    def is_starter_plan(self) -> bool:
        """Vérifie si c'est le plan Starter"""
        return self.plan_limitations['plan_type'] == 'Starter'
    
    def can_access_real_time(self) -> bool:
        """Vérifie l'accès aux données temps réel"""
        return self.plan_limitations['real_time_data']
    
    def get_data_delay_minutes(self) -> int:
        """Retourne le délai des données en minutes"""
        return self.plan_limitations['data_delay_minutes']

# Configuration par défaut
polygon_config = PolygonConfig()

if __name__ == "__main__":
    print("🔧 Configuration Polygon.io chargée")
    print(f"📊 Plan: {polygon_config.plan_limitations['plan_type']}")
    print(f"💰 Coût: ${polygon_config.plan_limitations['monthly_cost']}/mois")
    print(f"⏰ Délai données: {polygon_config.plan_limitations['data_delay_minutes']}min")
    print(f"📞 Calls/min: {polygon_config.plan_limitations['calls_per_minute']}")


