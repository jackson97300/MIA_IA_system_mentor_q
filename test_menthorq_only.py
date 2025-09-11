#!/usr/bin/env python3
"""
Test séparé pour MenthorQ seulement
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_menthorq_only():
    """Test MenthorQ seul"""
    print("🧪 TEST MENTHORQ SEUL")
    print("=" * 40)
    
    try:
        print("1. Import MenthorQ...")
        from features.menthorq_integration import MenthorQIntegration
        print("   ✅ Import OK")
        
        print("2. Initialisation...")
        menthorq = MenthorQIntegration()
        print("   ✅ Initialisation OK")
        
        print("3. Parsing...")
        levels = menthorq.parse_menthorq_data()  # Pas de raw_data pour forcer les vraies données
        print("   ✅ Parsing OK")
        
        if levels:
            print(f"   ✅ Résultat: {levels.symbol}")
            print(f"   Call Resistance: {levels.call_resistance}")
            print(f"   Put Support: {levels.put_support}")
            print(f"   HVL: {levels.hvl}")
            print(f"   GEX Levels: {len([v for v in levels.gex_levels if v > 0])}")
            print(f"   BL Levels: {len([v for v in levels.bl_levels if v > 0])}")
        else:
            print("   ❌ Résultat: None")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_menthorq_only()
