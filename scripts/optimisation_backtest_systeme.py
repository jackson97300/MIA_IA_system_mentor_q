#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimisation Backtest Système - MIA_IA System
Optimisation des paramètres pour améliorer les performances
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
import random
import yfinance as yf
import pandas as pd

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class OptimisationBacktestSysteme:
    def __init__(self):
        self.optimization_results = {
            'timestamp': datetime.now().isoformat(),
            'best_parameters': {},
            'performance_comparison': {},
            'recommendations': {}
        }
        
        # Paramètres à optimiser
        self.param_ranges = {
            'position_size': [0.01, 0.02, 0.03, 0.05],  # 1%, 2%, 3%, 5%
            'take_profit': [0.015, 0.02, 0.025, 0.03],  # 1.5%, 2%, 2.5%, 3%
            'stop_loss': [0.008, 0.01, 0.012, 0.015],   # 0.8%, 1%, 1.2%, 1.5%
            'signal_threshold': [1.0, 1.5, 2.0, 2.5],   # Seuil intensité signal
            'max_positions': [3, 5, 7, 10]              # Nombre max positions
        }
        
        # Données historiques
        self.historical_data = None
        self.options_data = None
        self.orderflow_data = None
        
        # Période de test
        self.start_date = "2024-01-01"
        self.end_date = "2024-12-31"
        self.symbol = "SPY"
    
    def load_data(self):
        """Charger données historiques"""
        print("📂 Chargement données pour optimisation...")
        
        try:
            ticker = yf.Ticker(self.symbol)
            self.historical_data = ticker.history(
                start=self.start_date,
                end=self.end_date,
                interval="1d"
            )
            
            print(f"✅ Données: {len(self.historical_data)} jours")
            
            # Générer données simulées
            self._generate_simulated_data()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def _generate_simulated_data(self):
        """Générer données options et order flow simulées"""
        print("📈 Génération données simulées...")
        
        self.options_data = {}
        self.orderflow_data = {}
        prices = self.historical_data['Close']
        volumes = self.historical_data['Volume']
        
        for i, (date, price) in enumerate(prices.items()):
            # Options data
            volatility = 0.15 + random.uniform(-0.05, 0.05)
            gex1 = price * (1 - volatility)
            gex2 = price * (1 + volatility)
            
            self.options_data[date] = {
                'gamma_exposure': {
                    'gex1': gex1,
                    'gex2': gex2,
                    'volatility': volatility
                }
            }
            
            # Order flow data
            if i > 0:
                price_change = (price - prices.iloc[i-1]) / prices.iloc[i-1] * 100
                volume_ratio = volumes.iloc[i] / volumes.iloc[i-1] if volumes.iloc[i-1] > 0 else 1.0
                
                if price_change > 0.3:
                    flow_direction = 'BULLISH'
                    flow_intensity = min(abs(price_change) / 1.5, 2.5)
                elif price_change < -0.3:
                    flow_direction = 'BEARISH'
                    flow_intensity = min(abs(price_change) / 1.5, 2.5)
                else:
                    flow_direction = 'NEUTRAL'
                    flow_intensity = 1.0
                
                if volume_ratio > 1.3:
                    flow_intensity *= 1.3
                elif volume_ratio < 0.8:
                    flow_intensity *= 0.8
            else:
                flow_direction = 'NEUTRAL'
                flow_intensity = 1.0
            
            self.orderflow_data[date] = {
                'aggressive_flow': {
                    'flow_direction': flow_direction,
                    'flow_intensity': flow_intensity
                }
            }
        
        print(f"   ✅ Données générées: {len(self.options_data)} jours")
    
    def run_backtest_with_params(self, params):
        """Exécuter backtest avec paramètres spécifiques"""
        initial_capital = 100000
        capital = initial_capital
        positions = []
        trades = []
        
        for i, (date, row) in enumerate(self.historical_data.iterrows()):
            current_price = row['Close']
            
            # Données du jour
            day_options = self.options_data.get(date, {})
            day_orderflow = self.orderflow_data.get(date, {})
            
            # Générer signaux optimisés
            signals = self._generate_optimized_signals(
                date, current_price, day_options, day_orderflow, params
            )
            
            # Exécuter trades
            for signal in signals:
                if len(positions) < params['max_positions']:
                    trade_size = capital * params['position_size']
                    shares = int(trade_size / current_price)
                    
                    if shares > 0:
                        position = {
                            'side': signal['action'],
                            'entry_price': current_price,
                            'entry_date': date,
                            'shares': shares,
                            'signal': signal['type']
                        }
                        positions.append(position)
                        
                        trades.append({
                            'date': date,
                            'action': signal['action'],
                            'price': current_price,
                            'shares': shares,
                            'signal': signal['type']
                        })
            
            # Gérer positions existantes
            for position in positions[:]:
                if position['side'] == 'BUY':
                    if current_price > position['entry_price'] * (1 + params['take_profit']):
                        pnl = (current_price - position['entry_price']) * position['shares']
                        capital += pnl
                        positions.remove(position)
                        trades.append({
                            'date': date,
                            'action': 'CLOSE_LONG',
                            'price': current_price,
                            'pnl': pnl
                        })
                    elif current_price < position['entry_price'] * (1 - params['stop_loss']):
                        pnl = (current_price - position['entry_price']) * position['shares']
                        capital += pnl
                        positions.remove(position)
                        trades.append({
                            'date': date,
                            'action': 'STOP_LONG',
                            'price': current_price,
                            'pnl': pnl
                        })
                
                elif position['side'] == 'SELL':
                    if current_price < position['entry_price'] * (1 - params['take_profit']):
                        pnl = (position['entry_price'] - current_price) * position['shares']
                        capital += pnl
                        positions.remove(position)
                        trades.append({
                            'date': date,
                            'action': 'CLOSE_SHORT',
                            'price': current_price,
                            'pnl': pnl
                        })
                    elif current_price > position['entry_price'] * (1 + params['stop_loss']):
                        pnl = (position['entry_price'] - current_price) * position['shares']
                        capital += pnl
                        positions.remove(position)
                        trades.append({
                            'date': date,
                            'action': 'STOP_SHORT',
                            'price': current_price,
                            'pnl': pnl
                        })
        
        # Fermer positions restantes
        for position in positions:
            if position['side'] == 'BUY':
                pnl = (current_price - position['entry_price']) * position['shares']
            else:
                pnl = (position['entry_price'] - current_price) * position['shares']
            capital += pnl
            trades.append({
                'date': date,
                'action': 'CLOSE_FINAL',
                'price': current_price,
                'pnl': pnl
            })
        
        # Calculer métriques
        return self._calculate_metrics(trades, initial_capital)
    
    def _generate_optimized_signals(self, date, current_price, options, orderflow, params):
        """Générer signaux optimisés"""
        signals = []
        
        # Signal Order Flow optimisé
        if orderflow:
            flow = orderflow.get('aggressive_flow', {})
            flow_direction = flow.get('flow_direction', 'NEUTRAL')
            flow_intensity = flow.get('flow_intensity', 1.0)
            
            if flow_intensity > params['signal_threshold']:
                if flow_direction == 'BULLISH':
                    signals.append({
                        'type': 'ORDERFLOW_BULL',
                        'action': 'BUY',
                        'strength': min(flow_intensity / 3.0, 1.0)
                    })
                elif flow_direction == 'BEARISH':
                    signals.append({
                        'type': 'ORDERFLOW_BEAR',
                        'action': 'SELL',
                        'strength': min(flow_intensity / 3.0, 1.0)
                    })
        
        # Signal Options optimisé
        if options:
            gex1 = options.get('gamma_exposure', {}).get('gex1', 0)
            gex2 = options.get('gamma_exposure', {}).get('gex2', 0)
            
            if current_price < gex1 and random.random() < 0.4:
                signals.append({
                    'type': 'GEX1_SUPPORT',
                    'action': 'BUY',
                    'strength': 0.8
                })
            elif current_price > gex2 and random.random() < 0.4:
                signals.append({
                    'type': 'GEX2_RESISTANCE',
                    'action': 'SELL',
                    'strength': 0.8
                })
        
        # Signal Momentum optimisé (plus équilibré)
        if len(self.historical_data) > 20:
            ma20 = self.historical_data['Close'].rolling(20).mean().iloc[-1]
            if current_price > ma20 * 1.005 and random.random() < 0.5:  # Plus de signaux BULL
                signals.append({
                    'type': 'MOMENTUM_BULL',
                    'action': 'BUY',
                    'strength': 0.7
                })
            elif current_price < ma20 * 0.995 and random.random() < 0.3:  # Moins de signaux BEAR
                signals.append({
                    'type': 'MOMENTUM_BEAR',
                    'action': 'SELL',
                    'strength': 0.7
                })
        
        return signals
    
    def _calculate_metrics(self, trades, initial_capital):
        """Calculer métriques de performance"""
        closed_trades = [t for t in trades if 'pnl' in t]
        winning_trades = [t for t in closed_trades if t['pnl'] > 0]
        losing_trades = [t for t in closed_trades if t['pnl'] < 0]
        
        total_trades = len(closed_trades)
        winning_count = len(winning_trades)
        win_rate = (winning_count / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum([t['pnl'] for t in closed_trades])
        winning_pnl = sum([t['pnl'] for t in winning_trades])
        losing_pnl = abs(sum([t['pnl'] for t in losing_trades]))
        
        profit_factor = winning_pnl / losing_pnl if losing_pnl > 0 else float('inf')
        total_return = (total_pnl / initial_capital) * 100
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_return': total_return,
            'total_pnl': total_pnl
        }
    
    def run_optimization(self):
        """Exécuter optimisation complète"""
        print("🔧 Démarrage optimisation système...")
        
        if not self.load_data():
            return False
        
        best_params = None
        best_score = -float('inf')
        results = []
        
        # Générer combinaisons de paramètres
        total_combinations = (
            len(self.param_ranges['position_size']) *
            len(self.param_ranges['take_profit']) *
            len(self.param_ranges['stop_loss']) *
            len(self.param_ranges['signal_threshold']) *
            len(self.param_ranges['max_positions'])
        )
        
        print(f"📊 Test de {total_combinations} combinaisons...")
        
        combination_count = 0
        
        for pos_size in self.param_ranges['position_size']:
            for tp in self.param_ranges['take_profit']:
                for sl in self.param_ranges['stop_loss']:
                    for threshold in self.param_ranges['signal_threshold']:
                        for max_pos in self.param_ranges['max_positions']:
                            combination_count += 1
                            
                            params = {
                                'position_size': pos_size,
                                'take_profit': tp,
                                'stop_loss': sl,
                                'signal_threshold': threshold,
                                'max_positions': max_pos
                            }
                            
                            # Exécuter backtest
                            metrics = self.run_backtest_with_params(params)
                            
                            # Calculer score (critères multiples)
                            score = 0
                            if metrics['total_trades'] >= 10:  # Minimum de trades
                                score += metrics['win_rate'] * 0.3  # 30% poids win rate
                                score += min(metrics['profit_factor'], 3.0) * 20  # 20% poids profit factor
                                score += metrics['total_return'] * 0.5  # 50% poids retour total
                            
                            results.append({
                                'params': params,
                                'metrics': metrics,
                                'score': score
                            })
                            
                            # Mettre à jour meilleur
                            if score > best_score:
                                best_score = score
                                best_params = params
                            
                            if combination_count % 50 == 0:
                                print(f"   🔄 Progression: {combination_count}/{total_combinations}")
        
        # Trier résultats par score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Sauvegarder résultats
        self.optimization_results['best_parameters'] = best_params
        self.optimization_results['top_results'] = results[:10]
        self.optimization_results['total_combinations'] = total_combinations
        
        # Afficher meilleurs résultats
        print("\n🏆 TOP 5 MEILLEURS PARAMÈTRES:")
        print("=" * 60)
        
        for i, result in enumerate(results[:5]):
            params = result['params']
            metrics = result['metrics']
            print(f"{i+1}. Score: {result['score']:.2f}")
            print(f"   📊 Position: {params['position_size']*100}%")
            print(f"   📊 Take Profit: {params['take_profit']*100}%")
            print(f"   📊 Stop Loss: {params['stop_loss']*100}%")
            print(f"   📊 Seuil Signal: {params['signal_threshold']}")
            print(f"   📊 Max Positions: {params['max_positions']}")
            print(f"   📊 Trades: {metrics['total_trades']}")
            print(f"   📊 Win Rate: {metrics['win_rate']:.1f}%")
            print(f"   📊 Profit Factor: {metrics['profit_factor']:.2f}")
            print(f"   📊 Retour: {metrics['total_return']:.2f}%")
            print()
        
        # Recommandations
        self._generate_recommendations(results)
        
        return True
    
    def _generate_recommendations(self, results):
        """Générer recommandations d'optimisation"""
        print("💡 RECOMMANDATIONS D'OPTIMISATION:")
        print("=" * 60)
        
        # Analyser patterns des meilleurs résultats
        best_results = results[:10]
        
        # Position size
        avg_pos_size = sum(r['params']['position_size'] for r in best_results) / len(best_results)
        print(f"📊 Taille position recommandée: {avg_pos_size*100:.1f}%")
        
        # Take profit
        avg_tp = sum(r['params']['take_profit'] for r in best_results) / len(best_results)
        print(f"📊 Take profit recommandé: {avg_tp*100:.1f}%")
        
        # Stop loss
        avg_sl = sum(r['params']['stop_loss'] for r in best_results) / len(best_results)
        print(f"📊 Stop loss recommandé: {avg_sl*100:.1f}%")
        
        # Signal threshold
        avg_threshold = sum(r['params']['signal_threshold'] for r in best_results) / len(best_results)
        print(f"📊 Seuil signal recommandé: {avg_threshold:.1f}")
        
        # Max positions
        avg_max_pos = sum(r['params']['max_positions'] for r in best_results) / len(best_results)
        print(f"📊 Max positions recommandé: {avg_max_pos:.0f}")
        
        # Améliorations suggérées
        print("\n🚀 AMÉLIORATIONS SUGGÉRÉES:")
        print("1. Augmenter les signaux BULLISH (moins de BEARISH)")
        print("2. Ajuster les seuils de signal pour plus de sensibilité")
        print("3. Optimiser la gestion des positions multiples")
        print("4. Implémenter des filtres de tendance")
        print("5. Ajouter des indicateurs de confirmation")
        
        self.optimization_results['recommendations'] = {
            'position_size': avg_pos_size,
            'take_profit': avg_tp,
            'stop_loss': avg_sl,
            'signal_threshold': avg_threshold,
            'max_positions': avg_max_pos
        }
    
    def save_results(self):
        """Sauvegarder résultats d'optimisation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/test_results/optimization_backtest_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.optimization_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Résultats sauvegardés: {filename}")
        return filename

def main():
    """Fonction principale"""
    print("🔧 OPTIMISATION BACKTEST SYSTÈME - MIA_IA SYSTEM")
    print("=" * 60)
    
    optimizer = OptimisationBacktestSysteme()
    success = optimizer.run_optimization()
    
    if success:
        optimizer.save_results()
        print("\n🎉 OPTIMISATION TERMINÉE !")
        print("📋 Paramètres optimaux identifiés")
    else:
        print("\n❌ Échec optimisation")
    
    return success

if __name__ == "__main__":
    main()










