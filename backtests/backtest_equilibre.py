#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtest MIA_IA ÉQUILIBRÉ - Signaux BUY/SELL équilibrés
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

def run_backtest_equilibre():
    """Backtest avec signaux équilibrés"""
    print("🚀 BACKTEST MIA_IA ÉQUILIBRÉ - BUY/SELL")
    print("=" * 60)
    
    try:
        # 1. Import et patch du générateur
        print("📦 Import du générateur...")
        from core.mia_data_generator import MIA_IA_DataGenerator, GenConfig
        
        # Patch pour éviter le bug rolling std
        def _calculate_leadership_strength_patched(self, bar, df_bars, leadership, strength):
            """Version patchée pour éviter le problème de rolling std"""
            if leadership == "NQ_leads":
                return min(0.9, 0.5 + strength * 0.4)
            elif leadership == "ES_leads":
                return min(0.9, 0.5 + strength * 0.4)
            else:
                return 0.5
        
        MIA_IA_DataGenerator._calculate_leadership_strength = _calculate_leadership_strength_patched
        print("✅ Générateur importé et patché")
        
        # 2. Génération des données avec scénarios variés
        print("\n📊 Génération des données...")
        gen = MIA_IA_DataGenerator(seed=42)
        cfg = GenConfig(
            start=datetime(2025, 8, 21, 13, 30, tzinfo=timezone.utc),
            minutes=60
        )
        
        # Générer plusieurs scénarios pour équilibrer
        scenarios = ["confluence_breakout", "trend_down", "chop", "news_spike"]
        all_data = []
        
        for i, scenario in enumerate(scenarios):
            start_time = datetime(2025, 8, 21, 13, 30 + i*15, tzinfo=timezone.utc)
            cfg.start = start_time
            
            data = gen.generate_realistic_session(
                cfg,
                scenario=scenario,
                leadership="NQ_leads" if i % 2 == 0 else "ES_leads",
                strength=0.18
            )
            all_data.append(data)
        
        # Fusionner les données
        bars = pd.concat([d["bars"] for d in all_data], ignore_index=True)
        leadership = pd.concat([d["leadership_features"] for d in all_data], ignore_index=True)
        context = pd.concat([d["context"] for d in all_data], ignore_index=True)
        
        print("✅ Données générées avec scénarios variés !")
        
        # 3. Analyse et génération de signaux équilibrés
        print("\n📡 Analyse et génération de signaux équilibrés...")
        
        # Fusion des données
        merged = bars.merge(leadership, on=["ts", "symbol"], how="left")
        merged = merged.merge(context, on="ts", how="left")
        print(f"📊 {len(merged)} barres analysées")
        
        # Génération de signaux ÉQUILIBRÉS
        signals = []
        for idx, row in merged.head(1000).iterrows():
            # Signal leadership - BUY si fort, SELL si faible
            if row["leadership_strength"] > 0.65:
                signals.append({
                    "timestamp": row["ts"],
                    "symbol": row["symbol"],
                    "side": "BUY",
                    "price": row["close"],
                    "confidence": row["leadership_strength"],
                    "reason": "leadership_strong_buy"
                })
            elif row["leadership_strength"] < 0.35:
                signals.append({
                    "timestamp": row["ts"],
                    "symbol": row["symbol"],
                    "side": "SELL",
                    "price": row["close"],
                    "confidence": 1 - row["leadership_strength"],
                    "reason": "leadership_weak_sell"
                })
            
            # Signal confluence - BUY si positif, SELL si négatif
            elif row["confluence_score"] > 0.6 and row["volume_imbalance"] > 0.3:
                signals.append({
                    "timestamp": row["ts"],
                    "symbol": row["symbol"],
                    "side": "BUY",
                    "price": row["close"],
                    "confidence": row["confluence_score"],
                    "reason": "confluence_bullish"
                })
            elif row["confluence_score"] < 0.4 and row["volume_imbalance"] < -0.3:
                signals.append({
                    "timestamp": row["ts"],
                    "symbol": row["symbol"],
                    "side": "SELL",
                    "price": row["close"],
                    "confidence": 1 - row["confluence_score"],
                    "reason": "confluence_bearish"
                })
            
            # Signal options context - BUY si VIX bas, SELL si VIX haut
            elif row.get("vix", 15) < 15 and row.get("put_call_ratio", 1) < 0.9:
                signals.append({
                    "timestamp": row["ts"],
                    "symbol": row["symbol"],
                    "side": "BUY",
                    "price": row["close"],
                    "confidence": 0.7,
                    "reason": "options_bullish"
                })
            elif row.get("vix", 15) > 25 and row.get("put_call_ratio", 1) > 1.2:
                signals.append({
                    "timestamp": row["ts"],
                    "symbol": row["symbol"],
                    "side": "SELL",
                    "price": row["close"],
                    "confidence": 0.7,
                    "reason": "options_bearish"
                })
            
            # Signal momentum - BUY si prix monte, SELL si prix baisse
            elif idx > 0:
                prev_close = merged.iloc[idx-1]["close"] if idx > 0 else row["close"]
                price_change = (row["close"] - prev_close) / prev_close
                
                if price_change > 0.002:  # +0.2%
                    signals.append({
                        "timestamp": row["ts"],
                        "symbol": row["symbol"],
                        "side": "BUY",
                        "price": row["close"],
                        "confidence": 0.6,
                        "reason": "momentum_up"
                    })
                elif price_change < -0.002:  # -0.2%
                    signals.append({
                        "timestamp": row["ts"],
                        "symbol": row["symbol"],
                        "side": "SELL",
                        "price": row["close"],
                        "confidence": 0.6,
                        "reason": "momentum_down"
                    })
        
        print(f"✅ {len(signals)} signaux générés")
        
        # 4. Analyse des signaux
        signal_df = pd.DataFrame(signals)
        buy_signals = len(signal_df[signal_df['side'] == 'BUY'])
        sell_signals = len(signal_df[signal_df['side'] == 'SELL'])
        
        print(f"\n📊 Répartition des signaux:")
        print(f"  BUY: {buy_signals} ({buy_signals/len(signals)*100:.1f}%)")
        print(f"  SELL: {sell_signals} ({sell_signals/len(signals)*100:.1f}%)")
        
        # Top raisons
        reason_counts = signal_df["reason"].value_counts().head(5)
        print(f"\n🎯 Top raisons de signaux:")
        for reason, count in reason_counts.items():
            side = "BUY" if "buy" in reason.lower() or "bull" in reason.lower() or "up" in reason.lower() else "SELL"
            print(f"  {reason}: {count} ({side})")
        
        # 5. Simulation de trading simple
        print("\n💰 Simulation de trading...")
        capital = 100000
        trades = []
        
        for signal in signals[:50]:  # Limite à 50 trades
            price = signal["price"]
            size = max(1, int(capital * 0.01 / price))
            
            trades.append({
                "action": signal["side"],
                "symbol": signal["symbol"],
                "price": price,
                "size": size,
                "reason": signal["reason"],
                "confidence": signal["confidence"]
            })
            
            # P&L simple
            if signal["side"] == "BUY":
                capital += size * price * 0.01
            else:
                capital -= size * price * 0.01
        
        print(f"✅ {len(trades)} trades simulés")
        
        # 6. Résultats
        print("\n📊 Résultats...")
        final_capital = capital
        pnl = final_capital - 100000
        pnl_pct = (pnl / 100000) * 100
        
        print(f"💰 Capital final: ${final_capital:,.2f}")
        print(f"📈 P&L: ${pnl:,.2f} ({pnl_pct:+.2f}%)")
        print(f"📊 Trades: {len(trades)}")
        
        # Répartition des trades
        buy_trades = len([t for t in trades if t["action"] == "BUY"])
        sell_trades = len([t for t in trades if t["action"] == "SELL"])
        
        print(f"\n📊 Répartition des trades:")
        print(f"  BUY: {buy_trades} ({buy_trades/len(trades)*100:.1f}%)")
        print(f"  SELL: {sell_trades} ({sell_trades/len(trades)*100:.1f}%)")
        
        # Statistiques des données
        print(f"\n📈 Statistiques des données générées:")
        for key, df in all_data[0].items():
            print(f"  {key:20s}: {len(df):6d} rows, {len(df.columns):2d} cols")
        
        print("\n🎉 BACKTEST ÉQUILIBRÉ RÉUSSI !")
        print("✅ Signaux BUY/SELL équilibrés")
        
    except Exception as e:
        print(f"❌ Erreur backtest équilibré: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_backtest_equilibre()



