#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPTIMISEUR DE STRATÉGIES TRADING
================================
Optimise les paramètres de trading basé sur l'analyse de performance
"""

import json
import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

@dataclass
class TradingStrategy:
    """Configuration d'une stratégie de trading"""
    name: str
    scenario: str
    risk_tolerance: float  # 0-100
    volatility_threshold: float  # %
    correlation_threshold: float  # 0-1
    menthorq_stability_min: float  # 0-1
    vwap_signal_weight: float  # 0-1
    volume_spike_weight: float  # 0-1
    momentum_weight: float  # 0-1
    position_size_multiplier: float  # 0.5-2.0
    stop_loss_pct: float  # %
    take_profit_pct: float  # %

class StrategyOptimizer:
    """Optimiseur de stratégies basé sur l'analyse de performance"""
    
    def __init__(self):
        self.scenarios_data = {
            "bullish": {
                "risk_score": 4.1,
                "trend_strength": 100.0,
                "vwap_above": 52.7,
                "volume_spike": 19.2,
                "momentum_positive": 54.4,
                "volatility_hourly": 1.21,
                "max_drawdown": 0.46,
                "sharpe_ratio": 0.737,
                "menthorq_stability": 0.991,
                "menthorq_trend": 2.95
            },
            "bearish": {
                "risk_score": 8.6,
                "trend_strength": 100.0,
                "vwap_above": 54.0,
                "volume_spike": 2.9,
                "momentum_positive": 20.9,
                "volatility_hourly": 1.81,
                "max_drawdown": 21.61,
                "sharpe_ratio": -0.424,
                "menthorq_stability": 0.993,
                "menthorq_trend": -2.00
            },
            "sideways": {
                "risk_score": 3.4,
                "trend_strength": 6.6,
                "vwap_above": 55.2,
                "volume_spike": 4.2,
                "momentum_positive": 18.0,
                "volatility_hourly": 0.91,
                "max_drawdown": 2.40,
                "sharpe_ratio": 0.005,
                "menthorq_stability": 0.999,
                "menthorq_trend": -0.01
            },
            "volatile": {
                "risk_score": 11.5,
                "trend_strength": 11.5,
                "vwap_above": 56.9,
                "volume_spike": 13.8,
                "momentum_positive": 37.7,
                "volatility_hourly": 3.15,
                "max_drawdown": 5.47,
                "sharpe_ratio": 0.006,
                "menthorq_stability": 0.998,
                "menthorq_trend": 0.38
            },
            "breakout": {
                "risk_score": 7.3,
                "trend_strength": 100.0,
                "vwap_above": 46.0,
                "volume_spike": 9.6,
                "momentum_positive": 59.0,
                "volatility_hourly": 2.22,
                "max_drawdown": 1.59,
                "sharpe_ratio": 0.580,
                "menthorq_stability": 0.987,
                "menthorq_trend": 4.44
            },
            "reversal": {
                "risk_score": 10.9,
                "trend_strength": 51.2,
                "vwap_above": 49.8,
                "volume_spike": 0.0,
                "momentum_positive": 33.1,
                "volatility_hourly": 2.89,
                "max_drawdown": 14.27,
                "sharpe_ratio": -0.158,
                "menthorq_stability": 0.996,
                "menthorq_trend": -1.08
            }
        }
    
    def calculate_optimal_parameters(self, scenario: str) -> TradingStrategy:
        """Calcule les paramètres optimaux pour un scénario"""
        data = self.scenarios_data[scenario]
        
        # Calculer la tolérance au risque basée sur le score de risque
        risk_tolerance = max(10, min(90, 100 - data["risk_score"]))
        
        # Seuil de volatilité basé sur la volatilité historique
        volatility_threshold = data["volatility_hourly"] * 1.5
        
        # Seuil de corrélation (toujours élevé pour MenthorQ stable)
        correlation_threshold = 0.4  # ES/NQ corrélation
        
        # Stabilité MenthorQ minimale
        menthorq_stability_min = max(0.95, data["menthorq_stability"] - 0.01)
        
        # Poids des signaux basés sur leur performance
        vwap_signal_weight = min(0.8, data["vwap_above"] / 100)
        volume_spike_weight = min(0.6, data["volume_spike"] / 100 * 2)
        momentum_weight = min(0.7, data["momentum_positive"] / 100)
        
        # Multiplicateur de taille de position basé sur le risque
        if data["risk_score"] < 5:
            position_size_multiplier = 1.5  # Risque faible = position plus grande
        elif data["risk_score"] < 10:
            position_size_multiplier = 1.0  # Risque moyen = position normale
        else:
            position_size_multiplier = 0.7  # Risque élevé = position réduite
        
        # Stop loss basé sur la volatilité et le drawdown
        stop_loss_pct = max(0.5, min(3.0, data["volatility_hourly"] * 2))
        
        # Take profit basé sur le Sharpe ratio et la tendance
        if data["sharpe_ratio"] > 0.5:
            take_profit_pct = stop_loss_pct * 2.5  # Ratio 1:2.5
        elif data["sharpe_ratio"] > 0:
            take_profit_pct = stop_loss_pct * 2.0  # Ratio 1:2
        else:
            take_profit_pct = stop_loss_pct * 1.5  # Ratio 1:1.5
        
        return TradingStrategy(
            name=f"Strategy_{scenario.upper()}",
            scenario=scenario,
            risk_tolerance=risk_tolerance,
            volatility_threshold=volatility_threshold,
            correlation_threshold=correlation_threshold,
            menthorq_stability_min=menthorq_stability_min,
            vwap_signal_weight=vwap_signal_weight,
            volume_spike_weight=volume_spike_weight,
            momentum_weight=momentum_weight,
            position_size_multiplier=position_size_multiplier,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct
        )
    
    def generate_all_strategies(self) -> Dict[str, TradingStrategy]:
        """Génère toutes les stratégies optimisées"""
        strategies = {}
        
        for scenario in self.scenarios_data.keys():
            strategies[scenario] = self.calculate_optimal_parameters(scenario)
        
        return strategies
    
    def analyze_strategy_performance(self, strategy: TradingStrategy) -> Dict[str, Any]:
        """Analyse la performance attendue d'une stratégie"""
        data = self.scenarios_data[strategy.scenario]
        
        # Score de performance basé sur les métriques
        performance_score = 0
        
        # Bonus pour Sharpe ratio positif
        if data["sharpe_ratio"] > 0.5:
            performance_score += 30
        elif data["sharpe_ratio"] > 0:
            performance_score += 20
        else:
            performance_score += 10
        
        # Bonus pour faible drawdown
        if data["max_drawdown"] < 2:
            performance_score += 25
        elif data["max_drawdown"] < 5:
            performance_score += 15
        else:
            performance_score += 5
        
        # Bonus pour MenthorQ stable
        if data["menthorq_stability"] > 0.99:
            performance_score += 20
        elif data["menthorq_stability"] > 0.95:
            performance_score += 15
        else:
            performance_score += 10
        
        # Bonus pour tendance forte
        if data["trend_strength"] > 80:
            performance_score += 15
        elif data["trend_strength"] > 50:
            performance_score += 10
        else:
            performance_score += 5
        
        # Bonus pour faible risque
        if data["risk_score"] < 5:
            performance_score += 10
        elif data["risk_score"] < 10:
            performance_score += 5
        
        # Calculer le ROI attendu
        expected_roi = 0
        if data["sharpe_ratio"] > 0:
            expected_roi = data["sharpe_ratio"] * 10  # Approximation
        
        return {
            "performance_score": min(100, performance_score),
            "expected_roi": expected_roi,
            "risk_level": "FAIBLE" if data["risk_score"] < 5 else "MOYEN" if data["risk_score"] < 10 else "ÉLEVÉ",
            "recommended": performance_score > 70,
            "confidence": min(100, performance_score + 20)
        }
    
    def generate_optimization_report(self):
        """Génère un rapport d'optimisation complet"""
        print("OPTIMISATION DES STRATÉGIES TRADING")
        print("=" * 80)
        
        strategies = self.generate_all_strategies()
        
        # Tableau des stratégies optimisées
        print(f"{'Stratégie':<15} {'Risque':<8} {'Vol':<6} {'MenthorQ':<8} {'Position':<8} {'Stop':<6} {'TP':<6} {'Score':<6}")
        print("-" * 80)
        
        for scenario, strategy in strategies.items():
            performance = self.analyze_strategy_performance(strategy)
            
            print(f"{strategy.name:<15} {strategy.risk_tolerance:<8.1f} {strategy.volatility_threshold:<6.2f} "
                  f"{strategy.menthorq_stability_min:<8.3f} {strategy.position_size_multiplier:<8.1f} "
                  f"{strategy.stop_loss_pct:<6.2f} {strategy.take_profit_pct:<6.2f} {performance['performance_score']:<6.1f}")
        
        # Recommandations par scénario
        print("\n" + "=" * 80)
        print("RECOMMANDATIONS PAR SCÉNARIO")
        print("=" * 80)
        
        for scenario, strategy in strategies.items():
            performance = self.analyze_strategy_performance(strategy)
            data = self.scenarios_data[scenario]
            
            print(f"\n{scenario.upper()}:")
            print(f"  Score de performance: {performance['performance_score']:.1f}/100")
            print(f"  ROI attendu: {performance['expected_roi']:.1f}%")
            print(f"  Niveau de risque: {performance['risk_level']}")
            print(f"  Recommandé: {'OUI' if performance['recommended'] else 'NON'}")
            print(f"  Confiance: {performance['confidence']:.1f}%")
            
            # Stratégie spécifique
            if scenario == "bullish":
                print("  → Stratégie: Suivre la tendance haussière avec positions longues")
                print("  → Focus: Momentum positif (54.4%) et VWAP au-dessus (52.7%)")
            elif scenario == "bearish":
                print("  → Stratégie: Positions courtes avec stop loss serré")
                print("  → Focus: Momentum négatif (53.6%) et drawdown élevé (21.6%)")
            elif scenario == "sideways":
                print("  → Stratégie: Trading range avec scalping")
                print("  → Focus: Faible volatilité (0.91%) et MenthorQ très stable (0.999)")
            elif scenario == "volatile":
                print("  → Stratégie: Réduction des positions, trading rapide")
                print("  → Focus: Haute volatilité (3.15%) et pics de volume (13.8%)")
            elif scenario == "breakout":
                print("  → Stratégie: Suivre les cassures avec momentum")
                print("  → Focus: Momentum positif fort (59.0%) et tendance claire")
            elif scenario == "reversal":
                print("  → Stratégie: Contre-tendance avec prudence")
                print("  → Focus: Momentum négatif (45.6%) et drawdown modéré (14.3%)")
        
        # Configuration optimale globale
        print("\n" + "=" * 80)
        print("CONFIGURATION OPTIMALE GLOBALE")
        print("=" * 80)
        
        # Calculer les moyennes pondérées
        total_score = sum(self.analyze_strategy_performance(s)["performance_score"] for s in strategies.values())
        avg_risk_tolerance = np.mean([s.risk_tolerance for s in strategies.values()])
        avg_volatility_threshold = np.mean([s.volatility_threshold for s in strategies.values()])
        avg_menthorq_stability = np.mean([s.menthorq_stability_min for s in strategies.values()])
        avg_position_multiplier = np.mean([s.position_size_multiplier for s in strategies.values()])
        
        print(f"Score moyen: {total_score/len(strategies):.1f}/100")
        print(f"Tolérance au risque: {avg_risk_tolerance:.1f}")
        print(f"Seuil volatilité: {avg_volatility_threshold:.2f}%/h")
        print(f"Stabilité MenthorQ min: {avg_menthorq_stability:.3f}")
        print(f"Multiplicateur position: {avg_position_multiplier:.1f}")
        
        # Seuils recommandés
        print("\nSeuils recommandés pour le système:")
        print(f"- Volatilité basse: < {avg_volatility_threshold * 0.7:.2f}%/h")
        print(f"- Volatilité haute: > {avg_volatility_threshold * 1.3:.2f}%/h")
        print(f"- Corrélation ES/NQ: > 0.4")
        print(f"- Stabilité MenthorQ: > {avg_menthorq_stability:.3f}")
        print(f"- Score de risque max: < 10")
        
        # Sauvegarder les stratégies
        self.save_strategies_to_file(strategies)
    
    def save_strategies_to_file(self, strategies: Dict[str, TradingStrategy]):
        """Sauvegarde les stratégies dans un fichier JSON"""
        strategies_dict = {}
        
        for scenario, strategy in strategies.items():
            performance = self.analyze_strategy_performance(strategy)
            
            strategies_dict[scenario] = {
                "name": strategy.name,
                "risk_tolerance": strategy.risk_tolerance,
                "volatility_threshold": strategy.volatility_threshold,
                "correlation_threshold": strategy.correlation_threshold,
                "menthorq_stability_min": strategy.menthorq_stability_min,
                "vwap_signal_weight": strategy.vwap_signal_weight,
                "volume_spike_weight": strategy.volume_spike_weight,
                "momentum_weight": strategy.momentum_weight,
                "position_size_multiplier": strategy.position_size_multiplier,
                "stop_loss_pct": strategy.stop_loss_pct,
                "take_profit_pct": strategy.take_profit_pct,
                "performance_score": performance["performance_score"],
                "expected_roi": performance["expected_roi"],
                "risk_level": performance["risk_level"],
                "recommended": performance["recommended"],
                "confidence": performance["confidence"]
            }
        
        with open("optimized_strategies.json", "w", encoding="utf-8") as f:
            json.dump(strategies_dict, f, indent=2, ensure_ascii=False)
        
        print(f"\nStratégies sauvegardées dans: optimized_strategies.json")

def main():
    optimizer = StrategyOptimizer()
    optimizer.generate_optimization_report()

if __name__ == "__main__":
    main()

