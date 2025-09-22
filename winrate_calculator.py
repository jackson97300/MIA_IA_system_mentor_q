#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CALCULATEUR DE WINRATE
======================
Calcule les winrates basés sur l'analyse des signaux de trading
"""

import json
import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

@dataclass
class WinrateAnalysis:
    """Analyse de winrate pour un scénario"""
    scenario: str
    total_signals: int
    winning_signals: int
    losing_signals: int
    winrate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    expected_value: float
    sharpe_ratio: float

class WinrateCalculator:
    """Calculateur de winrate basé sur les métriques de performance"""
    
    def __init__(self):
        # Données des scénarios avec métriques de performance
        self.scenarios_data = {
            "bullish": {
                "vwap_above": 52.7,      # % de temps au-dessus VWAP
                "vwap_below": 47.3,      # % de temps en-dessous VWAP
                "vwap_breakout": 48.5,   # % de cassures VWAP
                "volume_spike": 19.2,    # % de pics de volume
                "momentum_positive": 54.4, # % de momentum positif
                "momentum_negative": 8.4,  # % de momentum négatif
                "volatility_hourly": 1.21, # % volatilité horaire
                "max_drawdown": 0.46,    # % drawdown max
                "sharpe_ratio": 0.737,   # Ratio de Sharpe
                "trend_strength": 100.0, # Force de tendance
                "menthorq_stability": 0.991, # Stabilité MenthorQ
                "menthorq_trend": 2.95   # Tendance MenthorQ %
            },
            "bearish": {
                "vwap_above": 54.0,
                "vwap_below": 46.0,
                "vwap_breakout": 51.5,
                "volume_spike": 2.9,
                "momentum_positive": 20.9,
                "momentum_negative": 53.6,
                "volatility_hourly": 1.81,
                "max_drawdown": 21.61,
                "sharpe_ratio": -0.424,
                "trend_strength": 100.0,
                "menthorq_stability": 0.993,
                "menthorq_trend": -2.00
            },
            "sideways": {
                "vwap_above": 55.2,
                "vwap_below": 44.8,
                "vwap_breakout": 48.5,
                "volume_spike": 4.2,
                "momentum_positive": 18.0,
                "momentum_negative": 16.7,
                "volatility_hourly": 0.91,
                "max_drawdown": 2.40,
                "sharpe_ratio": 0.005,
                "trend_strength": 6.6,
                "menthorq_stability": 0.999,
                "menthorq_trend": -0.01
            },
            "volatile": {
                "vwap_above": 56.9,
                "vwap_below": 43.1,
                "vwap_breakout": 47.3,
                "volume_spike": 13.8,
                "momentum_positive": 37.7,
                "momentum_negative": 40.6,
                "volatility_hourly": 3.15,
                "max_drawdown": 5.47,
                "sharpe_ratio": 0.006,
                "trend_strength": 11.5,
                "menthorq_stability": 0.998,
                "menthorq_trend": 0.38
            },
            "breakout": {
                "vwap_above": 46.0,
                "vwap_below": 54.0,
                "vwap_breakout": 51.5,
                "volume_spike": 9.6,
                "momentum_positive": 59.0,
                "momentum_negative": 16.3,
                "volatility_hourly": 2.22,
                "max_drawdown": 1.59,
                "sharpe_ratio": 0.580,
                "trend_strength": 100.0,
                "menthorq_stability": 0.987,
                "menthorq_trend": 4.44
            },
            "reversal": {
                "vwap_above": 49.8,
                "vwap_below": 50.2,
                "vwap_breakout": 37.7,
                "volume_spike": 0.0,
                "momentum_positive": 33.1,
                "momentum_negative": 45.6,
                "volatility_hourly": 2.89,
                "max_drawdown": 14.27,
                "sharpe_ratio": -0.158,
                "trend_strength": 51.2,
                "menthorq_stability": 0.996,
                "menthorq_trend": -1.08
            }
        }
    
    def calculate_signal_winrate(self, scenario: str, signal_type: str) -> float:
        """Calcule le winrate pour un type de signal spécifique"""
        data = self.scenarios_data[scenario]
        
        if signal_type == "vwap_long":
            # Signal long : prix au-dessus VWAP + momentum positif
            vwap_success = data["vwap_above"] / 100
            momentum_success = data["momentum_positive"] / 100
            # Winrate = probabilité que les deux conditions soient remplies
            return vwap_success * momentum_success * 0.8  # Facteur de corrélation
        
        elif signal_type == "vwap_short":
            # Signal short : prix en-dessous VWAP + momentum négatif
            vwap_success = data["vwap_below"] / 100
            momentum_success = data["momentum_negative"] / 100
            return vwap_success * momentum_success * 0.8
        
        elif signal_type == "breakout_long":
            # Cassure haussière : breakout + momentum positif
            breakout_success = data["vwap_breakout"] / 100
            momentum_success = data["momentum_positive"] / 100
            return breakout_success * momentum_success * 0.7
        
        elif signal_type == "breakout_short":
            # Cassure baissière : breakout + momentum négatif
            breakout_success = data["vwap_breakout"] / 100
            momentum_success = data["momentum_negative"] / 100
            return breakout_success * momentum_success * 0.7
        
        elif signal_type == "volume_spike":
            # Pic de volume : volume élevé + momentum
            volume_success = data["volume_spike"] / 100
            momentum_success = max(data["momentum_positive"], data["momentum_negative"]) / 100
            return volume_success * momentum_success * 0.6
        
        elif signal_type == "menthorq_filtered":
            # Filtrage MenthorQ : stabilité élevée + tendance claire
            stability = data["menthorq_stability"]
            trend_strength = data["trend_strength"] / 100
            return stability * trend_strength * 0.9
        
        return 0.0
    
    def calculate_avg_win_loss(self, scenario: str) -> Tuple[float, float]:
        """Calcule le gain moyen et la perte moyenne"""
        data = self.scenarios_data[scenario]
        
        # Gain moyen basé sur la volatilité et le momentum positif
        avg_win = data["volatility_hourly"] * 2.0  # 2x la volatilité horaire
        
        # Perte moyenne basé sur le drawdown et la volatilité
        avg_loss = min(data["max_drawdown"], data["volatility_hourly"] * 1.5)
        
        # Ajustement basé sur le Sharpe ratio
        if data["sharpe_ratio"] > 0.5:
            avg_win *= 1.2  # Bonus pour bon Sharpe
            avg_loss *= 0.8  # Réduction des pertes
        elif data["sharpe_ratio"] < 0:
            avg_win *= 0.8  # Réduction des gains
            avg_loss *= 1.2  # Augmentation des pertes
        
        return avg_win, avg_loss
    
    def calculate_profit_factor(self, winrate: float, avg_win: float, avg_loss: float) -> float:
        """Calcule le profit factor"""
        if avg_loss == 0:
            return float('inf') if avg_win > 0 else 0.0
        
        return (winrate * avg_win) / ((1 - winrate) * avg_loss)
    
    def calculate_expected_value(self, winrate: float, avg_win: float, avg_loss: float) -> float:
        """Calcule la valeur attendue"""
        return (winrate * avg_win) - ((1 - winrate) * avg_loss)
    
    def analyze_scenario_winrate(self, scenario: str) -> WinrateAnalysis:
        """Analyse complète du winrate pour un scénario"""
        data = self.scenarios_data[scenario]
        
        # Calculer les winrates pour différents types de signaux
        signal_winrates = {
            "vwap_long": self.calculate_signal_winrate(scenario, "vwap_long"),
            "vwap_short": self.calculate_signal_winrate(scenario, "vwap_short"),
            "breakout_long": self.calculate_signal_winrate(scenario, "breakout_long"),
            "breakout_short": self.calculate_signal_winrate(scenario, "breakout_short"),
            "volume_spike": self.calculate_signal_winrate(scenario, "volume_spike"),
            "menthorq_filtered": self.calculate_signal_winrate(scenario, "menthorq_filtered")
        }
        
        # Winrate moyen pondéré
        weights = {
            "vwap_long": 0.25,
            "vwap_short": 0.25,
            "breakout_long": 0.20,
            "breakout_short": 0.15,
            "volume_spike": 0.10,
            "menthorq_filtered": 0.05
        }
        
        total_winrate = sum(signal_winrates[signal] * weights[signal] for signal in signal_winrates)
        
        # Calculer les gains/pertes moyens
        avg_win, avg_loss = self.calculate_avg_win_loss(scenario)
        
        # Calculer les métriques de performance
        profit_factor = self.calculate_profit_factor(total_winrate, avg_win, avg_loss)
        expected_value = self.calculate_expected_value(total_winrate, avg_win, avg_loss)
        
        # Nombre total de signaux (estimation basée sur la volatilité)
        total_signals = int(100 + data["volatility_hourly"] * 50)
        winning_signals = int(total_signals * total_winrate)
        losing_signals = total_signals - winning_signals
        
        return WinrateAnalysis(
            scenario=scenario,
            total_signals=total_signals,
            winning_signals=winning_signals,
            losing_signals=losing_signals,
            winrate=total_winrate * 100,  # En pourcentage
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            expected_value=expected_value,
            sharpe_ratio=data["sharpe_ratio"]
        )
    
    def generate_winrate_report(self):
        """Génère un rapport complet des winrates"""
        print("ANALYSE DES WINRATES PAR SCÉNARIO")
        print("=" * 80)
        
        analyses = {}
        
        # Analyser tous les scénarios
        for scenario in self.scenarios_data.keys():
            analyses[scenario] = self.analyze_scenario_winrate(scenario)
        
        # Tableau des winrates
        print(f"{'Scénario':<12} {'Winrate':<8} {'Signaux':<8} {'Gains':<8} {'Pertes':<8} {'PF':<6} {'EV':<8} {'Sharpe':<8}")
        print("-" * 80)
        
        for scenario, analysis in analyses.items():
            print(f"{scenario:<12} {analysis.winrate:<8.1f}% {analysis.total_signals:<8} "
                  f"{analysis.avg_win:<8.2f}% {analysis.avg_loss:<8.2f}% "
                  f"{analysis.profit_factor:<6.2f} {analysis.expected_value:<8.3f} {analysis.sharpe_ratio:<8.3f}")
        
        # Détail par scénario
        print("\n" + "=" * 80)
        print("DÉTAIL PAR SCÉNARIO")
        print("=" * 80)
        
        for scenario, analysis in analyses.items():
            print(f"\n{scenario.upper()}:")
            print(f"  Winrate global: {analysis.winrate:.1f}%")
            print(f"  Signaux gagnants: {analysis.winning_signals}/{analysis.total_signals}")
            print(f"  Gain moyen: {analysis.avg_win:.2f}%")
            print(f"  Perte moyenne: {analysis.avg_loss:.2f}%")
            print(f"  Profit Factor: {analysis.profit_factor:.2f}")
            print(f"  Valeur attendue: {analysis.expected_value:.3f}%")
            print(f"  Sharpe Ratio: {analysis.sharpe_ratio:.3f}")
            
            # Classification de performance
            if analysis.winrate > 60 and analysis.profit_factor > 1.5:
                performance = "EXCELLENT"
            elif analysis.winrate > 50 and analysis.profit_factor > 1.2:
                performance = "BON"
            elif analysis.winrate > 40 and analysis.profit_factor > 1.0:
                performance = "MOYEN"
            else:
                performance = "FAIBLE"
            
            print(f"  Performance: {performance}")
        
        # Statistiques globales
        print("\n" + "=" * 80)
        print("STATISTIQUES GLOBALES")
        print("=" * 80)
        
        avg_winrate = np.mean([a.winrate for a in analyses.values()])
        avg_profit_factor = np.mean([a.profit_factor for a in analyses.values()])
        avg_expected_value = np.mean([a.expected_value for a in analyses.values()])
        avg_sharpe = np.mean([a.sharpe_ratio for a in analyses.values()])
        
        print(f"Winrate moyen: {avg_winrate:.1f}%")
        print(f"Profit Factor moyen: {avg_profit_factor:.2f}")
        print(f"Valeur attendue moyenne: {avg_expected_value:.3f}%")
        print(f"Sharpe Ratio moyen: {avg_sharpe:.3f}")
        
        # Meilleurs scénarios
        best_winrate = max(analyses.values(), key=lambda x: x.winrate)
        best_profit_factor = max(analyses.values(), key=lambda x: x.profit_factor)
        best_expected_value = max(analyses.values(), key=lambda x: x.expected_value)
        
        print(f"\nMeilleur winrate: {best_winrate.scenario} ({best_winrate.winrate:.1f}%)")
        print(f"Meilleur Profit Factor: {best_profit_factor.scenario} ({best_profit_factor.profit_factor:.2f})")
        print(f"Meilleure valeur attendue: {best_expected_value.scenario} ({best_expected_value.expected_value:.3f}%)")
        
        # Sauvegarder les résultats
        self.save_winrate_analysis(analyses)
    
    def save_winrate_analysis(self, analyses: Dict[str, WinrateAnalysis]):
        """Sauvegarde l'analyse des winrates"""
        results = {}
        
        for scenario, analysis in analyses.items():
            results[scenario] = {
                "total_signals": analysis.total_signals,
                "winning_signals": analysis.winning_signals,
                "losing_signals": analysis.losing_signals,
                "winrate": analysis.winrate,
                "avg_win": analysis.avg_win,
                "avg_loss": analysis.avg_loss,
                "profit_factor": analysis.profit_factor,
                "expected_value": analysis.expected_value,
                "sharpe_ratio": analysis.sharpe_ratio
            }
        
        with open("winrate_analysis.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nAnalyse des winrates sauvegardée dans: winrate_analysis.json")

def main():
    calculator = WinrateCalculator()
    calculator.generate_winrate_report()

if __name__ == "__main__":
    main()

