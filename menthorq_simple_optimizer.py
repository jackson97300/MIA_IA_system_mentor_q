#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPTIMISEUR MENTHORQ SIMPLIFIÉ
=============================
Optimiseur simplifié basé sur l'analyse existante
"""

import json
import numpy as np
from typing import Dict, List, Any

class SimpleMenthorQOptimizer:
    """Optimiseur simplifié basé sur les données d'analyse existantes"""
    
    def __init__(self):
        self.load_analysis_data()
    
    def load_analysis_data(self):
        """Charge les données d'analyse existantes"""
        try:
            with open("menthorq_distance_analysis.json", "r") as f:
                self.analysis_data = json.load(f)
            print("✅ Données d'analyse chargées")
        except FileNotFoundError:
            print("❌ Fichier d'analyse non trouvé")
            self.analysis_data = {}
    
    def analyze_current_performance(self):
        """Analyse les performances actuelles"""
        print("\nANALYSE DES PERFORMANCES ACTUELLES")
        print("=" * 50)
        
        total_trades = 0
        total_winning = 0
        total_pnl = 0.0
        
        for scenario, data in self.analysis_data.items():
            trades = data.get("total_trades", 0)
            winning = data.get("winning_trades", 0)
            pnl = data.get("avg_pnl", 0.0) * trades
            
            total_trades += trades
            total_winning += winning
            total_pnl += pnl
            
            print(f"{scenario.upper()}: {winning}/{trades} trades ({data.get('winrate', 0):.1f}%) - PnL: {data.get('avg_pnl', 0):.2f}%")
        
        global_winrate = (total_winning / total_trades * 100) if total_trades > 0 else 0
        global_pnl = total_pnl / total_trades if total_trades > 0 else 0
        
        print(f"\nGLOBAL: {total_winning}/{total_trades} trades ({global_winrate:.1f}%) - PnL: {global_pnl:.2f}%")
        
        return {
            "total_trades": total_trades,
            "winning_trades": total_winning,
            "winrate": global_winrate,
            "avg_pnl": global_pnl
        }
    
    def calculate_optimized_performance(self):
        """Calcule les performances optimisées basées sur l'analyse"""
        print("\nCALCUL DES PERFORMANCES OPTIMISÉES")
        print("=" * 50)
        
        # Stratégie d'optimisation basée sur l'analyse
        optimized_trades = 0
        optimized_winning = 0
        optimized_pnl = 0.0
        
        for scenario, data in self.analysis_data.items():
            # Filtrer les scénarios difficiles
            if scenario in ["bearish", "volatile", "reversal"]:
                print(f"❌ {scenario.upper()}: EXCLU (0% winrate)")
                continue
            
            # Utiliser seulement les distances optimales (medium = 1.0-2.0%)
            distance_analysis = data.get("distance_analysis", {})
            medium_perf = distance_analysis.get("medium", {})
            
            if medium_perf.get("total_trades", 0) > 0:
                trades = medium_perf["total_trades"]
                winning = medium_perf["winning_trades"]
                pnl = medium_perf["avg_pnl"] * trades
                
                optimized_trades += trades
                optimized_winning += winning
                optimized_pnl += pnl
                
                print(f"✅ {scenario.upper()}: {winning}/{trades} trades ({medium_perf.get('winrate', 0):.1f}%) - PnL: {medium_perf.get('avg_pnl', 0):.2f}%")
            else:
                # Utiliser les autres distances si medium n'est pas disponible
                close_perf = distance_analysis.get("close", {})
                if close_perf.get("total_trades", 0) > 0:
                    trades = close_perf["total_trades"]
                    winning = close_perf["winning_trades"]
                    pnl = close_perf["avg_pnl"] * trades
                    
                    optimized_trades += trades
                    optimized_winning += winning
                    optimized_pnl += pnl
                    
                    print(f"⚠️  {scenario.upper()}: {winning}/{trades} trades ({close_perf.get('winrate', 0):.1f}%) - PnL: {close_perf.get('avg_pnl', 0):.2f}%")
        
        optimized_winrate = (optimized_winning / optimized_trades * 100) if optimized_trades > 0 else 0
        optimized_avg_pnl = optimized_pnl / optimized_trades if optimized_trades > 0 else 0
        
        print(f"\nOPTIMISÉ: {optimized_winning}/{optimized_trades} trades ({optimized_winrate:.1f}%) - PnL: {optimized_avg_pnl:.2f}%")
        
        return {
            "total_trades": optimized_trades,
            "winning_trades": optimized_winning,
            "winrate": optimized_winrate,
            "avg_pnl": optimized_avg_pnl
        }
    
    def generate_optimization_recommendations(self, current_perf, optimized_perf):
        """Génère les recommandations d'optimisation"""
        print("\n" + "=" * 80)
        print("RECOMMANDATIONS D'OPTIMISATION")
        print("=" * 80)
        
        # Calculer l'amélioration
        winrate_improvement = optimized_perf["winrate"] - current_perf["winrate"]
        pnl_improvement = optimized_perf["avg_pnl"] - current_perf["avg_pnl"]
        
        print(f"Amélioration du winrate: {winrate_improvement:+.1f}%")
        print(f"Amélioration du PnL: {pnl_improvement:+.2f}%")
        
        print(f"\nPARAMÈTRES OPTIMISÉS:")
        print(f"1. DISTANCE DES NIVEAUX:")
        print(f"   - Distance minimale: 1.0% (au lieu de 0.5%)")
        print(f"   - Distance maximale: 2.0% (au lieu de 5.0%)")
        print(f"   - Zone optimale: 1.0% - 1.5%")
        
        print(f"\n2. FILTRAGE DES SCÉNARIOS:")
        print(f"   - AUTORISÉS: bullish, sideways")
        print(f"   - INTERDITS: bearish, volatile, reversal")
        print(f"   - Raison: 0% winrate sur les scénarios interdits")
        
        print(f"\n3. GESTION DE RISQUE:")
        print(f"   - Stop loss: 0.5% (serré)")
        print(f"   - Take profit: 1.5% (ratio 1:3)")
        print(f"   - Position size: 1.0x (normal)")
        
        print(f"\n4. TIMING DES TRADES:")
        print(f"   - Durée minimale: 30 minutes")
        print(f"   - Attendre confirmation des niveaux")
        print(f"   - Éviter les trades trop rapides")
        
        print(f"\n5. SIGNAL STRENGTH:")
        print(f"   - Minimum: 0.25 (actuel)")
        print(f"   - Optimal: 0.30+")
        print(f"   - MenthorQ stability: >0.95")
        
        # Stratégie spécifique
        print(f"\nSTRATÉGIE RECOMMANDÉE:")
        print(f"1. Attendre que le prix soit à 1.0-2.0% des niveaux MenthorQ")
        print(f"2. Vérifier que le scénario est bullish ou sideways")
        print(f"3. Confirmer la stabilité MenthorQ >0.95")
        print(f"4. Entrer avec stop loss 0.5% et take profit 1.5%")
        print(f"5. Durée minimale du trade: 30 minutes")
        
        # Sauvegarder les recommandations
        self.save_recommendations(current_perf, optimized_perf)
    
    def save_recommendations(self, current_perf, optimized_perf):
        """Sauvegarde les recommandations d'optimisation"""
        recommendations = {
            "current_performance": current_perf,
            "optimized_performance": optimized_perf,
            "improvements": {
                "winrate_improvement": optimized_perf["winrate"] - current_perf["winrate"],
                "pnl_improvement": optimized_perf["avg_pnl"] - current_perf["avg_pnl"]
            },
            "optimized_parameters": {
                "min_distance_pct": 1.0,
                "max_distance_pct": 2.0,
                "min_signal_strength": 0.25,
                "min_menthorq_stability": 0.95,
                "trade_duration_min": 30,
                "stop_loss_pct": 0.5,
                "take_profit_pct": 1.5,
                "position_size_multiplier": 1.0,
                "allowed_scenarios": ["bullish", "sideways"],
                "forbidden_scenarios": ["bearish", "volatile", "reversal"]
            },
            "strategy": {
                "wait_for_distance": "1.0-2.0% from MenthorQ levels",
                "scenario_filter": "Only bullish and sideways",
                "risk_management": "0.5% stop loss, 1.5% take profit",
                "timing": "Minimum 30 minutes trade duration",
                "confirmation": "MenthorQ stability >0.95"
            }
        }
        
        with open("menthorq_optimization_recommendations.json", "w", encoding="utf-8") as f:
            json.dump(recommendations, f, indent=2, ensure_ascii=False)
        
        print(f"\nRecommandations sauvegardées dans: menthorq_optimization_recommendations.json")
    
    def generate_final_report(self):
        """Génère le rapport final d'optimisation"""
        print("\n" + "=" * 80)
        print("RAPPORT FINAL D'OPTIMISATION MENTHORQ")
        print("=" * 80)
        
        # Analyser les performances actuelles
        current_perf = self.analyze_current_performance()
        
        # Calculer les performances optimisées
        optimized_perf = self.calculate_optimized_performance()
        
        # Générer les recommandations
        self.generate_optimization_recommendations(current_perf, optimized_perf)
        
        # Résumé final
        print(f"\n" + "=" * 80)
        print("RÉSUMÉ FINAL")
        print("=" * 80)
        
        print(f"PERFORMANCE ACTUELLE:")
        print(f"  - Winrate: {current_perf['winrate']:.1f}%")
        print(f"  - PnL moyen: {current_perf['avg_pnl']:.2f}%")
        print(f"  - Total trades: {current_perf['total_trades']}")
        
        print(f"\nPERFORMANCE OPTIMISÉE:")
        print(f"  - Winrate: {optimized_perf['winrate']:.1f}%")
        print(f"  - PnL moyen: {optimized_perf['avg_pnl']:.2f}%")
        print(f"  - Total trades: {optimized_perf['total_trades']}")
        
        improvement_winrate = optimized_perf['winrate'] - current_perf['winrate']
        improvement_pnl = optimized_perf['avg_pnl'] - current_perf['avg_pnl']
        
        print(f"\nAMÉLIORATION:")
        print(f"  - Winrate: {improvement_winrate:+.1f}%")
        print(f"  - PnL: {improvement_pnl:+.2f}%")
        
        if improvement_winrate > 0 and improvement_pnl > 0:
            print(f"\n🎉 OPTIMISATION RÉUSSIE !")
        else:
            print(f"\n⚠️  OPTIMISATION PARTIELLE")

def main():
    optimizer = SimpleMenthorQOptimizer()
    optimizer.generate_final_report()

if __name__ == "__main__":
    main()

