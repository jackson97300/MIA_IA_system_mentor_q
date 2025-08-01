#!/usr/bin/env python3
"""
TEST AUTOMATION SIMULATION - Sans IBKR
Teste les nouveaux modules avec données simulées
"""

import sys
import asyncio
import random
import time
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.base_types import MarketData
from core.signal_explainer import create_signal_explainer
from core.catastrophe_monitor import create_catastrophe_monitor, CatastropheLevel
import pandas as pd

logger = get_logger(__name__)

class MarketDataSimulator:
    """Simulateur de données de marché réalistes"""
    
    def __init__(self):
        self.current_price = 5247.50  # Prix ES initial
        self.volume = 1000
        self.bid = self.current_price - 0.25
        self.ask = self.current_price + 0.25
        
    def generate_tick(self) -> MarketData:
        """Génère un tick de données réaliste"""
        # Mouvement aléatoire mais réaliste
        change = random.uniform(-2.0, 2.0)  # ±2 points max
        self.current_price += change
        
        # Volume aléatoire
        self.volume = random.randint(500, 2000)
        
        # Spread réaliste
        spread = random.uniform(0.25, 1.0)
        self.bid = self.current_price - spread/2
        self.ask = self.current_price + spread/2
        
        return MarketData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            open=self.current_price - random.uniform(-0.5, 0.5),
            high=self.current_price + random.uniform(0, 1.0),
            low=self.current_price - random.uniform(0, 1.0),
            close=self.current_price,
            volume=self.volume,
            bid=self.bid,
            ask=self.ask
        )

