"""
Test de la synchronisation ES/NQ dans confluence_integrator.py
============================================================

Script de validation de la synchronisation des données ES/NQ.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from features.confluence_integrator import ConfluenceIntegrator

def create_test_data():
    """Crée des données de test ES/NQ avec timestamps"""
    base_time = datetime.now(timezone.utc)
    
    # Données ES
    es_data = pd.DataFrame({
        'timestamp': [
            base_time - timedelta(seconds=10),
            base_time - timedelta(seconds=5),
            base_time - timedelta(seconds=2),
            base_time
        ],
        'close': [4500.0, 4501.0, 4502.0, 4503.0],
        'volume': [1000, 1100, 1200, 1300],
        'high': [4501.0, 4502.0, 4503.0, 4504.0],
        'low': [4499.0, 4500.0, 4501.0, 4502.0]
    })
    
    # Données NQ (avec décalage temporel)
    nq_data = pd.DataFrame({
        'timestamp': [
            base_time - timedelta(seconds=9),  # 1 seconde de décalage
            base_time - timedelta(seconds=4),  # 1 seconde de décalage
            base_time - timedelta(seconds=1),  # 1 seconde de décalage
            base_time + timedelta(seconds=1)   # 1 seconde en avance
        ],
        'close': [15000.0, 15010.0, 15020.0, 15030.0],
        'volume': [800, 900, 1000, 1100],
        'high': [15001.0, 15011.0, 15021.0, 15031.0],
        'low': [14999.0, 15009.0, 15019.0, 15029.0]
    })
    
    return es_data, nq_data

def test_es_nq_synchronization():
    """Test de la synchronisation ES/NQ"""
    print("🔄 TEST SYNCHRONISATION ES/NQ")
    print("=" * 50)
    
    # Créer l'intégrateur avec configuration
    config = {
        'sync_tolerance_seconds': 3.0,
        'max_sync_buffer_size': 50
    }
    integrator = ConfluenceIntegrator(config)
    
    # Créer les données de test
    es_data, nq_data = create_test_data()
    
    print(f"📊 Données ES: {len(es_data)} points")
    print(f"📊 Données NQ: {len(nq_data)} points")
    
    # Test 1: Synchronisation progressive
    print("\n1. Test synchronisation progressive...")
    
    for i in range(len(es_data)):
        # Simuler l'arrivée des données une par une
        market_data = {
            'ES': es_data.iloc[:i+1],
            'NQ': nq_data.iloc[:i+1] if i < len(nq_data) else nq_data
        }
        
        # Calculer la confluence (qui déclenche la synchronisation)
        result = integrator.calculate_confluence_with_leadership(market_data)
        
        # Obtenir les stats de synchronisation
        sync_stats = integrator.get_es_nq_sync_stats()
        
        print(f"   Étape {i+1}: {sync_stats['synchronized_pairs']} paires synchronisées")
        print(f"   Qualité moyenne: {sync_stats['average_sync_quality']:.3f}")
        print(f"   Taux de sync: {sync_stats['sync_rate']:.3f}")
    
    # Test 2: Test avec données asynchrones
    print("\n2. Test avec données asynchrones...")
    
    # Créer des données avec des timestamps très éloignés
    async_es_data = pd.DataFrame({
        'timestamp': [datetime.now(timezone.utc) - timedelta(seconds=30)],
        'close': [4500.0],
        'volume': [1000],
        'high': [4501.0],
        'low': [4499.0]
    })
    
    async_nq_data = pd.DataFrame({
        'timestamp': [datetime.now(timezone.utc) - timedelta(seconds=5)],
        'close': [15000.0],
        'volume': [800],
        'high': [15001.0],
        'low': [14999.0]
    })
    
    market_data = {
        'ES': async_es_data,
        'NQ': async_nq_data
    }
    
    result = integrator.calculate_confluence_with_leadership(market_data)
    sync_stats = integrator.get_es_nq_sync_stats()
    
    print(f"   Données asynchrones: {sync_stats['synchronized_pairs']} paires synchronisées")
    print(f"   Qualité: {sync_stats['average_sync_quality']:.3f}")
    
    # Test 3: Test de corrélation avec données synchronisées
    print("\n3. Test de corrélation avec données synchronisées...")
    
    # Créer des données parfaitement synchronisées
    sync_time = datetime.now(timezone.utc)
    sync_es_data = pd.DataFrame({
        'timestamp': [sync_time, sync_time + timedelta(seconds=1)],
        'close': [4500.0, 4505.0],
        'volume': [1000, 1100],
        'high': [4501.0, 4506.0],
        'low': [4499.0, 4504.0]
    })
    
    sync_nq_data = pd.DataFrame({
        'timestamp': [sync_time, sync_time + timedelta(seconds=1)],
        'close': [15000.0, 15050.0],
        'volume': [800, 900],
        'high': [15001.0, 15051.0],
        'low': [14999.0, 15049.0]
    })
    
    market_data = {
        'ES': sync_es_data,
        'NQ': sync_nq_data
    }
    
    result = integrator.calculate_confluence_with_leadership(market_data)
    sync_stats = integrator.get_es_nq_sync_stats()
    
    print(f"   Données synchronisées: {sync_stats['synchronized_pairs']} paires")
    print(f"   Qualité: {sync_stats['average_sync_quality']:.3f}")
    print(f"   Score de confluence: {result.final_score:.3f}")
    print(f"   Leader: {result.leader}")
    
    # Test 4: Test des statistiques de confluence
    print("\n4. Test des statistiques de confluence...")
    
    confluence_stats = integrator.get_confluence_stats()
    print(f"   Total signaux: {confluence_stats['total_signals']}")
    print(f"   Signaux valides: {confluence_stats['valid_signals']}")
    print(f"   Score moyen: {confluence_stats['avg_score']:.3f}")
    print(f"   Taux de validation: {confluence_stats['validation_rate']:.3f}")
    
    print("\n✅ Test synchronisation ES/NQ terminé avec succès!")
    return True

if __name__ == "__main__":
    test_es_nq_synchronization()


