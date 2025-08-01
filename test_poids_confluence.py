#!/usr/bin/env python3
"""
🧮 TEST POIDS CONFLUENCE - VÉRIFICATION EXACTE
"""

# Poids de confluence du feature_calculator
CONFLUENCE_WEIGHTS = {
    'gamma_levels_proximity': 0.25,      # 25%
    'volume_confirmation': 0.18,         # 18%
    'vwap_trend_signal': 0.15,           # 15%
    'sierra_pattern_strength': 0.15,     # 15%
    'mtf_confluence_score': 0.12,        # 12%
    'smart_money_strength': 0.10,        # 10%
    'order_book_imbalance': 0.03,        # 3%
    'options_flow_bias': 0.02,           # 2%
}

def test_poids():
    print("🧮 VÉRIFICATION POIDS CONFLUENCE")
    print("="*50)
    
    total = 0.0
    for feature, weight in CONFLUENCE_WEIGHTS.items():
        print(f"{feature:25s}: {weight:6.2%} ({weight:.3f})")
        total += weight
    
    print("-"*50)
    print(f"{'TOTAL':25s}: {total:6.2%} ({total:.10f})")
    
    # Vérifications
    if total == 1.0:
        print("✅ PARFAIT: Total = 100.0% exactement")
    elif abs(total - 1.0) < 0.001:
        print(f"✅ OK: Total ≈ 100% (différence: {abs(total - 1.0):.10f})")
    else:
        print(f"❌ ERREUR: Total ≠ 100% (différence: {abs(total - 1.0):.10f})")
        if total > 1.0:
            print(f"   → SURPLUS de {(total - 1.0)*100:.3f}%")
        else:
            print(f"   → MANQUE {(1.0 - total)*100:.3f}%")
    
    # Calcul manuel pour double-vérification
    calcul_manuel = 0.25 + 0.18 + 0.15 + 0.15 + 0.12 + 0.10 + 0.03 + 0.02
    print(f"\n🔢 Calcul manuel: {calcul_manuel:.10f}")
    
    if calcul_manuel == total:
        print("✅ Cohérence: Calcul automatique = Calcul manuel")
    else:
        print(f"❌ Incohérence: Différence = {abs(calcul_manuel - total):.10f}")

if __name__ == "__main__":
    test_poids()