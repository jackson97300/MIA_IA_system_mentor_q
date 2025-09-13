#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST COMPREHENSIF MENTHORQ FIRST METHOD
======================================

Test complet de la méthode MenthorQ First avec une batterie de données
de test couvrant tous les scénarios possibles.
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any

# Ajout du chemin du projet
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from test_data.menthorq_first_test_data import (
    MenthorQFirstTestData, TestData, TestScenario,
    get_test_data_by_scenario, get_test_data_by_expected_signal
)

def test_menthorq_first_comprehensive():
    """Test complet de la méthode MenthorQ First"""
    
    print("🎯 TEST COMPREHENSIF MENTHORQ FIRST METHOD")
    print("=" * 70)
    
    # === INITIALISATION ===
    try:
        from core.menthorq_first_method import MenthorQFirstMethod
        method = MenthorQFirstMethod()
        print("✅ Méthode MenthorQ First initialisée")
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        return False
    
    # === BATTERIE DE DONNÉES ===
    generator = MenthorQFirstTestData()
    all_scenarios = generator.get_all_test_scenarios()
    
    print(f"📊 Nombre de scénarios de test: {len(all_scenarios)}")
    print()
    
    # === RÉSULTATS ===
    results = {
        'total_tests': len(all_scenarios),
        'passed_tests': 0,
        'failed_tests': 0,
        'signal_accuracy': 0,
        'confidence_accuracy': 0,
        'scenario_results': []
    }
    
    # === EXÉCUTION DES TESTS ===
    for i, test_data in enumerate(all_scenarios, 1):
        print(f"🔍 TEST {i:2d}/{len(all_scenarios)}: {test_data.scenario.value.upper()}")
        print(f"   Description: {test_data.description}")
        print(f"   Signal attendu: {test_data.expected_signal}")
        print(f"   Confiance attendue: {test_data.expected_confidence:.2f}")
        
        try:
            # Exécution du test
            start_time = time.time()
            result = method.analyze_menthorq_first_opportunity(
                test_data.es_data, 
                test_data.nq_data
            )
            test_time = (time.time() - start_time) * 1000
            
            # Analyse des résultats
            actual_signal = result.signal_type
            actual_confidence = result.confidence
            
            # Vérification du signal
            signal_correct = actual_signal == test_data.expected_signal
            
            # Vérification de la confiance (tolérance de ±0.1)
            confidence_tolerance = 0.1
            confidence_correct = abs(actual_confidence - test_data.expected_confidence) <= confidence_tolerance
            
            # Score global
            test_passed = signal_correct and confidence_correct
            
            if test_passed:
                results['passed_tests'] += 1
                status = "✅ PASSÉ"
            else:
                results['failed_tests'] += 1
                status = "❌ ÉCHOUÉ"
            
            # Mise à jour des scores
            if signal_correct:
                results['signal_accuracy'] += 1
            if confidence_correct:
                results['confidence_accuracy'] += 1
            
            # Stockage des résultats
            scenario_result = {
                'scenario': test_data.scenario.value,
                'expected_signal': test_data.expected_signal,
                'actual_signal': actual_signal,
                'expected_confidence': test_data.expected_confidence,
                'actual_confidence': actual_confidence,
                'signal_correct': signal_correct,
                'confidence_correct': confidence_correct,
                'test_passed': test_passed,
                'test_time_ms': test_time,
                'description': test_data.description
            }
            results['scenario_results'].append(scenario_result)
            
            # Affichage des résultats
            print(f"   Signal obtenu: {actual_signal}")
            print(f"   Confiance obtenue: {actual_confidence:.3f}")
            print(f"   Temps: {test_time:.2f} ms")
            print(f"   Résultat: {status}")
            
            if not signal_correct:
                print(f"   ⚠️ Signal incorrect: attendu {test_data.expected_signal}, obtenu {actual_signal}")
            if not confidence_correct:
                print(f"   ⚠️ Confiance incorrecte: attendue {test_data.expected_confidence:.2f}, obtenue {actual_confidence:.3f}")
            
            print()
            
        except Exception as e:
            print(f"   ❌ Erreur lors du test: {e}")
            results['failed_tests'] += 1
            print()
    
    # === RÉSUMÉ FINAL ===
    print("=" * 70)
    print("📋 RÉSUMÉ FINAL")
    print("=" * 70)
    
    total_tests = results['total_tests']
    passed_tests = results['passed_tests']
    failed_tests = results['failed_tests']
    
    print(f"📊 Tests totaux: {total_tests}")
    print(f"✅ Tests passés: {passed_tests}")
    print(f"❌ Tests échoués: {failed_tests}")
    print(f"📈 Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    print(f"🎯 Précision des signaux: {(results['signal_accuracy']/total_tests)*100:.1f}%")
    print(f"📊 Précision de la confiance: {(results['confidence_accuracy']/total_tests)*100:.1f}%")
    print()
    
    # === ANALYSE PAR TYPE DE SIGNAL ===
    print("📊 ANALYSE PAR TYPE DE SIGNAL:")
    signal_types = ['LONG', 'SHORT', 'NO_SIGNAL']
    for signal_type in signal_types:
        scenarios = get_test_data_by_expected_signal(signal_type)
        if scenarios:
            passed_count = sum(1 for r in results['scenario_results'] 
                             if r['expected_signal'] == signal_type and r['test_passed'])
            total_count = len(scenarios)
            accuracy = (passed_count/total_count)*100 if total_count > 0 else 0
            print(f"   {signal_type:10}: {passed_count:2d}/{total_count:2d} ({accuracy:5.1f}%)")
    print()
    
    # === ANALYSE PAR SCÉNARIO ===
    print("📊 ANALYSE PAR SCÉNARIO:")
    for result in results['scenario_results']:
        status = "✅" if result['test_passed'] else "❌"
        print(f"   {status} {result['scenario']:25} | {result['expected_signal']:10} | {result['actual_signal']:10} | {result['actual_confidence']:.3f}")
    print()
    
    # === RECOMMANDATIONS ===
    print("💡 RECOMMANDATIONS:")
    
    if results['passed_tests'] == total_tests:
        print("   🎉 TOUS LES TESTS SONT PASSÉS !")
        print("   ✅ La méthode MenthorQ First est prête pour la production")
    elif results['passed_tests'] >= total_tests * 0.8:
        print("   ✅ La méthode fonctionne bien (≥80% de réussite)")
        print("   🔧 Quelques ajustements mineurs recommandés")
    elif results['passed_tests'] >= total_tests * 0.6:
        print("   ⚠️ La méthode fonctionne partiellement (≥60% de réussite)")
        print("   🔧 Des ajustements significatifs sont nécessaires")
    else:
        print("   ❌ La méthode a des problèmes majeurs (<60% de réussite)")
        print("   🚨 Une refonte est recommandée")
    
    # === EXPORT DES RÉSULTATS ===
    export_results(results)
    
    return results['passed_tests'] >= total_tests * 0.8

def export_results(results: Dict[str, Any]):
    """Exporte les résultats vers un fichier JSON"""
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"test_results/menthorq_first_test_results_{timestamp}.json"
        
        # Créer le dossier si nécessaire
        os.makedirs("test_results", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Résultats exportés vers: {filename}")
        
    except Exception as e:
        print(f"⚠️ Erreur export des résultats: {e}")

def test_specific_scenarios():
    """Test de scénarios spécifiques"""
    
    print("\n🎯 TEST DE SCÉNARIOS SPÉCIFIQUES")
    print("=" * 50)
    
    # Test du scénario bullish breakout
    try:
        test_data = get_test_data_by_scenario(TestScenario.BULLISH_BREAKOUT)
        print(f"📊 Test du scénario: {test_data.scenario.value}")
        print(f"   Description: {test_data.description}")
        print(f"   Signal attendu: {test_data.expected_signal}")
        print(f"   Confiance attendue: {test_data.expected_confidence:.2f}")
        
        from core.menthorq_first_method import MenthorQFirstMethod
        method = MenthorQFirstMethod()
        
        result = method.analyze_menthorq_first_opportunity(
            test_data.es_data, 
            test_data.nq_data
        )
        
        print(f"   Signal obtenu: {result.signal_type}")
        print(f"   Confiance obtenue: {result.confidence:.3f}")
        print(f"   Score MenthorQ: {result.menthorq_score:.3f}")
        print(f"   Score Orderflow: {result.orderflow_score:.3f}")
        print(f"   Score Structure: {result.structure_score:.3f}")
        print(f"   Score Final: {result.final_score:.3f}")
        
        if result.audit_data:
            print(f"   Audit Data: {len(result.audit_data)} éléments")
        
        print()
        
    except Exception as e:
        print(f"❌ Erreur test scénario spécifique: {e}")

def main():
    """Fonction principale"""
    
    print("🚀 LANCEMENT DU TEST COMPREHENSIF MENTHORQ FIRST")
    print("=" * 70)
    
    # Test principal
    success = test_menthorq_first_comprehensive()
    
    # Test de scénarios spécifiques
    test_specific_scenarios()
    
    print("=" * 70)
    if success:
        print("🎉 TEST COMPREHENSIF TERMINÉ AVEC SUCCÈS !")
    else:
        print("⚠️ TEST COMPREHENSIF TERMINÉ AVEC DES PROBLÈMES")
    print("=" * 70)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
