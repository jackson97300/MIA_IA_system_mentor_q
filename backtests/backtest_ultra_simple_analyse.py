#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse ultra-simple des données MIA_IA - Pourquoi que des BUY ?
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

def analyse_donnees_mia():
    """Analyse simple des données pour comprendre le biais BUY"""
    print("🔍 ANALYSE ULTRA-SIMPLE - POURQUOI QUE DES BUY ?")
    print("=" * 60)
    
    try:
        # 1. Import direct du générateur (sans core)
        print("📦 Import direct du générateur...")
        from core.mia_data_generator import MIA_IA_DataGenerator, GenConfig
        print("✅ Générateur importé")
        
        # 2. Patch simple
        def _calculate_leadership_strength_simple(self, bar, df_bars, leadership, strength):
            """Version ultra-simple"""
            return 0.6  # Valeur fixe pour test
        
        MIA_IA_DataGenerator._calculate_leadership_strength = _calculate_leadership_strength_simple
        print("✅ Patch appliqué")
        
        # 3. Génération de données simples
        print("\n📊 Génération de données...")
        gen = MIA_IA_DataGenerator(seed=42)
        cfg = GenConfig(
            start=datetime(2025, 8, 21, 13, 30, tzinfo=timezone.utc),
            minutes=10  # 10 minutes seulement
        )
        
        data = gen.generate_realistic_session(
            cfg,
            scenario="normal",
            leadership="NQ_leads",
            strength=0.18
        )
        print("✅ Données générées !")
        
        # 4. Analyse des données brutes
        print("\n📈 ANALYSE DES DONNÉES BRUTES:")
        bars = data["bars"]
        leadership = data["leadership_features"]
        context = data["context"]
        
        print(f"📊 Bars: {len(bars)} lignes")
        print(f"📊 Leadership: {len(leadership)} lignes")
        print(f"📊 Context: {len(context)} lignes")
        
        # 5. Analyse des valeurs leadership
        print("\n🔍 ANALYSE LEADERSHIP:")
        print(f"  leadership_strength min: {leadership['leadership_strength'].min():.3f}")
        print(f"  leadership_strength max: {leadership['leadership_strength'].max():.3f}")
        print(f"  leadership_strength mean: {leadership['leadership_strength'].mean():.3f}")
        print(f"  leadership_strength std: {leadership['leadership_strength'].std():.3f}")
        
        # Distribution
        print(f"\n📊 Distribution leadership_strength:")
        bins = [0, 0.3, 0.5, 0.7, 0.9, 1.0]
        hist = pd.cut(leadership['leadership_strength'], bins=bins).value_counts().sort_index()
        for bin_name, count in hist.items():
            print(f"  {bin_name}: {count} ({count/len(leadership)*100:.1f}%)")
        
        # 6. Analyse confluence
        print("\n🔍 ANALYSE CONFLUENCE:")
        print(f"  confluence_score min: {leadership['confluence_score'].min():.3f}")
        print(f"  confluence_score max: {leadership['confluence_score'].max():.3f}")
        print(f"  confluence_score mean: {leadership['confluence_score'].mean():.3f}")
        print(f"  volume_imbalance min: {leadership['volume_imbalance'].min():.3f}")
        print(f"  volume_imbalance max: {leadership['volume_imbalance'].max():.3f}")
        print(f"  volume_imbalance mean: {leadership['volume_imbalance'].mean():.3f}")
        
        # 7. Analyse context options
        print("\n🔍 ANALYSE CONTEXT OPTIONS:")
        print(f"  VIX min: {context['vix'].min():.1f}")
        print(f"  VIX max: {context['vix'].max():.1f}")
        print(f"  VIX mean: {context['vix'].mean():.1f}")
        print(f"  put_call_ratio min: {context['put_call_ratio'].min():.3f}")
        print(f"  put_call_ratio max: {context['put_call_ratio'].max():.3f}")
        print(f"  put_call_ratio mean: {context['put_call_ratio'].mean():.3f}")
        
        # 8. Test des conditions de signaux
        print("\n🧪 TEST DES CONDITIONS DE SIGNAUX:")
        
        # Condition leadership originale
        strong_leadership = leadership[leadership['leadership_strength'] > 0.55]
        weak_leadership = leadership[leadership['leadership_strength'] < 0.35]
        print(f"  Leadership > 0.55: {len(strong_leadership)} ({len(strong_leadership)/len(leadership)*100:.1f}%)")
        print(f"  Leadership < 0.35: {len(weak_leadership)} ({len(weak_leadership)/len(leadership)*100:.1f}%)")
        
        # Condition confluence originale
        bullish_confluence = leadership[(leadership['confluence_score'] > 0.4) & (leadership['volume_imbalance'] > 0.2)]
        bearish_confluence = leadership[(leadership['confluence_score'] < 0.4) & (leadership['volume_imbalance'] < -0.2)]
        print(f"  Confluence bullish: {len(bullish_confluence)} ({len(bullish_confluence)/len(leadership)*100:.1f}%)")
        print(f"  Confluence bearish: {len(bearish_confluence)} ({len(bearish_confluence)/len(leadership)*100:.1f}%)")
        
        # Condition options originale
        bullish_options = context[(context['vix'] < 15) & (context['put_call_ratio'] < 0.9)]
        bearish_options = context[(context['vix'] > 25) & (context['put_call_ratio'] > 1.2)]
        print(f"  Options bullish: {len(bullish_options)} ({len(bullish_options)/len(context)*100:.1f}%)")
        print(f"  Options bearish: {len(bearish_options)} ({len(bearish_options)/len(context)*100:.1f}%)")
        
        # 9. Simulation de génération de signaux
        print("\n🎯 SIMULATION GÉNÉRATION SIGNAUX:")
        
        merged = bars.merge(leadership, on=["ts", "symbol"], how="left")
        merged = merged.merge(context, on="ts", how="left")
        
        signals_buy = []
        signals_sell = []
        
        for idx, row in merged.head(100).iterrows():
            # Test conditions BUY
            if row["leadership_strength"] > 0.55:
                signals_buy.append(f"leadership_strong_{row['leadership_strength']:.2f}")
            elif row["confluence_score"] > 0.4 and row["volume_imbalance"] > 0.2:
                signals_buy.append(f"confluence_bull_{row['confluence_score']:.2f}")
            elif row.get("vix", 15) < 15 and row.get("put_call_ratio", 1) < 0.9:
                signals_buy.append(f"options_bull_vix{row.get('vix', 15):.1f}")
            
            # Test conditions SELL
            if row["leadership_strength"] < 0.35:
                signals_sell.append(f"leadership_weak_{row['leadership_strength']:.2f}")
            elif row["confluence_score"] < 0.4 and row["volume_imbalance"] < -0.2:
                signals_sell.append(f"confluence_bear_{row['confluence_score']:.2f}")
            elif row.get("vix", 15) > 25 and row.get("put_call_ratio", 1) > 1.2:
                signals_sell.append(f"options_bear_vix{row.get('vix', 15):.1f}")
        
        print(f"  Signaux BUY générés: {len(signals_buy)}")
        print(f"  Signaux SELL générés: {len(signals_sell)}")
        
        if signals_buy:
            print(f"  Exemples BUY: {signals_buy[:3]}")
        if signals_sell:
            print(f"  Exemples SELL: {signals_sell[:3]}")
        
        # 10. Conclusion
        print("\n📋 CONCLUSION:")
        if len(signals_buy) > len(signals_sell) * 3:
            print("  ❌ PROBLÈME: Biais BUY important détecté")
            print("  💡 CAUSES POSSIBLES:")
            print("    - Seuils trop bas pour BUY")
            print("    - Seuils trop hauts pour SELL")
            print("    - Scénario 'normal' naturellement haussier")
            print("    - Données générées avec biais positif")
        else:
            print("  ✅ Signaux relativement équilibrés")
        
        print("\n🎉 ANALYSE TERMINÉE !")
        
    except Exception as e:
        print(f"❌ Erreur analyse: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyse_donnees_mia()



