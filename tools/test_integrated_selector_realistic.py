#!/usr/bin/env python3
"""
Test réaliste du IntegratedStrategySelector avec des données de marché simulées
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.strategy_selector_integrated import (
    IntegratedStrategySelector, TradingContext, create_integrated_strategy_selector
)

def create_realistic_trading_context(scenario: str = "gamma_pin") -> TradingContext:
    """Crée un contexte de trading réaliste selon le scénario"""
    
    base_time = pd.Timestamp.now()
    base_price = 4500.0
    
    if scenario == "gamma_pin":
        # Scénario Gamma Pin Reversion
        return TradingContext(
            timestamp=base_time,
            symbol="ES",
            price=base_price,
            volume=2500.0,
            tick_size=0.25,
            market_data={
                "vwap": base_price - 2.0,
                "sd1_up": base_price + 2.0,
                "sd1_dn": base_price - 6.0,
                "vah": base_price + 5.0,
                "val": base_price - 5.0,
                "vpoc": base_price - 3.0,
            },
            structure_data={
                "menthorq": {
                    "nearest_wall": {"type": "CALL", "price": base_price + 4.0, "dist_ticks": 16},
                    "gamma_flip": False
                },
                "orderflow": {
                    "delta_burst": False,
                    "delta_flip": False,
                    "cvd_divergence": False,
                    "stacked_imbalance": {"side": "BUY", "rows": 0},
                    "absorption": {"side": "SELL", "at_price": base_price + 0.5},
                    "iceberg": None,
                }
            }
        )
    
    elif scenario == "dealer_flip_breakout":
        # Scénario Dealer Flip Breakout
        return TradingContext(
            timestamp=base_time,
            symbol="ES", 
            price=base_price + 8.0,  # Au-dessus de VWAP
            volume=3500.0,
            tick_size=0.25,
            market_data={
                "vwap": base_price,
                "sd1_up": base_price + 4.0,
                "sd1_dn": base_price - 4.0,
                "vah": base_price + 8.0,
                "val": base_price - 8.0,
                "vpoc": base_price,
            },
            structure_data={
                "menthorq": {
                    "nearest_wall": {"type": "CALL", "price": base_price + 12.0, "dist_ticks": 16},
                    "gamma_flip": True  # FLIP ACTIVÉ
                },
                "orderflow": {
                    "delta_burst": True,  # BURST ACTIVÉ
                    "delta_flip": True,
                    "cvd_divergence": False,
                    "stacked_imbalance": {"side": "BUY", "rows": 2},
                    "absorption": None,
                    "iceberg": None,
                }
            }
        )
    
    elif scenario == "liquidity_sweep":
        # Scénario Liquidity Sweep Reversal
        return TradingContext(
            timestamp=base_time,
            symbol="ES",
            price=base_price,
            volume=1800.0,
            tick_size=0.25,
            market_data={
                "vwap": base_price,
                "sd1_up": base_price + 3.0,
                "sd1_dn": base_price - 3.0,
            },
            structure_data={
                "menthorq": {
                    "nearest_wall": {"type": "PUT", "price": base_price - 8.0, "dist_ticks": 32},
                    "gamma_flip": False
                },
                "orderflow": {
                    "delta_burst": False,
                    "delta_flip": True,  # FLIP ACTIVÉ
                    "cvd_divergence": False,
                    "stacked_imbalance": {"side": "SELL", "rows": 1},
                    "absorption": {"side": "BUY", "at_price": base_price},
                    "iceberg": None,
                }
            }
        )
    
    elif scenario == "opening_drive_fail":
        # Scénario Opening Drive Fail
        return TradingContext(
            timestamp=base_time.replace(hour=9, minute=35),  # Ouverture
            symbol="ES",
            price=base_price + 6.0,
            volume=4200.0,
            tick_size=0.25,
            market_data={
                "vwap": base_price,
                "sd1_up": base_price + 4.0,
                "sd1_dn": base_price - 4.0,
                "vix": 22.5,
            },
            structure_data={
                "menthorq": {
                    "nearest_wall": {"type": "CALL", "price": base_price + 10.0, "dist_ticks": 16},
                    "gamma_flip": False
                },
                "orderflow": {
                    "delta_burst": False,  # STALL
                    "delta_flip": False,
                    "cvd_divergence": False,
                    "stacked_imbalance": {"side": "BUY", "rows": 0},
                    "absorption": None,
                    "iceberg": None,
                }
            }
        )
    
    else:
        # Scénario par défaut
        return TradingContext(
            timestamp=base_time,
            symbol="ES",
            price=base_price,
            volume=2000.0,
            tick_size=0.25
        )

def test_scenario(selector: IntegratedStrategySelector, scenario: str, description: str):
    """Test un scénario spécifique"""
    print(f"\n🧪 TEST: {description}")
    print("=" * 60)
    
    # Créer le contexte
    ctx = create_realistic_trading_context(scenario)
    
    # Analyser
    result = selector.analyze_and_select(ctx)
    
    # Afficher résultats
    print(f"📊 Résultat: {result.selected_strategy.value}")
    print(f"🎯 Patterns considérés: {len(result.patterns_considered)}")
    print(f"🏆 Meilleur pattern: {result.best_pattern}")
    print(f"⚖️ Décision: {result.final_decision.value}")
    print(f"📈 Confiance: {result.selection_confidence:.3f}")
    print(f"⏱️ Temps: {result.total_processing_time_ms:.1f}ms")
    
    if result.pattern_signal:
        signal = result.pattern_signal
        print(f"📡 Signal: {signal.side} @ {signal.entry}")
        print(f"🛑 Stop: {signal.stop}")
        print(f"🎯 Targets: {signal.targets}")
        print(f"💭 Raison: {signal.reason}")
    
    return result

def main():
    """Test principal avec plusieurs scénarios"""
    print("🚀 TEST INTÉGRÉ RÉALISTE - INTEGRATED STRATEGY SELECTOR")
    print("=" * 70)
    
    # Configuration
    config = {
        'pattern_fire_cooldown_sec': 10,  # Cooldown court pour les tests
        'min_pattern_confidence': 0.50,   # Seuil plus bas pour les tests
        'min_confluence_execution': 0.60,
    }
    
    # Créer le selector
    selector = create_integrated_strategy_selector(config)
    
    # Tests des scénarios
    scenarios = [
        ("gamma_pin", "Gamma Pin Reversion - Absorption vendeuse sur CALL wall"),
        ("dealer_flip_breakout", "Dealer Flip Breakout - Gamma flip + burst + breakout"),
        ("liquidity_sweep", "Liquidity Sweep Reversal - Sweep + absorption acheteuse"),
        ("opening_drive_fail", "Opening Drive Fail - Stall sur CALL wall en ouverture"),
    ]
    
    results = []
    
    for scenario, description in scenarios:
        result = test_scenario(selector, scenario, description)
        results.append((scenario, result))
    
    # Résumé final
    print(f"\n📋 RÉSUMÉ FINAL")
    print("=" * 70)
    
    total_signals = sum(1 for _, r in results if r.final_decision.value == "execute_signal")
    total_patterns = sum(len(r.patterns_considered) for _, r in results)
    avg_time = sum(r.total_processing_time_ms for _, r in results) / len(results)
    
    print(f"🎯 Scénarios testés: {len(scenarios)}")
    print(f"📡 Signaux générés: {total_signals}/{len(scenarios)}")
    print(f"🔍 Patterns considérés au total: {total_patterns}")
    print(f"⏱️ Temps moyen: {avg_time:.1f}ms")
    
    # Status système final
    status = selector.get_system_status()
    print(f"\n🔧 STATUS SYSTÈME FINAL:")
    print(f"  • Analyses totales: {status['total_analyses']}")
    print(f"  • Signaux patterns: {status['pattern_signals']}")
    print(f"  • Signaux rejetés: {status['rejected_signals']}")
    print(f"  • Temps moyen: {status['avg_processing_time_ms']:.1f}ms")
    print(f"  • Composants actifs: {status['system_components']}")
    
    print(f"\n✅ TEST INTÉGRÉ RÉALISTE TERMINÉ")
    return True

if __name__ == "__main__":
    main()

