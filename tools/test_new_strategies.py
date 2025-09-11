#!/usr/bin/env python3
"""
Test des 10 nouvelles stratégies
Simule différents contextes de marché pour valider le fonctionnement des stratégies.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

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


def create_test_context(scenario: str) -> dict:
    """
    Crée un contexte de test selon le scénario.
    
    Args:
        scenario: Type de scénario ("gamma_pin", "opening_drive", "lvn_entry", etc.)
        
    Returns:
        Contexte de trading simulé
    """
    base_ctx = {
        "price": {"last": 4500.0},
        "atr": 8.0,
        "tick_size": 0.25,
        "symbol": "ES",
        "vwap": {
            "vwap": 4500.0,
            "sd1_up": 4508.0,
            "sd1_dn": 4492.0,
            "sd2_up": 4516.0,
            "sd2_dn": 4484.0
        },
        "vva": {
            "vah": 4510.0,
            "val": 4490.0,
            "vpoc": 4500.0,
            "lvn_low": 4495.0,
            "lvn_high": 4505.0
        },
        "menthorq": {
            "nearest_wall": {"type": "CALL", "price": 4510.0, "dist_ticks": 4},
            "gamma_flip": False
        },
        "orderflow": {
            "cvd": 1000,
            "cvd_divergence": False,
            "delta_burst": False,
            "delta_flip": False,
            "stacked_imbalance": {"side": "BUY", "rows": 2},
            "absorption": {"side": "SELL", "at_price": 4500.0},
            "iceberg": {"side": "BUY", "price": 4498.0}
        },
        "quotes": {"speed_up": False},
        "correlation": {"es_nq": 0.8, "leader": "ES"},
        "vix": {"last": 20.0, "rising": False},
        "session": {"label": "POWER", "time_ok": True},
        "basedata": {"last_wick_ticks": 3}
    }
    
    if scenario == "gamma_pin":
        base_ctx["menthorq"]["nearest_wall"] = {"type": "CALL", "price": 4510.0, "dist_ticks": 4}
        base_ctx["orderflow"]["absorption"] = {"side": "SELL", "at_price": 4500.0}
        
    elif scenario == "gamma_flip_breakout":
        base_ctx["menthorq"]["gamma_flip"] = True
        base_ctx["orderflow"]["delta_burst"] = True
        base_ctx["quotes"]["speed_up"] = True
        base_ctx["price"]["last"] = 4508.0  # Au-dessus de VWAP
        
    elif scenario == "liquidity_sweep":
        base_ctx["basedata"]["last_wick_ticks"] = 8
        base_ctx["orderflow"]["delta_flip"] = True
        base_ctx["orderflow"]["absorption"] = {"side": "BUY", "at_price": 4500.0}
        
    elif scenario == "stacked_imbalance":
        base_ctx["orderflow"]["stacked_imbalance"] = {"side": "BUY", "rows": 4}
        base_ctx["price"]["last"] = 4505.0  # Au-dessus de VWAP
        
    elif scenario == "iceberg_follow":
        base_ctx["orderflow"]["iceberg"] = {"side": "SELL", "price": 4502.0}
        
    elif scenario == "cvd_divergence":
        base_ctx["orderflow"]["cvd_divergence"] = True
        base_ctx["orderflow"]["absorption"] = {"side": "BUY", "at_price": 4500.0}
        
    elif scenario == "opening_drive_fail":
        base_ctx["session"]["label"] = "OPEN"
        base_ctx["menthorq"]["nearest_wall"] = {"type": "CALL", "price": 4510.0, "dist_ticks": 2}
        base_ctx["vix"]["rising"] = True
        base_ctx["orderflow"]["delta_burst"] = False  # Stall
        
    elif scenario == "es_nq_decorrelation":
        base_ctx["correlation"]["es_nq"] = 0.3  # Décorrélation
        base_ctx["correlation"]["leader"] = "NQ"
        base_ctx["symbol"] = "NQ"
        base_ctx["orderflow"]["delta_burst"] = True
        base_ctx["price"]["last"] = 4505.0  # Au-dessus de VWAP
        
    elif scenario == "vwap_squeeze":
        base_ctx["vwap"]["sd1_up"] = 4502.0  # Compression
        base_ctx["vwap"]["sd1_dn"] = 4498.0
        base_ctx["orderflow"]["delta_burst"] = True
        base_ctx["quotes"]["speed_up"] = True
        base_ctx["price"]["last"] = 4503.0  # Breakout
        
    elif scenario == "lvn_entry":
        base_ctx["price"]["last"] = 4500.0  # Dans LVN
        base_ctx["orderflow"]["absorption"] = None  # Pas d'absorption
        
    return base_ctx


def test_strategy(strategy, scenario: str) -> dict:
    """
    Teste une stratégie avec un scénario donné.
    
    Args:
        strategy: Instance de la stratégie
        scenario: Nom du scénario
        
    Returns:
        Résultat du test
    """
    ctx = create_test_context(scenario)
    
    try:
        # Test should_run
        can_run = strategy.should_run(ctx)
        
        # Test generate
        signal = strategy.generate(ctx)
        
        return {
            "strategy": strategy.name,
            "scenario": scenario,
            "can_run": can_run,
            "signal": signal,
            "success": True,
            "error": None
        }
        
    except Exception as e:
        return {
            "strategy": strategy.name,
            "scenario": scenario,
            "can_run": False,
            "signal": None,
            "success": False,
            "error": str(e)
        }


def main():
    """Fonction principale de test."""
    print("=== Test des 10 nouvelles stratégies ===\n")
    
    # Instancier toutes les stratégies
    strategies = [
        GammaPinReversion(),
        DealerFlipBreakout(),
        LiquiditySweepReversal(),
        StackedImbalanceContinuation(),
        IcebergTrackerFollow(),
        CvdDivergenceTrap(),
        OpeningDriveFail(),
        EsNqLeadLagMirror(),
        VwapBandSqueezeBreak(),
        ProfileGapFill()
    ]
    
    # Scénarios de test
    scenarios = [
        "gamma_pin",
        "gamma_flip_breakout", 
        "liquidity_sweep",
        "stacked_imbalance",
        "iceberg_follow",
        "cvd_divergence",
        "opening_drive_fail",
        "es_nq_decorrelation",
        "vwap_squeeze",
        "lvn_entry"
    ]
    
    results = []
    
    # Tester chaque stratégie avec chaque scénario
    for strategy in strategies:
        print(f"Testing {strategy.name}...")
        
        for scenario in scenarios:
            result = test_strategy(strategy, scenario)
            results.append(result)
            
            if result["success"]:
                status = "✓" if result["signal"] else "○"
                print(f"  {status} {scenario}: {'Signal généré' if result['signal'] else 'Pas de signal'}")
            else:
                print(f"  ✗ {scenario}: ERREUR - {result['error']}")
    
    # Résumé
    print(f"\n=== RÉSUMÉ ===")
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r["success"])
    signals_generated = sum(1 for r in results if r["signal"])
    
    print(f"Tests réussis: {successful_tests}/{total_tests}")
    print(f"Signaux générés: {signals_generated}/{total_tests}")
    
    # Détail des signaux générés
    print(f"\n=== SIGNAUX GÉNÉRÉS ===")
    for result in results:
        if result["signal"]:
            signal = result["signal"]
            print(f"{result['strategy']} ({result['scenario']}): {signal['side']} @ {signal['entry']} "
                  f"SL:{signal['stop']} TP:{signal['targets']} Conf:{signal['confidence']}")
    
    # Erreurs
    errors = [r for r in results if not r["success"]]
    if errors:
        print(f"\n=== ERREURS ===")
        for error in errors:
            print(f"{error['strategy']} ({error['scenario']}): {error['error']}")


if __name__ == "__main__":
    main()

