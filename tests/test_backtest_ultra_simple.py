#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test ultra-simple du backtest MIA_IA
"""

print("🚀 TEST ULTRA-SIMPLE BACKTEST")
print("=" * 40)

try:
    print("📦 Import pandas...")
    import pandas as pd
    print("✅ Pandas importé")
    
    print("📦 Import numpy...")
    import numpy as np
    print("✅ Numpy importé")
    
    print("📦 Import datetime...")
    from datetime import datetime, timezone
    print("✅ Datetime importé")
    
    print("📦 Import MIA_IA_DataGenerator...")
    from core.mia_data_generator import MIA_IA_DataGenerator, GenConfig
    print("✅ MIA_IA_DataGenerator importé")
    
    print("📊 Création générateur...")
    gen = MIA_IA_DataGenerator(seed=42)
    print("✅ Générateur créé")
    
    print("⚙️ Configuration...")
    cfg = GenConfig(
        start=datetime(2025, 8, 21, 13, 30, tzinfo=timezone.utc),
        minutes=5  # 5 minutes seulement
    )
    print("✅ Configuration créée")
    
    print("📊 Génération données...")
    data = gen.generate_realistic_session(
        cfg,
        scenario="normal",
        leadership="NQ_leads",
        strength=0.18
    )
    print("✅ Données générées !")
    
    print("📈 Statistiques:")
    for key, df in data.items():
        print(f"  {key}: {len(df)} rows")
    
    print("🎉 TEST ULTRA-SIMPLE RÉUSSI !")
    
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()



