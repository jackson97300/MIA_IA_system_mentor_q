#!/usr/bin/env python3
"""
Test de l'intégration complète du pipeline de trading
"""

import sys
from pathlib import Path
import time
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).parent))

from core.pipeline_integrator import (
    PipelineIntegrator, 
    IntegrationStatus,
    create_pipeline_integrator
)

def test_pipeline_integration():
    """Test de l'intégration complète du pipeline"""
    print("🚀 === TEST INTÉGRATION PIPELINE COMPLET ===\n")
    
    # Test 1: Création de l'intégrateur
    print("🎯 Test 1: Création de l'intégrateur de pipeline")
    integrator = create_pipeline_integrator()
    print(f"✅ Intégrateur créé: {integrator}")
    
    # Test 2: Initialisation des composants
    print("\n🎯 Test 2: Initialisation des composants")
    success = integrator.initialize_components()
    print(f"✅ Composants initialisés: {success}")
    
    if not success:
        print("❌ Impossible de continuer - composants non initialisés")
        return
    
    # Test 3: Démarrage du pipeline
    print("\n🎯 Test 3: Démarrage du pipeline intégré")
    success = integrator.start_pipeline()
    print(f"✅ Pipeline démarré: {success}")
    
    if not success:
        print("❌ Impossible de continuer - pipeline non démarré")
        return
    
    # Test 4: Simulation de signaux de trading
    print("\n🎯 Test 4: Simulation de signaux de trading")
    
    # Créer des signaux de test avec différents scénarios
    test_signals = [
        {
            'symbol': 'ESZ5',
            'signal_type': 'BULLISH',
            'raw_score': 0.75,
            'leadership_gate': 0.8,
            'leader': 'ES',
            'leader_trend': 0.6,
            'vix_level': 22.5,
            'gamma_levels': {'call_resistance': 4500.0, 'put_support': 4480.0},
            'blind_spots': {'bl_1_10': 4490.0},
            'swing_levels': {'sg_1_60': 4485.0},
            'confluence': 0.7,
            'volume_profile': {'vpoc': 4495.0},
            'vwap_position': 0.6,
            'dealers_bias': 0.3
        },
        {
            'symbol': 'NQZ5',
            'signal_type': 'BEARISH',
            'raw_score': 0.45,
            'leadership_gate': 0.3,
            'leader': 'NQ',
            'leader_trend': -0.4,
            'vix_level': 35.2,
            'gamma_levels': {'call_resistance': 15500.0, 'put_support': 15480.0},
            'blind_spots': {'bl_1_10': 15490.0},
            'swing_levels': {'sg_1_60': 15485.0},
            'confluence': 0.4,
            'volume_profile': {'vpoc': 15495.0},
            'vwap_position': 0.3,
            'dealers_bias': -0.2
        },
        {
            'symbol': 'ESZ5',
            'signal_type': 'BULLISH',
            'raw_score': 0.85,
            'leadership_gate': 0.9,
            'leader': 'ES',
            'leader_trend': 0.8,
            'vix_level': 18.5,
            'gamma_levels': {'call_resistance': 4510.0, 'put_support': 4490.0},
            'blind_spots': {'bl_1_10': 4500.0},
            'swing_levels': {'sg_1_60': 4495.0},
            'confluence': 0.9,
            'volume_profile': {'vpoc': 4505.0},
            'vwap_position': 0.8,
            'dealers_bias': 0.5
        },
        {
            'symbol': 'ESZ5',
            'signal_type': 'BEARISH',
            'raw_score': 0.25,
            'leadership_gate': 0.2,
            'leader': 'ES',
            'leader_trend': -0.3,
            'vix_level': 55.8,
            'gamma_levels': {'call_resistance': 4520.0, 'put_support': 4500.0},
            'blind_spots': {'bl_1_10': 4510.0},
            'swing_levels': {'sg_1_60': 4505.0},
            'confluence': 0.2,
            'volume_profile': {'vpoc': 4515.0},
            'vwap_position': 0.2,
            'dealers_bias': -0.4
        },
        {
            'symbol': 'NQZ5',
            'signal_type': 'BULLISH',
            'raw_score': 0.65,
            'leadership_gate': 0.6,
            'leader': 'NQ',
            'leader_trend': 0.5,
            'vix_level': 28.1,
            'gamma_levels': {'call_resistance': 15520.0, 'put_support': 15500.0},
            'blind_spots': {'bl_1_10': 15510.0},
            'swing_levels': {'sg_1_60': 15505.0},
            'confluence': 0.6,
            'volume_profile': {'vpoc': 15515.0},
            'vwap_position': 0.5,
            'dealers_bias': 0.2
        }
    ]
    
    # Ajouter les signaux au pipeline
    for i, signal in enumerate(test_signals):
        success = integrator.add_signal(signal)
        print(f"   Signal {i+1} ajouté: {signal['symbol']} ({signal['signal_type']}) - Score: {signal['raw_score']:.2f}")
        time.sleep(0.5)  # Petite pause entre les signaux
    
    print(f"✅ {len(test_signals)} signaux ajoutés au pipeline")
    
    # Test 5: Surveillance du traitement
    print("\n🎯 Test 5: Surveillance du traitement des signaux")
    print("   (Le pipeline va traiter les signaux pendant 15 secondes)")
    
    for i in range(15):  # 15 secondes de surveillance
        time.sleep(1)
        status = integrator.get_pipeline_status()
        print(f"   Seconde {i+1}: {status['total_signals_processed']} signaux traités, {status['queue_size']} en attente")
    
    # Test 6: Statut du pipeline
    print("\n🎯 Test 6: Statut du pipeline")
    status = integrator.get_pipeline_status()
    print(f"✅ Statut du pipeline:")
    print(f"   - Statut: {status['status']}")
    print(f"   - En cours: {status['is_running']}")
    print(f"   - Uptime: {status['uptime_seconds']:.1f}s")
    print(f"   - Signaux traités: {status['total_signals_processed']}")
    print(f"   - Trades réussis: {status['successful_trades']}")
    print(f"   - Trades échoués: {status['failed_trades']}")
    print(f"   - Signaux bloqués: {status['blocked_signals']}")
    print(f"   - Temps moyen: {status['avg_processing_time_ms']:.1f}ms")
    print(f"   - Erreurs: {status['error_count']}")
    print(f"   - Queue: {status['queue_size']}")
    print(f"   - Signaux traités: {status['processed_signals_count']}")
    
    # Test 7: Statut des composants
    print("\n🎯 Test 7: Statut des composants")
    component_status = status['component_status']
    print(f"✅ Statut des composants:")
    for component_name, is_healthy in component_status.items():
        print(f"   - {component_name}: {'✅' if is_healthy else '❌'}")
    
    # Test 8: Métriques des composants
    print("\n🎯 Test 8: Métriques des composants")
    component_metrics = integrator.get_component_metrics()
    print(f"✅ Métriques des composants:")
    
    for component_name, metrics in component_metrics.items():
        print(f"   - {component_name}:")
        if isinstance(metrics, dict):
            for key, value in list(metrics.items())[:3]:  # Afficher les 3 premières métriques
                print(f"     * {key}: {value}")
        else:
            print(f"     * {metrics}")
    
    # Test 9: Signaux récents
    print("\n🎯 Test 9: Signaux récents traités")
    recent_signals = list(integrator.processed_signals)[-5:]  # 5 derniers signaux
    print(f"✅ Signaux récents ({len(recent_signals)}):")
    for i, signal in enumerate(recent_signals):
        print(f"   - Signal {i+1}: {signal.symbol} ({signal.signal_type})")
        print(f"     * Score final: {signal.final_score:.3f}")
        print(f"     * Régime VIX: {signal.vix_regime}")
        print(f"     * Latence: {signal.processing_latency_ms:.1f}ms")
        print(f"     * Raisons: {', '.join(signal.decision_reasons[:2])}")
    
    # Test 10: Export des données
    print("\n🎯 Test 10: Export des données du pipeline")
    try:
        exported_data = integrator.export_pipeline_data('json')
        print(f"✅ Données exportées: {len(exported_data)} caractères")
        print(f"   (Format JSON avec statut, métriques, signaux récents)")
    except Exception as e:
        print(f"❌ Erreur export: {e}")
    
    # Test 11: Arrêt du pipeline
    print("\n🎯 Test 11: Arrêt du pipeline")
    integrator.stop_pipeline()
    time.sleep(2)  # Attendre l'arrêt
    
    final_status = integrator.get_pipeline_status()
    print(f"✅ Pipeline arrêté: {final_status['status'] == 'stopped'}")
    
    # Test 12: Statistiques finales
    print("\n🎯 Test 12: Statistiques finales")
    print(f"✅ Résumé du test d'intégration:")
    print(f"   - Signaux simulés: {len(test_signals)}")
    print(f"   - Signaux traités: {final_status['total_signals_processed']}")
    print(f"   - Trades réussis: {final_status['successful_trades']}")
    print(f"   - Trades échoués: {final_status['failed_trades']}")
    print(f"   - Signaux bloqués: {final_status['blocked_signals']}")
    print(f"   - Temps moyen de traitement: {final_status['avg_processing_time_ms']:.1f}ms")
    print(f"   - Erreurs: {final_status['error_count']}")
    print(f"   - Composants intégrés: {sum(final_status['component_status'].values())}/{len(final_status['component_status'])}")
    print(f"   - Durée du test: {final_status['uptime_seconds']:.1f}s")
    
    print(f"\n🎉 Test d'intégration du pipeline terminé!")
    print(f"🔗 Le pipeline intégré est {'✅ OPÉRATIONNEL' if final_status['total_signals_processed'] > 0 else '❌ NON FONCTIONNEL'}")

if __name__ == "__main__":
    test_pipeline_integration()

