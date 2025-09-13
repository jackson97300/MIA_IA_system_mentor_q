#!/usr/bin/env python3
"""
🎭 TEST COMPLET SYSTÈME MIA_IA - MODE SIMULATION
=================================================

Script pour tester le système entier en simulation complète
- Données simulées ES/NQ
- Options SPX simulées
- Trading simulé
- Analyse complète
"""

import asyncio
import sys
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger

logger = get_logger(__name__)

class SystemeTestComplet:
    """Testeur complet du système MIA_IA en simulation"""
    
    def __init__(self):
        self.test_duration = 300  # 5 minutes de test
        self.signals_generated = 0
        self.trades_executed = 0
        self.test_results = {
            'signals_detected': 0,
            'signals_validated': 0,
            'trades_executed': 0,
            'pnl_simulated': 0.0,
            'win_rate': 0.0,
            'errors': []
        }
    
    async def generate_simulated_market_data(self):
        """Génère des données de marché simulées"""
        base_price_es = 5400.0
        base_price_nq = 18500.0
        
        # Simulation de mouvement de prix
        price_change_es = random.uniform(-10, 10)
        price_change_nq = random.uniform(-50, 50)
        
        es_data = {
            'symbol': 'ES',
            'last': base_price_es + price_change_es,
            'bid': base_price_es + price_change_es - 0.25,
            'ask': base_price_es + price_change_es + 0.25,
            'volume': random.randint(100, 1000),
            'bid_volume': random.randint(50, 500),
            'ask_volume': random.randint(50, 500),
            'delta': random.uniform(-0.8, 0.8),
            'mode': 'simulation',
            'timestamp': datetime.now()
        }
        
        nq_data = {
            'symbol': 'NQ',
            'last': base_price_nq + price_change_nq,
            'bid': base_price_nq + price_change_nq - 0.5,
            'ask': base_price_nq + price_change_nq + 0.5,
            'volume': random.randint(50, 500),
            'bid_volume': random.randint(25, 250),
            'ask_volume': random.randint(25, 250),
            'delta': random.uniform(-0.8, 0.8),
            'mode': 'simulation',
            'timestamp': datetime.now()
        }
        
        return es_data, nq_data
    
    async def generate_simulated_spx_options(self):
        """Génère des données options SPX simulées"""
        return {
            'put_call_ratio': random.uniform(0.8, 1.5),
            'gamma_exposure': random.uniform(50e9, 100e9),
            'dealer_position': random.choice(['long', 'short', 'neutral']),
            'vix_level': random.uniform(15, 30),
            'gamma_flip_level': random.uniform(5350, 5450),
            'unusual_options_activity': random.choice([True, False]),
            'nearby_pin_levels': [5350, 5400, 5450],
            'data_source': 'simulation',
            'timestamp': datetime.now()
        }
    
    async def simulate_signal_detection(self, es_data, nq_data, spx_data):
        """Simule la détection de signaux"""
        # Simulation de features
        gamma_proximity = random.uniform(0, 1)
        volume_confirmation = random.uniform(0, 1)
        vwap_trend = random.uniform(-1, 1)
        sierra_pattern = random.uniform(0, 1)
        options_flow = random.uniform(-1, 1)
        order_book_imbalance = random.uniform(-1, 1)
        
        # Calcul score de confluence simulé
        confluence_score = (
            gamma_proximity * 0.32 +
            volume_confirmation * 0.23 +
            abs(vwap_trend) * 0.18 +
            sierra_pattern * 0.18 +
            abs(options_flow) * 0.15 +
            abs(order_book_imbalance) * 0.15
        )
        
        # Seuils ultra-réduits pour calibration
        min_confidence = 0.05
        min_confluence = 0.05
        
        signal_detected = confluence_score > min_confluence
        signal_validated = confluence_score > min_confidence
        
        return {
            'detected': signal_detected,
            'validated': signal_validated,
            'confluence_score': confluence_score,
            'features': {
                'gamma_proximity': gamma_proximity,
                'volume_confirmation': volume_confirmation,
                'vwap_trend': vwap_trend,
                'sierra_pattern': sierra_pattern,
                'options_flow': options_flow,
                'order_book_imbalance': order_book_imbalance
            },
            'instrument': 'ES' if random.choice([True, False]) else 'NQ',
            'direction': 'long' if random.choice([True, False]) else 'short',
            'confidence': confluence_score
        }
    
    async def simulate_trade_execution(self, signal):
        """Simule l'exécution d'un trade"""
        if not signal['validated']:
            return None
        
        # Simulation P&L
        entry_price = 5400.0 if signal['instrument'] == 'ES' else 18500.0
        exit_price = entry_price + random.uniform(-20, 20) if signal['instrument'] == 'ES' else entry_price + random.uniform(-100, 100)
        
        if signal['direction'] == 'long':
            pnl = exit_price - entry_price
        else:
            pnl = entry_price - exit_price
        
        # Commission simulée
        commission = 2.5
        pnl -= commission
        
        return {
            'instrument': signal['instrument'],
            'direction': signal['direction'],
            'entry_price': entry_price,
            'exit_price': exit_price,
            'pnl': pnl,
            'commission': commission,
            'timestamp': datetime.now()
        }
    
    async def run_complete_system_test(self):
        """Lance le test complet du système"""
        print("🎭 TEST COMPLET SYSTÈME MIA_IA - MODE SIMULATION")
        print("=" * 60)
        print(f"⏰ Début test: {datetime.now().strftime('%H:%M:%S')}")
        print(f"⏱️ Durée: {self.test_duration} secondes")
        print("=" * 60)
        
        start_time = datetime.now()
        iteration = 0
        
        while (datetime.now() - start_time).seconds < self.test_duration:
            iteration += 1
            print(f"\n📊 Itération {iteration}")
            
            try:
                # 1. Génération données simulées
                es_data, nq_data = await self.generate_simulated_market_data()
                spx_data = await self.generate_simulated_spx_options()
                
                print(f"📈 ES: {es_data['last']:.2f} (Vol: {es_data['volume']})")
                print(f"📱 NQ: {nq_data['last']:.2f} (Vol: {nq_data['volume']})")
                print(f"📊 SPX: Put/Call {spx_data['put_call_ratio']:.3f}, VIX {spx_data['vix_level']:.1f}")
                
                # 2. Détection de signaux
                signal = await self.simulate_signal_detection(es_data, nq_data, spx_data)
                
                if signal['detected']:
                    self.test_results['signals_detected'] += 1
                    print(f"🎯 Signal détecté: {signal['instrument']} {signal['direction']} (Conf: {signal['confidence']:.3f})")
                    
                    if signal['validated']:
                        self.test_results['signals_validated'] += 1
                        print(f"✅ Signal validé!")
                        
                        # 3. Exécution trade
                        trade = await self.simulate_trade_execution(signal)
                        if trade:
                            self.test_results['trades_executed'] += 1
                            self.test_results['pnl_simulated'] += trade['pnl']
                            print(f"💰 Trade exécuté: {trade['pnl']:.2f}$")
                
                # 4. Statistiques en temps réel
                if iteration % 10 == 0:
                    self._display_test_statistics()
                
                # Attendre 2 secondes entre itérations
                await asyncio.sleep(2)
                
            except Exception as e:
                error_msg = f"Erreur itération {iteration}: {e}"
                self.test_results['errors'].append(error_msg)
                print(f"❌ {error_msg}")
        
        # 5. Résultats finaux
        self._display_final_results()
    
    def _display_test_statistics(self):
        """Affiche les statistiques en cours de test"""
        print(f"\n📊 STATISTIQUES INTERMÉDIAIRES:")
        print(f"   🎯 Signals détectés: {self.test_results['signals_detected']}")
        print(f"   ✅ Signals validés: {self.test_results['signals_validated']}")
        print(f"   💰 Trades exécutés: {self.test_results['trades_executed']}")
        print(f"   📈 P&L simulé: {self.test_results['pnl_simulated']:.2f}$")
        
        if self.test_results['signals_detected'] > 0:
            validation_rate = (self.test_results['signals_validated'] / self.test_results['signals_detected']) * 100
            print(f"   📊 Taux validation: {validation_rate:.1f}%")
    
    def _display_final_results(self):
        """Affiche les résultats finaux du test"""
        print("\n" + "=" * 60)
        print("🎯 RÉSULTATS FINAUX - TEST SYSTÈME COMPLET")
        print("=" * 60)
        
        print(f"⏰ Durée test: {self.test_duration} secondes")
        print(f"🎯 Signals détectés: {self.test_results['signals_detected']}")
        print(f"✅ Signals validés: {self.test_results['signals_validated']}")
        print(f"💰 Trades exécutés: {self.test_results['trades_executed']}")
        print(f"📈 P&L simulé: {self.test_results['pnl_simulated']:.2f}$")
        
        if self.test_results['signals_detected'] > 0:
            validation_rate = (self.test_results['signals_validated'] / self.test_results['signals_detected']) * 100
            print(f"📊 Taux validation: {validation_rate:.1f}%")
        
        if self.test_results['trades_executed'] > 0:
            avg_pnl = self.test_results['pnl_simulated'] / self.test_results['trades_executed']
            print(f"📊 P&L moyen par trade: {avg_pnl:.2f}$")
        
        if self.test_results['errors']:
            print(f"❌ Erreurs: {len(self.test_results['errors'])}")
            for error in self.test_results['errors'][:3]:  # Afficher les 3 premières
                print(f"   - {error}")
        
        print("\n🎭 TEST TERMINÉ - SYSTÈME SIMULATION COMPLÈTE")
        print("=" * 60)

async def main():
    """Fonction principale"""
    tester = SystemeTestComplet()
    
    try:
        await tester.run_complete_system_test()
    except KeyboardInterrupt:
        print("\n🛑 Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")

if __name__ == "__main__":
    asyncio.run(main())





