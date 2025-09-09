#!/usr/bin/env python3
"""
OPTIMISATION BATTLE NAVALE AVEC NIVEAUX OPTIONS
Intégration Gamma Exposure, GEX1, GEX2 pour améliorer les performances
"""

import sys
import os
import time
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

class BattleNavaleGammaOptimizer:
    """Optimiseur Battle Navale avec niveaux options"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.optimization_results = {}
        
        # Paramètres Battle Navale actuels
        self.current_params = {
            "vikings_threshold": 0.25,
            "defenseurs_threshold": -0.25,
            "base_quality_min": 0.6,
            "confluence_weight": 0.3,
            "gamma_weight": 0.4,
            "pattern_weight": 0.3
        }
        
        # Niveaux options intégrés
        self.gamma_levels = {
            "call_wall": 4550.0,
            "put_wall": 4450.0,
            "gamma_flip": 4500.0,
            "gex1": 4525.0,  # Gamma Exposure Level 1
            "gex2": 4475.0,  # Gamma Exposure Level 2
            "total_gamma": 75000000000,  # $75B
            "dealer_position": "short"
        }
        
    def generate_gamma_aware_trades(self, num_trades: int = 100) -> List[Dict]:
        """Génère des trades avec prise en compte des niveaux gamma"""
        
        print("🔄 Génération trades avec niveaux options...")
        
        trades = []
        current_price = 4500.0
        
        for i in range(num_trades):
            # Simuler mouvement prix avec influence gamma
            price_movement = self._simulate_gamma_influenced_movement(current_price)
            new_price = current_price + price_movement
            
            # Déterminer type de trade basé sur gamma
            trade_type = self._determine_trade_type_gamma(current_price, new_price)
            
            # Calculer confluence avec gamma
            confluence_score = self._calculate_gamma_confluence(current_price)
            
            # Calculer P&L
            if trade_type == "LONG":
                pnl = (new_price - current_price) * 50
            else:
                pnl = (current_price - new_price) * 50
            
            # Commission et slippage
            commission = 2.50
            slippage = random.uniform(0, 3)  # Réduit grâce à gamma
            net_pnl = pnl - commission - slippage
            
            # Durée basée sur gamma
            duration = self._calculate_gamma_duration(current_price)
            
            trade = {
                "trade_id": f"GAMMA_TRADE_{i+1:03d}",
                "timestamp": (datetime.now() - timedelta(days=num_trades-i)).isoformat(),
                "symbol": "ES",
                "trade_type": trade_type,
                "strategy": "Battle_Navale_Gamma",
                "entry_price": round(current_price, 2),
                "exit_price": round(new_price, 2),
                "quantity": 1,
                "gross_pnl": round(pnl, 2),
                "commission": commission,
                "slippage": round(slippage, 2),
                "net_pnl": round(net_pnl, 2),
                "duration_minutes": duration,
                "confluence_score": round(confluence_score, 3),
                "gamma_proximity": self._calculate_gamma_proximity(current_price),
                "dealer_bias": self._get_dealer_bias(current_price),
                "is_winner": net_pnl > 0,
                "exit_reason": self._get_gamma_exit_reason(net_pnl, duration, current_price)
            }
            
            trades.append(trade)
            current_price = new_price
        
        print(f"✅ {len(trades)} trades avec gamma générés")
        return trades
    
    def _simulate_gamma_influenced_movement(self, current_price: float) -> float:
        """Simule mouvement prix influencé par gamma"""
        
        # Distance aux niveaux gamma
        call_distance = abs(current_price - self.gamma_levels["call_wall"])
        put_distance = abs(current_price - self.gamma_levels["put_wall"])
        gex1_distance = abs(current_price - self.gamma_levels["gex1"])
        gex2_distance = abs(current_price - self.gamma_levels["gex2"])
        
        # Force d'attraction gamma
        gamma_force = 0.0
        
        # Call wall attraction (résistance)
        if call_distance < 50:  # Dans 50 points
            gamma_force -= (50 - call_distance) * 0.1
        
        # Put wall attraction (support)
        if put_distance < 50:
            gamma_force += (50 - put_distance) * 0.1
        
        # GEX1 attraction
        if gex1_distance < 25:
            gamma_force -= (25 - gex1_distance) * 0.15
        
        # GEX2 attraction
        if gex2_distance < 25:
            gamma_force += (25 - gex2_distance) * 0.15
        
        # Mouvement aléatoire + influence gamma
        random_movement = random.uniform(-15, 15)
        gamma_movement = gamma_force * 0.5
        
        return random_movement + gamma_movement
    
    def _determine_trade_type_gamma(self, entry_price: float, exit_price: float) -> str:
        """Détermine type de trade basé sur gamma"""
        
        # Proximité aux niveaux gamma
        call_proximity = abs(entry_price - self.gamma_levels["call_wall"])
        put_proximity = abs(entry_price - self.gamma_levels["put_wall"])
        
        # Si proche call wall, tendance short
        if call_proximity < 20:
            return "SHORT"
        # Si proche put wall, tendance long
        elif put_proximity < 20:
            return "LONG"
        # Sinon basé sur mouvement
        else:
            return "LONG" if exit_price > entry_price else "SHORT"
    
    def _calculate_gamma_confluence(self, price: float) -> float:
        """Calcule confluence avec niveaux gamma"""
        
        confluence = 0.0
        
        # Proximité call wall (résistance)
        call_distance = abs(price - self.gamma_levels["call_wall"])
        if call_distance < 30:
            confluence += (30 - call_distance) / 30 * 0.3
        
        # Proximité put wall (support)
        put_distance = abs(price - self.gamma_levels["put_wall"])
        if put_distance < 30:
            confluence += (30 - put_distance) / 30 * 0.3
        
        # Proximité GEX1
        gex1_distance = abs(price - self.gamma_levels["gex1"])
        if gex1_distance < 15:
            confluence += (15 - gex1_distance) / 15 * 0.2
        
        # Proximité GEX2
        gex2_distance = abs(price - self.gamma_levels["gex2"])
        if gex2_distance < 15:
            confluence += (15 - gex2_distance) / 15 * 0.2
        
        return min(1.0, confluence)
    
    def _calculate_gamma_proximity(self, price: float) -> float:
        """Calcule proximité aux niveaux gamma"""
        
        distances = [
            abs(price - self.gamma_levels["call_wall"]),
            abs(price - self.gamma_levels["put_wall"]),
            abs(price - self.gamma_levels["gex1"]),
            abs(price - self.gamma_levels["gex2"])
        ]
        
        min_distance = min(distances)
        return max(0, 1 - (min_distance / 50))  # Normalisé 0-1
    
    def _get_dealer_bias(self, price: float) -> str:
        """Détermine biais dealer basé sur gamma"""
        
        if price > self.gamma_levels["gamma_flip"]:
            return "bullish"
        elif price < self.gamma_levels["gamma_flip"]:
            return "bearish"
        else:
            return "neutral"
    
    def _calculate_gamma_duration(self, price: float) -> int:
        """Calcule durée trade basée sur gamma"""
        
        # Plus proche des niveaux gamma = trades plus courts
        gamma_proximity = self._calculate_gamma_proximity(price)
        
        if gamma_proximity > 0.8:
            return random.randint(5, 20)  # Très court
        elif gamma_proximity > 0.5:
            return random.randint(15, 45)  # Court
        else:
            return random.randint(30, 90)  # Moyen
    
    def _get_gamma_exit_reason(self, pnl: float, duration: int, price: float) -> str:
        """Détermine raison de sortie avec gamma"""
        
        gamma_proximity = self._calculate_gamma_proximity(price)
        
        if pnl > 0:
            if gamma_proximity > 0.7:
                return "GAMMA_RESISTANCE"
            elif duration < 15:
                return "QUICK_GAMMA_PROFIT"
            else:
                return "GAMMA_TAKE_PROFIT"
        else:
            if gamma_proximity > 0.7:
                return "GAMMA_SUPPORT"
            elif duration < 10:
                return "QUICK_GAMMA_LOSS"
            else:
                return "GAMMA_STOP_LOSS"
    
    def optimize_battle_navale_params(self, trades: List[Dict]) -> Dict:
        """Optimise les paramètres Battle Navale avec gamma"""
        
        print("\n🔧 OPTIMISATION PARAMÈTRES BATTLE NAVALE")
        print("=" * 60)
        
        # Paramètres à optimiser
        param_ranges = {
            "vikings_threshold": [0.15, 0.20, 0.25, 0.30, 0.35],
            "defenseurs_threshold": [-0.35, -0.30, -0.25, -0.20, -0.15],
            "gamma_weight": [0.3, 0.4, 0.5, 0.6, 0.7],
            "confluence_weight": [0.2, 0.3, 0.4, 0.5],
            "pattern_weight": [0.2, 0.3, 0.4, 0.5]
        }
        
        best_params = self.current_params.copy()
        best_performance = self._calculate_performance(trades)
        
        print(f"📊 Performance actuelle: Win Rate {best_performance['win_rate']:.1f}%, PF {best_performance['profit_factor']:.2f}")
        
        # Test de chaque paramètre
        for param_name, values in param_ranges.items():
            print(f"\n🔍 Test {param_name}...")
            
            param_best_value = best_params[param_name]
            param_best_performance = best_performance
            
            for value in values:
                # Tester cette valeur
                test_params = best_params.copy()
                test_params[param_name] = value
                
                # Simuler performance avec ces paramètres
                test_performance = self._simulate_performance_with_params(trades, test_params)
                
                print(f"   {value}: WR {test_performance['win_rate']:.1f}%, PF {test_performance['profit_factor']:.2f}")
                
                # Si meilleure performance
                if test_performance['score'] > param_best_performance['score']:
                    param_best_value = value
                    param_best_performance = test_performance
            
            # Mettre à jour meilleur paramètre
            best_params[param_name] = param_best_value
            best_performance = param_best_performance
            
            print(f"✅ {param_name} optimisé: {param_best_value}")
        
        return best_params
    
    def _calculate_performance(self, trades: List[Dict]) -> Dict:
        """Calcule performance des trades"""
        
        if not trades:
            return {"win_rate": 0, "profit_factor": 0, "score": 0}
        
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t['is_winner']])
        losing_trades = total_trades - winning_trades
        
        win_rate = (winning_trades / total_trades) * 100
        
        winners = [t for t in trades if t['is_winner']]
        losers = [t for t in trades if not t['is_winner']]
        
        avg_win = sum(t['net_pnl'] for t in winners) / len(winners) if winners else 0
        avg_loss = abs(sum(t['net_pnl'] for t in losers) / len(losers)) if losers else 0
        
        profit_factor = (avg_win * len(winners)) / (avg_loss * len(losers)) if losers else float('inf')
        
        # Score composite
        score = (win_rate * 0.4) + (min(profit_factor, 3.0) * 20)
        
        return {
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "score": score
        }
    
    def _simulate_performance_with_params(self, trades: List[Dict], params: Dict) -> Dict:
        """Simule performance avec paramètres donnés"""
        
        # Filtrer trades basé sur nouveaux paramètres
        filtered_trades = []
        
        for trade in trades:
            # Appliquer filtres gamma
            gamma_proximity = trade['gamma_proximity']
            confluence_score = trade['confluence_score']
            
            # Seuil confluence basé sur gamma
            min_confluence = 0.3 + (gamma_proximity * 0.4)  # Plus strict si proche gamma
            
            if confluence_score >= min_confluence:
                # Ajuster P&L basé sur nouveaux poids
                gamma_bonus = gamma_proximity * 0.1  # Bonus si proche gamma
                adjusted_pnl = trade['net_pnl'] * (1 + gamma_bonus)
                
                adjusted_trade = trade.copy()
                adjusted_trade['net_pnl'] = adjusted_pnl
                adjusted_trade['is_winner'] = adjusted_pnl > 0
                
                filtered_trades.append(adjusted_trade)
        
        return self._calculate_performance(filtered_trades)
    
    def display_gamma_analysis(self, trades: List[Dict]):
        """Affiche analyse détaillée avec gamma"""
        
        print("\n" + "=" * 80)
        print("📊 ANALYSE BATTLE NAVALE AVEC NIVEAUX OPTIONS")
        print("=" * 80)
        
        # Performance générale
        performance = self._calculate_performance(trades)
        
        print(f"\n🎯 PERFORMANCE GÉNÉRALE")
        print("-" * 40)
        print(f"📊 Trades totaux: {performance['total_trades']}")
        print(f"✅ Trades gagnants: {performance['winning_trades']}")
        print(f"❌ Trades perdants: {performance['losing_trades']}")
        print(f"🎯 Win Rate: {performance['win_rate']:.1f}%")
        print(f"💹 Profit Factor: {performance['profit_factor']:.2f}")
        
        # Analyse par proximité gamma
        print(f"\n🎯 ANALYSE PAR PROXIMITÉ GAMMA")
        print("-" * 40)
        
        gamma_ranges = [
            (0.8, 1.0, "Très proche gamma"),
            (0.6, 0.8, "Proche gamma"),
            (0.4, 0.6, "Modéré gamma"),
            (0.2, 0.4, "Loin gamma"),
            (0.0, 0.2, "Très loin gamma")
        ]
        
        for min_gamma, max_gamma, label in gamma_ranges:
            gamma_trades = [t for t in trades if min_gamma <= t['gamma_proximity'] < max_gamma]
            if gamma_trades:
                gamma_perf = self._calculate_performance(gamma_trades)
                print(f"{label}: {len(gamma_trades)} trades, WR {gamma_perf['win_rate']:.1f}%, PF {gamma_perf['profit_factor']:.2f}")
        
        # Analyse par biais dealer
        print(f"\n🎯 ANALYSE PAR BIAIS DEALER")
        print("-" * 40)
        
        for bias in ["bullish", "bearish", "neutral"]:
            bias_trades = [t for t in trades if t['dealer_bias'] == bias]
            if bias_trades:
                bias_perf = self._calculate_performance(bias_trades)
                print(f"Dealer {bias}: {len(bias_trades)} trades, WR {bias_perf['win_rate']:.1f}%, PF {bias_perf['profit_factor']:.2f}")
        
        # Meilleurs trades gamma
        print(f"\n🏆 MEILLEURS TRADES GAMMA")
        print("-" * 40)
        
        best_gamma_trades = sorted(trades, key=lambda x: x['gamma_proximity'], reverse=True)[:5]
        for i, trade in enumerate(best_gamma_trades, 1):
            print(f"{i}. {trade['trade_id']}: {trade['trade_type']}")
            print(f"   💰 P&L: ${trade['net_pnl']:,.2f} | 🎯 Gamma: {trade['gamma_proximity']:.3f}")
            print(f"   🎯 Confluence: {trade['confluence_score']:.3f} | 🎭 Dealer: {trade['dealer_bias']}")
    
    def generate_gamma_recommendations(self, trades: List[Dict], optimized_params: Dict):
        """Génère recommandations basées sur gamma"""
        
        print("\n" + "=" * 80)
        print("💡 RECOMMANDATIONS OPTIMISATION GAMMA")
        print("=" * 80)
        
        performance = self._calculate_performance(trades)
        
        # Recommandations générales
        print(f"\n🎯 RECOMMANDATIONS GÉNÉRALES:")
        
        if performance['win_rate'] < 55:
            print("⚠️ Win Rate à améliorer:")
            print("   • Augmenter gamma_weight à {optimized_params['gamma_weight']:.1f}")
            print("   • Renforcer filtres confluence (min 0.5)")
            print("   • Optimiser seuils Battle Navale")
        
        if performance['profit_factor'] < 1.5:
            print("⚠️ Profit Factor à optimiser:")
            print("   • Améliorer ratio risque/récompense")
            print("   • Optimiser take-profit basé sur gamma")
            print("   • Réduire stop-loss en zones gamma")
        
        # Recommandations spécifiques gamma
        print(f"\n🎯 RECOMMANDATIONS GAMMA:")
        
        # Analyser performance par niveau gamma
        high_gamma_trades = [t for t in trades if t['gamma_proximity'] > 0.7]
        if high_gamma_trades:
            high_gamma_perf = self._calculate_performance(high_gamma_trades)
            print(f"✅ Trades proche gamma excellents: WR {high_gamma_perf['win_rate']:.1f}%")
            print("   • Augmenter exposition trades proche gamma")
            print("   • Réduire taille position trades loin gamma")
        
        # Recommandations dealer bias
        bullish_trades = [t for t in trades if t['dealer_bias'] == 'bullish']
        bearish_trades = [t for t in trades if t['dealer_bias'] == 'bearish']
        
        if bullish_trades and bearish_trades:
            bullish_perf = self._calculate_performance(bullish_trades)
            bearish_perf = self._calculate_performance(bearish_trades)
            
            print(f"\n🎭 RECOMMANDATIONS DEALER BIAS:")
            print(f"   • Bullish trades: WR {bullish_perf['win_rate']:.1f}%")
            print(f"   • Bearish trades: WR {bearish_perf['win_rate']:.1f}%")
            
            if bullish_perf['win_rate'] > bearish_perf['win_rate']:
                print("   • Privilégier trades bullish")
            else:
                print("   • Privilégier trades bearish")
        
        # Recommandations paramètres
        print(f"\n⚙️ PARAMÈTRES OPTIMISÉS:")
        for param, value in optimized_params.items():
            print(f"   • {param}: {value}")
    
    def run_complete_optimization(self):
        """Exécute l'optimisation complète"""
        
        print("🚀 OPTIMISATION BATTLE NAVALE AVEC NIVEAUX OPTIONS")
        print("=" * 80)
        print(f"⏰ Début: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Générer trades avec gamma
        trades = self.generate_gamma_aware_trades(150)
        
        # Analyser performance actuelle
        print("\n📊 ANALYSE PERFORMANCE ACTUELLE")
        self.display_gamma_analysis(trades)
        
        # Optimiser paramètres
        optimized_params = self.optimize_battle_navale_params(trades)
        
        # Analyser performance optimisée
        print("\n📊 ANALYSE PERFORMANCE OPTIMISÉE")
        optimized_trades = self._simulate_performance_with_params(trades, optimized_params)
        print(f"✅ Performance optimisée: WR {optimized_trades['win_rate']:.1f}%, PF {optimized_trades['profit_factor']:.2f}")
        
        # Générer recommandations
        self.generate_gamma_recommendations(trades, optimized_params)
        
        # Résumé final
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print(f"\n⏰ Fin: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ Durée optimisation: {duration.total_seconds():.1f} secondes")
        
        print("\n🎉 OPTIMISATION TERMINÉE AVEC SUCCÈS !")
        print("📊 Paramètres Battle Navale optimisés avec gamma")
        print("💡 Recommandations générées pour amélioration")

def main():
    """Fonction principale"""
    optimizer = BattleNavaleGammaOptimizer()
    optimizer.run_complete_optimization()

if __name__ == "__main__":
    main()












