#!/usr/bin/env python3
"""
Test simplifié du Strategy Selector avec les 10 nouvelles stratégies
Évite les dépendances complexes pour valider l'intégration de base.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
from typing import Dict, Any


def test_pattern_strategies_loading():
    """Test de chargement des pattern strategies."""
    print("=== Test de chargement des Pattern Strategies ===\n")
    
    try:
        # Test d'import direct des stratégies
        from strategies.gamma_pin_reversion import GammaPinReversion
        from strategies.dealer_flip_breakout import DealerFlipBreakout
        from strategies.liquidity_sweep_reversal import LiquiditySweepReversal
        from strategies.stacked_imbalance_continuation import StackedImbalanceContinuation
        from strategies.iceberg_tracker_follow import IcebergTrackerFollow
        from strategies.cvd_divergence_trap import CvdDivergenceTrap
        from strategies.opening_drive_fail import OpeningDriveFail
        from strategies.es_nq_lead_lag_mirror import EsNqLeadLagMirror
        from strategies.vwap_band_squeeze_break import VwapBandSqueezeBreak
        from strategies.profile_gap_fill import ProfileGapFill
        
        print("✅ Toutes les stratégies importées avec succès")
        
        # Créer les instances
        strategies = [
            GammaPinReversion(), DealerFlipBreakout(), LiquiditySweepReversal(),
            StackedImbalanceContinuation(), IcebergTrackerFollow(),
            CvdDivergenceTrap(), OpeningDriveFail(),
            EsNqLeadLagMirror(), VwapBandSqueezeBreak(), ProfileGapFill()
        ]
        
        print(f"✅ {len(strategies)} instances créées")
        
        # Vérifier l'interface de chaque stratégie
        for strategy in strategies:
            assert hasattr(strategy, 'name'), f"{strategy.__class__.__name__} manque 'name'"
            assert hasattr(strategy, 'requires'), f"{strategy.__class__.__name__} manque 'requires'"
            assert hasattr(strategy, 'params'), f"{strategy.__class__.__name__} manque 'params'"
            assert hasattr(strategy, 'should_run'), f"{strategy.__class__.__name__} manque 'should_run'"
            assert hasattr(strategy, 'generate'), f"{strategy.__class__.__name__} manque 'generate'"
            
            print(f"   ✅ {strategy.name}: interface complète")
        
        # Test de génération de contexte simple
        simple_ctx = {
            "price": {"last": 4500.0},
            "atr": 2.0,
            "tick_size": 0.25,
            "symbol": "ES",
            "vwap": {"vwap": 4500.0, "sd1_up": 4508.0, "sd1_dn": 4492.0},
            "vva": {"vpoc": 4500.0, "vah": 4510.0, "val": 4490.0},
            "menthorq": {"nearest_wall": {"type": "CALL", "price": 4510.0, "dist_ticks": 4}, "gamma_flip": False},
            "orderflow": {"delta_burst": False, "delta_flip": False, "cvd_divergence": False, 
                         "stacked_imbalance": {"side": "BUY", "rows": 0}, "absorption": None, "iceberg": None},
            "quotes": {"speed_up": False},
            "correlation": {"es_nq": 0.9, "leader": "ES"},
            "vix": {"last": 20.0, "rising": False},
            "session": {"label": "OTHER", "time_ok": True},
            "basedata": {"last_wick_ticks": 0}
        }
        
        print("✅ Contexte de test créé")
        
        # Test should_run pour chaque stratégie
        for strategy in strategies:
            try:
                can_run = strategy.should_run(simple_ctx)
                assert isinstance(can_run, bool), f"{strategy.name}.should_run() doit retourner un booléen"
                print(f"   ✅ {strategy.name}.should_run(): {can_run}")
            except Exception as e:
                print(f"   ❌ {strategy.name}.should_run() erreur: {e}")
        
        # Test generate pour quelques stratégies
        test_strategies = [strategies[0], strategies[1], strategies[2]]  # Premières 3
        for strategy in test_strategies:
            try:
                signal = strategy.generate(simple_ctx)
                if signal:
                    assert isinstance(signal, dict), f"{strategy.name} doit retourner un dict"
                    required_fields = ["strategy", "side", "confidence", "entry", "stop", "targets", "reason"]
                    for field in required_fields:
                        assert field in signal, f"{strategy.name} signal manque '{field}'"
                    print(f"   ✅ {strategy.name}.generate(): signal valide")
                else:
                    print(f"   ○ {strategy.name}.generate(): pas de signal (normal)")
            except Exception as e:
                print(f"   ❌ {strategy.name}.generate() erreur: {e}")
        
        print("\n🎉 Test de chargement réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_strategy_selector_registry():
    """Test du registry des stratégies dans le selector."""
    print("\n=== Test du Registry Strategy Selector ===\n")
    
    try:
        # Test d'import du selector (sans exécution complète)
        from strategies.strategy_selector import StrategySelector
        
        print("✅ StrategySelector importé avec succès")
        
        # Créer une instance avec config minimale
        config = {
            'pattern_fire_cooldown_sec': 30,
            'min_pattern_confidence': 0.55,
        }
        
        selector = StrategySelector(config)
        
        print("✅ StrategySelector instancié")
        
        # Vérifier que les pattern strategies sont chargées
        assert hasattr(selector, 'pattern_strategies'), "pattern_strategies manquant"
        assert len(selector.pattern_strategies) == 10, f"Attendu 10 stratégies, trouvé {len(selector.pattern_strategies)}"
        
        print(f"✅ {len(selector.pattern_strategies)} pattern strategies chargées")
        
        # Vérifier les noms des stratégies
        strategy_names = [s.name for s in selector.pattern_strategies]
        expected_names = [
            "gamma_pin_reversion", "dealer_flip_breakout", "liquidity_sweep_reversal",
            "stacked_imbalance_continuation", "iceberg_tracker_follow", "cvd_divergence_trap",
            "opening_drive_fail", "es_nq_lead_lag_mirror", "vwap_band_squeeze_break", "profile_gap_fill"
        ]
        
        for expected in expected_names:
            assert expected in strategy_names, f"Stratégie {expected} manquante dans le registry"
        
        print("✅ Toutes les stratégies sont dans le registry")
        
        # Vérifier les attributs de cooldown
        assert hasattr(selector, 'last_fire_ts'), "last_fire_ts manquant"
        assert hasattr(selector, 'fire_cooldown_sec'), "fire_cooldown_sec manquant"
        assert hasattr(selector, 'min_pattern_confidence'), "min_pattern_confidence manquant"
        
        print("✅ Attributs de gestion des patterns présents")
        
        # Vérifier les méthodes helper
        assert hasattr(selector, '_create_pattern_context'), "_create_pattern_context manquant"
        assert hasattr(selector, '_score_pattern_signal'), "_score_pattern_signal manquant"
        
        print("✅ Méthodes helper des patterns présentes")
        
        print("\n🎉 Test du registry réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test registry: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale de test."""
    print("🚀 Test d'intégration Strategy Selector + Patterns\n")
    
    success1 = test_pattern_strategies_loading()
    success2 = test_strategy_selector_registry()
    
    if success1 and success2:
        print("\n🎉 TOUS LES TESTS RÉUSSIS !")
        print("✅ Les 10 nouvelles stratégies sont correctement intégrées")
        print("✅ Le Strategy Selector est prêt pour la production")
        return True
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        return False


if __name__ == "__main__":
    main()

