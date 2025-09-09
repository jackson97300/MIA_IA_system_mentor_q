#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtest MIA_IA Robuste et Complet
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
from core.mia_data_generator import MIA_IA_DataGenerator, GenConfig
from typing import Dict, List, Optional, Type, Union

class MIA_IA_Backtester:
    """Backtester robuste pour les stratégies MIA_IA"""
    
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {"ES": 0, "NQ": 0}
        self.trades = []
        self.equity_curve = []
        self.current_prices = {"ES": 0.0, "NQ": 0.0}
        
    def reset(self):
        """Reset le backtester"""
        self.capital = self.initial_capital
        self.positions = {"ES": 0, "NQ": 0}
        self.trades = []
        self.equity_curve = []
        self.current_prices = {"ES": 0.0, "NQ": 0.0}
    
    def calculate_position_size(self, capital: float, risk_per_trade: float = 0.02) -> int:
        """Calcule la taille de position basée sur le risque"""
        return max(1, int(capital * risk_per_trade / 1000))  # Minimum 1 contrat
    
    def execute_trade(self, symbol: str, side: str, price: float, size: int, timestamp: int, reason: str = ""):
        """Exécute un trade avec gestion robuste"""
        if size <= 0:
            return
            
        trade_info = {
            "timestamp": timestamp,
            "symbol": symbol,
            "side": side,
            "price": price,
            "size": size,
            "reason": reason,
            "capital_before": self.capital,
            "positions_before": self.positions.copy()
        }
        
        # Mise à jour du prix actuel
        self.current_prices[symbol] = price
        
        # Gestion des positions
        if side == "BUY":
            if self.positions[symbol] < 0:  # Fermer position short
                pnl = abs(self.positions[symbol]) * price * 0.1
                self.capital += pnl
                trade_info["action"] = "CLOSE_SHORT"
                trade_info["pnl"] = pnl
            
            # Ouvrir position long
            self.positions[symbol] += size
            self.capital -= size * price * 0.1
            trade_info["action"] = "OPEN_LONG" if "action" not in trade_info else "CLOSE_SHORT_AND_OPEN_LONG"
            
        elif side == "SELL":
            if self.positions[symbol] > 0:  # Fermer position long
                pnl = self.positions[symbol] * price * 0.1
                self.capital += pnl
                trade_info["action"] = "CLOSE_LONG"
                trade_info["pnl"] = pnl
            
            # Ouvrir position short
            self.positions[symbol] -= size
            self.capital += size * price * 0.1
            trade_info["action"] = "OPEN_SHORT" if "action" not in trade_info else "CLOSE_LONG_AND_OPEN_SHORT"
        
        trade_info["capital_after"] = self.capital
        trade_info["positions_after"] = self.positions.copy()
        
        self.trades.append(trade_info)
    
    def calculate_equity(self) -> float:
        """Calcule l'équité actuelle"""
        equity = self.capital
        for symbol, position in self.positions.items():
            if position != 0 and self.current_prices[symbol] > 0:
                equity += position * self.current_prices[symbol] * 0.1
        return equity

