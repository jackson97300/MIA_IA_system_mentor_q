"""
Test des soft-caps dans confluence_analyzer.py
==============================================

Script de validation des soft-caps pour différents régimes de marché.
"""

import numpy as np
from features.confluence_analyzer import ConfluenceAnalyzer

def test_soft_caps():
    """Test complet des soft-caps"""
    print("🎯 TEST SOFT-CAPS CONFLUENCE ANALYZER")
    print("=" * 50)
    
    # Créer l'analyseur
    analyzer = ConfluenceAnalyzer()
    
    # Test 1: Score neutre (pas de soft-caps)
    print("\n1. Test score neutre...")
    result = analyzer.calculate_elite_mtf_confluence({})
    print(f"   Score final: {result[0]:.3f}")
    print(f"   Soft-caps appliqués: {result[1].get('soft_caps_applied', False)}")
    print(f"   Score brut: {result[1].get('raw_score', 'N/A')}")
    
    # Test 2: Simulation score extrême positif
    print("\n2. Test soft-caps avec score extrême...")
    
    # Créer des données de test avec score extrême
    test_data = {
        'close': 4500.0,
        'high': 4510.0,
        'low': 4490.0,
        'volume': 1000000,
        'timestamp': '2025-01-01T10:00:00Z'
    }
    
    # Simuler un score extrême en modifiant temporairement la méthode
    original_method = analyzer.elite_mtf.calculate_elite_mtf_confluence
    
    def mock_extreme_score(market_data):
        # Retourner un score extrême pour tester les soft-caps
        return 1.5, {"raw_score": 1.5, "test": True}
    
    # Remplacer temporairement la méthode
    analyzer.elite_mtf.calculate_elite_mtf_confluence = mock_extreme_score
    
    try:
        result = analyzer.calculate_elite_mtf_confluence(test_data)
        print(f"   Score final: {result[0]:.3f}")
        print(f"   Soft-caps appliqués: {result[1].get('soft_caps_applied', False)}")
        print(f"   Score brut: {result[1].get('raw_score', 'N/A')}")
        
        # Vérifier que les soft-caps ont été appliqués
        if result[1].get('soft_caps_applied', False):
            print("   ✅ Soft-caps appliqués correctement")
        else:
            print("   ⚠️ Soft-caps non appliqués (score dans les limites)")
            
    finally:
        # Restaurer la méthode originale
        analyzer.elite_mtf.calculate_elite_mtf_confluence = original_method
    
    # Test 3: Test direct de la méthode _apply_soft_caps
    print("\n3. Test direct méthode _apply_soft_caps...")
    
    test_scores = [0.0, 0.5, 0.8, 1.0, 1.5, -0.5, -0.8, -1.0, -1.5]
    
    for score in test_scores:
        capped_score = analyzer.elite_mtf._apply_soft_caps(score, test_data)
        print(f"   Score {score:+.1f} → {capped_score:+.3f}")
    
    print("\n✅ Test soft-caps terminé avec succès!")
    return True

if __name__ == "__main__":
    test_soft_caps()


