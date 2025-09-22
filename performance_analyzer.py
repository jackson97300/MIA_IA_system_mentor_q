#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALYSEUR DE PERFORMANCE TRADING
================================
Analyse les scenarios avec des metriques de performance pertinentes
pour optimiser les strategies de trading
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta

class TradingPerformanceAnalyzer:
    """Analyseur de performance trading avec metriques pertinentes"""
    
    def __init__(self):
        self.scenarios = ["bullish", "bearish", "sideways", "volatile", "breakout", "reversal"]
        self.results = {}
    
    def calculate_price_momentum(self, prices: List[float], periods: List[int] = [5, 10, 20]) -> Dict[str, float]:
        """Calcule le momentum des prix sur differentes periodes"""
        momentum = {}
        
        for period in periods:
            if len(prices) >= period:
                # Momentum = (Prix actuel - Prix il y a N periodes) / Prix il y a N periodes
                current_price = prices[-1]
                past_price = prices[-period]
                momentum[f"momentum_{period}"] = (current_price - past_price) / past_price * 100
            else:
                momentum[f"momentum_{period}"] = 0.0
        
        return momentum
    
    def calculate_volatility_metrics(self, prices: List[float]) -> Dict[str, float]:
        """Calcule les metriques de volatilite pertinentes"""
        if len(prices) < 2:
            return {}
        
        returns = np.diff(prices) / prices[:-1] * 100
        
        return {
            "volatility_daily": np.std(returns) * np.sqrt(1440),  # Volatilite annualisee (1440 min/jour)
            "volatility_hourly": np.std(returns) * np.sqrt(60),   # Volatilite horaire
            "max_drawdown": self.calculate_max_drawdown(prices),
            "sharpe_ratio": np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0,
            "var_95": np.percentile(returns, 5),  # Value at Risk 95%
            "var_99": np.percentile(returns, 1)   # Value at Risk 99%
        }
    
    def calculate_max_drawdown(self, prices: List[float]) -> float:
        """Calcule le drawdown maximum"""
        if len(prices) < 2:
            return 0.0
        
        peak = prices[0]
        max_dd = 0.0
        
        for price in prices:
            if price > peak:
                peak = price
            dd = (peak - price) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def analyze_menthorq_performance(self, scenario: str) -> Dict[str, Any]:
        """Analyse la performance des niveaux MenthorQ"""
        file_path = f"test_data/{scenario}/chart_3_menthorq_gamma_test_{scenario}_4h.jsonl"
        
        if not os.path.exists(file_path):
            return {"error": "Fichier non trouve"}
        
        gamma_data = []
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    gamma_data.append(data)
        
        if len(gamma_data) < 2:
            return {"error": "Donnees insuffisantes"}
        
        # Analyser l'evolution des niveaux
        level_performance = {}
        
        for level_name in gamma_data[0].keys():
            if level_name not in ["t", "sym", "type", "i", "chart"]:
                values = [data[level_name] for data in gamma_data]
                
                # Calculer la stabilite du niveau
                stability = 1.0 - (np.std(values) / np.mean(values)) if np.mean(values) > 0 else 0.0
                
                # Calculer la tendance du niveau
                trend = (values[-1] - values[0]) / values[0] * 100 if values[0] > 0 else 0.0
                
                level_performance[level_name] = {
                    "stability": stability,
                    "trend": trend,
                    "volatility": np.std(values) / np.mean(values) * 100 if np.mean(values) > 0 else 0.0,
                    "range": max(values) - min(values)
                }
        
        return {
            "scenario": scenario,
            "total_levels": len(level_performance),
            "level_performance": level_performance,
            "avg_stability": np.mean([lp["stability"] for lp in level_performance.values()]),
            "avg_trend": np.mean([lp["trend"] for lp in level_performance.values()])
        }
    
    def analyze_trading_signals(self, scenario: str) -> Dict[str, Any]:
        """Analyse les signaux de trading potentiels"""
        basedata_file = f"test_data/{scenario}/chart_3_basedata_test_{scenario}_4h.jsonl"
        vwap_file = f"test_data/{scenario}/chart_3_vwap_test_{scenario}_4h.jsonl"
        
        if not os.path.exists(basedata_file) or not os.path.exists(vwap_file):
            return {"error": "Fichiers non trouves"}
        
        # Charger les donnees
        basedata = []
        vwap_data = []
        
        with open(basedata_file, 'r') as f:
            for line in f:
                if line.strip():
                    basedata.append(json.loads(line))
        
        with open(vwap_file, 'r') as f:
            for line in f:
                if line.strip():
                    vwap_data.append(json.loads(line))
        
        if len(basedata) != len(vwap_data):
            return {"error": "Donnees incohérentes"}
        
        # Analyser les signaux
        signals = {
            "vwap_above": 0,      # Prix au-dessus VWAP
            "vwap_below": 0,      # Prix en-dessous VWAP
            "vwap_breakout": 0,   # Cassure VWAP
            "volume_spike": 0,    # Pic de volume
            "momentum_positive": 0,
            "momentum_negative": 0
        }
        
        prices = [bar["c"] for bar in basedata]
        volumes = [bar["v"] for bar in basedata]
        vwaps = [vwap["v"] for vwap in vwap_data]
        
        # Calculer le volume moyen
        avg_volume = np.mean(volumes)
        
        for i in range(1, len(basedata)):
            current_price = prices[i]
            current_vwap = vwaps[i]
            current_volume = volumes[i]
            prev_price = prices[i-1]
            
            # Signaux VWAP
            if current_price > current_vwap:
                signals["vwap_above"] += 1
            else:
                signals["vwap_below"] += 1
            
            # Cassure VWAP
            if (prev_price <= vwaps[i-1] and current_price > current_vwap) or \
               (prev_price >= vwaps[i-1] and current_price < current_vwap):
                signals["vwap_breakout"] += 1
            
            # Pic de volume
            if current_volume > avg_volume * 1.5:
                signals["volume_spike"] += 1
            
            # Momentum
            price_change = (current_price - prev_price) / prev_price * 100
            if price_change > 0.1:
                signals["momentum_positive"] += 1
            elif price_change < -0.1:
                signals["momentum_negative"] += 1
        
        # Calculer les ratios
        total_bars = len(basedata) - 1
        signal_ratios = {}
        for signal, count in signals.items():
            signal_ratios[signal] = count / total_bars * 100 if total_bars > 0 else 0
        
        return {
            "scenario": scenario,
            "total_bars": total_bars,
            "signals": signals,
            "signal_ratios": signal_ratios,
            "avg_volume": avg_volume
        }
    
    def calculate_risk_metrics(self, scenario: str) -> Dict[str, Any]:
        """Calcule les metriques de risque"""
        file_path = f"test_data/{scenario}/chart_3_basedata_test_{scenario}_4h.jsonl"
        
        if not os.path.exists(file_path):
            return {"error": "Fichier non trouve"}
        
        prices = []
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    prices.append(data["c"])
        
        if len(prices) < 2:
            return {"error": "Donnees insuffisantes"}
        
        returns = np.diff(prices) / prices[:-1] * 100
        
        return {
            "scenario": scenario,
            "volatility_metrics": self.calculate_volatility_metrics(prices),
            "momentum_metrics": self.calculate_price_momentum(prices),
            "risk_score": self.calculate_risk_score(returns),
            "trend_strength": self.calculate_trend_strength(prices)
        }
    
    def calculate_risk_score(self, returns: List[float]) -> float:
        """Calcule un score de risque (0-100)"""
        if len(returns) == 0:
            return 0.0
        
        volatility = np.std(returns)
        max_loss = abs(min(returns))
        var_95 = abs(np.percentile(returns, 5))
        
        # Score de risque base sur volatilite, perte max et VaR
        risk_score = min(100, (volatility * 10 + max_loss * 5 + var_95 * 3))
        return risk_score
    
    def calculate_trend_strength(self, prices: List[float]) -> float:
        """Calcule la force de la tendance (0-100)"""
        if len(prices) < 10:
            return 0.0
        
        # Utiliser une regression lineaire simple
        x = np.arange(len(prices))
        y = np.array(prices)
        
        # Calculer la pente
        slope = np.polyfit(x, y, 1)[0]
        
        # Normaliser la pente par rapport au prix moyen
        avg_price = np.mean(prices)
        normalized_slope = abs(slope) / avg_price * 100
        
        # Convertir en score 0-100
        trend_strength = min(100, normalized_slope * 1000)
        return trend_strength
    
    def analyze_all_scenarios(self):
        """Analyse tous les scenarios avec metriques de performance"""
        print("ANALYSE DE PERFORMANCE TRADING")
        print("=" * 60)
        
        for scenario in self.scenarios:
            print(f"\nAnalyse du scenario: {scenario.upper()}")
            print("-" * 40)
            
            # Analyser les signaux de trading
            signals_analysis = self.analyze_trading_signals(scenario)
            if "error" not in signals_analysis:
                print(f"Signaux VWAP au-dessus: {signals_analysis['signal_ratios']['vwap_above']:.1f}%")
                print(f"Signaux VWAP en-dessous: {signals_analysis['signal_ratios']['vwap_below']:.1f}%")
                print(f"Cassures VWAP: {signals_analysis['signal_ratios']['vwap_breakout']:.1f}%")
                print(f"Pics de volume: {signals_analysis['signal_ratios']['volume_spike']:.1f}%")
                print(f"Momentum positif: {signals_analysis['signal_ratios']['momentum_positive']:.1f}%")
                print(f"Momentum negatif: {signals_analysis['signal_ratios']['momentum_negative']:.1f}%")
            
            # Analyser les metriques de risque
            risk_analysis = self.calculate_risk_metrics(scenario)
            if "error" not in risk_analysis:
                vol_metrics = risk_analysis["volatility_metrics"]
                print(f"Volatilite horaire: {vol_metrics['volatility_hourly']:.2f}%")
                print(f"Max drawdown: {vol_metrics['max_drawdown']:.2f}%")
                print(f"Sharpe ratio: {vol_metrics['sharpe_ratio']:.3f}")
                print(f"VaR 95%: {vol_metrics['var_95']:.2f}%")
                print(f"Score de risque: {risk_analysis['risk_score']:.1f}/100")
                print(f"Force de tendance: {risk_analysis['trend_strength']:.1f}/100")
            
            # Analyser MenthorQ
            menthorq_analysis = self.analyze_menthorq_performance(scenario)
            if "error" not in menthorq_analysis:
                print(f"Stabilite MenthorQ: {menthorq_analysis['avg_stability']:.3f}")
                print(f"Tendance MenthorQ: {menthorq_analysis['avg_trend']:.2f}%")
            
            self.results[scenario] = {
                "signals": signals_analysis,
                "risk": risk_analysis,
                "menthorq": menthorq_analysis
            }
    
    def generate_performance_summary(self):
        """Genere un resume de performance"""
        print("\n" + "=" * 80)
        print("RESUME DE PERFORMANCE")
        print("=" * 80)
        
        # Tableau de performance
        print(f"{'Scenario':<12} {'Risque':<8} {'Tendance':<10} {'VWAP+':<8} {'Vol+':<8} {'MenthorQ':<10}")
        print("-" * 80)
        
        for scenario in self.scenarios:
            if scenario in self.results:
                risk = self.results[scenario]["risk"]
                signals = self.results[scenario]["signals"]
                menthorq = self.results[scenario]["menthorq"]
                
                if "error" not in risk and "error" not in signals and "error" not in menthorq:
                    risk_score = f"{risk['risk_score']:.1f}"
                    trend_strength = f"{risk['trend_strength']:.1f}"
                    vwap_above = f"{signals['signal_ratios']['vwap_above']:.1f}%"
                    volume_spike = f"{signals['signal_ratios']['volume_spike']:.1f}%"
                    menthorq_stability = f"{menthorq['avg_stability']:.3f}"
                    
                    print(f"{scenario:<12} {risk_score:<8} {trend_strength:<10} {vwap_above:<8} {volume_spike:<8} {menthorq_stability:<10}")
    
    def suggest_optimization_strategies(self):
        """Suggere des strategies d'optimisation"""
        print("\n" + "=" * 80)
        print("STRATEGIES D'OPTIMISATION SUGGEREES")
        print("=" * 80)
        
        # Analyser les patterns
        high_risk_scenarios = []
        high_volatility_scenarios = []
        stable_menthorq_scenarios = []
        
        for scenario in self.scenarios:
            if scenario in self.results:
                risk = self.results[scenario]["risk"]
                menthorq = self.results[scenario]["menthorq"]
                
                if "error" not in risk and "error" not in menthorq:
                    if risk["risk_score"] > 50:
                        high_risk_scenarios.append(scenario)
                    
                    if risk["volatility_metrics"]["volatility_hourly"] > 2.0:
                        high_volatility_scenarios.append(scenario)
                    
                    if menthorq["avg_stability"] > 0.8:
                        stable_menthorq_scenarios.append(scenario)
        
        print("Scenarios a haut risque (score > 50):")
        for scenario in high_risk_scenarios:
            print(f"- {scenario}: Score {self.results[scenario]['risk']['risk_score']:.1f}")
        
        print("\nScenarios a haute volatilite (>2%/h):")
        for scenario in high_volatility_scenarios:
            vol = self.results[scenario]['risk']['volatility_metrics']['volatility_hourly']
            print(f"- {scenario}: {vol:.2f}%/h")
        
        print("\nScenarios avec MenthorQ stable (>0.8):")
        for scenario in stable_menthorq_scenarios:
            stability = self.results[scenario]['menthorq']['avg_stability']
            print(f"- {scenario}: {stability:.3f}")
        
        # Suggestions d'optimisation
        print("\nSuggestions d'optimisation:")
        print("1. Ajuster les seuils de risque selon le scenario")
        print("2. Utiliser MenthorQ comme filtre principal pour les scenarios stables")
        print("3. Augmenter la frequence de trading pour les scenarios volatils")
        print("4. Reduire la taille des positions pour les scenarios a haut risque")

def main():
    analyzer = TradingPerformanceAnalyzer()
    analyzer.analyze_all_scenarios()
    analyzer.generate_performance_summary()
    analyzer.suggest_optimization_strategies()

if __name__ == "__main__":
    main()

