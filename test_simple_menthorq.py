#!/usr/bin/env python3
"""
Test simple MenthorQ
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_simple_menthorq():
    """Test simple MenthorQ"""
    print("🔍 TEST SIMPLE MENTHORQ")
    print("=" * 30)
    
    try:
        print("1. Import data_reader...")
        from features.data_reader import get_menthorq_market_data
        print("   ✅ Import OK")
        
        print("2. Récupération des données...")
        menthorq_data = get_menthorq_market_data("ES")
        print("   ✅ Données récupérées")
        
        if menthorq_data and 'menthorq_levels' in menthorq_data:
            print(f"3. Niveaux trouvés: {len(menthorq_data['menthorq_levels'])}")
            for i, (name, price) in enumerate(menthorq_data['menthorq_levels'].items(), 1):
                print(f"   {i:2d}. {name} = {price}")
        else:
            print("3. ❌ Pas de données MenthorQ")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_menthorq()



