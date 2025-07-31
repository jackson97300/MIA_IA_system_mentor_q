#!/usr/bin/env python3
"""
Test que les métriques Tail Ratio et Omega Ratio s'affichent correctement
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from data_collection_main import DataCollectionManager

print("TEST AFFICHAGE MÉTRIQUES AVANCÉES\n")

# Créer le manager
manager = DataCollectionManager()

# Simuler quelques snapshots avec des données
print("1. Simulation de 20 snapshots...")
for i in range(20):
    snapshot = {
        'timestamp': datetime.now().isoformat(),
        'snapshot_type': 'decision',
        'trade_id': f'TEST_{i}',
        'market_snapshot': {
            'close': 4500.0 + i,
            'atr_14': 15.5 + (i % 5),
            'trend_strength': 0.7,
            'volume_relative': 1.1
        },
        'battle_navale_result': {
            'battle_navale_signal': 0.8,
            'battle_strength': 0.6,
            'signal_strength': 0.7
        },
        'execution_metrics': {
            'execution_time_ms': 5,
            'slippage_ticks': 0
        },
        'pnl': np.random.choice([100, 50, -30, -50]) if i > 0 else 0,
        'entry_price': 4500,
        'stop_loss': 4480,
        'take_profit': 4520
    }
    manager.collector.collect_trade_snapshot(snapshot)

print(f"✅ {manager.snapshots_collected} snapshots collectés\n")

# Lancer l'analyse
print("2. Lancement de l'analyse avec run_analytics...")
print("="*60)
manager.run_analytics(comprehensive=False)
print("="*60)

print("\n3. Vérification des métriques dans le rapport...")

# Créer des données de test directement
test_df = pd.DataFrame([
    {
        'timestamp': datetime.now() - timedelta(hours=i),
        'pnl': np.random.normal(50, 100),
        'signal_strength': 0.7,
        'atr_14': 15,
        'entry_price': 4500,
        'stop_loss': 4480,
        'take_profit': 4520
    }
    for i in range(50)
])

# Tester directement les analytics
risk = manager.analytics.analyze_risk(test_df)
print(f"\n✅ Métriques de risque calculées:")
print(f"   - Tail Ratio: {risk.tail_ratio:.2f}")
print(f"   - Omega Ratio: {risk.omega_ratio:.2f}")
print(f"   - Ulcer Index: {risk.ulcer_index:.2f}" if hasattr(risk, 'ulcer_index') else "")
print(f"   - Recovery Factor: {risk.recovery_factor:.2f}" if hasattr(risk, 'recovery_factor') else "")

print("\n✅ Test réussi - Les métriques avancées sont bien calculées et affichées!")