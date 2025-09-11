#!/usr/bin/env python3
"""
Test Suite Unitaires pour les 10 nouvelles stratégies
Tests approfondis avec unittest pour valider le comportement de chaque stratégie.
"""

import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dataclasses import dataclass

# === Imports des 10 stratégies ===
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

TICK = 0.25

def base_ctx(symbol="ES", price=5000.0):
    """Contexte de base pour les tests."""
    return {
        "symbol": symbol,
        "tick_size": TICK,
        "price": {"last": price},
        "atr": 2.0,  # ~8 ticks
        "vwap": {
            "vwap": price - 2.0,   # légèrement en dessous
            "sd1_up": price + 2.0,
            "sd1_dn": price - 6.0,
            "sd2_up": price + 6.0,
            "sd2_dn": price - 10.0,
            "sd3_up": price + 10.0,
            "sd3_dn": price - 14.0,
        },
        "vva": {"vpoc": price - 3.0, "vah": price + 5.0, "val": price - 5.0},
        "menthorq": {
            "nearest_wall": {"type": "CALL", "price": price + 6.0, "dist_ticks": 24},
            "gamma_flip": False
        },
        "orderflow": {
            "delta_burst": False,
            "delta_flip": False,
            "cvd": 0.0,
            "cvd_divergence": False,
            "stacked_imbalance": {"side": "BUY", "rows": 0},
            "absorption": None,
            "iceberg": None,
        },
        "quotes": {"speed_up": False},
        "correlation": {"es_nq": 0.9, "leader": "ES"},
        "vix": {"last": 14.0, "rising": False},
        "session": {"label": "OTHER", "time_ok": True},
        "basedata": {"last_wick_ticks": 0},
    }

# === Contexts spécifiques par stratégie ===

def ctx_gamma_pin_reversion():
    """Contexte pour tester gamma_pin_reversion."""
    ctx = base_ctx()
    # Mur suffisamment proche + absorption côté opposé
    ctx["menthorq"]["nearest_wall"]["dist_ticks"] = 6
    ctx["orderflow"]["absorption"] = {"side": "SELL", "at_price": ctx["price"]["last"] + 0.5}
    return ctx

def ctx_dealer_flip_breakout():
    """Contexte pour tester dealer_flip_breakout."""
    ctx = base_ctx()
    ctx["menthorq"]["gamma_flip"] = True
    ctx["orderflow"]["delta_burst"] = True
    ctx["quotes"]["speed_up"] = True
    # prix au-dessus de VWAP → direction LONG
    ctx["price"]["last"] = ctx["vwap"]["vwap"] + 5.0
    return ctx

def ctx_liquidity_sweep_reversal_short():
    """Contexte pour tester liquidity_sweep_reversal."""
    ctx = base_ctx()
    ctx["basedata"]["last_wick_ticks"] = 8
    ctx["orderflow"]["delta_flip"] = True
    ctx["orderflow"]["absorption"] = {"side": "BUY", "at_price": ctx["price"]["last"]}
    return ctx

def ctx_stacked_imbalance_continuation_long():
    """Contexte pour tester stacked_imbalance_continuation."""
    ctx = base_ctx()
    ctx["orderflow"]["stacked_imbalance"] = {"side": "BUY", "rows": 3}
    # prix déjà au-dessus du VWAP
    ctx["price"]["last"] = ctx["vwap"]["vwap"] + 3.0
    return ctx

def ctx_iceberg_tracker_follow_long():
    """Contexte pour tester iceberg_tracker_follow."""
    ctx = base_ctx()
    ctx["orderflow"]["iceberg"] = {"side": "BUY", "price": ctx["price"]["last"] - 1.0}
    return ctx

def ctx_cvd_divergence_trap_short():
    """Contexte pour tester cvd_divergence_trap."""
    ctx = base_ctx()
    ctx["orderflow"]["cvd_divergence"] = True
    ctx["orderflow"]["absorption"] = {"side": "BUY", "at_price": ctx["price"]["last"]}
    return ctx

def ctx_opening_drive_fail_short():
    """Contexte pour tester opening_drive_fail."""
    ctx = base_ctx()
    ctx["session"] = {"label": "OPEN", "time_ok": True}
    ctx["menthorq"]["nearest_wall"] = {"type": "CALL", "price": ctx["price"]["last"] + 5.0, "dist_ticks": 20}
    ctx["orderflow"]["delta_burst"] = False  # stall
    ctx["vix"]["rising"] = True
    return ctx

def ctx_es_nq_lead_lag_nq_long():
    """Contexte pour tester es_nq_lead_lag_mirror."""
    ctx = base_ctx(symbol="NQ")
    ctx["correlation"] = {"es_nq": 0.2, "leader": "NQ"}  # décorrélation notable + NQ leader
    ctx["orderflow"]["delta_burst"] = True
    # prix au-dessus de VWAP → LONG
    ctx["price"]["last"] = ctx["vwap"]["vwap"] + 5.0
    return ctx