class MIA_IA_Strategy:
    """Stratégie de trading MIA_IA robuste"""
    
    def __init__(self):
        self.name = "MIA_IA_Leadership_Strategy"
        self.signal_count = 0
        
    def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Génère des signaux de trading basés sur les données MIA_IA"""
        signals = []
        
        try:
            # Fusionner les données par timestamp
            bars = data["bars"].copy()
            leadership = data["leadership_features"].copy()
            
            # Jointure des données avec gestion d'erreurs
            merged = bars.merge(leadership, on=["ts", "symbol"], how="left")
            
            # Limiter le nombre de lignes pour éviter les boucles infinies
            max_rows = min(1000, len(merged))
            merged = merged.head(max_rows)
            
            print(f"📊 Analyse de {len(merged)} barres...")
            
            for idx, row in merged.iterrows():
                if self.signal_count >= 50:  # Limite de sécurité
                    break
                    
                signal = self._analyze_single_bar(row, data["context"])
                if signal:
                    signals.append(signal)
                    self.signal_count += 1
                    
                # Progress indicator
                if idx % 100 == 0:
                    print(f"  Progression: {idx}/{len(merged)} barres analysées")
            
        except Exception as e:
            print(f"❌ Erreur génération signaux: {e}")
            
        return signals
    
    def _analyze_single_bar(self, row: pd.Series, context: pd.DataFrame) -> Optional[Dict]:
        """Analyse une barre individuelle pour générer un signal"""
        try:
            # Récupérer le contexte options
            ctx_row = context[context["ts"] == row["ts"]]
            if ctx_row.empty:
                return None
            
            ctx = ctx_row.iloc[0]
            
            # Critères de signal avec seuils robustes
            signal = None
            
            # 1. Signal basé sur leadership strength
            if row["leadership_strength"] > 0.7:
                signal = {
                    "timestamp": row["ts"],
                    "symbol": row["symbol"],
                    "side": "BUY",
                    "confidence": row["leadership_strength"],
                    "reason": "NQ_leadership_strong",
                    "price": row["close"]
                }
            
            # 2. Signal basé sur confluence
            elif row["confluence_score"] > 0.6:
                if row["volume_imbalance"] > 0.3:  # Imbalance haussier
                    signal = {
                        "timestamp": row["ts"],
                        "symbol": row["symbol"],
                        "side": "BUY",
                        "confidence": row["confluence_score"],
                        "reason": "confluence_volume_imbalance",
                        "price": row["close"]
                    }
                elif row["volume_imbalance"] < -0.3:  # Imbalance baissier
                    signal = {
                        "timestamp": row["ts"],
                        "symbol": row["symbol"],
                        "side": "SELL",
                        "confidence": row["confluence_score"],
                        "reason": "confluence_volume_imbalance",
                        "price": row["close"]
                    }
            
            # 3. Signal basé sur options context
            elif ctx["put_call_ratio"] < 0.8 and row["options_flow_bias"] > 0.2:
                signal = {
                    "timestamp": row["ts"],
                    "symbol": row["symbol"],
                    "side": "BUY",
                    "confidence": abs(row["options_flow_bias"]),
                    "reason": "options_flow_bullish",
                    "price": row["close"]
                }
            elif ctx["put_call_ratio"] > 1.2 and row["options_flow_bias"] < -0.2:
                signal = {
                    "timestamp": row["ts"],
                    "symbol": row["symbol"],
                    "side": "SELL",
                    "confidence": abs(row["options_flow_bias"]),
                    "reason": "options_flow_bearish",
                    "price": row["close"]
                }
            
            # 4. Signal basé sur delta divergence
            elif abs(row["delta_divergence"]) > 0.1:
                side = "BUY" if row["delta_divergence"] > 0 else "SELL"
                signal = {
                    "timestamp": row["ts"],
                    "symbol": row["symbol"],
                    "side": side,
                    "confidence": abs(row["delta_divergence"]),
                    "reason": "delta_divergence",
                    "price": row["close"]
                }
            
            return signal
            
        except Exception as e:
            print(f"❌ Erreur analyse barre: {e}")
            return None

def run_backtest_robuste(
    data: Dict[str, pd.DataFrame],
    strategy: Union[Type[MIA_IA_Strategy], MIA_IA_Strategy],
    initial_capital: float = 100000.0
) -> Dict:
    """Exécute un backtest robuste et complet"""
    
    print("🚀 LANCEMENT DU BACKTEST MIA_IA ROBUSTE")
    print("=" * 50)
    
    try:
        # Initialisation
        backtester = MIA_IA_Backtester(initial_capital)
        
        # ⬇️ nouvelle logique: classe → on instancie, instance → on la garde
        strategy_instance = strategy() if isinstance(strategy, type) else strategy
        
        # Génération des signaux
        print("📊 Génération des signaux...")
        signals = strategy_instance.generate_signals(data)
        print(f"✅ {len(signals)} signaux générés")
        
        if not signals:
            print("⚠️ Aucun signal généré - backtest terminé")
            return {
                "backtester": backtester,
                "signals": signals,
                "performance": {"error": "Aucun signal généré"}
            }
        
        # Exécution des trades
        print("💰 Exécution des trades...")
        bars = data["bars"].sort_values("ts")
        
        trade_count = 0
        max_trades = 30  # Limite de sécurité
        
        for signal in signals:
            if trade_count >= max_trades:
                print(f"⚠️ Limite de {max_trades} trades atteinte")
                break
                
            # Trouver le prix d'exécution
            bar = bars[(bars["ts"] == signal["timestamp"]) & (bars["symbol"] == signal["symbol"])]
            if not bar.empty:
                price = bar.iloc[0]["close"]
                size = backtester.calculate_position_size(backtester.capital)
                
                if size > 0:
                    backtester.execute_trade(
                        signal["symbol"],
                        signal["side"],
                        price,
                        size,
                        signal["timestamp"],
                        signal["reason"]
                    )
                    trade_count += 1
                    
                    # Progress indicator
                    if trade_count % 5 == 0:
                        print(f"  Trades exécutés: {trade_count}")
        
        print(f"✅ {trade_count} trades exécutés")
        
        # Calcul des métriques de performance
        print("📈 Calcul des métriques...")
        performance = calculate_performance_metrics_robuste(backtester, data)
        
        return {
            "backtester": backtester,
            "signals": signals,
            "performance": performance
        }
        
    except Exception as e:
        print(f"❌ Erreur backtest: {e}")
        import traceback
        traceback.print_exc()
        return {
            "backtester": None,
            "signals": [],
            "performance": {"error": str(e)}
        }

def calculate_performance_metrics_robuste(backtester: MIA_IA_Backtester, data: Dict[str, pd.DataFrame]) -> Dict:
    """Calcule les métriques de performance robustes"""
    
    try:
        if not backtester.trades:
            return {"error": "Aucun trade exécuté"}
        
        # Convertir les trades en DataFrame
        trades_df = pd.DataFrame(backtester.trades)
        
        # Métriques de base
        total_trades = len(trades_df)
        closing_trades = trades_df[trades_df["action"].str.contains("CLOSE")]
        winning_trades = len(closing_trades[closing_trades.get("pnl", 0) > 0]) if not closing_trades.empty else 0
        
        # Calcul du P&L
        final_equity = backtester.calculate_equity()
        total_pnl = final_equity - backtester.initial_capital
        pnl_percentage = (total_pnl / backtester.initial_capital) * 100
        
        # Calcul du drawdown
        equity_curve = []
        current_equity = backtester.initial_capital
        
        for _, trade in trades_df.iterrows():
            if "OPEN" in trade["action"]:
                current_equity -= trade["size"] * trade["price"] * 0.1
            elif "CLOSE" in trade["action"]:
                current_equity += trade.get("pnl", 0)
            equity_curve.append(current_equity)
        
        if equity_curve:
            max_equity = max(equity_curve)
            min_equity = min(equity_curve)
            max_drawdown = ((max_equity - min_equity) / max_equity) * 100 if max_equity > 0 else 0
        else:
            max_drawdown = 0
        
        return {
            "initial_capital": backtester.initial_capital,
            "final_equity": final_equity,
            "total_pnl": total_pnl,
            "pnl_percentage": pnl_percentage,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "win_rate": (winning_trades / len(closing_trades) * 100) if len(closing_trades) > 0 else 0,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": calculate_sharpe_ratio_robuste(equity_curve) if equity_curve else 0
        }
        
    except Exception as e:
        print(f"❌ Erreur calcul métriques: {e}")
        return {"error": f"Erreur calcul métriques: {e}"}

def calculate_sharpe_ratio_robuste(equity_curve: List[float], risk_free_rate: float = 0.02) -> float:
    """Calcule le ratio de Sharpe de manière robuste"""
    try:
        if len(equity_curve) < 2:
            return 0
        
        returns = np.diff(equity_curve) / equity_curve[:-1]
        excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
        
        if len(excess_returns) == 0 or np.std(excess_returns) == 0:
            return 0
        
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        
    except Exception as e:
        print(f"❌ Erreur calcul Sharpe: {e}")
        return 0

def print_backtest_results_robuste(results: Dict):
    """Affiche les résultats du backtest de manière robuste"""
    
    print("\n" + "="*60)
    print("📊 RÉSULTATS DU BACKTEST MIA_IA ROBUSTE")
    print("="*60)
    
    performance = results["performance"]
    
    if "error" in performance:
        print(f"❌ {performance['error']}")
        return
    
    print(f"💰 Capital initial: ${performance['initial_capital']:,.2f}")
    print(f"💰 Capital final: ${performance['final_equity']:,.2f}")
    print(f"📈 P&L total: ${performance['total_pnl']:,.2f} ({performance['pnl_percentage']:+.2f}%)")
    print(f"📊 Nombre de trades: {performance['total_trades']}")
    print(f"✅ Trades gagnants: {performance['winning_trades']}")
    print(f"🎯 Taux de réussite: {performance['win_rate']:.1f}%")
    print(f"📉 Drawdown maximum: {performance['max_drawdown']:.2f}%")
    print(f"📊 Ratio de Sharpe: {performance['sharpe_ratio']:.2f}")
    
    # Analyse des signaux
    signals = results["signals"]
    if signals:
        signal_df = pd.DataFrame(signals)
        print(f"\n📡 Analyse des signaux:")
        print(f"  Total signaux: {len(signals)}")
        print(f"  Signaux BUY: {len(signal_df[signal_df['side'] == 'BUY'])}")
        print(f"  Signaux SELL: {len(signal_df[signal_df['side'] == 'SELL'])}")
        
        # Top raisons de signaux
        reason_counts = signal_df["reason"].value_counts().head(5)
        print(f"\n🎯 Top raisons de signaux:")
        for reason, count in reason_counts.items():
            print(f"  {reason}: {count}")

def main():
    """Fonction principale de backtesting robuste"""
    
    print("🧪 BACKTESTING MIA_IA ROBUSTE ET COMPLET")
    print("="*60)
    
    try:
        # Génération de données de test
        print("📊 Génération de données de test...")
        gen = MIA_IA_DataGenerator(seed=42)
        cfg = GenConfig(
            start=datetime(2025, 8, 21, 13, 30, tzinfo=timezone.utc),
            minutes=90  # 1h30 de données
        )
        
        data = gen.generate_realistic_session(
            cfg,
            scenario="confluence_breakout",
            leadership="NQ_leads",
            strength=0.18
        )
        
        print("✅ Données générées !")
        
        # Lancement du backtest
        strategy = MIA_IA_Strategy()
        results = run_backtest_robuste(data, strategy, initial_capital=100000.0)
        
        # Affichage des résultats
        print_backtest_results_robuste(results)
        
        # Vérification finale du statut
        performance = results.get("performance", {})
        if "error" in performance:
            print("\n⚠️ BACKTEST TERMINÉ AVEC ERREURS.")
        else:
            print("\n🎉 BACKTEST ROBUSTE TERMINÉ AVEC SUCCÈS !")
        
    except Exception as e:
        print(f"❌ Erreur principale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
