#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test spécifique de _mq_gex_score
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_mq_score():
    """Test spécifique de _mq_gex_score"""
    
    print("🔍 TEST SPÉCIFIQUE _mq_gex_score")
    print("=" * 40)
    
    try:
        from core.menthorq_distance_trading import MenthorQDistanceTrader
        
        # Créer une instance
        trader = MenthorQDistanceTrader()
        
        # Données de test simples
        price = 4500.0
        mq_levels = {
            'gamma_wall': {
                'call_resistance_1': 4500.25,  # 1 tick au-dessus
                'put_support_1': 4499.75      # 1 tick en dessous
            }
        }
        tick = 0.25
        config = {
            "mq_tolerance_ticks": {"gamma_wall": 10, "hvl": 10, "gex": 10}
        }
        
        print(f"Prix: {price}")
        print(f"Niveaux: {mq_levels}")
        print(f"Tick: {tick}")
        print(f"Tolérance: {config['mq_tolerance_ticks']}")
        
        # Test direct de _mq_gex_score
        result = trader._mq_gex_score(price, mq_levels, tick, config)
        
        print(f"\nRésultat: {result}")
        
        if result:
            print("✅ Score calculé avec succès")
            print(f"   - Best level: {result.get('best_level')}")
            print(f"   - Score: {result.get('score')}")
            print(f"   - Side: {result.get('side')}")
            print(f"   - Distance: {result.get('distance_ticks')} ticks")
        else:
            print("❌ Aucun score calculé")
            
            # Debug étape par étape
            print("\n🔍 DEBUG ÉTAPE PAR ÉTAPE:")
            for level_type, levels in mq_levels.items():
                print(f"Type: {level_type}")
                for level_name, level_price in levels.items():
                    distance_ticks = abs(price - level_price) / tick
                    tolerance = config["mq_tolerance_ticks"].get("gamma_wall", 3)
                    print(f"  - {level_name}: {level_price}")
                    print(f"    Distance: {distance_ticks} ticks")
                    print(f"    Tolérance: {tolerance} ticks")
                    print(f"    Dans tolérance: {distance_ticks <= tolerance}")
                    
                    if distance_ticks <= tolerance:
                        distance_score = max(0, 1 - (distance_ticks / tolerance))
                        print(f"    Score: {distance_score}")
                        
                        # Déterminer le side
                        if "call" in level_name.lower() or "resistance" in level_name.lower():
                            side = "SHORT"
                        elif "put" in level_name.lower() or "support" in level_name.lower():
                            side = "LONG"
                        else:
                            side = "LONG" if price < level_price else "SHORT"
                        print(f"    Side: {side}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mq_score()
