#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Battle Navale Simplifié - MIA_IA System
Version simplifiée pour générer des signaux effectifs
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

class BattleNavaleSimplifie:
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'battle_navale_results': {},
            'performance_metrics': {},
            'success': False
        }
        
        # Données historiques
        self.historical_data = None
        self.options_data = None
        self.orderflow_data = None
        
        # Paramètres simplifiés
        self.params = {
            'position_size': 0.05,     # 5%
            'take_profit': 0.02,       # 2%
            'stop_loss': 0.01,         # 1%
            'max_positions': 5         # Max positions
        }
        
        # Période de test
        self.start_date = "2024-01-01"
        self.end_date = "2024-12-31"
        self.symbol = "SPY"
    
    def load_data(self):
        """Charger données historiques"""
        print("📂 Chargement données pour Battle Navale Simplifié...")
        
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
        """Calculer indicateurs techniques simplifiés"""
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
    
    def _generate_simple_signals(self, date, current_price):
        """Générer signaux simplifiés basés sur indicateurs"""
        signals = []
        
        row = self.historical_data.loc[date]
        
        # 1. SIGNAL RSI (Survente/Surachat)
        rsi = row['RSI']
        if rsi < 30:  # Survente
            signals.append({
                'type': 'RSI_OVERSOLD',
                'action': 'BUY',
                'strength': 0.7,
                'reason': f'RSI survente: {rsi:.1f}'
            })
        elif rsi > 70:  # Surachat
            signals.append({
                'type': 'RSI_OVERBOUGHT',
                'action': 'SELL',
                'strength': 0.7,
                'reason': f'RSI surachat: {rsi:.1f}'
            })
        
        # 2. SIGNAL MACD (Croisement)
        macd = row['MACD']
        macd_signal = row['MACD_Signal']
        
        if macd > macd_signal and macd > 0:  # Signal haussier
            signals.append({
                'type': 'MACD_BULLISH',
                'action': 'BUY',
                'strength': 0.6,
                'reason': f'MACD haussier: {macd:.4f}'
            })
        elif macd < macd_signal and macd < 0:  # Signal baissier
            signals.append({
                'type': 'MACD_BEARISH',
                'action': 'SELL',
                'strength': 0.6,
                'reason': f'MACD baissier: {macd:.4f}'
            })
        
        # 3. SIGNAL BOLLINGER BANDS (Rebond)
        bb_upper = row['BB_Upper']
        bb_lower = row['BB_Lower']
        
        if current_price < bb_lower:  # Rebond support
            signals.append({
                'type': 'BB_SUPPORT',
                'action': 'BUY',
                'strength': 0.8,
                'reason': f'Support BB: {bb_lower:.2f}'
            })
        elif current_price > bb_upper:  # Rebond résistance
            signals.append({
                'type': 'BB_RESISTANCE',
                'action': 'SELL',
                'strength': 0.8,
                'reason': f'Résistance BB: {bb_upper:.2f}'
            })
        
        # 4. SIGNAL VWAP (Retour à la moyenne)
        vwap = row['VWAP']
        vwap_distance = abs(current_price - vwap) / vwap
        
        if vwap_distance > 0.01:  # Écart significatif du VWAP
            if current_price < vwap:
                signals.append({
                    'type': 'VWAP_MEAN_REVERSION',
                    'action': 'BUY',
                    'strength': 0.5,
                    'reason': f'Retour VWAP: {vwap:.2f}'
                })
            else:
                signals.append({
                    'type': 'VWAP_MEAN_REVERSION',
                    'action': 'SELL',
                    'strength': 0.5,
                    'reason': f'Retour VWAP: {vwap:.2f}'
                })
        
        # 5. SIGNAL GEX (Options)
        if date in self.options_data:
            gex1 = self.options_data[date]['gamma_exposure']['gex1']
            gex2 = self.options_data[date]['gamma_exposure']['gex2']
            
            if current_price < gex1:  # Support GEX
                signals.append({
                    'type': 'GEX_SUPPORT',
                    'action': 'BUY',
                    'strength': 0.9,
                    'reason': f'Support GEX: {gex1:.2f}'
                })
            elif current_price > gex2:  # Résistance GEX
                signals.append({
                    'type': 'GEX_RESISTANCE',
                    'action': 'SELL',
                    'strength': 0.9,
                    'reason': f'Résistance GEX: {gex2:.2f}'
                })
        
        # 6. SIGNAL ORDER FLOW
        if date in self.orderflow_data:
            flow = self.orderflow_data[date]['aggressive_flow']
            flow_direction = flow['flow_direction']
            flow_intensity = flow['flow_intensity']
            
            if flow_direction == 'BULLISH' and flow_intensity > 1.5:
                signals.append({
                    'type': 'ORDERFLOW_BULLISH',
                    'action': 'BUY',
                    'strength': 0.7,
                    'reason': f'Flow haussier: {flow_intensity:.2f}'
                })
            elif flow_direction == 'BEARISH' and flow_intensity > 1.5:
                signals.append({
                    'type': 'ORDERFLOW_BEARISH',
                    'action': 'SELL',
                    'strength': 0.7,
                    'reason': f'Flow baissier: {flow_intensity:.2f}'
                })
        
        return signals
    
    def run_simplified_backtest(self):
        """Exécuter backtest simplifié"""
        print("⚔️ Démarrage Battle Navale Simplifié...")
        
        if self.historical_data is None:
            print("❌ Pas de données historiques")
            return False
        
        # Paramètres trading
        initial_capital = 100000
        capital = initial_capital
        positions = []
        trades = []
        equity_curve = []
        
        print(f"   💰 Capital initial: ${initial_capital:,.0f}")
        print(f"   📊 Paramètres simplifiés appliqués")
        
        # Parcourir chaque jour
        for i, (date, row) in enumerate(self.historical_data.iterrows()):
            current_price = row['Close']
            
            # Générer signaux simplifiés
            signals = self._generate_simple_signals(date, current_price)
            
            # Exécuter trades
            for signal in signals:
                if len(positions) < self.params['max_positions']:
                    # Taille position basée sur force du signal
                    adjusted_position_size = self.params['position_size'] * signal['strength']
                    
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
                            'reason': signal['reason'],
                            'strength': signal['strength']
                        }
                        positions.append(position)
                        
                        trades.append({
                            'date': date,
                            'action': signal['action'],
                            'price': current_price,
                            'shares': shares,
                            'signal': signal['type'],
                            'reason': signal['reason'],
                            'strength': signal['strength'],
                            'capital': capital
                        })
                        
                        print(f"   {date.strftime('%Y-%m-%d')} - {signal['action']} {shares} @ {current_price:.2f}")
                        print(f"      🎯 {signal['type']} - {signal['reason']}")
            
            # Gestion des positions
            for position in positions[:]:
                if position['side'] == 'BUY':
                    tp_price = position['entry_price'] * (1 + self.params['take_profit'])
                    sl_price = position['entry_price'] * (1 - self.params['stop_loss'])
                    
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
                        print(f"   {date.strftime('%Y-%m-%d')} - ✅ CLOSE LONG: +${pnl:.2f}")
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
                        print(f"   {date.strftime('%Y-%m-%d')} - ❌ STOP LONG: ${pnl:.2f}")
                
                elif position['side'] == 'SELL':
                    tp_price = position['entry_price'] * (1 - self.params['take_profit'])
                    sl_price = position['entry_price'] * (1 + self.params['stop_loss'])
                    
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
                        print(f"   {date.strftime('%Y-%m-%d')} - ✅ CLOSE SHORT: +${pnl:.2f}")
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
                        print(f"   {date.strftime('%Y-%m-%d')} - ❌ STOP SHORT: ${pnl:.2f}")
            
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
        
        # Calculer résultats
        self._calculate_results(trades, equity_curve, initial_capital)
        
        return True
    
    def _calculate_results(self, trades, equity_curve, initial_capital):
        """Calculer résultats"""
        print("📊 Calcul résultats Battle Navale Simplifié...")
        
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
        
        # Drawdown
        max_capital = initial_capital
        max_drawdown = 0
        for point in equity_curve:
            capital = point['capital']
            if capital > max_capital:
                max_capital = capital
            drawdown = (max_capital - capital) / max_capital * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        # Sharpe ratio
        returns = [t['pnl'] for t in closed_trades]
        avg_return = sum(returns) / len(returns) if returns else 0
        std_return = (sum([(r - avg_return) ** 2 for r in returns]) / len(returns)) ** 0.5 if returns else 1
        sharpe_ratio = avg_return / std_return if std_return > 0 else 0
        
        # Analyser types de signaux
        signal_types = {}
        for trade in trades:
            if 'signal' in trade:
                signal_type = trade['signal']
                if signal_type not in signal_types:
                    signal_types[signal_type] = 0
                signal_types[signal_type] += 1
        
        # Résultats
        results = {
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
            'signals': signal_types
        }
        
        self.test_results['battle_navale_results'] = results['trading']
        self.test_results['performance_metrics'] = results['performance']
        
        # Affichage
        print(f"   📊 Trades totaux: {total_trades}")
        print(f"   📊 Win Rate: {win_rate:.1f}%")
        print(f"   📊 Profit Factor: {profit_factor:.2f}")
        print(f"   📊 Retour total: {total_return:.2f}%")
        print(f"   📊 Max Drawdown: {max_drawdown:.2f}%")
        print(f"   📊 Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"   💰 Capital final: ${results['performance']['final_capital']:,.2f}")
        
        print(f"\n   📈 TYPES DE SIGNAUX:")
        for signal_type, count in signal_types.items():
            print(f"      {signal_type}: {count} trades")
        
        return results
    
    def save_results(self):
        """Sauvegarder résultats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/test_results/battle_navale_simplifie_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Sauvegardé: {filename}")
        return filename
    
    def run_complete_backtest(self):
        """Exécuter backtest complet"""
        print("⚔️ BATTLE NAVALE SIMPLIFIÉ - MIA_IA SYSTEM")
        print("=" * 60)
        
        # 1. Charger données
        if not self.load_data():
            return False
        
        # 2. Exécuter Battle Navale simplifié
        if not self.run_simplified_backtest():
            return False
        
        # 3. Sauvegarder résultats
        self.save_results()
        
        # 4. Résultats finaux
        print("\n" + "=" * 60)
        print("📊 RÉSULTATS BATTLE NAVALE SIMPLIFIÉ")
        print("=" * 60)
        
        performance = self.test_results.get('performance_metrics', {})
        trading = self.test_results.get('battle_navale_results', {})
        
        print(f"📅 Période: {self.start_date} à {self.end_date}")
        print(f"📊 Trades exécutés: {trading.get('total_trades', 0)}")
        print(f"📊 Win Rate: {trading.get('win_rate', 0):.1f}%")
        print(f"📊 Profit Factor: {trading.get('profit_factor', 0):.2f}")
        print(f"📊 Retour total: {performance.get('total_return', 0):.2f}%")
        print(f"📊 Max Drawdown: {performance.get('max_drawdown', 0):.2f}%")
        print(f"📊 Sharpe Ratio: {performance.get('sharpe_ratio', 0):.2f}")
        print(f"💰 Capital final: ${performance.get('final_capital', 0):,.2f}")
        
        # Critères de succès
        if (trading.get('total_trades', 0) > 5 and 
            trading.get('win_rate', 0) >= 40 and 
            trading.get('profit_factor', 0) >= 1.1):
            print("\n🎉 BATTLE NAVALE SIMPLIFIÉ RÉUSSI !")
            self.test_results['success'] = True
        else:
            print("\n⚠️ Battle Navale simplifié - optimisations nécessaires")
        
        return self.test_results['success']

def main():
    """Fonction principale"""
    print("⚔️ BATTLE NAVALE SIMPLIFIÉ - MIA_IA SYSTEM")
    print("=" * 60)
    
    backtest = BattleNavaleSimplifie()
    success = backtest.run_complete_backtest()
    
    if success:
        print("\n🎉 BATTLE NAVALE SIMPLIFIÉ VALIDÉ !")
    else:
        print("\n⚠️ Battle Navale simplifié nécessite des optimisations")
    
    return success

if __name__ == "__main__":
    main()










