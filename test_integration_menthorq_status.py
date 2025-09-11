#!/usr/bin/env python3
"""
Test du statut d'intégration MenthorQ dans le système MIA_IA
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

def test_menthorq_modules_availability():
    """Test de la disponibilité des modules MenthorQ"""
    print("🧪 Test de disponibilité des modules MenthorQ...")
    
    try:
        # Test import MenthorQ modules
        from features.menthorq_dealers_bias import create_menthorq_dealers_bias_analyzer
        from features.menthorq_processor import MenthorQProcessor
        from features.menthorq_integration import create_menthorq_integration
        print("✅ Modules MenthorQ importés avec succès")
        
        # Test création des analyseurs
        bias_analyzer = create_menthorq_dealers_bias_analyzer()
        if bias_analyzer:
            print("✅ MenthorQDealersBiasAnalyzer créé")
        else:
            print("❌ Échec création MenthorQDealersBiasAnalyzer")
            
        processor = MenthorQProcessor()
        print("✅ MenthorQProcessor créé")
        
        integration = create_menthorq_integration()
        if integration:
            print("✅ MenthorQIntegration créé")
        else:
            print("❌ Échec création MenthorQIntegration")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur import modules MenthorQ: {e}")
        return False

def test_confluence_integration():
    """Test de l'intégration dans les modules de confluence"""
    print("\n🧪 Test intégration dans modules confluence...")
    
    try:
        # Test ConfluenceAnalyzer
        from features.confluence_analyzer import ConfluenceAnalyzer
        analyzer = ConfluenceAnalyzer()
        print("✅ ConfluenceAnalyzer créé")
        
        # Vérifier les méthodes disponibles
        methods = [method for method in dir(analyzer) if not method.startswith('_')]
        print(f"📋 Méthodes ConfluenceAnalyzer: {len(methods)}")
        
        # Chercher des méthodes liées à MenthorQ
        menthorq_methods = [m for m in methods if 'menthorq' in m.lower() or 'gamma' in m.lower() or 'dealers' in m.lower()]
        if menthorq_methods:
            print(f"✅ Méthodes MenthorQ trouvées: {menthorq_methods}")
        else:
            print("❌ Aucune méthode MenthorQ dans ConfluenceAnalyzer")
        
        # Test ConfluenceIntegrator
        from features.confluence_integrator import ConfluenceIntegrator
        integrator = ConfluenceIntegrator()
        print("✅ ConfluenceIntegrator créé")
        
        # Vérifier les méthodes disponibles
        integrator_methods = [method for method in dir(integrator) if not method.startswith('_')]
        print(f"📋 Méthodes ConfluenceIntegrator: {len(integrator_methods)}")
        
        # Chercher des méthodes liées à MenthorQ
        menthorq_integrator_methods = [m for m in integrator_methods if 'menthorq' in m.lower() or 'gamma' in m.lower() or 'dealers' in m.lower()]
        if menthorq_integrator_methods:
            print(f"✅ Méthodes MenthorQ trouvées: {menthorq_integrator_methods}")
        else:
            print("❌ Aucune méthode MenthorQ dans ConfluenceIntegrator")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test intégration confluence: {e}")
        return False

def test_data_availability():
    """Test de la disponibilité des données MenthorQ"""
    print("\n🧪 Test disponibilité données MenthorQ...")
    
    try:
        from features.data_reader import get_menthorq_market_data
        
        # Test récupération données
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

def test_dealers_bias_calculation():
    """Test du calcul Dealer's Bias MenthorQ"""
    print("\n🧪 Test calcul Dealer's Bias MenthorQ...")
    
    try:
        from features.menthorq_dealers_bias import create_menthorq_dealers_bias_analyzer
        
        # Créer l'analyseur
        bias_analyzer = create_menthorq_dealers_bias_analyzer()
        if not bias_analyzer:
            print("❌ Impossible de créer MenthorQDealersBiasAnalyzer")
            return False
        
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
        print(f"❌ Erreur calcul Dealer's Bias MenthorQ: {e}")
        return False

def main():
    """Test principal"""
    print("🚀 TEST DU STATUT D'INTÉGRATION MENTHORQ")
    print("=" * 60)
    
    # Tests
    modules_ok = test_menthorq_modules_availability()
    confluence_ok = test_confluence_integration()
    data_ok = test_data_availability()
    bias_ok = test_dealers_bias_calculation()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DU STATUT MENTHORQ:")
    print(f"   📦 Modules MenthorQ: {'✅ OK' if modules_ok else '❌ KO'}")
    print(f"   🔗 Intégration confluence: {'✅ OK' if confluence_ok else '❌ KO'}")
    print(f"   📊 Données MenthorQ: {'✅ OK' if data_ok else '❌ KO'}")
    print(f"   🎯 Dealer's Bias: {'✅ OK' if bias_ok else '❌ KO'}")
    
    if modules_ok and data_ok and bias_ok and not confluence_ok:
        print("\n🚨 CONCLUSION CRITIQUE:")
        print("   • MenthorQ est FONCTIONNEL mais PAS INTÉGRÉ dans le système de confluence!")
        print("   • Vous payez pour MenthorQ mais il n'influence PAS vos trades!")
        print("   • INTÉGRATION URGENTE NÉCESSAIRE!")
    elif modules_ok and data_ok and bias_ok and confluence_ok:
        print("\n✅ CONCLUSION: MenthorQ est complètement intégré!")
    else:
        print("\n❌ CONCLUSION: Problèmes avec MenthorQ - vérification nécessaire")

if __name__ == "__main__":
    main()


