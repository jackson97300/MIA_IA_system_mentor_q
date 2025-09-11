#!/usr/bin/env python3
"""
Test des conditions spécifiques pour déclencher chaque pattern strategy
"""

import sys
import os
import pandas as pd

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def test_gamma_pin_reversion():
    """Test Gamma Pin Reversion avec conditions parfaites"""
    print("🧪 TEST: Gamma Pin Reversion")
    print("-" * 40)
    
    strategy = GammaPinReversion()
    
    # Conditions parfaites pour gamma pin
    ctx = {
        "price": {"last": 4500.0},
        "atr": 2.0,
        "tick_size": 0.25,
        "menthorq": {
            "nearest_wall": {"type": "CALL", "price": 4502.0, "dist_ticks": 8},  # Proche mur
            "gamma_flip": False
        },
        "orderflow": {
            "delta_burst": False,  # Pas de burst
            "stacked_imbalance": {"side": "BUY", "rows": 1},  # Pas de stacked fort
            "absorption": {"side": "SELL", "at_price": 4500.5},  # Absorption vendeuse
        },
        "vwap": {"vwap": 4498.0},
        "vva": {"vpoc": 4497.0, "vah": 4505.0, "val": 4495.0}
    }
    
    signal = strategy.generate(ctx)
    if signal:
        print(f"✅ Signal généré: {signal['side']} @ {signal['entry']}")
        print(f"   Confiance: {signal['confidence']}")
        print(f"   Stop: {signal['stop']}")
        print(f"   Targets: {signal['targets']}")
    else:
        print("❌ Aucun signal généré")
    
    return signal is not None

def test_dealer_flip_breakout():
    """Test Dealer Flip Breakout avec conditions parfaites"""
    print("\n🧪 TEST: Dealer Flip Breakout")
    print("-" * 40)
    
    strategy = DealerFlipBreakout()
    
    # Conditions parfaites pour dealer flip breakout
    ctx = {
        "price": {"last": 4508.0},  # Au-dessus de VWAP
        "atr": 2.0,
        "tick_size": 0.25,
        "menthorq": {
            "gamma_flip": True  # FLIP ACTIVÉ
        },
        "orderflow": {
            "delta_burst": True  # BURST ACTIVÉ
        },
        "quotes": {
            "speed_up": True  # SPEED UP ACTIVÉ
        },
        "vwap": {"vwap": 4500.0, "sd1_up": 4504.0, "sd2_up": 4508.0},
        "vva": {"vpoc": 4500.0}
    }
    
    signal = strategy.generate(ctx)
    if signal:
        print(f"✅ Signal généré: {signal['side']} @ {signal['entry']}")
        print(f"   Confiance: {signal['confidence']}")
        print(f"   Stop: {signal['stop']}")
        print(f"   Targets: {signal['targets']}")
    else:
        print("❌ Aucun signal généré")
    
    return signal is not None

def test_liquidity_sweep_reversal():
    """Test Liquidity Sweep Reversal avec conditions parfaites"""
    print("\n🧪 TEST: Liquidity Sweep Reversal")
    print("-" * 40)
    
    strategy = LiquiditySweepReversal()
    
    # Conditions parfaites pour liquidity sweep
    ctx = {
        "price": {"last": 4500.0},
        "atr": 2.0,
        "tick_size": 0.25,
        "basedata": {"last_wick_ticks": 8},  # Wick suffisant
        "orderflow": {
            "delta_flip": True,  # FLIP ACTIVÉ
            "absorption": {"side": "BUY", "at_price": 4500.0}  # Absorption acheteuse
        }
    }
    
    signal = strategy.generate(ctx)
    if signal:
        print(f"✅ Signal généré: {signal['side']} @ {signal['entry']}")
        print(f"   Confiance: {signal['confidence']}")
        print(f"   Stop: {signal['stop']}")
        print(f"   Targets: {signal['targets']}")
    else:
        print("❌ Aucun signal généré")
    
    return signal is not None

