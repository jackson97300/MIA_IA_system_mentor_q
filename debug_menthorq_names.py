#!/usr/bin/env python3
"""
Debug des noms MenthorQ
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_menthorq_names():
    """Debug des noms MenthorQ"""
    print("🔍 DEBUG NOMS MENTHORQ")
    print("=" * 40)
    
    try:
        from features.data_reader import get_menthorq_market_data
        menthorq_data = get_menthorq_market_data("ES")
        
        if menthorq_data and 'menthorq_levels' in menthorq_data:
            print(f"📊 {len(menthorq_data['menthorq_levels'])} niveaux trouvés:")
            print()
            
            for i, (level_name, price) in enumerate(menthorq_data['menthorq_levels'].items(), 1):
                print(f"{i:2d}. {level_name} = {price}")
                
            print()
            print("🔍 Analyse des noms:")
            gamma_count = sum(1 for name in menthorq_data['menthorq_levels'].keys() if 'gamma' in name)
            blind_count = sum(1 for name in menthorq_data['menthorq_levels'].keys() if 'blind' in name)
            swing_count = sum(1 for name in menthorq_data['menthorq_levels'].keys() if 'swing' in name)
            
            print(f"   Gamma levels: {gamma_count}")
            print(f"   Blind spots: {blind_count}")
            print(f"   Swing levels: {swing_count}")
            
        else:
            print("❌ Pas de données MenthorQ")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_menthorq_names()


