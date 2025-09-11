"""
Test du filtre de leadership dans confluence_integrator.py
========================================================

Script de validation du filtre anti-contre-tendance du leader.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from features.confluence_integrator import ConfluenceIntegrator

def create_test_scenarios():
    """Crée des scénarios de test pour le filtre de leadership"""
    
    # Scénario 1: ES leader fort en hausse, signal short
    es_strong_up = pd.DataFrame({
        'timestamp': [datetime.now(timezone.utc) - timedelta(minutes=i) for i in range(10, 0, -1)],
        'close': [4500 + i * 2 for i in range(10)],  # Tendance haussière forte
        'volume': [1000 + i * 100 for i in range(10)],
        'high': [4501 + i * 2 for i in range(10)],
        'low': [4499 + i * 2 for i in range(10)]
    })
    
    nq_weak_down = pd.DataFrame({
        'timestamp': [datetime.now(timezone.utc) - timedelta(minutes=i) for i in range(10, 0, -1)],
        'close': [15000 - i * 1 for i in range(10)],  # Tendance baissière faible
        'volume': [800 - i * 50 for i in range(10)],
        'high': [15001 - i * 1 for i in range(10)],
        'low': [14999 - i * 1 for i in range(10)]
    })
    
    # Scénario 2: ES leader fort en baisse, signal long
    es_strong_down = pd.DataFrame({
        'timestamp': [datetime.now(timezone.utc) - timedelta(minutes=i) for i in range(10, 0, -1)],
        'close': [4500 - i * 2 for i in range(10)],  # Tendance baissière forte
        'volume': [1000 + i * 100 for i in range(10)],
        'high': [4501 - i * 2 for i in range(10)],
        'low': [4499 - i * 2 for i in range(10)]
    })
    
    nq_weak_up = pd.DataFrame({
        'timestamp': [datetime.now(timezone.utc) - timedelta(minutes=i) for i in range(10, 0, -1)],
        'close': [15000 + i * 1 for i in range(10)],  # Tendance haussière faible
        'volume': [800 + i * 50 for i in range(10)],
        'high': [15001 + i * 1 for i in range(10)],
        'low': [14999 + i * 1 for i in range(10)]
    })
    
    # Scénario 3: Leadership faible, signal accepté
    es_weak = pd.DataFrame({
        'timestamp': [datetime.now(timezone.utc) - timedelta(minutes=i) for i in range(10, 0, -1)],
        'close': [4500 + i * 0.5 for i in range(10)],  # Tendance faible
        'volume': [500 + i * 10 for i in range(10)],
        'high': [4501 + i * 0.5 for i in range(10)],
        'low': [4499 + i * 0.5 for i in range(10)]
    })
    
    nq_weak = pd.DataFrame({
        'timestamp': [datetime.now(timezone.utc) - timedelta(minutes=i) for i in range(10, 0, -1)],
        'close': [15000 + i * 0.3 for i in range(10)],  # Tendance faible
        'volume': [400 + i * 5 for i in range(10)],
        'high': [15001 + i * 0.3 for i in range(10)],
        'low': [14999 + i * 0.3 for i in range(10)]
    })
    
    return {
        'es_strong_up': es_strong_up,
        'nq_weak_down': nq_weak_down,
        'es_strong_down': es_strong_down,
        'nq_weak_up': nq_weak_up,
        'es_weak': es_weak,
        'nq_weak': nq_weak
    }

def test_leadership_filter():
    """Test du filtre de leadership"""
    print("🛡️ TEST FILTRE DE LEADERSHIP")
    print("=" * 50)
    
    # Créer l'intégrateur
    config = {
        'min_confluence_score': 0.3,
        'min_leadership_gate': 0.4,
        'sync_tolerance_seconds': 3.0
    }
    integrator = ConfluenceIntegrator(config)
    
    # Créer les scénarios de test
    scenarios = create_test_scenarios()
    
    # Test 1: ES leader fort en hausse, signal short (devrait être rejeté)
    print("\n1. Test ES leader fort en hausse + signal short...")
    market_data = {
        'ES': scenarios['es_strong_up'],
        'NQ': scenarios['nq_weak_down'],
        'bias': 'bearish',  # Signal short
        'session': 'regular'
    }
    
    result = integrator.calculate_confluence_with_leadership(market_data)
    print(f"   Score final: {result.final_score:.3f}")
    print(f"   Leader: {result.leader}")
    print(f"   Validé: {result.is_valid}")
    print(f"   Décision: {result.decision}")
    
    # Test 2: ES leader fort en baisse, signal long (devrait être rejeté)
    print("\n2. Test ES leader fort en baisse + signal long...")
    market_data = {
        'ES': scenarios['es_strong_down'],
        'NQ': scenarios['nq_weak_up'],
        'bias': 'bullish',  # Signal long
        'session': 'regular'
    }
    
    result = integrator.calculate_confluence_with_leadership(market_data)
    print(f"   Score final: {result.final_score:.3f}")
    print(f"   Leader: {result.leader}")
    print(f"   Validé: {result.is_valid}")
    print(f"   Décision: {result.decision}")
    
    # Test 3: Leadership faible, signal accepté
    print("\n3. Test leadership faible + signal accepté...")
    market_data = {
        'ES': scenarios['es_weak'],
        'NQ': scenarios['nq_weak'],
        'bias': 'bullish',  # Signal long
        'session': 'regular'
    }
    
    result = integrator.calculate_confluence_with_leadership(market_data)
    print(f"   Score final: {result.final_score:.3f}")
    print(f"   Leader: {result.leader}")
    print(f"   Validé: {result.is_valid}")
    print(f"   Décision: {result.decision}")
    
    # Test 4: Statistiques de synchronisation
    print("\n4. Statistiques de synchronisation...")
    sync_stats = integrator.get_es_nq_sync_stats()
    print(f"   Paires synchronisées: {sync_stats['synchronized_pairs']}")
    print(f"   Qualité moyenne: {sync_stats['average_sync_quality']:.3f}")
    print(f"   Taux de sync: {sync_stats['sync_rate']:.3f}")
    
    # Test 5: Statistiques de confluence
    print("\n5. Statistiques de confluence...")
    confluence_stats = integrator.get_confluence_stats()
    print(f"   Total signaux: {confluence_stats['total_signals']}")
    print(f"   Signaux valides: {confluence_stats['valid_signals']}")
    print(f"   Taux de validation: {confluence_stats['validation_rate']:.3f}")
    
    print("\n✅ Test filtre de leadership terminé!")
    return True

if __name__ == "__main__":
    test_leadership_filter()


