#!/usr/bin/env python3
"""
Script de test pour diagnostiquer le problème de lancement
"""

import sys
import traceback

def test_imports():
    """Test des imports critiques"""
    print("🔍 Test des imports...")
    
    try:
        print("  📦 Import core.logger...")
        from core.logger import get_logger
        print("    ✅ OK")
    except Exception as e:
        print(f"    ❌ ERREUR: {e}")
        return False
    
    try:
        print("  📦 Import automation_modules.config_manager...")
        from config.automation_config import AutomationConfig
        print("    ✅ OK")
    except Exception as e:
        print(f"    ❌ ERREUR: {e}")
        return False
    
    try:
        print("  📦 Import features.confluence_integrator...")
        from features.confluence_integrator import ConfluenceIntegrator
        print("    ✅ OK")
    except Exception as e:
        print(f"    ❌ ERREUR: {e}")
        return False
    
    return True

def test_syntax():
    """Test de la syntaxe du fichier principal"""
    print("\n🔍 Test de la syntaxe...")
    
    try:
        print("  📄 Compilation launch_24_7_orderflow_trading.py...")
        with open('launch_24_7_orderflow_trading.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Test de compilation
        compile(content, 'launch_24_7_orderflow_trading.py', 'exec')
        print("    ✅ Syntaxe OK")
        return True
    except SyntaxError as e:
        print(f"    ❌ ERREUR SYNTAXE: {e}")
        print(f"    📍 Ligne {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"    ❌ ERREUR: {e}")
        return False

def main():
    print("🚀 DIAGNOSTIC LANCEMENT MIA_IA_SYSTEM")
    print("=" * 50)
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ PROBLÈME D'IMPORTS DÉTECTÉ")
        return
    
    # Test 2: Syntaxe
    if not test_syntax():
        print("\n❌ PROBLÈME DE SYNTAXE DÉTECTÉ")
        return
    
    print("\n✅ TOUS LES TESTS PASSÉS")
    print("🎯 Le problème pourrait venir d'une erreur runtime")

if __name__ == "__main__":
    main()
