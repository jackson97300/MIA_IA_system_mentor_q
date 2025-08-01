#!/usr/bin/env python3
"""
🔧 DEBUG TEST - Automation Integration
Test spécifique pour identifier le problème automation_main
"""

import sys
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

def test_automation_imports():
    """Test des imports automation_main"""
    print("🔧 TEST IMPORTS AUTOMATION_MAIN")
    print("=" * 50)
    
    # Test 1: Import AutomationConfig
    try:
        from automation_main import AutomationConfig
        print("✅ AutomationConfig: OK")
        
        # Test création instance
        config = AutomationConfig()
        print(f"✅ Config créée: max_position_size={config.max_position_size}")
        
    except Exception as e:
        print(f"❌ AutomationConfig: {e}")
        traceback.print_exc()
    
    # Test 2: Import MIAAutomationSystem
    try:
        from automation_main import MIAAutomationSystem
        print("✅ MIAAutomationSystem: OK")
        
        # Test création instance
        config = AutomationConfig()
        system = MIAAutomationSystem(config)
        print("✅ System créé: OK")
        
    except Exception as e:
        print(f"❌ MIAAutomationSystem: {e}")
        traceback.print_exc()
    
    # Test 3: Test méthode _calculate_options_bias
    try:
        from automation_main import MIAAutomationSystem, AutomationConfig
        
        config = AutomationConfig()
        system = MIAAutomationSystem(config)
        
        # Test données
        put_call_ratio = 1.05
        implied_vol = 0.22
        greeks = {
            'delta': 0.3,
            'gamma': 0.025,
            'theta': -0.012,
            'vega': 0.18
        }
        
        # Test méthode
        options_bias = system._calculate_options_bias(put_call_ratio, implied_vol, greeks)
        print(f"✅ _calculate_options_bias: {options_bias:.3f}")
        
    except Exception as e:
        print(f"❌ _calculate_options_bias: {e}")
        traceback.print_exc()

def test_automation_methods():
    """Test des méthodes automation"""
    print("\n🔧 TEST MÉTHODES AUTOMATION")
    print("=" * 50)
    
    try:
        from automation_main import MIAAutomationSystem, AutomationConfig
        
        config = AutomationConfig()
        system = MIAAutomationSystem(config)
        
        # Test méthodes disponibles
        methods = [method for method in dir(system) if not method.startswith('_')]
        print(f"✅ Méthodes disponibles: {len(methods)}")
        
        # Vérifier si _calculate_options_bias existe
        if hasattr(system, '_calculate_options_bias'):
            print("✅ _calculate_options_bias: Existe")
        else:
            print("❌ _calculate_options_bias: N'existe pas")
        
        # Test autres méthodes importantes
        important_methods = [
            '_calculate_position_size',
            '_calculate_stop_loss', 
            '_calculate_take_profit',
            '_risk_management_check'
        ]
        
        for method in important_methods:
            if hasattr(system, method):
                print(f"✅ {method}: Existe")
            else:
                print(f"❌ {method}: N'existe pas")
                
    except Exception as e:
        print(f"❌ Test méthodes: {e}")
        traceback.print_exc()

def test_automation_config():
    """Test configuration automation"""
    print("\n🔧 TEST CONFIGURATION AUTOMATION")
    print("=" * 50)
    
    try:
        from automation_main import AutomationConfig
        
        config = AutomationConfig()
        
        # Vérifier attributs importants
        important_attrs = [
            'max_position_size',
            'daily_loss_limit',
            'min_signal_confidence',
            'trading_start_hour',
            'trading_end_hour',
            'position_risk_percent',
            'max_daily_trades',
            'stop_loss_ticks',
            'take_profit_ratio',
            'ml_ensemble_enabled',
            'ml_min_confidence',
            'gamma_cycles_enabled',
            'confluence_threshold',
            'confluence_adaptive',
            'performance_update_interval',
            'health_check_interval',
            'ibkr_host',
            'ibkr_port',
            'ibkr_client_id',
            'log_level',
            'log_to_file'
        ]
        
        for attr in important_attrs:
            if hasattr(config, attr):
                value = getattr(config, attr)
                print(f"✅ {attr}: {value}")
            else:
                print(f"❌ {attr}: N'existe pas")
                
    except Exception as e:
        print(f"❌ Test config: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_automation_imports()
    test_automation_methods()
    test_automation_config()
    
    print("\n🎯 DEBUG AUTOMATION COMPLET")
    print("=" * 50) 