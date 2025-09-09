#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtest simple MIA_IA - Version rapide
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
from core.mia_data_generator import MIA_IA_DataGenerator, GenConfig

def simple_backtest():
    """Backtest simple et rapide"""
    print("🚀 BACKTEST SIMPLE MIA_IA")
    print("=" * 40)
    
    # Génération de données
    print("📊 Génération données...")
    gen = MIA_IA_DataGenerator(seed=42)
    cfg = GenConfig(
        start=datetime(2025, 8, 21, 13, 30, tzinfo=timezone.utc),
        minutes=60  # 1 heure
    )
    
    data = gen.generate_realistic_session(
        cfg,
        scenario="confluence_breakout",
        leadership="NQ_leads",
        strength=0.18
    )
    
    print("✅ Données générées !")
    
    # Analyse des signaux
    print("\n📡 Analyse des signaux...")
    bars = data["bars"]
    leadership = data["leadership_features"]
    context = data["context"]
    
    # Fusion des données
    merged = bars.merge(leadership, on=["ts", "symbol"], how="left")
    
    # Génération de signaux simples
    signals = []
    
    for _, row in merged.iterrows():
        # Signal basé sur leadership
        if row["leadership_strength"] > 0.7:
            signals.append({
                "timestamp": row["ts"],
                "symbol": row["symbol"],
                "side": "BUY",
                "reason": "leadership_strong",
                "confidence": row["leadership_strength"]
            })
        
        # Signal basé sur confluence
        if row["confluence_score"] > 0.6 and row["volume_imbalance"] > 0.3:
            signals.append({
                "timestamp": row["ts"],
                "symbol": row["symbol"],
                "side": "BUY",
                "reason": "confluence_volume",
                "confidence": row["confluence_score"]
            })
    
    print(f"✅ {len(signals)} signaux générés")
    
    # Simulation de trading simple
    print("\n💰 Simulation trading...")
    initial_capital = 100000
    capital = initial_capital
    trades = []
    
    for signal in signals[:10]:  # Limiter à 10 trades pour la démo
        # Trouver le prix
        bar = bars[(bars["ts"] == signal["timestamp"]) & (bars["symbol"] == signal["symbol"])]
        if not bar.empty:
            price = bar.iloc[0]["close"]
            size = int(capital * 0.02 / price)  # 2% du capital
            
            if size > 0:
                trades.append({
                    "timestamp": signal["timestamp"],
                    "symbol": signal["symbol"],
                    "side": signal["side"],
                    "price": price,
                    "size": size,
                    "reason": signal["reason"]
                })
                
                # P&L simple
                if signal["side"] == "BUY":
                    capital += size * price * 0.01  # +1% approximatif
    
    print(f"✅ {len(trades)} trades exécutés")
    
    # Résultats
    print("\n📊 RÉSULTATS:")
    print(f"💰 Capital initial: ${initial_capital:,.2f}")
    print(f"💰 Capital final: ${capital:,.2f}")
    print(f"📈 P&L: ${capital - initial_capital:,.2f} ({(capital - initial_capital) / initial_capital * 100:+.2f}%)")
    print(f"📊 Nombre de trades: {len(trades)}")
    
    # Analyse des signaux
    if signals:
        signal_df = pd.DataFrame(signals)
        print(f"\n📡 Types de signaux:")
        reason_counts = signal_df["reason"].value_counts()
        for reason, count in reason_counts.items():
            print(f"  {reason}: {count}")
    
    print("\n🎉 BACKTEST TERMINÉ !")

if __name__ == "__main__":
    simple_backtest()



