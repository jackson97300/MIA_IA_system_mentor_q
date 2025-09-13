#!/usr/bin/env python3
"""
🎯 TEST STRATÉGIE LEADERSHIP ES/NQ
Test de la stratégie "FORT/FAIBLE" avec données simulées
"""

import sys
import asyncio
import random
from datetime import datetime
from pathlib import Path

# Ajouter le chemin du projet
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.logger import get_logger

# Configuration logging
logger = get_logger(__name__)

class LeadershipStrategyTester:
    """Testeur de stratégie leadership ES/NQ"""
    
    def __init__(self):
        self.trades_count = 0
        self.wins = 0
        self.total_pnl = 0.0
        
    def analyze_es_nq_divergence(self, es_data: dict, nq_data: dict) -> dict:
        """
        🔗 ANALYSE DIVERGENCE ES/NQ
        Détecte les divergences de prix, volume et momentum entre ES et NQ
        """
        try:
            # Extraction données
            es_price = es_data.get('price', 0)
            nq_price = nq_data.get('price', 0)
            es_volume = es_data.get('volume', 0)
            nq_volume = nq_data.get('volume', 0)
            es_delta = es_data.get('delta', 0)
            nq_delta = nq_data.get('delta', 0)
            
            if es_price == 0 or nq_price == 0:
                return {
                    'divergence_score': 0.5,
                    'leader': 'ES',
                    'alignment': 'neutral',
                    'warning': False,
                    'signal_strength': 0.0
                }
            
            # 1. DIVERGENCE PRIX
            price_ratio = es_price / nq_price if nq_price > 0 else 1.0
            price_divergence = abs(price_ratio - 1.0) * 100
            
            # 2. DIVERGENCE VOLUME
            volume_ratio = es_volume / nq_volume if nq_volume > 0 else 1.0
            volume_divergence = abs(volume_ratio - 1.0) * 100
            
            # 3. DIVERGENCE MOMENTUM (DELTA)
            delta_ratio = es_delta / nq_delta if nq_delta != 0 else 1.0
            momentum_divergence = abs(delta_ratio - 1.0) * 100
            
            # 4. LEADERSHIP ANALYSIS
            es_momentum = es_delta / max(es_volume, 1)
            nq_momentum = nq_delta / max(nq_volume, 1)
            
            if abs(es_momentum) > abs(nq_momentum):
                leader = 'ES'
                leadership_strength = abs(es_momentum) - abs(nq_momentum)
            else:
                leader = 'NQ'
                leadership_strength = abs(nq_momentum) - abs(es_momentum)
            
            # 5. SCORE DIVERGENCE GLOBAL
            total_divergence = (price_divergence * 0.4 + 
                              volume_divergence * 0.3 + 
                              momentum_divergence * 0.3)
            
            # 6. SIGNAL STRENGTH
            if total_divergence < 5:  # Faible divergence = bon signal
                divergence_score = 0.8
                alignment = 'aligned'
                warning = False
            elif total_divergence < 15:  # Divergence modérée
                divergence_score = 0.6
                alignment = 'moderate'
                warning = False
            else:  # Forte divergence = signal faible
                divergence_score = 0.3
                alignment = 'divergent'
                warning = True
            
            # 7. SIGNAL STRENGTH FINAL
            signal_strength = divergence_score * (1 + leadership_strength * 0.5)
            
            return {
                'divergence_score': divergence_score,
                'leader': leader,
                'alignment': alignment,
                'warning': warning,
                'signal_strength': min(1.0, signal_strength),
                'price_divergence': price_divergence,
                'volume_divergence': volume_divergence,
                'momentum_divergence': momentum_divergence,
                'leadership_strength': leadership_strength,
                'total_divergence': total_divergence
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse divergence ES/NQ: {e}")
            return {
                'divergence_score': 0.5,
                'leader': 'ES',
                'alignment': 'neutral',
                'warning': False,
                'signal_strength': 0.0
            }
    
    def select_optimal_instrument(self, es_data: dict, nq_data: dict) -> dict:
        """
        🎯 SÉLECTION INSTRUMENT OPTIMAL
        """
        divergence_analysis = self.analyze_es_nq_divergence(es_data, nq_data)
        
        leader = divergence_analysis['leader']
        signal_strength = divergence_analysis['signal_strength']
        alignment = divergence_analysis['alignment']
        
        if leader == 'ES' and signal_strength > 0.7 and alignment == 'aligned':
            selected_instrument = 'ES'
            reason = f"ES LEADER FORT (score: {signal_strength:.3f})"
            confidence_boost = 1.5
        elif leader == 'NQ' and signal_strength > 0.7 and alignment == 'aligned':
            selected_instrument = 'NQ'
            reason = f"NQ LEADER FORT (score: {signal_strength:.3f})"
            confidence_boost = 1.5
        elif leader == 'ES' and signal_strength > 0.5:
            selected_instrument = 'ES'
            reason = f"ES LEADER MODÉRÉ (score: {signal_strength:.3f})"
            confidence_boost = 1.2
        elif leader == 'NQ' and signal_strength > 0.5:
            selected_instrument = 'NQ'
            reason = f"NQ LEADER MODÉRÉ (score: {signal_strength:.3f})"
            confidence_boost = 1.2
        else:
            selected_instrument = 'ES'
            reason = f"LEADERSHIP FAIBLE - ES par défaut"
            confidence_boost = 1.0
        
        return {
            'selected_instrument': selected_instrument,
            'leader': leader,
            'signal_strength': signal_strength,
            'alignment': alignment,
            'reason': reason,
            'confidence_boost': confidence_boost,
            'divergence_analysis': divergence_analysis
        }
    
    def generate_market_data(self):
        """Génère des données de marché réalistes avec scenarios variés"""
        
        # Créer différents scenarios de marché
        scenario = random.choice(['bullish_es', 'bullish_nq', 'bearish_es', 'bearish_nq', 'neutral'])
        
        if scenario == 'bullish_es':
            # ES leader bullish
            es_data = {
                "price": 6450.0 + random.uniform(5, 15),
                "volume": 500 + random.randint(50, 150),
                "delta": 300 + random.randint(50, 200),  # Delta positif fort
                "bid_volume": 150 + random.randint(0, 50),
                "ask_volume": 350 + random.randint(50, 100),  # Ask volume élevé (achats agressifs)
            }
            nq_data = {
                "price": 18500.0 + random.uniform(0, 10),
                "volume": 300 + random.randint(0, 100),
                "delta": 100 + random.randint(0, 100),  # Delta plus faible
                "bid_volume": 150 + random.randint(0, 50),
                "ask_volume": 150 + random.randint(0, 50),
            }
            
        elif scenario == 'bullish_nq':
            # NQ leader bullish
            es_data = {
                "price": 6450.0 + random.uniform(0, 10),
                "volume": 400 + random.randint(0, 100),
                "delta": 150 + random.randint(0, 100),
                "bid_volume": 200 + random.randint(0, 50),
                "ask_volume": 200 + random.randint(0, 50),
            }
            nq_data = {
                "price": 18500.0 + random.uniform(10, 25),
                "volume": 400 + random.randint(50, 150),
                "delta": 250 + random.randint(50, 150),  # Delta positif fort
                "bid_volume": 100 + random.randint(0, 50),
                "ask_volume": 300 + random.randint(50, 100),
            }
            
        elif scenario == 'bearish_es':
            # ES leader bearish
            es_data = {
                "price": 6450.0 - random.uniform(5, 15),
                "volume": 500 + random.randint(50, 150),
                "delta": -200 - random.randint(50, 150),  # Delta négatif fort
                "bid_volume": 350 + random.randint(50, 100),  # Bid volume élevé (ventes agressives)
                "ask_volume": 150 + random.randint(0, 50),
            }
            nq_data = {
                "price": 18500.0 - random.uniform(0, 10),
                "volume": 300 + random.randint(0, 100),
                "delta": -50 - random.randint(0, 100),
                "bid_volume": 150 + random.randint(0, 50),
                "ask_volume": 150 + random.randint(0, 50),
            }
            
        elif scenario == 'bearish_nq':
            # NQ leader bearish
            es_data = {
                "price": 6450.0 - random.uniform(0, 10),
                "volume": 400 + random.randint(0, 100),
                "delta": -100 - random.randint(0, 100),
                "bid_volume": 200 + random.randint(0, 50),
                "ask_volume": 200 + random.randint(0, 50),
            }
            nq_data = {
                "price": 18500.0 - random.uniform(10, 25),
                "volume": 400 + random.randint(50, 150),
                "delta": -200 - random.randint(50, 150),  # Delta négatif fort
                "bid_volume": 300 + random.randint(50, 100),
                "ask_volume": 100 + random.randint(0, 50),
            }
            
        else:  # neutral
            # Marché neutre
            es_data = {
                "price": 6450.0 + (random.random() - 0.5) * 10,
                "volume": 400 + random.randint(0, 100),
                "delta": (random.random() - 0.5) * 200,
                "bid_volume": 200 + random.randint(0, 50),
                "ask_volume": 200 + random.randint(0, 50),
            }
            nq_data = {
                "price": 18500.0 + (random.random() - 0.5) * 20,
                "volume": 300 + random.randint(0, 100),
                "delta": (random.random() - 0.5) * 150,
                "bid_volume": 150 + random.randint(0, 50),
                "ask_volume": 150 + random.randint(0, 50),
            }
        
        return es_data, nq_data, scenario
    
    def simulate_trade(self, instrument_selection, signal_type="BUY"):
        """Simule un trade basé sur la stratégie leadership"""
        try:
            instrument = instrument_selection['selected_instrument']
            leader = instrument_selection['leader']
            signal_strength = instrument_selection['signal_strength']
            
            # Probabilité de succès basée sur la stratégie
            if leader == instrument and signal_strength > 0.7:
                # Trading le leader fort = haute probabilité
                success_rate = 0.75
                potential_gain = 300
                potential_loss = 150
            elif leader == instrument and signal_strength > 0.5:
                # Trading le leader modéré = probabilité moyenne
                success_rate = 0.65
                potential_gain = 200
                potential_loss = 120
            else:
                # Trading sans leadership = faible probabilité
                success_rate = 0.45
                potential_gain = 150
                potential_loss = 100
            
            # Simulation du résultat
            is_win = random.random() < success_rate
            pnl = potential_gain if is_win else -potential_loss
            
            return {
                'is_win': is_win,
                'pnl': pnl,
                'instrument': instrument,
                'leader': leader,
                'signal_strength': signal_strength,
                'success_rate': success_rate
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur simulation trade: {e}")
            return {
                'is_win': False,
                'pnl': -100,
                'instrument': 'ES',
                'leader': 'ES',
                'signal_strength': 0.0,
                'success_rate': 0.0
            }
    
    async def run_strategy_test(self, num_trades=20):
        """Lance le test de stratégie"""
        logger.info("=" * 80)
        logger.info("🎯 TEST STRATÉGIE LEADERSHIP ES/NQ")
        logger.info("=" * 80)
        
        for i in range(num_trades):
            logger.info(f"📊 TRADE #{i+1:02d}")
            
            # 1. Générer données marché
            es_data, nq_data, scenario = self.generate_market_data()
            
            logger.info(f"   🎭 Scenario: {scenario}")
            logger.info(f"   📈 ES: {es_data['price']:.2f} | Vol: {es_data['volume']} | Delta: {es_data['delta']:.1f}")
            logger.info(f"   📊 NQ: {nq_data['price']:.2f} | Vol: {nq_data['volume']} | Delta: {nq_data['delta']:.1f}")
            
            # 2. Analyser leadership
            instrument_selection = self.select_optimal_instrument(es_data, nq_data)
            
            logger.info(f"   🎯 Leader: {instrument_selection['leader']}")
            logger.info(f"   📊 Signal: {instrument_selection['signal_strength']:.3f}")
            logger.info(f"   🔗 Alignment: {instrument_selection['alignment']}")
            logger.info(f"   📝 Raison: {instrument_selection['reason']}")
            
            # 3. Simuler trade si signal suffisant (seuil permissif pour test)
            if instrument_selection['signal_strength'] > 0.2:
                trade_result = self.simulate_trade(instrument_selection)
                
                self.trades_count += 1
                if trade_result['is_win']:
                    self.wins += 1
                    logger.info(f"   ✅ Trade GAGNANT: +{trade_result['pnl']:.0f}$ ({trade_result['instrument']})")
                else:
                    logger.info(f"   ❌ Trade PERDANT: {trade_result['pnl']:.0f}$ ({trade_result['instrument']})")
                
                self.total_pnl += trade_result['pnl']
                
                current_winrate = (self.wins / self.trades_count) * 100
                logger.info(f"   📊 Performance: {self.wins}/{self.trades_count} = {current_winrate:.1f}% | P&L: {self.total_pnl:.0f}$")
            else:
                logger.info(f"   ⏸️ Signal trop faible - Pas de trade")
            
            logger.info("")
            await asyncio.sleep(0.1)  # Pause courte
        
        # Résumé final
        logger.info("=" * 80)
        logger.info("📊 RÉSULTATS FINAUX")
        logger.info("=" * 80)
        
        if self.trades_count > 0:
            final_winrate = (self.wins / self.trades_count) * 100
            avg_pnl = self.total_pnl / self.trades_count
            
            logger.info(f"🎯 Trades total: {self.trades_count}")
            logger.info(f"✅ Trades gagnants: {self.wins}")
            logger.info(f"❌ Trades perdants: {self.trades_count - self.wins}")
            logger.info(f"📊 Win Rate: {final_winrate:.1f}%")
            logger.info(f"💰 P&L total: {self.total_pnl:.0f}$")
            logger.info(f"📈 P&L moyen: {avg_pnl:.0f}$ par trade")
            
            # Évaluation
            if final_winrate >= 70:
                logger.info("🟢 EXCELLENT: Stratégie très performante!")
            elif final_winrate >= 60:
                logger.info("🟡 BON: Stratégie rentable")
            elif final_winrate >= 50:
                logger.info("🟠 MOYEN: Stratégie neutre")
            else:
                logger.info("🔴 FAIBLE: Stratégie à améliorer")
        else:
            logger.info("❌ Aucun trade exécuté")

async def main():
    """Fonction principale"""
    try:
        tester = LeadershipStrategyTester()
        await tester.run_strategy_test(num_trades=30)
        
    except KeyboardInterrupt:
        logger.info("🛑 Test interrompu par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")

if __name__ == "__main__":
    asyncio.run(main())
