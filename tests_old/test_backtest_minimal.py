#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test minimal du backtest MIA_IA
"""

print("🚀 TEST MINIMAL BACKTEST")
print("=" * 30)

try:
    print("📦 Import des modules...")
    import pandas as pd
    import numpy as np
    from datetime import datetime, timezone
    print("✅ Pandas et Numpy importés")
    
    print("📦 Import MIA_IA_DataGenerator...")
    from core.mia_data_generator import MIA_IA_DataGenerator, GenConfig
    print("✅ MIA_IA_DataGenerator importé")
    
    print("📊 Création du générateur...")
    gen = MIA_IA_DataGenerator(seed=42)
    print("✅ Générateur créé")
    
    print("⚙️ Configuration...")
    cfg = GenConfig(
        start=datetime(2025, 8, 21, 13, 30, tzinfo=timezone.utc),
        minutes=10  # 10 minutes seulement
    )
    print("✅ Configuration créée")
    
    print("📊 Génération des données...")
    data = gen.generate_realistic_session(
        cfg,
        scenario="normal",
        leadership="NQ_leads",
        strength=0.18
    )
    print("✅ Données générées !")
    
    print("📈 Statistiques des données:")
    for key, df in data.items():
        print(f"  {key}: {len(df)} rows, {len(df.columns)} cols")
    
    print("🎉 TEST RÉUSSI !")
    
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()



