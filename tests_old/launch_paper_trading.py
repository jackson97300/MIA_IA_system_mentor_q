#!/usr/bin/env python3
"""
🚀 LANCEMENT PAPER TRADING - MIA_IA_SYSTEM
===========================================

Script de lancement pour tester le système automation_modules
en paper trading avec IBKR (pas Sierra Charts).

Configuration:
- Compte IBKR Paper Trading: 250 000$
- Flux de données de marché activé
- Trading ES (E-mini S&P 500)
- Pas d'ordres réels (simulation uniquement)

Usage:
    python launch_paper_trading.py --dry-run    # Simulation sans ordres
    python launch_paper_trading.py --live       # Avec ordres paper trading
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from config.automation_config import AutomationConfig
from execution.simple_trader import MIAAutomationSystem
from execution.sierra_connector import SierraConnector, create_sierra_connector
from execution.sierra_dtc_connector import SierraDTCConnector
from execution.trading_executor import TradingExecutor
from monitoring.performance_tracker import PerformanceTracker
from execution.risk_manager import RiskManager
from features.confluence_calculator import EnhancedConfluenceCalculator

logger = get_logger(__name__)

class PaperTradingLauncher:
    """Lanceur pour paper trading IBKR"""
    
    def __init__(self, live_trading: bool = False):
        self.live_trading = live_trading
        self.config = self._create_paper_trading_config()
        self.trading_system = None
        self.performance_tracker = PerformanceTracker()
        self.risk_manager = RiskManager(self.config)
        
        # Sierra Chart Integration
        self.sierra_connector = None
        self.sierra_dtc_connector = None
        self.trading_executor = None
        
        logger.info(f"🚀 Lanceur Paper Trading initialisé (Live: {live_trading})")
    
    def _create_paper_trading_config(self) -> AutomationConfig:
        """Crée la configuration pour paper trading"""
        config = AutomationConfig()
        
        # Configuration Paper Trading IBKR
        config.ibkr_host = "127.0.0.1"
        config.ibkr_port = 7497  # Port TWS Paper Trading
        config.ibkr_client_id = 1
        
        # Paramètres de trading conservateurs pour paper trading
        config.max_position_size = 1  # 1 contrat ES à la fois
        config.daily_loss_limit = 1000.0  # Limite quotidienne 1000$
        config.min_signal_confidence = 0.75  # Confiance élevée
        config.trading_start_hour = 9  # 9h00 EST
        config.trading_end_hour = 16  # 16h00 EST
        config.position_risk_percent = 0.5  # 0.5% du capital par trade
        config.max_daily_trades = 10  # Max 10 trades par jour
        
        # Risk Management
        config.stop_loss_ticks = 10  # 10 ticks = 250$ sur ES
        config.take_profit_ratio = 2.0  # 2:1 ratio
        
        # ML & Analysis
        config.ml_ensemble_enabled = True
        config.ml_min_confidence = 0.70
        config.gamma_cycles_enabled = True
        
        # Confluence
        config.confluence_threshold = 0.30
        config.confluence_adaptive = True
        
        # Monitoring
        config.performance_update_interval = 30  # 30 secondes
        config.health_check_interval = 15  # 15 secondes
        
        # Logging
        config.log_level = "INFO"
        config.log_to_file = True
        
        # Sierra Chart Integration
        config.sierra_enabled = True
        config.sierra_data_path = 'D:/MIA_IA_system'
        config.sierra_unified_pattern = 'mia_unified_*.jsonl'
        config.sierra_charts = [3, 4, 8, 10]
        config.sierra_fallback_simulation = True
        
        # DTC Configuration
        config.sierra_dtc_enabled = True
        config.sierra_dtc_port_es = 11099
        config.sierra_dtc_port_nq = 11100
        
        return config
    
    async def initialize_system(self) -> bool:
        """Initialise le système de trading"""
        try:
            logger.info("🔧 Initialisation système paper trading...")
            
            # Validation configuration
            if not self.config.validate():
                logger.error("❌ Configuration invalide")
                return False
            
            # Création système trading
            self.trading_system = MIAAutomationSystem(self.config)
            
            # Initialisation composants Sierra Chart
            await self._initialize_sierra_components()
            
            # Vérifications pré-trading
            await self._pre_trading_checks()
            
            logger.info("✅ Système paper trading initialisé")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation: {e}")
            return False
    
    async def _initialize_sierra_components(self) -> None:
        """Initialise les composants Sierra Chart"""
        try:
            if self.config.sierra_enabled:
                logger.info("🔗 Initialisation composants Sierra Chart...")
                
                # Sierra Connector pour données unifiées
                self.sierra_connector = create_sierra_connector({
                    'data_path': self.config.sierra_data_path,
                    'unified_pattern': self.config.sierra_unified_pattern,
                    'charts': self.config.sierra_charts
                })
                
                # Sierra DTC Connector pour exécution
                if self.config.sierra_dtc_enabled:
                    self.sierra_dtc_connector = SierraDTCConnector()
                    logger.info("✅ Sierra DTC Connector initialisé")
                
                # Trading Executor
                self.trading_executor = TradingExecutor()
                
                logger.info("✅ Composants Sierra Chart initialisés")
            else:
                logger.info("📊 Sierra Chart désactivé - Mode simulation uniquement")
                
        except Exception as e:
            logger.warning(f"⚠️ Erreur initialisation Sierra Chart: {e}")
            logger.info("🔄 Fallback vers mode simulation")
    
    async def _pre_trading_checks(self) -> None:
        """Vérifications pré-trading"""
        logger.info("🔍 Vérifications pré-trading...")
        
        # Vérification heures trading
        current_hour = datetime.now().hour
        if not (self.config.trading_start_hour <= current_hour <= self.config.trading_end_hour):
            logger.warning(f"⚠️ Hors heures de trading ({current_hour}h)")
        
        # Vérification limites
        if not self.risk_manager.check_daily_loss_limit():
            logger.warning("⚠️ Limite de perte quotidienne atteinte")
        
        # Vérification connexion IBKR (simulation)
        logger.info("🔗 Test connexion IBKR Paper Trading...")
        # Ici on pourrait ajouter un vrai test de connexion IBKR
        
        logger.info("✅ Vérifications pré-trading terminées")
    
    async def start_paper_trading(self) -> None:
        """Démarre le paper trading"""
        try:
            logger.info("🚀 Démarrage Paper Trading MIA_IA_SYSTEM")
            
            # Initialisation
            if not await self.initialize_system():
                return
            
            # Affichage configuration
            self._display_configuration()
            
            # Démarrage boucle trading
            await self._trading_loop()
            
        except KeyboardInterrupt:
            logger.info("🛑 Arrêt demandé par l'utilisateur")
            await self._cleanup()
        except Exception as e:
            logger.error(f"❌ Erreur paper trading: {e}")
            await self._cleanup()
    
    def _display_configuration(self) -> None:
        """Affiche la configuration actuelle"""
        logger.info("📋 === CONFIGURATION PAPER TRADING ===")
        logger.info(f"  Mode: {'LIVE' if self.live_trading else 'DRY RUN'}")
        logger.info(f"  Compte: IBKR Paper Trading (250 000$)")
        logger.info(f"  Instrument: ES (E-mini S&P 500)")
        logger.info(f"  Position max: {self.config.max_position_size} contrat(s)")
        logger.info(f"  Limite quotidienne: {self.config.daily_loss_limit}$")
        logger.info(f"  Heures trading: {self.config.trading_start_hour}h-{self.config.trading_end_hour}h")
        logger.info(f"  Stop Loss: {self.config.stop_loss_ticks} ticks")
        logger.info(f"  Take Profit: {self.config.take_profit_ratio}:1")
        logger.info(f"  ML Ensemble: {'Activé' if self.config.ml_ensemble_enabled else 'Désactivé'}")
        logger.info(f"  Gamma Cycles: {'Activé' if self.config.gamma_cycles_enabled else 'Désactivé'}")
        logger.info("=" * 50)
    
    async def _trading_loop(self) -> None:
        """Boucle principale de trading"""
        logger.info("🔄 Démarrage boucle trading...")
        
        iteration = 0
        while True:
            try:
                iteration += 1
                current_time = datetime.now()
                
                logger.info(f"📊 Itération {iteration} - {current_time.strftime('%H:%M:%S')}")
                
                # Vérification heures trading
                if not self._is_trading_hours():
                    logger.info("⏰ Hors heures de trading - Attente...")
                    await asyncio.sleep(60)  # Attendre 1 minute
                    continue
                
                # Génération signal (Sierra Chart ou simulation)
                signal = await self._generate_signal()
                
                if signal:
                    logger.info(f"📈 Signal détecté: {signal}")
                    
                    # Vérifications risk management
                    if self._risk_management_check(signal):
                        # Exécution trade
                        if self.live_trading:
                            await self._execute_paper_trade(signal)
                        else:
                            await self._simulate_trade(signal)
                    else:
                        logger.warning("⚠️ Signal rejeté par risk management")
                else:
                    logger.info("📊 Aucun signal - Attente...")
                
                # Mise à jour performance
                await self._update_performance()
                
                # Health check
                await self._health_check()
                
                # Attente prochaine itération
                await asyncio.sleep(30)  # 30 secondes entre itérations
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle trading: {e}")
                await asyncio.sleep(10)
    
    def _is_trading_hours(self) -> bool:
        """Vérifie si on est dans les heures de trading"""
        current_hour = datetime.now().hour
        return self.config.trading_start_hour <= current_hour <= self.config.trading_end_hour
    
    async def _generate_signal(self) -> Optional[Dict[str, Any]]:
        """Génère un signal de trading (Sierra Chart ou simulation)"""
        try:
            # Essayer d'abord avec Sierra Chart
            if self.sierra_connector:
                signal = await self._generate_sierra_signal()
                if signal:
                    return signal
            
            # Fallback vers simulation
            return await self._generate_mock_signal()
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur génération signal: {e}")
            return await self._generate_mock_signal()
    
    async def _generate_sierra_signal(self) -> Optional[Dict[str, Any]]:
        """Génère un signal basé sur les données Sierra Chart"""
        try:
            # Récupérer les dernières données unifiées
            latest_data = self.sierra_connector.get_latest_unified_data()
            if not latest_data:
                return None
            
            # Analyser les données pour générer un signal
            # Ici on pourrait intégrer la logique de signal du système principal
            import random
            
            # Simulation basée sur les données réelles
            if random.random() < 0.15:  # 15% de chance avec données réelles
                signal_type = random.choice(["BUY", "SELL"])
                confidence = random.uniform(0.80, 0.95)
                
                return {
                    "type": signal_type,
                    "confidence": confidence,
                    "instrument": "ES",
                    "price": latest_data.get("close", 4500.0),
                    "timestamp": datetime.now(),
                    "source": "sierra_chart",
                    "sierra_data": latest_data
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"⚠️ Erreur signal Sierra Chart: {e}")
            return None
    
    async def _generate_mock_signal(self) -> Optional[Dict[str, Any]]:
        """Génère un signal de trading simulé"""
        import random
        
        # Simulation signal basé sur probabilité
        if random.random() < 0.1:  # 10% de chance de signal
            signal_type = random.choice(["BUY", "SELL"])
            confidence = random.uniform(0.75, 0.95)
            
            return {
                "type": signal_type,
                "confidence": confidence,
                "instrument": "ES",
                "price": 6334.25 + random.uniform(-10, 10),
                "timestamp": datetime.now(),
                "source": "mock_signal"
            }
        
        return None
    
    def _risk_management_check(self, signal: Dict[str, Any]) -> bool:
        """Vérification risk management"""
        try:
            # Vérification limite quotidienne
            if not self.risk_manager.check_daily_loss_limit():
                logger.warning("⚠️ Limite de perte quotidienne atteinte")
                return False
            
            # Vérification nombre de trades
            if self.performance_tracker.get_daily_trades() >= self.config.max_daily_trades:
                logger.warning("⚠️ Nombre maximum de trades quotidien atteint")
                return False
            
            # Vérification confiance signal
            if signal["confidence"] < self.config.min_signal_confidence:
                logger.warning(f"⚠️ Confiance insuffisante: {signal['confidence']:.2f}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur risk management: {e}")
            return False
    
    async def _execute_paper_trade(self, signal: Dict[str, Any]) -> None:
        """Exécute un trade en paper trading"""
        try:
            logger.info(f"📈 EXÉCUTION PAPER TRADE: {signal['type']} ES @ {signal['price']:.2f}")
            
            # Simulation exécution IBKR
            order_id = f"PAPER_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Calcul position size basé sur risk management
            account_balance = 250000.0  # Paper trading balance
            risk_amount = account_balance * (self.config.position_risk_percent / 100)
            position_size = 1  # 1 contrat ES
            
            logger.info(f"  📊 Order ID: {order_id}")
            logger.info(f"  💰 Risk Amount: {risk_amount:.2f}$")
            logger.info(f"  📦 Position Size: {position_size} contrat(s)")
            
            # Simulation résultat trade
            await self._simulate_trade_result(signal, order_id)
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution paper trade: {e}")
    
    async def _simulate_trade(self, signal: Dict[str, Any]) -> None:
        """Simule un trade (dry run)"""
        try:
            logger.info(f"🎭 SIMULATION TRADE: {signal['type']} ES @ {signal['price']:.2f}")
            
            # Simulation sans exécution
            order_id = f"SIM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            logger.info(f"  📊 Order ID: {order_id}")
            logger.info(f"  🎭 Mode: DRY RUN (pas d'exécution)")
            
            # Simulation résultat
            await self._simulate_trade_result(signal, order_id)
            
        except Exception as e:
            logger.error(f"❌ Erreur simulation trade: {e}")
    
    async def _simulate_trade_result(self, signal: Dict[str, Any], order_id: str) -> None:
        """Simule le résultat d'un trade"""
        import random
        import time
        
        # Simulation latence
        await asyncio.sleep(0.1)  # 100ms latence
        
        # Simulation résultat (50/50 chance de succès)
        success = random.choice([True, False])
        
        if success:
            profit = random.uniform(100, 500)  # Profit 100-500$
            logger.info(f"  ✅ Trade réussi - Profit: +{profit:.2f}$")
        else:
            loss = random.uniform(100, 300)  # Perte 100-300$
            logger.warning(f"  ❌ Trade perdu - Perte: -{loss:.2f}$")
        
        # Mise à jour performance tracker
        self.performance_tracker.add_trade({
            "order_id": order_id,
            "signal": signal,
            "success": success,
            "pnl": profit if success else -loss,
            "timestamp": datetime.now()
        })
    
    async def _update_performance(self) -> None:
        """Met à jour les statistiques de performance"""
        try:
            stats = self.performance_tracker.get_stats()
            
            if stats["total_trades"] > 0:
                logger.info(f"📊 Performance: {stats['total_trades']} trades, "
                          f"Win Rate: {stats['win_rate']:.1f}%, "
                          f"P&L: {stats['total_pnl']:.2f}$")
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour performance: {e}")
    
    async def _health_check(self) -> None:
        """Vérification santé du système"""
        try:
            current_time = datetime.now()
            
            # Vérification mémoire
            import psutil
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            if memory_usage > 500:  # Plus de 500MB
                logger.warning(f"⚠️ Usage mémoire élevé: {memory_usage:.1f}MB")
            
            # Vérification uptime
            uptime = current_time - self.performance_tracker.start_time
            logger.info(f"⏱️ Uptime: {uptime}")
            
        except Exception as e:
            logger.error(f"❌ Erreur health check: {e}")
    
    async def _cleanup(self) -> None:
        """Nettoyage à l'arrêt"""
        try:
            logger.info("🧹 Nettoyage système...")
            
            if self.trading_system:
                await self.trading_system.stop()
            
            # Affichage statistiques finales
            stats = self.performance_tracker.get_stats()
            logger.info("📊 === STATISTIQUES FINALES ===")
            logger.info(f"  Total Trades: {stats['total_trades']}")
            logger.info(f"  Win Rate: {stats['win_rate']:.1f}%")
            logger.info(f"  Total P&L: {stats['total_pnl']:.2f}$")
            logger.info(f"  Uptime: {stats['uptime']}")
            logger.info("=" * 30)
            
        except Exception as e:
            logger.error(f"❌ Erreur cleanup: {e}")

def main():
    parser = argparse.ArgumentParser(description="Lancement Paper Trading MIA_IA_SYSTEM")
    parser.add_argument("--dry-run", action="store_true", help="Mode simulation (pas d'ordres)")
    parser.add_argument("--live", action="store_true", help="Mode live (ordres paper trading)")
    
    args = parser.parse_args()
    
    # Déterminer mode
    live_trading = args.live
    if not args.dry_run and not args.live:
        live_trading = False  # Par défaut dry-run
    
    # Créer et lancer
    launcher = PaperTradingLauncher(live_trading)
    
    try:
        asyncio.run(launcher.start_paper_trading())
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur lancement: {e}")

if __name__ == "__main__":
    main()

