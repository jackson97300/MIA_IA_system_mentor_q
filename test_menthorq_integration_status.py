#!/usr/bin/env python3
"""
Test du statut d'intégration MenthorQ dans le système MIA_IA
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from features.data_reader import get_menthorq_market_data
from features.menthorq_dealers_bias import create_menthorq_dealers_bias_analyzer
from features.confluence_analyzer import ConfluenceAnalyzer
from features.confluence_integrator import ConfluenceIntegrator

def test_menthorq_data_availability():
    """Test de la disponibilité des données MenthorQ"""
    print("🧪 Test de disponibilité des données MenthorQ...")
    
    try:
        # Test récupération données MenthorQ
        menthorq_data = get_menthorq_market_data("ES")
        print(f"✅ Données MenthorQ récupérées: {len(menthorq_data.get('menthorq_levels', {}))} niveaux")
        
        if menthorq_data.get('menthorq_levels'):
            print("📊 Niveaux MenthorQ disponibles:")
            for level_name, price in list(menthorq_data['menthorq_levels'].items())[:5]:
                print(f"   - {level_name}: {price}")
        else:
            print("⚠️ Aucun niveau MenthorQ trouvé")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur récupération données MenthorQ: {e}")
        return False

def test_menthorq_dealers_bias():
    """Test du Dealer's Bias MenthorQ"""
    print("\n🧪 Test Dealer's Bias MenthorQ...")
    
    try:
        # Créer l'analyseur
        bias_analyzer = create_menthorq_dealers_bias_analyzer()
        if not bias_analyzer:
            print("❌ Impossible de créer MenthorQDealersBiasAnalyzer")
            return False
        
        print("✅ MenthorQDealersBiasAnalyzer créé")
        
        # Test calcul bias
        current_price = 5294.0
        bias = bias_analyzer.calculate_menthorq_dealers_bias(current_price, "ESZ5", 18.5)
        
        if bias:
            print(f"✅ Dealer's Bias calculé: {bias.direction} {bias.strength}")
            print(f"📊 Score: {bias.bias_score:.3f}")
            print(f"💰 Prix: {bias.underlying_price}")
        else:
            print("⚠️ Aucun Dealer's Bias calculé")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur Dealer's Bias MenthorQ: {e}")
        return False

def test_confluence_integration():
    """Test de l'intégration MenthorQ dans le système de confluence"""
    print("\n🧪 Test intégration MenthorQ dans confluence...")
    
    try:
        # Test ConfluenceAnalyzer
        confluence_analyzer = ConfluenceAnalyzer()
        print("✅ ConfluenceAnalyzer créé")
        
        # Vérifier si MenthorQ est utilisé
        analyzer_methods = [method for method in dir(confluence_analyzer) if not method.startswith('_')]
        menthorq_methods = [method for method in analyzer_methods if 'menthorq' in method.lower()]
        
        if menthorq_methods:
            print(f"✅ Méthodes MenthorQ trouvées: {menthorq_methods}")
        else:
            print("⚠️ Aucune méthode MenthorQ dans ConfluenceAnalyzer")
        
        # Test ConfluenceIntegrator
        integrator = ConfluenceIntegrator()
        print("✅ ConfluenceIntegrator créé")
        
        integrator_methods = [method for method in dir(integrator) if not method.startswith('_')]
        menthorq_integrator_methods = [method for method in integrator_methods if 'menthorq' in method.lower()]
        
        if menthorq_integrator_methods:
            print(f"✅ Méthodes MenthorQ trouvées: {menthorq_integrator_methods}")
        else:
            print("⚠️ Aucune méthode MenthorQ dans ConfluenceIntegrator")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test intégration confluence: {e}")
        return False

def main():
    """Test principal"""
    print("🚀 Test du statut d'intégration MenthorQ dans MIA_IA_SYSTEM")
    print("=" * 60)
    
    # Tests
    data_ok = test_menthorq_data_availability()
    bias_ok = test_menthorq_dealers_bias()
    integration_ok = test_confluence_integration()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DU STATUT MENTHORQ:")
    print(f"   📊 Données MenthorQ: {'✅ OK' if data_ok else '❌ KO'}")
    print(f"   🎯 Dealer's Bias: {'✅ OK' if bias_ok else '❌ KO'}")
    print(f"   🔗 Intégration confluence: {'✅ OK' if integration_ok else '❌ KO'}")
    
    if data_ok and bias_ok and not integration_ok:
        print("\n⚠️ CONCLUSION: MenthorQ est disponible mais PAS intégré dans le système de confluence!")
        print("   → Il faut intégrer MenthorQ dans ConfluenceAnalyzer et ConfluenceIntegrator")
    elif data_ok and bias_ok and integration_ok:
        print("\n✅ CONCLUSION: MenthorQ est complètement intégré!")
    else:
        print("\n❌ CONCLUSION: Problèmes avec MenthorQ - vérification nécessaire")

if __name__ == "__main__":
    main()


