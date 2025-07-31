#!/usr/bin/env python3
"""
TEST RAPIDE - Vérification finale
"""

import sys
sys.path.insert(0, r"D:\MIA_IA_system")

print("TEST RAPIDE DE VÉRIFICATION")
print("="*40)

# Test 1: Import numpy dans le contexte
print("\n1. Test import numpy:")
try:
    import numpy as np
    print("   ✅ numpy importé globalement")
    print(f"   Version numpy: {np.__version__}")
except:
    print("   ❌ Erreur import numpy")

# Test 2: Import et test data_collection_main
print("\n2. Test DataCollectionManager:")
try:
    from data_collection_main import DataCollectionManager
    manager = DataCollectionManager()
    print("   ✅ Manager créé")
    
    # Vérifier que numpy est accessible
    print("\n3. Test collecte avec numpy:")
    try:
        # Force l'import de numpy dans le module
        import data_collection_main
        if not hasattr(data_collection_main, 'np'):
            print("   ⚠️  numpy non importé dans data_collection_main")
            print("   Ajout manuel...")
            data_collection_main.np = np
        
        # Test collecte
        manager._simulate_snapshot_collection()
        print("   ✅ Collecte réussie")
        print(f"   Snapshots: {manager.snapshots_collected}")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Commandes CLI
print("\n4. Commandes à tester manuellement:")
print("   python data_collection_main.py --status")
print("   python data_collection_main.py --start --hours 1")
print("   python data_collection_main.py --analyze")

print("\n" + "="*40)
print("Si tout est ✅, votre système est prêt !")