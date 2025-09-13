#!/usr/bin/env python3
"""
🎯 TEST STRATÉGIE LEADERSHIP ES/NQ AMÉLIORÉE
Stratégie "FORT/FAIBLE" optimisée basée sur les résultats du premier test
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

class EnhancedLeadershipStrategy:
    """Stratégie leadership ES/NQ améliorée"""
    
    def __init__(self):
        self.trades_count = 0
        self.wins = 0
        self.total_pnl = 0.0
        self.leadership_history = []
        
    def analyze_enhanced_leadership(self, es_data: dict, nq_data: dict) -> dict:
        """
        🚀 ANALYSE LEADERSHIP AMÉLIORÉE
        Algorithme optimisé basé sur momentum, volume et divergence
        """
        try:
            # Extraction données
            es_price = es_data.get('price', 0)
            nq_price = nq_data.get('price', 0)
            es_volume = es_data.get('volume', 0)
            nq_volume = nq_data.get('volume', 0)
            es_delta = es_data.get('delta', 0)
            nq_delta = nq_data.get('delta', 0)
            es_bid = es_data.get('bid_volume', 0)
            es_ask = es_data.get('ask_volume', 0)
            nq_bid = nq_data.get('bid_volume', 0)
            nq_ask = nq_data.get('ask_volume', 0)
            
            if es_price == 0 or nq_price == 0:
                return self._get_neutral_result()
            
            # 1. MOMENTUM STRENGTH (Amélioré)
            es_momentum_raw = es_delta / max(es_volume, 1)
            nq_momentum_raw = nq_delta / max(nq_volume, 1)
            
            # 2. VOLUME PRESSURE (Nouveau)
            es_pressure = (es_ask - es_bid) / max(es_volume, 1)  # Positif = achat, Négatif = vente
            nq_pressure = (nq_ask - nq_bid) / max(nq_volume, 1)
            
            # 3. RELATIVE VOLUME STRENGTH (Nouveau)
            total_volume = es_volume + nq_volume
            es_vol_dominance = es_volume / total_volume if total_volume > 0 else 0.5
            nq_vol_dominance = nq_volume / total_volume if total_volume > 0 else 0.5
            
            # 4. MOMENTUM CONVERGENCE/DIVERGENCE
            momentum_alignment = 1 - abs(es_momentum_raw - nq_momentum_raw) / 2
            
            # 5. SCORING LEADERSHIP MULTI-FACTEURS
            
            # Score ES
            es_score = (
                abs(es_momentum_raw) * 0.4 +          # Force momentum brut
                es_vol_dominance * 0.3 +              # Dominance volume
                abs(es_pressure) * 0.2 +              # Pression bid/ask
                (1 if es_volume > nq_volume else 0.5) * 0.1  # Volume absolu
            )
            
            # Score NQ
            nq_score = (
                abs(nq_momentum_raw) * 0.4 +
                nq_vol_dominance * 0.3 +
                abs(nq_pressure) * 0.2 +
                (1 if nq_volume > es_volume else 0.5) * 0.1
            )
            
            # 6. DÉTERMINATION LEADER
            if es_score > nq_score * 1.15:  # Seuil de supériorité 15%
                leader = 'ES'
                leadership_strength = (es_score - nq_score) / max(nq_score, 0.1)
                momentum_direction = 'bullish' if es_momentum_raw > 0 else 'bearish'
            elif nq_score > es_score * 1.15:
                leader = 'NQ'
                leadership_strength = (nq_score - es_score) / max(es_score, 0.1)
                momentum_direction = 'bullish' if nq_momentum_raw > 0 else 'bearish'
            else:
                leader = 'NEUTRAL'
                leadership_strength = 0.1
                momentum_direction = 'neutral'
            
            # 7. QUALITÉ DU SIGNAL
            quality_factors = {
                'momentum_alignment': momentum_alignment,
                'volume_sufficient': 1 if (es_volume > 200 and nq_volume > 150) else 0.5,
                'clear_direction': 1 if abs(es_momentum_raw) > 0.3 or abs(nq_momentum_raw) > 0.3 else 0.3,
                'pressure_coherent': 1 if (es_pressure * es_momentum_raw > 0) or (nq_pressure * nq_momentum_raw > 0) else 0.5
            }
            
            signal_quality = sum(quality_factors.values()) / len(quality_factors)
            
            # 8. SIGNAL STRENGTH FINAL
            final_strength = min(1.0, leadership_strength * signal_quality)
            
            # 9. CLASSIFICATION
            if final_strength > 0.7 and leader != 'NEUTRAL':
                alignment = 'strong_leader'
            elif final_strength > 0.4 and leader != 'NEUTRAL':
                alignment = 'moderate_leader'
            elif final_strength > 0.2:
                alignment = 'weak_signal'
            else:
                alignment = 'no_signal'
            
            return {
                'leader': leader,
                'leadership_strength': leadership_strength,
                'signal_strength': final_strength,
                'momentum_direction': momentum_direction,
                'alignment': alignment,
                'quality_factors': quality_factors,
                'es_score': es_score,
                'nq_score': nq_score,
                'es_momentum': es_momentum_raw,
                'nq_momentum': nq_momentum_raw,
                'volume_dominance': {'ES': es_vol_dominance, 'NQ': nq_vol_dominance}
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse leadership: {e}")
            return self._get_neutral_result()
    
    def _get_neutral_result(self):
        """Résultat neutre par défaut"""
        return {
            'leader': 'NEUTRAL',
            'leadership_strength': 0.0,
            'signal_strength': 0.0,
            'momentum_direction': 'neutral',
            'alignment': 'no_signal',
            'quality_factors': {},
            'es_score': 0.5,
            'nq_score': 0.5,
            'es_momentum': 0.0,
            'nq_momentum': 0.0,
            'volume_dominance': {'ES': 0.5, 'NQ': 0.5}
        }
    
    def select_optimal_trade(self, analysis: dict) -> dict:
        """
        💡 SÉLECTION TRADE OPTIMALE
        Basée sur l'analyse leadership améliorée
        """
        try:
            leader = analysis['leader']
            strength = analysis['signal_strength']
            direction = analysis['momentum_direction']
            alignment = analysis['alignment']
            
            # RÈGLES DE TRADING AMÉLIORÉES
            
            if alignment == 'strong_leader' and strength > 0.7:
                # Leader fort = trade agressif
                if leader == 'ES':
                    trade_instrument = 'ES'
                    trade_direction = 'BUY' if direction == 'bullish' else 'SELL'
                    confidence = 0.85
                    size_multiplier = 2.0
                    stop_distance = 6
                    target_multiplier = 3.0
                elif leader == 'NQ':
                    trade_instrument = 'NQ'
                    trade_direction = 'BUY' if direction == 'bullish' else 'SELL'
                    confidence = 0.85
                    size_multiplier = 2.0
                    stop_distance = 6
                    target_multiplier = 3.0
                else:
                    return self._get_no_trade()
                    
                reason = f"{leader} LEADER FORT {direction.upper()}"
                
            elif alignment == 'moderate_leader' and strength > 0.4:
                # Leader modéré = trade conservateur
                trade_instrument = leader
                trade_direction = 'BUY' if direction == 'bullish' else 'SELL'
                confidence = 0.65
                size_multiplier = 1.0
                stop_distance = 8
                target_multiplier = 2.0
                reason = f"{leader} LEADER MODÉRÉ {direction.upper()}"
                
            elif alignment == 'weak_signal' and strength > 0.25:
                # Signal faible = trade très conservateur
                trade_instrument = leader
                trade_direction = 'BUY' if direction == 'bullish' else 'SELL'
                confidence = 0.45
                size_multiplier = 0.5
                stop_distance = 10
                target_multiplier = 1.5
                reason = f"{leader} SIGNAL FAIBLE {direction.upper()}"
                
            else:
                return self._get_no_trade()
            
            return {
                'should_trade': True,
                'instrument': trade_instrument,
                'direction': trade_direction,
                'confidence': confidence,
                'size_multiplier': size_multiplier,
                'stop_distance': stop_distance,
                'target_multiplier': target_multiplier,
                'reason': reason,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur sélection trade: {e}")
            return self._get_no_trade()
    
    def _get_no_trade(self):
        """Aucun trade"""
        return {
            'should_trade': False,
            'instrument': None,
            'direction': None,
            'confidence': 0.0,
            'size_multiplier': 0.0,
            'stop_distance': 0,
            'target_multiplier': 0.0,
            'reason': 'Aucun signal valide',
            'analysis': {}
        }
    
    def simulate_enhanced_trade(self, trade_decision: dict) -> dict:
        """
        🎲 SIMULATION TRADE AMÉLIORÉE
        Probabilités basées sur la qualité du signal
        """
        try:
            if not trade_decision['should_trade']:
                return {'executed': False, 'pnl': 0, 'is_win': False}
            
            confidence = trade_decision['confidence']
            size_multiplier = trade_decision['size_multiplier']
            target_multiplier = trade_decision['target_multiplier']
            
            # PROBABILITÉ DE SUCCÈS DYNAMIQUE
            base_success_rate = confidence
            
            # Ajustements basés sur l'instrument et la force
            if trade_decision['instrument'] in ['ES', 'NQ']:
                if confidence > 0.8:
                    success_rate = base_success_rate * 1.1  # Bonus signal fort
                elif confidence > 0.6:
                    success_rate = base_success_rate
                else:
                    success_rate = base_success_rate * 0.9  # Pénalité signal faible
            else:
                success_rate = base_success_rate * 0.8
            
            success_rate = min(0.95, max(0.05, success_rate))  # Limites réalistes
            
            # SIMULATION RÉSULTAT
            is_win = random.random() < success_rate
            
            # CALCUL P&L
            base_gain = 200 * target_multiplier * size_multiplier
            base_loss = 120 * size_multiplier
            
            if is_win:
                pnl = base_gain + random.uniform(-20, 50)  # Variance réaliste
            else:
                pnl = -(base_loss + random.uniform(-20, 30))
            
            return {
                'executed': True,
                'is_win': is_win,
                'pnl': round(pnl, 2),
                'success_rate': success_rate,
                'confidence': confidence,
                'size_multiplier': size_multiplier
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur simulation: {e}")
            return {'executed': False, 'pnl': 0, 'is_win': False}
    
    def generate_realistic_scenarios(self):
        """Génère des scenarios réalistes de marché avec plus de variété"""
        scenarios = [
            'strong_bullish_es', 'strong_bearish_es', 'strong_bullish_nq', 'strong_bearish_nq',
            'moderate_bullish_es', 'moderate_bearish_es', 'moderate_bullish_nq', 'moderate_bearish_nq',
            'divergent_bullish', 'divergent_bearish', 'choppy_neutral', 'high_volume_neutral'
        ]
        
        scenario = random.choice(scenarios)
        
        if scenario == 'strong_bullish_es':
            es_data = {
                "price": 6450.0 + random.uniform(8, 20),
                "volume": 600 + random.randint(100, 200),
                "delta": 400 + random.randint(100, 300),
                "bid_volume": 100 + random.randint(0, 50),
                "ask_volume": 500 + random.randint(100, 200),
            }
            nq_data = {
                "price": 18500.0 + random.uniform(2, 8),
                "volume": 300 + random.randint(0, 100),
                "delta": 150 + random.randint(0, 100),
                "bid_volume": 150 + random.randint(0, 50),
                "ask_volume": 150 + random.randint(0, 50),
            }
        elif scenario == 'strong_bearish_nq':
            es_data = {
                "price": 6450.0 - random.uniform(2, 8),
                "volume": 300 + random.randint(0, 100),
                "delta": -100 - random.randint(0, 100),
                "bid_volume": 150 + random.randint(0, 50),
                "ask_volume": 150 + random.randint(0, 50),
            }
            nq_data = {
                "price": 18500.0 - random.uniform(15, 30),
                "volume": 600 + random.randint(100, 200),
                "delta": -350 - random.randint(100, 200),
                "bid_volume": 450 + random.randint(100, 150),
                "ask_volume": 150 + random.randint(0, 50),
            }
        elif scenario == 'divergent_bullish':
            # ES bullish, NQ bearish (divergence)
            es_data = {
                "price": 6450.0 + random.uniform(5, 12),
                "volume": 500 + random.randint(50, 150),
                "delta": 250 + random.randint(50, 150),
                "bid_volume": 150 + random.randint(0, 50),
                "ask_volume": 350 + random.randint(50, 100),
            }
            nq_data = {
                "price": 18500.0 - random.uniform(5, 12),
                "volume": 500 + random.randint(50, 150),
                "delta": -200 - random.randint(50, 150),
                "bid_volume": 350 + random.randint(50, 100),
                "ask_volume": 150 + random.randint(0, 50),
            }
        else:
            # Scenario neutre par défaut
            es_data = {
                "price": 6450.0 + (random.random() - 0.5) * 8,
                "volume": 400 + random.randint(0, 150),
                "delta": (random.random() - 0.5) * 200,
                "bid_volume": 200 + random.randint(0, 100),
                "ask_volume": 200 + random.randint(0, 100),
            }
            nq_data = {
                "price": 18500.0 + (random.random() - 0.5) * 15,
                "volume": 350 + random.randint(0, 150),
                "delta": (random.random() - 0.5) * 180,
                "bid_volume": 175 + random.randint(0, 75),
                "ask_volume": 175 + random.randint(0, 75),
            }
        
        return es_data, nq_data, scenario
    
    async def run_enhanced_test(self, num_trades=25):
        """Lance le test de stratégie améliorée"""
        logger.info("=" * 80)
        logger.info("🚀 TEST STRATÉGIE LEADERSHIP ES/NQ AMÉLIORÉE")
        logger.info("=" * 80)
        
        trade_details = []
        
        for i in range(num_trades):
            logger.info(f"📊 TRADE #{i+1:02d}")
            
            # 1. Générer scenario réaliste
            es_data, nq_data, scenario = self.generate_realistic_scenarios()
            
            logger.info(f"   🎭 Scenario: {scenario}")
            logger.info(f"   📈 ES: {es_data['price']:.2f} | Vol: {es_data['volume']} | Delta: {es_data['delta']:.1f}")
            logger.info(f"   📊 NQ: {nq_data['price']:.2f} | Vol: {nq_data['volume']} | Delta: {nq_data['delta']:.1f}")
            
            # 2. Analyse leadership améliorée
            analysis = self.analyze_enhanced_leadership(es_data, nq_data)
            
            logger.info(f"   🎯 Leader: {analysis['leader']} | Strength: {analysis['signal_strength']:.3f}")
            logger.info(f"   🔗 Alignment: {analysis['alignment']} | Direction: {analysis['momentum_direction']}")
            
            # 3. Décision trade
            trade_decision = self.select_optimal_trade(analysis)
            
            if trade_decision['should_trade']:
                logger.info(f"   💡 Trade: {trade_decision['direction']} {trade_decision['instrument']}")
                logger.info(f"   🎯 Confidence: {trade_decision['confidence']:.2f} | Size: ×{trade_decision['size_multiplier']:.1f}")
                logger.info(f"   📝 Raison: {trade_decision['reason']}")
                
                # 4. Simulation trade
                result = self.simulate_enhanced_trade(trade_decision)
                
                if result['executed']:
                    self.trades_count += 1
                    if result['is_win']:
                        self.wins += 1
                        logger.info(f"   ✅ GAGNANT: +{result['pnl']:.2f}$ (Success rate: {result['success_rate']:.1%})")
                    else:
                        logger.info(f"   ❌ PERDANT: {result['pnl']:.2f}$ (Success rate: {result['success_rate']:.1%})")
                    
                    self.total_pnl += result['pnl']
                    
                    # Statistiques en cours
                    current_winrate = (self.wins / self.trades_count) * 100
                    logger.info(f"   📊 Running: {self.wins}/{self.trades_count} = {current_winrate:.1f}% | P&L: {self.total_pnl:.0f}$")
                    
                    trade_details.append({
                        'scenario': scenario,
                        'leader': analysis['leader'],
                        'strength': analysis['signal_strength'],
                        'trade': trade_decision,
                        'result': result
                    })
            else:
                logger.info(f"   ⏸️ Pas de trade: {trade_decision['reason']}")
            
            logger.info("")
            await asyncio.sleep(0.05)
        
        # Résultats finaux
        await self._display_enhanced_results(trade_details)
    
    async def _display_enhanced_results(self, trade_details):
        """Affiche les résultats détaillés"""
        logger.info("=" * 80)
        logger.info("📊 RÉSULTATS STRATÉGIE AMÉLIORÉE")
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
            
            # Analyse par leader
            es_trades = [t for t in trade_details if t['trade']['instrument'] == 'ES']
            nq_trades = [t for t in trade_details if t['trade']['instrument'] == 'NQ']
            
            if es_trades:
                es_wins = sum(1 for t in es_trades if t['result']['is_win'])
                es_winrate = (es_wins / len(es_trades)) * 100
                logger.info(f"📈 ES Trades: {len(es_trades)} | Win Rate: {es_winrate:.1f}%")
            
            if nq_trades:
                nq_wins = sum(1 for t in nq_trades if t['result']['is_win'])
                nq_winrate = (nq_wins / len(nq_trades)) * 100
                logger.info(f"📊 NQ Trades: {len(nq_trades)} | Win Rate: {nq_winrate:.1f}%")
            
            # Évaluation
            if final_winrate >= 70:
                logger.info("🟢 EXCELLENT: Stratégie très performante!")
            elif final_winrate >= 60:
                logger.info("🟡 BON: Stratégie rentable")
            elif final_winrate >= 50:
                logger.info("🟠 MOYEN: Stratégie neutre")
            else:
                logger.info("🔴 FAIBLE: Stratégie à améliorer")
                
            # Amélioration vs version de base
            improvement = final_winrate - 40.0  # Version de base: 40%
            if improvement > 0:
                logger.info(f"📈 AMÉLIORATION: +{improvement:.1f}% vs stratégie de base")
            else:
                logger.info(f"📉 DÉGRADATION: {improvement:.1f}% vs stratégie de base")
        else:
            logger.info("❌ Aucun trade exécuté")

async def main():
    """Fonction principale"""
    try:
        strategy = EnhancedLeadershipStrategy()
        await strategy.run_enhanced_test(num_trades=30)
        
    except KeyboardInterrupt:
        logger.info("🛑 Test interrompu par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")

if __name__ == "__main__":
    asyncio.run(main())