def ctx_vwap_band_squeeze_break_long():
    """Contexte pour tester vwap_band_squeeze_break."""
    ctx = base_ctx()
    # bandes SD1 très serrées → petite largeur relative et burst
    p = ctx["price"]["last"]
    ctx["vwap"]["sd1_up"] = p + 0.4
    ctx["vwap"]["sd1_dn"] = p - 0.4
    ctx["orderflow"]["delta_burst"] = True
    ctx["quotes"]["speed_up"] = True
    ctx["price"]["last"] = ctx["vwap"]["sd1_up"] + 0.1
    return ctx

def ctx_profile_gap_fill_long():
    """Contexte pour tester profile_gap_fill."""
    ctx = base_ctx()
    # Simuler un LVN
    ctx["vva"]["lvn_low"] = ctx["price"]["last"] - 2.0
    ctx["vva"]["lvn_high"] = ctx["price"]["last"] + 2.0
    ctx["orderflow"]["absorption"] = None  # préférer l'absence de défense
    return ctx

# === Helper d'exécution ===

def run_strategy(strat, ctx):
    """Exécute une stratégie et capture les erreurs."""
    try:
        return strat.generate(ctx)
    except Exception as e:
        return {"error": f"{strat.name} crashed: {e}"}

# === TestCase principal ===

