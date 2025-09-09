#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtest Système Longue Durée - MIA_IA System
Backtesting du système sur données historiques étendues
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
import random
import glob
import yfinance as yf
import pandas as pd

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BacktestSystemeLongueDuree:
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'backtest_period': {},
            'trading_results': {},
            'performance_metrics': {},
            'success': False
        }
        
        # Données historiques
        self.historical_data = None
        self.options_data = None
        self.orderflow_data = None
        
        # Paramètres backtest
        self.start_date = "2024-01-01"
        self.end_date = "2024-12-31"
        self.symbol = "SPY"  # S&P 500 ETF pour données historiques
    
    def load_historical_data(self):
        """Charger données historiques étendues"""
        print("📂 Chargement données historiques...")
        
        try:
            # Télécharger données historiques SPY
            ticker = yf.Ticker(self.symbol)
            self.historical_data = ticker.history(
                start=self.start_date,
                end=self.end_date,
                interval="1d"
            )
            
            print(f"✅ Données historiques: {len(self.historical_data)} jours")
            print(f"   📅 Période: {self.start_date} à {self.end_date}")
            print(f"   📊 Prix initial: {self.historical_data['Close'].iloc[0]:.2f}")
            print(f"   📊 Prix final: {self.historical_data['Close'].iloc[-1]:.2f}")
            
            # Générer données options simulées basées sur volatilité historique
            self._generate_historical_options_data()
            
            # Générer Order Flow basé sur volume et prix
            self._generate_historical_orderflow_data()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
            return False
    
    def _generate_historical_options_data(self):
        """Générer données options basées sur volatilité historique"""
        print("📈 Génération données options historiques...")
        
        self.options_data = {}
        prices = self.historical_data['Close']
        
        for i, (date, price) in enumerate(prices.items()):
            # Calculer volatilité sur 20 jours
            if i >= 20:
                volatility = prices.iloc[i-20:i].pct_change().std() * 100
            else:
                volatility = 0.15  # Volatilité par défaut
            
            # Générer niveaux GEX basés sur prix et volatilité
            gex1 = price * (1 - volatility/100)
            gex2 = price * (1 + volatility/100)
            
            # Strike levels autour du prix
            strikes = []
            for j in range(-5, 6):
                strike = price * (1 + j * 0.01)  # 1% d'intervalle
                strikes.append({
                    'strike': strike,
                    'put_volume': random.randint(100, 1000),
                    'call_volume': random.randint(100, 1000),
                    'put_call_ratio': random.uniform(0.5, 2.0)
                })
            
            self.options_data[date] = {
                'gamma_exposure': {
                    'gex1': gex1,
                    'gex2': gex2,
                    'volatility': volatility
                },
                'strike_levels': strikes,
                'put_call_ratio': random.uniform(0.8, 1.2)
            }
        
        print(f"   ✅ Options générées: {len(self.options_data)} jours")
    
    def _generate_historical_orderflow_data(self):
        """Générer Order Flow basé sur volume et mouvement de prix"""
        print("🌊 Génération Order Flow historique...")
        
        self.orderflow_data = {}
        prices = self.historical_data['Close']
        volumes = self.historical_data['Volume']
        
        for i, (date, price) in enumerate(prices.items()):
            if i == 0:
                price_change = 0
                volume_ratio = 1.0
            else:
                price_change = (price - prices.iloc[i-1]) / prices.iloc[i-1] * 100
                volume_ratio = volumes.iloc[i] / volumes.iloc[i-1] if volumes.iloc[i-1] > 0 else 1.0
            
            # Déterminer direction du flow
            if price_change > 0.5:
                flow_direction = 'BULLISH'
                flow_intensity = min(abs(price_change) / 2.0, 3.0)
            elif price_change < -0.5:
                flow_direction = 'BEARISH'
                flow_intensity = min(abs(price_change) / 2.0, 3.0)
            else:
                flow_direction = 'NEUTRAL'
                flow_intensity = 1.0
            
            # Ajuster avec volume
            if volume_ratio > 1.5:
                flow_intensity *= 1.5
            elif volume_ratio < 0.7:
                flow_intensity *= 0.7
            
            self.orderflow_data[date] = {
                'aggressive_flow': {
                    'flow_direction': flow_direction,
                    'flow_intensity': flow_intensity,
                    'price_change': price_change,
                    'volume_ratio': volume_ratio
                },
                'bid_ask_imbalance': {
                    'imbalance_percent': random.uniform(-20, 20),
                    'bid_volume': volumes.iloc[i] * random.uniform(0.4, 0.6),
                    'ask_volume': volumes.iloc[i] * random.uniform(0.4, 0.6)
                },
                'cumulative_delta': {
                    'delta': price_change * 1000,  # Delta approximatif
                    'trend': 'BULLISH' if price_change > 0 else 'BEARISH'
                }
            }
        
        print(f"   ✅ Order Flow généré: {len(self.orderflow_data)} jours")
    
    def run_backtest(self):
        """Exécuter backtest sur longue durée"""
        print("🎯 Démarrage backtest longue durée...")
        
        if self.historical_data is None:
            print("❌ Pas de données historiques")
            return False
        
        # Paramètres trading
        initial_capital = 100000  # 100k USD
        position_size = 0.02  # 2% du capital par trade
        max_positions = 5
        
        # Variables tracking
        capital = initial_capital
        positions = []
        trades = []
        equity_curve = []
        
        print(f"   💰 Capital initial: ${initial_capital:,.0f}")
        print(f"   📊 Taille position: {position_size*100}%")
        
        # Parcourir chaque jour
        for i, (date, row) in enumerate(self.historical_data.iterrows()):
            current_price = row['Close']
            current_volume = row['Volume']
            
            # Données du jour
            day_options = self.options_data.get(date, {})
            day_orderflow = self.orderflow_data.get(date, {})
            
            # Générer signaux
            signals = self._generate_daily_signals(date, current_price, day_options, day_orderflow)
            
            # Exécuter trades
            for signal in signals:
                if len(positions) < max_positions:
                    # Calculer taille position
                    trade_size = capital * position_size
                    shares = int(trade_size / current_price)
                    
                    if shares > 0:
                        position = {
                            'id': len(positions) + 1,
                            'side': signal['action'],
                            'entry_price': current_price,
                            'entry_date': date,
                            'shares': shares,
                            'signal': signal['type'],
                            'strength': signal['strength']
                        }
                        positions.append(position)
                        
                        trades.append({
                            'date': date,
                            'action': signal['action'],
                            'price': current_price,
                            'shares': shares,
                            'signal': signal['type'],
                            'capital': capital
                        })
                        
                        print(f"   {date.strftime('%Y-%m-%d')} - {signal['action']} {shares} @ {current_price:.2f} ({signal['type']})")
            
            # Gérer positions existantes
            for position in positions[:]:
                if position['side'] == 'BUY':
                    # Take profit 2% ou Stop loss 1%
                    if current_price > position['entry_price'] * 1.02:
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
                        print(f"   {date.strftime('%Y-%m-%d')} - ✅ CLOSE LONG: +${pnl:.2f}")
                    elif current_price < position['entry_price'] * 0.99:
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
                        print(f"   {date.strftime('%Y-%m-%d')} - ❌ STOP LONG: ${pnl:.2f}")
                
                elif position['side'] == 'SELL':
                    # Take profit 2% ou Stop loss 1%
                    if current_price < position['entry_price'] * 0.98:
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
                        print(f"   {date.strftime('%Y-%m-%d')} - ✅ CLOSE SHORT: +${pnl:.2f}")
                    elif current_price > position['entry_price'] * 1.01:
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
                        print(f"   {date.strftime('%Y-%m-%d')} - ❌ STOP SHORT: ${pnl:.2f}")
            
            # Fermer positions à la fin de la période
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
        
        # Calculer résultats
        self._calculate_backtest_results(trades, equity_curve, initial_capital)
        
        return True
    
    def _generate_daily_signals(self, date, current_price, options, orderflow):
        """Générer signaux quotidiens"""
        signals = []
        
        # Signal basé sur Order Flow
        if orderflow:
            flow = orderflow.get('aggressive_flow', {})
            flow_direction = flow.get('flow_direction', 'NEUTRAL')
            flow_intensity = flow.get('flow_intensity', 1.0)
            
            if flow_intensity > 1.5:
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
        
        # Signal basé sur Options (GEX)
        if options:
            gex1 = options.get('gamma_exposure', {}).get('gex1', 0)
            gex2 = options.get('gamma_exposure', {}).get('gex2', 0)
            
            if current_price < gex1 and random.random() < 0.3:
                signals.append({
                    'type': 'GEX1_SUPPORT',
                    'action': 'BUY',
                    'strength': 0.8
                })
            elif current_price > gex2 and random.random() < 0.3:
                signals.append({
                    'type': 'GEX2_RESISTANCE',
                    'action': 'SELL',
                    'strength': 0.8
                })
        
        # Signal basé sur momentum (prix vs moyenne mobile)
        if len(self.historical_data) > 20:
            ma20 = self.historical_data['Close'].rolling(20).mean().iloc[-1]
            if current_price > ma20 * 1.01 and random.random() < 0.4:
                signals.append({
                    'type': 'MOMENTUM_BULL',
                    'action': 'BUY',
                    'strength': 0.7
                })
            elif current_price < ma20 * 0.99 and random.random() < 0.4:
                signals.append({
                    'type': 'MOMENTUM_BEAR',
                    'action': 'SELL',
                    'strength': 0.7
                })
        
        return signals
    
    def _calculate_backtest_results(self, trades, equity_curve, initial_capital):
        """Calculer résultats du backtest"""
        print("📊 Calcul résultats backtest...")
        
        # Trades fermés (avec P&L)
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
        
        # Drawdown
        max_capital = initial_capital
        max_drawdown = 0
        for point in equity_curve:
            capital = point['capital']
            if capital > max_capital:
                max_capital = capital
            drawdown = (max_capital - capital) / max_capital * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        # Sharpe ratio (approximatif)
        returns = [t['pnl'] for t in closed_trades]
        avg_return = sum(returns) / len(returns) if returns else 0
        std_return = (sum([(r - avg_return) ** 2 for r in returns]) / len(returns)) ** 0.5 if returns else 1
        sharpe_ratio = avg_return / std_return if std_return > 0 else 0
        
        # Résultats
        results = {
            'period': {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'days': len(self.historical_data)
            },
            'trading': {
                'total_trades': total_trades,
                'winning_trades': winning_count,
                'losing_trades': losing_count,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'winning_pnl': winning_pnl,
                'losing_pnl': losing_pnl,
                'profit_factor': profit_factor
            },
            'performance': {
                'initial_capital': initial_capital,
                'final_capital': equity_curve[-1]['capital'] if equity_curve else initial_capital,
                'total_return': total_return,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'avg_trade': total_pnl / total_trades if total_trades > 0 else 0
            },
            'trades': trades,
            'equity_curve': equity_curve
        }
        
        self.test_results['backtest_period'] = results['period']
        self.test_results['trading_results'] = results['trading']
        self.test_results['performance_metrics'] = results['performance']
        
        # Affichage
        print(f"   📊 Trades totaux: {total_trades}")
        print(f"   📊 Win Rate: {win_rate:.1f}%")
        print(f"   📊 Profit Factor: {profit_factor:.2f}")
        print(f"   📊 Retour total: {total_return:.2f}%")
        print(f"   📊 Max Drawdown: {max_drawdown:.2f}%")
        print(f"   📊 Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"   💰 Capital final: ${results['performance']['final_capital']:,.2f}")
        
        return results
    
    def save_results(self):
        """Sauvegarder résultats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/test_results/backtest_longue_duree_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Sauvegardé: {filename}")
        return filename
    
    def run_complete_backtest(self):
        """Exécuter backtest complet"""
        print("🏆 BACKTEST SYSTÈME LONGUE DURÉE - MIA_IA SYSTEM")
        print("=" * 60)
        
        # 1. Charger données historiques
        if not self.load_historical_data():
            return False
        
        # 2. Exécuter backtest
        if not self.run_backtest():
            return False
        
        # 3. Sauvegarder résultats
        self.save_results()
        
        # 4. Résultats finaux
        print("\n" + "=" * 60)
        print("📊 RÉSULTATS BACKTEST LONGUE DURÉE")
        print("=" * 60)
        
        performance = self.test_results.get('performance_metrics', {})
        trading = self.test_results.get('trading_results', {})
        
        print(f"📅 Période: {self.start_date} à {self.end_date}")
        print(f"📊 Trades exécutés: {trading.get('total_trades', 0)}")
        print(f"📊 Win Rate: {trading.get('win_rate', 0):.1f}%")
        print(f"📊 Profit Factor: {trading.get('profit_factor', 0):.2f}")
        print(f"📊 Retour total: {performance.get('total_return', 0):.2f}%")
        print(f"📊 Max Drawdown: {performance.get('max_drawdown', 0):.2f}%")
        print(f"📊 Sharpe Ratio: {performance.get('sharpe_ratio', 0):.2f}")
        print(f"💰 Capital final: ${performance.get('final_capital', 0):,.2f}")
        
        # Critères de succès
        if (trading.get('total_trades', 0) > 10 and 
            trading.get('win_rate', 0) >= 40 and 
            trading.get('profit_factor', 0) >= 1.2):
            print("\n🎉 BACKTEST RÉUSSI ! Système profitable")
            self.test_results['success'] = True
        else:
            print("\n⚠️ Backtest partiel - optimisations nécessaires")
        
        return self.test_results['success']

def main():
    """Fonction principale"""
    print("🏆 BACKTEST SYSTÈME LONGUE DURÉE - MIA_IA SYSTEM")
    print("=" * 60)
    
    backtest = BacktestSystemeLongueDuree()
    success = backtest.run_complete_backtest()
    
    if success:
        print("\n🎉 SYSTÈME VALIDÉ SUR LONGUE DURÉE !")
    else:
        print("\n⚠️ Système nécessite des optimisations")
    
    return success

if __name__ == "__main__":
    main()










