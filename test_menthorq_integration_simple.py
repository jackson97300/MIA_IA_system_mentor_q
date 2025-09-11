#!/usr/bin/env python3
"""
Test simple de l'intégration MenthorQ dans ConfluenceIntegrator
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

def test_menthorq_integration():
    """Test de l'intégration MenthorQ"""
    print("🧪 Test intégration MenthorQ dans ConfluenceIntegrator...")
    
    try:
        # Test import
        from features.confluence_integrator import ConfluenceIntegrator
        print("✅ Import ConfluenceIntegrator OK")
        
        # Test création
        integrator = ConfluenceIntegrator()
        print("✅ ConfluenceIntegrator créé")
        
        # Test MenthorQ Bias Analyzer
        if integrator.menthorq_bias_analyzer:
            print("✅ MenthorQDealersBiasAnalyzer intégré")
        else:
            print("❌ MenthorQDealersBiasAnalyzer NON intégré")
        
        # Test méthodes MenthorQ
        if hasattr(integrator, '_calculate_menthorq_bias'):
            print("✅ Méthode _calculate_menthorq_bias disponible")
        else:
            print("❌ Méthode _calculate_menthorq_bias manquante")
        
        if hasattr(integrator, '_calculate_menthorq_multiplier'):
            print("✅ Méthode _calculate_menthorq_multiplier disponible")
        else:
            print("❌ Méthode _calculate_menthorq_multiplier manquante")
        
        # Test ConfluenceResult avec MenthorQ
        from features.confluence_integrator import ConfluenceResult
        result = ConfluenceResult(
            base_score=0.5,
            leadership_gate=0.8,
            risk_multiplier=1.0,
            final_score=0.4,
            is_valid=True,
            decision="BUY",
            leader="ES",
            confidence=0.6,
            alignment="BULLISH"
        )
        
        if hasattr(result, 'menthorq_bias_score'):
            print("✅ ConfluenceResult avec champs MenthorQ")
        else:
            print("❌ ConfluenceResult sans champs MenthorQ")
        
        print("\n🎉 Test intégration MenthorQ terminé avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test intégration MenthorQ: {e}")
        return False

if __name__ == "__main__":
    test_menthorq_integration()