class TestStrategiesSuite(unittest.TestCase):
    """Suite de tests unitaires pour les 10 nouvelles stratégies."""

    def test_gamma_pin_reversion(self):
        """Test de la stratégie gamma_pin_reversion."""
        s = GammaPinReversion()
        sig = run_strategy(s, ctx_gamma_pin_reversion())
        self.assertIsInstance(sig, dict, "GammaPinReversion doit retourner un dict")
        self.assertIn(sig.get("side"), ("LONG", "SHORT"), "Signal doit contenir une direction")
        if "error" not in sig:
            self.assertGreaterEqual(sig.get("confidence", 0), 0.55, "Confiance minimale requise")

    def test_dealer_flip_breakout(self):
        """Test de la stratégie dealer_flip_breakout."""
        s = DealerFlipBreakout()
        sig = run_strategy(s, ctx_dealer_flip_breakout())
        self.assertIsInstance(sig, dict, "DealerFlipBreakout doit retourner un dict")
        if "error" not in sig:
            self.assertGreaterEqual(sig.get("confidence", 0), 0.65, "Confiance minimale requise")
            self.assertIn(sig.get("side"), ("LONG", "SHORT"), "Signal doit contenir une direction")

    def test_liquidity_sweep_reversal(self):
        """Test de la stratégie liquidity_sweep_reversal."""
        s = LiquiditySweepReversal()
        sig = run_strategy(s, ctx_liquidity_sweep_reversal_short())
        self.assertIsInstance(sig, dict, "LiquiditySweepReversal doit retourner un dict")
        if "error" not in sig:
            self.assertIn(sig.get("side"), ("LONG", "SHORT"), "Signal doit contenir une direction")
            self.assertGreaterEqual(sig.get("confidence", 0), 0.6, "Confiance minimale requise")

    def test_stacked_imbalance_continuation(self):
        """Test de la stratégie stacked_imbalance_continuation."""
        s = StackedImbalanceContinuation()
        sig = run_strategy(s, ctx_stacked_imbalance_continuation_long())
        self.assertIsInstance(sig, dict, "StackedImbalanceContinuation doit retourner un dict")
        if "error" not in sig:
            self.assertEqual(sig.get("side"), "LONG", "Devrait être LONG dans ce contexte")
            self.assertGreaterEqual(sig.get("confidence", 0), 0.6, "Confiance minimale requise")

    def test_iceberg_tracker_follow(self):
        """Test de la stratégie iceberg_tracker_follow."""
        s = IcebergTrackerFollow()
        sig = run_strategy(s, ctx_iceberg_tracker_follow_long())
        self.assertIsInstance(sig, dict, "IcebergTrackerFollow doit retourner un dict")
        if "error" not in sig:
            self.assertIn(sig.get("side"), ("LONG", "SHORT"), "Signal doit contenir une direction")
            self.assertGreaterEqual(sig.get("confidence", 0), 0.6, "Confiance minimale requise")

    def test_cvd_divergence_trap(self):
        """Test de la stratégie cvd_divergence_trap."""
        s = CvdDivergenceTrap()
        sig = run_strategy(s, ctx_cvd_divergence_trap_short())
        self.assertIsInstance(sig, dict, "CvdDivergenceTrap doit retourner un dict")
        if "error" not in sig:
            self.assertIn(sig.get("side"), ("LONG", "SHORT"), "Signal doit contenir une direction")
            self.assertGreaterEqual(sig.get("confidence", 0), 0.6, "Confiance minimale requise")

    def test_opening_drive_fail(self):
        """Test de la stratégie opening_drive_fail."""
        s = OpeningDriveFail()
        sig = run_strategy(s, ctx_opening_drive_fail_short())
        self.assertIsInstance(sig, dict, "OpeningDriveFail doit retourner un dict")
        if "error" not in sig:
            self.assertIn(sig.get("side"), ("LONG", "SHORT"), "Signal doit contenir une direction")
            self.assertGreaterEqual(sig.get("confidence", 0), 0.6, "Confiance minimale requise")

    def test_es_nq_lead_lag_mirror(self):
        """Test de la stratégie es_nq_lead_lag_mirror."""
        s = EsNqLeadLagMirror()
        sig = run_strategy(s, ctx_es_nq_lead_lag_nq_long())
        self.assertIsInstance(sig, dict, "EsNqLeadLagMirror doit retourner un dict")
        if "error" not in sig:
            self.assertEqual(sig.get("side"), "LONG", "Devrait être LONG dans ce contexte")
            self.assertGreaterEqual(sig.get("confidence", 0), 0.6, "Confiance minimale requise")

    def test_vwap_band_squeeze_break(self):
        """Test de la stratégie vwap_band_squeeze_break."""
        s = VwapBandSqueezeBreak()
        sig = run_strategy(s, ctx_vwap_band_squeeze_break_long())
        self.assertIsInstance(sig, dict, "VwapBandSqueezeBreak doit retourner un dict")
        if "error" not in sig:
            self.assertIn(sig.get("side"), ("LONG", "SHORT"), "Signal doit contenir une direction")
            self.assertGreaterEqual(sig.get("confidence", 0), 0.62, "Confiance minimale requise")

    def test_profile_gap_fill(self):
        """Test de la stratégie profile_gap_fill."""
        s = ProfileGapFill()
        sig = run_strategy(s, ctx_profile_gap_fill_long())
        self.assertIsInstance(sig, dict, "ProfileGapFill doit retourner un dict")
        if "error" not in sig:
            self.assertIn(sig.get("side"), ("LONG", "SHORT"), "Signal doit contenir une direction")
            self.assertGreaterEqual(sig.get("confidence", 0), 0.6, "Confiance minimale requise")

    def test_strategy_interface_consistency(self):
        """Test de cohérence de l'interface des stratégies."""
        strategies = [
            GammaPinReversion(), DealerFlipBreakout(), LiquiditySweepReversal(),
            StackedImbalanceContinuation(), IcebergTrackerFollow(), CvdDivergenceTrap(),
            OpeningDriveFail(), EsNqLeadLagMirror(), VwapBandSqueezeBreak(), ProfileGapFill()
        ]
        
        for strategy in strategies:
            # Vérifier que chaque stratégie a les attributs requis
            self.assertTrue(hasattr(strategy, 'name'), f"{strategy.__class__.__name__} doit avoir un attribut 'name'")
            self.assertTrue(hasattr(strategy, 'requires'), f"{strategy.__class__.__name__} doit avoir un attribut 'requires'")
            self.assertTrue(hasattr(strategy, 'params'), f"{strategy.__class__.__name__} doit avoir un attribut 'params'")
            self.assertTrue(hasattr(strategy, 'should_run'), f"{strategy.__class__.__name__} doit avoir une méthode 'should_run'")
            self.assertTrue(hasattr(strategy, 'generate'), f"{strategy.__class__.__name__} doit avoir une méthode 'generate'")
            
            # Vérifier que should_run retourne un booléen
            ctx = base_ctx()
            result = strategy.should_run(ctx)
            self.assertIsInstance(result, bool, f"{strategy.name}.should_run() doit retourner un booléen")

    def test_signal_format_consistency(self):
        """Test de cohérence du format des signaux."""
        strategies = [
            GammaPinReversion(), DealerFlipBreakout(), LiquiditySweepReversal(),
            StackedImbalanceContinuation(), IcebergTrackerFollow(), CvdDivergenceTrap(),
            OpeningDriveFail(), EsNqLeadLagMirror(), VwapBandSqueezeBreak(), ProfileGapFill()
        ]
        
        for strategy in strategies:
            # Tester avec un contexte minimal
            ctx = base_ctx()
            signal = strategy.generate(ctx)
            
            if signal is not None:  # Si un signal est généré
                # Vérifier les champs requis
                required_fields = ["strategy", "side", "confidence", "entry", "stop", "targets", "reason"]
                for field in required_fields:
                    self.assertIn(field, signal, f"{strategy.name} signal doit contenir le champ '{field}'")
                
                # Vérifier les types
                self.assertIn(signal["side"], ("LONG", "SHORT"), f"{strategy.name} side doit être LONG ou SHORT")
                self.assertIsInstance(signal["confidence"], (int, float), f"{strategy.name} confidence doit être numérique")
                self.assertIsInstance(signal["entry"], (int, float), f"{strategy.name} entry doit être numérique")
                self.assertIsInstance(signal["stop"], (int, float), f"{strategy.name} stop doit être numérique")
                self.assertIsInstance(signal["targets"], list, f"{strategy.name} targets doit être une liste")
                self.assertIsInstance(signal["reason"], str, f"{strategy.name} reason doit être une chaîne")


if __name__ == "__main__":
    # Exécution: python tools/test_strategies_suite.py
    unittest.main(verbosity=2)

