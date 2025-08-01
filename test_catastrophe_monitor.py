#!/usr/bin/env python3
"""
Test simple du Catastrophe Monitor
Lancez avec: python test_catastrophe_monitor.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.catastrophe_monitor import CatastropheMonitor, CatastropheLevel

def test_catastrophe_monitor():
    """Test du Catastrophe Monitor"""
    print("🛡️ Test Catastrophe Monitor...")
    
    # Créer monitor avec limites de test
    config = {
        'daily_loss_limit': 100.0,      # $100 pour test
        'max_consecutive_losses': 3,    # 3 pertes pour test
        'max_position_size': 1          # 1 contrat pour test
    }
    
    monitor = CatastropheMonitor(config)
    
    # Test 1: Conditions normales
    print("\n✅ Test 1: Conditions normales")
    alert = monitor.check_catastrophe_conditions(
        current_pnl=-50.0,    # Perte acceptable
        account_balance=5000.0,
        position_size=1
    )
    print(f"Niveau: {alert.level.value}, Action: {alert.action_required}")
    assert alert.level == CatastropheLevel.NORMAL
    
    # Test 2: Perte journalière excessive
    print("\n🚨 Test 2: Perte journalière excessive")
    alert = monitor.check_catastrophe_conditions(
        current_pnl=-150.0,   # > limite de $100
        account_balance=5000.0,
        position_size=1
    )
    print(f"Niveau: {alert.level.value}, Trigger: {alert.trigger}")
    print(f"Action: {alert.action_required}")
    assert alert.level == CatastropheLevel.EMERGENCY
    
    # Test 3: Pertes consécutives
    print("\n⚠️ Test 3: Pertes consécutives")
    # Simuler 4 pertes consécutives
    for i in range(4):
        monitor.record_trade_result(pnl=-25.0, is_winner=False)
    
    alert = monitor.check_catastrophe_conditions(
        current_pnl=-50.0,
        account_balance=5000.0,
        position_size=1
    )
    print(f"Niveau: {alert.level.value}, Pertes consécutives: {monitor.consecutive_losses}")
    print(f"Action: {alert.action_required}")
    assert alert.level == CatastropheLevel.DANGER
    
    # Test 4: Position trop grande
    print("\n⚠️ Test 4: Position trop grande")
    alert = monitor.check_catastrophe_conditions(
        current_pnl=-30.0,
        account_balance=5000.0,
        position_size=3  # > limite de 1
    )
    print(f"Niveau: {alert.level.value}, Position: 3 (max: 1)")
    print(f"Action: {alert.action_required}")
    assert alert.level == CatastropheLevel.DANGER
    
    # Test 5: Status summary
    print("\n📊 Test 5: Status Summary")
    status = monitor.get_status_summary()
    print(f"Emergency stop actif: {status['emergency_stop_active']}")
    print(f"Alertes générées: {status['stats']['alerts_generated']}")
    print(f"Dernière alerte: {status['last_alert']}")
    
    print("\n✅ Tous les tests passés!")
    print("🛡️ Catastrophe Monitor opérationnel")

if __name__ == "__main__":
    test_catastrophe_monitor()