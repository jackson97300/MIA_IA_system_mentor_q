#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtest MIA_IA Final - Version fonctionnelle
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
from core.mia_data_generator import MIA_IA_DataGenerator, GenConfig

def run_mia_backtest():
    """Backtest MIA_IA complet et fonctionnel"""
    print("🚀 BACKTEST MIA_IA FINAL")
    print("=" * 50)
    
    # 1. Génération des données
    print("📊 Génération des données...")
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
    
    # 2. Analyse des signaux
    print("\n📡 Analyse des signaux...")
    bars = data["bars"]
    leadership = data["leadership_features"]
    context = data["context"]
    
    # Fusion des données
    merged = bars.merge(leadership, on=["ts", "symbol"], how="left")
    
    # Génération de signaux
    signals = []
    
    for _, row in merged.iterrows():
        signal = None
        
        # Signal 1: Leadership fort
        if row["leadership_strength"] > 0.7:
            signal = {
                "timestamp": row["ts"],
                "symbol": row["symbol"],
                "side": "BUY",
                "reason": "leadership_strong",
                "confidence": row["leadership_strength"],
                "price": row["close"]
            }
        
        # Signal 2: Confluence + Volume imbalance
        elif row["confluence_score"] > 0.6 and row["volume_imbalance"] > 0.3:
            signal = {
                "timestamp": row["ts"],
                "symbol": row["symbol"],
                "side": "BUY",
                "reason": "confluence_volume",
                "confidence": row["confluence_score"],
                "price": row["close"]
            }
        
        # Signal 3: Delta divergence
        elif abs(row["delta_divergence"]) > 0.1:
            side = "BUY" if row["delta_divergence"] > 0 else "SELL"
            signal = {
                "timestamp": row["ts"],
                "symbol": row["symbol"],
                "side": side,
                "reason": "delta_divergence",
                "confidence": abs(row["delta_divergence"]),
                "price": row["close"]
            }
        
        if signal:
            signals.append(signal)
    
    print(f"✅ {len(signals)} signaux générés")
    
    # 3. Simulation de trading
    print("\n💰 Simulation de trading...")
    initial_capital = 100000
    capital = initial_capital
    positions = {"ES": 0, "NQ": 0}
    trades = []
    
    for signal in signals[:20]:  # Limiter à 20 trades
        symbol = signal["symbol"]
        side = signal["side"]
        price = signal["price"]
        
        # Calcul de la taille de position (2% du capital)
        position_size = int(capital * 0.02 / price)
        
        if position_size > 0:
            # Exécution du trade
            if side == "BUY":
                if positions[symbol] < 0:  # Fermer position short
                    pnl = abs(positions[symbol]) * price * 0.1
                    capital += pnl
                    trades.append({
                        "timestamp": signal["timestamp"],
                        "symbol": symbol,
                        "action": "CLOSE_SHORT",
                        "price": price,
                        "size": abs(positions[symbol]),
                        "pnl": pnl
                    })
                
                # Ouvrir position long
                positions[symbol] += position_size
                capital -= position_size * price * 0.1
                trades.append({
                    "timestamp": signal["timestamp"],
                    "symbol": symbol,
                    "action": "OPEN_LONG",
                    "price": price,
                    "size": position_size,
                    "reason": signal["reason"]
                })
            
            elif side == "SELL":
                if positions[symbol] > 0:  # Fermer position long
                    pnl = positions[symbol] * price * 0.1
                    capital += pnl
                    trades.append({
                        "timestamp": signal["timestamp"],
                        "symbol": symbol,
                        "action": "CLOSE_LONG",
                        "price": price,
                        "size": positions[symbol],
                        "pnl": pnl
                    })
                
                # Ouvrir position short
                positions[symbol] -= position_size
                capital += position_size * price * 0.1
                trades.append({
                    "timestamp": signal["timestamp"],
                    "symbol": symbol,
                    "action": "OPEN_SHORT",
                    "price": price,
                    "size": position_size,
                    "reason": signal["reason"]
                })
    
    print(f"✅ {len(trades)} trades exécutés")
    
    # 4. Calcul des résultats
    print("\n📊 Calcul des résultats...")
    
    # P&L final
    final_equity = capital
    total_pnl = final_equity - initial_capital
    pnl_percentage = (total_pnl / initial_capital) * 100
    
    # Analyse des trades
    trades_df = pd.DataFrame(trades)
    total_trades = len(trades_df)
    closing_trades = trades_df[trades_df["action"].str.contains("CLOSE")]
    winning_trades = len(closing_trades[closing_trades["pnl"] > 0]) if not closing_trades.empty else 0
    
    # Analyse des signaux
    signal_df = pd.DataFrame(signals)
    
    # 5. Affichage des résultats
    print("\n" + "="*60)
    print("📊 RÉSULTATS DU BACKTEST MIA_IA")
    print("="*60)
    
    print(f"💰 Capital initial: ${initial_capital:,.2f}")
    print(f"💰 Capital final: ${final_equity:,.2f}")
    print(f"📈 P&L total: ${total_pnl:,.2f} ({pnl_percentage:+.2f}%)")
    print(f"📊 Nombre de trades: {total_trades}")
    print(f"✅ Trades gagnants: {winning_trades}")
    print(f"🎯 Taux de réussite: {(winning_trades / len(closing_trades) * 100) if len(closing_trades) > 0 else 0:.1f}%")
    
    # Positions finales
    print(f"\n📋 Positions finales:")
    for symbol, pos in positions.items():
        if pos != 0:
            print(f"  {symbol}: {pos:+d} contrats")
    
    # Analyse des signaux
    if not signal_df.empty:
        print(f"\n📡 Analyse des signaux:")
        print(f"  Total signaux: {len(signals)}")
        print(f"  Signaux BUY: {len(signal_df[signal_df['side'] == 'BUY'])}")
        print(f"  Signaux SELL: {len(signal_df[signal_df['side'] == 'SELL'])}")
        
        # Top raisons
        reason_counts = signal_df["reason"].value_counts().head(3)
        print(f"\n🎯 Top raisons de signaux:")
        for reason, count in reason_counts.items():
            print(f"  {reason}: {count}")
    
    print("\n🎉 BACKTEST TERMINÉ AVEC SUCCÈS !")

if __name__ == "__main__":
    run_mia_backtest()



