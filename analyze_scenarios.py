#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALYSEUR COMPARATIF DES SCENARIOS
==================================
Compare les 6 scenarios generes pour optimiser les seuils
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any
import matplotlib.pyplot as plt

class ScenarioAnalyzer:
    """Analyseur des scenarios de test"""
    
    def __init__(self):
        self.scenarios = ["bullish", "bearish", "sideways", "volatile", "breakout", "reversal"]
        self.results = {}
    
    def analyze_basedata(self, scenario: str) -> Dict[str, Any]:
        """Analyse les donnees basedata d'un scenario"""
        file_path = f"test_data/{scenario}/chart_3_basedata_test_{scenario}_4h.jsonl"
        
        if not os.path.exists(file_path):
            return {"error": "Fichier non trouve"}
        
        prices = []
        volumes = []
        spreads = []
        
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    prices.append(data['c'])
                    volumes.append(data['v'])
                    spreads.append(data['h'] - data['l'])
        
        if not prices:
            return {"error": "Aucune donnee"}
        
        return {
            "scenario": scenario,
            "price_stats": {
                "min": min(prices),
                "max": max(prices),
                "mean": np.mean(prices),
                "std": np.std(prices),
                "range": max(prices) - min(prices),
                "volatility": np.std(prices) / np.mean(prices) * 100
            },
            "volume_stats": {
                "min": min(volumes),
                "max": max(volumes),
                "mean": np.mean(volumes),
                "std": np.std(volumes)
            },
            "spread_stats": {
                "min": min(spreads),
                "max": max(spreads),
                "mean": np.mean(spreads),
                "std": np.std(spreads)
            },
            "trend": self.calculate_trend(prices),
            "total_bars": len(prices)
        }
    
    def calculate_trend(self, prices: List[float]) -> str:
        """Calcule la tendance des prix"""
        if len(prices) < 2:
            return "unknown"
        
        start_price = prices[0]
        end_price = prices[-1]
        change_pct = (end_price - start_price) / start_price * 100
        
        if change_pct > 0.5:
            return "bullish"
        elif change_pct < -0.5:
            return "bearish"
        else:
            return "sideways"
    
    def analyze_menthorq_gamma(self, scenario: str) -> Dict[str, Any]:
        """Analyse les donnees MenthorQ Gamma"""
        file_path = f"test_data/{scenario}/chart_3_menthorq_gamma_test_{scenario}_4h.jsonl"
        
        if not os.path.exists(file_path):
            return {"error": "Fichier non trouve"}
        
        gamma_levels = []
        updates = 0
        
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    updates += 1
                    
                    # Extraire les niveaux gamma
                    levels = {}
                    for key, value in data.items():
                        if key not in ["t", "sym", "type", "i", "chart"]:
                            levels[key] = value
                    
                    gamma_levels.append(levels)
        
        if not gamma_levels:
            return {"error": "Aucune donnee"}
        
        # Analyser l'evolution des niveaux
        level_changes = {}
        for level_name in gamma_levels[0].keys():
            values = [levels[level_name] for levels in gamma_levels]
            level_changes[level_name] = {
                "min": min(values),
                "max": max(values),
                "range": max(values) - min(values),
                "volatility": np.std(values) / np.mean(values) * 100 if np.mean(values) > 0 else 0
            }
        
        return {
            "scenario": scenario,
            "total_updates": updates,
            "level_changes": level_changes,
            "avg_volatility": np.mean([lc["volatility"] for lc in level_changes.values()])
        }
    
    def analyze_correlation(self, scenario: str) -> Dict[str, Any]:
        """Analyse les donnees de correlation"""
        file_path = f"test_data/{scenario}/chart_3_correlation_unified_test_{scenario}_4h.jsonl"
        
        if not os.path.exists(file_path):
            return {"error": "Fichier non trouve"}
        
        correlations = []
        
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    correlations.append(data['cc'])
        
        if not correlations:
            return {"error": "Aucune donnee"}
        
        return {
            "scenario": scenario,
            "correlation_stats": {
                "min": min(correlations),
                "max": max(correlations),
                "mean": np.mean(correlations),
                "std": np.std(correlations),
                "range": max(correlations) - min(correlations)
            },
            "total_points": len(correlations)
        }
    
    def analyze_all_scenarios(self):
        """Analyse tous les scenarios"""
        print("ANALYSE COMPARATIVE DES SCENARIOS")
        print("=" * 50)
        
        for scenario in self.scenarios:
            print(f"\nAnalyse du scenario: {scenario.upper()}")
            print("-" * 30)
            
            # Analyser basedata
            basedata_analysis = self.analyze_basedata(scenario)
            if "error" not in basedata_analysis:
                print(f"Prix: {basedata_analysis['price_stats']['min']:.2f} - {basedata_analysis['price_stats']['max']:.2f}")
                print(f"Volatilite: {basedata_analysis['price_stats']['volatility']:.2f}%")
                print(f"Tendance: {basedata_analysis['trend']}")
                print(f"Volume moyen: {basedata_analysis['volume_stats']['mean']:.0f}")
            
            # Analyser MenthorQ
            menthorq_analysis = self.analyze_menthorq_gamma(scenario)
            if "error" not in menthorq_analysis:
                print(f"MenthorQ updates: {menthorq_analysis['total_updates']}")
                print(f"Volatilite niveaux: {menthorq_analysis['avg_volatility']:.2f}%")
            
            # Analyser correlation
            corr_analysis = self.analyze_correlation(scenario)
            if "error" not in corr_analysis:
                print(f"Correlation: {corr_analysis['correlation_stats']['mean']:.3f} ± {corr_analysis['correlation_stats']['std']:.3f}")
            
            self.results[scenario] = {
                "basedata": basedata_analysis,
                "menthorq": menthorq_analysis,
                "correlation": corr_analysis
            }
    
    def generate_comparison_table(self):
        """Genere un tableau de comparaison"""
        print("\n" + "=" * 80)
        print("TABLEAU DE COMPARAISON")
        print("=" * 80)
        
        # En-tete du tableau
        print(f"{'Scenario':<12} {'Tendance':<10} {'Volatilite':<12} {'Prix Range':<15} {'MenthorQ':<10} {'Correlation':<12}")
        print("-" * 80)
        
        for scenario in self.scenarios:
            if scenario in self.results:
                basedata = self.results[scenario]["basedata"]
                menthorq = self.results[scenario]["menthorq"]
                corr = self.results[scenario]["correlation"]
                
                if "error" not in basedata and "error" not in menthorq and "error" not in corr:
                    trend = basedata["trend"]
                    volatility = f"{basedata['price_stats']['volatility']:.1f}%"
                    price_range = f"{basedata['price_stats']['range']:.1f}"
                    menthorq_updates = str(menthorq["total_updates"])
                    correlation = f"{corr['correlation_stats']['mean']:.3f}"
                    
                    print(f"{scenario:<12} {trend:<10} {volatility:<12} {price_range:<15} {menthorq_updates:<10} {correlation:<12}")
    
    def suggest_optimizations(self):
        """Suggere des optimisations basees sur l'analyse"""
        print("\n" + "=" * 80)
        print("SUGGESTIONS D'OPTIMISATION")
        print("=" * 80)
        
        # Analyser les patterns
        volatilities = []
        correlations = []
        
        for scenario in self.scenarios:
            if scenario in self.results:
                basedata = self.results[scenario]["basedata"]
                corr = self.results[scenario]["correlation"]
                
                if "error" not in basedata and "error" not in corr:
                    volatilities.append(basedata["price_stats"]["volatility"])
                    correlations.append(corr["correlation_stats"]["mean"])
        
        if volatilities and correlations:
            avg_volatility = np.mean(volatilities)
            avg_correlation = np.mean(correlations)
            
            print(f"Volatilite moyenne: {avg_volatility:.2f}%")
            print(f"Correlation moyenne: {avg_correlation:.3f}")
            
            # Suggestions
            print("\nSuggestions de seuils:")
            print(f"- Seuil volatilite basse: < {avg_volatility * 0.7:.1f}%")
            print(f"- Seuil volatilite haute: > {avg_volatility * 1.3:.1f}%")
            print(f"- Seuil correlation forte: > {avg_correlation + 0.1:.3f}")
            print(f"- Seuil correlation faible: < {avg_correlation - 0.1:.3f}")
            
            # Scenarios extremes
            print("\nScenarios extremes identifies:")
            for scenario in self.scenarios:
                if scenario in self.results:
                    basedata = self.results[scenario]["basedata"]
                    if "error" not in basedata:
                        vol = basedata["price_stats"]["volatility"]
                        if vol > avg_volatility * 1.5:
                            print(f"- {scenario}: Volatilite tres elevee ({vol:.1f}%)")
                        elif vol < avg_volatility * 0.5:
                            print(f"- {scenario}: Volatilite tres faible ({vol:.1f}%)")

def main():
    analyzer = ScenarioAnalyzer()
    analyzer.analyze_all_scenarios()
    analyzer.generate_comparison_table()
    analyzer.suggest_optimizations()

if __name__ == "__main__":
    main()

