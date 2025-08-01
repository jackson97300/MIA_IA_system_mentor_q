#!/usr/bin/env python3
"""
🔧 DEBUG TEST - Identification problèmes importation
Test minimal pour identifier les erreurs d'import
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test des imports critiques un par un"""
    print("🔧 TEST IMPORTS CRITIQUES")
    print("=" * 50)
    
    # Test 1: Core logger
    try:
        from core.logger import get_logger
        print("✅ Core logger: OK")
    except Exception as e:
        print(f"❌ Core logger: {e}")
        traceback.print_exc()
    
    # Test 2: Core base_types
    try:
        from core.base_types import MarketData
        print("✅ Core base_types: OK")
    except Exception as e:
        print(f"❌ Core base_types: {e}")
        traceback.print_exc()
    
    # Test 3: IBKR Connector
    try:
        from core.ibkr_connector import create_ibkr_connector
        print("✅ IBKR Connector: OK")
    except Exception as e:
        print(f"❌ IBKR Connector: {e}")
        traceback.print_exc()
    
    # Test 4: Advanced Features
    try:
        from features.advanced import get_advanced_features_status
        print("✅ Advanced Features: OK")
    except Exception as e:
        print(f"❌ Advanced Features: {e}")
        traceback.print_exc()
    
    # Test 5: Delta Divergence spécifiquement
    try:
        from features.advanced.delta_divergence import create_delta_divergence_detector
        print("✅ Delta Divergence: OK")
    except Exception as e:
        print(f"❌ Delta Divergence: {e}")
        traceback.print_exc()
    
    # Test 6: Tick Momentum spécifiquement
    try:
        from features.advanced.tick_momentum import create_tick_momentum_calculator
        print("✅ Tick Momentum: OK")
    except Exception as e:
        print(f"❌ Tick Momentum: {e}")
        traceback.print_exc()
    
    # Test 7: Sierra Config
    try:
        from config.sierra_config import create_paper_trading_config
        print("✅ Sierra Config: OK")
    except Exception as e:
        print(f"❌ Sierra Config: {e}")
        traceback.print_exc()
    
    # Test 8: Automation Main
    try:
        from automation_main import MIAAutomationSystem, AutomationConfig
        print("✅ Automation Main: OK")
    except Exception as e:
        print(f"❌ Automation Main: {e}")
        traceback.print_exc()

def test_advanced_features_detailed():
    """Test détaillé des features avancées"""
    print("\n🔧 TEST FEATURES AVANCÉES DÉTAILLÉ")
    print("=" * 50)
    
    try:
        from features.advanced import get_advanced_features_status
        status = get_advanced_features_status()
        print(f"✅ Status: {status['success_rate']}")
        print(f"✅ Available: {status['available_features']}")
        print(f"❌ Failed: {status['unavailable_features']}")
        
        if status['import_errors']:
            print("📋 Erreurs d'import:")
            for feature, error in status['import_errors'].items():
                print(f"   {feature}: {error}")
                
    except Exception as e:
        print(f"❌ Test features avancées: {e}")
        traceback.print_exc()

def test_simulation_mode():
    """Test mode simulation"""
    print("\n🔧 TEST MODE SIMULATION")
    print("=" * 50)
    
    try:
        # Test création IBKR en mode simulation
        from core.ibkr_connector import create_ibkr_connector
        
        ibkr = create_ibkr_connector({
            'ibkr_host': '127.0.0.1',
            'ibkr_port': 7497,
            'ibkr_client_id': 1,
            'simulation_mode': True
        })
        
        print("✅ IBKR Connector créé en mode simulation")
        
        # Test features avancées
        from features.advanced import get_all_advanced_features
        features = get_all_advanced_features()
        print(f"✅ Features avancées chargées: {len(features)}")
        
        for name, feature in features.items():
            print(f"   - {name}: {type(feature).__name__}")
            
    except Exception as e:
        print(f"❌ Test simulation: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_imports()
    test_advanced_features_detailed()
    test_simulation_mode()
    
    print("\n🎯 DEBUG COMPLET")
    print("=" * 50) 