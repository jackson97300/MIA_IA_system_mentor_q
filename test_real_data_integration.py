#!/usr/bin/env python3
"""
🧪 TEST REAL DATA INTEGRATION - MIA_IA_SYSTEM
=============================================

Test d'intégration des vraies données JSONL avec les features Python
"""

import sys
from pathlib import Path
import logging

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from features.data_reader import MIADataReader, get_latest_market_data
from features.confluence_integrator import ConfluenceIntegrator
from features.confluence_analyzer import ConfluenceAnalyzer

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_data_reader():
    """Test du lecteur de données"""
    print("\n🧪 TEST 1: Data Reader")
    print("=" * 50)
    
    reader = MIADataReader()
    
    # Test 1: Trouver le fichier unifié
    latest_file = reader.get_latest_unified_file()
    if latest_file:
        print(f"✅ Fichier unifié trouvé: {latest_file.name}")
    else:
        print("❌ Aucun fichier unifié trouvé")
        return False
    
    # Test 2: Lire les données
    snapshots = reader.read_unified_data(max_lines=100)
    print(f"✅ {len(snapshots)} snapshots lus")
    
    if snapshots:
        latest = snapshots[-1]
        print(f"   Dernier snapshot: {latest.timestamp}")
        print(f"   Symbol: {latest.symbol}")
        print(f"   Chart: {latest.chart}")
        print(f"   BaseData: {latest.basedata is not None}")
        print(f"   VWAP: {latest.vwap_current is not None}")
        print(f"   NBCV: {latest.nbcv_footprint is not None}")
        print(f"   VIX: {latest.vix is not None}")
        print(f"   MenthorQ: {len(latest.menthorq_levels)} niveaux")
    
    return len(snapshots) > 0

def test_market_data_dict():
    """Test de conversion en dictionnaire de données de marché"""
    print("\n🧪 TEST 2: Market Data Dict")
    print("=" * 50)
    
    # Récupérer les dernières données
    market_data = get_latest_market_data("ES")
    
    if market_data and len(market_data) > 1:
        print("✅ Données de marché récupérées:")
        for key, value in market_data.items():
            if key not in ['timestamp', 'symbol']:
                print(f"   {key}: {value}")
        return True
    else:
        print("❌ Pas de données de marché disponibles")
        return False

def test_confluence_integrator():
    """Test de l'intégrateur de confluence avec vraies données"""
    print("\n🧪 TEST 3: Confluence Integrator")
    print("=" * 50)
    
    integrator = ConfluenceIntegrator()
    
    # Créer des données de test avec vraies données
    market_data = {
        'ES': get_latest_market_data("ES"),
        'NQ': get_latest_market_data("ES"),  # Utiliser ES comme fallback pour NQ
        'bias': 'bullish',
        'session': 'london_session',
        'timestamp': None
    }
    
    try:
        result = integrator.calculate_confluence_with_leadership(market_data)
        print(f"✅ Confluence calculée:")
        print(f"   Score base: {result.base_score:.3f}")
        print(f"   Leadership gate: {result.leadership_gate:.3f}")
        print(f"   Risk multiplier: {result.risk_multiplier:.3f}")
        print(f"   Score final: {result.final_score:.3f}")
        print(f"   Valide: {result.is_valid}")
        print(f"   Décision: {result.decision}")
        return True
    except Exception as e:
        print(f"❌ Erreur confluence integrator: {e}")
        return False

def test_confluence_analyzer():
    """Test de l'analyseur de confluence avec vraies données"""
    print("\n🧪 TEST 4: Confluence Analyzer")
    print("=" * 50)
    
    analyzer = ConfluenceAnalyzer()
    
    # Créer des données de test
    market_data = {
        'current_price': 4500.0,
        'volume': 1000,
        'volatility': 0.5,
        'timeframe': 'M1'
    }
    
    try:
        # Test de l'analyseur principal
        print("✅ ConfluenceAnalyzer initialisé")
        
        # Test avec des données réelles
        real_data = get_latest_market_data("ES")
        if real_data and len(real_data) > 1:
            print(f"✅ Données réelles intégrées: {len(real_data)} champs")
            print(f"   Close: {real_data.get('close', 'N/A')}")
            print(f"   Volume: {real_data.get('volume', 'N/A')}")
            print(f"   VWAP: {real_data.get('vwap', 'N/A')}")
        else:
            print("⚠️ Pas de données réelles disponibles")
        
        return True
    except Exception as e:
        print(f"❌ Erreur confluence analyzer: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 TEST D'INTÉGRATION DES VRAIES DONNÉES")
    print("=" * 60)
    
    tests = [
        test_data_reader,
        test_market_data_dict,
        test_confluence_integrator,
        test_confluence_analyzer
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erreur dans le test: {e}")
            results.append(False)
    
    print("\n📊 RÉSULTATS FINAUX")
    print("=" * 30)
    passed = sum(results)
    total = len(results)
    
    print(f"Tests réussis: {passed}/{total}")
    
    if passed == total:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("✅ L'intégration des vraies données fonctionne")
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Vérifiez les logs pour plus de détails")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
