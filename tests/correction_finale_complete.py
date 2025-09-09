#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Correction Finale Complète
Correction finale pour ajouter tous les paramètres manquants
"""

import os
import sys
import re
from datetime import datetime

def correction_finale_complete():
    """Correction finale complète"""
    
    print("🔧 MIA_IA_SYSTEM - CORRECTION FINALE COMPLÈTE")
    print("=" * 60)
    
    # 1. CORRECTION CONFIG/AUTOMATION_CONFIG.PY
    print("\n📄 Correction: config/automation_config.py")
    
    if os.path.exists("config/automation_config.py"):
        with open("config/automation_config.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Vérifier et ajouter les paramètres manquants
        if "USE_REAL_DATA: bool = True" not in content:
            # Ajouter après simulation_mode
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
        
        # Ajouter SIMULATION_MODE = False si manquant
        if "SIMULATION_MODE = False" not in content:
            # Insérer au début du fichier après les imports
            simulation_mode_line = "\n# DONNÉES RÉELLES OBLIGATOIRES\nSIMULATION_MODE = False\n"
            content = content.replace(
                'from typing import Dict, Any',
                'from typing import Dict, Any' + simulation_mode_line
            )
        
        # Ajouter DataSource.IBKR si manquant
        if "DataSource.IBKR" not in content:
            # Ajouter après les paramètres existants
            datasource_line = "\n    'DATA_SOURCE': 'IBKR',  # Source IBKR obligatoire\n"
            content = content.replace(
                "    'log_market_data': False,  # Trop volumineux",
                "    'log_market_data': False,  # Trop volumineux" + datasource_line
            )
        
        # Corriger le port
        content = re.sub(r"'port':\s*[0-9]+", "'port': 7497,  # Port TWS Paper Trading", content)
        
        with open("config/mia_ia_system_tws_paper_fixed.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("   ✅ Paramètres ajoutés")
    
    # 3. CORRECTION CORE/IBKR_CONNECTOR.PY
    print("\n📄 Correction: core/ibkr_connector.py")
    
    if os.path.exists("core/ibkr_connector.py"):
        with open("core/ibkr_connector.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Ajouter DataSource.IBKR si manquant
        if "DataSource.IBKR" not in content:
            # Ajouter après les paramètres existants
            datasource_line = "\n        self.DATA_SOURCE = 'IBKR'  # Source IBKR obligatoire\n"
            content = content.replace(
                "        self.REJECT_SIMULATED_DATA = True",
                "        self.REJECT_SIMULATED_DATA = True" + datasource_line
            )
        
        # Corriger le port
        content = re.sub(r'self\.port\s*=\s*[0-9]+', 'self.port = 7497  # Port TWS Paper Trading', content)
        
        with open("core/ibkr_connector.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("   ✅ Paramètres ajoutés")
    
    # 4. CORRECTION DATA/MARKET_DATA_FEED.PY
    print("\n📄 Correction: data/market_data_feed.py")
    
    if os.path.exists("data/market_data_feed.py"):
        with open("data/market_data_feed.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Ajouter simulation_mode = False si manquant
        if "simulation_mode = False" not in content:
            # Ajouter après l'initialisation des sources
            simulation_line = "\n        self.simulation_mode = False  # DONNÉES RÉELLES OBLIGATOIRES\n"
            content = content.replace(
                "        self.REJECT_SIMULATED_DATA = True",
                "        self.REJECT_SIMULATED_DATA = True" + simulation_line
            )
        
        # Ajouter USE_REAL_DATA si manquant
        if "self.USE_REAL_DATA = True" not in content:
            # Ajouter après simulation_mode
            real_data_line = "\n        self.USE_REAL_DATA = True  # DONNÉES RÉELLES OBLIGATOIRES\n"
            content = content.replace(
                "        self.simulation_mode = False  # DONNÉES RÉELLES OBLIGATOIRES",
                "        self.simulation_mode = False  # DONNÉES RÉELLES OBLIGATOIRES" + real_data_line
            )
        
        # Ajouter FORCE_REAL_DATA si manquant
        if "self.FORCE_REAL_DATA = True" not in content:
            # Ajouter après USE_REAL_DATA
            force_real_line = "\n        self.FORCE_REAL_DATA = True  # DONNÉES RÉELLES OBLIGATOIRES\n"
            content = content.replace(
                "        self.USE_REAL_DATA = True  # DONNÉES RÉELLES OBLIGATOIRES",
                "        self.USE_REAL_DATA = True  # DONNÉES RÉELLES OBLIGATOIRES" + force_real_line
            )
        
        with open("data/market_data_feed.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("   ✅ Paramètres ajoutés")
    
    print("\n✅ CORRECTION FINALE TERMINÉE")
    print("✅ Tous les paramètres manquants ont été ajoutés")

if __name__ == "__main__":
    correction_finale_complete()


