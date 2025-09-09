#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Récupération Données Backtesting Weekend - MIA_IA System
Récupère les données historiques et niveaux options pour backtesting
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
import requests
import urllib3
import yfinance as yf
import pandas as pd

# Désactiver les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class RecuperationBacktestingWeekend:
    def __init__(self):
        self.backtesting_data = {
            'timestamp': datetime.now().isoformat(),
            'friday_close': None,
            'es_historical_data': {},
            'spx_historical_data': {},
            'options_levels': {},
            'market_analysis': {},
            'success': False,
            'errors': []
        }
    
    def get_friday_close_time(self):
        """Déterminer l'heure de fermeture du vendredi"""
        today = datetime.now()
        
        # Trouver le dernier vendredi
        days_since_friday = (today.weekday() - 4) % 7
        if days_since_friday == 0:  # Aujourd'hui est vendredi
            friday = today
        else:
            friday = today - timedelta(days=days_since_friday)
        
        # Heure de fermeture US (16:00 EST = 21:00 UTC en hiver, 20:00 UTC en été)
        friday_close = friday.replace(hour=21, minute=0, second=0, microsecond=0)
        
        print(f"📅 Dernier vendredi: {friday.strftime('%Y-%m-%d')}")
        print(f"🕐 Heure de fermeture: {friday_close.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.backtesting_data['friday_close'] = friday_close.isoformat()
        return friday_close
    
    def get_es_historical_data(self):
        """Récupérer données historiques ES via Yahoo Finance"""
        print("📈 Récupération données historiques ES...")
        
        try:
            # ES futures via Yahoo Finance (approximatif)
            es_ticker = "ES=F"  # E-mini S&P 500 futures
            
            # Récupérer données des 30 derniers jours
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            es_data = yf.download(es_ticker, start=start_date, end=end_date, interval="1d")
            
            if not es_data.empty:
                print("✅ Données ES récupérées")
                
                # Convertir en format compatible
                historical_data = []
                for date, row in es_data.iterrows():
                    historical_data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'open': float(row['Open']),
                        'high': float(row['High']),
                        'low': float(row['Low']),
                        'close': float(row['Close']),
                        'volume': int(row['Volume'])
                    })
                
                self.backtesting_data['es_historical_data'] = {
                    'symbol': 'ES',
                    'period': '30d',
                    'data': historical_data,
                    'last_close': float(es_data['Close'].iloc[-1]),
                    'records_count': len(historical_data)
                }
                
                print(f"   - Période: 30 jours")
                print(f"   - Dernier close: {self.backtesting_data['es_historical_data']['last_close']}")
                print(f"   - Records: {len(historical_data)}")
                
                return True
            else:
                print("❌ Données ES non disponibles")
                return False
                
        except Exception as e:
            print(f"❌ Erreur ES: {e}")
            self.backtesting_data['errors'].append(f"ES Data: {str(e)}")
            return False
    
    def get_spx_historical_data(self):
        """Récupérer données historiques SPX"""
        print("📊 Récupération données historiques SPX...")
        
        try:
            # SPX via Yahoo Finance
            spx_ticker = "^SPX"
            
            # Récupérer données des 30 derniers jours
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            spx_data = yf.download(spx_ticker, start=start_date, end=end_date, interval="1d")
            
            if not spx_data.empty:
                print("✅ Données SPX récupérées")
                
                # Convertir en format compatible
                historical_data = []
                for date, row in spx_data.iterrows():
                    historical_data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'open': float(row['Open']),
                        'high': float(row['High']),
                        'low': float(row['Low']),
                        'close': float(row['Close']),
                        'volume': int(row['Volume'])
                    })
                
                self.backtesting_data['spx_historical_data'] = {
                    'symbol': 'SPX',
                    'period': '30d',
                    'data': historical_data,
                    'last_close': float(spx_data['Close'].iloc[-1]),
                    'records_count': len(historical_data)
                }
                
                print(f"   - Période: 30 jours")
                print(f"   - Dernier close: {self.backtesting_data['spx_historical_data']['last_close']}")
                print(f"   - Records: {len(historical_data)}")
                
                return True
            else:
                print("❌ Données SPX non disponibles")
                return False
                
        except Exception as e:
            print(f"❌ Erreur SPX: {e}")
            self.backtesting_data['errors'].append(f"SPX Data: {str(e)}")
            return False
    
    def generate_simulated_options_levels(self):
        """Générer niveaux options simulés basés sur les données historiques"""
        print("🎯 Génération niveaux options simulés...")
        
        try:
            # Utiliser le dernier prix SPX comme référence
            spx_price = self.backtesting_data['spx_historical_data'].get('last_close', 5000)
            
            # Générer niveaux options réalistes
            options_levels = {
                'spx_current_price': spx_price,
                'gamma_exposure': {
                    'gex1': spx_price - 50,  # Niveau GEX1
                    'gex2': spx_price + 50   # Niveau GEX2
                },
                'put_call_ratio': 1.2,  # Ratio Put/Call réaliste
                'implied_volatility': 18.5,  # Volatilité implicite
                'strike_levels': [
                    {'strike': spx_price - 100, 'type': 'put', 'volume': 1500},
                    {'strike': spx_price - 50, 'type': 'put', 'volume': 2000},
                    {'strike': spx_price, 'type': 'atm', 'volume': 2500},
                    {'strike': spx_price + 50, 'type': 'call', 'volume': 2000},
                    {'strike': spx_price + 100, 'type': 'call', 'volume': 1500}
                ]
            }
            
            self.backtesting_data['options_levels'] = options_levels
            
            print("✅ Niveaux options générés")
            print(f"   - Prix SPX: {spx_price}")
            print(f"   - GEX1: {options_levels['gamma_exposure']['gex1']}")
            print(f"   - GEX2: {options_levels['gamma_exposure']['gex2']}")
            print(f"   - Put/Call Ratio: {options_levels['put_call_ratio']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur options: {e}")
            self.backtesting_data['errors'].append(f"Options: {str(e)}")
            return False
    
    def analyze_market_data(self):
        """Analyser les données de marché"""
        print("📊 Analyse données marché...")
        
        try:
            # Analyser données ES
            es_data = self.backtesting_data['es_historical_data'].get('data', [])
            if es_data:
                # Calculer moyennes mobiles
                closes = [bar['close'] for bar in es_data]
                sma_20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else sum(closes) / len(closes)
                sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else sum(closes) / len(closes)
                
                # Calculer volatilité
                returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
                volatility = (sum([r**2 for r in returns]) / len(returns))**0.5 * (252**0.5) * 100
                
                # Déterminer tendance
                current_price = closes[-1]
                if current_price > sma_20 > sma_50:
                    trend = "BULLISH"
                elif current_price < sma_20 < sma_50:
                    trend = "BEARISH"
                else:
                    trend = "NEUTRAL"
                
                market_analysis = {
                    'trend': trend,
                    'sma_20': sma_20,
                    'sma_50': sma_50,
                    'volatility': volatility,
                    'current_price': current_price,
                    'support_levels': [current_price * 0.98, current_price * 0.96],
                    'resistance_levels': [current_price * 1.02, current_price * 1.04]
                }
                
                self.backtesting_data['market_analysis'] = market_analysis
                
                print("✅ Analyse marché générée")
                print(f"   - Tendance: {trend}")
                print(f"   - SMA 20: {sma_20:.2f}")
                print(f"   - SMA 50: {sma_50:.2f}")
                print(f"   - Volatilité: {volatility:.1f}%")
                
                return True
            else:
                print("❌ Pas de données pour analyse")
                return False
                
        except Exception as e:
            print(f"❌ Erreur analyse: {e}")
            self.backtesting_data['errors'].append(f"Analysis: {str(e)}")
            return False
    
    def generate_backtesting_scenarios(self):
        """Générer scénarios de backtesting"""
        print("🎯 Génération scénarios backtesting...")
        
        try:
            scenarios = {
                'scenario_1': {
                    'name': 'Breakout Haussier',
                    'description': 'Test breakout au-dessus de la résistance',
                    'entry_price': self.backtesting_data['market_analysis'].get('resistance_levels', [5000])[0],
                    'stop_loss': self.backtesting_data['market_analysis'].get('sma_20', 5000),
                    'take_profit': self.backtesting_data['market_analysis'].get('resistance_levels', [5000])[0] * 1.02
                },
                'scenario_2': {
                    'name': 'Breakdown Baissier',
                    'description': 'Test breakdown en-dessous du support',
                    'entry_price': self.backtesting_data['market_analysis'].get('support_levels', [5000])[0],
                    'stop_loss': self.backtesting_data['market_analysis'].get('sma_20', 5000),
                    'take_profit': self.backtesting_data['market_analysis'].get('support_levels', [5000])[0] * 0.98
                },
                'scenario_3': {
                    'name': 'Range Trading',
                    'description': 'Test trading dans un range',
                    'entry_price': self.backtesting_data['market_analysis'].get('current_price', 5000),
                    'stop_loss': self.backtesting_data['market_analysis'].get('support_levels', [5000])[0],
                    'take_profit': self.backtesting_data['market_analysis'].get('resistance_levels', [5000])[0]
                }
            }
            
            self.backtesting_data['backtesting_scenarios'] = scenarios
            
            print("✅ Scénarios backtesting générés")
            print(f"   - Scénario 1: {scenarios['scenario_1']['name']}")
            print(f"   - Scénario 2: {scenarios['scenario_2']['name']}")
            print(f"   - Scénario 3: {scenarios['scenario_3']['name']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur scénarios: {e}")
            self.backtesting_data['errors'].append(f"Scenarios: {str(e)}")
            return False
    
    def save_backtesting_data(self):
        """Sauvegarder données backtesting"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/backtesting/weekend_backtesting_data_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.backtesting_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Données backtesting sauvegardées: {filename}")
        return filename
    
    def run_weekend_backtesting_recuperation(self):
        """Exécuter récupération backtesting weekend complète"""
        print("🏆 RÉCUPÉRATION DONNÉES BACKTESTING WEEKEND")
        print("=" * 50)
        
        # 1. Déterminer heure fermeture vendredi
        self.get_friday_close_time()
        
        # 2. Récupération données
        success_count = 0
        tests = [
            ('ES Historical Data', self.get_es_historical_data),
            ('SPX Historical Data', self.get_spx_historical_data),
            ('Options Levels', self.generate_simulated_options_levels),
            ('Market Analysis', self.analyze_market_data),
            ('Backtesting Scenarios', self.generate_backtesting_scenarios)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 {test_name}...")
            if test_func():
                success_count += 1
            time.sleep(1)
        
        # 3. Sauvegarder résultats
        filename = self.save_backtesting_data()
        
        # 4. Résultats finaux
        print("\n" + "=" * 50)
        print("📊 RÉSULTATS RÉCUPÉRATION BACKTESTING")
        print("=" * 50)
        
        success_rate = (success_count / len(tests)) * 100
        print(f"✅ Tests réussis: {success_count}/{len(tests)}")
        print(f"📊 Taux de succès: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 RÉCUPÉRATION BACKTESTING RÉUSSIE !")
            self.backtesting_data['success'] = True
            
            # Afficher résumé
            print("\n📋 RÉSUMÉ DONNÉES BACKTESTING:")
            print(f"   - ES Prix: {self.backtesting_data['es_historical_data'].get('last_close', 'N/A')}")
            print(f"   - SPX Prix: {self.backtesting_data['spx_historical_data'].get('last_close', 'N/A')}")
            print(f"   - Tendance: {self.backtesting_data['market_analysis'].get('trend', 'N/A')}")
            print(f"   - Scénarios: {len(self.backtesting_data.get('backtesting_scenarios', {}))}")
            
        else:
            print("⚠️ Récupération incomplète")
        
        return self.backtesting_data['success']

def main():
    """Fonction principale"""
    print("🏆 RÉCUPÉRATION DONNÉES BACKTESTING WEEKEND - MIA_IA SYSTEM")
    print("=" * 60)
    
    recuperator = RecuperationBacktestingWeekend()
    success = recuperator.run_weekend_backtesting_recuperation()
    
    if success:
        print("\n🎉 DONNÉES BACKTESTING RÉCUPÉRÉES !")
        print("📋 Prêt pour l'analyse weekend et la préparation backtesting")
    else:
        print("\n⚠️ Récupération incomplète")
    
    return success

if __name__ == "__main__":
    main()










