#!/usr/bin/env python3
"""
Test connexion données ES réelles - Version Définitive
"""

import os
import sys
import socket
import time
from datetime import datetime

def test_connexion_reelle_definitif():
    """Test définitif de la connexion données réelles"""
    
    print("🧪 TEST DÉFINITIF CONNEXION DONNÉES ES RÉELLES")
    print("=" * 50)
    
    # 1. Test TWS accessible
    print("\n🔌 Test 1: Accessibilité TWS")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7497))
        sock.close()
        
        if result == 0:
            print("   ✅ TWS accessible sur port 7497")
            tws_ok = True
        else:
            print("   ❌ TWS non accessible sur port 7497")
            tws_ok = False
    except Exception as e:
        print(f"   ❌ Erreur test TWS: {e}")
        tws_ok = False
    
    # 2. Test import IBKR Connector
    print("\n📦 Test 2: Import IBKR Connector")
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from core.ibkr_connector import IBKRConnector
        print("   ✅ IBKR Connector importé")
        connector_ok = True
    except ImportError as e:
        print(f"   ❌ Erreur import IBKR Connector: {e}")
        connector_ok = False
    
    # 3. Test configuration
    print("\n⚙️ Test 3: Configuration données réelles")
    try:
        from config.automation_config import get_automation_config
        config = get_automation_config()
        
        if hasattr(config, 'simulation_mode') and not config.simulation_mode:
            print("   ✅ Configuration: Mode simulation désactivé")
            config_ok = True
        else:
            print("   ❌ Configuration: Mode simulation encore actif")
            config_ok = False
    except Exception as e:
        print(f"   ❌ Erreur configuration: {e}")
        config_ok = False
    
    # Résumé
    print("\n📊 RÉSUMÉ TESTS")
    print("=" * 30)
    print(f"   TWS Accessible: {'✅' if tws_ok else '❌'}")
    print(f"   IBKR Connector: {'✅' if connector_ok else '❌'}")
    print(f"   Configuration: {'✅' if config_ok else '❌'}")
    
    all_tests_ok = tws_ok and connector_ok and config_ok
    
    if all_tests_ok:
        print("\n✅ TOUS LES TESTS RÉUSSIS")
        print("✅ Prêt pour données ES réelles")
    else:
        print("\n❌ TESTS ÉCHOUÉS")
        print("❌ Correction nécessaire")
    
    return all_tests_ok

if __name__ == "__main__":
    success = test_connexion_reelle_definitif()
    exit(0 if success else 1)
