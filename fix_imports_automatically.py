#!/usr/bin/env python3
"""
🔧 SCRIPT DE CORRECTION AUTOMATIQUE DES IMPORTS
===============================================

Corrige automatiquement tous les imports cassés après la centralisation execution/
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Corrige les imports dans un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Corrections principales
        replacements = [
            # Core Sierra
            (r'from core\.sierra_connector import', 'from execution.sierra_connector import'),
            (r'from core\.sierra_order_router import', 'from execution.sierra_order_router import'),
            (r'from core\.sierra_dtc_connector import', 'from execution.sierra_dtc_connector import'),
            (r'import core\.sierra_connector', 'import execution.sierra_connector'),
            (r'import core\.sierra_order_router', 'import execution.sierra_order_router'),
            (r'import core\.sierra_dtc_connector', 'import execution.sierra_dtc_connector'),
            
            # Automation modules
            (r'from automation_modules\.order_manager import', 'from execution.order_manager import'),
            (r'from automation_modules\.risk_manager import', 'from execution.risk_manager import'),
            (r'from automation_modules\.sierra_battle_navale_integrator import', 'from execution.sierra_battle_navale_integrator import'),
            (r'from automation_modules\.sierra_optimizer import', 'from execution.sierra_optimizer import'),
            (r'from automation_modules\.config_manager import', 'from config.automation_config import'),
            (r'from automation_modules\.trading_executor import', 'from execution.trading_executor import'),
            (r'from automation_modules\.optimized_trading_system import', 'from execution.simple_trader import'),
            (r'from automation_modules\.performance_tracker import', 'from monitoring.performance_tracker import'),
            (r'from automation_modules\.validation_engine import', 'from features.validation_engine import'),
            (r'from automation_modules\.confluence_calculator import', 'from features.confluence_calculator import'),
            (r'from automation_modules\.orderflow_analyzer import', 'from features.orderflow_analyzer import'),
            
            # Imports
            (r'import automation_modules\.order_manager', 'import execution.order_manager'),
            (r'import automation_modules\.risk_manager', 'import execution.risk_manager'),
            (r'import automation_modules\.sierra_battle_navale_integrator', 'import execution.sierra_battle_navale_integrator'),
            (r'import automation_modules\.sierra_optimizer', 'import execution.sierra_optimizer'),
        ]
        
        # Appliquer les remplacements
        for old_pattern, new_pattern in replacements:
            content = re.sub(old_pattern, new_pattern, content)
        
        # Sauvegarder si changé
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Corrigé: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Erreur dans {file_path}: {e}")
        return False

def main():
    """Corrige tous les fichiers Python"""
    print("🔧 CORRECTION AUTOMATIQUE DES IMPORTS")
    print("=" * 50)
    
    # Dossiers à traiter
    directories = [
        'tests',
        'automation_modules', 
        'tools',
        'monitoring',
        'LAUNCH'
    ]
    
    total_files = 0
    corrected_files = 0
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"\n📁 Traitement de {directory}/")
            for file_path in Path(directory).rglob('*.py'):
                total_files += 1
                if fix_imports_in_file(file_path):
                    corrected_files += 1
    
    print(f"\n🎯 RÉSULTAT:")
    print(f"   Fichiers traités: {total_files}")
    print(f"   Fichiers corrigés: {corrected_files}")
    print(f"   Fichiers inchangés: {total_files - corrected_files}")

if __name__ == "__main__":
    main()
