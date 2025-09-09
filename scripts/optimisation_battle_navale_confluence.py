#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimisation Battle Navale Confluence - MIA_IA System
Optimisation des paramètres pour générer plus de signaux
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
import random
import yfinance as yf
import pandas as pd
import numpy as np

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class OptimisationBattleNavaleConfluence:
    def __init__(self):
        self.optimization_results = {
            'timestamp': datetime.now().isoformat(),
            'best_parameters': {},
            'performance_comparison': {},
            'recommendations': {}
        }
        
        # Paramètres à optimiser
        self.param_ranges = {
            'confluence_threshold': [0.3, 0.4, 0.5, 0.6],  # Seuil confluence
            'level_proximity': [0.003, 0.005, 0.008, 0.01],  # Proximité niveaux
            'position_size': [0.02, 0.03, 0.04, 0.05],  # Taille position
            'take_profit': [0.015, 0.02, 0.025, 0.03],  # Take profit
            'stop_loss': [0.008, 0.01, 0.012, 0.015]   # Stop loss
        }
        
        self.historical_data = None
        self.options_data = None
        self.orderflow_data = None
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
            
            # Calculer indicateurs techniques
            self._calculate_technical_indicators()
            
            # Générer données simulées
            self._generate_simulated_data()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def _calculate_technical_indicators(self):
        """Calculer indicateurs techniques"""
        print("📈 Calcul indicateurs techniques...")
        
        # RSI
        delta = self.historical_data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.historical_data['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = self.historical_data['Close'].ewm(span=12).mean()
        exp2 = self.historical_data['Close'].ewm(span=26).mean()
        self.historical_data['MACD'] = exp1 - exp2
        self.historical_data['MACD_Signal'] = self.historical_data['MACD'].ewm(span=9).mean()
        
        # Bollinger Bands
        self.historical_data['BB_Middle'] = self.historical_data['Close'].rolling(window=20).mean()
        bb_std = self.historical_data['Close'].rolling(window=20).std()
        self.historical_data['BB_Upper'] = self.historical_data['BB_Middle'] + (bb_std * 2)
        self.historical_data['BB_Lower'] = self.historical_data['BB_Middle'] - (bb_std * 2)
        
        # VWAP
        typical_price = (self.historical_data['High'] + self.historical_data['Low'] + self.historical_data['Close']) / 3
        volume_price = typical_price * self.historical_data['Volume']
        self.historical_data['VWAP'] = volume_price.rolling(window=20).sum() / self.historical_data['Volume'].rolling(window=20).sum()
        
        # Pivot Points
        self.historical_data['PP'] = (self.historical_data['High'] + self.historical_data['Low'] + self.historical_data['Close']) / 3
        self.historical_data['R1'] = 2 * self.historical_data['PP'] - self.historical_data['Low']
        self.historical_data['S1'] = 2 * self.historical_data['PP'] - self.historical_data['High']
        
        print("   ✅ Indicateurs calculés")
    
    def _generate_simulated_data(self):
        """Générer données options et order flow simulées"""
        print("📈 Génération données simulées...")
        
        self.options_data = {}
        self.orderflow_data = {}
        prices = self.historical_data['Close']
        volumes = self.historical_data['Volume']
        
        for i, (date, price) in enumerate(prices.items()):
            # Options data avec GEX réaliste
            volatility = 0.15 + random.uniform(-0.05, 0.05)
            gex1 = price * (1 - volatility * 0.8)  # Support GEX
            gex2 = price * (1 + volatility * 0.8)  # Résistance GEX
            
            self.options_data[date] = {
                'gamma_exposure': {
                    'gex1': gex1,
                    'gex2': gex2,
                    'volatility': volatility
                },
                'put_call_ratio': random.uniform(0.8, 1.2)
            }
            
            # Order flow data réaliste
            if i > 0:
                price_change = (price - prices.iloc[i-1]) / prices.iloc[i-1] * 100
                volume_ratio = volumes.iloc[i] / volumes.iloc[i-1] if volumes.iloc[i-1] > 0 else 1.0
                
                # Déterminer flow basé sur prix et volume
                if price_change > 0.3 and volume_ratio > 1.2:
                    flow_direction = 'BULLISH'
                    flow_intensity = min(abs(price_change) / 1.5, 2.5)
                elif price_change < -0.3 and volume_ratio > 1.2:
                    flow_direction = 'BEARISH'
                    flow_intensity = min(abs(price_change) / 1.5, 2.5)
                else:
                    flow_direction = 'NEUTRAL'
                    flow_intensity = 1.0
            else:
                flow_direction = 'NEUTRAL'
                flow_intensity = 1.0
                price_change = 0
            
            self.orderflow_data[date] = {
                'aggressive_flow': {
                    'flow_direction': flow_direction,
                    'flow_intensity': flow_intensity
                },
                'cumulative_delta': {
                    'delta': price_change * 1000,
                    'trend': 'BULLISH' if price_change > 0 else 'BEARISH'
                }
            }
        
        print(f"   ✅ Données générées: {len(self.options_data)} jours")
    
    def _calculate_battle_navale_levels(self, date, current_price):
        """Calculer niveaux Battle Navale"""
        levels = {
            'support_levels': [],
            'resistance_levels': [],
            'pivot_points': {},
            'zones': []
        }
        
        # Pivot Points
        row = self.historical_data.loc[date]
        levels['pivot_points'] = {
            'PP': row['PP'],
            'R1': row['R1'],
            'S1': row['S1']
        }
        
        # Niveaux GEX
        if date in self.options_data:
            gex1 = self.options_data[date]['gamma_exposure']['gex1']
            gex2 = self.options_data[date]['gamma_exposure']['gex2']
            
            if current_price > gex1:
                levels['support_levels'].append(('GEX1', gex1, 0.8))
            if current_price < gex2:
                levels['resistance_levels'].append(('GEX2', gex2, 0.8))
        
        # Bollinger Bands
        bb_upper = row['BB_Upper']
        bb_lower = row['BB_Lower']
        
        if current_price < bb_upper:
            levels['resistance_levels'].append(('BB_Upper', bb_upper, 0.6))
        if current_price > bb_lower:
            levels['support_levels'].append(('BB_Lower', bb_lower, 0.6))
        
        # VWAP
        vwap = row['VWAP']
        if abs(current_price - vwap) / vwap < 0.01:  # Proche du VWAP
            if current_price > vwap:
                levels['resistance_levels'].append(('VWAP', vwap, 0.7))
            else:
                levels['support_levels'].append(('VWAP', vwap, 0.7))
        
        return levels
    
    def _calculate_confluence_score(self, date, current_price, signal_type):
        """Calculer score de confluence"""
        confluence_factors = {
            'technical': 0,
            'volume': 0,
            'options': 0,
            'orderflow': 0,
            'total': 0
        }
        
        row = self.historical_data.loc[date]
        
        # 1. FACTEURS TECHNIQUES (30%)
        tech_score = 0
        
        # RSI
        rsi = row['RSI']
        if signal_type == 'BUY' and rsi < 30:
            tech_score += 0.3
        elif signal_type == 'SELL' and rsi > 70:
            tech_score += 0.3
        
        # MACD
        macd = row['MACD']
        macd_signal = row['MACD_Signal']
        if signal_type == 'BUY' and macd > macd_signal:
            tech_score += 0.3
        elif signal_type == 'SELL' and macd < macd_signal:
            tech_score += 0.3
        
        # Bollinger Bands
        bb_upper = row['BB_Upper']
        bb_lower = row['BB_Lower']
        if signal_type == 'BUY' and current_price < bb_lower:
            tech_score += 0.4
        elif signal_type == 'SELL' and current_price > bb_upper:
            tech_score += 0.4
        
        confluence_factors['technical'] = min(tech_score, 1.0)
        
        # 2. FACTEURS VOLUME (20%)
        volume_score = 0
        volume_ratio = row['Volume'] / self.historical_data['Volume'].rolling(20).mean().loc[date]
        
        if volume_ratio > 1.5:
            volume_score = 1.0
        elif volume_ratio > 1.2:
            volume_score = 0.7
        elif volume_ratio > 1.0:
            volume_score = 0.5
        
        confluence_factors['volume'] = volume_score
        
        # 3. FACTEURS OPTIONS (25%)
        options_score = 0
        if date in self.options_data:
            gex1 = self.options_data[date]['gamma_exposure']['gex1']
            gex2 = self.options_data[date]['gamma_exposure']['gex2']
            
            if signal_type == 'BUY' and current_price < gex1:
                options_score = 0.8
            elif signal_type == 'SELL' and current_price > gex2:
                options_score = 0.8
        
        confluence_factors['options'] = options_score
        
        # 4. FACTEURS ORDER FLOW (25%)
        orderflow_score = 0
        if date in self.orderflow_data:
            flow = self.orderflow_data[date]['aggressive_flow']
            flow_direction = flow['flow_direction']
            flow_intensity = flow['flow_intensity']
            
            if signal_type == 'BUY' and flow_direction == 'BULLISH' and flow_intensity > 1.5:
                orderflow_score = 0.8
            elif signal_type == 'SELL' and flow_direction == 'BEARISH' and flow_intensity > 1.5:
                orderflow_score = 0.8
        
        confluence_factors['orderflow'] = orderflow_score
        
        # SCORE TOTAL
        confluence_factors['total'] = (
            confluence_factors['technical'] * 0.30 +
            confluence_factors['volume'] * 0.20 +
            confluence_factors['options'] * 0.25 +
            confluence_factors['orderflow'] * 0.25
        )
        
        return confluence_factors
    
    def _generate_battle_navale_signals(self, date, current_price, params):
        """Générer signaux Battle Navale avec paramètres optimisés"""
        signals = []
        
        # Calculer niveaux Battle Navale
        levels = self._calculate_battle_navale_levels(date, current_price)
        
        # Analyser zones de combat avec paramètres optimisés
        for support_name, support_price, strength in levels['support_levels']:
            if abs(current_price - support_price) / support_price < params['level_proximity']:
                # Calculer confluence pour signal BUY
                confluence = self._calculate_confluence_score(date, current_price, 'BUY')
                
                if confluence['total'] > params['confluence_threshold']:
                    signals.append({
                        'type': f'BATTLE_NAVALE_SUPPORT_{support_name}',
                        'action': 'BUY',
                        'strength': strength,
                        'confluence_score': confluence['total'],
                        'confluence_factors': confluence,
                        'level_price': support_price
                    })
        
        for resistance_name, resistance_price, strength in levels['resistance_levels']:
            if abs(current_price - resistance_price) / resistance_price < params['level_proximity']:
                # Calculer confluence pour signal SELL
                confluence = self._calculate_confluence_score(date, current_price, 'SELL')
                
                if confluence['total'] > params['confluence_threshold']:
                    signals.append({
                        'type': f'BATTLE_NAVALE_RESISTANCE_{resistance_name}',
                        'action': 'SELL',
                        'strength': strength,
                        'confluence_score': confluence['total'],
                        'confluence_factors': confluence,
                        'level_price': resistance_price
                    })
        
        return signals
    
    def run_backtest_with_params(self, params):
        """Exécuter backtest avec paramètres donnés"""
        if self.historical_data is None:
            return None
        
        # Paramètres trading
        initial_capital = 100000
        capital = initial_capital
        positions = []
        trades = []
        equity_curve = []
        
        # Parcourir chaque jour
        for i, (date, row) in enumerate(self.historical_data.iterrows()):
            current_price = row['Close']
            
            # Générer signaux Battle Navale avec paramètres optimisés
            signals = self._generate_battle_navale_signals(date, current_price, params)
            
            # Exécuter trades
            for signal in signals:
                if len(positions) < 6:  # Max positions
                    # Taille position basée sur confluence
                    confluence_multiplier = signal['confluence_score']
                    adjusted_position_size = params['position_size'] * confluence_multiplier
                    
                    trade_size = capital * adjusted_position_size
                    shares = int(trade_size / current_price)
                    
                    if shares > 0:
                        position = {
                            'id': len(positions) + 1,
                            'side': signal['action'],
                            'entry_price': current_price,
                            'entry_date': date,
                            'shares': shares,
                            'signal': signal['type'],
                            'confluence_score': signal['confluence_score']
                        }
                        positions.append(position)
                        
                        trades.append({
                            'date': date,
                            'action': signal['action'],
                            'price': current_price,
                            'shares': shares,
                            'signal': signal['type'],
                            'confluence_score': signal['confluence_score'],
                            'capital': capital
                        })
            
            # Gestion des positions
            for position in positions[:]:
                if position['side'] == 'BUY':
                    tp_price = position['entry_price'] * (1 + params['take_profit'])
                    sl_price = position['entry_price'] * (1 - params['stop_loss'])
                    
                    if current_price > tp_price:
                        pnl = (current_price - position['entry_price']) * position['shares']
                        capital += pnl
                        positions.remove(position)
                        trades.append({
                            'date': date,
                            'action': 'CLOSE_LONG',
                            'price': current_price,
                            'pnl': pnl,
                            'capital': capital
                        })
                    elif current_price < sl_price:
                        pnl = (current_price - position['entry_price']) * position['shares']
                        capital += pnl
                        positions.remove(position)
                        trades.append({
                            'date': date,
                            'action': 'STOP_LONG',
                            'price': current_price,
                            'pnl': pnl,
                            'capital': capital
                        })
                
                elif position['side'] == 'SELL':
                    tp_price = position['entry_price'] * (1 - params['take_profit'])
                    sl_price = position['entry_price'] * (1 + params['stop_loss'])
                    
                    if current_price < tp_price:
                        pnl = (position['entry_price'] - current_price) * position['shares']
                        capital += pnl
                        positions.remove(position)
                        trades.append({
                            'date': date,
                            'action': 'CLOSE_SHORT',
                            'price': current_price,
                            'pnl': pnl,
                            'capital': capital
                        })
                    elif current_price > sl_price:
                        pnl = (position['entry_price'] - current_price) * position['shares']
                        capital += pnl
                        positions.remove(position)
                        trades.append({
                            'date': date,
                            'action': 'STOP_SHORT',
                            'price': current_price,
                            'pnl': pnl,
                            'capital': capital
                        })
            
            # Fermer positions à la fin
            if i == len(self.historical_data) - 1:
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
                        'pnl': pnl,
                        'capital': capital
                    })
            
            # Track equity
            equity_curve.append({
                'date': date,
                'capital': capital,
                'positions': len(positions)
            })
        
        # Calculer métriques
        return self._calculate_metrics(trades, initial_capital)
    
    def _calculate_metrics(self, trades, initial_capital):
        """Calculer métriques de performance"""
        # Trades fermés
        closed_trades = [t for t in trades if 'pnl' in t]
        winning_trades = [t for t in closed_trades if t['pnl'] > 0]
        losing_trades = [t for t in closed_trades if t['pnl'] < 0]
        
        # Métriques de base
        total_trades = len(closed_trades)
        winning_count = len(winning_trades)
        losing_count = len(losing_trades)
        win_rate = (winning_count / total_trades * 100) if total_trades > 0 else 0
        
        # P&L
        total_pnl = sum([t['pnl'] for t in closed_trades])
        winning_pnl = sum([t['pnl'] for t in winning_trades])
        losing_pnl = abs(sum([t['pnl'] for t in losing_trades]))
        
        # Profit factor
        profit_factor = winning_pnl / losing_pnl if losing_pnl > 0 else float('inf')
        
        # Retour total
        total_return = (total_pnl / initial_capital) * 100
        
        # Score composite
        if total_trades == 0:
            score = 0
        else:
            score = (win_rate * 0.3 + 
                    min(profit_factor, 3.0) * 20 + 
                    total_return * 0.5 + 
                    total_trades * 0.1)
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_return': total_return,
            'total_pnl': total_pnl,
            'score': score
        }
    
    def run_optimization(self):
        """Exécuter optimisation complète"""
        print("🔧 OPTIMISATION BATTLE NAVALE CONFLUENCE")
        print("=" * 60)
        
        # Charger données
        if not self.load_data():
            return False
        
        print("📊 Démarrage optimisation...")
        
        best_score = -1
        best_params = None
        all_results = []
        
        # Générer toutes les combinaisons
        total_combinations = 1
        for param_name, values in self.param_ranges.items():
            total_combinations *= len(values)
        
        print(f"   🔍 {total_combinations} combinaisons à tester")
        
        combination_count = 0
        
        # Tester toutes les combinaisons
        for confluence_threshold in self.param_ranges['confluence_threshold']:
            for level_proximity in self.param_ranges['level_proximity']:
                for position_size in self.param_ranges['position_size']:
                    for take_profit in self.param_ranges['take_profit']:
                        for stop_loss in self.param_ranges['stop_loss']:
                            combination_count += 1
                            
                            params = {
                                'confluence_threshold': confluence_threshold,
                                'level_proximity': level_proximity,
                                'position_size': position_size,
                                'take_profit': take_profit,
                                'stop_loss': stop_loss
                            }
                            
                            print(f"   🔄 Test {combination_count}/{total_combinations}: {params}")
                            
                            # Exécuter backtest
                            results = self.run_backtest_with_params(params)
                            
                            if results:
                                all_results.append({
                                    'params': params,
                                    'results': results
                                })
                                
                                # Vérifier si c'est le meilleur
                                if results['score'] > best_score:
                                    best_score = results['score']
                                    best_params = params
                                    
                                    print(f"      🎯 NOUVEAU MEILLEUR SCORE: {best_score:.2f}")
                                    print(f"         📊 Trades: {results['total_trades']}")
                                    print(f"         📊 Win Rate: {results['win_rate']:.1f}%")
                                    print(f"         📊 Profit Factor: {results['profit_factor']:.2f}")
                                    print(f"         📊 Return: {results['total_return']:.2f}%")
        
        # Sauvegarder résultats
        self.optimization_results['best_parameters'] = best_params
        self.optimization_results['performance_comparison'] = {
            'best_score': best_score,
            'total_combinations': total_combinations,
            'all_results': all_results
        }
        
        # Générer recommandations
        self._generate_recommendations(all_results)
        
        # Sauvegarder
        self.save_results()
        
        # Afficher résultats finaux
        print("\n" + "=" * 60)
        print("🎯 RÉSULTATS OPTIMISATION BATTLE NAVALE")
        print("=" * 60)
        
        if best_params:
            print(f"🏆 MEILLEURS PARAMÈTRES:")
            for param, value in best_params.items():
                print(f"   {param}: {value}")
            
            print(f"\n📊 PERFORMANCE OPTIMALE:")
            best_result = next((r for r in all_results if r['params'] == best_params), None)
            if best_result:
                results = best_result['results']
                print(f"   📊 Score: {results['score']:.2f}")
                print(f"   📊 Trades: {results['total_trades']}")
                print(f"   📊 Win Rate: {results['win_rate']:.1f}%")
                print(f"   📊 Profit Factor: {results['profit_factor']:.2f}")
                print(f"   📊 Retour total: {results['total_return']:.2f}%")
                print(f"   📊 P&L total: ${results['total_pnl']:,.2f}")
            
            print(f"\n💡 RECOMMANDATIONS:")
            recommendations = self.optimization_results.get('recommendations', {})
            for key, value in recommendations.items():
                print(f"   {key}: {value}")
        
        return True
    
    def _generate_recommendations(self, all_results):
        """Générer recommandations basées sur les résultats"""
        recommendations = {}
        
        # Analyser les meilleurs résultats
        top_results = sorted(all_results, key=lambda x: x['results']['score'], reverse=True)[:10]
        
        # Recommandations générales
        if top_results:
            avg_confluence = sum(r['params']['confluence_threshold'] for r in top_results) / len(top_results)
            avg_proximity = sum(r['params']['level_proximity'] for r in top_results) / len(top_results)
            
            recommendations['confluence_threshold_optimal'] = f"{avg_confluence:.3f}"
            recommendations['level_proximity_optimal'] = f"{avg_proximity:.3f}"
            recommendations['trades_generated'] = f"Meilleur: {top_results[0]['results']['total_trades']} trades"
            recommendations['win_rate_achieved'] = f"Meilleur: {top_results[0]['results']['win_rate']:.1f}%"
            recommendations['profit_factor_achieved'] = f"Meilleur: {top_results[0]['results']['profit_factor']:.2f}"
        
        self.optimization_results['recommendations'] = recommendations
    
    def save_results(self):
        """Sauvegarder résultats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/test_results/optimisation_battle_navale_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.optimization_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Sauvegardé: {filename}")
        return filename

def main():
    """Fonction principale"""
    print("🔧 OPTIMISATION BATTLE NAVALE CONFLUENCE - MIA_IA SYSTEM")
    print("=" * 60)
    
    optimizer = OptimisationBattleNavaleConfluence()
    success = optimizer.run_optimization()
    
    if success:
        print("\n🎉 OPTIMISATION TERMINÉE !")
    else:
        print("\n❌ Échec de l'optimisation")
    
    return success

if __name__ == "__main__":
    main()










