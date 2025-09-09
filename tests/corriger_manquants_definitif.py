#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Correction Manuelle Paramètres Manquants
Corrige manuellement tous les paramètres manquants pour les données réelles
"""

import os
import sys
import re
from datetime import datetime

def corriger_manquants_definitif():
    """Correction manuelle des paramètres manquants"""
    
    print("🔧 MIA_IA_SYSTEM - CORRECTION MANUELLE PARAMÈTRES MANQUANTS")
    print("=" * 60)
    
    # 1. CORRECTION CONFIG/AUTOMATION_CONFIG.PY
    print("\n📄 Correction: config/automation_config.py")
    
    if os.path.exists("config/automation_config.py"):
        with open("config/automation_config.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Ajouter les paramètres manquants après simulation_mode
        if "simulation_mode: bool = False" in content:
            # Ajouter les paramètres manquants
            additional_params = """
    # DONNÉES RÉELLES OBLIGATOIRES
    USE_REAL_DATA: bool = True
    FORCE_REAL_DATA: bool = True
    DISABLE_SIMULATION: bool = True
    REAL_DATA_SOURCE: str = 'IBKR'
    ENABLE_LIVE_FEED: bool = True
    USE_CACHED_DATA: bool = False
    FORCE_FRESH_DATA: bool = True
    DATA_SOURCE_PRIORITY: str = 'real'
    FALLBACK_TO_SIMULATION: bool = False
    REAL_TIME_DATA_ONLY: bool = True
    VALIDATE_REAL_DATA: bool = True
    REJECT_SIMULATED_DATA: bool = True
"""
            
            # Insérer après simulation_mode
            content = content.replace(
                "simulation_mode: bool = False  # DONNÉES RÉELLES OBLIGATOIRES",
                "simulation_mode: bool = False  # DONNÉES RÉELLES OBLIGATOIRES" + additional_params
            )
            
            # Corriger le port IBKR
            content = re.sub(r'config\.ibkr\.port\s*=\s*[0-9]+', 'config.ibkr.port = 7497  # Port TWS Paper Trading', content)
            content = re.sub(r'config\.ibkr\.market_data_type\s*=\s*[0-9]+', 'config.ibkr.market_data_type = 1  # Données réelles', content)
            
            with open("config/automation_config.py", "w", encoding="utf-8") as f:
                f.write(content)
            
            print("   ✅ Paramètres ajoutés")
    
    # 2. CORRECTION CONFIG/MIA_IA_SYSTEM_TWS_PAPER_FIXED.PY
    print("\n📄 Correction: config/mia_ia_system_tws_paper_fixed.py")
    
    if os.path.exists("config/mia_ia_system_tws_paper_fixed.py"):
        with open("config/mia_ia_system_tws_paper_fixed.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Ajouter les paramètres manquants
        additional_config = """
# DONNÉES RÉELLES OBLIGATOIRES
SIMULATION_MODE = False
USE_REAL_DATA = True
FORCE_REAL_DATA = True
DISABLE_SIMULATION = True
REAL_DATA_SOURCE = 'IBKR'
ENABLE_LIVE_FEED = True
USE_CACHED_DATA = False
FORCE_FRESH_DATA = True
DATA_SOURCE_PRIORITY = 'real'
FALLBACK_TO_SIMULATION = False
REAL_TIME_DATA_ONLY = True
VALIDATE_REAL_DATA = True
REJECT_SIMULATED_DATA = True
"""
        
        # Insérer après la configuration existante
        if "MIA_IA_SYSTEM_GATEWAY_CONFIG = {" in content:
            # Trouver la fin de la configuration
            end_pos = content.find("def get_gateway_config()")
            if end_pos != -1:
                content = content[:end_pos] + additional_config + "\n" + content[end_pos:]
            
            with open("config/mia_ia_system_tws_paper_fixed.py", "w", encoding="utf-8") as f:
                f.write(content)
            
            print("   ✅ Paramètres ajoutés")
    
    # 3. CORRECTION CORE/IBKR_CONNECTOR.PY
    print("\n📄 Correction: core/ibkr_connector.py")
    
    if os.path.exists("core/ibkr_connector.py"):
        with open("core/ibkr_connector.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Ajouter les paramètres manquants dans __init__
        additional_init_params = """
        # DONNÉES RÉELLES OBLIGATOIRES
        self.USE_REAL_DATA = True
        self.FORCE_REAL_DATA = True
        self.DISABLE_SIMULATION = True
        self.REAL_DATA_SOURCE = 'IBKR'
        self.ENABLE_LIVE_FEED = True
        self.USE_CACHED_DATA = False
        self.FORCE_FRESH_DATA = True
        self.DATA_SOURCE_PRIORITY = 'real'
        self.FALLBACK_TO_SIMULATION = False
        self.REAL_TIME_DATA_ONLY = True
        self.VALIDATE_REAL_DATA = True
        self.REJECT_SIMULATED_DATA = True
"""
        
        # Insérer après simulation_mode dans __init__
        if "self.simulation_mode = False" in content:
            content = content.replace(
                "self.simulation_mode = False  # DONNÉES RÉELLES OBLIGATOIRES",
                "self.simulation_mode = False  # DONNÉES RÉELLES OBLIGATOIRES" + additional_init_params
            )
            
            with open("core/ibkr_connector.py", "w", encoding="utf-8") as f:
                f.write(content)
            
            print("   ✅ Paramètres ajoutés")
    
    # 4. CORRECTION DATA/MARKET_DATA_FEED.PY
    print("\n📄 Correction: data/market_data_feed.py")
    
    if os.path.exists("data/market_data_feed.py"):
        with open("data/market_data_feed.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Ajouter les paramètres manquants dans __init__
        additional_feed_params = """
        # DONNÉES RÉELLES OBLIGATOIRES
        self.USE_REAL_DATA = True
        self.FORCE_REAL_DATA = True
        self.DISABLE_SIMULATION = True
        self.REAL_DATA_SOURCE = 'IBKR'
        self.ENABLE_LIVE_FEED = True
        self.USE_CACHED_DATA = False
        self.FORCE_FRESH_DATA = True
        self.DATA_SOURCE_PRIORITY = 'real'
        self.FALLBACK_TO_SIMULATION = False
        self.REAL_TIME_DATA_ONLY = True
        self.VALIDATE_REAL_DATA = True
        self.REJECT_SIMULATED_DATA = True
"""
        
        # Insérer après l'initialisation des sources
        if "self.primary_source = DataSource.IBKR" in content:
            content = content.replace(
                "self.primary_source = DataSource.IBKR  # DONNÉES RÉELLES OBLIGATOIRES",
                "self.primary_source = DataSource.IBKR  # DONNÉES RÉELLES OBLIGATOIRES" + additional_feed_params
            )
            
            with open("data/market_data_feed.py", "w", encoding="utf-8") as f:
                f.write(content)
            
            print("   ✅ Paramètres ajoutés")
    
    print("\n✅ CORRECTION MANUELLE TERMINÉE")
    print("✅ Tous les paramètres manquants ont été ajoutés")

if __name__ == "__main__":
    corriger_manquants_definitif()


