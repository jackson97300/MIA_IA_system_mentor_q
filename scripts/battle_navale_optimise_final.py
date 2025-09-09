#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Battle Navale Optimisé Final - MIA_IA System
Version optimisée avec filtres intelligents
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

class BattleNavaleOptimiseFinal:
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
        
        # Paramètres OPTIMISÉS
        self.params = {
            'position_size': 0.08,     # 8% - Équilibré
            'take_profit': 0.025,      # 2.5% - Plus réaliste
            'stop_loss': 0.012,        # 1.2% - Équilibré
            'max_positions': 6         # Limité pour éviter l'over-trading
        }
        
        # Filtres intelligents
        self.filters = {
            'min_confluence': 0.4,     # Score confluence minimum
            'max_daily_trades': 3,     # Max trades par jour
            'trend_filter': True,      # Filtrer contre la tendance
            'volume_filter': True,     # Filtrer par volume
            'volatility_filter': True  # Filtrer par volatilité
        }
        
        # Période de test
        self.start_date = "2024-01-01"
        self.end_date = "2024-12-31"
        self.symbol = "SPY"
    
    def load_data(self):
        """Charger données historiques"""
        print("📂 Chargement données pour Battle Navale Optimisé Final...")
        
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
        """Calculer indicateurs techniques optimisés"""
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
        
        # Tendance (SMA 50)
        self.historical_data['SMA_50'] = self.historical_data['Close'].rolling(window=50).mean()
        
        # ATR (Average True Range)
        high_low = self.historical_data['High'] - self.historical_data['Low']
        high_close = np.abs(self.historical_data['High'] - self.historical_data['Close'].shift())
        low_close = np.abs(self.historical_data['Low'] - self.historical_data['Close'].shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        self.historical_data['ATR'] = true_range.rolling(window=14).mean()
        
        # Volatilité
        self.historical_data['Volatility'] = self.historical_data['Close'].rolling(window=20).std() / self.historical_data['Close'].rolling(window=20).mean()
        
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
    
    def _calculate_confluence_score(self, date, current_price, signal_type):
        """Calculer score de confluence optimisé"""
        confluence_factors = {
            'technical': 0,
            'volume': 0,
            'options': 0,
            'orderflow': 0,
            'trend': 0,
            'total': 0
        }
        
        row = self.historical_data.loc[date]
        
        # 1. FACTEURS TECHNIQUES (25%)
        tech_score = 0
        
        # RSI
        rsi = row['RSI']
        if signal_type == 'BUY' and rsi < 35:
            tech_score += 0.3
        elif signal_type == 'SELL' and rsi > 65:
            tech_score += 0.3
        
        # MACD
        macd = row['MACD']
        macd_signal = row['MACD_Signal']
        if signal_type == 'BUY' and macd > macd_signal and macd > 0:
            tech_score += 0.3
        elif signal_type == 'SELL' and macd < macd_signal and macd < 0:
            tech_score += 0.3
        
        # Bollinger Bands
        bb_upper = row['BB_Upper']
        bb_lower = row['BB_Lower']
        if signal_type == 'BUY' and current_price < bb_lower * 1.01:
            tech_score += 0.4
        elif signal_type == 'SELL' and current_price > bb_upper * 0.99:
            tech_score += 0.4
        
        confluence_factors['technical'] = min(tech_score, 1.0)
        
        # 2. FACTEURS VOLUME (20%)
        volume_score = 0
        volume_ratio = row['Volume'] / self.historical_data['Volume'].rolling(20).mean().loc[date]
        
        if volume_ratio > 1.3:
            volume_score = 1.0
        elif volume_ratio > 1.1:
            volume_score = 0.7
        elif volume_ratio > 1.0:
            volume_score = 0.4
        
        confluence_factors['volume'] = volume_score
        
        # 3. FACTEURS OPTIONS (20%)
        options_score = 0
        if date in self.options_data:
            gex1 = self.options_data[date]['gamma_exposure']['gex1']
            gex2 = self.options_data[date]['gamma_exposure']['gex2']
            
            if signal_type == 'BUY' and current_price < gex1 * 1.02:
                options_score = 0.8
            elif signal_type == 'SELL' and current_price > gex2 * 0.98:
                options_score = 0.8
        
        confluence_factors['options'] = options_score
        
        # 4. FACTEURS ORDER FLOW (15%)
        orderflow_score = 0
        if date in self.orderflow_data:
            flow = self.orderflow_data[date]['aggressive_flow']
            flow_direction = flow['flow_direction']
            flow_intensity = flow['flow_intensity']
            
            if signal_type == 'BUY' and flow_direction == 'BULLISH' and flow_intensity > 1.2:
                orderflow_score = 0.8
            elif signal_type == 'SELL' and flow_direction == 'BEARISH' and flow_intensity > 1.2:
                orderflow_score = 0.8
        
        confluence_factors['orderflow'] = orderflow_score
        
        # 5. FACTEURS TENDANCE (20%)
        trend_score = 0
        sma_50 = row['SMA_50']
        
        if signal_type == 'BUY' and current_price > sma_50:
            trend_score = 0.8
        elif signal_type == 'SELL' and current_price < sma_50:
            trend_score = 0.8
        
        confluence_factors['trend'] = trend_score
        
        # SCORE TOTAL
        confluence_factors['total'] = (
            confluence_factors['technical'] * 0.25 +
            confluence_factors['volume'] * 0.20 +
            confluence_factors['options'] * 0.20 +
            confluence_factors['orderflow'] * 0.15 +
            confluence_factors['trend'] * 0.20
        )
        
        return confluence_factors
    
    def _apply_intelligent_filters(self, date, current_price, signal_type, confluence_score):
        """Appliquer filtres intelligents"""
        row = self.historical_data.loc[date]
        
        # 1. FILTRE CONFLUENCE
        if confluence_score < self.filters['min_confluence']:
            return False
        
        # 2. FILTRE TENDANCE
        if self.filters['trend_filter']:
            sma_50 = row['SMA_50']
            if signal_type == 'BUY' and current_price < sma_50 * 0.98:
                return False  # Éviter les achats trop bas dans une tendance baissière
            elif signal_type == 'SELL' and current_price > sma_50 * 1.02:
                return False  # Éviter les ventes trop hautes dans une tendance haussière
        
        # 3. FILTRE VOLUME
        if self.filters['volume_filter']:
            volume_ratio = row['Volume'] / self.historical_data['Volume'].rolling(20).mean().loc[date]
            if volume_ratio < 0.8:
                return False  # Éviter les trades avec volume faible
        
        # 4. FILTRE VOLATILITÉ
        if self.filters['volatility_filter']:
            volatility = row['Volatility']
            if volatility > 0.03:  # Éviter les périodes trop volatiles
                return False
        
        # 5. FILTRE ATR
        atr = row['ATR']
        atr_ratio = atr / current_price
        if atr_ratio > 0.025:  # Éviter les périodes de forte volatilité
            return False
        
        return True
    
    def _generate_optimized_signals(self, date, current_price):
        """Générer signaux optimisés avec filtres intelligents"""
        signals = []
        
        row = self.historical_data.loc[date]
        
        # 1. SIGNAL RSI (Seuils optimisés)
        rsi = row['RSI']
        if rsi < 35:  # Survente optimisée
            confluence = self._calculate_confluence_score(date, current_price, 'BUY')
            if self._apply_intelligent_filters(date, current_price, 'BUY', confluence['total']):
                signals.append({
                    'type': 'RSI_OVERSOLD',
                    'action': 'BUY',
                    'strength': 0.7,
                    'confluence_score': confluence['total'],
                    'reason': f'RSI survente: {rsi:.1f}'
                })
        elif rsi > 65:  # Surachat optimisé
            confluence = self._calculate_confluence_score(date, current_price, 'SELL')
            if self._apply_intelligent_filters(date, current_price, 'SELL', confluence['total']):
                signals.append({
                    'type': 'RSI_OVERBOUGHT',
                    'action': 'SELL',
                    'strength': 0.7,
                    'confluence_score': confluence['total'],
                    'reason': f'RSI surachat: {rsi:.1f}'
                })
        
        # 2. SIGNAL MACD (Croisement avec confirmation)
        macd = row['MACD']
        macd_signal = row['MACD_Signal']
        
        if macd > macd_signal and macd > 0:  # Signal haussier confirmé
            confluence = self._calculate_confluence_score(date, current_price, 'BUY')
            if self._apply_intelligent_filters(date, current_price, 'BUY', confluence['total']):
                signals.append({
                    'type': 'MACD_BULLISH',
                    'action': 'BUY',
                    'strength': 0.6,
                    'confluence_score': confluence['total'],
                    'reason': f'MACD haussier: {macd:.4f}'
                })
        elif macd < macd_signal and macd < 0:  # Signal baissier confirmé
            confluence = self._calculate_confluence_score(date, current_price, 'SELL')
            if self._apply_intelligent_filters(date, current_price, 'SELL', confluence['total']):
                signals.append({
                    'type': 'MACD_BEARISH',
                    'action': 'SELL',
                    'strength': 0.6,
                    'confluence_score': confluence['total'],
                    'reason': f'MACD baissier: {macd:.4f}'
                })
        
        # 3. SIGNAL BOLLINGER BANDS (Contact direct)
        bb_upper = row['BB_Upper']
        bb_lower = row['BB_Lower']
        
        if current_price < bb_lower:  # Contact support
            confluence = self._calculate_confluence_score(date, current_price, 'BUY')
            if self._apply_intelligent_filters(date, current_price, 'BUY', confluence['total']):
                signals.append({
                    'type': 'BB_SUPPORT',
                    'action': 'BUY',
                    'strength': 0.8,
                    'confluence_score': confluence['total'],
                    'reason': f'Contact support BB: {bb_lower:.2f}'
                })
        elif current_price > bb_upper:  # Contact résistance
            confluence = self._calculate_confluence_score(date, current_price, 'SELL')
            if self._apply_intelligent_filters(date, current_price, 'SELL', confluence['total']):
                signals.append({
                    'type': 'BB_RESISTANCE',
                    'action': 'SELL',
                    'strength': 0.8,
                    'confluence_score': confluence['total'],
                    'reason': f'Contact résistance BB: {bb_upper:.2f}'
                })
        
        # 4. SIGNAL GEX (Contact direct)
        if date in self.options_data:
            gex1 = self.options_data[date]['gamma_exposure']['gex1']
            gex2 = self.options_data[date]['gamma_exposure']['gex2']
            
            if current_price < gex1:  # Contact support GEX
                confluence = self._calculate_confluence_score(date, current_price, 'BUY')
                if self._apply_intelligent_filters(date, current_price, 'BUY', confluence['total']):
                    signals.append({
                        'type': 'GEX_SUPPORT',
                        'action': 'BUY',
                        'strength': 0.9,
                        'confluence_score': confluence['total'],
                        'reason': f'Contact support GEX: {gex1:.2f}'
                    })
            elif current_price > gex2:  # Contact résistance GEX
                confluence = self._calculate_confluence_score(date, current_price, 'SELL')
                if self._apply_intelligent_filters(date, current_price, 'SELL', confluence['total']):
                    signals.append({
                        'type': 'GEX_RESISTANCE',
                        'action': 'SELL',
                        'strength': 0.9,
                        'confluence_score': confluence['total'],
                        'reason': f'Contact résistance GEX: {gex2:.2f}'
                    })
        
        # Trier par score de confluence (meilleurs en premier)
        signals.sort(key=lambda x: x['confluence_score'], reverse=True)
        
        # Limiter le nombre de signaux par jour
        return signals[:self.filters['max_daily_trades']]
    
    def run_optimized_backtest(self):
        """Exécuter backtest optimisé"""
        print("⚔️ Démarrage Battle Navale Optimisé Final...")
        
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
        print(f"   🔍 Filtres intelligents activés")
        
        # Parcourir chaque jour
        for i, (date, row) in enumerate(self.historical_data.iterrows()):
            current_price = row['Close']
            
            # Générer signaux optimisés
            signals = self._generate_optimized_signals(date, current_price)
            
            # Exécuter trades
            for signal in signals:
                if len(positions) < self.params['max_positions']:
                    # Taille position basée sur confluence
                    adjusted_position_size = self.params['position_size'] * signal['confluence_score']
                    
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
                            'confluence_score': signal['confluence_score']
                        }
                        positions.append(position)
                        
                        trades.append({
                            'date': date,
                            'action': signal['action'],
                            'price': current_price,
                            'shares': shares,
                            'signal': signal['type'],
                            'reason': signal['reason'],
                            'confluence_score': signal['confluence_score'],
                            'capital': capital
                        })
                        
                        print(f"   {date.strftime('%Y-%m-%d')} - {signal['action']} {shares} @ {current_price:.2f}")
                        print(f"      🎯 {signal['type']} - {signal['reason']}")
                        print(f"      📊 Confluence: {signal['confluence_score']:.2f}")
            
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
        print("📊 Calcul résultats Battle Navale Optimisé Final...")
        
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
        filename = f"data/test_results/battle_navale_optimise_final_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Sauvegardé: {filename}")
        return filename
    
    def run_complete_backtest(self):
        """Exécuter backtest complet"""
        print("⚔️ BATTLE NAVALE OPTIMISÉ FINAL - MIA_IA SYSTEM")
        print("=" * 60)
        
        # 1. Charger données
        if not self.load_data():
            return False
        
        # 2. Exécuter Battle Navale optimisé
        if not self.run_optimized_backtest():
            return False
        
        # 3. Sauvegarder résultats
        self.save_results()
        
        # 4. Résultats finaux
        print("\n" + "=" * 60)
        print("📊 RÉSULTATS BATTLE NAVALE OPTIMISÉ FINAL")
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
        if (trading.get('total_trades', 0) > 20 and 
            trading.get('win_rate', 0) >= 45 and 
            trading.get('profit_factor', 0) >= 1.1):
            print("\n🎉 BATTLE NAVALE OPTIMISÉ FINAL RÉUSSI !")
            self.test_results['success'] = True
        else:
            print("\n⚠️ Battle Navale optimisé final - optimisations nécessaires")
        
        return self.test_results['success']

def main():
    """Fonction principale"""
    print("⚔️ BATTLE NAVALE OPTIMISÉ FINAL - MIA_IA SYSTEM")
    print("=" * 60)
    
    backtest = BattleNavaleOptimiseFinal()
    success = backtest.run_complete_backtest()
    
    if success:
        print("\n🎉 BATTLE NAVALE OPTIMISÉ FINAL VALIDÉ !")
    else:
        print("\n⚠️ Battle Navale optimisé final nécessite des optimisations")
    
    return success

if __name__ == "__main__":
    main()










