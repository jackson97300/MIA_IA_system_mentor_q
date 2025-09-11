#!/usr/bin/env python3
"""
Test séparé pour Dealer's Bias seulement
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dealers_bias_only():
    """Test Dealer's Bias seul"""
    print("🧪 TEST DEALER'S BIAS SEUL")
    print("=" * 40)
    
    try:
        print("1. Import modules...")
        from features.menthorq_processor import MenthorQProcessor
        from features.menthorq_dealers_bias import MenthorQDealersBiasAnalyzer
        print("   ✅ Imports OK")
        
        print("2. Initialisation...")
        processor = MenthorQProcessor()
        analyzer = MenthorQDealersBiasAnalyzer(processor)
        print("   ✅ Initialisation OK")
        
        print("3. Calcul...")
        result = analyzer.calculate_menthorq_dealers_bias(5295.0, "ES", 20.0)
        print("   ✅ Calcul OK")
        
        if result:
            print(f"   ✅ Résultat: {result.dealers_bias_score:.3f}")
            print(f"   Direction: {result.direction.value}")
            print(f"   Strength: {result.strength.value}")
        else:
            print("   ❌ Résultat: None")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dealers_bias_only()



