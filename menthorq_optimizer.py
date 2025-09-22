#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPTIMISEUR MENTHORQ COMPLET
===========================
Optimise tous les paramètres du système MenthorQ pour améliorer les performances
"""

import json
import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import itertools

@dataclass
class OptimizedParameters:
    """Paramètres optimisés pour le trading MenthorQ"""
    min_distance_pct: float
    max_distance_pct: float
    min_signal_strength: float
    min_menthorq_stability: float
    trade_duration_min: int
    stop_loss_pct: float
    take_profit_pct: float
    position_size_multiplier: float
    allowed_scenarios: List[str]
    correlation_threshold: float
    volatility_threshold: float

class MenthorQOptimizer:
    """Optimiseur complet du système MenthorQ"""
    
    def __init__(self):
        # Charger les données d'analyse existantes
        self.load_analysis_data()
        
        # Paramètres à optimiser
        self.optimization_ranges = {
            "min_distance_pct": [0.8, 1.0, 1.2, 1.5],
            "max_distance_pct": [1.5, 2.0, 2.5, 3.0],
            "min_signal_strength": [0.3, 0.4, 0.5, 0.6],
            "min_menthorq_stability": [0.95, 0.97, 0.99],
            "trade_duration_min": [15, 30, 45, 60],
            "stop_loss_pct": [0.3, 0.5, 0.7, 1.0],
            "take_profit_pct": [1.0, 1.5, 2.0, 2.5],
            "position_size_multiplier": [0.5, 0.7, 1.0, 1.2]
        }
        
        # Scénarios autorisés (basé sur l'analyse)
        self.scenario_performance = {
            "bullish": {"winrate": 50.0, "pnl": 0.18, "allowed": True},
            "sideways": {"winrate": 66.7, "pnl": 0.27, "allowed": True},
            "bearish": {"winrate": 0.0, "pnl": -5.04, "allowed": False},
            "volatile": {"winrate": 0.0, "pnl": -1.56, "allowed": False},
            "reversal": {"winrate": 0.0, "pnl": -1.67, "allowed": False}
        }
    
    def load_analysis_data(self):
        """Charge les données d'analyse existantes"""
        try:
            with open("menthorq_distance_analysis.json", "r") as f:
                self.analysis_data = json.load(f)
        except FileNotFoundError:
            print("Fichier d'analyse non trouvé, utilisation des données par défaut")
            self.analysis_data = {}
    
    def simulate_optimized_trading(self, params: OptimizedParameters) -> Dict[str, Any]:
        """Simule le trading avec des paramètres optimisés"""
        total_trades = 0
        winning_trades = 0
        total_pnl = 0.0
        max_drawdown = 0.0
        current_drawdown = 0.0
        peak_equity = 0.0
        
        # Simuler les trades pour chaque scénario autorisé
        for scenario in params.allowed_scenarios:
            if scenario in self.analysis_data:
                scenario_data = self.analysis_data[scenario]
                
                # Appliquer les filtres optimisés
                filtered_trades = self.filter_trades_by_parameters(scenario_data, params)
                
                for trade in filtered_trades:
                    total_trades += 1
                    
                    # Calculer le PnL avec la gestion de risque
                    pnl = self.calculate_optimized_pnl(trade, params)
                    total_pnl += pnl
                    
                    if pnl > 0:
                        winning_trades += 1
                        current_drawdown = 0.0
                        peak_equity = max(peak_equity, total_pnl)
                    else:
                        current_drawdown += abs(pnl)
                        max_drawdown = max(max_drawdown, current_drawdown)
        
        # Calculer les métriques de performance
        winrate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
        profit_factor = self.calculate_profit_factor(total_trades, winning_trades, total_pnl)
        sharpe_ratio = self.calculate_sharpe_ratio(total_pnl, max_drawdown)
        
        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "winrate": winrate,
            "avg_pnl": avg_pnl,
            "total_pnl": total_pnl,
            "max_drawdown": max_drawdown,
            "profit_factor": profit_factor,
            "sharpe_ratio": sharpe_ratio,
            "parameters": params
        }
    
    def filter_trades_by_parameters(self, scenario_data: Dict, params: OptimizedParameters) -> List[Dict]:
        """Filtre les trades selon les paramètres optimisés"""
        # Simuler des trades basés sur les données existantes
        trades = []
        
        # Créer des trades simulés avec les bonnes distances
        for distance_type, perf in scenario_data.get("distance_analysis", {}).items():
            if perf["total_trades"] > 0:
                # Vérifier si la distance est dans la plage optimisée
                distance_range = self.get_distance_range(distance_type)
                
                if (distance_range[0] >= params.min_distance_pct and 
                    distance_range[1] <= params.max_distance_pct):
                    
                    # Créer des trades avec les performances observées
                    for i in range(perf["total_trades"]):
                        trade = {
                            "distance_type": distance_type,
                            "pnl": perf["avg_pnl"],
                            "signal_strength": perf["avg_signal_strength"],
                            "is_winner": i < perf["winning_trades"]
                        }
                        trades.append(trade)
        
        return trades
    
    def get_distance_range(self, distance_type: str) -> Tuple[float, float]:
        """Retourne la plage de distance pour un type donné"""
        ranges = {
            "very_close": (0.0, 0.5),
            "close": (0.5, 1.0),
            "medium": (1.0, 2.0),
            "far": (2.0, 5.0)
        }
        return ranges.get(distance_type, (0.0, 5.0))
    
    def calculate_optimized_pnl(self, trade: Dict, params: OptimizedParameters) -> float:
        """Calcule le PnL optimisé avec gestion de risque"""
        base_pnl = trade["pnl"]
        
        # Appliquer le multiplicateur de position
        adjusted_pnl = base_pnl * params.position_size_multiplier
        
        # Appliquer la gestion de risque (stop loss / take profit)
        if adjusted_pnl > 0:
            # Take profit
            max_profit = params.take_profit_pct
            adjusted_pnl = min(adjusted_pnl, max_profit)
        else:
            # Stop loss
            max_loss = params.stop_loss_pct
            adjusted_pnl = max(adjusted_pnl, -max_loss)
        
        return adjusted_pnl
    
    def calculate_profit_factor(self, total_trades: int, winning_trades: int, total_pnl: float) -> float:
        """Calcule le profit factor"""
        if total_trades == 0:
            return 0.0
        
        # Estimation basée sur le PnL total
        if total_pnl > 0:
            return 1.0 + (total_pnl / 10.0)  # Approximation
        else:
            return 0.5 + (total_pnl / 20.0)  # Approximation
    
    def calculate_sharpe_ratio(self, total_pnl: float, max_drawdown: float) -> float:
        """Calcule le ratio de Sharpe"""
        if max_drawdown == 0:
            return 0.0
        
        return total_pnl / max_drawdown if max_drawdown > 0 else 0.0
    
    def generate_parameter_combinations(self) -> List[OptimizedParameters]:
        """Génère toutes les combinaisons de paramètres à tester"""
        combinations = []
        
        # Générer les combinaisons
        for min_dist in self.optimization_ranges["min_distance_pct"]:
            for max_dist in self.optimization_ranges["max_distance_pct"]:
                if max_dist <= min_dist:  # Skip invalid combinations
                    continue
                    
                for signal_strength in self.optimization_ranges["min_signal_strength"]:
                    for stability in self.optimization_ranges["min_menthorq_stability"]:
                        for duration in self.optimization_ranges["trade_duration_min"]:
                            for stop_loss in self.optimization_ranges["stop_loss_pct"]:
                                for take_profit in self.optimization_ranges["take_profit_pct"]:
                                    for position_size in self.optimization_ranges["position_size_multiplier"]:
                                        # Scénarios autorisés (seulement bullish et sideways)
                                        allowed_scenarios = ["bullish", "sideways"]
                                        
                                        params = OptimizedParameters(
                                            min_distance_pct=min_dist,
                                            max_distance_pct=max_dist,
                                            min_signal_strength=signal_strength,
                                            min_menthorq_stability=stability,
                                            trade_duration_min=duration,
                                            stop_loss_pct=stop_loss,
                                            take_profit_pct=take_profit,
                                            position_size_multiplier=position_size,
                                            allowed_scenarios=allowed_scenarios,
                                            correlation_threshold=0.4,
                                            volatility_threshold=2.0
                                        )
                                        
                                        combinations.append(params)
        
        return combinations
    
    def optimize_parameters(self) -> Dict[str, Any]:
        """Optimise les paramètres pour maximiser les performances"""
        print("OPTIMISATION DES PARAMÈTRES MENTHORQ")
        print("=" * 60)
        
        # Générer les combinaisons (limitées pour éviter l'explosion combinatoire)
        combinations = self.generate_parameter_combinations()
        
        # Limiter à 1000 combinaisons pour la performance
        if len(combinations) > 1000:
            combinations = combinations[:1000]
        
        print(f"Test de {len(combinations)} combinaisons de paramètres...")
        
        best_performance = None
        best_params = None
        results = []
        
        for i, params in enumerate(combinations):
            if i % 100 == 0:
                print(f"Progression: {i}/{len(combinations)}")
            
            # Simuler le trading avec ces paramètres
            performance = self.simulate_optimized_trading(params)
            results.append(performance)
            
            # Vérifier si c'est la meilleure performance
            if best_performance is None or self.is_better_performance(performance, best_performance):
                best_performance = performance
                best_params = params
        
        return {
            "best_performance": best_performance,
            "best_params": best_params,
            "all_results": results,
            "total_combinations_tested": len(combinations)
        }
    
    def is_better_performance(self, new_perf: Dict, current_best: Dict) -> bool:
        """Détermine si une performance est meilleure que la précédente"""
        # Critères de sélection : winrate > 50%, profit factor > 1.2, drawdown < 5%
        new_score = self.calculate_performance_score(new_perf)
        current_score = self.calculate_performance_score(current_best)
        
        return new_score > current_score
    
    def calculate_performance_score(self, performance: Dict) -> float:
        """Calcule un score de performance global"""
        winrate = performance["winrate"]
        profit_factor = performance["profit_factor"]
        max_drawdown = performance["max_drawdown"]
        total_trades = performance["total_trades"]
        
        # Score basé sur plusieurs critères
        score = 0.0
        
        # Bonus pour winrate élevé
        if winrate > 60:
            score += 50
        elif winrate > 50:
            score += 30
        elif winrate > 40:
            score += 20
        
        # Bonus pour profit factor élevé
        if profit_factor > 2.0:
            score += 30
        elif profit_factor > 1.5:
            score += 20
        elif profit_factor > 1.2:
            score += 10
        
        # Bonus pour faible drawdown
        if max_drawdown < 2.0:
            score += 20
        elif max_drawdown < 5.0:
            score += 10
        
        # Bonus pour nombre de trades suffisant
        if total_trades > 10:
            score += 10
        
        return score
    
    def generate_optimization_report(self, optimization_results: Dict[str, Any]):
        """Génère un rapport d'optimisation complet"""
        print("\n" + "=" * 80)
        print("RAPPORT D'OPTIMISATION MENTHORQ")
        print("=" * 80)
        
        best_perf = optimization_results["best_performance"]
        best_params = optimization_results["best_params"]
        
        print(f"Combinaisons testées: {optimization_results['total_combinations_tested']}")
        print(f"Meilleure performance trouvée:")
        print(f"  Winrate: {best_perf['winrate']:.1f}%")
        print(f"  Profit Factor: {best_perf['profit_factor']:.2f}")
        print(f"  PnL moyen: {best_perf['avg_pnl']:.2f}%")
        print(f"  Max Drawdown: {best_perf['max_drawdown']:.2f}%")
        print(f"  Total trades: {best_perf['total_trades']}")
        print(f"  Sharpe Ratio: {best_perf['sharpe_ratio']:.3f}")
        
        print(f"\nParamètres optimaux:")
        print(f"  Distance min: {best_params.min_distance_pct:.1f}%")
        print(f"  Distance max: {best_params.max_distance_pct:.1f}%")
        print(f"  Signal strength min: {best_params.min_signal_strength:.2f}")
        print(f"  MenthorQ stability min: {best_params.min_menthorq_stability:.3f}")
        print(f"  Durée trade: {best_params.trade_duration_min} min")
        print(f"  Stop loss: {best_params.stop_loss_pct:.1f}%")
        print(f"  Take profit: {best_params.take_profit_pct:.1f}%")
        print(f"  Position size: {best_params.position_size_multiplier:.1f}x")
        print(f"  Scénarios autorisés: {', '.join(best_params.allowed_scenarios)}")
        
        # Analyser les top 10 performances
        print(f"\nTOP 10 DES PERFORMANCES:")
        print(f"{'Rang':<4} {'Winrate':<8} {'PF':<6} {'PnL':<8} {'DD':<6} {'Score':<6}")
        print("-" * 50)
        
        sorted_results = sorted(optimization_results["all_results"], 
                              key=lambda x: self.calculate_performance_score(x), 
                              reverse=True)
        
        for i, result in enumerate(sorted_results[:10]):
            score = self.calculate_performance_score(result)
            print(f"{i+1:<4} {result['winrate']:<8.1f}% {result['profit_factor']:<6.2f} "
                  f"{result['avg_pnl']:<8.2f}% {result['max_drawdown']:<6.2f}% {score:<6.1f}")
        
        # Sauvegarder les résultats
        self.save_optimization_results(optimization_results)
    
    def save_optimization_results(self, results: Dict[str, Any]):
        """Sauvegarde les résultats d'optimisation"""
        # Préparer les données pour la sauvegarde (sans les objets non sérialisables)
        save_data = {
            "best_performance": {
                "total_trades": results["best_performance"]["total_trades"],
                "winning_trades": results["best_performance"]["winning_trades"],
                "winrate": results["best_performance"]["winrate"],
                "avg_pnl": results["best_performance"]["avg_pnl"],
                "total_pnl": results["best_performance"]["total_pnl"],
                "max_drawdown": results["best_performance"]["max_drawdown"],
                "profit_factor": results["best_performance"]["profit_factor"],
                "sharpe_ratio": results["best_performance"]["sharpe_ratio"]
            },
            "best_params": {
                "min_distance_pct": results["best_params"].min_distance_pct,
                "max_distance_pct": results["best_params"].max_distance_pct,
                "min_signal_strength": results["best_params"].min_signal_strength,
                "min_menthorq_stability": results["best_params"].min_menthorq_stability,
                "trade_duration_min": results["best_params"].trade_duration_min,
                "stop_loss_pct": results["best_params"].stop_loss_pct,
                "take_profit_pct": results["best_params"].take_profit_pct,
                "position_size_multiplier": results["best_params"].position_size_multiplier,
                "allowed_scenarios": results["best_params"].allowed_scenarios,
                "correlation_threshold": results["best_params"].correlation_threshold,
                "volatility_threshold": results["best_params"].volatility_threshold
            },
            "total_combinations_tested": results["total_combinations_tested"],
            "optimization_date": "2025-01-20"
        }
        
        with open("menthorq_optimization_results.json", "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nRésultats d'optimisation sauvegardés dans: menthorq_optimization_results.json")

def main():
    optimizer = MenthorQOptimizer()
    results = optimizer.optimize_parameters()
    optimizer.generate_optimization_report(results)

if __name__ == "__main__":
    main()
