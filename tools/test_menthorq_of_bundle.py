#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Tests pour les stratégies MenthorQ + Orderflow Bundle
Tests unitaires pour les 6 nouvelles stratégies MenthorQ

Version: Production Ready v1.0
Performance: <100ms pour tous les tests
Responsabilité: Validation des stratégies MenthorQ
"""

import unittest
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.menthorq_of_bundle import (
    ZeroDTEWallSweepReversal, GammaWallBreakAndGo, HVLMagnetFade,
    D1ExtremeTrap, GexClusterMeanRevert, CallPutChannelRotation,
    get_family_tag, deduplicate_by_family, FAMILY_TAGS
)

TICK = 0.25

def base_ctx(price=6500.0):
    """Contexte de base pour les tests"""
    return {
        "tick_size": TICK,
        "price": {"last": price},
        "atr": 2.0,  # ~8 ticks
        "vwap": {"vwap": price - 2.0, "sd2_up": price + 6.0, "sd2_dn": price - 6.0},
        "vva": {"vpoc": price - 3.0, "vah": price + 5.0, "val": price - 5.0},
        "orderflow": {
            "delta_burst": False,
            "delta_flip": False,
            "cvd_divergence": False,
            "stacked_imbalance": {"side": "BUY", "rows": 0},
            "absorption": None,
        },
        "quotes": {"speed_up": False},
        "menthorq": {
            # exemples typiques inspirés de votre JSON
            "call_resistance": 6425.0,
            "put_support": 6465.0,
            "hvl": 6460.25,
            "d1min": 6451.75,   # Corrigé pour être cohérent (d1min < d1max)
            "d1max": 6525.00,
            "zero_dte": {"call": 6425.0, "put": 6465.0, "gamma_wall": 6500.0},
            "gex_levels": [6510.0, 6510.5, 6511.0, 6511.5, 6512.0],  # Cluster très serré (span = 2 points = 8 ticks)
            "gamma_flip": True
        },
        "basedata": {"last_wick_ticks": 0},
    }


class TestMenthorQBundle(unittest.TestCase):
    """Tests pour les stratégies MenthorQ Bundle"""

    def test_zero_dte_wall_sweep_reversal_short(self):
        """Test ZeroDTE Wall Sweep Reversal - SHORT"""
        ctx = base_ctx()
        ctx["basedata"]["last_wick_ticks"] = 8
        ctx["orderflow"]["delta_flip"] = True
        ctx["orderflow"]["absorption"] = {"side": "BUY", "at_price": ctx["price"]["last"]}  # au-dessus CALL
        # Rapprocher le prix du mur CALL pour que le test fonctionne
        ctx["price"]["last"] = ctx["menthorq"]["zero_dte"]["call"] + 1.0  # Proche du CALL
        s = ZeroDTEWallSweepReversal()
        sig = s.generate(ctx)
        self.assertIsInstance(sig, dict)
        self.assertEqual(sig["side"], "SHORT")
        self.assertEqual(sig["strategy"], "zero_dte_wall_sweep_reversal")
        self.assertGreater(sig["confidence"], 0.6)

    def test_zero_dte_wall_sweep_reversal_long(self):
        """Test ZeroDTE Wall Sweep Reversal - LONG"""
        ctx = base_ctx()
        ctx["basedata"]["last_wick_ticks"] = 8
        ctx["orderflow"]["delta_flip"] = True
        ctx["orderflow"]["absorption"] = {"side": "SELL", "at_price": ctx["price"]["last"]}  # sous PUT
        # rapprocher le prix du PUT pour rendre le test plus plausible
        ctx["price"]["last"] = ctx["menthorq"]["zero_dte"]["put"] - 0.5
        s = ZeroDTEWallSweepReversal()
        sig = s.generate(ctx)
        self.assertIsInstance(sig, dict)
        self.assertEqual(sig["side"], "LONG")
        self.assertEqual(sig["strategy"], "zero_dte_wall_sweep_reversal")

    def test_gamma_wall_break_and_go_long(self):
        """Test Gamma Wall Break and Go - LONG"""
        ctx = base_ctx()
        ctx["orderflow"]["delta_burst"] = True
        ctx["quotes"]["speed_up"] = True
        # prix > gamma_wall ET > vwap
        ctx["price"]["last"] = ctx["menthorq"]["zero_dte"]["gamma_wall"] + 3.0
        ctx["vwap"]["vwap"] = ctx["price"]["last"] - 1.0
        s = GammaWallBreakAndGo()
        sig = s.generate(ctx)
        self.assertIsInstance(sig, dict)
        self.assertEqual(sig["side"], "LONG")
        self.assertEqual(sig["strategy"], "gamma_wall_break_and_go")
        self.assertGreater(sig["confidence"], 0.6)

    def test_gamma_wall_break_and_go_short(self):
        """Test Gamma Wall Break and Go - SHORT"""
        ctx = base_ctx()
        ctx["orderflow"]["delta_burst"] = True
        ctx["quotes"]["speed_up"] = True
        # prix < gamma_wall ET < vwap
        ctx["price"]["last"] = ctx["menthorq"]["zero_dte"]["gamma_wall"] - 3.0
        ctx["vwap"]["vwap"] = ctx["price"]["last"] + 1.0
        s = GammaWallBreakAndGo()
        sig = s.generate(ctx)
        self.assertIsInstance(sig, dict)
        self.assertEqual(sig["side"], "SHORT")
        self.assertEqual(sig["strategy"], "gamma_wall_break_and_go")

    def test_hvl_magnet_fade_short(self):
        """Test HVL Magnet Fade - SHORT"""
        ctx = base_ctx()
        # extension au-dessus de HVL sans burst → fade short vers HVL
        ctx["price"]["last"] = ctx["menthorq"]["hvl"] + 1.0
        ctx["orderflow"]["delta_burst"] = False
        s = HVLMagnetFade()
        sig = s.generate(ctx)
        self.assertIsInstance(sig, dict)
        self.assertEqual(sig["side"], "SHORT")
        self.assertEqual(sig["strategy"], "hvl_magnet_fade")

    def test_hvl_magnet_fade_long(self):
        """Test HVL Magnet Fade - LONG"""
        ctx = base_ctx()
        # extension en-dessous de HVL sans burst → fade long vers HVL
        ctx["price"]["last"] = ctx["menthorq"]["hvl"] - 1.0
        ctx["orderflow"]["delta_burst"] = False
        s = HVLMagnetFade()
        sig = s.generate(ctx)
        self.assertIsInstance(sig, dict)
        self.assertEqual(sig["side"], "LONG")
        self.assertEqual(sig["strategy"], "hvl_magnet_fade")

    def test_d1_extreme_trap_short(self):
        """Test D1 Extreme Trap - SHORT"""
        ctx = base_ctx()
        ctx["orderflow"]["cvd_divergence"] = True
        # fake au-dessus 1d_max
        ctx["price"]["last"] = ctx["menthorq"]["d1max"] + 1.0
        s = D1ExtremeTrap()
        sig = s.generate(ctx)
        self.assertIsInstance(sig, dict)
        self.assertEqual(sig["side"], "SHORT")
        self.assertEqual(sig["strategy"], "d1_extreme_trap")

    def test_d1_extreme_trap_long(self):
        """Test D1 Extreme Trap - LONG"""
        ctx = base_ctx()
        ctx["orderflow"]["cvd_divergence"] = True
        # fake en-dessous 1d_min
        ctx["price"]["last"] = ctx["menthorq"]["d1min"] - 1.0
        s = D1ExtremeTrap()
        sig = s.generate(ctx)
        self.assertIsInstance(sig, dict)
        self.assertEqual(sig["side"], "LONG")
        self.assertEqual(sig["strategy"], "d1_extreme_trap")

    def test_gex_cluster_mean_revert_short(self):
        """Test GEX Cluster Mean Revert - SHORT"""
        ctx = base_ctx()
        # sortir par le haut du cluster => short vers centre
        hi = max(ctx["menthorq"]["gex_levels"])
        ctx["price"]["last"] = hi + 1.0
        s = GexClusterMeanRevert()
        sig = s.generate(ctx)
        self.assertIsInstance(sig, dict)
        self.assertEqual(sig["side"], "SHORT")
        self.assertEqual(sig["strategy"], "gex_cluster_mean_revert")

    def test_gex_cluster_mean_revert_long(self):
        """Test GEX Cluster Mean Revert - LONG"""
        ctx = base_ctx()
        # sortir par le bas du cluster => long vers centre
        lo = min(ctx["menthorq"]["gex_levels"])
        ctx["price"]["last"] = lo - 1.0
        s = GexClusterMeanRevert()
        sig = s.generate(ctx)
        self.assertIsInstance(sig, dict)
        self.assertEqual(sig["side"], "LONG")
        self.assertEqual(sig["strategy"], "gex_cluster_mean_revert")

    def test_call_put_channel_rotation_short(self):
        """Test Call Put Channel Rotation - SHORT"""
        ctx = base_ctx()
        # prix proche du CALL → short vers centre
        ctx["price"]["last"] = ctx["menthorq"]["call_resistance"] + 0.5
        s = CallPutChannelRotation()
        sig = s.generate(ctx)
        self.assertIsInstance(sig, dict)
        self.assertEqual(sig["side"], "SHORT")
        self.assertEqual(sig["strategy"], "call_put_channel_rotation")

    def test_call_put_channel_rotation_long(self):
        """Test Call Put Channel Rotation - LONG"""
        ctx = base_ctx()
        # prix proche du PUT → long vers centre
        ctx["price"]["last"] = ctx["menthorq"]["put_support"] - 0.5
        s = CallPutChannelRotation()
        sig = s.generate(ctx)
        self.assertIsInstance(sig, dict)
        self.assertEqual(sig["side"], "LONG")
        self.assertEqual(sig["strategy"], "call_put_channel_rotation")

    def test_strategy_interface_consistency(self):
        """Test que toutes les stratégies respectent l'interface"""
        strategies = [
            ZeroDTEWallSweepReversal(),
            GammaWallBreakAndGo(),
            HVLMagnetFade(),
            D1ExtremeTrap(),
            GexClusterMeanRevert(),
            CallPutChannelRotation(),
        ]
        
        for strategy in strategies:
            # Vérifier les attributs requis
            self.assertTrue(hasattr(strategy, 'name'))
            self.assertTrue(hasattr(strategy, 'requires'))
            self.assertTrue(hasattr(strategy, 'params'))
            self.assertTrue(hasattr(strategy, 'should_run'))
            self.assertTrue(hasattr(strategy, 'generate'))
            
            # Vérifier les types
            self.assertIsInstance(strategy.name, str)
            self.assertIsInstance(strategy.requires, tuple)
            self.assertIsInstance(strategy.params, dict)

    def test_signal_format_consistency(self):
        """Test que tous les signaux respectent le format standard"""
        ctx = base_ctx()
        ctx["basedata"]["last_wick_ticks"] = 8
        ctx["orderflow"]["delta_flip"] = True
        ctx["orderflow"]["absorption"] = {"side": "BUY", "at_price": ctx["price"]["last"]}
        ctx["orderflow"]["delta_burst"] = True
        ctx["quotes"]["speed_up"] = True
        ctx["orderflow"]["cvd_divergence"] = True
        
        strategies = [
            ZeroDTEWallSweepReversal(),
            GammaWallBreakAndGo(),
            HVLMagnetFade(),
            D1ExtremeTrap(),
            GexClusterMeanRevert(),
            CallPutChannelRotation(),
        ]
        
        for strategy in strategies:
            sig = strategy.generate(ctx)
            if sig:  # Si un signal est généré
                # Vérifier les clés requises
                required_keys = ["strategy", "side", "confidence", "entry", "stop", "targets", "reason", "metadata"]
                for key in required_keys:
                    self.assertIn(key, sig, f"Clé manquante '{key}' dans {strategy.name}")
                
                # Vérifier les types et valeurs
                self.assertIn(sig["side"], ["LONG", "SHORT"])
                self.assertIsInstance(sig["confidence"], (int, float))
                self.assertGreaterEqual(sig["confidence"], 0.0)
                self.assertLessEqual(sig["confidence"], 1.0)
                self.assertIsInstance(sig["entry"], (int, float))
                self.assertIsInstance(sig["stop"], (int, float))
                self.assertIsInstance(sig["targets"], list)
                self.assertIsInstance(sig["reason"], str)
                self.assertIsInstance(sig["metadata"], dict)

    def test_family_tags(self):
        """Test du système de tags de famille"""
        # Test des nouvelles stratégies
        self.assertEqual(get_family_tag("zero_dte_wall_sweep_reversal"), "REVERSAL")
        self.assertEqual(get_family_tag("gamma_wall_break_and_go"), "BREAKOUT")
        self.assertEqual(get_family_tag("hvl_magnet_fade"), "MEAN_REVERT")
        self.assertEqual(get_family_tag("d1_extreme_trap"), "TRAP")
        self.assertEqual(get_family_tag("gex_cluster_mean_revert"), "MEAN_REVERT")
        self.assertEqual(get_family_tag("call_put_channel_rotation"), "RANGE_ROTATION")
        
        # Test des stratégies existantes
        self.assertEqual(get_family_tag("dealer_flip_breakout"), "BREAKOUT")
        self.assertEqual(get_family_tag("gamma_pin_reversion"), "REVERSAL")
        
        # Test stratégie inconnue
        self.assertEqual(get_family_tag("unknown_strategy"), "OTHER")

    def test_deduplication_by_family(self):
        """Test du dédoublonnage par famille"""
        # Créer des signaux de test avec différents scores
        signals = [
            (0.7, {"strategy": "gamma_wall_break_and_go", "side": "LONG"}),
            (0.6, {"strategy": "dealer_flip_breakout", "side": "LONG"}),  # Même famille BREAKOUT
            (0.8, {"strategy": "zero_dte_wall_sweep_reversal", "side": "SHORT"}),
            (0.5, {"strategy": "liquidity_sweep_reversal", "side": "SHORT"}),  # Même famille REVERSAL
            (0.9, {"strategy": "hvl_magnet_fade", "side": "LONG"}),
        ]
        
        deduplicated = deduplicate_by_family(signals)
        
        # Vérifier qu'on a un signal par famille
        families = [get_family_tag(sig["strategy"]) for _, sig in deduplicated]
        self.assertEqual(len(families), len(set(families)))  # Pas de doublons
        
        # Vérifier que les meilleurs scores sont gardés
        breakout_signals = [sig for _, sig in deduplicated if get_family_tag(sig["strategy"]) == "BREAKOUT"]
        self.assertEqual(len(breakout_signals), 1)
        self.assertEqual(breakout_signals[0]["strategy"], "gamma_wall_break_and_go")  # Score 0.7 > 0.6
        
        reversal_signals = [sig for _, sig in deduplicated if get_family_tag(sig["strategy"]) == "REVERSAL"]
        self.assertEqual(len(reversal_signals), 1)
        self.assertEqual(reversal_signals[0]["strategy"], "zero_dte_wall_sweep_reversal")  # Score 0.8 > 0.5

    def test_no_signal_when_conditions_not_met(self):
        """Test qu'aucun signal n'est généré quand les conditions ne sont pas remplies"""
        ctx = base_ctx()
        # Contexte vide - aucune condition remplie
        ctx["menthorq"] = {}
        ctx["orderflow"] = {}
        ctx["basedata"] = {"last_wick_ticks": 0}
        
        strategies = [
            ZeroDTEWallSweepReversal(),
            GammaWallBreakAndGo(),
            HVLMagnetFade(),
            D1ExtremeTrap(),
            GexClusterMeanRevert(),
            CallPutChannelRotation(),
        ]
        
        for strategy in strategies:
            sig = strategy.generate(ctx)
            self.assertIsNone(sig, f"{strategy.name} devrait retourner None avec un contexte vide")

    def test_should_run_method(self):
        """Test de la méthode should_run"""
        strategies = [
            ZeroDTEWallSweepReversal(),
            GammaWallBreakAndGo(),
            HVLMagnetFade(),
            D1ExtremeTrap(),
            GexClusterMeanRevert(),
            CallPutChannelRotation(),
        ]
        
        # Contexte complet
        ctx_complete = base_ctx()
        for strategy in strategies:
            self.assertTrue(strategy.should_run(ctx_complete), f"{strategy.name} devrait run avec contexte complet")
        
        # Contexte vide
        ctx_empty = {}
        for strategy in strategies:
            self.assertFalse(strategy.should_run(ctx_empty), f"{strategy.name} ne devrait pas run avec contexte vide")


if __name__ == "__main__":
    # Exécution: python -m unittest -v tools.test_menthorq_of_bundle
    unittest.main(verbosity=2)