def test_stacked_imbalance_continuation():
    """Test Stacked Imbalance Continuation avec conditions parfaites"""
    print("\n🧪 TEST: Stacked Imbalance Continuation")
    print("-" * 40)
    
    strategy = StackedImbalanceContinuation()
    
    # Conditions parfaites pour stacked imbalance
    ctx = {
        "price": {"last": 4505.0},  # Au-dessus de VWAP
        "atr": 2.0,
        "tick_size": 0.25,
        "orderflow": {
            "stacked_imbalance": {"side": "BUY", "rows": 4}  # Stacked fort
        },
        "vwap": {"vwap": 4500.0}
    }
    
    signal = strategy.generate(ctx)
    if signal:
        print(f"✅ Signal généré: {signal['side']} @ {signal['entry']}")
        print(f"   Confiance: {signal['confidence']}")
        print(f"   Stop: {signal['stop']}")
        print(f"   Targets: {signal['targets']}")
    else:
        print("❌ Aucun signal généré")
    
    return signal is not None

def test_iceberg_tracker_follow():
    """Test Iceberg Tracker Follow avec conditions parfaites"""
    print("\n🧪 TEST: Iceberg Tracker Follow")
    print("-" * 40)
    
    strategy = IcebergTrackerFollow()
    
    # Conditions parfaites pour iceberg tracker
    ctx = {
        "price": {"last": 4500.0},
        "atr": 2.0,
        "tick_size": 0.25,
        "orderflow": {
            "iceberg": {"side": "BUY", "price": 4499.0}  # Iceberg acheteur
        }
    }
    
    signal = strategy.generate(ctx)
    if signal:
        print(f"✅ Signal généré: {signal['side']} @ {signal['entry']}")
        print(f"   Confiance: {signal['confidence']}")
        print(f"   Stop: {signal['stop']}")
        print(f"   Targets: {signal['targets']}")
    else:
        print("❌ Aucun signal généré")
    
    return signal is not None

def test_cvd_divergence_trap():
    """Test CVD Divergence Trap avec conditions parfaites"""
    print("\n🧪 TEST: CVD Divergence Trap")
    print("-" * 40)
    
    strategy = CvdDivergenceTrap()
    
    # Conditions parfaites pour CVD divergence
    ctx = {
        "price": {"last": 4500.0},
        "atr": 2.0,
        "tick_size": 0.25,
        "orderflow": {
            "cvd_divergence": True,  # DIVERGENCE ACTIVÉE
            "absorption": {"side": "BUY", "at_price": 4500.0}  # Absorption
        },
        "vva": {"vpoc": 4500.0},
        "vwap": {"vwap": 4500.0}
    }
    
    signal = strategy.generate(ctx)
    if signal:
        print(f"✅ Signal généré: {signal['side']} @ {signal['entry']}")
        print(f"   Confiance: {signal['confidence']}")
        print(f"   Stop: {signal['stop']}")
        print(f"   Targets: {signal['targets']}")
    else:
        print("❌ Aucun signal généré")
    
    return signal is not None

def test_opening_drive_fail():
    """Test Opening Drive Fail avec conditions parfaites"""
    print("\n🧪 TEST: Opening Drive Fail")
    print("-" * 40)
    
    strategy = OpeningDriveFail()
    
    # Conditions parfaites pour opening drive fail
    ctx = {
        "price": {"last": 4500.0},
        "atr": 2.0,
        "tick_size": 0.25,
        "session": {"label": "OPEN", "time_ok": True},  # Session ouverture
        "menthorq": {
            "nearest_wall": {"type": "CALL", "price": 4505.0, "dist_ticks": 20}
        },
        "orderflow": {
            "delta_burst": False  # STALL
        },
        "vix": {"rising": True},  # VIX en hausse
        "vwap": {"vwap": 4498.0}
    }
    
    signal = strategy.generate(ctx)
    if signal:
        print(f"✅ Signal généré: {signal['side']} @ {signal['entry']}")
        print(f"   Confiance: {signal['confidence']}")
        print(f"   Stop: {signal['stop']}")
        print(f"   Targets: {signal['targets']}")
    else:
        print("❌ Aucun signal généré")
    
    return signal is not None

