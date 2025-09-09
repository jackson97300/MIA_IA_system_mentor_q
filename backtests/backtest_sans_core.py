#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtest MIA_IA sans core module - Contournement du problème
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour éviter l'import du core
sys.path.insert(0, str(Path(__file__).parent))

# Import direct du générateur sans passer par le core
try:
    from core.mia_data_generator import MIA_IA_DataGenerator, GenConfig
    print("✅ MIA_IA_DataGenerator importé directement")
except Exception as e:
    print(f"❌ Erreur import générateur: {e}")
    sys.exit(1)

def run_backtest_simple():
    """Backtest simple sans core module"""
    print("🚀 BACKTEST MIA_IA SANS CORE MODULE")
    print("=" * 50)
    
    try:
        # 1. Génération des données
        print("📊 Génération des données...")
        gen = MIA_IA_DataGenerator(seed=42)
        cfg = GenConfig(
            start=datetime(2025, 8, 21, 13, 30, tzinfo=timezone.utc),
            minutes=60
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
        
        # Fusion des données
        merged = bars.merge(leadership, on=["ts", "symbol"], how="left")
        print(f"📊 {len(merged)} barres analysées")
        
        # Génération de signaux
        signals = []
        for idx, row in merged.head(500).iterrows():  # Limite à 500 barres
            # Signal leadership
            if row["leadership_strength"] > 0.7:
                signals.append({
                    "timestamp": row["ts"],
                    "symbol": row["symbol"],
                    "side": "BUY",
                    "reason": "leadership_strong",
                    "confidence": row["leadership_strength"],
                    "price": row["close"]
                })
            
            # Signal confluence
            elif row["confluence_score"] > 0.6 and row["volume_imbalance"] > 0.3:
                signals.append({
                    "timestamp": row["ts"],
                    "symbol": row["symbol"],
                    "side": "BUY",
                    "reason": "confluence_volume",
                    "confidence": row["confluence_score"],
                    "price": row["close"]
                })
        
        print(f"✅ {len(signals)} signaux générés")
        
        # 3. Simulation de trading
        print("\n💰 Simulation de trading...")
        initial_capital = 100000
        capital = initial_capital
        positions = {"ES": 0, "NQ": 0}
        trades = []
        
        for signal in signals[:20]:  # Limite à 20 trades
            symbol = signal["symbol"]
            side = signal["side"]
            price = signal["price"]
            
            # Calcul de la taille de position
            position_size = max(1, int(capital * 0.02 / price))
            
            # Exécution du trade
            if side == "BUY":
                if positions[symbol] < 0:  # Fermer position short
                    pnl = abs(positions[symbol]) * price * 0.1
                    capital += pnl
                    trades.append({
                        "action": "CLOSE_SHORT",
                        "symbol": symbol,
                        "price": price,
                        "pnl": pnl
                    })
                
                # Ouvrir position long
                positions[symbol] += position_size
                capital -= position_size * price * 0.1
                trades.append({
                    "action": "OPEN_LONG",
                    "symbol": symbol,
                    "price": price,
                    "size": position_size,
                    "reason": signal["reason"]
                })
            
            elif side == "SELL":
                if positions[symbol] > 0:  # Fermer position long
                    pnl = positions[symbol] * price * 0.1
                    capital += pnl
                    trades.append({
                        "action": "CLOSE_LONG",
                        "symbol": symbol,
                        "price": price,
                        "pnl": pnl
                    })
                
                # Ouvrir position short
                positions[symbol] -= position_size
                capital += position_size * price * 0.1
                trades.append({
                    "action": "OPEN_SHORT",
                    "symbol": symbol,
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
        closing_trades = [t for t in trades if "CLOSE" in t["action"]]
        winning_trades = len([t for t in closing_trades if t.get("pnl", 0) > 0])
        
        # 5. Affichage des résultats
        print("\n" + "="*60)
        print("📊 RÉSULTATS DU BACKTEST MIA_IA")
        print("="*60)
        
        print(f"💰 Capital initial: ${initial_capital:,.2f}")
        print(f"💰 Capital final: ${final_equity:,.2f}")
        print(f"📈 P&L total: ${total_pnl:,.2f} ({pnl_percentage:+.2f}%)")
        print(f"📊 Nombre de trades: {len(trades)}")
        print(f"✅ Trades gagnants: {winning_trades}")
        print(f"🎯 Taux de réussite: {(winning_trades / len(closing_trades) * 100) if closing_trades else 0:.1f}%")
        
        # Positions finales
        print(f"\n📋 Positions finales:")
        for symbol, pos in positions.items():
            if pos != 0:
                print(f"  {symbol}: {pos:+d} contrats")
        
        # Analyse des signaux
        signal_df = pd.DataFrame(signals)
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
        
    except Exception as e:
        print(f"❌ Erreur backtest: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_backtest_simple()



