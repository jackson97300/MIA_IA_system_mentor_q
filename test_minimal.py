#!/usr/bin/env python3
"""
Test minimal pour isoler le problème
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_minimal():
    """Test minimal étape par étape"""
    print("🔍 TEST MINIMAL")
    print("=" * 30)
    
    try:
        print("1. Import...")
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
        
        print("4. Résultat...")
        if result:
            print(f"   ✅ Score: {result.dealers_bias_score:.3f}")
            print(f"   ✅ Direction: {result.direction.value}")
            print(f"   ✅ Strength: {result.strength.value}")
            print("🎉 SUCCÈS COMPLET !")
        else:
            print("   ❌ Résultat: None")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_minimal()



