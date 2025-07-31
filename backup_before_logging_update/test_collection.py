#!/usr/bin/env python3
"""
Test de la collection de données
"""

from data_collection_main import DataCollectionManager
import time

print("TEST COLLECTION DE DONNÉES\n")

# Créer le manager
manager = DataCollectionManager()

print("1. État initial:")
print(f"   - Snapshots en mémoire: {len(manager.current_session_snapshots)}")
print(f"   - Snapshots collectés: {manager.snapshots_collected}")
print(f"   - Collection active: {manager.is_collecting}")

print("\n2. Simulation de 10 snapshots...")
for i in range(10):
    manager._simulate_snapshot_collection()
    print(f"   Snapshot {i+1} collecté")
    time.sleep(0.1)  # Petite pause

print(f"\n3. État après simulation:")
print(f"   - Snapshots collectés: {manager.snapshots_collected}")
print(f"   - Collection active: {manager.is_collecting}")

print("\n4. Test organisation des données...")
manager._organize_data()
print("   ✅ Organisation terminée")

print("\n5. Vérification du statut...")
status = manager.get_status()
print(f"   - Session: {status['session']['id']}")
print(f"   - Snapshots: {status['session']['snapshots_collected']}")
print(f"   - Stockage: {status['storage']['total_mb']:.2f} MB")

print("\n6. Test collection directe...")
success = manager.collector.collect_trade_snapshot({
    'timestamp': '2025-06-27T00:00:00',
    'snapshot_type': 'test',
    'trade_id': 'TEST_001',
    'market_snapshot': {'close': 4500},
    'battle_navale_result': {'signal': 0.8}
})
print(f"   - Collection directe: {'✅ Succès' if success else '❌ Échec'}")

# Récupérer les stats du collector
stats = manager.collector.get_collection_statistics()
print(f"\n7. Statistiques collector:")
print(f"   - Snapshots traités: {stats['collection_stats']['snapshots_processed']}")
print(f"   - Qualité globale: {stats['data_quality_summary']['overall_quality']}")

print("\n✅ Test terminé!")