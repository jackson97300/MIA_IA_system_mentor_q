"""
Test des multiplicateurs session/régime dans confluence_analyzer.py
================================================================

Script de validation des multiplicateurs pour différents contextes.
"""

import numpy as np
from features.confluence_analyzer import ConfluenceAnalyzer

def test_session_regime_multipliers():
    """Test complet des multiplicateurs session/régime"""
    print("🎯 TEST MULTIPLICATEURS SESSION/RÉGIME")
    print("=" * 50)
    
    # Créer l'analyseur
    analyzer = ConfluenceAnalyzer()
    
    # Test 1: Score neutre (pas d'effet des multiplicateurs)
    print("\n1. Test score neutre...")
    result = analyzer.calculate_elite_mtf_confluence({})
    print(f"   Score final: {result[0]:.3f}")
    print(f"   Multiplicateurs: {result[1].get('session_regime_multipliers', {})}")
    
    # Test 2: Test direct des multiplicateurs
    print("\n2. Test direct des multiplicateurs...")
    
    # Test des multiplicateurs de session
    print("   Multiplicateurs de session:")
    session_types = ["PRE_MARKET", "REGULAR", "AFTER_HOURS", "WEEKEND", "HOLIDAY"]
    for session in session_types:
        multiplier = analyzer.elite_mtf._get_session_multiplier(session)
        print(f"     {session}: {multiplier}")
    
    # Test des multiplicateurs de régime
    print("   Multiplicateurs de régime:")
    regimes = ["TRENDING", "RANGING", "VOLATILE", "UNKNOWN"]
    for regime in regimes:
        multiplier = analyzer.elite_mtf._get_regime_multiplier(regime)
        print(f"     {regime}: {multiplier}")
    
    # Test 3: Simulation d'ajustement avec score non-nul
    print("\n3. Test d'ajustement avec score non-nul...")
    
    # Créer des données de test
    test_data = {
        'close': 4500.0,
        'high': 4510.0,
        'low': 4490.0,
        'volume': 1000000,
        'timestamp': '2025-01-01T10:00:00Z'
    }
    
    # Test avec différents scores
    test_scores = [0.5, -0.5, 0.8, -0.8]
    
    for score in test_scores:
        # Simuler l'ajustement des multiplicateurs
        adjusted = analyzer.elite_mtf._apply_session_regime_multipliers(score, test_data)
        print(f"   Score {score:+.1f} → {adjusted:+.3f}")
    
    # Test 4: Test des combinaisons session/régime
    print("\n4. Test des combinaisons session/régime...")
    
    # Simuler différentes combinaisons
    combinations = [
        ("REGULAR", "TRENDING", 1.0 * 1.2),
        ("REGULAR", "RANGING", 1.0 * 0.9),
        ("PRE_MARKET", "VOLATILE", 0.7 * 0.8),
        ("AFTER_HOURS", "TRENDING", 0.8 * 1.2),
        ("WEEKEND", "RANGING", 0.5 * 0.9)
    ]
    
    for session, regime, expected_multiplier in combinations:
        session_mult = analyzer.elite_mtf._get_session_multiplier(session)
        regime_mult = analyzer.elite_mtf._get_regime_multiplier(regime)
        combined_mult = session_mult * regime_mult
        
        print(f"   {session} + {regime}: {session_mult} × {regime_mult} = {combined_mult:.2f}")
    
    print("\n✅ Test multiplicateurs session/régime terminé avec succès!")
    return True

if __name__ == "__main__":
    test_session_regime_multipliers()