def test_es_nq_lead_lag_mirror():
    """Test ES-NQ Lead-Lag Mirror avec conditions parfaites"""
    print("\n🧪 TEST: ES-NQ Lead-Lag Mirror")
    print("-" * 40)
    
    strategy = EsNqLeadLagMirror()
    
    # Conditions parfaites pour ES-NQ lead-lag
    ctx = {
        "price": {"last": 4505.0},  # Au-dessus de VWAP
        "atr": 2.0,
        "tick_size": 0.25,
        "symbol": "NQ",
        "correlation": {"es_nq": 0.2, "leader": "NQ"},  # Décorrélation + NQ leader
        "orderflow": {
            "delta_burst": True  # BURST ACTIVÉ
        },
        "vwap": {"vwap": 4500.0}
    }
    
    signal = strategy.generate(ctx)
    if signal:
        print(f"✅ Signal généré: {signal['side']} @ {signal['entry']}")
        print(f"   Confiance: {signal['confidence']}")
        print(f"   Stop: {signal['stop']}")
        print(f"   Targets: {signal['targets']}")
    else:
        print("❌ Aucun signal généré")
    
    return signal is not None

def test_vwap_band_squeeze_break():
    """Test VWAP Band Squeeze Break avec conditions parfaites"""
    print("\n🧪 TEST: VWAP Band Squeeze Break")
    print("-" * 40)
    
    strategy = VwapBandSqueezeBreak()
    
    # Conditions parfaites pour VWAP squeeze break
    ctx = {
        "price": {"last": 4503.0},  # Au-dessus de SD1
        "atr": 2.0,
        "tick_size": 0.25,
        "vwap": {
            "vwap": 4500.0,
            "sd1_up": 4502.0,  # Bande serrée
            "sd1_dn": 4498.0,  # Bande serrée
            "sd2_up": 4516.0,
            "sd2_dn": 4484.0
        },
        "orderflow": {
            "delta_burst": True  # BURST ACTIVÉ
        },
        "quotes": {
            "speed_up": True  # SPEED UP ACTIVÉ
        }
    }
    
    signal = strategy.generate(ctx)
    if signal:
        print(f"✅ Signal généré: {signal['side']} @ {signal['entry']}")
        print(f"   Confiance: {signal['confidence']}")
        print(f"   Stop: {signal['stop']}")
        print(f"   Targets: {signal['targets']}")
    else:
        print("❌ Aucun signal généré")
    
    return signal is not None

def main():
    """Test principal de toutes les conditions"""
    print("🚀 TEST DES CONDITIONS SPÉCIFIQUES - PATTERN STRATEGIES")
    print("=" * 70)
    
    tests = [
        test_gamma_pin_reversion,
        test_dealer_flip_breakout,
        test_liquidity_sweep_reversal,
        test_stacked_imbalance_continuation,
        test_iceberg_tracker_follow,
        test_cvd_divergence_trap,
        test_opening_drive_fail,
        test_es_nq_lead_lag_mirror,
        test_vwap_band_squeeze_break,
    ]
    
    results = []
    for test in tests:
        try:
            success = test()
            results.append(success)
        except Exception as e:
            print(f"❌ Erreur dans le test: {e}")
            results.append(False)
    
    # Résumé
    print(f"\n📋 RÉSUMÉ DES TESTS")
    print("=" * 70)
    successful = sum(results)
    total = len(results)
    
    print(f"🎯 Tests réussis: {successful}/{total}")
    print(f"📈 Taux de succès: {successful/total*100:.1f}%")
    
    if successful == total:
        print("🎉 TOUS LES PATTERNS FONCTIONNENT !")
    else:
        print("⚠️ Certains patterns nécessitent des ajustements")
    
    return successful == total

if __name__ == "__main__":
    main()


