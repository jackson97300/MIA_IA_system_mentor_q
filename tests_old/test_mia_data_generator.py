# -*- coding: utf-8 -*-
"""
Tests pour MIA_IA_DataGenerator - Version Hybride Optimale
Valide les shapes, invariants, et fonctionnalités critiques
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
from pathlib import Path
import sys

# Ajouter le répertoire parent au path pour importer core
sys.path.append(str(Path(__file__).parent.parent))

from core.mia_data_generator import MIA_IA_DataGenerator, GenConfig


def test_shapes_and_invariants():
    """Test principal : shapes, colonnes, et invariants critiques"""
    print("🧪 Test 1: Shapes et invariants de base")
    
    gen = MIA_IA_DataGenerator(seed=1)
    cfg = GenConfig(start=datetime(2025,8,21,13,30,tzinfo=timezone.utc), minutes=30)
    data = gen.generate_realistic_session(cfg, scenario="confluence_breakout")

    l1, l2, bars, foot, ctx, feats, gt = (data[k] for k in ["l1","l2","bars","footprint","context","leadership_features","ground_truth"])

    # ✅ Colonnes clés présentes
    print("  ✅ Vérification des colonnes...")
    for df, cols in [
        (l1, ["ts","symbol","bid","ask","last_price","bid_size","ask_size","last_size"]),
        (l2, ["ts","symbol","bid_px","ask_px","bid_sz","ask_sz","mid","spread"]),
        (bars, ["ts","symbol","open","high","low","close","volume","vwap"]),
        (feats, ["ts","symbol","confluence_score","delta_divergence","volume_imbalance","sierra_pattern_strength","leadership_strength","volatility_regime","options_flow_bias","gamma_proximity"]),
        (gt, ["ts","symbol","label","confidence","side"])
    ]:
        missing = set(cols) - set(df.columns)
        assert not missing, f"Colonnes manquantes dans {df.name if hasattr(df, 'name') else 'DataFrame'}: {missing}"

    # ✅ Invariants critiques
    print("  ✅ Vérification des invariants...")
    
    # L1: ask > bid
    assert (l1["ask"] > l1["bid"]).all(), "❌ Violation: ask <= bid dans L1"
    
    # L2: book monotone
    def is_mono(row): 
        return row["bid_px"][0] > row["bid_px"][-1] and row["ask_px"][0] < row["ask_px"][-1]
    assert l2.head(200).apply(is_mono, axis=1).all(), "❌ Violation: book non monotone dans L2"
    
    # Bars: OHLC cohérent
    assert (bars["high"] >= bars["low"]).all(), "❌ Violation: high < low dans bars"
    assert (bars["high"] >= bars["open"]).all(), "❌ Violation: high < open dans bars"
    assert (bars["high"] >= bars["close"]).all(), "❌ Violation: high < close dans bars"
    assert (bars["low"] <= bars["open"]).all(), "❌ Violation: low > open dans bars"
    assert (bars["low"] <= bars["close"]).all(), "❌ Violation: low > close dans bars"
    
    # Ground truth: side cohérent avec label
    long_mask = gt["label"] == "long_bias"
    short_mask = gt["label"] == "short_bias"
    assert (gt.loc[long_mask, "side"] == 1).all(), "❌ Violation: long_bias sans side=1"
    assert (gt.loc[short_mask, "side"] == -1).all(), "❌ Violation: short_bias sans side=-1"
    
    print("  ✅ Tous les invariants respectés !")


def test_leadership_features():
    """Test des features leadership améliorées"""
    print("🧪 Test 2: Features leadership")
    
    gen = MIA_IA_DataGenerator(seed=42)
    cfg = GenConfig(start=datetime(2025,8,21,13,30,tzinfo=timezone.utc), minutes=60)
    
    # Test avec leadership NQ
    data_nq = gen.generate_realistic_session(cfg, scenario="normal", leadership="NQ_leads", strength=0.2)
    feats_nq = data_nq["leadership_features"]
    
    # Test avec leadership ES
    data_es = gen.generate_realistic_session(cfg, scenario="normal", leadership="ES_leads", strength=0.2)
    feats_es = data_es["leadership_features"]
    
    # ✅ Vérifications
    print("  ✅ Vérification des ranges...")
    
    # Confluence score: [0, 1]
    assert (feats_nq["confluence_score"] >= 0).all() and (feats_nq["confluence_score"] <= 1).all()
    assert (feats_es["confluence_score"] >= 0).all() and (feats_es["confluence_score"] <= 1).all()
    
    # Volume imbalance: [-1, 1]
    assert (feats_nq["volume_imbalance"] >= -1).all() and (feats_nq["volume_imbalance"] <= 1).all()
    
    # Leadership strength: [0, 1]
    assert (feats_nq["leadership_strength"] >= 0).all() and (feats_nq["leadership_strength"] <= 1).all()
    
    # Options flow bias: [-1, 1]
    assert (feats_nq["options_flow_bias"] >= -1).all() and (feats_nq["options_flow_bias"] <= 1).all()
    
    # Volatility regime: valeurs attendues
    expected_regimes = {"low_vol", "normal_vol", "high_vol"}
    assert set(feats_nq["volatility_regime"].unique()).issubset(expected_regimes)
    
    print("  ✅ Features leadership valides !")


def test_scenarios_mia_ia():
    """Test des scénarios MIA_IA spécifiques"""
    print("🧪 Test 3: Scénarios MIA_IA")
    
    gen = MIA_IA_DataGenerator(seed=123)
    cfg = GenConfig(start=datetime(2025,8,21,13,30,tzinfo=timezone.utc), minutes=60)
    
    scenarios = ["orderflow_accumulation", "orderflow_distribution", "confluence_breakout", "delta_divergence"]
    
    for scenario in scenarios:
        print(f"  🎯 Test du scénario: {scenario}")
        data = gen.generate_realistic_session(cfg, scenario=scenario)
        gt = data["ground_truth"]
        
        # ✅ Vérification des labels selon le scénario
        if scenario in ["orderflow_accumulation", "confluence_breakout"]:
            assert (gt["label"] == "long_bias").any(), f"❌ Scénario {scenario}: pas de long_bias"
            assert (gt["side"] == 1).any(), f"❌ Scénario {scenario}: pas de side=1"
        elif scenario == "orderflow_distribution":
            assert (gt["label"] == "short_bias").any(), f"❌ Scénario {scenario}: pas de short_bias"
            assert (gt["side"] == -1).any(), f"❌ Scénario {scenario}: pas de side=-1"
        elif scenario == "delta_divergence":
            assert (gt["label"] == "divergence_warning").any(), f"❌ Scénario {scenario}: pas de divergence_warning"
    
    print("  ✅ Tous les scénarios MIA_IA valides !")


def test_options_context():
    """Test du contexte options enrichi"""
    print("🧪 Test 4: Contexte options")
    
    gen = MIA_IA_DataGenerator(seed=456)
    cfg = GenConfig(start=datetime(2025,8,21,13,30,tzinfo=timezone.utc), minutes=30)
    data = gen.generate_realistic_session(cfg, scenario="gamma_pin")
    ctx = data["context"]
    
    # ✅ Vérifications
    print("  ✅ Vérification des métriques options...")
    
    # VIX: raisonnable
    assert (ctx["vix"] >= 10).all() and (ctx["vix"] <= 50).all()
    
    # Gamma exposure: positif
    assert (ctx["gamma_exposure"] > 0).all()
    
    # Put/Call ratio: [0.7, 1.3]
    assert (ctx["put_call_ratio"] >= 0.7).all() and (ctx["put_call_ratio"] <= 1.3).all()
    
    # Pin strength: [0, 1]
    assert (ctx["pin_strength"] >= 0).all() and (ctx["pin_strength"] <= 1).all()
    
    # Vol trigger: [0, 1]
    assert (ctx["vol_trigger"] >= 0).all() and (ctx["vol_trigger"] <= 1).all()
    
    print("  ✅ Contexte options valide !")


def test_export_parquet():
    """Test de l'export Parquet"""
    print("🧪 Test 5: Export Parquet")
    
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        print("  ⚠️ PyArrow non installé - test d'export ignoré")
        return
    
    gen = MIA_IA_DataGenerator(seed=789)
    cfg = GenConfig(start=datetime(2025,8,21,13,30,tzinfo=timezone.utc), minutes=15)
    data = gen.generate_realistic_session(cfg, scenario="normal")
    
    # Export test
    test_dir = Path("test_output")
    MIA_IA_DataGenerator.export_to_parquet(data, str(test_dir))
    
    # Vérification
    expected_files = ["l1.parquet", "l2.parquet", "bars.parquet", "footprint.parquet", 
                     "context.parquet", "leadership_features.parquet", "ground_truth.parquet"]
    
    for file_name in expected_files:
        file_path = test_dir / file_name
        assert file_path.exists(), f"❌ Fichier manquant: {file_name}"
        
        # Vérification que le fichier est lisible
        df_read = pq.read_table(str(file_path)).to_pandas()
        assert len(df_read) > 0, f"❌ Fichier vide: {file_name}"
    
    # Nettoyage
    import shutil
    shutil.rmtree(test_dir)
    
    print("  ✅ Export Parquet fonctionnel !")


