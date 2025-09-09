#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtest Confluence Battle Navale - MIA_IA System
Backtesting avec vraie confluence et stratégie Battle Navale
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

class BacktestConfluenceBattleNavale:
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'battle_navale_results': {},
            'confluence_analysis': {},
            'performance_metrics': {},
            'success': False
        }
        
        # Données historiques
        self.historical_data = None
        self.options_data = None
        self.orderflow_data = None
        
        # Paramètres optimisés
        self.params = {
            'position_size': 0.041,  # 4.1%
            'take_profit': 0.017,    # 1.7%
            'stop_loss': 0.011,      # 1.1%
            'signal_threshold': 1.0, # Seuil signal
            'max_positions': 6       # Max positions
        }
        
        # Période de test
        self.start_date = "2024-01-01"
        self.end_date = "2024-12-31"
        self.symbol = "SPY"
    
    def load_data(self):
        """Charger données historiques"""
        print("📂 Chargement données pour Battle Navale...")
        
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
        """Calculer indicateurs techniques pour confluence"""
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
                price_change = 0  # Initialiser pour le premier jour
            
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
    
    def _generate_battle_navale_signals(self, date, current_price):
        """Générer signaux Battle Navale avec confluence"""
        signals = []
        
        # Calculer niveaux Battle Navale
        levels = self._calculate_battle_navale_levels(date, current_price)
        
        # Analyser zones de combat
        for support_name, support_price, strength in levels['support_levels']:
            if abs(current_price - support_price) / support_price < 0.005:  # Proche du support
                # Calculer confluence pour signal BUY
                confluence = self._calculate_confluence_score(date, current_price, 'BUY')
                
                if confluence['total'] > 0.6:  # Seuil confluence élevé
                    signals.append({
                        'type': f'BATTLE_NAVALE_SUPPORT_{support_name}',
                        'action': 'BUY',
                        'strength': strength,
                        'confluence_score': confluence['total'],
                        'confluence_factors': confluence,
                        'level_price': support_price
                    })
        
        for resistance_name, resistance_price, strength in levels['resistance_levels']:
            if abs(current_price - resistance_price) / resistance_price < 0.005:  # Proche de la résistance
                # Calculer confluence pour signal SELL
                confluence = self._calculate_confluence_score(date, current_price, 'SELL')
                
                if confluence['total'] > 0.6:  # Seuil confluence élevé
                    signals.append({
                        'type': f'BATTLE_NAVALE_RESISTANCE_{resistance_name}',
                        'action': 'SELL',
                        'strength': strength,
                        'confluence_score': confluence['total'],
                        'confluence_factors': confluence,
                        'level_price': resistance_price
                    })
        
        return signals
    
    def run_battle_navale_backtest(self):
        """Exécuter backtest Battle Navale avec confluence"""
        print("⚔️ Démarrage Battle Navale avec Confluence...")
        
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
        print(f"   📊 Paramètres optimisés appliqués")
        
        # Parcourir chaque jour
        for i, (date, row) in enumerate(self.historical_data.iterrows()):
            current_price = row['Close']
            
            # Générer signaux Battle Navale avec confluence
            signals = self._generate_battle_navale_signals(date, current_price)
            
            # Exécuter trades avec gestion avancée
            for signal in signals:
                if len(positions) < self.params['max_positions']:
                    # Taille position basée sur confluence
                    confluence_multiplier = signal['confluence_score']
                    adjusted_position_size = self.params['position_size'] * confluence_multiplier
                    
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
                            'confluence_score': signal['confluence_score'],
                            'level_price': signal.get('level_price', 0)
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
                        
                        print(f"   {date.strftime('%Y-%m-%d')} - {signal['action']} {shares} @ {current_price:.2f}")
                        print(f"      🎯 {signal['type']} (Confluence: {signal['confluence_score']:.2f})")
            
            # Gestion avancée des positions
            for position in positions[:]:
                if position['side'] == 'BUY':
                    # Take profit et stop loss adaptatifs
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
                    # Take profit et stop loss adaptatifs
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
        self._calculate_battle_navale_results(trades, equity_curve, initial_capital)
        
        return True
    
    def _calculate_battle_navale_results(self, trades, equity_curve, initial_capital):
        """Calculer résultats Battle Navale"""
        print("📊 Calcul résultats Battle Navale...")
        
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
        
        # Analyser confluence
        confluence_trades = [t for t in trades if 'confluence_score' in t]
        avg_confluence = sum(t['confluence_score'] for t in confluence_trades) / len(confluence_trades) if confluence_trades else 0
        
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
            'battle_navale': {
                'avg_confluence_score': avg_confluence,
                'high_confluence_trades': len([t for t in confluence_trades if t['confluence_score'] > 0.7]),
                'strategy_effectiveness': 'EXCELLENT' if win_rate > 60 and profit_factor > 1.5 else 'GOOD' if win_rate > 50 else 'NEEDS_IMPROVEMENT'
            }
        }
        
        self.test_results['battle_navale_results'] = results['trading']
        self.test_results['performance_metrics'] = results['performance']
        self.test_results['confluence_analysis'] = results['battle_navale']
        
        # Affichage
        print(f"   📊 Trades totaux: {total_trades}")
        print(f"   📊 Win Rate: {win_rate:.1f}%")
        print(f"   📊 Profit Factor: {profit_factor:.2f}")
        print(f"   📊 Retour total: {total_return:.2f}%")
        print(f"   📊 Max Drawdown: {max_drawdown:.2f}%")
        print(f"   📊 Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"   🎯 Confluence moyenne: {avg_confluence:.2f}")
        print(f"   💰 Capital final: ${results['performance']['final_capital']:,.2f}")
        
        return results
    
    def save_results(self):
        """Sauvegarder résultats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/test_results/battle_navale_confluence_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Sauvegardé: {filename}")
        return filename
    
    def run_complete_backtest(self):
        """Exécuter backtest complet"""
        print("⚔️ BATTLE NAVALE AVEC CONFLUENCE - MIA_IA SYSTEM")
        print("=" * 60)
        
        # 1. Charger données
        if not self.load_data():
            return False
        
        # 2. Exécuter Battle Navale
        if not self.run_battle_navale_backtest():
            return False
        
        # 3. Sauvegarder résultats
        self.save_results()
        
        # 4. Résultats finaux
        print("\n" + "=" * 60)
        print("📊 RÉSULTATS BATTLE NAVALE AVEC CONFLUENCE")
        print("=" * 60)
        
        performance = self.test_results.get('performance_metrics', {})
        trading = self.test_results.get('battle_navale_results', {})
        confluence = self.test_results.get('confluence_analysis', {})
        
        print(f"📅 Période: {self.start_date} à {self.end_date}")
        print(f"📊 Trades exécutés: {trading.get('total_trades', 0)}")
        print(f"📊 Win Rate: {trading.get('win_rate', 0):.1f}%")
        print(f"📊 Profit Factor: {trading.get('profit_factor', 0):.2f}")
        print(f"📊 Retour total: {performance.get('total_return', 0):.2f}%")
        print(f"📊 Max Drawdown: {performance.get('max_drawdown', 0):.2f}%")
        print(f"📊 Sharpe Ratio: {performance.get('sharpe_ratio', 0):.2f}")
        print(f"🎯 Confluence moyenne: {confluence.get('avg_confluence_score', 0):.2f}")
        print(f"💰 Capital final: ${performance.get('final_capital', 0):,.2f}")
        print(f"⚔️ Efficacité stratégie: {confluence.get('strategy_effectiveness', 'UNKNOWN')}")
        
        # Critères de succès
        if (trading.get('total_trades', 0) > 10 and 
            trading.get('win_rate', 0) >= 50 and 
            trading.get('profit_factor', 0) >= 1.2):
            print("\n🎉 BATTLE NAVALE RÉUSSI ! Stratégie profitable")
            self.test_results['success'] = True
        else:
            print("\n⚠️ Battle Navale partiel - optimisations nécessaires")
        
        return self.test_results['success']

def main():
    """Fonction principale"""
    print("⚔️ BATTLE NAVALE AVEC CONFLUENCE - MIA_IA SYSTEM")
    print("=" * 60)
    
    backtest = BacktestConfluenceBattleNavale()
    success = backtest.run_complete_backtest()
    
    if success:
        print("\n🎉 BATTLE NAVALE VALIDÉ !")
    else:
        print("\n⚠️ Battle Navale nécessite des optimisations")
    
    return success

if __name__ == "__main__":
    main()
