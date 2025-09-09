#!/usr/bin/env python3
"""
Signaux de trading basés sur VIX pour MIA_IA System
"""

import numpy as np
from datetime import datetime, timedelta

class VIXSignals:
    def __init__(self, vix_manager):
        self.vix_mgr = vix_manager
        self.vix_history = []
        
    def add_vix_data(self, vix_spot, timestamp=None):
        """Ajouter des données VIX à l'historique"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.vix_history.append({
            'vix': vix_spot,
            'timestamp': timestamp
        })
        
        # Garder seulement les 100 derniers points
        if len(self.vix_history) > 100:
            self.vix_history = self.vix_history[-100:]
    
    def get_vix_extremes(self, lookback_periods=20):
        """Détecter les extrêmes VIX (survente/surachat)"""
        if len(self.vix_history) < lookback_periods:
            return {'status': 'INSUFFICIENT_DATA'}
        
        recent_vix = [d['vix'] for d in self.vix_history[-lookback_periods:]]
        current_vix = recent_vix[-1]
        
        # Calculer les percentiles
        p20 = np.percentile(recent_vix, 20)
        p80 = np.percentile(recent_vix, 80)
        
        # Déterminer le signal
        if current_vix <= p20:
            signal = 'OVERSOLD'  # VIX bas = opportunité d'achat
            strength = (p20 - current_vix) / p20
        elif current_vix >= p80:
            signal = 'OVERBOUGHT'  # VIX haut = risque de correction
            strength = (current_vix - p80) / p80
        else:
            signal = 'NEUTRAL'
            strength = 0
        
        return {
            'signal': signal,
            'strength': strength,
            'current_vix': current_vix,
            'p20': p20,
            'p80': p80,
            'lookback_periods': lookback_periods
        }
    
    def get_vix_momentum(self, short_period=5, long_period=20):
        """Analyser le momentum VIX"""
        if len(self.vix_history) < long_period:
            return {'status': 'INSUFFICIENT_DATA'}
        
        recent_vix = [d['vix'] for d in self.vix_history]
        
        # Moyennes mobiles
        short_ma = np.mean(recent_vix[-short_period:])
        long_ma = np.mean(recent_vix[-long_period:])
        
        # Momentum
        momentum = short_ma - long_ma
        momentum_pct = (momentum / long_ma) * 100
        
        # Signal de momentum
        if momentum_pct > 10:
            momentum_signal = 'ACCELERATING'  # VIX monte rapidement
        elif momentum_pct < -10:
            momentum_signal = 'DECELERATING'  # VIX baisse rapidement
        else:
            momentum_signal = 'STABLE'
        
        return {
            'momentum_signal': momentum_signal,
            'momentum_pct': momentum_pct,
            'short_ma': short_ma,
            'long_ma': long_ma,
            'current_vix': recent_vix[-1]
        }
    
    def get_volatility_regime(self):
        """Déterminer le régime de volatilité"""
        vix_spot = self.vix_mgr.get_vix_spot()
        
        if vix_spot is None:
            return {'status': 'UNKNOWN'}
        
        # Régimes de volatilité
        if vix_spot < 12:
            regime = 'ULTRA_LOW_VOL'
            description = 'Volatilité ultra-faible, risque de correction'
            trading_implication = 'Augmenter la taille des positions, surveiller les signaux de retournement'
        elif vix_spot < 18:
            regime = 'LOW_VOL'
            description = 'Volatilité faible, marché calme'
            trading_implication = 'Trading normal, opportunités de trend following'
        elif vix_spot < 25:
            regime = 'NORMAL_VOL'
            description = 'Volatilité normale'
            trading_implication = 'Trading standard, équilibre risque/récompense'
        elif vix_spot < 35:
            regime = 'HIGH_VOL'
            description = 'Volatilité élevée, marché stressé'
            trading_implication = 'Réduire la taille des positions, privilégier le hedging'
        else:
            regime = 'EXTREME_VOL'
            description = 'Volatilité extrême, panique'
            trading_implication = 'Position sizing minimal, opportunités de mean reversion'
        
        return {
            'regime': regime,
            'vix_level': vix_spot,
            'description': description,
            'trading_implication': trading_implication
        }
    
    def get_trading_signals(self):
        """Générer des signaux de trading complets"""
        # Mettre à jour l'historique
        current_vix = self.vix_mgr.get_vix_spot()
        if current_vix:
            self.add_vix_data(current_vix)
        
        # Analyser les différents aspects
        extremes = self.get_vix_extremes()
        momentum = self.get_vix_momentum()
        regime = self.get_volatility_regime()
        sentiment = self.vix_mgr.get_market_sentiment()
        
        # Générer les signaux
        signals = []
        
        # Signal basé sur les extrêmes
        if extremes.get('signal') == 'OVERSOLD' and extremes.get('strength', 0) > 0.2:
            signals.append({
                'type': 'VIX_OVERSOLD',
                'action': 'BUY_OPPORTUNITY',
                'strength': extremes['strength'],
                'reason': f"VIX {current_vix} en survente (p20: {extremes.get('p20', 0)})"
            })
        
        elif extremes.get('signal') == 'OVERBOUGHT' and extremes.get('strength', 0) > 0.2:
            signals.append({
                'type': 'VIX_OVERBOUGHT',
                'action': 'REDUCE_RISK',
                'strength': extremes['strength'],
                'reason': f"VIX {current_vix} en surachat (p80: {extremes.get('p80', 0)})"
            })
        
        # Signal basé sur le momentum
        if momentum.get('momentum_signal') == 'ACCELERATING':
            signals.append({
                'type': 'VIX_ACCELERATING',
                'action': 'HEDGE_AGGRESSIVE',
                'strength': abs(momentum.get('momentum_pct', 0)) / 100,
                'reason': f"VIX accélère (+{momentum.get('momentum_pct', 0):.1f}%)"
            })
        
        # Signal basé sur le régime
        if regime.get('regime') in ['HIGH_VOL', 'EXTREME_VOL']:
            signals.append({
                'type': 'HIGH_VOLATILITY',
                'action': 'DEFENSIVE_MODE',
                'strength': 1.0,
                'reason': f"Régime {regime.get('regime')}: {regime.get('description', '')}"
            })
        
        return {
            'current_vix': current_vix,
            'sentiment': sentiment,
            'regime': regime,
            'extremes': extremes,
            'momentum': momentum,
            'signals': signals,
            'timestamp': datetime.now()
        }

# Exemple d'utilisation
if __name__ == "__main__":
    from vix_integration import VIXManager
    from ib_insync import IB
    
    # Connexion
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=7)
    
    # Initialiser
    vix_mgr = VIXManager(ib)
    vix_signals = VIXSignals(vix_mgr)
    
    # Simuler des données historiques
    for i in range(30):
        vix_signals.add_vix_data(15 + i * 0.5, datetime.now() - timedelta(hours=i))
    
    # Générer les signaux
    signals = vix_signals.get_trading_signals()
    print("=== VIX TRADING SIGNALS ===")
    print(f"Current VIX: {signals['current_vix']}")
    print(f"Sentiment: {signals['sentiment']}")
    print(f"Regime: {signals['regime']['regime']}")
    print(f"Signals: {len(signals['signals'])}")
    
    for signal in signals['signals']:
        print(f"  - {signal['type']}: {signal['action']} ({signal['reason']})")
    
    ib.disconnect()




