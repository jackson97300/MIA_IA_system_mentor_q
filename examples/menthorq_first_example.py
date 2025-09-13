#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXEMPLE D'UTILISATION MENTHORQ FIRST METHOD
==========================================

Exemple pratique d'utilisation de la méthode MenthorQ First
pour tester et valider le fonctionnement.
"""

import sys
import os
import json
import time
from pathlib import Path

# Ajout du chemin du projet
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.menthorq_first_method import MenthorQFirstMethod, MenthorQFirstResult
from core.logger import get_logger

logger = get_logger(__name__)

def create_sample_es_data():
    """Crée des données ES d'exemple pour le test"""
    return {
        'basedata': {
            'close': 4500.0,
            'volume': 1000
        },
        'quote': {
            'bid': 4499.75,
            'ask': 4500.25,
            'mid': 4500.0
        },
        'trade': {
            'price': 4500.0,
            'size': 10
        },
        'vwap': {
            'value': 4499.5,
            'deviation': 0.5
        },
        'volume_profile': {
            'vah': 4501.0,
            'val': 4498.0,
            'vpoc': 4499.5
        },
        'vix': {
            'value': 18.5
        },
        'nbcv': {
            'value': 150.0,
            'trend': 'bullish'
        },
        'cumulative_delta': {
            'value': 200.0,
            'trend': 'bullish'
        },
        'depth': {
            'bid_levels': [
                {'price': 4499.75, 'size': 100},
                {'price': 4499.50, 'size': 150},
                {'price': 4499.25, 'size': 200}
            ],
            'ask_levels': [
                {'price': 4500.25, 'size': 120},
                {'price': 4500.50, 'size': 180},
                {'price': 4500.75, 'size': 160}
            ]
        }
    }

def create_sample_nq_data():
    """Crée des données NQ d'exemple pour le test"""
    return {
        'basedata': {
            'close': 15000.0,
            'volume': 800
        },
        'quote': {
            'bid': 14999.5,
            'ask': 15000.5,
            'mid': 15000.0
        },
        'trade': {
            'price': 15000.0,
            'size': 5
        }
    }

def test_menthorq_first_method():
    """Test de la méthode MenthorQ First"""
    
    print("🚀 TEST MENTHORQ FIRST METHOD")
    print("=" * 50)
    
    # === INITIALISATION ===
    try:
        method = MenthorQFirstMethod()
        print("✅ Méthode MenthorQ First initialisée")
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        return
    
    # === DONNÉES D'EXEMPLE ===
    es_data = create_sample_es_data()
    nq_data = create_sample_nq_data()
    
    print(f"📊 Données ES: {es_data['basedata']['close']}")
    print(f"📊 Données NQ: {nq_data['basedata']['close']}")
    print(f"📊 VIX: {es_data['vix']['value']}")
    
    # === ANALYSE ===
    try:
        print("\n🔍 ANALYSE MENTHORQ FIRST...")
        start_time = time.time()
        
        result = method.analyze_menthorq_first_opportunity(es_data, nq_data)
        
        analysis_time = (time.time() - start_time) * 1000
        print(f"⏱️ Temps d'analyse: {analysis_time:.2f} ms")
        
        # === RÉSULTATS ===
        print(f"\n📈 RÉSULTATS:")
        print(f"   Signal: {result.signal_type}")
        print(f"   Confidence: {result.confidence:.3f}")
        print(f"   Score MenthorQ: {result.menthorq_score:.3f}")
        print(f"   Score Orderflow: {result.orderflow_score:.3f}")
        print(f"   Score Structure: {result.structure_score:.3f}")
        print(f"   Score Final: {result.final_score:.3f}")
        
        # === E/U/L ===
        if result.eul_levels:
            print(f"\n💰 E/U/L LEVELS:")
            for key, value in result.eul_levels.items():
                print(f"   {key}: {value}")
        
        # === AUDIT DATA ===
        if result.audit_data:
            print(f"\n🔍 AUDIT DATA:")
            for key, value in result.audit_data.items():
                if key != 'error':
                    print(f"   {key}: {value}")
        
        # === STATISTIQUES ===
        stats = method.get_stats()
        print(f"\n📊 STATISTIQUES:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # === ÉVALUATION ===
        if result.signal_type != "NO_SIGNAL":
            print(f"\n✅ SIGNAL GÉNÉRÉ: {result.signal_type}")
            print(f"   Confidence: {result.confidence:.3f}")
            if result.confidence >= 0.7:
                print("   🎯 Signal fort (≥ 0.7)")
            elif result.confidence >= 0.5:
                print("   ⚠️ Signal modéré (≥ 0.5)")
            else:
                print("   🔶 Signal faible (< 0.5)")
        else:
            print(f"\n❌ PAS DE SIGNAL")
            print("   Raisons possibles:")
            print("   - Pas de trigger MenthorQ")
            print("   - Gate MIA Bullish échoué")
            print("   - Gate Leadership échoué")
            print("   - Validation Orderflow échouée")
            print("   - Score final insuffisant")
        
    except Exception as e:
        print(f"❌ Erreur analyse: {e}")
        import traceback
        traceback.print_exc()

def test_different_vix_regimes():
    """Test avec différents régimes VIX"""
    
    print("\n🌡️ TEST DIFFÉRENTS RÉGIMES VIX")
    print("=" * 50)
    
    method = MenthorQFirstMethod()
    
    vix_regimes = [
        (12.0, "LOW"),
        (18.5, "MID"),
        (25.0, "HIGH"),
        (40.0, "EXTREME")
    ]
    
    for vix_value, regime in vix_regimes:
        print(f"\n📊 VIX: {vix_value} ({regime})")
        
        # Données avec VIX différent
        es_data = create_sample_es_data()
        es_data['vix']['value'] = vix_value
        
        nq_data = create_sample_nq_data()
        
        try:
            result = method.analyze_menthorq_first_opportunity(es_data, nq_data)
            
            print(f"   Signal: {result.signal_type}")
            print(f"   Score Final: {result.final_score:.3f}")
            
            if result.audit_data.get('vix_multiplier'):
                print(f"   Multiplicateur VIX: {result.audit_data['vix_multiplier']:.3f}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

def main():
    """Fonction principale"""
    
    print("🎯 EXEMPLE MENTHORQ FIRST METHOD")
    print("=" * 60)
    
    # Test principal
    test_menthorq_first_method()
    
    # Test régimes VIX
    test_different_vix_regimes()
    
    print("\n✅ TESTS TERMINÉS")
    print("=" * 60)

if __name__ == "__main__":
    main()
