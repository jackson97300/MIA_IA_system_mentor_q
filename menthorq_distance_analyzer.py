#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALYSEUR DE DISTANCES MENTHORQ
===============================
Analyse les distances des niveaux MenthorQ lors des trades
et calcule les statistiques de performance
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class MenthorQLevel:
    """Niveau MenthorQ avec ses propriétés"""
    name: str
    value: float
    type: str  # "support", "resistance", "gamma", "blind_spot"
    distance_to_price: float
    strength: float

@dataclass
class TradeAnalysis:
    """Analyse d'un trade avec distances MenthorQ"""
    entry_price: float
    exit_price: float
    entry_time: float
    exit_time: float
    direction: str  # "long" ou "short"
    pnl: float
    pnl_pct: float
    nearest_support: MenthorQLevel
    nearest_resistance: MenthorQLevel
    support_distance: float
    resistance_distance: float
    menthorq_signal_strength: float
    trade_duration: float  # en minutes

class MenthorQDistanceAnalyzer:
    """Analyseur des distances MenthorQ pour optimiser les trades"""
    
    def __init__(self):
        self.scenarios = ["bullish", "bearish", "sideways", "volatile", "breakout", "reversal"]
        self.menthorq_levels = {}
        self.trade_analyses = {}
    
    def load_menthorq_data(self, scenario: str) -> List[Dict]:
        """Charge les données MenthorQ pour un scénario"""
        file_path = f"test_data/{scenario}/chart_3_menthorq_gamma_test_{scenario}_4h.jsonl"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = []
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
                return data
        except FileNotFoundError:
            print(f"Fichier non trouvé: {file_path}")
            return []
    
    def load_price_data(self, scenario: str) -> List[Dict]:
        """Charge les données de prix pour un scénario"""
        file_path = f"test_data/{scenario}/chart_3_basedata_test_{scenario}_4h.jsonl"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = []
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
                return data
        except FileNotFoundError:
            print(f"Fichier non trouvé: {file_path}")
            return []
    
    def extract_menthorq_levels(self, menthorq_data: List[Dict]) -> List[MenthorQLevel]:
        """Extrait les niveaux MenthorQ d'une entrée de données"""
        if not menthorq_data:
            return []
        
        # Prendre la dernière entrée (la plus récente)
        latest_data = menthorq_data[-1]
        levels = []
        
        # Extraire les niveaux de support (put_support)
        for key, value in latest_data.items():
            if key.startswith("put_support") and isinstance(value, (int, float)):
                levels.append(MenthorQLevel(
                    name=key,
                    value=value,
                    type="support",
                    distance_to_price=0.0,  # Sera calculé plus tard
                    strength=0.8  # Support généralement fort
                ))
        
        # Extraire les niveaux de résistance (call_resistance)
        for key, value in latest_data.items():
            if key.startswith("call_resistance") and isinstance(value, (int, float)):
                levels.append(MenthorQLevel(
                    name=key,
                    value=value,
                    type="resistance",
                    distance_to_price=0.0,
                    strength=0.8
                ))
        
        # Extraire les niveaux gamma (gbl_, gea_, gex_)
        for key, value in latest_data.items():
            if key.startswith(("gbl_", "gea_", "gex_")) and isinstance(value, (int, float)):
                level_type = "gamma"
                if key.startswith("gbl_"):
                    level_type = "gamma_balance"
                elif key.startswith("gea_"):
                    level_type = "gamma_above"
                elif key.startswith("gex_"):
                    level_type = "gamma_excess"
                
                levels.append(MenthorQLevel(
                    name=key,
                    value=value,
                    type=level_type,
                    distance_to_price=0.0,
                    strength=0.6  # Gamma moins fort que support/resistance
                ))
        
        # Extraire les niveaux blind spots (bl_)
        for key, value in latest_data.items():
            if key.startswith("bl_") and isinstance(value, (int, float)):
                levels.append(MenthorQLevel(
                    name=key,
                    value=value,
                    type="blind_spot",
                    distance_to_price=0.0,
                    strength=0.4  # Blind spots moins fiables
                ))
        
        return levels
    
    def calculate_distances_to_price(self, levels: List[MenthorQLevel], current_price: float) -> List[MenthorQLevel]:
        """Calcule les distances de chaque niveau au prix actuel"""
        for level in levels:
            level.distance_to_price = abs(level.value - current_price)
        return levels
    
    def find_nearest_levels(self, levels: List[MenthorQLevel], current_price: float) -> Tuple[MenthorQLevel, MenthorQLevel]:
        """Trouve les niveaux de support et résistance les plus proches"""
        supports = [l for l in levels if l.value < current_price and l.type in ["support", "gamma_balance"]]
        resistances = [l for l in levels if l.value > current_price and l.type in ["resistance", "gamma_balance"]]
        
        nearest_support = min(supports, key=lambda x: x.distance_to_price) if supports else None
        nearest_resistance = min(resistances, key=lambda x: x.distance_to_price) if resistances else None
        
        # Si pas de niveau spécifique, utiliser les niveaux gamma les plus proches
        if not nearest_support:
            supports = [l for l in levels if l.value < current_price]
            nearest_support = min(supports, key=lambda x: x.distance_to_price) if supports else None
        
        if not nearest_resistance:
            resistances = [l for l in levels if l.value > current_price]
            nearest_resistance = min(resistances, key=lambda x: x.distance_to_price) if resistances else None
        
        return nearest_support, nearest_resistance
    
    def simulate_trades(self, scenario: str) -> List[TradeAnalysis]:
        """Simule des trades basés sur les données de prix et MenthorQ"""
        menthorq_data = self.load_menthorq_data(scenario)
        price_data = self.load_price_data(scenario)
        
        if not menthorq_data or not price_data:
            return []
        
        trades = []
        
        # Simuler des trades sur des périodes de 30 minutes
        trade_interval = 30  # minutes
        current_time = 0
        
        while current_time < len(price_data) - 60:  # Laisser 60 minutes pour la sortie
            entry_bar = price_data[current_time]
            entry_price = entry_bar["c"]
            entry_time = entry_bar["t"]
            
            # Extraire les niveaux MenthorQ
            levels = self.extract_menthorq_levels(menthorq_data)
            levels = self.calculate_distances_to_price(levels, entry_price)
            
            # Trouver les niveaux les plus proches
            nearest_support, nearest_resistance = self.find_nearest_levels(levels, entry_price)
            
            if nearest_support and nearest_resistance:
                # Calculer les distances
                support_distance = (entry_price - nearest_support.value) / entry_price * 100
                resistance_distance = (nearest_resistance.value - entry_price) / entry_price * 100
                
                # Déterminer la direction du trade basée sur les distances
                if support_distance < resistance_distance:
                    direction = "long"
                    target_price = nearest_resistance.value
                    stop_price = nearest_support.value
                else:
                    direction = "short"
                    target_price = nearest_support.value
                    stop_price = nearest_resistance.value
                
                # Trouver la sortie (30 minutes plus tard)
                exit_time_idx = min(current_time + trade_interval, len(price_data) - 1)
                exit_bar = price_data[exit_time_idx]
                exit_price = exit_bar["c"]
                exit_time = exit_bar["t"]
                
                # Calculer le PnL
                if direction == "long":
                    pnl = exit_price - entry_price
                    pnl_pct = (exit_price - entry_price) / entry_price * 100
                else:
                    pnl = entry_price - exit_price
                    pnl_pct = (entry_price - exit_price) / entry_price * 100
                
                # Calculer la force du signal MenthorQ
                menthorq_signal_strength = self.calculate_menthorq_signal_strength(
                    levels, entry_price, direction
                )
                
                # Durée du trade
                trade_duration = (exit_time - entry_time) * 24 * 60  # en minutes
                
                trade = TradeAnalysis(
                    entry_price=entry_price,
                    exit_price=exit_price,
                    entry_time=entry_time,
                    exit_time=exit_time,
                    direction=direction,
                    pnl=pnl,
                    pnl_pct=pnl_pct,
                    nearest_support=nearest_support,
                    nearest_resistance=nearest_resistance,
                    support_distance=support_distance,
                    resistance_distance=resistance_distance,
                    menthorq_signal_strength=menthorq_signal_strength,
                    trade_duration=trade_duration
                )
                
                trades.append(trade)
            
            current_time += trade_interval
        
        return trades
    
    def calculate_menthorq_signal_strength(self, levels: List[MenthorQLevel], price: float, direction: str) -> float:
        """Calcule la force du signal MenthorQ"""
        if not levels:
            return 0.0
        
        # Compter les niveaux favorables
        favorable_levels = 0
        total_levels = len(levels)
        
        for level in levels:
            if direction == "long":
                # Pour un long, on veut des supports proches et des résistances éloignées
                if level.type in ["support", "gamma_balance"] and level.value < price:
                    distance_pct = (price - level.value) / price * 100
                    if distance_pct < 2.0:  # Support proche
                        favorable_levels += 1
                elif level.type in ["resistance", "gamma_balance"] and level.value > price:
                    distance_pct = (level.value - price) / price * 100
                    if distance_pct > 1.0:  # Résistance éloignée
                        favorable_levels += 1
            else:
                # Pour un short, on veut des résistances proches et des supports éloignés
                if level.type in ["resistance", "gamma_balance"] and level.value > price:
                    distance_pct = (level.value - price) / price * 100
                    if distance_pct < 2.0:  # Résistance proche
                        favorable_levels += 1
                elif level.type in ["support", "gamma_balance"] and level.value < price:
                    distance_pct = (price - level.value) / price * 100
                    if distance_pct > 1.0:  # Support éloigné
                        favorable_levels += 1
        
        return favorable_levels / total_levels if total_levels > 0 else 0.0
    
    def analyze_scenario_distances(self, scenario: str) -> Dict[str, Any]:
        """Analyse les distances MenthorQ pour un scénario"""
        trades = self.simulate_trades(scenario)
        
        if not trades:
            return {"error": "Aucun trade simulé"}
        
        # Statistiques des distances
        support_distances = [t.support_distance for t in trades]
        resistance_distances = [t.resistance_distance for t in trades]
        pnl_pcts = [t.pnl_pct for t in trades]
        signal_strengths = [t.menthorq_signal_strength for t in trades]
        
        # Trades gagnants et perdants
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        
        # Analyse par distance
        distance_analysis = self.analyze_distance_performance(trades)
        
        return {
            "scenario": scenario,
            "total_trades": len(trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "winrate": len(winning_trades) / len(trades) * 100,
            "avg_pnl": np.mean(pnl_pcts),
            "avg_support_distance": np.mean(support_distances),
            "avg_resistance_distance": np.mean(resistance_distances),
            "avg_signal_strength": np.mean(signal_strengths),
            "distance_analysis": distance_analysis,
            "trades": trades
        }
    
    def analyze_distance_performance(self, trades: List[TradeAnalysis]) -> Dict[str, Any]:
        """Analyse la performance par distance des niveaux"""
        # Grouper les trades par distance
        distance_groups = {
            "very_close": [],    # < 0.5%
            "close": [],         # 0.5% - 1.0%
            "medium": [],        # 1.0% - 2.0%
            "far": []            # > 2.0%
        }
        
        for trade in trades:
            min_distance = min(trade.support_distance, trade.resistance_distance)
            
            if min_distance < 0.5:
                distance_groups["very_close"].append(trade)
            elif min_distance < 1.0:
                distance_groups["close"].append(trade)
            elif min_distance < 2.0:
                distance_groups["medium"].append(trade)
            else:
                distance_groups["far"].append(trade)
        
        # Analyser chaque groupe
        analysis = {}
        for group_name, group_trades in distance_groups.items():
            if group_trades:
                winning = [t for t in group_trades if t.pnl > 0]
                analysis[group_name] = {
                    "total_trades": len(group_trades),
                    "winning_trades": len(winning),
                    "winrate": len(winning) / len(group_trades) * 100,
                    "avg_pnl": np.mean([t.pnl_pct for t in group_trades]),
                    "avg_signal_strength": np.mean([t.menthorq_signal_strength for t in group_trades])
                }
            else:
                analysis[group_name] = {
                    "total_trades": 0,
                    "winning_trades": 0,
                    "winrate": 0,
                    "avg_pnl": 0,
                    "avg_signal_strength": 0
                }
        
        return analysis
    
    def generate_distance_report(self):
        """Génère un rapport complet des distances MenthorQ"""
        print("ANALYSE DES DISTANCES MENTHORQ")
        print("=" * 80)
        
        all_analyses = {}
        
        # Analyser tous les scénarios
        for scenario in self.scenarios:
            print(f"\nAnalyse du scénario: {scenario.upper()}")
            print("-" * 40)
            
            analysis = self.analyze_scenario_distances(scenario)
            all_analyses[scenario] = analysis
            
            if "error" not in analysis:
                print(f"Total trades: {analysis['total_trades']}")
                print(f"Trades gagnants: {analysis['winning_trades']}")
                print(f"Winrate: {analysis['winrate']:.1f}%")
                print(f"PnL moyen: {analysis['avg_pnl']:.2f}%")
                print(f"Distance support moyenne: {analysis['avg_support_distance']:.2f}%")
                print(f"Distance résistance moyenne: {analysis['avg_resistance_distance']:.2f}%")
                print(f"Force signal moyenne: {analysis['avg_signal_strength']:.3f}")
                
                # Analyse par distance
                print("\nPerformance par distance:")
                for distance_type, perf in analysis['distance_analysis'].items():
                    if perf['total_trades'] > 0:
                        print(f"  {distance_type}: {perf['winrate']:.1f}% winrate, "
                              f"{perf['avg_pnl']:.2f}% PnL, {perf['total_trades']} trades")
        
        # Statistiques globales
        print("\n" + "=" * 80)
        print("STATISTIQUES GLOBALES")
        print("=" * 80)
        
        # Calculer les moyennes globales
        total_trades = sum(a.get('total_trades', 0) for a in all_analyses.values() if 'error' not in a)
        total_winning = sum(a.get('winning_trades', 0) for a in all_analyses.values() if 'error' not in a)
        global_winrate = (total_winning / total_trades * 100) if total_trades > 0 else 0
        
        avg_pnl = np.mean([a.get('avg_pnl', 0) for a in all_analyses.values() if 'error' not in a])
        avg_support_dist = np.mean([a.get('avg_support_distance', 0) for a in all_analyses.values() if 'error' not in a])
        avg_resistance_dist = np.mean([a.get('avg_resistance_distance', 0) for a in all_analyses.values() if 'error' not in a])
        avg_signal_strength = np.mean([a.get('avg_signal_strength', 0) for a in all_analyses.values() if 'error' not in a])
        
        print(f"Total trades simulés: {total_trades}")
        print(f"Winrate global: {global_winrate:.1f}%")
        print(f"PnL moyen global: {avg_pnl:.2f}%")
        print(f"Distance support moyenne: {avg_support_dist:.2f}%")
        print(f"Distance résistance moyenne: {avg_resistance_dist:.2f}%")
        print(f"Force signal moyenne: {avg_signal_strength:.3f}")
        
        # Tableau de comparaison
        print(f"\n{'Scénario':<12} {'Trades':<8} {'Winrate':<8} {'PnL':<8} {'Dist.Sup':<8} {'Dist.Res':<8} {'Signal':<8}")
        print("-" * 80)
        
        for scenario, analysis in all_analyses.items():
            if 'error' not in analysis:
                print(f"{scenario:<12} {analysis['total_trades']:<8} {analysis['winrate']:<8.1f}% "
                      f"{analysis['avg_pnl']:<8.2f}% {analysis['avg_support_distance']:<8.2f}% "
                      f"{analysis['avg_resistance_distance']:<8.2f}% {analysis['avg_signal_strength']:<8.3f}")
        
        # Recommandations
        print("\n" + "=" * 80)
        print("RECOMMANDATIONS BASÉES SUR LES DISTANCES")
        print("=" * 80)
        
        # Analyser les meilleures distances
        best_distance_performance = {}
        for scenario, analysis in all_analyses.items():
            if 'error' not in analysis:
                for distance_type, perf in analysis['distance_analysis'].items():
                    if perf['total_trades'] > 0:
                        if distance_type not in best_distance_performance:
                            best_distance_performance[distance_type] = []
                        best_distance_performance[distance_type].append(perf['winrate'])
        
        print("Winrate moyen par distance:")
        for distance_type, winrates in best_distance_performance.items():
            avg_winrate = np.mean(winrates)
            print(f"  {distance_type}: {avg_winrate:.1f}%")
        
        # Sauvegarder les résultats
        self.save_distance_analysis(all_analyses)
    
    def save_distance_analysis(self, analyses: Dict[str, Any]):
        """Sauvegarde l'analyse des distances"""
        # Préparer les données pour la sauvegarde
        save_data = {}
        for scenario, analysis in analyses.items():
            if 'error' not in analysis:
                save_data[scenario] = {
                    "total_trades": analysis['total_trades'],
                    "winning_trades": analysis['winning_trades'],
                    "winrate": analysis['winrate'],
                    "avg_pnl": analysis['avg_pnl'],
                    "avg_support_distance": analysis['avg_support_distance'],
                    "avg_resistance_distance": analysis['avg_resistance_distance'],
                    "avg_signal_strength": analysis['avg_signal_strength'],
                    "distance_analysis": analysis['distance_analysis']
                }
        
        with open("menthorq_distance_analysis.json", "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nAnalyse des distances sauvegardée dans: menthorq_distance_analysis.json")

def main():
    analyzer = MenthorQDistanceAnalyzer()
    analyzer.generate_distance_report()

if __name__ == "__main__":
    main()

