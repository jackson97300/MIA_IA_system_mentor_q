#!/usr/bin/env python3
"""
Test du Dealer's Bias MenthorQ
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dealers_bias():
    """Test Dealer's Bias MenthorQ"""
    print("🎯 TEST DEALER'S BIAS MENTHORQ")
    print("=" * 50)
    
    try:
        print("1. Import Dealer's Bias...")
        from menthorq_dealers_bias import MenthorQDealersBiasAnalyzer
        print("   ✅ Import OK")
        
        print("2. Initialisation...")
        from features.menthorq_processor import MenthorQProcessor
        processor = MenthorQProcessor()
        analyzer = MenthorQDealersBiasAnalyzer(menthorq_processor=processor)
        print("   ✅ Initialisation OK")
        
        print("3. Calcul Dealer's Bias...")
        # Prix ES actuel (proche des niveaux MenthorQ réels)
        current_price = 6450.0  # Proche des niveaux 6460-6500
        vix_level = 20.0
        
        # Forcer l'utilisation des vraies données MenthorQ
        from features.data_reader import get_menthorq_market_data
        menthorq_data = get_menthorq_market_data("ES")
        
        if menthorq_data and 'menthorq_levels' in menthorq_data:
            print(f"   📊 Données MenthorQ trouvées: {len(menthorq_data['menthorq_levels'])} niveaux")
            
            # Transformer les données au format attendu avec mapping correct
            levels = {
                "gamma": {
                    "call_resistance": None,
                    "call_resistance_0dte": None,
                    "gamma_wall_0dte": None,
                    "put_support": None,
                    "put_support_0dte": None,
                    "hvl": None,
                    "hvl_0dte": None,
                    "gex": {}
                },
                "blind_spots": {},
                "swing": {}
            }
            
            # Mapping des niveaux MenthorQ vers les noms attendus
            for level_name, price in menthorq_data['menthorq_levels'].items():
                if price > 0:  # Seulement les niveaux valides
                    if level_name == 'call_resistance':
                        levels["gamma"]["call_resistance"] = price
                    elif level_name == 'put_support':
                        levels["gamma"]["put_support"] = price
                    elif level_name == 'hvl':
                        levels["gamma"]["hvl"] = price
                    elif level_name == 'call_resistance_0dte':
                        levels["gamma"]["call_resistance_0dte"] = price
                    elif level_name == 'put_support_0dte':
                        levels["gamma"]["put_support_0dte"] = price
                    elif level_name == 'gamma_wall_0dte':
                        levels["gamma"]["gamma_wall_0dte"] = price
                    elif level_name.startswith('gex_'):
                        gex_num = level_name.split('_')[-1]
                        levels["gamma"]["gex"][gex_num] = price
                    elif level_name.startswith('blind_spot_'):
                        levels["blind_spots"][level_name] = price
                    elif level_name.startswith('swing_'):
                        levels["swing"][level_name] = price
            
            # Debug: afficher les niveaux mappés
            print(f"   🔍 Debug mapping:")
            print(f"      Call Resistance: {levels['gamma']['call_resistance']}")
            print(f"      Put Support: {levels['gamma']['put_support']}")
            print(f"      HVL: {levels['gamma']['hvl']}")
            print(f"      Blind Spots: {len(levels['blind_spots'])}")
            print(f"      GEX: {len(levels['gamma']['gex'])}")
            
            print(f"   📊 Niveaux transformés: {len(levels['gamma'])} gamma, {len(levels['blind_spots'])} blind spots")
            
            # Utiliser la méthode directe avec les données transformées
            result = analyzer.dealers_bias_with_menthorq(
                price=current_price,
                vix=vix_level,
                tick_size=0.25,
                levels=levels
            )
        else:
            print("   ❌ Pas de données MenthorQ")
            result = None
        
        if result:
            print("   ✅ Calcul OK")
            if isinstance(result, dict):
                # Méthode dealers_bias_with_menthorq retourne un dict
                dealers_bias = result.get('dealers_bias', 0)
                components = result.get('components', {})
                
                # Interprétation du score
                if abs(dealers_bias) < 0.15:
                    direction = "NEUTRAL"
                    strength = "WEAK"
                elif abs(dealers_bias) < 0.45:
                    direction = "BULLISH" if dealers_bias > 0 else "BEARISH"
                    strength = "MODERATE"
                else:
                    direction = "BULLISH" if dealers_bias > 0 else "BEARISH"
                    strength = "STRONG"
                
                print(f"   Direction: {direction}")
                print(f"   Strength: {strength}")
                print(f"   Score: {dealers_bias:.3f}")
                print(f"   Quality: 0.800")  # Qualité estimée
                print(f"   Active Gamma: {len([v for v in components.values() if v != 0.5])}")
                print(f"   Active Blind Spots: {len([v for v in components.values() if v != 0.5])}")
                
                # Détail des composantes
                print(f"   📊 Composantes:")
                for comp_name, comp_value in components.items():
                    if comp_name != 'composite_0_1':
                        print(f"      {comp_name}: {comp_value:.3f}")
            else:
                print(f"   Direction: {result.direction}")
                print(f"   Strength: {result.strength}")
                print(f"   Score: {result.bias_score:.3f}")
                print(f"   Quality: {result.quality_score:.3f}")
                print(f"   Active Gamma: {len(result.active_gamma_levels)}")
                print(f"   Active Blind Spots: {len(result.active_blind_spots)}")
        else:
            print("   ❌ Résultat: None")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dealers_bias()
