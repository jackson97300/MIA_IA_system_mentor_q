#!/usr/bin/env python3
"""
Test du lazy loading features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_lazy_loading():
    """Test du lazy loading"""
    print("🔍 TEST LAZY LOADING FEATURES")
    print("=" * 50)
    
    try:
        # 1. Test import initial
        print("1. Import features module...")
        from features import get_features_status, is_module_available
        print("   ✅ Import OK")
        
        # 2. Test statut initial (sans charger)
        print("\n2. Statut initial (sans chargement):")
        status = get_features_status()
        
        for module_name, module_status in status.items():
            if module_name != 'summary':
                available = "✅" if module_status['available'] else "❌"
                loaded = "✅" if module_status['loaded'] else "❌"
                print(f"   {module_name}: {available} (chargé: {loaded})")
        
        print(f"\n📊 Résumé initial:")
        summary = status['summary']
        print(f"   Total modules: {summary['total_modules']}")
        print(f"   Disponibles: {summary['available_modules']}")
        print(f"   Chargés: {summary['loaded_modules']}")
        print(f"   Taux disponibilité: {summary['availability_rate']:.1%}")
        
        # 3. Test chargement d'un module
        print("\n3. Test chargement module 'order_book_imbalance':")
        from features import create_order_book_imbalance_calculator
        
        calculator = create_order_book_imbalance_calculator()
        if calculator:
            print("   ✅ Module chargé et instancié")
        else:
            print("   ❌ Échec chargement module")
        
        # 4. Vérifier statut après chargement
        print("\n4. Statut après chargement:")
        status_after = get_features_status()
        order_book_status = status_after['order_book_imbalance']
        print(f"   order_book_imbalance: {'✅' if order_book_status['loaded'] else '❌'} (chargé)")
        
        # 5. Test performance
        print("\n5. Test performance lazy loading:")
        import time
        
        start_time = time.time()
        from features import create_menthorq_integration
        menthorq = create_menthorq_integration()
        end_time = time.time()
        
        print(f"   Temps chargement MenthorQ: {(end_time - start_time)*1000:.1f}ms")
        
        if menthorq:
            print("   ✅ MenthorQ chargé avec succès")
        else:
            print("   ❌ Échec chargement MenthorQ")
        
        print("\n✅ Test lazy loading terminé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_lazy_loading()


