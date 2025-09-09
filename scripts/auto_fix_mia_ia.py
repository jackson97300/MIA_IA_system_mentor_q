#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Auto Fix Script
Correction automatique des problèmes identifiés
"""

import json
import os
from pathlib import Path

def fix_orderflow_thresholds():
    """Corrige les seuils OrderFlow"""
    config_path = Path("config/constants.py")
    
    if config_path.exists():
        # Lecture du fichier
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacements des seuils
        replacements = {
            "'min_confidence': 0.200": "'min_confidence': 0.150",
            "'min_footprint': 0.100": "'min_footprint': 0.075",
            "'volume_threshold': 20": "'volume_threshold': 15",
            "'delta_threshold': 0.15": "'delta_threshold': 0.10"
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Sauvegarde
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Seuils OrderFlow corrigés")

def fix_ibkr_connection():
    """Corrige la configuration IBKR"""
    config_path = Path("config/ibkr_config.py")
    
    if config_path.exists():
        # Lecture du fichier
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacements
        replacements = {
            "'port': 7496": "'port': 7497",  # Paper trading
            "'client_id': 0": "'client_id': 1",  # Unique
            "'timeout': 10": "'timeout': 30"  # Plus de temps
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Sauvegarde
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Configuration IBKR corrigée")

def main():
    """Exécution des corrections"""
    print("🔧 MIA_IA_SYSTEM - Auto Fix Script")
    print("==================================")
    
    fix_orderflow_thresholds()
    fix_ibkr_connection()
    
    print("✅ Toutes les corrections appliquées")
    print("🔄 Redémarrez le système pour appliquer les changements")

if __name__ == "__main__":
    main()
