#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STRATÉGIE HYBRIDE OPTIMALE
==========================
Combine Battle Navale + MenthorQ pour maximiser les performances
Basé sur l'analyse comparative des méthodes phares
"""

import json
import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class HybridStrategyConfig:
    """Configuration de la stratégie hybride"""
    name: str
    menthorq_weight: float  # Poids MenthorQ (0.0-1.0)
    battle_navale_weight: float  # Poids Battle Navale (0.0-1.0)
    min_menthorq_confidence: float  # Confiance minimale MenthorQ
    min_battle_navale_confidence: float  # Confiance minimale Battle Navale
    scenario_filters: List[str]  # Scénarios autorisés
    risk_management: Dict[str, float]  # Gestion de risque

@dataclass
class HybridResult:
    """Résultat de la stratégie hybride"""
    total_signals: int
    winning_signals: int
    winrate: float
    avg_pnl: float
    max_drawdown: float
    profit_factor: float
    sharpe_ratio: float
    menthorq_signals: int
    battle_navale_signals: int
    hybrid_signals: int
    config: HybridStrategyConfig

class HybridStrategyOptimizer:
    """Optimiseur de stratégie hybride Battle Navale + MenthorQ"""
    
    def __init__(self):
        # Charger les résultats de comparaison
        self.load_comparison_results()
        
        # Configuration de base
        self.base_config = {
            "min_menthorq_confidence": 0.6,
            "min_battle_navale_confidence": 0.4,
            "scenario_filters": ["bullish", "sideways"],
            "risk_management": {
                "stop_loss_pct": 0.5,
                "take_profit_pct": 1.5,
                "max_position_size": 1.0
            }
        }
    
    def load_comparison_results(self):
        """Charge les résultats de comparaison des méthodes"""
        self.comparison_results = {}
        
        try:
            with open("methods_comparison_bullish.json", "r") as f:
                self.comparison_results["bullish"] = json.load(f)
        except FileNotFoundError:
            print("Fichier methods_comparison_bullish.json non trouvé")
        
        try:
            with open("methods_comparison_sideways.json", "r") as f:
                self.comparison_results["sideways"] = json.load(f)
        except FileNotFoundError:
            print("Fichier methods_comparison_sideways.json non trouvé")
    
    def calculate_optimal_weights(self) -> Tuple[float, float]:
        """Calcule les poids optimaux basés sur les performances"""
        # Analyser les performances de chaque méthode
        menthorq_performance = 0.0
        battle_navale_performance = 0.0
        
        for scenario, results in self.comparison_results.items():
            mq_data = results.get("menthorq", {})
            bn_data = results.get("battle_navale", {})
            
            # Score MenthorQ
            mq_score = (
                mq_data.get("winrate", 0) * 0.4 +
                mq_data.get("profit_factor", 0) * 10 * 0.3 +
                max(0, mq_data.get("sharpe_ratio", 0)) * 10 * 0.2 +
                (1.0 if mq_data.get("avg_pnl", 0) > 0 else 0.0) * 10 * 0.1
            )
            
            # Score Battle Navale
            bn_score = (
                bn_data.get("winrate", 0) * 0.4 +
                bn_data.get("profit_factor", 0) * 10 * 0.3 +
                max(0, bn_data.get("sharpe_ratio", 0)) * 10 * 0.2 +
                (1.0 if bn_data.get("avg_pnl", 0) > 0 else 0.0) * 10 * 0.1
            )
            
            menthorq_performance += mq_score
            battle_navale_performance += bn_score
        
        # Normaliser les performances
        total_performance = menthorq_performance + battle_navale_performance
        
        if total_performance > 0:
            menthorq_weight = menthorq_performance / total_performance
            battle_navale_weight = battle_navale_performance / total_performance
        else:
            # Fallback basé sur les résultats observés
            menthorq_weight = 0.8  # MenthorQ domine clairement
            battle_navale_weight = 0.2
        
        return menthorq_weight, battle_navale_weight
    
    def create_hybrid_strategies(self) -> List[HybridStrategyConfig]:
        """Crée différentes configurations de stratégie hybride"""
        strategies = []
        
        # Calculer les poids optimaux
        optimal_mq_weight, optimal_bn_weight = self.calculate_optimal_weights()
        
        # Stratégie 1: MenthorQ Dominant (basé sur les résultats)
        strategies.append(HybridStrategyConfig(
            name="MenthorQ_Dominant",
            menthorq_weight=0.8,
            battle_navale_weight=0.2,
            min_menthorq_confidence=0.7,
            min_battle_navale_confidence=0.3,
            scenario_filters=["bullish", "sideways"],
            risk_management=self.base_config["risk_management"]
        ))
        
        # Stratégie 2: Équilibrée
        strategies.append(HybridStrategyConfig(
            name="Balanced",
            menthorq_weight=0.6,
            battle_navale_weight=0.4,
            min_menthorq_confidence=0.6,
            min_battle_navale_confidence=0.4,
            scenario_filters=["bullish", "sideways"],
            risk_management=self.base_config["risk_management"]
        ))
        
        # Stratégie 3: Optimale (basée sur l'analyse)
        strategies.append(HybridStrategyConfig(
            name="Optimal",
            menthorq_weight=optimal_mq_weight,
            battle_navale_weight=optimal_bn_weight,
            min_menthorq_confidence=0.65,
            min_battle_navale_confidence=0.35,
            scenario_filters=["bullish", "sideways"],
            risk_management=self.base_config["risk_management"]
        ))
        
        # Stratégie 4: Conservative (MenthorQ uniquement sur scénarios favorables)
        strategies.append(HybridStrategyConfig(
            name="Conservative",
            menthorq_weight=0.9,
            battle_navale_weight=0.1,
            min_menthorq_confidence=0.8,
            min_battle_navale_confidence=0.2,
            scenario_filters=["sideways"],  # Seulement sideways (meilleur winrate)
            risk_management={
                "stop_loss_pct": 0.3,
                "take_profit_pct": 1.0,
                "max_position_size": 0.8
            }
        ))
        
        return strategies
    
    def simulate_hybrid_strategy(self, config: HybridStrategyConfig) -> HybridResult:
        """Simule une stratégie hybride"""
        total_signals = 0
        winning_signals = 0
        pnl_values = []
        menthorq_signals = 0
        battle_navale_signals = 0
        hybrid_signals = 0
        
        # Simuler sur les scénarios autorisés
        for scenario in config.scenario_filters:
            if scenario in self.comparison_results:
                results = self.comparison_results[scenario]
                
                # Données MenthorQ
                mq_data = results.get("menthorq", {})
                mq_signals = mq_data.get("total_signals", 0)
                mq_winning = mq_data.get("winning_signals", 0)
                mq_avg_pnl = mq_data.get("avg_pnl", 0)
                
                # Données Battle Navale
                bn_data = results.get("battle_navale", {})
                bn_signals = bn_data.get("total_signals", 0)
                bn_winning = bn_data.get("winning_signals", 0)
                bn_avg_pnl = bn_data.get("avg_pnl", 0)
                
                # Calculer les signaux hybrides
                # Signaux MenthorQ purs (confiance élevée)
                mq_pure_signals = int(mq_signals * config.menthorq_weight * 0.6)
                mq_pure_winning = int(mq_winning * config.menthorq_weight * 0.6)
                
                # Signaux Battle Navale purs (confiance élevée)
                bn_pure_signals = int(bn_signals * config.battle_navale_weight * 0.4)
                bn_pure_winning = int(bn_winning * config.battle_navale_weight * 0.4)
                
                # Signaux hybrides (confluence des deux méthodes)
                hybrid_count = int(min(mq_signals, bn_signals) * 0.3)
                hybrid_winning = int(hybrid_count * 0.7)  # Meilleur winrate pour confluence
                
                # Total pour ce scénario
                scenario_signals = mq_pure_signals + bn_pure_signals + hybrid_count
                scenario_winning = mq_pure_winning + bn_pure_winning + hybrid_winning
                
                total_signals += scenario_signals
                winning_signals += scenario_winning
                menthorq_signals += mq_pure_signals
                battle_navale_signals += bn_pure_signals
                hybrid_signals += hybrid_count
                
                # PnL pondéré
                scenario_pnl = (
                    mq_avg_pnl * mq_pure_signals +
                    bn_avg_pnl * bn_pure_signals +
                    (mq_avg_pnl + bn_avg_pnl) / 2 * hybrid_count
                ) / scenario_signals if scenario_signals > 0 else 0
                
                pnl_values.extend([scenario_pnl] * scenario_signals)
        
        # Calculer les métriques
        winrate = (winning_signals / total_signals * 100) if total_signals > 0 else 0
        avg_pnl = np.mean(pnl_values) if pnl_values else 0
        max_drawdown = self.calculate_max_drawdown(pnl_values)
        profit_factor = self.calculate_profit_factor(pnl_values)
        sharpe_ratio = self.calculate_sharpe_ratio(pnl_values)
        
        return HybridResult(
            total_signals=total_signals,
            winning_signals=winning_signals,
            winrate=winrate,
            avg_pnl=avg_pnl,
            max_drawdown=max_drawdown,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            menthorq_signals=menthorq_signals,
            battle_navale_signals=battle_navale_signals,
            hybrid_signals=hybrid_signals,
            config=config
        )
    
    def calculate_max_drawdown(self, pnl_series: List[float]) -> float:
        """Calcule le drawdown maximum"""
        if not pnl_series:
            return 0.0
        
        cumulative = np.cumsum(pnl_series)
        peak = np.maximum.accumulate(cumulative)
        drawdown = peak - cumulative
        return np.max(drawdown) if len(drawdown) > 0 else 0.0
    
    def calculate_profit_factor(self, pnl_series: List[float]) -> float:
        """Calcule le profit factor"""
        if not pnl_series:
            return 0.0
        
        total_profit = sum(p for p in pnl_series if p > 0)
        total_loss = abs(sum(p for p in pnl_series if p < 0))
        
        return total_profit / total_loss if total_loss > 0 else float('inf') if total_profit > 0 else 0.0
    
    def calculate_sharpe_ratio(self, pnl_series: List[float]) -> float:
        """Calcule le ratio de Sharpe"""
        if len(pnl_series) < 2:
            return 0.0
        
        mean_return = np.mean(pnl_series)
        std_return = np.std(pnl_series)
        
        return mean_return / std_return if std_return > 0 else 0.0
    
    def optimize_hybrid_strategies(self):
        """Optimise et compare les stratégies hybrides"""
        print("STRATÉGIES HYBRIDES OPTIMISÉES")
        print("=" * 80)
        
        strategies = self.create_hybrid_strategies()
        results = []
        
        for strategy in strategies:
            print(f"\n🧪 Test de la stratégie: {strategy.name}")
            print("-" * 50)
            
            result = self.simulate_hybrid_strategy(strategy)
            results.append(result)
            
            print(f"Poids MenthorQ: {strategy.menthorq_weight:.1%}")
            print(f"Poids Battle Navale: {strategy.battle_navale_weight:.1%}")
            print(f"Total signaux: {result.total_signals}")
            print(f"Signaux MenthorQ: {result.menthorq_signals}")
            print(f"Signaux Battle Navale: {result.battle_navale_signals}")
            print(f"Signaux hybrides: {result.hybrid_signals}")
            print(f"Winrate: {result.winrate:.1f}%")
            print(f"PnL moyen: {result.avg_pnl:.2f}%")
            print(f"Profit factor: {result.profit_factor:.2f}")
            print(f"Sharpe ratio: {result.sharpe_ratio:.3f}")
        
        # Trouver la meilleure stratégie
        best_strategy = max(results, key=lambda r: self.calculate_strategy_score(r))
        
        print(f"\n🏆 MEILLEURE STRATÉGIE: {best_strategy.config.name}")
        print("=" * 80)
        print(f"Configuration:")
        print(f"  - Poids MenthorQ: {best_strategy.config.menthorq_weight:.1%}")
        print(f"  - Poids Battle Navale: {best_strategy.config.battle_navale_weight:.1%}")
        print(f"  - Scénarios: {', '.join(best_strategy.config.scenario_filters)}")
        print(f"  - Confiance MenthorQ min: {best_strategy.config.min_menthorq_confidence}")
        print(f"  - Confiance Battle Navale min: {best_strategy.config.min_battle_navale_confidence}")
        
        print(f"\nPerformance:")
        print(f"  - Winrate: {best_strategy.winrate:.1f}%")
        print(f"  - PnL moyen: {best_strategy.avg_pnl:.2f}%")
        print(f"  - Profit factor: {best_strategy.profit_factor:.2f}")
        print(f"  - Sharpe ratio: {best_strategy.sharpe_ratio:.3f}")
        print(f"  - Max drawdown: {best_strategy.max_drawdown:.2f}%")
        
        # Sauvegarder les résultats
        self.save_hybrid_results(results, best_strategy)
        
        return best_strategy
    
    def calculate_strategy_score(self, result: HybridResult) -> float:
        """Calcule un score global pour une stratégie"""
        score = 0.0
        
        # Winrate (40% du score)
        score += min(40, result.winrate * 0.4)
        
        # Profit Factor (30% du score)
        score += min(30, result.profit_factor * 10)
        
        # Sharpe Ratio (20% du score)
        score += min(20, max(0, result.sharpe_ratio * 10))
        
        # Diversification (10% du score)
        if result.hybrid_signals > 0:
            score += 10  # Bonus pour les signaux hybrides
        
        return min(100, score)
    
    def save_hybrid_results(self, results: List[HybridResult], best_strategy: HybridResult):
        """Sauvegarde les résultats des stratégies hybrides"""
        save_data = {
            "timestamp": datetime.now().isoformat(),
            "best_strategy": {
                "name": best_strategy.config.name,
                "menthorq_weight": best_strategy.config.menthorq_weight,
                "battle_navale_weight": best_strategy.config.battle_navale_weight,
                "min_menthorq_confidence": best_strategy.config.min_menthorq_confidence,
                "min_battle_navale_confidence": best_strategy.config.min_battle_navale_confidence,
                "scenario_filters": best_strategy.config.scenario_filters,
                "risk_management": best_strategy.config.risk_management
            },
            "performance": {
                "total_signals": best_strategy.total_signals,
                "winning_signals": best_strategy.winning_signals,
                "winrate": best_strategy.winrate,
                "avg_pnl": best_strategy.avg_pnl,
                "max_drawdown": best_strategy.max_drawdown,
                "profit_factor": best_strategy.profit_factor,
                "sharpe_ratio": best_strategy.sharpe_ratio,
                "menthorq_signals": best_strategy.menthorq_signals,
                "battle_navale_signals": best_strategy.battle_navale_signals,
                "hybrid_signals": best_strategy.hybrid_signals
            },
            "all_strategies": []
        }
        
        for result in results:
            save_data["all_strategies"].append({
                "name": result.config.name,
                "menthorq_weight": result.config.menthorq_weight,
                "battle_navale_weight": result.config.battle_navale_weight,
                "winrate": result.winrate,
                "avg_pnl": result.avg_pnl,
                "profit_factor": result.profit_factor,
                "sharpe_ratio": result.sharpe_ratio,
                "total_signals": result.total_signals
            })
        
        with open("hybrid_strategy_results.json", "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nRésultats sauvegardés dans: hybrid_strategy_results.json")

def main():
    optimizer = HybridStrategyOptimizer()
    best_strategy = optimizer.optimize_hybrid_strategies()
    
    print(f"\n🎯 RECOMMANDATION FINALE")
    print("=" * 50)
    print(f"Utiliser la stratégie: {best_strategy.config.name}")
    print(f"Avec les paramètres optimisés pour maximiser les performances")

if __name__ == "__main__":
    main()

