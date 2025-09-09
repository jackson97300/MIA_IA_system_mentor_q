#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génération Order Flow Estimé - MIA_IA System
Génère des données Order Flow réalistes basées sur vraies données
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
import random
import math
import glob

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class GenerationOrderFlowEstime:
    def __init__(self):
        self.orderflow_data = {
            'timestamp': datetime.now().isoformat(),
            'cumulative_delta': {},
            'bid_ask_imbalance': {},
            'aggressive_flow': {},
            'options_flow': {},
            'market_microstructure': {},
            'success': False,
            'errors': []
        }
    
    def load_real_market_data(self):
        """Charger données réelles de marché"""
        print("📂 Chargement données réelles...")
        
        try:
            # Chercher le fichier le plus récent
            pattern = "data/real_market/real_weekend_data_*.json"
            files = glob.glob(pattern)
            
            if not files:
                print("❌ Aucun fichier de données réelles trouvé")
                return False
            
            # Prendre le plus récent
            latest_file = max(files, key=os.path.getctime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                self.real_data = json.load(f)
            
            print(f"✅ Données chargées: {latest_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
            return False
    
    def generate_cumulative_delta(self):
        """Générer Cumulative Delta basé sur données réelles"""
        print("📊 Génération Cumulative Delta...")
        
        try:
            spx_data = self.real_data.get('market_data', {}).get('spx', {})
            if not spx_data:
                print("❌ Données SPX manquantes")
                return False
            
            current_price = spx_data['current_price']
            price_change_pct = spx_data['price_change_pct']
            volume = spx_data['volume']
            
            # Générer Cumulative Delta basé sur mouvement de prix
            # Si prix monte = plus d'acheteurs agressifs
            # Si prix baisse = plus de vendeurs agressifs
            
            # Calculer ratio acheteurs/vendeurs basé sur mouvement
            if price_change_pct > 0:
                buyer_ratio = 0.6 + (price_change_pct / 100) * 0.3
                seller_ratio = 0.4 - (price_change_pct / 100) * 0.3
            else:
                buyer_ratio = 0.4 + (price_change_pct / 100) * 0.3
                seller_ratio = 0.6 - (price_change_pct / 100) * 0.3
            
            # Générer données minute par minute (simulation)
            minutes_in_day = 390  # 6h30 de trading
            cumulative_delta_data = []
            
            current_delta = 0
            for minute in range(minutes_in_day):
                # Volume par minute (approximatif)
                minute_volume = volume / minutes_in_day
                
                # Générer flow aléatoire basé sur ratio
                if random.random() < buyer_ratio:
                    # Acheteur agressif
                    aggressive_volume = minute_volume * random.uniform(0.1, 0.3)
                    current_delta += aggressive_volume
                else:
                    # Vendeur agressif
                    aggressive_volume = minute_volume * random.uniform(0.1, 0.3)
                    current_delta -= aggressive_volume
                
                cumulative_delta_data.append({
                    'minute': minute,
                    'delta': current_delta,
                    'volume': minute_volume,
                    'price': current_price + (current_delta / volume) * 10  # Prix simulé
                })
            
            cumulative_delta = {
                'current_delta': current_delta,
                'buyer_ratio': buyer_ratio,
                'seller_ratio': seller_ratio,
                'data_points': len(cumulative_delta_data),
                'final_price': cumulative_delta_data[-1]['price'],
                'delta_change': current_delta
            }
            
            self.orderflow_data['cumulative_delta'] = cumulative_delta
            
            print("✅ Cumulative Delta généré")
            print(f"   - Delta final: {current_delta:,.0f}")
            print(f"   - Ratio acheteurs: {buyer_ratio:.2f}")
            print(f"   - Ratio vendeurs: {seller_ratio:.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur Cumulative Delta: {e}")
            self.orderflow_data['errors'].append(f"Cumulative Delta: {str(e)}")
            return False
    
    def generate_bid_ask_imbalance(self):
        """Générer Bid/Ask Imbalance"""
        print("⚖️ Génération Bid/Ask Imbalance...")
        
        try:
            spx_data = self.real_data.get('market_data', {}).get('spx', {})
            volatility_data = self.real_data.get('technical_analysis', {}).get('volatility', {})
            
            if not spx_data or not volatility_data:
                print("❌ Données manquantes")
                return False
            
            current_price = spx_data['current_price']
            volatility = volatility_data['historical_volatility']
            price_change_pct = spx_data['price_change_pct']
            
            # Calculer spread basé sur volatilité
            base_spread = current_price * (volatility / 100) * 0.001
            bid_price = current_price - base_spread / 2
            ask_price = current_price + base_spread / 2
            
            # Calculer imbalance basé sur mouvement
            if price_change_pct > 0:
                # Plus d'acheteurs = plus de volume à l'ask
                bid_volume = 1000
                ask_volume = 1500 + (price_change_pct * 100)
            else:
                # Plus de vendeurs = plus de volume au bid
                bid_volume = 1500 + (abs(price_change_pct) * 100)
                ask_volume = 1000
            
            imbalance = (ask_volume - bid_volume) / (ask_volume + bid_volume)
            
            bid_ask_data = {
                'bid_price': bid_price,
                'ask_price': ask_price,
                'spread': base_spread,
                'bid_volume': bid_volume,
                'ask_volume': ask_volume,
                'imbalance': imbalance,
                'imbalance_percent': imbalance * 100,
                'mid_price': current_price
            }
            
            self.orderflow_data['bid_ask_imbalance'] = bid_ask_data
            
            print("✅ Bid/Ask Imbalance généré")
            print(f"   - Spread: {base_spread:.2f}")
            print(f"   - Imbalance: {imbalance:.3f} ({imbalance*100:.1f}%)")
            print(f"   - Bid Volume: {bid_volume:,.0f}")
            print(f"   - Ask Volume: {ask_volume:,.0f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur Bid/Ask: {e}")
            self.orderflow_data['errors'].append(f"Bid/Ask: {str(e)}")
            return False
    
    def generate_aggressive_flow(self):
        """Générer Aggressive Flow"""
        print("🔥 Génération Aggressive Flow...")
        
        try:
            spx_data = self.real_data.get('market_data', {}).get('spx', {})
            cumulative_delta = self.orderflow_data.get('cumulative_delta', {})
            
            if not spx_data or not cumulative_delta:
                print("❌ Données manquantes")
                return False
            
            current_price = spx_data['current_price']
            volume = spx_data['volume']
            price_change_pct = spx_data['price_change_pct']
            
            # Calculer flow agressif basé sur mouvement et volume
            if price_change_pct > 0:
                # Flow haussier
                aggressive_buys = volume * 0.4
                aggressive_sells = volume * 0.2
                flow_direction = "BULLISH"
            else:
                # Flow baissier
                aggressive_buys = volume * 0.2
                aggressive_sells = volume * 0.4
                flow_direction = "BEARISH"
            
            # Calculer intensité du flow
            flow_intensity = abs(price_change_pct) * 10
            
            aggressive_flow = {
                'aggressive_buys': aggressive_buys,
                'aggressive_sells': aggressive_sells,
                'net_flow': aggressive_buys - aggressive_sells,
                'flow_direction': flow_direction,
                'flow_intensity': flow_intensity,
                'buy_pressure': aggressive_buys / volume,
                'sell_pressure': aggressive_sells / volume,
                'pressure_ratio': aggressive_buys / aggressive_sells if aggressive_sells > 0 else 2.0
            }
            
            self.orderflow_data['aggressive_flow'] = aggressive_flow
            
            print("✅ Aggressive Flow généré")
            print(f"   - Direction: {flow_direction}")
            print(f"   - Intensité: {flow_intensity:.1f}")
            print(f"   - Net Flow: {aggressive_flow['net_flow']:,.0f}")
            print(f"   - Pressure Ratio: {aggressive_flow['pressure_ratio']:.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur Aggressive Flow: {e}")
            self.orderflow_data['errors'].append(f"Aggressive Flow: {str(e)}")
            return False
    
    def generate_options_flow(self):
        """Générer Options Flow basé sur données réelles"""
        print("🎯 Génération Options Flow...")
        
        try:
            options_levels = self.real_data.get('options_levels', {})
            gamma_exposure = self.real_data.get('gamma_exposure', {})
            
            if not options_levels or not gamma_exposure:
                print("❌ Données options manquantes")
                return False
            
            current_price = options_levels['current_price']
            put_call_ratio = options_levels['put_call_ratio']
            volatility = options_levels['volatility']
            
            # Analyser strike levels pour déterminer flow
            strike_levels = options_levels['strike_levels']
            
            total_put_volume = 0
            total_call_volume = 0
            unusual_activity = []
            
            for strike in strike_levels:
                if strike['type'] == 'put':
                    total_put_volume += strike['volume']
                    # Détecter activité inhabituelle
                    if strike['volume'] > 2000:
                        unusual_activity.append({
                            'strike': strike['strike'],
                            'type': 'put',
                            'volume': strike['volume'],
                            'unusual': True
                        })
                elif strike['type'] == 'call':
                    total_call_volume += strike['volume']
                    # Détecter activité inhabituelle
                    if strike['volume'] > 2000:
                        unusual_activity.append({
                            'strike': strike['strike'],
                            'type': 'call',
                            'volume': strike['volume'],
                            'unusual': True
                        })
            
            # Calculer flow options
            options_flow = {
                'total_put_volume': total_put_volume,
                'total_call_volume': total_call_volume,
                'put_call_ratio': put_call_ratio,
                'unusual_activity_count': len(unusual_activity),
                'unusual_activity': unusual_activity,
                'gamma_exposure': {
                    'gex1': gamma_exposure['gex1'],
                    'gex2': gamma_exposure['gex2'],
                    'current_price': current_price
                },
                'flow_analysis': self._analyze_options_flow(put_call_ratio, unusual_activity)
            }
            
            self.orderflow_data['options_flow'] = options_flow
            
            print("✅ Options Flow généré")
            print(f"   - Put Volume: {total_put_volume:,.0f}")
            print(f"   - Call Volume: {total_call_volume:,.0f}")
            print(f"   - Put/Call Ratio: {put_call_ratio:.2f}")
            print(f"   - Unusual Activity: {len(unusual_activity)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur Options Flow: {e}")
            self.orderflow_data['errors'].append(f"Options Flow: {str(e)}")
            return False
    
    def _analyze_options_flow(self, put_call_ratio, unusual_activity):
        """Analyser le flow options"""
        analysis = {
            'sentiment': 'NEUTRAL',
            'pressure': 'BALANCED',
            'risk_level': 'MODERATE'
        }
        
        # Analyser sentiment basé sur Put/Call ratio
        if put_call_ratio > 1.2:
            analysis['sentiment'] = 'BEARISH'
        elif put_call_ratio < 0.8:
            analysis['sentiment'] = 'BULLISH'
        
        # Analyser pression basé sur activité inhabituelle
        put_unusual = len([a for a in unusual_activity if a['type'] == 'put'])
        call_unusual = len([a for a in unusual_activity if a['type'] == 'call'])
        
        if put_unusual > call_unusual:
            analysis['pressure'] = 'PUT_HEAVY'
        elif call_unusual > put_unusual:
            analysis['pressure'] = 'CALL_HEAVY'
        
        # Analyser niveau de risque
        total_unusual = len(unusual_activity)
        if total_unusual > 5:
            analysis['risk_level'] = 'HIGH'
        elif total_unusual > 2:
            analysis['risk_level'] = 'MODERATE'
        else:
            analysis['risk_level'] = 'LOW'
        
        return analysis
    
    def generate_market_microstructure(self):
        """Générer données microstructure de marché"""
        print("🔬 Génération Microstructure Marché...")
        
        try:
            spx_data = self.real_data.get('market_data', {}).get('spx', {})
            volatility_data = self.real_data.get('technical_analysis', {}).get('volatility', {})
            
            if not spx_data or not volatility_data:
                print("❌ Données manquantes")
                return False
            
            current_price = spx_data['current_price']
            volatility = volatility_data['historical_volatility']
            volume = spx_data['volume']
            
            # Calculer métriques microstructure
            # VWAP (Volume Weighted Average Price)
            vwap = current_price  # Approximation
            
            # POC (Point of Control) - niveau de prix avec plus de volume
            poc = current_price
            
            # Value Area (70% du volume)
            value_area_high = current_price * 1.005
            value_area_low = current_price * 0.995
            
            # Calculer efficacité du marché
            market_efficiency = 1 - (volatility / 100) * 0.5
            
            microstructure = {
                'vwap': vwap,
                'poc': poc,
                'value_area': {
                    'high': value_area_high,
                    'low': value_area_low,
                    'width': value_area_high - value_area_low
                },
                'market_efficiency': market_efficiency,
                'liquidity_score': volume / 1000000,  # Score de liquidité
                'volatility_regime': 'LOW' if volatility < 15 else 'MODERATE' if volatility < 25 else 'HIGH',
                'microstructure_analysis': {
                    'fair_value': current_price,
                    'deviation': 0,
                    'efficiency_rating': market_efficiency
                }
            }
            
            self.orderflow_data['market_microstructure'] = microstructure
            
            print("✅ Microstructure générée")
            print(f"   - VWAP: {vwap:.2f}")
            print(f"   - Value Area: {value_area_low:.2f} - {value_area_high:.2f}")
            print(f"   - Market Efficiency: {market_efficiency:.2f}")
            print(f"   - Liquidity Score: {microstructure['liquidity_score']:.1f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur Microstructure: {e}")
            self.orderflow_data['errors'].append(f"Microstructure: {str(e)}")
            return False
    
    def save_orderflow_data(self):
        """Sauvegarder données Order Flow"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/orderflow/estimated_orderflow_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.orderflow_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Données Order Flow sauvegardées: {filename}")
        return filename
    
    def run_orderflow_generation(self):
        """Exécuter génération Order Flow complète"""
        print("🏆 GÉNÉRATION ORDER FLOW ESTIMÉ")
        print("=" * 50)
        
        # 1. Charger données réelles
        if not self.load_real_market_data():
            return False
        
        # 2. Génération données
        success_count = 0
        generations = [
            ('Cumulative Delta', self.generate_cumulative_delta),
            ('Bid/Ask Imbalance', self.generate_bid_ask_imbalance),
            ('Aggressive Flow', self.generate_aggressive_flow),
            ('Options Flow', self.generate_options_flow),
            ('Market Microstructure', self.generate_market_microstructure)
        ]
        
        for gen_name, gen_func in generations:
            print(f"\n🔍 {gen_name}...")
            if gen_func():
                success_count += 1
            time.sleep(1)
        
        # 3. Sauvegarder résultats
        filename = self.save_orderflow_data()
        
        # 4. Résultats finaux
        print("\n" + "=" * 50)
        print("📊 RÉSULTATS GÉNÉRATION ORDER FLOW")
        print("=" * 50)
        
        success_rate = (success_count / len(generations)) * 100
        print(f"✅ Générations réussies: {success_count}/{len(generations)}")
        print(f"📊 Taux de succès: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 GÉNÉRATION ORDER FLOW RÉUSSIE !")
            self.orderflow_data['success'] = True
            
            # Afficher résumé
            cumulative_delta = self.orderflow_data.get('cumulative_delta', {})
            aggressive_flow = self.orderflow_data.get('aggressive_flow', {})
            options_flow = self.orderflow_data.get('options_flow', {})
            
            print("\n📋 RÉSUMÉ ORDER FLOW:")
            print(f"   - Cumulative Delta: {cumulative_delta.get('current_delta', 'N/A'):,.0f}")
            print(f"   - Flow Direction: {aggressive_flow.get('flow_direction', 'N/A')}")
            print(f"   - Put/Call Ratio: {options_flow.get('put_call_ratio', 'N/A'):.2f}")
            print(f"   - Unusual Activity: {options_flow.get('unusual_activity_count', 'N/A')}")
            
        else:
            print("⚠️ Génération incomplète")
        
        return self.orderflow_data['success']

def main():
    """Fonction principale"""
    print("🏆 GÉNÉRATION ORDER FLOW ESTIMÉ - MIA_IA SYSTEM")
    print("=" * 60)
    
    generator = GenerationOrderFlowEstime()
    success = generator.run_orderflow_generation()
    
    if success:
        print("\n🎉 ORDER FLOW GÉNÉRÉ !")
        print("📋 Basé sur vraies données de marché")
    else:
        print("\n⚠️ Génération incomplète")
    
    return success

if __name__ == "__main__":
    main()










