#!/usr/bin/env python3
"""
TEST SIMPLE - Juste nos nouveaux modules
Sans connexions réseau
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.signal_explainer import create_signal_explainer
from core.catastrophe_monitor import create_catastrophe_monitor, CatastropheLevel
from core.base_types import MarketData
import pandas as pd

def test_integration_complete():
    """Test d'intégration simple de nos modules"""
    print("🧪 TEST INTÉGRATION COMPLÈTE - NOS NOUVEAUX MODULES")
    print("=" * 60)
    
    # Test 1: Création des modules
    print("\n1️⃣ CRÉATION MODULES")
    try:
        explainer = create_signal_explainer()
        print("✅ Signal Explainer créé")
        
        monitor = create_catastrophe_monitor({
            'daily_loss_limit': 200.0,
            'max_position_size': 1
        })
        print("✅ Catastrophe Monitor créé")
    except Exception as e:
        print(f"❌ Erreur création: {e}")
        return False
    
    # Test 2: Données de marché simulées
    print("\n2️⃣ DONNÉES MARCHÉ SIMULÉES")
    try:
        market_data = MarketData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            open=5247.0,
            high=5248.0,
            low=5246.0,
            close=5247.5,
            volume=1500,
            bid=5247.25,
            ask=5247.75
        )
        print(f"✅ Market Data: ES @ {market_data.close} (Vol: {market_data.volume})")
    except Exception as e:
        print(f"❌ Erreur market data: {e}")
        return False
    
    # Test 3: Signal Explainer avec confluence faible
    print("\n3️⃣ TEST SIGNAL EXPLAINER")
    try:
        reasons = explainer.explain_no_signal(
            market_data=market_data,
            confluence_score=0.65,  # Trop faible
            last_signal_time=0
        )
        
        explanation = explainer.format_explanation(reasons)
        print("🔍 EXPLICATION SIGNAL:")
        print(explanation)
        print("✅ Signal Explainer fonctionne")
    except Exception as e:
        print(f"❌ Erreur Signal Explainer: {e}")
        return False
    
    # Test 4: Catastrophe Monitor conditions normales
    print("\n4️⃣ TEST CATASTROPHE MONITOR - Conditions normales")
    try:
        alert = monitor.check_catastrophe_conditions(
            current_pnl=-50.0,      # Perte acceptable
            account_balance=5000.0,
            position_size=1
        )
        
        print(f"🛡️ Niveau alerte: {alert.level.value}")
        print(f"🛡️ Action: {alert.action_required}")
        print("✅ Catastrophe Monitor - Normal OK")
    except Exception as e:
        print(f"❌ Erreur Catastrophe Monitor: {e}")
        return False
    
    # Test 5: Catastrophe Monitor EMERGENCY
    print("\n5️⃣ TEST CATASTROPHE MONITOR - EMERGENCY")
    try:
        alert = monitor.check_catastrophe_conditions(
            current_pnl=-250.0,     # Perte excessive > 200
            account_balance=5000.0,
            position_size=1
        )
        
        print(f"🚨 Niveau alerte: {alert.level.value}")
        print(f"🚨 Trigger: {alert.trigger}")
        print(f"🚨 Action: {alert.action_required}")
        
        if alert.level == CatastropheLevel.EMERGENCY:
            print("✅ Catastrophe Monitor - EMERGENCY détecté correctement")
        else:
            print("❌ EMERGENCY pas détecté")
            return False
            
    except Exception as e:
        print(f"❌ Erreur Catastrophe Monitor Emergency: {e}")
        return False
    
    # Test 6: Simulation mini trading
    print("\n6️⃣ SIMULATION MINI TRADING")
    try:
        daily_pnl = 0.0
        consecutive_losses = 0
        
        # Simuler 5 trades
        trades = [
            (+75.0, True),   # Win
            (-50.0, False),  # Loss
            (+100.0, True),  # Win
            (-25.0, False),  # Loss
            (+150.0, True)   # Win
        ]
        
        for i, (pnl, is_winner) in enumerate(trades, 1):
            daily_pnl += pnl
            
            # Enregistrer dans monitor
            monitor.record_trade_result(pnl, is_winner)
            
            # Vérifier état après trade
            alert = monitor.check_catastrophe_conditions(
                current_pnl=daily_pnl,
                account_balance=5000.0,
                position_size=0  # Pas de position après trade
            )
            
            result = "WIN" if is_winner else "LOSS"
            print(f"  Trade {i}: {result} {pnl:+.2f}$ (Total: {daily_pnl:+.2f}$) - Alert: {alert.level.value}")
        
        print("✅ Simulation trading OK")
    except Exception as e:
        print(f"❌ Erreur simulation: {e}")
        return False
    
    # Test 7: Status final
    print("\n7️⃣ STATUS FINAL")
    try:
        status = monitor.get_status_summary()
        print(f"🛡️ Emergency stop: {status['emergency_stop_active']}")
        print(f"📊 P&L journalier: {status['daily_pnl']:+.2f}$")
        print(f"📉 Pertes consécutives: {status['consecutive_losses']}")
        print(f"🔔 Alertes générées: {status['alerts_today']}")
        print("✅ Status récupéré")
    except Exception as e:
        print(f"❌ Erreur status: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 TOUS LES TESTS PASSÉS - INTÉGRATION RÉUSSIE !")
    print("🔍 Signal Explainer: ✅ Fonctionnel")
    print("🛡️ Catastrophe Monitor: ✅ Fonctionnel") 
    print("🚀 PRÊT POUR CONNEXION IBKR !")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_integration_complete()
    if not success:
        sys.exit(1)
    print("\n🎯 Prochaine étape: Connecter à IBKR pour trading réel !")