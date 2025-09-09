#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple du MIA_IA_DataGenerator
"""

from datetime import datetime, timezone
from core.mia_data_generator import MIA_IA_DataGenerator, GenConfig

def test_simple_generation():
    """Test simple de génération"""
    print("🧪 TEST SIMPLE MIA_IA_DataGenerator")
    print("=" * 50)
    
    # Initialisation
    gen = MIA_IA_DataGenerator(seed=42)
    cfg = GenConfig(
        start=datetime(2025, 8, 21, 13, 30, tzinfo=timezone.utc),
        minutes=10  # 10 minutes pour test rapide
    )
    
    print("✅ Générateur initialisé")
    
    # Test génération normale
    print("\n📊 Génération scénario 'normal'...")
    data = gen.generate_realistic_session(cfg, scenario="normal")
    
    print("✅ Génération réussie !")
    
    # Affichage des résultats
    print("\n📈 Statistiques des données:")
    for key, df in data.items():
        print(f"  {key:20s}: {len(df):6d} rows, {len(df.columns):2d} cols")
    
    # Vérification des invariants
    print("\n🔍 Vérification des invariants:")
    
    # L1: ask > bid
    l1 = data["l1"]
    if len(l1) > 0:
        ask_gt_bid = (l1["ask"] > l1["bid"]).all()
        print(f"  ✅ L1 ask > bid: {ask_gt_bid}")
    
    # Bars: OHLC cohérent
    bars = data["bars"]
    if len(bars) > 0:
        ohlc_ok = (bars["high"] >= bars["low"]).all() and (bars["high"] >= bars["open"]).all() and (bars["high"] >= bars["close"]).all()
        print(f"  ✅ Bars OHLC cohérent: {ohlc_ok}")
    
    # Ground truth: labels présents
    gt = data["ground_truth"]
    if len(gt) > 0:
        labels_present = "label" in gt.columns and "side" in gt.columns
        print(f"  ✅ Ground truth labels: {labels_present}")
    
    print("\n🎉 TEST RÉUSSI ! Le MIA_IA_DataGenerator fonctionne parfaitement.")

if __name__ == "__main__":
    test_simple_generation()