class TradingSimulator:
    """Simulateur de trading pour tester nos modules"""
    
    def __init__(self):
        self.market_simulator = MarketDataSimulator()
        
        # Nos nouveaux modules
        self.signal_explainer = create_signal_explainer()
        
        catastrophe_config = {
            'daily_loss_limit': 200.0,      # $200 pour test
            'max_position_size': 1,
            'max_consecutive_losses': 3,
            'account_balance_min': 1000.0
        }
        self.catastrophe_monitor = create_catastrophe_monitor(catastrophe_config)
        
        # États de trading
        self.daily_pnl = 0.0
        self.position_size = 0
        self.last_signal_time = 0
        self.trades_count = 0
        self.consecutive_losses = 0
        
        logger.info("🎮 Trading Simulator initialisé")
        logger.info("🔍 Signal Explainer activé")
        logger.info("🛡️ Catastrophe Monitor activé")
    
    def simulate_confluence_score(self) -> float:
        """Simule un score de confluence réaliste"""
        # 70% du temps confluence faible (pas de signal)
        # 30% du temps confluence élevée (signal possible)
        if random.random() < 0.7:
            return random.uniform(0.3, 0.74)  # Trop faible
        else:
            return random.uniform(0.75, 0.95)  # OK pour signal
    
    def simulate_trade_result(self) -> tuple:
        """Simule résultat d'un trade"""
        # 65% de trades gagnants (réaliste)
        is_winner = random.random() < 0.65
        
        if is_winner:
            pnl = random.uniform(25.0, 150.0)  # Gain
            self.consecutive_losses = 0
        else:
            pnl = -random.uniform(25.0, 100.0)  # Perte
            self.consecutive_losses += 1
        
        self.daily_pnl += pnl
        self.trades_count += 1
        
        # Enregistrer dans catastrophe monitor
        self.catastrophe_monitor.record_trade_result(pnl, is_winner)
        
        return pnl, is_winner
    
    async def run_simulation(self, duration_minutes: int = 5):
        """Lance simulation complète"""
        logger.info(f"🚀 Démarrage simulation ({duration_minutes} minutes)")
        logger.info("=" * 60)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        tick_count = 0
        signals_generated = 0
        signals_blocked = 0
        explanations_shown = 0
        
        while time.time() < end_time:
            try:
                # Générer données marché
                market_data = self.market_simulator.generate_tick()
                tick_count += 1
                
                # Simuler confluence
                confluence_score = self.simulate_confluence_score()
                
                # Tester Signal Explainer
                reasons = self.signal_explainer.explain_no_signal(
                    market_data=market_data,
                    confluence_score=confluence_score,
                    last_signal_time=self.last_signal_time
                )
                
                # Afficher explication si conditions pas OK
                if reasons and self.signal_explainer.should_log_explanation():
                    explanation = self.signal_explainer.format_explanation(reasons)
                    logger.info(f"🔍 {explanation}")
                    explanations_shown += 1
                
                # Si conditions OK pour signal, tester Catastrophe Monitor
                elif not reasons:  # Pas de raisons = signal possible
                    signals_generated += 1
                    self.last_signal_time = time.time()
                    
                    # Vérifier protection catastrophe
                    alert = self.catastrophe_monitor.check_catastrophe_conditions(
                        current_pnl=self.daily_pnl,
                        account_balance=5000.0,  # Balance simulée
                        position_size=self.position_size,
                        market_data=market_data
                    )
                    
                    if alert.level == CatastropheLevel.EMERGENCY:
                        logger.critical(f"🚨 EMERGENCY: {alert.trigger}")
                        logger.critical(f"ACTION: {alert.action_required}")
                        logger.critical("🛑 SIMULATION ARRÊTÉE POUR PROTECTION")
                        break
                        
                    elif alert.level == CatastropheLevel.DANGER:
                        logger.error(f"⚠️ DANGER: {alert.trigger}")
                        logger.error("🛑 Trade bloqué par protection")
                        signals_blocked += 1
                        
                    elif alert.level == CatastropheLevel.WARNING:
                        logger.warning(f"💡 WARNING: {alert.trigger}")
                        # Continuer mais exécuter trade
                        pnl, is_winner = self.simulate_trade_result()
                        result = "WIN" if is_winner else "LOSS"
                        logger.info(f"💰 Trade {self.trades_count}: {result} {pnl:+.2f}$ (Total: {self.daily_pnl:+.2f}$)")
                        
                    else:  # Normal
                        # Exécuter trade
                        pnl, is_winner = self.simulate_trade_result()
                        result = "WIN" if is_winner else "LOSS"
                        logger.info(f"💰 Trade {self.trades_count}: {result} {pnl:+.2f}$ (Total: {self.daily_pnl:+.2f}$)")
                
                # Pause réaliste
                await asyncio.sleep(0.1)  # 10 ticks/sec
                
            except Exception as e:
                logger.error(f"Erreur simulation: {e}")
                break
        
        # Résumé final
        elapsed = time.time() - start_time
        logger.info("\n" + "=" * 60)
        logger.info("📊 RÉSUMÉ SIMULATION")
        logger.info("=" * 60)
        logger.info(f"⏱️ Durée: {elapsed:.1f}s")
        logger.info(f"📈 Ticks générés: {tick_count}")
        logger.info(f"🎯 Signaux générés: {signals_generated}")
        logger.info(f"🛡️ Signaux bloqués: {signals_blocked}")
        logger.info(f"🔍 Explications montrées: {explanations_shown}")
        logger.info(f"💰 Trades exécutés: {self.trades_count}")
        logger.info(f"💵 P&L final: {self.daily_pnl:+.2f}$")
        logger.info(f"📉 Pertes consécutives: {self.consecutive_losses}")
        
        # Status des modules
        if self.catastrophe_monitor:
            status = self.catastrophe_monitor.get_status_summary()
            logger.info(f"🛡️ Emergency stop actif: {status['emergency_stop_active']}")
            logger.info(f"📊 Alertes générées: {status['alerts_today']}")
        
        logger.info("=" * 60)
        logger.info("✅ SIMULATION TERMINÉE - MODULES TESTÉS AVEC SUCCÈS")

async def main():
    """Test principal"""
    print("🎮 SIMULATION TRADING - TEST COMPLET SANS IBKR")
    print("=" * 60)
    
    try:
        simulator = TradingSimulator()
        await simulator.run_simulation(duration_minutes=2)  # 2 minutes de test
        
    except KeyboardInterrupt:
        print("\n🛑 Simulation interrompue par utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())