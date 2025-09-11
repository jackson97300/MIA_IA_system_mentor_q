#!/usr/bin/env python3
"""
Test simplifié pour diagnostiquer le problème Dealer's Bias
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_simple():
    """Test simplifié étape par étape"""
    print("🔍 DIAGNOSTIC SIMPLIFIÉ")
    print("=" * 40)
    
    try:
        print("1. Import des modules...")
        from features.menthorq_processor import MenthorQProcessor
        print("   ✅ MenthorQProcessor importé")
        
        from features.menthorq_dealers_bias import MenthorQDealersBiasAnalyzer
        print("   ✅ MenthorQDealersBiasAnalyzer importé")
        
        print("2. Initialisation...")
        processor = MenthorQProcessor()
        print("   ✅ MenthorQProcessor initialisé")
        
        analyzer = MenthorQDealersBiasAnalyzer(processor)
        print("   ✅ MenthorQDealersBiasAnalyzer initialisé")
        
        print("3. Test de calcul...")
        result = analyzer.calculate_menthorq_dealers_bias(5295.0, "ES", 20.0)
        
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
    test_simple()



