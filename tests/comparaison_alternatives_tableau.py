#!/usr/bin/env python3
"""
COMPARAISON ALTERNATIVES - TABLEAU SIMPLE
Tableau clair et lisible des alternatives à IBKR/DXFeed/IQFeed
"""

import json
from datetime import datetime

def generer_tableau_comparaison():
    """Générer un tableau de comparaison simple"""
    
    # Données des fournisseurs
    fournisseurs = [
        {
            "nom": "DXFeed",
            "prix": "2000$/mois",
            "options_chains": "✅ Complètes",
            "greeks": "✅ Oui",
            "gamma_exposure": "✅ Oui",
            "level2": "✅ 20 niveaux",
            "orderflow": "✅ Complet",
            "latence": "<10ms",
            "api": "✅ REST + WebSocket",
            "couverture_bot": "96%",
            "note": "Premium, très cher"
        },
        {
            "nom": "IQFeed",
            "prix": "150$/mois",
            "options_chains": "✅ Partielles",
            "greeks": "✅ Oui",
            "gamma_exposure": "❌ Limité",
            "level2": "⚠️ 10 niveaux",
            "orderflow": "⚠️ Partiel",
            "latence": "50ms",
            "api": "✅ WebSocket",
            "couverture_bot": "88%",
            "note": "Bon rapport Q/P"
        },
        {
            "nom": "Polygon.io",
            "prix": "199$/mois",
            "options_chains": "✅ Complètes",
            "greeks": "✅ Oui",
            "gamma_exposure": "❌ Non",
            "level2": "⚠️ Limité",
            "orderflow": "❌ Non",
            "latence": "100ms",
            "api": "✅ REST + WebSocket",
            "couverture_bot": "60%",
            "note": "Développeur-friendly"
        },
        {
            "nom": "MarketData.app",
            "prix": "99$/mois",
            "options_chains": "✅ Oui",
            "greeks": "✅ Oui",
            "gamma_exposure": "❌ Non",
            "level2": "❌ Non",
            "orderflow": "❌ Non",
            "latence": "N/A",
            "api": "✅ REST",
            "couverture_bot": "45%",
            "note": "Simple d'usage"
        },
        {
            "nom": "Theta Data",
            "prix": "Contact",
            "options_chains": "✅ Oui",
            "greeks": "✅ 2nd ordre",
            "gamma_exposure": "❌ Non",
            "level2": "❌ Non",
            "orderflow": "❌ Non",
            "latence": "N/A",
            "api": "✅ REST",
            "couverture_bot": "50%",
            "note": "Greeks avancés"
        },
        {
            "nom": "Intrinio",
            "prix": "1250$/mois",
            "options_chains": "✅ Complètes",
            "greeks": "✅ Oui",
            "gamma_exposure": "❌ Non",
            "level2": "❌ Non",
            "orderflow": "❌ Non",
            "latence": "N/A",
            "api": "✅ REST + WebSocket",
            "couverture_bot": "70%",
            "note": "Très cher"
        },
        {
            "nom": "Databento",
            "prix": "299$/mois",
            "options_chains": "✅ Oui",
            "greeks": "❌ Non",
            "gamma_exposure": "❌ Non",
            "level2": "❌ Non",
            "orderflow": "❌ Non",
            "latence": "N/A",
            "api": "✅ REST",
            "couverture_bot": "40%",
            "note": "Données brutes"
        },
        {
            "nom": "QuoteMedia",
            "prix": "99$/mois",
            "options_chains": "✅ Oui",
            "greeks": "✅ Oui",
            "gamma_exposure": "❌ Non",
            "level2": "❌ Non",
            "orderflow": "❌ Non",
            "latence": "N/A",
            "api": "✅ REST",
            "couverture_bot": "55%",
            "note": "Bon compromis"
        },
        {
            "nom": "IEX Cloud",
            "prix": "299$/mois",
            "options_chains": "⚠️ Limitée",
            "greeks": "❌ Non",
            "gamma_exposure": "❌ Non",
            "level2": "⚠️ Limité",
            "orderflow": "❌ Non",
            "latence": "50ms",
            "api": "✅ REST",
            "couverture_bot": "50%",
            "note": "API moderne"
        },
        {
            "nom": "Alpaca Markets",
            "prix": "99$/mois",
            "options_chains": "❌ Non",
            "greeks": "❌ Non",
            "gamma_exposure": "❌ Non",
            "level2": "⚠️ Limité",
            "orderflow": "❌ Non",
            "latence": "100ms",
            "api": "✅ REST",
            "couverture_bot": "30%",
            "note": "Trading intégré"
        }
    ]
    
    # Générer tableau
    print("📊 COMPARAISON ALTERNATIVES MARKET DATA")
    print("=" * 120)
    print()
    
    # En-tête
    print(f"{'Fournisseur':<15} {'Prix':<12} {'Options':<8} {'Greeks':<8} {'Gamma':<8} {'Level2':<8} {'Orderflow':<10} {'Latence':<8} {'API':<8} {'Couverture':<10} {'Note'}")
    print("-" * 120)
    
    # Lignes de données
    for f in fournisseurs:
        print(f"{f['nom']:<15} {f['prix']:<12} {f['options_chains']:<8} {f['greeks']:<8} {f['gamma_exposure']:<8} {f['level2']:<8} {f['orderflow']:<10} {f['latence']:<8} {f['api']:<8} {f['couverture_bot']:<10} {f['note']}")
    
    print()
    print("LÉGENDE:")
    print("✅ = Oui/Complet  ⚠️ = Partiel/Limité  ❌ = Non/Non disponible")
    print()
    
    # Recommandations par budget
    print("💡 RECOMMANDATIONS PAR BUDGET")
    print("-" * 50)
    
    print("💰 Budget < 100$/mois:")
    print("   • QuoteMedia (99$/mois) - Bon compromis options + Greeks")
    print("   • Alpaca Markets (99$/mois) - Trading intégré, données limitées")
    print()
    
    print("💰 Budget 100-200$/mois:")
    print("   • IQFeed (150$/mois) - Meilleur rapport qualité/prix")
    print("   • MarketData.app (99$/mois) - Simple, options + Greeks")
    print()
    
    print("💰 Budget 200-500$/mois:")
    print("   • Polygon.io (199$/mois) - Développeur-friendly, options complètes")
    print("   • IEX Cloud (299$/mois) - API moderne, données étendues")
    print("   • Databento (299$/mois) - Données brutes, calculs manuels")
    print()
    
    print("💰 Budget > 500$/mois:")
    print("   • DXFeed (2000$/mois) - Premium, toutes les fonctionnalités")
    print("   • Intrinio (1250$/mois) - Options complètes, très cher")
    print()
    
    # Analyse pour MIA_IA_SYSTEM
    print("🤖 ANALYSE POUR MIA_IA_SYSTEM")
    print("-" * 50)
    
    print("Besoins critiques du bot:")
    print("• Options chains complètes (SPX)")
    print("• Gamma exposure")
    print("• Level 2 data")
    print("• Orderflow/Cumulative delta")
    print("• Latence < 50ms")
    print()
    
    print("✅ RECOMMANDATION FINALE:")
    print("1. IQFeed (150$/mois) + Workarounds")
    print("   • Couverture: 88% des besoins")
    print("   • Économies: 1850$/mois vs DXFeed")
    print("   • Gaps compensables par développement")
    print()
    print("2. Polygon.io (199$/mois) + Workarounds")
    print("   • Couverture: 60% des besoins")
    print("   • Économies: 1801$/mois vs DXFeed")
    print("   • API excellente pour développement")
    print()
    print("3. Stratégie hybride")
    print("   • IQFeed (150$) + Polygon.io (199$) = 349$/mois")
    print("   • Couverture étendue, redondance")
    print("   • Économies: 1651$/mois vs DXFeed")
    
    # Sauvegarder données
    report = {
        "timestamp": datetime.now().isoformat(),
        "fournisseurs": fournisseurs,
        "recommandations": {
            "budget_faible": ["QuoteMedia", "Alpaca Markets"],
            "budget_moyen": ["IQFeed", "MarketData.app"],
            "budget_eleve": ["Polygon.io", "IEX Cloud", "Databento"],
            "budget_premium": ["DXFeed", "Intrinio"]
        }
    }
    
    with open("comparaison_alternatives_tableau.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Données sauvegardées: comparaison_alternatives_tableau.json")

if __name__ == "__main__":
    generer_tableau_comparaison()

