#!/usr/bin/env python3
"""
Test direct du Dealer's Bias
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dealers_bias_direct():
    """Test direct du Dealer's Bias"""
    print("🎯 TEST DIRECT DEALER'S BIAS")
    print("=" * 40)
    
    try:
        print("1. Récupération des données MenthorQ...")
        from features.data_reader import get_menthorq_market_data
        menthorq_data = get_menthorq_market_data("ES")
        
        if menthorq_data and 'menthorq_levels' in menthorq_data:
            print(f"   📊 {len(menthorq_data['menthorq_levels'])} niveaux trouvés")
            
            # Afficher les premiers niveaux
            for i, (name, price) in enumerate(list(menthorq_data['menthorq_levels'].items())[:10], 1):
                print(f"   {i:2d}. {name} = {price}")
            
            print("\n2. Test du Dealer's Bias...")
            from menthorq_dealers_bias import MenthorQDealersBiasAnalyzer
            from features.menthorq_processor import MenthorQProcessor
            
            processor = MenthorQProcessor()
            analyzer = MenthorQDealersBiasAnalyzer(menthorq_processor=processor)
            
            # Test avec les données réelles
            current_price = 4500.0
            vix_level = 20.0
            
            result = analyzer.dealers_bias_with_menthorq(
                price=current_price,
                vix=vix_level,
                tick_size=0.25,
                levels=menthorq_data['menthorq_levels']
            )
            
            print(f"   Direction: {result.get('direction', 'N/A')}")
            print(f"   Strength: {result.get('strength', 'N/A')}")
            print(f"   Score: {result.get('bias_score', 0):.3f}")
            print(f"   Quality: {result.get('quality_score', 0):.3f}")
            
        else:
            print("   ❌ Pas de données MenthorQ")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dealers_bias_direct()