def test_performance():
    """Test de performance basique"""
    print("🧪 Test 6: Performance")
    
    import time
    
    gen = MIA_IA_DataGenerator(seed=999)
    cfg = GenConfig(start=datetime(2025,8,21,13,30,tzinfo=timezone.utc), minutes=120)
    
    start_time = time.time()
    data = gen.generate_realistic_session(cfg, scenario="confluence_breakout", leadership="NQ_leads", strength=0.18)
    end_time = time.time()
    
    generation_time = end_time - start_time
    print(f"  ⏱️ Temps de génération 2h: {generation_time:.2f}s")
    
    # Vérification des tailles
    total_rows = sum(len(df) for df in data.values())
    print(f"  📊 Total rows générées: {total_rows:,}")
    
    # Performance acceptable: < 5s pour 2h de données
    assert generation_time < 5.0, f"❌ Performance insuffisante: {generation_time:.2f}s > 5s"
    
    print("  ✅ Performance acceptable !")


def run_all_tests():
    """Lance tous les tests"""
    print("🚀 LANCEMENT DES TESTS MIA_IA_DataGenerator - Version Hybride")
    print("=" * 70)
    
    tests = [
        test_shapes_and_invariants,
        test_leadership_features,
        test_scenarios_mia_ia,
        test_options_context,
        test_export_parquet,
        test_performance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
            print(f"✅ {test.__name__} - SUCCÈS\n")
        except Exception as e:
            print(f"❌ {test.__name__} - ÉCHEC: {e}\n")
    
    print("=" * 70)
    print(f"📊 RÉSULTATS: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS RÉUSSIS ! Version hybride prête pour la production !")
        return True
    else:
        print("⚠️ Certains tests ont échoué - vérification nécessaire")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)




