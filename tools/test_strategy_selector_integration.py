#!/usr/bin/env python3
"""
Test d'intégration du Strategy Selector avec les 10 nouvelles stratégies
Valide que l'intégration fonctionne correctement.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
from strategies.strategy_selector import StrategySelector, TradingContext, ExecutionMode
from core.base_types import MarketData


def test_strategy_selector_integration():
    """Test d'intégration du strategy selector avec les patterns."""
    print("=== Test d'intégration Strategy Selector + Patterns ===\n")
    
    # Créer le selector avec configuration
    config = {
        'pattern_fire_cooldown_sec': 30,  # Cooldown court pour test
        'min_pattern_confidence': 0.55,   # Seuil bas pour test
        'min_dist_ticks_wall': 4,         # Seuil bas pour test
    }
    
    selector = StrategySelector(config)
    
    print(f"✅ Strategy Selector initialisé avec {len(selector.pattern_strategies)} pattern strategies")
    
    # Vérifier que toutes les stratégies sont chargées
    expected_strategies = [
        "gamma_pin_reversion", "dealer_flip_breakout", "liquidity_sweep_reversal",
        "stacked_imbalance_continuation", "iceberg_tracker_follow", "cvd_divergence_trap",
        "opening_drive_fail", "es_nq_lead_lag_mirror", "vwap_band_squeeze_break", "profile_gap_fill"
    ]
    
    loaded_strategies = [s.name for s in selector.pattern_strategies]
    print(f"✅ Stratégies chargées: {loaded_strategies}")
    
    for expected in expected_strategies:
        assert expected in loaded_strategies, f"Stratégie {expected} manquante"
    
    print("✅ Toutes les stratégies sont présentes")
    
    # Test avec un contexte de trading simple
    market_data = MarketData(
        timestamp=pd.Timestamp.now(),
        symbol="ES",
        open=4500.0,
        high=4510.0,
        low=4495.0,
        close=4505.0,
        volume=2000
    )
    
    trading_context = TradingContext(
        timestamp=pd.Timestamp.now(),
        market_data=market_data,
        execution_mode=ExecutionMode.PAPER_TRADING
    )
    
    print("✅ Contexte de trading créé")
    
    # Test de l'analyse complète
    try:
        result = selector.analyze_and_select(trading_context)
        print("✅ Analyse complète exécutée avec succès")
        
        # Vérifier les nouveaux champs
        assert hasattr(result, 'patterns_considered'), "Champ patterns_considered manquant"
        assert hasattr(result, 'best_pattern'), "Champ best_pattern manquant"
        assert hasattr(result, 'features_snapshot'), "Champ features_snapshot manquant"
        
        print("✅ Nouveaux champs de tracking présents")
        
        # Afficher les résultats
        print(f"\n📊 Résultats de l'analyse:")
        print(f"   • Stratégie sélectionnée: {result.selected_strategy.value}")
        print(f"   • Régime marché: {result.market_regime.value}")
        print(f"   • Patterns considérés: {len(result.patterns_considered)}")
        print(f"   • Meilleur pattern: {result.best_pattern or 'Aucun'}")
        print(f"   • Décision finale: {result.final_decision.value}")
        print(f"   • Temps de traitement: {result.total_processing_time_ms:.1f}ms")
        
        # Vérifier le status système
        status = selector.get_system_status()
        assert 'pattern_signals' in status, "pattern_signals manquant dans le status"
        assert 'pattern_strategies' in status['components_status'], "pattern_strategies manquant dans components_status"
        
        print("✅ Status système mis à jour avec les patterns")
        
        print(f"\n📈 Status système:")
        print(f"   • Total analyses: {status['total_analyses']}")
        print(f"   • Pattern signals: {status['pattern_signals']}")
        print(f"   • Composants actifs: {len(status['components_status'])}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        raise
    
    # Test de la méthode _create_pattern_context
    try:
        # Simuler un features_result minimal
        class MockFeaturesResult:
            def __init__(self):
                self.confluence_score = 0.7
                self.atr = 2.0
        
        mock_features = MockFeaturesResult()
        pattern_ctx = selector._create_pattern_context(mock_features, trading_context)
        
        # Vérifier que le contexte contient les champs requis
        required_fields = ["price", "atr", "tick_size", "symbol", "vwap", "vva", "menthorq", "orderflow"]
        for field in required_fields:
            assert field in pattern_ctx, f"Champ {field} manquant dans le contexte pattern"
        
        print("✅ Méthode _create_pattern_context fonctionne")
        
    except Exception as e:
        print(f"❌ Erreur dans _create_pattern_context: {e}")
        raise
    
    # Test de la méthode _score_pattern_signal
    try:
        # Simuler un signal pattern
        mock_signal = {
            "strategy": "dealer_flip_breakout",
            "side": "LONG",
            "confidence": 0.7
        }
        
        class MockRegimeData:
            def __init__(self):
                self.regime = type('obj', (object,), {'name': 'STRONG_TREND_BULLISH'})()
        
        mock_regime = MockRegimeData()
        score = selector._score_pattern_signal(mock_signal, mock_regime, mock_features)
        
        assert score is not None, "Score pattern ne devrait pas être None"
        assert 0.0 <= score <= 1.0, f"Score pattern invalide: {score}"
        
        print("✅ Méthode _score_pattern_signal fonctionne")
        
    except Exception as e:
        print(f"❌ Erreur dans _score_pattern_signal: {e}")
        raise
    
    print("\n🎉 Test d'intégration réussi !")
    print("✅ Strategy Selector intégré avec succès aux 10 nouvelles stratégies")
    
    return True


if __name__ == "__main__":
    test_strategy_selector_integration()

